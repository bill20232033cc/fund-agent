"""精选基金池字段级抽取快照能力。

本模块位于 Agent 层基金能力，负责 P4-S1 精选基金池年报抽取质量快照：
读取基金池 CSV、调用 `FundDataExtractor.extract(...)`、将结构化数据包拆成
字段级 `SnapshotRecord`，并输出 JSONL、错误明细和人工可读 summary。
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, Protocol, Sequence

from fund_agent.config.paths import (
    DEFAULT_EXTRACTION_SNAPSHOT_ROOT,
    DEFAULT_SELECTED_FUNDS_CSV as _DEFAULT_SELECTED_FUNDS_CSV,
)
from fund_agent.fund._value_utils import value_mapping
from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.extractors import BondRiskEvidenceValue, EvidenceAnchor, ExtractedField

DEFAULT_SELECTED_FUNDS_CSV: Final[Path] = _DEFAULT_SELECTED_FUNDS_CSV
DEFAULT_SNAPSHOT_OUTPUT_ROOT: Final[Path] = DEFAULT_EXTRACTION_SNAPSHOT_ROOT
REQUIRED_SELECTED_FUND_COLUMNS: Final[tuple[str, ...]] = ("基金名称", "基金代码", "类别")
SNAPSHOT_FIELD_ORDER: Final[tuple[tuple[str, str], ...]] = (
    ("profile", "basic_identity"),
    ("profile", "product_profile"),
    ("profile", "benchmark"),
    ("profile", "index_profile"),
    ("profile", "fee_schedule"),
    ("profile", "classified_fund_type"),
    ("performance", "nav_benchmark_performance"),
    ("performance", "investor_return"),
    ("performance", "tracking_error"),
    ("manager", "manager_strategy_text"),
    ("manager", "turnover_rate"),
    ("manager", "manager_alignment"),
    ("holder", "holder_structure"),
    ("holdings", "holdings_snapshot"),
    ("risk", "bond_risk_evidence"),
    ("share_change", "share_change"),
    ("nav", "nav_data"),
)
COMPARABLE_SUB_FIELDS_BY_FIELD: Final[dict[str, tuple[str, ...]]] = {
    "basic_identity": (
        "fund_name",
        "fund_code",
        "fund_category",
        "management_company",
        "custodian",
        "inception_date",
        "classified_fund_type",
    ),
    "benchmark": ("benchmark_name", "benchmark_text"),
    "index_profile": (
        "benchmark_text",
        "benchmark_identity_status",
        "benchmark_index_name",
        "benchmark_index_code",
        "methodology_availability",
        "constituents_availability",
        "source_tier",
    ),
    "nav_benchmark_performance": ("nav_growth_rate", "benchmark_return_rate"),
    "tracking_error": (
        "value_text",
        "period_label",
        "annualized",
        "source_type",
        "calculation_method",
        "benchmark_identity_status",
        "benchmark_index_name",
        "benchmark_index_code",
        "frequency",
        "input_period_complete",
    ),
    "classified_fund_type": ("fund_type",),
    "holdings_snapshot": ("top_holdings_status", "top_holdings_source"),
}
_EXTRACTION_MODE_DIRECT: Final[str] = "direct"
_EXTRACTION_MODE_MISSING: Final[str] = "missing"
_KNOWN_FAILURE_004393_NOTE: Final[str] = (
    "known_failure:P4-S1 当前记录 004393 被误判为 index_fund 的真实输出，不在本 slice 修正。"
)


class SnapshotExtractor(Protocol):
    """字段级快照依赖的结构化抽取协议。

    Protocol 用于测试注入 fake extractor，生产默认使用 `FundDataExtractor`。
    """

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """抽取结构化基金数据。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新底层仓库和净值缓存。

        Returns:
            结构化基金数据包。

        Raises:
            Exception: 允许底层 extractor 异常向上传播，由 run 级逻辑记录。
        """


@dataclass(frozen=True, slots=True)
class SelectedFundRecord:
    """精选基金池中的单条基金记录。

    Attributes:
        line_number: CSV 原始行号。
        fund_name: 基金名称。
        fund_code: 6 位基金代码。
        app_category: App 中的基金类别。
    """

    line_number: int
    fund_name: str
    fund_code: str
    app_category: str


@dataclass(frozen=True, slots=True)
class SelectedFundPoolValidation:
    """精选基金池校验结果。

    Attributes:
        missing_rows: 基金名称、代码或类别缺失的行号。
        bad_code_rows: 代码不是 6 位数字的行号与原始代码。
        duplicate_codes: 重复出现的基金代码。
    """

    missing_rows: tuple[int, ...]
    bad_code_rows: tuple[tuple[int, str], ...]
    duplicate_codes: tuple[str, ...]

    @property
    def has_blocking_errors(self) -> bool:
        """返回是否存在会阻断抽取的输入错误。

        Args:
            无。

        Returns:
            缺少字段或代码非法时返回 `True`；重复代码只在 summary 标红，不阻断。

        Raises:
            无显式抛出。
        """

        return bool(self.missing_rows or self.bad_code_rows)


@dataclass(frozen=True, slots=True)
class SnapshotRecord:
    """字段级抽取快照记录。

    Attributes:
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: 精选基金池 CSV 路径。
        fund_code: 基金代码。
        fund_name: CSV 中的基金名称。
        app_category: CSV 中的 App 类别。
        report_year: 年报年份。
        classified_fund_type: 系统识别基金类型。
        classification_basis: 类型识别依据。
        field_name: 字段名。
        field_group: 字段组。
        extraction_mode: 抽取模式。
        value_present: 是否存在非空值。
        anchor_present: 是否存在证据锚点。
        section_id: 年报章节。
        page: 页码。
        table_id: 表格 ID。
        row_id: 行级定位。
        comparable_values: correctness 可直接比较的白名单子字段值。
        note: 缺失、降级或异常说明。
        source_provenance_schema_version: 公共来源 provenance schema 版本。
        source_strategy: 公共来源策略标签。
        resolved_source_name: 解析出的公开来源名。
        fallback_used: 是否使用 fallback 来源。
        primary_failure_category: 主来源失败分类；缺失时为 `None`。
        fallback_eligibility: fallback 公开安全分类。
        source_provenance_status: provenance 完整性状态。
        source_provenance_reason: 稳定短原因码。
        bond_risk_contract_status: 债券风险证据契约状态，见模板第 6 章“核心风险”。
        bond_risk_satisfied_groups: 已满足的债券风险证据组。
        bond_risk_missing_groups: 缺失的债券风险证据组。
        bond_risk_weak_groups: 弱证据债券风险证据组。
        bond_risk_ambiguous_groups: 歧义债券风险证据组。
    """

    run_id: str
    extraction_timestamp: str
    source_csv: str
    fund_code: str
    fund_name: str
    app_category: str
    report_year: int
    classified_fund_type: str | None
    classification_basis: tuple[str, ...]
    field_name: str
    field_group: str
    extraction_mode: str
    value_present: bool
    anchor_present: bool
    section_id: str | None
    page: int | None
    table_id: str | None
    row_id: str | None
    comparable_values: dict[str, str]
    note: str | None
    source_provenance_schema_version: str
    source_strategy: str
    resolved_source_name: str | None
    fallback_used: bool
    primary_failure_category: str | None
    fallback_eligibility: str
    source_provenance_status: str
    source_provenance_reason: str
    bond_risk_contract_status: str | None = None
    bond_risk_satisfied_groups: tuple[str, ...] = ()
    bond_risk_missing_groups: tuple[str, ...] = ()
    bond_risk_weak_groups: tuple[str, ...] = ()
    bond_risk_ambiguous_groups: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SnapshotErrorRecord:
    """单只基金抽取失败记录。

    Attributes:
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: 精选基金池 CSV 路径。
        fund_code: 基金代码。
        fund_name: CSV 中的基金名称。
        app_category: CSV 中的 App 类别。
        report_year: 年报年份。
        error_type: 异常类型名。
        error_message: 异常信息。
    """

    run_id: str
    extraction_timestamp: str
    source_csv: str
    fund_code: str
    fund_name: str
    app_category: str
    report_year: int
    error_type: str
    error_message: str


@dataclass(frozen=True, slots=True)
class SnapshotRunResult:
    """抽取快照运行结果。

    Attributes:
        run_id: 本次运行 ID。
        output_dir: 输出目录。
        snapshot_path: 字段快照 JSONL 路径。
        summary_path: 汇总 Markdown 路径。
        errors_path: 错误 JSONL 路径。
        selected_count: 实际请求抽取的基金记录数。
        succeeded_fund_codes: 成功基金代码。
        failed_fund_codes: 失败基金代码。
        record_count: snapshot 记录总数。
        validation: CSV 校验结果。
    """

    run_id: str
    output_dir: Path
    snapshot_path: Path
    summary_path: Path
    errors_path: Path
    selected_count: int
    succeeded_fund_codes: tuple[str, ...]
    failed_fund_codes: tuple[str, ...]
    record_count: int
    validation: SelectedFundPoolValidation


def load_selected_funds(source_csv: Path) -> list[SelectedFundRecord]:
    """读取精选基金池 CSV。

    Args:
        source_csv: CSV 文件路径，需包含“基金名称 / 基金代码 / 类别”三列。

    Returns:
        精选基金记录列表。

    Raises:
        FileNotFoundError: CSV 文件不存在时抛出。
        ValueError: CSV 缺少必需列时抛出。
    """

    with source_csv.open(encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        fieldnames = tuple(reader.fieldnames or ())
        missing_columns = [
            column for column in REQUIRED_SELECTED_FUND_COLUMNS if column not in fieldnames
        ]
        if missing_columns:
            raise ValueError(f"CSV 缺少必需列：{', '.join(missing_columns)}")
        return [
            SelectedFundRecord(
                line_number=line_number,
                fund_name=(row.get("基金名称") or "").strip(),
                fund_code=(row.get("基金代码") or "").strip(),
                app_category=(row.get("类别") or "").strip(),
            )
            for line_number, row in enumerate(reader, start=2)
        ]


def validate_selected_fund_pool(funds: Sequence[SelectedFundRecord]) -> SelectedFundPoolValidation:
    """校验精选基金池输入质量。

    Args:
        funds: 精选基金记录序列。

    Returns:
        校验结果；重复代码只作为质量问题记录，不阻断 P4-S1 快照。

    Raises:
        无显式抛出。
    """

    missing_rows = tuple(
        fund.line_number
        for fund in funds
        if not fund.fund_name or not fund.fund_code or not fund.app_category
    )
    bad_code_rows = tuple(
        (fund.line_number, fund.fund_code)
        for fund in funds
        if not _is_valid_fund_code(fund.fund_code)
    )
    code_counts = Counter(fund.fund_code for fund in funds)
    duplicate_codes = tuple(
        sorted(code for code, count in code_counts.items() if code and count > 1)
    )
    return SelectedFundPoolValidation(
        missing_rows=missing_rows,
        bad_code_rows=bad_code_rows,
        duplicate_codes=duplicate_codes,
    )


def select_snapshot_funds(
    funds: Sequence[SelectedFundRecord],
    *,
    fund_code: str | None,
    sample_per_category: int,
    limit: int | None,
) -> list[SelectedFundRecord]:
    """选择需要生成 snapshot 的基金。

    Args:
        funds: 精选基金池记录。
        fund_code: 显式指定单只基金代码；为空时按类别抽样。
        sample_per_category: 未指定基金代码时每个类别抽样数量。
        limit: 最大返回数量。

    Returns:
        待抽取基金记录列表。

    Raises:
        ValueError: 指定代码不存在，或抽样参数为负数时抛出。
    """

    if sample_per_category < 0:
        raise ValueError("sample_per_category 不能为负数")
    if limit is not None and limit < 0:
        raise ValueError("limit 不能为负数")
    if fund_code:
        selected = [fund for fund in funds if fund.fund_code == fund_code]
        if not selected:
            raise ValueError(f"指定基金代码不在精选基金池中：{fund_code}")
    else:
        selected = _select_by_category(funds, sample_per_category)
    if limit is not None:
        return selected[:limit]
    return selected


async def run_extraction_snapshot(
    *,
    fund_code: str | None,
    report_year: int,
    source_csv: Path,
    run_id: str,
    output_dir: Path | None,
    force_refresh: bool,
    sample_per_category: int = 1,
    limit: int | None = None,
    extractor: SnapshotExtractor | None = None,
) -> SnapshotRunResult:
    """生成精选基金池字段级抽取快照。

    Args:
        fund_code: 指定单只基金代码；为空时按类别抽样。
        report_year: 年报年份。
        source_csv: 精选基金池 CSV 路径。
        run_id: 本次运行 ID。
        output_dir: 显式输出目录；为空时使用 `reports/extraction-snapshots/<run_id>`。
        force_refresh: 是否强制刷新统一仓库和净值缓存。
        sample_per_category: 未指定基金代码时每个类别抽样数量。
        limit: 最大抽取数量。
        extractor: 可注入结构化 extractor；生产默认使用 `FundDataExtractor`。

    Returns:
        本次 snapshot 产物路径和统计结果。

    Raises:
        ValueError: CSV 输入存在阻断错误或选择参数非法时抛出。
        OSError: 输出目录或文件写入失败时抛出。
    """

    funds = load_selected_funds(source_csv)
    validation = validate_selected_fund_pool(funds)
    if validation.has_blocking_errors:
        raise ValueError(_format_blocking_validation_error(validation))

    selected_funds = select_snapshot_funds(
        funds,
        fund_code=fund_code,
        sample_per_category=sample_per_category,
        limit=limit,
    )
    resolved_output_dir = output_dir or DEFAULT_SNAPSHOT_OUTPUT_ROOT / run_id
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = resolved_output_dir / "snapshot.jsonl"
    errors_path = resolved_output_dir / "errors.jsonl"
    summary_path = resolved_output_dir / "summary.md"
    snapshot_path.write_text("", encoding="utf-8")
    errors_path.write_text("", encoding="utf-8")

    active_extractor = extractor or FundDataExtractor()
    extraction_timestamp = _utc_now()
    source_csv_text = _path_for_output(source_csv)
    all_records: list[SnapshotRecord] = []
    error_records: list[SnapshotErrorRecord] = []
    succeeded_codes: list[str] = []
    failed_codes: list[str] = []

    for fund in selected_funds:
        try:
            bundle = await active_extractor.extract(
                fund.fund_code,
                report_year,
                force_refresh=force_refresh,
            )
        except Exception as exc:
            failed_codes.append(fund.fund_code)
            error_record = SnapshotErrorRecord(
                run_id=run_id,
                extraction_timestamp=extraction_timestamp,
                source_csv=source_csv_text,
                fund_code=fund.fund_code,
                fund_name=fund.fund_name,
                app_category=fund.app_category,
                report_year=report_year,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            error_records.append(error_record)
            _append_jsonl(errors_path, asdict(error_record))
            continue

        records = build_snapshot_records(
            bundle=bundle,
            selected_fund=fund,
            run_id=run_id,
            extraction_timestamp=extraction_timestamp,
            source_csv=source_csv_text,
        )
        succeeded_codes.append(fund.fund_code)
        all_records.extend(records)
        for record in records:
            _append_jsonl(snapshot_path, asdict(record))

    write_snapshot_summary(
        summary_path=summary_path,
        run_id=run_id,
        source_csv=source_csv_text,
        report_year=report_year,
        selected_funds=selected_funds,
        records=all_records,
        errors=error_records,
        validation=validation,
    )
    return SnapshotRunResult(
        run_id=run_id,
        output_dir=resolved_output_dir,
        snapshot_path=snapshot_path,
        summary_path=summary_path,
        errors_path=errors_path,
        selected_count=len(selected_funds),
        succeeded_fund_codes=tuple(succeeded_codes),
        failed_fund_codes=tuple(failed_codes),
        record_count=len(all_records),
        validation=validation,
    )


def build_snapshot_records(
    *,
    bundle: StructuredFundDataBundle,
    selected_fund: SelectedFundRecord,
    run_id: str,
    extraction_timestamp: str,
    source_csv: str,
) -> list[SnapshotRecord]:
    """把结构化基金数据包拆为字段级 snapshot 记录。

    Args:
        bundle: `FundDataExtractor.extract(...)` 返回的数据包。
        selected_fund: CSV 中对应基金记录。
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: 输出记录中的 CSV 路径文本。

    Returns:
        字段级 snapshot 记录；P13 新增指数画像和跟踪误差观测字段，但不进入可比值分母。

    Raises:
        无显式抛出。
    """

    classified_fund_type = _extract_classified_fund_type(bundle)
    classification_basis = _extract_classification_basis(bundle)
    records: list[SnapshotRecord] = []
    for field_group, field_name in SNAPSHOT_FIELD_ORDER:
        if field_name == "classified_fund_type":
            records.append(
                _build_classification_record(
                    bundle=bundle,
                    selected_fund=selected_fund,
                    run_id=run_id,
                    extraction_timestamp=extraction_timestamp,
                    source_csv=source_csv,
                    classified_fund_type=classified_fund_type,
                    classification_basis=classification_basis,
                    field_group=field_group,
                    field_name=field_name,
                )
            )
            continue
        if field_name == "nav_data":
            records.append(
                _build_nav_record(
                    bundle=bundle,
                    selected_fund=selected_fund,
                    run_id=run_id,
                    extraction_timestamp=extraction_timestamp,
                    source_csv=source_csv,
                    classified_fund_type=classified_fund_type,
                    classification_basis=classification_basis,
                    field_group=field_group,
                    field_name=field_name,
                )
            )
            continue
        if field_name == "bond_risk_evidence":
            records.append(
                _build_bond_risk_evidence_record(
                    bundle=bundle,
                    selected_fund=selected_fund,
                    run_id=run_id,
                    extraction_timestamp=extraction_timestamp,
                    source_csv=source_csv,
                    classified_fund_type=classified_fund_type,
                    classification_basis=classification_basis,
                    field_group=field_group,
                    field_name=field_name,
                )
            )
            continue
        extracted_field = getattr(bundle, field_name)
        records.append(
            _build_extracted_field_record(
                extracted_field=extracted_field,
                bundle=bundle,
                selected_fund=selected_fund,
                run_id=run_id,
                extraction_timestamp=extraction_timestamp,
                source_csv=source_csv,
                classified_fund_type=classified_fund_type,
                classification_basis=classification_basis,
                field_group=field_group,
                field_name=field_name,
            )
        )
    return records


def write_snapshot_summary(
    *,
    summary_path: Path,
    run_id: str,
    source_csv: str,
    report_year: int,
    selected_funds: Sequence[SelectedFundRecord],
    records: Sequence[SnapshotRecord],
    errors: Sequence[SnapshotErrorRecord],
    validation: SelectedFundPoolValidation,
) -> None:
    """写入 P4-S1 snapshot 汇总 Markdown。

    Args:
        summary_path: summary 输出路径。
        run_id: 本次运行 ID。
        source_csv: 精选基金池 CSV 路径文本。
        report_year: 年报年份。
        selected_funds: 本次选择抽取的基金记录。
        records: 已生成的字段级记录。
        errors: 单基金失败记录。
        validation: CSV 校验结果。

    Returns:
        无返回值。

    Raises:
        OSError: 写入 summary 失败时抛出。
    """

    succeeded_funds = {record.fund_code for record in records}
    category_counts = Counter(fund.app_category for fund in selected_funds)
    field_counts = _summarize_fields(records)
    lines = [
        "# Selected Fund Extraction Snapshot Summary",
        "",
        f"- run_id: `{run_id}`",
        f"- source_csv: `{source_csv}`",
        f"- report_year: `{report_year}`",
        f"- selected_funds: {len(selected_funds)}",
        f"- succeeded_funds: {len(succeeded_funds)}",
        f"- failed_funds: {len(errors)}",
        f"- snapshot_records: {len(records)}",
        "",
        "## App Category Counts",
        "",
        "| App 类别 | 数量 |",
        "|---|---:|",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(["", "## Duplicate Codes", ""])
    if validation.duplicate_codes:
        for code in validation.duplicate_codes:
            lines.append(f"- <mark>{code}</mark>")
    else:
        lines.append("- 无")

    lines.extend(
        [
            "",
            "## Field Coverage",
            "",
            "| field_group | field_name | records | coverage | traceability |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for field_group, field_name in SNAPSHOT_FIELD_ORDER:
        summary = field_counts.get((field_group, field_name), _FieldSummary())
        lines.append(
            "| "
            f"{field_group} | "
            f"{field_name} | "
            f"{summary.total} | "
            f"{_format_ratio(summary.value_present, summary.total)} | "
            f"{_format_ratio(summary.anchor_present, summary.total)} |"
        )

    lines.extend(_source_provenance_summary_lines(records, errors))
    lines.extend(
        [
            "",
            "## Fund Results",
            "",
            "| 基金代码 | 基金名称 | App 类别 | 状态 | classified_fund_type | note |",
            "|---|---|---|---|---|---|",
        ]
    )
    fund_classification = _classification_by_fund(records)
    errors_by_code = {error.fund_code: error for error in errors}
    for fund in selected_funds:
        error = errors_by_code.get(fund.fund_code)
        if error is not None:
            lines.append(
                "| "
                f"{fund.fund_code} | {fund.fund_name} | {fund.app_category} | failed |  | "
                f"{error.error_type}: {error.error_message} |"
            )
            continue
        classified_type = fund_classification.get(fund.fund_code)
        note = (
            _KNOWN_FAILURE_004393_NOTE
            if fund.fund_code == "004393" and classified_type == "index_fund"
            else ""
        )
        lines.append(
            "| "
            f"{fund.fund_code} | {fund.fund_name} | {fund.app_category} | succeeded | "
            f"{classified_type or ''} | {note} |"
        )

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@dataclass(slots=True)
class _FieldSummary:
    """字段级 coverage / traceability 计数。"""

    total: int = 0
    value_present: int = 0
    anchor_present: int = 0


def _is_valid_fund_code(code: str) -> bool:
    """判断基金代码是否为 6 位数字。

    Args:
        code: 基金代码。

    Returns:
        合法返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    return len(code) == 6 and code.isdigit()


def _select_by_category(
    funds: Sequence[SelectedFundRecord], sample_per_category: int
) -> list[SelectedFundRecord]:
    """按类别从文件顺序抽样。

    Args:
        funds: 精选基金池记录。
        sample_per_category: 每个类别抽样数量。

    Returns:
        待抽取基金记录。

    Raises:
        无显式抛出。
    """

    selected: list[SelectedFundRecord] = []
    category_counts: Counter[str] = Counter()
    for fund in funds:
        if category_counts[fund.app_category] >= sample_per_category:
            continue
        selected.append(fund)
        category_counts[fund.app_category] += 1
    return selected


def _format_blocking_validation_error(validation: SelectedFundPoolValidation) -> str:
    """格式化阻断级 CSV 校验错误。

    Args:
        validation: CSV 校验结果。

    Returns:
        可读错误信息。

    Raises:
        无显式抛出。
    """

    parts: list[str] = []
    if validation.missing_rows:
        parts.append(f"缺少必填字段行：{', '.join(str(row) for row in validation.missing_rows)}")
    if validation.bad_code_rows:
        bad_rows = ", ".join(f"{line}:{code}" for line, code in validation.bad_code_rows)
        parts.append(f"非法基金代码行：{bad_rows}")
    return "；".join(parts)


def _extract_classified_fund_type(bundle: StructuredFundDataBundle) -> str | None:
    """从基础身份字段读取当前分类结果。

    Args:
        bundle: 结构化基金数据包。

    Returns:
        当前分类结果；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    value = bundle.basic_identity.value or {}
    raw_value = value.get("classified_fund_type")
    if raw_value is None:
        return None
    return str(raw_value)


def _extract_classification_basis(bundle: StructuredFundDataBundle) -> tuple[str, ...]:
    """从基础身份字段读取当前分类依据。

    Args:
        bundle: 结构化基金数据包。

    Returns:
        分类依据元组。

    Raises:
        无显式抛出。
    """

    value = bundle.basic_identity.value or {}
    raw_basis = value.get("classification_basis")
    if raw_basis is None:
        return ()
    if isinstance(raw_basis, str):
        return (raw_basis,)
    if isinstance(raw_basis, Sequence):
        return tuple(str(item) for item in raw_basis)
    return (str(raw_basis),)


def _build_extracted_field_record(
    *,
    extracted_field: ExtractedField[object],
    bundle: StructuredFundDataBundle,
    selected_fund: SelectedFundRecord,
    run_id: str,
    extraction_timestamp: str,
    source_csv: str,
    classified_fund_type: str | None,
    classification_basis: tuple[str, ...],
    field_group: str,
    field_name: str,
) -> SnapshotRecord:
    """构造普通 `ExtractedField` 的快照记录。

    Args:
        extracted_field: 带证据的抽取字段。
        bundle: 结构化基金数据包。
        selected_fund: CSV 中的基金记录。
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: CSV 路径文本。
        classified_fund_type: 当前分类结果。
        classification_basis: 当前分类依据。
        field_group: 字段组。
        field_name: 字段名。

    Returns:
        字段级快照记录。

    Raises:
        无显式抛出。
    """

    anchor = extracted_field.anchors[0] if extracted_field.anchors else None
    return _snapshot_record(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id=run_id,
        extraction_timestamp=extraction_timestamp,
        source_csv=source_csv,
        classified_fund_type=classified_fund_type,
        classification_basis=classification_basis,
        field_group=field_group,
        field_name=field_name,
        extraction_mode=extracted_field.extraction_mode,
        value_present=extracted_field.extraction_mode != _EXTRACTION_MODE_MISSING
        and _has_present_value(extracted_field.value),
        anchor=anchor,
        comparable_values=_comparable_values_for_field(field_name, extracted_field.value),
        note=_record_note(selected_fund, classified_fund_type, field_name, extracted_field.note),
    )


def _build_classification_record(
    *,
    bundle: StructuredFundDataBundle,
    selected_fund: SelectedFundRecord,
    run_id: str,
    extraction_timestamp: str,
    source_csv: str,
    classified_fund_type: str | None,
    classification_basis: tuple[str, ...],
    field_group: str,
    field_name: str,
) -> SnapshotRecord:
    """构造分类派生字段的快照记录。

    Args:
        bundle: 结构化基金数据包。
        selected_fund: CSV 中的基金记录。
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: CSV 路径文本。
        classified_fund_type: 当前分类结果。
        classification_basis: 当前分类依据。
        field_group: 字段组。
        field_name: 字段名。

    Returns:
        分类字段快照记录。

    Raises:
        无显式抛出。
    """

    anchor = bundle.basic_identity.anchors[0] if bundle.basic_identity.anchors else None
    return _snapshot_record(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id=run_id,
        extraction_timestamp=extraction_timestamp,
        source_csv=source_csv,
        classified_fund_type=classified_fund_type,
        classification_basis=classification_basis,
        field_group=field_group,
        field_name=field_name,
        extraction_mode=_EXTRACTION_MODE_DIRECT
        if classified_fund_type
        else _EXTRACTION_MODE_MISSING,
        value_present=bool(classified_fund_type),
        anchor=anchor,
        comparable_values=(
            {COMPARABLE_SUB_FIELDS_BY_FIELD[field_name][0]: classified_fund_type}
            if classified_fund_type
            else {}
        ),
        note=_record_note(selected_fund, classified_fund_type, field_name, None),
    )


def _build_nav_record(
    *,
    bundle: StructuredFundDataBundle,
    selected_fund: SelectedFundRecord,
    run_id: str,
    extraction_timestamp: str,
    source_csv: str,
    classified_fund_type: str | None,
    classification_basis: tuple[str, ...],
    field_group: str,
    field_name: str,
) -> SnapshotRecord:
    """构造净值数据快照记录。

    Args:
        bundle: 结构化基金数据包。
        selected_fund: CSV 中的基金记录。
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: CSV 路径文本。
        classified_fund_type: 当前分类结果。
        classification_basis: 当前分类依据。
        field_group: 字段组。
        field_name: 字段名。

    Returns:
        净值数据字段快照记录。

    Raises:
        无显式抛出。
    """

    nav_data = bundle.nav_data
    value_present = _has_nav_records(nav_data)
    note = f"source={nav_data.source}; cached={nav_data.cached}; records={len(nav_data.records)}"
    if nav_data.unavailable:
        note = f"{note}; unavailable=True; reason={nav_data.unavailable_reason}"
    return _snapshot_record(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id=run_id,
        extraction_timestamp=extraction_timestamp,
        source_csv=source_csv,
        classified_fund_type=classified_fund_type,
        classification_basis=classification_basis,
        field_group=field_group,
        field_name=field_name,
        extraction_mode=_EXTRACTION_MODE_DIRECT if value_present else _EXTRACTION_MODE_MISSING,
        value_present=value_present,
        anchor=None,
        comparable_values={},
        note=note,
    )


def _build_bond_risk_evidence_record(
    *,
    bundle: StructuredFundDataBundle,
    selected_fund: SelectedFundRecord,
    run_id: str,
    extraction_timestamp: str,
    source_csv: str,
    classified_fund_type: str | None,
    classification_basis: tuple[str, ...],
    field_group: str,
    field_name: str,
) -> SnapshotRecord:
    """构造债券风险证据快照记录，见模板第 6 章“核心风险”。

    Args:
        bundle: 结构化基金数据包。
        selected_fund: CSV 中的基金记录。
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: CSV 路径文本。
        classified_fund_type: 当前分类结果。
        classification_basis: 当前分类依据。
        field_group: 字段组。
        field_name: 字段名。

    Returns:
        债券风险证据字段级快照记录。

    Raises:
        无显式抛出。
    """

    extracted_field = bundle.bond_risk_evidence
    value = extracted_field.value
    structured_value = value if isinstance(value, BondRiskEvidenceValue) else None
    anchor = _first_traceable_anchor(extracted_field.anchors)
    return _snapshot_record(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id=run_id,
        extraction_timestamp=extraction_timestamp,
        source_csv=source_csv,
        classified_fund_type=classified_fund_type,
        classification_basis=classification_basis,
        field_group=field_group,
        field_name=field_name,
        extraction_mode=extracted_field.extraction_mode,
        value_present=_bond_risk_value_present(structured_value),
        anchor=anchor,
        comparable_values={},
        note=_bond_risk_note(structured_value, extracted_field.note),
        bond_risk_contract_status=(
            structured_value.contract_status if structured_value is not None else None
        ),
        bond_risk_satisfied_groups=_string_tuple(
            structured_value.satisfied_group_ids if structured_value is not None else ()
        ),
        bond_risk_missing_groups=_string_tuple(
            structured_value.missing_group_ids if structured_value is not None else ()
        ),
        bond_risk_weak_groups=_string_tuple(
            structured_value.weak_group_ids if structured_value is not None else ()
        ),
        bond_risk_ambiguous_groups=_string_tuple(
            structured_value.ambiguous_group_ids if structured_value is not None else ()
        ),
    )


def _snapshot_record(
    *,
    bundle: StructuredFundDataBundle,
    selected_fund: SelectedFundRecord,
    run_id: str,
    extraction_timestamp: str,
    source_csv: str,
    classified_fund_type: str | None,
    classification_basis: tuple[str, ...],
    field_group: str,
    field_name: str,
    extraction_mode: str,
    value_present: bool,
    anchor: EvidenceAnchor | None,
    comparable_values: dict[str, str],
    note: str | None,
    bond_risk_contract_status: str | None = None,
    bond_risk_satisfied_groups: tuple[str, ...] = (),
    bond_risk_missing_groups: tuple[str, ...] = (),
    bond_risk_weak_groups: tuple[str, ...] = (),
    bond_risk_ambiguous_groups: tuple[str, ...] = (),
) -> SnapshotRecord:
    """构造字段级快照记录的公共部分。

    Args:
        bundle: 结构化基金数据包。
        selected_fund: CSV 中的基金记录。
        run_id: 本次运行 ID。
        extraction_timestamp: ISO-8601 抽取时间戳。
        source_csv: CSV 路径文本。
        classified_fund_type: 当前分类结果。
        classification_basis: 当前分类依据。
        field_group: 字段组。
        field_name: 字段名。
        extraction_mode: 抽取模式。
        value_present: 是否存在非空值。
        anchor: 首个证据锚点。
        comparable_values: correctness 可直接比较的白名单子字段值。
        note: 附加说明。
        bond_risk_contract_status: 债券风险证据契约状态。
        bond_risk_satisfied_groups: 已满足的债券风险证据组。
        bond_risk_missing_groups: 缺失的债券风险证据组。
        bond_risk_weak_groups: 弱证据债券风险证据组。
        bond_risk_ambiguous_groups: 歧义债券风险证据组。

    Returns:
        字段级快照记录。

    Raises:
        无显式抛出。
    """

    provenance = bundle.source_provenance
    return SnapshotRecord(
        run_id=run_id,
        extraction_timestamp=extraction_timestamp,
        source_csv=source_csv,
        fund_code=bundle.fund_code,
        fund_name=selected_fund.fund_name,
        app_category=selected_fund.app_category,
        report_year=bundle.report_year,
        classified_fund_type=classified_fund_type,
        classification_basis=classification_basis,
        field_name=field_name,
        field_group=field_group,
        extraction_mode=_normalize_extraction_mode(extraction_mode),
        value_present=value_present,
        anchor_present=anchor is not None,
        section_id=anchor.section_id if anchor else None,
        page=anchor.page_number if anchor else None,
        table_id=anchor.table_id if anchor else None,
        row_id=anchor.row_locator if anchor else None,
        comparable_values=comparable_values,
        note=note,
        source_provenance_schema_version=provenance.source_provenance_schema_version,
        source_strategy=provenance.source_strategy,
        resolved_source_name=provenance.resolved_source_name,
        fallback_used=provenance.fallback_used,
        primary_failure_category=provenance.primary_failure_category,
        fallback_eligibility=provenance.fallback_eligibility,
        source_provenance_status=provenance.source_provenance_status,
        source_provenance_reason=provenance.source_provenance_reason,
        bond_risk_contract_status=bond_risk_contract_status,
        bond_risk_satisfied_groups=bond_risk_satisfied_groups,
        bond_risk_missing_groups=bond_risk_missing_groups,
        bond_risk_weak_groups=bond_risk_weak_groups,
        bond_risk_ambiguous_groups=bond_risk_ambiguous_groups,
    )


def _source_provenance_summary_lines(
    records: Sequence[SnapshotRecord],
    errors: Sequence[SnapshotErrorRecord],
) -> list[str]:
    """构造 snapshot summary 的公共来源 provenance 表。

    Args:
        records: 已生成的字段级记录。
        errors: 单基金失败记录。

    Returns:
        Markdown 行列表；失败基金 v1 不进入表格，只输出简短说明。

    Raises:
        无显式抛出。
    """

    first_records_by_fund: dict[str, SnapshotRecord] = {}
    for record in records:
        first_records_by_fund.setdefault(record.fund_code, record)

    lines = [
        "",
        "## Source Provenance",
        "",
        "| fund_code | resolved_source_name | fallback_used | fallback_eligibility | source_provenance_status | source_provenance_reason |",
        "|---|---|---|---|---|---|",
    ]
    for fund_code in sorted(first_records_by_fund):
        record = first_records_by_fund[fund_code]
        lines.append(
            "| "
            f"{record.fund_code} | "
            f"{_summary_nullable_text(record.resolved_source_name)} | "
            f"{_summary_bool_text(record.fallback_used)} | "
            f"{record.fallback_eligibility} | "
            f"{record.source_provenance_status} | "
            f"{record.source_provenance_reason} |"
        )
    if errors:
        lines.extend(
            [
                "",
                "_Failed funds without snapshot records are omitted from Source Provenance v1._",
            ]
        )
    return lines


def _summary_nullable_text(value: str | None) -> str:
    """把 summary 表中的空值格式化为稳定 `null`。

    Args:
        value: 可选文本。

    Returns:
        非空文本或 `null`。

    Raises:
        无显式抛出。
    """

    return value if value is not None else "null"


def _summary_bool_text(value: bool) -> str:
    """把 summary 表中的布尔值格式化为小写 JSON 风格文本。

    Args:
        value: 布尔值。

    Returns:
        `true` 或 `false`。

    Raises:
        无显式抛出。
    """

    return "true" if value else "false"


def _comparable_values_for_field(
    field_name: str,
    value: object,
) -> dict[str, str]:
    """从抽取字段值中提取 correctness 可比子字段。

    Args:
        field_name: snapshot 字段名。
        value: 字段结构化值。

    Returns:
        白名单子字段到可比较文本值的映射；非白名单字段返回空映射。

    Raises:
        无显式抛出。
    """

    allowed_sub_fields = COMPARABLE_SUB_FIELDS_BY_FIELD.get(field_name)
    mapped_value = value_mapping(value)
    if allowed_sub_fields is None or mapped_value is None:
        return {}
    comparable_values: dict[str, str] = {}
    for sub_field in allowed_sub_fields:
        comparable_value = _comparable_scalar(mapped_value.get(sub_field))
        if comparable_value is not None:
            comparable_values[sub_field] = comparable_value
    if field_name == "benchmark" and "benchmark_name" not in comparable_values:
        benchmark_text = _comparable_scalar(mapped_value.get("benchmark_text"))
        if benchmark_text is not None:
            comparable_values["benchmark_name"] = benchmark_text
    return comparable_values


def _comparable_scalar(value: object) -> str | None:
    """把可比子字段值转换为保守文本。

    Args:
        value: 原始子字段值。

    Returns:
        非空标量文本；嵌套结构、空值和空白文本返回 `None`。

    Raises:
        无显式抛出。
    """

    if value is None or isinstance(value, (dict, list, tuple, set)):
        return None
    text = str(value).strip()
    return text or None


def _normalize_extraction_mode(extraction_mode: str) -> str:
    """规范化 snapshot 支持的抽取模式。

    Args:
        extraction_mode: 底层 extractor 输出模式。

    Returns:
        `direct / estimated / missing / partial` 之一；`derived` 当前归入 `direct`。

    Raises:
        无显式抛出。
    """

    if extraction_mode == "derived":
        return _EXTRACTION_MODE_DIRECT
    if extraction_mode in {"direct", "estimated", "missing", "partial"}:
        return extraction_mode
    return _EXTRACTION_MODE_MISSING


def _has_present_value(value: object) -> bool:
    """判断抽取值是否包含有效内容。

    Args:
        value: 抽取字段值。

    Returns:
        存在任一非空内容时返回 `True`。

    Raises:
        无显式抛出。
    """

    if value is None:
        return False
    if isinstance(value, dict):
        return any(_has_present_value(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_has_present_value(item) for item in value)
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _bond_risk_value_present(value: BondRiskEvidenceValue | None) -> bool:
    """判断债券风险证据契约值是否可视为已存在，见模板第 6 章“核心风险”。

    Args:
        value: 债券风险证据契约值；缺失或 malformed 时为 `None`。

    Returns:
        仅当结构化值存在且契约状态不是 `missing` 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return value is not None and value.contract_status != _EXTRACTION_MODE_MISSING


def _first_traceable_anchor(anchors: Sequence[EvidenceAnchor]) -> EvidenceAnchor | None:
    """返回首个字段级可追溯锚点。

    Args:
        anchors: 字段级证据锚点序列。

    Returns:
        首个 `source_kind=annual_report` 的锚点；不存在年报锚点时返回首个任意锚点。

    Raises:
        无显式抛出。
    """

    for anchor in anchors:
        if anchor.source_kind == "annual_report":
            return anchor
    return anchors[0] if anchors else None


def _bond_risk_note(value: BondRiskEvidenceValue | None, note: str | None) -> str | None:
    """构造债券风险证据 snapshot 备注 token，见模板第 6 章“核心风险”。

    Args:
        value: 债券风险证据契约值。
        note: 底层字段备注。

    Returns:
        可读备注；结构化字段仍是机器判定真源。

    Raises:
        无显式抛出。
    """

    notes: list[str] = []
    if value is not None:
        notes.append(
            " ".join(
                (
                    f"contract_id={value.contract_id};",
                    f"contract_status={value.contract_status};",
                    f"satisfied_groups={','.join(value.satisfied_group_ids)};",
                    f"missing_groups={','.join(value.missing_group_ids)};",
                    f"weak_groups={','.join(value.weak_group_ids)};",
                    f"ambiguous_groups={','.join(value.ambiguous_group_ids)}",
                )
            )
        )
    if note:
        notes.append(note)
    if not notes:
        return None
    return " ".join(notes)


def _string_tuple(values: Sequence[object]) -> tuple[str, ...]:
    """把结构化组 ID 序列规范化为字符串元组。

    Args:
        values: 任意组 ID 序列。

    Returns:
        字符串元组，保持原始顺序。

    Raises:
        无显式抛出。
    """

    return tuple(str(value) for value in values)


def _has_nav_records(nav_data: NavDataResult) -> bool:
    """判断净值数据是否存在记录。

    Args:
        nav_data: 净值数据读取结果。

    Returns:
        有净值记录时返回 `True`。

    Raises:
        无显式抛出。
    """

    return bool(nav_data.records)


def _record_note(
    selected_fund: SelectedFundRecord,
    classified_fund_type: str | None,
    field_name: str,
    note: str | None,
) -> str | None:
    """追加 P4-S1 已知 failure 说明。

    Args:
        selected_fund: CSV 中的基金记录。
        classified_fund_type: 当前分类结果。
        field_name: 字段名。
        note: 底层字段说明。

    Returns:
        合并后的说明。

    Raises:
        无显式抛出。
    """

    notes = [note] if note else []
    if (
        selected_fund.fund_code == "004393"
        and classified_fund_type == "index_fund"
        and field_name == "classified_fund_type"
    ):
        notes.append(_KNOWN_FAILURE_004393_NOTE)
    if not notes:
        return None
    return " ".join(notes)


def _summarize_fields(records: Sequence[SnapshotRecord]) -> dict[tuple[str, str], _FieldSummary]:
    """按字段统计 coverage 与 traceability。

    Args:
        records: 字段级快照记录。

    Returns:
        `(field_group, field_name)` 到计数结果的映射。

    Raises:
        无显式抛出。
    """

    summaries: dict[tuple[str, str], _FieldSummary] = {}
    for record in records:
        key = (record.field_group, record.field_name)
        summary = summaries.setdefault(key, _FieldSummary())
        summary.total += 1
        if record.value_present:
            summary.value_present += 1
        if record.anchor_present:
            summary.anchor_present += 1
    return summaries


def _classification_by_fund(records: Sequence[SnapshotRecord]) -> dict[str, str | None]:
    """提取每只基金的分类结果。

    Args:
        records: 字段级快照记录。

    Returns:
        基金代码到分类结果的映射。

    Raises:
        无显式抛出。
    """

    return {
        record.fund_code: record.classified_fund_type
        for record in records
        if record.field_name == "classified_fund_type"
    }


def _format_ratio(numerator: int, denominator: int) -> str:
    """格式化百分比统计。

    Args:
        numerator: 分子。
        denominator: 分母。

    Returns:
        形如 `50.0% (1/2)` 的文本。

    Raises:
        无显式抛出。
    """

    if denominator == 0:
        return "0.0% (0/0)"
    return f"{numerator / denominator:.1%} ({numerator}/{denominator})"


def _append_jsonl(path: Path, payload: dict[str, object]) -> None:
    """追加写入一行 JSONL。

    Args:
        path: JSONL 路径。
        payload: 可 JSON 序列化的字典。

    Returns:
        无返回值。

    Raises:
        OSError: 文件写入失败时抛出。
        TypeError: payload 无法 JSON 序列化时抛出。
    """

    with path.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _path_for_output(path: Path) -> str:
    """把路径转换为 summary / snapshot 中使用的文本。

    Args:
        path: 输入路径。

    Returns:
        优先返回相对当前工作目录路径；不可相对时返回原路径字符串。

    Raises:
        无显式抛出。
    """

    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _utc_now() -> str:
    """返回 UTC ISO-8601 时间戳。

    Args:
        无。

    Returns:
        UTC 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()
