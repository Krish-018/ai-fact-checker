import faiss
import numpy as np
import pandas as pd
import time
from fact_checker.models.embedding_engine import generate_embeddings


class FactChecker:
    def __init__(self, csv_path):
        # Load verified claims
        self.data = pd.read_csv(csv_path)
        self.claims = self.data["claim"].tolist()
        
        print(f"📚 Loaded {len(self.claims)} verified facts")

        # Generate embeddings
        start_time = time.time()
        self.claim_embeddings = generate_embeddings(self.claims)
        self.claim_embeddings = np.array(self.claim_embeddings).astype("float32")
        embed_time = round((time.time() - start_time) * 1000, 2)
        print(f"⚡ Embedding generation: {embed_time}ms")

        # Normalize for cosine similarity
        faiss.normalize_L2(self.claim_embeddings)

        # Create FAISS index (Inner Product = cosine similarity)
        dimension = self.claim_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.claim_embeddings)
        
        print(f"✅ FAISS index created with {self.index.ntotal} vectors")

    def search(self, query, top_k=1, threshold=0.5):
        """
        Search for similar claims
        Returns: dict with claim, label, score, and metrics
        score range: 0-1, higher = more similar
        """
        
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = generate_embeddings([query])
        query_embedding = np.array(query_embedding).astype("float32")
        embed_time = round((time.time() - start_time) * 1000, 2)
        
        # Normalize query
        faiss.normalize_L2(query_embedding)

        # Search
        search_start = time.time()
        similarities, indices = self.index.search(query_embedding, top_k)
        search_time = round((time.time() - search_start) * 1000, 2)
        
        best_score = float(similarities[0][0])
        best_idx = indices[0][0]
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        # Check if above threshold
        if best_score < threshold:
            return {
                "claim": "No reliable match found",
                "label": "Unknown",
                "score": best_score,
                "note": "Below confidence threshold",
                "metrics": {
                    "embedding_time_ms": embed_time,
                    "search_time_ms": search_time,
                    "total_time_ms": total_time,
                    "threshold": threshold
                }
            }
        
        return {
            "claim": self.claims[best_idx],
            "label": str(self.data.iloc[best_idx]["label"]),
            "score": best_score,
            "metrics": {
                "embedding_time_ms": embed_time,
                "search_time_ms": search_time,
                "total_time_ms": total_time,
                "threshold": threshold,
                "matched_index": int(best_idx)
            }
        }
    
    def search_with_details(self, query, top_k=3):
        """Get top K matches with details and metrics"""
        
        start_time = time.time()
        
        query_embedding = generate_embeddings([query])
        query_embedding = np.array(query_embedding).astype("float32")
        faiss.normalize_L2(query_embedding)
        
        similarities, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in range(top_k):
            if indices[0][i] != -1:
                results.append({
                    "claim": self.claims[indices[0][i]],
                    "label": str(self.data.iloc[indices[0][i]]["label"]),
                    "score": float(similarities[0][i]),
                })
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "results": results,
            "metrics": {
                "total_time_ms": total_time,
                "top_k": top_k
            }
        }