import os

from fastapi.testclient import TestClient

# Set env vars before importing app modules so settings picks them up.
os.environ["DATABASE_URL"] = "sqlite:///./test_manual.db"
os.environ["LLM_MODE"] = "mock"
os.environ["CONFIDENCE_THRESHOLD"] = "0.75"

from app.db.database import init_db
from app.main import create_app


def test_manual_review_low_confidence() -> None:
    app = create_app()
    init_db()
    client = TestClient(app)

    payload = {
        "customer_email": "john@example.com",
        "customer_name": "John",
        "subject": "Question about my order",
        "message": "I am not sure what happened with my order and unsure what to do.",
    }

    response = client.post("/api/v1/tickets/process", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "manual_review"
    assert "low_confidence" in body["manual_review_reasons"]
    assert body["ticket_id"] > 0


def test_manual_review_missing_order_id_for_payment_issue() -> None:
    app = create_app()
    init_db()
    client = TestClient(app)

    payload = {
        "customer_email": "amy@example.com",
        "customer_name": "Amy",
        "subject": "Payment issue",
        "message": "I was charged twice and need help with payment.",
    }

    response = client.post("/api/v1/tickets/process", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "manual_review"
    assert "missing_required_order_id" in body["manual_review_reasons"]
