"""
Seed script — loads CSV data into the database and computes behaviour_stats.

Usage:
    python -m backend.seed

Idempotent: skips seeding if data already exists.
"""

import os
import sys
import logging
import pandas as pd
from datetime import date, time, timedelta
from collections import defaultdict

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.app.database.connection import engine, Base, SessionLocal
from backend.app.models.customer import Customer, CustomerSegment, CSV_SEGMENT_MAP
from backend.app.models.slot import Slot, SlotStatus
from backend.app.models.booking import Booking
from backend.app.models.behaviour_stats import BehaviourStats
from backend.app.models.notification import Notification
from backend.app.models.agent_activity import AgentActivity

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ── Time slots for each sport ────────────────────────────────────────────
SPORT_SLOTS = {
    "Badminton":           {"duration": 60, "price": 400, "start": 6, "end": 22},
    "Tennis":              {"duration": 60, "price": 600, "start": 6, "end": 22},
    "Football (5-a-side)": {"duration": 60, "price": 900, "start": 6, "end": 22},
    "Football (7-a-side)": {"duration": 60, "price": 1200, "start": 6, "end": 22},
    "Futsal":              {"duration": 60, "price": 850, "start": 6, "end": 22},
    "Box Cricket":         {"duration": 60, "price": 1200, "start": 6, "end": 22},
}


def seed_customers(db):
    """Load customers from CSV."""
    existing = db.query(Customer).count()
    if existing > 0:
        logger.info(f"Customers already seeded ({existing} records). Skipping.")
        return

    csv_path = os.path.join(DATA_DIR, "customers.csv")
    if not os.path.exists(csv_path):
        logger.error(f"Customer CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    customers = []
    for _, row in df.iterrows():
        segment = CSV_SEGMENT_MAP.get(row["segment"], CustomerSegment.OTHER)
        customers.append(Customer(
            id=row["id"],
            name=row["name"],
            segment=segment,
            age=int(row["age"]) if pd.notna(row["age"]) else None,
            sport=row["sport"] if pd.notna(row.get("sport")) else None,
        ))

    db.add_all(customers)
    db.commit()
    logger.info(f"Seeded {len(customers)} customers")


def seed_slots(db):
    """Generate slot records from the bookings CSV.

    Strategy:
    - Extract unique (slot_id, date, sport, price) from bookings
    - For those booked slots, mark them BOOKED
    - Generate additional VACANT slots for demo
    """
    existing = db.query(Slot).count()
    if existing > 0:
        logger.info(f"Slots already seeded ({existing} records). Skipping.")
        return

    csv_path = os.path.join(DATA_DIR, "bookings.csv")
    if not os.path.exists(csv_path):
        logger.error(f"Bookings CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Build a mapping of slot IDs to their info from bookings
    slot_info = {}
    for _, row in df.iterrows():
        sid = row["slot_id"]
        if sid not in slot_info:
            slot_info[sid] = {
                "sport": row["sport"],
                "date": row["date"],
                "price": float(row["price"]),
                "discount": float(row["discount"]) if pd.notna(row.get("discount")) else 0.0,
            }

    # Generate time for each slot based on its numeric ID
    # SL0001 → slot index 0, etc.
    slots = []
    for sid, info in slot_info.items():
        num = int(sid.replace("SL", ""))
        sport_config = SPORT_SLOTS.get(info["sport"], SPORT_SLOTS["Badminton"])

        # Distribute across hours of the day
        total_hours = sport_config["end"] - sport_config["start"]
        hour_offset = num % total_hours
        start_hour = sport_config["start"] + hour_offset

        slot = Slot(
            id=sid,
            sport=info["sport"],
            date=info["date"],
            start_time=time(start_hour, 0),
            end_time=time(start_hour + 1, 0) if start_hour < 23 else time(23, 0),
            price=info["price"],
            status=SlotStatus.BOOKED,
            discount_percent=info["discount"],
            final_price=info["price"] * (1 - info["discount"] / 100) if info["discount"] else info["price"],
        )
        slots.append(slot)

    # Generate some VACANT slots for demo purposes
    # Use dates from the dataset + a few future dates
    dates_in_data = sorted(set(info["date"] for info in slot_info.values()))
    demo_date = max(dates_in_data) + timedelta(days=1) if dates_in_data else date.today()

    vacant_id_start = max(int(sid.replace("SL", "")) for sid in slot_info.keys()) + 1

    for sport, config in SPORT_SLOTS.items():
        for hour in range(config["start"], config["end"], 2):  # Every 2 hours
            sid = f"SL{vacant_id_start:04d}"
            vacant_id_start += 1
            slot = Slot(
                id=sid,
                sport=sport,
                date=demo_date,
                start_time=time(hour, 0),
                end_time=time(hour + 1, 0),
                price=config["price"],
                status=SlotStatus.VACANT,
                discount_percent=0.0,
                final_price=config["price"],
            )
            slots.append(slot)

    db.add_all(slots)
    db.commit()
    logger.info(f"Seeded {len(slots)} slots ({len(slot_info)} booked + {len(slots) - len(slot_info)} vacant)")


def seed_bookings(db):
    """Load booking records from CSV (marks historical bookings)."""
    existing = db.query(Booking).count()
    if existing > 0:
        logger.info(f"Bookings already seeded ({existing} records). Skipping.")
        return

    csv_path = os.path.join(DATA_DIR, "bookings.csv")
    df = pd.read_csv(csv_path)

    bookings = []
    for _, row in df.iterrows():
        price = float(row["price"])
        discount = float(row["discount"]) if pd.notna(row.get("discount")) else 0.0
        final_price = price * (1 - discount / 100)

        booking = Booking(
            id=row["id"],
            customer_id=row["customer_id"],
            slot_id=row["slot_id"],
            original_price=price,
            discount_percent=discount,
            final_price=final_price,
        )
        bookings.append(booking)

    db.add_all(bookings)
    db.commit()
    logger.info(f"Seeded {len(bookings)} bookings")


def compute_behaviour_stats(db):
    """Compute behaviour_stats from the bookings + customers + slots data.

    Groups by (segment, sport, day_of_week, hour) and calculates:
    - fill_rate: proportion of slots booked
    - avg_time_to_book: average lead time (simulated from data)
    - conversion_rate: bookings / available customers in segment
    - num_bookings: total bookings for this combination
    """
    existing = db.query(BehaviourStats).count()
    if existing > 0:
        logger.info(f"Behaviour stats already computed ({existing} records). Skipping.")
        return

    # Load all data
    slots = {s.id: s for s in db.query(Slot).all()}
    customers = db.query(Customer).all()
    bookings = db.query(Booking).all()

    # Count customers per segment
    segment_counts = defaultdict(int)
    for c in customers:
        segment_counts[c.segment.value] += 1

    # Map customer_id → segment
    customer_segments = {c.id: c.segment.value for c in customers}

    # Total slots per (sport, day, hour)
    slot_counts = defaultdict(int)
    for s in slots.values():
        key = (s.sport, s.date.weekday(), s.start_time.hour)
        slot_counts[key] += 1

    # Aggregate bookings by (segment, sport, day_of_week, hour)
    booking_agg = defaultdict(lambda: {"count": 0, "total_lead_minutes": 0})
    for b in bookings:
        slot = slots.get(b.slot_id)
        if not slot:
            continue
        segment = customer_segments.get(b.customer_id, "OTHER")
        day = slot.date.weekday()
        hour = slot.start_time.hour
        key = (segment, slot.sport, day, hour)
        booking_agg[key]["count"] += 1
        # Simulate lead time: hash-based deterministic minutes (30-480 range)
        lead_min = 30 + (hash(b.id) % 450)
        booking_agg[key]["total_lead_minutes"] += lead_min

    # Build stats records
    stats = []
    for (segment, sport, day, hour), agg in booking_agg.items():
        num_bookings = agg["count"]
        total_slots = slot_counts.get((sport, day, hour), 1)
        seg_count = segment_counts.get(segment, 1)

        fill_rate = min(1.0, num_bookings / max(total_slots, 1))
        conversion_rate = min(1.0, num_bookings / max(seg_count, 1))
        avg_time = agg["total_lead_minutes"] / num_bookings if num_bookings > 0 else 0

        stat = BehaviourStats(
            segment=segment,
            sport=sport,
            day_of_week=day,
            hour=hour,
            fill_rate=round(fill_rate, 4),
            avg_time_to_book=round(avg_time, 1),
            conversion_rate=round(conversion_rate, 4),
            num_bookings=num_bookings,
        )
        stats.append(stat)

    db.add_all(stats)
    db.commit()
    logger.info(f"Computed {len(stats)} behaviour_stats records")


def main():
    """Run the full seed process."""
    logger.info("=" * 60)
    logger.info("SportsLot Optimizer — Database Seed")
    logger.info("=" * 60)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created / verified")

    db = SessionLocal()
    try:
        seed_customers(db)
        seed_slots(db)
        seed_bookings(db)
        compute_behaviour_stats(db)

        # Print summary
        logger.info("=" * 60)
        logger.info("Seed Summary:")
        logger.info(f"  Customers:       {db.query(Customer).count()}")
        logger.info(f"  Slots:           {db.query(Slot).count()}")
        logger.info(f"  Bookings:        {db.query(Booking).count()}")
        logger.info(f"  BehaviourStats:  {db.query(BehaviourStats).count()}")

        # Show some vacant slots for demo
        vacant = db.query(Slot).filter(Slot.status == SlotStatus.VACANT).limit(5).all()
        if vacant:
            logger.info("=" * 60)
            logger.info("Sample VACANT slots (for testing):")
            for s in vacant:
                logger.info(
                    f"  {s.id}: {s.sport} on {s.date} "
                    f"({s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}) "
                    f"₹{s.price:.0f}"
                )
        logger.info("=" * 60)
        logger.info("Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
