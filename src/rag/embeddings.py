"""Embedding generation and vector-index persistence for the RAG pipeline.

Vectors are L2-normalised before storage so that cosine similarity can be
computed as a simple dot product at query time.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import openai

from .chunker import DocumentChunk

DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

# OpenAI permits up to 2 048 inputs per call; 100 keeps payloads small and
# avoids timeouts for long texts.
_BATCH_SIZE: int = 100


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def get_embeddings(
    texts: list[str],
    api_key: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> np.ndarray:
    """Call the OpenAI Embeddings API and return an ``(N, D)`` float32 array.

    Texts are sent in batches of ``_BATCH_SIZE``.  The returned array
    preserves the input ordering.
    """
    client = openai.OpenAI(api_key=api_key)
    all_embeddings: list[list[float]] = []

    for start in range(0, len(texts), _BATCH_SIZE):
        batch = texts[start : start + _BATCH_SIZE]
        response = client.embeddings.create(input=batch, model=model)
        # Sort by index so ordering matches the input list.
        sorted_data = sorted(response.data, key=lambda item: item.index)
        all_embeddings.extend([item.embedding for item in sorted_data])

    return np.array(all_embeddings, dtype=np.float32)


# ---------------------------------------------------------------------------
# Index building
# ---------------------------------------------------------------------------

def build_index(
    chunks: list[DocumentChunk],
    api_key: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> tuple[np.ndarray, list[dict]]:
    """Embed *chunks* and return the normalised vector matrix + metadata.

    Returns
    -------
    vectors : np.ndarray
        ``(N, D)`` float32 matrix of L2-normalised embeddings.
    metadata : list[dict]
        One dict per chunk containing ``text``, ``chunk_id``, and all
        fields from :pyattr:`DocumentChunk.metadata`.
    """
    if not chunks:
        raise ValueError("No chunks provided – nothing to embed.")

    texts = [c.text for c in chunks]
    vectors = get_embeddings(texts, api_key, model)

    # L2-normalise so dot-product == cosine similarity.
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    vectors = vectors / norms

    metadata = [
        {"text": c.text, "chunk_id": c.chunk_id, **c.metadata}
        for c in chunks
    ]

    return vectors, metadata


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_index(
    vectors: np.ndarray,
    metadata: list[dict],
    output_dir: str | Path,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> Path:
    """Save vectors, metadata, and config to *output_dir*.

    Creates three files:

    * ``vectors.npy``   – the ``(N, D)`` embedding matrix
    * ``metadata.json`` – chunk texts and provenance
    * ``index.json``    – model name, dimensions, vector count
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    np.save(output_dir / "vectors.npy", vectors)

    with open(output_dir / "metadata.json", "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False)

    index_info = {
        "embedding_model": model,
        "num_vectors": len(metadata),
        "dimensions": int(vectors.shape[1]),
    }
    with open(output_dir / "index.json", "w", encoding="utf-8") as fh:
        json.dump(index_info, fh, indent=2)

    return output_dir


def load_index(index_dir: str | Path) -> tuple[np.ndarray, list[dict], dict]:
    """Load a previously saved index.

    Returns
    -------
    vectors : np.ndarray
    metadata : list[dict]
    index_info : dict
    """
    index_dir = Path(index_dir)

    vectors = np.load(index_dir / "vectors.npy")

    with open(index_dir / "metadata.json", "r", encoding="utf-8") as fh:
        metadata = json.load(fh)

    with open(index_dir / "index.json", "r", encoding="utf-8") as fh:
        index_info = json.load(fh)

    return vectors, metadata, index_info
