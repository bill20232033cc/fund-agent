"""报告质量 gate 能力。

本模块属于 Capability 层，只消费 `extraction-score` 产出的 `score.json`，
根据 coverage / traceability 质量信号生成报告质量 gate 结果。它不读取
PDF、cache 或基金文档，也不执行 correctness 比对。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, Mapping

GATE_JSON_FILENAME: Final[str] = "quality_gate.json"
GATE_MARKDOWN_FILENAME: Final[str] = "quality_gate.md"
GATE_STATUS_PASS: Final[str] = "pass"
GATE_STATUS_WARN: Final[str] = "warn"
GATE_STATUS_BLOCK: Final[str] = "block"
SEVERITY_BLOCK: Final[str] = "block"
SEVERITY_WARN: Final[str] = "warn"
SEVERITY_INFO: Final[str] = "info"
PRIORITY_P0: Final[str] = "P0"
PRIORITY_P1: Final[str] = "P1"
STATUS_FAIL: Final[str] = "fail"


@dataclass(frozen=True, slots=True)
class QualityGateIssue:
    """单条质量 gate issue。

    Attributes:
        rule_code: 质量规则码。
        severity: 严重级别，取值为 `block / warn / info`。
        field_name: 关联字段名；全局 issue 可为空。
        priority: 字段优先级；全局 issue 可为空。
        message: 人类可读说明。
        coverage_rate: 字段 coverage；全局 issue 可为空。
        traceability_rate: 字段 traceability；全局 issue 可为空。
    """

    rule_code: str
    severity: str
    field_name: str | None
    priority: str | None
    message: str
    coverage_rate: float | None = None
    traceability_rate: float | None = None


@dataclass(frozen=True, slots=True)
class QualityGateResult:
    """报告质量 gate 运行结果。

    Attributes:
        score_path: 输入 `score.json` 路径。
        output_dir: 输出目录。
        gate_json_path: gate JSON 输出路径。
        gate_markdown_path: gate Markdown 输出路径。
        status: 聚合状态，取值为 `pass / warn / block`。
        issues: 质量问题列表。
    """

    score_path: Path
    output_dir: Path
    gate_json_path: Path
    gate_markdown_path: Path
    status: str
    issues: tuple[QualityGateIssue, ...]


def run_quality_gate(
    *,
    score_path: Path,
    output_dir: Path | None = None,
) -> QualityGateResult:
    """基于 `score.json` 生成报告质量 gate 结果。

    Args:
        score_path: `fund-analysis extraction-score` 产出的 `score.json` 路径。
        output_dir: 输出目录；为空时使用 `score_path` 所在目录。

    Returns:
        质量 gate 运行结果。

    Raises:
        FileNotFoundError: `score_path` 不存在时抛出。
        ValueError: `score.json` 结构缺少必要字段时抛出。
        json.JSONDecodeError: `score.json` 不是合法 JSON 时抛出。
        OSError: 输出文件写入失败时抛出。
    """

    score_payload = _load_score_payload(score_path)
    issues = _evaluate_score_payload(score_payload)
    status = _aggregate_gate_status(issues)
    resolved_output_dir = output_dir or score_path.parent
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    result = QualityGateResult(
        score_path=score_path,
        output_dir=resolved_output_dir,
        gate_json_path=resolved_output_dir / GATE_JSON_FILENAME,
        gate_markdown_path=resolved_output_dir / GATE_MARKDOWN_FILENAME,
        status=status,
        issues=tuple(issues),
    )
    result.gate_json_path.write_text(
        json.dumps(_json_payload(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    result.gate_markdown_path.write_text(_markdown_payload(result), encoding="utf-8")
    return result


def _load_score_payload(score_path: Path) -> dict[str, object]:
    """读取并校验 score JSON 顶层结构。

    Args:
        score_path: score JSON 路径。

    Returns:
        score payload。

    Raises:
        FileNotFoundError: 文件不存在时抛出。
        ValueError: 顶层不是 JSON object 时抛出。
        json.JSONDecodeError: JSON 非法时抛出。
    """

    payload = json.loads(score_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("score_path 必须指向 JSON object")
    return payload


def _evaluate_score_payload(score_payload: Mapping[str, object]) -> list[QualityGateIssue]:
    """从 score payload 生成质量 issue。

    Args:
        score_payload: `score.json` 顶层 payload。

    Returns:
        质量 issue 列表。

    Raises:
        ValueError: 缺少 `field_scores` 或字段行结构非法时抛出。
    """

    field_scores = score_payload.get("field_scores")
    if not isinstance(field_scores, list):
        raise ValueError("score.json 缺少 field_scores 列表")
    issues: list[QualityGateIssue] = []
    for index, raw_row in enumerate(field_scores):
        if not isinstance(raw_row, dict):
            raise ValueError(f"field_scores[{index}] 必须是 JSON object")
        issues.extend(_evaluate_field_score(raw_row, index))
    correctness = score_payload.get("correctness")
    if isinstance(correctness, dict) and correctness.get("status") == "not_implemented":
        issues.append(
            QualityGateIssue(
                rule_code="FQ0",
                severity=SEVERITY_INFO,
                field_name=None,
                priority=None,
                message="correctness 尚未接入；等待人工审核后的 golden-answer.json",
            )
        )
    return issues


def _evaluate_field_score(row: Mapping[str, object], index: int) -> list[QualityGateIssue]:
    """评估单个字段评分行。

    Args:
        row: `field_scores` 中的单行。
        index: 行号，用于错误信息。

    Returns:
        该字段触发的 issue 列表。

    Raises:
        ValueError: 字段评分行缺少必要键时抛出。
    """

    field_name = _required_text(row, "field_name", index)
    priority = _required_text(row, "priority", index)
    status = _required_text(row, "status", index)
    coverage_rate = _required_number(row, "coverage_rate", index)
    traceability_rate = _required_number(row, "traceability_rate", index)
    issues: list[QualityGateIssue] = []
    if priority == PRIORITY_P0 and status == STATUS_FAIL:
        issues.append(
            QualityGateIssue(
                rule_code="FQ2",
                severity=SEVERITY_BLOCK,
                field_name=field_name,
                priority=priority,
                message=f"P0 必须字段 `{field_name}` coverage/traceability 未达标，阻断报告可用状态",
                coverage_rate=coverage_rate,
                traceability_rate=traceability_rate,
            )
        )
        if traceability_rate < 0.9:
            issues.append(
                QualityGateIssue(
                    rule_code="FQ3",
                    severity=SEVERITY_BLOCK,
                    field_name=field_name,
                    priority=priority,
                    message=f"P0 必须字段 `{field_name}` 证据锚点不足",
                    coverage_rate=coverage_rate,
                    traceability_rate=traceability_rate,
                )
            )
    elif priority == PRIORITY_P1 and status == STATUS_FAIL:
        issues.append(
            QualityGateIssue(
                rule_code="FQ2",
                severity=SEVERITY_WARN,
                field_name=field_name,
                priority=priority,
                message=f"P1 关键字段 `{field_name}` coverage/traceability 未达标，报告应提示数据不足",
                coverage_rate=coverage_rate,
                traceability_rate=traceability_rate,
            )
        )
    return issues


def _required_text(row: Mapping[str, object], key: str, index: int) -> str:
    """读取字段评分行中的必需文本。

    Args:
        row: 字段评分行。
        key: 字段名。
        index: 行号。

    Returns:
        非空文本。

    Raises:
        ValueError: 缺少字段或字段非文本时抛出。
    """

    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"field_scores[{index}].{key} 必须是非空字符串")
    return value


def _required_number(row: Mapping[str, object], key: str, index: int) -> float:
    """读取字段评分行中的必需数值。

    Args:
        row: 字段评分行。
        key: 字段名。
        index: 行号。

    Returns:
        浮点数。

    Raises:
        ValueError: 缺少字段或字段非数值时抛出。
    """

    value = row.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"field_scores[{index}].{key} 必须是数值")
    return float(value)


def _aggregate_gate_status(issues: tuple[QualityGateIssue, ...] | list[QualityGateIssue]) -> str:
    """聚合 gate 状态。

    Args:
        issues: 质量 issue 列表。

    Returns:
        任一 block 则 `block`，否则任一 warn 则 `warn`，否则 `pass`。

    Raises:
        无显式抛出。
    """

    severities = {issue.severity for issue in issues}
    if SEVERITY_BLOCK in severities:
        return GATE_STATUS_BLOCK
    if SEVERITY_WARN in severities:
        return GATE_STATUS_WARN
    return GATE_STATUS_PASS


def _json_payload(result: QualityGateResult) -> dict[str, object]:
    """构造 gate JSON payload。

    Args:
        result: gate 运行结果。

    Returns:
        可序列化 JSON。

    Raises:
        无显式抛出。
    """

    return {
        "score_path": str(result.score_path),
        "status": result.status,
        "issue_count": len(result.issues),
        "issues": [asdict(issue) for issue in result.issues],
    }


def _markdown_payload(result: QualityGateResult) -> str:
    """构造 gate Markdown payload。

    Args:
        result: gate 运行结果。

    Returns:
        Markdown 文本。

    Raises:
        无显式抛出。
    """

    lines = [
        "# Report Quality Gate",
        "",
        f"- score_path: `{result.score_path}`",
        f"- status: `{result.status}`",
        f"- issue_count: {len(result.issues)}",
        "",
        "## Issues",
        "",
        "| rule | severity | field | priority | coverage | traceability | message |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for issue in result.issues:
        lines.append(
            "| "
            f"{issue.rule_code} | "
            f"{issue.severity} | "
            f"{issue.field_name or ''} | "
            f"{issue.priority or ''} | "
            f"{_format_rate(issue.coverage_rate)} | "
            f"{_format_rate(issue.traceability_rate)} | "
            f"{issue.message} |"
        )
    return "\n".join(lines) + "\n"


def _format_rate(value: float | None) -> str:
    """格式化百分比。

    Args:
        value: 比率值。

    Returns:
        一位小数百分比；空值返回空字符串。

    Raises:
        无显式抛出。
    """

    if value is None:
        return ""
    return f"{value:.1%}"
