from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import WorkflowResult
from app.services.steps.base import WorkflowContext
from app.utils.logging import get_logger, log_event

logger = get_logger(__name__)


@dataclass
class RoutingStep:
    def run(self, ctx: WorkflowContext) -> None:
        if ctx.validation_errors:
            ctx.status = "manual_review"
        else:
            ctx.status = "auto_processed"

        triage = ctx.triage
        ctx.result = WorkflowResult(
            status=ctx.status,
            category=triage.category if triage else None,
            urgency=triage.urgency if triage else None,
            confidence=triage.confidence if triage else None,
            draft_reply=triage.draft_reply if triage else None,
            manual_review_reasons=ctx.validation_errors,
            llm_raw_output=ctx.llm_raw_output,
        )
        log_event(
            logger,
            "routing_complete",
            request_id=ctx.request_id,
            status=ctx.status,
            reasons=ctx.validation_errors,
        )
