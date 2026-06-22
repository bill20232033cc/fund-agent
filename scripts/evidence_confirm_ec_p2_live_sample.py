"""EC-P2 repository-bounded live sample runner。

该脚本只允许 004393/2025，用于验证 repository -> ParsedAnnualReport ->
section smoke projection -> annual_report reference materializer -> V2 Evidence Confirm
通路。它不输出 PDF 路径、来源 URL、全文 excerpt 或字段正确性结论。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from typing import Final

from fund_agent.fund.chapter_facts import (
    CHAPTER_FACT_SCHEMA_VERSION,
    ChapterEvidenceAnchor,
    ChapterFacetResolution,
    ChapterFactEntry,
    ChapterFactInput,
    ChapterFactProjection,
    ChapterItemRuleProjection,
    ChapterLensResolution,
)
from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.evidence_confirm_sources import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
    run_repository_bounded_evidence_confirm,
)
from fund_agent.fund.template.contracts import get_chapter_contract

AUTHORIZED_FUND_CODE: Final[str] = "004393"
AUTHORIZED_REPORT_YEAR: Final[int] = 2025
PROJECTION_KIND: Final[str] = "ec_p2_live_section_smoke"
SMOKE_SOURCE_FIELD_ID: Final[str] = "ec_p2.live_section_smoke"
SMOKE_ANCHOR_ID: Final[str] = "ec-p2-live-section-smoke-anchor"
SMOKE_FACT_ID: Final[str] = "ec-p2-live-section-smoke-fact"
SMOKE_CHAPTER_ID: Final[int] = 0


class LiveProjectionUnavailableError(RuntimeError):
    """表示 live parsed report 无可用非空 section。"""


def build_live_section_smoke_projection(parsed_report: ParsedAnnualReport) -> ChapterFactProjection:
    """从 live ParsedAnnualReport 构造 EC-P2 section smoke projection。

    Args:
        parsed_report: repository 已加载的年报解析结果。

    Returns:
        只含一个 section smoke fact 的章节事实投影。

    Raises:
        LiveProjectionUnavailableError: 没有任何非空 section 可用于 smoke path。
    """

    section_id, token = _first_non_empty_section_token(parsed_report)
    contract = get_chapter_contract(SMOKE_CHAPTER_ID)
    anchor = ChapterEvidenceAnchor(
        anchor_id=SMOKE_ANCHOR_ID,
        source_kind="annual_report",
        document_year=parsed_report.key.year,
        section_id=section_id,
        page_number=None,
        table_id=None,
        row_locator=None,
        note=PROJECTION_KIND,
    )
    fact = ChapterFactEntry(
        fact_id=SMOKE_FACT_ID,
        chapter_id=SMOKE_CHAPTER_ID,
        field_path="ec_p2.live_section_smoke.section_token",
        source_field_id=SMOKE_SOURCE_FIELD_ID,
        source_field_name="EC-P2 live section smoke token",
        status="available",
        value={"section_smoke_token": token},
        extraction_mode=None,
        evidence_anchor_ids=(SMOKE_ANCHOR_ID,),
        missing_reason=None,
        missing_detail=None,
        required_by=("EC-P2 repository-bounded live pathway smoke",),
    )
    chapter = ChapterFactInput(
        chapter_id=SMOKE_CHAPTER_ID,
        title=contract.title,
        contract=contract,
        fund_type="unknown",
        classification_basis=(PROJECTION_KIND,),
        facet_resolution=ChapterFacetResolution(
            chapter_id=SMOKE_CHAPTER_ID,
            fund_type="unknown",
            facets=(),
            status="empty",
            reason=PROJECTION_KIND,
            source="empty",
            non_asserted_facets=(),
        ),
        lens_resolution=ChapterLensResolution(
            chapter_id=SMOKE_CHAPTER_ID,
            fund_type="unknown",
            lens_key="unknown",
            used_default=False,
            statements=(),
            facets_any=(),
            priority=None,
            missing_reason="classified_fund_type_missing",
        ),
        item_rule_projection=ChapterItemRuleProjection(chapter_id=SMOKE_CHAPTER_ID, decisions=()),
        facts=(fact,),
        evidence_anchors=(anchor,),
        missing_reasons=(),
        source_field_ids=(SMOKE_SOURCE_FIELD_ID,),
    )
    return ChapterFactProjection(
        schema_version=CHAPTER_FACT_SCHEMA_VERSION,
        fund_code=parsed_report.key.fund_code,
        report_year=parsed_report.key.year,
        fund_type="unknown",
        classification_basis=(PROJECTION_KIND,),
        chapters=(chapter,),
        global_missing_reasons=(),
    )


async def run_authorized_sample(*, force_refresh: bool, repository: object | None = None) -> dict[str, object]:
    """执行已授权 004393/2025 live sample 并返回安全 JSON payload。

    Args:
        force_refresh: 是否强制刷新 repository。
        repository: 可选注入 repository；CLI 为空时由 runner 创建默认 repository。

    Returns:
        只包含标量和计数的安全 payload。

    Raises:
        无显式抛出；runner 会把 repository 和 projection failure 转为安全结果。
    """

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code=AUTHORIZED_FUND_CODE,
            report_year=AUTHORIZED_REPORT_YEAR,
            projection_factory=build_live_section_smoke_projection,
            repository=repository,
            force_refresh=force_refresh,
        )
    )
    return _safe_result_payload(result)


def _first_non_empty_section_token(parsed_report: ParsedAnnualReport) -> tuple[str, str]:
    """选择第一个稳定排序的非空 section token。

    Args:
        parsed_report: repository 已加载的年报解析结果。

    Returns:
        section id 与可在 section excerpt 中匹配的短 token。

    Raises:
        LiveProjectionUnavailableError: 没有非空 section。
    """

    for section_id in sorted(parsed_report.sections):
        text = _normalize_whitespace(parsed_report.get_section_text(section_id))
        if text:
            return section_id, text[:24]
    raise LiveProjectionUnavailableError("live_projection_section_unavailable")


def _safe_result_payload(
    result: EvidenceConfirmRepositoryRunResult,
) -> dict[str, object]:
    """把 runner 结果压缩为安全标量 payload。

    Args:
        result: repository runner 结果。

    Returns:
        不含 excerpt、PDF 路径或 URL 的 JSON 兼容字典。

    Raises:
        无显式抛出。
    """

    reference_count = (
        len(result.reference_build_result.references)
        if result.reference_build_result is not None
        else 0
    )
    evidence_status = (
        result.evidence_confirm_result.overall_status
        if result.evidence_confirm_result is not None
        else None
    )
    metadata_admitted = (
        result.source_provenance.metadata_admitted
        if result.source_provenance is not None
        else False
    )
    return {
        "sample": f"{AUTHORIZED_FUND_CODE}/{AUTHORIZED_REPORT_YEAR}",
        "status": result.status,
        "pathway_status": result.pathway_status,
        "pathway_warning_reasons": result.pathway_warning_reasons,
        "projection_kind": PROJECTION_KIND,
        "field_correctness_proven": False,
        "source_metadata_admitted": metadata_admitted,
        "reference_count": reference_count,
        "evidence_confirm_overall_status": evidence_status,
        "issue_reasons": tuple(issue.reason for issue in result.issues),
        "failure_categories": tuple(
            issue.failure_category for issue in result.issues if issue.failure_category is not None
        ),
    }


def _normalize_whitespace(value: str) -> str:
    """归一化空白字符。

    Args:
        value: 原始文本。

    Returns:
        压缩空白后的文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"\s+", " ", value).strip()


def _parse_args() -> argparse.Namespace:
    """解析 CLI 参数。

    Args:
        无。

    Returns:
        argparse namespace。

    Raises:
        SystemExit: 参数解析失败时由 argparse 抛出。
    """

    parser = argparse.ArgumentParser(description="Run EC-P2 authorized live sample.")
    parser.add_argument("--fund-code", required=True)
    parser.add_argument("--report-year", required=True, type=int)
    parser.add_argument("--force-refresh", action="store_true")
    return parser.parse_args()


def _reject_payload(reason: str) -> dict[str, object]:
    """构造安全拒绝 payload。

    Args:
        reason: 拒绝原因码。

    Returns:
        JSON 兼容 payload。

    Raises:
        无显式抛出。
    """

    return {
        "sample": f"{AUTHORIZED_FUND_CODE}/{AUTHORIZED_REPORT_YEAR}",
        "status": "fail",
        "reason": reason,
        "projection_kind": PROJECTION_KIND,
        "field_correctness_proven": False,
    }


async def _main_async() -> int:
    """执行 CLI 主流程。

    Args:
        无。

    Returns:
        进程退出码。

    Raises:
        无显式抛出。
    """

    args = _parse_args()
    if args.fund_code != AUTHORIZED_FUND_CODE or args.report_year != AUTHORIZED_REPORT_YEAR:
        print(json.dumps(_reject_payload("unauthorized_sample"), ensure_ascii=False, sort_keys=True))
        return 2
    try:
        payload = await run_authorized_sample(force_refresh=args.force_refresh)
    except LiveProjectionUnavailableError as exc:
        print(json.dumps(_reject_payload(str(exc)), ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def main() -> int:
    """同步 CLI 入口。

    Args:
        无。

    Returns:
        进程退出码。

    Raises:
        无显式抛出。
    """

    return asyncio.run(_main_async())


if __name__ == "__main__":
    raise SystemExit(main())
