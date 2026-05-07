"""
One-time script to build the RAG vector index from visa documents.

Usage:
    cd /workspaces/gen_ai-project
    python backend/build_rag_index.py

Creates indices/ directory with vectors.npy, metadata.json, index.json.
Requires OPENAI_API_KEY in backend/.env.
"""
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env")

from src.rag.chunker import chunk_directory
from src.rag.embeddings import build_index, save_index

VISA_DOCS_SOURCE = PROJECT_ROOT / "data" / "visa docs"
CORPUS_VISA_DIR = PROJECT_ROOT / "data" / "corpus" / "visa"
OUTPUT_DIR = PROJECT_ROOT / "indices"


def setup_corpus():
    """Copy visa PDFs into the corpus/visa/ structure the RAG pipeline expects."""
    CORPUS_VISA_DIR.mkdir(parents=True, exist_ok=True)
    if not VISA_DOCS_SOURCE.exists():
        print(f"Warning: source directory not found: {VISA_DOCS_SOURCE}")
        return

    for pdf in VISA_DOCS_SOURCE.glob("*.pdf"):
        dest = CORPUS_VISA_DIR / pdf.name
        if not dest.exists():
            shutil.copy2(pdf, dest)
            print(f"  Copied: {pdf.name}")


def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("Error: OPENAI_API_KEY not set. Add it to backend/.env")
        return

    print("Setting up corpus structure...")
    setup_corpus()

    if not CORPUS_VISA_DIR.exists() or not list(CORPUS_VISA_DIR.glob("*.pdf")):
        print(f"Error: No PDFs found in {CORPUS_VISA_DIR}")
        return

    print(f"\nChunking visa documents from: {CORPUS_VISA_DIR}")
    chunks = chunk_directory(
        CORPUS_VISA_DIR, chunk_size=512, chunk_overlap=64, doc_type="visa"
    )
    print(f"  Total chunks: {len(chunks)}")

    if not chunks:
        print("No chunks generated.")
        return

    print("Generating embeddings (this may take a minute)...")
    vectors, metadata = build_index(chunks, api_key)

    print(f"Saving index to: {OUTPUT_DIR}")
    save_index(vectors, metadata, OUTPUT_DIR)

    print(f"\nDone! {len(metadata)} vectors saved to {OUTPUT_DIR}/")
    print("The visa agent will now use RAG retrieval automatically.")


if __name__ == "__main__":
    main()
