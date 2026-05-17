"""基金文档仓库内部缓存层。

P1-S3 只冻结 raw PDF 元信息与 parsed report 物化缓存，
不提前引入 `structured_data`。
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport

DOCUMENT_CACHE_ROOT: Final[Path] = Path("cache/documents")
PARSED_REPORT_CACHE_DIRNAME: Final[str] = "parsed_reports"
SQLITE_CACHE_FILENAME: Final[str] = "documents.sqlite3"
PARSED_REPORT_SCHEMA_VERSION: Final[int] = 1


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
        return await asyncio.to_thread(self._get_pdf_path_sync, key)

    def _get_pdf_path_sync(self, key: DocumentKey) -> Path | None:
        """同步读取缓存中的原始 PDF 路径。

        Args:
            key: 文档主键。

        Returns:
            命中且文件存在时返回 PDF 路径，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT pdf_path
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
        return pdf_path

    async def record_pdf_path(self, key: DocumentKey, pdf_path: Path) -> None:
        """写入原始 PDF 的缓存元信息。

        Args:
            key: 文档主键。
            pdf_path: 已缓存 PDF 的本地路径。

        Returns:
            无返回值。

        Raises:
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        await self.initialize()
        await asyncio.to_thread(self._record_pdf_path_sync, key, pdf_path)

    def _record_pdf_path_sync(self, key: DocumentKey, pdf_path: Path) -> None:
        """同步写入原始 PDF 的缓存元信息。

        Args:
            key: 文档主键。
            pdf_path: 已缓存 PDF 的本地路径。

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
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_key) DO UPDATE SET
                    pdf_path = excluded.pdf_path,
                    updated_at = excluded.updated_at
                """,
                (
                    _document_cache_key(key),
                    key.fund_code,
                    key.year,
                    key.document_kind,
                    str(pdf_path),
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
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        return ParsedAnnualReport.from_dict(payload)

    async def save_parsed_report(
        self,
        report: ParsedAnnualReport,
        *,
        pdf_path: Path | None = None,
    ) -> None:
        """物化已解析年报缓存。

        Args:
            report: 已解析年报对象。
            pdf_path: 原始 PDF 路径；提供时会一并刷新 documents 表。

        Returns:
            无返回值。

        Raises:
            OSError: 写入缓存文件失败时抛出。
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        await self.initialize()
        await asyncio.to_thread(self._save_parsed_report_sync, report, pdf_path)

    def _save_parsed_report_sync(
        self,
        report: ParsedAnnualReport,
        pdf_path: Path | None,
    ) -> None:
        """同步物化已解析年报缓存。

        Args:
            report: 已解析年报对象。
            pdf_path: 原始 PDF 路径；提供时会一并刷新 documents 表。

        Returns:
            无返回值。

        Raises:
            OSError: 写入缓存文件失败时抛出。
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        payload_path = self._parsed_report_payload_path(report.key)
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        payload_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
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
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(document_key) DO UPDATE SET
                        pdf_path = excluded.pdf_path,
                        updated_at = excluded.updated_at
                    """,
                    (
                        _document_cache_key(report.key),
                        report.key.fund_code,
                        report.key.year,
                        report.key.document_kind,
                        str(pdf_path),
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
                    _document_cache_key(report.key),
                    report.key.fund_code,
                    report.key.year,
                    report.key.document_kind,
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
