"""Extractor output 仓库化 Service 编排层。

本模块属于 Service 层，负责把 UI 输入收敛为显式请求对象，并委托
Agent 层 Fund 能力抽取和保存结构化输出。Service 不直接读取年报文件、
PDF/cache、parser 原始产物或底层来源 helper。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.extractor_output_repository import (
    ExtractorOutputRecord,
    ExtractorOutputRepository,
)


class ExtractorOutputExtractor(Protocol):
    """Extractor output Service 依赖的抽取协议。"""

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """抽取结构化基金数据包。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新底层仓库和净值缓存。

        Returns:
            结构化基金数据包。

        Raises:
            Exception: 允许具体 extractor 传播异常。
        """


class ExtractorOutputRepositoryProtocol(Protocol):
    """Extractor output Service 依赖的保存协议。"""

    def save(
        self,
        *,
        bundle: StructuredFundDataBundle,
        report_type: str = "annual_report",
    ) -> ExtractorOutputRecord:
        """保存结构化基金数据包。

        Args:
            bundle: 结构化基金数据包。
            report_type: 报告类型。

        Returns:
            保存后的记录。

        Raises:
            Exception: 允许具体 repository 传播校验或写入异常。
        """


RepositoryFactory = Callable[[Path | None], ExtractorOutputRepositoryProtocol]


@dataclass(frozen=True, slots=True)
class ExtractorOutputSaveRequest:
    """Extractor output 保存请求。

    Attributes:
        fund_code: 6 位基金代码。
        report_year: 年报年份。
        report_type: 报告类型；v1 仅支持 `annual_report`。
        output_root: 输出根目录；为空时使用 Fund 层默认 `reports/extractor-outputs`。
        force_refresh: 是否强制刷新底层仓库和净值缓存。
    """

    fund_code: str
    report_year: int
    report_type: str = "annual_report"
    output_root: Path | None = None
    force_refresh: bool = False


class ExtractorOutputService:
    """Extractor output 仓库化用例编排 Service。"""

    def __init__(
        self,
        extractor: ExtractorOutputExtractor | None = None,
        repository_factory: RepositoryFactory | None = None,
    ) -> None:
        """初始化 Service。

        Args:
            extractor: 可注入 extractor；未提供时使用 `FundDataExtractor`。
            repository_factory: 可注入 repository factory；未提供时使用
                `ExtractorOutputRepository`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._extractor = extractor or FundDataExtractor()
        self._repository_factory = repository_factory or _default_repository_factory

    async def save(self, request: ExtractorOutputSaveRequest) -> ExtractorOutputRecord:
        """抽取并保存结构化基金数据包。

        Args:
            request: 显式保存请求，不使用 `extra_payload`。

        Returns:
            保存后的 extractor output 记录。

        Raises:
            ValueError: 请求字段非法时抛出。
            Exception: 允许 extractor 或 repository 传播异常。
        """

        _validate_request(request)
        bundle = await self._extractor.extract(
            request.fund_code,
            request.report_year,
            force_refresh=request.force_refresh,
        )
        _validate_bundle_identity(request, bundle)
        repository = self._repository_factory(request.output_root)
        return repository.save(bundle=bundle, report_type=request.report_type)


def _default_repository_factory(root_dir: Path | None) -> ExtractorOutputRepository:
    """构造默认 extractor output repository。

    Args:
        root_dir: 输出根目录；为空时使用 repository 默认值。

    Returns:
        默认 repository。

    Raises:
        无显式抛出。
    """

    if root_dir is None:
        return ExtractorOutputRepository()
    return ExtractorOutputRepository(root_dir=root_dir)


def _validate_request(request: ExtractorOutputSaveRequest) -> None:
    """校验 extractor output 保存请求。

    Args:
        request: 保存请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 基金代码、年份或报告类型非法时抛出。
    """

    if len(request.fund_code) != 6 or not request.fund_code.isdigit():
        raise ValueError("fund_code 必须是 6 位数字")
    if request.report_year <= 0:
        raise ValueError("report_year 必须为正整数")
    if request.report_type != "annual_report":
        raise ValueError("report_type 当前仅支持 annual_report")


def _validate_bundle_identity(
    request: ExtractorOutputSaveRequest,
    bundle: StructuredFundDataBundle,
) -> None:
    """校验 extractor 返回 bundle 与请求身份一致。

    Args:
        request: 保存请求。
        bundle: extractor 返回的结构化数据包。

    Returns:
        无返回值。

    Raises:
        RuntimeError: bundle 基金代码或年份与请求不一致时抛出。
    """

    if bundle.fund_code != request.fund_code or bundle.report_year != request.report_year:
        raise RuntimeError(
            "Extractor output bundle identity mismatch: "
            f"requested {request.fund_code}/{request.report_year}, "
            f"extracted {bundle.fund_code}/{bundle.report_year}"
        )
