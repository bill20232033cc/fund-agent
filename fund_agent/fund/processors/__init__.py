"""Fund Processor/Extractor 公共入口。

本包当前只提供 S1 no-live Processor/Extractor 契约、注册表和主动基金年报
`ParsedAnnualReport` processor，不导出 Docling、candidate、PDF/cache/source helper
或生产 parser 替换能力。
"""

from fund_agent.fund.processors.active_annual import (
    FIELD_FAMILY_MAPPINGS,
    ActiveFundAnnualProcessor,
    FieldFamilyMapping,
)
from fund_agent.fund.processors.contracts import (
    CandidateBoundaryStatus,
    FundExtractionGap,
    FundFieldFamilyResult,
    FundProcessorDispatchKey,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.registry import (
    FundProcessorRegistry,
    UnsupportedFundProcessorError,
)

__all__ = [
    "ActiveFundAnnualProcessor",
    "CandidateBoundaryStatus",
    "FIELD_FAMILY_MAPPINGS",
    "FieldFamilyMapping",
    "FundExtractionGap",
    "FundFieldFamilyResult",
    "FundProcessorDispatchKey",
    "FundProcessorInput",
    "FundProcessorRegistry",
    "FundProcessorResult",
    "UnsupportedFundProcessorError",
]
