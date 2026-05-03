"""
Step 2: Bidder Processor
─────────────────────────
Takes a bidder's submission text (from OCR/PDF extraction) and uses
Claude to extract all relevant financial, registration, and compliance data.

Again: LLM for extraction only. No decisions made here.
"""

from __future__ import annotations
from models.schemas import BidderData, Evidence, WorkExperience
from utils.llm_client import extract_json

SYSTEM_PROMPT = """You are a document analyst reviewing Indian government tender bid submissions.
Extract all relevant bidder information from the provided documents into structured JSON.

Rules:
1. Respond ONLY with valid JSON — no markdown, no preamble.
2. All monetary values must be numeric INR.
3. average_annual_turnover_inr: compute the mean of the last 3 financial years if multiple years are given.
4. solvency_inr: extract from banker's certificate or auditor's statement.
5. For boolean flags (is_msme, is_nsic, is_dpiit_startup): true only if certificate/registration is present.
6. For every extracted value, include page_number and text_snippet (max 120 chars).
7. confidence: 1.0 = explicitly stated with certificate, 0.7 = stated without certificate, 0.4 = inferred.
8. documents_submitted: map each document name to true/false based on presence in submission.

Return this exact JSON schema:
{
  "firm_name": "string",
  "average_annual_turnover_inr": number | null,
  "turnover_evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null,
  "solvency_inr": number | null,
  "solvency_evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null,
  "is_msme": boolean,
  "is_nsic": boolean,
  "is_dpiit_startup": boolean,
  "registration_evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null,
  "past_works": [
    {
      "description": "string",
      "value_inr": number,
      "completion_year": int | null,
      "client_name": "string" | null,
      "evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null
    }
  ],
  "tech_specs_claimed": {"parameter_name": numeric_value},
  "documents_submitted": {"document_name": boolean},
  "emd_paid_inr": number | null,
  "bid_security_declaration_present": boolean
}"""


def process_bidder(
    bidder_id: str,
    firm_name_hint: str,
    submission_text: str,
    mandatory_docs: list[str],
) -> BidderData:
    """
    Process a bidder's submission and return a validated BidderData object.

    Args:
        bidder_id: Unique identifier for this bidder.
        firm_name_hint: Name from the cover page (used as fallback).
        submission_text: Full OCR/extracted text of all submitted documents.
        mandatory_docs: List of document names from the tender criteria
                        (used to prime the documents_submitted checklist).
    """
    docs_hint = "\n".join(f"- {d}" for d in mandatory_docs) if mandatory_docs else "(none specified)"

    user_prompt = f"""Extract all bidder information from the following submission documents.

Mandatory documents to check for (mark each as true/false in documents_submitted):
{docs_hint}

BIDDER SUBMISSION DOCUMENTS:
{submission_text[:25000]}
"""

    raw = extract_json(SYSTEM_PROMPT, user_prompt)

    def _ev(d: dict | None) -> Evidence | None:
        if not d:
            return None
        return Evidence(
            page_number=d.get("page_number", 0),
            text_snippet=d.get("text_snippet", ""),
            confidence=float(d.get("confidence", 0.7)),
        )

    past_works = []
    for w in raw.get("past_works", []):
        past_works.append(WorkExperience(
            description=w.get("description", ""),
            value_inr=float(w.get("value_inr", 0)),
            completion_year=w.get("completion_year"),
            client_name=w.get("client_name"),
            evidence=_ev(w.get("evidence")),
        ))

    return BidderData(
        bidder_id=bidder_id,
        firm_name=raw.get("firm_name") or firm_name_hint,
        average_annual_turnover_inr=raw.get("average_annual_turnover_inr"),
        turnover_evidence=_ev(raw.get("turnover_evidence")),
        solvency_inr=raw.get("solvency_inr"),
        solvency_evidence=_ev(raw.get("solvency_evidence")),
        is_msme=bool(raw.get("is_msme", False)),
        is_nsic=bool(raw.get("is_nsic", False)),
        is_dpiit_startup=bool(raw.get("is_dpiit_startup", False)),
        registration_evidence=_ev(raw.get("registration_evidence")),
        past_works=past_works,
        tech_specs_claimed=raw.get("tech_specs_claimed", {}),
        documents_submitted=raw.get("documents_submitted", {}),
        emd_paid_inr=raw.get("emd_paid_inr"),
        bid_security_declaration_present=bool(raw.get("bid_security_declaration_present", False)),
    )


# ─── CLI helper ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from utils.pdf_utils import extract_full_text

    if len(sys.argv) < 2:
        print("Usage: python -m modules.bidder_processor <path_to_bidder_submission.pdf>")
        sys.exit(1)

    text = extract_full_text(sys.argv[1])
    result = process_bidder("B001", "Unknown Firm", text, [
        "PAN Card", "GSTIN Certificate", "Income Tax Returns (3 years)",
        "Firm Registration Certificate", "Tender Acceptance Letter",
        "Banker's Certificate of Solvency",
    ])
    print(result.model_dump_json(indent=2))
