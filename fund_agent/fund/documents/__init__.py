"""基金文档仓库公共入口。

当前仅实现年报读取契约，供后续结构化提取与模板章节分析复用。
"""

from fund_agent.fund.documents.models import (
    ANNUAL_REPORT_DOCUMENT_KIND,
    DocumentKey,
    ParsedAnnualReport,
    ParsedTable,
    ReportSection,
)
from fund_agent.fund.documents.repository import FundDocumentRepository

__all__ = [
    "ANNUAL_REPORT_DOCUMENT_KIND",
    "DocumentKey",
    "ParsedAnnualReport",
    "ParsedTable",
    "ReportSection",
    "FundDocumentRepository",
]
