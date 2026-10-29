from datetime import date
from sqlalchemy.dialects.postgresql import insert
from app.database import SessionLocal
from app.models import Order

def seed(db):
    for identifier, actual, fee in [("DH001", date(2026,10,27), 40000), ("DH002", date(2026,10,25), 20000), ("DH003", None, 30000)]:
        db.execute(insert(Order).values(order_id=identifier, customer_email=f"{identifier.lower()}@example.com",
            order_status="Delivered" if actual else "In Transit", expected_delivery_date=date(2026,10,25) if actual else date(2026,10,29),
            actual_delivery_date=actual, shipping_fee=fee).on_conflict_do_nothing(index_elements=[Order.order_id]))
    db.commit()
if __name__ == "__main__":
    with SessionLocal() as db:
        seed(db)
    print("Sample orders seeded (existing orders preserved).")
