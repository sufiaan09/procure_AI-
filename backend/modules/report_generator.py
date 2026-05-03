"""
Step 4: Report Generator
─────────────────────────
Assembles the final AuditReport from evaluated bidder data.
Also provides a function to render the report as a human-readable
Markdown string (for export or email).
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from models.schemas import (
    TenderCriteria, BidderEvaluation, AuditReport
)


def generate_report(
    criteria: TenderCriteria,
    evaluations: list[BidderEvaluation],
) -> AuditReport:
    """Create a structured AuditReport from criteria + evaluations."""
    qualified = [e for e in evaluations if e.overall_status == "QUALIFIED"]
    disqualified = [e for e in evaluations if e.overall_status == "DISQUALIFIED"]

    return AuditReport(
        report_id=f"RPT-{uuid.uuid4().hex[:8].upper()}",
        tender_id=criteria.tender_id,
        tender_title=criteria.tender_title,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_bidders=len(evaluations),
        qualified_count=len(qualified),
        disqualified_count=len(disqualified),
        evaluations=evaluations,
        tender_criteria=criteria,
    )


def report_to_markdown(report: AuditReport) -> str:
    """Render an AuditReport as a Markdown string."""
    lines: list[str] = []
    c = report.tender_criteria

    lines += [
        f"# ProcureAI Tender Evaluation Report",
        f"",
        f"**Report ID:** {report.report_id}  ",
        f"**Tender:** {report.tender_title}  ",
        f"**Tender ID:** {report.tender_id}  ",
        f"**Generated:** {report.generated_at}  ",
        f"",
        f"---",
        f"",
        f"## Summary",
        f"",
        f"| | Count |",
        f"|---|---|",
        f"| Total Bidders | {report.total_bidders} |",
        f"| ✅ Qualified | {report.qualified_count} |",
        f"| ❌ Disqualified | {report.disqualified_count} |",
        f"",
        f"---",
        f"",
        f"## Tender Criteria Used",
        f"",
    ]

    if c.estimated_cost_inr:
        lines.append(f"- **Estimated Cost:** ₹{c.estimated_cost_inr:,.0f}")
    if c.emd_amount_inr:
        lines.append(f"- **EMD Required:** ₹{c.emd_amount_inr:,.0f}")
    if c.solvency_percent:
        lines.append(f"- **Solvency Required:** {c.solvency_percent}% of estimated cost")
    if c.turnover_percent:
        lines.append(f"- **Turnover Required:** {c.turnover_percent}% of estimated cost")
    if c.performance_security_percent:
        lines.append(f"- **Performance Security:** {c.performance_security_percent}% of contract value")
    if c.experience:
        exp = c.experience
        lines.append(f"- **Experience (any one):**")
        if exp.option_a_count:
            lines.append(f"  - Option A: {exp.option_a_count} works ≥ {exp.option_a_percent}% of cost")
        if exp.option_b_count:
            lines.append(f"  - Option B: {exp.option_b_count} works ≥ {exp.option_b_percent}% of cost")
        if exp.option_c_count:
            lines.append(f"  - Option C: {exp.option_c_count} works ≥ {exp.option_c_percent}% of cost")

    lines += ["", "---", "", "## Bidder Evaluations", ""]

    for ev in report.evaluations:
        status_icon = "✅" if ev.overall_status == "QUALIFIED" else "❌"
        lines += [
            f"### {status_icon} {ev.firm_name} ({ev.bidder_id})",
            f"**Overall Status: {ev.overall_status}**",
            "",
        ]
        if ev.disqualification_reasons:
            lines.append("**Disqualification Reasons:**")
            for r in ev.disqualification_reasons:
                lines.append(f"- {r}")
            lines.append("")

        lines.append("| Criterion | Status | Required | Bidder Value | Evidence |")
        lines.append("|---|---|---|---|---|")
        for cr in ev.criteria_results:
            icon = {"PASS": "✅", "FAIL": "❌", "EXEMPT": "🔵", "NOT_APPLICABLE": "—"}.get(cr.status, "?")
            ev_str = ""
            if cr.evidence:
                ev_str = f"Page {cr.evidence.page_number}"
            lines.append(
                f"| {cr.criterion} | {icon} {cr.status} | "
                f"{cr.required_value or '—'} | {cr.bidder_value or '—'} | {ev_str} |"
            )
        lines += ["", "---", ""]

    return "\n".join(lines)
