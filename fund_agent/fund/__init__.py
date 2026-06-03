"""Agent 层基金领域能力包公共入口。

本包承载基金类型、模板第 0-7 章、证据锚点、章节事实和证据可用性等 Fund
领域能力；不承担 UI、Service、Host 生命周期治理或 provider runtime 管理。
"""

from fund_agent.fund.evidence_availability import (
    EVIDENCE_AVAILABILITY_SCHEMA_VERSION,
    EvidenceAvailability,
    EvidenceGapReference,
    RequirementAvailability,
    derive_chapter_evidence_availability,
    derive_evidence_availability,
)

__all__ = [
    "EVIDENCE_AVAILABILITY_SCHEMA_VERSION",
    "EvidenceAvailability",
    "EvidenceGapReference",
    "RequirementAvailability",
    "derive_chapter_evidence_availability",
    "derive_evidence_availability",
]
