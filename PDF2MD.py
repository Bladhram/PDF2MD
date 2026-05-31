#!/usr/bin/env python3
"""
PDF to Markdown Converter (EasyOCR - no Tesseract/Poppler/API key required)
- Scans the input/ folder for PDFs
- Renders each page as an image and reads it with EasyOCR
- Saves a .md file to output/
- Archives the original PDF to archive/

Install:
    pip install pymupdf easyocr

First run will download the OCR model (~100MB, one time only).
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    print("Missing dependency. Run:  pip install pymupdf")
    sys.exit(1)

try:
    import easyocr
except ImportError:
    print("Missing dependency. Run:  pip install easyocr")
    sys.exit(1)

import numpy as np

# ── Settings ──────────────────────────────────────────────────────────────────
DPI  = 200   # higher = better accuracy but slower; 200 is a good balance
LANG = ["en"] # add languages if needed e.g. ["en", "fr"]

# ── Folder defaults (relative to this script) ─────────────────────────────────
_SCRIPT_DIR     = Path(__file__).parent.resolve()
DEFAULT_INPUT   = str(_SCRIPT_DIR / "input")
DEFAULT_OUTPUT  = str(_SCRIPT_DIR / "output")
DEFAULT_ARCHIVE = str(_SCRIPT_DIR / "archive")

# ── Core extraction ───────────────────────────────────────────────────────────

def page_to_numpy(page: fitz.Page, dpi: int) -> np.ndarray:
    """Render a PDF page to a numpy array (RGB)."""
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, 3)
    return img


def extract_pdf_to_markdown(pdf_path: Path, reader: easyocr.Reader) -> str:
    doc = fitz.open(str(pdf_path))
    total = len(doc)
    print(f"  Reading {total} page(s) with EasyOCR...")

    md_parts = []
    for i, page in enumerate(doc, start=1):
        print(f"    Page {i}/{total}...")
        img = page_to_numpy(page, DPI)

        # EasyOCR returns list of (bbox, text, confidence)
        results = reader.readtext(img, detail=1, paragraph=False)

        if not results:
            continue

        # Sort results top-to-bottom, then left-to-right using bbox top-left corner
        results.sort(key=lambda r: (round(r[0][0][1] / 20), r[0][0][0]))

        # Group into lines by similar y-coordinate
        lines = []
        current_line = []
        last_y = None

        for bbox, text, conf in results:
            top_y = bbox[0][1]
            if last_y is None or abs(top_y - last_y) < 20:
                current_line.append(text)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [text]
            last_y = top_y

        if current_line:
            lines.append(" ".join(current_line))

        page_text = "\n".join(lines).strip()
        if page_text:
            md_parts.append(f"## Page {i}\n\n{page_text}")

    doc.close()
    return "\n\n---\n\n".join(md_parts)

# ── File management ───────────────────────────────────────────────────────────

def process_pdfs(input_dir: Path, output_dir: Path, archive_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_dir.glob("*.[pP][dD][fF]"))
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'.")
        return

    print(f"Found {len(pdf_files)} PDF(s) in '{input_dir}'.\n")
    print("Loading EasyOCR model (first run downloads ~100MB)...")
    reader = easyocr.Reader(LANG, gpu=False)
    print("Model ready.\n")

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        try:
            md_content = extract_pdf_to_markdown(pdf_path, reader)

            if not md_content.strip():
                print(f"  Warning: No text extracted — skipping.\n")
                continue

            md_path = output_dir / (pdf_path.stem + ".md")
            md_path.write_text(md_content, encoding="utf-8")
            print(f"  Markdown saved  -> {md_path}")

            archive_path = archive_dir / pdf_path.name
            counter = 1
            while archive_path.exists():
                archive_path = archive_dir / f"{pdf_path.stem}_{counter}{pdf_path.suffix}"
                counter += 1

            shutil.move(str(pdf_path), archive_path)
            print(f"  PDF archived    -> {archive_path}\n")

        except Exception as exc:
            print(f"  Error: {exc}\n")

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OCR scanned PDFs using EasyOCR and save as Markdown."
    )
    parser.add_argument("--input",   default=DEFAULT_INPUT,   help="Folder to scan for PDFs")
    parser.add_argument("--output",  default=DEFAULT_OUTPUT,  help="Folder for .md output files")
    parser.add_argument("--archive", default=DEFAULT_ARCHIVE, help="Folder for archived PDFs")
    args = parser.parse_args()

    input_dir   = Path(args.input)
    output_dir  = Path(args.output)
    archive_dir = Path(args.archive)

    if not input_dir.exists():
        input_dir.mkdir(parents=True)
        print(f"Created input folder. Place PDFs in:\n  {input_dir.resolve()}\nThen re-run.")
        return

    process_pdfs(input_dir, output_dir, archive_dir)
    print("Done.")

if __name__ == "__main__":
    main()