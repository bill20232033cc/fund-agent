"""精选基金池字段级抽取评分与 correctness 比对能力。

本模块位于 Capability 层，负责 P4-S2 前半段质量基线：
只消费 P4-S1 `snapshot.jsonl` 字段级记录，计算 coverage / traceability，
并从精选基金池 CSV 中选择最小 golden set。P4-R10 起额外消费 strict
golden answer JSON，对 snapshot 明确暴露的可比字段执行 correctness 比对。
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, Mapping, Sequence

from fund_agent.fund.extraction_snapshot import (
    DEFAULT_SELECTED_FUNDS_CSV,
    SNAPSHOT_FIELD_ORDER,
    SelectedFundRecord,
    load_selected_funds,
    validate_selected_fund_pool,
)
from fund_agent.fund.golden_answer import (
    GoldenAnswerFund,
    GoldenAnswerRecord,
    load_golden_answer_json,
)

FIELD_PRIORITY_BY_NAME: Final[dict[str, str]] = {
    "basic_identity": "P0",
    "classified_fund_type": "P0",
    "benchmark": "P0",
    "nav_benchmark_performance": "P0",
    "fee_schedule": "P0",
    "manager_strategy_text": "P0",
    "product_profile": "P1",
    "turnover_rate": "P1",
    "holder_structure": "P1",
    "manager_alignment": "P1",
    "holdings_snapshot": "P1",
    "share_change": "P1",
    "investor_return": "P2",
    "nav_data": "P2",
}
UNKNOWN_FIELD_PRIORITY: Final[str] = "UNMAPPED"
STATUS_PASS: Final[str] = "pass"
STATUS_WATCH: Final[str] = "watch"
STATUS_FAIL: Final[str] = "fail"
PASS_COVERAGE_THRESHOLD: Final[float] = 0.90
PASS_TRACEABILITY_THRESHOLD: Final[float] = 0.90
WATCH_COVERAGE_THRESHOLD: Final[float] = 0.70
WATCH_TRACEABILITY_THRESHOLD: Final[float] = 0.70
MANDATORY_GOLDEN_CODE: Final[str] = "004393"
DOMESTIC_STOCK_CATEGORY: Final[str] = "国内股票类"
MONEY_MARKET_CATEGORY: Final[str] = "货币基金类"
EXCLUDED_GOLDEN_CATEGORIES: Final[tuple[str, ...]] = (MONEY_MARKET_CATEGORY,)
REQUIRED_GOLDEN_CATEGORIES: Final[tuple[str, ...]] = (
    "黄金类",
    "海外股票类",
    "海外债券/稳健类",
    "国内债券类",
)
GOLDEN_OUTPUT_FILENAME: Final[str] = "golden_set.json"
SCORE_JSON_FILENAME: Final[str] = "score.json"
SCORE_MARKDOWN_FILENAME: Final[str] = "score.md"
CORRECTNESS_STATUS_AVAILABLE: Final[str] = "available"
CORRECTNESS_STATUS_UNAVAILABLE: Final[str] = "unavailable"
CORRECTNESS_MATCH: Final[str] = "match"
CORRECTNESS_MISMATCH: Final[str] = "mismatch"
CORRECTNESS_UNAVAILABLE: Final[str] = "unavailable"
CLASSIFIED_FUND_TYPE_FIELD: Final[str] = "classified_fund_type"
CLASSIFIED_FUND_TYPE_SUB_FIELD: Final[str] = "fund_type"


@dataclass(frozen=True, slots=True)
class ScoreThresholds:
    """字段级评分阈值。

    Attributes:
        pass_coverage: coverage 达到 pass 的阈值。
        pass_traceability: traceability 达到 pass 的阈值。
        watch_coverage: coverage 达到 watch 的阈值。
        watch_traceability: traceability 达到 watch 的阈值。
    """

    pass_coverage: float = PASS_COVERAGE_THRESHOLD
    pass_traceability: float = PASS_TRACEABILITY_THRESHOLD
    watch_coverage: float = WATCH_COVERAGE_THRESHOLD
    watch_traceability: float = WATCH_TRACEABILITY_THRESHOLD


@dataclass(frozen=True, slots=True)
class FieldScoreRow:
    """单个字段的 coverage / traceability 评分行。

    Attributes:
        field_group: P4-S1 snapshot 字段组。
        field_name: P4-S1 snapshot 字段名。
        priority: P4-S2 字段优先级。
        records: 参与评分的记录数。
        covered_records: `value_present=True` 的记录数。
        traceable_records: `anchor_present=True` 的记录数。
        coverage_rate: covered_records / records。
        traceability_rate: traceable_records / records。
        status: `pass / watch / fail`。
    """

    field_group: str
    field_name: str
    priority: str
    records: int
    covered_records: int
    traceable_records: int
    coverage_rate: float
    traceability_rate: float
    status: str


@dataclass(frozen=True, slots=True)
class FundScoreRow:
    """单只基金的抽取质量汇总行。

    Attributes:
        fund_code: 基金代码。
        fund_name: snapshot 中的基金名称。
        app_category: App 类别。
        records: 参与该基金评分的 snapshot 记录数。
        p0_status: 该基金 P0 字段聚合状态。
        p1_status: 该基金 P1 字段聚合状态。
        status: 该基金整体状态，优先反映 P0/P1 阻断风险。
        p0_failed_fields: 该基金 fail 的 P0 字段名。
        p1_failed_fields: 该基金 fail 的 P1 字段名。
    """

    fund_code: str
    fund_name: str | None
    app_category: str | None
    records: int
    p0_status: str
    p1_status: str
    status: str
    p0_failed_fields: tuple[str, ...]
    p1_failed_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CorrectnessRecordResult:
    """单条 golden answer correctness 比对结果。

    Attributes:
        fund_code: 基金代码。
        field_name: golden answer 字段名。
        sub_field: golden answer 子字段。
        status: `match / mismatch / unavailable`。
        expected_value: 人工审核真值。
        actual_value: snapshot 明确暴露的可比值；不可比时为空。
        normalized_expected: 保守 normalize 后的期望值。
        normalized_actual: 保守 normalize 后的实际值。
        reason: 状态说明。
        confidence: golden answer 置信度。
        source: golden answer 来源。
    """

    fund_code: str
    field_name: str
    sub_field: str
    status: str
    expected_value: str
    actual_value: str | None
    normalized_expected: str
    normalized_actual: str | None
    reason: str
    confidence: str
    source: str


@dataclass(frozen=True, slots=True)
class CorrectnessSummary:
    """correctness 自动比对汇总。

    Attributes:
        status: `available / unavailable`。
        golden_answer_path: strict golden answer JSON 路径；未提供时为空。
        total_records: golden answer 有效记录数，不包含 skipped fields。
        comparable_records: 可直接比对记录数，作为 correctness 分母。
        matched_records: 匹配记录数。
        mismatched_records: 明确冲突记录数。
        unavailable_records: golden 有效但 snapshot 未暴露可比值的记录数。
        skipped_records: golden 中明确 skipped 的记录数。
        accuracy_rate: matched_records / comparable_records。
        reason: 汇总说明。
        record_results: 字段级 correctness 明细。
    """

    status: str
    golden_answer_path: str | None
    total_records: int
    comparable_records: int
    matched_records: int
    mismatched_records: int
    unavailable_records: int
    skipped_records: int
    accuracy_rate: float | None
    reason: str
    record_results: tuple[CorrectnessRecordResult, ...]


@dataclass(frozen=True, slots=True)
class GoldenSetRecord:
    """最小 golden set 中的一只基金。

    Attributes:
        line_number: CSV 原始行号。
        fund_name: 基金名称。
        fund_code: 基金代码。
        app_category: App 类别。
        selection_reason: 入选原因。
    """

    line_number: int
    fund_name: str
    fund_code: str
    app_category: str
    selection_reason: str


@dataclass(frozen=True, slots=True)
class GoldenSetSelection:
    """最小 golden set 选择结果。

    Attributes:
        source_csv: CSV 路径文本。
        records: 入选基金记录。
        excluded_categories: 本 slice 明确排除的类别。
        exclusion_reason: 排除原因。
    """

    source_csv: str
    records: tuple[GoldenSetRecord, ...]
    excluded_categories: tuple[str, ...]
    exclusion_reason: str


@dataclass(frozen=True, slots=True)
class ExtractionScoreResult:
    """字段级评分运行结果。

    Attributes:
        snapshot_path: 输入 snapshot JSONL 路径。
        source_csv: 精选基金池 CSV 路径。
        output_dir: 输出目录。
        score_json_path: 结构化评分 JSON 路径。
        score_markdown_path: Markdown 汇总路径。
        golden_set_path: 最小 golden set JSON 路径。
        field_scores: 字段级评分行。
        fund_scores: 单只基金质量汇总行。
        golden_set: 最小 golden set 选择结果。
        thresholds: 本次评分阈值。
        correctness: strict golden answer correctness 比对汇总。
    """

    snapshot_path: Path
    source_csv: Path
    output_dir: Path
    score_json_path: Path
    score_markdown_path: Path
    golden_set_path: Path
    field_scores: tuple[FieldScoreRow, ...]
    fund_scores: tuple[FundScoreRow, ...]
    golden_set: GoldenSetSelection
    thresholds: ScoreThresholds
    correctness: CorrectnessSummary


@dataclass(slots=True)
class _FieldScoreCounter:
    """字段级评分内部计数器。"""

    field_group: str
    field_name: str
    records: int = 0
    covered_records: int = 0
    traceable_records: int = 0


def load_snapshot_records(snapshot_path: Path) -> list[dict[str, object]]:
    """读取 P4-S1 snapshot JSONL 记录。

    Args:
        snapshot_path: P4-S1 输出的 `snapshot.jsonl` 路径。

    Returns:
        JSON 对象记录列表；空行会被忽略。

    Raises:
        FileNotFoundError: snapshot 文件不存在时抛出。
        ValueError: JSONL 行不是对象时抛出。
        json.JSONDecodeError: JSONL 行内容非法时抛出。
    """

    records: list[dict[str, object]] = []
    with snapshot_path.open(encoding="utf-8") as file_obj:
        for line_number, line in enumerate(file_obj, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"snapshot 第 {line_number} 行不是 JSON object")
            records.append(payload)
    return records


def score_snapshot_records(
    records: Sequence[Mapping[str, object]],
    *,
    thresholds: ScoreThresholds = ScoreThresholds(),
) -> tuple[FieldScoreRow, ...]:
    """从字段级 snapshot 记录计算 coverage / traceability。

    Args:
        records: P4-S1 `snapshot.jsonl` 解析后的字段级记录。
        thresholds: 显式评分阈值。

    Returns:
        字段级评分行，优先按当前 snapshot 字段顺序输出，额外字段排在末尾。

    Raises:
        ValueError: 阈值非法或记录缺少 `field_name` / `field_group` 时抛出。
    """

    _validate_thresholds(thresholds)
    counters: dict[tuple[str, str], _FieldScoreCounter] = {}
    for record in records:
        field_group = _required_text(record, "field_group")
        field_name = _required_text(record, "field_name")
        key = (field_group, field_name)
        counter = counters.setdefault(
            key,
            _FieldScoreCounter(field_group=field_group, field_name=field_name),
        )
        counter.records += 1
        if _truthy_bool(record.get("value_present")):
            counter.covered_records += 1
        if _truthy_bool(record.get("anchor_present")):
            counter.traceable_records += 1

    return tuple(
        _build_score_row(counter, thresholds=thresholds) for counter in _ordered_counters(counters)
    )


def score_fund_records(
    records: Sequence[Mapping[str, object]],
    *,
    thresholds: ScoreThresholds = ScoreThresholds(),
) -> tuple[FundScoreRow, ...]:
    """从 snapshot 记录计算单只基金质量汇总。

    Args:
        records: P4-S1 `snapshot.jsonl` 解析后的字段级记录。
        thresholds: 显式评分阈值。

    Returns:
        按基金代码排序的单基金质量汇总行。

    Raises:
        ValueError: 阈值非法或记录缺少 `fund_code` / `field_name` / `field_group` 时抛出。
    """

    _validate_thresholds(thresholds)
    records_by_fund: dict[str, list[Mapping[str, object]]] = {}
    for record in records:
        fund_code = _required_text(record, "fund_code")
        records_by_fund.setdefault(fund_code, []).append(record)
    return tuple(
        _build_fund_score_row(fund_code, fund_records, thresholds=thresholds)
        for fund_code, fund_records in sorted(records_by_fund.items())
    )


def select_minimal_golden_set(source_csv: Path = DEFAULT_SELECTED_FUNDS_CSV) -> GoldenSetSelection:
    """从精选基金池 CSV 选择 P4-S2 最小 golden set。

    Args:
        source_csv: 精选基金池 CSV 路径，只允许选择文件中真实存在的基金代码。

    Returns:
        最小 golden set 选择结果，固定包含 `004393`，并覆盖黄金、海外股票、
        海外债券/稳健、国内债券和额外一只国内股票。

    Raises:
        FileNotFoundError: CSV 文件不存在时抛出。
        ValueError: CSV 输入非法、必需类别缺失或 `004393` 缺失时抛出。
    """

    funds = load_selected_funds(source_csv)
    validation = validate_selected_fund_pool(funds)
    if validation.has_blocking_errors:
        raise ValueError("精选基金池 CSV 存在阻断错误，不能选择 golden set")

    selected: list[GoldenSetRecord] = []
    selected_codes: set[str] = set()
    mandatory_fund = _find_fund_by_code(funds, MANDATORY_GOLDEN_CODE)
    _append_golden_record(
        selected=selected,
        selected_codes=selected_codes,
        fund=mandatory_fund,
        reason="mandatory_known_failure_domestic_stock",
    )
    for category in REQUIRED_GOLDEN_CATEGORIES:
        fund = _first_fund_by_category(funds, category, selected_codes=selected_codes)
        _append_golden_record(
            selected=selected,
            selected_codes=selected_codes,
            fund=fund,
            reason=f"required_category:{category}",
        )

    domestic_fund = _first_fund_by_category(
        funds,
        DOMESTIC_STOCK_CATEGORY,
        selected_codes=selected_codes,
    )
    _append_golden_record(
        selected=selected,
        selected_codes=selected_codes,
        fund=domestic_fund,
        reason="additional_domestic_stock",
    )

    return GoldenSetSelection(
        source_csv=str(source_csv),
        records=tuple(selected),
        excluded_categories=EXCLUDED_GOLDEN_CATEGORIES,
        exclusion_reason="P4-S2 前半段先排除货币基金类；当前 8 章模板对货币基金适配度较低，作为 edge case 记录。",
    )


def run_extraction_score(
    *,
    snapshot_path: Path,
    source_csv: Path = DEFAULT_SELECTED_FUNDS_CSV,
    output_dir: Path | None = None,
    thresholds: ScoreThresholds = ScoreThresholds(),
    golden_answer_path: Path | None = None,
) -> ExtractionScoreResult:
    """读取 snapshot 并输出 P4-S2 字段级评分产物。

    Args:
        snapshot_path: P4-S1 输出的 `snapshot.jsonl`。
        source_csv: 精选基金池 CSV，用于选择最小 golden set。
        output_dir: 显式输出目录；为空时使用 snapshot 所在目录。
        thresholds: 显式评分阈值。
        golden_answer_path: strict golden answer JSON 路径；为空时不执行 correctness。

    Returns:
        评分运行结果和输出路径。

    Raises:
        FileNotFoundError: snapshot 或 CSV 不存在时抛出。
        ValueError: snapshot schema、阈值或 CSV 输入非法时抛出。
        OSError: 输出目录或文件写入失败时抛出。
    """

    records = load_snapshot_records(snapshot_path)
    field_scores = score_snapshot_records(records, thresholds=thresholds)
    fund_scores = score_fund_records(records, thresholds=thresholds)
    golden_set = select_minimal_golden_set(source_csv)
    correctness = compare_snapshot_correctness(
        records=records,
        golden_answer_path=golden_answer_path,
    )
    resolved_output_dir = output_dir or snapshot_path.parent
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    score_json_path = resolved_output_dir / SCORE_JSON_FILENAME
    score_markdown_path = resolved_output_dir / SCORE_MARKDOWN_FILENAME
    golden_set_path = resolved_output_dir / GOLDEN_OUTPUT_FILENAME
    result = ExtractionScoreResult(
        snapshot_path=snapshot_path,
        source_csv=source_csv,
        output_dir=resolved_output_dir,
        score_json_path=score_json_path,
        score_markdown_path=score_markdown_path,
        golden_set_path=golden_set_path,
        field_scores=field_scores,
        fund_scores=fund_scores,
        golden_set=golden_set,
        thresholds=thresholds,
        correctness=correctness,
    )
    score_json_path.write_text(
        json.dumps(_score_json_payload(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    score_markdown_path.write_text(_score_markdown(result), encoding="utf-8")
    golden_set_path.write_text(
        json.dumps(asdict(golden_set), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def compare_snapshot_correctness(
    *,
    records: Sequence[Mapping[str, object]],
    golden_answer_path: Path | None,
) -> CorrectnessSummary:
    """用 strict golden answer JSON 对 snapshot 明确字段做 correctness 比对。

    当前 P4-R10 最小闭环只比较 snapshot 直接暴露的 `classified_fund_type.fund_type`。
    其他 golden 有效记录标记为 `unavailable`，不进入 correctness 分母；skipped
    golden 字段只计入 skipped 数，不进入分母。见模板第 1 章产品本质的基金类型识别约束。

    Args:
        records: P4-S1 `snapshot.jsonl` 解析后的字段级记录。
        golden_answer_path: strict golden answer JSON 路径；为空时返回 unavailable。

    Returns:
        correctness 汇总。

    Raises:
        FileNotFoundError: golden answer JSON 路径存在但文件不存在时抛出。
        GoldenAnswerValidationError: strict JSON 不合法时由 loader 抛出。
        json.JSONDecodeError: strict JSON 非法时由 loader 抛出。
        ValueError: snapshot 记录缺少必要字段时抛出。
    """

    if golden_answer_path is None:
        return CorrectnessSummary(
            status=CORRECTNESS_STATUS_UNAVAILABLE,
            golden_answer_path=None,
            total_records=0,
            comparable_records=0,
            matched_records=0,
            mismatched_records=0,
            unavailable_records=0,
            skipped_records=0,
            accuracy_rate=None,
            reason="未提供 strict golden answer JSON；correctness 未接入。",
            record_results=(),
        )
    golden_funds = load_golden_answer_json(golden_answer_path)
    actual_index = _snapshot_actual_index(records)
    record_results = _compare_golden_funds(golden_funds, actual_index)
    comparable = [
        row for row in record_results if row.status in {CORRECTNESS_MATCH, CORRECTNESS_MISMATCH}
    ]
    matched_records = sum(1 for row in comparable if row.status == CORRECTNESS_MATCH)
    mismatched_records = sum(1 for row in comparable if row.status == CORRECTNESS_MISMATCH)
    unavailable_records = sum(1 for row in record_results if row.status == CORRECTNESS_UNAVAILABLE)
    skipped_records = sum(len(fund.skipped_fields) for fund in golden_funds)
    return CorrectnessSummary(
        status=CORRECTNESS_STATUS_AVAILABLE,
        golden_answer_path=str(golden_answer_path),
        total_records=sum(len(fund.records) for fund in golden_funds),
        comparable_records=len(comparable),
        matched_records=matched_records,
        mismatched_records=mismatched_records,
        unavailable_records=unavailable_records,
        skipped_records=skipped_records,
        accuracy_rate=_optional_rate(matched_records, len(comparable)),
        reason="仅对 snapshot 显式暴露的可比字段做保守 normalize 后比对；不可比字段不进入分母。",
        record_results=tuple(record_results),
    )


def _validate_thresholds(thresholds: ScoreThresholds) -> None:
    """校验评分阈值。

    Args:
        thresholds: 字段级评分阈值。

    Returns:
        无返回值。

    Raises:
        ValueError: 阈值不在 0 到 1 之间，或 watch 高于 pass 时抛出。
    """

    values = (
        thresholds.pass_coverage,
        thresholds.pass_traceability,
        thresholds.watch_coverage,
        thresholds.watch_traceability,
    )
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("评分阈值必须位于 0 到 1 之间")
    if thresholds.watch_coverage > thresholds.pass_coverage:
        raise ValueError("watch coverage 阈值不能高于 pass coverage 阈值")
    if thresholds.watch_traceability > thresholds.pass_traceability:
        raise ValueError("watch traceability 阈值不能高于 pass traceability 阈值")


def _required_text(record: Mapping[str, object], key: str) -> str:
    """读取 snapshot 记录中的必需文本字段。

    Args:
        record: 单条 snapshot 记录。
        key: 字段名。

    Returns:
        去空格后的文本值。

    Raises:
        ValueError: 字段缺失或为空时抛出。
    """

    value = record.get(key)
    if value is None:
        raise ValueError(f"snapshot 记录缺少字段：{key}")
    text = str(value).strip()
    if not text:
        raise ValueError(f"snapshot 记录字段不能为空：{key}")
    return text


def _truthy_bool(value: object) -> bool:
    """把 snapshot 布尔字段转换为布尔值。

    Args:
        value: JSON 解析后的字段值。

    Returns:
        仅 `True` 或文本 `true` 视为真。

    Raises:
        无显式抛出。
    """

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _ordered_counters(
    counters: Mapping[tuple[str, str], _FieldScoreCounter],
) -> list[_FieldScoreCounter]:
    """按当前 snapshot 字段顺序排列评分计数器。

    Args:
        counters: `(field_group, field_name)` 到计数器的映射。

    Returns:
        排序后的计数器列表。

    Raises:
        无显式抛出。
    """

    ordered_keys = list(SNAPSHOT_FIELD_ORDER)
    known_keys = set(ordered_keys)
    ordered = [counters[key] for key in ordered_keys if key in counters]
    extra_keys = sorted(key for key in counters if key not in known_keys)
    ordered.extend(counters[key] for key in extra_keys)
    return ordered


def _build_score_row(counter: _FieldScoreCounter, *, thresholds: ScoreThresholds) -> FieldScoreRow:
    """把字段计数器转换为评分行。

    Args:
        counter: 字段级计数器。
        thresholds: 显式评分阈值。

    Returns:
        字段评分行。

    Raises:
        无显式抛出。
    """

    coverage_rate = _rate(counter.covered_records, counter.records)
    traceability_rate = _rate(counter.traceable_records, counter.records)
    return FieldScoreRow(
        field_group=counter.field_group,
        field_name=counter.field_name,
        priority=FIELD_PRIORITY_BY_NAME.get(counter.field_name, UNKNOWN_FIELD_PRIORITY),
        records=counter.records,
        covered_records=counter.covered_records,
        traceable_records=counter.traceable_records,
        coverage_rate=coverage_rate,
        traceability_rate=traceability_rate,
        status=_score_status(coverage_rate, traceability_rate, thresholds=thresholds),
    )


def _build_fund_score_row(
    fund_code: str,
    records: Sequence[Mapping[str, object]],
    *,
    thresholds: ScoreThresholds,
) -> FundScoreRow:
    """构造单只基金的抽取质量汇总行。

    Args:
        fund_code: 基金代码。
        records: 该基金对应的 snapshot 记录。
        thresholds: 显式评分阈值。

    Returns:
        单基金质量汇总。

    Raises:
        ValueError: snapshot 记录缺少字段名或字段组时抛出。
    """

    field_scores = _score_records_for_single_fund(records, thresholds=thresholds)
    p0_failed_fields = tuple(
        row.field_name for row in field_scores if row.priority == "P0" and row.status == STATUS_FAIL
    )
    p1_failed_fields = tuple(
        row.field_name for row in field_scores if row.priority == "P1" and row.status == STATUS_FAIL
    )
    p0_rows = [row for row in field_scores if row.priority == "P0"]
    p1_rows = [row for row in field_scores if row.priority == "P1"]
    p0_status = _aggregate_status(p0_rows)
    p1_status = _aggregate_status(p1_rows)
    return FundScoreRow(
        fund_code=fund_code,
        fund_name=_first_optional_text(records, "fund_name"),
        app_category=_first_optional_text(records, "app_category"),
        records=len(records),
        p0_status=p0_status,
        p1_status=p1_status,
        status=_aggregate_status((*p0_rows, *p1_rows)),
        p0_failed_fields=p0_failed_fields,
        p1_failed_fields=p1_failed_fields,
    )


def _score_records_for_single_fund(
    records: Sequence[Mapping[str, object]],
    *,
    thresholds: ScoreThresholds,
) -> tuple[FieldScoreRow, ...]:
    """计算单只基金内部的字段级评分。

    Args:
        records: 单只基金的 snapshot 记录。
        thresholds: 显式评分阈值。

    Returns:
        字段级评分行。

    Raises:
        ValueError: 记录缺少 `field_name` / `field_group` 时抛出。
    """

    counters: dict[tuple[str, str], _FieldScoreCounter] = {}
    for record in records:
        field_group = _required_text(record, "field_group")
        field_name = _required_text(record, "field_name")
        key = (field_group, field_name)
        counter = counters.setdefault(
            key,
            _FieldScoreCounter(field_group=field_group, field_name=field_name),
        )
        counter.records += 1
        if _truthy_bool(record.get("value_present")):
            counter.covered_records += 1
        if _truthy_bool(record.get("anchor_present")):
            counter.traceable_records += 1
    return tuple(
        _build_score_row(counter, thresholds=thresholds) for counter in _ordered_counters(counters)
    )


def _first_optional_text(records: Sequence[Mapping[str, object]], key: str) -> str | None:
    """读取记录集合中的第一个非空文本。

    Args:
        records: snapshot 记录集合。
        key: 字段名。

    Returns:
        第一个非空文本；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for record in records:
        value = record.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _rate(numerator: int, denominator: int) -> float:
    """计算比例。

    Args:
        numerator: 分子。
        denominator: 分母。

    Returns:
        分母为 0 时返回 0，否则返回 `numerator / denominator`。

    Raises:
        无显式抛出。
    """

    if denominator == 0:
        return 0.0
    return numerator / denominator


def _optional_rate(numerator: int, denominator: int) -> float | None:
    """计算可为空比例。

    Args:
        numerator: 分子。
        denominator: 分母。

    Returns:
        分母为 0 时返回 `None`，否则返回 `numerator / denominator`。

    Raises:
        无显式抛出。
    """

    if denominator == 0:
        return None
    return numerator / denominator


def _snapshot_actual_index(
    records: Sequence[Mapping[str, object]],
) -> dict[tuple[str, str, str], str | None]:
    """构造 snapshot 可比字段索引。

    Args:
        records: P4-S1 snapshot 记录。

    Returns:
        `(fund_code, field_name, sub_field)` 到实际值的索引；值为 `None` 表示字段明确缺失。

    Raises:
        ValueError: snapshot 记录缺少 `fund_code` 或 `field_name` 时抛出。
    """

    actual_index: dict[tuple[str, str, str], str | None] = {}
    for record in records:
        fund_code = _required_text(record, "fund_code")
        field_name = _required_text(record, "field_name")
        if field_name != CLASSIFIED_FUND_TYPE_FIELD:
            continue
        actual_value = _optional_record_text(record, CLASSIFIED_FUND_TYPE_FIELD)
        if not _truthy_bool(record.get("value_present")):
            actual_value = None
        actual_index[(fund_code, CLASSIFIED_FUND_TYPE_FIELD, CLASSIFIED_FUND_TYPE_SUB_FIELD)] = (
            actual_value
        )
    return actual_index


def _compare_golden_funds(
    golden_funds: Sequence[GoldenAnswerFund],
    actual_index: Mapping[tuple[str, str, str], str | None],
) -> list[CorrectnessRecordResult]:
    """对 golden answer 基金集合执行字段级 correctness 比对。

    Args:
        golden_funds: strict golden answer 基金集合。
        actual_index: snapshot 可比字段索引。

    Returns:
        correctness 明细列表。

    Raises:
        无显式抛出。
    """

    results: list[CorrectnessRecordResult] = []
    for fund in golden_funds:
        for record in fund.records:
            results.append(_compare_golden_record(record, actual_index))
    return results


def _compare_golden_record(
    record: GoldenAnswerRecord,
    actual_index: Mapping[tuple[str, str, str], str | None],
) -> CorrectnessRecordResult:
    """对单条 golden answer 记录执行 correctness 比对。

    Args:
        record: `GoldenAnswerRecord` 对象。
        actual_index: snapshot 可比字段索引。

    Returns:
        单条 correctness 结果。

    Raises:
        无显式抛出。
    """

    fund_code = record.fund_code
    field_name = record.field_name
    sub_field = record.sub_field
    expected_value = record.expected_value
    confidence = record.confidence
    source = record.source
    normalized_expected = _normalize_comparable_value(expected_value)
    key = (fund_code, field_name, sub_field)
    if key not in actual_index:
        return CorrectnessRecordResult(
            fund_code=fund_code,
            field_name=field_name,
            sub_field=sub_field,
            status=CORRECTNESS_UNAVAILABLE,
            expected_value=expected_value,
            actual_value=None,
            normalized_expected=normalized_expected,
            normalized_actual=None,
            reason="snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。",
            confidence=confidence,
            source=source,
        )
    actual_value = actual_index[key]
    if actual_value is None:
        return CorrectnessRecordResult(
            fund_code=fund_code,
            field_name=field_name,
            sub_field=sub_field,
            status=CORRECTNESS_MISMATCH,
            expected_value=expected_value,
            actual_value=None,
            normalized_expected=normalized_expected,
            normalized_actual=None,
            reason="golden 期望存在该字段，但 snapshot 明确标记为缺失。",
            confidence=confidence,
            source=source,
        )
    normalized_actual = _normalize_comparable_value(actual_value)
    status = CORRECTNESS_MATCH if normalized_actual == normalized_expected else CORRECTNESS_MISMATCH
    reason = (
        "保守 normalize 后完全一致。"
        if status == CORRECTNESS_MATCH
        else "保守 normalize 后不一致。"
    )
    return CorrectnessRecordResult(
        fund_code=fund_code,
        field_name=field_name,
        sub_field=sub_field,
        status=status,
        expected_value=expected_value,
        actual_value=actual_value,
        normalized_expected=normalized_expected,
        normalized_actual=normalized_actual,
        reason=reason,
        confidence=confidence,
        source=source,
    )


def _optional_record_text(record: Mapping[str, object], key: str) -> str | None:
    """读取 snapshot 记录中的可选文本字段。

    Args:
        record: snapshot 记录。
        key: 字段名。

    Returns:
        非空文本；缺失或空白时返回 `None`。

    Raises:
        无显式抛出。
    """

    value = record.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_comparable_value(value: object) -> str:
    """对可比字段执行保守 normalize。

    该函数只做大小写、全角空白和连续空白归一化，不做同义词映射、不补值，
    避免用间接证据或经验推断修正 correctness。

    Args:
        value: 原始值。

    Returns:
        归一化后的文本。

    Raises:
        无显式抛出。
    """

    text = str(value).strip().replace("\u3000", " ")
    return " ".join(text.split()).casefold()


def _score_status(
    coverage_rate: float, traceability_rate: float, *, thresholds: ScoreThresholds
) -> str:
    """根据 coverage / traceability 阈值计算状态。

    Args:
        coverage_rate: 字段 coverage。
        traceability_rate: 字段 traceability。
        thresholds: 显式评分阈值。

    Returns:
        `pass / watch / fail`。

    Raises:
        无显式抛出。
    """

    if (
        coverage_rate >= thresholds.pass_coverage
        and traceability_rate >= thresholds.pass_traceability
    ):
        return STATUS_PASS
    if (
        coverage_rate >= thresholds.watch_coverage
        and traceability_rate >= thresholds.watch_traceability
    ):
        return STATUS_WATCH
    return STATUS_FAIL


def _find_fund_by_code(funds: Sequence[SelectedFundRecord], fund_code: str) -> SelectedFundRecord:
    """按基金代码查找 CSV 基金记录。

    Args:
        funds: CSV 基金记录。
        fund_code: 目标基金代码。

    Returns:
        第一条匹配基金记录。

    Raises:
        ValueError: 代码不存在或属于排除类别时抛出。
    """

    for fund in funds:
        if fund.fund_code != fund_code:
            continue
        if fund.app_category in EXCLUDED_GOLDEN_CATEGORIES:
            raise ValueError(f"基金代码 {fund_code} 属于当前排除类别：{fund.app_category}")
        return fund
    raise ValueError(f"精选基金池缺少必选基金代码：{fund_code}")


def _first_fund_by_category(
    funds: Sequence[SelectedFundRecord],
    category: str,
    *,
    selected_codes: set[str],
) -> SelectedFundRecord:
    """按 CSV 顺序选择某类别第一只未入选基金。

    Args:
        funds: CSV 基金记录。
        category: 目标 App 类别。
        selected_codes: 已入选代码集合。

    Returns:
        第一只符合条件的基金。

    Raises:
        ValueError: 类别缺失或没有未入选代码时抛出。
    """

    for fund in funds:
        if fund.app_category != category:
            continue
        if fund.fund_code in selected_codes:
            continue
        if fund.app_category in EXCLUDED_GOLDEN_CATEGORIES:
            continue
        return fund
    raise ValueError(f"精选基金池缺少可用于 golden set 的类别：{category}")


def _append_golden_record(
    *,
    selected: list[GoldenSetRecord],
    selected_codes: set[str],
    fund: SelectedFundRecord,
    reason: str,
) -> None:
    """追加一条 golden set 记录并去重。

    Args:
        selected: 已选择的 golden set 列表。
        selected_codes: 已选择基金代码集合。
        fund: 待追加基金。
        reason: 入选原因。

    Returns:
        无返回值。

    Raises:
        ValueError: 同一基金代码重复追加时抛出。
    """

    if fund.fund_code in selected_codes:
        raise ValueError(f"golden set 重复选择基金代码：{fund.fund_code}")
    selected.append(
        GoldenSetRecord(
            line_number=fund.line_number,
            fund_name=fund.fund_name,
            fund_code=fund.fund_code,
            app_category=fund.app_category,
            selection_reason=reason,
        )
    )
    selected_codes.add(fund.fund_code)


def _score_json_payload(result: ExtractionScoreResult) -> dict[str, object]:
    """构造 `score.json` 结构化输出。

    Args:
        result: 字段级评分运行结果。

    Returns:
        可 JSON 序列化的评分 payload。

    Raises:
        无显式抛出。
    """

    status_counts = Counter(row.status for row in result.field_scores)
    p0_rows = [row for row in result.field_scores if row.priority == "P0"]
    return {
        "snapshot_path": str(result.snapshot_path),
        "source_csv": str(result.source_csv),
        "thresholds": asdict(result.thresholds),
        "field_count": len(result.field_scores),
        "fund_count": len(result.fund_scores),
        "status_counts": dict(sorted(status_counts.items())),
        "p0_status": _aggregate_status(p0_rows),
        "field_scores": [asdict(row) for row in result.field_scores],
        "fund_scores": [asdict(row) for row in result.fund_scores],
        "golden_set": asdict(result.golden_set),
        "correctness": asdict(result.correctness),
    }


def _aggregate_status(rows: Sequence[FieldScoreRow]) -> str:
    """聚合一组字段的状态。

    Args:
        rows: 字段评分行。

    Returns:
        任一 fail 则返回 fail；否则任一 watch 返回 watch；全 pass 返回 pass；空集合返回 fail。

    Raises:
        无显式抛出。
    """

    if not rows:
        return STATUS_FAIL
    statuses = {row.status for row in rows}
    if STATUS_FAIL in statuses:
        return STATUS_FAIL
    if STATUS_WATCH in statuses:
        return STATUS_WATCH
    return STATUS_PASS


def _score_markdown(result: ExtractionScoreResult) -> str:
    """构造字段级评分 Markdown 汇总。

    Args:
        result: 字段级评分运行结果。

    Returns:
        Markdown 文本。

    Raises:
        无显式抛出。
    """

    status_counts = Counter(row.status for row in result.field_scores)
    lines = [
        "# Extraction Score Summary",
        "",
        f"- snapshot_path: `{result.snapshot_path}`",
        f"- source_csv: `{result.source_csv}`",
        f"- field_count: {len(result.field_scores)}",
        f"- fund_count: {len(result.fund_scores)}",
        f"- p0_status: `{_aggregate_status([row for row in result.field_scores if row.priority == 'P0'])}`",
        f"- thresholds: coverage pass `{result.thresholds.pass_coverage:.0%}` / watch `{result.thresholds.watch_coverage:.0%}`, traceability pass `{result.thresholds.pass_traceability:.0%}` / watch `{result.thresholds.watch_traceability:.0%}`",
        f"- correctness: `{result.correctness.status}`",
        f"- correctness_comparable_records: {result.correctness.comparable_records}",
        f"- correctness_mismatched_records: {result.correctness.mismatched_records}",
        "",
        "## Status Counts",
        "",
        "| status | fields |",
        "|---|---:|",
    ]
    for status in (STATUS_PASS, STATUS_WATCH, STATUS_FAIL):
        lines.append(f"| {status} | {status_counts.get(status, 0)} |")

    lines.extend(
        [
            "",
            "## Correctness",
            "",
            f"- golden_answer_path: `{result.correctness.golden_answer_path or ''}`",
            f"- total_records: {result.correctness.total_records}",
            f"- comparable_records: {result.correctness.comparable_records}",
            f"- matched_records: {result.correctness.matched_records}",
            f"- mismatched_records: {result.correctness.mismatched_records}",
            f"- unavailable_records: {result.correctness.unavailable_records}",
            f"- skipped_records: {result.correctness.skipped_records}",
            f"- accuracy_rate: `{_format_optional_rate(result.correctness.accuracy_rate)}`",
            f"- reason: {result.correctness.reason}",
            "",
            "| fund_code | field | sub_field | status | expected | actual | reason |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in result.correctness.record_results:
        lines.append(
            "| "
            f"{row.fund_code} | "
            f"{row.field_name} | "
            f"{row.sub_field} | "
            f"{row.status} | "
            f"{_escape_markdown_cell(row.expected_value)} | "
            f"{_escape_markdown_cell(row.actual_value or '')} | "
            f"{_escape_markdown_cell(row.reason)} |"
        )

    lines.extend(
        [
            "",
            "## Fund Scores",
            "",
            "| fund_code | fund_name | app_category | records | p0_status | p1_status | status | p0_failed_fields | p1_failed_fields |",
            "|---|---|---|---:|---|---|---|---|---|",
        ]
    )
    for row in result.fund_scores:
        lines.append(
            "| "
            f"{row.fund_code} | "
            f"{row.fund_name or ''} | "
            f"{row.app_category or ''} | "
            f"{row.records} | "
            f"{row.p0_status} | "
            f"{row.p1_status} | "
            f"{row.status} | "
            f"{', '.join(row.p0_failed_fields)} | "
            f"{', '.join(row.p1_failed_fields)} |"
        )

    lines.extend(
        [
            "",
            "## Field Scores",
            "",
            "| field_group | field_name | priority | records | coverage_rate | traceability_rate | status |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in result.field_scores:
        lines.append(
            "| "
            f"{row.field_group} | "
            f"{row.field_name} | "
            f"{row.priority} | "
            f"{row.records} | "
            f"{row.coverage_rate:.1%} | "
            f"{row.traceability_rate:.1%} | "
            f"{row.status} |"
        )

    lines.extend(
        [
            "",
            "## Minimal Golden Set",
            "",
            "| fund_code | fund_name | app_category | reason |",
            "|---|---|---|---|",
        ]
    )
    for record in result.golden_set.records:
        lines.append(
            "| "
            f"{record.fund_code} | "
            f"{record.fund_name} | "
            f"{record.app_category} | "
            f"{record.selection_reason} |"
        )
    lines.extend(
        [
            "",
            "## Excluded Categories",
            "",
            f"- {', '.join(result.golden_set.excluded_categories)}",
            f"- reason: {result.golden_set.exclusion_reason}",
        ]
    )
    return "\n".join(lines) + "\n"


def _format_optional_rate(value: float | None) -> str:
    """格式化可为空比率。

    Args:
        value: 比率值。

    Returns:
        一位小数百分比；空值返回 `n/a`。

    Raises:
        无显式抛出。
    """

    if value is None:
        return "n/a"
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
