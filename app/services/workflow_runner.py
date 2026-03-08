from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.schemas import TicketProcessResponse, TicketRequest
from app.services.llm_service import get_llm_service
from app.services.steps.base import WorkflowContext
from app.services.steps.llm_triage import LLMTriageStep
from app.services.steps.persist import PersistStep
from app.services.steps.route import RoutingStep
from app.services.steps.validate import ValidationGateStep


@dataclass
class WorkflowRunner:
    steps: list

    def run(self, ctx: WorkflowContext) -> WorkflowContext:
        for step in self.steps:
            step.run(ctx)
        return ctx


class SupportTriageWorkflow:
    def __init__(self) -> None:
        self.runner = WorkflowRunner(
            steps=[
                LLMTriageStep(llm_service=get_llm_service(), max_retries=1),
                ValidationGateStep(),
                RoutingStep(),
                PersistStep(),
            ]
        )

    def execute(self, request_id: str, ticket: TicketRequest, db: Session) -> TicketProcessResponse:
        ctx = WorkflowContext(request_id=request_id, ticket=ticket, db=db)
        result_ctx = self.runner.run(ctx)

        if result_ctx.result is None or result_ctx.persisted_ticket_id is None:
            raise ValueError("workflow completed without result or persisted ticket id")

        result = result_ctx.result
        return TicketProcessResponse(
            ticket_id=result_ctx.persisted_ticket_id,
            status=result.status,
            category=result.category,
            urgency=result.urgency,
            confidence=result.confidence,
            draft_reply=result.draft_reply,
            manual_review_reasons=result.manual_review_reasons,
        )
