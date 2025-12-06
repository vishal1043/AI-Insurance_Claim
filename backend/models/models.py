# backend/models/models.py
# ONLY ORM table definitions here – NO engine, NO SessionLocal

from datetime import datetime, date
import uuid

from sqlalchemy import (
    Column,
    String,
    Date,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base  # import Base from single DB config


# -------------------------
# User Table
# -------------------------
class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    mobile_no = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    role = Column(String, default="user")  # "user" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    policies = relationship("InsurancePolicyModel", back_populates="user")
    claims = relationship("ClaimModel", back_populates="user")


# -------------------------
# Insurance Policy Table
# -------------------------
class InsurancePolicyModel(Base):
    __tablename__ = "insurance_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    insurance_id = Column(String, unique=True, nullable=False)
    total_coverage_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    expiry_date = Column(Date, nullable=False)
    emi_pending = Column(Boolean, default=False)
    status = Column(String, default="active")  # active, inactive, blocked

    user = relationship("UserModel", back_populates="policies")


# -------------------------
# Hospital Table
# -------------------------
class HospitalModel(Base):
    __tablename__ = "hospitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    registration_no = Column(String, nullable=False)
    is_blacklisted = Column(Boolean, default=False)


# -------------------------
# Claim Table
# -------------------------
class ClaimModel(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    insurance_id = Column(String, nullable=False)
    aadhar_no = Column(String, nullable=False)
    hospital_name = Column(String, nullable=False)
    date_of_admission = Column(Date, nullable=False)
    disease_description = Column(Text, nullable=False)
    total_claim_amount = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)
    reimbursement_amount = Column(Float, nullable=True)
    status = Column(
        String,
        default="Under Review",   # Submitted, Under Review, Approved, Rejected
    )
    issues_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("UserModel", back_populates="claims")
    expenses = relationship(
        "ClaimExpenseModel", back_populates="claim", cascade="all, delete-orphan"
    )
    files = relationship(
        "ClaimFileModel", back_populates="claim", cascade="all, delete-orphan"
    )


# -------------------------
# Claim Expense Table
# -------------------------
class ClaimExpenseModel(Base):
    __tablename__ = "claim_expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    expense_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    claim = relationship("ClaimModel", back_populates="expenses")


# -------------------------
# Claim File Table
# -------------------------
class ClaimFileModel(Base):
    __tablename__ = "claim_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    file_type = Column(String, nullable=False)  # "bill" or "report"
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)

    claim = relationship("ClaimModel", back_populates="files")
