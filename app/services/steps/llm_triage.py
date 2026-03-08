from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from app.models.schemas import LLMTriageOutput
from app.services.llm_service import LLMService
from app.services.steps.base import WorkflowContext
from app.utils.logging import get_logger, log_event

logger = get_logger(__name__)


@dataclass
class LLMTriageStep:
    llm_service: LLMService
    max_retries: int = 1

    def run(self, ctx: WorkflowContext) -> None:
        attempts = self.max_retries + 1
        last_error: str | None = None

        for attempt in range(1, attempts + 1):
            try:
                raw = self.llm_service.triage_ticket(ctx.ticket)
                ctx.llm_raw_output = raw
                ctx.triage = LLMTriageOutput.model_validate(raw)
                log_event(logger, "llm_triage_success", request_id=ctx.request_id, attempt=attempt)
                return
            except (httpx.HTTPError, TimeoutError) as exc:
                last_error = f"transient_llm_error: {str(exc)}"
                log_event(logger, "llm_triage_transient_error", request_id=ctx.request_id, attempt=attempt, error=str(exc))
            except (json.JSONDecodeError, ValueError, KeyError) as exc:
                last_error = f"invalid_llm_output: {str(exc)}"
                log_event(logger, "llm_triage_invalid_output", request_id=ctx.request_id, attempt=attempt, error=str(exc))
                break
            except Exception as exc:
                last_error = f"unexpected_llm_error: {str(exc)}"
                log_event(logger, "llm_triage_unexpected_error", request_id=ctx.request_id, attempt=attempt, error=str(exc))
                break

        ctx.validation_errors.append(last_error or "llm_call_failed")
