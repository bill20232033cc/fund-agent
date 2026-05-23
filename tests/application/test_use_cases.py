"""Application use-case facade 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.application import (
    FundAnalysisRequest,
    FundAnalysisUseCase,
    ThermometerRequest,
    ThermometerUseCase,
)


class _FakeFundAnalysisService:
    """Application 测试用基金分析 Service。"""

    last_checklist_request = None

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """返回收到的分析请求。

        Args:
            request: 基金分析请求。

        Returns:
            原样返回请求，便于断言委托边界。

        Raises:
            无显式抛出。
        """

        return request

    async def checklist(self, request):  # type: ignore[no-untyped-def]
        """记录并返回收到的检查清单请求。

        Args:
            request: 基金分析请求。

        Returns:
            原样返回请求，便于断言委托边界。

        Raises:
            无显式抛出。
        """

        type(self).last_checklist_request = request
        return request


class _FakeThermometerService:
    """Application 测试用温度计 Service。"""

    last_request = None

    async def run(self, request):  # type: ignore[no-untyped-def]
        """记录并返回收到的温度计请求。

        Args:
            request: 温度计请求。

        Returns:
            原样返回请求，便于断言委托边界。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return request


@pytest.mark.asyncio
async def test_fund_analysis_use_case_delegates_checklist_request_without_mutation(
    tmp_path: Path,
) -> None:
    """验证 Application 不改变 checklist typed request。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当请求字段被 Application 改写时抛出。
    """

    request = FundAnalysisRequest(
        fund_code="110011",
        report_year=2024,
        valuation_state="low",
        thermometer_cache_dir=tmp_path,
        force_refresh=True,
    )
    service = _FakeFundAnalysisService()
    use_case = FundAnalysisUseCase(service=service)

    result = await use_case.checklist(request)

    assert result is request
    assert service.last_checklist_request is request
    assert service.last_checklist_request.valuation_state == "low"
    assert service.last_checklist_request.force_refresh is True
    assert service.last_checklist_request.thermometer_cache_dir == tmp_path


@pytest.mark.asyncio
async def test_thermometer_use_case_delegates_request_without_mutation(tmp_path: Path) -> None:
    """验证温度计 Application 只做请求委托。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当请求字段被 Application 改写时抛出。
    """

    request = ThermometerRequest(
        cache_dir=tmp_path,
        force_refresh=True,
        index_code=None,
        index_codes=("wind_all_a", "000300"),
    )
    service = _FakeThermometerService()
    use_case = ThermometerUseCase(service=service)

    result = await use_case.run(request)

    assert result is request
    assert service.last_request is request
    assert service.last_request.cache_dir == tmp_path
    assert service.last_request.force_refresh is True
    assert service.last_request.index_codes == ("wind_all_a", "000300")
