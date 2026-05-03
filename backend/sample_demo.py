"""
Sample data for the /api/demo/evaluate endpoint.
Mirrors a real ProcureAI 9mm Pistol procurement tender scenario.
"""
from models.schemas import (
    TenderCriteria, BidderData, Evidence,
    ExperienceCriteria, TechnicalSpec, WorkExperience
)


def get_sample_data() -> tuple[TenderCriteria, list[BidderData]]:
    criteria = TenderCriteria(
        tender_id="PAI-9MM-2024-001",
        tender_title="Supply of 9mm Pistols to ProcureAI — Batch 2024",
        estimated_cost_inr=4_80_00_000,   # ₹4.8 Crore
        emd_amount_inr=12_00_000,          # ₹12 Lakh
        emd_evidence=Evidence(
            page_number=3,
            text_snippet="Earnest Money Deposit of Rs. 12,00,000/- is required",
            confidence=1.0,
        ),
        performance_security_percent=5.0,
        solvency_percent=25.0,
        turnover_percent=30.0,
        financial_evidence=Evidence(
            page_number=5,
            text_snippet="Solvency certificate of not less than 25% of estimated cost and annual turnover of 30%",
            confidence=1.0,
        ),
        experience=ExperienceCriteria(
            option_a_count=3,
            option_a_percent=40.0,
            option_b_count=2,
            option_b_percent=60.0,
            option_c_count=1,
            option_c_percent=80.0,
            evidence=Evidence(
                page_number=6,
                text_snippet="Three similar works at 40% OR two works at 60% OR one work at 80% of estimated cost",
                confidence=1.0,
            ),
        ),
        technical_specs=[
            TechnicalSpec(
                parameter="Weight (with empty magazine)",
                condition="max",
                value=900.0,
                unit="gm",
                evidence=Evidence(page_number=8, text_snippet="Weight: Not more than 900gm with empty magazine", confidence=1.0),
            ),
            TechnicalSpec(
                parameter="Overall Height",
                condition="max",
                value=150.0,
                unit="mm",
                evidence=Evidence(page_number=8, text_snippet="Overall height: Not more than 150mm", confidence=1.0),
            ),
            TechnicalSpec(
                parameter="Magazine Capacity",
                condition="min",
                value=15.0,
                unit="rounds",
                evidence=Evidence(page_number=8, text_snippet="Magazine capacity: Minimum 15 rounds", confidence=1.0),
            ),
        ],
        mandatory_documents=[
            "PAN Card",
            "GSTIN Certificate",
            "Firm Registration Certificate",
            "Income Tax Returns (3 years)",
            "Banker's Certificate of Solvency",
            "Tender Acceptance Letter",
            "Manufacturing License (Arms Act)",
        ],
        emd_exempted_for=["MSME", "NSIC", "Startup"],
        raw_text_pages=12,
    )

    bidders = [
        # ── Bidder 1: Fully qualified ──────────────────────────────────────
        BidderData(
            bidder_id="B001",
            firm_name="Bharat Arms Manufacturing Ltd.",
            average_annual_turnover_inr=1_80_00_000,   # ₹1.8 Cr (> 30% of ₹4.8 Cr = ₹1.44 Cr)
            turnover_evidence=Evidence(
                page_number=2,
                text_snippet="Average annual turnover for FY21-22, 22-23, 23-24: Rs. 1,80,00,000/-",
                confidence=1.0,
            ),
            solvency_inr=1_50_00_000,   # ₹1.5 Cr (> 25% of ₹4.8 Cr = ₹1.2 Cr)
            solvency_evidence=Evidence(
                page_number=4,
                text_snippet="Certified that the firm has solvency of Rs. 1,50,00,000/-",
                confidence=1.0,
            ),
            past_works=[
                WorkExperience(
                    description="Supply of 9mm pistols to BSF",
                    value_inr=2_00_00_000,  # 41.6% of ₹4.8 Cr
                    completion_year=2022,
                    client_name="BSF HQ",
                    evidence=Evidence(page_number=6, text_snippet="Contract No. BSF/2022/ARMS/091", confidence=1.0),
                ),
                WorkExperience(
                    description="Supply of 9mm pistols to CISF",
                    value_inr=1_95_00_000,
                    completion_year=2023,
                    client_name="CISF",
                    evidence=Evidence(page_number=7, text_snippet="Contract No. CISF/2023/WEPN/44", confidence=1.0),
                ),
                WorkExperience(
                    description="Supply of sidearms to state police",
                    value_inr=2_10_00_000,
                    completion_year=2023,
                    client_name="UP Police",
                    evidence=Evidence(page_number=7, text_snippet="Contract No. UPP/ARMS/2023/11", confidence=1.0),
                ),
            ],
            tech_specs_claimed={
                "Weight (with empty magazine)": 870.0,
                "Overall Height": 142.0,
                "Magazine Capacity": 17.0,
            },
            documents_submitted={
                "PAN Card": True,
                "GSTIN Certificate": True,
                "Firm Registration Certificate": True,
                "Income Tax Returns (3 years)": True,
                "Banker's Certificate of Solvency": True,
                "Tender Acceptance Letter": True,
                "Manufacturing License (Arms Act)": True,
            },
            emd_paid_inr=12_00_000,
        ),

        # ── Bidder 2: Fails turnover + missing document ────────────────────
        BidderData(
            bidder_id="B002",
            firm_name="Rajputana Defence Products Pvt. Ltd.",
            average_annual_turnover_inr=80_00_000,   # ₹80L — too low
            turnover_evidence=Evidence(
                page_number=2,
                text_snippet="Annual turnover: Rs. 80,00,000/-",
                confidence=1.0,
            ),
            solvency_inr=1_40_00_000,
            solvency_evidence=Evidence(
                page_number=3,
                text_snippet="Solvency: Rs. 1,40,00,000/-",
                confidence=1.0,
            ),
            past_works=[
                WorkExperience(
                    description="Supply of pistols to state reserve",
                    value_inr=2_90_00_000,
                    completion_year=2023,
                    client_name="MP Police",
                ),
            ],
            tech_specs_claimed={
                "Weight (with empty magazine)": 920.0,  # OVER LIMIT
                "Overall Height": 145.0,
                "Magazine Capacity": 15.0,
            },
            documents_submitted={
                "PAN Card": True,
                "GSTIN Certificate": True,
                "Firm Registration Certificate": True,
                "Income Tax Returns (3 years)": True,
                "Banker's Certificate of Solvency": True,
                "Tender Acceptance Letter": False,   # MISSING
                "Manufacturing License (Arms Act)": True,
            },
            emd_paid_inr=12_00_000,
        ),

        # ── Bidder 3: MSME, EMD-exempt, submits BSD, otherwise qualified ──
        BidderData(
            bidder_id="B003",
            firm_name="Sovereign Small Arms (MSME)",
            is_msme=True,
            registration_evidence=Evidence(
                page_number=1,
                text_snippet="MSME Registration No. MH/2019/0087432",
                confidence=1.0,
            ),
            average_annual_turnover_inr=1_60_00_000,
            turnover_evidence=Evidence(
                page_number=2,
                text_snippet="FY21: 1.5 Cr, FY22: 1.6 Cr, FY23: 1.7 Cr — average Rs. 1,60,00,000",
                confidence=0.9,
            ),
            solvency_inr=1_30_00_000,
            solvency_evidence=Evidence(
                page_number=3,
                text_snippet="Solvency certificate: Rs. 1,30,00,000/-",
                confidence=1.0,
            ),
            past_works=[
                WorkExperience(
                    description="Supply of 9mm pistols to ITBP",
                    value_inr=4_10_00_000,  # 85% of ₹4.8 Cr — satisfies Option C
                    completion_year=2022,
                    client_name="ITBP HQ",
                ),
            ],
            tech_specs_claimed={
                "Weight (with empty magazine)": 880.0,
                "Overall Height": 148.0,
                "Magazine Capacity": 16.0,
            },
            documents_submitted={
                "PAN Card": True,
                "GSTIN Certificate": True,
                "Firm Registration Certificate": True,
                "Income Tax Returns (3 years)": True,
                "Banker's Certificate of Solvency": True,
                "Tender Acceptance Letter": True,
                "Manufacturing License (Arms Act)": True,
            },
            emd_paid_inr=None,
            bid_security_declaration_present=True,
        ),
    ]

    return criteria, bidders
