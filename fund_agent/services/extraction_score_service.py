"""精选基金池抽取评分 Service 编排层。

本模块属于 Service/Application 边界，负责把 UI 输入收敛为显式请求对象，
并委托 Capability 层 `fund_agent.fund.extraction_score` 消费 P4-S1 snapshot。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fund_agent.fund.extraction_score import ExtractionScoreResult, ScoreThresholds, run_extraction_score


@dataclass(frozen=True, slots=True)
class ExtractionScoreRequest:
    """精选基金池抽取评分 Service 请求。

    Attributes:
        snapshot_path: P4-S1 输出的 `snapshot.jsonl` 路径。
        source_csv: 精选基金池 CSV 路径。
        output_dir: 显式输出目录；为空时使用 snapshot 所在目录。
        thresholds: 显式评分阈值。
    """

    snapshot_path: Path
    source_csv: Path
    output_dir: Path | None
    thresholds: ScoreThresholds = ScoreThresholds()


class ExtractionScoreService:
    """精选基金池抽取评分用例编排 Service。

    Service 只负责请求校验与边界隔离；字段评分、golden set 选择和文件输出
    由 Capability 层实现。
    """

    def run(self, request: ExtractionScoreRequest) -> ExtractionScoreResult:
        """执行字段级抽取评分。

        Args:
            request: 显式评分参数，不使用 `extra_payload`。

        Returns:
            Capability 返回的评分运行结果。

        Raises:
            ValueError: 当请求参数非法时抛出。
            Exception: 允许 Capability 层传播 CSV、JSONL 或写文件异常。
        """

        _validate_request(request)
        return run_extraction_score(
            snapshot_path=request.snapshot_path,
            source_csv=request.source_csv,
            output_dir=request.output_dir,
            thresholds=request.thresholds,
        )


def _validate_request(request: ExtractionScoreRequest) -> None:
    """校验评分请求的 Service 层显式输入。

    Args:
        request: 评分请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当 snapshot 路径不是 JSONL 或输出目录指向文件时抛出。
    """

    if request.snapshot_path.suffix != ".jsonl":
        raise ValueError("snapshot_path 必须指向 .jsonl 文件")
    if request.output_dir is not None and request.output_dir.exists() and not request.output_dir.is_dir():
        raise ValueError("output_dir 必须是目录")
