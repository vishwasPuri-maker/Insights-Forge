"""
app/core/rag/events.py
----------------------
Event-driven hook system for RAG indexing and synchronization. Decouples dataset ingestion
tasks from direct vector store operations, enabling flexible asynchronous execution.
"""

import uuid
import logging
from typing import Callable, Dict, List, Any

from app.db.session import SessionLocal
from app.services.indexing_service import IndexingService

logger = logging.getLogger("rag-events")


class RAGEvent:
    """
    Constant event names for RAG indexing lifecycle.
    """

    DATASET_COMPLETED = "dataset_completed"
    DATASET_UPDATED = "dataset_updated"
    DATASET_DELETED = "dataset_deleted"


class RAGEventDispatcher:
    """
    In-memory pub-sub dispatcher for RAG event execution.
    """

    _listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    @classmethod
    def register(
        cls, event_type: str, listener: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Registers a listener function to be executed when an event is dispatched.
        """
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(listener)
        logger.debug(f"Registered RAG event listener for event: {event_type}")

    @classmethod
    def dispatch(cls, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Triggers all registered listeners for a specific event type.
        """
        logger.info(f"Dispatching RAG event '{event_type}' with payload: {payload}")
        listeners = cls._listeners.get(event_type, [])
        for listener in listeners:
            try:
                listener(payload)
            except Exception as e:
                logger.error(
                    f"Error executing RAG event listener for '{event_type}': {str(e)}"
                )


# ----------------------------------------------------------------------
# Default Listener Implementations
# ----------------------------------------------------------------------


def handle_dataset_completed(payload: Dict[str, Any]) -> None:
    """
    Triggered when a dataset is successfully completed. Triggers full record vector indexing.
    """
    dataset_id_str = payload.get("dataset_id")
    if not dataset_id_str:
        logger.error("RAG event payload missing 'dataset_id'.")
        return

    dataset_id = uuid.UUID(dataset_id_str)
    db = SessionLocal()
    try:
        indexer = IndexingService(db)
        success = indexer.index_dataset(dataset_id)
        if success:
            logger.info(f"Successfully indexed dataset {dataset_id} via event hook.")
        else:
            logger.error(f"Failed to index dataset {dataset_id} via event hook.")
    finally:
        db.close()


def handle_dataset_updated(payload: Dict[str, Any]) -> None:
    """
    Triggered when a dataset is updated. Purges old vector store documents and rebuilds index.
    """
    dataset_id_str = payload.get("dataset_id")
    if not dataset_id_str:
        logger.error("RAG event payload missing 'dataset_id'.")
        return

    dataset_id = uuid.UUID(dataset_id_str)
    db = SessionLocal()
    try:
        indexer = IndexingService(db)
        # Purge existing first
        indexer.delete_dataset_index(dataset_id)
        # Re-index
        success = indexer.index_dataset(dataset_id)
        if success:
            logger.info(f"Successfully re-indexed dataset {dataset_id} via event hook.")
        else:
            logger.error(f"Failed to re-index dataset {dataset_id} via event hook.")
    finally:
        db.close()


def handle_dataset_deleted(payload: Dict[str, Any]) -> None:
    """
    Triggered when a dataset is deleted. Removes all its vector documents from vector store.
    """
    dataset_id_str = payload.get("dataset_id")
    if not dataset_id_str:
        logger.error("RAG event payload missing 'dataset_id'.")
        return

    dataset_id = uuid.UUID(dataset_id_str)
    db = SessionLocal()
    try:
        indexer = IndexingService(db)
        indexer.delete_dataset_index(dataset_id)
        logger.info(
            f"Successfully deleted vector index for dataset {dataset_id} via event hook."
        )
    finally:
        db.close()


# Register default listener callbacks to the dispatcher
RAGEventDispatcher.register(RAGEvent.DATASET_COMPLETED, handle_dataset_completed)
RAGEventDispatcher.register(RAGEvent.DATASET_UPDATED, handle_dataset_updated)
RAGEventDispatcher.register(RAGEvent.DATASET_DELETED, handle_dataset_deleted)
