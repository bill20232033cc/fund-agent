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
CORRECTNESS_COVERAGE_NOT_CONFIGURED: Final[str] = "not_configured"
CORRECTNESS_COVERAGE_FUND_NOT_COVERED: Final[str] = "fund_not_covered"
CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS: Final[str] = "no_comparable_fields"
CORRECTNESS_COVERAGE_PARTIALLY_COVERED: Final[str] = "partially_covered"
CORRECTNESS_COVERAGE_COVERED: Final[str] = "covered"
CORRECTNESS_MISMATCH: Final[str] = "mismatch"
APP_CATEGORY_STATUS_CONFLICT: Final[str] = "conflict"
PREFERRED_LENS_STATUS_MISMATCH: Final[str] = "mismatch"
PREFERRED_LENS_STATUS_RESOLVED: Final[str] = "resolved"
PREFERRED_LENS_STATUS_NOT_APPLICABLE: Final[str] = "not_applicable"
LEGACY_PREFERRED_LENS_STATUS_MATCH: Final[str] = "match"
FQ4_WARN_MISSING_FIELD_RATE: Final[float] = 0.20
FQ4_BLOCK_MISSING_FIELD_RATE: Final[float] = 0.35


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
        app_category: App 类别；非类别相关 issue 为空。
        classified_fund_type: 系统识别基金类型；非类型相关 issue 为空。
        preferred_lens_key: preferred_lens key；非 lens 相关 issue 为空。
        observed_rate: 观测比例，如 FQ4 缺失率。
        threshold: 触发阈值。
        error_type: 抽取失败异常类型；非失败基金 issue 为空。
        error_message: 抽取失败异常信息；非失败基金 issue 为空。
        reason: 机器可读原因；correctness coverage issue 使用。
        golden_answer_path: strict golden answer JSON 路径。
        coverage_scope: correctness 覆盖范围。
        comparable_records: 可比 correctness 记录数。
        unavailable_records: 不可比 correctness 记录数。
        total_records: strict golden answer 有效记录数。
        missing_fund_codes: 缺少 correctness 覆盖的基金代码。
        covered_fund_codes: 已有可比 correctness 覆盖的基金代码。
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
    app_category: str | None = None
    classified_fund_type: str | None = None
    preferred_lens_key: str | None = None
    observed_rate: float | None = None
    threshold: float | None = None
    error_type: str | None = None
    error_message: str | None = None
    reason: str | None = None
    golden_answer_path: str | None = None
    coverage_scope: str | None = None
    comparable_records: int | None = None
    unavailable_records: int | None = None
    total_records: int | None = None
    missing_fund_codes: tuple[str, ...] = ()
    covered_fund_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class QualityGateRuleResult:
    """质量 gate 单条规则运行结果。

    Attributes:
        rule_code: 质量规则码。
        severity: 规则结果严重级别。
        fund_code: 关联基金代码；全局规则可为空。
        status: 规则状态。
        message: 人类可读说明。
        app_category: App 类别；非类别相关规则为空。
        classified_fund_type: 系统识别基金类型；非类型相关规则为空。
        preferred_lens_key: preferred_lens key；非 lens 相关规则为空。
    """

    rule_code: str
    severity: str
    fund_code: str | None
    status: str
    message: str
    app_category: str | None = None
    classified_fund_type: str | None = None
    preferred_lens_key: str | None = None


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
        rule_results: 规则运行结果列表，包含未触发 issue 的解释性结果。
    """

    score_path: Path
    output_dir: Path
    gate_json_path: Path
    gate_markdown_path: Path
    status: str
    issues: tuple[QualityGateIssue, ...]
    rule_results: tuple[QualityGateRuleResult, ...] = ()


@dataclass(frozen=True, slots=True)
class _ScoreEvaluation:
    """score payload 内部评估结果。

    Attributes:
        issues: 质量问题列表。
        rule_results: 规则运行结果列表。
    """

    issues: tuple[QualityGateIssue, ...]
    rule_results: tuple[QualityGateRuleResult, ...]


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
    evaluation = _evaluate_score_payload(score_payload)
    issues = evaluation.issues
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
        rule_results=evaluation.rule_results,
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


def _evaluate_score_payload(score_payload: Mapping[str, object]) -> _ScoreEvaluation:
    """从 score payload 生成质量 issue 和规则结果。

    Args:
        score_payload: `score.json` 顶层 payload。

    Returns:
        质量 issue 与规则结果。

    Raises:
        ValueError: 缺少 `field_scores` 或字段行结构非法时抛出。
    """

    field_scores = score_payload.get("field_scores")
    if not isinstance(field_scores, list):
        raise ValueError("score.json 缺少 field_scores 列表")
    issues: list[QualityGateIssue] = []
    rule_results: list[QualityGateRuleResult] = []
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
    fund_quality = score_payload.get("fund_quality")
    if fund_quality is None:
        issues.append(
            QualityGateIssue(
                rule_code="FQ0",
                severity=SEVERITY_INFO,
                fund_code=None,
                field_name=None,
                priority=None,
                message="score.json 未包含 fund_quality；FQ1 App 类别、FQ4、FQ5 未运行",
            )
        )
    else:
        if not isinstance(fund_quality, list):
            raise ValueError("score.json 的 fund_quality 必须是 JSON array")
        for index, raw_row in enumerate(fund_quality):
            if not isinstance(raw_row, dict):
                raise ValueError(f"fund_quality[{index}] 必须是 JSON object")
            fund_quality_evaluation = _evaluate_fund_quality(raw_row, index)
            issues.extend(fund_quality_evaluation.issues)
            rule_results.extend(fund_quality_evaluation.rule_results)
    failed_funds = score_payload.get("failed_funds")
    if failed_funds is not None:
        if not isinstance(failed_funds, list):
            raise ValueError("score.json 的 failed_funds 必须是 JSON array")
        for index, raw_row in enumerate(failed_funds):
            if not isinstance(raw_row, dict):
                raise ValueError(f"failed_funds[{index}] 必须是 JSON object")
            issues.append(_evaluate_failed_fund(raw_row, index))
    return _ScoreEvaluation(issues=tuple(issues), rule_results=tuple(rule_results))


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
                reason=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
                coverage_scope=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
            )
        ]
    status = correctness.get("status")
    if status == "not_implemented":
        return [
            _correctness_coverage_issue(
                fund_code=None,
                correctness=correctness,
                reason=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
                coverage_scope=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
                message="correctness 尚未接入；等待人工审核后的 golden-answer.json",
            )
        ]
    if status == CORRECTNESS_STATUS_UNAVAILABLE:
        reason = _optional_correctness_summary_text(correctness, "coverage_reason")
        coverage_scope = _optional_correctness_summary_text(correctness, "coverage_scope")
        _valid_unavailable = {None, CORRECTNESS_COVERAGE_NOT_CONFIGURED}
        if reason not in _valid_unavailable:
            raise ValueError(f"score.json correctness.coverage_reason 不受支持：{reason}")
        if coverage_scope not in _valid_unavailable:
            raise ValueError(f"score.json correctness.coverage_scope 不受支持：{coverage_scope}")
        missing_codes = _optional_correctness_text_list(correctness, "missing_fund_codes")
        return [
            _correctness_coverage_issue(
                fund_code=missing_codes[0] if len(missing_codes) == 1 else None,
                correctness=correctness,
                reason=reason or CORRECTNESS_COVERAGE_NOT_CONFIGURED,
                coverage_scope=coverage_scope or CORRECTNESS_COVERAGE_NOT_CONFIGURED,
                message="strict golden answer 未配置；本次 quality gate 未执行 correctness oracle。",
            )
        ]
    if status != CORRECTNESS_STATUS_AVAILABLE:
        raise ValueError("score.json correctness.status 必须是 available / unavailable")
    record_results = correctness.get("record_results", [])
    if not isinstance(record_results, list):
        raise ValueError("score.json correctness.record_results 必须是 JSON array")
    issues: list[QualityGateIssue] = []
    coverage_issue = _correctness_available_coverage_issue(correctness)
    if coverage_issue is not None:
        issues.append(coverage_issue)
    for index, raw_row in enumerate(record_results):
        if not isinstance(raw_row, dict):
            raise ValueError(f"correctness.record_results[{index}] 必须是 JSON object")
        if raw_row.get("status") == CORRECTNESS_MISMATCH:
            issues.append(_correctness_mismatch_issue(raw_row, index))
    return issues


def _correctness_available_coverage_issue(
    correctness: Mapping[str, object],
) -> QualityGateIssue | None:
    """为 available correctness 汇总生成覆盖缺口 FQ0/info。

    Args:
        correctness: score.json correctness 汇总。

    Returns:
        有覆盖缺口时返回 FQ0/info；覆盖充分时返回 `None`。

    Raises:
        ValueError: coverage 字段类型非法时抛出。
    """

    coverage_scope = _optional_correctness_summary_text(correctness, "coverage_scope")
    if coverage_scope in {None, CORRECTNESS_COVERAGE_COVERED}:
        return None
    if coverage_scope == CORRECTNESS_COVERAGE_PARTIALLY_COVERED:
        missing_codes = _optional_correctness_text_list(correctness, "missing_fund_codes")
        covered_codes = _optional_correctness_text_list(correctness, "covered_fund_codes")
        if not missing_codes:
            fund_code = covered_codes[0] if len(covered_codes) == 1 else None
            return _correctness_coverage_issue(
                fund_code=fund_code,
                correctness=correctness,
                reason="field_not_comparable",
                coverage_scope=coverage_scope,
                message=(
                    "当前基金 strict golden answer 部分字段超出 snapshot 可比合约；"
                    "本次 correctness oracle 仅比较已暴露的可比字段。"
                ),
            )
        return _correctness_coverage_issue(
            fund_code=missing_codes[0] if len(missing_codes) == 1 else None,
            correctness=correctness,
            reason=CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
            coverage_scope=coverage_scope,
            message=_correctness_coverage_message(
                fund_code=missing_codes[0] if len(missing_codes) == 1 else None,
                reason=CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
            ),
        )
    if coverage_scope in {
        CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
        CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS,
    }:
        missing_codes = _optional_correctness_text_list(correctness, "missing_fund_codes")
        return _correctness_coverage_issue(
            fund_code=missing_codes[0] if len(missing_codes) == 1 else None,
            correctness=correctness,
            reason=coverage_scope,
            coverage_scope=coverage_scope,
            message=_correctness_coverage_message(
                fund_code=missing_codes[0] if len(missing_codes) == 1 else None,
                reason=coverage_scope,
            ),
        )
    if coverage_scope == CORRECTNESS_COVERAGE_NOT_CONFIGURED:
        return _correctness_coverage_issue(
            fund_code=None,
            correctness=correctness,
            reason=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
            coverage_scope=coverage_scope,
            message="strict golden answer 未配置；本次 quality gate 未执行 correctness oracle。",
        )
    raise ValueError(f"score.json correctness.coverage_scope 不受支持：{coverage_scope}")


def _correctness_coverage_issue(
    *,
    fund_code: str | None,
    correctness: Mapping[str, object],
    reason: str,
    coverage_scope: str,
    message: str,
) -> QualityGateIssue:
    """构造 correctness coverage 的 FQ0/info issue。

    Args:
        fund_code: 当前基金代码；多基金聚合缺口可为空。
        correctness: score.json correctness 汇总。
        reason: 机器可读 coverage reason。
        coverage_scope: coverage scope。
        message: 人类可读消息。

    Returns:
        FQ0/info issue。

    Raises:
        ValueError: count 或列表字段类型非法时抛出。
    """

    return QualityGateIssue(
        rule_code="FQ0",
        severity=SEVERITY_INFO,
        fund_code=fund_code,
        field_name=None,
        priority=None,
        message=message,
        reason=reason,
        golden_answer_path=_optional_correctness_summary_text(correctness, "golden_answer_path"),
        coverage_scope=coverage_scope,
        comparable_records=_optional_correctness_int(correctness, "comparable_records"),
        unavailable_records=_optional_correctness_int(correctness, "unavailable_records"),
        total_records=_optional_correctness_int(correctness, "total_records"),
        missing_fund_codes=_optional_correctness_text_list(correctness, "missing_fund_codes"),
        covered_fund_codes=_optional_correctness_text_list(correctness, "covered_fund_codes"),
    )


def _correctness_coverage_message(*, fund_code: str | None, reason: str) -> str:
    """生成 correctness coverage FQ0/info 消息。

    Args:
        fund_code: 当前基金代码。
        reason: coverage reason。

    Returns:
        用户可读消息。

    Raises:
        无显式抛出。
    """

    target = f"基金 `{fund_code}`" if fund_code is not None else "当前基金"
    if reason == CORRECTNESS_COVERAGE_FUND_NOT_COVERED:
        return (
            f"{target} 在精选池中，但 strict golden answer 尚未覆盖；本次 quality gate 已执行 "
            "coverage/traceability/fund_quality 检查，未执行该基金 correctness oracle。"
        )
    if reason == CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS:
        return (
            f"{target} 已有 strict golden answer 记录，但当前 snapshot 合约没有可比字段；"
            "本次 correctness oracle 不进入阻断分母。"
        )
    return "strict golden answer 未配置；本次 quality gate 未执行 correctness oracle。"


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


def _evaluate_fund_quality(row: Mapping[str, object], index: int) -> _ScoreEvaluation:
    """评估单只基金质量派生行。

    Args:
        row: `fund_quality` 中的单行。
        index: 行号，用于错误信息。

    Returns:
        该基金触发的 issue 与 FQ5 规则结果。

    Raises:
        ValueError: 基金质量行结构非法时抛出。
    """

    fund_code = _required_quality_text(row, "fund_code", index)
    app_category = _optional_quality_text(row, "app_category")
    classified_fund_type = _optional_quality_text(row, "classified_fund_type")
    preferred_lens_key = _optional_quality_text(row, "preferred_lens_key")
    reason = _optional_quality_text(row, "reason") or ""
    app_category_status = _required_quality_text(row, "app_category_status", index)
    preferred_lens_status = _normalize_preferred_lens_status(
        _required_quality_text(row, "preferred_lens_status", index),
        index,
    )
    missing_field_rate = _required_quality_number(row, "missing_field_rate", index)
    issues: list[QualityGateIssue] = []
    rule_result = _fund_quality_rule_result(
        fund_code=fund_code,
        app_category=app_category,
        classified_fund_type=classified_fund_type,
        preferred_lens_key=preferred_lens_key,
        preferred_lens_status=preferred_lens_status,
        reason=reason,
    )
    if app_category_status == APP_CATEGORY_STATUS_CONFLICT:
        issues.append(
            QualityGateIssue(
                rule_code="FQ1",
                severity=SEVERITY_BLOCK,
                fund_code=fund_code,
                field_name=None,
                priority=None,
                message=(
                    f"基金 `{fund_code}` 的 App 类别 `{app_category}` 与系统基金类型 "
                    f"`{classified_fund_type}` 明确冲突；{reason}"
                ),
                app_category=app_category,
                classified_fund_type=classified_fund_type,
            )
        )
    issues.extend(
        _missing_rate_issues(
            fund_code=fund_code,
            missing_field_rate=missing_field_rate,
        )
    )
    if preferred_lens_status == PREFERRED_LENS_STATUS_MISMATCH:
        issues.append(
            QualityGateIssue(
                rule_code="FQ5",
                severity=SEVERITY_BLOCK,
                fund_code=fund_code,
                field_name=None,
                priority=None,
                message=(
                    f"基金 `{fund_code}` 无法稳定应用模板契约；"
                    f"fund_type=`{classified_fund_type or ''}`，{reason}"
                ),
                app_category=app_category,
                classified_fund_type=classified_fund_type,
                preferred_lens_key=preferred_lens_key,
            )
        )
    return _ScoreEvaluation(issues=tuple(issues), rule_results=(rule_result,))


def _missing_rate_issues(
    *,
    fund_code: str,
    missing_field_rate: float,
) -> list[QualityGateIssue]:
    """按缺失率生成 FQ4 issue。

    Args:
        fund_code: 基金代码。
        missing_field_rate: snapshot 字段缺失率。

    Returns:
        FQ4 issue 列表。

    Raises:
        无显式抛出。
    """

    if missing_field_rate >= FQ4_BLOCK_MISSING_FIELD_RATE:
        return [
            QualityGateIssue(
                rule_code="FQ4",
                severity=SEVERITY_BLOCK,
                fund_code=fund_code,
                field_name=None,
                priority=None,
                message=f"基金 `{fund_code}` snapshot 字段缺失率过高，阻断报告可用状态",
                observed_rate=missing_field_rate,
                threshold=FQ4_BLOCK_MISSING_FIELD_RATE,
            )
        ]
    if missing_field_rate >= FQ4_WARN_MISSING_FIELD_RATE:
        return [
            QualityGateIssue(
                rule_code="FQ4",
                severity=SEVERITY_WARN,
                fund_code=fund_code,
                field_name=None,
                priority=None,
                message=f"基金 `{fund_code}` snapshot 字段缺失率偏高，报告应提示数据不足",
                observed_rate=missing_field_rate,
                threshold=FQ4_WARN_MISSING_FIELD_RATE,
            )
        ]
    return []


def _normalize_preferred_lens_status(status: str, index: int) -> str:
    """规范化 score.json 中的 FQ5 状态。

    Args:
        status: score.json `preferred_lens_status` 原始状态。
        index: `fund_quality` 行号，用于错误信息。

    Returns:
        `resolved / not_applicable / mismatch` 之一。

    Raises:
        ValueError: 状态不受支持时抛出。
    """

    if status == LEGACY_PREFERRED_LENS_STATUS_MATCH:
        return PREFERRED_LENS_STATUS_RESOLVED
    if status in {
        PREFERRED_LENS_STATUS_RESOLVED,
        PREFERRED_LENS_STATUS_NOT_APPLICABLE,
        PREFERRED_LENS_STATUS_MISMATCH,
    }:
        return status
    raise ValueError(f"fund_quality[{index}].preferred_lens_status 不受支持：{status}")


def _fund_quality_rule_result(
    *,
    fund_code: str,
    app_category: str | None,
    classified_fund_type: str | None,
    preferred_lens_key: str | None,
    preferred_lens_status: str,
    reason: str,
) -> QualityGateRuleResult:
    """构造 FQ5 模板契约适用性规则结果。

    Args:
        fund_code: 基金代码。
        app_category: App 类别。
        classified_fund_type: 系统识别基金类型。
        preferred_lens_key: score.json 中记录的 preferred_lens key。
        preferred_lens_status: 已规范化的 FQ5 状态。
        reason: score.json 中的基金质量原因。

    Returns:
        FQ5 规则运行结果。

    Raises:
        无显式抛出。
    """

    severity = (
        SEVERITY_BLOCK if preferred_lens_status == PREFERRED_LENS_STATUS_MISMATCH else SEVERITY_INFO
    )
    return QualityGateRuleResult(
        rule_code="FQ5",
        severity=severity,
        fund_code=fund_code,
        status=preferred_lens_status,
        message=(
            f"基金 `{fund_code}` FQ5 template_contract_applicability="
            f"`{preferred_lens_status}`；{reason}"
        ),
        app_category=app_category,
        classified_fund_type=classified_fund_type,
        preferred_lens_key=preferred_lens_key,
    )


def _evaluate_failed_fund(row: Mapping[str, object], index: int) -> QualityGateIssue:
    """评估完全抽取失败基金。

    Args:
        row: `failed_funds` 中的单行。
        index: 行号，用于错误信息。

    Returns:
        FQ6 阻断 issue。

    Raises:
        ValueError: 失败基金行缺少必要基金代码时抛出。
    """

    fund_code = _required_failed_fund_text(row, "fund_code", index)
    error_type = _optional_failed_fund_text(row, "error_type")
    error_message = _optional_failed_fund_text(row, "error_message")
    return QualityGateIssue(
        rule_code="FQ6",
        severity=SEVERITY_BLOCK,
        fund_code=fund_code,
        field_name=None,
        priority=None,
        message=(
            f"基金 `{fund_code}` 抽取流程失败，无法生成可靠报告；error_type=`{error_type or ''}`"
        ),
        error_type=error_type,
        error_message=error_message,
    )


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


def _required_quality_text(row: Mapping[str, object], key: str, index: int) -> str:
    """读取基金质量行中的必需文本。

    Args:
        row: 基金质量行。
        key: 字段名。
        index: 行号。

    Returns:
        非空文本。

    Raises:
        ValueError: 缺少字段或字段非文本时抛出。
    """

    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"fund_quality[{index}].{key} 必须是非空字符串")
    return value


def _optional_quality_text(row: Mapping[str, object], key: str) -> str | None:
    """读取基金质量行中的可选文本。

    Args:
        row: 基金质量行。
        key: 字段名。

    Returns:
        文本或 `None`。

    Raises:
        无显式抛出。
    """

    value = row.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _required_quality_number(row: Mapping[str, object], key: str, index: int) -> float:
    """读取基金质量行中的必需数值。

    Args:
        row: 基金质量行。
        key: 字段名。
        index: 行号。

    Returns:
        浮点数。

    Raises:
        ValueError: 缺少字段或字段非数值时抛出。
    """

    value = row.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"fund_quality[{index}].{key} 必须是数值")
    return float(value)


def _required_failed_fund_text(row: Mapping[str, object], key: str, index: int) -> str:
    """读取失败基金行中的必需文本。

    Args:
        row: 失败基金行。
        key: 字段名。
        index: 行号。

    Returns:
        非空文本。

    Raises:
        ValueError: 缺少字段或字段非文本时抛出。
    """

    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"failed_funds[{index}].{key} 必须是非空字符串")
    return value


def _optional_failed_fund_text(row: Mapping[str, object], key: str) -> str | None:
    """读取失败基金行中的可选文本。

    Args:
        row: 失败基金行。
        key: 字段名。

    Returns:
        文本或 `None`。

    Raises:
        无显式抛出。
    """

    value = row.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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


def _optional_correctness_summary_text(row: Mapping[str, object], key: str) -> str | None:
    """读取 correctness 汇总中的可选文本。

    Args:
        row: correctness 汇总。
        key: 字段名。

    Returns:
        文本或 `None`。

    Raises:
        ValueError: 字段存在但不是文本时抛出。
    """

    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"score.json correctness.{key} 必须是字符串")
    return value


def _optional_correctness_int(row: Mapping[str, object], key: str) -> int | None:
    """读取 correctness 汇总中的可选整数。

    Args:
        row: correctness 汇总。
        key: 字段名。

    Returns:
        整数或 `None`。

    Raises:
        ValueError: 字段存在但不是整数时抛出。
    """

    value = row.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"score.json correctness.{key} 必须是整数")
    return value


def _optional_correctness_text_list(row: Mapping[str, object], key: str) -> tuple[str, ...]:
    """读取 correctness 汇总中的可选文本列表。

    Args:
        row: correctness 汇总。
        key: 字段名。

    Returns:
        文本元组；缺失时返回空元组。

    Raises:
        ValueError: 字段存在但不是字符串数组时抛出。
    """

    value = row.get(key)
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"score.json correctness.{key} 必须是字符串数组")
    return tuple(value)


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
        "rule_results": [asdict(rule_result) for rule_result in result.rule_results],
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
        f"- rule_result_count: {len(result.rule_results)}",
        "",
        "## Issues",
        "",
        "| rule | severity | fund_code | field | priority | coverage | traceability | observed | threshold | app_category | fund_type | lens | expected | actual | error_type | message |",
        "|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|",
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
            f"{_format_rate(issue.observed_rate)} | "
            f"{_format_rate(issue.threshold)} | "
            f"{_escape_markdown_cell(issue.app_category or '')} | "
            f"{_escape_markdown_cell(issue.classified_fund_type or '')} | "
            f"{_escape_markdown_cell(issue.preferred_lens_key or '')} | "
            f"{_escape_markdown_cell(issue.expected_value or '')} | "
            f"{_escape_markdown_cell(issue.actual_value or '')} | "
            f"{_escape_markdown_cell(issue.error_type or '')} | "
            f"{_escape_markdown_cell(_issue_message_with_reason(issue))} |"
        )
    lines.extend(
        [
            "",
            "## Rule Results",
            "",
            "| rule | severity | fund_code | status | app_category | fund_type | lens | message |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for rule_result in result.rule_results:
        lines.append(
            "| "
            f"{rule_result.rule_code} | "
            f"{rule_result.severity} | "
            f"{rule_result.fund_code or ''} | "
            f"{rule_result.status} | "
            f"{_escape_markdown_cell(rule_result.app_category or '')} | "
            f"{_escape_markdown_cell(rule_result.classified_fund_type or '')} | "
            f"{_escape_markdown_cell(rule_result.preferred_lens_key or '')} | "
            f"{_escape_markdown_cell(rule_result.message)} |"
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


def _issue_message_with_reason(issue: QualityGateIssue) -> str:
    """把 issue 消息与机器原因合并为 Markdown 单元格。

    Args:
        issue: quality gate issue。

    Returns:
        Markdown 表格中展示的消息。

    Raises:
        无显式抛出。
    """

    if issue.reason is None:
        return issue.message
    return f"{issue.message} reason={issue.reason}; coverage_scope={issue.coverage_scope or ''}"


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
