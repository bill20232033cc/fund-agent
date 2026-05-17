"""基金 extractor 公共入口。"""

from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    PerformanceExtractionResult,
    ProfileExtractionResult,
)
from fund_agent.fund.extractors.performance import extract_performance
from fund_agent.fund.extractors.profile import extract_profile

__all__ = [
    "EvidenceAnchor",
    "ExtractedField",
    "PerformanceExtractionResult",
    "ProfileExtractionResult",
    "extract_performance",
    "extract_profile",
]
