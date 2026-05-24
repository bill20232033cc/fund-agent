"""精选基金池抽取快照 Service 编排层。

本模块属于 Service 层，负责把 UI 输入收敛为显式请求对象，
并委托 Agent 层基金能力 `fund_agent.fund.extraction_snapshot` 生成字段级快照。
UI 只能依赖本模块，不直接依赖 Agent 内部实现。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fund_agent.fund.extraction_snapshot import SnapshotRunResult, run_extraction_snapshot


@dataclass(frozen=True, slots=True)
class ExtractionSnapshotRequest:
    """精选基金池抽取快照 Service 请求。

    Attributes:
        fund_code: 指定单只基金代码；为空时按类别抽样。
        report_year: 年报年份。
        source_csv: 精选基金池 CSV 路径。
        run_id: 本次运行 ID。
        output_dir: 显式输出目录；为空时使用 Agent 层基金能力默认输出根目录。
        force_refresh: 是否强制刷新统一仓库和净值缓存。
        sample_per_category: 未指定基金代码时每个类别抽样数量。
        limit: 最大抽取数量。
    """

    fund_code: str | None
    report_year: int
    source_csv: Path
    run_id: str
    output_dir: Path | None
    force_refresh: bool
    sample_per_category: int = 1
    limit: int | None = None


class ExtractionSnapshotService:
    """精选基金池抽取快照用例编排 Service。

    Service 只负责请求编排与边界隔离；字段级抽取、CSV 校验和文件输出
    仍由 Agent 层基金能力实现。
    """

    async def run(self, request: ExtractionSnapshotRequest) -> SnapshotRunResult:
        """执行字段级抽取快照。

        Args:
            request: 显式快照参数，不使用 `extra_payload`。

        Returns:
            Agent 层基金能力返回的快照运行结果。

        Raises:
            ValueError: 当请求或 CSV 输入非法时抛出。
            Exception: 允许 Agent 层基金能力传播抽取或写文件异常。
        """

        _validate_request(request)
        return await run_extraction_snapshot(
            fund_code=request.fund_code,
            report_year=request.report_year,
            source_csv=request.source_csv,
            run_id=request.run_id,
            output_dir=request.output_dir,
            force_refresh=request.force_refresh,
            sample_per_category=request.sample_per_category,
            limit=request.limit,
        )


def _validate_request(request: ExtractionSnapshotRequest) -> None:
    """校验快照请求的 Service 层显式输入。

    Args:
        request: 快照请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当基金代码、年报年份、run_id 或抽样参数非法时抛出。
    """

    if request.fund_code is not None and (len(request.fund_code) != 6 or not request.fund_code.isdigit()):
        raise ValueError("fund_code 必须是 6 位数字")
    if request.report_year <= 0:
        raise ValueError("report_year 必须为正整数")
    if not request.run_id.strip():
        raise ValueError("run_id 不能为空")
    if request.sample_per_category < 0:
        raise ValueError("sample_per_category 不能为负数")
    if request.limit is not None and request.limit < 0:
        raise ValueError("limit 不能为负数")
