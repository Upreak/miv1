"""
consolidated_extractor.py

Consolidated extraction wrapper that:
- Calls existing extractors (unstructured primary, alt, docx, PyPDF2, Tesseract)
- Adds two additional fallback layers:
    6) OpenCV-based preprocessing + Tesseract retry
    7) PaddleOCR extraction
- Runs a quality check after each attempt; triggers fallback when quality < threshold
- Logs each attempt to a SQLite 'extraction_logbook.db' (table: extraction_logs)
- Provides a simple API: extract_with_logging(file_path, metadata={})
"""

from pathlib import Path
import time
import json
import sqlite3
import logging
import statistics
import re

# Try optional imports for new fallbacks
try:
    import cv2
except Exception:
    cv2 = None

try:
    from paddleocr import PaddleOCR
except Exception:
    PaddleOCR = None

# Imports from existing modules (your files)
# These functions should already exist in your uploaded files:
# - extract_text_97_percent(file_path, strategy)
# - extract_text_from_file(file_path, config, mode)  (unified)
# - extract_text_with_pypdf2_fallback(file_path)
# - (or other names used in your extractor). We'll try several names.
from backend_app.text_extraction import final_97_percent_extractor as extractor97
from backend_app.text_extraction import unstructured_io_runner as unstructured_runner

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------- Logbook manager (simple SQLite) ----------
LOG_DB_PATH = Path("logs/extraction_logbook.db")
LOG_DB_PATH.parent.mkdir(exist_ok=True)


class Logbook:
    def __init__(self, db_path: Path = LOG_DB_PATH):
        self.db_path = db_path
        self._ensure_table()

    def _conn(self):
        return sqlite3.connect(str(self.db_path), timeout=30)

    def _ensure_table(self):
        q = """
        CREATE TABLE IF NOT EXISTS extraction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            file_path TEXT,
            file_size INTEGER,
            page_count INTEGER,
            attempts_json TEXT,   -- list of attempts with module name, success, length, notes
            success_module TEXT,
            success BOOLEAN,
            extracted_length INTEGER,
            quality_score REAL,
            metadata_json TEXT
        );
        """
        with self._conn() as c:
            c.execute(q)
            c.commit()

    def record(self, file_path: str, file_size: int, page_count: int,
               attempts: list, success_module: str,
               success: bool, extracted_length: int,
               quality_score: float, metadata: dict):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO extraction_logs (timestamp, file_path, file_size, page_count, attempts_json, success_module, success, extracted_length, quality_score, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (time.strftime("%Y-%m-%d %H:%M:%S"), file_path, file_size, page_count,
                 json.dumps(attempts), success_module, int(success), extracted_length, quality_score, json.dumps(metadata))
            )
            conn.commit()

    def fetch_recent(self, limit=100):
        with self._conn() as conn:
            cur = conn.execute("SELECT * FROM extraction_logs ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()


logbook = Logbook()

# ---------- Utility helpers ----------
EMAIL_PHONE_RE = re.compile(r'(@)|(gmail\.|yahoo\.|hotmail\.)|(\+?\d{6,})', re.I)
KEYWORD_SET = {
    "experience", "education", "skills", "project", "bachelor", "master", "phd",
    "company", "intern", "years", "education", "degree", "summary", "objective",
    "contact", "phone", "email", "skill", "github", "linkedin"
}

def simple_page_count(file_path: Path) -> int:
    # Try to get page count cheaply: PyPDF2 if available.
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)
    except Exception:
        return 1


def text_stats(text: str) -> dict:
    if not text:
        return {"chars": 0, "words": 0, "digit_ratio": 0.0, "whitespace_ratio": 0.0, "keyword_hits": 0}
    chars = len(text)
    words = len(text.split())
    digits = sum(c.isdigit() for c in text)
    whitespace = sum(1 for c in text if c.isspace())
    digit_ratio = digits / max(1, chars)
    whitespace_ratio = whitespace / max(1, chars)
    keyword_hits = sum(1 for kw in KEYWORD_SET if kw.lower() in text.lower())
    return {
        "chars": chars,
        "words": words,
        "digit_ratio": digit_ratio,
        "whitespace_ratio": whitespace_ratio,
        "keyword_hits": keyword_hits
    }

def quality_score(text: str, file_path: Path) -> float:
    """
    Returns score 0-100. Higher is better.
    Heuristics:
      - chars length thresholds
      - keyword_hits
      - page_count vs chars
      - digit / whitespace garbage heuristics
    """
    stats = text_stats(text)
    chars = stats["chars"]
    kw = stats["keyword_hits"]
    pages = simple_page_count(file_path)
    # length score
    if chars >= 2000:
        length_score = 100
    elif chars >= 800:
        length_score = 85
    elif chars >= 400:
        length_score = 70
    elif chars >= 200:
        length_score = 50
    elif chars >= 100:
        length_score = 30
    else:
        length_score = 0

    # keyword score (cap 100)
    kw_score = min(100, kw * 20)  # each keyword contributes up to 20

    # page vs length penalty
    expected_per_page = 800  # rough chars per page
    page_expectation = pages * expected_per_page
    if chars >= page_expectation * 0.8:
        page_score = 100
    else:
        ratio = chars / max(1, page_expectation)
        page_score = max(0, int(ratio * 100))

    # garbage penalty
    garbage_penalty = 0
    if stats["digit_ratio"] > 0.6:
        garbage_penalty += 30
    if stats["whitespace_ratio"] > 0.6:
        garbage_penalty += 20

    # Weighted sum
    score = (
        0.35 * length_score +
        0.35 * kw_score +
        0.25 * page_score -
        0.05 * garbage_penalty * 1.0
    )
    # clamp
    score = max(0.0, min(100.0, score))
    return score

# ---------- OpenCV preprocess ----------
def opencv_preprocess_pdf_image(image_path: Path, out_path: Path) -> bool:
    """
    Read image with OpenCV -> deskew, denoise, threshold, upscale -> write out_path
    Returns True if processed file written.
    """
    if cv2 is None:
        logger.warning("OpenCV not installed. Skipping OpenCV preprocessing.")
        return False

    try:
        img = cv2.imread(str(image_path))
        if img is None:
            logger.warning("OpenCV failed to read image.")
            return False

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Adaptive threshold for contrast enhancement
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 10)

        # Optional: morphological ops to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

        # Upscale if small
        h, w = th.shape
        if max(h, w) < 1200:
            scale = 2
            th = cv2.resize(th, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)

        # Save
        cv2.imwrite(str(out_path), th)
        return True
    except Exception as e:
        logger.exception("OpenCV preprocessing failed: %s", e)
        return False

# ---------- PaddleOCR wrapper ----------
_paddle_ocr_instance = None

def paddle_extract_from_image(image_path: Path, lang="en") -> str:
    global _paddle_ocr_instance
    if PaddleOCR is None:
        logger.warning("PaddleOCR not installed. Skipping PaddleOCR.")
        return ""
    if _paddle_ocr_instance is None:
        _paddle_ocr_instance = PaddleOCR(use_angle_cls=True, lang=lang)  # may download models
    try:
        res = _paddle_ocr_instance.ocr(str(image_path), cls=True)
        lines = []
        for page in res:
            for line in page:
                # line format: [ [bbox], (text, confidence) ]
                txt = line[-1][0] if isinstance(line[-1], tuple) else str(line[-1])
                lines.append(txt)
        return "\n".join(lines)
    except Exception as e:
        logger.exception("PaddleOCR extraction failed: %s", e)
        return ""

# ---------- Main consolidated function ----------
def extract_with_logging(file_path: Path, metadata: dict = None, quality_threshold: float = 70.0) -> dict:
    """
    Main API:
      - file_path: Path to file (pdf/docx)
      - metadata: optional dict with additional info
      - quality_threshold: fallback threshold (0-100)
    Returns:
      dict with keys: success (bool), module (which module produced result), text, score, attempts (list)
    """
    if metadata is None:
        metadata = {}

    attempts = []
    last_text = None
    success_module = None
    success = False

    file_size = file_path.stat().st_size if file_path.exists() else 0
    page_count = simple_page_count(file_path)

    # Helper to append attempt
    def record_attempt(name, text, notes=""):
        st = text or ""
        rec = {
            "module": name,
            "success": bool(st.strip()),
            "length": len(st),
            "notes": notes,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        attempts.append(rec)
        return rec

    # ---------- 1. Unstructured primary: try extractor97.extract_text_97_percent or unified fallback ----------
    try:
        logger.info("Attempt 1: Unstructured (primary) via final_97_percent_extractor")
        # prefer extract_text_97_percent if present
        if hasattr(extractor97, "extract_text_97_percent"):
            text = extractor97.extract_text_97_percent(file_path, strategy="fast")
        else:
            # fallback to unified interface - use extract_text function directly
            # The extract_text function expects file_bytes and filename
            try:
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
                text = extractor97.extract_text(file_bytes, file_path.name)
            except Exception as e:
                logger.warning(f"Failed to use extract_text fallback: {e}")
                text = None
        record_attempt("unstructured_primary", text)
        score = quality_score(text or "", file_path)
        logger.info(f"Unstructured primary quality score: {score:.1f}")
        if text and score >= quality_threshold:
            last_text = text
            success_module = "unstructured_primary"
            success = True
        else:
            logger.info("Unstructured primary either failed or below quality threshold; continuing to fallback.")
    except Exception as e:
        record_attempt("unstructured_primary", None, notes=f"exception: {e}")
        logger.exception("Unstructured primary raised exception")

    # ---------- 2. Unstructured alternate (if available) ----------
    if not success:
        try:
            logger.info("Attempt 2: Unstructured alternate / inference path")
            if hasattr(unstructured_runner, "extract_text_from_file"):
                text = unstructured_runner.extract_text_from_file(file_path, strategy="fast")
            else:
                text = None
            record_attempt("unstructured_alternate", text)
            score = quality_score(text or "", file_path)
            logger.info(f"Unstructured alternate quality score: {score:.1f}")
            if text and score >= quality_threshold:
                last_text = text
                success_module = "unstructured_alternate"
                success = True
            else:
                logger.info("Unstructured alternate failed or low quality.")
        except Exception as e:
            record_attempt("unstructured_alternate", None, notes=f"exception: {e}")
            logger.exception("Unstructured alternate raised exception")

    # ---------- 3. DOCX (direct doc extractor) ----------
    if not success and file_path.suffix.lower() in {".doc", ".docx"}:
        try:
            logger.info("Attempt 3: DOCX direct extractor")
            if hasattr(unstructured_runner, "extract_text_from_docx"):
                text = unstructured_runner.extract_text_from_docx(file_path)
            else:
                text = None
            record_attempt("docx_extractor", text)
            score = quality_score(text or "", file_path)
            logger.info(f"DOCX extractor quality score: {score:.1f}")
            if text and score >= quality_threshold:
                last_text = text
                success_module = "docx_extractor"
                success = True
            else:
                logger.info("DOCX extractor failed or low quality.")
        except Exception as e:
            record_attempt("docx_extractor", None, notes=f"exception: {e}")
            logger.exception("DOCX extractor raised exception")

    # ---------- 4. PyPDF2 fallback ----------
    if not success and file_path.suffix.lower() == ".pdf":
        try:
            logger.info("Attempt 4: PyPDF2 fallback")
            if hasattr(extractor97, "extract_text_with_pypdf2_fallback"):
                text = extractor97.extract_text_with_pypdf2_fallback(file_path)
            else:
                # simple fallback manual attempt
                import PyPDF2
                with open(file_path, "rb") as f:
                    r = PyPDF2.PdfReader(f)
                    pages_text = []
                    for p in r.pages:
                        try:
                            pages_text.append(p.extract_text() or "")
                        except Exception:
                            continue
                    text = "\n\n".join(pages_text) or None
            record_attempt("pypdf2", text)
            score = quality_score(text or "", file_path)
            logger.info(f"PyPDF2 quality score: {score:.1f}")
            if text and score >= quality_threshold:
                last_text = text
                success_module = "pypdf2"
                success = True
            else:
                logger.info("PyPDF2 failed or low quality.")
        except Exception as e:
            record_attempt("pypdf2", None, notes=f"exception: {e}")
            logger.exception("PyPDF2 fallback raised exception")

    # ---------- 5. OCR via Tesseract (via pdf2image/poppler) ----------
    if not success and file_path.suffix.lower() == ".pdf":
        try:
            logger.info("Attempt 5: OCR via Tesseract (pdf2image -> pytesseract)")
            # Use extractor's OCR routine if it exposes one
            # try final extractor OCR function names
            text = None
            if hasattr(extractor97, "extract_text_with_poppler_optimization"):
                text = extractor97.extract_text_with_poppler_optimization(file_path)
            else:
                # Minimal common approach: pdf2image -> pytesseract
                from pdf2image import convert_from_path
                import pytesseract
                pages = convert_from_path(str(file_path))
                page_texts = []
                for page_img in pages:
                    page_texts.append(pytesseract.image_to_string(page_img))
                text = "\n\n".join(page_texts) if page_texts else None

            record_attempt("tesseract_ocr", text)
            score = quality_score(text or "", file_path)
            logger.info(f"Tesseract OCR quality score: {score:.1f}")
            if text and score >= quality_threshold:
                last_text = text
                success_module = "tesseract_ocr"
                success = True
            else:
                logger.info("Tesseract OCR failed or produced low quality.")
        except Exception as e:
            record_attempt("tesseract_ocr", None, notes=f"exception: {e}")
            logger.exception("Tesseract OCR raised exception")

    # ---------- 6. NEW: OpenCV preprocessing -> Tesseract (retry) ----------
    if not success and file_path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}:
        try:
            logger.info("Attempt 6: OpenCV preprocess + Tesseract retry")
            # Convert pdf page(s) to images first (use pdf2image)
            from pdf2image import convert_from_path
            images = []
            if file_path.suffix.lower() == ".pdf":
                images = convert_from_path(str(file_path))
            else:
                # image file
                import PIL.Image as PILImage
                images = [PILImage.open(str(file_path))]

            # process each page: save temp, preprocess, OCR
            import tempfile
            import pytesseract
            page_texts = []
            for idx, pil_img in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_in:
                    pil_img.save(tmp_in.name, format="PNG")
                    tmp_in_path = Path(tmp_in.name)
                tmp_out = tmp_in_path.with_name(tmp_in_path.stem + "_cv.png")
                processed = opencv_preprocess_pdf_image(tmp_in_path, tmp_out)
                ocr_source = tmp_out if processed else tmp_in_path
                try:
                    txt = pytesseract.image_to_string(str(ocr_source))
                except Exception:
                    txt = ""
                page_texts.append(txt)
            text = "\n\n".join(t for t in page_texts if t.strip())
            record_attempt("opencv_tesseract_retry", text)
            score = quality_score(text or "", file_path)
            logger.info(f"OpenCV+Tesseract quality score: {score:.1f}")
            if text and score >= quality_threshold:
                last_text = text
                success_module = "opencv_tesseract_retry"
                success = True
            else:
                logger.info("OpenCV+Tesseract retry failed or low quality.")
        except Exception as e:
            record_attempt("opencv_tesseract_retry", None, notes=f"exception: {e}")
            logger.exception("OpenCV preprocessing or retry failed")

    # ---------- 7. NEW: PaddleOCR fallback ----------
    if not success and file_path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}:
        try:
            logger.info("Attempt 7: PaddleOCR fallback")
            # Convert to images (pdf2image for PDFs) then run paddle_extract_from_image
            from pdf2image import convert_from_path
            import tempfile
            images = []
            if file_path.suffix.lower() == ".pdf":
                images = convert_from_path(str(file_path))
            else:
                import PIL.Image as PILImage
                images = [PILImage.open(str(file_path))]

            page_texts = []
            for idx, pil_img in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
                    pil_img.save(t.name, format="PNG")
                    tpath = Path(t.name)
                txt = paddle_extract_from_image(tpath)
                page_texts.append(txt)
            text = "\n\n".join([t for t in page_texts if t and t.strip()])
            record_attempt("paddleocr", text)
            score = quality_score(text or "", file_path)
            logger.info(f"PaddleOCR quality score: {score:.1f}")
            if text and score >= quality_threshold:
                last_text = text
                success_module = "paddleocr"
                success = True
            else:
                logger.info("PaddleOCR failed or low quality.")
        except Exception as e:
            record_attempt("paddleocr", None, notes=f"exception: {e}")
            logger.exception("PaddleOCR fallback raised exception")

    # Finalize
    final_score = quality_score(last_text or "", file_path)
    total_length = len(last_text or "")
    logbook.record(str(file_path), file_size, page_count, attempts, success_module or "", success, total_length, final_score, metadata or {})

    return {
        "success": success,
        "module": success_module,
        "text": last_text,
        "score": final_score,
        "attempts": attempts
    }