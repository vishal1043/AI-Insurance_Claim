import logging
from datetime import datetime, date
import re

logger = logging.getLogger(__name__)

def validate_claim_data(claim, policy, extracted_texts, expenses) -> dict:
    """Validate claim data against policy and extracted text."""
    
    checks = {
        "policy_active": False,
        "policy_not_expired": False,
        "no_emi_pending": False,
        "coverage_sufficient": False,
        "hospital_name_found": False,
        "date_reasonable": False,
    }
    
    issues = []
    
    # Check 1: Policy active
    if policy and policy.get('status') == 'active':
        checks["policy_active"] = True
    else:
        issues.append("⚠️ Insurance policy is not active")
    
    # Check 2: Policy not expired
    if policy:
        expiry_date = policy.get('expiry_date')
        if isinstance(expiry_date, str):
            expiry_date = datetime.fromisoformat(expiry_date).date()
        if expiry_date and expiry_date >= date.today():
            checks["policy_not_expired"] = True
        else:
            issues.append("⚠️ Insurance policy has expired")
    
    # Check 3: EMI pending
    if policy and not policy.get('emi_pending', False):
        checks["no_emi_pending"] = True
    else:
        issues.append("⚠️ EMI payment is pending")
    
    # Check 4: Coverage sufficient
    total_claim = claim.get('total_claim_amount', 0)
    if policy:
        remaining = policy.get('remaining_amount', 0)
        if remaining >= total_claim:
            checks["coverage_sufficient"] = True
        else:
            issues.append(f"⚠️ Claim amount (Rs. {total_claim}) exceeds remaining coverage (Rs. {remaining})")
    
    # Check 5: Hospital name in documents
    hospital_name = claim.get('hospital_name', '').lower()
    combined_text = ' '.join(extracted_texts).lower()
    
    # Check if hospital name appears in extracted text
    if hospital_name and len(hospital_name) > 3:
        # Split hospital name into words and check if most words appear
        hospital_words = [w for w in hospital_name.split() if len(w) > 3]
        found_words = sum(1 for word in hospital_words if word in combined_text)
        if found_words >= len(hospital_words) * 0.5:  # At least 50% of words found
            checks["hospital_name_found"] = True
        else:
            issues.append(f"⚠️ Hospital name '{claim.get('hospital_name')}' not clearly found in documents")
    
    # Check 6: Date reasonable
    admission_date = claim.get('date_of_admission')
    if isinstance(admission_date, str):
        admission_date = datetime.fromisoformat(admission_date).date()
    
    if admission_date:
        if admission_date <= date.today():
            checks["date_reasonable"] = True
        else:
            issues.append("⚠️ Admission date is in the future")
    
    # Calculate confidence score
    passed_checks = sum(1 for v in checks.values() if v)
    total_checks = len(checks)
    confidence_score = (passed_checks / total_checks) * 100
    
    return {
        "checks": checks,
        "issues": issues,
        "confidence_score": confidence_score
    }

def calculate_reimbursement(claim_amount: float, policy_remaining: float, confidence_score: float) -> float:
    """Calculate suggested reimbursement amount."""
    
    if confidence_score < 30:
        # Too many issues, reject
        return 0.0
    elif confidence_score < 60:
        # Some issues, approve partial amount
        max_amount = min(claim_amount, policy_remaining)
        return round(max_amount * 0.7, 2)  # 70% of claim
    else:
        # Good confidence, approve full amount
        return round(min(claim_amount, policy_remaining), 2)
