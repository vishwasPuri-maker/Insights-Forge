import os

class MockVectorDB:
    def search(self, query: str, top_k: int = 3):
        print(f"Searching vector space for: {query}")
        return [
            {"score": 0.92, "content": "Revenue in Q3 dropped by 4% due to supply chain delays."},
            {"score": 0.85, "content": "Customer churn increased in the retail sector."},
            {"score": 0.77, "content": "GMROI for winter apparel remains high."}
        ]

class RAGPipeline:
    def __init__(self):
        self.db = MockVectorDB()
        try:
            from app.core.rag.retriever import Retriever
            self.retriever = Retriever()
        except Exception as e:
            print(f"RAG RETRIEVER INITIALIZATION ERROR: {str(e)}")
            self.retriever = None

    def retrieve_context(self, user_query: str, db=None, workspace_id=None, organization_id=None):
        if self.retriever is not None and workspace_id is not None and organization_id is not None:
            try:
                import uuid
                org_uuid = uuid.UUID(str(organization_id))
                ws_uuid = uuid.UUID(str(workspace_id))
                context = self.retriever.retrieve_and_build_context(
                    query=user_query,
                    organization_id=org_uuid,
                    workspace_id=ws_uuid
                )
                if context:
                    return context
            except Exception as e:
                print(f"RAG PRODUCTION RETRIEVAL ERROR: {str(e)}")

        # Fallback to the original mock behavior
        results = self.db.search(user_query)
        context = "\n".join([r['content'] for r in results])
        return context
