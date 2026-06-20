"""FundDisclosureDocument 中间态 processor（S4 skeleton）。

本 processor 只做：注册、身份校验、S3 admission 判定消费、fail-closed extract。
字段族提取在 FundDisclosureDocument schema gate 完成前全部返回 missing。
不读取 FundDocumentRepository、PDF/cache/source helper、Docling、network、
provider、LLM、Service/UI/Host、renderer 或 quality gate。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
from typing import Final, Iterable, cast

from fund_agent.fund.extractors.models import EvidenceAnchor, TrackingErrorValue
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.processors.contracts import (
    FundCandidateEvidenceRecord,
    FundDisclosureCellLike,
    FundDisclosureDocumentContentIntermediate,
    FundDisclosureDocumentIntermediate,
    FundDisclosureParagraphBlockLike,
    FundDisclosureSourceTruthAdmissionProof,
    FundDisclosureTableBlockLike,
    FundExtractionGap,
    FundExtractionGapCode,
    FundExtractionSourceBoundary,
    FundFieldFamilyId,
    FundFieldFamilyResult,
    FundProcessorContractStatus,
    FundProcessorDispatchKey,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.fund_disclosure_dispatch import (
    admit_disclosure_intermediate,
)
from fund_agent.fund.source_provenance import PublicSourceProvenance

_OUTPUT_SCHEMA_VERSION: Final[str] = "fund_processor_result.v1"
_FUND_DISCLOSURE_INTERMEDIATE_KIND: Final[str] = "fund_disclosure_document.v1"

_FAMILY_ORDER: Final[tuple[FundFieldFamilyId, ...]] = (
    "product_essence.v1",
    "return_attribution.v1",
    "manager_profile.v1",
    "investor_experience.v1",
    "current_stage.v1",
    "core_risk.v1",
)

_CHAPTER_IDS: Final[dict[FundFieldFamilyId, tuple[int, ...]]] = {
    "product_essence.v1": (1,),
    "return_attribution.v1": (2,),
    "manager_profile.v1": (3,),
    "investor_experience.v1": (4,),
    "current_stage.v1": (5,),
    "core_risk.v1": (6,),
}

_PRODUCT_ESSENCE_CANDIDATE_LIMIT: Final[int] = 12
_RETURN_ATTRIBUTION_CANDIDATE_LIMIT: Final[int] = 12
_MANAGER_PROFILE_CANDIDATE_LIMIT: Final[int] = 16
_INVESTOR_EXPERIENCE_CANDIDATE_LIMIT: Final[int] = 16
_CURRENT_STAGE_CANDIDATE_LIMIT: Final[int] = 16
_CORE_RISK_CANDIDATE_LIMIT: Final[int] = 16
_CORE_RISK_REQUIRED_TOP_LEVEL: Final[tuple[str, ...]] = (
    "risk_characteristic_text",
    "liquidation_or_scale_risk",
    "tracking_error_or_deviation_risk",
    "turnover_or_style_drift_risk",
    "concentration_risk",
)
_CORE_RISK_ROLE_KEYS: Final[tuple[str, ...]] = (
    "liquidation_or_scale_risk",
    "tracking_error_or_deviation_risk",
    "turnover_or_style_drift_risk",
    "concentration_risk",
)
_CANDIDATE_EXCERPT_LIMIT: Final[int] = 160
_PRODUCT_ESSENCE_MATCH_GROUPS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    (
        "product_identity",
        ("基金简介", "基金基本情况", "产品概况", "基金产品资料概要", "基金名称", "基金代码"),
    ),
    ("investment_scope", ("投资目标", "投资范围", "投资策略")),
    ("benchmark", ("业绩比较基准", "比较基准")),
    ("risk_characteristic", ("风险收益特征", "风险特征")),
)
_PRODUCT_ESSENCE_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "basic_identity.fund_name": ("基金名称", "基金简称"),
    "basic_identity.fund_code": ("基金主代码", "基金代码"),
    "basic_identity.fund_category": ("基金类别", "基金类型"),
    "basic_identity.fund_scale": ("基金规模", "基金资产净值"),
    "basic_identity.fund_manager": ("基金经理",),
    "basic_identity.management_company": ("基金管理人",),
    "basic_identity.custodian": ("基金托管人",),
    "basic_identity.inception_date": ("基金合同生效日", "成立日期"),
    "product_profile.investment_objective": ("投资目标",),
    "product_profile.investment_scope": ("投资范围",),
    "product_profile.investment_strategy": ("投资策略",),
    "product_profile.style_positioning": ("投资风格", "产品定位", "风格定位"),
    "benchmark.benchmark_text": ("业绩比较基准", "比较基准"),
    "risk_characteristic_text.risk_characteristic_text": ("风险收益特征", "基金风险收益特征"),
}
_PRODUCT_ESSENCE_PARAGRAPH_OUTPUT_PATHS: Final[tuple[str, ...]] = (
    "product_profile.investment_objective",
    "product_profile.investment_scope",
    "product_profile.investment_strategy",
    "product_profile.style_positioning",
    "benchmark.benchmark_text",
    "risk_characteristic_text.risk_characteristic_text",
)
_RISK_CHARACTERISTIC_OUTPUT_PATH: Final[str] = (
    "risk_characteristic_text.risk_characteristic_text"
)
_PRODUCT_ESSENCE_GENERIC_CELL_TEXTS: Final[frozenset[str]] = frozenset(
    ("项目", "指标", "名称", "内容", "说明")
)
_PRODUCT_ESSENCE_REQUIRED_TOP_LEVEL: Final[tuple[str, ...]] = (
    "basic_identity",
    "product_profile",
    "benchmark",
    "risk_characteristic_text",
)
_RETURN_ATTRIBUTION_MATCH_GROUPS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    (
        "nav_benchmark_performance",
        (
            "基金份额净值增长率",
            "净值增长率",
            "基金净值表现",
            "业绩比较基准收益率",
            "基准收益率",
            "业绩比较基准",
        ),
    ),
    (
        "fee_schedule",
        (
            "基金管理费",
            "管理费率",
            "管理费",
            "基金托管费",
            "托管费率",
            "托管费",
            "销售服务费率",
            "销售服务费",
        ),
    ),
    (
        "tracking_error",
        ("跟踪误差", "年化跟踪误差", "日均跟踪偏离度", "日均偏离度"),
    ),
)
_RETURN_ATTRIBUTION_REQUIRED_TOP_LEVEL: Final[tuple[str, ...]] = (
    "nav_benchmark_performance",
    "fee_schedule",
    "tracking_error",
)
_RETURN_ATTRIBUTION_NAV_LABELS: Final[tuple[str, ...]] = (
    "基金份额净值增长率",
    "净值增长率",
)
_RETURN_ATTRIBUTION_BENCHMARK_LABELS: Final[tuple[str, ...]] = (
    "业绩比较基准收益率",
    "基准收益率",
)
_RETURN_ATTRIBUTION_FEE_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "fee_schedule.management_fee": ("基金管理费", "管理费率", "管理费"),
    "fee_schedule.custody_fee": ("基金托管费", "托管费率", "托管费"),
}
_RETURN_ATTRIBUTION_TRACKING_ERROR_LABELS: Final[tuple[str, ...]] = (
    "跟踪误差",
    "年化跟踪误差",
    "日均跟踪偏离度",
    "日均偏离度",
)
_RETURN_ATTRIBUTION_GENERIC_CELL_TEXTS: Final[frozenset[str]] = frozenset(
    ("项目", "指标", "名称", "内容", "说明", "费率")
)
_RETURN_ATTRIBUTION_TRACKING_ERROR_REJECT_CONTEXT: Final[tuple[str, ...]] = (
    "目标",
    "控制",
    "不超过",
    "力争",
    "偏离度绝对值",
)
_RETURN_ATTRIBUTION_PERCENT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?P<value>[-+]?\d+(?:,\d{3})*(?:\.\d+)?)\s*[％%]"
)
_MANAGER_PROFILE_REQUIRED_TOP_LEVEL: Final[tuple[str, ...]] = (
    "portfolio_managers",
    "manager_strategy_text",
    "turnover_rate",
    "manager_alignment",
    "holdings_snapshot",
)
_MANAGER_PROFILE_ROSTER_HEADINGS: Final[tuple[str, ...]] = (
    "基金经理简介",
    "基金管理人及基金经理情况",
    "基金经理情况",
    "主要人员情况",
)
_MANAGER_PROFILE_ROSTER_NAME_LABELS: Final[tuple[str, ...]] = ("姓名",)
_MANAGER_PROFILE_ROSTER_ROLE_LABELS: Final[tuple[str, ...]] = ("职务", "职责", "岗位")
_MANAGER_PROFILE_ROSTER_START_DATE_LABELS: Final[tuple[str, ...]] = (
    "任职日期",
    "任职时间",
    "聘任日期",
    "起始日期",
)
_MANAGER_PROFILE_ROSTER_END_DATE_LABELS: Final[tuple[str, ...]] = (
    "离任日期",
    "离任时间",
    "终止日期",
)
_MANAGER_PROFILE_STRATEGY_HEADINGS: Final[tuple[str, ...]] = (
    "报告期内基金投资策略和运作分析",
    "投资策略和运作分析",
    "投资策略",
    "运作分析",
)
_MANAGER_PROFILE_OUTLOOK_HEADINGS: Final[tuple[str, ...]] = (
    "管理人对宏观经济、证券市场及行业走势的简要展望",
    "后市展望",
    "市场展望",
)
_MANAGER_PROFILE_TURNOVER_LABELS: Final[tuple[str, ...]] = (
    "换手率",
    "股票换手率",
    "报告期内股票换手率",
    "换手率口径",
    "换手率计算口径",
)
_MANAGER_PROFILE_TURNOVER_BASIS_LABELS: Final[tuple[str, ...]] = (
    "换手率口径",
    "换手率计算口径",
    "计算口径",
    "口径",
)
_MANAGER_PROFILE_ALIGNMENT_STRONG_TOKENS: Final[tuple[str, ...]] = (
    "基金经理持有本基金",
    "基金经理持有份额",
    "本基金基金经理持有本开放式基金",
    "基金管理人所有从业人员持有本基金",
    "从业人员持有本基金",
)
_MANAGER_PROFILE_ALIGNMENT_GENERIC_TOKENS: Final[tuple[str, ...]] = (
    "基金经理持有",
    "从业人员持有",
    "持有本基金",
)
_MANAGER_PROFILE_ALIGNMENT_GUARD_TOKENS: Final[tuple[str, ...]] = (
    "基金经理",
    "从业人员",
    "基金管理人",
)
_MANAGER_PROFILE_ALIGNMENT_MANAGER_TOKENS: Final[tuple[str, ...]] = (
    "基金经理",
)
_MANAGER_PROFILE_ALIGNMENT_EMPLOYEE_TOKENS: Final[tuple[str, ...]] = (
    "从业人员",
    "基金管理人所有从业人员",
)
_MANAGER_PROFILE_HOLDINGS_TOP_HEADINGS: Final[tuple[str, ...]] = (
    "报告期末按公允价值占基金资产净值比例大小排序的前十名股票投资明细",
    "前十名股票投资明细",
)
_MANAGER_PROFILE_HOLDINGS_INDUSTRY_HEADINGS: Final[tuple[str, ...]] = (
    "报告期末按行业分类的股票投资组合",
    "期末按行业分类的股票投资组合",
)
_MANAGER_PROFILE_HOLDINGS_CONTEXT_HEADINGS: Final[tuple[str, ...]] = (
    *_MANAGER_PROFILE_HOLDINGS_TOP_HEADINGS,
    *_MANAGER_PROFILE_HOLDINGS_INDUSTRY_HEADINGS,
    "报告期末基金资产组合情况",
)
_MANAGER_PROFILE_TOP_HOLDINGS_IDENTITY_LABELS: Final[tuple[str, ...]] = (
    "股票代码",
    "股票名称",
    "证券代码",
    "证券名称",
)
_MANAGER_PROFILE_INDUSTRY_IDENTITY_LABELS: Final[tuple[str, ...]] = (
    "行业类别",
    "行业名称",
    "行业",
)
_MANAGER_PROFILE_GENERIC_TABLE_HEADERS: Final[frozenset[str]] = frozenset(
    ("项目", "内容", "说明", "序号")
)
_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL: Final[tuple[str, ...]] = (
    "investor_return",
    "holder_structure",
    "share_change",
)
_INVESTOR_RETURN_DIRECT_LABELS: Final[tuple[str, ...]] = (
    "加权平均投资者收益率",
    "投资者收益率",
    "投资者实际收益",
)
_INVESTOR_RETURN_ESTIMATED_LABELS: Final[tuple[str, ...]] = (
    "加权平均投资者收益率（估算）",
    "投资者收益率（估算）",
    "估算投资者收益率",
)
_INVESTOR_RETURN_UNAVAILABLE_TOKENS: Final[tuple[str, ...]] = (
    "未披露",
    "未提供",
    "无法取得",
    "不适用",
    "无",
)
_HOLDER_STRUCTURE_INSTITUTIONAL_LABELS: Final[tuple[str, ...]] = (
    "机构投资者",
    "机构投资者持有",
    "机构投资者持有比例",
    "机构投资者持有份额",
)
_HOLDER_STRUCTURE_INDIVIDUAL_LABELS: Final[tuple[str, ...]] = (
    "个人投资者",
    "个人投资者持有",
    "个人投资者持有比例",
    "个人投资者持有份额",
)
_HOLDER_STRUCTURE_GUARD_LABELS: Final[tuple[str, ...]] = (
    "基金份额持有人信息",
    "基金份额持有人结构",
    "基金份额持有人情况",
    "持有人结构",
)
_HOLDER_STRUCTURE_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    ("", "无", "不适用", "-", "—", "未披露")
)
_SHARE_CHANGE_BEGINNING_LABELS: Final[tuple[str, ...]] = (
    "期初基金份额总额",
    "报告期期初基金份额总额",
    "期初份额",
)
_SHARE_CHANGE_ENDING_LABELS: Final[tuple[str, ...]] = (
    "期末基金份额总额",
    "报告期期末基金份额总额",
    "期末份额",
)
_SHARE_CHANGE_NET_LABELS: Final[tuple[str, ...]] = (
    "净变动",
    "本期申购赎回净额",
)
_SHARE_CHANGE_TABLE_GUARD_LABELS: Final[tuple[str, ...]] = (
    "基金份额变动",
    "份额变动",
    "基金份额总额变动",
)
_SHARE_CHANGE_LABEL_COLUMN_TOKENS: Final[tuple[str, ...]] = (
    "项目",
    "项目名称",
    "份额类别",
    "类别",
    "基金份额",
    "基金份额项目",
    "变动项目",
    "期初",
    "期末",
    "申购",
    "赎回",
    *_SHARE_CHANGE_BEGINNING_LABELS,
    *_SHARE_CHANGE_ENDING_LABELS,
    *_SHARE_CHANGE_NET_LABELS,
)
_SHARE_CHANGE_VALUE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?"
)
_CURRENT_STAGE_REQUIRED_TOP_LEVEL: Final[tuple[str, ...]] = (
    "basic_identity",
    "share_change",
    "holdings_snapshot",
    "portfolio_managers",
)


@dataclass(frozen=True, slots=True)
class _ProductEssenceValueCandidate:
    """product_essence.v1 单个字段值候选。"""

    output_path: str
    value: str
    anchor: EvidenceAnchor
    source_field_path: str


@dataclass(frozen=True, slots=True)
class _RiskCharacteristicValueCandidate:
    """风险收益特征文本 source-truth 字段候选，见模板第 1/6 章。"""

    output_path: str
    value: str
    anchor: EvidenceAnchor
    source_field_path: str


@dataclass(frozen=True, slots=True)
class _CoreRiskRoleValueCandidate:
    """核心风险单角色 source-truth 披露文本候选，见模板第 6 章。"""

    output_path: str
    role: str
    value: str
    anchor: EvidenceAnchor
    source_field_path: str


_CoreRiskValueCandidate = _RiskCharacteristicValueCandidate | _CoreRiskRoleValueCandidate


@dataclass(frozen=True, slots=True)
class _ReturnAttributionValueCandidate:
    """return_attribution.v1 单个字段值候选，见模板第 2 章 R=A+B-C。"""

    output_path: str
    value: object
    anchor: EvidenceAnchor
    source_field_path: str
    period_label: str | None = None


@dataclass(frozen=True, slots=True)
class _ManagerProfileValueCandidate:
    """manager_profile.v1 单个 source-truth 字段值候选，见模板第 3 章。"""

    output_path: str
    value: object
    anchor: EvidenceAnchor
    source_field_path: str


@dataclass(frozen=True, slots=True)
class _InvestorExperienceValueCandidate:
    """investor_experience.v1 单个 source-truth 字段值候选，见模板第 4 章。"""

    output_path: str
    value: object
    anchor: EvidenceAnchor
    source_field_path: str


@dataclass(frozen=True, slots=True)
class _CurrentStageValueCandidate:
    """current_stage.v1 单个 source-truth 字段值候选，见模板第 5 章。"""

    output_path: str
    value: object
    anchors: tuple[EvidenceAnchor, ...]
    source_field_path: str
_MANAGER_PROFILE_MATCH_GROUPS: Final[
    tuple[tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...]], ...]
] = (
    (
        "portfolio_managers",
        ("基金经理简介", "基金管理人及基金经理情况", "基金经理情况", "主要人员情况"),
        (
            "姓名",
            "职务",
            "职责",
            "岗位",
            "任职日期",
            "任职时间",
            "聘任日期",
            "起始日期",
            "离任日期",
            "离任时间",
            "终止日期",
        ),
        ("基金经理", "管理人"),
    ),
    (
        "manager_strategy_text",
        (
            "报告期内基金投资策略和运作分析",
            "投资策略和运作分析",
            "投资策略",
            "运作分析",
            "管理人对宏观经济、证券市场及行业走势的简要展望",
            "后市展望",
            "市场展望",
        ),
        (),
        (),
    ),
    (
        "turnover_rate",
        ("换手率", "股票换手率", "报告期内股票换手率", "换手率口径", "换手率计算口径"),
        (),
        (),
    ),
    (
        "manager_alignment",
        (
            "基金经理持有本基金",
            "基金经理持有份额",
            "本基金基金经理持有本开放式基金",
            "基金管理人所有从业人员持有本基金",
            "从业人员持有本基金",
        ),
        ("基金经理持有", "从业人员持有", "持有本基金"),
        ("基金经理", "从业人员", "基金管理人"),
    ),
    (
        "holdings_snapshot",
        (
            "报告期末按行业分类的股票投资组合",
            "期末按行业分类的股票投资组合",
            "报告期末按公允价值占基金资产净值比例大小排序的前十名股票投资明细",
            "前十名股票投资明细",
            "报告期末基金资产组合情况",
            "持仓集中度",
        ),
        (),
        (),
    ),
)
_INVESTOR_EXPERIENCE_MATCH_GROUPS: Final[
    tuple[tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...]], ...]
] = (
    (
        "investor_return",
        (
            "投资者实际收益",
            "加权平均投资者收益率",
            "盈利投资者占比",
            "投资者回报",
            "投资者获得感",
            "行为损益",
        ),
        ("实际收益", "盈利占比"),
        ("投资者", "持有人", "基金份额持有人"),
    ),
    (
        "holder_structure",
        (
            "基金份额持有人信息",
            "基金份额持有人结构",
            "基金份额持有人情况",
            "持有人户数",
            "户均持有份额",
            "机构投资者持有",
            "个人投资者持有",
        ),
        ("机构投资者", "个人投资者", "持有人", "户数"),
        ("基金份额持有人", "持有人结构", "持有人信息", "持有人情况"),
    ),
    (
        "share_change",
        (
            "基金份额变动",
            "份额变动",
            "基金份额总额变动",
            "报告期期初基金份额总额",
            "报告期期末基金份额总额",
            "期初基金份额总额",
            "期末基金份额总额",
        ),
        ("期初份额", "期末份额", "份额总额"),
        ("基金份额", "份额变动", "基金份额总额变动"),
    ),
    (
        "subscription_redemption",
        (
            "基金总申购份额",
            "基金总赎回份额",
            "总申购份额",
            "总赎回份额",
            "本期申购",
            "本期赎回",
            "申购赎回",
        ),
        ("申购", "赎回", "净申购", "净赎回"),
        (
            "份额变动",
            "基金份额变动",
            "基金份额总额变动",
            "基金总申购",
            "基金总赎回",
            "总申购份额",
            "总赎回份额",
            "申购赎回",
        ),
    ),
    (
        "income_distribution",
        (
            "基金收益分配",
            "收益分配",
            "利润分配",
            "收益分配情况",
            "基金利润分配",
            "每10份基金份额分红数",
        ),
        ("分红", "红利"),
        ("收益分配", "利润分配", "基金份额", "分配"),
    ),
)
_CURRENT_STAGE_MATCH_GROUPS: Final[
    tuple[tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...]], ...]
] = (
    (
        "stage_status",
        (
            "当前阶段",
            "所处阶段",
            "运作阶段",
            "建仓期",
            "稳定期",
            "膨胀期",
            "萎缩期",
            "转型期",
            "基金运作情况",
            "报告期内基金运作",
        ),
        ("阶段", "状态", "运作"),
        (
            "当前阶段",
            "所处阶段",
            "关键变化",
            "基金运作情况",
            "报告期内基金运作",
        ),
    ),
    (
        "manager_change",
        (
            "基金经理变更",
            "基金经理变动",
            "基金经理发生变化",
            "新任基金经理",
            "基金经理离任",
            "离任基金经理",
            "基金经理任职",
            "基金经理聘任",
        ),
        ("变更", "变动", "任职", "离任", "聘任"),
        (
            "基金经理",
            "投资经理",
            "主要人员情况",
            "基金管理人及基金经理情况",
            "基金经理情况",
        ),
    ),
    (
        "share_scale_change",
        (
            "基金份额变动",
            "份额变动",
            "基金份额总额变动",
            "报告期期初基金份额总额",
            "报告期期末基金份额总额",
            "期初基金份额总额",
            "期末基金份额总额",
            "规模变化",
            "规模波动",
            "规模剧变",
            "大额申购",
            "大额赎回",
            "净申购",
            "净赎回",
        ),
        ("份额", "规模", "申购", "赎回", "净申购", "净赎回"),
        (
            "基金份额变动",
            "基金份额总额变动",
            "期初基金份额总额",
            "期末基金份额总额",
            "规模变化",
            "规模波动",
            "大额申购",
            "大额赎回",
        ),
    ),
    (
        "holding_strategy_change",
        (
            "投资策略调整",
            "策略调整",
            "投资策略发生重大变化",
            "投资风格发生重大变化",
            "资产配置变化",
            "持仓结构变化",
            "行业配置变化",
            "仓位变化",
            "前十大重仓股变化",
            "投资组合重大变动",
            "报告期内基金投资策略和运作分析",
        ),
        ("策略", "持仓", "配置", "仓位", "行业", "重仓", "变化", "调整", "变动"),
        ("投资策略", "投资组合", "资产配置", "持仓结构", "行业配置", "运作分析", "重大变化"),
    ),
)
_CORE_RISK_MATCH_GROUPS: Final[
    tuple[tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...]], ...]
] = (
    (
        "risk_characteristic",
        ("风险收益特征", "风险特征", "基金风险收益特征", "产品风险收益特征"),
        ("风险", "收益"),
        ("风险收益特征", "风险特征", "基金产品资料概要", "基金简介"),
    ),
    (
        "liquidation_or_scale_risk",
        (
            "基金资产净值低于五千万元",
            "基金资产净值低于5000万元",
            "基金份额持有人数量不满二百人",
            "基金份额持有人数量不满200人",
            "连续二十个工作日",
            "连续20个工作日",
            "基金合同终止事由",
            "基金合同自动终止",
            "基金财产清算",
        ),
        ("规模", "清盘", "持有人", "基金资产净值"),
        (
            "基金合同终止",
            "基金财产清算",
            "连续二十个工作日",
            "连续20个工作日",
            "五千万元",
            "5000万元",
            "二百人",
            "200人",
            "基金份额持有人数量",
        ),
    ),
    (
        "tracking_error_or_deviation_risk",
        ("跟踪误差", "年化跟踪误差", "日均跟踪偏离度", "日均偏离度", "跟踪偏离度"),
        ("跟踪", "偏离"),
        ("跟踪误差", "跟踪偏离度", "业绩比较基准", "标的指数", "指数基金", "指数增强"),
    ),
    (
        "turnover_or_style_drift_risk",
        (
            "换手率",
            "股票换手率",
            "报告期内股票换手率",
            "换手率口径",
            "换手率计算口径",
            "投资风格发生重大变化",
            "投资策略发生重大变化",
            "风格漂移",
        ),
        ("换手", "风格", "漂移", "策略变化"),
        ("换手率", "投资策略", "投资风格", "报告期内基金投资策略和运作分析", "运作分析", "重大变化"),
    ),
    (
        "concentration_risk",
        (
            "持仓集中度",
            "报告期末按行业分类的股票投资组合",
            "期末按行业分类的股票投资组合",
            "报告期末按公允价值占基金资产净值比例大小排序的前十名股票投资明细",
            "前十名股票投资明细",
            "报告期末基金资产组合情况",
        ),
        ("持仓", "集中", "行业集中", "前十名"),
        ("股票投资组合", "资产组合情况", "公允价值占基金资产净值比例", "前十名股票投资明细", "行业分类", "持仓集中度"),
    ),
)


class _FundDisclosureDocumentFundProcessor:
    """分类型 FundDisclosureDocument 中间态 processor 基类。

    子类按 `supported_fund_type` 分别支持单一基金类型的
    `annual_report + fund_disclosure_document.v1` 输入。字段族抽取、proof/candidate
    admission 与 fail-closed 语义共享，避免跨类型复制 extraction 规则。
    不声明 source truth、parser replacement、candidate proof、readiness 或 release。
    """

    processor_id: str = ""
    priority: int = 50
    output_schema_version: str = _OUTPUT_SCHEMA_VERSION
    supported_fund_type: FundType = "active_fund"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """判断是否支持当前 dispatch key。

        Args:
            context: Processor 路由键。

        Returns:
            仅在子类声明基金类型的年报 FundDisclosureDocument 中间态返回 True。

        Raises:
            无显式抛出。
        """

        return (
            context.fund_type == self.supported_fund_type
            and context.report_type == "annual_report"
            and context.intermediate_kind == _FUND_DISCLOSURE_INTERMEDIATE_KIND
            and context.processor_goal == "template_chapters_1_6_minimum_field_families"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        """执行 admission 判定与 identity 校验；字段抽取 deferred 到 schema gate。

        Args:
            input_data: Processor 输入契约。

        Returns:
            Processor 输出结果；当前所有字段族为 missing。

        Raises:
            无显式抛出；所有异常路径转为 fail-closed result。
        """

        context = input_data.context

        if not self.supports(context):
            gap_code, source_boundary = _unsupported_block_details(
                context,
                supported_fund_type=self.supported_fund_type,
            )
            return _blocked_result(
                self.processor_id,
                context,
                gap_code=gap_code,
                message="FundDisclosureDocumentProcessor 不支持当前 dispatch key",
                source_boundary=source_boundary,
            )

        intermediate = input_data.intermediate
        if not isinstance(intermediate, FundDisclosureDocumentIntermediate):
            return _blocked_result(
                self.processor_id,
                context,
                gap_code="input_type_mismatch",
                message="FundDisclosureDocumentProcessor 只接受 FundDisclosureDocumentIntermediate",
                source_boundary="unsupported_intermediate",
            )

        identity_blocked = _check_identity(
            context,
            intermediate,
            processor_id=self.processor_id,
        )
        if identity_blocked is not None:
            return identity_blocked

        try:
            admission = admit_disclosure_intermediate(intermediate, context)
        except KeyError:
            return _blocked_result(
                self.processor_id,
                context,
                gap_code="unsupported_intermediate",
                message=(
                    f"admission helper 无法识别 failure_class：{intermediate.failure_class}；"
                    "标准五类来源失败分类之外的非法值"
                ),
                source_boundary="unsupported_intermediate",
            )

        source_provenance = intermediate.source_provenance
        candidate_boundary = intermediate.candidate_boundary

        if not admission.admitted:
            return FundProcessorResult(
                processor_id=self.processor_id,
                output_schema_version=self.output_schema_version,
                fund_code=context.fund_code,
                report_year=context.document_year,
                fund_type=context.fund_type,
                report_type=context.report_type,
                input_intermediate_kind=context.intermediate_kind,
                field_families=(),
                gaps=(
                    FundExtractionGap(
                        gap_code=admission.gap_code,  # type: ignore[arg-type]
                        message=f"admission 拒绝：gap_code={admission.gap_code}",
                        field_family_id=None,
                        source_field_path=None,
                        source_boundary=admission.source_boundary,  # type: ignore[arg-type]
                        required=True,
                    ),
                ),
                anchors=(),
                source_provenance=source_provenance,
                candidate_boundary=candidate_boundary,
                contract_status=admission.contract_status,
            )

        source_truth_gap_code: FundExtractionGapCode | None = None
        if admission.contract_status != "blocked":
            source_truth_gap_code = _validate_source_truth_admission(intermediate, context)

        field_families = _field_families_for_intermediate(
            intermediate,
            source_provenance,
            context=context,
            source_truth_extraction_allowed=(
                admission.contract_status != "blocked" and source_truth_gap_code is None
            ),
            source_truth_gap_code=source_truth_gap_code,
        )
        contract_status: FundProcessorContractStatus = (
            "blocked"
            if admission.contract_status == "blocked"
            else _derive_contract_status(field_families)
        )
        result_anchors = _dedupe_anchors(
            anchor for family in field_families for anchor in family.anchors
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=context.fund_code,
            report_year=context.document_year,
            fund_type=context.fund_type,
            report_type=context.report_type,
            input_intermediate_kind=context.intermediate_kind,
            field_families=field_families,
            gaps=(),
            anchors=result_anchors,
            source_provenance=source_provenance,
            candidate_boundary=candidate_boundary,
            contract_status=contract_status,
        )


class FundDisclosureDocumentProcessor(_FundDisclosureDocumentFundProcessor):
    """主动基金 FundDisclosureDocument processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "active_fund_disclosure.fund_disclosure_document.v1"
    priority: Final[int] = 50
    supported_fund_type: Final[FundType] = "active_fund"


class IndexFundDisclosureDocumentProcessor(_FundDisclosureDocumentFundProcessor):
    """指数基金 FundDisclosureDocument processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "index_fund_disclosure.fund_disclosure_document.v1"
    priority: Final[int] = 50
    supported_fund_type: Final[FundType] = "index_fund"


class EnhancedIndexDisclosureDocumentProcessor(_FundDisclosureDocumentFundProcessor):
    """指数增强基金 FundDisclosureDocument processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "enhanced_index_disclosure.fund_disclosure_document.v1"
    priority: Final[int] = 50
    supported_fund_type: Final[FundType] = "enhanced_index"


class BondFundDisclosureDocumentProcessor(_FundDisclosureDocumentFundProcessor):
    """债券基金 FundDisclosureDocument processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "bond_fund_disclosure.fund_disclosure_document.v1"
    priority: Final[int] = 50
    supported_fund_type: Final[FundType] = "bond_fund"


class QdiiFundDisclosureDocumentProcessor(_FundDisclosureDocumentFundProcessor):
    """QDII 基金 FundDisclosureDocument processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "qdii_fund_disclosure.fund_disclosure_document.v1"
    priority: Final[int] = 50
    supported_fund_type: Final[FundType] = "qdii_fund"


class FofFundDisclosureDocumentProcessor(_FundDisclosureDocumentFundProcessor):
    """FOF 基金 FundDisclosureDocument processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "fof_fund_disclosure.fund_disclosure_document.v1"
    priority: Final[int] = 50
    supported_fund_type: Final[FundType] = "fof_fund"


def _check_identity(
    context: FundProcessorDispatchKey,
    intermediate: FundDisclosureDocumentIntermediate,
    *,
    processor_id: str,
) -> FundProcessorResult | None:
    """校验 dispatch key 与 intermediate 身份一致性。

    Args:
        context: Processor 路由键。
        intermediate: 受控文档表示中间态。

    Returns:
        身份不一致时返回 blocked result（contract_status 固定为 "blocked"）；
        一致时返回 None。

    Raises:
        无显式抛出。
    """

    if intermediate.intermediate_kind != context.intermediate_kind:
        return _blocked_result(
            processor_id=processor_id,
            context=context,
            gap_code="input_type_mismatch",
            message=(
                f"intermediate_kind 不匹配："
                f"intermediate={intermediate.intermediate_kind} "
                f"dispatch={context.intermediate_kind}"
            ),
            source_boundary="unsupported_intermediate",
            contract_status="blocked",
        )
    if intermediate.document_kind != context.report_type:
        return _blocked_result(
            processor_id=processor_id,
            context=context,
            gap_code="unsupported_report_type",
            message=(
                f"document_kind 不匹配："
                f"intermediate={intermediate.document_kind} "
                f"dispatch={context.report_type}"
            ),
            source_boundary="unsupported_report_type",
            contract_status="blocked",
        )
    if intermediate.fund_code != context.fund_code:
        return _blocked_result(
            processor_id=processor_id,
            context=context,
            gap_code="unsupported_intermediate",
            message=(
                f"fund_code 不匹配："
                f"intermediate={intermediate.fund_code} "
                f"dispatch={context.fund_code}"
            ),
            source_boundary="unsupported_intermediate",
            contract_status="blocked",
        )
    if intermediate.report_year != context.document_year:
        return _blocked_result(
            processor_id=processor_id,
            context=context,
            gap_code="unsupported_intermediate",
            message=(
                f"report_year 不匹配："
                f"intermediate={intermediate.report_year} "
                f"dispatch={context.document_year}"
            ),
            source_boundary="unsupported_intermediate",
            contract_status="blocked",
        )
    return None


def _field_families_for_intermediate(
    intermediate: FundDisclosureDocumentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    *,
    context: FundProcessorDispatchKey,
    source_truth_extraction_allowed: bool = False,
    source_truth_gap_code: FundExtractionGapCode | None = None,
) -> tuple[FundFieldFamilyResult, ...]:
    """构造 FundDisclosureDocument processor 字段族结果。

    Args:
        intermediate: 已通过身份校验和 admission 的中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。
        source_truth_extraction_allowed: admission 非 blocked 且 source-truth proof 合法时为真。
        source_truth_gap_code: source-truth admission proof 缺失或非法时的本地 gap。

    Returns:
        六个字段族结果；proof-positive source-truth 路径可进入已授权 direct extractor，
        其余已接受字段族仅附加 candidate evidence。

    Raises:
        无显式抛出。
    """

    product_essence_source_truth: FundFieldFamilyResult | None = None
    return_attribution_source_truth: FundFieldFamilyResult | None = None
    manager_profile_source_truth: FundFieldFamilyResult | None = None
    investor_experience_source_truth: FundFieldFamilyResult | None = None
    current_stage_source_truth: FundFieldFamilyResult | None = None
    core_risk_source_truth: FundFieldFamilyResult | None = None
    content_intermediate = _content_intermediate_or_none(intermediate)
    if source_truth_extraction_allowed and content_intermediate is not None:
        product_essence_source_truth = _extract_product_essence_source_truth(
            content_intermediate, source_provenance, context
        )
        return_attribution_source_truth = _extract_return_attribution_source_truth(
            content_intermediate, source_provenance, context
        )
        manager_profile_source_truth = _extract_manager_profile_source_truth(
            content_intermediate, source_provenance, context
        )
        investor_experience_source_truth = _extract_investor_experience_source_truth(
            content_intermediate, source_provenance, context
        )
        current_stage_source_truth = _extract_current_stage_source_truth(
            content_intermediate, source_provenance, context
        )
        core_risk_source_truth = _extract_core_risk_source_truth(
            content_intermediate, source_provenance, context
        )

    product_essence_evidence = (
        ()
        if product_essence_source_truth is not None
        else _select_product_essence_candidate_evidence(intermediate)
    )
    return_attribution_evidence = (
        ()
        if return_attribution_source_truth is not None
        else _select_return_attribution_candidate_evidence(intermediate)
    )
    manager_profile_evidence = (
        ()
        if manager_profile_source_truth is not None
        else _select_manager_profile_candidate_evidence(intermediate)
    )
    investor_experience_evidence = (
        ()
        if investor_experience_source_truth is not None
        else _select_investor_experience_candidate_evidence(intermediate)
    )
    current_stage_evidence = (
        ()
        if current_stage_source_truth is not None
        else _select_current_stage_candidate_evidence(intermediate)
    )
    core_risk_evidence = (
        () if core_risk_source_truth is not None else _select_core_risk_candidate_evidence(intermediate)
    )
    candidate_evidence_by_family: dict[
        FundFieldFamilyId, tuple[FundCandidateEvidenceRecord, ...]
    ] = {
        "product_essence.v1": product_essence_evidence,
        "return_attribution.v1": return_attribution_evidence,
        "manager_profile.v1": manager_profile_evidence,
        "investor_experience.v1": investor_experience_evidence,
        "current_stage.v1": current_stage_evidence,
        "core_risk.v1": core_risk_evidence,
    }

    field_families = tuple(
        product_essence_source_truth
        if family_id == "product_essence.v1" and product_essence_source_truth is not None
        else return_attribution_source_truth
        if family_id == "return_attribution.v1"
        and return_attribution_source_truth is not None
        else manager_profile_source_truth
        if family_id == "manager_profile.v1"
        and manager_profile_source_truth is not None
        else investor_experience_source_truth
        if family_id == "investor_experience.v1"
        and investor_experience_source_truth is not None
        else current_stage_source_truth
        if family_id == "current_stage.v1"
        and current_stage_source_truth is not None
        else core_risk_source_truth
        if family_id == "core_risk.v1" and core_risk_source_truth is not None
        else (
            _candidate_missing_field_family(
                family_id, source_provenance, candidate_evidence_by_family[family_id]
            )
            if candidate_evidence_by_family.get(family_id)
            else _missing_field_family(family_id, source_provenance)
        )
        for family_id in _FAMILY_ORDER
    )
    if source_truth_gap_code is None:
        return field_families
    return tuple(
        _with_source_truth_admission_gap(family, source_truth_gap_code)
        for family in field_families
    )


def _validate_source_truth_admission(
    intermediate: FundDisclosureDocumentIntermediate,
    context: FundProcessorDispatchKey,
) -> FundExtractionGapCode | None:
    """校验 FundDisclosureDocument source-truth admission 正向证明。

    Args:
        intermediate: 已通过基础 admission 的中间态。
        context: Processor dispatch 身份。

    Returns:
        proof 通过时返回 None；缺 proof 返回 ``source_truth_admission_missing``；
        proof 身份或类型非法返回 ``source_truth_admission_invalid``。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return "source_truth_admission_missing"

    proof = getattr(content_intermediate, "source_truth_admission", None)
    if proof is None:
        return "source_truth_admission_missing"
    if not isinstance(proof, FundDisclosureSourceTruthAdmissionProof):
        return "source_truth_admission_invalid"
    if content_intermediate.candidate_boundary is not None:
        return "source_truth_admission_invalid"
    if content_intermediate.failure_class is not None:
        return "source_truth_admission_invalid"
    if content_intermediate.source_provenance is None:
        return "source_truth_admission_invalid"
    if (
        proof.fund_code != context.fund_code
        or proof.fund_code != content_intermediate.fund_code
        or proof.report_year != context.document_year
        or proof.report_year != content_intermediate.report_year
        or proof.document_kind != context.report_type
        or proof.document_kind != content_intermediate.document_kind
        or proof.intermediate_kind != context.intermediate_kind
        or proof.intermediate_kind != content_intermediate.intermediate_kind
        or proof.source_kind != context.source_kind
        or proof.source_kind != "annual_report"
    ):
        return "source_truth_admission_invalid"
    return None


def _extract_product_essence_source_truth(
    intermediate: FundDisclosureDocumentContentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    context: FundProcessorDispatchKey,
) -> FundFieldFamilyResult:
    """从 proof-positive FDD 正文抽取模板第 1 章产品本质字段族。

    Args:
        intermediate: 已通过 source-truth admission proof 的正文中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。

    Returns:
        `product_essence.v1` 字段族；只包含 Slice B 允许的四个 top-level key。

    Raises:
        无显式抛出。
    """

    selected_values, ambiguous_paths = _select_product_essence_values(intermediate, context)
    value = _build_product_essence_value(selected_values, context)
    gaps = _product_essence_source_truth_gaps(value, ambiguous_paths)
    status = _product_essence_status(value)
    anchors = _dedupe_anchors(
        selected_values[output_path].anchor
        for output_path in _product_essence_emitted_output_paths(value, selected_values)
    )
    return FundFieldFamilyResult(
        field_family_id="product_essence.v1",
        chapter_ids=_CHAPTER_IDS["product_essence.v1"],
        value=value,
        status=status,
        extraction_mode="missing" if status == "missing" else "direct",
        anchors=anchors,
        gaps=gaps,
        source_provenance=source_provenance,
        candidate_evidence=(),
    )


def _extract_core_risk_source_truth(
    intermediate: FundDisclosureDocumentContentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    context: FundProcessorDispatchKey,
) -> FundFieldFamilyResult:
    """从 proof-positive FDD 正文抽取模板第 6 章核心风险最小字段族。

    Args:
        intermediate: 已通过 source-truth admission proof 的正文中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。

    Returns:
        `core_risk.v1` 字段族；支持 risk_characteristic_text 及四个 role disclosure subvalue。

    Raises:
        无显式抛出。
    """

    selected_values, ambiguous_paths = _select_core_risk_values(intermediate, context)
    value = _build_core_risk_value(selected_values, context)
    gaps = _core_risk_source_truth_gaps(value, ambiguous_paths)
    status = _core_risk_status(value)
    anchors = _dedupe_anchors(
        selected_values[output_path].anchor
        for output_path in _core_risk_emitted_output_paths(value, selected_values)
    )
    return FundFieldFamilyResult(
        field_family_id="core_risk.v1",
        chapter_ids=_CHAPTER_IDS["core_risk.v1"],
        value=value,
        status=status,
        extraction_mode="missing" if status == "missing" else "direct",
        anchors=anchors,
        gaps=gaps,
        source_provenance=source_provenance,
        candidate_evidence=(),
    )


def _extract_return_attribution_source_truth(
    intermediate: FundDisclosureDocumentContentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    context: FundProcessorDispatchKey,
) -> FundFieldFamilyResult:
    """从 proof-positive FDD 正文抽取模板第 2 章收益归因字段族。

    Args:
        intermediate: 已通过 source-truth admission proof 的正文中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。

    Returns:
        `return_attribution.v1` 字段族；只包含 Slice 2 允许的三个 public top-level key。

    Raises:
        无显式抛出。
    """

    selected_values, ambiguous_paths = _select_return_attribution_values(intermediate, context)
    value = _build_return_attribution_value(selected_values)
    gaps = _return_attribution_source_truth_gaps(value, ambiguous_paths)
    status = _return_attribution_status(value)
    anchors = _dedupe_anchors(
        selected_values[output_path].anchor
        for output_path in _return_attribution_emitted_output_paths(value, selected_values)
    )
    return FundFieldFamilyResult(
        field_family_id="return_attribution.v1",
        chapter_ids=_CHAPTER_IDS["return_attribution.v1"],
        value=value,
        status=status,
        extraction_mode="missing" if status == "missing" else "direct",
        anchors=anchors,
        gaps=gaps,
        source_provenance=source_provenance,
        candidate_evidence=(),
    )


def _extract_manager_profile_source_truth(
    intermediate: FundDisclosureDocumentContentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    context: FundProcessorDispatchKey,
) -> FundFieldFamilyResult:
    """从 proof-positive FDD 正文抽取模板第 3 章基金经理画像字段族。

    Args:
        intermediate: 已通过 source-truth admission proof 的正文中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。

    Returns:
        `manager_profile.v1` 字段族；Slice 3 包含五个已授权 top-level subvalues。

    Raises:
        无显式抛出。
    """

    selected_values, ambiguous_paths = _select_manager_profile_values(intermediate, context)
    value = _build_manager_profile_value(selected_values)
    gaps = _manager_profile_source_truth_gaps(value, ambiguous_paths)
    status = _manager_profile_status(value, ambiguous_paths)
    anchors = _dedupe_anchors(
        selected_values[output_path].anchor
        for output_path in _manager_profile_emitted_output_paths(value, selected_values)
    )
    return FundFieldFamilyResult(
        field_family_id="manager_profile.v1",
        chapter_ids=_CHAPTER_IDS["manager_profile.v1"],
        value=value,
        status=status,
        extraction_mode="missing" if status == "missing" else "direct",
        anchors=anchors,
        gaps=gaps,
        source_provenance=source_provenance,
        candidate_evidence=(),
    )


def _select_manager_profile_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _ManagerProfileValueCandidate], set[str]]:
    """按 Slice 3 fail-closed 规则选择基金经理画像字段值。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        `(selected_values, ambiguous_paths)`；歧义路径不会进入 selected_values。

    Raises:
        无显式抛出。
    """

    selected_values: dict[str, _ManagerProfileValueCandidate] = {}
    ambiguous_paths: set[str] = set()
    portfolio_managers = _select_manager_profile_portfolio_managers(
        intermediate, context, ambiguous_paths
    )
    if portfolio_managers is not None:
        selected_values["portfolio_managers"] = portfolio_managers
    strategy_text = _select_manager_profile_strategy_text(intermediate, context, ambiguous_paths)
    if strategy_text is not None:
        selected_values["manager_strategy_text"] = strategy_text
    turnover_rate = _select_manager_profile_turnover_rate(intermediate, context, ambiguous_paths)
    if turnover_rate is not None:
        selected_values["turnover_rate"] = turnover_rate
    manager_alignment = _select_manager_profile_alignment(intermediate, context, ambiguous_paths)
    if manager_alignment is not None:
        selected_values["manager_alignment"] = manager_alignment
    holdings_snapshot = _select_manager_profile_holdings_snapshot(
        intermediate, context, ambiguous_paths
    )
    if holdings_snapshot is not None:
        selected_values["holdings_snapshot"] = holdings_snapshot
    return selected_values, ambiguous_paths


def _select_manager_profile_portfolio_managers(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _ManagerProfileValueCandidate | None:
    """从稳定经理 roster 表格行选择 portfolio_managers 值。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        存在至少一个非歧义经理行时返回字段候选，否则返回 None。

    Raises:
        无显式抛出。
    """

    entries: list[dict[str, object]] = []
    anchors: list[EvidenceAnchor] = []
    seen_by_name: dict[str, tuple[str, dict[str, object], EvidenceAnchor]] = {}
    conflicted_names: set[str] = set()
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable" or not _manager_profile_roster_table_allowed(table):
            continue
        rows = _manager_profile_rows_by_index(table)
        for row_index in sorted(rows):
            entry = _manager_profile_roster_entry(table, row_index, rows[row_index], context)
            if entry is None:
                continue
            entry_value, anchor = entry
            name = str(entry_value["name"])
            normalized_name = _normalize_match_text(name)
            normalized_entry = _normalize_manager_profile_roster_entry(entry_value)
            previous = seen_by_name.get(normalized_name)
            if previous is None:
                seen_by_name[normalized_name] = (normalized_entry, entry_value, anchor)
                continue
            if previous[0] != normalized_entry:
                conflicted_names.add(normalized_name)
                ambiguous_paths.add("portfolio_managers")
    for normalized_name, (_normalized_entry, entry_value, anchor) in seen_by_name.items():
        if normalized_name in conflicted_names:
            continue
        entries.append(entry_value)
        anchors.append(anchor)
    if not entries or not anchors:
        return None
    value = {
        "schema_version": "portfolio_manager_tenure_list.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "portfolio_managers": entries,
    }
    return _ManagerProfileValueCandidate(
        output_path="portfolio_managers",
        value=value,
        anchor=anchors[0],
        source_field_path="portfolio_managers",
    )


def _manager_profile_roster_table_allowed(table: FundDisclosureTableBlockLike) -> bool:
    """判断表格 heading/caption 是否属于经理 roster 允许来源。

    Args:
        table: FDD table block。

    Returns:
        表格上下文命中经理 roster heading 时返回 True。

    Raises:
        无显式抛出。
    """

    texts = (
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
    )
    return _matches_any_token(texts, _MANAGER_PROFILE_ROSTER_HEADINGS)


def _manager_profile_rows_by_index(
    table: FundDisclosureTableBlockLike,
) -> dict[int, tuple[FundDisclosureCellLike, ...]]:
    """按 row_index 分组稳定 table cells。

    Args:
        table: FDD table block。

    Returns:
        row_index 到稳定 cells 的映射。

    Raises:
        无显式抛出。
    """

    rows: dict[int, list[FundDisclosureCellLike]] = {}
    for cell in sorted(table.cells, key=lambda item: (item.row_index, item.column_index)):
        if cell.locator_stability != "stable":
            continue
        rows.setdefault(cell.row_index, []).append(cell)
    return {row_index: tuple(cells) for row_index, cells in rows.items()}


def _manager_profile_roster_entry(
    table: FundDisclosureTableBlockLike,
    row_index: int,
    cells: tuple[FundDisclosureCellLike, ...],
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, object], EvidenceAnchor] | None:
    """从单行稳定 cells 构造经理 roster entry。

    Args:
        table: FDD table block。
        row_index: 表格行号。
        cells: 当前行稳定 cells。
        context: Processor dispatch 身份。

    Returns:
        `(entry, anchor)`；缺姓名或缺同源经理角色语境时返回 None。

    Raises:
        无显式抛出。
    """

    name = _manager_profile_row_value(cells, _MANAGER_PROFILE_ROSTER_NAME_LABELS)
    if name is None:
        return None
    role = _manager_profile_row_value(cells, _MANAGER_PROFILE_ROSTER_ROLE_LABELS)
    row_context = _manager_profile_roster_row_context(cells)
    if role is not None and "基金经理" not in role:
        return None
    if role is None:
        if not _matches_any_token(row_context, ("基金经理",)):
            return None
        role = _first_non_empty(
            tuple(text for text in row_context if text and "基金经理" in text)
        )
    start_date = _manager_profile_row_value(cells, _MANAGER_PROFILE_ROSTER_START_DATE_LABELS)
    end_date = _manager_profile_row_value(cells, _MANAGER_PROFILE_ROSTER_END_DATE_LABELS)
    anchor_cell = _manager_profile_first_stable_cell(cells)
    table_id = anchor_cell.table_id or table.table_id
    row_locator = (
        f"field=portfolio_managers; table_id={table_id}; row={row_index}; manager={name}"
    )
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=anchor_cell.section_anchor or table.section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=_truncate(" ".join(text for text in (name, role, start_date, end_date) if text)),
    )
    entry: dict[str, object] = {
        "name": name,
        "role": role,
        "start_date": start_date,
        "source_anchor": {
            "section_id": anchor.section_id,
            "section_title": _first_non_empty(
                (
                    table.table_caption_or_nearby_heading,
                    table.heading_text,
                    *_tuple_text(table.heading_path),
                )
            ),
            "page_number": None,
            "table_id": table_id,
            "row_locator": f"portfolio_manager:{name}",
        },
    }
    if end_date:
        entry["end_date"] = end_date
    return entry, anchor


def _manager_profile_row_value(
    cells: tuple[FundDisclosureCellLike, ...],
    labels: tuple[str, ...],
) -> str | None:
    """读取当前行中指定 label 对应的非空 disclosed value。

    Args:
        cells: 当前行稳定 cells。
        labels: 允许标签。

    Returns:
        首个匹配 label 的 disclosed value；无匹配时返回 None。

    Raises:
        无显式抛出。
    """

    for cell in cells:
        if not (
            _path_contains_any_label(cell.column_header_path, labels)
            or _path_contains_any_label(cell.row_label_path, labels)
        ):
            continue
        value = _manager_profile_cell_value(cell)
        if value and not _path_contains_any_label((value,), labels):
            return value
    return None


def _manager_profile_roster_row_context(
    cells: tuple[FundDisclosureCellLike, ...],
) -> tuple[str | None, ...]:
    """返回 roster 行级 role guard context，不使用表格 broad heading 自守卫。

    Args:
        cells: 当前行稳定 cells。

    Returns:
        row/cell label 与 disclosed cell 文本。

    Raises:
        无显式抛出。
    """

    context: list[str | None] = []
    for cell in cells:
        context.extend(
            (
                cell.cell_text_normalized,
                cell.cell_text,
                *_tuple_text(cell.row_label_path),
                *_tuple_text(cell.column_header_path),
            )
        )
    return tuple(context)


def _manager_profile_first_stable_cell(
    cells: tuple[FundDisclosureCellLike, ...],
) -> FundDisclosureCellLike:
    """返回当前行第一个稳定 cell。

    Args:
        cells: 当前行稳定 cells。

    Returns:
        按 column_index 排序后的第一个 cell。

    Raises:
        IndexError: 调用方传入空行时由 tuple 索引抛出。
    """

    return sorted(cells, key=lambda item: item.column_index)[0]


def _select_manager_profile_strategy_text(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _ManagerProfileValueCandidate | None:
    """从稳定 strategy/outlook 段落选择 manager_strategy_text 值。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        至少包含 strategy_summary 或 market_outlook 时返回候选。

    Raises:
        无显式抛出。
    """

    grouped_texts: dict[str, list[str]] = {
        "manager_strategy_text.strategy_summary": [],
        "manager_strategy_text.market_outlook": [],
    }
    grouped_anchors: dict[str, _ManagerProfileValueCandidate] = {}
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        text = _manager_profile_paragraph_text(paragraph)
        if not text:
            continue
        if _manager_profile_paragraph_matches_strategy(paragraph, _MANAGER_PROFILE_STRATEGY_HEADINGS):
            _append_manager_profile_strategy_group(
                grouped_texts,
                grouped_anchors,
                "manager_strategy_text.strategy_summary",
                text,
                paragraph_index,
                paragraph,
                context,
            )
        if _manager_profile_paragraph_matches_strategy(paragraph, _MANAGER_PROFILE_OUTLOOK_HEADINGS):
            _append_manager_profile_strategy_group(
                grouped_texts,
                grouped_anchors,
                "manager_strategy_text.market_outlook",
                text,
                paragraph_index,
                paragraph,
                context,
            )
    selected: dict[str, _ManagerProfileValueCandidate] = {}
    for output_path, texts in grouped_texts.items():
        if not texts:
            continue
        first_candidate = grouped_anchors[output_path]
        selected[output_path] = _ManagerProfileValueCandidate(
            output_path=output_path,
            value="\n".join(texts),
            anchor=first_candidate.anchor,
            source_field_path=first_candidate.source_field_path,
        )
    strategy_summary = _selected_manager_profile_value(
        selected, "manager_strategy_text.strategy_summary"
    )
    market_outlook = _selected_manager_profile_value(
        selected, "manager_strategy_text.market_outlook"
    )
    if strategy_summary is None and market_outlook is None:
        return None
    value = {
        "strategy_summary": strategy_summary,
        "market_outlook": market_outlook,
    }
    anchor = selected[
        "manager_strategy_text.strategy_summary"
        if "manager_strategy_text.strategy_summary" in selected
        else "manager_strategy_text.market_outlook"
    ].anchor
    return _ManagerProfileValueCandidate(
        output_path="manager_strategy_text",
        value=value,
        anchor=anchor,
        source_field_path="manager_strategy_text",
    )


def _append_manager_profile_strategy_group(
    grouped_texts: dict[str, list[str]],
    grouped_anchors: dict[str, _ManagerProfileValueCandidate],
    output_path: str,
    text: str,
    paragraph_index: int,
    paragraph: FundDisclosureParagraphBlockLike,
    context: FundProcessorDispatchKey,
) -> None:
    """追加 strategy/outlook 段落文本并保留首个 anchor。

    Args:
        grouped_texts: output path 到段落文本列表的映射。
        grouped_anchors: output path 到首个候选 anchor 的映射。
        output_path: 目标输出路径。
        text: 当前段落披露文本。
        paragraph_index: paragraph tuple 索引。
        paragraph: FDD paragraph block。
        context: Processor dispatch 身份。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    grouped_texts[output_path].append(text)
    if output_path in grouped_anchors:
        return
    grouped_anchors[output_path] = _manager_profile_paragraph_candidate(
        output_path,
        text,
        paragraph_index,
        paragraph,
        context,
    )


def _manager_profile_paragraph_matches_strategy(
    paragraph: FundDisclosureParagraphBlockLike,
    headings: tuple[str, ...],
) -> bool:
    """判断 paragraph 是否位于 strategy/outlook 允许 heading 下。

    Args:
        paragraph: FDD paragraph block。
        headings: 允许 heading tokens。

    Returns:
        heading_path 命中时返回 True。

    Raises:
        无显式抛出。
    """

    return _matches_any_token(_tuple_text(paragraph.heading_path), headings)


def _manager_profile_paragraph_candidate(
    output_path: str,
    value: str,
    paragraph_index: int,
    paragraph: FundDisclosureParagraphBlockLike,
    context: FundProcessorDispatchKey,
) -> _ManagerProfileValueCandidate:
    """构造 paragraph-backed manager_profile 字段候选。

    Args:
        output_path: 目标输出路径。
        value: 输出文本。
        paragraph_index: paragraph tuple 索引。
        paragraph: FDD paragraph block。
        context: Processor dispatch 身份。

    Returns:
        字段值候选。

    Raises:
        无显式抛出。
    """

    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=paragraph.section_id,
        page_number=None,
        table_id=None,
        row_locator=f"field={output_path}; block_id={paragraph.block_id}",
        note=_truncate(value),
    )
    return _ManagerProfileValueCandidate(
        output_path=output_path,
        value=value,
        anchor=anchor,
        source_field_path=f"paragraph_blocks[{paragraph_index}]",
    )


def _select_manager_profile_turnover_rate(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _ManagerProfileValueCandidate | None:
    """从稳定表格或段落选择已披露 turnover_rate 百分比。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        有百分比换手率时返回候选；basis-only 返回 None。

    Raises:
        无显式抛出。
    """

    rate_candidates: list[_ManagerProfileValueCandidate] = []
    basis_candidates: list[_ManagerProfileValueCandidate] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            context_text = _manager_profile_turnover_cell_context(table, cell)
            if not _matches_any_token((context_text,), _MANAGER_PROFILE_TURNOVER_LABELS):
                continue
            value_text = _return_attribution_percent_text(_manager_profile_cell_value(cell))
            if value_text is not None:
                rate_candidates.append(
                    _manager_profile_cell_candidate(
                        "turnover_rate.turnover_rate",
                        value_text,
                        table_index,
                        cell_index,
                        table,
                        cell,
                        context,
                    )
                )
            if _matches_any_token((context_text,), _MANAGER_PROFILE_TURNOVER_BASIS_LABELS):
                basis_candidates.append(
                    _manager_profile_cell_candidate(
                        "turnover_rate.turnover_basis",
                        _manager_profile_cell_value(cell),
                        table_index,
                        cell_index,
                        table,
                        cell,
                        context,
                    )
                )
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        text = _manager_profile_paragraph_text(paragraph)
        if not _matches_any_token((text, *_tuple_text(paragraph.heading_path)), _MANAGER_PROFILE_TURNOVER_LABELS):
            continue
        value_text = _return_attribution_percent_text(text)
        if value_text is not None:
            rate_candidates.append(
                _manager_profile_paragraph_candidate(
                    "turnover_rate.turnover_rate",
                    value_text,
                    paragraph_index,
                    paragraph,
                    context,
                )
            )
        if _matches_any_token((text, *_tuple_text(paragraph.heading_path)), _MANAGER_PROFILE_TURNOVER_BASIS_LABELS):
            basis_candidates.append(
                _manager_profile_paragraph_candidate(
                    "turnover_rate.turnover_basis",
                    text,
                    paragraph_index,
                    paragraph,
                    context,
                )
            )
    selected_rate = _resolve_manager_profile_candidate(
        "turnover_rate.turnover_rate", tuple(rate_candidates), ambiguous_paths
    )
    if selected_rate is None:
        return None
    selected_basis = _resolve_manager_profile_candidate(
        "turnover_rate.turnover_basis", tuple(basis_candidates), ambiguous_paths
    )
    value = {
        "turnover_rate": selected_rate.value,
        "turnover_basis": None if selected_basis is None else selected_basis.value,
    }
    return _ManagerProfileValueCandidate(
        output_path="turnover_rate",
        value=value,
        anchor=selected_rate.anchor,
        source_field_path=selected_rate.source_field_path,
    )


def _select_manager_profile_alignment(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _ManagerProfileValueCandidate | None:
    """从稳定段落或表格选择基金经理/从业人员持有披露。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        至少存在 manager_holding 或 employee_holding 时返回候选；judgment 固定为 None。

    Raises:
        无显式抛出。
    """

    candidates: dict[str, list[_ManagerProfileValueCandidate]] = {
        "manager_alignment.manager_holding": [],
        "manager_alignment.employee_holding": [],
    }
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        text = _manager_profile_paragraph_text(paragraph)
        source_texts = (text, *_tuple_text(paragraph.heading_path))
        guard_context = _manager_profile_paragraph_guard_context("manager_alignment", paragraph)
        if not _manager_profile_alignment_source_allowed(source_texts, guard_context):
            continue
        for output_path in _manager_profile_alignment_output_paths(source_texts):
            candidates[output_path].append(
                _manager_profile_paragraph_candidate(
                    output_path,
                    text,
                    paragraph_index,
                    paragraph,
                    context,
                )
            )
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        rows = _manager_profile_rows_by_index(table)
        for row_index in sorted(rows):
            cells = rows[row_index]
            source_texts = _manager_profile_alignment_row_context(table, cells)
            if not _manager_profile_alignment_source_allowed(source_texts, source_texts):
                continue
            value = _manager_profile_alignment_row_value(cells)
            if value is None:
                continue
            anchor_cell = _manager_profile_first_stable_cell(cells)
            cell_index = _manager_profile_cell_original_index(table, anchor_cell)
            for output_path in _manager_profile_alignment_output_paths(source_texts):
                candidates[output_path].append(
                    _manager_profile_cell_candidate(
                        output_path,
                        value,
                        table_index,
                        cell_index,
                        table,
                        anchor_cell,
                        context,
                    )
                )
    selected_manager = _resolve_manager_profile_candidate(
        "manager_alignment.manager_holding",
        tuple(candidates["manager_alignment.manager_holding"]),
        ambiguous_paths,
    )
    selected_employee = _resolve_manager_profile_candidate(
        "manager_alignment.employee_holding",
        tuple(candidates["manager_alignment.employee_holding"]),
        ambiguous_paths,
    )
    if selected_manager is None and selected_employee is None:
        return None
    value = {
        "manager_holding": None if selected_manager is None else selected_manager.value,
        "employee_holding": None if selected_employee is None else selected_employee.value,
        "judgment": None,
    }
    anchor = selected_manager.anchor if selected_manager is not None else selected_employee.anchor
    source_field_path = (
        selected_manager.source_field_path
        if selected_manager is not None
        else selected_employee.source_field_path
    )
    return _ManagerProfileValueCandidate(
        output_path="manager_alignment",
        value=value,
        anchor=anchor,
        source_field_path=source_field_path,
    )


def _manager_profile_alignment_source_allowed(
    texts: tuple[str | None, ...],
    guard_context: tuple[str | None, ...],
) -> bool:
    """判断 source 是否满足 manager_alignment 强 token 或 generic guard。

    Args:
        texts: 当前 source 候选文本。
        guard_context: generic token 同源 guard 文本。

    Returns:
        命中允许持有披露语境时返回 True。

    Raises:
        无显式抛出。
    """

    return _matches_guarded_manager_profile_source(
        texts,
        _MANAGER_PROFILE_ALIGNMENT_STRONG_TOKENS,
        _MANAGER_PROFILE_ALIGNMENT_GENERIC_TOKENS,
        guard_context,
        _MANAGER_PROFILE_ALIGNMENT_GUARD_TOKENS,
    )


def _manager_profile_alignment_output_paths(
    texts: tuple[str | None, ...],
) -> tuple[str, ...]:
    """按披露语境判断 alignment 值归属 manager 或 employee。

    Args:
        texts: 当前 source 文本集合。

    Returns:
        可写入的 alignment 子路径；无明确归属时返回空元组。

    Raises:
        无显式抛出。
    """

    output_paths: list[str] = []
    if _matches_any_token(texts, _MANAGER_PROFILE_ALIGNMENT_MANAGER_TOKENS):
        output_paths.append("manager_alignment.manager_holding")
    if _matches_any_token(texts, _MANAGER_PROFILE_ALIGNMENT_EMPLOYEE_TOKENS):
        output_paths.append("manager_alignment.employee_holding")
    return tuple(output_paths)


def _manager_profile_alignment_row_context(
    table: FundDisclosureTableBlockLike,
    cells: tuple[FundDisclosureCellLike, ...],
) -> tuple[str | None, ...]:
    """拼接 alignment 表格行同源上下文。

    Args:
        table: parent table block。
        cells: 同一行稳定 cells。

    Returns:
        表格标题、路径、行列标签与 cell 文本集合。

    Raises:
        无显式抛出。
    """

    context: list[str | None] = [
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
    ]
    for cell in cells:
        context.extend(
            (
                cell.cell_text_normalized,
                cell.cell_text,
                *_tuple_text(cell.row_label_path),
                *_tuple_text(cell.column_header_path),
                *_tuple_text(cell.heading_path),
            )
        )
    return tuple(context)


def _manager_profile_alignment_row_value(
    cells: tuple[FundDisclosureCellLike, ...],
) -> str | None:
    """选择 alignment 行中披露的持有值或区间文本。

    Args:
        cells: 同一行稳定 cells。

    Returns:
        首个非标签值；仅有标签文本时返回该行首个非空披露文本。

    Raises:
        无显式抛出。
    """

    fallback: str | None = None
    for cell in sorted(cells, key=lambda item: item.column_index):
        value = _manager_profile_cell_value(cell)
        if not value:
            continue
        if fallback is None:
            fallback = value
        if _manager_profile_alignment_value_is_label(value):
            continue
        if _path_contains_any_label(
            cell.column_header_path,
            tuple(_MANAGER_PROFILE_GENERIC_TABLE_HEADERS),
        ):
            return value
        if not _matches_any_token(
            (value,),
            (
                *_MANAGER_PROFILE_ALIGNMENT_STRONG_TOKENS,
                *_MANAGER_PROFILE_ALIGNMENT_GENERIC_TOKENS,
            ),
        ):
            return value
    return fallback


def _manager_profile_alignment_value_is_label(value: str) -> bool:
    """判断 alignment cell 文本是否只是标签而非披露值。

    Args:
        value: cell 披露文本。

    Returns:
        文本等同于持有语境标签时返回 True。

    Raises:
        无显式抛出。
    """

    return _matches_any_token(
        (value,),
        (
            *_MANAGER_PROFILE_ALIGNMENT_STRONG_TOKENS,
            *_MANAGER_PROFILE_ALIGNMENT_GENERIC_TOKENS,
        ),
    )


def _select_manager_profile_holdings_snapshot(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _ManagerProfileValueCandidate | None:
    """从稳定持仓表格选择前十持仓与行业分布快照。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        至少存在 top_holdings 或 industry_distribution 时返回候选。

    Raises:
        无显式抛出。
    """

    top_rows, top_anchor = _select_manager_profile_holdings_rows(
        intermediate,
        context,
        ambiguous_paths,
        output_path="holdings_snapshot.top_holdings",
        headings=_MANAGER_PROFILE_HOLDINGS_TOP_HEADINGS,
        identity_labels=_MANAGER_PROFILE_TOP_HOLDINGS_IDENTITY_LABELS,
        limit=10,
    )
    industry_rows, industry_anchor = _select_manager_profile_holdings_rows(
        intermediate,
        context,
        ambiguous_paths,
        output_path="holdings_snapshot.industry_distribution",
        headings=_MANAGER_PROFILE_HOLDINGS_INDUSTRY_HEADINGS,
        identity_labels=_MANAGER_PROFILE_INDUSTRY_IDENTITY_LABELS,
        limit=None,
    )
    if not top_rows and not industry_rows:
        return None
    value = {
        "top_holdings": top_rows or None,
        "top_holdings_status": "direct_top_ten" if top_rows else "missing",
        "top_holdings_source": "top_ten" if top_rows else "none",
        "industry_distribution": industry_rows or None,
        "industry_distribution_status": "direct" if industry_rows else "missing",
    }
    anchor = top_anchor if top_anchor is not None else industry_anchor
    if anchor is None:
        return None
    return _ManagerProfileValueCandidate(
        output_path="holdings_snapshot",
        value=value,
        anchor=anchor,
        source_field_path="holdings_snapshot",
    )


def _select_manager_profile_holdings_rows(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
    *,
    output_path: str,
    headings: tuple[str, ...],
    identity_labels: tuple[str, ...],
    limit: int | None,
) -> tuple[list[dict[str, str]], EvidenceAnchor | None]:
    """选择指定 holdings_snapshot 子表的非冲突披露行。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。
        output_path: 目标输出路径。
        headings: 允许的表格 heading/caption tokens。
        identity_labels: 行身份列 labels。
        limit: 最大行数；None 表示不限。

    Returns:
        `(rows, first_anchor)`；冲突 identity 行被省略。

    Raises:
        无显式抛出。
    """

    seen_rows: dict[str, tuple[str, dict[str, str], EvidenceAnchor]] = {}
    conflicted_identities: set[str] = set()
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable" or not _manager_profile_holdings_table_allowed(
            table, headings
        ):
            continue
        rows = _manager_profile_rows_by_index(table)
        for row_index in sorted(rows):
            row = _manager_profile_holdings_row_dict(rows[row_index])
            if row is None:
                continue
            identity = _manager_profile_holdings_row_identity(row, identity_labels)
            normalized_row = _normalize_manager_profile_value(row)
            anchor_cell = _manager_profile_first_stable_cell(rows[row_index])
            cell_index = _manager_profile_cell_original_index(table, anchor_cell)
            candidate = _manager_profile_cell_candidate(
                output_path,
                row,
                table_index,
                cell_index,
                table,
                anchor_cell,
                context,
            )
            previous = seen_rows.get(identity)
            if previous is None:
                seen_rows[identity] = (normalized_row, row, candidate.anchor)
                continue
            if previous[0] != normalized_row:
                conflicted_identities.add(identity)
                ambiguous_paths.add(output_path)
    accepted_rows: list[dict[str, str]] = []
    anchors: list[EvidenceAnchor] = []
    for identity, (_normalized_row, row, anchor) in seen_rows.items():
        if identity in conflicted_identities:
            continue
        accepted_rows.append(row)
        anchors.append(anchor)
        if limit is not None and len(accepted_rows) >= limit:
            break
    first_anchor = anchors[0] if anchors else None
    return accepted_rows, first_anchor


def _manager_profile_holdings_table_allowed(
    table: FundDisclosureTableBlockLike,
    headings: tuple[str, ...],
) -> bool:
    """判断 holdings_snapshot 表格是否位于允许 heading 下。

    Args:
        table: FDD table block。
        headings: 当前子表允许 heading tokens。

    Returns:
        表格上下文命中指定持仓 heading 时返回 True。

    Raises:
        无显式抛出。
    """

    texts = (
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
    )
    return _matches_any_token(texts, headings) and _matches_any_token(
        texts, _MANAGER_PROFILE_HOLDINGS_CONTEXT_HEADINGS
    )


def _manager_profile_holdings_row_dict(
    cells: tuple[FundDisclosureCellLike, ...],
) -> dict[str, str] | None:
    """把同一稳定表格行转换为中文表头到披露 cell 文本的映射。

    Args:
        cells: 同一行稳定 cells。

    Returns:
        非空 row dict；缺少可识别中文表头或无披露值时返回 None。

    Raises:
        无显式抛出。
    """

    row: dict[str, str] = {}
    for cell in sorted(cells, key=lambda item: item.column_index):
        header = _manager_profile_holdings_cell_header(cell)
        value = _manager_profile_cell_value(cell)
        if header is None or not value:
            continue
        row[header] = value
    if not row:
        return None
    return row


def _manager_profile_holdings_cell_header(cell: FundDisclosureCellLike) -> str | None:
    """选择 holdings_snapshot cell 的披露中文列头。

    Args:
        cell: FDD table cell。

    Returns:
        非 generic 的 column header；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    for header in reversed(cell.column_header_path):
        normalized = _normalize_match_text(header)
        if not normalized or normalized in _MANAGER_PROFILE_GENERIC_TABLE_HEADERS:
            continue
        return header
    return None


def _manager_profile_holdings_row_identity(
    row: dict[str, str],
    identity_labels: tuple[str, ...],
) -> str:
    """生成 holdings_snapshot 行去重身份。

    Args:
        row: 已构造的披露行。
        identity_labels: 优先用于身份判断的列名。

    Returns:
        规范化后的行身份；没有专用身份列时使用整行首个披露值。

    Raises:
        无显式抛出。
    """

    identity_values = [
        row[label]
        for label in identity_labels
        if label in row and _normalize_match_text(row[label])
    ]
    if identity_values:
        return "|".join(_normalize_match_text(value) for value in identity_values)
    first_key = next(iter(row))
    return _normalize_match_text(row[first_key])


def _manager_profile_cell_original_index(
    table: FundDisclosureTableBlockLike,
    target_cell: FundDisclosureCellLike,
) -> int:
    """返回 cell 在 table.cells tuple 中的原始索引。

    Args:
        table: parent table block。
        target_cell: 目标 cell。

    Returns:
        原始 tuple index。

    Raises:
        ValueError: target_cell 不属于 table.cells 时抛出。
    """

    for cell_index, cell in enumerate(table.cells):
        if cell is target_cell:
            return cell_index
    raise ValueError("target_cell not found in table.cells")


def _manager_profile_cell_candidate(
    output_path: str,
    value: object,
    table_index: int,
    cell_index: int,
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
    context: FundProcessorDispatchKey,
) -> _ManagerProfileValueCandidate:
    """构造 table/cell-backed manager_profile 字段候选。

    Args:
        output_path: 目标输出路径。
        value: 输出值。
        table_index: table tuple 索引。
        cell_index: cell tuple 索引。
        table: parent table block。
        cell: FDD table cell。
        context: Processor dispatch 身份。

    Returns:
        字段值候选。

    Raises:
        无显式抛出。
    """

    table_id = cell.table_id or table.table_id
    row_locator = (
        f"field={output_path}; table_id={table_id}; "
        f"row={cell.row_index}; column={cell.column_index}"
    )
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=cell.section_anchor or table.section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=_truncate(_manager_profile_cell_value(cell)),
    )
    return _ManagerProfileValueCandidate(
        output_path=output_path,
        value=value,
        anchor=anchor,
        source_field_path=f"table_blocks[{table_index}].cells[{cell_index}]",
    )


def _manager_profile_turnover_cell_context(
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
) -> str:
    """拼接 turnover cell 周边语义。

    Args:
        table: parent table block。
        cell: FDD table cell。

    Returns:
        表格标题、路径、行列标签和值的合并文本。

    Raises:
        无显式抛出。
    """

    return " ".join(
        part
        for part in (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
            *_tuple_text(cell.heading_path),
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            cell.cell_text_normalized,
            cell.cell_text,
        )
        if part
    )


def _manager_profile_cell_value(cell: FundDisclosureCellLike) -> str:
    """返回 manager_profile cell 的规范化披露文本。

    Args:
        cell: FDD table cell。

    Returns:
        `cell_text_normalized` 非空时优先，否则回退 `cell_text`。

    Raises:
        无显式抛出。
    """

    value = cell.cell_text_normalized.strip() if cell.cell_text_normalized else ""
    if value:
        return value
    return cell.cell_text.strip()


def _manager_profile_paragraph_text(paragraph: FundDisclosureParagraphBlockLike) -> str:
    """返回 manager_profile paragraph 的规范化披露文本。

    Args:
        paragraph: FDD paragraph block。

    Returns:
        `text_normalized` 非空时优先，否则回退 `text_raw`。

    Raises:
        无显式抛出。
    """

    text = paragraph.text_normalized.strip() if paragraph.text_normalized else ""
    if text:
        return text
    return paragraph.text_raw.strip()


def _resolve_manager_profile_candidate(
    output_path: str,
    candidates: tuple[_ManagerProfileValueCandidate, ...],
    ambiguous_paths: set[str],
) -> _ManagerProfileValueCandidate | None:
    """按重复/歧义规则解析 manager_profile 候选。

    Args:
        output_path: 目标输出路径。
        candidates: 同一路径候选。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        唯一可采信候选；无候选或冲突时返回 None。

    Raises:
        无显式抛出。
    """

    if not candidates:
        return None
    normalized_values = {
        _normalize_manager_profile_value(candidate.value) for candidate in candidates
    }
    if len(normalized_values) > 1:
        ambiguous_paths.add(output_path)
        return None
    return candidates[0]


def _normalize_manager_profile_value(value: object) -> str:
    """规范化 manager_profile 候选值用于冲突判断。

    Args:
        value: 候选值。

    Returns:
        稳定比较字符串。

    Raises:
        无显式抛出。
    """

    if isinstance(value, dict):
        return "|".join(f"{key}={_normalize_manager_profile_value(value[key])}" for key in sorted(value))
    if isinstance(value, list):
        return "||".join(_normalize_manager_profile_value(item) for item in value)
    return _normalize_match_text(str(value))


def _normalize_manager_profile_roster_entry(entry: dict[str, object]) -> str:
    """规范化 roster entry 的披露语义值，排除 locator anchor。

    Args:
        entry: portfolio manager entry。

    Returns:
        只包含姓名、角色和披露日期的稳定比较字符串。

    Raises:
        无显式抛出。
    """

    semantic_entry = {
        key: value for key, value in entry.items() if key != "source_anchor"
    }
    return _normalize_manager_profile_value(semantic_entry)


def _build_manager_profile_value(
    selected_values: dict[str, _ManagerProfileValueCandidate],
) -> dict[str, object]:
    """构造 `manager_profile.v1.value` Slice 3 public shape。

    Args:
        selected_values: 已解析的输出路径值。

    Returns:
        只包含 schema_version 与已发出的 top-level subvalues；全缺时返回空字典。

    Raises:
        无显式抛出。
    """

    value: dict[str, object] = {}
    for top_level in _MANAGER_PROFILE_REQUIRED_TOP_LEVEL:
        selected = selected_values.get(top_level)
        if selected is not None:
            value[top_level] = selected.value
    if not value:
        return {}
    return {"schema_version": "manager_profile.v1", **value}


def _manager_profile_emitted_output_paths(
    value: dict[str, object],
    selected_values: dict[str, _ManagerProfileValueCandidate],
) -> tuple[str, ...]:
    """返回实际进入 public value 的 manager_profile output paths。

    Args:
        value: 已构造的 manager_profile value。
        selected_values: 已解析的输出路径值。

    Returns:
        需要进入 family anchors 的输出路径元组。

    Raises:
        无显式抛出。
    """

    return tuple(
        top_level
        for top_level in _MANAGER_PROFILE_REQUIRED_TOP_LEVEL
        if top_level in value and top_level in selected_values
    )


def _manager_profile_source_truth_gaps(
    value: dict[str, object],
    ambiguous_paths: set[str],
) -> tuple[FundExtractionGap, ...]:
    """构造 manager_profile.v1 source-truth 字段族本地 gaps。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 发生 duplicate ambiguity 的输出路径集合。

    Returns:
        missing/partial/ambiguity gaps。

    Raises:
        无显式抛出。
    """

    gaps: list[FundExtractionGap] = []
    for output_path in sorted(ambiguous_paths):
        gaps.append(
            FundExtractionGap(
                gap_code="ambiguous_table_or_locator",
                message=f"{output_path} 存在多个冲突的稳定 FDD locator 值",
                field_family_id="manager_profile.v1",
                source_field_path=output_path,
                source_boundary="ambiguous_locator",
                required=True,
            )
        )
    missing_top_level = tuple(
        top_level for top_level in _MANAGER_PROFILE_REQUIRED_TOP_LEVEL if top_level not in value
    )
    if not value:
        gaps.append(
            FundExtractionGap(
                gap_code="field_family_missing",
                message="manager_profile.v1 未形成 Slice 3 允许的 source-truth 字段值",
                field_family_id="manager_profile.v1",
                source_field_path=None,
                source_boundary="annual_report",
                required=True,
            )
        )
    elif missing_top_level:
        gaps.extend(
            FundExtractionGap(
                gap_code="field_family_partial",
                message=f"manager_profile.v1 缺少 required top-level value: {top_level}",
                field_family_id="manager_profile.v1",
                source_field_path=top_level,
                source_boundary="annual_report",
                required=True,
            )
            for top_level in missing_top_level
        )
    return tuple(gaps)


def _manager_profile_status(value: dict[str, object], ambiguous_paths: set[str]) -> str:
    """按五个 top-level 完整度派生 manager_profile 字段族状态。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 已发现的歧义输出路径集合。

    Returns:
        `accepted`、`partial` 或 `missing`。

    Raises:
        无显式抛出。
    """

    if all(top_level in value for top_level in _MANAGER_PROFILE_REQUIRED_TOP_LEVEL) and not ambiguous_paths:
        return "accepted"
    if value:
        return "partial"
    return "missing"


def _selected_manager_profile_value(
    selected_values: dict[str, _ManagerProfileValueCandidate],
    output_path: str,
) -> object | None:
    """返回已选择 output path 的字段值。

    Args:
        selected_values: 已解析的输出路径值。
        output_path: 目标输出路径。

    Returns:
        字段值；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    candidate = selected_values.get(output_path)
    if candidate is None:
        return None
    return candidate.value


def _select_return_attribution_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _ReturnAttributionValueCandidate], set[str]]:
    """按 Slice 2 fail-closed 规则选择收益归因字段值。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        `(selected_values, ambiguous_paths)`；歧义路径不会进入 selected_values。

    Raises:
        无显式抛出。
    """

    selected_values: dict[str, _ReturnAttributionValueCandidate] = {}
    ambiguous_paths: set[str] = set()
    selected_values.update(
        _select_return_attribution_nav_benchmark_values(intermediate, context, ambiguous_paths)
    )
    fee_candidates = _collect_return_attribution_fee_candidates(intermediate, context)
    for output_path in _RETURN_ATTRIBUTION_FEE_LABELS:
        selected = _resolve_return_attribution_candidate(
            output_path, fee_candidates.get(output_path, ()), ambiguous_paths
        )
        if selected is not None:
            selected_values[output_path] = selected
    tracking_candidates = _collect_return_attribution_tracking_error_candidates(
        intermediate, context
    )
    selected_tracking = _resolve_return_attribution_candidate(
        "tracking_error", tracking_candidates, ambiguous_paths
    )
    if selected_tracking is not None:
        selected_values["tracking_error"] = selected_tracking
    return selected_values, ambiguous_paths


def _select_return_attribution_nav_benchmark_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> dict[str, _ReturnAttributionValueCandidate]:
    """选择唯一同表同行的 NAV/benchmark 收益率组合。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        同行 NAV 与 benchmark 候选；缺任一侧或多行冲突时返回空字典。

    Raises:
        无显式抛出。
    """

    row_pairs: list[tuple[_ReturnAttributionValueCandidate, _ReturnAttributionValueCandidate]] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        nav_by_row: dict[int, _ReturnAttributionValueCandidate] = {}
        benchmark_by_row: dict[int, _ReturnAttributionValueCandidate] = {}
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            value_text = _return_attribution_percent_text(_return_attribution_cell_value(cell))
            if value_text is None:
                continue
            if _return_attribution_cell_matches_label(cell, _RETURN_ATTRIBUTION_NAV_LABELS):
                nav_by_row.setdefault(
                    cell.row_index,
                    _return_attribution_cell_candidate(
                        "nav_benchmark_performance.nav_growth_rate",
                        value_text,
                        table_index,
                        cell_index,
                        table,
                        cell,
                        context,
                        period_label=_return_attribution_cell_period_label(table, cell),
                    ),
                )
            if _return_attribution_cell_matches_label(cell, _RETURN_ATTRIBUTION_BENCHMARK_LABELS):
                benchmark_by_row.setdefault(
                    cell.row_index,
                    _return_attribution_cell_candidate(
                        "nav_benchmark_performance.benchmark_return_rate",
                        value_text,
                        table_index,
                        cell_index,
                        table,
                        cell,
                        context,
                        period_label=_return_attribution_cell_period_label(table, cell),
                    ),
                )
        for row_index, nav_candidate in nav_by_row.items():
            benchmark_candidate = benchmark_by_row.get(row_index)
            if benchmark_candidate is not None:
                row_pairs.append((nav_candidate, benchmark_candidate))
    if len(row_pairs) > 1:
        ambiguous_paths.add("nav_benchmark_performance")
        return {}
    if not row_pairs:
        return {}
    nav_candidate, benchmark_candidate = row_pairs[0]
    return {
        nav_candidate.output_path: nav_candidate,
        benchmark_candidate.output_path: benchmark_candidate,
    }


def _collect_return_attribution_fee_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> dict[str, tuple[_ReturnAttributionValueCandidate, ...]]:
    """收集管理费/托管费显式费率候选，见模板第 2 章 Cost。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        output path 到候选元组的映射。

    Raises:
        无显式抛出。
    """

    candidates: dict[str, list[_ReturnAttributionValueCandidate]] = {}
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            output_path = _match_return_attribution_fee_cell_output_path(cell)
            if output_path is None:
                continue
            value_text = _return_attribution_percent_text(_return_attribution_cell_value(cell))
            if value_text is None:
                continue
            candidates.setdefault(output_path, []).append(
                _return_attribution_cell_candidate(
                    output_path, value_text, table_index, cell_index, table, cell, context
                )
            )
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        for output_path, labels in _RETURN_ATTRIBUTION_FEE_LABELS.items():
            candidate = _return_attribution_fee_paragraph_candidate(
                output_path, labels, paragraph_index, paragraph, context
            )
            if candidate is not None:
                candidates.setdefault(output_path, []).append(candidate)
    return {key: tuple(value) for key, value in candidates.items()}


def _collect_return_attribution_tracking_error_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[_ReturnAttributionValueCandidate, ...]:
    """收集实际披露的跟踪误差候选，拒绝目标/控制/上限语境。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        跟踪误差候选元组。

    Raises:
        无显式抛出。
    """

    candidates: list[_ReturnAttributionValueCandidate] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            context_text = _return_attribution_cell_context_text(table, cell)
            if not _return_attribution_mentions_tracking_error(context_text):
                continue
            if _return_attribution_tracking_error_rejected(context_text):
                continue
            value_text = _return_attribution_percent_text(_return_attribution_cell_value(cell))
            ratio = _return_attribution_percent_ratio(value_text)
            if value_text is None or ratio is None:
                continue
            period_label = _return_attribution_cell_period_label(table, cell)
            candidates.append(
                _return_attribution_cell_candidate(
                    "tracking_error",
                    _return_attribution_tracking_error_value(
                        value_text=value_text,
                        ratio=ratio,
                        period_label=period_label,
                        annualized="年化" in _normalize_match_text(context_text),
                    ),
                    table_index,
                    cell_index,
                    table,
                    cell,
                    context,
                    period_label=period_label,
                )
            )
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        candidate = _return_attribution_tracking_error_paragraph_candidate(
            paragraph_index, paragraph, context
        )
        if candidate is not None:
            candidates.append(candidate)
    return tuple(candidates)


def _match_return_attribution_fee_cell_output_path(
    cell: FundDisclosureCellLike,
) -> str | None:
    """匹配费率 cell 的 public output path。

    Args:
        cell: FDD table cell。

    Returns:
        `fee_schedule.management_fee`、`fee_schedule.custody_fee` 或 None。

    Raises:
        无显式抛出。
    """

    for output_path, labels in _RETURN_ATTRIBUTION_FEE_LABELS.items():
        if _return_attribution_cell_matches_label(cell, labels):
            return output_path
    return None


def _return_attribution_cell_matches_label(
    cell: FundDisclosureCellLike,
    labels: tuple[str, ...],
) -> bool:
    """判断 cell 的标签路径是否命中指定 label。

    Args:
        cell: FDD table cell。
        labels: 允许标签。

    Returns:
        row label、column header 或 heading path 命中时返回 True。

    Raises:
        无显式抛出。
    """

    return (
        _path_contains_any_label(cell.row_label_path, labels)
        or _path_contains_any_label(cell.column_header_path, labels)
        or _path_contains_any_label(cell.heading_path, labels)
    )


def _return_attribution_cell_value(cell: FundDisclosureCellLike) -> str:
    """返回收益归因 cell 的规范化取值。

    Args:
        cell: FDD table cell。

    Returns:
        `cell_text_normalized` 非空时优先，否则回退 `cell_text`。

    Raises:
        无显式抛出。
    """

    value = cell.cell_text_normalized.strip() if cell.cell_text_normalized else ""
    if value:
        return value
    return cell.cell_text.strip()


def _return_attribution_cell_context_text(
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
) -> str:
    """拼接 cell 周边语义，供跟踪误差上下文判定。

    Args:
        table: parent table block。
        cell: FDD table cell。

    Returns:
        表格标题、路径、行列标签和值的合并文本。

    Raises:
        无显式抛出。
    """

    return " ".join(
        part
        for part in (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
            *_tuple_text(cell.heading_path),
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            cell.cell_text_normalized,
            cell.cell_text,
        )
        if part
    )


def _return_attribution_cell_period_label(
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
) -> str:
    """生成人可读的跟踪误差或表现期间标签。

    Args:
        table: parent table block。
        cell: FDD table cell。

    Returns:
        优先使用行标签；否则使用表格标题和行号。

    Raises:
        无显式抛出。
    """

    row_label = _first_non_empty(tuple(cell.row_label_path))
    if row_label != "candidate evidence":
        return row_label
    table_label = table.table_caption_or_nearby_heading or table.heading_text or table.table_id
    return f"{table_label} 第{cell.row_index}行"


def _return_attribution_cell_candidate(
    output_path: str,
    value: object,
    table_index: int,
    cell_index: int,
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
    context: FundProcessorDispatchKey,
    *,
    period_label: str | None = None,
) -> _ReturnAttributionValueCandidate:
    """构造 table/cell source-truth 候选。

    Args:
        output_path: 目标输出路径。
        value: 输出值。
        table_index: table tuple 索引。
        cell_index: cell tuple 索引。
        table: parent table block。
        cell: FDD table cell。
        context: Processor dispatch 身份。
        period_label: 可选人可读期间标签。

    Returns:
        收益归因字段值候选。

    Raises:
        无显式抛出。
    """

    anchor = _return_attribution_cell_anchor(output_path, table, cell, context)
    return _ReturnAttributionValueCandidate(
        output_path=output_path,
        value=value,
        anchor=anchor,
        source_field_path=f"table_blocks[{table_index}].cells[{cell_index}]",
        period_label=period_label,
    )


def _return_attribution_cell_anchor(
    output_path: str,
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
    context: FundProcessorDispatchKey,
) -> EvidenceAnchor:
    """构造收益归因 table/cell EvidenceAnchor。

    Args:
        output_path: 目标输出路径。
        table: parent table block。
        cell: FDD table cell。
        context: Processor dispatch 身份。

    Returns:
        source_kind 固定为 annual_report 的公共锚点。

    Raises:
        无显式抛出。
    """

    table_id = cell.table_id or table.table_id
    row_locator = (
        f"field={output_path}; table_id={table_id}; "
        f"row={cell.row_index}; column={cell.column_index}; cell_id={cell.cell_id}"
    )
    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=cell.section_anchor or table.section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=_truncate(_return_attribution_cell_value(cell)),
    )


def _return_attribution_fee_paragraph_candidate(
    output_path: str,
    labels: tuple[str, ...],
    paragraph_index: int,
    paragraph: FundDisclosureParagraphBlockLike,
    context: FundProcessorDispatchKey,
) -> _ReturnAttributionValueCandidate | None:
    """从显式费率 paragraph 中提取管理费或托管费。

    Args:
        output_path: 目标输出路径。
        labels: 允许费率标签。
        paragraph_index: paragraph tuple 索引。
        paragraph: FDD paragraph block。
        context: Processor dispatch 身份。

    Returns:
        命中显式 label 与百分比时返回候选；否则返回 None。

    Raises:
        无显式抛出。
    """

    text = paragraph.text_normalized.strip() if paragraph.text_normalized else ""
    if not text:
        text = paragraph.text_raw.strip()
    if not _return_attribution_text_starts_with_label(text, labels):
        return None
    value_text = _return_attribution_percent_text(text)
    if value_text is None:
        return None
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=paragraph.section_id,
        page_number=None,
        table_id=None,
        row_locator=f"field={output_path}; block_id={paragraph.block_id}",
        note=_truncate(text),
    )
    return _ReturnAttributionValueCandidate(
        output_path=output_path,
        value=value_text,
        anchor=anchor,
        source_field_path=f"paragraph_blocks[{paragraph_index}]",
    )


def _return_attribution_tracking_error_paragraph_candidate(
    paragraph_index: int,
    paragraph: FundDisclosureParagraphBlockLike,
    context: FundProcessorDispatchKey,
) -> _ReturnAttributionValueCandidate | None:
    """从 paragraph 中提取实际披露的跟踪误差。

    Args:
        paragraph_index: paragraph tuple 索引。
        paragraph: FDD paragraph block。
        context: Processor dispatch 身份。

    Returns:
        命中实际披露百分比时返回候选；否则返回 None。

    Raises:
        无显式抛出。
    """

    text = paragraph.text_normalized.strip() if paragraph.text_normalized else ""
    if not text:
        text = paragraph.text_raw.strip()
    if not _return_attribution_mentions_tracking_error(text):
        return None
    if _return_attribution_tracking_error_rejected(text):
        return None
    value_text = _return_attribution_percent_text(text)
    ratio = _return_attribution_percent_ratio(value_text)
    if value_text is None or ratio is None:
        return None
    period_label = _return_attribution_paragraph_period_label(paragraph)
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=paragraph.section_id,
        page_number=None,
        table_id=None,
        row_locator=f"field=tracking_error; block_id={paragraph.block_id}",
        note=_truncate(text),
    )
    return _ReturnAttributionValueCandidate(
        output_path="tracking_error",
        value=_return_attribution_tracking_error_value(
            value_text=value_text,
            ratio=ratio,
            period_label=period_label,
            annualized="年化" in _normalize_match_text(text),
        ),
        anchor=anchor,
        source_field_path=f"paragraph_blocks[{paragraph_index}]",
        period_label=period_label,
    )


def _return_attribution_paragraph_period_label(
    paragraph: FundDisclosureParagraphBlockLike,
) -> str:
    """生成 paragraph 跟踪误差的人可读期间标签。

    Args:
        paragraph: FDD paragraph block。

    Returns:
        heading path、block id 或报告期语义标签。

    Raises:
        无显式抛出。
    """

    text = paragraph.text_normalized or paragraph.text_raw
    if "过去一年" in text:
        return "过去一年"
    if "本报告期" in text:
        return "本报告期"
    if "报告期" in text:
        return "报告期"
    heading = " / ".join(part for part in paragraph.heading_path if part)
    if heading:
        return heading
    return f"段落 {paragraph.block_id}"


def _return_attribution_tracking_error_value(
    *,
    value_text: str,
    ratio: Decimal,
    period_label: str,
    annualized: bool,
) -> TrackingErrorValue:
    """构造直接披露语义的 TrackingErrorValue。

    Args:
        value_text: 年报披露百分比文本。
        ratio: 标准化小数比例。
        period_label: 人可读期间标签。
        annualized: 是否年化。

    Returns:
        公开 tracking_error 结构化值。

    Raises:
        无显式抛出。
    """

    return TrackingErrorValue(
        value=ratio,
        value_text=value_text,
        unit="ratio",
        period_label=period_label,
        period_start=None,
        period_end=None,
        annualized=annualized,
        source_type="direct_disclosure",
        calculation_method="disclosed",
        benchmark_identity_status="missing",
        benchmark_index_name=None,
        benchmark_index_code=None,
        fund_series_source=None,
        index_series_source=None,
        observation_count=None,
        frequency="annual_report_period",
        annualization_factor=None,
        input_period_complete=True,
        provenance_note="FundDisclosureDocument 年报直接披露的实际跟踪误差；未使用序列、基准收益率或标准差推导。",
    )


def _return_attribution_mentions_tracking_error(text: str) -> bool:
    """判断文本是否包含跟踪误差披露标签。

    Args:
        text: 候选上下文。

    Returns:
        包含允许跟踪误差 label 时返回 True。

    Raises:
        无显式抛出。
    """

    normalized_text = _normalize_match_text(text)
    return any(_normalize_match_text(label) in normalized_text for label in _RETURN_ATTRIBUTION_TRACKING_ERROR_LABELS)


def _return_attribution_tracking_error_rejected(text: str) -> bool:
    """判断跟踪误差上下文是否属于目标/控制/限制语境。

    Args:
        text: 候选上下文。

    Returns:
        命中禁止语境时返回 True。

    Raises:
        无显式抛出。
    """

    normalized_text = _normalize_match_text(text)
    return any(
        _normalize_match_text(token) in normalized_text
        for token in _RETURN_ATTRIBUTION_TRACKING_ERROR_REJECT_CONTEXT
    )


def _return_attribution_text_starts_with_label(text: str, labels: tuple[str, ...]) -> bool:
    """判断 paragraph 是否以显式 label 开头。

    Args:
        text: paragraph 文本。
        labels: 允许 label。

    Returns:
        `label:`、`label：` 或 label 直接开头时返回 True。

    Raises:
        无显式抛出。
    """

    normalized_text = _normalize_match_text(text)
    return any(normalized_text.startswith(_normalize_match_text(label)) for label in labels)


def _return_attribution_percent_text(text: str | None) -> str | None:
    """从候选文本中提取百分比原文。

    Args:
        text: 候选文本。

    Returns:
        规范化为 ASCII `%` 的百分比文本；未命中时返回 None。

    Raises:
        无显式抛出。
    """

    if text is None:
        return None
    match = _RETURN_ATTRIBUTION_PERCENT_PATTERN.search(text)
    if match is None:
        return None
    return f"{match.group('value').replace(',', '')}%"


def _return_attribution_percent_ratio(value_text: str | None) -> Decimal | None:
    """把百分比文本解析为小数比例。

    Args:
        value_text: 百分比文本。

    Returns:
        小数比例；不可解析时返回 None。

    Raises:
        无显式抛出。
    """

    if value_text is None:
        return None
    match = _RETURN_ATTRIBUTION_PERCENT_PATTERN.search(value_text)
    if match is None:
        return None
    try:
        return Decimal(match.group("value").replace(",", "")) / Decimal("100")
    except InvalidOperation:
        return None


def _resolve_return_attribution_candidate(
    output_path: str,
    candidates: tuple[_ReturnAttributionValueCandidate, ...],
    ambiguous_paths: set[str],
) -> _ReturnAttributionValueCandidate | None:
    """按重复/歧义规则解析收益归因候选。

    Args:
        output_path: 目标输出路径。
        candidates: 同一路径候选。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        唯一可采信候选；无候选或冲突时返回 None。

    Raises:
        无显式抛出。
    """

    if not candidates:
        return None
    normalized_values = {_normalize_return_attribution_value(candidate.value) for candidate in candidates}
    if len(normalized_values) > 1:
        ambiguous_paths.add(output_path)
        return None
    return candidates[0]


def _normalize_return_attribution_value(value: object) -> str:
    """规范化收益归因候选值用于冲突判断。

    Args:
        value: 候选值。

    Returns:
        稳定比较字符串。

    Raises:
        无显式抛出。
    """

    if isinstance(value, TrackingErrorValue):
        return f"{value.value_text}|{value.period_label}|{value.annualized}"
    return _normalize_match_text(str(value))


def _build_return_attribution_value(
    selected_values: dict[str, _ReturnAttributionValueCandidate],
) -> dict[str, object]:
    """构造 `return_attribution.v1.value` exact public shape。

    Args:
        selected_values: 已解析的输出路径值。

    Returns:
        只包含 `schema_version` 与三个已允许 top-level key 的 value；全缺时返回空字典。

    Raises:
        无显式抛出。
    """

    value: dict[str, object] = {}
    nav_benchmark = _build_return_attribution_nav_benchmark_value(selected_values)
    fee_schedule = _build_return_attribution_fee_schedule_value(selected_values)
    tracking_error = _build_return_attribution_tracking_error_value(selected_values)
    if nav_benchmark is not None:
        value["nav_benchmark_performance"] = nav_benchmark
    if fee_schedule is not None:
        value["fee_schedule"] = fee_schedule
    if tracking_error is not None:
        value["tracking_error"] = tracking_error
    if not value:
        return {}
    return {"schema_version": "return_attribution.v1", **value}


def _build_return_attribution_nav_benchmark_value(
    selected_values: dict[str, _ReturnAttributionValueCandidate],
) -> dict[str, object] | None:
    """构造同一稳定行的 NAV/benchmark 表现值。

    Args:
        selected_values: 已解析的输出路径值。

    Returns:
        同时包含 nav 和 benchmark 时返回 dict；否则返回 None。

    Raises:
        无显式抛出。
    """

    nav_growth_rate = _selected_return_attribution_value(
        selected_values, "nav_benchmark_performance.nav_growth_rate"
    )
    benchmark_return_rate = _selected_return_attribution_value(
        selected_values, "nav_benchmark_performance.benchmark_return_rate"
    )
    if nav_growth_rate is None or benchmark_return_rate is None:
        return None
    return {
        "nav_growth_rate": nav_growth_rate,
        "benchmark_return_rate": benchmark_return_rate,
    }


def _build_return_attribution_fee_schedule_value(
    selected_values: dict[str, _ReturnAttributionValueCandidate],
) -> dict[str, object] | None:
    """构造费率字段值，只允许管理费和托管费。

    Args:
        selected_values: 已解析的输出路径值。

    Returns:
        任一费率存在时返回包含两个允许 subkey 的 dict；全缺时返回 None。

    Raises:
        无显式抛出。
    """

    management_fee = _selected_return_attribution_value(
        selected_values, "fee_schedule.management_fee"
    )
    custody_fee = _selected_return_attribution_value(selected_values, "fee_schedule.custody_fee")
    if management_fee is None and custody_fee is None:
        return None
    return {
        "management_fee": management_fee,
        "custody_fee": custody_fee,
    }


def _build_return_attribution_tracking_error_value(
    selected_values: dict[str, _ReturnAttributionValueCandidate],
) -> TrackingErrorValue | None:
    """读取已采信的跟踪误差结构化值。

    Args:
        selected_values: 已解析的输出路径值。

    Returns:
        TrackingErrorValue；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    value = _selected_return_attribution_value(selected_values, "tracking_error")
    if isinstance(value, TrackingErrorValue):
        return value
    return None


def _selected_return_attribution_value(
    selected_values: dict[str, _ReturnAttributionValueCandidate],
    output_path: str,
) -> object | None:
    """返回已选择 output path 的字段值。

    Args:
        selected_values: 已解析的输出路径值。
        output_path: 目标输出路径。

    Returns:
        字段值；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    candidate = selected_values.get(output_path)
    if candidate is None:
        return None
    return candidate.value


def _return_attribution_emitted_output_paths(
    value: dict[str, object],
    selected_values: dict[str, _ReturnAttributionValueCandidate],
) -> tuple[str, ...]:
    """返回实际进入 public value 的 source output paths。

    Args:
        value: 已构造的 return_attribution value。
        selected_values: 已解析的输出路径值。

    Returns:
        需要进入 family anchors 的输出路径元组。

    Raises:
        无显式抛出。
    """

    emitted: list[str] = []
    if "nav_benchmark_performance" in value:
        emitted.extend(
            (
                "nav_benchmark_performance.nav_growth_rate",
                "nav_benchmark_performance.benchmark_return_rate",
            )
        )
    if "fee_schedule" in value:
        emitted.extend(
            output_path
            for output_path in (
                "fee_schedule.management_fee",
                "fee_schedule.custody_fee",
            )
            if output_path in selected_values
        )
    if "tracking_error" in value and "tracking_error" in selected_values:
        emitted.append("tracking_error")
    return tuple(emitted)


def _return_attribution_source_truth_gaps(
    value: dict[str, object],
    ambiguous_paths: set[str],
) -> tuple[FundExtractionGap, ...]:
    """构造 return_attribution.v1 source-truth 字段族本地 gaps。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 发生 duplicate ambiguity 的输出路径集合。

    Returns:
        missing/partial/ambiguity gaps。

    Raises:
        无显式抛出。
    """

    gaps: list[FundExtractionGap] = []
    for output_path in sorted(ambiguous_paths):
        gaps.append(
            FundExtractionGap(
                gap_code="ambiguous_table_or_locator",
                message=f"{output_path} 存在多个冲突的稳定 FDD locator 值",
                field_family_id="return_attribution.v1",
                source_field_path=output_path,
                source_boundary="ambiguous_locator",
                required=True,
            )
        )
    missing_top_level = tuple(
        top_level
        for top_level in _RETURN_ATTRIBUTION_REQUIRED_TOP_LEVEL
        if top_level not in value
    )
    if not value:
        gaps.append(
            FundExtractionGap(
                gap_code="field_family_missing",
                message="return_attribution.v1 未形成 Slice 2 允许的 source-truth 字段值",
                field_family_id="return_attribution.v1",
                source_field_path=None,
                source_boundary="annual_report",
                required=True,
            )
        )
    elif missing_top_level:
        gaps.extend(
            FundExtractionGap(
                gap_code="field_family_partial",
                message=f"return_attribution.v1 缺少 required top-level value: {top_level}",
                field_family_id="return_attribution.v1",
                source_field_path=top_level,
                source_boundary="annual_report",
                required=True,
            )
            for top_level in missing_top_level
        )
    return tuple(gaps)


def _return_attribution_status(value: dict[str, object]) -> str:
    """按 Slice 2 top-level 完整度派生字段族状态。

    Args:
        value: 已构造的字段族 value。

    Returns:
        `accepted`、`partial` 或 `missing`。

    Raises:
        无显式抛出。
    """

    if all(top_level in value for top_level in _RETURN_ATTRIBUTION_REQUIRED_TOP_LEVEL):
        return "accepted"
    if value:
        return "partial"
    return "missing"


def _select_product_essence_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _ProductEssenceValueCandidate], set[str]]:
    """按 Slice B 优先级选择 product_essence 输出路径值。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        `(selected_values, ambiguous_paths)`；歧义路径不会进入 selected_values。

    Raises:
        无显式抛出。
    """

    selected_values: dict[str, _ProductEssenceValueCandidate] = {}
    ambiguous_paths: set[str] = set()
    table_candidates = _collect_product_essence_table_candidates(intermediate, context)
    paragraph_candidates = _collect_product_essence_paragraph_candidates(intermediate, context)
    risk_values, risk_ambiguous_paths = _select_risk_characteristic_value(
        intermediate, context
    )
    ambiguous_paths.update(risk_ambiguous_paths)
    for output_path in _PRODUCT_ESSENCE_LABELS:
        if output_path == _RISK_CHARACTERISTIC_OUTPUT_PATH:
            risk_candidate = risk_values.get(output_path)
            if risk_candidate is not None:
                selected_values[output_path] = _ProductEssenceValueCandidate(
                    output_path=risk_candidate.output_path,
                    value=risk_candidate.value,
                    anchor=risk_candidate.anchor,
                    source_field_path=risk_candidate.source_field_path,
                )
            continue
        candidates = table_candidates.get(output_path, ())
        if not candidates and output_path in _PRODUCT_ESSENCE_PARAGRAPH_OUTPUT_PATHS:
            candidates = paragraph_candidates.get(output_path, ())
        selected = _resolve_product_essence_candidate(
            output_path, candidates, ambiguous_paths, context
        )
        if selected is not None:
            selected_values[output_path] = selected
    if "basic_identity.fund_code" in ambiguous_paths:
        selected_values.pop("basic_identity.fund_code", None)
    return selected_values, ambiguous_paths


def _select_risk_characteristic_value(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _RiskCharacteristicValueCandidate], set[str]]:
    """选择风险收益特征文本字段值，供模板第 1/6 章 direct route 复用。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        `(selected_values, ambiguous_paths)`；仅包含 risk_characteristic_text 路径。

    Raises:
        无显式抛出。
    """

    selected_values: dict[str, _RiskCharacteristicValueCandidate] = {}
    ambiguous_paths: set[str] = set()
    table_candidates = _collect_risk_characteristic_table_candidates(intermediate, context)
    paragraph_candidates = _collect_risk_characteristic_paragraph_candidates(
        intermediate, context
    )
    candidates = table_candidates.get(_RISK_CHARACTERISTIC_OUTPUT_PATH, ())
    if not candidates:
        candidates = paragraph_candidates.get(_RISK_CHARACTERISTIC_OUTPUT_PATH, ())
    selected = _resolve_risk_characteristic_candidate(candidates, ambiguous_paths)
    if selected is not None:
        selected_values[_RISK_CHARACTERISTIC_OUTPUT_PATH] = selected
    return selected_values, ambiguous_paths


def _collect_risk_characteristic_table_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> dict[str, tuple[_RiskCharacteristicValueCandidate, ...]]:
    """收集稳定 table/cell 风险收益特征文本候选。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        仅包含 `risk_characteristic_text.risk_characteristic_text` 的候选映射。

    Raises:
        无显式抛出。
    """

    candidates: dict[str, list[_RiskCharacteristicValueCandidate]] = {}
    labels = _PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            if not (
                _path_contains_any_label(cell.row_label_path, labels)
                or _path_contains_any_label(cell.column_header_path, labels)
            ):
                continue
            value = _risk_characteristic_cell_value(cell)
            if not _is_risk_characteristic_value_allowed(value):
                continue
            anchor = _risk_characteristic_cell_anchor(table, cell, context)
            source_path = f"table_blocks[{table_index}].cells[{cell_index}]"
            candidates.setdefault(_RISK_CHARACTERISTIC_OUTPUT_PATH, []).append(
                _RiskCharacteristicValueCandidate(
                    output_path=_RISK_CHARACTERISTIC_OUTPUT_PATH,
                    value=value,
                    anchor=anchor,
                    source_field_path=source_path,
                )
            )
    return {key: tuple(value) for key, value in candidates.items()}


def _collect_risk_characteristic_paragraph_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> dict[str, tuple[_RiskCharacteristicValueCandidate, ...]]:
    """收集稳定 paragraph 风险收益特征文本候选。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        仅包含 `risk_characteristic_text.risk_characteristic_text` 的候选映射。

    Raises:
        无显式抛出。
    """

    candidates: dict[str, list[_RiskCharacteristicValueCandidate]] = {}
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        candidate = _risk_characteristic_paragraph_candidate(
            paragraph_index, paragraph, context
        )
        if candidate is not None:
            candidates.setdefault(_RISK_CHARACTERISTIC_OUTPUT_PATH, []).append(candidate)
    return {key: tuple(value) for key, value in candidates.items()}


def _risk_characteristic_paragraph_candidate(
    paragraph_index: int,
    paragraph: FundDisclosureParagraphBlockLike,
    context: FundProcessorDispatchKey,
) -> _RiskCharacteristicValueCandidate | None:
    """从单个 paragraph 尝试构造风险收益特征文本候选。

    Args:
        paragraph_index: paragraph tuple 索引。
        paragraph: FDD paragraph block。
        context: Processor dispatch 身份。

    Returns:
        命中时返回候选；未命中或值为空时返回 None。

    Raises:
        无显式抛出。
    """

    text = paragraph.text_normalized.strip() if paragraph.text_normalized else ""
    if not text:
        text = paragraph.text_raw.strip()
    if not text:
        return None
    labels = _PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]
    value = _extract_product_essence_labeled_paragraph_value(text, labels)
    if value is None and _path_contains_any_label(paragraph.heading_path, labels):
        value = text
    if value is None or not _is_risk_characteristic_value_allowed(value):
        return None
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=paragraph.section_id,
        page_number=None,
        table_id=None,
        row_locator=f"field={_RISK_CHARACTERISTIC_OUTPUT_PATH}; block_id={paragraph.block_id}",
        note=_truncate(value),
    )
    return _RiskCharacteristicValueCandidate(
        output_path=_RISK_CHARACTERISTIC_OUTPUT_PATH,
        value=value,
        anchor=anchor,
        source_field_path=f"paragraph_blocks[{paragraph_index}]",
    )


def _risk_characteristic_cell_value(cell: FundDisclosureCellLike) -> str:
    """返回风险收益特征 cell 的规范化取值。

    Args:
        cell: FDD table cell。

    Returns:
        `cell_text_normalized` 非空时优先，否则回退 `cell_text`。

    Raises:
        无显式抛出。
    """

    value = cell.cell_text_normalized.strip() if cell.cell_text_normalized else ""
    if value:
        return value
    return cell.cell_text.strip()


def _is_risk_characteristic_value_allowed(value: str) -> bool:
    """判断风险收益特征候选值是否可进入 source-truth 选择。

    Args:
        value: 候选值。

    Returns:
        非空、非 label 本身、非泛化表头时返回 True。

    Raises:
        无显式抛出。
    """

    if not value:
        return False
    normalized_value = _normalize_match_text(value)
    labels = tuple(
        _normalize_match_text(label)
        for label in _PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]
    )
    generic_texts = tuple(
        _normalize_match_text(text) for text in _PRODUCT_ESSENCE_GENERIC_CELL_TEXTS
    )
    return normalized_value not in labels and normalized_value not in generic_texts


def _risk_characteristic_cell_anchor(
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
    context: FundProcessorDispatchKey,
) -> EvidenceAnchor:
    """构造风险收益特征 table/cell source-truth EvidenceAnchor。

    Args:
        table: parent table block。
        cell: FDD table cell。
        context: Processor dispatch 身份。

    Returns:
        source_kind 固定为 annual_report 的公共锚点。

    Raises:
        无显式抛出。
    """

    table_id = cell.table_id or table.table_id
    row_locator = (
        f"field={_RISK_CHARACTERISTIC_OUTPUT_PATH}; table_id={table_id}; "
        f"row={cell.row_index}; column={cell.column_index}; cell_id={cell.cell_id}"
    )
    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=cell.section_anchor or table.section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=_truncate(_risk_characteristic_cell_value(cell)),
    )


def _resolve_risk_characteristic_candidate(
    candidates: tuple[_RiskCharacteristicValueCandidate, ...],
    ambiguous_paths: set[str],
) -> _RiskCharacteristicValueCandidate | None:
    """按重复/歧义规则解析风险收益特征文本候选。

    Args:
        candidates: 同一路径候选。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        唯一可采信候选；无候选或歧义时返回 None。

    Raises:
        无显式抛出。
    """

    if not candidates:
        return None
    normalized_values = {_normalize_match_text(candidate.value) for candidate in candidates}
    if len(normalized_values) > 1:
        ambiguous_paths.add(_RISK_CHARACTERISTIC_OUTPUT_PATH)
        return None
    return candidates[0]


def _collect_product_essence_table_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> dict[str, tuple[_ProductEssenceValueCandidate, ...]]:
    """收集稳定 table/cell 字段候选，不做 sibling lookup。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        output path 到 table/cell 候选元组的映射。

    Raises:
        无显式抛出。
    """

    candidates: dict[str, list[_ProductEssenceValueCandidate]] = {}
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            output_path = _match_product_essence_cell_output_path(cell)
            if output_path is None:
                continue
            value = _product_essence_cell_value(cell)
            if not _is_product_essence_cell_value_allowed(value, output_path):
                continue
            anchor = _product_essence_cell_anchor(output_path, table, cell, context)
            source_path = f"table_blocks[{table_index}].cells[{cell_index}]"
            candidates.setdefault(output_path, []).append(
                _ProductEssenceValueCandidate(
                    output_path=output_path,
                    value=value,
                    anchor=anchor,
                    source_field_path=source_path,
                )
            )
    return {key: tuple(value) for key, value in candidates.items()}


def _match_product_essence_cell_output_path(cell: FundDisclosureCellLike) -> str | None:
    """按 row_label_path 优先、column_header_path 次之匹配 output path。

    Args:
        cell: FDD table cell。

    Returns:
        命中的 output path；未命中时返回 None。

    Raises:
        无显式抛出。
    """

    for output_path, labels in _PRODUCT_ESSENCE_LABELS.items():
        if output_path == _RISK_CHARACTERISTIC_OUTPUT_PATH:
            continue
        if _path_contains_any_label(cell.row_label_path, labels):
            return output_path
    for output_path, labels in _PRODUCT_ESSENCE_LABELS.items():
        if output_path == _RISK_CHARACTERISTIC_OUTPUT_PATH:
            continue
        if _path_contains_any_label(cell.column_header_path, labels):
            return output_path
    return None


def _product_essence_cell_value(cell: FundDisclosureCellLike) -> str:
    """返回 cell 的规范化取值。

    Args:
        cell: FDD table cell。

    Returns:
        `cell_text_normalized` 非空时优先，否则回退 `cell_text`。

    Raises:
        无显式抛出。
    """

    value = cell.cell_text_normalized.strip() if cell.cell_text_normalized else ""
    if value:
        return value
    return cell.cell_text.strip()


def _is_product_essence_cell_value_allowed(value: str, output_path: str) -> bool:
    """判断 table/cell value 是否可作为 Slice B 字段值。

    Args:
        value: cell 值。
        output_path: 目标输出路径。

    Returns:
        非空、非 label 本身、非泛化表头时返回 True。

    Raises:
        无显式抛出。
    """

    if not value:
        return False
    normalized_value = _normalize_match_text(value)
    labels = tuple(_normalize_match_text(label) for label in _PRODUCT_ESSENCE_LABELS[output_path])
    generic_texts = tuple(
        _normalize_match_text(text) for text in _PRODUCT_ESSENCE_GENERIC_CELL_TEXTS
    )
    return normalized_value not in labels and normalized_value not in generic_texts


def _product_essence_cell_anchor(
    output_path: str,
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
    context: FundProcessorDispatchKey,
) -> EvidenceAnchor:
    """构造 table/cell source-truth EvidenceAnchor。

    Args:
        output_path: 目标输出路径。
        table: parent table block。
        cell: FDD table cell。
        context: Processor dispatch 身份。

    Returns:
        source_kind 固定为 annual_report 的公共锚点。

    Raises:
        无显式抛出。
    """

    table_id = cell.table_id or table.table_id
    row_locator = (
        f"field={output_path}; table_id={table_id}; "
        f"row={cell.row_index}; column={cell.column_index}; cell_id={cell.cell_id}"
    )
    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=cell.section_anchor or table.section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=_truncate(_product_essence_cell_value(cell)),
    )


def _collect_product_essence_paragraph_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> dict[str, tuple[_ProductEssenceValueCandidate, ...]]:
    """收集 Slice B 允许 fallback 的 paragraph 字段候选。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        output path 到 paragraph 候选元组的映射。

    Raises:
        无显式抛出。
    """

    candidates: dict[str, list[_ProductEssenceValueCandidate]] = {}
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        for output_path in _PRODUCT_ESSENCE_PARAGRAPH_OUTPUT_PATHS:
            if output_path == _RISK_CHARACTERISTIC_OUTPUT_PATH:
                continue
            candidate = _product_essence_paragraph_candidate(
                output_path, paragraph_index, paragraph, context
            )
            if candidate is not None:
                candidates.setdefault(output_path, []).append(candidate)
    return {key: tuple(value) for key, value in candidates.items()}


def _product_essence_paragraph_candidate(
    output_path: str,
    paragraph_index: int,
    paragraph: FundDisclosureParagraphBlockLike,
    context: FundProcessorDispatchKey,
) -> _ProductEssenceValueCandidate | None:
    """从单个 paragraph 尝试构造字段值候选。

    Args:
        output_path: 目标输出路径。
        paragraph_index: paragraph tuple 索引。
        paragraph: FDD paragraph block。
        context: Processor dispatch 身份。

    Returns:
        命中时返回候选；未命中或值为空时返回 None。

    Raises:
        无显式抛出。
    """

    text = paragraph.text_normalized.strip() if paragraph.text_normalized else ""
    if not text:
        text = paragraph.text_raw.strip()
    if not text:
        return None
    labels = _PRODUCT_ESSENCE_LABELS[output_path]
    value = _extract_product_essence_labeled_paragraph_value(text, labels)
    if value is None and _path_contains_any_label(paragraph.heading_path, labels):
        value = text
    if value is None or not _is_product_essence_paragraph_value_allowed(value, labels):
        return None
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=paragraph.section_id,
        page_number=None,
        table_id=None,
        row_locator=f"field={output_path}; block_id={paragraph.block_id}",
        note=_truncate(value),
    )
    return _ProductEssenceValueCandidate(
        output_path=output_path,
        value=value,
        anchor=anchor,
        source_field_path=f"paragraph_blocks[{paragraph_index}]",
    )


def _extract_product_essence_labeled_paragraph_value(
    text: str,
    labels: tuple[str, ...],
) -> str | None:
    """从 `label:` / `label：` / `label ` 段落中提取 label 后文本。

    Args:
        text: paragraph 文本。
        labels: 允许的字段 label。

    Returns:
        label 后非空文本；未命中时返回 None。

    Raises:
        无显式抛出。
    """

    for label in labels:
        for separator in (":", "：", " "):
            prefix = f"{label}{separator}"
            if text.startswith(prefix):
                value = text[len(prefix) :].strip()
                return value or None
    return None


def _is_product_essence_paragraph_value_allowed(value: str, labels: tuple[str, ...]) -> bool:
    """判断 paragraph fallback 值是否非空且不只是 label 本身。

    Args:
        value: paragraph 候选值。
        labels: 目标输出路径 labels。

    Returns:
        可作为字段值时返回 True。

    Raises:
        无显式抛出。
    """

    if not value:
        return False
    normalized_value = _normalize_match_text(value)
    return normalized_value not in tuple(_normalize_match_text(label) for label in labels)


def _resolve_product_essence_candidate(
    output_path: str,
    candidates: tuple[_ProductEssenceValueCandidate, ...],
    ambiguous_paths: set[str],
    context: FundProcessorDispatchKey,
) -> _ProductEssenceValueCandidate | None:
    """按重复/歧义规则解析同一路径候选。

    Args:
        output_path: 目标输出路径。
        candidates: 同一路径候选。
        ambiguous_paths: 待追加的歧义路径集合。
        context: Processor dispatch 身份。

    Returns:
        唯一可采信候选；无候选或歧义时返回 None。

    Raises:
        无显式抛出。
    """

    if not candidates:
        return None
    normalized_values = {_normalize_match_text(candidate.value) for candidate in candidates}
    if output_path == "basic_identity.fund_code":
        if normalized_values != {_normalize_match_text(context.fund_code)}:
            ambiguous_paths.add(output_path)
            return None
    if len(normalized_values) > 1:
        ambiguous_paths.add(output_path)
        return None
    return candidates[0]


def _build_product_essence_value(
    selected_values: dict[str, _ProductEssenceValueCandidate],
    context: FundProcessorDispatchKey,
) -> dict[str, object]:
    """按 Slice B exact shape 构造 `product_essence.v1.value`。

    Args:
        selected_values: 已解析的输出路径值。
        context: Processor dispatch 身份。

    Returns:
        顶层只包含 basic_identity、product_profile、benchmark、risk_characteristic_text。

    Raises:
        无显式抛出。
    """

    value: dict[str, object] = {}
    basic_identity = _build_product_essence_basic_identity(selected_values, context)
    if basic_identity is not None:
        value["basic_identity"] = basic_identity
    product_profile = _build_product_essence_product_profile(selected_values)
    if product_profile is not None:
        value["product_profile"] = product_profile
    benchmark_text = _selected_product_essence_value(selected_values, "benchmark.benchmark_text")
    if benchmark_text is not None:
        value["benchmark"] = {"benchmark_text": benchmark_text}
    risk_text = _selected_product_essence_value(
        selected_values, "risk_characteristic_text.risk_characteristic_text"
    )
    if risk_text is not None:
        risk_anchor = selected_values["risk_characteristic_text.risk_characteristic_text"].anchor
        value["risk_characteristic_text"] = _build_risk_characteristic_text_value(
            risk_text, risk_anchor, context
        )
    return value


def _build_product_essence_basic_identity(
    selected_values: dict[str, _ProductEssenceValueCandidate],
    context: FundProcessorDispatchKey,
) -> dict[str, object] | None:
    """构造 basic_identity，要求 fund_name 和匹配 dispatch 的 fund_code 同时存在。

    Args:
        selected_values: 已解析的输出路径值。
        context: Processor dispatch 身份。

    Returns:
        basic_identity 字典；必要字段缺失时返回 None。

    Raises:
        无显式抛出。
    """

    fund_name = _selected_product_essence_value(selected_values, "basic_identity.fund_name")
    fund_code = _selected_product_essence_value(selected_values, "basic_identity.fund_code")
    if fund_name is None or fund_code != context.fund_code:
        return None
    return {
        "fund_name": fund_name,
        "fund_code": fund_code,
        "fund_category": _selected_product_essence_value(
            selected_values, "basic_identity.fund_category"
        ),
        "fund_scale": _selected_product_essence_value(
            selected_values, "basic_identity.fund_scale"
        ),
        "fund_manager": _selected_product_essence_value(
            selected_values, "basic_identity.fund_manager"
        ),
        "management_company": _selected_product_essence_value(
            selected_values, "basic_identity.management_company"
        ),
        "custodian": _selected_product_essence_value(selected_values, "basic_identity.custodian"),
        "inception_date": _selected_product_essence_value(
            selected_values, "basic_identity.inception_date"
        ),
        "classified_fund_type": context.fund_type,
        "classification_basis": ("dispatch_key.fund_type=active_fund",),
    }


def _build_product_essence_product_profile(
    selected_values: dict[str, _ProductEssenceValueCandidate],
) -> dict[str, object] | None:
    """构造 product_profile，禁止从投资目标推导 style_positioning。

    Args:
        selected_values: 已解析的输出路径值。

    Returns:
        product_profile 字典；无 objective/scope/strategy 时返回 None。

    Raises:
        无显式抛出。
    """

    investment_objective = _selected_product_essence_value(
        selected_values, "product_profile.investment_objective"
    )
    investment_scope = _selected_product_essence_value(
        selected_values, "product_profile.investment_scope"
    )
    investment_strategy = _selected_product_essence_value(
        selected_values, "product_profile.investment_strategy"
    )
    if not any((investment_objective, investment_scope, investment_strategy)):
        return None
    return {
        "investment_objective": investment_objective,
        "style_positioning": _selected_product_essence_value(
            selected_values, "product_profile.style_positioning"
        ),
        "investment_scope": investment_scope,
        "investment_strategy": investment_strategy,
    }


def _selected_product_essence_value(
    selected_values: dict[str, _ProductEssenceValueCandidate],
    output_path: str,
) -> str | None:
    """返回已选择 output path 的字段值。

    Args:
        selected_values: 已解析的输出路径值。
        output_path: 目标输出路径。

    Returns:
        字段值；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    candidate = selected_values.get(output_path)
    if candidate is None:
        return None
    return candidate.value


def _risk_characteristic_anchor_ref(anchor: EvidenceAnchor) -> dict[str, object]:
    """构造 risk_characteristic_text.value.source_anchors 条目。

    Args:
        anchor: 字段公共锚点。

    Returns:
        只包含 Slice B 允许键的 anchor ref。

    Raises:
        无显式抛出。
    """

    return {
        "section_id": anchor.section_id,
        "page_number": None,
        "table_id": anchor.table_id,
        "row_locator": anchor.row_locator,
    }


def _build_risk_characteristic_text_value(
    risk_text: str,
    risk_anchor: EvidenceAnchor,
    context: FundProcessorDispatchKey,
) -> dict[str, object]:
    """构造 risk_characteristic_text.v1 公共值，供模板第 1/6 章复用。

    Args:
        risk_text: 直接披露的风险收益特征文本。
        risk_anchor: 文本对应公共锚点。
        context: Processor dispatch 身份。

    Returns:
        既有 `risk_characteristic_text.v1` 字典形状。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": "risk_characteristic_text.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "risk_characteristic_text": risk_text,
        "source_anchors": [_risk_characteristic_anchor_ref(risk_anchor)],
    }


def _product_essence_emitted_output_paths(
    value: dict[str, object],
    selected_values: dict[str, _ProductEssenceValueCandidate],
) -> tuple[str, ...]:
    """返回实际进入 public value 的 source output paths。

    Args:
        value: 已构造的 product_essence value。
        selected_values: 已解析的输出路径值。

    Returns:
        需要进入 family anchors 的输出路径元组。

    Raises:
        无显式抛出。
    """

    emitted: list[str] = []
    if "basic_identity" in value:
        emitted.extend(
            output_path
            for output_path in selected_values
            if output_path.startswith("basic_identity.")
        )
    if "product_profile" in value:
        emitted.extend(
            output_path
            for output_path in selected_values
            if output_path.startswith("product_profile.")
        )
    if "benchmark" in value and "benchmark.benchmark_text" in selected_values:
        emitted.append("benchmark.benchmark_text")
    risk_path = "risk_characteristic_text.risk_characteristic_text"
    if "risk_characteristic_text" in value and risk_path in selected_values:
        emitted.append(risk_path)
    return tuple(emitted)


def _product_essence_source_truth_gaps(
    value: dict[str, object],
    ambiguous_paths: set[str],
) -> tuple[FundExtractionGap, ...]:
    """构造 product_essence.v1 source-truth 字段族本地 gaps。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 发生 duplicate ambiguity 的输出路径集合。

    Returns:
        missing/partial/ambiguity gaps。

    Raises:
        无显式抛出。
    """

    gaps: list[FundExtractionGap] = []
    for output_path in sorted(ambiguous_paths):
        gaps.append(
            FundExtractionGap(
                gap_code="ambiguous_table_or_locator",
                message=f"{output_path} 存在多个冲突的稳定 FDD locator 值",
                field_family_id="product_essence.v1",
                source_field_path=output_path,
                source_boundary="ambiguous_locator",
                required=output_path.startswith("basic_identity."),
            )
        )
    missing_top_level = tuple(
        top_level for top_level in _PRODUCT_ESSENCE_REQUIRED_TOP_LEVEL if top_level not in value
    )
    if not value:
        gaps.append(
            FundExtractionGap(
                gap_code="field_family_missing",
                message="product_essence.v1 未形成 Slice B 允许的 source-truth 字段值",
                field_family_id="product_essence.v1",
                source_field_path=None,
                source_boundary="annual_report",
                required=True,
            )
        )
    elif missing_top_level:
        gaps.extend(
            FundExtractionGap(
                gap_code="field_family_partial",
                message=f"product_essence.v1 缺少 required top-level value: {top_level}",
                field_family_id="product_essence.v1",
                source_field_path=top_level,
                source_boundary="annual_report",
                required=True,
            )
            for top_level in missing_top_level
        )
    return tuple(gaps)


def _product_essence_status(value: dict[str, object]) -> str:
    """按 Slice B top-level 完整度派生字段族状态。

    Args:
        value: 已构造的字段族 value。

    Returns:
        `accepted`、`partial` 或 `missing`。

    Raises:
        无显式抛出。
    """

    if all(top_level in value for top_level in _PRODUCT_ESSENCE_REQUIRED_TOP_LEVEL):
        return "accepted"
    if value:
        return "partial"
    return "missing"


# ── core_risk role source-truth helpers ────────────────────────────────────


def _select_core_risk_role_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _CoreRiskRoleValueCandidate], set[str]]:
    """从 FDD 正文选择四个 core_risk role 的 source-truth 披露文本。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        ``(selected_values, ambiguous_paths)``；key 为 role key。

    Raises:
        无显式抛出。
    """

    selected_values: dict[str, _CoreRiskRoleValueCandidate] = {}
    ambiguous_paths: set[str] = set()
    for role, strong_tokens, generic_tokens, guard_tokens in _CORE_RISK_MATCH_GROUPS:
        if role == "risk_characteristic":
            continue
        paragraph_candidates = _collect_core_risk_role_paragraph_candidates(
            intermediate, role, strong_tokens, generic_tokens, guard_tokens, context
        )
        cell_candidates = _collect_core_risk_role_cell_candidates(
            intermediate, role, strong_tokens, generic_tokens, guard_tokens, context
        )
        all_candidates = paragraph_candidates + cell_candidates
        resolved = _resolve_core_risk_role_candidate(role, all_candidates, ambiguous_paths)
        if resolved is not None:
            selected_values[role] = resolved
    return selected_values, ambiguous_paths


def _collect_core_risk_role_paragraph_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
    context: FundProcessorDispatchKey,
) -> tuple[_CoreRiskRoleValueCandidate, ...]:
    """收集 core_risk 单个 role 的 paragraph 候选。

    Args:
        intermediate: FDD 正文中间态。
        role: role key。
        strong_tokens: 强匹配 token。
        generic_tokens: 需 guard context 的 token。
        guard_tokens: guard context 允许 token。
        context: Processor dispatch 身份。

    Returns:
        paragraph 候选元组，按 paragraph tuple 索引顺序。

    Raises:
        无显式抛出。
    """

    candidates: list[_CoreRiskRoleValueCandidate] = []
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        text = paragraph.text_normalized.strip() if paragraph.text_normalized else ""
        if not text:
            text = paragraph.text_raw.strip()
        if not text:
            continue
        candidate_texts = (text,)
        guard_context = (
            *_tuple_text(paragraph.heading_path),
            text,
        )
        if not _matches_guarded_core_risk_source(
            candidate_texts, strong_tokens, generic_tokens, guard_context, guard_tokens
        ):
            continue
        if _is_core_risk_role_heading_only(text, strong_tokens, generic_tokens):
            continue
        anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=context.document_year,
            section_id=paragraph.section_id,
            page_number=None,
            table_id=None,
            row_locator=(
                f"field={role}; source=paragraph_blocks[{paragraph_index}]; "
                f"block_id={paragraph.block_id}"
            ),
            note=_truncate(text),
        )
        candidates.append(
            _CoreRiskRoleValueCandidate(
                output_path=role,
                role=role,
                value=text,
                anchor=anchor,
                source_field_path=f"paragraph_blocks[{paragraph_index}]",
            )
        )
    return tuple(candidates)


def _collect_core_risk_role_cell_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
    context: FundProcessorDispatchKey,
) -> tuple[_CoreRiskRoleValueCandidate, ...]:
    """收集 core_risk 单个 role 的 table cell 候选。

    Args:
        intermediate: FDD 正文中间态。
        role: role key。
        strong_tokens: 强匹配 token。
        generic_tokens: 需 guard context 的 token。
        guard_tokens: guard context 允许 token。
        context: Processor dispatch 身份。

    Returns:
        cell 候选元组，按 table 索引和 ``(row_index, column_index)`` 顺序。

    Raises:
        无显式抛出。
    """

    candidates: list[_CoreRiskRoleValueCandidate] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        header_rows = getattr(table, "header_rows", ())
        body_rows = getattr(table, "body_rows", ())
        indexed_cells = sorted(
            enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
        )
        for cell_index, cell in indexed_cells:
            if cell.locator_stability != "stable":
                continue
            if getattr(cell, "is_header_cell", False):
                continue
            if cell.row_index in header_rows:
                continue
            if body_rows and cell.row_index not in body_rows:
                continue
            text = cell.cell_text_normalized.strip() if cell.cell_text_normalized else ""
            if not text:
                text = cell.cell_text.strip()
            if not text:
                continue
            if _is_core_risk_role_placeholder(text):
                continue
            guard_context = _core_risk_cell_guard_context(table, cell)
            normalized = _normalize_match_text(text)
            if _any_ascii_digit(normalized):
                candidate_texts = (text,) + tuple(
                    g for g in (
                        table.heading_text,
                        table.table_caption_or_nearby_heading,
                        *_tuple_text(cell.row_label_path),
                        *_tuple_text(cell.column_header_path),
                    ) if g
                )
            else:
                candidate_texts = (text,)
            if not _matches_guarded_core_risk_source(
                candidate_texts, strong_tokens, generic_tokens, guard_context, guard_tokens
            ):
                continue
            if _is_core_risk_role_heading_only(text, strong_tokens, generic_tokens):
                continue
            anchor = EvidenceAnchor(
                source_kind="annual_report",
                document_year=context.document_year,
                section_id=cell.section_anchor,
                page_number=None,
                table_id=table.table_id,
                row_locator=(
                    f"field={role}; "
                    f"source=table_blocks[{table_index}].cells[{cell_index}]; "
                    f"table_id={table.table_id}; "
                    f"row={cell.row_index}; column={cell.column_index}; "
                    f"cell_id={cell.cell_id}"
                ),
                note=_truncate(text),
            )
            candidates.append(
                _CoreRiskRoleValueCandidate(
                    output_path=role,
                    role=role,
                    value=text,
                    anchor=anchor,
                    source_field_path=f"table_blocks[{table_index}].cells[{cell_index}]",
                )
            )
    return tuple(candidates)


def _is_core_risk_role_placeholder(text: str) -> bool:
    """判断 cell 文本是否为空值占位符。

    Args:
        text: 候选文本。

    Returns:
        占位符时返回 True。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_match_text(text)
    return normalized in {"", "无", "不适用", "-", "—", "--", "未披露", "n/a", "N/A"}


def _is_core_risk_role_heading_only(
    text: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
) -> bool:
    """判断文本是否仅为一个结构性标签/表头，无实质性披露。

    Args:
        text: 候选文本。
        strong_tokens: 强匹配 token。
        generic_tokens: 通用 token。

    Returns:
        仅结构性标签时返回 True。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_match_text(text)
    if not normalized:
        return True
    all_tokens_normalized = {
        _normalize_match_text(t) for t in (*strong_tokens, *generic_tokens)
    }
    if normalized in all_tokens_normalized:
        return True
    if len(normalized) < 15:
        if not _any_ascii_digit(normalized):
            return True
    return False


def _any_ascii_digit(text: str) -> bool:
    """判断文本是否包含 ASCII 数字字符。

    Args:
        text: 规范化后的候选文本。

    Returns:
        含 ``0-9`` 时返回 True。

    Raises:
        无显式抛出。
    """

    return any(ch.isdigit() for ch in text)


def _resolve_core_risk_role_candidate(
    role: str,
    candidates: tuple[_CoreRiskRoleValueCandidate, ...],
    ambiguous_paths: set[str],
) -> _CoreRiskRoleValueCandidate | None:
    """解析单个 role 的候选集。

    Args:
        role: role key。
        candidates: 按 scan order 排列的候选。
        ambiguous_paths: 发生歧义的路径集合（就地修改）。

    Returns:
        唯一解析结果；无候选或冲突时返回 None。

    Raises:
        无显式抛出。
    """

    if not candidates:
        return None
    first_normalized = _normalize_match_text(candidates[0].value)
    if all(_normalize_match_text(c.value) == first_normalized for c in candidates):
        return candidates[0]
    ambiguous_paths.add(role)
    return None


def _build_core_risk_role_disclosure_value(
    candidate: _CoreRiskRoleValueCandidate,
    context: FundProcessorDispatchKey,
) -> dict[str, object]:
    """构造 ``core_risk_role_disclosure.v1`` subvalue。

    Args:
        candidate: 已解析的 role 候选。
        context: Processor dispatch 身份。

    Returns:
        五键 role disclosure subvalue。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": "core_risk_role_disclosure.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "role": candidate.role,
        "risk_disclosure_text": candidate.value,
    }


# ── core_risk public functions ──────────────────────────────────────────────


def _select_core_risk_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _CoreRiskValueCandidate], set[str]]:
    """选择 core_risk.v1 所有五个 required source-truth subvalue。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        ``(selected_values, ambiguous_paths)``。

    Raises:
        无显式抛出。
    """

    risk_values, risk_ambiguous_paths = _select_risk_characteristic_value(
        intermediate, context
    )
    role_values, role_ambiguous_paths = _select_core_risk_role_values(
        intermediate, context
    )
    selected_values: dict[str, _CoreRiskValueCandidate] = {}
    for rv in risk_values.values():
        selected_values[_RISK_CHARACTERISTIC_OUTPUT_PATH] = rv
    for role_key, rv in role_values.items():
        selected_values[role_key] = rv
    ambiguous_paths = risk_ambiguous_paths | role_ambiguous_paths
    return selected_values, ambiguous_paths


def _build_core_risk_value(
    selected_values: dict[str, _CoreRiskValueCandidate],
    context: FundProcessorDispatchKey,
) -> dict[str, object]:
    """构造 core_risk.v1 完整 public value。

    Args:
        selected_values: 已选择的所有 subvalue 候选。
        context: Processor dispatch 身份。

    Returns:
        core_risk.v1 字段族 value；无可发射 subvalue 时返回空字典。

    Raises:
        无显式抛出。
    """

    value: dict[str, object] = {"schema_version": "core_risk.v1"}
    for output_path, candidate in selected_values.items():
        if output_path == _RISK_CHARACTERISTIC_OUTPUT_PATH:
            if isinstance(candidate, _RiskCharacteristicValueCandidate):
                value["risk_characteristic_text"] = _build_risk_characteristic_text_value(
                    candidate.value, candidate.anchor, context
                )
        elif isinstance(candidate, _CoreRiskRoleValueCandidate):
            value[output_path] = _build_core_risk_role_disclosure_value(candidate, context)
    if len(value) == 1:
        return {}
    return value


def _core_risk_emitted_output_paths(
    value: dict[str, object],
    selected_values: dict[str, _CoreRiskValueCandidate],
) -> tuple[str, ...]:
    """返回实际进入 public value 的 core_risk output paths。

    Args:
        value: 已构造的字段族 value。
        selected_values: 已解析的候选值。

    Returns:
        需要进入 family anchors 的输出路径元组，按 required top-level 顺序。

    Raises:
        无显式抛出。
    """

    paths: list[str] = []
    for top_level in _CORE_RISK_REQUIRED_TOP_LEVEL:
        if top_level == "risk_characteristic_text":
            if "risk_characteristic_text" in value and _RISK_CHARACTERISTIC_OUTPUT_PATH in selected_values:
                paths.append(_RISK_CHARACTERISTIC_OUTPUT_PATH)
        else:
            if top_level in value and top_level in selected_values:
                paths.append(top_level)
    return tuple(paths)


def _core_risk_source_truth_gaps(
    value: dict[str, object],
    ambiguous_paths: set[str],
) -> tuple[FundExtractionGap, ...]:
    """构造 core_risk.v1 source-truth 字段族本地 gaps。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 发生 duplicate ambiguity 的输出路径集合。

    Returns:
        missing/partial/ambiguity gaps；不再发射 ``deferred_role``。

    Raises:
        无显式抛出。
    """

    gaps: list[FundExtractionGap] = []
    for output_path in sorted(ambiguous_paths):
        gaps.append(
            FundExtractionGap(
                gap_code="ambiguous_table_or_locator",
                message=f"{output_path} 存在多个冲突的稳定 FDD locator 值",
                field_family_id="core_risk.v1",
                source_field_path=output_path,
                source_boundary="ambiguous_locator",
                required=True,
            )
        )
    if not value:
        if not ambiguous_paths:
            gaps.append(
                FundExtractionGap(
                    gap_code="field_family_missing",
                    message="core_risk.v1 未形成任何 source-truth 字段值",
                    field_family_id="core_risk.v1",
                    source_field_path=None,
                    source_boundary="annual_report",
                    required=True,
                )
            )
        return tuple(gaps)
    emitted_top_level = {k for k in value if k != "schema_version"}
    for top_level in _CORE_RISK_REQUIRED_TOP_LEVEL:
        if top_level not in emitted_top_level and top_level not in ambiguous_paths:
            gaps.append(
                FundExtractionGap(
                    gap_code="field_family_partial",
                    message=f"core_risk.v1 {top_level} source-truth subvalue missing",
                    field_family_id="core_risk.v1",
                    source_field_path=top_level,
                    source_boundary="annual_report",
                    required=True,
                )
            )
    return tuple(gaps)


def _core_risk_status(value: dict[str, object]) -> str:
    """按 required top-level 完整性派生 core_risk 字段族状态。

    Args:
        value: 已构造的字段族 value。

    Returns:
        ``"accepted"`` / ``"partial"`` / ``"missing"``。

    Raises:
        无显式抛出。
    """

    if not value:
        return "missing"
    emitted = {k for k in value if k != "schema_version"}
    if emitted == set(_CORE_RISK_REQUIRED_TOP_LEVEL):
        return "accepted"
    if emitted:
        return "partial"
    return "missing"


def _path_contains_any_label(path: tuple[str, ...], labels: tuple[str, ...]) -> bool:
    """判断路径任一片段是否等于目标 label。

    Args:
        path: row label、column header 或 heading path。
        labels: 允许 label。

    Returns:
        规范化后任一片段等于任一 label 时返回 True。

    Raises:
        无显式抛出。
    """

    normalized_labels = {_normalize_match_text(label) for label in labels}
    return any(_normalize_match_text(part) in normalized_labels for part in path)


def _derive_contract_status(
    field_families: tuple[FundFieldFamilyResult, ...],
) -> FundProcessorContractStatus:
    """从字段族状态派生 processor contract status。

    Args:
        field_families: 六个字段族结果。

    Returns:
        全 accepted 为 satisfied；任一 accepted/partial 为 partial；否则 missing。

    Raises:
        无显式抛出。
    """

    statuses = {family.status for family in field_families}
    if statuses == {"accepted"}:
        return "satisfied"
    if "accepted" in statuses or "partial" in statuses:
        return "partial"
    return "missing"


def _dedupe_anchors(anchors: Iterable[EvidenceAnchor]) -> tuple[EvidenceAnchor, ...]:
    """按 dataclass 值去重公共 EvidenceAnchor。

    Args:
        anchors: 可迭代公共锚点。

    Returns:
        去重且保持首次出现顺序的锚点元组。

    Raises:
        无显式抛出。
    """

    deduped: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for anchor in anchors:
        if anchor in seen:
            continue
        seen.add(anchor)
        deduped.append(anchor)
    return tuple(deduped)


def _content_intermediate_or_none(
    intermediate: FundDisclosureDocumentIntermediate,
) -> FundDisclosureDocumentContentIntermediate | None:
    """按正文结构识别 FundDisclosureDocument content intermediate。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        具备 section/paragraph/table 正文结构时返回 content 协议视图，否则返回 None。

    Raises:
        无显式抛出。
    """

    if not all(
        hasattr(intermediate, attribute_name)
        for attribute_name in ("sections", "paragraph_blocks", "table_blocks")
    ):
        return None
    return cast(FundDisclosureDocumentContentIntermediate, intermediate)


def _select_product_essence_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择产品本质字段族的 candidate-only locator evidence。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-B mapping table 排序和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, tokens in _PRODUCT_ESSENCE_MATCH_GROUPS:
        _extend_product_essence_section_records(
            records, seen_paths, content_intermediate, role, tokens
        )
        _extend_product_essence_paragraph_records(
            records, seen_paths, content_intermediate, role, tokens
        )
        _extend_product_essence_table_records(records, seen_paths, content_intermediate, role, tokens)
        if len(records) >= _PRODUCT_ESSENCE_CANDIDATE_LIMIT:
            break
    return tuple(records[:_PRODUCT_ESSENCE_CANDIDATE_LIMIT])


def _extend_product_essence_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="product_essence.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_product_essence_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="product_essence.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_product_essence_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_any_token(texts, tokens):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="product_essence.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_product_essence_cell_records(records, seen_paths, table_index, table, role, tokens)


def _extend_product_essence_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="product_essence.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _select_return_attribution_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择收益归因字段族的 candidate-only locator evidence。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-C mapping table 排序、去重和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, tokens in _RETURN_ATTRIBUTION_MATCH_GROUPS:
        _extend_return_attribution_section_records(
            records, seen_paths, content_intermediate, role, tokens
        )
        _extend_return_attribution_paragraph_records(
            records, seen_paths, content_intermediate, role, tokens
        )
        _extend_return_attribution_table_records(
            records, seen_paths, content_intermediate, role, tokens
        )
    return tuple(records[:_RETURN_ATTRIBUTION_CANDIDATE_LIMIT])


def _extend_return_attribution_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 return_attribution section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="return_attribution.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_return_attribution_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 return_attribution paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="return_attribution.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_return_attribution_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 return_attribution table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_any_token(texts, tokens):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="return_attribution.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_return_attribution_cell_records(records, seen_paths, table_index, table, role, tokens)


def _extend_return_attribution_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 return_attribution table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="return_attribution.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _select_manager_profile_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择基金经理画像字段族的 candidate-only locator evidence（见模板第3章）。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-D mapping table 排序、去重和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, strong_tokens, generic_tokens, guard_tokens in _MANAGER_PROFILE_MATCH_GROUPS:
        _extend_manager_profile_section_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_manager_profile_paragraph_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_manager_profile_table_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        if len(records) >= _MANAGER_PROFILE_CANDIDATE_LIMIT:
            break
    return tuple(records[:_MANAGER_PROFILE_CANDIDATE_LIMIT])


def _extend_manager_profile_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 manager_profile section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 guard context 的匹配 token。
        guard_tokens: generic token 的 source-level guard token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_guarded_manager_profile_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="manager_profile.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_manager_profile_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 manager_profile paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 guard context 的匹配 token。
        guard_tokens: generic token 的 source-level guard token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        guard_context = _manager_profile_paragraph_guard_context(role, paragraph)
        if path in seen_paths or not _matches_guarded_manager_profile_source(
            texts, strong_tokens, generic_tokens, guard_context, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="manager_profile.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_manager_profile_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 manager_profile table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 guard context 的匹配 token。
        guard_tokens: generic token 的 source-level guard token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_guarded_manager_profile_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="manager_profile.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_manager_profile_cell_records(
            records, seen_paths, table_index, table, role, strong_tokens, generic_tokens, guard_tokens
        )


def _extend_manager_profile_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 manager_profile table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 guard context 的匹配 token。
        guard_tokens: generic token 的 source-level guard token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        guard_context = _manager_profile_cell_guard_context(role, table, cell)
        if path in seen_paths or not _matches_guarded_manager_profile_source(
            texts, strong_tokens, generic_tokens, guard_context, guard_tokens
        ):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="manager_profile.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _matches_guarded_manager_profile_source(
    texts: tuple[str | None, ...],
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_context: tuple[str | None, ...],
    guard_tokens: tuple[str, ...],
) -> bool:
    """按 S6-D source-level guard 规则判断 manager_profile source 是否可追加。

    Args:
        texts: 当前 source 的候选匹配文本。
        strong_tokens: 无需额外 context 的 token。
        generic_tokens: 需要 source-level guard 的 token。
        guard_context: 当前 source 允许用于 guard 的上下文文本。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        strong token 命中时返回 True；generic token 命中且 guard context 命中时返回 True。

    Raises:
        无显式抛出。
    """

    if _matches_any_token(texts, strong_tokens):
        return True
    if not generic_tokens or not _matches_any_token(texts, generic_tokens):
        return False
    return _matches_any_token(guard_context, guard_tokens)


def _manager_profile_paragraph_guard_context(role: str, paragraph: object) -> tuple[str | None, ...]:
    """返回 paragraph 级 generic guard context。

    Args:
        role: 当前 manager_profile evidence role。
        paragraph: paragraph block 协议对象。

    Returns:
        只含 plan/controller 允许字段的 guard context。

    Raises:
        无显式抛出。
    """

    heading_path = _tuple_text(paragraph.heading_path)
    if role == "manager_alignment":
        return (paragraph.text_normalized, paragraph.text_raw, *heading_path)
    return (*heading_path,)


def _manager_profile_cell_guard_context(
    role: str,
    table: FundDisclosureTableBlockLike,
    cell: object,
) -> tuple[str | None, ...]:
    """返回 cell 级 generic guard context。

    Args:
        role: 当前 manager_profile evidence role。
        table: parent table block 协议对象。
        cell: table cell 协议对象。

    Returns:
        只含 plan/controller 允许字段的 guard context。

    Raises:
        无显式抛出。
    """

    table_context = (
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
    )
    if role == "manager_alignment":
        return (
            *table_context,
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
    return (*table_context, *_tuple_text(cell.heading_path))


def _extract_investor_experience_source_truth(
    intermediate: FundDisclosureDocumentContentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    context: FundProcessorDispatchKey,
) -> FundFieldFamilyResult:
    """从 proof-positive FDD 正文抽取模板第 4 章投资者获得感字段族。

    Args:
        intermediate: 已通过 source-truth admission proof 的正文中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。

    Returns:
        `investor_experience.v1` 字段族；只包含既有 public/bundle 三个 top-level key。

    Raises:
        无显式抛出。
    """

    selected_values, ambiguous_paths = _select_investor_experience_values(
        intermediate, context
    )
    value = _build_investor_experience_value(selected_values)
    gaps = _investor_experience_source_truth_gaps(value, ambiguous_paths)
    status = _investor_experience_status(value, ambiguous_paths)
    anchors = _dedupe_anchors(
        selected_values[output_path].anchor
        for output_path in _investor_experience_emitted_output_paths(value, selected_values)
    )
    return FundFieldFamilyResult(
        field_family_id="investor_experience.v1",
        chapter_ids=_CHAPTER_IDS["investor_experience.v1"],
        value=value,
        status=status,
        extraction_mode="missing" if status == "missing" else "direct",
        anchors=anchors,
        gaps=gaps,
        source_provenance=source_provenance,
        candidate_evidence=(),
    )


def _select_investor_experience_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _InvestorExperienceValueCandidate], set[str]]:
    """按 proof-positive fail-closed 规则选择投资者获得感字段值。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        `(selected_values, ambiguous_paths)`；歧义路径不会进入 selected_values。

    Raises:
        无显式抛出。
    """

    ambiguous_paths: set[str] = set()
    selected_values: dict[str, _InvestorExperienceValueCandidate] = {}
    for candidate in (
        _select_investor_experience_return(intermediate, context, ambiguous_paths),
        _select_investor_experience_holder_structure(intermediate, context, ambiguous_paths),
        _select_investor_experience_share_change(intermediate, context, ambiguous_paths),
    ):
        if candidate is not None:
            selected_values[candidate.output_path] = candidate
    return selected_values, ambiguous_paths


def _select_investor_experience_return(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _InvestorExperienceValueCandidate | None:
    """选择投资者收益率 public subvalue。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        可采信 investor_return 候选；缺失或冲突时返回 None。

    Raises:
        无显式抛出。
    """

    candidates = (
        *_collect_investor_return_paragraph_candidates(intermediate, context),
        *_collect_investor_return_table_candidates(intermediate, context),
    )
    direct = tuple(candidate for candidate in candidates if _investor_return_status(candidate) == "direct")
    estimated = tuple(
        candidate for candidate in candidates if _investor_return_status(candidate) == "estimated"
    )
    selected = _resolve_investor_experience_candidate(
        "investor_return", direct or estimated, ambiguous_paths
    )
    return selected


def _collect_investor_return_paragraph_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[_InvestorExperienceValueCandidate, ...]:
    """收集 paragraph 投资者收益率候选。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        稳定 paragraph 候选元组。

    Raises:
        无显式抛出。
    """

    candidates: list[_InvestorExperienceValueCandidate] = []
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        text = _first_non_empty((paragraph.text_normalized, paragraph.text_raw)).strip()
        if not text:
            continue
        value = _investor_return_value_from_text(text)
        if value is None:
            continue
        disclosure_status = _investor_return_label_kind(text)
        if disclosure_status is None:
            continue
        anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=context.document_year,
            section_id=paragraph.section_id,
            page_number=None,
            table_id=None,
            row_locator=f"field=investor_return; block_id={paragraph.block_id}",
            note=_truncate(value),
        )
        candidates.append(
            _InvestorExperienceValueCandidate(
                output_path="investor_return",
                value={
                    "investor_return_rate": value,
                    "disclosure_status": disclosure_status,
                    "fallback_status": _investor_return_fallback_status(disclosure_status),
                },
                anchor=anchor,
                source_field_path=f"paragraph_blocks[{paragraph_index}]",
            )
        )
    return tuple(candidates)


def _collect_investor_return_table_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[_InvestorExperienceValueCandidate, ...]:
    """收集 table/cell 投资者收益率候选。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        稳定 table row/cell 候选元组。

    Raises:
        无显式抛出。
    """

    candidates: list[_InvestorExperienceValueCandidate] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable":
            continue
        stable_cells = _stable_indexed_cells(table)
        rows = _cells_by_row(stable_cells)
        for row_index, row_cells in rows.items():
            row_context = _row_text_context(row_cells)
            disclosure_status = _investor_return_label_kind(" ".join(row_context))
            if disclosure_status is None:
                continue
            for cell_index, cell in row_cells:
                value = _percent_value_from_text(_cell_value(cell))
                if value is None:
                    continue
                anchor = _investor_experience_cell_anchor(
                    "investor_return", table, cell, context
                )
                candidates.append(
                    _InvestorExperienceValueCandidate(
                        output_path="investor_return",
                        value={
                            "investor_return_rate": value,
                            "disclosure_status": disclosure_status,
                            "fallback_status": _investor_return_fallback_status(
                                disclosure_status
                            ),
                        },
                        anchor=anchor,
                        source_field_path=f"table_blocks[{table_index}].cells[{cell_index}]",
                    )
                )
                break
            if row_index < 0:
                break
    return tuple(candidates)


def _investor_return_label_kind(text: str) -> str | None:
    """判断文本命中的投资者收益率 label 类型。

    Args:
        text: 候选文本。

    Returns:
        `direct`、`estimated` 或 None。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_match_text(text)
    for label in _INVESTOR_RETURN_ESTIMATED_LABELS:
        if _normalize_match_text(label) in normalized:
            return "estimated"
    for label in _INVESTOR_RETURN_DIRECT_LABELS:
        if _normalize_match_text(label) in normalized:
            return "direct"
    return None


def _investor_return_value_from_text(text: str) -> str | None:
    """从同源 label/value 文本中抽取投资者收益率。

    Args:
        text: paragraph、cell 或 row context 文本。

    Returns:
        显式百分比文本；缺 label、缺值或不可用表述时返回 None。

    Raises:
        无显式抛出。
    """

    label = _first_investor_return_label(text)
    if label is None:
        return None
    label_index = text.find(label)
    value_text = text[label_index + len(label) :] if label_index >= 0 else text
    if _investor_return_has_unavailable_wording(value_text):
        return None
    match = _RETURN_ATTRIBUTION_PERCENT_PATTERN.search(value_text)
    if match is None:
        return None
    return match.group("value") + "%"


def _percent_value_from_text(text: str) -> str | None:
    """从文本中抽取首个百分比值。

    Args:
        text: 候选文本。

    Returns:
        百分比文本；无百分比时返回 None。

    Raises:
        无显式抛出。
    """

    match = _RETURN_ATTRIBUTION_PERCENT_PATTERN.search(text)
    if match is None:
        return None
    return match.group("value") + "%"


def _first_investor_return_label(text: str) -> str | None:
    """返回文本中最先出现的投资者收益率 label。

    Args:
        text: 候选文本。

    Returns:
        label 原文；无命中时返回 None。

    Raises:
        无显式抛出。
    """

    labels = (*_INVESTOR_RETURN_ESTIMATED_LABELS, *_INVESTOR_RETURN_DIRECT_LABELS)
    positions = tuple((text.find(label), label) for label in labels if text.find(label) >= 0)
    if not positions:
        return None
    return min(positions, key=lambda item: item[0])[1]


def _investor_return_has_unavailable_wording(text_after_label: str) -> bool:
    """判断 label 后近邻文本是否表达未披露或不可用。

    Args:
        text_after_label: label 后文本。

    Returns:
        命中不可用语义时返回 True。

    Raises:
        无显式抛出。
    """

    window = _normalize_match_text(text_after_label[:32])
    for token in _INVESTOR_RETURN_UNAVAILABLE_TOKENS:
        normalized = _normalize_match_text(token)
        if normalized == "无":
            if window.startswith("无"):
                return True
            continue
        if normalized in window:
            return True
    return False


def _investor_return_fallback_status(disclosure_status: str) -> str:
    """返回 investor_return 既有 public shape 的 fallback_status。

    Args:
        disclosure_status: `direct` 或 `estimated`。

    Returns:
        public fallback_status 字符串。

    Raises:
        无显式抛出。
    """

    if disclosure_status == "estimated":
        return "estimated_disclosure_in_section"
    return "not_needed"


def _investor_return_status(candidate: _InvestorExperienceValueCandidate) -> str:
    """读取 investor_return 候选的 disclosure_status。

    Args:
        candidate: investor_return 候选。

    Returns:
        disclosure_status 字符串。

    Raises:
        无显式抛出。
    """

    if isinstance(candidate.value, dict):
        return str(candidate.value.get("disclosure_status"))
    return ""


def _select_investor_experience_holder_structure(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _InvestorExperienceValueCandidate | None:
    """选择持有人结构 public subvalue。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        holder_structure 候选；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    side_candidates = {
        "holder_structure.institutional_holder": (
            *_collect_holder_structure_paragraph_candidates(
                "holder_structure.institutional_holder",
                _HOLDER_STRUCTURE_INSTITUTIONAL_LABELS,
                intermediate,
                context,
            ),
            *_collect_holder_structure_table_candidates(
                "holder_structure.institutional_holder",
                _HOLDER_STRUCTURE_INSTITUTIONAL_LABELS,
                intermediate,
                context,
            ),
        ),
        "holder_structure.individual_holder": (
            *_collect_holder_structure_paragraph_candidates(
                "holder_structure.individual_holder",
                _HOLDER_STRUCTURE_INDIVIDUAL_LABELS,
                intermediate,
                context,
            ),
            *_collect_holder_structure_table_candidates(
                "holder_structure.individual_holder",
                _HOLDER_STRUCTURE_INDIVIDUAL_LABELS,
                intermediate,
                context,
            ),
        ),
    }
    institutional = _resolve_investor_experience_candidate(
        "holder_structure.institutional_holder",
        side_candidates["holder_structure.institutional_holder"],
        ambiguous_paths,
    )
    individual = _resolve_investor_experience_candidate(
        "holder_structure.individual_holder",
        side_candidates["holder_structure.individual_holder"],
        ambiguous_paths,
    )
    if institutional is None and individual is None:
        return None
    value = {
        "institutional_holder": institutional.value if institutional is not None else None,
        "individual_holder": individual.value if individual is not None else None,
    }
    anchor = (institutional or individual).anchor
    source_path = (institutional or individual).source_field_path
    return _InvestorExperienceValueCandidate(
        output_path="holder_structure",
        value=value,
        anchor=anchor,
        source_field_path=source_path,
    )


def _collect_holder_structure_paragraph_candidates(
    output_path: str,
    labels: tuple[str, ...],
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[_InvestorExperienceValueCandidate, ...]:
    """收集 paragraph 持有人结构候选。

    Args:
        output_path: holder side 输出路径。
        labels: 允许的 side label。
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        稳定 paragraph 候选元组。

    Raises:
        无显式抛出。
    """

    candidates: list[_InvestorExperienceValueCandidate] = []
    for paragraph_index, paragraph in enumerate(intermediate.paragraph_blocks):
        if paragraph.locator_stability != "stable":
            continue
        text = _first_non_empty((paragraph.text_normalized, paragraph.text_raw)).strip()
        value = _holder_structure_value_from_text(text, labels)
        if value is None:
            continue
        anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=context.document_year,
            section_id=paragraph.section_id,
            page_number=None,
            table_id=None,
            row_locator=f"field={output_path}; block_id={paragraph.block_id}",
            note=_truncate(value),
        )
        candidates.append(
            _InvestorExperienceValueCandidate(
                output_path=output_path,
                value=value,
                anchor=anchor,
                source_field_path=f"paragraph_blocks[{paragraph_index}]",
            )
        )
    return tuple(candidates)


def _collect_holder_structure_table_candidates(
    output_path: str,
    labels: tuple[str, ...],
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[_InvestorExperienceValueCandidate, ...]:
    """收集 table/cell 持有人结构候选。

    Args:
        output_path: holder side 输出路径。
        labels: 允许的 side label。
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        稳定 table/cell 候选元组。

    Raises:
        无显式抛出。
    """

    candidates: list[_InvestorExperienceValueCandidate] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable" or not _holder_structure_table_has_guard(table):
            continue
        for cell_index, cell in _stable_indexed_cells(table):
            context_texts = (
                _cell_value(cell),
                *_tuple_text(cell.row_label_path),
                *_tuple_text(cell.column_header_path),
                *_tuple_text(cell.heading_path),
            )
            context_text = " ".join(
                (
                    *context_texts,
                )
            )
            value = _holder_structure_cell_value(context_texts, labels, _cell_value(cell))
            if value is None:
                value = _holder_structure_value_from_text(context_text, labels)
            if value is None:
                continue
            anchor = _investor_experience_cell_anchor(output_path, table, cell, context)
            candidates.append(
                _InvestorExperienceValueCandidate(
                    output_path=output_path,
                    value=value,
                    anchor=anchor,
                    source_field_path=f"table_blocks[{table_index}].cells[{cell_index}]",
                )
            )
    return tuple(candidates)


def _holder_structure_table_has_guard(table: FundDisclosureTableBlockLike) -> bool:
    """判断 table 是否具备持有人结构上下文。

    Args:
        table: FDD table block。

    Returns:
        table heading/caption/path 命中 guard 时返回 True。

    Raises:
        无显式抛出。
    """

    return _matches_any_token(
        (table.heading_text, table.table_caption_or_nearby_heading, *_tuple_text(table.heading_path)),
        _HOLDER_STRUCTURE_GUARD_LABELS,
    )


def _holder_structure_value_from_text(text: str, labels: tuple[str, ...]) -> str | None:
    """从同源 label/value 文本中抽取持有人结构值。

    Args:
        text: 候选文本。
        labels: 允许 label。

    Returns:
        披露值；无 label、无值或 placeholder 时返回 None。

    Raises:
        无显式抛出。
    """

    for label in sorted(labels, key=len, reverse=True):
        index = text.find(label)
        if index < 0:
            continue
        value = text[index + len(label) :].strip(" ：:，,")
        if not value:
            return None
        if _normalize_match_text(value) in {
            _normalize_match_text(item) for item in _HOLDER_STRUCTURE_PLACEHOLDERS
        }:
            return None
        return value
    return None


def _holder_structure_cell_value(
    context_texts: tuple[str, ...],
    labels: tuple[str, ...],
    cell_value: str,
) -> str | None:
    """从 row/column label 命中的 cell 中读取持有人结构值。

    Args:
        context_texts: cell value 与 label/header/path 文本集合。
        labels: 允许 label。
        cell_value: 当前 cell 披露值。

    Returns:
        当前 cell 可作为值时返回 cell value；否则返回 None。

    Raises:
        无显式抛出。
    """

    if not _matches_any_token(context_texts, labels):
        return None
    normalized = _normalize_match_text(cell_value)
    if normalized in {_normalize_match_text(label) for label in labels}:
        return None
    if normalized in {_normalize_match_text(item) for item in _HOLDER_STRUCTURE_PLACEHOLDERS}:
        return None
    return cell_value


def _select_investor_experience_share_change(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _InvestorExperienceValueCandidate | None:
    """选择基金份额变动 public subvalue。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        share_change 候选；缺失或冲突时返回 None。

    Raises:
        无显式抛出。
    """

    candidates = _collect_share_change_table_candidates(intermediate, context, ambiguous_paths)
    return _resolve_investor_experience_candidate("share_change", candidates, ambiguous_paths)


def _collect_share_change_table_candidates(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> tuple[_InvestorExperienceValueCandidate, ...]:
    """收集 table 份额变动候选。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        稳定 table 候选元组。

    Raises:
        无显式抛出。
    """

    candidates: list[_InvestorExperienceValueCandidate] = []
    for table_index, table in enumerate(intermediate.table_blocks):
        if table.locator_stability != "stable" or not _share_change_table_has_guard(table):
            continue
        candidate = _share_change_candidate_from_table(table_index, table, context, ambiguous_paths)
        if candidate is not None:
            candidates.append(candidate)
    return tuple(candidates)


def _share_change_table_has_guard(table: FundDisclosureTableBlockLike) -> bool:
    """判断 table 是否具备份额变动上下文。

    Args:
        table: FDD table block。

    Returns:
        table heading/caption/path 命中 guard，或行 label 命中份额变动 label 时返回 True。

    Raises:
        无显式抛出。
    """

    if _matches_any_token(
        (table.heading_text, table.table_caption_or_nearby_heading, *_tuple_text(table.heading_path)),
        _SHARE_CHANGE_TABLE_GUARD_LABELS,
    ):
        return True
    labels = (*_SHARE_CHANGE_BEGINNING_LABELS, *_SHARE_CHANGE_ENDING_LABELS, *_SHARE_CHANGE_NET_LABELS)
    return any(
        _path_contains_any_label(cell.row_label_path, labels)
        or _matches_any_token((_cell_value(cell),), labels)
        for _, cell in _stable_indexed_cells(table)
    )


def _share_change_candidate_from_table(
    table_index: int,
    table: FundDisclosureTableBlockLike,
    context: FundProcessorDispatchKey,
    ambiguous_paths: set[str],
) -> _InvestorExperienceValueCandidate | None:
    """从单个 share-change table 构造 public subvalue。

    Args:
        table_index: table tuple 中的原始索引。
        table: FDD table block。
        context: Processor dispatch 身份。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        share_change 候选；无法选定 value column 时返回 None。

    Raises:
        无显式抛出。
    """

    stable_cells = _stable_indexed_cells(table)
    rows = _cells_by_row(stable_cells)
    value_columns = _share_change_value_columns(stable_cells, rows)
    if not value_columns:
        return None
    selected_column, reason = _select_share_change_value_column(value_columns, stable_cells, context)
    if selected_column is None or reason is None:
        if len(value_columns) > 1:
            ambiguous_paths.add("share_change")
        return None
    values = _share_change_values_for_column(selected_column, rows)
    if not any(values.values()):
        return None
    if values["net_change"] is None:
        values["net_change"] = _calculate_investor_share_net_change(
            values["beginning_share"], values["ending_share"]
        )
    header = _share_change_column_header(selected_column, stable_cells)
    anchor_cell = _first_share_change_anchor_cell(selected_column, rows)
    if anchor_cell is None:
        return None
    cell_index, cell = anchor_cell
    anchor = _investor_experience_cell_anchor("share_change", table, cell, context)
    return _InvestorExperienceValueCandidate(
        output_path="share_change",
        value={
            "beginning_share": values["beginning_share"],
            "ending_share": values["ending_share"],
            "net_change": values["net_change"],
            "share_class_column": header,
            "share_class_selection_reason": reason,
        },
        anchor=anchor,
        source_field_path=f"table_blocks[{table_index}].cells[{cell_index}]",
    )


def _share_change_value_columns(
    stable_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
    rows: dict[int, tuple[tuple[int, FundDisclosureCellLike], ...]],
) -> tuple[int, ...]:
    """筛选 share-change value columns，排除 label columns。

    Args:
        stable_cells: 稳定 cell 列表。
        rows: row_index 到 cell 列表的映射。

    Returns:
        候选 value column index 元组。

    Raises:
        无显式抛出。
    """

    columns = sorted({cell.column_index for _, cell in stable_cells})
    return tuple(
        column
        for column in columns
        if not _share_change_is_label_column(column, stable_cells)
        and _share_change_column_has_row_value(column, rows)
    )


def _share_change_is_label_column(
    column: int,
    stable_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
) -> bool:
    """判断某列是否是 label column。

    Args:
        column: column_index。
        stable_cells: 稳定 cell 列表。

    Returns:
        label column 返回 True。

    Raises:
        无显式抛出。
    """

    column_cells = tuple(cell for _, cell in stable_cells if cell.column_index == column)
    header = _share_change_column_header(column, stable_cells)
    if _matches_any_token((header,), _SHARE_CHANGE_LABEL_COLUMN_TOKENS):
        return True
    label_like_count = sum(
        1
        for cell in column_cells
        if _matches_any_token((_cell_value(cell),), _SHARE_CHANGE_LABEL_COLUMN_TOKENS)
    )
    numeric_count = sum(1 for cell in column_cells if _looks_like_share_change_value(_cell_value(cell)))
    return label_like_count > 0 and label_like_count >= numeric_count


def _share_change_column_has_row_value(
    column: int,
    rows: dict[int, tuple[tuple[int, FundDisclosureCellLike], ...]],
) -> bool:
    """判断 column 是否包含 share-change 行的有效数值。

    Args:
        column: column_index。
        rows: row_index 到 cell 列表的映射。

    Returns:
        至少一个 begin/end/net 行有数值时返回 True。

    Raises:
        无显式抛出。
    """

    for row_cells in rows.values():
        if _share_change_row_kind(row_cells) is None:
            continue
        value = _cell_for_column(column, row_cells)
        if value is not None and _looks_like_share_change_value(_cell_value(value)):
            return True
    return False


def _select_share_change_value_column(
    value_columns: tuple[int, ...],
    stable_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
    context: FundProcessorDispatchKey,
) -> tuple[int | None, str | None]:
    """选择 share-change value column。

    Args:
        value_columns: 已过滤的 value columns。
        stable_cells: 稳定 cell 列表。
        context: Processor dispatch 身份。

    Returns:
        `(column_index, reason)`；无法唯一选择时返回 `(None, None)`。

    Raises:
        无显式抛出。
    """

    if len(value_columns) == 1:
        return value_columns[0], "single_value_column"
    fund_code = _normalize_match_text(context.fund_code)
    matched = tuple(
        column
        for column in value_columns
        if _normalize_match_text(_share_change_column_header(column, stable_cells)) == fund_code
    )
    if len(matched) == 1:
        return matched[0], "fund_code_header_match"
    return None, None


def _share_change_values_for_column(
    column: int,
    rows: dict[int, tuple[tuple[int, FundDisclosureCellLike], ...]],
) -> dict[str, str | None]:
    """读取 selected share-change column 的 begin/end/net 值。

    Args:
        column: selected value column。
        rows: row_index 到 cell 列表的映射。

    Returns:
        public shape 三个数值字段。

    Raises:
        无显式抛出。
    """

    values: dict[str, str | None] = {
        "beginning_share": None,
        "ending_share": None,
        "net_change": None,
    }
    for row_cells in rows.values():
        kind = _share_change_row_kind(row_cells)
        if kind is None:
            continue
        value_cell = _cell_for_column(column, row_cells)
        if value_cell is None:
            continue
        value = _cell_value(value_cell)
        if not _looks_like_share_change_value(value):
            continue
        values[kind] = value
    return values


def _share_change_row_kind(
    row_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
) -> str | None:
    """判断 share-change 行类型。

    Args:
        row_cells: 同一 row 的 cell 列表。

    Returns:
        `beginning_share`、`ending_share`、`net_change` 或 None。

    Raises:
        无显式抛出。
    """

    context_text = " ".join(_row_text_context(row_cells))
    if _matches_any_token((context_text,), _SHARE_CHANGE_BEGINNING_LABELS):
        return "beginning_share"
    if _matches_any_token((context_text,), _SHARE_CHANGE_ENDING_LABELS):
        return "ending_share"
    if _matches_any_token((context_text,), _SHARE_CHANGE_NET_LABELS):
        return "net_change"
    return None


def _first_share_change_anchor_cell(
    column: int,
    rows: dict[int, tuple[tuple[int, FundDisclosureCellLike], ...]],
) -> tuple[int, FundDisclosureCellLike] | None:
    """返回 selected column 的首个 share-change anchor cell。

    Args:
        column: selected value column。
        rows: row_index 到 cell 列表的映射。

    Returns:
        `(cell_index, cell)`；无稳定数值 cell 时返回 None。

    Raises:
        无显式抛出。
    """

    for row_cells in rows.values():
        if _share_change_row_kind(row_cells) is None:
            continue
        for cell_index, cell in row_cells:
            if cell.column_index == column and _looks_like_share_change_value(_cell_value(cell)):
                return cell_index, cell
    return None


def _share_change_column_header(
    column: int,
    stable_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
) -> str:
    """聚合 FDD `column_header_path` 构造 share-class column 文本。

    Args:
        column: column_index。
        stable_cells: 稳定 cell 列表。

    Returns:
        去重后以 ` / ` 连接的列头文本；缺失时为空字符串。

    Raises:
        无显式抛出。
    """

    parts: list[str] = []
    seen: set[str] = set()
    for _, cell in stable_cells:
        if cell.column_index != column:
            continue
        for part in cell.column_header_path:
            trimmed = part.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            parts.append(trimmed)
    return " / ".join(parts)


def _calculate_investor_share_net_change(
    beginning_share: str | None,
    ending_share: str | None,
) -> str | None:
    """用 Decimal 计算份额净变动，见模板第 4 章“投资者获得感”。

    Args:
        beginning_share: 期初基金份额。
        ending_share: 期末基金份额。

    Returns:
        两个输入均可解析时返回逗号分隔、两位小数的净变动；否则返回 None。

    Raises:
        无显式抛出。
    """

    if beginning_share is None or ending_share is None:
        return None
    try:
        beginning_value = Decimal(beginning_share.replace(",", ""))
        ending_value = Decimal(ending_share.replace(",", ""))
    except InvalidOperation:
        return None
    net_change = ending_value - beginning_value
    return f"{net_change:,.2f}"


def _looks_like_share_change_value(value: str) -> bool:
    """判断文本是否可作为份额变动数值。

    Args:
        value: cell 文本。

    Returns:
        包含 Decimal-like 数值且不是 placeholder 时返回 True。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_match_text(value)
    if normalized in {"", "无", "不适用", "-", "—", "未披露"}:
        return False
    return _SHARE_CHANGE_VALUE_PATTERN.fullmatch(normalized) is not None


def _resolve_investor_experience_candidate(
    output_path: str,
    candidates: tuple[_InvestorExperienceValueCandidate, ...],
    ambiguous_paths: set[str],
) -> _InvestorExperienceValueCandidate | None:
    """按重复/歧义规则解析 investor_experience 候选。

    Args:
        output_path: 目标输出路径。
        candidates: 同一路径候选。
        ambiguous_paths: 待追加的歧义路径集合。

    Returns:
        唯一可采信候选；无候选或冲突时返回 None。

    Raises:
        无显式抛出。
    """

    if not candidates:
        return None
    normalized_values = {
        _normalize_investor_experience_value(candidate.value) for candidate in candidates
    }
    if len(normalized_values) > 1:
        ambiguous_paths.add(output_path)
        return None
    return candidates[0]


def _normalize_investor_experience_value(value: object) -> str:
    """规范化 investor_experience 候选值用于冲突判断。

    Args:
        value: 候选值。

    Returns:
        稳定比较字符串。

    Raises:
        无显式抛出。
    """

    if isinstance(value, dict):
        return "|".join(
            f"{key}={_normalize_investor_experience_value(value[key])}" for key in sorted(value)
        )
    if isinstance(value, list):
        return "||".join(_normalize_investor_experience_value(item) for item in value)
    return _normalize_match_text(str(value))


def _build_investor_experience_value(
    selected_values: dict[str, _InvestorExperienceValueCandidate],
) -> dict[str, object]:
    """构造 `investor_experience.v1.value` public shape。

    Args:
        selected_values: 已解析的 top-level 候选值。

    Returns:
        只包含 schema_version 与已发出的三个既有 top-level subvalues；全缺时返回空字典。

    Raises:
        无显式抛出。
    """

    value: dict[str, object] = {}
    for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL:
        selected = selected_values.get(top_level)
        if selected is not None:
            value[top_level] = selected.value
    if not value:
        return {}
    return {"schema_version": "investor_experience.v1", **value}


def _investor_experience_emitted_output_paths(
    value: dict[str, object],
    selected_values: dict[str, _InvestorExperienceValueCandidate],
) -> tuple[str, ...]:
    """返回实际进入 public value 的 investor_experience output paths。

    Args:
        value: 已构造的字段族 value。
        selected_values: 已解析的 top-level 候选值。

    Returns:
        需要进入 family anchors 的输出路径元组。

    Raises:
        无显式抛出。
    """

    return tuple(
        top_level
        for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL
        if top_level in value and top_level in selected_values
    )


def _investor_experience_source_truth_gaps(
    value: dict[str, object],
    ambiguous_paths: set[str],
) -> tuple[FundExtractionGap, ...]:
    """构造 investor_experience.v1 source-truth 字段族本地 gaps。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 发生 duplicate ambiguity 的输出路径集合。

    Returns:
        missing/partial/ambiguity gaps。

    Raises:
        无显式抛出。
    """

    gaps: list[FundExtractionGap] = []
    for output_path in sorted(ambiguous_paths):
        gaps.append(
            FundExtractionGap(
                gap_code="ambiguous_table_or_locator",
                message=f"{output_path} 存在多个冲突的稳定 FDD locator 值",
                field_family_id="investor_experience.v1",
                source_field_path=output_path,
                source_boundary="ambiguous_locator",
                required=True,
            )
        )
    missing_top_level = tuple(
        top_level for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL if top_level not in value
    )
    if not value:
        gaps.append(
            FundExtractionGap(
                gap_code="field_family_missing",
                message="investor_experience.v1 未形成允许的 source-truth 字段值",
                field_family_id="investor_experience.v1",
                source_field_path=None,
                source_boundary="annual_report",
                required=True,
            )
        )
    elif missing_top_level:
        gaps.extend(
            FundExtractionGap(
                gap_code="field_family_partial",
                message=f"investor_experience.v1 缺少 required top-level value: {top_level}",
                field_family_id="investor_experience.v1",
                source_field_path=top_level,
                source_boundary="annual_report",
                required=True,
            )
            for top_level in missing_top_level
        )
    return tuple(gaps)


def _investor_experience_status(value: dict[str, object], ambiguous_paths: set[str]) -> str:
    """按三个 top-level 完整度派生 investor_experience 字段族状态。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 已发现的歧义输出路径集合。

    Returns:
        `accepted`、`partial` 或 `missing`。

    Raises:
        无显式抛出。
    """

    if all(top_level in value for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL) and not ambiguous_paths:
        return "accepted"
    if value:
        return "partial"
    return "missing"


def _extract_current_stage_source_truth(
    intermediate: FundDisclosureDocumentContentIntermediate,
    source_provenance: PublicSourceProvenance | None,
    context: FundProcessorDispatchKey,
) -> FundFieldFamilyResult:
    """从 proof-positive FDD 正文抽取模板第 5 章当前阶段输入字段族。

    Args:
        intermediate: 已通过 source-truth admission proof 的正文中间态。
        source_provenance: 公共来源 provenance。
        context: Processor dispatch 身份。

    Returns:
        `current_stage.v1` 字段族；只复用既有 public 字段形状，不输出阶段判断。

    Raises:
        无显式抛出。
    """

    selected_values, ambiguous_paths = _select_current_stage_values(intermediate, context)
    value = _build_current_stage_value(selected_values)
    gaps = _current_stage_source_truth_gaps(value, ambiguous_paths)
    status = _current_stage_status(value, ambiguous_paths)
    anchors = _dedupe_anchors(
        anchor
        for output_path in _current_stage_emitted_output_paths(value, selected_values)
        for anchor in selected_values[output_path].anchors
    )
    return FundFieldFamilyResult(
        field_family_id="current_stage.v1",
        chapter_ids=_CHAPTER_IDS["current_stage.v1"],
        value=value,
        status=status,
        extraction_mode="missing" if status == "missing" else "direct",
        anchors=anchors,
        gaps=gaps,
        source_provenance=source_provenance,
        candidate_evidence=(),
    )


def _select_current_stage_values(
    intermediate: FundDisclosureDocumentContentIntermediate,
    context: FundProcessorDispatchKey,
) -> tuple[dict[str, _CurrentStageValueCandidate], set[str]]:
    """选择 current_stage.v1 允许复用的四个事实输入。

    Args:
        intermediate: FDD 正文中间态。
        context: Processor dispatch 身份。

    Returns:
        `(selected_values, ambiguous_paths)`；只包含允许 public top-level key。

    Raises:
        无显式抛出。
    """

    selected_values: dict[str, _CurrentStageValueCandidate] = {}
    ambiguous_paths: set[str] = set()
    product_values, product_ambiguous_paths = _select_product_essence_values(
        intermediate, context
    )
    basic_identity = _build_product_essence_basic_identity(product_values, context)
    if basic_identity is not None:
        emitted_paths = tuple(
            output_path
            for output_path in _product_essence_emitted_output_paths(
                {"basic_identity": basic_identity}, product_values
            )
            if output_path.startswith("basic_identity.")
        )
        selected_values["basic_identity"] = _CurrentStageValueCandidate(
            output_path="basic_identity",
            value=basic_identity,
            anchors=tuple(product_values[output_path].anchor for output_path in emitted_paths),
            source_field_path="basic_identity",
        )
    if any(path.startswith("basic_identity.") for path in product_ambiguous_paths):
        ambiguous_paths.add("basic_identity")

    share_change = _select_investor_experience_share_change(
        intermediate, context, ambiguous_paths
    )
    if share_change is not None:
        selected_values["share_change"] = _CurrentStageValueCandidate(
            output_path="share_change",
            value=share_change.value,
            anchors=(share_change.anchor,),
            source_field_path=share_change.source_field_path,
        )

    holdings_snapshot = _select_manager_profile_holdings_snapshot(
        intermediate, context, ambiguous_paths
    )
    if holdings_snapshot is not None:
        selected_values["holdings_snapshot"] = _CurrentStageValueCandidate(
            output_path="holdings_snapshot",
            value=holdings_snapshot.value,
            anchors=(holdings_snapshot.anchor,),
            source_field_path=holdings_snapshot.source_field_path,
        )

    portfolio_managers = _select_manager_profile_portfolio_managers(
        intermediate, context, ambiguous_paths
    )
    if portfolio_managers is not None:
        selected_values["portfolio_managers"] = _CurrentStageValueCandidate(
            output_path="portfolio_managers",
            value=portfolio_managers.value,
            anchors=(portfolio_managers.anchor,),
            source_field_path=portfolio_managers.source_field_path,
        )
    return selected_values, ambiguous_paths


def _build_current_stage_value(
    selected_values: dict[str, _CurrentStageValueCandidate],
) -> dict[str, object]:
    """构造 `current_stage.v1.value`，不生成当前阶段语义摘要。

    Args:
        selected_values: 已解析的允许 top-level 候选值。

    Returns:
        只包含 schema_version 与允许 top-level key；无值时返回空字典。

    Raises:
        无显式抛出。
    """

    value: dict[str, object] = {}
    for top_level in _CURRENT_STAGE_REQUIRED_TOP_LEVEL:
        selected = selected_values.get(top_level)
        if selected is not None:
            value[top_level] = selected.value
    if not value:
        return {}
    return {"schema_version": "current_stage.v1", **value}


def _current_stage_emitted_output_paths(
    value: dict[str, object],
    selected_values: dict[str, _CurrentStageValueCandidate],
) -> tuple[str, ...]:
    """返回实际进入 public value 的 current_stage output paths。

    Args:
        value: 已构造的字段族 value。
        selected_values: 已解析的 top-level 候选值。

    Returns:
        需要进入 family anchors 的输出路径元组。

    Raises:
        无显式抛出。
    """

    return tuple(
        top_level
        for top_level in _CURRENT_STAGE_REQUIRED_TOP_LEVEL
        if top_level in value and top_level in selected_values
    )


def _current_stage_source_truth_gaps(
    value: dict[str, object],
    ambiguous_paths: set[str],
) -> tuple[FundExtractionGap, ...]:
    """构造 current_stage.v1 source-truth 字段族本地 gaps。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 发生 duplicate ambiguity 的输出路径集合。

    Returns:
        missing/partial/ambiguity gaps。

    Raises:
        无显式抛出。
    """

    gaps: list[FundExtractionGap] = []
    for output_path in sorted(ambiguous_paths):
        gaps.append(
            FundExtractionGap(
                gap_code="ambiguous_table_or_locator",
                message=f"{output_path} 存在多个冲突的稳定 FDD locator 值",
                field_family_id="current_stage.v1",
                source_field_path=output_path,
                source_boundary="ambiguous_locator",
                required=True,
            )
        )
    missing_top_level = tuple(
        top_level for top_level in _CURRENT_STAGE_REQUIRED_TOP_LEVEL if top_level not in value
    )
    if not value:
        gaps.append(
            FundExtractionGap(
                gap_code="field_family_missing",
                message="current_stage.v1 未形成允许的 source-truth 字段值",
                field_family_id="current_stage.v1",
                source_field_path=None,
                source_boundary="annual_report",
                required=True,
            )
        )
    elif missing_top_level:
        gaps.extend(
            FundExtractionGap(
                gap_code="field_family_partial",
                message=f"current_stage.v1 缺少 required top-level value: {top_level}",
                field_family_id="current_stage.v1",
                source_field_path=top_level,
                source_boundary="annual_report",
                required=True,
            )
            for top_level in missing_top_level
        )
    return tuple(gaps)


def _current_stage_status(value: dict[str, object], ambiguous_paths: set[str]) -> str:
    """按四个允许 top-level 完整度派生 current_stage 字段族状态。

    Args:
        value: 已构造的字段族 value。
        ambiguous_paths: 已发现的歧义输出路径集合。

    Returns:
        `accepted`、`partial` 或 `missing`。

    Raises:
        无显式抛出。
    """

    if all(top_level in value for top_level in _CURRENT_STAGE_REQUIRED_TOP_LEVEL) and not ambiguous_paths:
        return "accepted"
    if value:
        return "partial"
    return "missing"


def _investor_experience_cell_anchor(
    output_path: str,
    table: FundDisclosureTableBlockLike,
    cell: FundDisclosureCellLike,
    context: FundProcessorDispatchKey,
) -> EvidenceAnchor:
    """构造 investor_experience table/cell source-truth EvidenceAnchor。

    Args:
        output_path: 目标输出路径。
        table: parent table block。
        cell: FDD table cell。
        context: Processor dispatch 身份。

    Returns:
        source_kind 固定为 annual_report 的公共锚点。

    Raises:
        无显式抛出。
    """

    table_id = cell.table_id or table.table_id
    row_locator = (
        f"field={output_path}; table_id={table_id}; "
        f"row={cell.row_index}; column={cell.column_index}; cell_id={cell.cell_id}"
    )
    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=context.document_year,
        section_id=cell.section_anchor or table.section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=_truncate(_cell_value(cell)),
    )


def _stable_indexed_cells(
    table: FundDisclosureTableBlockLike,
) -> tuple[tuple[int, FundDisclosureCellLike], ...]:
    """返回按 row/column 排序的 stable cell。

    Args:
        table: FDD table block。

    Returns:
        `(原始 cell tuple index, cell)` 元组。

    Raises:
        无显式抛出。
    """

    return tuple(
        sorted(
            (
                (index, cell)
                for index, cell in enumerate(table.cells)
                if cell.locator_stability == "stable"
            ),
            key=lambda item: (item[1].row_index, item[1].column_index),
        )
    )


def _cells_by_row(
    stable_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
) -> dict[int, tuple[tuple[int, FundDisclosureCellLike], ...]]:
    """按 row_index 分组 stable cells。

    Args:
        stable_cells: 稳定 cell 列表。

    Returns:
        row_index 到 cell 列表的映射。

    Raises:
        无显式抛出。
    """

    rows: dict[int, list[tuple[int, FundDisclosureCellLike]]] = {}
    for cell_index, cell in stable_cells:
        rows.setdefault(cell.row_index, []).append((cell_index, cell))
    return {row: tuple(cells) for row, cells in sorted(rows.items())}


def _row_text_context(
    row_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
) -> tuple[str, ...]:
    """返回同一 row 的文本上下文。

    Args:
        row_cells: 同一 row 的 cell 列表。

    Returns:
        cell value、row label、column header 和 heading path 文本。

    Raises:
        无显式抛出。
    """

    texts: list[str] = []
    for _, cell in row_cells:
        texts.extend(
            (
                _cell_value(cell),
                *_tuple_text(cell.row_label_path),
                *_tuple_text(cell.column_header_path),
                *_tuple_text(cell.heading_path),
            )
        )
    return tuple(text for text in texts if text)


def _cell_for_column(
    column: int,
    row_cells: tuple[tuple[int, FundDisclosureCellLike], ...],
) -> FundDisclosureCellLike | None:
    """返回指定 row 中指定 column 的 cell。

    Args:
        column: column_index。
        row_cells: 同一 row 的 cell 列表。

    Returns:
        命中的 cell；缺失时返回 None。

    Raises:
        无显式抛出。
    """

    for _, cell in row_cells:
        if cell.column_index == column:
            return cell
    return None


def _cell_value(cell: FundDisclosureCellLike) -> str:
    """返回 FDD cell 的规范化取值。

    Args:
        cell: FDD table cell。

    Returns:
        `cell_text_normalized` 非空时优先，否则回退 `cell_text`。

    Raises:
        无显式抛出。
    """

    value = cell.cell_text_normalized.strip() if cell.cell_text_normalized else ""
    if value:
        return value
    return cell.cell_text.strip()


def _select_investor_experience_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择投资者获得感字段族的 candidate-only locator evidence（见模板第4章）。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-E mapping table 排序、去重和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, strong_tokens, generic_tokens, guard_tokens in _INVESTOR_EXPERIENCE_MATCH_GROUPS:
        _extend_investor_experience_section_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_investor_experience_paragraph_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_investor_experience_table_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        if len(records) >= _INVESTOR_EXPERIENCE_CANDIDATE_LIMIT:
            break
    return tuple(records[:_INVESTOR_EXPERIENCE_CANDIDATE_LIMIT])


def _extend_investor_experience_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 investor_experience section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_guarded_investor_experience_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="investor_experience.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_investor_experience_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 investor_experience paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        if path in seen_paths or not _matches_guarded_investor_experience_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="investor_experience.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_investor_experience_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 investor_experience table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_guarded_investor_experience_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="investor_experience.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_investor_experience_cell_records(
            records, seen_paths, table_index, table, role, strong_tokens, generic_tokens, guard_tokens
        )


def _extend_investor_experience_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 investor_experience table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        guard_context = _investor_experience_cell_guard_context(role, table, cell)
        if path in seen_paths or not _matches_guarded_investor_experience_source(
            texts, strong_tokens, generic_tokens, guard_context, guard_tokens
        ):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="investor_experience.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _matches_guarded_investor_experience_source(
    texts: tuple[str | None, ...],
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_context: tuple[str | None, ...],
    guard_tokens: tuple[str, ...],
) -> bool:
    """按 S6-E source-level guard 规则判断 investor_experience source 是否可追加。

    Args:
        texts: 当前 source 的候选匹配文本。
        strong_tokens: 无需额外 context 的 token。
        generic_tokens: 需要 source-level guard 的 token。
        guard_context: 当前 source 允许用于 guard 的上下文文本。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        strong token 命中时返回 True；generic token 命中且 guard context 命中时返回 True。

    Raises:
        无显式抛出。
    """

    if _matches_any_token(texts, strong_tokens):
        return True
    if not generic_tokens or not _matches_any_token(texts, generic_tokens):
        return False
    return _matches_any_token(guard_context, guard_tokens)


def _investor_experience_cell_guard_context(
    role: str,
    table: FundDisclosureTableBlockLike,
    cell: object,
) -> tuple[str | None, ...]:
    """返回 cell 级 generic guard context。

    Args:
        role: 当前 investor_experience evidence role。
        table: parent table block 协议对象。
        cell: table cell 协议对象。

    Returns:
        只含 plan/controller 允许字段的 guard context。

    Raises:
        无显式抛出。
    """

    table_context = (
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
    )
    if role == "subscription_redemption":
        return (
            *table_context,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
    return (
        *table_context,
        cell.cell_text_normalized,
        cell.cell_text,
        *_tuple_text(cell.row_label_path),
        *_tuple_text(cell.column_header_path),
        *_tuple_text(cell.heading_path),
    )


def _select_current_stage_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择当前阶段字段族的 candidate-only locator evidence（见模板第5章）。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-G mapping table 排序、去重和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, strong_tokens, generic_tokens, guard_tokens in _CURRENT_STAGE_MATCH_GROUPS:
        _extend_current_stage_section_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_current_stage_paragraph_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_current_stage_table_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        if len(records) >= _CURRENT_STAGE_CANDIDATE_LIMIT:
            break
    return tuple(records[:_CURRENT_STAGE_CANDIDATE_LIMIT])


def _extend_current_stage_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 current_stage section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_guarded_current_stage_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="current_stage.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_current_stage_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 current_stage paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        if path in seen_paths or not _matches_guarded_current_stage_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="current_stage.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_current_stage_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 current_stage table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_guarded_current_stage_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="current_stage.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_current_stage_cell_records(
            records, seen_paths, table_index, table, role, strong_tokens, generic_tokens, guard_tokens
        )


def _extend_current_stage_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 current_stage table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        guard_context = _current_stage_cell_guard_context(table, cell)
        if path in seen_paths or not _matches_guarded_current_stage_source(
            texts, strong_tokens, generic_tokens, guard_context, guard_tokens
        ):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="current_stage.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _matches_guarded_current_stage_source(
    texts: tuple[str | None, ...],
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_context: tuple[str | None, ...],
    guard_tokens: tuple[str, ...],
) -> bool:
    """按 S6-G source-level guard 规则判断 current_stage source 是否可追加。

    Args:
        texts: 当前 source 的候选匹配文本。
        strong_tokens: 无需额外 context 的 token。
        generic_tokens: 需要 source-level guard 的 token。
        guard_context: 当前 source 允许用于 guard 的上下文文本。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        strong token 命中时返回 True；generic token 命中且 guard context 命中时返回 True。

    Raises:
        无显式抛出。
    """

    if _matches_any_token(texts, strong_tokens):
        return True
    if not generic_tokens or not _matches_any_token(texts, generic_tokens):
        return False
    return _matches_any_token(guard_context, guard_tokens)


def _current_stage_cell_guard_context(
    table: FundDisclosureTableBlockLike,
    cell: object,
) -> tuple[str | None, ...]:
    """返回 current_stage cell 级 generic guard context。

    Args:
        table: parent table block 协议对象。
        cell: table cell 协议对象。

    Returns:
        role-invariant guard context；始终排除 cell_text / cell_text_normalized。

    Raises:
        无显式抛出。
    """

    return (
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
        *_tuple_text(cell.row_label_path),
        *_tuple_text(cell.column_header_path),
        *_tuple_text(cell.heading_path),
    )


def _select_core_risk_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择核心风险字段族的 candidate-only locator evidence（见模板第6章）。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-F mapping table 排序、去重和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    content_intermediate = _content_intermediate_or_none(intermediate)
    if content_intermediate is None:
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, strong_tokens, generic_tokens, guard_tokens in _CORE_RISK_MATCH_GROUPS:
        _extend_core_risk_section_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_core_risk_paragraph_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        _extend_core_risk_table_records(
            records,
            seen_paths,
            content_intermediate,
            role,
            strong_tokens,
            generic_tokens,
            guard_tokens,
        )
        if len(records) >= _CORE_RISK_CANDIDATE_LIMIT:
            break
    return tuple(records[:_CORE_RISK_CANDIDATE_LIMIT])


def _extend_core_risk_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 core_risk section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_guarded_core_risk_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="core_risk.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_core_risk_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 core_risk paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        if path in seen_paths or not _matches_guarded_core_risk_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="core_risk.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_core_risk_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 core_risk table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_guarded_core_risk_source(
            texts, strong_tokens, generic_tokens, texts, guard_tokens
        ):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="core_risk.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_core_risk_cell_records(
            records, seen_paths, table_index, table, role, strong_tokens, generic_tokens, guard_tokens
        )


def _extend_core_risk_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_tokens: tuple[str, ...],
) -> None:
    """追加 core_risk table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        strong_tokens: 不需要额外 context 的匹配 token。
        generic_tokens: 需要 source-level guard 的匹配 token。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        guard_context = _core_risk_cell_guard_context(table, cell)
        if path in seen_paths or not _matches_guarded_core_risk_source(
            texts, strong_tokens, generic_tokens, guard_context, guard_tokens
        ):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="core_risk.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _matches_guarded_core_risk_source(
    texts: tuple[str | None, ...],
    strong_tokens: tuple[str, ...],
    generic_tokens: tuple[str, ...],
    guard_context: tuple[str | None, ...],
    guard_tokens: tuple[str, ...],
) -> bool:
    """按 S6-F source-level guard 规则判断 core_risk source 是否可追加。

    Args:
        texts: 当前 source 的候选匹配文本。
        strong_tokens: 无需额外 context 的 token。
        generic_tokens: 需要 source-level guard 的 token。
        guard_context: 当前 source 允许用于 guard 的上下文文本。
        guard_tokens: 允许 generic token 通过的 context token。

    Returns:
        strong token 命中时返回 True；generic token 命中且 guard context 命中时返回 True。

    Raises:
        无显式抛出。
    """

    if _matches_any_token(texts, strong_tokens):
        return True
    if not generic_tokens or not _matches_any_token(texts, generic_tokens):
        return False
    return _matches_any_token(guard_context, guard_tokens)


def _core_risk_cell_guard_context(
    table: FundDisclosureTableBlockLike,
    cell: object,
) -> tuple[str | None, ...]:
    """返回 core_risk cell 级 generic guard context。

    Args:
        table: parent table block 协议对象。
        cell: table cell 协议对象。

    Returns:
        role-invariant guard context；始终排除 cell_text / cell_text_normalized。

    Raises:
        无显式抛出。
    """

    return (
        table.heading_text,
        table.table_caption_or_nearby_heading,
        *_tuple_text(table.heading_path),
        *_tuple_text(cell.row_label_path),
        *_tuple_text(cell.column_header_path),
        *_tuple_text(cell.heading_path),
    )


def _candidate_missing_field_family(
    family_id: FundFieldFamilyId,
    source_provenance: PublicSourceProvenance | None,
    candidate_evidence: tuple[FundCandidateEvidenceRecord, ...],
) -> FundFieldFamilyResult:
    """构造带 candidate evidence 的 public-missing 字段族。

    Args:
        family_id: 字段族 ID。
        source_provenance: 公共来源 provenance。
        candidate_evidence: candidate-only 证据记录。

    Returns:
        public status 仍为 missing 的字段族结果。

    Raises:
        无显式抛出。
    """

    return FundFieldFamilyResult(
        field_family_id=family_id,
        chapter_ids=_CHAPTER_IDS[family_id],
        value={},
        status="missing",
        extraction_mode="missing",
        anchors=(),
        gaps=(
            FundExtractionGap(
                gap_code="candidate_only_not_source_truth",
                message=(
                    f"{family_id} 仅存在 candidate-only locator evidence；"
                    "未证明 source truth 或字段正确性"
                ),
                field_family_id=family_id,
                source_field_path=None,
                source_boundary="candidate_only",
                required=True,
            ),
        ),
        source_provenance=source_provenance,
        candidate_evidence=candidate_evidence,
    )


def _missing_field_family(
    family_id: FundFieldFamilyId,
    source_provenance: PublicSourceProvenance | None,
) -> FundFieldFamilyResult:
    """构造全缺字段族结果。

    Args:
        family_id: 字段族 ID。
        source_provenance: 公共来源 provenance。

    Returns:
        status="missing" 的字段族结果。

    Raises:
        无显式抛出。
    """

    return FundFieldFamilyResult(
        field_family_id=family_id,
        chapter_ids=_CHAPTER_IDS[family_id],
        value={},
        status="missing",
        extraction_mode="missing",
        anchors=(),
        gaps=(
            FundExtractionGap(
                gap_code="field_family_missing",
                message=(
                    f"{family_id} 字段抽取未实现："
                    "FundDisclosureDocument schema gate 完成前全部返回 missing"
                ),
                field_family_id=family_id,
                source_field_path=None,
                source_boundary="unsupported_intermediate",
                required=True,
            ),
        ),
        source_provenance=source_provenance,
    )


def _with_source_truth_admission_gap(
    family: FundFieldFamilyResult,
    gap_code: FundExtractionGapCode,
) -> FundFieldFamilyResult:
    """给字段族追加 source-truth admission fail-closed 本地 gap。

    Args:
        family: 原字段族结果。
        gap_code: source-truth admission 缺失或非法 gap code。

    Returns:
        保留 public missing 形状、追加 source-truth admission gap 的字段族结果。

    Raises:
        无显式抛出。
    """

    if gap_code == "source_truth_admission_missing":
        message = "FundDisclosureDocument source-truth admission proof is missing"
    else:
        message = "FundDisclosureDocument source-truth admission proof is invalid"
    return FundFieldFamilyResult(
        field_family_id=family.field_family_id,
        chapter_ids=family.chapter_ids,
        value={},
        status="missing",
        extraction_mode="missing",
        anchors=(),
        gaps=(
            *family.gaps,
            FundExtractionGap(
                gap_code=gap_code,
                message=message,
                field_family_id=family.field_family_id,
                source_field_path=None,
                source_boundary="source_truth_unverified",
                required=True,
            ),
        ),
        source_provenance=family.source_provenance,
        candidate_evidence=family.candidate_evidence,
    )


def _matches_any_token(texts: tuple[str | None, ...], tokens: tuple[str, ...]) -> bool:
    """判断文本集合是否命中任一 token。

    Args:
        texts: 候选文本集合。
        tokens: 匹配 token。

    Returns:
        任一文本包含任一 token 时返回 True。

    Raises:
        无显式抛出。
    """

    normalized_tokens = tuple(_normalize_match_text(token) for token in tokens)
    return any(
        token and token in _normalize_match_text(text)
        for text in texts
        for token in normalized_tokens
    )


def _normalize_match_text(text: str | None) -> str:
    """规范化用于 token matching 的文本。

    Args:
        text: 原始文本或 None。

    Returns:
        去除常见空白后的文本。

    Raises:
        无显式抛出。
    """

    if text is None:
        return ""
    return "".join(str(text).split()).replace("\u3000", "")


def _first_non_empty(texts: tuple[str | None, ...]) -> str:
    """返回第一个非空文本。

    Args:
        texts: 候选文本集合。

    Returns:
        第一个非空文本；全部为空时返回固定占位。

    Raises:
        无显式抛出。
    """

    for text in texts:
        if text:
            return text
    return "candidate evidence"


def _truncate(text: str) -> str:
    """截断 candidate excerpt。

    Args:
        text: 原始摘录。

    Returns:
        最长 160 字符的摘录。

    Raises:
        无显式抛出。
    """

    return text[:_CANDIDATE_EXCERPT_LIMIT]


def _tuple_text(values: tuple[str, ...]) -> tuple[str, ...]:
    """返回字符串 tuple，供类型检查和展开使用。

    Args:
        values: 字符串 tuple。

    Returns:
        原值。

    Raises:
        无显式抛出。
    """

    return values


def _unsupported_block_details(
    context: FundProcessorDispatchKey,
    *,
    supported_fund_type: FundType,
) -> tuple[FundExtractionGapCode, FundExtractionSourceBoundary]:
    """按 dispatch key 不匹配维度选择 fail-closed gap 归因。

    Args:
        context: Processor 路由键。
        supported_fund_type: 当前 processor 子类声明支持的基金类型。

    Returns:
        跨字段缺口码与 source boundary。

    Raises:
        无显式抛出。
    """

    if context.fund_type != supported_fund_type:
        return "unsupported_fund_type", "unsupported_fund_type"
    if context.report_type != "annual_report":
        return "unsupported_report_type", "unsupported_report_type"
    if context.intermediate_kind != _FUND_DISCLOSURE_INTERMEDIATE_KIND:
        return "unsupported_intermediate_kind", "unsupported_intermediate"
    if context.processor_goal != "template_chapters_1_6_minimum_field_families":
        return "unsupported_processor_goal", "unsupported_processor_goal"
    return "unsupported_processor", "unsupported_intermediate"


def _blocked_result(
    processor_id: str,
    context: FundProcessorDispatchKey,
    *,
    gap_code: FundExtractionGapCode,
    message: str,
    source_boundary: FundExtractionSourceBoundary,
    contract_status: FundProcessorContractStatus | None = None,
) -> FundProcessorResult:
    """构造跨字段 fail-closed processor 结果。

    Args:
        processor_id: 当前 processor ID。
        context: Processor 路由键。
        gap_code: 跨字段缺口码。
        message: 缺口说明。
        source_boundary: 跨字段缺口来源边界。
        contract_status: 显式契约状态；缺省时从 gap_code 前缀自动推导。

    Returns:
        unsupported 或 blocked 状态结果。

    Raises:
        无显式抛出。
    """

    if contract_status is None:
        contract_status = "unsupported" if gap_code.startswith("unsupported_") else "blocked"
    return FundProcessorResult(
        processor_id=processor_id,
        output_schema_version=_OUTPUT_SCHEMA_VERSION,
        fund_code=context.fund_code,
        report_year=context.document_year,
        fund_type=context.fund_type,
        report_type=context.report_type,
        input_intermediate_kind=context.intermediate_kind,
        field_families=(),
        gaps=(
            FundExtractionGap(
                gap_code=gap_code,
                message=message,
                field_family_id=None,
                source_field_path=None,
                source_boundary=source_boundary,
                required=True,
            ),
        ),
        anchors=(),
        source_provenance=None,
        candidate_boundary=None,
        contract_status=contract_status,
    )
