from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Text, DateTime, Numeric, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint("shipping_fee >= 0"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(100), unique=True)
    customer_email: Mapped[str] = mapped_column(String(320))
    order_status: Mapped[str] = mapped_column(String(40))
    expected_delivery_date: Mapped[date | None]
    actual_delivery_date: Mapped[date | None]
    shipping_fee: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint("case_status IN ('processing','pending_review','insufficient_information','processing_failed','processed')"),
        CheckConstraint("priority IS NULL OR priority IN ('low','medium','high')"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    gmail_message_id: Mapped[str] = mapped_column(String(200), unique=True)
    sender_email: Mapped[str] = mapped_column(String(320))
    email_subject: Mapped[str] = mapped_column(Text)
    email_body: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    complaint_type: Mapped[str | None] = mapped_column(String(40), index=True)
    order_id: Mapped[str | None] = mapped_column(String(100))
    verified_order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    verified_order: Mapped[Order | None] = relationship()
    requested_action: Mapped[str | None] = mapped_column(String(40))
    ai_summary: Mapped[str | None] = mapped_column(Text)
    missing_information: Mapped[list] = mapped_column(JSONB, default=list)
    priority: Mapped[str | None] = mapped_column(String(10))
    verification_status: Mapped[str] = mapped_column(String(40), default="not_checked")
    sender_matches_order: Mapped[bool | None]
    policy_result: Mapped[str | None] = mapped_column(String(40))
    policy_reason: Mapped[str | None] = mapped_column(Text)
    case_status: Mapped[str] = mapped_column(String(40), default="processing", index=True)
    processing_error: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
