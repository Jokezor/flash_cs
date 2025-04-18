# Add a real embedding model here
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_text(text):
    """
    Dummy embedding: in a full solution, call a model (e.g., via sentence-transformers)
    and return a numeric vector.
    """
    embedding = model.encode(text)
    return embedding

if __name__ == '__main__':
    emb = embed_text("Sample text for embedding")
    print("Embedding:", emb) 