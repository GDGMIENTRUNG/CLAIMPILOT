from datetime import datetime, date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
ComplaintType = Literal["late_delivery", "not_received", "damaged_item", "wrong_item", "refund_request", "other"]
CaseStatus = Literal["processing", "pending_review", "insufficient_information", "processing_failed", "processed"]
class Analysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_complaint: bool
    complaint_type: ComplaintType
    order_id: str | None = Field(max_length=100)
    requested_action: Literal["shipping_fee_refund", "order_refund", "replacement", "request_information", "other"]
    summary: str = Field(min_length=1, max_length=4000)
    missing_information: list[str] = Field(max_length=30)
    priority: Literal["low", "medium", "high"]
    @field_validator("order_id")
    @classmethod
    def normalize_order(cls, v):
        return v.strip() or None if v is not None else None
class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: str
    customer_email: str
    order_status: str
    expected_delivery_date: date | None
    actual_delivery_date: date | None
    shipping_fee: Decimal
class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    gmail_message_id: str
    sender_email: str
    email_subject: str
    received_at: datetime
    complaint_type: str | None
    order_id: str | None
    requested_action: str | None
    priority: str | None
    policy_result: str | None
    case_status: str
    processing_error: str | None
class ComplaintDetail(ComplaintOut):
    email_body: str
    ai_summary: str | None
    missing_information: list[str]
    verification_status: str
    sender_matches_order: bool | None
    verified_order: OrderOut | None
    policy_reason: str | None
    created_at: datetime
    updated_at: datetime
class ComplaintPage(BaseModel):
    items: list[ComplaintOut]
    total: int
    page: int
    page_size: int
class Stats(BaseModel):
    total: int
    pending_review: int
    insufficient_information: int
    processed: int
class SyncIssue(BaseModel):
    message_id: str
    error: str
class SyncResult(BaseModel):
    successful: int = 0
    skipped: int = 0
    failed: int = 0
    deferred: int = 0
    errors: list[SyncIssue] = Field(default_factory=list)
class Health(BaseModel):
    status: str
class IntegrationStatus(BaseModel):
    gmail_configured: bool
    gemini_configured: bool
    ai_provider: str
    ai_model: str
    ai_configured: bool
    note: str
