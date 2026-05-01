"""Document loading and chunking utilities for the RAG pipeline.

Supports plain-text (.txt), Markdown (.md), and PDF (.pdf) documents.

Document types
--------------
Every chunk carries a ``doc_type`` field in its metadata.  The corpus is
expected to be organised into subdirectories that map to one of the four
domain-specific types used by the retriever:

    data/corpus/
    ├── visa/          → doc_type = "visa"
    ├── programs/      → doc_type = "program"
    ├── admissions/    → doc_type = "admissions"
    └── careers/       → doc_type = "career"

Files placed directly under ``data/corpus/`` receive ``doc_type = "general"``.

Chunking strategy
-----------------
Uses recursive character splitting that tries separators in order
(paragraphs → lines → sentences → words → characters) so chunks respect
natural text boundaries.  Consecutive chunks share an overlap window for
context continuity.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import pypdf

# ---------------------------------------------------------------------------
# Document-type constants
# ---------------------------------------------------------------------------

DocType = Literal["visa", "program", "admissions", "career", "general"]

# Maps the name of a corpus subdirectory (lowercased) to a DocType value.
# Supports both singular and plural spellings.
DIR_TO_DOCTYPE: dict[str, str] = {
    "visa": "visa",
    "visas": "visa",
    "program": "program",
    "programs": "program",
    "admissions": "admissions",
    "admission": "admissions",
    "career": "career",
    "careers": "career",
}

SUPPORTED_EXTENSIONS: set[str] = {".txt", ".md", ".pdf"}

# Separators ordered from coarsest to finest.
_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " "]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class DocumentChunk:
    """A single chunk of text together with its provenance metadata."""

    text: str
    metadata: dict[str, str | int] = field(default_factory=dict)

    @property
    def doc_type(self) -> str:
        """Domain category this chunk belongs to."""
        return str(self.metadata.get("doc_type", "general"))

    @property
    def chunk_id(self) -> str:
        """Deterministic 16-hex-char ID derived from source path and index."""
        source = self.metadata.get("source", "")
        index = self.metadata.get("chunk_index", 0)
        return hashlib.sha256(f"{source}::{index}".encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

def load_document(path: str | Path) -> tuple[str, dict[str, str]]:
    """Read a document and return ``(text, metadata)``.

    Raises
    ------
    FileNotFoundError
        When *path* does not exist on disk.
    ValueError
        When the file extension is not in ``SUPPORTED_EXTENSIONS``.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: '{path.suffix}'. "
            f"Supported extensions: {SUPPORTED_EXTENSIONS}"
        )

    metadata: dict[str, str] = {"source": str(path), "filename": path.name}

    if path.suffix.lower() == ".pdf":
        text = _load_pdf(path)
    else:
        text = path.read_text(encoding="utf-8")

    return text, metadata


def _load_pdf(path: Path) -> str:
    """Extract and concatenate text from every page of a PDF."""
    reader = pypdf.PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)
    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[str]:
    """Split *text* into overlapping chunks using recursive character splitting.

    Parameters
    ----------
    text:
        Source text to split.
    chunk_size:
        Target maximum number of characters per chunk.
    chunk_overlap:
        Characters of context carried from the end of one chunk to the
        start of the next (aids retrieval at boundary regions).

    Returns
    -------
    list[str]
        Non-empty, stripped chunk strings.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    # Phase 1 – non-overlapping boundary-aware split.
    chunks = _recursive_chunk(text, chunk_size, _SEPARATORS)

    # Phase 2 – inject overlap between consecutive chunks.
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-chunk_overlap:]
            # Advance to the nearest word boundary so we don't start mid-word.
            space_idx = prev_tail.find(" ")
            if 0 <= space_idx < len(prev_tail) - 1:
                prev_tail = prev_tail[space_idx + 1 :]
            overlapped.append(prev_tail + " " + chunks[i])
        chunks = overlapped

    return [c.strip() for c in chunks if c.strip()]


def _recursive_chunk(
    text: str,
    max_size: int,
    separators: list[str],
) -> list[str]:
    """Recursively split *text* into pieces each ≤ *max_size* characters."""
    if len(text) <= max_size:
        return [text]

    for i, sep in enumerate(separators):
        if sep not in text:
            continue

        parts = text.split(sep)
        chunks: list[str] = []
        current = ""

        for part in parts:
            candidate = (current + sep + part) if current else part

            if len(candidate) <= max_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(part) > max_size:
                    # Single part still too large – recurse with finer sep.
                    chunks.extend(
                        _recursive_chunk(part, max_size, separators[i + 1 :])
                    )
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        return chunks

    # Last resort: hard character split.
    return [text[j : j + max_size] for j in range(0, len(text), max_size)]


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------

def chunk_document(
    path: str | Path,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    doc_type: str = "general",
) -> list[DocumentChunk]:
    """Load a single document and return its chunks with metadata.

    Parameters
    ----------
    path:
        Path to a .txt, .md, or .pdf file.
    chunk_size:
        Maximum characters per chunk.
    chunk_overlap:
        Overlap characters between consecutive chunks.
    doc_type:
        Domain category for this document (``"visa"``, ``"program"``,
        ``"admissions"``, ``"career"``, or ``"general"``).
    """
    text, metadata = load_document(path)
    raw_chunks = chunk_text(text, chunk_size, chunk_overlap)

    return [
        DocumentChunk(
            text=chunk,
            metadata={
                **metadata,
                "doc_type": doc_type,
                "chunk_index": i,
                "total_chunks": len(raw_chunks),
            },
        )
        for i, chunk in enumerate(raw_chunks)
    ]


def chunk_directory(
    dir_path: str | Path,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    doc_type: str = "general",
) -> list[DocumentChunk]:
    """Chunk every supported file under *dir_path* with a fixed *doc_type*.

    Recurses into subdirectories.  All files receive the same *doc_type*;
    use :func:`chunk_corpus` when you need automatic per-subdirectory type
    inference.
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    all_chunks: list[DocumentChunk] = []
    for ext in sorted(SUPPORTED_EXTENSIONS):
        for file_path in sorted(dir_path.rglob(f"*{ext}")):
            all_chunks.extend(
                chunk_document(file_path, chunk_size, chunk_overlap, doc_type=doc_type)
            )

    return all_chunks


def chunk_corpus(
    corpus_dir: str | Path,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[DocumentChunk]:
    """Chunk a corpus whose subdirectories encode document type.

    Expected layout::

        corpus/
        ├── visa/          → doc_type = "visa"
        ├── programs/      → doc_type = "program"
        ├── admissions/    → doc_type = "admissions"
        ├── careers/       → doc_type = "career"
        └── *.txt|md|pdf   → doc_type = "general"   (root-level files)

    Subdirectory names are matched case-insensitively against
    ``DIR_TO_DOCTYPE``.  Unknown subdirectory names fall back to
    ``"general"``.
    """
    corpus_dir = Path(corpus_dir)
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    all_chunks: list[DocumentChunk] = []

    # 1. Typed subdirectories
    for subdir in sorted(p for p in corpus_dir.iterdir() if p.is_dir()):
        inferred_type = DIR_TO_DOCTYPE.get(subdir.name.lower(), "general")
        all_chunks.extend(
            chunk_directory(subdir, chunk_size, chunk_overlap, doc_type=inferred_type)
        )

    # 2. Root-level files (no subdirectory context → general)
    for ext in sorted(SUPPORTED_EXTENSIONS):
        for file_path in sorted(corpus_dir.glob(f"*{ext}")):
            all_chunks.extend(
                chunk_document(file_path, chunk_size, chunk_overlap, doc_type="general")
            )

    return all_chunks
