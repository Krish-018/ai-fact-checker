from sentence_transformers import SentenceTransformer
import numpy as np

# Load small fast model
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(text_list):
    embeddings = model.encode(text_list)
    return np.array(embeddings)