"""
Unit tests for the Evaluation Engine (Step 3).
These run without any API key — pure deterministic logic testing.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from models.schemas import (
    TenderCriteria, BidderData, Evidence, ExperienceCriteria, TechnicalSpec, WorkExperience
)
from modules.evaluation_engine import evaluate_bidder


def _base_criteria() -> TenderCriteria:
    return TenderCriteria(
        tender_id="TEST-001",
        tender_title="Test Tender",
        estimated_cost_inr=1_00_00_000,   # ₹1 Cr
        emd_amount_inr=2_50_000,           # ₹2.5 L
        solvency_percent=25.0,
        turnover_percent=30.0,
        experience=ExperienceCriteria(
            option_a_count=3, option_a_percent=40.0,
            option_b_count=2, option_b_percent=60.0,
            option_c_count=1, option_c_percent=80.0,
        ),
        technical_specs=[
            TechnicalSpec(parameter="Weight", condition="max", value=900.0, unit="gm"),
        ],
        mandatory_documents=["PAN Card", "GSTIN Certificate"],
        emd_exempted_for=["MSME"],
    )


def _base_bidder(bidder_id="B001") -> BidderData:
    """A fully qualified bidder."""
    return BidderData(
        bidder_id=bidder_id,
        firm_name="Test Firm",
        average_annual_turnover_inr=35_00_000,   # 35% — passes 30%
        solvency_inr=30_00_000,                  # 30% — passes 25%
        past_works=[
            WorkExperience(description="Work A", value_inr=45_00_000, completion_year=2023),
            WorkExperience(description="Work B", value_inr=42_00_000, completion_year=2022),
            WorkExperience(description="Work C", value_inr=41_00_000, completion_year=2021),
        ],
        tech_specs_claimed={"Weight": 850.0},
        documents_submitted={"PAN Card": True, "GSTIN Certificate": True},
        emd_paid_inr=2_50_000,
    )


class TestEMD:
    def test_emd_pass(self):
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        emd = next(r for r in result.criteria_results if r.criterion == "EMD Payment")
        assert emd.status == "PASS"

    def test_emd_fail_low(self):
        b = _base_bidder()
        b.emd_paid_inr = 1_00_000
        result = evaluate_bidder(_base_criteria(), b)
        emd = next(r for r in result.criteria_results if r.criterion == "EMD Payment")
        assert emd.status == "FAIL"

    def test_emd_exempt_msme_with_bsd(self):
        b = _base_bidder()
        b.is_msme = True
        b.emd_paid_inr = None
        b.bid_security_declaration_present = True
        result = evaluate_bidder(_base_criteria(), b)
        emd = next(r for r in result.criteria_results if r.criterion == "EMD Payment")
        assert emd.status == "EXEMPT"

    def test_emd_exempt_msme_without_bsd_fails(self):
        b = _base_bidder()
        b.is_msme = True
        b.emd_paid_inr = None
        b.bid_security_declaration_present = False
        result = evaluate_bidder(_base_criteria(), b)
        emd = next(r for r in result.criteria_results if r.criterion == "EMD Payment")
        assert emd.status == "FAIL"


class TestSolvency:
    def test_solvency_pass(self):
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        sol = next(r for r in result.criteria_results if r.criterion == "Solvency Certificate")
        assert sol.status == "PASS"

    def test_solvency_fail(self):
        b = _base_bidder()
        b.solvency_inr = 10_00_000   # 10% — below 25% required
        result = evaluate_bidder(_base_criteria(), b)
        sol = next(r for r in result.criteria_results if r.criterion == "Solvency Certificate")
        assert sol.status == "FAIL"

    def test_solvency_missing(self):
        b = _base_bidder()
        b.solvency_inr = None
        result = evaluate_bidder(_base_criteria(), b)
        sol = next(r for r in result.criteria_results if r.criterion == "Solvency Certificate")
        assert sol.status == "FAIL"


class TestTurnover:
    def test_turnover_pass(self):
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        to = next(r for r in result.criteria_results if r.criterion == "Average Annual Turnover")
        assert to.status == "PASS"

    def test_turnover_fail(self):
        b = _base_bidder()
        b.average_annual_turnover_inr = 20_00_000   # 20% — below 30%
        result = evaluate_bidder(_base_criteria(), b)
        to = next(r for r in result.criteria_results if r.criterion == "Average Annual Turnover")
        assert to.status == "FAIL"


class TestExperience:
    def test_experience_option_a(self):
        """3 works ≥ 40% → Option A satisfied."""
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        exp = next(r for r in result.criteria_results if r.criterion == "Past Experience")
        assert exp.status == "PASS"

    def test_experience_option_c(self):
        """1 big work ≥ 80% → Option C satisfied."""
        b = _base_bidder()
        b.past_works = [
            WorkExperience(description="One big work", value_inr=85_00_000, completion_year=2023),
        ]
        result = evaluate_bidder(_base_criteria(), b)
        exp = next(r for r in result.criteria_results if r.criterion == "Past Experience")
        assert exp.status == "PASS"

    def test_experience_none_satisfied(self):
        b = _base_bidder()
        b.past_works = [
            WorkExperience(description="Small work", value_inr=10_00_000, completion_year=2023),
        ]
        result = evaluate_bidder(_base_criteria(), b)
        exp = next(r for r in result.criteria_results if r.criterion == "Past Experience")
        assert exp.status == "FAIL"


class TestTechSpecs:
    def test_weight_pass(self):
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        wt = next(r for r in result.criteria_results if "Weight" in r.criterion)
        assert wt.status == "PASS"

    def test_weight_fail_over_limit(self):
        b = _base_bidder()
        b.tech_specs_claimed["Weight"] = 950.0
        result = evaluate_bidder(_base_criteria(), b)
        wt = next(r for r in result.criteria_results if "Weight" in r.criterion)
        assert wt.status == "FAIL"

    def test_tech_spec_not_provided(self):
        b = _base_bidder()
        b.tech_specs_claimed = {}
        result = evaluate_bidder(_base_criteria(), b)
        wt = next(r for r in result.criteria_results if "Weight" in r.criterion)
        assert wt.status == "FAIL"


class TestDocuments:
    def test_all_docs_present(self):
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        doc = next(r for r in result.criteria_results if "PAN Card" in r.criterion)
        assert doc.status == "PASS"

    def test_missing_doc_fails(self):
        b = _base_bidder()
        b.documents_submitted["PAN Card"] = False
        result = evaluate_bidder(_base_criteria(), b)
        doc = next(r for r in result.criteria_results if "PAN Card" in r.criterion)
        assert doc.status == "FAIL"


class TestOverallStatus:
    def test_fully_qualified(self):
        result = evaluate_bidder(_base_criteria(), _base_bidder())
        assert result.overall_status == "QUALIFIED"
        assert result.disqualification_reasons == []

    def test_disqualified_on_one_fail(self):
        b = _base_bidder()
        b.emd_paid_inr = 0
        result = evaluate_bidder(_base_criteria(), b)
        assert result.overall_status == "DISQUALIFIED"
        assert len(result.disqualification_reasons) >= 1
