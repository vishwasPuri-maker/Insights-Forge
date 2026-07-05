# Walkthrough — Milestone 4E, 4G & 4H: Memory, Decisions, and Vector Architecture

This walkthrough summarizes the changes made to introduce:
1. A production-grade, tenant-isolated, PostgreSQL-backed conversation memory system (4E).
2. A decoupled, highly validated Decision Intelligence engine utilizing metadata schema separation (4G).
3. An enterprise-grade, provider-agnostic Vector Database and Embedding Pipeline supporting pgvector and Chroma alongside Ollama/OpenAI (4H).

---

## 1. Database Schema Updates
- **AIConversation DB Model** (`app/models/ai_conversation.py`):
  - `summary`: Stores the consolidated conversation summary.
  - `total_messages`: Tracks message count on this thread.
  - `total_tokens`: Tracks cumulative token count (estimated as `len(text) // 4`).
  - `last_message_at`: Indexes the last activity timestamp.
  - `last_summary_at`: Tracks the timestamp of the last generated summary.
- **AIRecommendation DB Model** (`app/models/ai_recommendation.py`):
  - `metadata_json`: Added a dedicated JSON column compiled as `JSONB` on PostgreSQL (with variants for backend-agnostic support on SQLite). This segregates human-readable recommendation text from audit trails, sources, and KPIs.
- **VectorChunk DB Model** (`app/models/vector_chunk.py`):
  - Created a dedicated `vector_chunks` table to house isolated document chunk texts, float array embeddings (using the `Vector(384)` type), and foreign key references to datasets and records.

An Alembic migration was successfully generated and applied for memory and vector columns.

---

## 2. Decoupled Repositories (`app/repositories/`)
- **`ConversationRepository`** (`conversation_repository.py`): Handles creating, listing, updating metadata/metrics, soft-deletes, and aggregate statistics.
- **`MessageRepository`** (`message_repository.py`): Handles writing and loading chronological message exchanges.
- **`DecisionCardRepository`** (`decision_card_repository.py`): Re-engineered to remain thin and focused strictly on database access.

---

## 3. Modular Memory Service Components (`app/core/memory/`)
- **`ConversationMemoryService`** (`conversation_memory_service.py`): Maps API requests to repositories and context compilation without writing raw ORM code.
- **`ContextWindowManager`** (`context_window.py`): Standardizes context layouts.
- **`SummaryManager`** (`summary_manager.py`): Integrates with `LLMFactory.get_provider()` to asynchronously write titles and summaries.
- **`ConversationMaintenance`** (`conversation_maintenance.py`): Inspects conversation metrics and registers non-blocking title/summary background tasks.

---

## 4. Decision Intelligence Orchestration (`app/services/`)
- **`DecisionEngine`**: Builds prompts and handles LLM text generation with exponential backoff and retry capability.
- **`DecisionParser`**: Regex-based cleaning that recovers JSON from conversational wraps and balances truncated closing braces/brackets.
- **`DecisionValidator`**: Runs Pydantic validation on schema models and calculates derived confidence.
- **`DecisionService`**: Orchestrator linking context aggregation, generation, parsing, validation, persistence, and duplicate card checks.

---

## 5. Production Vector Database & Embedding Layer (Milestone 4H)
- **`PgVectorStore`**: Integrates pgvector using SQLAlchemy. Performs dynamic vector size validation, wipes duplicates on re-indexing, applies composite B-Tree filters for tenant isolation, and queries cosine distance similarity.
- **`ChromaVectorStore`**: Updated to standard interface methods (`upsert`, `delete`, `search`, `statistics`, `health_check`).
- **`OllamaEmbeddingProvider`**: Calls local Ollama endpoints. Automatically probes the model at startup to discover the embedding dimension size dynamically.
- **`OpenAIEmbeddingProvider`**: Implements OpenAI compatibility with sorted index mapping.
- **`Retriever`**: Refactored into a pure orchestration block: Coordinates `Embedding Provider` -> `Vector Store` -> `Reranker` -> `Context Builder`.

---

## 6. API Endpoint Integration
- **Chat Router (`app/api/v1/chat.py`)**:
  - `POST /chat/completions`: Chat execution endpoint.
  - `GET /chat/vector-store/health`: Exposes deep diagnostics, extension status, and collection statistics for embedding and vector database pipelines.
- **Decision Cards Router (`app/api/v1/decision_cards.py`)**:
  - `POST /decision-cards/generate`: Triggers automated decision card generation based on search context.

---

## 7. Verification Results

All **46 backend unit tests** ran and passed successfully:
```bash
tests\unit\test_conversation_memory.py ...........                       [ 23%]
tests\unit\test_decision_intelligence.py ...........                     [ 47%]
tests\unit\test_production_llm.py .........                              [ 67%]
tests\unit\test_provider_factory.py .                                    [ 69%]
tests\unit\test_rag_pipeline.py .......                                  [ 84%]
tests\unit\test_vector_pipeline.py .......                               [100%]

============================= 46 passed in 84.77s =============================
```

### Coverage Highlights:
- **test_embedding_factory_resolution**: Asserts factory returns appropriate models and dimension counts.
- **test_ollama_provider_embeddings**: Mocks Ollama endpoints, verifying sequential and batch responses.
- **test_openai_provider_embeddings**: Mocks OpenAI payloads, verifying correct index ordering.
- **test_pgvector_upsert_validation_and_inserts**: Verifies PgVectorStore validates dimensions, wipes duplicates, and commits chunks.
- **test_pgvector_search_isolation_and_scores**: Verifies cosine distance checks and tenant isolation.
- **test_pgvector_health_and_statistics**: Probes extension diagnostics and database row metrics.
- **test_duplicate_indexing_and_cleanup**: Confirms matching active queries reuse existing cards instead of inserting duplicate rows.
