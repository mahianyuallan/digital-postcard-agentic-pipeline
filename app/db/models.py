from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ProcessedTicket(Base):
    __tablename__ = "processed_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    order_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    customer_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    draft_reply: Mapped[str | None] = mapped_column(Text, nullable=True)

    manual_review_reasons: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    llm_raw_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
