from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.models.schemas import LLMTriageOutput, TicketRequest, WorkflowResult


@dataclass
class WorkflowContext:
    request_id: str
    ticket: TicketRequest
    db: Session
    llm_raw_output: dict[str, Any] | None = None
    triage: LLMTriageOutput | None = None
    validation_errors: list[str] = field(default_factory=list)
    status: str = "manual_review"
    persisted_ticket_id: int | None = None
    result: WorkflowResult | None = None
