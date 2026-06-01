"""Golden readiness preflight Service 编排层。

本模块属于 Service 层，只负责把 UI 或调用方传入的显式参数校验后转发给
Agent/Fund 层 `golden_readiness_preflight` 能力；不读取 prompt manifest，
不管理 Host session/run，也不接入 dayu runtime。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fund_agent.fund.golden_readiness_preflight import (
    FundArtifactInput,
    GoldenReadinessPreflightResult,
    run_golden_readiness_preflight,
)


@dataclass(frozen=True, slots=True)
class GoldenReadinessPreflightRequest:
    """Golden readiness preflight Service 请求。

    Attributes:
        source_csv: 精选基金池 CSV 路径。
        output_dir: 输出目录。
        run_id: 运行 ID。
        fund_artifacts: 单基金或 slot artifact 输入。
        golden_answer_path: strict golden answer JSON 路径。
        fixture_promotion_state_path: fixture promotion state JSON 路径。
        coverage_disposition_path: coverage disposition manifest JSON 路径。
        preflight_input_path: 完整 preflight input JSON 路径。
        selected_pool_path: selected pool JSON 路径。
    """

    source_csv: Path
    output_dir: Path
    run_id: str
    fund_artifacts: tuple[FundArtifactInput, ...] = ()
    golden_answer_path: Path | None = None
    fixture_promotion_state_path: Path | None = None
    coverage_disposition_path: Path | None = None
    preflight_input_path: Path | None = None
    selected_pool_path: Path | None = None


class GoldenReadinessPreflightService:
    """Golden readiness preflight 用例编排 Service。

    Service 只承担边界校验；readiness 聚合、静态 disposition manifest 和产物输出
    由 Agent 层 Fund 能力实现。
    """

    def run(self, request: GoldenReadinessPreflightRequest) -> GoldenReadinessPreflightResult:
        """执行 golden readiness preflight。

        Args:
            request: 显式 preflight 请求，不使用 `extra_payload`。

        Returns:
            Agent/Fund 层返回的 preflight 结果。

        Raises:
            ValueError: 请求参数互斥或路径后缀非法时抛出。
            Exception: 允许 Fund 层传播 JSON/JSONL 或写文件异常。
        """

        _validate_request(request)
        return run_golden_readiness_preflight(
            source_csv=request.source_csv,
            output_dir=request.output_dir,
            run_id=request.run_id,
            fund_artifacts=request.fund_artifacts,
            golden_answer_path=request.golden_answer_path,
            fixture_promotion_state_path=request.fixture_promotion_state_path,
            coverage_disposition_path=request.coverage_disposition_path,
            preflight_input_path=request.preflight_input_path,
            selected_pool_path=request.selected_pool_path,
        )


def _validate_request(request: GoldenReadinessPreflightRequest) -> None:
    """校验 Service 层显式请求。

    Args:
        request: preflight 请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 参数互斥、后缀非法或输出目录指向文件时抛出。
    """

    if request.preflight_input_path is not None:
        conflicts: list[str] = []
        if request.fund_artifacts:
            conflicts.append("fund_artifacts")
        if request.selected_pool_path is not None:
            conflicts.append("selected_pool_path")
        if request.coverage_disposition_path is not None:
            conflicts.append("coverage_disposition_path")
        if request.fixture_promotion_state_path is not None:
            conflicts.append("fixture_promotion_state_path")
        if conflicts:
            raise ValueError(
                "--preflight-input 不能与逐项输入同时使用："
                + ", ".join(sorted(conflicts))
            )
        if request.preflight_input_path.suffix != ".json":
            raise ValueError("preflight_input_path 必须指向 .json 文件")
    if request.golden_answer_path is not None and request.golden_answer_path.suffix != ".json":
        raise ValueError("golden_answer_path 必须指向 .json 文件")
    if (
        request.fixture_promotion_state_path is not None
        and request.fixture_promotion_state_path.suffix != ".json"
    ):
        raise ValueError("fixture_promotion_state_path 必须指向 .json 文件")
    if (
        request.coverage_disposition_path is not None
        and request.coverage_disposition_path.suffix != ".json"
    ):
        raise ValueError("coverage_disposition_path 必须指向 .json 文件")
    if request.selected_pool_path is not None and request.selected_pool_path.suffix != ".json":
        raise ValueError("selected_pool_path 必须指向 .json 文件")
    if request.output_dir.exists() and not request.output_dir.is_dir():
        raise ValueError("output_dir 必须是目录")
