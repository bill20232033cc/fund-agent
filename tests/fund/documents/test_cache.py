"""文档缓存测试。"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from fund_agent.fund.documents.cache import (
    AnnualReportDocumentCache,
    PARSED_REPORT_SCHEMA_VERSION,
)
from fund_agent.fund.documents.models import (
    AnnualReportCacheProvenance,
    AnnualReportMetadata,
    AnnualReportSourceFailureCategory,
    AnnualReportSourceMetadata,
    AnnualReportSourceName,
    DocumentKey,
    ParsedAnnualReport,
    ReportSection,
)


def _build_stub_report(fund_code: str, year: int) -> ParsedAnnualReport:
    """构造缓存测试使用的可用年报对象。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        最小可用的年报对象。

    Raises:
        无显式抛出。
    """

    raw_text = "\n".join(
        (
            "§2 基金简介",
            "基金名称：缓存样本基金",
            "§3 主要财务指标、基金净值表现及利润分配情况",
            "净值表现正文",
            "§4 管理人报告",
            "管理人报告正文",
            "§8 投资组合报告",
            "投资组合正文",
            "§9 基金份额持有人信息",
            "持有人正文",
            "§10 基金份额变动",
            "份额变动正文",
            "缓存正文" * 300,
        )
    )
    section_ids = ("§2", "§3", "§4", "§8", "§9", "§10")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=year),
        raw_text=raw_text,
        sections={
            section_id: ReportSection(
                section_id=section_id,
                title=section_id,
                start_offset=raw_text.index(section_id),
                end_offset=raw_text.index(section_ids[index + 1]) if index + 1 < len(section_ids) else len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            )
            for index, section_id in enumerate(section_ids)
        },
        tables=(),
    )


def _build_unusable_report(fund_code: str, year: int) -> ParsedAnnualReport:
    """构造低质量缓存年报对象。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        不满足真实年报缓存门槛的年报对象。

    Raises:
        无显式抛出。
    """

    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=year),
        raw_text="§1 基金简介\n测试正文",
        sections={},
        tables=(),
    )


def _eid_metadata(fund_code: str = "110011", year: int = 2024) -> AnnualReportSourceMetadata:
    """构造缓存测试使用的 EID 来源元数据。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        EID 来源元数据。

    Raises:
        无显式抛出。
    """

    return AnnualReportSourceMetadata(
        source="eid",
        source_url="http://eid.test/fund/disclose/instance_show_pdf_id.do?instanceid=1248088",
        fund_code=fund_code,
        fund_id="1618",
        report_year=year,
        report_code="FB010010",
        report_desp="年度报告",
        report_name="中欧时代先锋股票型发起式证券投资基金2024年年度报告",
        upload_info_id="1248088",
        upload_info_detail_id="1285356",
        table_name="PDF",
        report_send_date="2025-03-31",
        operation_upload_type="9090-1010",
        corrections_num=0,
        fallback_used=False,
        selected_source="eid",
        source_mode="single_source_only",
        fallback_enabled=False,
        discovery_contract_version="eid_annual_report_discovery.v1",
    )


def test_source_metadata_round_trips_primary_failure_category() -> None:
    """验证来源元数据会序列化并反序列化主来源失败类别。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段 key 或往返值不稳定时抛出。
    """

    metadata = AnnualReportSourceMetadata(
        source="eastmoney",
        fallback_used=True,
        primary_failure_category="unavailable",
    )

    payload = metadata.to_dict()
    restored = AnnualReportSourceMetadata.from_dict(payload)

    assert payload["primary_failure_category"] == "unavailable"
    assert restored.primary_failure_category == "unavailable"


def test_source_metadata_round_trips_eid_single_source_policy() -> None:
    """验证 EID single-source policy 元数据会稳定序列化。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当新增 policy 字段无法往返时抛出。
    """

    metadata = _eid_metadata()

    payload = metadata.to_dict()
    restored = AnnualReportSourceMetadata.from_dict(payload)

    assert payload["selected_source"] == "eid"
    assert payload["source_mode"] == "single_source_only"
    assert payload["fallback_enabled"] is False
    assert payload["discovery_contract_version"] == "eid_annual_report_discovery.v1"
    assert restored == metadata


def test_source_metadata_legacy_or_unknown_failure_category_degrades_to_none() -> None:
    """验证旧元数据或未知失败类别兼容降级为空分类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧缓存无法兼容读取时抛出。
    """

    legacy = AnnualReportSourceMetadata.from_dict({"source": "eastmoney", "fallback_used": True})
    unknown = AnnualReportSourceMetadata.from_dict(
        {
            "source": "eastmoney",
            "fallback_used": True,
            "primary_failure_category": "unexpected",
        }
    )

    assert legacy.primary_failure_category is None
    assert unknown.primary_failure_category is None
    assert legacy.selected_source is None
    assert legacy.source_mode is None
    assert legacy.fallback_enabled is None


def test_document_models_exports_source_failure_category_without_sources_import() -> None:
    """验证 models 层独立拥有来源名称和失败类别类型。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 models 类型无法独立导入时抛出。
    """

    assert AnnualReportSourceMetadata(source="eid").source == "eid"
    assert AnnualReportSourceName is not None
    assert AnnualReportSourceFailureCategory is not None


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
            ("annual_report:110011:2024",),
        ).fetchone()

    assert tables == {"documents", "parsed_reports"}
    assert parsed_report_row == (PARSED_REPORT_SCHEMA_VERSION,)


@pytest.mark.asyncio
async def test_cache_returns_reference_metadata_without_body_or_path_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证引用元数据查询不会读取正文或 PDF 路径。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的 monkeypatch 工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当查询触发正文/PDF 路径访问或泄漏禁用字段时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    await cache.record_pdf_path(
        document_key,
        tmp_path / "missing.pdf",
        source_metadata=_eid_metadata(),
    )

    monkeypatch.setattr(
        cache,
        "_load_parsed_report_sync",
        lambda key: pytest.fail("reference metadata must not read parsed payload"),
    )
    monkeypatch.setattr(
        cache,
        "_get_pdf_entry_sync",
        lambda key: pytest.fail("reference metadata must not read PDF entry"),
    )

    result = await cache.get_reference_metadata(document_key)

    assert result.status == "available"
    assert result.reason is None
    assert result.metadata is not None
    payload = result.metadata.to_dict()
    assert payload == {
        "fund_code": "110011",
        "document_year": 2024,
        "report_type": "annual_report",
        "source": "eid",
        "selected_source": "eid",
        "source_mode": "single_source_only",
        "fallback_enabled": False,
        "fallback_used": False,
        "primary_failure_category": None,
        "metadata_identity_hash": result.metadata.metadata_identity_hash,
    }
    assert result.metadata.metadata_identity_hash is not None
    assert len(result.metadata.metadata_identity_hash) == 64
    forbidden_keys = {
        "pdf_path",
        "payload_path",
        "source_url",
        "report_name",
        "report_code",
        "report_desp",
        "upload_info_id",
        "updated_at",
    }
    assert forbidden_keys.isdisjoint(payload)


@pytest.mark.asyncio
async def test_cache_reference_metadata_reports_missing_without_pdf_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证缺失引用元数据时不会回退到 PDF 路径探测。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的 monkeypatch 工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失查询触发 PDF 条目读取时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    monkeypatch.setattr(
        cache,
        "_get_pdf_entry_sync",
        lambda key: pytest.fail("missing metadata must not probe PDF entry"),
    )

    result = await cache.get_reference_metadata(document_key)

    assert result.status == "missing"
    assert result.metadata is None
    assert result.reason == "metadata_row_missing"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("metadata", "reason"),
    (
        (
            AnnualReportSourceMetadata(
                source="eastmoney",
                fund_code="110011",
                report_year=2024,
                fallback_used=True,
            ),
            "source_not_eid",
        ),
        (
            AnnualReportSourceMetadata(
                source="eid",
                fund_code="110011",
                report_year=2024,
                selected_source="eid",
                source_mode="single_source_only",
                fallback_enabled=True,
                fallback_used=False,
            ),
            "fallback_enabled_not_false",
        ),
        (
            AnnualReportSourceMetadata(
                source="eid",
                fund_code="110011",
                report_year=2024,
                selected_source="eid",
                source_mode="single_source_only",
                fallback_enabled=False,
                fallback_used=False,
                primary_failure_category="schema_drift",
            ),
            "primary_failure_category_present",
        ),
        (
            AnnualReportSourceMetadata(
                source="eid",
                fund_code="004393",
                report_year=2024,
                selected_source="eid",
                source_mode="single_source_only",
                fallback_enabled=False,
                fallback_used=False,
            ),
            "source_metadata_fund_code_mismatch",
        ),
    ),
)
async def test_cache_reference_metadata_rejects_unsafe_metadata(
    tmp_path: Path,
    metadata: AnnualReportSourceMetadata,
    reason: str,
) -> None:
    """验证非 EID single-source 元数据被标记为不安全。

    Args:
        tmp_path: pytest 提供的临时目录。
        metadata: 待写入的来源元数据。
        reason: 预期失败原因。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不安全元数据被错误接受时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    await cache.record_pdf_path(
        document_key,
        tmp_path / "missing.pdf",
        source_metadata=metadata,
    )

    result = await cache.get_reference_metadata(document_key)

    assert result.status == "unsafe_metadata"
    assert result.metadata is None
    assert result.reason == reason


@pytest.mark.asyncio
async def test_cache_persists_pdf_source_metadata(tmp_path: Path) -> None:
    """验证 documents 表会持久化 PDF 来源元数据。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当来源元数据未正确持久化时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata = _eid_metadata()
    metadata = replace(
        metadata,
        fallback_used=True,
        primary_failure_category="not_found",
    )

    await cache.record_pdf_path(document_key, pdf_path, source_metadata=metadata)
    entry = await cache.get_pdf_entry(document_key)

    assert entry is not None
    assert entry.pdf_path == pdf_path
    assert entry.source_metadata == metadata
    assert entry.source_metadata.primary_failure_category == "not_found"


@pytest.mark.asyncio
async def test_cache_loads_legacy_documents_row_without_source_metadata(tmp_path: Path) -> None:
    """验证 legacy documents 行缺少来源元数据时仍可读取。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy 行不能兼容读取时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")

    await cache.initialize()
    with sqlite3.connect(cache.sqlite_path) as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_key,
                fund_code,
                year,
                document_kind,
                pdf_path,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "annual_report:110011:2024",
                "110011",
                2024,
                "annual_report",
                str(pdf_path),
                "2026-05-20T00:00:00+00:00",
            ),
        )
        connection.commit()

    entry = await cache.get_pdf_entry(document_key)

    assert entry is not None
    assert entry.pdf_path == pdf_path
    assert entry.source_metadata is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source_metadata_json",
    [
        "{not-json",
        json.dumps(["not", "object"], ensure_ascii=False),
        json.dumps({"source": "cninfo", "fund_code": "110011"}, ensure_ascii=False),
    ],
)
async def test_cache_degrades_invalid_source_metadata_json_to_none(
    tmp_path: Path,
    source_metadata_json: str,
) -> None:
    """验证损坏的来源元数据不会阻断 PDF cache entry 读取。

    Args:
        tmp_path: pytest 提供的临时目录。
        source_metadata_json: 损坏或非法的来源元数据 JSON。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当损坏元数据导致 PDF 路径不可用时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")

    await cache.initialize()
    with sqlite3.connect(cache.sqlite_path) as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_key,
                fund_code,
                year,
                document_kind,
                pdf_path,
                source_metadata_json,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "annual_report:110011:2024",
                "110011",
                2024,
                "annual_report",
                str(pdf_path),
                source_metadata_json,
                "2026-05-20T00:00:00+00:00",
            ),
        )
        connection.commit()

    entry = await cache.get_pdf_entry(document_key)
    pdf_path_only = await cache.get_pdf_path(document_key)

    assert entry is not None
    assert entry.pdf_path == pdf_path
    assert entry.source_metadata is None
    assert pdf_path_only == pdf_path


@pytest.mark.asyncio
async def test_parsed_report_payload_round_trips_metadata(tmp_path: Path) -> None:
    """验证 parsed report payload 会保留来源元数据。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当来源元数据未随 parsed payload 往返时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    metadata = _eid_metadata()
    report = replace(
        _build_stub_report("110011", 2024),
        metadata=AnnualReportMetadata(
            source=metadata,
            cache=AnnualReportCacheProvenance(source_metadata_present=True),
        ),
    )

    await cache.save_parsed_report(report, pdf_path=None)
    loaded_report = await cache.load_parsed_report(report.key)

    assert loaded_report is not None
    assert loaded_report.metadata.source == metadata


@pytest.mark.asyncio
async def test_legacy_parsed_report_without_metadata_loads_with_empty_metadata(
    tmp_path: Path,
) -> None:
    """验证旧 parsed JSON 缺少 metadata 时仍可加载。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧 payload 不能兼容读取时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    report = _build_stub_report("110011", 2024)
    await cache.initialize()
    payload_path = cache.parsed_reports_dir / "legacy.json"
    payload = report.to_dict()
    payload.pop("metadata")
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
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
                str(payload_path),
                PARSED_REPORT_SCHEMA_VERSION,
                "2026-05-20T00:00:00+00:00",
            ),
        )
        connection.commit()

    loaded_report = await cache.load_parsed_report(report.key)

    assert loaded_report is not None
    assert loaded_report.metadata.source is None


@pytest.mark.asyncio
async def test_save_parsed_report_aligns_explicit_source_metadata_with_payload(
    tmp_path: Path,
) -> None:
    """验证显式 source_metadata 会同步覆盖 documents 行和 parsed payload。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当两处持久化元数据静默分叉时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata_a = _eid_metadata(fund_code="110011")
    metadata_b = replace(metadata_a, upload_info_id="999999", upload_info_detail_id="888888")
    report = replace(
        _build_stub_report("110011", 2024),
        metadata=AnnualReportMetadata(source=metadata_a),
    )

    await cache.save_parsed_report(report, pdf_path=pdf_path, source_metadata=metadata_b)
    loaded_report = await cache.load_parsed_report(report.key)
    entry = await cache.get_pdf_entry(report.key)

    assert loaded_report is not None
    assert entry is not None
    assert loaded_report.metadata.source == metadata_b
    assert entry.source_metadata == metadata_b


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


@pytest.mark.asyncio
async def test_cache_returns_none_for_corrupt_parsed_report_payload(tmp_path: Path) -> None:
    """验证损坏 parsed report JSON 会安全回退为缓存未命中。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当损坏 payload 抛出异常或被误用时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    payload_path = tmp_path / "corrupt.json"
    payload_path.write_text('{"key": ', encoding="utf-8")
    await cache.initialize()

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
                str(payload_path),
                PARSED_REPORT_SCHEMA_VERSION,
                "2026-05-17T00:00:00+00:00",
            ),
        )
        connection.commit()

    assert await cache.load_parsed_report(document_key) is None


@pytest.mark.asyncio
async def test_parsed_report_load_and_save_are_serialized_per_cache_instance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 parsed report 读写在同一缓存实例内串行执行。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 parsed report 读写临界区发生重入时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    report = _build_stub_report("110011", 2024)
    active_operations = 0
    max_active_operations = 0
    original_load = cache._load_parsed_report_sync
    original_save = cache._save_parsed_report_sync

    def _enter_operation() -> None:
        nonlocal active_operations, max_active_operations
        active_operations += 1
        max_active_operations = max(max_active_operations, active_operations)

    def _exit_operation() -> None:
        nonlocal active_operations
        active_operations -= 1

    def _serialized_load(key: DocumentKey) -> ParsedAnnualReport | None:
        _enter_operation()
        try:
            return original_load(key)
        finally:
            _exit_operation()

    def _serialized_save(
        parsed_report: ParsedAnnualReport,
        pdf_path: Path | None,
        source_metadata: AnnualReportSourceMetadata | None,
    ) -> None:
        _enter_operation()
        try:
            original_save(parsed_report, pdf_path, source_metadata)
        finally:
            _exit_operation()

    monkeypatch.setattr(cache, "_load_parsed_report_sync", _serialized_load)
    monkeypatch.setattr(cache, "_save_parsed_report_sync", _serialized_save)

    await asyncio.gather(
        cache.save_parsed_report(report),
        cache.load_parsed_report(document_key),
        cache.save_parsed_report(report),
        cache.load_parsed_report(document_key),
    )

    assert max_active_operations == 1


@pytest.mark.asyncio
async def test_cache_rejects_unusable_parsed_report_payload(tmp_path: Path) -> None:
    """验证低质量 parsed report 缓存不会被误用为真实年报。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当低质量缓存仍被返回时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    report = _build_unusable_report("110011", 2024)

    await cache.save_parsed_report(report, pdf_path=None)

    assert await cache.load_parsed_report(document_key) is None


@pytest.mark.asyncio
async def test_save_parsed_report_cleans_temp_payload_when_atomic_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 parsed report 原子替换失败时会清理临时 payload。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败写入留下临时文件或 SQLite 行时抛出。
    """

    cache = AnnualReportDocumentCache(tmp_path / "documents-cache")
    document_key = DocumentKey(fund_code="110011", year=2024)
    report = _build_stub_report("110011", 2024)
    original_replace = Path.replace

    def _fail_payload_replace(source_path: Path, target_path: Path) -> Path:
        """只让目标 parsed payload 的原子替换失败。

        Args:
            source_path: 临时 payload 路径。
            target_path: 最终 payload 路径。

        Returns:
            非目标路径时返回原始 replace 结果。

        Raises:
            OSError: 目标 payload 替换时模拟文件系统失败。
        """

        if target_path == cache._parsed_report_payload_path(document_key):
            raise OSError("simulated atomic replace failure")
        return original_replace(source_path, target_path)

    monkeypatch.setattr(Path, "replace", _fail_payload_replace)

    with pytest.raises(OSError, match="simulated atomic replace failure"):
        await cache.save_parsed_report(report, pdf_path=None)

    await cache.initialize()
    leaked_temp_paths = tuple(cache.parsed_reports_dir.glob("*.json"))
    with sqlite3.connect(cache.sqlite_path) as connection:
        row = connection.execute(
            "SELECT payload_path FROM parsed_reports WHERE document_key = ?",
            (_document_cache_key_for_test(document_key),),
        ).fetchone()

    assert leaked_temp_paths == ()
    assert row is None


def _document_cache_key_for_test(key: DocumentKey) -> str:
    """构造测试断言使用的缓存主键。

    Args:
        key: 文档主键。

    Returns:
        与缓存实现一致的 SQLite 主键字符串。

    Raises:
        无显式抛出。
    """

    return f"{key.document_kind}:{key.fund_code}:{key.year}"
