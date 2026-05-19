"""精选基金池字段级抽取评分能力。

本模块位于 Capability 层，负责 P4-S2 前半段质量基线：
只消费 P4-S1 `snapshot.jsonl` 字段级记录，计算 coverage / traceability，
并从精选基金池 CSV 中选择最小 golden set。当前 slice 不实现 correctness 评分。
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
        golden_set: 最小 golden set 选择结果。
        thresholds: 本次评分阈值。
    """

    snapshot_path: Path
    source_csv: Path
    output_dir: Path
    score_json_path: Path
    score_markdown_path: Path
    golden_set_path: Path
    field_scores: tuple[FieldScoreRow, ...]
    golden_set: GoldenSetSelection
    thresholds: ScoreThresholds


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

    return tuple(_build_score_row(counter, thresholds=thresholds) for counter in _ordered_counters(counters))


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
) -> ExtractionScoreResult:
    """读取 snapshot 并输出 P4-S2 字段级评分产物。

    Args:
        snapshot_path: P4-S1 输出的 `snapshot.jsonl`。
        source_csv: 精选基金池 CSV，用于选择最小 golden set。
        output_dir: 显式输出目录；为空时使用 snapshot 所在目录。
        thresholds: 显式评分阈值。

    Returns:
        评分运行结果和输出路径。

    Raises:
        FileNotFoundError: snapshot 或 CSV 不存在时抛出。
        ValueError: snapshot schema、阈值或 CSV 输入非法时抛出。
        OSError: 输出目录或文件写入失败时抛出。
    """

    records = load_snapshot_records(snapshot_path)
    field_scores = score_snapshot_records(records, thresholds=thresholds)
    golden_set = select_minimal_golden_set(source_csv)
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
        golden_set=golden_set,
        thresholds=thresholds,
    )
    score_json_path.write_text(json.dumps(_score_json_payload(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    score_markdown_path.write_text(_score_markdown(result), encoding="utf-8")
    golden_set_path.write_text(json.dumps(asdict(golden_set), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


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


def _ordered_counters(counters: Mapping[tuple[str, str], _FieldScoreCounter]) -> list[_FieldScoreCounter]:
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


def _score_status(coverage_rate: float, traceability_rate: float, *, thresholds: ScoreThresholds) -> str:
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

    if coverage_rate >= thresholds.pass_coverage and traceability_rate >= thresholds.pass_traceability:
        return STATUS_PASS
    if coverage_rate >= thresholds.watch_coverage and traceability_rate >= thresholds.watch_traceability:
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
        "status_counts": dict(sorted(status_counts.items())),
        "p0_status": _aggregate_status(p0_rows),
        "field_scores": [asdict(row) for row in result.field_scores],
        "golden_set": asdict(result.golden_set),
        "correctness": {
            "status": "not_implemented",
            "reason": "P4-S2 前半段只实现 coverage / traceability；人工 golden answer 留到 P4-S2 后半段。",
        },
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
        f"- p0_status: `{_aggregate_status([row for row in result.field_scores if row.priority == 'P0'])}`",
        f"- thresholds: coverage pass `{result.thresholds.pass_coverage:.0%}` / watch `{result.thresholds.watch_coverage:.0%}`, traceability pass `{result.thresholds.pass_traceability:.0%}` / watch `{result.thresholds.watch_traceability:.0%}`",
        "- correctness: `not_implemented`（P4-S2 后半段再引入人工 golden answer）",
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
