"""
Chat Service
------------
Service layer orchestrating multi-agent chatbot reasoning, database context retrieval,
structured prompt compilation, and streaming response generation.
"""

import os
import sys
import logging
import uuid
import time
import datetime
from typing import Optional, Generator
from sqlalchemy.orm import Session
from app.models.enums import AIModel, AIMessageSender
from app.core.memory.conversation_memory_service import ConversationMemoryService
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.core.llm.token_counter import TokenCounter
from app.core.llm.prompt_builder import StructuredPromptBuilder
from app.core.llm.provider import LLMChunk
from app.db.session import SessionLocal
from app.api.deps import CurrentUser

# Dynamic path resolution to resolve chatbot modules
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHATBOT_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, "../../../../chatbot/Apex-AI-main/backend")
)
if CHATBOT_PATH not in sys.path:
    sys.path.insert(0, CHATBOT_PATH)

from agents.router import MultiAgentRouter  # noqa: E402
from agents.prompt_engine import PromptTemplateEngine  # noqa: E402
from app.core.llm.factory import LLMFactory  # noqa: E402
from app.core.config import settings  # noqa: E402

logger = logging.getLogger("chat-service")


class ChatService:
    """
    Service layer orchestrating multi-agent chatbot reasoning and completions.
    """

    def __init__(self) -> None:
        self.agent_router = MultiAgentRouter()

        # Resolve chatbot prompts path relative to workspace
        prompts_path = os.path.abspath(
            os.path.join(CURRENT_DIR, "../../../../chatbot/Apex-AI-main/prompts")
        )
        self.prompt_engine = PromptTemplateEngine(prompts_dir=prompts_path)
        self.llm_provider = LLMFactory.get_provider()
        self.memory_service = ConversationMemoryService()

    def get_chat_completion(
        self,
        db: Session,
        query: str,
        response_mode: str,
        current_user: CurrentUser,
        conversation_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """
        Executes query routing via MultiAgentRouter, retrieves scoped workspace records
        to feed context, compiles prompt, calls LLM, and formats response.
        """
        # If conversation_id is not provided, create a default one
        if not conversation_id:
            convo = self.memory_service.create_conversation(
                db=db,
                title="New Chat Session",
                model_name=AIModel.LLAMA,
                workspace_id=current_user.workspace_id,
                organization_id=current_user.organization_id,
                user_id=current_user.id,
            )
            conversation_id = convo.id
            db.commit()

        # 1. Save user query immediately to protect history
        user_tokens = TokenCounter.estimate_tokens(query)
        self.memory_service.save_user_message(
            db=db,
            conversation_id=conversation_id,
            message=query,
            tokens_used=user_tokens,
        )
        db.commit()

        # 2. Call MultiAgentRouter to classify intent and select virtual agent
        routing_decision = self.agent_router.route_query(
            user_query=query,
            tenant_id=str(current_user.organization_id),
            response_mode=response_mode,
            db=db,
            workspace_id=current_user.workspace_id,
            organization_id=current_user.organization_id,
        )

        agent_role = routing_decision["role"]

        # Handle SecurityAgent or FactCheckAgent blocks (immediate block returned)
        if agent_role in ("SecurityAgent", "FactCheckAgent"):
            ai_response = routing_decision.get(
                "response", "Request blocked by security rules."
            )
            ai_tokens = TokenCounter.estimate_tokens(ai_response)
            self.memory_service.save_ai_message(
                db=db,
                conversation_id=conversation_id,
                message=ai_response,
                tokens_used=ai_tokens,
                response_time_ms=0,
            )
            db.commit()
            return {
                "status": "success",
                "agent": agent_role,
                "analysis_type": routing_decision.get("analysis_type", "general"),
                "analysis": ai_response,
                "confidence": routing_decision["confidence"],
                "provider": "system",
                "model": "rule_guard",
                "conversation_id": conversation_id,
            }

        # 3. Render prompt from PromptTemplateEngine (grounded RAG database context)
        analysis_type = routing_decision.get("analysis_type", "general")
        context_data = routing_decision.get("context", "")

        rendered_prompt = self.prompt_engine.render_prompt(
            analysis_type=analysis_type,
            input_data=context_data,
        )

        if not rendered_prompt:
            logger.warning(
                f"Failed to load prompt template for: {analysis_type}. Using fallback."
            )
            rendered_prompt = f"Agent Context:\n{context_data}"

        # 4. Fetch memory states from database
        conversation = self.memory_service.get_conversation_by_id(
            db=db,
            conversation_id=conversation_id,
            workspace_id=current_user.workspace_id,
            organization_id=current_user.organization_id,
        )
        summary = conversation.summary if conversation else None

        message_repo = MessageRepository(db)
        # Fetch recent messages (+1 to fetch current query we just inserted)
        recent_messages = message_repo.get_recent_messages(
            conversation_id, limit=settings.MEMORY_RECENT_MESSAGES + 1
        )
        # Slice off current query from history compilation
        if (
            recent_messages
            and recent_messages[-1].message == query
            and recent_messages[-1].sender_type == AIMessageSender.USER
        ):
            recent_messages = recent_messages[:-1]

        # 5. Compile prompt messages list using pure StructuredPromptBuilder
        messages = StructuredPromptBuilder.build_messages(
            system_prompt=rendered_prompt,
            summary=summary,
            recent_messages=recent_messages,
            rag_context=context_data,
            query=query,
        )

        # 6. Execute LLM Provider call
        start_time = time.time()
        llm_res = self.llm_provider.generate(messages)
        latency_ms = int((time.time() - start_time) * 1000)

        ai_response = llm_res.content or ""
        ai_tokens = TokenCounter.estimate_tokens(ai_response)

        # 7. Persist AI message response
        if llm_res.status == "success":
            self.memory_service.save_ai_message(
                db=db,
                conversation_id=conversation_id,
                message=ai_response,
                tokens_used=ai_tokens,
                response_time_ms=latency_ms,
            )
            db.commit()

        return {
            "status": llm_res.status,
            "agent": agent_role,
            "analysis_type": analysis_type,
            "analysis": ai_response,
            "confidence": routing_decision["confidence"],
            "provider": llm_res.provider,
            "model": llm_res.model,
            "conversation_id": conversation_id,
        }

    def get_chat_completion_stream(
        self,
        db: Session,
        query: str,
        response_mode: str,
        current_user: CurrentUser,
        conversation_id: Optional[uuid.UUID] = None,
    ) -> Generator[LLMChunk, None, None]:
        """
        Executes query routing, retrieves scoped records, compiles prompt,
        yields streaming token LLMChunks, and safely persists final AI response.
        """
        # If conversation_id is not provided, create a default one
        if not conversation_id:
            convo = self.memory_service.create_conversation(
                db=db,
                title="New Chat Session",
                model_name=AIModel.LLAMA,
                workspace_id=current_user.workspace_id,
                organization_id=current_user.organization_id,
                user_id=current_user.id,
            )
            conversation_id = convo.id
            db.commit()

        # 1. Save user query immediately to protect history
        user_tokens = TokenCounter.estimate_tokens(query)
        self.memory_service.save_user_message(
            db=db,
            conversation_id=conversation_id,
            message=query,
            tokens_used=user_tokens,
        )
        db.commit()

        # 2. Call MultiAgentRouter to classify intent and select virtual agent
        routing_decision = self.agent_router.route_query(
            user_query=query,
            tenant_id=str(current_user.organization_id),
            response_mode=response_mode,
            db=db,
            workspace_id=current_user.workspace_id,
            organization_id=current_user.organization_id,
        )

        agent_role = routing_decision["role"]

        # Handle SecurityAgent or FactCheckAgent blocks (immediate block returned as single chunk)
        if agent_role in ("SecurityAgent", "FactCheckAgent"):
            ai_response = routing_decision.get(
                "response", "Request blocked by security rules."
            )
            ai_tokens = TokenCounter.estimate_tokens(ai_response)
            self.memory_service.save_ai_message(
                db=db,
                conversation_id=conversation_id,
                message=ai_response,
                tokens_used=ai_tokens,
                response_time_ms=0,
            )
            db.commit()
            yield LLMChunk(
                text=ai_response,
                finished=True,
                finish_reason="stop",
                model="rule_guard",
                provider="system",
                prompt_tokens=user_tokens,
                completion_tokens=ai_tokens,
                total_tokens=user_tokens + ai_tokens,
                conversation_id=str(conversation_id),
            )
            return

        # 3. Render prompt from PromptTemplateEngine (grounded RAG database context)
        analysis_type = routing_decision.get("analysis_type", "general")
        context_data = routing_decision.get("context", "")

        rendered_prompt = self.prompt_engine.render_prompt(
            analysis_type=analysis_type,
            input_data=context_data,
        )

        if not rendered_prompt:
            rendered_prompt = f"Agent Context:\n{context_data}"

        # 4. Fetch memory states from database
        conversation = self.memory_service.get_conversation_by_id(
            db=db,
            conversation_id=conversation_id,
            workspace_id=current_user.workspace_id,
            organization_id=current_user.organization_id,
        )
        summary = conversation.summary if conversation else None

        message_repo = MessageRepository(db)
        recent_messages = message_repo.get_recent_messages(
            conversation_id, limit=settings.MEMORY_RECENT_MESSAGES + 1
        )
        if (
            recent_messages
            and recent_messages[-1].message == query
            and recent_messages[-1].sender_type == AIMessageSender.USER
        ):
            recent_messages = recent_messages[:-1]

        # 5. Compile prompt messages list using pure StructuredPromptBuilder
        messages = StructuredPromptBuilder.build_messages(
            system_prompt=rendered_prompt,
            summary=summary,
            recent_messages=recent_messages,
            rag_context=context_data,
            query=query,
        )

        # 6. Stream tokens and handle client cancellations safely
        from asyncio import CancelledError

        start_time = time.time()
        full_ai_response = []

        try:
            for chunk in self.llm_provider.stream(messages):
                full_ai_response.append(chunk.text)
                # Inject prompt metadata into the chunk for the client
                chunk.prompt_tokens = user_tokens
                chunk.model = self.llm_provider.model
                chunk.provider = "ollama"
                chunk.conversation_id = str(conversation_id)

                yield chunk
        except GeneratorExit:
            logger.debug("Inference stream generator closed (Client disconnect).")
        except CancelledError:
            logger.debug("Inference stream task cancelled (Client disconnect).")
            raise
        finally:
            # Safe Persistence: Commit whatever was successfully generated in a fresh DB session
            accumulated_text = "".join(full_ai_response)
            if accumulated_text:
                latency_ms = int((time.time() - start_time) * 1000)
                ai_tokens = TokenCounter.estimate_tokens(accumulated_text)

                fresh_db = SessionLocal()
                try:
                    convo_repo = ConversationRepository(fresh_db)
                    msg_repo = MessageRepository(fresh_db)

                    msg_repo.create_message(
                        conversation_id=conversation_id,
                        sender_type=AIMessageSender.AI,
                        message=accumulated_text,
                        tokens_used=ai_tokens,
                        response_time_ms=latency_ms,
                    )

                    db_convo = convo_repo.get_conversation_by_id_simple(conversation_id)
                    if db_convo:
                        convo_repo.update_metrics(
                            db_convo,
                            ai_tokens,
                            datetime.datetime.now(datetime.timezone.utc),
                        )
                        fresh_db.commit()
                        logger.info(
                            "Ollama stream completion success",
                            extra={
                                "provider": "ollama",
                                "model": self.llm_provider.model,
                                "prompt_tokens": user_tokens,
                                "completion_tokens": ai_tokens,
                                "total_tokens": user_tokens + ai_tokens,
                                "latency_ms": latency_ms,
                            },
                        )
                except Exception as db_err:
                    logger.error(
                        f"Failed to persist streamed AI response to database: {str(db_err)}"
                    )
                finally:
                    fresh_db.close()

    def get_llm_health(self) -> dict:
        """
        Retrieves connectivity and status metadata for the configured LLM provider.
        """
        health = self.llm_provider.health_check()
        return {
            "reachable": health.reachable,
            "model": health.model,
            "latency_ms": health.latency_ms,
            "version": health.version,
        }
