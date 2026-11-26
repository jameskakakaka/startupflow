"""Two chunking strategies that the evaluation compares.

A) fixed_size_chunks: sliding window of N words with overlap. Simple and
   format-agnostic, but a window can cut a fact in half or mix two sections.
B) heading_chunks: one chunk per markdown "## " section. It follows the
   document's own structure, so each chunk is one coherent topic, but chunk
   length varies with the section.

Both strategies prefix each chunk with the document title ("PayNest | ...").
Without it a chunk like "Raising 2.5M USD" would not say which company it is
about. Using the same prefix for both keeps the comparison fair.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from startupflow_ai.text import normalize


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str  # raw markdown


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    section: str
    text: str  # what gets embedded/indexed (includes the title prefix)


def load_documents(corpus_dir: Path) -> list[Document]:
    docs = []
    for path in sorted(corpus_dir.glob("*.md")):
        raw = normalize_markdown(path.read_text(encoding="utf-8"))
        title = raw.splitlines()[0].lstrip("# ").strip()
        docs.append(Document(doc_id=path.stem, title=title, text=raw))
    if not docs:
        raise FileNotFoundError(f"No .md documents in {corpus_dir}")
    return docs


def normalize_markdown(raw: str) -> str:
    """Normalise each line (NFC etc.) but keep line breaks for heading parsing."""
    return "\n".join(normalize(line) for line in raw.splitlines())


def _body_lines(doc: Document) -> list[str]:
    # Drop the H1 title and the "> synthetic" disclaimer line.
    return [ln for ln in doc.text.splitlines()[1:] if ln and not ln.startswith(">")]


def heading_chunks(doc: Document) -> list[Chunk]:
    chunks: list[Chunk] = []
    section, buf = "", []

    def flush() -> None:
        if buf:
            body = " ".join(buf)
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}#h{len(chunks)}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    section=section,
                    text=f"{doc.title} | {section}: {body}",
                )
            )

    for line in _body_lines(doc):
        if line.startswith("## "):
            flush()
            section, buf = line[3:].strip(), []
        else:
            buf.append(line)
    flush()
    return chunks


def fixed_size_chunks(doc: Document, size: int = 60, overlap: int = 15) -> list[Chunk]:
    if not 0 <= overlap < size:
        raise ValueError("require 0 <= overlap < size")
    words = " ".join(ln for ln in _body_lines(doc) if not ln.startswith("## ")).split()
    step = size - overlap
    chunks = []
    for start in range(0, max(len(words) - overlap, 1), step):
        piece = words[start : start + size]
        chunks.append(
            Chunk(
                chunk_id=f"{doc.doc_id}#f{len(chunks)}",
                doc_id=doc.doc_id,
                title=doc.title,
                section=f"words {start}-{start + len(piece)}",
                text=f"{doc.title} | " + " ".join(piece),
            )
        )
    return chunks


def chunk_corpus(docs: list[Document], strategy: str) -> list[Chunk]:
    if strategy == "heading":
        return [c for d in docs for c in heading_chunks(d)]
    if strategy == "fixed":
        return [c for d in docs for c in fixed_size_chunks(d)]
    if strategy == "fixed30":  # same size as a typical section: isolates size from boundaries
        return [c for d in docs for c in fixed_size_chunks(d, size=30, overlap=8)]
    raise ValueError(f"unknown chunking strategy: {strategy}")
