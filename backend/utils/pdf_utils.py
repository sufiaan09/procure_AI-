"""
PDF text extraction utilities using PyMuPDF (fitz).
Returns text with page-level metadata so evidence links work correctly.
"""

from __future__ import annotations
import fitz  # PyMuPDF


def extract_text_with_pages(pdf_path: str) -> list[dict]:
    """
    Extract text from each page of a PDF.

    Returns a list of dicts:
        [{"page": 1, "text": "...", "word_count": N}, ...]
    """
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append({
            "page": i,
            "text": text,
            "word_count": len(text.split()),
        })
    doc.close()
    return pages


def extract_full_text(pdf_path: str) -> str:
    """Return the entire PDF as a single string with page separators."""
    pages = extract_text_with_pages(pdf_path)
    parts = []
    for p in pages:
        parts.append(f"\n--- PAGE {p['page']} ---\n{p['text']}")
    return "\n".join(parts)


def extract_full_text_from_bytes(pdf_bytes: bytes) -> tuple[str, int]:
    """
    Accept raw PDF bytes (from an uploaded file) and return
    (full_text_with_page_markers, total_pages).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        parts.append(f"\n--- PAGE {i} ---\n{text}")
    total = doc.page_count
    doc.close()
    return "\n".join(parts), total


def find_text_page(full_text_with_markers: str, snippet: str) -> int:
    """
    Given the full text (with --- PAGE N --- markers) and a short snippet,
    return the 1-based page number where the snippet appears, or 0 if not found.
    """
    import re
    lines = full_text_with_markers.split("\n")
    current_page = 0
    snippet_lower = snippet.lower().strip()
    for line in lines:
        m = re.match(r"--- PAGE (\d+) ---", line)
        if m:
            current_page = int(m.group(1))
            continue
        if snippet_lower in line.lower():
            return current_page
    return 0
