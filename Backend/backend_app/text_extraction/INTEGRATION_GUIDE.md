# Consolidated Extractor Integration Guide

This guide explains how to integrate the new consolidated extractor with OpenCV preprocessing, PaddleOCR fallback, and Logbook system.

## Files Added

1. **`consolidated_extractor.py`** - Main consolidated extraction wrapper
2. **`analyze_logbook.py`** - Simple script to analyze extraction logs
3. **`requirements_fallbacks.txt`** - New dependencies for fallback layers

## New Dependencies

Install the new requirements:

```bash
pip install -r Backend/backend_app/text_extraction/requirements_fallbacks.txt
```

### System Packages Required

- **poppler-utils** (for `pdf2image`)
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
  - Windows: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

- **tesseract-ocr** (for pytesseract)
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract tesseract-lang`
  - Windows: Download from [tesseract-ocr](https://github.com/tesseract-ocr/tesseract)

- **PaddleOCR** (optional, will be skipped if not available)
  - CPU: `pip install paddlepaddle==2.5.2 -f https://paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html`
  - GPU: `pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html`

## Integration Options

### Option A: Replace Brain Service Text Extraction (Recommended)

Modify `Backend/backend_app/brain_module/brain_core.py` to use the consolidated extractor:

```python
# In the _extract_text method, replace the current extraction logic:
def _extract_text(self, file_path: Path) -> Optional[str]:
    """
    Extract text from file using the consolidated extractor.
    """
    try:
        from backend_app.text_extraction.consolidated_extractor import extract_with_logging
        
        # Use consolidated extractor with logging
        result = extract_with_logging(
            file_path=file_path,
            metadata={"source": "brain_core"},
            quality_threshold=70.0
        )
        
        if result["success"]:
            self.logger.info(f"Text extraction successful using {result['module']}")
            return result["text"]
        else:
            self.logger.warning(f"Text extraction failed for {file_path}")
            return None
            
    except Exception as e:
        self.logger.error(f"Error extracting text from {file_path}: {e}")
        return None
```

### Option B: Patch Intake Router (Alternative)

Modify `Backend/backend_app/file_intake/intake_router.py` to use consolidated extraction:

```python
# Replace the current text extraction in process_file method:
from backend_app.text_extraction.consolidated_extractor import extract_with_logging

# In the process_file method, replace steps 5-6:
# Step 5: Extract text using consolidated extractor
logger.debug("Step 5: Extracting text with consolidated extractor")
extraction_result = extract_with_logging(
    file_path=tmp_path,
    metadata={"source": source, "filename": filename},
    quality_threshold=70.0
)

if extraction_result["success"]:
    extracted_text = extraction_result["text"]
    logger.debug(f"Text extraction successful using {extraction_result['module']}")
else:
    extracted_text = ""
    logger.warning(f"Text extraction failed for {filename}")

# Step 6: Parse resume using brain service (pass extracted text)
logger.debug("Step 6: Parsing resume using brain service")
brain_output = parse_resume_from_path(extracted_text, strategy="fast")  # Pass text instead of path
```

## Logbook Analysis

After running extractions, analyze the results:

```bash
cd Backend
python backend_app/text_extraction/analyze_logbook.py
```

This will show:
- Success/failure rates by module
- Average quality scores
- Recent extraction attempts
- Attempt breakdown by module

## Database Schema

The logbook stores data in `logs/extraction_logbook.db` with the following schema:

```sql
CREATE TABLE extraction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    file_path TEXT,
    file_size INTEGER,
    page_count INTEGER,
    attempts_json TEXT,           -- JSON array of all attempts
    success_module TEXT,          -- Which module succeeded
    success BOOLEAN,
    extracted_length INTEGER,     -- Length of extracted text
    quality_score REAL,           -- Quality score (0-100)
    metadata_json TEXT            -- Additional metadata
);
```

## Quality Threshold

The default quality threshold is 70.0. You can adjust this based on your needs:

- **Higher threshold (80-90)**: More aggressive fallbacks, higher quality output
- **Lower threshold (60-70)**: Fewer fallbacks, faster processing
- **Very low threshold (40-50)**: Minimal fallbacks, fastest processing

## Fallback Order

The consolidated extractor tries modules in this order:

1. **Unstructured primary** (your existing extractor)
2. **Unstructured alternate** (if available)
3. **DOCX extractor** (for Word documents)
4. **PyPDF2** (for PDFs)
5. **Tesseract OCR** (for scanned PDFs)
6. **OpenCV + Tesseract retry** (preprocessed OCR)
7. **PaddleOCR** (alternative OCR engine)

Each step is only attempted if the previous step fails or produces low quality.

## Monitoring and Debugging

1. **Check logs**: The extractor logs each attempt with quality scores
2. **Analyze logbook**: Run the analysis script to see which modules work best
3. **Adjust threshold**: Based on results, tune the quality threshold
4. **Monitor PaddleOCR**: First run may download models (slow)

## Rollback

To revert to the original system:

1. Remove the consolidated extractor import
2. Restore the original text extraction logic
3. The existing extractors remain unchanged and functional

## Testing

Test the integration with various file types:

```python
from pathlib import Path
from backend_app.text_extraction.consolidated_extractor import extract_with_logging

# Test with a PDF
result = extract_with_logging(
    file_path=Path("test_resume.pdf"),
    metadata={"test": True},
    quality_threshold=70.0
)

print(f"Success: {result['success']}")
print(f"Module: {result['module']}")
print(f"Quality: {result['score']:.1f}")
print(f"Text length: {len(result['text'] or '')}")