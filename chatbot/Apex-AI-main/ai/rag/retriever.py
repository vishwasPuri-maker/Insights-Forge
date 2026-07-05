import os
import json
from typing import List, Dict, Any

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class RAGRetriever:
    def __init__(self, index_path: str = None):
        self.index_path = index_path
        self.documents = []
        if FAISS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = None
            
    def index_document(self, file_path: str):
        if not FAISS_AVAILABLE:
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Simple chunking by paragraphs
        self.documents = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
        
        # Create embeddings and FAISS index
        embeddings = self.model.encode(self.documents)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not FAISS_AVAILABLE or self.index is None or not self.documents:
            return ["RAG System Not Initialized or FAISS missing."]
            
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
                
        return results
