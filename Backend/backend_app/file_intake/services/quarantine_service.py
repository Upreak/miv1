# file_intake/services/quarantine_service.py
from pathlib import Path
from shutil import move

DATA_ROOT = Path("/data")

def save_local_upload(temp_path: str, qid: str, filename: str) -> str:
    dest_dir = Path("/data/quarantine") / qid
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    move(temp_path, dest)
    return str(dest)