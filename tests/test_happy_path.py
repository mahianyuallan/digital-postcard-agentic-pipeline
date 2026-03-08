import os

from fastapi.testclient import TestClient

# Set env vars before importing app modules so settings picks them up.
os.environ["DATABASE_URL"] = "sqlite:///./test_happy.db"
os.environ["LLM_MODE"] = "mock"
os.environ["CONFIDENCE_THRESHOLD"] = "0.75"

from app.db.database import init_db
from app.main import create_app


def test_happy_path_auto_processed() -> None:
    app = create_app()
    init_db()
    client = TestClient(app)

    payload = {
        "customer_email": "jane@example.com",
        "customer_name": "Jane",
        "order_id": "ORD-101",
        "subject": "Refund needed",
        "message": "I want a refund because my postcard never arrived.",
    }

    response = client.post("/api/v1/tickets/process", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "auto_processed"
    assert body["category"] == "refund_request"
    assert body["ticket_id"] > 0
    assert body["manual_review_reasons"] == []
