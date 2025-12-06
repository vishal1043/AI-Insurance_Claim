# backend/routes/claim_routes.py

from fastapi import (
    APIRouter,
    HTTPException,
    Header,
    File,
    UploadFile,
    Form,
    Depends,
)
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from datetime import datetime
import shutil
import json
import uuid

# SQLAlchemy models
from backend.models.models import (
    ClaimModel,
    ClaimExpenseModel,
    ClaimFileModel,
    InsurancePolicyModel,
)

# Pydantic schemas
from backend.models.schemas import (
    ClaimCreate,
    Claim,
    ClaimDetailResponse,
    ClaimExpense,
    ClaimFile,
)

from backend.database import SessionLocal

# Auth
from backend.routes.auth_routes import get_current_user

# Services
from backend.services.ocr_service import extract_text_from_file
from backend.services.ai_service import analyze_claim_with_ai
from backend.services.validation_service import (
    validate_claim_data,
    calculate_reimbursement,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claims", tags=["Claims"])

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ==========================
# DB Dependency
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# GET USER CLAIMS
# ==========================
@router.get("", response_model=List[Claim])
def get_user_claims(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get all claims for current user (SQL version)."""

    user = get_current_user(authorization, db)

    claim_objs = (
        db.query(ClaimModel)
        .filter(ClaimModel.user_id == uuid.UUID(user.id))
        .all()
    )

    claims: List[Claim] = []
    for c in claim_objs:
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


# ==========================
# CREATE A CLAIM
# ==========================
@router.post("", response_model=Claim)
async def create_claim(
    claim_data: str = Form(...),
    bills: List[UploadFile] = File([]),
    reports: List[UploadFile] = File([]),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Create a new insurance claim."""

    user = get_current_user(authorization, db)

    # Parse form JSON into Pydantic
    claim_dict = json.loads(claim_data)
    claim_create = ClaimCreate(**claim_dict)

    # Total from expenses
    total_amount = sum(exp.amount for exp in claim_create.expenses)

    # Create DB claim object
    claim_obj = ClaimModel(
        user_id=uuid.UUID(user.id),
        insurance_id=claim_create.insurance_id,
        aadhar_no=claim_create.aadhar_no,
        hospital_name=claim_create.hospital_name,
        date_of_admission=claim_create.date_of_admission,
        disease_description=claim_create.disease_description,
        total_claim_amount=total_amount,
        status="Under Review",
    )

    db.add(claim_obj)
    db.commit()
    db.refresh(claim_obj)

    claim_id = str(claim_obj.id)

    # ================
    # Save expenses
    # ================
    for exp in claim_create.expenses:
        exp_obj = ClaimExpenseModel(
            claim_id=claim_obj.id,
            expense_name=exp.expense_name,
            amount=exp.amount,
        )
        db.add(exp_obj)

    db.commit()

    # ================
    # Save files + OCR
    # ================
    extracted_texts: List[str] = []

    def save_files(files, file_type: str):
        for file in files:
            path = UPLOADS_DIR / file_type / f"{claim_id}_{file.filename}"
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            extracted_text = extract_text_from_file(str(path))
            extracted_texts.append(extracted_text)

            file_obj = ClaimFileModel(
                claim_id=claim_obj.id,
                file_type=file_type,
                file_path=str(path),
                extracted_text=extracted_text,
            )
            db.add(file_obj)

    save_files(bills, "bills")
    save_files(reports, "reports")

    db.commit()

    # ==========================
    # Get policy from DB
    # ==========================
    policy_obj = (
        db.query(InsurancePolicyModel)
        .filter(InsurancePolicyModel.insurance_id == claim_obj.insurance_id)
        .first()
    )

    policy_data = (
        {
            "insurance_id": policy_obj.insurance_id,
            "total_coverage_amount": policy_obj.total_coverage_amount,
            "remaining_amount": policy_obj.remaining_amount,
            "expiry_date": policy_obj.expiry_date,
            "emi_pending": policy_obj.emi_pending,
            "status": policy_obj.status,
        }
        if policy_obj
        else None
    )

    # ==========================
    # Validation Logic
    # ==========================
    expense_objs = (
        db.query(ClaimExpenseModel)
        .filter(ClaimExpenseModel.claim_id == claim_obj.id)
        .all()
    )

    expenses_list = [
        {"expense_name": e.expense_name, "amount": e.amount} for e in expense_objs
    ]

    validation_result = validate_claim_data(
        claim={
            "insurance_id": claim_obj.insurance_id,
            "hospital_name": claim_obj.hospital_name,
            "aadhar_no": claim_obj.aadhar_no,
            "date_of_admission": str(claim_obj.date_of_admission),
            "disease_description": claim_obj.disease_description,
        },
        policy=policy_data,
        extracted_texts=extracted_texts,
        expenses=expenses_list,
    )

    # ==========================
    # AI Analysis (OpenRouter)
    # ==========================
    ai_result = await analyze_claim_with_ai(
        {
            "id": str(claim_obj.id),
            "insurance_id": claim_obj.insurance_id,
            "hospital_name": claim_obj.hospital_name,
            "aadhar_no": claim_obj.aadhar_no,
            "date_of_admission": str(claim_obj.date_of_admission),
            "disease_description": claim_obj.disease_description,
            "total_claim_amount": claim_obj.total_claim_amount,
        },
        extracted_texts,
    )

    confidence_score = (
        validation_result["confidence_score"] + ai_result["consistency_score"]
    ) / 2

    all_issues = validation_result["issues"] + ai_result["issues"]

    # Reimbursement
    policy_remaining = policy_data["remaining_amount"] if policy_data else 0

    suggested_reimbursement = calculate_reimbursement(
        total_amount,
        policy_remaining,
        confidence_score,
    )

    issues_summary = (
        f"AI Summary: {ai_result['summary']}\n\nIssues:\n" + "\n".join(all_issues)
    )

    # Update claim
    claim_obj.confidence_score = confidence_score
    claim_obj.reimbursement_amount = suggested_reimbursement
    claim_obj.issues_summary = issues_summary
    claim_obj.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(claim_obj)

    # Return Pydantic Claim
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


# ==========================
# GET CLAIM DETAIL (User)
# ==========================
@router.get("/{claim_id}", response_model=ClaimDetailResponse)
def get_claim_detail(
    claim_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get detailed claim information."""

    user = get_current_user(authorization, db)

    try:
        cid = uuid.UUID(claim_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid claim ID")

    claim_obj = (
        db.query(ClaimModel)
        .filter(ClaimModel.id == cid, ClaimModel.user_id == uuid.UUID(user.id))
        .first()
    )
    if not claim_obj:
        raise HTTPException(status_code=404, detail="Claim not found")

    expenses = (
        db.query(ClaimExpenseModel)
        .filter(ClaimExpenseModel.claim_id == cid)
        .all()
    )
    files = (
        db.query(ClaimFileModel)
        .filter(ClaimFileModel.claim_id == cid)
        .all()
    )

    return ClaimDetailResponse(
        **Claim(
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
        ).model_dump(),
        expenses=[
            ClaimExpense(
                id=str(e.id),
                claim_id=str(e.claim_id),
                expense_name=e.expense_name,
                amount=e.amount,
            )
            for e in expenses
        ],
        files=[
            ClaimFile(
                id=str(f.id),
                claim_id=str(f.claim_id),
                file_type=f.file_type,
                file_path=f.file_path,
                extracted_text=f.extracted_text,
            )
            for f in files
        ],
    )


def create_claim_router():
    return router
