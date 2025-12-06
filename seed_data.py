"""
Seed PostgreSQL database with sample data.
"""

from datetime import datetime, timedelta, date
from pathlib import Path
import uuid

from dotenv import load_dotenv

from backend.database import SessionLocal, Base, engine
from backend.models.models import (
    UserModel,
    InsurancePolicyModel,
    HospitalModel,
)
from backend.services.auth_service import hash_password

# Load env (from project root: app/.env)
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")


def seed_database():
    db = SessionLocal()
    try:
        print("Creating tables (if not exist)...")
        Base.metadata.create_all(bind=engine)

        print("Seeding database with sample data...")

        # Clear existing data (CAREFUL: this wipes tables)
        db.query(HospitalModel).delete()
        db.query(InsurancePolicyModel).delete()
        db.query(UserModel).delete()
        db.commit()

        # -----------------------------
        # Create admin user
        # -----------------------------
        admin_user = UserModel(
            id=uuid.uuid4(),
            name="Admin User",
            email="admin@insurance.com",
            password_hash=hash_password("admin123"),
            mobile_no="9999999999",
            dob=date(1990, 1, 1),
            role="admin",
            created_at=datetime.utcnow(),
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print("Created admin user: admin@insurance.com / admin123")

        # -----------------------------
        # Create sample users
        # -----------------------------
        users = []
        for i in range(1, 4):
            user_obj = UserModel(
                id=uuid.uuid4(),
                name=f"User {i}",
                email=f"user{i}@example.com",
                password_hash=hash_password("password123"),
                mobile_no=f"98765432{i:02d}",
                dob=date(1990, 1, 1) + timedelta(days=i * 365),
                role="user",
                created_at=datetime.utcnow(),
            )
            db.add(user_obj)
            users.append(user_obj)
            print(f"Prepared user: user{i}@example.com / password123")

        db.commit()

        # refresh to get IDs
        for u in users:
            db.refresh(u)
            print(f"Created user in DB: {u.email}")

        # -----------------------------
        # Create insurance policies
        # -----------------------------
        policies = [
            InsurancePolicyModel(
                id=uuid.uuid4(),
                user_id=users[0].id,
                insurance_id="POL001",
                total_coverage_amount=500000.0,
                remaining_amount=500000.0,
                expiry_date=date.today() + timedelta(days=365),
                emi_pending=False,
                status="active",
            ),
            InsurancePolicyModel(
                id=uuid.uuid4(),
                user_id=users[1].id,
                insurance_id="POL002",
                total_coverage_amount=300000.0,
                remaining_amount=300000.0,
                expiry_date=date.today() + timedelta(days=180),
                emi_pending=False,
                status="active",
            ),
            InsurancePolicyModel(
                id=uuid.uuid4(),
                user_id=users[2].id,
                insurance_id="POL003",
                total_coverage_amount=200000.0,
                remaining_amount=200000.0,
                expiry_date=date.today() + timedelta(days=90),
                emi_pending=True,
                status="active",
            ),
        ]

        for p in policies:
            db.add(p)

        db.commit()
        print(f"Created {len(policies)} insurance policies")

        # -----------------------------
        # Create hospitals
        # -----------------------------
        hospitals = [
            HospitalModel(
                id=uuid.uuid4(),
                name="City Hospital",
                address="123 Main Street, City Center",
                registration_no="HOSP001",
                is_blacklisted=False,
            ),
            HospitalModel(
                id=uuid.uuid4(),
                name="Apollo Medical Center",
                address="456 Health Avenue, Medical District",
                registration_no="HOSP002",
                is_blacklisted=False,
            ),
            HospitalModel(
                id=uuid.uuid4(),
                name="Max Super Speciality Hospital",
                address="789 Care Lane, Healthcare Zone",
                registration_no="HOSP003",
                is_blacklisted=False,
            ),
            HospitalModel(
                id=uuid.uuid4(),
                name="Fraudulent Clinic",
                address="Unknown Location",
                registration_no="HOSP999",
                is_blacklisted=True,
            ),
        ]

        for h in hospitals:
            db.add(h)

        db.commit()
        print(f"Created {len(hospitals)} hospitals")

        # -----------------------------
        # Summary
        # -----------------------------
        print("\n" + "=" * 50)
        print("PostgreSQL database seeded successfully!")
        print("=" * 50)
        print("\nLogin Credentials:")
        print("-" * 50)
        print("Admin:")
        print("  Email: admin@insurance.com")
        print("  Password: admin123")
        print("\nUsers:")
        for i in range(1, 4):
            print(f"  User {i}: user{i}@example.com / password123")
            print(f"    Policy: POL{i:03d}")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
