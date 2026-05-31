# PDF2MD — Scanned PDF to Markdown Converter

Convert scanned or image-based PDFs into readable Markdown files using OCR — no Tesseract, no Poppler, no API key required.

---

## How It Works

1. Scans the `input/` folder for any `.pdf` files
2. Renders each page as an image using PyMuPDF
3. Runs OCR on each page image using EasyOCR
4. Saves the extracted text as a `.md` file in `output/`
5. Moves the original PDF to `archive/` to avoid reprocessing

---

## Requirements

- Python 3.7+
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) — PDF rendering
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — OCR engine

Install both with:

```bash
pip install pymupdf easyocr
```

> **Note:** The first run will download the EasyOCR language model (~100MB). Subsequent runs use the cached model.

---

## Usage

### Basic (uses default folders)

```bash
python PDF2MD.py
```

This will look for PDFs in `./input/`, write Markdown to `./output/`, and archive processed PDFs to `./archive/`. All three folders are created automatically if they don't exist.

### Custom folders

```bash
python PDF2MD.py --input /path/to/pdfs --output /path/to/markdown --archive /path/to/archive
```

| Argument    | Default                  | Description                          |
|-------------|--------------------------|--------------------------------------|
| `--input`   | `./input/`               | Folder to scan for PDF files         |
| `--output`  | `./output/`              | Folder where `.md` files are saved   |
| `--archive` | `./archive/`             | Folder where processed PDFs are kept |

---

## Output Format

Each PDF becomes a single `.md` file. Pages are separated by a horizontal rule, and each page gets a heading:

```markdown
## Page 1

Your extracted text here...

---

## Page 2

More extracted text...
```

---

## Configuration

Two settings can be tweaked near the top of the script:

```python
DPI  = 200    # Render resolution — higher = better accuracy but slower
LANG = ["en"] # OCR languages — e.g. ["en", "fr"] for English + French
```

A DPI of 200 is a good balance between speed and accuracy for most documents. Increase it (e.g. `300`) for finer print or degraded scans.

---

## Folder Structure

```
project/
├── PDF2MD.py
├── input/        ← drop PDFs here
├── output/       ← Markdown files appear here
└── archive/      ← processed PDFs moved here
```

---

## Notes

- OCR works best on cleanly scanned documents. Skewed, low-contrast, or handwritten pages may produce lower-quality results.
- If a PDF produces no text (e.g. a blank page or unreadable scan), it is skipped with a warning and **not** archived.
- If an archived filename already exists, a numeric suffix is appended (e.g. `report_1.pdf`) to avoid overwrites.
- GPU acceleration is disabled by default (`gpu=False`). If you have a CUDA-compatible GPU, change this to `gpu=True` in the `process_pdfs` function for significantly faster processing.

---

## License

MIT — use freely, contributions welcome.
