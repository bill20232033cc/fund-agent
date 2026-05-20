"""基金文档仓库内部缓存层。

P1-S3 只冻结 raw PDF 元信息与 parsed report 物化缓存，
不提前引入 `structured_data`。
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from fund_agent.fund.documents.models import AnnualReportSourceMetadata, DocumentKey, ParsedAnnualReport

DOCUMENT_CACHE_ROOT: Final[Path] = Path("cache/documents")
PARSED_REPORT_CACHE_DIRNAME: Final[str] = "parsed_reports"
SQLITE_CACHE_FILENAME: Final[str] = "documents.sqlite3"
PARSED_REPORT_SCHEMA_VERSION: Final[int] = 1
MIN_PARSED_REPORT_RAW_TEXT_LENGTH: Final[int] = 1_000
REQUIRED_PARSED_REPORT_SECTION_IDS: Final[frozenset[str]] = frozenset(
    {"§2", "§3", "§4", "§8", "§9", "§10"}
)


@dataclass(frozen=True, slots=True)
class AnnualReportPdfCacheEntry:
    """原始 PDF 缓存条目。

    Attributes:
        pdf_path: 原始 PDF 本地路径。
        source_metadata: 年报来源元数据。
        updated_at: 缓存更新时间。
    """

    pdf_path: Path
    source_metadata: AnnualReportSourceMetadata | None
    updated_at: str


def _document_cache_key(key: DocumentKey) -> str:
    """构造 SQLite 使用的稳定文档键。

    Args:
        key: 文档主键。

    Returns:
        用于 SQLite 主键的稳定字符串。

    Raises:
        无显式抛出。
    """

    return f"{key.document_kind}:{key.fund_code}:{key.year}"


def _utc_timestamp() -> str:
    """生成 UTC 时间戳字符串。

    Args:
        无。

    Returns:
        ISO 8601 UTC 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()


def is_parsed_annual_report_cache_usable(report: ParsedAnnualReport) -> bool:
    """判断 parsed report 缓存是否达到真实年报的最低质量门槛。

    Args:
        report: 从缓存反序列化或刚解析得到的年报对象。

    Returns:
        缓存足以支撑模板第 1-7 章核心抽取时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    if len(report.raw_text.strip()) < MIN_PARSED_REPORT_RAW_TEXT_LENGTH:
        return False
    return REQUIRED_PARSED_REPORT_SECTION_IDS <= set(report.sections)


def _source_metadata_to_json(metadata: AnnualReportSourceMetadata | None) -> str | None:
    """把来源元数据序列化为 SQLite JSON 字符串。

    Args:
        metadata: 来源元数据。

    Returns:
        JSON 字符串；无元数据时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if metadata is None:
        return None
    return json.dumps(metadata.to_dict(), ensure_ascii=False, separators=(",", ":"))


def _source_metadata_from_json(payload: object) -> AnnualReportSourceMetadata | None:
    """从 SQLite JSON 字符串反序列化来源元数据。

    Args:
        payload: SQLite 字段值。

    Returns:
        来源元数据；空值返回 ``None``。

    Raises:
        无显式抛出；缓存中的非法来源元数据会降级为空元数据。
    """

    if payload is None:
        return None
    try:
        parsed = json.loads(str(payload))
    except (TypeError, ValueError):
        return None
    if not isinstance(parsed, dict):
        return None
    try:
        return AnnualReportSourceMetadata.from_dict(parsed)
    except ValueError:
        return None


def _normalize_report_source_metadata(
    report: ParsedAnnualReport,
    source_metadata: AnnualReportSourceMetadata | None,
) -> ParsedAnnualReport:
    """对齐 parsed payload 与 documents row 的来源元数据。

    Args:
        report: 原始 parsed report。
        source_metadata: 应写入 documents row 的来源元数据。

    Returns:
        来源元数据已对齐的 parsed report。

    Raises:
        无显式抛出。
    """

    return replace(
        report,
        metadata=replace(report.metadata, source=source_metadata),
    )


class AnnualReportDocumentCache:
    """年报文档缓存。

    该缓存位于 `documents` 层内部：
    - 原始 PDF 继续使用文件缓存
    - documents SQLite 只记录 PDF 元信息
    - parsed_reports SQLite + JSON 文件负责已解析年报物化
    """

    def __init__(self, root_dir: Path | None = None) -> None:
        """初始化缓存实例。

        Args:
            root_dir: 缓存根目录；未提供时使用默认 `cache/documents`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.root_dir = root_dir or DOCUMENT_CACHE_ROOT
        self.parsed_reports_dir = self.root_dir / PARSED_REPORT_CACHE_DIRNAME
        self.sqlite_path = self.root_dir / SQLITE_CACHE_FILENAME
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化缓存目录与 SQLite schema。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            OSError: 创建目录失败时抛出。
            sqlite3.Error: 初始化 SQLite 失败时抛出。
        """

        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        """同步初始化缓存目录与 SQLite schema。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            OSError: 创建目录失败时抛出。
            sqlite3.Error: 初始化 SQLite 失败时抛出。
        """

        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_reports_dir.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.sqlite_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_key TEXT PRIMARY KEY,
                    fund_code TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    document_kind TEXT NOT NULL,
                    pdf_path TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._ensure_documents_source_metadata_column(connection)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS parsed_reports (
                    document_key TEXT PRIMARY KEY,
                    fund_code TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    document_kind TEXT NOT NULL,
                    payload_path TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def _ensure_documents_source_metadata_column(self, connection: sqlite3.Connection) -> None:
        """确保 documents 表存在来源元数据 JSON 列。

        Args:
            connection: SQLite 连接。

        Returns:
            无返回值。

        Raises:
            sqlite3.Error: 查询或修改 schema 失败时抛出。
        """

        columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(documents)").fetchall()
        }
        if "source_metadata_json" not in columns:
            connection.execute("ALTER TABLE documents ADD COLUMN source_metadata_json TEXT")

    async def get_pdf_path(self, key: DocumentKey) -> Path | None:
        """读取缓存中的原始 PDF 路径。

        Args:
            key: 文档主键。

        Returns:
            命中且文件存在时返回 PDF 路径，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        await self.initialize()
        entry = await asyncio.to_thread(self._get_pdf_entry_sync, key)
        return entry.pdf_path if entry is not None else None

    async def get_pdf_entry(self, key: DocumentKey) -> AnnualReportPdfCacheEntry | None:
        """读取缓存中的原始 PDF 条目。

        Args:
            key: 文档主键。

        Returns:
            命中且文件存在时返回 PDF 缓存条目，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        await self.initialize()
        return await asyncio.to_thread(self._get_pdf_entry_sync, key)

    def _get_pdf_path_sync(self, key: DocumentKey) -> Path | None:
        """同步读取缓存中的原始 PDF 路径。

        Args:
            key: 文档主键。

        Returns:
            命中且文件存在时返回 PDF 路径，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        entry = self._get_pdf_entry_sync(key)
        return entry.pdf_path if entry is not None else None

    def _get_pdf_entry_sync(self, key: DocumentKey) -> AnnualReportPdfCacheEntry | None:
        """同步读取缓存中的原始 PDF 条目。

        Args:
            key: 文档主键。

        Returns:
            命中且文件存在时返回 PDF 缓存条目，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
            self._ensure_documents_source_metadata_column(connection)
            row = connection.execute(
                """
                SELECT pdf_path, source_metadata_json, updated_at
                FROM documents
                WHERE document_key = ?
                """,
                (_document_cache_key(key),),
            ).fetchone()
        if row is None:
            return None
        pdf_path = Path(str(row[0]))
        if not pdf_path.exists():
            return None
        return AnnualReportPdfCacheEntry(
            pdf_path=pdf_path,
            source_metadata=_source_metadata_from_json(row[1]),
            updated_at=str(row[2]),
        )

    async def record_pdf_path(
        self,
        key: DocumentKey,
        pdf_path: Path,
        *,
        source_metadata: AnnualReportSourceMetadata | None = None,
    ) -> None:
        """写入原始 PDF 的缓存元信息。

        Args:
            key: 文档主键。
            pdf_path: 已缓存 PDF 的本地路径。
            source_metadata: 年报来源元数据。

        Returns:
            无返回值。

        Raises:
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        await self.initialize()
        await asyncio.to_thread(self._record_pdf_path_sync, key, pdf_path, source_metadata)

    def _record_pdf_path_sync(
        self,
        key: DocumentKey,
        pdf_path: Path,
        source_metadata: AnnualReportSourceMetadata | None,
    ) -> None:
        """同步写入原始 PDF 的缓存元信息。

        Args:
            key: 文档主键。
            pdf_path: 已缓存 PDF 的本地路径。
            source_metadata: 年报来源元数据。

        Returns:
            无返回值。

        Raises:
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
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
                ON CONFLICT(document_key) DO UPDATE SET
                    pdf_path = excluded.pdf_path,
                    source_metadata_json = excluded.source_metadata_json,
                    updated_at = excluded.updated_at
                """,
                (
                    _document_cache_key(key),
                    key.fund_code,
                    key.year,
                    key.document_kind,
                    str(pdf_path),
                    _source_metadata_to_json(source_metadata),
                    _utc_timestamp(),
                ),
            )
            connection.commit()

    async def load_parsed_report(self, key: DocumentKey) -> ParsedAnnualReport | None:
        """读取已解析年报缓存。

        Args:
            key: 文档主键。

        Returns:
            命中时返回 `ParsedAnnualReport`，否则返回 `None`。

        Raises:
            OSError: 读取缓存文件失败时抛出。
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        await self.initialize()
        async with self._lock:
            return await asyncio.to_thread(self._load_parsed_report_sync, key)

    def _load_parsed_report_sync(self, key: DocumentKey) -> ParsedAnnualReport | None:
        """同步读取已解析年报缓存。

        Args:
            key: 文档主键。

        Returns:
            命中时返回 `ParsedAnnualReport`，否则返回 `None`。

        Raises:
            OSError: 读取缓存文件失败时抛出。
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT payload_path, schema_version
                FROM parsed_reports
                WHERE document_key = ?
                """,
                (_document_cache_key(key),),
            ).fetchone()
        if row is None:
            return None
        payload_path = Path(str(row[0]))
        schema_version = int(row[1])
        if schema_version != PARSED_REPORT_SCHEMA_VERSION:
            return None
        if not payload_path.exists():
            return None
        try:
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return None
            report = ParsedAnnualReport.from_dict(payload)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return None
        if not is_parsed_annual_report_cache_usable(report):
            return None
        return report

    async def save_parsed_report(
        self,
        report: ParsedAnnualReport,
        *,
        pdf_path: Path | None = None,
        source_metadata: AnnualReportSourceMetadata | None = None,
    ) -> None:
        """物化已解析年报缓存。

        Args:
            report: 已解析年报对象。
            pdf_path: 原始 PDF 路径；提供时会一并刷新 documents 表。
            source_metadata: 显式来源元数据，优先于 report.metadata.source。

        Returns:
            无返回值。

        Raises:
            OSError: 写入缓存文件失败时抛出。
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        await self.initialize()
        async with self._lock:
            await asyncio.to_thread(
                self._save_parsed_report_sync,
                report,
                pdf_path,
                source_metadata,
            )

    def _save_parsed_report_sync(
        self,
        report: ParsedAnnualReport,
        pdf_path: Path | None,
        source_metadata: AnnualReportSourceMetadata | None,
    ) -> None:
        """同步物化已解析年报缓存。

        Args:
            report: 已解析年报对象。
            pdf_path: 原始 PDF 路径；提供时会一并刷新 documents 表。
            source_metadata: 显式来源元数据，优先于 report.metadata.source。

        Returns:
            无返回值。

        Raises:
            OSError: 写入缓存文件失败时抛出。
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        effective_source_metadata = source_metadata or report.metadata.source
        normalized_report = _normalize_report_source_metadata(report, effective_source_metadata)
        payload_path = self._parsed_report_payload_path(normalized_report.key)
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        payload_path.write_text(
            json.dumps(normalized_report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        with sqlite3.connect(self.sqlite_path) as connection:
            if pdf_path is not None:
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
                    ON CONFLICT(document_key) DO UPDATE SET
                        pdf_path = excluded.pdf_path,
                        source_metadata_json = excluded.source_metadata_json,
                        updated_at = excluded.updated_at
                    """,
                    (
                        _document_cache_key(normalized_report.key),
                        normalized_report.key.fund_code,
                        normalized_report.key.year,
                        normalized_report.key.document_kind,
                        str(pdf_path),
                        _source_metadata_to_json(effective_source_metadata),
                        _utc_timestamp(),
                    ),
                )
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
                ON CONFLICT(document_key) DO UPDATE SET
                    payload_path = excluded.payload_path,
                    schema_version = excluded.schema_version,
                    updated_at = excluded.updated_at
                """,
                (
                    _document_cache_key(normalized_report.key),
                    normalized_report.key.fund_code,
                    normalized_report.key.year,
                    normalized_report.key.document_kind,
                    str(payload_path),
                    PARSED_REPORT_SCHEMA_VERSION,
                    _utc_timestamp(),
                ),
            )
            connection.commit()

    def _parsed_report_payload_path(self, key: DocumentKey) -> Path:
        """计算已解析年报缓存文件路径。

        Args:
            key: 文档主键。

        Returns:
            对应 JSON 物化文件路径。

        Raises:
            无显式抛出。
        """

        return self.parsed_reports_dir / f"{key.fund_code}_{key.year}_{key.document_kind}.json"
