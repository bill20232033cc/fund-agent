"""golden answer 预填底稿 Service 编排层。

本模块属于 Service/Application 边界，负责把 UI 输入收敛为显式请求对象，
并委托 Capability 层 `fund_agent.fund.golden_prefill` 生成预填底稿。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fund_agent.fund.golden_prefill import GoldenPrefillResult, run_golden_prefill


@dataclass(frozen=True, slots=True)
class GoldenPrefillRequest:
    """golden answer 预填 Service 请求。

    Attributes:
        template_path: golden answer Markdown 模板路径。
        output_path: 预填底稿输出路径。
        report_year: 年报年份。
        force_refresh: 是否强制刷新统一文档仓库和净值缓存。
    """

    template_path: Path
    output_path: Path
    report_year: int
    force_refresh: bool


class GoldenPrefillService:
    """golden answer 预填用例编排 Service。"""

    async def run(self, request: GoldenPrefillRequest) -> GoldenPrefillResult:
        """执行 golden answer 预填。

        Args:
            request: 显式预填参数，不使用 `extra_payload`。

        Returns:
            Capability 返回的预填运行结果。

        Raises:
            ValueError: 当请求参数非法时抛出。
            Exception: 允许 Capability 层传播抽取或写文件异常。
        """

        _validate_request(request)
        return await run_golden_prefill(
            template_path=request.template_path,
            output_path=request.output_path,
            report_year=request.report_year,
            force_refresh=request.force_refresh,
        )


def _validate_request(request: GoldenPrefillRequest) -> None:
    """校验 golden prefill 请求的 Service 层显式输入。

    Args:
        request: 预填请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当模板路径、输出路径或年报年份非法时抛出。
    """

    if request.template_path.suffix != ".md":
        raise ValueError("template_path 必须指向 .md 文件")
    if request.output_path.suffix != ".md":
        raise ValueError("output_path 必须指向 .md 文件")
    if request.report_year <= 0:
        raise ValueError("report_year 必须为正整数")
