# PDF / Document Processor (Python)

A professional Python project that extracts text, extracts tables, merges/splits PDFs,
generates polished reports and handles encryption.

---

## Features at a Glance

- Extract text (digital PDF) | pdfplumber + pypdf
- Extract tables → structured data | pdfplumber 
- Merge multiple PDFs | pypdf 
- Split PDF into pages/chunks | pypdf 
- Extract page range | pypdf 
- Rotate pages | pypdf 
- Add watermark | pypdf 
- Encrypt / Decrypt PDF | pypdf 
- Read PDF metadata | pypdf 
- Full-text search with regex | pdfplumber 
- Generate professional reports | reportlab 
- Read Word (.docx) documents | python-docx 
- Convert .docx → PDF | python-docx + reportlab 

---

## Project Structure

```
pdf_processor/
│
├── pdf_processor.py          ← Core engine: all PDF/docx operations
├── report_generator.py       ← ReportLab report builder (styled PDFs)
├── main.py                   ← CLI demo runner (9 feature demos)
│
├── test_pdf_processor.py     ← Full pytest test suite (50+ tests)
├── run_tests.py              ← Standalone test runner (no pytest needed)
│
├── requirements.txt          ← Production dependencies
├── requirements-dev.txt      ← Dev + test dependencies
├── pyproject.toml            ← Black / isort / pytest / coverage configs
│
├── .gitignore
```

---

## Quick Start

### 1. Clone the project

```bash
git clone https://github.com/YOUR-USERNAME/pdf-processor.git
cd pdf-processor
```

### 2. Create a virtual environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the full demo

```bash
python main.py
```

This creates `sample_pdfs/` with 3 sample PDFs, runs all 9 feature demos,
and writes results to `outputs/`:

```
outputs/
  extracted_text.txt          ← Raw text extracted from PDF
  extracted_tables.txt        ← Tables as formatted text
  merged.pdf                  ← 3 PDFs merged into one
  split_pages/                ← Individual page PDFs
  professional_report.pdf     ← Full styled report with tables
  encrypted.pdf               ← Password-protected PDF
  decrypted.pdf               ← Decrypted back
  rotated.pdf                 ← Page rotated 90°
  from_docx.pdf               ← Word doc converted to PDF
```

### 5. Run a specific feature only

```bash
python main.py --feature text     # Text extraction
python main.py --feature table    # Table extraction
python main.py --feature merge    # Merge & split
python main.py --feature metadata # PDF info
python main.py --feature search   # Search with regex
python main.py --feature report   # Report generation
python main.py --feature encrypt  # Encryption
python main.py --feature rotate   # Rotate pages
python main.py --feature docx     # Word doc processing
```

---


## Running Tests

### Quick test (no pytest needed)

```bash
python run_tests.py
```

Expected output:
```
======================================================================
  PDF PROCESSOR — TEST SUITE
======================================================================

test_extract_all_contains_content ... ok
test_extract_all_file_not_found_raises ... ok
...

Ran 45 tests in 1.0s
OK

  RESULTS: 45/45 tests passed
  ALL TESTS PASSED 
```

### With pytest (after pip install pytest pytest-cov)

```bash
# Basic run
pytest -v

# With coverage report
pytest -v --cov=pdf_processor --cov=report_generator --cov-report=term

# Only smoke tests
pytest -v -m smoke

# Skip slow tests
pytest -v -m "not slow"

# HTML report
pytest -v --html=report.html --self-contained-html
```

