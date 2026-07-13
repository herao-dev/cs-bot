from __future__ import annotations
import os
import re
from config import Config


def parse_file(filepath: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return _read_txt(filepath)
    elif ext == ".md":
        return _read_txt(filepath)
    elif ext == ".pdf":
        return _read_pdf(filepath)
    elif ext == ".docx":
        return _read_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def _read_txt(filepath: str) -> str:
    for enc in ["utf-8", "gbk", "gb2312", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError("Cannot decode file")


def _read_pdf(filepath: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(filepath)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _read_docx(filepath: str) -> str:
    from docx import Document
    doc = Document(filepath)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list:
    chunk_size = chunk_size or Config.CHUNK_SIZE
    overlap = overlap or Config.CHUNK_OVERLAP

    text = re.sub(r"\n{3,}", "\n\n", text)
    paragraphs = text.split("\n\n")

    chunks = []
    current = ""
    chunk_idx = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) < chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append({"content": current, "index": chunk_idx})
                chunk_idx += 1
                overlap_text = current[-overlap:] if len(current) > overlap else current
                current = overlap_text + "\n\n" + para
            else:
                current = para

    if current.strip():
        chunks.append({"content": current.strip(), "index": chunk_idx})

    return chunks
