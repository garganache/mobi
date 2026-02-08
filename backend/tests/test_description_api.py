import os
from fastapi.testclient import TestClient

# Ensure we use a local SQLite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app, init_db  # noqa: E402


client = TestClient(app)


def setup_module(module):  # type: ignore[override]
    # Recreate DB for a clean slate
    init_db()


def test_create_description_and_get_latest():
    # Initially, no description
    resp = client.get("/description/latest")
    assert resp.status_code == 404

    # Create one description
    payload = {"text": "First test description"}
    resp = client.post("/description", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["text"] == payload["text"]
    assert "id" in data

    # Latest should now return this description
    resp = client.get("/description/latest")
    assert resp.status_code == 200
    latest = resp.json()
    assert latest["text"] == payload["text"]


def test_empty_description_rejected():
    resp = client.post("/description", json={"text": "   "})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Description cannot be empty"
