"""受控 live EID 年报失败分支观察脚本。

该脚本只用于 `controlled live EID failure-branch evidence gate`。它通过
`FundDocumentRepository.load_annual_report()` 执行一次 EID single-source
年报 acquisition，输出安全 JSON 标量，不保留 PDF bytes、原始文本或完整解析内容。
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Final

from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.cache import AnnualReportDocumentCache
from fund_agent.fund.documents.repository import FundDocumentRepository
from fund_agent.fund.documents.sources import (
    AnnualReportSourceAggregateError,
    AnnualReportSourceFallbackBlockedError,
    AnnualReportSourceNotFoundError,
    AnnualReportSourceOrchestrator,
    AnnualReportSourceUnavailableError,
    EidAnnualReportSource,
)

FUND_CODE: Final[str] = "006597"
REPORT_YEAR: Final[int] = 2024


def _safe_exception_payload(exc: BaseException) -> dict[str, object]:
    """把异常映射为安全 JSON 标量。

    Args:
        exc: live acquisition 过程中捕获到的异常。

    Returns:
        不含原始响应、PDF bytes 或原始文本的异常摘要。

    Raises:
        无显式抛出。
    """

    payload: dict[str, object] = {
        "exception_type": type(exc).__name__,
        "message": str(exc),
    }
    if isinstance(exc, AnnualReportSourceFallbackBlockedError):
        payload["category"] = exc.blocking_failure.category
        payload["source"] = exc.blocking_failure.source
    elif isinstance(exc, AnnualReportSourceAggregateError):
        payload["failures"] = [
            {
                "source": failure.source,
                "category": failure.category,
                "message": failure.message,
            }
            for failure in exc.failures
        ]
    elif isinstance(exc, AnnualReportSourceNotFoundError):
        payload["category"] = "not_found"
    elif isinstance(exc, AnnualReportSourceUnavailableError):
        payload["category"] = "unavailable"
    return payload


def _safe_report_payload(report: Any) -> dict[str, object]:
    """把成功解析结果映射为安全 JSON 标量。

    Args:
        report: `FundDocumentRepository.load_annual_report()` 返回的解析年报对象。

    Returns:
        不含 PDF bytes、原始文本或完整表格内容的成功摘要。

    Raises:
        无显式抛出。
    """

    source_metadata = report.metadata.source
    cache_metadata = report.metadata.cache
    return {
        "status": "success",
        "fund_code": report.key.fund_code,
        "report_year": report.key.year,
        "document_kind": report.key.document_kind,
        "section_count": len(report.sections),
        "table_count": len(report.tables),
        "raw_text_length": len(report.raw_text),
        "source": source_metadata.source if source_metadata else None,
        "selected_source": source_metadata.selected_source if source_metadata else None,
        "source_mode": source_metadata.source_mode if source_metadata else None,
        "fallback_enabled": source_metadata.fallback_enabled if source_metadata else None,
        "fallback_used": source_metadata.fallback_used if source_metadata else None,
        "primary_failure_category": source_metadata.primary_failure_category if source_metadata else None,
        "discovery_contract_version": (
            source_metadata.discovery_contract_version if source_metadata else None
        ),
        "pdf_cache_hit": cache_metadata.pdf_cache_hit,
        "parsed_cache_hit": cache_metadata.parsed_cache_hit,
        "source_metadata_present": cache_metadata.source_metadata_present,
    }


async def _run_observation() -> dict[str, object]:
    """执行一次受控 EID single-source FDR acquisition。

    Args:
        无。

    Returns:
        成功或失败的安全 JSON 标量结果。

    Raises:
        无显式抛出；所有异常会被转换为安全结果。
    """

    with tempfile.TemporaryDirectory(prefix="fund-agent-live-eid-") as tmp_dir:
        root = Path(tmp_dir)
        eid_source = EidAnnualReportSource(cache_dir=root / "pdf-cache")
        orchestrator = AnnualReportSourceOrchestrator((eid_source,))
        adapter = AnnualReportPdfAdapter(orchestrator)
        repository = FundDocumentRepository(adapter)
        # Gate-local cache isolation: production code has no public parsed-cache
        # injection point, so this script replaces the repository instance cache
        # without changing runtime source code or global defaults.
        repository._cache = AnnualReportDocumentCache(root_dir=root / "document-cache")  # noqa: SLF001
        try:
            report = await repository.load_annual_report(FUND_CODE, REPORT_YEAR, force_refresh=True)
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "fund_code": FUND_CODE,
                "report_year": REPORT_YEAR,
                "error": _safe_exception_payload(exc),
            }
        return _safe_report_payload(report)


def main() -> None:
    """运行 live observation 并输出单行 JSON。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    result = asyncio.run(_run_observation())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
