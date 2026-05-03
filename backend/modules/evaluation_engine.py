"""
Step 3: Evaluation Engine
──────────────────────────
Pure rule-based evaluation. No LLM calls here — only deterministic
comparisons of extracted values against tender criteria.

Every decision is traceable and auditable.
"""

from __future__ import annotations
from models.schemas import (
    TenderCriteria, BidderData,
    BidderEvaluation, CriterionResult, Evidence
)


def _inr(amount: float) -> str:
    """Format a number as INR lakhs for display."""
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.2f} Cr"
    if amount >= 100_000:
        return f"₹{amount/100_000:.2f} L"
    return f"₹{amount:,.0f}"


def _pct(v: float) -> str:
    return f"{v:.1f}%"


def evaluate_bidder(
    criteria: TenderCriteria,
    bidder: BidderData,
) -> BidderEvaluation:
    """
    Evaluate a single bidder against the tender criteria.
    Returns a BidderEvaluation with Pass/Fail for every criterion.
    """
    results: list[CriterionResult] = []
    disqualification_reasons: list[str] = []

    est_cost = criteria.estimated_cost_inr or 0.0

    # ── 1. EMD Check ──────────────────────────────────────────────────────────
    is_emd_exempt = (
        bidder.is_msme and "MSME" in criteria.emd_exempted_for
        or bidder.is_nsic and "NSIC" in criteria.emd_exempted_for
        or bidder.is_dpiit_startup and "DPIIT" in criteria.emd_exempted_for
        or bidder.is_dpiit_startup and "Startup" in criteria.emd_exempted_for
    )

    if criteria.emd_amount_inr is None:
        results.append(CriterionResult(
            criterion="EMD Payment",
            status="NOT_APPLICABLE",
            note="No EMD specified in tender",
        ))
    elif is_emd_exempt:
        # Exempt: must have submitted a Bid Security Declaration
        if bidder.bid_security_declaration_present:
            results.append(CriterionResult(
                criterion="EMD Payment",
                status="EXEMPT",
                required_value=_inr(criteria.emd_amount_inr),
                bidder_value="Bid Security Declaration submitted",
                note="Bidder is EMD-exempt (MSME/NSIC/Startup). BSD present.",
            ))
        else:
            results.append(CriterionResult(
                criterion="EMD Payment",
                status="FAIL",
                required_value=_inr(criteria.emd_amount_inr),
                bidder_value="No Bid Security Declaration found",
                note="EMD-exempt bidder must submit a Bid Security Declaration.",
            ))
            disqualification_reasons.append("Missing Bid Security Declaration (EMD-exempt bidder)")
    else:
        if bidder.emd_paid_inr is not None and bidder.emd_paid_inr >= criteria.emd_amount_inr:
            results.append(CriterionResult(
                criterion="EMD Payment",
                status="PASS",
                required_value=_inr(criteria.emd_amount_inr),
                bidder_value=_inr(bidder.emd_paid_inr),
                evidence=criteria.emd_evidence,
            ))
        else:
            paid_str = _inr(bidder.emd_paid_inr) if bidder.emd_paid_inr else "Not found"
            results.append(CriterionResult(
                criterion="EMD Payment",
                status="FAIL",
                required_value=_inr(criteria.emd_amount_inr),
                bidder_value=paid_str,
                evidence=criteria.emd_evidence,
            ))
            disqualification_reasons.append(
                f"Insufficient EMD: required {_inr(criteria.emd_amount_inr)}, "
                f"submitted {paid_str}"
            )

    # ── 2. Solvency Check ─────────────────────────────────────────────────────
    if est_cost > 0 and criteria.solvency_percent:
        required_solvency = est_cost * criteria.solvency_percent / 100
        if bidder.solvency_inr is not None and bidder.solvency_inr >= required_solvency:
            results.append(CriterionResult(
                criterion="Solvency Certificate",
                status="PASS",
                required_value=f">= {_inr(required_solvency)} ({_pct(criteria.solvency_percent)} of est. cost)",
                bidder_value=_inr(bidder.solvency_inr),
                evidence=bidder.solvency_evidence,
            ))
        else:
            bidder_str = _inr(bidder.solvency_inr) if bidder.solvency_inr else "Not provided"
            results.append(CriterionResult(
                criterion="Solvency Certificate",
                status="FAIL",
                required_value=f">= {_inr(required_solvency)} ({_pct(criteria.solvency_percent)} of est. cost)",
                bidder_value=bidder_str,
                evidence=bidder.solvency_evidence,
            ))
            disqualification_reasons.append(
                f"Solvency insufficient: required {_inr(required_solvency)}, provided {bidder_str}"
            )

    # ── 3. Annual Turnover Check ──────────────────────────────────────────────
    if est_cost > 0 and criteria.turnover_percent:
        required_turnover = est_cost * criteria.turnover_percent / 100
        if (bidder.average_annual_turnover_inr is not None
                and bidder.average_annual_turnover_inr >= required_turnover):
            results.append(CriterionResult(
                criterion="Average Annual Turnover",
                status="PASS",
                required_value=f">= {_inr(required_turnover)} ({_pct(criteria.turnover_percent)} of est. cost)",
                bidder_value=_inr(bidder.average_annual_turnover_inr),
                evidence=bidder.turnover_evidence,
            ))
        else:
            bidder_str = (
                _inr(bidder.average_annual_turnover_inr)
                if bidder.average_annual_turnover_inr
                else "Not provided"
            )
            results.append(CriterionResult(
                criterion="Average Annual Turnover",
                status="FAIL",
                required_value=f">= {_inr(required_turnover)} ({_pct(criteria.turnover_percent)} of est. cost)",
                bidder_value=bidder_str,
                evidence=bidder.turnover_evidence,
            ))
            disqualification_reasons.append(
                f"Turnover insufficient: required {_inr(required_turnover)}, provided {bidder_str}"
            )

    # ── 4. Past Experience Check ──────────────────────────────────────────────
    if criteria.experience and est_cost > 0:
        exp = criteria.experience
        satisfied = False
        satisfied_option = ""

        def _works_at_pct(count: int | None, pct: float | None) -> bool:
            if count is None or pct is None:
                return False
            threshold = est_cost * pct / 100
            qualifying = [w for w in bidder.past_works if w.value_inr >= threshold]
            return len(qualifying) >= count

        if _works_at_pct(exp.option_a_count, exp.option_a_percent):
            satisfied = True
            satisfied_option = (
                f"Option A: {exp.option_a_count} works "
                f"≥ {_pct(exp.option_a_percent or 0)} of estimated cost"
            )
        elif _works_at_pct(exp.option_b_count, exp.option_b_percent):
            satisfied = True
            satisfied_option = (
                f"Option B: {exp.option_b_count} works "
                f"≥ {_pct(exp.option_b_percent or 0)} of estimated cost"
            )
        elif _works_at_pct(exp.option_c_count, exp.option_c_percent):
            satisfied = True
            satisfied_option = (
                f"Option C: {exp.option_c_count} work(s) "
                f"≥ {_pct(exp.option_c_percent or 0)} of estimated cost"
            )

        works_summary = (
            f"{len(bidder.past_works)} similar works submitted"
            if bidder.past_works
            else "No past works provided"
        )

        results.append(CriterionResult(
            criterion="Past Experience",
            status="PASS" if satisfied else "FAIL",
            required_value=(
                f"A: {exp.option_a_count}×{_pct(exp.option_a_percent or 0)} OR "
                f"B: {exp.option_b_count}×{_pct(exp.option_b_percent or 0)} OR "
                f"C: {exp.option_c_count}×{_pct(exp.option_c_percent or 0)}"
            ),
            bidder_value=satisfied_option or works_summary,
            evidence=exp.evidence,
        ))
        if not satisfied:
            disqualification_reasons.append(
                "Past experience criteria not met (none of the OR conditions satisfied)"
            )

    # ── 5. Technical Specifications Check ────────────────────────────────────
    for spec in criteria.technical_specs:
        claimed = bidder.tech_specs_claimed.get(spec.parameter)
        if claimed is None:
            results.append(CriterionResult(
                criterion=f"Tech Spec: {spec.parameter}",
                status="FAIL",
                required_value=f"{spec.condition} {spec.value} {spec.unit}",
                bidder_value="Not provided",
                evidence=spec.evidence,
            ))
            disqualification_reasons.append(
                f"Technical spec not declared: {spec.parameter}"
            )
            continue

        if spec.condition == "max":
            passes = claimed <= spec.value
        elif spec.condition == "min":
            passes = claimed >= spec.value
        else:  # exact
            passes = abs(claimed - spec.value) < 0.01

        results.append(CriterionResult(
            criterion=f"Tech Spec: {spec.parameter}",
            status="PASS" if passes else "FAIL",
            required_value=f"{spec.condition} {spec.value} {spec.unit}",
            bidder_value=f"{claimed} {spec.unit}",
            evidence=spec.evidence,
        ))
        if not passes:
            disqualification_reasons.append(
                f"Tech spec {spec.parameter}: required {spec.condition} {spec.value} {spec.unit}, "
                f"claimed {claimed} {spec.unit}"
            )

    # ── 6. Mandatory Documents Check ─────────────────────────────────────────
    for doc_name in criteria.mandatory_documents:
        submitted = bidder.documents_submitted.get(doc_name, False)
        results.append(CriterionResult(
            criterion=f"Document: {doc_name}",
            status="PASS" if submitted else "FAIL",
            required_value="Must be present",
            bidder_value="Submitted" if submitted else "Missing",
        ))
        if not submitted:
            disqualification_reasons.append(f"Missing mandatory document: {doc_name}")

    overall = "QUALIFIED" if not disqualification_reasons else "DISQUALIFIED"

    return BidderEvaluation(
        bidder_id=bidder.bidder_id,
        firm_name=bidder.firm_name,
        overall_status=overall,
        disqualification_reasons=disqualification_reasons,
        criteria_results=results,
    )


def evaluate_all(
    criteria: TenderCriteria,
    bidders: list[BidderData],
) -> list[BidderEvaluation]:
    """Evaluate all bidders and return sorted list (qualified first)."""
    evaluations = [evaluate_bidder(criteria, b) for b in bidders]
    evaluations.sort(key=lambda e: (0 if e.overall_status == "QUALIFIED" else 1, e.firm_name))
    return evaluations
