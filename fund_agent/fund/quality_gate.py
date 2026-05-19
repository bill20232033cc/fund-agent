"""报告质量 gate 能力。

本模块属于 Capability 层，只消费 `extraction-score` 产出的 `score.json`，
根据 coverage / traceability / correctness 质量信号生成报告质量 gate 结果。
它不读取 PDF、cache 或基金文档，也不执行 LLM 审计。
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
CORRECTNESS_STATUS_AVAILABLE: Final[str] = "available"
CORRECTNESS_STATUS_UNAVAILABLE: Final[str] = "unavailable"
CORRECTNESS_MISMATCH: Final[str] = "mismatch"


@dataclass(frozen=True, slots=True)
class QualityGateIssue:
    """单条质量 gate issue。

    Attributes:
        rule_code: 质量规则码。
        severity: 严重级别，取值为 `block / warn / info`。
        fund_code: 关联基金代码；字段聚合或全局 issue 可为空。
        field_name: 关联字段名；全局 issue 可为空。
        priority: 字段优先级；全局 issue 可为空。
        message: 人类可读说明。
        coverage_rate: 字段 coverage；全局 issue 可为空。
        traceability_rate: 字段 traceability；全局 issue 可为空。
        expected_value: correctness 期望值；非 correctness issue 为空。
        actual_value: correctness 实际值；非 correctness issue 为空。
    """

    rule_code: str
    severity: str
    fund_code: str | None
    field_name: str | None
    priority: str | None
    message: str
    coverage_rate: float | None = None
    traceability_rate: float | None = None
    expected_value: str | None = None
    actual_value: str | None = None


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
    fund_scores = score_payload.get("fund_scores")
    if fund_scores is not None:
        if not isinstance(fund_scores, list):
            raise ValueError("score.json 的 fund_scores 必须是 JSON array")
        for index, raw_row in enumerate(fund_scores):
            if not isinstance(raw_row, dict):
                raise ValueError(f"fund_scores[{index}] 必须是 JSON object")
            issues.extend(_evaluate_fund_score(raw_row, index))
    issues.extend(_evaluate_correctness(score_payload.get("correctness")))
    return issues


def _evaluate_correctness(correctness: object) -> list[QualityGateIssue]:
    """评估 score.json 中的 correctness 结果。

    Args:
        correctness: score payload 的 `correctness` 字段。

    Returns:
        correctness 相关 gate issue。

    Raises:
        ValueError: correctness 结构非法时抛出。
    """

    if not isinstance(correctness, dict):
        return [
            QualityGateIssue(
                rule_code="FQ0",
                severity=SEVERITY_INFO,
                fund_code=None,
                field_name=None,
                priority=None,
                message="score.json 未包含 correctness；等待 strict golden-answer.json 接入",
            )
        ]
    status = correctness.get("status")
    if status in {"not_implemented", CORRECTNESS_STATUS_UNAVAILABLE}:
        return [
            QualityGateIssue(
                rule_code="FQ0",
                severity=SEVERITY_INFO,
                fund_code=None,
                field_name=None,
                priority=None,
                message="correctness 尚未接入；等待人工审核后的 golden-answer.json",
            )
        ]
    if status != CORRECTNESS_STATUS_AVAILABLE:
        raise ValueError("score.json correctness.status 必须是 available / unavailable")
    record_results = correctness.get("record_results", [])
    if not isinstance(record_results, list):
        raise ValueError("score.json correctness.record_results 必须是 JSON array")
    issues: list[QualityGateIssue] = []
    for index, raw_row in enumerate(record_results):
        if not isinstance(raw_row, dict):
            raise ValueError(f"correctness.record_results[{index}] 必须是 JSON object")
        if raw_row.get("status") == CORRECTNESS_MISMATCH:
            issues.append(_correctness_mismatch_issue(raw_row, index))
    return issues


def _correctness_mismatch_issue(row: Mapping[str, object], index: int) -> QualityGateIssue:
    """把 correctness mismatch 明细转成 FQ1 issue。

    Args:
        row: correctness.record_results 中的单行。
        index: 行号，用于错误信息。

    Returns:
        FQ1 阻断 issue。

    Raises:
        ValueError: mismatch 行缺少必要文本时抛出。
    """

    fund_code = _required_correctness_text(row, "fund_code", index)
    field_name = _required_correctness_text(row, "field_name", index)
    sub_field = _required_correctness_text(row, "sub_field", index)
    expected_value = _required_correctness_text(row, "expected_value", index)
    actual_value = _optional_correctness_text(row, "actual_value")
    reason = _required_correctness_text(row, "reason", index)
    return QualityGateIssue(
        rule_code="FQ1",
        severity=SEVERITY_BLOCK,
        fund_code=fund_code,
        field_name=field_name,
        priority=None,
        message=(
            f"基金 `{fund_code}` 的 `{field_name}.{sub_field}` 与 golden answer 明显冲突；{reason}"
        ),
        expected_value=expected_value,
        actual_value=actual_value,
    )


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
                fund_code=None,
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
                    fund_code=None,
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
                fund_code=None,
                field_name=field_name,
                priority=priority,
                message=f"P1 关键字段 `{field_name}` coverage/traceability 未达标，报告应提示数据不足",
                coverage_rate=coverage_rate,
                traceability_rate=traceability_rate,
            )
        )
    return issues


def _evaluate_fund_score(row: Mapping[str, object], index: int) -> list[QualityGateIssue]:
    """评估单只基金质量汇总行。

    Args:
        row: `fund_scores` 中的单行。
        index: 行号，用于错误信息。

    Returns:
        该基金触发的 issue 列表。

    Raises:
        ValueError: 基金评分行缺少必要键时抛出。
    """

    fund_code = _required_fund_text(row, "fund_code", index)
    p0_status = _required_fund_text(row, "p0_status", index)
    p1_status = _required_fund_text(row, "p1_status", index)
    issues: list[QualityGateIssue] = []
    p0_failed_fields = _optional_text_list(row, "p0_failed_fields", index)
    p1_failed_fields = _optional_text_list(row, "p1_failed_fields", index)
    if p0_status == STATUS_FAIL:
        issues.append(
            QualityGateIssue(
                rule_code="FQ2F",
                severity=SEVERITY_BLOCK,
                fund_code=fund_code,
                field_name=None,
                priority=PRIORITY_P0,
                message=(
                    f"基金 `{fund_code}` 存在 P0 字段失败，阻断单基金报告可用状态；"
                    f"失败字段：{_join_fields(p0_failed_fields)}"
                ),
            )
        )
    if p1_status == STATUS_FAIL:
        issues.append(
            QualityGateIssue(
                rule_code="FQ2F",
                severity=SEVERITY_WARN,
                fund_code=fund_code,
                field_name=None,
                priority=PRIORITY_P1,
                message=f"基金 `{fund_code}` 存在 P1 字段失败；失败字段：{_join_fields(p1_failed_fields)}",
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


def _required_fund_text(row: Mapping[str, object], key: str, index: int) -> str:
    """读取基金评分行中的必需文本。

    Args:
        row: 基金评分行。
        key: 字段名。
        index: 行号。

    Returns:
        非空文本。

    Raises:
        ValueError: 缺少字段或字段非文本时抛出。
    """

    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"fund_scores[{index}].{key} 必须是非空字符串")
    return value


def _optional_text_list(row: Mapping[str, object], key: str, index: int) -> tuple[str, ...]:
    """读取基金评分行中的可选文本列表。

    Args:
        row: 基金评分行。
        key: 字段名。
        index: 行号。

    Returns:
        文本元组；缺失时返回空元组。

    Raises:
        ValueError: 字段存在但不是文本列表时抛出。
    """

    value = row.get(key)
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"fund_scores[{index}].{key} 必须是字符串数组")
    return tuple(value)


def _required_correctness_text(row: Mapping[str, object], key: str, index: int) -> str:
    """读取 correctness 明细行中的必需文本。

    Args:
        row: correctness 明细行。
        key: 字段名。
        index: 行号。

    Returns:
        非空文本。

    Raises:
        ValueError: 缺少字段或字段非文本时抛出。
    """

    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"correctness.record_results[{index}].{key} 必须是非空字符串")
    return value


def _optional_correctness_text(row: Mapping[str, object], key: str) -> str | None:
    """读取 correctness 明细行中的可选文本。

    Args:
        row: correctness 明细行。
        key: 字段名。

    Returns:
        文本或 `None`。

    Raises:
        无显式抛出。
    """

    value = row.get(key)
    if value is None:
        return None
    return str(value)


def _join_fields(fields: tuple[str, ...]) -> str:
    """格式化失败字段列表。

    Args:
        fields: 失败字段名。

    Returns:
        逗号分隔字段；空列表返回 `unknown`。

    Raises:
        无显式抛出。
    """

    if not fields:
        return "unknown"
    return ", ".join(fields)


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
        "| rule | severity | fund_code | field | priority | coverage | traceability | expected | actual | message |",
        "|---|---|---|---|---|---:|---:|---|---|---|",
    ]
    for issue in result.issues:
        lines.append(
            "| "
            f"{issue.rule_code} | "
            f"{issue.severity} | "
            f"{issue.fund_code or ''} | "
            f"{issue.field_name or ''} | "
            f"{issue.priority or ''} | "
            f"{_format_rate(issue.coverage_rate)} | "
            f"{_format_rate(issue.traceability_rate)} | "
            f"{_escape_markdown_cell(issue.expected_value or '')} | "
            f"{_escape_markdown_cell(issue.actual_value or '')} | "
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


def _escape_markdown_cell(value: str) -> str:
    """转义 Markdown 表格单元格。

    Args:
        value: 原始文本。

    Returns:
        转义竖线并压平换行后的文本。

    Raises:
        无显式抛出。
    """

    return value.replace("|", "\\|").replace("\n", " ")
