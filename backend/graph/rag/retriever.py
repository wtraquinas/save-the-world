"""
ChromaDB vector store singleton.
Embeddings run locally via OpenAI text-embedding-3-small.
The collection persists to data/chroma_db/ — built once, reused forever.
"""
import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

PERSIST_DIR = str(Path(__file__).parent.parent.parent / "data" / "chroma_db")
COLLECTION   = "un_knowledge_base"

_vectorstore = None   # module-level singleton


def get_vectorstore(chunks=None):
    """
    Returns the ChromaDB vectorstore.
    If it doesn't exist yet, builds it from `chunks`.
    If it already exists, loads from disk (no re-embedding).
    """
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",   # cheapest, ~$0.00002 / 1K tokens
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    db_path = Path(PERSIST_DIR)
    if (db_path / "chroma.sqlite3").exists():
        print("[RAG] 📂 Loading existing ChromaDB from disk...")
        _vectorstore = Chroma(
            collection_name=COLLECTION,
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings,
        )
    elif chunks:
        print(f"[RAG] 🔨 Building ChromaDB from {len(chunks)} chunks...")
        _vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION,
            persist_directory=PERSIST_DIR,
        )
        print("[RAG] ✅ ChromaDB built and persisted to disk")
    else:
        raise RuntimeError(
            "ChromaDB not found and no chunks provided. "
            "Run: python scripts/build_vectorstore.py"
        )

    return _vectorstore


def retrieve(query: str, k: int = 3) -> list[str]:
    """
    Retrieve top-k relevant chunks for a query.
    Returns list of text strings ready to inject into a prompt.
    """
    vs = get_vectorstore()
    docs = vs.similarity_search(query, k=k)
    return [d.page_content for d in docs]