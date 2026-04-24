"""Shared retrieval service for the RAG pipeline.

A single ``Retriever`` instance loads one vector index and serves all four
document domains through a unified interface:

    retriever.retrieve_visa(query)       → visa guidance chunks
    retriever.retrieve_programs(query)   → program description chunks
    retriever.retrieve_admissions(query) → admissions text chunks
    retriever.retrieve_careers(query)    → career description chunks
    retriever.retrieve(query)            → across all doc types

All domain methods delegate to the same :meth:`Retriever.retrieve` method and
share the same embedding call; only the cosine-score mask differs per domain.

Usage::

    from rag.retriever import Retriever

    retriever = Retriever("indices", api_key="sk-...")

    # Domain-specific retrieval
    visa_hits    = retriever.retrieve_visa("F-1 visa work authorization", top_k=5)
    program_hits = retriever.retrieve_programs("CS programs with AI focus", top_k=5)
    career_hits  = retriever.retrieve_careers("data science job outlook", top_k=3)

    # Cross-domain retrieval (no filter)
    all_hits = retriever.retrieve("living costs in Germany", top_k=8)

    for hit in program_hits:
        print(f"[{hit.score:.3f}] {hit.metadata['source']}\\n{hit.text[:120]}\\n")
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import openai

from .embeddings import DEFAULT_EMBEDDING_MODEL, load_index


@dataclass
class RetrievalResult:
    """A single retrieval hit."""

    text: str
    score: float
    metadata: dict


class Retriever:
    """Cosine-similarity retriever that serves all RAG document domains.

    The index is loaded once at initialisation.  Domain filtering uses
    precomputed boolean masks (one per ``doc_type``) applied to the score
    vector after the single matrix–vector dot product, so there is no
    redundant computation across domain methods.

    Parameters
    ----------
    index_dir:
        Directory produced by :func:`rag.embeddings.save_index`.
    api_key:
        OpenAI API key used to embed queries at inference time.
    """

    def __init__(self, index_dir: str | Path, api_key: str) -> None:
        self._vectors, self._metadata, self._index_info = load_index(index_dir)
        self._model: str = self._index_info.get(
            "embedding_model", DEFAULT_EMBEDDING_MODEL
        )
        self._client = openai.OpenAI(api_key=api_key)

        # Precompute one boolean mask per doc_type for O(N) filtered search.
        self._doc_type_masks: dict[str, np.ndarray] = {}
        all_types: set[str] = {
            str(m["doc_type"])
            for m in self._metadata
            if "doc_type" in m
        }
        for dt in all_types:
            self._doc_type_masks[dt] = np.array(
                [m.get("doc_type") == dt for m in self._metadata]
            )

    # -- public properties ---------------------------------------------------

    @property
    def num_chunks(self) -> int:
        """Total chunks stored in the index."""
        return len(self._metadata)

    @property
    def embedding_model(self) -> str:
        """Name of the OpenAI embedding model used to build this index."""
        return self._model

    @property
    def indexed_doc_types(self) -> list[str]:
        """Sorted list of doc_type values present in the index."""
        return sorted(self._doc_type_masks.keys())

    # -- core retrieval ------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_type: str | None = None,
    ) -> list[RetrievalResult]:
        """Return the *top_k* chunks most similar to *query*.

        Parameters
        ----------
        query:
            Natural-language question or search phrase.
        top_k:
            Maximum number of results to return.
        doc_type:
            When provided, restricts results to chunks with this domain tag
            (``"visa"``, ``"program"``, ``"admissions"``, ``"career"``, or
            ``"general"``).  Pass ``None`` to search across all types.

        Returns
        -------
        list[RetrievalResult]
            Ranked by descending cosine similarity.  May be shorter than
            *top_k* if the index contains fewer matching chunks.
        """
        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        query_vec = self._embed_query(query)

        # Full cosine similarity (dot product — vectors are L2-normalised).
        scores: np.ndarray = self._vectors @ query_vec

        # Apply domain mask if requested.
        if doc_type is not None:
            mask = self._doc_type_masks.get(doc_type)
            if mask is None or not mask.any():
                return []  # doc_type not present in this index
            scores = np.where(mask, scores, -np.inf)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results: list[RetrievalResult] = []
        for idx in top_indices:
            if not np.isfinite(scores[idx]):
                break  # reached masked-out region
            meta = self._metadata[idx]
            results.append(
                RetrievalResult(
                    text=meta["text"],
                    score=float(scores[idx]),
                    metadata={k: v for k, v in meta.items() if k != "text"},
                )
            )
        return results

    # -- domain-specific convenience methods ---------------------------------

    def retrieve_visa(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Retrieve chunks from visa guidance documents.

        Searches only chunks ingested from the ``corpus/visa/`` subdirectory
        (``doc_type="visa"``).
        """
        return self.retrieve(query, top_k=top_k, doc_type="visa")

    def retrieve_programs(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Retrieve chunks from program description documents.

        Searches only chunks ingested from the ``corpus/programs/``
        subdirectory (``doc_type="program"``).
        """
        return self.retrieve(query, top_k=top_k, doc_type="program")

    def retrieve_admissions(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Retrieve chunks from admissions text documents.

        Searches only chunks ingested from the ``corpus/admissions/``
        subdirectory (``doc_type="admissions"``).
        """
        return self.retrieve(query, top_k=top_k, doc_type="admissions")

    def retrieve_careers(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Retrieve chunks from career description documents.

        Searches only chunks ingested from the ``corpus/careers/``
        subdirectory (``doc_type="career"``).
        """
        return self.retrieve(query, top_k=top_k, doc_type="career")

    # -- internals -----------------------------------------------------------

    def _embed_query(self, text: str) -> np.ndarray:
        """Embed a single query string and return an L2-normalised vector."""
        response = self._client.embeddings.create(
            input=[text], model=self._model
        )
        vec = np.array(response.data[0].embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
