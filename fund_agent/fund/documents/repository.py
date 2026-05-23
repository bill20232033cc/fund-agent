"""基金文档仓库实现。

`FundDocumentRepository` 是 Agent 层基金能力对外唯一公开的文档读取入口。
当前仅支持年报，并复用 PDF 适配器完成下载与解析。
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path
from typing import Protocol

from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.cache import AnnualReportDocumentCache, PARSED_REPORT_SCHEMA_VERSION
from fund_agent.fund.documents.models import (
    AnnualReportCacheProvenance,
    AnnualReportMetadata,
    AnnualReportPdfFetchResult,
    AnnualReportSourceMetadata,
    DocumentKey,
    ParsedAnnualReport,
)


class _AnnualReportLoader(Protocol):
    """年报加载器协议。

    该协议用于隔离文档仓库与具体 PDF 适配器实现。
    """

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """加载并解析年报。

        Args:
            fund_code: 基金代码。
            year: 报告年份。
            force_refresh: 是否强制跳过本地 PDF 缓存重新下载。

        Returns:
            解析后的年报对象。

        Raises:
            FileNotFoundError: 未找到对应年报时抛出。
            Exception: 允许具体适配器传播下载或解析异常。
        """


class _CacheAwareAnnualReportLoader(_AnnualReportLoader, Protocol):
    """支持仓库内缓存编排的年报加载器协议。"""

    async def fetch_pdf_path(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> Path:
        """确保原始 PDF 已缓存并返回其路径。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            本地 PDF 文件路径。

        Raises:
            FileNotFoundError: 未找到对应年报时抛出。
            Exception: 允许底层下载异常直接传播。
        """


class _MetadataAwareAnnualReportLoader(_CacheAwareAnnualReportLoader, Protocol):
    """支持显式 PDF 获取结果的年报加载器协议。"""

    async def fetch_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportPdfFetchResult:
        """确保原始 PDF 已缓存并返回路径与来源元数据。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            PDF 获取结果。

        Raises:
            FileNotFoundError: 未找到对应年报时抛出。
            Exception: 允许底层下载异常直接传播。
        """

    async def parse_pdf(
        self,
        pdf_path: Path,
        fund_code: str,
        year: int,
    ) -> ParsedAnnualReport:
        """基于本地 PDF 路径解析年报对象。

        Args:
            pdf_path: 本地 PDF 文件路径。
            fund_code: 基金代码。
            year: 年报年份。

        Returns:
            统一的年报解析对象。

        Raises:
            Exception: 允许底层文本提取、表格提取或章节定位异常直接传播。
        """


def _validate_fund_code(fund_code: str) -> str:
    """校验并标准化基金代码。

    Args:
        fund_code: 原始基金代码。

    Returns:
        去除首尾空白后的基金代码。

    Raises:
        ValueError: 基金代码为空。
    """

    normalized = fund_code.strip()
    if not normalized:
        raise ValueError("fund_code 不能为空")
    return normalized


def _validate_year(year: int) -> int:
    """校验年报年份。

    Args:
        year: 原始年份。

    Returns:
        校验后的年份。

    Raises:
        ValueError: 年份不是正整数。
    """

    if year <= 0:
        raise ValueError("year 必须为正整数")
    return year


def _create_default_cache() -> AnnualReportDocumentCache:
    """创建默认文档缓存实例。

    Args:
        无。

    Returns:
        默认文档缓存实例。

    Raises:
        无显式抛出。
    """

    return AnnualReportDocumentCache()


def _get_cache_aware_loader(
    annual_report_loader: _AnnualReportLoader,
) -> _CacheAwareAnnualReportLoader | None:
    """判断加载器是否支持仓库内缓存编排。

    Args:
        annual_report_loader: 年报加载器实例。

    Returns:
        支持缓存编排时返回对应协议视图，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    fetch_pdf_path = getattr(annual_report_loader, "fetch_pdf_path", None)
    parse_pdf = getattr(annual_report_loader, "parse_pdf", None)
    if not inspect.iscoroutinefunction(fetch_pdf_path):
        return None
    if not inspect.iscoroutinefunction(parse_pdf):
        return None
    return annual_report_loader


def _get_metadata_aware_loader(
    annual_report_loader: _AnnualReportLoader,
) -> _MetadataAwareAnnualReportLoader | None:
    """判断加载器是否支持显式来源元数据获取。

    Args:
        annual_report_loader: 年报加载器实例。

    Returns:
        支持显式 PDF 获取结果时返回对应协议视图，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    cache_aware_loader = _get_cache_aware_loader(annual_report_loader)
    if cache_aware_loader is None:
        return None
    fetch_pdf = getattr(annual_report_loader, "fetch_pdf", None)
    if not inspect.iscoroutinefunction(fetch_pdf):
        return None
    return annual_report_loader


def _with_annual_report_metadata(
    report: ParsedAnnualReport,
    *,
    source_metadata: AnnualReportSourceMetadata | None,
    pdf_path: Path | None,
    pdf_cache_hit: bool,
    parsed_cache_hit: bool,
) -> ParsedAnnualReport:
    """给 parsed report 附加来源与缓存元数据。

    Args:
        report: 原始 parsed report。
        source_metadata: 年报来源元数据。
        pdf_path: 原始 PDF 路径。
        pdf_cache_hit: 是否命中 PDF 路径缓存。
        parsed_cache_hit: 是否命中 parsed report 缓存。

    Returns:
        附加元数据后的 parsed report。

    Raises:
        无显式抛出。
    """

    return replace(
        report,
        metadata=AnnualReportMetadata(
            source=source_metadata,
            cache=AnnualReportCacheProvenance(
                pdf_path=str(pdf_path) if pdf_path is not None else None,
                pdf_cache_hit=pdf_cache_hit,
                parsed_cache_hit=parsed_cache_hit,
                source_metadata_present=source_metadata is not None,
                cache_schema_version=PARSED_REPORT_SCHEMA_VERSION,
            ),
        ),
    )


class FundDocumentRepository:
    """基金文档仓库。

    当前仓库只开放 `load_annual_report()`，用于把 PDF 下载与解析细节收口到
    Agent 层基金能力内部，为后续模板第 2 章和第 4 章的数据提取提供统一输入。
    """

    def __init__(self, annual_report_loader: _AnnualReportLoader | None = None) -> None:
        """初始化文档仓库。

        Args:
            annual_report_loader: 自定义年报加载器；未提供时使用默认 PDF 适配器。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._annual_report_loader = annual_report_loader or AnnualReportPdfAdapter()
        self._cache = _create_default_cache()

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """加载指定基金年报并返回统一解析结果。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            解析后的年报对象，不向上层暴露本地文件路径。

        Raises:
            ValueError: 输入参数非法时抛出。
            FileNotFoundError: 未找到对应年报时抛出。
        """

        normalized_fund_code = _validate_fund_code(fund_code)
        normalized_year = _validate_year(year)
        cache_aware_loader = _get_cache_aware_loader(self._annual_report_loader)
        if cache_aware_loader is None:
            return await self._annual_report_loader.load_annual_report(
                normalized_fund_code,
                normalized_year,
                force_refresh=force_refresh,
            )

        document_key = self._build_document_key(normalized_fund_code, normalized_year)
        if not force_refresh:
            cached_report = await self._cache.load_parsed_report(document_key)
            if cached_report is not None:
                return _with_annual_report_metadata(
                    cached_report,
                    source_metadata=cached_report.metadata.source,
                    pdf_path=Path(cached_report.metadata.cache.pdf_path)
                    if cached_report.metadata.cache.pdf_path
                    else None,
                    pdf_cache_hit=cached_report.metadata.cache.pdf_cache_hit,
                    parsed_cache_hit=True,
                )

        pdf_path = None
        source_metadata = None
        pdf_cache_hit = False
        if not force_refresh:
            pdf_entry = await self._cache.get_pdf_entry(document_key)
            if pdf_entry is not None:
                pdf_path = pdf_entry.pdf_path
                source_metadata = pdf_entry.source_metadata
                pdf_cache_hit = True
        if pdf_path is None:
            metadata_aware_loader = _get_metadata_aware_loader(self._annual_report_loader)
            if metadata_aware_loader is not None:
                fetch_result = await metadata_aware_loader.fetch_pdf(
                    normalized_fund_code,
                    normalized_year,
                    force_refresh=force_refresh,
                )
                pdf_path = fetch_result.pdf_path
                source_metadata = fetch_result.source_metadata
            else:
                pdf_path = await cache_aware_loader.fetch_pdf_path(
                    normalized_fund_code,
                    normalized_year,
                    force_refresh=force_refresh,
                )
                source_metadata = None
            await self._cache.record_pdf_path(
                document_key,
                pdf_path,
                source_metadata=source_metadata,
            )

        parsed_report = await cache_aware_loader.parse_pdf(
            pdf_path,
            normalized_fund_code,
            normalized_year,
        )
        parsed_report = _with_annual_report_metadata(
            parsed_report,
            source_metadata=source_metadata,
            pdf_path=pdf_path,
            pdf_cache_hit=pdf_cache_hit,
            parsed_cache_hit=False,
        )
        await self._cache.save_parsed_report(
            parsed_report,
            pdf_path=pdf_path,
            source_metadata=source_metadata,
        )
        return parsed_report

    def _build_document_key(self, fund_code: str, year: int) -> DocumentKey:
        """构造当前仓库使用的文档主键。

        Args:
            fund_code: 规范化后的基金代码。
            year: 规范化后的年报年份。

        Returns:
            当前请求对应的文档主键。

        Raises:
            无显式抛出。
        """

        return DocumentKey(fund_code=fund_code, year=year)
