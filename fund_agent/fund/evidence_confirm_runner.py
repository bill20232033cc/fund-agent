"""Evidence Confirm 生产 runner 公开边界，见基金分析模板第 0-7 章。

本模块是 Fund 层提供给 Service 的 typed facade。Service 只依赖这里暴露的
repository-bounded runner 契约，不直接导入底层 materializer/source 模块名；
具体实现仍由 Fund 层内部模块承载。
"""

from __future__ import annotations

from fund_agent.fund.evidence_confirm_sources import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
    run_repository_bounded_evidence_confirm,
)

__all__ = [
    "EvidenceConfirmRepositoryRunRequest",
    "EvidenceConfirmRepositoryRunResult",
    "run_repository_bounded_evidence_confirm",
]
