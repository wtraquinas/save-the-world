"""
Run once to build the ChromaDB vector store:
    cd backend
    python scripts/build_vectorstore.py

This downloads UN PDFs, chunks them, embeds them via OpenAI,
and persists the result to data/chroma_db/.
Commit data/chroma_db/ to git so Render never needs to rebuild it.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from graph.rag.loader import download_docs, load_chunks
from graph.rag.retriever import get_vectorstore

if __name__ == "__main__":
    print("=== Building UN Knowledge Base Vector Store ===\n")

    # Step 1: Download PDFs
    download_docs()

    # Step 2: Chunk all docs
    chunks = load_chunks()

    # Step 3: Embed + persist to ChromaDB
    vs = get_vectorstore(chunks=chunks)

    # Step 4: Quick sanity check
    from graph.rag.retriever import retrieve
    test_results = retrieve("food insecurity famine drought solutions")
    print(f"\n[TEST] Query: 'food insecurity famine drought solutions'")
    print(f"[TEST] Top result preview: {test_results[0][:200]}...")
    print("\n✅ Vector store ready. Commit data/chroma_db/ to git.")