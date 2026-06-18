"""基金文档仓库公共数据模型。

这些模型承载年报解析后的稳定契约，供后续模板第 1-4 章与证据锚点提取使用。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Final, Literal

# P1-S1 当前只支持年报文档类型，避免在多个模块散落同一个魔法字符串。
ANNUAL_REPORT_DOCUMENT_KIND: Final[Literal["annual_report"]] = "annual_report"
AnnualReportSourceName = Literal["eid", "eastmoney"]
AnnualReportSourceMode = Literal["single_source_only"]
AnnualReportSourceFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
]
AnnualReportReferenceMetadataStatus = Literal["available", "missing", "unsafe_metadata"]


@dataclass(frozen=True, slots=True)
class AnnualReportSourceMetadata:
    """年报来源元数据。

    Attributes:
        source: 来源名称。
        source_url: 来源 URL。
        fund_code: 基金代码。
        fund_id: 来源平台基金 ID。
        report_year: 报告年份。
        report_code: 来源报告类型代码。
        report_desp: 来源报告类型描述。
        report_name: 来源报告名称。
        upload_info_id: 来源公告实例 ID。
        upload_info_detail_id: 来源公告详情 ID。
        table_name: 来源文件类型标记。
        report_send_date: 来源报告发送日期。
        operation_upload_type: 来源上传操作类型。
        corrections_num: 来源更正次数。
        fallback_used: 是否为 fallback 来源命中。
        primary_failure_category: 主来源失败后允许 fallback 的失败类别。
        selected_source: 当前来源策略选中的来源。
        source_mode: 当前来源策略模式。
        fallback_enabled: 当前来源策略是否启用 fallback。
        discovery_contract_version: 来源 discovery 契约版本。
    """

    source: AnnualReportSourceName | None = None
    source_url: str | None = None
    fund_code: str | None = None
    fund_id: str | None = None
    report_year: int | None = None
    report_code: str | None = None
    report_desp: str | None = None
    report_name: str | None = None
    upload_info_id: str | None = None
    upload_info_detail_id: str | None = None
    table_name: str | None = None
    report_send_date: str | None = None
    operation_upload_type: str | None = None
    corrections_num: int | None = None
    fallback_used: bool = False
    primary_failure_category: AnnualReportSourceFailureCategory | None = None
    selected_source: AnnualReportSourceName | None = None
    source_mode: AnnualReportSourceMode | None = None
    fallback_enabled: bool | None = None
    discovery_contract_version: str | None = None

    def to_dict(self) -> dict[str, object]:
        """把来源元数据序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "source": self.source,
            "source_url": self.source_url,
            "fund_code": self.fund_code,
            "fund_id": self.fund_id,
            "report_year": self.report_year,
            "report_code": self.report_code,
            "report_desp": self.report_desp,
            "report_name": self.report_name,
            "upload_info_id": self.upload_info_id,
            "upload_info_detail_id": self.upload_info_detail_id,
            "table_name": self.table_name,
            "report_send_date": self.report_send_date,
            "operation_upload_type": self.operation_upload_type,
            "corrections_num": self.corrections_num,
            "fallback_used": self.fallback_used,
            "primary_failure_category": self.primary_failure_category,
            "selected_source": self.selected_source,
            "source_mode": self.source_mode,
            "fallback_enabled": self.fallback_enabled,
            "discovery_contract_version": self.discovery_contract_version,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AnnualReportSourceMetadata":
        """从字典反序列化来源元数据。

        Args:
            payload: JSON 兼容字典。

        Returns:
            反序列化后的来源元数据。

        Raises:
            ValueError: 字段值无法转换时抛出。
        """

        source_value = _optional_string(payload.get("source"))
        selected_source_value = _optional_string(payload.get("selected_source"))
        source_mode_value = _optional_string(payload.get("source_mode"))
        failure_category_value = _optional_string(payload.get("primary_failure_category"))
        return cls(
            source=_normalize_source_name(source_value),
            source_url=_optional_string(payload.get("source_url")),
            fund_code=_optional_string(payload.get("fund_code")),
            fund_id=_optional_string(payload.get("fund_id")),
            report_year=_optional_int(payload.get("report_year")),
            report_code=_optional_string(payload.get("report_code")),
            report_desp=_optional_string(payload.get("report_desp")),
            report_name=_optional_string(payload.get("report_name")),
            upload_info_id=_optional_string(payload.get("upload_info_id")),
            upload_info_detail_id=_optional_string(payload.get("upload_info_detail_id")),
            table_name=_optional_string(payload.get("table_name")),
            report_send_date=_optional_string(payload.get("report_send_date")),
            operation_upload_type=_optional_string(payload.get("operation_upload_type")),
            corrections_num=_optional_int(payload.get("corrections_num")),
            fallback_used=bool(payload.get("fallback_used", False)),
            primary_failure_category=_normalize_failure_category(failure_category_value),
            selected_source=_normalize_source_name(selected_source_value),
            source_mode=_normalize_source_mode(source_mode_value),
            fallback_enabled=_optional_bool(payload.get("fallback_enabled")),
            discovery_contract_version=_optional_string(
                payload.get("discovery_contract_version")
            ),
        )


@dataclass(frozen=True, slots=True)
class AnnualReportCacheProvenance:
    """年报缓存命中来源信息。

    Attributes:
        pdf_path: 原始 PDF 本地缓存路径。
        pdf_cache_hit: 是否命中 PDF 路径缓存。
        parsed_cache_hit: 是否命中 parsed report 缓存。
        source_metadata_present: 是否存在来源元数据。
        cache_schema_version: parsed report 缓存 schema 版本。
    """

    pdf_path: str | None = None
    pdf_cache_hit: bool = False
    parsed_cache_hit: bool = False
    source_metadata_present: bool = False
    cache_schema_version: int | None = None

    def to_dict(self) -> dict[str, object]:
        """把缓存来源信息序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "pdf_path": self.pdf_path,
            "pdf_cache_hit": self.pdf_cache_hit,
            "parsed_cache_hit": self.parsed_cache_hit,
            "source_metadata_present": self.source_metadata_present,
            "cache_schema_version": self.cache_schema_version,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AnnualReportCacheProvenance":
        """从字典反序列化缓存来源信息。

        Args:
            payload: JSON 兼容字典。

        Returns:
            反序列化后的缓存来源信息。

        Raises:
            ValueError: 字段值无法转换时抛出。
        """

        return cls(
            pdf_path=_optional_string(payload.get("pdf_path")),
            pdf_cache_hit=bool(payload.get("pdf_cache_hit", False)),
            parsed_cache_hit=bool(payload.get("parsed_cache_hit", False)),
            source_metadata_present=bool(payload.get("source_metadata_present", False)),
            cache_schema_version=_optional_int(payload.get("cache_schema_version")),
        )


@dataclass(frozen=True, slots=True)
class AnnualReportMetadata:
    """年报解析结果元数据。

    Attributes:
        source: 年报来源元数据。
        cache: 缓存命中来源信息。
    """

    source: AnnualReportSourceMetadata | None = None
    cache: AnnualReportCacheProvenance = field(default_factory=AnnualReportCacheProvenance)

    def to_dict(self) -> dict[str, object]:
        """把年报元数据序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "source": self.source.to_dict() if self.source is not None else None,
            "cache": self.cache.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> "AnnualReportMetadata":
        """从字典反序列化年报元数据。

        Args:
            payload: JSON 兼容字典；旧缓存缺失时可为 ``None``。

        Returns:
            反序列化后的年报元数据。

        Raises:
            ValueError: 字段值无法转换时抛出。
        """

        if not isinstance(payload, dict):
            return cls()
        raw_source = payload.get("source")
        source = (
            AnnualReportSourceMetadata.from_dict(dict(raw_source))
            if isinstance(raw_source, dict)
            else None
        )
        raw_cache = payload.get("cache")
        cache = (
            AnnualReportCacheProvenance.from_dict(dict(raw_cache))
            if isinstance(raw_cache, dict)
            else AnnualReportCacheProvenance()
        )
        return cls(source=source, cache=cache)


@dataclass(frozen=True, slots=True)
class AnnualReportPdfFetchResult:
    """年报 PDF 获取结果。

    Attributes:
        pdf_path: 已缓存的本地 PDF 路径。
        source_metadata: 与本次 PDF 获取同源的来源元数据。
    """

    pdf_path: Path
    source_metadata: AnnualReportSourceMetadata | None = None


@dataclass(frozen=True, slots=True)
class AnnualReportReferenceMetadata:
    """年报同源引用可用性元数据。

    该模型只承载模板第 1-6 章后续证据准入所需的来源身份字段，不包含
    PDF 路径、缓存路径、正文、表格、章节、来源 URL 或公告详情字段。

    Attributes:
        fund_code: 基金代码。
        document_year: 报告年份。
        report_type: 报告类型，当前只支持年报。
        source: 来源名称。
        selected_source: 来源策略选中的来源。
        source_mode: 来源策略模式。
        fallback_enabled: 来源策略是否启用 fallback。
        fallback_used: 是否实际使用 fallback。
        primary_failure_category: 主来源失败类别。
        metadata_identity_hash: 只覆盖本模型允许字段的稳定摘要。
    """

    fund_code: str
    document_year: int
    report_type: Literal["annual_report"] = ANNUAL_REPORT_DOCUMENT_KIND
    source: AnnualReportSourceName | None = None
    selected_source: AnnualReportSourceName | None = None
    source_mode: AnnualReportSourceMode | None = None
    fallback_enabled: bool | None = None
    fallback_used: bool = False
    primary_failure_category: AnnualReportSourceFailureCategory | None = None
    metadata_identity_hash: str | None = None

    def with_identity_hash(self) -> "AnnualReportReferenceMetadata":
        """返回带稳定身份摘要的元数据副本。

        Args:
            无。

        Returns:
            ``metadata_identity_hash`` 已填充的元数据。

        Raises:
            无显式抛出。
        """

        return replace(self, metadata_identity_hash=self.compute_identity_hash())

    def compute_identity_hash(self) -> str:
        """计算只覆盖允许字段的稳定 SHA-256 摘要。

        Args:
            无。

        Returns:
            十六进制 SHA-256 摘要。

        Raises:
            无显式抛出。
        """

        payload = self.to_dict(include_hash=False)
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self, *, include_hash: bool = True) -> dict[str, object]:
        """把元数据序列化为 JSON 兼容字典。

        Args:
            include_hash: 是否包含 ``metadata_identity_hash`` 字段。

        Returns:
            只含允许字段的字典结构。

        Raises:
            无显式抛出。
        """

        payload: dict[str, object] = {
            "fund_code": self.fund_code,
            "document_year": self.document_year,
            "report_type": self.report_type,
            "source": self.source,
            "selected_source": self.selected_source,
            "source_mode": self.source_mode,
            "fallback_enabled": self.fallback_enabled,
            "fallback_used": self.fallback_used,
            "primary_failure_category": self.primary_failure_category,
        }
        if include_hash:
            payload["metadata_identity_hash"] = self.metadata_identity_hash
        return payload


@dataclass(frozen=True, slots=True)
class AnnualReportReferenceMetadataResult:
    """年报同源引用元数据查询结果。

    Attributes:
        status: 查询状态。
        metadata: 状态为 ``available`` 时返回的元数据。
        reason: ``missing`` 或 ``unsafe_metadata`` 的稳定原因。
    """

    status: AnnualReportReferenceMetadataStatus
    metadata: AnnualReportReferenceMetadata | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        """把查询结果序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            查询结果字典。

        Raises:
            无显式抛出。
        """

        return {
            "status": self.status,
            "metadata": self.metadata.to_dict() if self.metadata is not None else None,
            "reason": self.reason,
        }


def _optional_string(value: Any) -> str | None:
    """把可选字段规范化为字符串。

    Args:
        value: 原始字段值。

    Returns:
        非空字符串；空值返回 ``None``。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _optional_int(value: Any) -> int | None:
    """把可选字段规范化为整数。

    Args:
        value: 原始字段值。

    Returns:
        整数；空值返回 ``None``。

    Raises:
        ValueError: 非空字段无法转换为整数时抛出。
    """

    normalized = _optional_string(value)
    if normalized is None:
        return None
    return int(normalized)


def _optional_bool(value: Any) -> bool | None:
    """把可选字段规范化为布尔值。

    Args:
        value: 原始字段值。

    Returns:
        布尔值；空值返回 ``None``。

    Raises:
        ValueError: 非空字段无法转换为布尔值时抛出。
    """

    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("true", "1"):
            return True
        if normalized in ("false", "0"):
            return False
    raise ValueError(f"布尔字段非法: {value!r}")


def _normalize_source_name(source: str | None) -> AnnualReportSourceName | None:
    """校验并规范化年报来源名称。

    Args:
        source: 原始来源名称。

    Returns:
        合法来源名称；空值返回 ``None``。

    Raises:
        ValueError: 来源名称不在闭集内时抛出。
    """

    if source is None:
        return None
    if source not in ("eid", "eastmoney"):
        raise ValueError(f"未知年报来源: {source}")
    return source


def _normalize_failure_category(
    category: str | None,
) -> AnnualReportSourceFailureCategory | None:
    """校验并规范化年报来源失败类别。

    Args:
        category: 原始失败类别。

    Returns:
        合法失败类别；空值或未知类别返回 ``None``，以兼容旧缓存和损坏字段。

    Raises:
        无显式抛出。
    """

    if category in (
        "not_found",
        "unavailable",
        "schema_drift",
        "identity_mismatch",
        "integrity_error",
    ):
        return category
    return None


def _normalize_source_mode(mode: str | None) -> AnnualReportSourceMode | None:
    """校验并规范化年报来源策略模式。

    Args:
        mode: 原始来源策略模式。

    Returns:
        合法来源策略模式；空值返回 ``None``。

    Raises:
        ValueError: 来源策略模式不在闭集内时抛出。
    """

    if mode is None:
        return None
    if mode != "single_source_only":
        raise ValueError(f"未知年报来源策略模式: {mode}")
    return mode


@dataclass(frozen=True, slots=True)
class DocumentKey:
    """年报文档唯一标识。

    Attributes:
        fund_code: 基金代码。
        year: 报告年份。
        document_kind: 文档类型，P1-S1 仅支持 annual_report。
    """

    fund_code: str
    year: int
    document_kind: Literal["annual_report"] = ANNUAL_REPORT_DOCUMENT_KIND

    def to_dict(self) -> dict[str, object]:
        """把文档主键序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "fund_code": self.fund_code,
            "year": self.year,
            "document_kind": self.document_kind,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "DocumentKey":
        """从字典反序列化文档主键。

        Args:
            payload: JSON 兼容字典。

        Returns:
            反序列化后的文档主键对象。

        Raises:
            KeyError: 缺少必需字段时抛出。
            ValueError: 字段值无法转换时抛出。
        """

        return cls(
            fund_code=str(payload["fund_code"]),
            year=int(payload["year"]),
            document_kind=str(payload.get("document_kind", ANNUAL_REPORT_DOCUMENT_KIND)),
        )


@dataclass(frozen=True, slots=True)
class ReportSection:
    """年报章节索引。

    Attributes:
        section_id: 章节编号，如 ``§3``。
        title: 章节标题行。
        start_offset: 章节在全文中的起始偏移。
        end_offset: 章节在全文中的结束偏移。
        matched_rule: 当前用于定位章节的规则来源。
        confidence: 当前章节定位结果的置信度。
    """

    section_id: str
    title: str
    start_offset: int
    end_offset: int
    matched_rule: str
    confidence: float

    def to_dict(self) -> dict[str, object]:
        """把章节索引序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "section_id": self.section_id,
            "title": self.title,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "matched_rule": self.matched_rule,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ReportSection":
        """从字典反序列化章节索引。

        Args:
            payload: JSON 兼容字典。

        Returns:
            反序列化后的章节索引对象。

        Raises:
            KeyError: 缺少必需字段时抛出。
            ValueError: 字段值无法转换时抛出。
        """

        return cls(
            section_id=str(payload["section_id"]),
            title=str(payload["title"]),
            start_offset=int(payload["start_offset"]),
            end_offset=int(payload["end_offset"]),
            matched_rule=str(payload["matched_rule"]),
            confidence=float(payload["confidence"]),
        )


@dataclass(frozen=True, slots=True)
class ParsedTable:
    """年报表格结构化结果。

    Attributes:
        page_number: 表格所在页码，从 1 开始。
        table_index: 同页内的表格序号，从 0 开始。
        headers: 表头元组。
        rows: 表格数据行。
    """

    page_number: int
    table_index: int
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def to_dict(self) -> dict[str, object]:
        """把表格对象序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "page_number": self.page_number,
            "table_index": self.table_index,
            "headers": list(self.headers),
            "rows": [list(row) for row in self.rows],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ParsedTable":
        """从字典反序列化表格对象。

        Args:
            payload: JSON 兼容字典。

        Returns:
            反序列化后的表格对象。

        Raises:
            KeyError: 缺少必需字段时抛出。
            ValueError: 字段值无法转换时抛出。
        """

        return cls(
            page_number=int(payload["page_number"]),
            table_index=int(payload["table_index"]),
            headers=tuple(str(value) for value in payload.get("headers", [])),
            rows=tuple(
                tuple(str(cell) for cell in row)
                for row in payload.get("rows", [])
            ),
        )


@dataclass(frozen=True, slots=True)
class ParsedAnnualReport:
    """统一年报读取结果。

    Attributes:
        key: 文档主键。
        raw_text: 全文文本。
        sections: 章节索引映射。
        tables: 结构化表格列表。
        metadata: 年报来源与缓存元数据。
    """

    key: DocumentKey
    raw_text: str
    sections: dict[str, ReportSection]
    tables: tuple[ParsedTable, ...]
    metadata: AnnualReportMetadata = field(default_factory=AnnualReportMetadata)

    def to_dict(self) -> dict[str, object]:
        """把已解析年报序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            可直接写入 JSON 的字典结构。

        Raises:
            无显式抛出。
        """

        return {
            "key": self.key.to_dict(),
            "raw_text": self.raw_text,
            "sections": {
                section_id: section.to_dict()
                for section_id, section in self.sections.items()
            },
            "tables": [table.to_dict() for table in self.tables],
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ParsedAnnualReport":
        """从字典反序列化已解析年报。

        Args:
            payload: JSON 兼容字典。

        Returns:
            反序列化后的年报对象。

        Raises:
            KeyError: 缺少必需字段时抛出。
            ValueError: 字段值无法转换时抛出。
        """

        raw_sections = payload.get("sections", {})
        raw_tables = payload.get("tables", [])
        return cls(
            key=DocumentKey.from_dict(dict(payload["key"])),
            raw_text=str(payload["raw_text"]),
            sections={
                str(section_id): ReportSection.from_dict(dict(section_payload))
                for section_id, section_payload in dict(raw_sections).items()
            },
            tables=tuple(
                ParsedTable.from_dict(dict(table_payload))
                for table_payload in raw_tables
            ),
            metadata=AnnualReportMetadata.from_dict(
                payload.get("metadata") if isinstance(payload, dict) else None
            ),
        )

    def get_section_text(self, section_id: str) -> str | None:
        """按章节编号返回正文片段。

        Args:
            section_id: 章节编号，如 ``§4``。

        Returns:
            命中时返回章节文本；未命中时返回 ``None``。

        Raises:
            无显式抛出；若对象状态被外部破坏，可能传播底层切片异常。
        """

        section = self.sections.get(section_id)
        if section is None:
            return None
        return self.raw_text[section.start_offset:section.end_offset].strip()
