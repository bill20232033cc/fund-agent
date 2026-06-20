"""Fund Processor/Extractor 公共入口。

本包当前提供 no-live Processor/Extractor 契约、注册表和按基金类型拆分的年报
`ParsedAnnualReport` processor，不导出 Docling、candidate、PDF/cache/source helper
或生产 parser 替换能力。
"""

from fund_agent.fund.processors.active_annual import (
    FIELD_FAMILY_MAPPINGS,
    ActiveFundAnnualProcessor,
    BondFundAnnualProcessor,
    EnhancedIndexFundAnnualProcessor,
    FieldFamilyMapping,
    FofFundAnnualProcessor,
    IndexFundAnnualProcessor,
    QdiiFundAnnualProcessor,
)
from fund_agent.fund.processors.fund_disclosure_processor import (
    BondFundDisclosureDocumentProcessor,
    EnhancedIndexDisclosureDocumentProcessor,
    FofFundDisclosureDocumentProcessor,
    FundDisclosureDocumentProcessor,
    IndexFundDisclosureDocumentProcessor,
    QdiiFundDisclosureDocumentProcessor,
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
    "BondFundAnnualProcessor",
    "BondFundDisclosureDocumentProcessor",
    "CandidateBoundaryStatus",
    "EnhancedIndexDisclosureDocumentProcessor",
    "EnhancedIndexFundAnnualProcessor",
    "FIELD_FAMILY_MAPPINGS",
    "FieldFamilyMapping",
    "FofFundDisclosureDocumentProcessor",
    "FofFundAnnualProcessor",
    "FundExtractionGap",
    "FundDisclosureDocumentProcessor",
    "FundFieldFamilyResult",
    "FundProcessorDispatchKey",
    "FundProcessorInput",
    "FundProcessorRegistry",
    "FundProcessorResult",
    "IndexFundDisclosureDocumentProcessor",
    "IndexFundAnnualProcessor",
    "QdiiFundDisclosureDocumentProcessor",
    "QdiiFundAnnualProcessor",
    "UnsupportedFundProcessorError",
]
