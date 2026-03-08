from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.models.schemas import TicketCategory
from app.services.steps.base import WorkflowContext
from app.utils.logging import get_logger, log_event

logger = get_logger(__name__)
TRANSACTIONAL_CATEGORIES = {
    TicketCategory.refund_request,
    TicketCategory.payment_issue,
    TicketCategory.delivery_complaint,
}


@dataclass
class ValidationGateStep:
    def run(self, ctx: WorkflowContext) -> None:
        settings = get_settings()

        if ctx.triage is None:
            ctx.validation_errors.append("missing_or_invalid_llm_triage_output")
            log_event(logger, "validation_failed", request_id=ctx.request_id, reason="missing_triage")
            return

        if ctx.triage.category not in set(TicketCategory):
            ctx.validation_errors.append("invalid_category")

        if not (0.0 <= ctx.triage.confidence <= 1.0):
            ctx.validation_errors.append("confidence_out_of_range")

        if ctx.triage.confidence < settings.confidence_threshold:
            ctx.validation_errors.append("low_confidence")

        extracted_order_id = None
        if isinstance(ctx.triage.extracted_fields, dict):
            extracted_order_id = ctx.triage.extracted_fields.get("order_id")

        if ctx.triage.category in TRANSACTIONAL_CATEGORIES and not (ctx.ticket.order_id or extracted_order_id):
            ctx.validation_errors.append("missing_required_order_id")

        if ctx.validation_errors:
            log_event(
                logger,
                "validation_failed",
                request_id=ctx.request_id,
                reasons=ctx.validation_errors,
            )
        else:
            log_event(logger, "validation_passed", request_id=ctx.request_id)
