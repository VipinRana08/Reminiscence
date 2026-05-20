import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_PATH, EMBEDDING_MODEL, MAX_CONTEXT_RESULTS

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="conversations")

# Load embedding model
embedder = SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str):
    """Convert text to embedding vector."""
    return embedder.encode(text).tolist()


def save_embedding(user_id, conversation_id, text):
    """Save a conversation embedding to ChromaDB."""
    embedding = embed_text(text)

    collection.add(
        ids=[str(conversation_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"user_id": user_id}]
    )


def search_similar(user_id, query_text, n_results=MAX_CONTEXT_RESULTS):
    """Search for semantically similar past conversations."""
    query_embedding = embed_text(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"user_id": user_id}
    )

    return results["documents"][0] if results["documents"] else []