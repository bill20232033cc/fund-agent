"""基金文档仓库实现。

`FundDocumentRepository` 是 Capability 层对外唯一公开的文档读取入口。
当前仅支持年报，并复用 PDF 适配器完成下载与解析。
"""

from __future__ import annotations

from typing import Protocol

from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.models import ParsedAnnualReport


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


class FundDocumentRepository:
    """基金文档仓库。

    当前仓库只开放 `load_annual_report()`，用于把 PDF 下载与解析细节收口到
    Capability 层内部，为后续模板第 2 章和第 4 章的数据提取提供统一输入。
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
        return await self._annual_report_loader.load_annual_report(
            normalized_fund_code,
            normalized_year,
            force_refresh=force_refresh,
        )
