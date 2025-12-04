# file_intake/services/extraction_service.py
from pathlib import Path
from backend_app.text_extraction.consolidated_extractor import extract_with_logging  # consolidated extractor.

def extract_text_for_qid(path: str, metadata: dict = None, quality_threshold: float = 70.0):
    p = Path(path)
    result = extract_with_logging(file_path=p, metadata=metadata or {}, quality_threshold=quality_threshold)
    return result