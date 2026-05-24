"""报告质量 gate Service 编排层。

本模块属于 Service 层，负责把 UI 输入收敛为显式请求对象，
并委托 Agent 层基金能力 `fund_agent.fund.quality_gate` 消费 `score.json`。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fund_agent.fund.quality_gate import QualityGateResult, run_quality_gate


@dataclass(frozen=True, slots=True)
class QualityGateRequest:
    """报告质量 gate 请求。

    Attributes:
        score_path: `fund-analysis extraction-score` 产出的 `score.json` 路径。
        output_dir: 输出目录；为空时使用 `score_path` 所在目录。
    """

    score_path: Path
    output_dir: Path | None


class QualityGateService:
    """报告质量 gate 用例编排 Service。"""

    def run(self, request: QualityGateRequest) -> QualityGateResult:
        """执行报告质量 gate。

        Args:
            request: 显式 gate 参数，不使用 `extra_payload`。

        Returns:
            Agent 层基金能力返回的质量 gate 结果。

        Raises:
            ValueError: 请求路径非法时抛出。
            Exception: 允许 Agent 层基金能力传播 JSON 解析或文件写入异常。
        """

        _validate_request(request)
        return run_quality_gate(score_path=request.score_path, output_dir=request.output_dir)


def _validate_request(request: QualityGateRequest) -> None:
    """校验报告质量 gate 请求。

    Args:
        request: gate 请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当 score 路径或输出目录非法时抛出。
    """

    if request.score_path.suffix != ".json":
        raise ValueError("score_path 必须指向 .json 文件")
    if request.output_dir is not None and request.output_dir.exists() and not request.output_dir.is_dir():
        raise ValueError("output_dir 必须是目录")
