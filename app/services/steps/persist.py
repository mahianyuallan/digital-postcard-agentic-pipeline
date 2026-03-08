from __future__ import annotations

from dataclasses import dataclass

from app.db.models import ProcessedTicket
from app.services.steps.base import WorkflowContext
from app.utils.logging import get_logger, log_event

logger = get_logger(__name__)


@dataclass
class PersistStep:
    def run(self, ctx: WorkflowContext) -> None:
        if ctx.result is None:
            raise ValueError("workflow result must be set before persistence")

        triage = ctx.triage
        row = ProcessedTicket(
            customer_email=str(ctx.ticket.customer_email),
            subject=ctx.ticket.subject,
            message=ctx.ticket.message,
            order_id=ctx.ticket.order_id,
            customer_name=ctx.ticket.customer_name,
            status=ctx.result.status,
            category=triage.category.value if triage else None,
            urgency=triage.urgency.value if triage else None,
            confidence=triage.confidence if triage else None,
            draft_reply=triage.draft_reply if triage else None,
            manual_review_reasons=ctx.result.manual_review_reasons,
            llm_raw_output=ctx.result.llm_raw_output,
        )
        ctx.db.add(row)
        ctx.db.flush()

        ctx.persisted_ticket_id = row.id

        log_event(
            logger,
            "ticket_persisted",
            request_id=ctx.request_id,
            ticket_id=row.id,
            status=row.status,
        )
