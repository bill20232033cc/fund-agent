"""Application 层用例 facade。

这些 facade 是 UI 到 Service 的薄转发层，目标是关闭 UI 直接依赖 Service 的
边界债。这里不实现基金类型判断、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、
证据锚点或审计规则。
"""

from __future__ import annotations

from typing import Protocol

from fund_agent.services import (
    ExtractionScoreRequest,
    ExtractionScoreService,
    ExtractionSnapshotRequest,
    ExtractionSnapshotService,
    FundAnalysisRequest,
    FundAnalysisService,
    GoldenAnswerBuildRequest,
    GoldenAnswerService,
    GoldenPrefillRequest,
    GoldenPrefillService,
    QualityGateRequest,
    QualityGateService,
    ThermometerRequest,
    ThermometerService,
)


class _FundAnalysisService(Protocol):
    """基金分析 Service 协议。

    本协议只描述 Application 需要委托的 Service 方法，便于测试注入 fake。
    """

    async def analyze(self, request: FundAnalysisRequest):  # type: ignore[no-untyped-def]
        """执行完整分析。

        Args:
            request: 基金分析请求。

        Returns:
            Service 返回的完整分析结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

    async def checklist(self, request: FundAnalysisRequest):  # type: ignore[no-untyped-def]
        """执行独立买入前检查清单。

        Args:
            request: 基金分析请求。

        Returns:
            Service 返回的检查清单结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """


class _AsyncRunService(Protocol):
    """异步 run Service 协议。"""

    async def run(self, request):  # type: ignore[no-untyped-def]
        """执行异步 Service。

        Args:
            request: typed request。

        Returns:
            Service 返回值。

        Raises:
            Exception: 透传底层 Service 异常。
        """


class _SyncRunService(Protocol):
    """同步 run Service 协议。"""

    def run(self, request):  # type: ignore[no-untyped-def]
        """执行同步 Service。

        Args:
            request: typed request。

        Returns:
            Service 返回值。

        Raises:
            Exception: 透传底层 Service 异常。
        """


class _BuildService(Protocol):
    """同步 build Service 协议。"""

    def build(self, request):  # type: ignore[no-untyped-def]
        """执行构建型 Service。

        Args:
            request: typed request。

        Returns:
            Service 返回值。

        Raises:
            Exception: 透传底层 Service 异常。
        """


class FundAnalysisUseCase:
    """基金分析 Application 用例 facade。

    Args:
        service: 可注入的基金分析 Service；为空时使用默认生产 Service。
    """

    def __init__(self, service: _FundAnalysisService | None = None) -> None:
        """初始化基金分析用例。

        Args:
            service: 可注入的基金分析 Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or FundAnalysisService()

    async def analyze(self, request: FundAnalysisRequest):  # type: ignore[no-untyped-def]
        """执行完整基金分析。

        Args:
            request: 基金分析请求。

        Returns:
            完整基金分析结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return await self._service.analyze(request)

    async def checklist(self, request: FundAnalysisRequest):  # type: ignore[no-untyped-def]
        """执行独立买入前检查清单。

        Args:
            request: 基金分析请求。

        Returns:
            检查清单结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return await self._service.checklist(request)


class ThermometerUseCase:
    """温度计 Application 用例 facade。"""

    def __init__(self, service: _AsyncRunService | None = None) -> None:
        """初始化温度计用例。

        Args:
            service: 可注入的温度计 Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or ThermometerService()

    async def run(self, request: ThermometerRequest):  # type: ignore[no-untyped-def]
        """执行温度计查询。

        Args:
            request: 温度计请求。

        Returns:
            温度计读数或批量结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return await self._service.run(request)


class ExtractionSnapshotUseCase:
    """抽取快照 Application 用例 facade。"""

    def __init__(self, service: _AsyncRunService | None = None) -> None:
        """初始化抽取快照用例。

        Args:
            service: 可注入的抽取快照 Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or ExtractionSnapshotService()

    async def run(self, request: ExtractionSnapshotRequest):  # type: ignore[no-untyped-def]
        """执行抽取快照。

        Args:
            request: 抽取快照请求。

        Returns:
            抽取快照结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return await self._service.run(request)


class ExtractionScoreUseCase:
    """抽取评分 Application 用例 facade。"""

    def __init__(self, service: _SyncRunService | None = None) -> None:
        """初始化抽取评分用例。

        Args:
            service: 可注入的抽取评分 Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or ExtractionScoreService()

    def run(self, request: ExtractionScoreRequest):  # type: ignore[no-untyped-def]
        """执行抽取评分。

        Args:
            request: 抽取评分请求。

        Returns:
            抽取评分结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return self._service.run(request)


class GoldenPrefillUseCase:
    """Golden answer 预填 Application 用例 facade。"""

    def __init__(self, service: _AsyncRunService | None = None) -> None:
        """初始化 golden prefill 用例。

        Args:
            service: 可注入的 golden prefill Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or GoldenPrefillService()

    async def run(self, request: GoldenPrefillRequest):  # type: ignore[no-untyped-def]
        """执行 golden answer 预填。

        Args:
            request: golden prefill 请求。

        Returns:
            golden prefill 结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return await self._service.run(request)


class GoldenAnswerUseCase:
    """Golden answer 构建 Application 用例 facade。"""

    def __init__(self, service: _BuildService | None = None) -> None:
        """初始化 golden answer 构建用例。

        Args:
            service: 可注入的 golden answer Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or GoldenAnswerService()

    def build(self, request: GoldenAnswerBuildRequest):  # type: ignore[no-untyped-def]
        """执行 golden answer 构建。

        Args:
            request: golden answer build 请求。

        Returns:
            golden answer build 结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return self._service.build(request)


class QualityGateUseCase:
    """Quality gate Application 用例 facade。"""

    def __init__(self, service: _SyncRunService | None = None) -> None:
        """初始化 quality gate 用例。

        Args:
            service: 可注入的 quality gate Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service or QualityGateService()

    def run(self, request: QualityGateRequest):  # type: ignore[no-untyped-def]
        """执行 quality gate。

        Args:
            request: quality gate 请求。

        Returns:
            quality gate 结果。

        Raises:
            Exception: 透传底层 Service 异常。
        """

        return self._service.run(request)
