# file_intake/utils/qid_generator.py
import uuid
from datetime import datetime

def generate_qid() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short = uuid.uuid4().hex[:10]
    return f"QID-{ts}-{short}"