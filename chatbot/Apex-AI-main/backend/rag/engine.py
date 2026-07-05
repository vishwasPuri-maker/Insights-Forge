import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

class RAGEngine:
    def __init__(self, db_dir="../vector_db"):
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(name="apex_analytics_docs")
        
    def ingest_text(self, text_id: str, text: str):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)
        
        self.collection.add(
            documents=chunks,
            ids=[f"{text_id}_chunk_{i}" for i in range(len(chunks))]
        )
        print(f"Ingested {len(chunks)} chunks for {text_id}")
        
    def retrieve(self, query: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
