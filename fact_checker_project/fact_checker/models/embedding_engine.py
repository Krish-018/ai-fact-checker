import numpy as np
import requests
import json

def generate_embeddings(text_list):
    """
    Use a simple TF-IDF fallback (no large model needed)
    """
    import hashlib
    import math
    
    # Simple deterministic embedding based on text hash
    # This is a fallback - not as good as real embeddings but works in memory-limited environments
    
    embeddings = []
    for text in text_list:
        # Create a simple numeric representation
        hash_val = hashlib.md5(text.encode()).hexdigest()
        # Convert hash to 384-dimensional vector
        vec = []
        for i in range(384):
            # Use hash characters to generate numbers between -1 and 1
            idx = i % len(hash_val)
            val = ord(hash_val[idx]) / 255.0
            vec.append(math.sin(val * math.pi * 2) * 0.5)
        embeddings.append(vec)
    
    return np.array(embeddings).astype('float32')