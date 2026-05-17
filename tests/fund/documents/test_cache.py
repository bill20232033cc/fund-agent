"""文档缓存测试。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from fund_agent.fund.documents.cache import (
    AnnualReportDocumentCache,
    PARSED_REPORT_SCHEMA_VERSION,
)
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport


def _build_stub_report(fund_code: str, year: int) -> ParsedAnnualReport:
    """构造缓存测试使用的最小年报对象。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        最小可用的年报对象。

    Raises:
        无显式抛出。
    """

    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=year),
        raw_text="§1 基金简介\n缓存正文",
        sections={},
        tables=(),
    )


@pytest.mark.asyncio
async def test_cache_persists_pdf_metadata_and_parsed_report(tmp_path: Path) -> None:
    """验证缓存会同时物化 documents 元信息与 parsed report 内容。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存内容未正确落地时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    report = _build_stub_report("110011", 2024)

    await cache.record_pdf_path(document_key, pdf_path)
    await cache.save_parsed_report(report, pdf_path=pdf_path)

    assert await cache.get_pdf_path(document_key) == pdf_path
    assert await cache.load_parsed_report(document_key) == report

    with sqlite3.connect(cache.sqlite_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        parsed_report_row = connection.execute(
            "SELECT schema_version FROM parsed_reports WHERE document_key = ?",
            (f"annual_report:110011:2024",),
        ).fetchone()

    assert tables == {"documents", "parsed_reports"}
    assert parsed_report_row == (PARSED_REPORT_SCHEMA_VERSION,)


@pytest.mark.asyncio
async def test_cache_returns_none_for_missing_or_stale_payload(tmp_path: Path) -> None:
    """验证缓存在 payload 缺失时会安全回退为未命中。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 payload 仍错误返回缓存对象时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    await cache.initialize()

    assert await cache.load_parsed_report(document_key) is None

    with sqlite3.connect(cache.sqlite_path) as connection:
        connection.execute(
            """
            INSERT INTO parsed_reports (
                document_key,
                fund_code,
                year,
                document_kind,
                payload_path,
                schema_version,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "annual_report:110011:2024",
                "110011",
                2024,
                "annual_report",
                str(tmp_path / "missing.json"),
                PARSED_REPORT_SCHEMA_VERSION,
                "2026-05-17T00:00:00+00:00",
            ),
        )
        connection.commit()

    assert await cache.load_parsed_report(document_key) is None
