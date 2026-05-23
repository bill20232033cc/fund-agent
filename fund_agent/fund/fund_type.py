"""基金类型识别能力。

本模块只基于年报 `§1/§2` 的稳定披露信息做基金类型识别，
用于满足 P1-S4 “基金类型判断优先于通用抽取输出”的约束。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable

FundType = Literal[
    "index_fund",
    "active_fund",
    "bond_fund",
    "enhanced_index",
    "qdii_fund",
    "fof_fund",
]

_INDEX_IDENTITY_KEYWORDS: Final[tuple[str, ...]] = (
    "指数",
    "ETF",
    "交易型开放式",
    "联接",
)
_INDEX_STRATEGY_KEYWORDS: Final[tuple[str, ...]] = (
    "标的指数",
    "跟踪指数",
    "紧密跟踪标的指数",
    "紧密跟踪指数",
    "复制法",
    "完全复制",
    "抽样复制",
)
_ENHANCED_KEYWORDS: Final[tuple[str, ...]] = ("指数增强", "增强指数", "增强型指数")
_QDII_KEYWORDS: Final[tuple[str, ...]] = ("QDII", "境外")
_FOF_KEYWORDS: Final[tuple[str, ...]] = ("FOF", "基金中基金")
_BOND_KEYWORDS: Final[tuple[str, ...]] = ("债券", "中债")
_ACTIVE_EQUITY_CATEGORY_KEYWORDS: Final[tuple[str, ...]] = ("混合型", "股票型")
_PROFILE_FIELD_PATTERNS: Final[dict[str, tuple[str, ...]]] = {
    "fund_name": (
        r"基金名称\s*[：:]\s*(.+)",
        r"基金简称\s*[：:]\s*(.+)",
    ),
    "fund_category": (
        r"基金类别\s*[：:]\s*(.+)",
        r"基金类型\s*[：:]\s*(.+)",
    ),
    "benchmark": (
        r"业绩比较基准\s*[：:]\s*(.+)",
    ),
    "investment_scope": (
        r"投资范围\s*[：:]\s*(.+)",
    ),
    "investment_objective": (
        r"投资目标\s*[：:]\s*(.+)",
    ),
    "investment_strategy": (
        r"投资策略\s*[：:]\s*(.+)",
    ),
}
_PROFILE_TABLE_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "fund_name": ("基金简称", "基金名称"),
    "fund_category": ("基金类型", "基金类别"),
    "benchmark": ("业绩比较基准",),
    "investment_scope": ("投资范围",),
    "investment_objective": ("投资目标",),
    "investment_strategy": ("投资策略",),
}


@dataclass(frozen=True, slots=True)
class FundTypeClassification:
    """基金类型识别结果。

    Attributes:
        classified_fund_type: 标准化基金类型标签。
        classification_basis: 触发当前分类结论的依据说明。
    """

    classified_fund_type: FundType
    classification_basis: tuple[str, ...]


def _extract_profile_value(report: ParsedAnnualReport, field_name: str) -> str | None:
    """从 `§1/§2` 中提取基金类型识别所需的基础字段。

    Args:
        report: 已解析年报对象。
        field_name: 待提取字段名。

    Returns:
        命中时返回字段值，否则返回 `None`。

    Raises:
        KeyError: 请求未知字段时抛出。
    """

    patterns = _PROFILE_FIELD_PATTERNS[field_name]
    for section_id in ("§1", "§2"):
        section_text = report.get_section_text(section_id)
        if not section_text:
            continue
        for line in section_text.splitlines():
            normalized_line = line.strip()
            for pattern in patterns:
                match = re.match(pattern, normalized_line)
                if match:
                    return match.group(1).strip()
    return _extract_profile_value_from_tables(report, field_name)


def _extract_profile_value_from_tables(report: ParsedAnnualReport, field_name: str) -> str | None:
    """从 `§2` 键值型表格提取基金类型识别字段。

    Args:
        report: 已解析年报对象。
        field_name: 待提取字段名。

    Returns:
        命中时返回字段值，否则返回 `None`。

    Raises:
        KeyError: 请求未知字段时抛出。
    """

    labels = _PROFILE_TABLE_LABELS[field_name]
    for table in report.tables:
        matched_value = _match_table_value(table, labels)
        if matched_value:
            return matched_value
    return None


def _match_table_value(table: ParsedTable, labels: tuple[str, ...]) -> str | None:
    """在键值型表格中查找字段值。

    Args:
        table: 年报解析出的表格。
        labels: 允许匹配的字段标签。

    Returns:
        命中时返回字段值，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    normalized_labels = tuple(_normalize_table_label(label) for label in labels)
    for normalized_label in normalized_labels:
        for row in _iter_key_value_rows(table):
            cells = tuple(cell.strip() for cell in row)
            for index, cell in enumerate(cells):
                normalized_cell = _normalize_table_label(cell)
                if normalized_cell != normalized_label:
                    continue
                value = _first_non_empty_after(cells, index)
                if value:
                    return value
    return None


def _iter_key_value_rows(table: ParsedTable) -> tuple[tuple[str, ...], ...]:
    """返回可按键值行解释的表头与表格行。

    Args:
        table: 年报解析出的表格。

    Returns:
        先包含表头、再包含数据行的元组，便于处理真实年报中把首个键值对放入表头的情况。

    Raises:
        无显式抛出。
    """

    return (table.headers, *table.rows)


def _first_non_empty_after(cells: tuple[str, ...], start_index: int) -> str | None:
    """读取字段名单元格之后第一个非空值。

    Args:
        cells: 当前表格行的单元格。
        start_index: 字段名单元格下标。

    Returns:
        第一个非空值；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for cell in cells[start_index + 1:]:
        if cell.strip():
            return cell.strip()
    return None


def _normalize_table_label(value: str) -> str:
    """规范化表格字段标签。

    Args:
        value: 原始标签。

    Returns:
        去除空白和常见分隔符后的标签文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"[\s：:]+", "", value)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    """判断文本是否包含任一关键词。

    Args:
        text: 待检测文本。
        keywords: 候选关键词元组。

    Returns:
        命中任一关键词时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    return any(keyword in text for keyword in keywords)


def _has_index_identity_evidence(fund_name: str, fund_category: str, strategy_text: str) -> bool:
    """判断是否存在指数基金身份级证据。

    本函数服务于模板第 1 章“产品本质”与第 2 章 `R=A+B-C` 的前置基金类型判断。
    业绩比较基准只能描述收益参照物，不能单独证明产品是指数基金，因此不参与触发。

    Args:
        fund_name: 基金名称或简称。
        fund_category: 年报披露的基金类别。
        strategy_text: 投资目标、投资范围与投资策略拼接文本。

    Returns:
        存在基金名称/类别/策略层面的指数身份证据时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    identity_text = f"{fund_name} {fund_category}"
    return _contains_any(identity_text, _INDEX_IDENTITY_KEYWORDS) or _contains_any(
        strategy_text,
        _INDEX_STRATEGY_KEYWORDS,
    )


def _build_concurrent_index_basis(
    fund_name: str,
    fund_category: str,
    index_strategy_text: str,
    index_evidence_text: str,
) -> tuple[str, ...]:
    """构造 QDII/FOF 顶层分类下的并发指数身份依据。

    本函数服务于模板第 1 章“产品本质”的前置分类：QDII/FOF 是当前稳定
    `FundType` 的顶层产品类型，但真实产品可能同时具备指数或增强指数身份。
    在不引入复合类型的前提下，将并发证据保留到 `classification_basis`。

    Args:
        fund_name: 基金名称或简称。
        fund_category: 年报披露的基金类别。
        index_strategy_text: 投资目标、投资范围与投资策略拼接文本。
        index_evidence_text: 基金身份与策略拼接后的完整指数证据文本。

    Returns:
        存在指数身份证据时返回依据元组，否则返回空元组。

    Raises:
        无显式抛出。
    """

    if not _has_index_identity_evidence(fund_name, fund_category, index_strategy_text):
        return ()

    basis: tuple[str, ...] = (
        f"同时命中指数基金身份或策略证据：{index_evidence_text}",
    )
    if _contains_any(index_evidence_text, _ENHANCED_KEYWORDS):
        basis = (
            *basis,
            f"同时命中增强关键词：{index_evidence_text}",
        )
    return basis


def classify_fund_type(report: ParsedAnnualReport) -> FundTypeClassification:
    """基于 `§1/§2` 披露信息识别基金类型。

    Args:
        report: 已解析年报对象。

    Returns:
        标准化基金类型与分类依据。

    Raises:
        无显式抛出。
    """

    fund_name = _extract_profile_value(report, "fund_name") or ""
    fund_category = _extract_profile_value(report, "fund_category") or ""
    benchmark = _extract_profile_value(report, "benchmark") or ""
    investment_scope = _extract_profile_value(report, "investment_scope") or ""
    investment_objective = _extract_profile_value(report, "investment_objective") or ""
    investment_strategy = _extract_profile_value(report, "investment_strategy") or ""
    identity_text = f"{fund_name} {fund_category}"
    index_strategy_text = f"{investment_objective} {investment_scope} {investment_strategy}"
    index_evidence_text = f"{identity_text} {index_strategy_text}"
    qdii_fof_text = f"{fund_name} {fund_category} {investment_objective} {investment_scope} {investment_strategy}"

    if _contains_any(qdii_fof_text, _QDII_KEYWORDS):
        return FundTypeClassification(
            classified_fund_type="qdii_fund",
            classification_basis=(
                f"基金类别/名称命中 QDII 关键词：{fund_category or fund_name}",
                *_build_concurrent_index_basis(
                    fund_name,
                    fund_category,
                    index_strategy_text,
                    index_evidence_text,
                ),
            ),
        )

    if _contains_any(qdii_fof_text, _FOF_KEYWORDS):
        return FundTypeClassification(
            classified_fund_type="fof_fund",
            classification_basis=(
                f"基金类别/名称命中 FOF 关键词：{fund_category or fund_name}",
                *_build_concurrent_index_basis(
                    fund_name,
                    fund_category,
                    index_strategy_text,
                    index_evidence_text,
                ),
            ),
        )

    if _contains_any(fund_category, _BOND_KEYWORDS) or _contains_any(fund_name, _BOND_KEYWORDS):
        return FundTypeClassification(
            classified_fund_type="bond_fund",
            classification_basis=(
                f"基金类别或名称命中债券特征：{fund_category or fund_name}",
            ),
        )

    if _has_index_identity_evidence(fund_name, fund_category, index_strategy_text):
        if _contains_any(index_evidence_text, _ENHANCED_KEYWORDS):
            return FundTypeClassification(
                classified_fund_type="enhanced_index",
                classification_basis=(
                    f"基金类别/名称/策略命中指数特征：{fund_category or fund_name}",
                    f"基金身份或策略命中增强关键词：{index_evidence_text}",
                ),
            )
        return FundTypeClassification(
            classified_fund_type="index_fund",
            classification_basis=(
                f"基金类别/名称/策略命中指数特征：{fund_category or fund_name}",
                f"业绩比较基准仅作参照：{benchmark}" if benchmark else "未披露基准，按身份信息识别",
            ),
        )

    if _contains_any(fund_category, _ACTIVE_EQUITY_CATEGORY_KEYWORDS):
        return FundTypeClassification(
            classified_fund_type="active_fund",
            classification_basis=(
                f"基金类别：{fund_category}",
                "基金类别已披露为混合型/股票型，且未命中指数基金身份或策略证据",
            ),
        )

    if _contains_any(investment_scope, _BOND_KEYWORDS) and "股票" not in investment_scope:
        return FundTypeClassification(
            classified_fund_type="bond_fund",
            classification_basis=(
                f"基金类别或投资范围命中债券特征且不含股票：{fund_category or investment_scope}",
            ),
        )

    return FundTypeClassification(
        classified_fund_type="active_fund",
        classification_basis=(
            f"基金类别：{fund_category or '未披露'}",
            "未命中指数/QDII/FOF/债券规则，按主动权益基金处理",
        ),
    )
