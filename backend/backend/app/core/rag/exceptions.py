"""
app/core/rag/exceptions.py
--------------------------
Domain-specific exceptions for the RAG (Retrieval-Augmented Generation) pipeline,
handling errors related to retrieval operations, tenant isolation violations,
and embedding model/version mismatches.
"""


class RAGException(Exception):
    """Base exception class for all RAG and retrieval-related errors."""

    pass


class TenantIsolationViolationError(RAGException):
    """Raised when a cross-tenant data access is detected or attempted."""

    pass


class EmbeddingModelMismatchError(RAGException):
    """Raised when there is a mismatch between the configured embedding model/version and the stored embeddings."""

    pass
