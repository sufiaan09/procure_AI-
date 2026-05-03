"""
Pydantic schemas for the CRPF Tender Evaluation Platform.
All data structures used across the pipeline are defined here.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Evidence: where the AI found a value in the source PDF
# ─────────────────────────────────────────────────────────────────────────────

class Evidence(BaseModel):
    page_number: int = Field(description="1-based page number in the PDF")
    text_snippet: str = Field(description="Raw text from which the value was extracted")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence 0–1")


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 Output: Parsed Tender Criteria
# ─────────────────────────────────────────────────────────────────────────────

class ExperienceCriteria(BaseModel):
    """
    Multi-condition experience rule. Any one of the OR conditions suffices.
    E.g. 3 works ≥ 40% OR 2 works ≥ 60% OR 1 work ≥ 80%.
    """
    option_a_count: Optional[int] = Field(None, description="Number of similar works required for option A")
    option_a_percent: Optional[float] = Field(None, description="% of estimated cost per work for option A")
    option_b_count: Optional[int] = Field(None, description="Number of similar works required for option B")
    option_b_percent: Optional[float] = Field(None, description="% of estimated cost per work for option B")
    option_c_count: Optional[int] = Field(None, description="Number of similar works required for option C")
    option_c_percent: Optional[float] = Field(None, description="% of estimated cost per work for option C")
    evidence: Optional[Evidence] = None


class TechnicalSpec(BaseModel):
    parameter: str = Field(description="Specification parameter name, e.g. 'Weight'")
    condition: str = Field(description="Condition operator: 'max', 'min', 'exact'")
    value: float
    unit: str = Field(description="Unit of measurement, e.g. 'gm', 'mm', 'rounds'")
    evidence: Optional[Evidence] = None


class TenderCriteria(BaseModel):
    """Complete eligibility criteria extracted from a tender document."""

    # Identification
    tender_id: str
    tender_title: str
    estimated_cost_inr: Optional[float] = Field(None, description="Estimated cost in INR")

    # Financial thresholds
    emd_amount_inr: Optional[float] = Field(None, description="Earnest Money Deposit in INR")
    emd_evidence: Optional[Evidence] = None

    performance_security_percent: Optional[float] = Field(
        None, description="Performance security as % of contract value"
    )
    solvency_percent: Optional[float] = Field(
        None, description="Required solvency as % of estimated cost (default 25)"
    )
    turnover_percent: Optional[float] = Field(
        None, description="Required avg annual turnover as % of estimated cost (default 30)"
    )
    financial_evidence: Optional[Evidence] = None

    # Experience
    experience: Optional[ExperienceCriteria] = None

    # Technical specs (for equipment/weapon tenders)
    technical_specs: list[TechnicalSpec] = Field(default_factory=list)

    # Mandatory documents checklist
    mandatory_documents: list[str] = Field(
        default_factory=list,
        description="List of mandatory document names bidder must submit"
    )

    # Exemptions
    emd_exempted_for: list[str] = Field(
        default_factory=list,
        description="Categories exempted from EMD, e.g. ['MSME', 'NSIC']"
    )

    # Raw extraction metadata
    raw_text_pages: int = Field(default=0, description="Total pages in source PDF")


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 Output: Processed Bidder Data
# ─────────────────────────────────────────────────────────────────────────────

class WorkExperience(BaseModel):
    description: str
    value_inr: float
    completion_year: Optional[int] = None
    client_name: Optional[str] = None
    evidence: Optional[Evidence] = None


class BidderData(BaseModel):
    """Data extracted from a single bidder's submission documents."""

    bidder_id: str
    firm_name: str

    # Financial data
    average_annual_turnover_inr: Optional[float] = None
    turnover_evidence: Optional[Evidence] = None

    solvency_inr: Optional[float] = None
    solvency_evidence: Optional[Evidence] = None

    # Registrations
    is_msme: bool = False
    is_nsic: bool = False
    is_dpiit_startup: bool = False
    registration_evidence: Optional[Evidence] = None

    # Experience
    past_works: list[WorkExperience] = Field(default_factory=list)

    # Technical compliance (for equipment tenders)
    tech_specs_claimed: dict[str, float] = Field(
        default_factory=dict,
        description="Parameter → claimed value mapping"
    )

    # Document presence (boolean checklist)
    documents_submitted: dict[str, bool] = Field(
        default_factory=dict,
        description="Document name → True/False"
    )

    # EMD
    emd_paid_inr: Optional[float] = None
    bid_security_declaration_present: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 Output: Evaluation Results
# ─────────────────────────────────────────────────────────────────────────────

class CriterionResult(BaseModel):
    criterion: str
    status: str  # "PASS" | "FAIL" | "EXEMPT" | "NOT_APPLICABLE"
    required_value: Optional[str] = None
    bidder_value: Optional[str] = None
    evidence: Optional[Evidence] = None
    note: Optional[str] = None


class BidderEvaluation(BaseModel):
    bidder_id: str
    firm_name: str
    overall_status: str  # "QUALIFIED" | "DISQUALIFIED"
    disqualification_reasons: list[str] = Field(default_factory=list)
    criteria_results: list[CriterionResult] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 Output: Final Audit Report
# ─────────────────────────────────────────────────────────────────────────────

class AuditReport(BaseModel):
    report_id: str
    tender_id: str
    tender_title: str
    generated_at: str  # ISO datetime string
    total_bidders: int
    qualified_count: int
    disqualified_count: int
    evaluations: list[BidderEvaluation]
    tender_criteria: TenderCriteria


# ─────────────────────────────────────────────────────────────────────────────
# API Request / Response shapes
# ─────────────────────────────────────────────────────────────────────────────

class EvaluationRequest(BaseModel):
    tender_id: str
    tender_text: str = Field(description="Full text extracted from tender PDF")
    bidder_submissions: list[dict] = Field(
        description="List of {bidder_id, firm_name, text} dicts"
    )


class EvaluationResponse(BaseModel):
    success: bool
    report: Optional[AuditReport] = None
    error: Optional[str] = None
