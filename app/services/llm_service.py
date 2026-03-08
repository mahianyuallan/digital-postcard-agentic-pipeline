from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.schemas import TicketRequest


class LLMService(ABC):
    @abstractmethod
    def triage_ticket(self, ticket: TicketRequest) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMService(LLMService):
    def triage_ticket(self, ticket: TicketRequest) -> dict[str, Any]:
        message = ticket.message.lower()
        subject = ticket.subject.lower()
        text = f"{subject} {message}"

        category = "general_support"
        urgency = "medium"
        confidence = 0.88

        if "refund" in text:
            category = "refund_request"
            urgency = "high"
        elif "payment" in text or "charged" in text:
            category = "payment_issue"
            urgency = "high"
        elif "delivery" in text or "arrive" in text or "late" in text:
            category = "delivery_complaint"
        elif "wrong recipient" in text or "wrong address" in text:
            category = "wrong_recipient"

        if "unsure" in text or "not sure" in text:
            confidence = 0.42

        draft_reply = (
            f"Hi {ticket.customer_name or 'there'}, thanks for contacting Digital Postcard support. "
            "We have reviewed your request and started handling it. "
            "If needed, our team will follow up with any additional details shortly."
        )

        return {
            "category": category,
            "urgency": urgency,
            "confidence": confidence,
            "extracted_fields": {
                "order_id": ticket.order_id,
                "customer_email": ticket.customer_email,
            },
            "draft_reply": draft_reply,
        }


class OpenAILLMService(LLMService):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_MODE=openai")
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.timeout = settings.llm_timeout_seconds

    def triage_ticket(self, ticket: TicketRequest) -> dict[str, Any]:
        system_prompt = (
            "You are a support triage assistant for a digital postcard startup. "
            "Return ONLY valid JSON with keys: category, urgency, confidence, extracted_fields, draft_reply. "
            "Allowed categories: refund_request, payment_issue, delivery_complaint, wrong_recipient, general_support. "
            "Urgency must be one of: low, medium, high. Confidence must be 0-1 float."
        )
        user_prompt = (
            f"customer_email: {ticket.customer_email}\n"
            f"customer_name: {ticket.customer_name}\n"
            f"order_id: {ticket.order_id}\n"
            f"subject: {ticket.subject}\n"
            f"message: {ticket.message}\n"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("OpenAI response content must be a JSON object")
        return parsed


def get_llm_service() -> LLMService:
    settings = get_settings()
    if settings.llm_mode.lower() == "openai":
        return OpenAILLMService()
    return MockLLMService()
