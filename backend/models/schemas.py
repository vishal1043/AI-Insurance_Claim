# backend/models/schemas.py
# Pydantic models for requests/responses (NO SQLAlchemy here)

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime, date
import uuid


# ==========================
# User Models
# ==========================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    mobile_no: str
    dob: date


class UserCreate(UserBase):
    password: str   # plain password from client


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"  # "user" or "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================
# Insurance Policy Models
# ==========================

class InsurancePolicyBase(BaseModel):
    insurance_id: str
    total_coverage_amount: float
    expiry_date: date
    emi_pending: bool = False
    status: str = "active"  # active, inactive, blocked


class InsurancePolicy(InsurancePolicyBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    remaining_amount: float


# ==========================
# Hospital Models
# ==========================

class HospitalBase(BaseModel):
    name: str
    address: str
    registration_no: str
    is_blacklisted: bool = False


class Hospital(HospitalBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# ==========================
# Claim Expense Models
# ==========================

class ClaimExpenseBase(BaseModel):
    expense_name: str
    amount: float


class ClaimExpense(ClaimExpenseBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_id: str


# ==========================
# Claim Models
# ==========================

class ClaimCreate(BaseModel):
    name: str
    insurance_id: str
    aadhar_no: str
    hospital_name: str
    date_of_admission: date
    disease_description: str
    expenses: List[ClaimExpenseBase]


class Claim(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insurance_id: str
    aadhar_no: str
    hospital_name: str
    date_of_admission: date
    disease_description: str
    total_claim_amount: float
    confidence_score: Optional[float] = None
    reimbursement_amount: Optional[float] = None
    status: str = "Under Review"  # Submitted, Under Review, Approved, Rejected
    issues_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================
# Claim File Models
# ==========================

class ClaimFile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_id: str
    file_type: str  # "bill" or "report"
    file_path: str
    extracted_text: Optional[str] = None


# ==========================
# Admin Actions
# ==========================

class AdminClaimAction(BaseModel):
    reimbursement_amount: float
    status: str  # "Approved" or "Rejected"
    remarks: Optional[str] = None


# ==========================
# Response Models
# ==========================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User


class ClaimDetailResponse(Claim):
    expenses: List[ClaimExpense]
    files: List[ClaimFile]
    user_info: Optional[User] = None
    policy_info: Optional[InsurancePolicy] = None
