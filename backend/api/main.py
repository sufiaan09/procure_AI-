"""
FastAPI Application — ProcureAI Tender Evaluation Platform
Exposes REST endpoints used by the React dashboard.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import json

from database import engine, Base, get_db
from models.db_models import User
from modules.auth import get_password_hash, verify_password, create_access_token, get_current_user
from pydantic import BaseModel
from datetime import timedelta

from models.schemas import (
    AuditReport, EvaluationResponse, TenderCriteria, BidderData
)
from modules.tender_parser import parse_tender
from modules.bidder_processor import process_bidder
from modules.evaluation_engine import evaluate_all
from modules.report_generator import generate_report, report_to_markdown
from utils.pdf_utils import extract_full_text_from_bytes

app = FastAPI(
    title="ProcureAI Tender Evaluation API",
    description="AI-powered tender eligibility evaluation for ProcureAI platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (replace with DB in production)
_reports: dict[str, AuditReport] = {}
_criteria_cache: dict[str, TenderCriteria] = {}


@app.get("/")
def root():
    return {"status": "ok", "service": "ProcureAI Tender Evaluation API v1.0"}

# Initialize DB
Base.metadata.create_all(bind=engine)

# Pydantic schema for registration
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

@app.post("/api/auth/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=60*24)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user.email, "full_name": user.full_name}}

# ─── Step 1: Parse a tender PDF ───────────────────────────────────────────────

@app.post("/api/tender/parse")
async def parse_tender_endpoint(
    tender_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a tender PDF and extract its eligibility criteria."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    pdf_bytes = await file.read()
    text, page_count = extract_full_text_from_bytes(pdf_bytes)

    if not text.strip():
        raise HTTPException(422, "Could not extract text from PDF. Try a text-based PDF.")

    try:
        criteria = parse_tender(text, tender_id=tender_id)
        criteria.raw_text_pages = page_count
        _criteria_cache[tender_id] = criteria
        return {"success": True, "criteria": criteria.model_dump()}
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {e}")


@app.get("/api/tender/{tender_id}/criteria")
def get_criteria(tender_id: str):
    """Retrieve previously parsed tender criteria."""
    if tender_id not in _criteria_cache:
        raise HTTPException(404, f"Tender '{tender_id}' not found. Parse it first.")
    return _criteria_cache[tender_id].model_dump()


# ─── Step 2: Process a bidder submission ─────────────────────────────────────

@app.post("/api/bidder/process")
async def process_bidder_endpoint(
    tender_id: str = Form(...),
    bidder_id: str = Form(...),
    firm_name: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a bidder's submission PDF and extract their eligibility data."""
    if tender_id not in _criteria_cache:
        raise HTTPException(404, f"Tender '{tender_id}' not found. Parse it first.")

    criteria = _criteria_cache[tender_id]
    pdf_bytes = await file.read()
    text, _ = extract_full_text_from_bytes(pdf_bytes)

    try:
        bidder = process_bidder(bidder_id, firm_name, text, criteria.mandatory_documents)
        return {"success": True, "bidder_data": bidder.model_dump()}
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {e}")


# ─── Step 3 + 4: Evaluate all bidders and generate report ────────────────────

@app.post("/api/evaluate")
def evaluate_endpoint(payload: dict):
    """
    Run the evaluation engine on pre-processed bidder data.

    Payload:
    {
      "tender_id": "...",
      "bidders": [ <BidderData JSON>, ... ]
    }
    """
    tender_id = payload.get("tender_id")
    if not tender_id or tender_id not in _criteria_cache:
        raise HTTPException(404, f"Tender '{tender_id}' not found")

    criteria = _criteria_cache[tender_id]
    raw_bidders = payload.get("bidders", [])
    if not raw_bidders:
        raise HTTPException(400, "No bidder data provided")

    bidders = [BidderData(**b) for b in raw_bidders]
    evaluations = evaluate_all(criteria, bidders)
    report = generate_report(criteria, evaluations)
    _reports[report.report_id] = report

    return {"success": True, "report": report.model_dump()}


# ─── Full pipeline: tender PDF + multiple bidder PDFs in one call ─────────────

@app.post("/api/pipeline/full")
async def full_pipeline(
    tender_id: str = Form(...),
    tender_file: UploadFile = File(...),
    bidder_files: list[UploadFile] = File(...),
    bidder_names: str = Form(...),  # JSON array of firm names
):
    """
    Run the complete 4-step pipeline in one API call.
    bidder_names: JSON string, e.g. '["Firm A", "Firm B"]'
    """
    names = json.loads(bidder_names)
    if len(names) != len(bidder_files):
        raise HTTPException(400, "bidder_names count must match bidder_files count")

    # Step 1
    tender_bytes = await tender_file.read()
    tender_text, page_count = extract_full_text_from_bytes(tender_bytes)
    criteria = parse_tender(tender_text, tender_id=tender_id)
    criteria.raw_text_pages = page_count
    _criteria_cache[tender_id] = criteria

    # Steps 2 + 3
    bidders: list[BidderData] = []
    for i, (bf, name) in enumerate(zip(bidder_files, names)):
        bid_bytes = await bf.read()
        bid_text, _ = extract_full_text_from_bytes(bid_bytes)
        bidder = process_bidder(
            bidder_id=f"B{i+1:03d}",
            firm_name_hint=name,
            submission_text=bid_text,
            mandatory_docs=criteria.mandatory_documents,
        )
        bidders.append(bidder)

    evaluations = evaluate_all(criteria, bidders)
    report = generate_report(criteria, evaluations)
    _reports[report.report_id] = report

    return {"success": True, "report": report.model_dump()}


# ─── Report retrieval ─────────────────────────────────────────────────────────

@app.get("/api/reports")
def list_reports():
    """List all generated reports."""
    return {
        "reports": [
            {
                "report_id": r.report_id,
                "tender_id": r.tender_id,
                "tender_title": r.tender_title,
                "generated_at": r.generated_at,
                "total_bidders": r.total_bidders,
                "qualified_count": r.qualified_count,
            }
            for r in _reports.values()
        ]
    }


@app.get("/api/reports/{report_id}")
def get_report(report_id: str):
    if report_id not in _reports:
        raise HTTPException(404, f"Report '{report_id}' not found")
    return _reports[report_id].model_dump()


@app.get("/api/reports/{report_id}/markdown", response_class=PlainTextResponse)
def get_report_markdown(report_id: str):
    if report_id not in _reports:
        raise HTTPException(404, f"Report '{report_id}' not found")
    return report_to_markdown(_reports[report_id])


# ─── Demo: evaluate using sample JSON data (no PDF needed) ───────────────────

@app.post("/api/demo/evaluate")
def demo_evaluate():
    """
    Run evaluation on built-in sample data.
    Use this to test the system without uploading PDFs.
    """
    from sample_demo import get_sample_data
    criteria, bidders = get_sample_data()
    _criteria_cache[criteria.tender_id] = criteria
    evaluations = evaluate_all(criteria, bidders)
    report = generate_report(criteria, evaluations)
    _reports[report.report_id] = report
    return {"success": True, "report": report.model_dump()}

