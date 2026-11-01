from threading import Lock
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.models import Complaint
from app.schemas import SyncResult, SyncIssue
from app.services.errors import IntegrationError
from app.services.policy import assess

sync_lock = Lock()

def analyze_saved_complaint(db, record, gemini):
    record.case_status = "processing"
    record.processing_error = None
    db.commit()
    try:
        analysis = gemini.analyze(record.email_subject, record.email_body)
        record.is_complaint = analysis.is_complaint
        record.complaint_type = analysis.complaint_type
        record.order_id = analysis.order_id
        record.requested_action = analysis.requested_action
        record.ai_summary = analysis.summary
        record.missing_information = analysis.missing_information
        record.priority = analysis.priority
        if not analysis.is_complaint:
            record.verified_order_id = None
            record.verification_status = "not_checked"
            record.sender_matches_order = None
            record.policy_result = "not_applicable"
            record.policy_reason = "The email was classified as unrelated to a customer complaint."
            record.case_status = "processed"
            record.processing_error = None
            db.commit()
            return record
        order, verification, matches, policy_result, reason = assess(db, analysis, record.sender_email)
        record.verified_order_id = order.id if order else None
        record.verification_status = verification
        record.sender_matches_order = matches
        record.policy_result = policy_result
        record.policy_reason = reason
        record.case_status = "insufficient_information" if policy_result == "insufficient_information" else "pending_review"
        record.processing_error = None
        db.commit()
        db.expire(record, ["verified_order"])
        return record
    except IntegrationError as exc:
        db.rollback()
        record.case_status = "processing_failed"
        record.processing_error = exc.code
        db.commit()
        raise

def synchronize(db, gmail, gemini):
    result = SyncResult()
    # Retry saved failures even if the original message no longer matches the query.
    failed_ids = list(db.scalars(select(Complaint.gmail_message_id).where(Complaint.case_status.in_(["processing_failed", "processing"])).order_by(Complaint.id).limit(settings.gmail_batch_size))) if settings.gmail_retry_failed else []
    known_ids = set(db.scalars(select(Complaint.gmail_message_id).where(Complaint.case_status.not_in(["processing_failed", "processing"]))))
    ids = list(dict.fromkeys(failed_ids + gmail.list_ids(known_ids=known_ids)))
    attempted = 0
    for index, message_id in enumerate(ids):
        record = db.scalar(select(Complaint).where(Complaint.gmail_message_id == message_id))
        if record and record.case_status not in {"processing_failed", "processing"}:
            result.skipped += 1
            continue
        if attempted >= settings.gmail_batch_size:
            result.deferred += 1
            continue
        attempted += 1
        try:
            if record is None:
                record = Complaint(**gmail.get_message(message_id))
                db.add(record)
                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()
                    if db.scalar(select(Complaint.id).where(Complaint.gmail_message_id == message_id)) is None:
                        raise
                    result.skipped += 1
                    continue
            analyzed = analyze_saved_complaint(db, record, gemini)
            if analyzed.is_complaint:
                result.successful += 1
            else:
                result.skipped += 1
        except IntegrationError as exc:
            db.rollback()
            if record is not None and record.id is not None:
                record.case_status = "processing_failed"
                record.processing_error = exc.code
                db.commit()
            result.failed += 1
            result.errors.append(SyncIssue(message_id=message_id, error=exc.code))
            # A provider-wide error will also affect the rest of this batch.
            if exc.code.startswith(("gemini_", "groq_")):
                result.deferred += sum(
                    ident not in known_ids for ident in ids[index + 1:]
                )
                break
    return result
