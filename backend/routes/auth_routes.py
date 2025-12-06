# backend/routes/auth_routes.py

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
import logging
import uuid

from backend.models.schemas import UserCreate, UserLogin, User, TokenResponse
from backend.models.models import UserModel
from backend.database import SessionLocal
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str,
    db: Session,
) -> User:
    """Get current user from JWT token using SQLAlchemy."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")

    user_obj: Optional[UserModel] = (
        db.query(UserModel).filter(UserModel.id == user_uuid).first()
    )

    if not user_obj:
        raise HTTPException(status_code=401, detail="User not found")

    return User(
        id=str(user_obj.id),
        name=user_obj.name,
        email=user_obj.email,
        mobile_no=user_obj.mobile_no,
        dob=user_obj.dob,
        role=user_obj.role,
        created_at=user_obj.created_at,
    )


def create_auth_router():
    @router.post("/register", response_model=TokenResponse)
    def register(user_data: UserCreate, db: Session = Depends(get_db)):
        """Register a new user (PostgreSQL version)."""

        existing_user = (
            db.query(UserModel)
            .filter(UserModel.email == user_data.email)
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        password_hash = hash_password(user_data.password)

        user_obj = UserModel(
            name=user_data.name,
            email=user_data.email,
            mobile_no=user_data.mobile_no,
            dob=user_data.dob,
            role="user",
            password_hash=password_hash,
        )

        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)

        user = User(
            id=str(user_obj.id),
            name=user_obj.name,
            email=user_obj.email,
            mobile_no=user_obj.mobile_no,
            dob=user_obj.dob,
            role=user_obj.role,
            created_at=user_obj.created_at,
        )

        access_token = create_access_token(
            {"user_id": user.id, "email": user.email, "role": user.role}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user,
        )

    @router.post("/login", response_model=TokenResponse)
    def login(credentials: UserLogin, db: Session = Depends(get_db)):
        """Login user (PostgreSQL version)."""

        user_obj: Optional[UserModel] = (
            db.query(UserModel)
            .filter(UserModel.email == credentials.email)
            .first()
        )
        if not user_obj:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not verify_password(credentials.password, user_obj.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user = User(
            id=str(user_obj.id),
            name=user_obj.name,
            email=user_obj.email,
            mobile_no=user_obj.mobile_no,
            dob=user_obj.dob,
            role=user_obj.role,
            created_at=user_obj.created_at,
        )

        access_token = create_access_token(
            {"user_id": user.id, "email": user.email, "role": user.role}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user,
        )

    @router.get("/me", response_model=User)
    def get_me(
        authorization: str = Header(None),
        db: Session = Depends(get_db),
    ):
        """Get current user info."""
        user = get_current_user(authorization, db)
        return user

    return router
