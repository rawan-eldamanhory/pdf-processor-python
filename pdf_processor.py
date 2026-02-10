"""
PDF/Document Processor — Core Engine.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber
from pypdf import PdfReader, PdfWriter


# Text extraction


def extract_text_all_pages(pdf_path: str) -> str:
    """
    Extract all text from every page of a PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages_text: List[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"--- Page {i} ---\n{text}")

    if not pages_text:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"--- Page {i} ---\n{text}")

    return "\n\n".join(pages_text)


def extract_text_by_page(
    pdf_path: str, page_number: int
) -> str:
    """
    Extract text from a single page (1-based index).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        if page_number < 1 or page_number > total:
            raise ValueError(
                f"Page {page_number} out of range (1–{total})"
            )
        return pdf.pages[page_number - 1].extract_text() or ""


def extract_text_page_range(
    pdf_path: str, start: int, end: int
) -> Dict[int, str]:
    """
    Extract text from a range of pages.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    result: Dict[int, str] = {}

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        end = min(end, total)
        for i in range(start, end + 1):
            result[i] = pdf.pages[i - 1].extract_text() or ""

    return result


# Table extraction


def extract_tables(
    pdf_path: str,
    pages: Optional[List[int]] = None
) -> List[Dict]:
    """
    Extract all tables from a PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    all_tables: List[Dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if pages and page_num not in pages:
                continue

            raw_tables = page.extract_tables()
            for tbl_idx, raw in enumerate(raw_tables):
                if not raw or len(raw) < 2:
                    continue

                headers = [str(h or "").strip() for h in raw[0]]
                rows = [
                    [str(cell or "").strip() for cell in row]
                    for row in raw[1:]
                ]

                all_tables.append({
                    "page": page_num,
                    "index": tbl_idx + 1,
                    "headers": headers,
                    "rows": rows,
                })

    return all_tables


def tables_to_text(tables: List[Dict]) -> str:
    """
    Format extracted tables as readable text.
    """
    lines: List[str] = []

    for tbl in tables:
        lines.append(
            f"\n=== Table {tbl['index']} (Page {tbl['page']}) ===\n"
        )

        headers = tbl["headers"]
        widths = [max(len(h), 8) for h in headers]

        for row in tbl["rows"]:
            for j, cell in enumerate(row):
                if j < len(widths):
                    widths[j] = max(widths[j], len(cell))

        # Header row
        header_line = " | ".join(
            h.ljust(widths[i]) for i, h in enumerate(headers)
        )
        separator = "-+-".join("-" * w for w in widths)
        lines.append(header_line)
        lines.append(separator)

        for row in tbl["rows"]:
            row_line = " | ".join(
                (row[i] if i < len(row) else "").ljust(widths[i])
                for i in range(len(headers))
            )
            lines.append(row_line)

    return "\n".join(lines)


# Merge & split


def merge_pdfs(
    input_paths: List[str],
    output_path: str
) -> int:
    """
    Merge multiple PDF files into one.
    """
    writer = PdfWriter()
    total_pages = 0

    for path in input_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"PDF not found: {path}")
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    return total_pages


def split_pdf(
    pdf_path: str,
    output_dir: str,
    pages_per_chunk: int = 1
) -> List[str]:
    """
    Split a PDF into chunks.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)

    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    stem = Path(pdf_path).stem
    output_files: List[str] = []

    chunk_start = 0
    chunk_num = 1

    while chunk_start < total:
        chunk_end = min(chunk_start + pages_per_chunk, total)
        writer = PdfWriter()

        for i in range(chunk_start, chunk_end):
            writer.add_page(reader.pages[i])

        if pages_per_chunk == 1:
            filename = f"{stem}_page_{chunk_start + 1}.pdf"
        else:
            filename = (
                f"{stem}_pages_{chunk_start + 1}"
                f"-{chunk_end}.pdf"
            )

        out_path = os.path.join(output_dir, filename)
        with open(out_path, "wb") as f:
            writer.write(f)

        output_files.append(out_path)
        chunk_start = chunk_end
        chunk_num += 1

    return output_files


def extract_page_range(
    pdf_path: str,
    start: int,
    end: int,
    output_path: str
) -> str:
    """
    Extract a range of pages into a new PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in range(start - 1, min(end, len(reader.pages))):
        writer.add_page(reader.pages[i])

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


# Rotate & watermark


def rotate_pages(
    pdf_path: str,
    output_path: str,
    degrees: int = 90,
    page_numbers: Optional[List[int]] = None
) -> str:
    """
    Rotate pages in a PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages, start=1):
        if page_numbers is None or i in page_numbers:
            page.rotate(degrees)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def add_watermark(
    pdf_path: str,
    watermark_path: str,
    output_path: str
) -> str:
    """
    Apply a watermark PDF to every page of a document.
    """
    reader = PdfReader(pdf_path)
    watermark_reader = PdfReader(watermark_path)
    watermark_page = watermark_reader.pages[0]

    writer = PdfWriter()

    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


# Encryption


def encrypt_pdf(
    pdf_path: str,
    output_path: str,
    user_password: str,
    owner_password: Optional[str] = None
) -> str:
    """
    Password-protect a PDF.
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password
    )

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def decrypt_pdf(
    pdf_path: str,
    output_path: str,
    password: str
) -> str:
    """
    Remove password protection from a PDF.
    """
    reader = PdfReader(pdf_path)

    if reader.is_encrypted:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError("Wrong password")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


# Metadata


def get_pdf_info(pdf_path: str) -> Dict:
    """
    Read PDF metadata and basic statistics.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    meta = reader.metadata or {}

    return {
        "num_pages": len(reader.pages),
        "file_size_kb": round(os.path.getsize(pdf_path) / 1024, 1),
        "encrypted": reader.is_encrypted,
        "title": meta.get("/Title", ""),
        "author": meta.get("/Author", ""),
        "subject": meta.get("/Subject", ""),
        "creator": meta.get("/Creator", ""),
        "producer": meta.get("/Producer", ""),
        "creation_date": meta.get("/CreationDate", ""),
    }


# Word (.docx) support


def extract_text_from_docx(docx_path: str) -> str:
    """
    Extract all text paragraphs from a Word .docx file.
    """
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "python-docx required: pip install python-docx"
        ) from exc

    doc = Document(docx_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def docx_to_pdf_text_report(docx_path: str, output_pdf: str) -> str:
    """
    Read a .docx and write its text content into a PDF report.
    """
    text = extract_text_from_docx(docx_path)

    from report_generator import generate_text_report

    generate_text_report(
        title=Path(docx_path).stem,
        sections=[{"heading": "Document Content", "body": text}],
        output_path=output_pdf
    )

    return output_pdf


# Search


def search_pdf(
    pdf_path: str,
    query: str,
    case_sensitive: bool = False
) -> List[Dict]:
    """
    Search for a word or regex pattern across all pages.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(query, flags)
    matches: List[Dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            for line_num, line in enumerate(text.splitlines(), start=1):
                for match in pattern.finditer(line):
                    matches.append({
                        "page": page_num,
                        "line_number": line_num,
                        "line": line.strip(),
                        "match": match.group(),
                    })

    return matches
