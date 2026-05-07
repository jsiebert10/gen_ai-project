"""Singleton RAG retriever service for the backend agents."""
from __future__ import annotations

import sys
from pathlib import Path

from config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

INDEX_DIR = PROJECT_ROOT / "indices"

_retriever = None


def get_retriever():
    """Return a lazily-initialized Retriever singleton (or None if unavailable)."""
    global _retriever

    if _retriever is not None:
        return _retriever

    if not INDEX_DIR.exists() or not (INDEX_DIR / "vectors.npy").exists():
        return None

    api_key = settings.openai_api_key
    if not api_key:
        return None

    try:
        from src.rag.retriever import Retriever
        _retriever = Retriever(str(INDEX_DIR), api_key=api_key)
        return _retriever
    except Exception:
        return None


def retrieve_visa_context(query: str, top_k: int = 8) -> str:
    """Retrieve and format visa document chunks as a context string."""
    retriever = get_retriever()
    if retriever is None:
        return ""

    try:
        results = retriever.retrieve_visa(query, top_k=top_k)
        if not results:
            return ""

        parts = []
        for i, hit in enumerate(results, 1):
            source = hit.metadata.get("filename", "unknown")
            parts.append(f"[Document {i} — {source} (score: {hit.score:.2f})]\n{hit.text}")
        return "\n\n---\n\n".join(parts)
    except Exception:
        return ""
