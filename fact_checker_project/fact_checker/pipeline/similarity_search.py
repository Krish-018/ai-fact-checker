import numpy as np
import pandas as pd
from fact_checker.models.embedding_engine import generate_embeddings


class FactChecker:
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.claims = self.data["claim"].tolist()
        self.labels = [str(label) for label in self.data["label"]]
        
        print(f"📚 Loaded {len(self.claims)} verified facts")
        
        # Generate embeddings for all claims
        self.claim_embeddings = generate_embeddings(self.claims)
        
    def search(self, query, top_k=1, threshold=0.5):
        """
        Simple cosine similarity search (no FAISS needed)
        """
        # Generate query embedding
        query_embedding = generate_embeddings([query])[0]
        
        # Calculate cosine similarity with all claims
        similarities = []
        for i, claim_emb in enumerate(self.claim_embeddings):
            # Cosine similarity
            dot = np.dot(query_embedding, claim_emb)
            norm1 = np.linalg.norm(query_embedding)
            norm2 = np.linalg.norm(claim_emb)
            if norm1 > 0 and norm2 > 0:
                sim = dot / (norm1 * norm2)
            else:
                sim = 0
            similarities.append((sim, i))
        
        # Sort by similarity (higher is better)
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        best_score = similarities[0][0]
        best_idx = similarities[0][1]
        
        if best_score < threshold:
            return {
                "claim": "No reliable match found",
                "label": "Unknown",
                "score": best_score,
                "note": "Below confidence threshold"
            }
        
        return {
            "claim": self.claims[best_idx],
            "label": self.labels[best_idx],
            "score": best_score
        }