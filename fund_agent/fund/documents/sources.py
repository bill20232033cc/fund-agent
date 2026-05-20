"""年报来源抽象与来源编排。

本模块属于 Fund Capability 文档仓库内部实现，用于把“从哪里取得年报 PDF”
从 PDF 解析适配器中拆出。外部调用方仍只能通过 `FundDocumentRepository`
读取年报，不应直接依赖这里的具体来源实现。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Awaitable, Callable, Literal, Protocol

import httpx

from fund_agent.fund.pdf.downloader import _download_annual_report_pdf

AnnualReportSourceName = Literal["eid", "eastmoney"]
AnnualReportDownloader = Callable[..., Awaitable[Path]]


class AnnualReportSourceUnavailableError(Exception):
    """表示年报来源临时不可用。

    Args:
        message: 错误说明。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """


class AnnualReportSourceNotFoundError(FileNotFoundError):
    """表示年报来源未找到目标基金指定年份年报。

    Args:
        message: 错误说明。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """


class AnnualReportSourceMismatchError(ValueError):
    """表示来源返回了与请求基金、年份或报告类型矛盾的数据。

    Args:
        message: 错误说明。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """


class AnnualReportSourceSchemaError(ValueError):
    """表示来源响应结构缺少必需字段或无法解析。

    Args:
        message: 错误说明。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """


@dataclass(frozen=True, slots=True)
class AnnualReportSourceFailure:
    """单个年报来源失败记录。

    Attributes:
        source: 来源名称。
        category: 失败类别。
        message: 失败说明。
    """

    source: AnnualReportSourceName
    category: Literal["not_found", "unavailable"]
    message: str


class AnnualReportSourceAggregateError(Exception):
    """表示多个年报来源均未成功且需保留逐来源失败类别。

    Args:
        failures: 逐来源失败记录。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    def __init__(self, failures: tuple[AnnualReportSourceFailure, ...]) -> None:
        """初始化聚合错误。

        Args:
            failures: 逐来源失败记录。

        Returns:
            无返回值。

        Raises:
            ValueError: 失败记录为空时抛出。
        """

        if not failures:
            raise ValueError("failures 不能为空")
        self.failures = failures
        super().__init__(_format_failures(failures))


@dataclass(frozen=True, slots=True)
class AnnualReportSourceConfig:
    """年报来源访问配置。

    P7-S2 只定义配置边界；EID 客户端在 P7-S3 才会实际消费网络超时与重试。

    Attributes:
        metadata_timeout_seconds: 元数据请求超时秒数。
        pdf_timeout_seconds: PDF 下载请求超时秒数。
        retry_attempts: 瞬时错误重试次数。
        max_concurrency: 单个来源默认最大并发数。
    """

    metadata_timeout_seconds: float = 10.0
    pdf_timeout_seconds: float = 60.0
    retry_attempts: int = 2
    max_concurrency: int = 1


@dataclass(frozen=True, slots=True)
class AnnualReportSourceMetadata:
    """年报来源元数据。

    P7-S2 只在内部返回和测试该对象，暂不持久化到 parsed report 或 cache schema。

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
        fallback_used: 是否为 fallback 来源命中。
    """

    source: AnnualReportSourceName
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
    fallback_used: bool = False


@dataclass(frozen=True, slots=True)
class AnnualReportSourceResult:
    """年报来源返回结果。

    Attributes:
        pdf_path: 已缓存的本地 PDF 路径。
        metadata: 来源元数据。
    """

    pdf_path: Path
    metadata: AnnualReportSourceMetadata


class AnnualReportSource(Protocol):
    """年报 PDF 来源协议。

    该协议只服务于文档仓库内部，具体来源必须按显式基金代码和年份返回 PDF。
    """

    name: AnnualReportSourceName

    async def fetch_annual_report_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportSourceResult:
        """获取指定基金指定年份年报 PDF。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否绕过来源内部缓存重新获取。

        Returns:
            年报 PDF 路径和来源元数据。

        Raises:
            AnnualReportSourceUnavailableError: 来源临时不可用。
            AnnualReportSourceNotFoundError: 来源未找到指定年报。
            AnnualReportSourceMismatchError: 来源返回内容与请求矛盾。
            AnnualReportSourceSchemaError: 来源响应结构非法。
        """


class EastmoneyAnnualReportSource:
    """Eastmoney/akshare 年报来源包装器。

    该类保持当前生产默认行为，只把既有下载 helper 包装成统一来源协议。
    """

    name: AnnualReportSourceName = "eastmoney"

    def __init__(self, downloader: AnnualReportDownloader = _download_annual_report_pdf) -> None:
        """初始化 Eastmoney 来源。

        Args:
            downloader: 既有年报 PDF 下载 helper。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._downloader = downloader

    async def fetch_annual_report_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportSourceResult:
        """通过既有 Eastmoney/akshare helper 获取年报 PDF。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            年报 PDF 路径和 Eastmoney 来源元数据。

        Raises:
            AnnualReportSourceNotFoundError: 未找到对应年报时抛出。
            Exception: 其他下载异常保持原始异常类别向上抛出。
        """

        try:
            pdf_path = await self._downloader(
                fund_code,
                year,
                force_refresh=force_refresh,
            )
        except FileNotFoundError as exc:
            raise AnnualReportSourceNotFoundError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise AnnualReportSourceUnavailableError(str(exc)) from exc
        return AnnualReportSourceResult(
            pdf_path=pdf_path,
            metadata=AnnualReportSourceMetadata(
                source=self.name,
                fund_code=fund_code,
                report_year=year,
            ),
        )


class AnnualReportSourceOrchestrator:
    """年报来源编排器。

    编排器负责按顺序尝试来源，并按失败类别决定是否继续 fallback。
    """

    def __init__(
        self,
        sources: tuple[AnnualReportSource, ...] | None = None,
        *,
        config: AnnualReportSourceConfig | None = None,
    ) -> None:
        """初始化来源编排器。

        Args:
            sources: 按优先级排列的年报来源；未提供时使用当前生产默认 Eastmoney 来源。
            config: 来源访问配置。

        Returns:
            无返回值。

        Raises:
            ValueError: 来源列表为空时抛出。
        """

        self.sources = (EastmoneyAnnualReportSource(),) if sources is None else sources
        if not self.sources:
            raise ValueError("sources 不能为空")
        self.config = config or AnnualReportSourceConfig()

    async def fetch_annual_report_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportSourceResult:
        """按来源优先级获取指定年报 PDF。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层来源缓存。

        Returns:
            首个成功来源返回的年报 PDF 路径和元数据。

        Raises:
            AnnualReportSourceMismatchError: 来源返回矛盾内容时抛出。
            AnnualReportSourceSchemaError: 来源响应结构非法时抛出。
            AnnualReportSourceNotFoundError: 所有来源均为 not-found 时抛出。
            AnnualReportSourceUnavailableError: 单个来源不可用且无其他失败类别时抛出。
            AnnualReportSourceAggregateError: 混合失败或多个不可用失败需要保留类别时抛出。
        """

        failures: list[AnnualReportSourceFailure] = []
        for source in self.sources:
            try:
                result = await source.fetch_annual_report_pdf(
                    fund_code,
                    year,
                    force_refresh=force_refresh,
                )
            except AnnualReportSourceNotFoundError as exc:
                failures.append(_build_failure(source.name, "not_found", exc))
                continue
            except AnnualReportSourceUnavailableError as exc:
                failures.append(_build_failure(source.name, "unavailable", exc))
                continue
            except (AnnualReportSourceMismatchError, AnnualReportSourceSchemaError):
                raise
            if failures:
                return _mark_fallback_used(result)
            return result
        return _raise_exhausted_sources(tuple(failures))


def _build_failure(
    source: AnnualReportSourceName,
    category: Literal["not_found", "unavailable"],
    exc: Exception,
) -> AnnualReportSourceFailure:
    """构造来源失败记录。

    Args:
        source: 来源名称。
        category: 失败类别。
        exc: 原始异常。

    Returns:
        来源失败记录。

    Raises:
        无显式抛出。
    """

    return AnnualReportSourceFailure(source=source, category=category, message=str(exc))


def _format_failures(failures: tuple[AnnualReportSourceFailure, ...]) -> str:
    """格式化逐来源失败记录。

    Args:
        failures: 逐来源失败记录。

    Returns:
        可读的失败摘要。

    Raises:
        无显式抛出。
    """

    details = ", ".join(
        f"{failure.source}:{failure.category}:{failure.message}" for failure in failures
    )
    return f"所有年报来源均未成功: {details}"


def _mark_fallback_used(result: AnnualReportSourceResult) -> AnnualReportSourceResult:
    """标记来源结果来自 fallback。

    Args:
        result: 原始来源结果。

    Returns:
        标记 fallback 后的新结果。

    Raises:
        无显式抛出。
    """

    return replace(result, metadata=replace(result.metadata, fallback_used=True))


def _raise_exhausted_sources(
    failures: tuple[AnnualReportSourceFailure, ...],
) -> AnnualReportSourceResult:
    """根据耗尽后的失败类别抛出最终异常。

    Args:
        failures: 逐来源失败记录。

    Returns:
        不返回；返回类型仅用于调用点类型收窄。

    Raises:
        AnnualReportSourceNotFoundError: 所有来源均为 not-found 时抛出。
        AnnualReportSourceUnavailableError: 单一来源不可用时抛出。
        AnnualReportSourceAggregateError: 多来源不可用或混合失败时抛出。
    """

    if not failures:
        raise AnnualReportSourceNotFoundError("未配置可用年报来源")

    categories = {failure.category for failure in failures}
    message = _format_failures(failures)
    if categories == {"not_found"}:
        raise AnnualReportSourceNotFoundError(message)
    if categories == {"unavailable"} and len(failures) == 1:
        raise AnnualReportSourceUnavailableError(message)
    raise AnnualReportSourceAggregateError(failures)
