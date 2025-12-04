# file_intake/tests/test_intake_router.py
from fastapi.testclient import TestClient
from backend_app.main import app
client = TestClient(app)

def test_initiate_upload():
    payload = {"filename": "resume.pdf", "mime": "application/pdf", "size": 12345}
    r = client.post("/intake/initiate-upload", json=payload)
    assert r.status_code == 200
    assert "qid" in r.json()