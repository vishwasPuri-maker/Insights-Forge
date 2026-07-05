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

    def retrieve_context(self, user_query: str):
        results = self.db.search(user_query)
        context = "\n".join([r['content'] for r in results])
        return context
