from sqlalchemy import select
from app.models import Order

def assess(db, analysis, sender):
    if not analysis.order_id:
        return None, "missing_order_id", None, "insufficient_information", "An order ID is required."
    order = db.scalar(select(Order).where(Order.order_id == analysis.order_id))
    if order is None:
        return None, "order_not_found", None, "order_not_found", "The extracted order ID was not found in the database."
    matches = sender.casefold() == order.customer_email.casefold()
    if order.order_status.casefold() != "delivered":
        status = "not_delivered" if order.actual_delivery_date is None else "insufficient_data"
        return order, status, matches, "insufficient_information", "Delivery is not confirmed by a consistent database record."
    if not order.expected_delivery_date or not order.actual_delivery_date:
        return order, "insufficient_data", matches, "insufficient_information", "Required delivery dates are missing."
    if not matches:
        return order, "delivered", matches, "insufficient_information", "Sender differs from the order customer; staff must verify ownership."
    if order.actual_delivery_date <= order.expected_delivery_date:
        return order, "delivered", matches, "not_eligible", "Database dates show delivery on or before the expected date; no late-delivery shipping refund applies."
    if analysis.requested_action == "shipping_fee_refund":
        return order, "delivered", matches, "eligible_for_review", "Database dates confirm late delivery and the email requests a shipping-fee refund. Staff review is required; no refund has been issued."
    return order, "delivered", matches, "insufficient_information", "This request is outside the sample late-delivery shipping-refund policy; staff review is required."
