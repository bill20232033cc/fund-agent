"""精选基金池字段级抽取评分与 correctness 比对能力。

本模块位于 Agent 层基金能力，负责 P4-S2 前半段质量基线：
只消费 P4-S1 `snapshot.jsonl` 字段级记录，计算 coverage / traceability，
并从精选基金池 CSV 中选择最小 golden set。P4-R10 起额外消费 strict
golden answer JSON，对 snapshot 明确暴露的可比字段执行 correctness 比对。
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Final, Mapping, Sequence, cast, get_args

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.extraction_snapshot import (
    COMPARABLE_SUB_FIELDS_BY_FIELD,
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
from fund_agent.fund.template.contracts import (
    load_template_contract_manifest,
    resolve_preferred_lens,
)
from fund_agent.fund.template.item_rules import (
    evaluate_template_item_rules,
    load_template_item_rule_manifest,
)

FIELD_PRIORITY_BY_NAME: Final[dict[str, str]] = {
    "basic_identity": "P0",
    "classified_fund_type": "P0",
    "benchmark": "P0",
    "nav_benchmark_performance": "P0",
    "fee_schedule": "P0",
    "manager_strategy_text": "P0",
    "product_profile": "P1",
    "index_profile": "P1",
    "tracking_error": "P1",
    "turnover_rate": "P1",
    "holder_structure": "P1",
    "manager_alignment": "P1",
    "holdings_snapshot": "P1",
    "share_change": "P1",
    "investor_return": "P2",
    "nav_data": "P2",
}
UNKNOWN_FIELD_PRIORITY: Final[str] = "UNMAPPED"
PRIORITY_P0: Final[str] = "P0"
PRIORITY_P1: Final[str] = "P1"
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
CORRECTNESS_COVERAGE_NOT_CONFIGURED: Final[str] = "not_configured"
CORRECTNESS_COVERAGE_FUND_NOT_COVERED: Final[str] = "fund_not_covered"
CORRECTNESS_COVERAGE_YEAR_NOT_COVERED: Final[str] = "year_not_covered"
CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS: Final[str] = "no_comparable_fields"
CORRECTNESS_COVERAGE_PARTIALLY_COVERED: Final[str] = "partially_covered"
CORRECTNESS_COVERAGE_COVERED: Final[str] = "covered"
CORRECTNESS_MATCH: Final[str] = "match"
CORRECTNESS_MISMATCH: Final[str] = "mismatch"
CORRECTNESS_UNAVAILABLE: Final[str] = "unavailable"
CLASSIFIED_FUND_TYPE_FIELD: Final[str] = "classified_fund_type"
CLASSIFIED_FUND_TYPE_SUB_FIELD: Final[str] = "fund_type"
APP_CATEGORY_STATUS_MATCH: Final[str] = "match"
APP_CATEGORY_STATUS_CONFLICT: Final[str] = "conflict"
APP_CATEGORY_STATUS_UNKNOWN: Final[str] = "unknown"
PREFERRED_LENS_STATUS_RESOLVED: Final[str] = "resolved"
PREFERRED_LENS_STATUS_NOT_APPLICABLE: Final[str] = "not_applicable"
PREFERRED_LENS_STATUS_MISMATCH: Final[str] = "mismatch"
SUPPORTED_CONTRACT_FUND_TYPES: Final[tuple[str, ...]] = tuple(get_args(FundType))
INDEX_QUALITY_FIELD_NAMES: Final[tuple[str, ...]] = ("index_profile", "tracking_error")
HOLDINGS_SNAPSHOT_FIELD_NAME: Final[str] = "holdings_snapshot"
TOP_HOLDINGS_STATUS_SUB_FIELD: Final[str] = "top_holdings_status"
TOP_HOLDINGS_SOURCE_SUB_FIELD: Final[str] = "top_holdings_source"
TOP_HOLDINGS_COVERED_STATUS_SOURCE_PAIRS: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("direct_top_ten", "top_ten"),
        ("direct_all_stock_details", "all_stock_investment_details"),
    }
)
TOP_HOLDINGS_STATUS_MISSING: Final[str] = "missing"
BOND_FUND_TYPE: Final[str] = "bond_fund"
BOND_RISK_EVIDENCE_CONTRACT_ID: Final[str] = "bond_risk_evidence.v1"
BOND_RISK_REPLACEMENT_FIELD_NAME: Final[str] = "bond_risk_evidence"
BOND_RISK_EVIDENCE_MISSING_ISSUE_CODE: Final[str] = "bond_risk_evidence_missing"
BOND_HOLDINGS_NOT_APPLICABLE_REASON: Final[str] = "not_applicable_to_bond_fund_equity_holdings"
APPLICABILITY_STATUS_NOT_APPLICABLE_REPLACED: Final[str] = "not_applicable_replaced"
APPLICABILITY_STATUS_UNKNOWN_FAIL_CLOSED: Final[str] = "unknown_fail_closed"
DENOMINATOR_EFFECT_EXCLUDED_WITH_REPLACEMENT_ISSUE: Final[str] = (
    "excluded_with_replacement_issue"
)
DENOMINATOR_EFFECT_INCLUDED_FAIL_CLOSED: Final[str] = "included_fail_closed"
BENCHMARK_FIELD_NAME: Final[str] = "benchmark"
BENCHMARK_NORMALIZED_SUB_FIELDS: Final[tuple[str, ...]] = ("benchmark_name", "benchmark_text")
INTRA_CHINESE_VISUAL_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])"
)
BASIC_IDENTITY_FIELD_NAME: Final[str] = "basic_identity"
INCEPTION_DATE_SUB_FIELD: Final[str] = "inception_date"
CHINESE_DATE_VISUAL_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日"
)
INDEX_QUALITY_APPLICABLE_FUND_TYPES: Final[tuple[str, ...]] = (
    "index_fund",
    "enhanced_index",
)
APP_CATEGORY_ALLOWED_FUND_TYPES: Final[dict[str, tuple[str, ...]]] = {
    "国内股票类": ("active_fund", "index_fund", "enhanced_index"),
    "国内债券类": ("bond_fund",),
    "海外股票类": ("qdii_fund",),
    "海外债券/稳健类": ("qdii_fund", "bond_fund", "fof_fund"),
    "黄金类": ("qdii_fund", "fof_fund", "index_fund", "enhanced_index"),
}
TEMPLATE_NOT_APPLICABLE_CATEGORIES: Final[tuple[str, ...]] = (MONEY_MARKET_CATEGORY,)


@dataclass(frozen=True, slots=True)
class BondRiskEvidenceGroup:
    """债券基金替代风险证据组。

    这些组定义 `bond_risk_evidence.v1` 最小证据契约，见模板第 6 章核心风险
    与债券基金 preferred_lens。当前 slice 只声明并保守评估缺口，不读取年报。

    Attributes:
        group_id: 证据组稳定标识。
        required_evidence: 可满足该组的证据类型说明。
        allowed_na_reasons: 允许的显式不可得原因。
        failure_behavior: 缺少该组证据时的处理方式。
        severity: 当前 score-applicability issue 严重级别。
        baseline_blocking: 是否阻断 baseline / golden 候选。
    """

    group_id: str
    required_evidence: str
    allowed_na_reasons: tuple[str, ...]
    failure_behavior: str
    severity: str
    baseline_blocking: bool


BOND_RISK_EVIDENCE_GROUPS: Final[tuple[BondRiskEvidenceGroup, ...]] = (
    BondRiskEvidenceGroup(
        group_id="duration_rate_risk",
        required_evidence=(
            "组合久期、平均剩余期限、利率敏感性披露、利率风险说明，或带证据锚点的已复核派生证据"
        ),
        allowed_na_reasons=(
            "bond_duration_rate_risk_not_disclosed",
            "bond_duration_rate_risk_not_yet_reviewed",
        ),
        failure_behavior="missing_reviewed_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
    BondRiskEvidenceGroup(
        group_id="credit_risk",
        required_evidence=(
            "债券评级分布、信用债敞口、违约/减值风险披露、非政策性金融债敞口或发行人信用集中度"
        ),
        allowed_na_reasons=(
            "bond_credit_risk_not_disclosed",
            "bond_credit_risk_not_yet_reviewed",
        ),
        failure_behavior="missing_reviewed_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
    BondRiskEvidenceGroup(
        group_id="leverage_liquidity",
        required_evidence="杠杆率、回购/融资敞口、流动性风险说明或大额赎回/持有人集中度披露",
        allowed_na_reasons=(
            "bond_leverage_liquidity_not_disclosed",
            "bond_leverage_liquidity_not_yet_reviewed",
        ),
        failure_behavior="missing_reviewed_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
    BondRiskEvidenceGroup(
        group_id="asset_allocation_holdings_mix",
        required_evidence="债券/现金/金融工具结构、前五大债券持仓、发行人或行业集中度披露",
        allowed_na_reasons=(
            "bond_asset_mix_not_disclosed",
            "bond_asset_mix_not_yet_reviewed",
        ),
        failure_behavior="missing_reviewed_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
    BondRiskEvidenceGroup(
        group_id="drawdown_stress",
        required_evidence="最大回撤、波动率、压力测试阈值状态，或带来源锚点的回撤/压力计算",
        allowed_na_reasons=(
            "bond_drawdown_stress_not_disclosed",
            "bond_drawdown_stress_not_yet_reviewed",
        ),
        failure_behavior="missing_reviewed_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
    BondRiskEvidenceGroup(
        group_id="redemption_share_pressure",
        required_evidence="份额变化、申赎趋势、持有人集中压力、大额赎回披露或显式歧义/数据缺口",
        allowed_na_reasons=(
            "bond_redemption_pressure_not_disclosed",
            "bond_redemption_pressure_ambiguous",
            "bond_redemption_pressure_not_yet_reviewed",
        ),
        failure_behavior="missing_or_ambiguous_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
    BondRiskEvidenceGroup(
        group_id="convertible_bond_equity_exposure",
        required_evidence="可转债敞口、股票敞口、二级债/混合债权益配置，或无权益/可转债敞口披露",
        allowed_na_reasons=(
            "bond_convertible_equity_exposure_not_disclosed",
            "bond_convertible_equity_exposure_not_yet_reviewed",
        ),
        failure_behavior="missing_reviewed_evidence_emits_bond_risk_evidence_missing",
        severity="warn",
        baseline_blocking=True,
    ),
)


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
class FundQualityRow:
    """单只基金的质量派生判断行。

    Attributes:
        fund_code: 基金代码。
        fund_name: 基金名称。
        app_category: App 类别。
        classified_fund_type: 系统识别基金类型。
        app_category_status: App 类别与基金类型匹配状态。
        preferred_lens_status: preferred_lens 可解析状态。
        preferred_lens_key: 由基金类型解析出的 lens key。
        missing_field_count: 缺失字段记录数。
        total_field_count: 参与统计字段记录数。
        missing_field_rate: 缺失字段比例。
        missing_p0_fields: 缺失的 P0 字段。
        missing_p1_fields: 缺失的 P1 字段。
        reason: 人类可读原因。
        contract_template_id: CHAPTER_CONTRACT manifest 标识；未评估时为空。
        item_rule_template_id: ITEM_RULE manifest 标识；未评估时为空。
        preferred_lens_chapters: 每章 preferred_lens 解析事实。
        preferred_lens_unresolved_chapter_ids: 未能解析 preferred_lens 的章节编号。
        item_rule_decisions: ITEM_RULE evaluator 的确定性适用性决策。
    """

    fund_code: str
    fund_name: str | None
    app_category: str | None
    classified_fund_type: str | None
    app_category_status: str
    preferred_lens_status: str
    preferred_lens_key: str | None
    missing_field_count: int
    total_field_count: int
    missing_field_rate: float
    missing_p0_fields: tuple[str, ...]
    missing_p1_fields: tuple[str, ...]
    reason: str
    contract_template_id: str | None
    item_rule_template_id: str | None
    preferred_lens_chapters: tuple["PreferredLensChapterResolution", ...]
    preferred_lens_unresolved_chapter_ids: tuple[int, ...]
    item_rule_decisions: tuple["ItemRuleDecisionSummary", ...]


@dataclass(frozen=True, slots=True)
class PreferredLensChapterResolution:
    """单章 preferred_lens 解析事实。

    Attributes:
        chapter_id: 模板章节编号，见模板第 0-7 章。
        title: 模板章节标题。
        lens_key: 当前章节解析出的 lens key。
        used_default: 是否回退到 `default` lens。
    """

    chapter_id: int
    title: str
    lens_key: str
    used_default: bool


@dataclass(frozen=True, slots=True)
class ItemRuleDecisionSummary:
    """ITEM_RULE evaluator 决策摘要。

    Attributes:
        rule_id: ITEM_RULE 规则编号。
        chapter_id: 规则所属模板章节编号。
        item_title: 规则对应条目标题。
        triggered: 当前基金类型是否触发规则。
        status: evaluator 决定渲染或删除的状态。
        missing_behavior: 未触发或缺失时的策略。
    """

    rule_id: str
    chapter_id: int
    item_title: str
    triggered: bool
    status: str
    missing_behavior: str


@dataclass(frozen=True, slots=True)
class FieldApplicabilityDecision:
    """字段评分适用性决策。

    该决策用于解释字段是否进入 coverage / traceability 分母，见模板第 6 章债券风险
    preferred_lens。债券基金的权益持仓字段只有在替代 `bond_risk_evidence.v1`
    issue 同时存在时才允许排除。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份；缺失时为 `unknown-year`。
        field_name: 原始 snapshot 字段名。
        classified_fund_type: 已解析基金类型；未知或冲突时为空。
        applicability_status: 适用性状态。
        reason_code: 机器可读原因。
        replacement_field_name: 替代字段名。
        contract_id: 替代证据契约编号。
        denominator_effect: 对评分分母的影响。
        raw_total_field_count: 原始字段记录数。
        raw_missing_field_count: 原始缺失记录数。
        raw_missing_field_rate: 原始缺失率。
        applicable_total_field_count: 适用性过滤后的字段记录数。
        applicable_missing_field_count: 适用性过滤后的缺失记录数。
        applicable_missing_field_rate: 适用性过滤后的缺失率。
        excluded_non_applicable_fields: 被排除的非适用字段。
        replacement_issue_ids: 与排除决策配对的替代 issue id。
    """

    fund_code: str
    report_year: str
    field_name: str
    classified_fund_type: str | None
    applicability_status: str
    reason_code: str
    replacement_field_name: str | None
    contract_id: str | None
    denominator_effect: str
    raw_total_field_count: int
    raw_missing_field_count: int
    raw_missing_field_rate: float
    applicable_total_field_count: int
    applicable_missing_field_count: int
    applicable_missing_field_rate: float
    excluded_non_applicable_fields: tuple[str, ...]
    replacement_issue_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScoreApplicabilityIssue:
    """评分适用性替代 issue。

    Attributes:
        issue_id: 稳定 issue id。
        issue_code: issue 分类码。
        severity: gate 聚合严重级别。
        fund_code: 基金代码。
        report_year: 年报年份；缺失时为 `unknown-year`。
        field_name: 被替代的原始字段名。
        classified_fund_type: 已解析基金类型。
        replacement_field_name: 替代字段名。
        contract_id: 替代证据契约编号。
        priority: 字段优先级。
        message: 人类可读说明。
        baseline_blocking: 是否阻断 baseline / golden 候选。
        rule_code_hint: 推荐 quality gate 规则码。
        denominator_excluded_fields: 该 issue 支撑排除的字段。
        required_evidence_groups: 契约要求证据组。
        missing_evidence_groups: 当前缺失证据组。
    """

    issue_id: str
    issue_code: str
    severity: str
    fund_code: str
    report_year: str
    field_name: str
    classified_fund_type: str | None
    replacement_field_name: str
    contract_id: str
    priority: str
    message: str
    baseline_blocking: bool
    rule_code_hint: str
    denominator_excluded_fields: tuple[str, ...]
    required_evidence_groups: tuple[str, ...]
    missing_evidence_groups: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FailedFundRow:
    """完全抽取失败的基金行。

    Attributes:
        fund_code: 基金代码。
        fund_name: 基金名称；旧错误记录缺失时为空。
        app_category: App 类别；旧错误记录缺失时为空。
        report_year: 年报年份；旧错误记录缺失时为空。
        error_type: 异常类型名；旧错误记录缺失时为空。
        error_message: 异常信息；旧错误记录缺失时为空。
    """

    fund_code: str
    fund_name: str | None
    app_category: str | None
    report_year: int | None
    error_type: str | None
    error_message: str | None


@dataclass(frozen=True, slots=True)
class CorrectnessRecordResult:
    """单条 golden answer correctness 比对结果。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
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
    report_year: int
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
        coverage_scope: 当前 run 的 strict golden 覆盖范围。
        coverage_reason: 覆盖范围的机器可读原因。
        covered_fund_codes: 当前 run 中已有可比 golden 记录的基金代码。
        missing_fund_codes: 当前 run 中缺少 correctness 覆盖的基金代码。
        coverage_required: 当前策略是否要求 strict golden 覆盖；P9-S2 固定为 false。
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
    coverage_scope: str
    coverage_reason: str
    covered_fund_codes: tuple[str, ...]
    missing_fund_codes: tuple[str, ...]
    coverage_required: bool
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
        fund_quality: 单只基金质量派生判断行。
        field_applicability_decisions: 字段适用性决策。
        score_applicability_issues: 评分适用性替代 issue。
        failed_funds: 完全抽取失败的基金行。
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
    fund_quality: tuple[FundQualityRow, ...]
    field_applicability_decisions: tuple[FieldApplicabilityDecision, ...]
    score_applicability_issues: tuple[ScoreApplicabilityIssue, ...]
    failed_funds: tuple[FailedFundRow, ...]
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


@dataclass(frozen=True, slots=True)
class _ContractApplicability:
    """内部使用的模板契约适用性派生结果。

    Attributes:
        status: FQ5 适用性状态。
        preferred_lens_key: 当前尝试应用的 preferred_lens key。
        preferred_lens_chapters: 每章 lens 解析事实。
        preferred_lens_unresolved_chapter_ids: 未解析成功的章节编号。
        item_rule_decisions: ITEM_RULE evaluator 决策摘要。
        reason: 人类可读原因。
        contract_template_id: CHAPTER_CONTRACT manifest 标识。
        item_rule_template_id: ITEM_RULE manifest 标识。
    """

    status: str
    preferred_lens_key: str | None
    preferred_lens_chapters: tuple[PreferredLensChapterResolution, ...]
    preferred_lens_unresolved_chapter_ids: tuple[int, ...]
    item_rule_decisions: tuple[ItemRuleDecisionSummary, ...]
    reason: str
    contract_template_id: str | None
    item_rule_template_id: str | None


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


def load_snapshot_error_records(errors_path: Path) -> tuple[FailedFundRow, ...]:
    """读取 P4-S1 `errors.jsonl` 并转换为失败基金行。

    Args:
        errors_path: P4-S1 输出的 `errors.jsonl` 路径。

    Returns:
        完全抽取失败基金行元组；空行会被忽略。

    Raises:
        FileNotFoundError: errors 文件不存在时抛出。
        ValueError: JSONL 行不是对象或缺少 `fund_code` 时抛出。
        json.JSONDecodeError: JSONL 行内容非法时抛出。
    """

    failed_funds: list[FailedFundRow] = []
    with errors_path.open(encoding="utf-8") as file_obj:
        for line_number, line in enumerate(file_obj, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"errors 第 {line_number} 行不是 JSON object")
            failed_funds.append(_failed_fund_row(payload, line_number=line_number))
    return tuple(failed_funds)


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
    for record in _scorable_records(records):
        field_group = _required_text(record, "field_group")
        field_name = _required_text(record, "field_name")
        key = (field_group, field_name)
        counter = counters.setdefault(
            key,
            _FieldScoreCounter(field_group=field_group, field_name=field_name),
        )
        counter.records += 1
        if _record_is_covered(record):
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


def derive_fund_quality_records(
    records: Sequence[Mapping[str, object]],
) -> tuple[FundQualityRow, ...]:
    """从 snapshot 记录派生单基金质量判断。

    Args:
        records: P4-S1 `snapshot.jsonl` 解析后的字段级记录。

    Returns:
        按基金代码排序的质量派生行。

    Raises:
        ValueError: 记录缺少 `fund_code` / `field_name` 时抛出。
    """

    records_by_fund: dict[str, list[Mapping[str, object]]] = {}
    for record in records:
        fund_code = _required_text(record, "fund_code")
        records_by_fund.setdefault(fund_code, []).append(record)
    return tuple(
        _build_fund_quality_row(fund_code, fund_records)
        for fund_code, fund_records in sorted(records_by_fund.items())
    )


def derive_field_applicability_decisions(
    records: Sequence[Mapping[str, object]],
) -> tuple[FieldApplicabilityDecision, ...]:
    """从 snapshot 记录派生字段适用性决策。

    当前只输出会改变分母的债券基金权益持仓排除，以及未知/冲突基金类型下
    holdings_snapshot 的 fail-closed 可观测决策。见模板第 6 章债券风险证据要求。

    Args:
        records: P4-S1 `snapshot.jsonl` 解析后的字段级记录。

    Returns:
        字段适用性决策元组。

    Raises:
        ValueError: 记录缺少 `fund_code`、`field_name` 或 `report_year` 非法时抛出。
    """

    records_by_fund: dict[str, list[Mapping[str, object]]] = {}
    for record in records:
        fund_code = _required_text(record, "fund_code")
        records_by_fund.setdefault(fund_code, []).append(record)

    decisions: list[FieldApplicabilityDecision] = []
    for fund_code, fund_records in sorted(records_by_fund.items()):
        decisions.extend(_fund_field_applicability_decisions(fund_code, fund_records))
    return tuple(decisions)


def derive_score_applicability_issues(
    records: Sequence[Mapping[str, object]],
) -> tuple[ScoreApplicabilityIssue, ...]:
    """从 snapshot 记录派生评分适用性替代 issue。

    当前实现对 exact `bond_fund` 保守生成聚合 `bond_risk_evidence_missing`，
    以防 `holdings_snapshot` 排除后被误判为通过。见模板第 6 章核心风险。

    Args:
        records: P4-S1 `snapshot.jsonl` 解析后的字段级记录。

    Returns:
        评分适用性 issue 元组。

    Raises:
        ValueError: 记录缺少 `fund_code`、`field_name` 或 `report_year` 非法时抛出。
    """

    records_by_fund: dict[str, list[Mapping[str, object]]] = {}
    for record in records:
        fund_code = _required_text(record, "fund_code")
        records_by_fund.setdefault(fund_code, []).append(record)

    issues: list[ScoreApplicabilityIssue] = []
    for fund_code, fund_records in sorted(records_by_fund.items()):
        classified_fund_type, _fund_type_reason = _unique_optional_text(
            fund_records,
            "classified_fund_type",
        )
        if classified_fund_type != BOND_FUND_TYPE:
            continue
        if not any(_is_bond_holdings_replacement_record(record) for record in fund_records):
            continue
        report_year = _fund_report_year_text(fund_records)
        issues.append(
            _bond_risk_evidence_missing_issue(
                fund_code=fund_code,
                report_year=report_year,
                classified_fund_type=classified_fund_type,
            )
        )
    return tuple(issues)


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
    errors_path: Path | None = None,
) -> ExtractionScoreResult:
    """读取 snapshot 并输出 P4-S2 字段级评分产物。

    Args:
        snapshot_path: P4-S1 输出的 `snapshot.jsonl`。
        source_csv: 精选基金池 CSV，用于选择最小 golden set。
        output_dir: 显式输出目录；为空时使用 snapshot 所在目录。
        thresholds: 显式评分阈值。
        golden_answer_path: strict golden answer JSON 路径；为空时不执行 correctness。
        errors_path: P4-S1 输出的 `errors.jsonl`；提供后纳入 failed_funds accounting。

    Returns:
        评分运行结果和输出路径。

    Raises:
        FileNotFoundError: snapshot、errors 或 CSV 不存在时抛出。
        ValueError: snapshot schema、阈值或 CSV 输入非法时抛出。
        OSError: 输出目录或文件写入失败时抛出。
    """

    records = load_snapshot_records(snapshot_path)
    failed_funds = load_snapshot_error_records(errors_path) if errors_path is not None else ()
    golden_set = select_minimal_golden_set(source_csv)
    return write_extraction_score_records(
        records=records,
        snapshot_path=snapshot_path,
        source_csv=source_csv,
        output_dir=output_dir,
        thresholds=thresholds,
        golden_answer_path=golden_answer_path,
        golden_set=golden_set,
        failed_funds=failed_funds,
    )


def write_extraction_score_records(
    *,
    records: Sequence[Mapping[str, object]],
    snapshot_path: Path,
    source_csv: Path,
    output_dir: Path | None = None,
    thresholds: ScoreThresholds = ScoreThresholds(),
    golden_answer_path: Path | None = None,
    golden_set: GoldenSetSelection | None = None,
    failed_funds: Sequence[FailedFundRow] = (),
) -> ExtractionScoreResult:
    """对已加载的 snapshot 记录写出字段级评分产物。

    Args:
        records: 已加载的 P4-S1 snapshot 记录。
        snapshot_path: snapshot 记录来源路径，用于输出元数据。
        source_csv: 精选基金池 CSV 路径。
        output_dir: 显式输出目录；为空时使用 snapshot 所在目录。
        thresholds: 显式评分阈值。
        golden_answer_path: strict golden answer JSON 路径；为空时不执行 correctness。
        golden_set: 最小 golden set；为空时写入单基金 gate 专用空选择。
        failed_funds: 已解析的完全抽取失败基金行。

    Returns:
        评分运行结果和输出路径。

    Raises:
        ValueError: snapshot schema 或阈值非法时抛出。
        OSError: 输出目录或文件写入失败时抛出。
    """

    field_scores = score_snapshot_records(records, thresholds=thresholds)
    fund_scores = score_fund_records(records, thresholds=thresholds)
    fund_quality = derive_fund_quality_records(records)
    field_applicability_decisions = derive_field_applicability_decisions(records)
    score_applicability_issues = derive_score_applicability_issues(records)
    resolved_golden_set = golden_set or GoldenSetSelection(
        source_csv=str(source_csv),
        records=(),
        excluded_categories=(),
        exclusion_reason="single-fund analyze quality gate does not select a minimal golden set",
    )
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
        fund_quality=fund_quality,
        field_applicability_decisions=field_applicability_decisions,
        score_applicability_issues=score_applicability_issues,
        failed_funds=tuple(failed_funds),
        golden_set=resolved_golden_set,
        thresholds=thresholds,
        correctness=correctness,
    )
    score_json_path.write_text(
        json.dumps(_score_json_payload(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    score_markdown_path.write_text(_score_markdown(result), encoding="utf-8")
    golden_set_path.write_text(
        json.dumps(asdict(resolved_golden_set), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def compare_snapshot_correctness(
    *,
    records: Sequence[Mapping[str, object]],
    golden_answer_path: Path | None,
) -> CorrectnessSummary:
    """用 strict golden answer JSON 对 snapshot 明确字段做 correctness 比对。

    当前 P5-S3 比较 snapshot `comparable_values` 明确暴露的白名单子字段；
    其他 golden 有效记录标记为 `unavailable`，不进入 correctness 分母。只有
    白名单字段/子字段且 snapshot 明确缺失时才记为 mismatch。见模板第 1 章产品本质
    的基金类型识别约束，以及模板第 2 章 R=A+B-C 的净值/基准字段约束。

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
            coverage_scope=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
            coverage_reason=CORRECTNESS_COVERAGE_NOT_CONFIGURED,
            covered_fund_codes=(),
            missing_fund_codes=_snapshot_fund_codes(records),
            coverage_required=False,
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
    coverage_scope, coverage_reason, covered_fund_codes, missing_fund_codes = _correctness_coverage(
        snapshot_fund_identities=_snapshot_fund_identities(records),
        golden_funds=golden_funds,
        record_results=record_results,
    )
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
        coverage_scope=coverage_scope,
        coverage_reason=coverage_reason,
        covered_fund_codes=covered_fund_codes,
        missing_fund_codes=missing_fund_codes,
        coverage_required=False,
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


def _failed_fund_row(record: Mapping[str, object], *, line_number: int) -> FailedFundRow:
    """把 snapshot error 记录转换为失败基金行。

    Args:
        record: `errors.jsonl` 中的单条 JSON object。
        line_number: JSONL 行号，用于错误信息。

    Returns:
        失败基金行。

    Raises:
        ValueError: `fund_code` 缺失或为空时抛出。
    """

    fund_code = _required_error_text(record, "fund_code", line_number)
    return FailedFundRow(
        fund_code=fund_code,
        fund_name=_optional_error_text(record, "fund_name"),
        app_category=_optional_error_text(record, "app_category"),
        report_year=_optional_error_int(record, "report_year", line_number),
        error_type=_optional_error_text(record, "error_type"),
        error_message=_optional_error_text(record, "error_message"),
    )


def _required_error_text(record: Mapping[str, object], key: str, line_number: int) -> str:
    """读取错误记录中的必需文本字段。

    Args:
        record: 错误记录。
        key: 字段名。
        line_number: JSONL 行号。

    Returns:
        非空文本。

    Raises:
        ValueError: 字段缺失或为空时抛出。
    """

    value = record.get(key)
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError(f"errors 第 {line_number} 行缺少必需字段：{key}")
    return text


def _optional_error_text(record: Mapping[str, object], key: str) -> str | None:
    """读取错误记录中的可选文本字段。

    Args:
        record: 错误记录。
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


def _optional_error_int(
    record: Mapping[str, object],
    key: str,
    line_number: int,
) -> int | None:
    """读取错误记录中的可选整数字段。

    Args:
        record: 错误记录。
        key: 字段名。
        line_number: JSONL 行号。

    Returns:
        整数；缺失时返回 `None`。

    Raises:
        ValueError: 字段存在但不是整数或整数字符串时抛出。
    """

    value = record.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"errors 第 {line_number} 行字段必须是整数：{key}")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ValueError(f"errors 第 {line_number} 行字段必须是整数：{key}")


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


def _required_snapshot_int(record: Mapping[str, object], key: str) -> int:
    """读取 snapshot 记录中的必需整数字段。

    Args:
        record: 单条 snapshot 记录。
        key: 字段名。

    Returns:
        整数字段值。

    Raises:
        ValueError: 字段缺失、为空或不是整数时抛出。
    """

    value = record.get(key)
    if value is None:
        raise ValueError(f"snapshot 记录缺少字段：{key}")
    if isinstance(value, bool):
        raise ValueError(f"snapshot 记录字段必须是整数：{key}")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ValueError(f"snapshot 记录字段必须是整数：{key}")


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

    classified_fund_type, _fund_type_reason = _unique_optional_text(
        records,
        "classified_fund_type",
    )
    scorable_records = _scorable_records(
        records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=False,
    )
    field_scores = _score_records_for_single_fund(
        scorable_records,
        thresholds=thresholds,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=False,
    )
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
        records=len(scorable_records),
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
    classified_fund_type: str | None = None,
    use_record_fund_type: bool = True,
) -> tuple[FieldScoreRow, ...]:
    """计算单只基金内部的字段级评分。

    Args:
        records: 单只基金的 snapshot 记录。
        thresholds: 显式评分阈值。
        classified_fund_type: 已解析的单基金类型，用于一致过滤指数质量字段。
        use_record_fund_type: 已解析类型为空时是否回看单条记录类型。

    Returns:
        字段级评分行。

    Raises:
        ValueError: 记录缺少 `field_name` / `field_group` 时抛出。
    """

    counters: dict[tuple[str, str], _FieldScoreCounter] = {}
    for record in _scorable_records(
        records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=use_record_fund_type,
    ):
        field_group = _required_text(record, "field_group")
        field_name = _required_text(record, "field_name")
        key = (field_group, field_name)
        counter = counters.setdefault(
            key,
            _FieldScoreCounter(field_group=field_group, field_name=field_name),
        )
        counter.records += 1
        if _record_is_covered(record):
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


def _build_fund_quality_row(
    fund_code: str,
    records: Sequence[Mapping[str, object]],
) -> FundQualityRow:
    """构造单只基金质量派生判断。

    Args:
        fund_code: 基金代码。
        records: 该基金对应的 snapshot 记录。

    Returns:
        单基金质量派生判断。

    Raises:
        ValueError: 记录缺少 `field_name` 时抛出。
    """

    fund_name, fund_name_reason = _unique_optional_text(records, "fund_name")
    app_category, app_category_reason = _unique_optional_text(records, "app_category")
    classified_fund_type, fund_type_reason = _unique_optional_text(records, "classified_fund_type")
    scorable_records = _scorable_records(
        records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=False,
    )
    missing_fields = _missing_fields_by_priority(
        scorable_records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=False,
    )
    app_category_status = _app_category_status(app_category, classified_fund_type)
    contract_applicability = _derive_contract_applicability(
        classified_fund_type=classified_fund_type,
        app_category=app_category,
        app_category_status=app_category_status,
        fund_type_reason=fund_type_reason,
    )
    # FundQualityRow 的缺失率是基金类型适用性过滤后的 applicable rate；
    # 原始/适用分母差异写入 field_applicability_decisions，避免 FQ4 阈值语义漂移。
    total_field_count = len(scorable_records)
    missing_field_count = sum(1 for record in scorable_records if not _record_is_covered(record))
    reasons = [
        fund_name_reason,
        app_category_reason,
        fund_type_reason,
        _app_category_reason(app_category, classified_fund_type, app_category_status),
        contract_applicability.reason,
    ]
    return FundQualityRow(
        fund_code=fund_code,
        fund_name=fund_name,
        app_category=app_category,
        classified_fund_type=classified_fund_type,
        app_category_status=app_category_status,
        preferred_lens_status=contract_applicability.status,
        preferred_lens_key=contract_applicability.preferred_lens_key,
        missing_field_count=missing_field_count,
        total_field_count=total_field_count,
        missing_field_rate=_rate(missing_field_count, total_field_count),
        missing_p0_fields=missing_fields[PRIORITY_P0],
        missing_p1_fields=missing_fields[PRIORITY_P1],
        reason="；".join(reason for reason in reasons if reason),
        contract_template_id=contract_applicability.contract_template_id,
        item_rule_template_id=contract_applicability.item_rule_template_id,
        preferred_lens_chapters=contract_applicability.preferred_lens_chapters,
        preferred_lens_unresolved_chapter_ids=(
            contract_applicability.preferred_lens_unresolved_chapter_ids
        ),
        item_rule_decisions=contract_applicability.item_rule_decisions,
    )


def _fund_field_applicability_decisions(
    fund_code: str,
    records: Sequence[Mapping[str, object]],
) -> tuple[FieldApplicabilityDecision, ...]:
    """构造单基金字段适用性决策。

    Args:
        fund_code: 基金代码。
        records: 单基金 snapshot 记录。

    Returns:
        适用性决策元组。

    Raises:
        ValueError: `report_year` 非法时抛出。
    """

    classified_fund_type, _fund_type_reason = _unique_optional_text(records, "classified_fund_type")
    decisions: list[FieldApplicabilityDecision] = []
    if not any(_required_text(record, "field_name") == HOLDINGS_SNAPSHOT_FIELD_NAME for record in records):
        return ()

    raw_records = _records_after_index_applicability(
        records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=False,
    )
    raw_total_field_count = len(raw_records)
    raw_missing_field_count = sum(1 for record in raw_records if not _record_is_covered(record))
    applicable_records = _scorable_records(
        records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=False,
    )
    applicable_missing_field_count = sum(
        1 for record in applicable_records if not _record_is_covered(record)
    )
    report_year = _fund_report_year_text(records)
    if classified_fund_type == BOND_FUND_TYPE:
        replacement_issue_id = _score_applicability_issue_id(
            fund_code=fund_code,
            report_year=report_year,
            field_name=HOLDINGS_SNAPSHOT_FIELD_NAME,
            issue_code=BOND_RISK_EVIDENCE_MISSING_ISSUE_CODE,
            contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        )
        decisions.append(
            FieldApplicabilityDecision(
                fund_code=fund_code,
                report_year=report_year,
                field_name=HOLDINGS_SNAPSHOT_FIELD_NAME,
                classified_fund_type=classified_fund_type,
                applicability_status=APPLICABILITY_STATUS_NOT_APPLICABLE_REPLACED,
                reason_code=BOND_HOLDINGS_NOT_APPLICABLE_REASON,
                replacement_field_name=BOND_RISK_REPLACEMENT_FIELD_NAME,
                contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
                denominator_effect=DENOMINATOR_EFFECT_EXCLUDED_WITH_REPLACEMENT_ISSUE,
                raw_total_field_count=raw_total_field_count,
                raw_missing_field_count=raw_missing_field_count,
                raw_missing_field_rate=_rate(raw_missing_field_count, raw_total_field_count),
                applicable_total_field_count=len(applicable_records),
                applicable_missing_field_count=applicable_missing_field_count,
                applicable_missing_field_rate=_rate(
                    applicable_missing_field_count,
                    len(applicable_records),
                ),
                excluded_non_applicable_fields=(HOLDINGS_SNAPSHOT_FIELD_NAME,),
                replacement_issue_ids=(replacement_issue_id,),
            )
        )
    elif classified_fund_type is None:
        decisions.append(
            FieldApplicabilityDecision(
                fund_code=fund_code,
                report_year=report_year,
                field_name=HOLDINGS_SNAPSHOT_FIELD_NAME,
                classified_fund_type=None,
                applicability_status=APPLICABILITY_STATUS_UNKNOWN_FAIL_CLOSED,
                reason_code="unknown_fund_type_fail_closed",
                replacement_field_name=None,
                contract_id=None,
                denominator_effect=DENOMINATOR_EFFECT_INCLUDED_FAIL_CLOSED,
                raw_total_field_count=raw_total_field_count,
                raw_missing_field_count=raw_missing_field_count,
                raw_missing_field_rate=_rate(raw_missing_field_count, raw_total_field_count),
                applicable_total_field_count=len(applicable_records),
                applicable_missing_field_count=applicable_missing_field_count,
                applicable_missing_field_rate=_rate(
                    applicable_missing_field_count,
                    len(applicable_records),
                ),
                excluded_non_applicable_fields=(),
                replacement_issue_ids=(),
            )
        )
    return tuple(decisions)


def _bond_risk_evidence_missing_issue(
    *,
    fund_code: str,
    report_year: str,
    classified_fund_type: str,
) -> ScoreApplicabilityIssue:
    """构造债券风险替代证据缺口 issue。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份文本。
        classified_fund_type: 已解析基金类型。

    Returns:
        `bond_risk_evidence_missing` issue。

    Raises:
        无显式抛出。
    """

    group_ids = tuple(group.group_id for group in BOND_RISK_EVIDENCE_GROUPS)
    return ScoreApplicabilityIssue(
        issue_id=_score_applicability_issue_id(
            fund_code=fund_code,
            report_year=report_year,
            field_name=HOLDINGS_SNAPSHOT_FIELD_NAME,
            issue_code=BOND_RISK_EVIDENCE_MISSING_ISSUE_CODE,
            contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        ),
        issue_code=BOND_RISK_EVIDENCE_MISSING_ISSUE_CODE,
        severity="warn",
        fund_code=fund_code,
        report_year=report_year,
        field_name=HOLDINGS_SNAPSHOT_FIELD_NAME,
        classified_fund_type=classified_fund_type,
        replacement_field_name=BOND_RISK_REPLACEMENT_FIELD_NAME,
        contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        priority=FIELD_PRIORITY_BY_NAME[HOLDINGS_SNAPSHOT_FIELD_NAME],
        message=(
            f"基金 `{fund_code}` 为债券基金，权益持仓型 holdings_snapshot 不进入股票持仓分母；"
            f"但 `{BOND_RISK_EVIDENCE_CONTRACT_ID}` 尚无已复核债券风险证据。"
        ),
        baseline_blocking=True,
        rule_code_hint="FQ2F",
        denominator_excluded_fields=(HOLDINGS_SNAPSHOT_FIELD_NAME,),
        required_evidence_groups=group_ids,
        missing_evidence_groups=group_ids,
    )


def _score_applicability_issue_id(
    *,
    fund_code: str,
    report_year: str,
    field_name: str,
    issue_code: str,
    contract_id: str,
) -> str:
    """生成确定性 score applicability issue id。

    Args:
        fund_code: 六位基金代码。
        report_year: 年报年份文本。
        field_name: 原始字段名。
        issue_code: issue 分类码。
        contract_id: 替代证据契约编号。

    Returns:
        稳定小写 issue id。

    Raises:
        无显式抛出。
    """

    return f"score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}"


def _fund_report_year_text(records: Sequence[Mapping[str, object]]) -> str:
    """读取单基金 report_year 文本。

    Args:
        records: 单基金 snapshot 记录。

    Returns:
        唯一年份文本；缺失时返回 `unknown-year`，冲突时也 fail-closed 为 `unknown-year`。

    Raises:
        ValueError: 存在非整数年份字段时抛出。
    """

    values = sorted(
        {
            _required_snapshot_int(record, "report_year")
            for record in records
            if record.get("report_year") is not None
        }
    )
    if len(values) == 1:
        return str(values[0])
    return "unknown-year"


def _is_bond_holdings_replacement_record(record: Mapping[str, object]) -> bool:
    """判断记录是否触发债券基金 holdings 替代契约。

    Args:
        record: snapshot 字段记录。

    Returns:
        `holdings_snapshot` 记录返回 `True`。

    Raises:
        ValueError: 记录缺少 `field_name` 时抛出。
    """

    return _required_text(record, "field_name") == HOLDINGS_SNAPSHOT_FIELD_NAME


def _records_after_index_applicability(
    records: Sequence[Mapping[str, object]],
    *,
    classified_fund_type: str | None = None,
    use_record_fund_type: bool = True,
) -> tuple[Mapping[str, object], ...]:
    """过滤既有指数质量适用性后的记录。

    Args:
        records: snapshot 记录集合。
        classified_fund_type: 已解析的单基金类型；为空时使用记录自身类型。
        use_record_fund_type: 已解析类型为空时是否回看单条记录类型。

    Returns:
        未应用债券 holdings 替代规则的基准评分记录。

    Raises:
        ValueError: 指数质量记录缺少 `field_name` 时抛出。
    """

    return tuple(
        record
        for record in records
        if not _is_non_applicable_index_quality_record(
            record,
            classified_fund_type=classified_fund_type,
            use_record_fund_type=use_record_fund_type,
        )
    )


def _unique_optional_text(
    records: Sequence[Mapping[str, object]],
    key: str,
) -> tuple[str | None, str]:
    """读取基金级字段，并显式识别多值冲突。

    Args:
        records: 单基金 snapshot 记录。
        key: 基金级字段名。

    Returns:
        `(value, reason)`；字段冲突时 value 为 `None`。

    Raises:
        无显式抛出。
    """

    values = sorted(
        {
            str(record.get(key)).strip()
            for record in records
            if record.get(key) is not None and str(record.get(key)).strip()
        }
    )
    if len(values) == 1:
        return values[0], ""
    if len(values) > 1:
        return None, f"{key} 存在冲突值：{', '.join(values)}"
    return None, f"{key} 缺失"


def _missing_fields_by_priority(
    records: Sequence[Mapping[str, object]],
    *,
    classified_fund_type: str | None = None,
    use_record_fund_type: bool = True,
) -> dict[str, tuple[str, ...]]:
    """按字段优先级统计缺失字段。

    Args:
        records: 单基金 snapshot 记录。
        classified_fund_type: 已解析的单基金类型，用于一致过滤非适用指数质量字段。
        use_record_fund_type: 已解析类型为空时是否回看单条记录类型。

    Returns:
        P0/P1 缺失字段名映射。

    Raises:
        ValueError: 记录缺少 `field_name` 时抛出。
    """

    missing_by_priority: dict[str, set[str]] = {PRIORITY_P0: set(), PRIORITY_P1: set()}
    for record in _scorable_records(
        records,
        classified_fund_type=classified_fund_type,
        use_record_fund_type=use_record_fund_type,
    ):
        field_name = _required_text(record, "field_name")
        if _record_is_covered(record):
            continue
        priority = FIELD_PRIORITY_BY_NAME.get(field_name, UNKNOWN_FIELD_PRIORITY)
        if priority in missing_by_priority:
            missing_by_priority[priority].add(field_name)
    return {priority: tuple(sorted(fields)) for priority, fields in missing_by_priority.items()}


def _record_is_covered(record: Mapping[str, object]) -> bool:
    """判断 snapshot 记录是否满足字段 coverage。

    `holdings_snapshot` 的 coverage 以股票持仓明细为准，避免只有行业分布时把
    模板第 3 章“实际投资行为”的股票持仓缺口误计为已覆盖。

    Args:
        record: snapshot 字段记录。

    Returns:
        记录满足字段 coverage 时返回 `True`。

    Raises:
        ValueError: `holdings_snapshot.comparable_values` 结构非法时抛出。
    """

    if not _truthy_bool(record.get("value_present")):
        return False
    if _required_text(record, "field_name") != HOLDINGS_SNAPSHOT_FIELD_NAME:
        return True
    comparable_values = _record_comparable_values(record)
    top_holdings_status = _optional_scalar_text(comparable_values.get(TOP_HOLDINGS_STATUS_SUB_FIELD))
    top_holdings_source = _optional_scalar_text(comparable_values.get(TOP_HOLDINGS_SOURCE_SUB_FIELD))
    return (top_holdings_status, top_holdings_source) in TOP_HOLDINGS_COVERED_STATUS_SOURCE_PAIRS


def _scorable_records(
    records: Sequence[Mapping[str, object]],
    *,
    classified_fund_type: str | None = None,
    use_record_fund_type: bool = True,
) -> tuple[Mapping[str, object], ...]:
    """过滤非适用字段后的评分记录。

    Args:
        records: snapshot 记录集合。
        classified_fund_type: 已解析的单基金类型；为空时使用记录自身类型。
        use_record_fund_type: 已解析类型为空时是否回看单条记录类型。

    Returns:
        参与 coverage、traceability 和缺失分母的记录。

    Raises:
        ValueError: 适用性判断记录缺少 `field_name` 时抛出。
    """

    return tuple(
        record
        for record in records
        if not _is_non_applicable_index_quality_record(
            record,
            classified_fund_type=classified_fund_type,
            use_record_fund_type=use_record_fund_type,
        )
        and not _is_bond_holdings_replacement_record_for_type(
            record,
            classified_fund_type=classified_fund_type,
            use_record_fund_type=use_record_fund_type,
        )
    )


def _is_bond_holdings_replacement_record_for_type(
    record: Mapping[str, object],
    *,
    classified_fund_type: str | None = None,
    use_record_fund_type: bool = True,
) -> bool:
    """判断记录是否为 exact bond_fund 下被替代的权益持仓字段。

    Args:
        record: snapshot 字段记录。
        classified_fund_type: 已解析的单基金类型；为空时读取记录上的类型。
        use_record_fund_type: 已解析类型为空时是否回看单条记录类型。

    Returns:
        exact `bond_fund` 的 `holdings_snapshot` 返回 `True`；未知或冲突类型返回 `False`。

    Raises:
        ValueError: 记录缺少 `field_name` 时抛出。
    """

    if _required_text(record, "field_name") != HOLDINGS_SNAPSHOT_FIELD_NAME:
        return False
    fund_type = classified_fund_type
    if fund_type is None and use_record_fund_type:
        fund_type = _optional_record_text(record, "classified_fund_type")
    return fund_type == BOND_FUND_TYPE


def _is_non_applicable_index_quality_record(
    record: Mapping[str, object],
    *,
    classified_fund_type: str | None = None,
    use_record_fund_type: bool = True,
) -> bool:
    """判断记录是否为当前基金类型下不适用的指数质量字段。

    Args:
        record: snapshot 字段记录。
        classified_fund_type: 已解析的单基金类型；为空时读取记录上的类型。
        use_record_fund_type: 已解析类型为空时是否回看单条记录类型。

    Returns:
        非指数基金的 `index_profile` / `tracking_error` 返回 `True`；
        指数基金、增强指数基金和未知基金类型保持 `False`，继续保守评分。

    Raises:
        ValueError: 指数质量记录缺少 `field_name` 时抛出。
    """

    field_name = _required_text(record, "field_name")
    if field_name not in INDEX_QUALITY_FIELD_NAMES:
        return False
    fund_type = classified_fund_type
    if fund_type is None and use_record_fund_type:
        fund_type = _optional_record_text(record, "classified_fund_type")
    if fund_type is None:
        return False
    return fund_type not in INDEX_QUALITY_APPLICABLE_FUND_TYPES


def _app_category_status(app_category: str | None, classified_fund_type: str | None) -> str:
    """判断 App 类别与基金类型是否明确冲突。

    Args:
        app_category: App 类别。
        classified_fund_type: 系统基金类型。

    Returns:
        `match / conflict / unknown`。

    Raises:
        无显式抛出。
    """

    if not app_category or not classified_fund_type:
        return APP_CATEGORY_STATUS_UNKNOWN
    allowed_types = APP_CATEGORY_ALLOWED_FUND_TYPES.get(app_category)
    if allowed_types is None:
        return APP_CATEGORY_STATUS_UNKNOWN
    if classified_fund_type in allowed_types:
        return APP_CATEGORY_STATUS_MATCH
    return APP_CATEGORY_STATUS_CONFLICT


def _derive_contract_applicability(
    *,
    classified_fund_type: str | None,
    app_category: str | None,
    app_category_status: str,
    fund_type_reason: str,
) -> _ContractApplicability:
    """派生单基金模板契约适用性事实。

    本函数只使用模板 manifest 与已识别基金类型，见模板第 0-7 章
    CHAPTER_CONTRACT 和第 1/2 章 ITEM_RULE；不读取报告 Markdown 或基金文档。

    Args:
        classified_fund_type: 系统识别基金类型。
        app_category: App 类别。
        app_category_status: App 类别与基金类型匹配状态。
        fund_type_reason: 基金类型字段唯一性判断原因。

    Returns:
        FQ5 模板契约适用性派生结果。

    Raises:
        无显式抛出；manifest/evaluator 异常会转为 `mismatch` 结果。
    """

    if "classified_fund_type 存在冲突值" in fund_type_reason:
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_MISMATCH,
            preferred_lens_key=None,
            reason=fund_type_reason,
        )
    if app_category in TEMPLATE_NOT_APPLICABLE_CATEGORIES:
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_NOT_APPLICABLE,
            preferred_lens_key=None,
            reason=f"App 类别 `{app_category}` 不适用当前 8 章基金分析模板",
        )
    if classified_fund_type is None:
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_NOT_APPLICABLE,
            preferred_lens_key=None,
            reason=f"基金类型缺失，FQ5 不声明模板契约适用性；{fund_type_reason}",
        )
    if app_category_status == APP_CATEGORY_STATUS_CONFLICT:
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_MISMATCH,
            preferred_lens_key=classified_fund_type,
            reason=f"App 类别与基金类型冲突，不能稳定应用模板契约：{classified_fund_type}",
        )
    if not _is_supported_contract_fund_type(classified_fund_type):
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_MISMATCH,
            preferred_lens_key=classified_fund_type,
            reason=f"基金类型 `{classified_fund_type}` 不受当前模板契约支持",
        )

    fund_type = cast(FundType, classified_fund_type)
    contract_manifest = load_template_contract_manifest()
    chapter_resolutions: list[PreferredLensChapterResolution] = []
    unresolved_chapter_ids: list[int] = []
    resolution_errors: list[str] = []
    for chapter in contract_manifest.chapters:
        try:
            lens = resolve_preferred_lens(chapter.chapter_id, fund_type)
            chapter_resolutions.append(
                PreferredLensChapterResolution(
                    chapter_id=chapter.chapter_id,
                    title=chapter.title,
                    lens_key=lens.fund_type,
                    used_default=lens.fund_type == "default",
                )
            )
        except ValueError as exc:
            unresolved_chapter_ids.append(chapter.chapter_id)
            resolution_errors.append(f"chapter_id={chapter.chapter_id}: {exc}")
    if unresolved_chapter_ids:
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_MISMATCH,
            preferred_lens_key=fund_type,
            preferred_lens_chapters=tuple(chapter_resolutions),
            preferred_lens_unresolved_chapter_ids=tuple(unresolved_chapter_ids),
            reason=f"CHAPTER_CONTRACT preferred_lens 解析失败：{'; '.join(resolution_errors)}",
            contract_template_id=contract_manifest.template_id,
        )

    try:
        item_rule_manifest = load_template_item_rule_manifest()
        item_rule_decisions = tuple(
            ItemRuleDecisionSummary(
                rule_id=decision.rule_id,
                chapter_id=decision.chapter_id,
                item_title=decision.item_title,
                triggered=decision.triggered,
                status=decision.status,
                missing_behavior=decision.missing_behavior,
            )
            for decision in evaluate_template_item_rules(fund_type=fund_type, facets=())
        )
    except ValueError as exc:
        return _contract_applicability_result(
            status=PREFERRED_LENS_STATUS_MISMATCH,
            preferred_lens_key=fund_type,
            preferred_lens_chapters=tuple(chapter_resolutions),
            reason=f"ITEM_RULE evaluator 运行失败：{exc}",
            contract_template_id=contract_manifest.template_id,
        )

    return _contract_applicability_result(
        status=PREFERRED_LENS_STATUS_RESOLVED,
        preferred_lens_key=fund_type,
        preferred_lens_chapters=tuple(chapter_resolutions),
        item_rule_decisions=item_rule_decisions,
        reason="8 个模板章节均已解析 preferred_lens，ITEM_RULE 已完成确定性适用性评估",
        contract_template_id=contract_manifest.template_id,
        item_rule_template_id=item_rule_manifest.template_id,
    )


def _contract_applicability_result(
    *,
    status: str,
    preferred_lens_key: str | None,
    reason: str,
    preferred_lens_chapters: tuple[PreferredLensChapterResolution, ...] = (),
    preferred_lens_unresolved_chapter_ids: tuple[int, ...] = (),
    item_rule_decisions: tuple[ItemRuleDecisionSummary, ...] = (),
    contract_template_id: str | None = None,
    item_rule_template_id: str | None = None,
) -> _ContractApplicability:
    """构造内部模板契约适用性结果。

    Args:
        status: FQ5 适用性状态。
        preferred_lens_key: 当前尝试应用的 lens key。
        reason: 状态原因。
        preferred_lens_chapters: 每章 lens 解析事实。
        preferred_lens_unresolved_chapter_ids: 未解析章节编号。
        item_rule_decisions: ITEM_RULE 决策摘要。
        contract_template_id: CHAPTER_CONTRACT manifest 标识。
        item_rule_template_id: ITEM_RULE manifest 标识。

    Returns:
        `_ContractApplicability` 对象。

    Raises:
        无显式抛出。
    """

    return _ContractApplicability(
        status=status,
        preferred_lens_key=preferred_lens_key,
        preferred_lens_chapters=preferred_lens_chapters,
        preferred_lens_unresolved_chapter_ids=preferred_lens_unresolved_chapter_ids,
        item_rule_decisions=item_rule_decisions,
        reason=reason,
        contract_template_id=contract_template_id,
        item_rule_template_id=item_rule_template_id,
    )


def _is_supported_contract_fund_type(value: str) -> bool:
    """判断文本是否为当前模板契约支持的基金类型。

    Args:
        value: 基金类型文本。

    Returns:
        属于当前 `FundType` 集合时返回 `True`。

    Raises:
        无显式抛出。
    """

    return value in SUPPORTED_CONTRACT_FUND_TYPES


def _app_category_reason(
    app_category: str | None,
    classified_fund_type: str | None,
    status: str,
) -> str:
    """构造 App 类别状态说明。

    Args:
        app_category: App 类别。
        classified_fund_type: 系统基金类型。
        status: App 类别状态。

    Returns:
        状态说明。

    Raises:
        无显式抛出。
    """

    if status == APP_CATEGORY_STATUS_CONFLICT:
        return f"App 类别 `{app_category}` 与基金类型 `{classified_fund_type}` 明确冲突"
    if status == APP_CATEGORY_STATUS_MATCH:
        return f"App 类别 `{app_category}` 与基金类型 `{classified_fund_type}` 匹配"
    return "App 类别无法映射或基金类型缺失，类别冲突判断为 unknown"


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


def _snapshot_fund_identities(records: Sequence[Mapping[str, object]]) -> tuple[tuple[str, int], ...]:
    """读取当前 snapshot run 中涉及的基金代码和年报年份。

    Args:
        records: P4-S1 snapshot 记录。

    Returns:
        去重排序后的 `(fund_code, report_year)`。

    Raises:
        ValueError: snapshot 记录缺少 `fund_code` 或 `report_year` 时抛出。
    """

    return tuple(
        sorted(
            {
                (_required_text(record, "fund_code"), _required_snapshot_int(record, "report_year"))
                for record in records
            }
        )
    )


def _snapshot_fund_codes(records: Sequence[Mapping[str, object]]) -> tuple[str, ...]:
    """读取当前 snapshot run 中涉及的基金代码。

    Args:
        records: P4-S1 snapshot 记录。

    Returns:
        去重排序后的基金代码。

    Raises:
        ValueError: snapshot 记录缺少 `fund_code` 时抛出。
    """

    return tuple(sorted({_required_text(record, "fund_code") for record in records}))


def _correctness_coverage(
    *,
    snapshot_fund_identities: tuple[tuple[str, int], ...],
    golden_funds: Sequence[GoldenAnswerFund],
    record_results: Sequence[CorrectnessRecordResult],
) -> tuple[str, str, tuple[str, ...], tuple[str, ...]]:
    """派生当前 run 的 strict golden 覆盖范围。

    该函数只使用 strict golden answer 与当前 snapshot 的同源比对结果，不用
    其它间接证据推断覆盖。见模板第 1 章产品本质和第 2 章 R=A+B-C 的
    correctness oracle 边界。

    Args:
        snapshot_fund_identities: 当前 run 中的基金代码和年报年份。
        golden_funds: strict golden answer 中的基金集合。
        record_results: 字段级 correctness 比对结果。

    Returns:
        `(coverage_scope, coverage_reason, covered_fund_codes, missing_fund_codes)`。

    Raises:
        无显式抛出。
    """

    if not snapshot_fund_identities:
        return (
            CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
            CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
            (),
            (),
        )
    snapshot_fund_codes = tuple(sorted({fund_code for fund_code, _ in snapshot_fund_identities}))
    golden_codes = {fund.fund_code for fund in golden_funds}
    golden_identities = {(fund.fund_code, fund.report_year) for fund in golden_funds}
    target_identities = set(snapshot_fund_identities)
    comparable_codes = {
        row.fund_code
        for row in record_results
        if (row.fund_code, row.report_year) in target_identities
        and row.status in {CORRECTNESS_MATCH, CORRECTNESS_MISMATCH}
    }
    target_results = [
        row for row in record_results if (row.fund_code, row.report_year) in target_identities
    ]
    covered_fund_codes = tuple(sorted(comparable_codes))
    missing_fund_codes = tuple(code for code in snapshot_fund_codes if code not in comparable_codes)
    if all(code not in golden_codes for code in snapshot_fund_codes):
        return (
            CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
            CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
            (),
            snapshot_fund_codes,
        )
    if not any(identity in golden_identities for identity in snapshot_fund_identities):
        return (
            CORRECTNESS_COVERAGE_YEAR_NOT_COVERED,
            CORRECTNESS_COVERAGE_YEAR_NOT_COVERED,
            (),
            snapshot_fund_codes,
        )
    if target_results and not comparable_codes:
        return (
            CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS,
            CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS,
            (),
            snapshot_fund_codes,
        )
    if missing_fund_codes:
        return (
            CORRECTNESS_COVERAGE_PARTIALLY_COVERED,
            CORRECTNESS_COVERAGE_PARTIALLY_COVERED,
            covered_fund_codes,
            missing_fund_codes,
        )
    if any(row.status == CORRECTNESS_UNAVAILABLE for row in target_results):
        return (
            CORRECTNESS_COVERAGE_PARTIALLY_COVERED,
            CORRECTNESS_COVERAGE_PARTIALLY_COVERED,
            covered_fund_codes,
            missing_fund_codes,
        )
    return (
        CORRECTNESS_COVERAGE_COVERED,
        CORRECTNESS_COVERAGE_COVERED,
        covered_fund_codes,
        missing_fund_codes,
    )


def _snapshot_actual_index(
    records: Sequence[Mapping[str, object]],
) -> dict[tuple[str, int, str, str], str | None]:
    """构造 snapshot 可比字段索引。

    Args:
        records: P4-S1 snapshot 记录。

    Returns:
        `(fund_code, report_year, field_name, sub_field)` 到实际值的索引；
        值为 `None` 表示字段明确缺失。

    Raises:
        ValueError: snapshot 记录缺少 `fund_code` 或 `field_name` 时抛出。
    """

    actual_index: dict[tuple[str, int, str, str], str | None] = {}
    for record in records:
        fund_code = _required_text(record, "fund_code")
        report_year = _required_snapshot_int(record, "report_year")
        field_name = _required_text(record, "field_name")
        has_explicit_comparable_values = "comparable_values" in record
        if has_explicit_comparable_values:
            for sub_field in COMPARABLE_SUB_FIELDS_BY_FIELD.get(field_name, ()):
                actual_index.setdefault((fund_code, report_year, field_name, sub_field), None)
        for sub_field, value in _record_comparable_values(record).items():
            if not _is_comparable_sub_field(field_name, sub_field):
                continue
            actual_value = _optional_scalar_text(value)
            if actual_value is not None:
                actual_index[(fund_code, report_year, field_name, sub_field)] = actual_value
        if field_name == CLASSIFIED_FUND_TYPE_FIELD:
            actual_value = _optional_record_text(record, CLASSIFIED_FUND_TYPE_FIELD)
            if not _truthy_bool(record.get("value_present")):
                actual_value = None
            actual_index.setdefault(
                (
                    fund_code,
                    report_year,
                    CLASSIFIED_FUND_TYPE_FIELD,
                    CLASSIFIED_FUND_TYPE_SUB_FIELD,
                ),
                actual_value,
            )
    return actual_index


def _compare_golden_funds(
    golden_funds: Sequence[GoldenAnswerFund],
    actual_index: Mapping[tuple[str, int, str, str], str | None],
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
    actual_index: Mapping[tuple[str, int, str, str], str | None],
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
    report_year = record.report_year
    field_name = record.field_name
    sub_field = record.sub_field
    expected_value = record.expected_value
    confidence = record.confidence
    source = record.source
    normalized_expected = _normalize_comparable_value(
        expected_value,
        field_name=field_name,
        sub_field=sub_field,
    )
    key = (fund_code, report_year, field_name, sub_field)
    if key not in actual_index:
        return CorrectnessRecordResult(
            fund_code=fund_code,
            report_year=report_year,
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
            report_year=report_year,
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
    normalized_actual = _normalize_comparable_value(
        actual_value,
        field_name=field_name,
        sub_field=sub_field,
    )
    status = CORRECTNESS_MATCH if normalized_actual == normalized_expected else CORRECTNESS_MISMATCH
    reason = (
        "保守 normalize 后完全一致。"
        if status == CORRECTNESS_MATCH
        else "保守 normalize 后不一致。"
    )
    return CorrectnessRecordResult(
        fund_code=fund_code,
        report_year=report_year,
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


def _record_comparable_values(record: Mapping[str, object]) -> Mapping[str, object]:
    """读取 snapshot 记录中的 `comparable_values`。

    Args:
        record: snapshot 记录。

    Returns:
        子字段到原始可比值的映射；旧 snapshot 或空值返回空映射。

    Raises:
        ValueError: `comparable_values` 存在但不是对象时抛出。
    """

    value = record.get("comparable_values")
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("snapshot 记录 comparable_values 必须是 JSON object")
    return value


def _is_comparable_sub_field(field_name: str, sub_field: object) -> bool:
    """判断子字段是否在 correctness 可比白名单内。

    Args:
        field_name: snapshot 字段名。
        sub_field: comparable_values 中的子字段名。

    Returns:
        子字段名是文本且属于该字段白名单时返回 `True`。

    Raises:
        无显式抛出。
    """

    if not isinstance(sub_field, str):
        return False
    return sub_field in COMPARABLE_SUB_FIELDS_BY_FIELD.get(field_name, ())


def _optional_scalar_text(value: object) -> str | None:
    """把 correctness 可比值转换成非空文本。

    Args:
        value: JSON 解析后的原始值。

    Returns:
        非空标量文本；嵌套结构、空值和空白文本返回 `None`。

    Raises:
        无显式抛出。
    """

    if value is None or isinstance(value, (Mapping, list, tuple, set)):
        return None
    text = str(value).strip()
    return text or None


def _normalize_comparable_value(
    value: object,
    *,
    field_name: str | None = None,
    sub_field: str | None = None,
) -> str:
    """对可比字段执行保守 normalize。

    默认只做大小写、全角空白和连续空白归一化；仅对 benchmark 字段的
    benchmark_name / benchmark_text 额外移除中文字符之间的视觉空白；仅对
    basic_identity.inception_date 的完整中文年月日日期移除日期单位周围视觉空白。
    不做同义词映射、不补值，避免用间接证据或经验推断修正 correctness。

    Args:
        value: 原始值。
        field_name: correctness 字段名。
        sub_field: correctness 子字段名。

    Returns:
        归一化后的文本。

    Raises:
        无显式抛出。
    """

    text = str(value).strip().replace("\u3000", " ")
    if _is_benchmark_visual_whitespace_field(field_name, sub_field):
        text = INTRA_CHINESE_VISUAL_WHITESPACE_PATTERN.sub("", text)
    if _is_chinese_date_visual_whitespace_field(field_name, sub_field):
        text = _normalize_chinese_date_visual_whitespace(text)
    return " ".join(text.split()).casefold()


def _is_benchmark_visual_whitespace_field(
    field_name: str | None,
    sub_field: str | None,
) -> bool:
    """判断 correctness 字段是否允许 benchmark 视觉空白归一化。

    Args:
        field_name: correctness 字段名。
        sub_field: correctness 子字段名。

    Returns:
        仅 `benchmark.benchmark_name` / `benchmark.benchmark_text` 返回 `True`。

    Raises:
        无显式抛出。
    """

    return field_name == BENCHMARK_FIELD_NAME and sub_field in BENCHMARK_NORMALIZED_SUB_FIELDS


def _is_chinese_date_visual_whitespace_field(
    field_name: str | None,
    sub_field: str | None,
) -> bool:
    """判断 correctness 字段是否允许中文年月日视觉空白归一化。

    Args:
        field_name: correctness 字段名。
        sub_field: correctness 子字段名。

    Returns:
        仅 `basic_identity.inception_date` 返回 `True`。

    Raises:
        无显式抛出。
    """

    return field_name == BASIC_IDENTITY_FIELD_NAME and sub_field == INCEPTION_DATE_SUB_FIELD


def _normalize_chinese_date_visual_whitespace(text: str) -> str:
    """归一化完整中文年月日日期中的视觉空白。

    只处理整体符合 `YYYY 年 M 月 D 日` 形态的日期文本，避免把非日期说明、
    基金名称或其他中文字符串中的空格误删。

    Args:
        text: 已完成首尾裁剪和全角空白替换的原始文本。

    Returns:
        若文本是完整中文日期，返回移除内部空白后的日期；否则原样返回。

    Raises:
        无显式抛出。
    """

    if CHINESE_DATE_VISUAL_WHITESPACE_PATTERN.fullmatch(text):
        return "".join(text.split())
    return text


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
        "fund_quality": [asdict(row) for row in result.fund_quality],
        "field_applicability_decisions": [
            asdict(row) for row in result.field_applicability_decisions
        ],
        "score_applicability_issues": [
            asdict(row) for row in result.score_applicability_issues
        ],
        "failed_funds": [asdict(row) for row in result.failed_funds],
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
        f"- failed_fund_count: {len(result.failed_funds)}",
        f"- score_applicability_issue_count: {len(result.score_applicability_issues)}",
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
            "## Fund Quality",
            "",
            "| fund_code | fund_name | app_category | classified_fund_type | app_category_status | preferred_lens_status | preferred_lens_key | resolved_chapters | unresolved_chapters | item_rule_decisions | missing_field_rate | missing_p0_fields | missing_p1_fields | reason |",
            "|---|---|---|---|---|---|---|---:|---|---|---:|---|---|---|",
        ]
    )
    for row in result.fund_quality:
        lines.append(
            "| "
            f"{row.fund_code} | "
            f"{row.fund_name or ''} | "
            f"{row.app_category or ''} | "
            f"{row.classified_fund_type or ''} | "
            f"{row.app_category_status} | "
            f"{row.preferred_lens_status} | "
            f"{row.preferred_lens_key or ''} | "
            f"{len(row.preferred_lens_chapters)} | "
            f"{', '.join(str(chapter_id) for chapter_id in row.preferred_lens_unresolved_chapter_ids)} | "
            f"{_item_rule_decision_summary(row.item_rule_decisions)} | "
            f"{row.missing_field_rate:.1%} | "
            f"{', '.join(row.missing_p0_fields)} | "
            f"{', '.join(row.missing_p1_fields)} | "
            f"{_escape_markdown_cell(row.reason)} |"
        )

    lines.extend(
        [
            "",
            "## Score Applicability Issues",
            "",
            "| issue_id | issue_code | severity | fund_code | field | contract | baseline_blocking | missing_groups | message |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    if result.score_applicability_issues:
        for row in result.score_applicability_issues:
            lines.append(
                "| "
                f"{row.issue_id} | "
                f"{row.issue_code} | "
                f"{row.severity} | "
                f"{row.fund_code} | "
                f"{row.field_name} | "
                f"{row.contract_id} | "
                f"{row.baseline_blocking} | "
                f"{', '.join(row.missing_evidence_groups)} | "
                f"{_escape_markdown_cell(row.message)} |"
            )
    else:
        lines.append("|  |  |  |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Failed Funds",
            "",
            "| fund_code | fund_name | app_category | report_year | error_type | error_message |",
            "|---|---|---|---:|---|---|",
        ]
    )
    if result.failed_funds:
        for row in result.failed_funds:
            lines.append(
                "| "
                f"{row.fund_code} | "
                f"{row.fund_name or ''} | "
                f"{row.app_category or ''} | "
                f"{row.report_year or ''} | "
                f"{row.error_type or ''} | "
                f"{_escape_markdown_cell(row.error_message or '')} |"
            )
    else:
        lines.append("|  |  |  |  |  |  |")

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


def _item_rule_decision_summary(decisions: Sequence[ItemRuleDecisionSummary]) -> str:
    """汇总 ITEM_RULE evaluator 决策数量。

    Args:
        decisions: ITEM_RULE 决策摘要序列。

    Returns:
        形如 `delete=2/render=2` 的摘要；无决策时返回空字符串。

    Raises:
        无显式抛出。
    """

    if not decisions:
        return ""
    counts = Counter(decision.status for decision in decisions)
    return "/".join(f"{status}={counts[status]}" for status in sorted(counts))


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
