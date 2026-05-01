#!/usr/bin/env python
"""CLI script to ingest corpus documents into the RAG vector store.

Pipeline
--------
1. Chunk  – load documents from the corpus and split into text chunks.
            The corpus is expected to use the typed subdirectory layout:

            data/corpus/
            ├── visa/          → doc_type = "visa"
            ├── programs/      → doc_type = "program"
            ├── admissions/    → doc_type = "admissions"
            ├── careers/       → doc_type = "career"
            └── *.txt|md|pdf   → doc_type = "general"

2. Embed  – call the OpenAI Embeddings API to generate vectors.
3. Save   – write the L2-normalised vector matrix and metadata to disk.

Usage examples
--------------
    # Standard typed-corpus ingest (default)
    python scripts/ingest.py data/corpus

    # Custom output directory and chunk settings
    python scripts/ingest.py data/corpus \\
        --output-dir indices \\
        --chunk-size 800 --chunk-overlap 100

    # Flat directory (no subdirectory type inference)
    python scripts/ingest.py my_docs/ --flat

    # API key inline (or set OPENAI_API_KEY env var)
    python scripts/ingest.py data/corpus --api-key sk-...
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure src/ is on sys.path so the ``rag`` package is importable
# regardless of where the script is invoked from.
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from rag.chunker import DIR_TO_DOCTYPE, chunk_corpus, chunk_directory  # noqa: E402
from rag.embeddings import (  # noqa: E402
    DEFAULT_EMBEDDING_MODEL,
    build_index,
    save_index,
)


def _resolve_api_key(cli_value: str | None) -> str:
    key = cli_value or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        print(
            "Error: provide --api-key or set the OPENAI_API_KEY env var.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def _print_type_summary(chunks: list) -> None:
    """Print a breakdown of how many chunks were produced per doc_type."""
    from collections import Counter
    counts: Counter = Counter(c.metadata.get("doc_type", "general") for c in chunks)
    for dt in sorted(counts):
        print(f"        {dt:<15} {counts[dt]:>5} chunks")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Ingest corpus documents into the RAG vector store.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "corpus_dir",
        help=(
            "Corpus root directory.  Expected subdirectories: "
            + ", ".join(sorted(DIR_TO_DOCTYPE.keys()))
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="indices",
        help="Directory where the vector index will be saved (default: indices).",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Maximum characters per chunk (default: 512).",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=64,
        help="Overlap characters between consecutive chunks (default: 64).",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help=f"OpenAI embedding model name (default: {DEFAULT_EMBEDDING_MODEL}).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenAI API key. Falls back to the OPENAI_API_KEY env var.",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help=(
            "Treat corpus_dir as a flat directory of files (no subdirectory "
            "type inference).  All chunks receive doc_type='general'."
        ),
    )

    args = parser.parse_args(argv)

    api_key = _resolve_api_key(args.api_key)

    corpus_dir = Path(args.corpus_dir)
    if not corpus_dir.is_dir():
        print(f"Error: corpus directory not found: {corpus_dir}", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 1 – Chunk
    # ------------------------------------------------------------------
    if args.flat:
        print(f"[1/3] Chunking files (flat) in {corpus_dir} ...")
        chunks = chunk_directory(
            corpus_dir, args.chunk_size, args.chunk_overlap, doc_type="general"
        )
    else:
        print(f"[1/3] Chunking typed corpus in {corpus_dir} ...")
        chunks = chunk_corpus(corpus_dir, args.chunk_size, args.chunk_overlap)

    print(f"      {len(chunks)} total chunks created.")
    if chunks:
        _print_type_summary(chunks)

    if not chunks:
        print("      No supported documents found. Nothing to do.")
        return

    # ------------------------------------------------------------------
    # Step 2 – Embed
    # ------------------------------------------------------------------
    print(f"[2/3] Generating embeddings with {args.embedding_model} ...")
    vectors, metadata = build_index(chunks, api_key, args.embedding_model)
    print(f"      {vectors.shape[0]} vectors of dimension {vectors.shape[1]}.")

    # ------------------------------------------------------------------
    # Step 3 – Save
    # ------------------------------------------------------------------
    output_dir = Path(args.output_dir)
    print(f"[3/3] Saving index to {output_dir} ...")
    save_index(vectors, metadata, output_dir, args.embedding_model)
    print("      Done.")
    print()
    print(
        f"  Index ready.  Load with:\n"
        f"    from rag.retriever import Retriever\n"
        f"    r = Retriever('{output_dir}', api_key=...)\n"
        f"    r.retrieve_visa(...)\n"
        f"    r.retrieve_programs(...)\n"
        f"    r.retrieve_admissions(...)\n"
        f"    r.retrieve_careers(...)"
    )


if __name__ == "__main__":
    main()
