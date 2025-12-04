# file_intake/services/sanitizer_service.py
from pathlib import Path
from backend_app.text_extraction.utils import sanitize_filename  # reuse existing util.

def sanitize_and_normalize(path: str) -> str:
    p = Path(path)
    safe = sanitize_filename(p.name)
    dest = p.with_name(safe)
    # rename safe
    if p != dest:
        p.rename(dest)
    # optional: strip PDF metadata or normalize using external tools here
    return str(dest)