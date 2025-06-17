# vector_db.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class VectorDatabase:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
    
    def build_index(self, documents: List[Dict]):
        """Build FAISS index from documents."""
        self.documents = documents
        texts = [doc["content"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create and train index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for similar documents."""
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:  # -1 indicates no result
                doc = self.documents[idx]
                results.append({
                    "content": doc["content"],
                    "source_url": doc["source_url"],
                    "score": float(1 / (1 + distance))  # Convert distance to similarity score
                })
        
        return results
    
    def save(self, filepath: str):
        """Save index and documents."""
        faiss.write_index(self.index, f"{filepath}.index")
        with open(f"{filepath}.docs.json", 'w') as f:
            json.dump(self.documents, f)
    
    def load(self, filepath: str):
        """Load index and documents."""
        self.index = faiss.read_index(f"{filepath}.index")
        with open(f"{filepath}.docs.json", 'r') as f:
            self.documents = json.load(f)

# Example usage
if __name__ == "__main__":
    # Load processed data
    with open("processed_data.json", 'r') as f:
        documents = json.load(f)
    
    # Build and save index
    db = VectorDatabase()
    db.build_index(documents)
    db.save("tds_vector_db")