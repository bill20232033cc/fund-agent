"""golden answer JSON 构建 Service 编排层。

本模块属于 Service 层，负责把 UI 输入收敛为显式请求对象，
并委托 Agent 层基金能力 `fund_agent.fund.golden_answer` 完成 Markdown 转 JSON。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fund_agent.fund.golden_answer import GoldenAnswerBuildResult, build_golden_answer_json


@dataclass(frozen=True, slots=True)
class GoldenAnswerBuildRequest:
    """golden answer JSON 构建请求。

    Attributes:
        input_path: 人工审核后的 Markdown 路径。
        output_path: 输出 JSON 路径。
    """

    input_path: Path
    output_path: Path


class GoldenAnswerService:
    """golden answer JSON 构建用例编排 Service。"""

    def build(self, request: GoldenAnswerBuildRequest) -> GoldenAnswerBuildResult:
        """构建 strict golden answer JSON。

        Args:
            request: 显式构建参数，不使用 `extra_payload`。

        Returns:
            Agent 层基金能力返回的构建结果。

        Raises:
            ValueError: 请求参数非法时抛出。
            GoldenAnswerValidationError: Markdown 校验失败时由 Agent 层基金能力抛出。
            OSError: 输入读取或输出写入失败时抛出。
        """

        _validate_request(request)
        return build_golden_answer_json(input_path=request.input_path, output_path=request.output_path)


def _validate_request(request: GoldenAnswerBuildRequest) -> None:
    """校验 golden answer JSON 构建请求。

    Args:
        request: 构建请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当输入或输出路径后缀非法时抛出。
    """

    if request.input_path.suffix != ".md":
        raise ValueError("input_path 必须指向 .md 文件")
    if request.output_path.suffix != ".json":
        raise ValueError("output_path 必须指向 .json 文件")
