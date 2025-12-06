from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List
from datetime import datetime
from uuid import UUID as UUIDType
import logging

from sqlalchemy.orm import Session

# SQLAlchemy models & Session
from backend.models.models import (
    ClaimModel,
    ClaimExpenseModel,
    ClaimFileModel,
    UserModel,
    InsurancePolicyModel,
)
from backend.database import SessionLocal
# Pydantic schemas
from backend.models.schemas import (
    Claim,
    AdminClaimAction,
    ClaimDetailResponse,
    User,
    InsurancePolicy,
    ClaimExpense,
    ClaimFile,
)

# Auth helper (you must update this to use SQLAlchemy as well)
from backend.routes.auth_routes import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==========================
# DB Dependency
# ==========================
def get_db():
    """FastAPI dependency that provides a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# Admin check helper
# ==========================
def require_admin(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Verify user is admin.
    NOTE: make sure get_current_user(authorization, db) is implemented
    to work with SQLAlchemy and returns a Pydantic User object.
    """
    user = get_current_user(authorization, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ==========================
# Routes
# ==========================

@router.get("/claims", response_model=List[Claim])
def get_all_claims(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get all claims (admin only)."""
    require_admin(authorization, db)

    orm_claims = db.query(ClaimModel).all()
    claims: List[Claim] = []

    for c in orm_claims:
        claims.append(
            Claim(
                id=str(c.id),
                user_id=str(c.user_id),
                insurance_id=c.insurance_id,
                aadhar_no=c.aadhar_no,
                hospital_name=c.hospital_name,
                date_of_admission=c.date_of_admission,
                disease_description=c.disease_description,
                total_claim_amount=c.total_claim_amount,
                confidence_score=c.confidence_score,
                reimbursement_amount=c.reimbursement_amount,
                status=c.status,
                issues_summary=c.issues_summary,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return claims


@router.get("/claims/{claim_id}", response_model=ClaimDetailResponse)
def get_claim_for_review(
    claim_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get detailed claim for admin review."""
    require_admin(authorization, db)

    # Convert string to UUID for lookup
    try:
        cid = UUIDType(claim_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid claim ID format")

    # Get claim
    claim_obj = db.query(ClaimModel).filter(ClaimModel.id == cid).first()
    if not claim_obj:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Get expenses
    expense_objs = (
        db.query(ClaimExpenseModel)
        .filter(ClaimExpenseModel.claim_id == cid)
        .all()
    )

    expenses: List[ClaimExpense] = [
        ClaimExpense(
            id=str(e.id),
            claim_id=str(e.claim_id),
            expense_name=e.expense_name,
            amount=e.amount,
        )
        for e in expense_objs
    ]

    # Get files
    file_objs = (
        db.query(ClaimFileModel)
        .filter(ClaimFileModel.claim_id == cid)
        .all()
    )

    files: List[ClaimFile] = [
        ClaimFile(
            id=str(f.id),
            claim_id=str(f.claim_id),
            file_type=f.file_type,
            file_path=f.file_path,
            extracted_text=f.extracted_text,
        )
        for f in file_objs
    ]

    # Get user info
    user_obj = db.query(UserModel).filter(UserModel.id == claim_obj.user_id).first()
    user_info = (
        User(
            id=str(user_obj.id),
            name=user_obj.name,
            email=user_obj.email,
            mobile_no=user_obj.mobile_no,
            dob=user_obj.dob,
            role=user_obj.role,
            created_at=user_obj.created_at,
        )
        if user_obj
        else None
    )

    # Get policy info
    policy_obj = (
        db.query(InsurancePolicyModel)
        .filter(InsurancePolicyModel.insurance_id == claim_obj.insurance_id)
        .first()
    )

    policy_info = (
        InsurancePolicy(
            id=str(policy_obj.id),
            user_id=str(policy_obj.user_id),
            insurance_id=policy_obj.insurance_id,
            total_coverage_amount=policy_obj.total_coverage_amount,
            remaining_amount=policy_obj.remaining_amount,
            expiry_date=policy_obj.expiry_date,
            emi_pending=policy_obj.emi_pending,
            status=policy_obj.status,
        )
        if policy_obj
        else None
    )

    # Build base claim schema
    claim_schema = Claim(
        id=str(claim_obj.id),
        user_id=str(claim_obj.user_id),
        insurance_id=claim_obj.insurance_id,
        aadhar_no=claim_obj.aadhar_no,
        hospital_name=claim_obj.hospital_name,
        date_of_admission=claim_obj.date_of_admission,
        disease_description=claim_obj.disease_description,
        total_claim_amount=claim_obj.total_claim_amount,
        confidence_score=claim_obj.confidence_score,
        reimbursement_amount=claim_obj.reimbursement_amount,
        status=claim_obj.status,
        issues_summary=claim_obj.issues_summary,
        created_at=claim_obj.created_at,
        updated_at=claim_obj.updated_at,
    )

    return ClaimDetailResponse(
        **claim_schema.model_dump(),
        expenses=expenses,
        files=files,
        user_info=user_info,
        policy_info=policy_info,
    )


@router.put("/claims/{claim_id}/action", response_model=Claim)
def admin_claim_action(
    claim_id: str,
    action: AdminClaimAction,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Approve or reject a claim (admin only)."""
    admin_user = require_admin(authorization, db)
    logger.info(f"Admin {admin_user.email} performing action on claim {claim_id}")

    # Convert claim_id to UUID
    try:
        cid = UUIDType(claim_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid claim ID format")

    # Get claim
    claim_obj = db.query(ClaimModel).filter(ClaimModel.id == cid).first()
    if not claim_obj:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Update claim
    claim_obj.status = action.status
    claim_obj.reimbursement_amount = action.reimbursement_amount
    claim_obj.updated_at = datetime.utcnow()

    if action.remarks:
        current_summary = claim_obj.issues_summary or ""
        claim_obj.issues_summary = (
            f"{current_summary}\n\nAdmin Remarks: {action.remarks}".strip()
        )

    # If approved, update policy remaining amount
    if action.status == "Approved":
        policy_obj = (
            db.query(InsurancePolicyModel)
            .filter(InsurancePolicyModel.insurance_id == claim_obj.insurance_id)
            .first()
        )
        if policy_obj:
            policy_obj.remaining_amount = max(
                0.0, policy_obj.remaining_amount - action.reimbursement_amount
            )

    db.commit()
    db.refresh(claim_obj)

    # Return updated claim as Pydantic schema
    return Claim(
        id=str(claim_obj.id),
        user_id=str(claim_obj.user_id),
        insurance_id=claim_obj.insurance_id,
        aadhar_no=claim_obj.aadhar_no,
        hospital_name=claim_obj.hospital_name,
        date_of_admission=claim_obj.date_of_admission,
        disease_description=claim_obj.disease_description,
        total_claim_amount=claim_obj.total_claim_amount,
        confidence_score=claim_obj.confidence_score,
        reimbursement_amount=claim_obj.reimbursement_amount,
        status=claim_obj.status,
        issues_summary=claim_obj.issues_summary,
        created_at=claim_obj.created_at,
        updated_at=claim_obj.updated_at,
    )


def create_admin_router():
    """Factory to keep same pattern as before."""
    return router
