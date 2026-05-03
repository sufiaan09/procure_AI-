"""
Step 1: Tender Parser
─────────────────────
Takes the raw text of a tender PDF and uses Claude to extract all
eligibility criteria into a validated TenderCriteria object.

The LLM is used ONLY for extraction.
All downstream pass/fail logic is deterministic (Step 3).
"""

from __future__ import annotations
import json
from models.schemas import (
    TenderCriteria, Evidence, ExperienceCriteria, TechnicalSpec
)
from utils.llm_client import extract_json

# ─── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a procurement specialist for the Indian Government.
Your task is to read tender documents and
extract all eligibility and technical criteria into a structured JSON object.

Rules:
1. Respond ONLY with valid JSON — no markdown, no preamble.
2. All monetary values must be in numeric INR (e.g., 1200000 not "Rs. 12 Lakh").
3. All percentages must be numeric floats (e.g., 25.0 not "25%").
4. If a field is not mentioned in the document, set it to null.
5. For experience criteria, extract all OR conditions (option_a, option_b, option_c).
6. For every extracted value, include page_number and a short text_snippet
   (max 120 chars) from the document proving where you found it.
7. For confidence: 1.0 = explicitly stated, 0.7 = inferred, 0.4 = assumed default.

Return this exact JSON schema (no extra fields):
{
  "tender_id": "string",
  "tender_title": "string",
  "estimated_cost_inr": number | null,
  "emd_amount_inr": number | null,
  "emd_evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null,
  "performance_security_percent": number | null,
  "solvency_percent": number | null,
  "turnover_percent": number | null,
  "financial_evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null,
  "experience": {
    "option_a_count": int | null,
    "option_a_percent": float | null,
    "option_b_count": int | null,
    "option_b_percent": float | null,
    "option_c_count": int | null,
    "option_c_percent": float | null,
    "evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null
  } | null,
  "technical_specs": [
    {
      "parameter": "string",
      "condition": "max" | "min" | "exact",
      "value": number,
      "unit": "string",
      "evidence": {"page_number": int, "text_snippet": "string", "confidence": float} | null
    }
  ],
  "mandatory_documents": ["string"],
  "emd_exempted_for": ["string"]
}"""


def parse_tender(tender_text: str, tender_id: str = "UNKNOWN") -> TenderCriteria:
    """
    Parse a tender's text and return a validated TenderCriteria object.

    Args:
        tender_text: Full text of the tender PDF (with page markers).
        tender_id: Identifier for this tender (used if LLM can't find one).

    Returns:
        TenderCriteria: Validated, structured criteria object.
    """
    user_prompt = f"""Extract all eligibility and technical criteria from the following tender document.

TENDER DOCUMENT:
{tender_text[:30000]}
"""

    raw = extract_json(SYSTEM_PROMPT, user_prompt)

    # Ensure tender_id fallback
    if not raw.get("tender_id"):
        raw["tender_id"] = tender_id

    # Count pages from tender text
    page_count = tender_text.count("--- PAGE ")

    # Build Evidence objects
    def _ev(d: dict | None) -> Evidence | None:
        if not d:
            return None
        return Evidence(
            page_number=d.get("page_number", 0),
            text_snippet=d.get("text_snippet", ""),
            confidence=float(d.get("confidence", 0.7)),
        )

    # Build ExperienceCriteria
    exp_raw = raw.get("experience")
    experience = None
    if exp_raw:
        experience = ExperienceCriteria(
            option_a_count=exp_raw.get("option_a_count"),
            option_a_percent=exp_raw.get("option_a_percent"),
            option_b_count=exp_raw.get("option_b_count"),
            option_b_percent=exp_raw.get("option_b_percent"),
            option_c_count=exp_raw.get("option_c_count"),
            option_c_percent=exp_raw.get("option_c_percent"),
            evidence=_ev(exp_raw.get("evidence")),
        )

    # Build TechnicalSpec list
    tech_specs = []
    for spec_raw in raw.get("technical_specs", []):
        tech_specs.append(TechnicalSpec(
            parameter=spec_raw.get("parameter", ""),
            condition=spec_raw.get("condition", "max"),
            value=float(spec_raw.get("value", 0)),
            unit=spec_raw.get("unit", ""),
            evidence=_ev(spec_raw.get("evidence")),
        ))

    return TenderCriteria(
        tender_id=raw.get("tender_id", tender_id),
        tender_title=raw.get("tender_title", "Unknown Tender"),
        estimated_cost_inr=raw.get("estimated_cost_inr"),
        emd_amount_inr=raw.get("emd_amount_inr"),
        emd_evidence=_ev(raw.get("emd_evidence")),
        performance_security_percent=raw.get("performance_security_percent"),
        solvency_percent=raw.get("solvency_percent") or 25.0,
        turnover_percent=raw.get("turnover_percent") or 30.0,
        financial_evidence=_ev(raw.get("financial_evidence")),
        experience=experience,
        technical_specs=tech_specs,
        mandatory_documents=raw.get("mandatory_documents", []),
        emd_exempted_for=raw.get("emd_exempted_for", []),
        raw_text_pages=page_count,
    )


# ─── CLI helper ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from utils.pdf_utils import extract_full_text

    if len(sys.argv) < 2:
        print("Usage: python -m modules.tender_parser <path_to_tender.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    print(f"Extracting text from: {pdf_path}")
    text = extract_full_text(pdf_path)
    print(f"Extracted {len(text)} characters. Parsing with LLM...")

    criteria = parse_tender(text, tender_id="CLI_TEST")
    print("\n=== Extracted Tender Criteria ===")
    print(criteria.model_dump_json(indent=2))
