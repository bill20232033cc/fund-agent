"""FundDisclosureDocument 中间态 processor（S4 skeleton）。

本 processor 只做：注册、身份校验、S3 admission 判定消费、fail-closed extract。
字段族提取在 FundDisclosureDocument schema gate 完成前全部返回 missing。
不读取 FundDocumentRepository、PDF/cache/source helper、Docling、network、
provider、LLM、Service/UI/Host、renderer 或 quality gate。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable, cast

from fund_agent.fund.extractors.models import EvidenceAnchor
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


@dataclass(frozen=True, slots=True)
class _ProductEssenceValueCandidate:
    """product_essence.v1 单个字段值候选。"""

    output_path: str
    value: str
    anchor: EvidenceAnchor
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


class FundDisclosureDocumentProcessor:
    """FundDisclosureDocument 中间态 processor（S4 skeleton）。

    本 processor 只支持 active_fund + annual_report + fund_disclosure_document.v1，
    在 FundDisclosureDocument schema gate 完成前所有字段族返回 missing。
    不声明 source truth、parser replacement、candidate proof、readiness 或 release。
    """

    processor_id: Final[str] = "fund_disclosure_document.fund_disclosure_document.v1"
    priority: Final[int] = 50
    output_schema_version: Final[str] = _OUTPUT_SCHEMA_VERSION

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """判断是否支持当前 dispatch key。

        Args:
            context: Processor 路由键。

        Returns:
            仅在主动基金年报 FundDisclosureDocument 中间态返回 True。

        Raises:
            无显式抛出。
        """

        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "fund_disclosure_document.v1"
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
            gap_code, source_boundary = _unsupported_block_details(context)
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

        identity_blocked = _check_identity(context, intermediate)
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


def _check_identity(
    context: FundProcessorDispatchKey,
    intermediate: FundDisclosureDocumentIntermediate,
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
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
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
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
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
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
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
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
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
        六个字段族结果；S6-B/S6-C/S6-D/S6-E/S6-F/S6-G 仅为已接受字段族附加
        candidate evidence。

    Raises:
        无显式抛出。
    """

    product_essence_source_truth: FundFieldFamilyResult | None = None
    content_intermediate = _content_intermediate_or_none(intermediate)
    if source_truth_extraction_allowed and content_intermediate is not None:
        product_essence_source_truth = _extract_product_essence_source_truth(
            content_intermediate, source_provenance, context
        )

    product_essence_evidence = (
        ()
        if product_essence_source_truth is not None
        else _select_product_essence_candidate_evidence(intermediate)
    )
    return_attribution_evidence = _select_return_attribution_candidate_evidence(intermediate)
    manager_profile_evidence = _select_manager_profile_candidate_evidence(intermediate)
    investor_experience_evidence = _select_investor_experience_candidate_evidence(intermediate)
    current_stage_evidence = _select_current_stage_candidate_evidence(intermediate)
    core_risk_evidence = _select_core_risk_candidate_evidence(intermediate)
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
    for output_path in _PRODUCT_ESSENCE_LABELS:
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
        if _path_contains_any_label(cell.row_label_path, labels):
            return output_path
    for output_path, labels in _PRODUCT_ESSENCE_LABELS.items():
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
        value["risk_characteristic_text"] = {
            "schema_version": "risk_characteristic_text.v1",
            "fund_code": context.fund_code,
            "report_year": context.document_year,
            "risk_characteristic_text": risk_text,
            "source_anchors": [_risk_characteristic_anchor_ref(risk_anchor)],
        }
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
) -> tuple[FundExtractionGapCode, FundExtractionSourceBoundary]:
    """按 dispatch key 不匹配维度选择 fail-closed gap 归因。

    Args:
        context: Processor 路由键。

    Returns:
        跨字段缺口码与 source boundary。

    Raises:
        无显式抛出。
    """

    if context.fund_type != "active_fund":
        return "unsupported_fund_type", "unsupported_fund_type"
    if context.report_type != "annual_report":
        return "unsupported_report_type", "unsupported_report_type"
    if context.intermediate_kind != "fund_disclosure_document.v1":
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
