"""RAG (Retrieval-Augmented Generation) pipeline for the AI Consultant.

Corpus layout expected by the ingestion pipeline::

    data/corpus/
    ├── visa/          → doc_type = "visa"
    ├── programs/      → doc_type = "program"
    ├── admissions/    → doc_type = "admissions"
    ├── careers/       → doc_type = "career"
    └── *.txt|md|pdf   → doc_type = "general"

Quick start::

    # Ingest
    from rag.chunker import chunk_corpus
    from rag.embeddings import build_index, save_index

    chunks = chunk_corpus("data/corpus")
    vectors, metadata = build_index(chunks, api_key="sk-...")
    save_index(vectors, metadata, "indices")

    # Retrieve
    from rag.retriever import Retriever

    r = Retriever("indices", api_key="sk-...")
    r.retrieve_visa("F-1 visa work authorization rules")
    r.retrieve_programs("top AI master's programs in Europe")
    r.retrieve_admissions("GRE requirements for US universities")
    r.retrieve_careers("data science salaries by country")
"""

from .chunker import (
    DIR_TO_DOCTYPE,
    DocType,
    DocumentChunk,
    chunk_corpus,
    chunk_directory,
    chunk_document,
)
from .embeddings import build_index, load_index, save_index
from .retriever import RetrievalResult, Retriever

__all__ = [
    # chunker
    "DocType",
    "DIR_TO_DOCTYPE",
    "DocumentChunk",
    "chunk_document",
    "chunk_directory",
    "chunk_corpus",
    # embeddings
    "build_index",
    "save_index",
    "load_index",
    # retriever
    "Retriever",
    "RetrievalResult",
]
