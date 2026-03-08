from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketCategory(str, Enum):
    refund_request = "refund_request"
    payment_issue = "payment_issue"
    delivery_complaint = "delivery_complaint"
    wrong_recipient = "wrong_recipient"
    general_support = "general_support"


class UrgencyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TicketRequest(BaseModel):
    customer_email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=5, max_length=4000)
    order_id: str | None = Field(default=None, max_length=80)
    customer_name: str | None = Field(default=None, max_length=120)


class LLMTriageOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: TicketCategory
    urgency: UrgencyLevel
    confidence: float = Field(ge=0.0, le=1.0)
    extracted_fields: dict[str, Any] = Field(default_factory=dict)
    draft_reply: str = Field(min_length=20, max_length=2000)


class TicketProcessResponse(BaseModel):
    ticket_id: int
    status: str
    category: TicketCategory | None = None
    urgency: UrgencyLevel | None = None
    confidence: float | None = None
    draft_reply: str | None = None
    manual_review_reasons: list[str] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    status: str
    category: TicketCategory | None = None
    urgency: UrgencyLevel | None = None
    confidence: float | None = None
    draft_reply: str | None = None
    manual_review_reasons: list[str] = Field(default_factory=list)
    llm_raw_output: dict[str, Any] | None = None
