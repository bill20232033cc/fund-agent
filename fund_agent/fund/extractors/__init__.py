"""基金 extractor 公共入口。"""

from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    ProfileExtractionResult,
)
from fund_agent.fund.extractors.profile import extract_profile

__all__ = [
    "EvidenceAnchor",
    "ExtractedField",
    "ProfileExtractionResult",
    "extract_profile",
]
