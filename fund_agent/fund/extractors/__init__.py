"""基金 extractor 公共入口。"""

from fund_agent.fund.extractors.models import (
    BondRiskEvidenceValue,
    EvidenceAnchor,
    ExtractedField,
    HoldingsShareChangeExtractionResult,
    IndexProfileValue,
    ManagerOwnershipExtractionResult,
    PerformanceExtractionResult,
    ProfileExtractionResult,
    TrackingErrorValue,
)
from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence
from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change
from fund_agent.fund.extractors.manager_ownership import extract_manager_ownership
from fund_agent.fund.extractors.performance import extract_performance
from fund_agent.fund.extractors.profile import extract_profile

__all__ = [
    "EvidenceAnchor",
    "ExtractedField",
    "BondRiskEvidenceValue",
    "HoldingsShareChangeExtractionResult",
    "IndexProfileValue",
    "ManagerOwnershipExtractionResult",
    "PerformanceExtractionResult",
    "ProfileExtractionResult",
    "TrackingErrorValue",
    "extract_bond_risk_evidence",
    "extract_holdings_share_change",
    "extract_manager_ownership",
    "extract_performance",
    "extract_profile",
]
