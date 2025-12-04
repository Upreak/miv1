# Text Extraction System Requirements

## Overview

This document provides the complete requirement sheet for your entire text extraction subsystem, including:

- ✅ Your existing extractors
- ✅ All dependencies
- ✅ New fallback layers (OpenCV + PaddleOCR)
- ✅ Quality scoring system
- ✅ Logbook system
- ✅ System-level packages

## Master Requirements Sheet

### 1. Python Library Requirements (PIP)

#### Core Extractors (Your Existing Logic)
These are required by your existing modules:

```txt
# Primary extraction
unstructured[local-inference]==0.10.27
unstructured-inference

# Fallback extraction
PyPDF2
python-magic
lxml
Pillow

# PDF to image conversion
pdf2image

# OCR fallback
pytesseract
```

**Purpose:**
- `unstructured` - primary PDF/DOCX extraction
- `unstructured-inference` - fallback for layout inference
- `PyPDF2` - fallback text extraction
- `python-magic` - true MIME type detection
- `lxml` - DOCX parser internal requirement
- `Pillow` - image reading for OCR fallback
- `pdf2image` - PDFs → images (needed for Tesseract, OpenCV, PaddleOCR)
- `pytesseract` - OCR fallback

#### New Fallback Layers (OpenCV + PaddleOCR)
These power the 6th and 7th fallback layers:

```txt
# OpenCV preprocessing
opencv-python-headless>=4.7.0

# PaddleOCR fallback
paddleocr>=2.6.1
paddlepaddle==2.5.2
```

**Purpose:**
- `OpenCV` - deskew, enhance, denoise, upscale, threshold images before OCR
- `PaddleOCR` - deep-learning OCR fallback
- `paddlepaddle` - ML backend for PaddleOCR

**IMPORTANT:** PaddlePaddle needs a platform-specific wheel.

#### Quality Scoring System
All implemented in pure Python - no extra packages needed.

Optional for enhanced text cleaning:
```txt
regex
```

#### Logbook System
Uses built-in Python libraries:
- `sqlite3` (built-in)
- `json` (built-in)
- `time` (built-in)
- `statistics` (built-in)

Optional for analytics:
```txt
pandas
matplotlib
```

#### Optional Enhancements
Recommended for maximum compatibility:
```txt
opencv-contrib-python-headless
rapidfuzz            # for fuzzy keyword matching
spacy                # NLP quality check (optional future)
python-poppler       # direct PDF parsing support
```

### 2. Complete Final Python Requirements Block

Use this as your official `text_extraction_requirements.txt`:

```txt
# ================================================
# TEXT EXTRACTION SUBSYSTEM — FINAL REQUIREMENTS
# ================================================

# --- Unstructured extractors (Primary & fallback 1,2,3) ---
unstructured[local-inference]==0.10.27
unstructured-inference
PyPDF2
python-magic
lxml
Pillow

# PDF -> Image conversion for OCR
pdf2image

# OCR (Fallback 5)
pytesseract

# --- NEW: Fallback Layer 6: OpenCV preprocessing ---
opencv-python-headless>=4.7.0

# --- NEW: Fallback Layer 7: PaddleOCR ---
paddleocr>=2.6.1
paddlepaddle==2.5.2   # Use CPU wheel for Linux or Mac

# --- Utility (Optional/Recommended) ---
regex
rapidfuzz
pandas
matplotlib
```

### 3. System-Level (OS) Dependencies

These must be installed manually.

#### Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libtesseract-dev
```

#### macOS (Homebrew)
```bash
brew install poppler tesseract
```

#### Windows
1. **Install Poppler:**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Add `poppler/bin` to PATH

2. **Install Tesseract OCR:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH

### 4. PaddleOCR System Notes

PaddleOCR uses PaddlePaddle which may need:
- `libstdc++6` updated
- `libgcc` 
- CPU instruction support (AVX, etc.)

### 5. Platform-Specific PaddlePaddle Installation

#### Ubuntu CPU
```bash
pip install paddlepaddle==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/cpu/
```

#### macOS CPU
```bash
pip install paddlepaddle==2.5.2 -f https://www.paddlepaddle.org.cn/whl/macos/cpu/
```

#### GPU (if CUDA available)
```bash
pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable/
```

### 6. System Architecture Coverage

This requirement sheet covers:

✅ **Unstructured** (PDF, DOCX parsing)
✅ **Unstructured inference mode**
✅ **PyPDF2 fallback**
✅ **Tesseract OCR fallback**
✅ **OpenCV enhancement fallback**
✅ **PaddleOCR final fallback**
✅ **Quality scoring module**
✅ **Logbook system (SQLite)**
✅ **Utilities for images & OCR**

### 7. Installation Commands

#### Quick Start (All-in-One)
```bash
# Install Python dependencies
pip install -r Backend/backend_app/text_extraction/requirements_fallbacks.txt

# Install system packages (Ubuntu)
sudo apt-get install -y poppler-utils tesseract-ocr

# Install PaddlePaddle (CPU)
pip install paddlepaddle==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/cpu/

# Create logs directory
mkdir -p logs
```

### 8. Verification Commands

After installation, verify each component:

```python
# Test imports
import cv2
from paddleocr import PaddleOCR
import pytesseract
from pdf2image import convert_from_path
import PyPDF2
import unstructured
```

```bash
# Test system commands
tesseract --version
pdfinfo  # (from poppler-utils)
```

### 9. Troubleshooting

#### Common Issues

1. **PaddleOCR slow on first run:**
   - Downloads models automatically (normal)
   - Subsequent runs are fast

2. **OpenCV import errors:**
   - Ensure `opencv-python-headless` is installed
   - Not `opencv-python` (which requires GUI)

3. **Tesseract not found:**
   - Verify `tesseract --version` works
   - Check PATH includes tesseract installation

4. **Poppler not found:**
   - Verify `pdfinfo` command works
   - Check PATH includes poppler/bin

### 10. Next Steps

1. **Install dependencies** using the commands above
2. **Apply integration patch** to brain core or intake router
3. **Test with sample files** to verify functionality
4. **Run analysis script** to monitor performance

### 11. Files Referenced

- `Backend/backend_app/text_extraction/requirements_fallbacks.txt` - Python requirements
- `Backend/backend_app/text_extraction/INTEGRATION_GUIDE.md` - Integration instructions
- `Backend/backend_app/text_extraction/CONSOLIDATED_EXTRACTOR_SUMMARY.md` - Implementation summary
- `Backend/backend_app/text_extraction/analyze_logbook.py` - Analysis script

---

**Note:** This requirement sheet ensures everything installs cleanly on Ubuntu, Mac, or Windows. All dependencies are explicitly listed with versions where necessary.