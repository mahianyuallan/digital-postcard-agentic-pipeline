from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.schemas import TicketProcessResponse, TicketRequest
from app.services.workflow_runner import SupportTriageWorkflow
from app.utils.logging import get_logger, log_event

router = APIRouter(prefix="/tickets", tags=["tickets"])
logger = get_logger(__name__)


@router.post("/process", response_model=TicketProcessResponse)
def process_ticket(payload: TicketRequest, db: Session = Depends(get_db)) -> TicketProcessResponse:
    request_id = str(uuid.uuid4())
    workflow = SupportTriageWorkflow()

    log_event(logger, "ticket_received", request_id=request_id, customer_email=str(payload.customer_email))

    response = workflow.execute(request_id=request_id, ticket=payload, db=db)

    log_event(
        logger,
        "ticket_processed",
        request_id=request_id,
        ticket_id=response.ticket_id,
        status=response.status,
    )
    return response


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
