"""FundDisclosureDocument candidate source failure 映射。

本模块只把 candidate-internal source failure code 映射到当前五类年报来源失败分类。
projection blocker 不是来源失败，必须 fail-closed，不能进入生产 fallback 语义。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, get_args

from fund_agent.fund.documents.models import AnnualReportSourceFailureCategory

FundDisclosureCandidateSourceFailureCode = Literal[
    "index_unavailable",
    "list_row_missing",
    "identity_mismatch",
    "redirect_unavailable",
    "render_unavailable",
    "render_domain_mismatch",
    "render_structure_missing",
    "locator_unstable",
]
FundDisclosureProjectionBlocker = Literal[
    "value_unvalidated",
    "raw_xml_not_proven",
]
FundDisclosureCandidateFailureCode = (
    FundDisclosureCandidateSourceFailureCode | FundDisclosureProjectionBlocker
)

SOURCE_FAILURE_CODES: tuple[FundDisclosureCandidateSourceFailureCode, ...] = get_args(
    FundDisclosureCandidateSourceFailureCode
)
PROJECTION_BLOCKERS: tuple[FundDisclosureProjectionBlocker, ...] = get_args(
    FundDisclosureProjectionBlocker
)

_OFFICIAL_EID_DOMAINS = frozenset(
    (
        "eid.csrc.gov.cn",
        "eidfile.csrc.gov.cn",
    )
)


@dataclass(frozen=True, slots=True)
class FundDisclosureFailureContext:
    """FundDisclosureDocument source failure 映射上下文。

    Args:
        无。

    Attributes:
        http_status: HTTP 状态码；无响应或不可判定时为 ``None``。
        error_type: 连接层错误类型，如 ``timeout``、``dns``、``tls``。
        redirect_target_url: redirect 目标 URL，仅用于诊断。
        redirect_domain: redirect 目标域名。
        official_domain_status: 官方域名状态，仅用于诊断。
        render_url_known: render URL 是否已知。
        body_empty: render body 是否为空。
        body_is_html: render body 是否为 HTML。
        navigation_present: navigation 是否存在。
        sections_present: sections 是否存在。
        retry_count: 已重试次数。
        structure_absence_observed_consistently: 结构缺失是否跨重试稳定复现。

    Raises:
        无显式抛出。
    """

    http_status: int | None = None
    error_type: str | None = None
    redirect_target_url: str | None = None
    redirect_domain: str | None = None
    official_domain_status: str | None = None
    render_url_known: bool = False
    body_empty: bool = False
    body_is_html: bool = True
    navigation_present: bool | None = None
    sections_present: bool | None = None
    retry_count: int = 0
    structure_absence_observed_consistently: bool = False


def map_fund_disclosure_failure_to_source_category(
    failure_code: FundDisclosureCandidateSourceFailureCode,
    context: FundDisclosureFailureContext | None = None,
) -> AnnualReportSourceFailureCategory:
    """把 FundDisclosureDocument candidate source failure 映射到五类来源失败分类。

    Args:
        failure_code: candidate-internal source failure code。
        context: redirect/render split rule 需要的 typed context。

    Returns:
        当前生产年报来源契约中的 canonical failure category。

    Raises:
        ValueError: projection blocker 或未知 code 被传入时抛出。
    """

    if failure_code in PROJECTION_BLOCKERS:
        raise ValueError(f"projection blocker 不能映射为来源失败分类：{failure_code}")
    if failure_code not in SOURCE_FAILURE_CODES:
        raise ValueError(f"未知 FundDisclosureDocument failure code：{failure_code}")

    if failure_code == "index_unavailable":
        return "unavailable"
    if failure_code == "list_row_missing":
        return "not_found"
    if failure_code == "identity_mismatch":
        return "identity_mismatch"
    if failure_code == "redirect_unavailable":
        return _map_redirect_unavailable(context or FundDisclosureFailureContext())
    if failure_code == "render_unavailable":
        return _map_render_unavailable(context or FundDisclosureFailureContext())
    if failure_code == "render_domain_mismatch":
        return "identity_mismatch"
    if failure_code == "render_structure_missing":
        return "schema_drift"
    if failure_code == "locator_unstable":
        return "schema_drift"
    raise ValueError(f"未覆盖 FundDisclosureDocument failure code：{failure_code}")


def mapped_fund_disclosure_source_failure_codes() -> frozenset[str]:
    """返回当前已映射的 FundDisclosureDocument source failure code 集合。

    Args:
        无。

    Returns:
        source failure code 字符串集合。

    Raises:
        无显式抛出。
    """

    return frozenset(SOURCE_FAILURE_CODES)


def _map_redirect_unavailable(
    context: FundDisclosureFailureContext,
) -> AnnualReportSourceFailureCategory:
    """执行 redirect_unavailable 的总有序决策表。

    Args:
        context: failure context。

    Returns:
        canonical failure category。

    Raises:
        无显式抛出。
    """

    if context.redirect_domain is not None and context.redirect_domain not in _OFFICIAL_EID_DOMAINS:
        return "identity_mismatch"
    if _is_temporary_infrastructure_failure(context):
        return "unavailable"
    if _is_not_found_status(context.http_status):
        return "not_found"
    return "unavailable"


def _map_render_unavailable(
    context: FundDisclosureFailureContext,
) -> AnnualReportSourceFailureCategory:
    """执行 render_unavailable 的总有序决策表。

    Args:
        context: failure context。

    Returns:
        canonical failure category。

    Raises:
        无显式抛出。
    """

    if context.http_status == 200 and context.body_empty:
        return "schema_drift"
    if context.http_status == 200 and not context.body_is_html:
        return "schema_drift"
    if (
        context.http_status == 200
        and context.body_is_html
        and context.structure_absence_observed_consistently
    ):
        return "schema_drift"
    if _is_temporary_infrastructure_failure(context):
        return "unavailable"
    if context.render_url_known and _is_not_found_status(context.http_status):
        return "not_found"
    return "unavailable"


def _is_temporary_infrastructure_failure(context: FundDisclosureFailureContext) -> bool:
    """判断上下文是否表示临时基础设施失败。

    Args:
        context: failure context。

    Returns:
        5xx、timeout、DNS 或 TLS 错误返回 ``True``。

    Raises:
        无显式抛出。
    """

    if context.http_status is not None and 500 <= context.http_status <= 599:
        return True
    return context.error_type in {"timeout", "dns", "tls"}


def _is_not_found_status(http_status: int | None) -> bool:
    """判断 HTTP 状态是否是当前 gate 认可的 gone/not-found。

    Args:
        http_status: HTTP 状态码。

    Returns:
        404 或 410 返回 ``True``。

    Raises:
        无显式抛出。
    """

    return http_status in {404, 410}
