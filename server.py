# server.py

from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import logging
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# PostgreSQL database setup
from backend.database import engine
from backend.models.models import Base

# Routers (SQL versions)
from backend.routes.auth_routes import create_auth_router
from backend.routes.claim_routes import create_claim_router
from backend.routes.admin_routes import create_admin_router

# ----------------------------------------------------
# Load environment variables
# ----------------------------------------------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# ----------------------------------------------------
# Database Initialization
# ----------------------------------------------------
def init_database():
    """Create PostgreSQL tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("✔ PostgreSQL tables initialized")


# ----------------------------------------------------
# FastAPI Application
# ----------------------------------------------------
app = FastAPI(
    title="AI Insurance Claim System",
    description="AI-powered OCR, validation, and reimbursement processing",
    version="1.0.0",
)

# ----------------------------------------------------
# Register Routers
# ----------------------------------------------------
app.include_router(create_auth_router(), prefix="/api")
app.include_router(create_claim_router(), prefix="/api")
app.include_router(create_admin_router(), prefix="/api")


# ----------------------------------------------------
# Health Check Route
# ----------------------------------------------------
@app.get("/api/")
async def root():
    return {
        "message": "Insurance Claim System API",
        "status": "running",
    }


# ----------------------------------------------------
# CORS Middleware
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),  # frontend URLs
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Logging Setup
# ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("server")


# ----------------------------------------------------
# Startup Event
# ----------------------------------------------------
@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Starting AI Insurance Claim System (PostgreSQL version)")
    init_database()

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
print("Serving uploads from:", UPLOADS_DIR)
print("Uploads exists:", UPLOADS_DIR.exists())
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads",
)