"""年报来源抽象与来源编排。

本模块属于 Agent 层基金能力文档仓库内部实现，用于把“从哪里取得年报 PDF”
从 PDF 解析适配器中拆出。外部调用方仍只能通过 `FundDocumentRepository`
读取年报，不应直接依赖这里的具体来源实现。
"""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, replace
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Awaitable, Callable, Final, Literal, Protocol

import httpx

from fund_agent.fund.documents.models import (
    AnnualReportSourceFailureCategory,
    AnnualReportSourceMetadata,
    AnnualReportSourceName,
)
from fund_agent.fund.pdf.downloader import DEFAULT_CACHE_DIR, _download_annual_report_pdf

AnnualReportDownloader = Callable[..., Awaitable[Path]]
EidClientFactory = Callable[..., AbstractAsyncContextManager[Any]]

EID_BASE_URL = "http://eid.csrc.gov.cn/fund"
EID_VALIDATE_FUND_PATH = "/fund/disclose/validate_fund.do"
EID_ADVANCED_SEARCH_REPORT_PATH = "/fund/disclose/advanced_search_report.do"
EID_PDF_PATH = "/fund/disclose/instance_show_pdf_id.do"
EID_ANNUAL_REPORT_TYPE = "FB010"
EID_ANNUAL_REPORT_CODE = "FB010010"
EID_ANNUAL_REPORT_DESP = "年度报告"
PDF_CONTENT_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF-"
_FALLBACK_ELIGIBLE_CATEGORIES: Final[frozenset[AnnualReportSourceFailureCategory]] = frozenset(
    {"not_found", "unavailable"}
)
EID_SELECTED_SOURCE: Final[Literal["eid"]] = "eid"
EID_SINGLE_SOURCE_MODE: Final[Literal["single_source_only"]] = "single_source_only"
EID_DISCOVERY_CONTRACT_VERSION: Final[str] = "eid_annual_report_discovery.v1"
_EID_DISPLAY_START = 0
_EID_DISPLAY_LENGTH = 20
_EID_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36"
    ),
}


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


class AnnualReportSourceIntegrityError(ValueError):
    """表示来源返回的 PDF 或文件内容未通过完整性校验。

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
    category: AnnualReportSourceFailureCategory
    message: str


class AnnualReportSourceFallbackBlockedError(Exception):
    """表示来源失败类别不允许 fallback，编排器主动阻断后续来源。

    Args:
        failures: 已记录的逐来源失败记录，包含阻断失败。
        blocking_failure: 触发阻断的失败记录。

    Returns:
        无返回值。

    Raises:
        ValueError: 失败记录为空或阻断失败不在失败记录中时抛出。
    """

    def __init__(
        self,
        failures: tuple[AnnualReportSourceFailure, ...],
        blocking_failure: AnnualReportSourceFailure,
    ) -> None:
        """初始化 fallback 阻断错误。

        Args:
            failures: 已记录的逐来源失败记录，包含阻断失败。
            blocking_failure: 触发阻断的失败记录。

        Returns:
            无返回值。

        Raises:
            ValueError: 失败记录为空或阻断失败不在失败记录末尾时抛出。
        """

        if not failures:
            raise ValueError("failures 不能为空")
        if failures[-1] != blocking_failure:
            raise ValueError("blocking_failure 必须是最后一条失败记录")
        self.failures = failures
        self.blocking_failure = blocking_failure
        super().__init__(_format_blocked_failure(failures, blocking_failure))


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
            AnnualReportSourceIntegrityError: PDF 内容完整性校验失败。
        """


@dataclass(frozen=True, slots=True)
class _EidValidatedFund:
    """EID 基金代码校验结果。"""

    fund_id: str


@dataclass(frozen=True, slots=True)
class _EidAnnualReportCandidate:
    """EID 年报候选记录。"""

    fund_code: str
    fund_id: str
    report_year: int
    report_desp: str
    report_code: str
    upload_info_id: str
    upload_info_detail_id: str
    table_name: str
    report_name: str | None = None
    report_send_date: str | None = None
    operation_upload_type: str | None = None
    corrections_num: int | None = None
    attach_file_name: str | None = None
    attach_file_path: str | None = None


class EidAnnualReportSource:
    """EID/证监会披露平台年报来源。

    该来源只负责模板第 1 章数据底座之前的年报 PDF 获取，不解析 PDF 内容。
    """

    name: AnnualReportSourceName = "eid"

    def __init__(
        self,
        *,
        base_url: str = EID_BASE_URL,
        cache_dir: Path | None = None,
        config: AnnualReportSourceConfig | None = None,
        client_factory: EidClientFactory | None = None,
    ) -> None:
        """初始化 EID 年报来源。

        Args:
            base_url: EID 平台基础 URL。
            cache_dir: PDF 缓存目录。
            config: 来源访问配置。
            client_factory: 测试用异步客户端工厂。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._base_url = base_url.rstrip("/")
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._config = config or AnnualReportSourceConfig()
        self._client_factory = client_factory or self._default_client_factory
        self._cache_locks: dict[str, asyncio.Lock] = {}

    def _default_client_factory(self) -> AbstractAsyncContextManager[Any]:
        """创建默认 HTTP 客户端。

        Args:
            无。

        Returns:
            支持异步上下文管理的 HTTP 客户端。

        Raises:
            无显式抛出。
        """

        return httpx.AsyncClient(follow_redirects=True, headers=_EID_HEADERS)

    async def fetch_annual_report_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportSourceResult:
        """从 EID 获取指定基金指定年份年报 PDF。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新 PDF 缓存。

        Returns:
            年报 PDF 路径和 EID 元数据。

        Raises:
            AnnualReportSourceUnavailableError: 来源临时不可用。
            AnnualReportSourceNotFoundError: EID 未找到指定年报。
            AnnualReportSourceMismatchError: EID 返回内容与请求矛盾。
            AnnualReportSourceSchemaError: EID 响应结构非法。
            AnnualReportSourceIntegrityError: PDF 内容完整性校验失败。
            OSError: 写入 PDF 缓存失败时抛出。
        """

        normalized_fund_code = _normalize_fund_code(fund_code)
        lock_key = f"{normalized_fund_code}:{year}"
        if lock_key not in self._cache_locks:
            self._cache_locks[lock_key] = asyncio.Lock()
        async with self._cache_locks[lock_key]:
            async with self._client_factory() as client:
                validated_fund = await self._validate_fund(client, normalized_fund_code)
                candidate = await self._search_annual_report(
                    client,
                    normalized_fund_code,
                    year,
                    validated_fund,
                )
                pdf_url = _build_eid_pdf_url(self._base_url, candidate.upload_info_id)
                metadata = _build_eid_metadata(pdf_url, candidate)
                pdf_path = self._build_pdf_cache_path(normalized_fund_code, year)
                if await asyncio.to_thread(pdf_path.exists) and not force_refresh:
                    if await asyncio.to_thread(_is_valid_cached_pdf, pdf_path):
                        return AnnualReportSourceResult(pdf_path=pdf_path, metadata=metadata)
                    await asyncio.to_thread(pdf_path.unlink, missing_ok=True)
                response = await _request_with_retries(
                    client,
                    "GET",
                    pdf_url,
                    timeout=self._config.pdf_timeout_seconds,
                    retry_attempts=self._config.retry_attempts,
                )
                _validate_pdf_response(response)
                await asyncio.to_thread(pdf_path.parent.mkdir, parents=True, exist_ok=True)
                await asyncio.to_thread(_write_pdf_bytes_atomic, pdf_path, response.content)
                return AnnualReportSourceResult(pdf_path=pdf_path, metadata=metadata)

    async def _validate_fund(self, client: Any, fund_code: str) -> _EidValidatedFund:
        """调用 EID 基金代码校验接口。

        Args:
            client: 异步 HTTP 客户端。
            fund_code: 规范化基金代码。

        Returns:
            基金代码校验结果。

        Raises:
            AnnualReportSourceUnavailableError: 网络或服务端瞬时错误。
            AnnualReportSourceNotFoundError: EID 明确表示基金不存在。
            AnnualReportSourceSchemaError: 响应结构非法。
        """

        response = await _request_with_retries(
            client,
            "POST",
            _join_eid_url(self._base_url, EID_VALIDATE_FUND_PATH),
            data={"cFundCode": fund_code},
            timeout=self._config.metadata_timeout_seconds,
            retry_attempts=self._config.retry_attempts,
        )
        return _parse_eid_validate_response(_response_json(response))

    async def _search_annual_report(
        self,
        client: Any,
        fund_code: str,
        year: int,
        validated_fund: _EidValidatedFund,
    ) -> _EidAnnualReportCandidate:
        """调用 EID 年报检索接口并选择唯一候选。

        Args:
            client: 异步 HTTP 客户端。
            fund_code: 规范化基金代码。
            year: 年报年份。
            validated_fund: 基金代码校验结果。

        Returns:
            唯一 EID 年报候选。

        Raises:
            AnnualReportSourceUnavailableError: 网络或服务端瞬时错误。
            AnnualReportSourceNotFoundError: EID 未找到候选。
            AnnualReportSourceMismatchError: 候选与请求矛盾。
            AnnualReportSourceSchemaError: 响应结构非法。
        """

        encoded_ao_data = _build_eid_ao_data(fund_code, year)
        response = await _request_with_retries(
            client,
            "GET",
            _join_eid_url(self._base_url, EID_ADVANCED_SEARCH_REPORT_PATH),
            params={"aoData": encoded_ao_data},
            timeout=self._config.metadata_timeout_seconds,
            retry_attempts=self._config.retry_attempts,
        )
        candidates = _parse_eid_search_response(_response_json(response))
        return _select_eid_annual_report_candidate(
            candidates,
            fund_code,
            year,
            validated_fund.fund_id,
        )

    def _build_pdf_cache_path(self, fund_code: str, year: int) -> Path:
        """构造 EID PDF 本地缓存路径。

        Args:
            fund_code: 规范化基金代码。
            year: 年报年份。

        Returns:
            EID PDF 缓存路径。

        Raises:
            无显式抛出。
        """

        return self._cache_dir / f"{fund_code}_{year}_annual_report_eid.pdf"


class EastmoneyAnnualReportSource:
    """Eastmoney/akshare 年报来源包装器。

    该类当前仅保留为 deferred future source candidate，不在 EID single-source
    生产默认路径中使用。不要在本 gate 中把它重新接入 production fallback。
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
            AnnualReportSourceUnavailableError: 来源临时不可用或缓存写入失败时抛出。
        """

        try:
            pdf_path = await self._downloader(
                fund_code,
                year,
                force_refresh=force_refresh,
            )
        except FileNotFoundError as exc:
            raise AnnualReportSourceNotFoundError(str(exc)) from exc
        except (httpx.HTTPError, OSError, ValueError) as exc:
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

    当前生产策略是 EID single-source only。编排器只接受一个来源；
    `not_found` / `unavailable` 在单源模式下是终态失败，不触发 fallback。
    """

    def __init__(
        self,
        sources: tuple[AnnualReportSource, ...] | None = None,
        *,
        config: AnnualReportSourceConfig | None = None,
    ) -> None:
        """初始化来源编排器。

        Args:
            sources: 按优先级排列的年报来源；未提供时使用 EID 主源与 Eastmoney fallback。
            config: 来源访问配置。

        Returns:
            无返回值。

        Raises:
            ValueError: 来源列表为空或包含多个来源时抛出。
        """

        self.config = config or AnnualReportSourceConfig()
        self.sources = (
            (EidAnnualReportSource(config=self.config),)
            if sources is None
            else sources
        )
        if not self.sources:
            raise ValueError("sources 不能为空")
        if len(self.sources) != 1:
            raise ValueError("EID single-source 模式只允许一个年报来源")

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
            AnnualReportSourceFallbackBlockedError: 来源失败类别不允许 fallback 时抛出。
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
                failure = _build_failure(source.name, "not_found", exc)
                failures.append(failure)
                if not _can_fallback_after_failure(failure.category):
                    _raise_fallback_blocked(tuple(failures), failure, exc)
                continue
            except AnnualReportSourceUnavailableError as exc:
                failure = _build_failure(source.name, "unavailable", exc)
                failures.append(failure)
                if not _can_fallback_after_failure(failure.category):
                    _raise_fallback_blocked(tuple(failures), failure, exc)
                continue
            except AnnualReportSourceMismatchError as exc:
                failure = _build_failure(source.name, "identity_mismatch", exc)
                failures.append(failure)
                _raise_fallback_blocked(tuple(failures), failure, exc)
            except AnnualReportSourceSchemaError as exc:
                failure = _build_failure(source.name, "schema_drift", exc)
                failures.append(failure)
                _raise_fallback_blocked(tuple(failures), failure, exc)
            except AnnualReportSourceIntegrityError as exc:
                failure = _build_failure(source.name, "integrity_error", exc)
                failures.append(failure)
                _raise_fallback_blocked(tuple(failures), failure, exc)
            if failures:
                return _mark_fallback_used(
                    result,
                    primary_failure_category=failures[0].category,
                )
            return result
        return _raise_exhausted_sources(tuple(failures))


def _build_failure(
    source: AnnualReportSourceName,
    category: AnnualReportSourceFailureCategory,
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


def _can_fallback_after_failure(category: AnnualReportSourceFailureCategory) -> bool:
    """判断指定失败类别是否允许尝试下一个来源。

    Args:
        category: 来源失败类别。

    Returns:
        类别允许 fallback 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return category in _FALLBACK_ELIGIBLE_CATEGORIES


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


def _format_blocked_failure(
    failures: tuple[AnnualReportSourceFailure, ...],
    blocking_failure: AnnualReportSourceFailure,
) -> str:
    """格式化 fallback 被阻断时的逐来源失败记录。

    Args:
        failures: 已记录的逐来源失败记录。
        blocking_failure: 触发阻断的失败记录。

    Returns:
        可读的阻断摘要。

    Raises:
        无显式抛出。
    """

    return (
        "年报来源 fallback 被阻断: "
        f"blocking={blocking_failure.source}:{blocking_failure.category}:"
        f"{blocking_failure.message}; "
        f"{_format_failures(failures)}"
    )


def _raise_fallback_blocked(
    failures: tuple[AnnualReportSourceFailure, ...],
    blocking_failure: AnnualReportSourceFailure,
    exc: Exception,
) -> None:
    """抛出 fallback 阻断错误并保留原始异常 cause。

    Args:
        failures: 已记录的逐来源失败记录。
        blocking_failure: 触发阻断的失败记录。
        exc: 原始来源异常。

    Returns:
        不返回。

    Raises:
        AnnualReportSourceFallbackBlockedError: 始终抛出。
    """

    raise AnnualReportSourceFallbackBlockedError(failures, blocking_failure) from exc


def _mark_fallback_used(
    result: AnnualReportSourceResult,
    *,
    primary_failure_category: AnnualReportSourceFailureCategory | None = None,
) -> AnnualReportSourceResult:
    """标记来源结果来自 fallback。

    Args:
        result: 原始来源结果。
        primary_failure_category: 触发 fallback 的主来源失败类别。

    Returns:
        标记 fallback 后的新结果。

    Raises:
        无显式抛出。
    """

    return replace(
        result,
        metadata=replace(
            result.metadata,
            fallback_used=True,
            primary_failure_category=primary_failure_category,
        ),
    )


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


def _normalize_fund_code(fund_code: str) -> str:
    """规范化基金代码。

    Args:
        fund_code: 原始基金代码。

    Returns:
        六位基金代码字符串。

    Raises:
        AnnualReportSourceMismatchError: 基金代码格式不符合六位数字时抛出。
    """

    normalized = str(fund_code).strip()
    if len(normalized) != 6 or not normalized.isdigit():
        raise AnnualReportSourceMismatchError(f"EID 基金代码非法: {fund_code!r}")
    return normalized


def _join_eid_url(base_url: str, path: str) -> str:
    """拼接 EID 接口 URL。

    Args:
        base_url: EID 基础 URL。
        path: 接口路径。

    Returns:
        完整接口 URL。

    Raises:
        无显式抛出。
    """

    normalized_base = base_url.rstrip("/")
    normalized_path = f"/{path.lstrip('/')}"
    if normalized_base.endswith("/fund") and normalized_path.startswith("/fund/"):
        normalized_base = normalized_base.removesuffix("/fund")
    return f"{normalized_base}{normalized_path}"


async def _request_with_retries(
    client: Any,
    method: Literal["GET", "POST"],
    url: str,
    *,
    timeout: float,
    retry_attempts: int,
    params: dict[str, str] | None = None,
    data: dict[str, str] | None = None,
) -> httpx.Response:
    """按请求级 timeout 执行 EID 请求并重试瞬时错误。

    Args:
        client: 异步 HTTP 客户端。
        method: HTTP 方法。
        url: 请求 URL。
        timeout: 本次请求使用的超时秒数。
        retry_attempts: 瞬时错误重试次数。
        params: GET 查询参数。
        data: POST 表单参数。

    Returns:
        HTTP 响应对象。

    Raises:
        AnnualReportSourceUnavailableError: 网络、超时或 5xx 错误耗尽重试后抛出。
    """

    attempts = max(1, retry_attempts)
    last_error: Exception | None = None
    for attempt_index in range(attempts):
        try:
            if method == "POST":
                response = await client.post(url, data=data, timeout=timeout)
            else:
                response = await client.get(url, params=params, timeout=timeout)
            if response.status_code >= 500:
                raise AnnualReportSourceUnavailableError(
                    f"EID 服务端错误 {response.status_code}: {url}"
                )
            if response.status_code != 200:
                raise AnnualReportSourceUnavailableError(
                    f"EID 请求失败 {response.status_code}: {url}"
                )
            return response
        except AnnualReportSourceUnavailableError as exc:
            last_error = exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_error = exc
        if attempt_index < attempts - 1:
            await asyncio.sleep(0)
    raise AnnualReportSourceUnavailableError(str(last_error)) from last_error


def _response_json(response: httpx.Response) -> dict[str, Any]:
    """解析 EID JSON 响应。

    Args:
        response: HTTP 响应对象。

    Returns:
        JSON 对象。

    Raises:
        AnnualReportSourceSchemaError: 响应不是 JSON 对象时抛出。
    """

    try:
        payload = response.json()
    except ValueError as exc:
        raise AnnualReportSourceSchemaError("EID 响应不是合法 JSON") from exc
    if not isinstance(payload, dict):
        raise AnnualReportSourceSchemaError("EID JSON 响应不是对象")
    return payload


def _parse_eid_validate_response(payload: dict[str, Any]) -> _EidValidatedFund:
    """解析 EID 基金代码校验响应。

    Args:
        payload: EID JSON 响应对象。

    Returns:
        基金代码校验结果。

    Raises:
        AnnualReportSourceNotFoundError: EID 明确表示基金不存在。
        AnnualReportSourceSchemaError: 响应缺少必需字段。
    """

    if payload.get("isSuccess") is not True:
        if payload.get("isSuccess") is False:
            raise AnnualReportSourceNotFoundError("EID 未找到基金代码")
        raise AnnualReportSourceSchemaError("EID validate_fund 缺少 isSuccess=true")
    fund_id = _optional_string(payload.get("fundId"))
    if fund_id is None:
        raise AnnualReportSourceSchemaError("EID validate_fund 缺少 fundId")
    return _EidValidatedFund(fund_id=fund_id)


def _build_eid_ao_data(fund_code: str, year: int) -> str:
    """构造 EID advanced_search_report.do 的 aoData 参数。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        JSON 字符串形式的 aoData。

    Raises:
        无显式抛出。
    """

    ao_data = [
        {"name": "iDisplayStart", "value": _EID_DISPLAY_START},
        {"name": "iDisplayLength", "value": _EID_DISPLAY_LENGTH},
        {"name": "fundType", "value": ""},
        {"name": "reportType", "value": EID_ANNUAL_REPORT_TYPE},
        {"name": "reportYear", "value": str(year)},
        {"name": "fundCompanyShortName", "value": ""},
        {"name": "fundCode", "value": fund_code},
        {"name": "fundShortName", "value": ""},
        {"name": "startUploadDate", "value": ""},
        {"name": "endUploadDate", "value": ""},
    ]
    return json.dumps(ao_data, ensure_ascii=False, separators=(",", ":"))


def _parse_eid_search_response(payload: dict[str, Any]) -> tuple[_EidAnnualReportCandidate, ...]:
    """解析 EID 年报检索响应。

    Args:
        payload: EID JSON 响应对象。

    Returns:
        年报候选元组。

    Raises:
        AnnualReportSourceUnavailableError: EID 明确返回服务不可用时抛出。
        AnnualReportSourceSchemaError: 响应结构非法时抛出。
    """

    if payload.get("success") is False:
        raise AnnualReportSourceUnavailableError("EID advanced_search_report 返回 success=false")
    raw_rows = payload.get("aaData")
    if not isinstance(raw_rows, list):
        raise AnnualReportSourceSchemaError("EID advanced_search_report 缺少 aaData 列表")
    return tuple(_parse_eid_candidate(row) for row in raw_rows)


def _parse_eid_candidate(payload: Any) -> _EidAnnualReportCandidate:
    """解析单条 EID 年报候选。

    Args:
        payload: 原始候选对象。

    Returns:
        结构化年报候选。

    Raises:
        AnnualReportSourceSchemaError: 必需字段缺失或类型非法时抛出。
    """

    if not isinstance(payload, dict):
        raise AnnualReportSourceSchemaError("EID 候选记录不是对象")
    report_year_raw = _required_string(payload, "reportYear")
    try:
        report_year = int(report_year_raw)
    except ValueError as exc:
        raise AnnualReportSourceSchemaError(
            f"EID 候选 reportYear 非法: {report_year_raw!r}"
        ) from exc
    return _EidAnnualReportCandidate(
        fund_code=_required_string(payload, "fundCode"),
        fund_id=_required_string(payload, "fundId"),
        report_year=report_year,
        report_desp=_required_string(payload, "reportDesp"),
        report_code=_required_string(payload, "reportCode"),
        upload_info_id=_required_string(payload, "uploadInfoId"),
        upload_info_detail_id=_required_string(payload, "uploadInfoDetailId"),
        table_name=_required_string(payload, "tableName"),
        report_name=_optional_string(payload.get("reportName")),
        report_send_date=_optional_string(payload.get("reportSendDate")),
        operation_upload_type=_optional_string(payload.get("operationUploadType")),
        corrections_num=_optional_int(payload.get("correctionsNum")),
        attach_file_name=_optional_string(payload.get("attachFileName")),
        attach_file_path=_optional_string(payload.get("attachFilePath")),
    )


def _select_eid_annual_report_candidate(
    candidates: tuple[_EidAnnualReportCandidate, ...],
    fund_code: str,
    year: int,
    fund_id: str,
) -> _EidAnnualReportCandidate:
    """按 fail-closed 规则选择唯一 EID 年报候选。

    Args:
        candidates: EID 年报候选。
        fund_code: 请求基金代码。
        year: 请求年报年份。
        fund_id: validate_fund.do 返回的基金 ID。

    Returns:
        唯一年报候选。

    Raises:
        AnnualReportSourceNotFoundError: 候选为空时抛出。
        AnnualReportSourceMismatchError: 候选与请求矛盾时抛出。
        AnnualReportSourceSchemaError: 多个有效候选或不支持附件链路时抛出。
    """

    if not candidates:
        raise AnnualReportSourceNotFoundError(f"EID 未找到 {fund_code} {year} 年年报")

    valid_candidates: list[_EidAnnualReportCandidate] = []
    mismatch_reasons: list[str] = []
    for candidate in candidates:
        # 逐字段收集矛盾原因，避免混入季度报或摘要时被误判成“未找到”。
        reason = _eid_candidate_mismatch_reason(candidate, fund_code, year, fund_id)
        if reason is None:
            valid_candidates.append(candidate)
        else:
            mismatch_reasons.append(reason)

    if len(valid_candidates) == 1:
        return valid_candidates[0]
    if len(valid_candidates) > 1:
        raise AnnualReportSourceSchemaError("EID 命中多个年度 PDF 候选，拒绝静默选择")
    raise AnnualReportSourceMismatchError(
        "EID 候选与请求不匹配: " + "; ".join(mismatch_reasons)
    )


def _eid_candidate_mismatch_reason(
    candidate: _EidAnnualReportCandidate,
    fund_code: str,
    year: int,
    fund_id: str,
) -> str | None:
    """返回候选不匹配原因，匹配时返回空值。

    Args:
        candidate: EID 年报候选。
        fund_code: 请求基金代码。
        year: 请求年报年份。
        fund_id: validate_fund.do 返回的基金 ID。

    Returns:
        不匹配原因；匹配时返回 ``None``。

    Raises:
        AnnualReportSourceSchemaError: 候选使用 P7-S3 不支持的附件链路时抛出。
    """

    if candidate.fund_code != fund_code:
        return f"fundCode={candidate.fund_code!r}"
    if candidate.fund_id != fund_id:
        return f"fundId={candidate.fund_id!r}"
    if candidate.report_year != year:
        return f"reportYear={candidate.report_year!r}"
    if candidate.report_code != EID_ANNUAL_REPORT_CODE:
        return f"reportCode={candidate.report_code!r}"
    if candidate.report_desp != EID_ANNUAL_REPORT_DESP:
        return f"reportDesp={candidate.report_desp!r}"
    if candidate.table_name != "PDF":
        return f"tableName={candidate.table_name!r}"
    if candidate.report_name and "摘要" in candidate.report_name:
        return f"reportName={candidate.report_name!r}"
    if candidate.attach_file_name or candidate.attach_file_path:
        raise AnnualReportSourceSchemaError("EID 候选包含 P7-S3 不支持的附件链路")
    return None


def _build_eid_pdf_url(base_url: str, upload_info_id: str) -> str:
    """构造 EID PDF 查看 URL。

    Args:
        base_url: EID 基础 URL。
        upload_info_id: EID 公告实例 ID。

    Returns:
        PDF URL。

    Raises:
        无显式抛出。
    """

    return f"{_join_eid_url(base_url, EID_PDF_PATH)}?instanceid={upload_info_id}"


def _validate_pdf_response(response: httpx.Response) -> None:
    """校验 EID PDF 响应确为 PDF。

    Args:
        response: HTTP 响应对象。

    Returns:
        无返回值。

    Raises:
        AnnualReportSourceIntegrityError: 响应不是 PDF 时抛出。
    """

    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower().strip()
    if content_type != PDF_CONTENT_TYPE:
        raise AnnualReportSourceIntegrityError(f"EID PDF Content-Type 非法: {content_type!r}")
    if not response.content.startswith(PDF_MAGIC_BYTES):
        raise AnnualReportSourceIntegrityError("EID PDF 响应缺少 %PDF- 文件头")


def _is_valid_cached_pdf(path: Path) -> bool:
    """检查本地缓存 PDF 是否满足最小完整性要求。

    Args:
        path: PDF 缓存路径。

    Returns:
        文件存在、非空且以 PDF 文件头开头时返回 ``True``。

    Raises:
        无显式抛出；读取失败会被视为无效缓存。
    """

    try:
        if path.stat().st_size < len(PDF_MAGIC_BYTES):
            return False
        with path.open("rb") as file_obj:
            return file_obj.read(len(PDF_MAGIC_BYTES)) == PDF_MAGIC_BYTES
    except OSError:
        return False


def _write_pdf_bytes_atomic(dest_path: Path, content: bytes) -> None:
    """以临时文件加原子替换方式写入 PDF 缓存。

    Args:
        dest_path: 最终 PDF 路径。
        content: 已校验的 PDF 内容。

    Returns:
        无返回值。

    Raises:
        OSError: 写入或替换失败时抛出。
        AnnualReportSourceIntegrityError: 内容缺少 PDF 文件头时抛出。
    """

    if not content.startswith(PDF_MAGIC_BYTES):
        raise AnnualReportSourceIntegrityError("PDF 内容缺少 %PDF- 文件头")
    temp_path: Path | None = None
    try:
        with NamedTemporaryFile(
            "wb",
            dir=dest_path.parent,
            prefix=f".{dest_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, dest_path)
    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise


def _build_eid_metadata(
    source_url: str,
    candidate: _EidAnnualReportCandidate,
) -> AnnualReportSourceMetadata:
    """构造 EID 来源元数据。

    Args:
        source_url: EID PDF URL。
        candidate: EID 年报候选。

    Returns:
        来源元数据。

    Raises:
        无显式抛出。
    """

    return AnnualReportSourceMetadata(
        source="eid",
        source_url=source_url,
        fund_code=candidate.fund_code,
        fund_id=candidate.fund_id,
        report_year=candidate.report_year,
        report_code=candidate.report_code,
        report_desp=candidate.report_desp,
        report_name=candidate.report_name,
        upload_info_id=candidate.upload_info_id,
        upload_info_detail_id=candidate.upload_info_detail_id,
        table_name=candidate.table_name,
        report_send_date=candidate.report_send_date,
        operation_upload_type=candidate.operation_upload_type,
        corrections_num=candidate.corrections_num,
        selected_source=EID_SELECTED_SOURCE,
        source_mode=EID_SINGLE_SOURCE_MODE,
        fallback_enabled=False,
        discovery_contract_version=EID_DISCOVERY_CONTRACT_VERSION,
    )


def _required_string(payload: dict[str, Any], key: str) -> str:
    """读取必需字符串字段。

    Args:
        payload: 原始字段映射。
        key: 字段名。

    Returns:
        非空字符串字段值。

    Raises:
        AnnualReportSourceSchemaError: 字段缺失或为空时抛出。
    """

    value = _optional_string(payload.get(key))
    if value is None:
        raise AnnualReportSourceSchemaError(f"EID 候选缺少字段 {key}")
    return value


def _optional_string(value: Any) -> str | None:
    """把可选 EID 字段规范化为字符串。

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
    """把可选 EID 字段规范化为整数。

    Args:
        value: 原始字段值。

    Returns:
        整数；空值返回 ``None``。

    Raises:
        AnnualReportSourceSchemaError: 非空字段无法转换为整数时抛出。
    """

    normalized = _optional_string(value)
    if normalized is None:
        return None
    try:
        return int(normalized)
    except ValueError as exc:
        raise AnnualReportSourceSchemaError(f"EID 整数字段非法: {value!r}") from exc
