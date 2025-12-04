# file_intake/tests/test_qid_generator.py
from backend_app.file_intake.utils.qid_generator import generate_qid

def test_qid_format():
    q = generate_qid()
    assert q.startswith("QID-") and len(q.split("-")) == 3