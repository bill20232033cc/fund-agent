"""Correctness golden answer 预填底稿生成能力。

本模块位于 Capability 层，只负责把模板中的基金与字段行转换为可人工复核的
silver label 底稿。预填值来自 `FundDataExtractor`，不能直接作为最终
correctness golden answer 使用。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Protocol

from fund_agent.config.paths import DEFAULT_GOLDEN_PREFILL_OUTPUT, DEFAULT_GOLDEN_TEMPLATE_PATH
from fund_agent.fund._value_utils import value_mapping
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.extractors import EvidenceAnchor, ExtractedField

_FUND_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^##\s+(?P<code>\d{6})\s+.+$")
_TABLE_ROW_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\|\s*(?P<field>[^|]+?)\s*\|\s*(?P<sub_field>[^|]+?)\s*\|")
_GOLDEN_PREFILL_NOTICE: Final[str] = (
    "> 说明：本文件为自动预填底稿，值来自当前 extractor 输出，只能用于人工复核；"
    "不能直接作为 correctness golden answer。"
)
_SKIPPED_CELL: Final[str] = "—"
_SUB_FIELD_ALIASES: Final[dict[tuple[str, str], str]] = {
    ("benchmark", "benchmark_name"): "benchmark_text",
}


class GoldenPrefillExtractor(Protocol):
    """golden prefill 依赖的结构化抽取协议。"""

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
            force_refresh: 是否强制刷新统一文档仓库和净值缓存。

        Returns:
            结构化基金数据包。

        Raises:
            Exception: 允许底层 extractor 异常向上传播。
        """


@dataclass(frozen=True, slots=True)
class GoldenPrefillResult:
    """golden answer 预填运行结果。

    Attributes:
        template_path: 输入模板路径。
        output_path: 输出预填 Markdown 路径。
        report_year: 年报年份。
        fund_codes: 已尝试预填的基金代码。
        succeeded_fund_codes: 成功预填的基金代码。
        failed_fund_codes: 预填失败的基金代码。
    """

    template_path: Path
    output_path: Path
    report_year: int
    fund_codes: tuple[str, ...]
    succeeded_fund_codes: tuple[str, ...]
    failed_fund_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _PrefillContext:
    """单只基金的预填上下文。"""

    bundle: StructuredFundDataBundle | None
    error_message: str | None


@dataclass(frozen=True, slots=True)
class _PrefillValue:
    """单个 golden answer 单元格预填结果。"""

    expected_value: str
    confidence: str
    source: str


async def run_golden_prefill(
    *,
    template_path: Path = DEFAULT_GOLDEN_TEMPLATE_PATH,
    output_path: Path = DEFAULT_GOLDEN_PREFILL_OUTPUT,
    report_year: int = 2024,
    force_refresh: bool = False,
    extractor: GoldenPrefillExtractor | None = None,
) -> GoldenPrefillResult:
    """按模板生成 correctness golden answer 预填底稿。

    Args:
        template_path: golden answer Markdown 模板路径。
        output_path: 预填底稿输出路径。
        report_year: 年报年份。
        force_refresh: 是否强制刷新统一文档仓库和净值缓存。
        extractor: 结构化抽取器；未提供时使用 `FundDataExtractor`。

    Returns:
        预填运行结果。

    Raises:
        FileNotFoundError: 模板不存在时抛出。
        ValueError: 年报年份非法或模板中没有基金代码时抛出。
        OSError: 输出文件写入失败时抛出。
    """

    if report_year <= 0:
        raise ValueError("report_year 必须为正整数")
    template_text = template_path.read_text(encoding="utf-8")
    fund_codes = _extract_fund_codes(template_text)
    if not fund_codes:
        raise ValueError("模板中未找到 6 位基金代码标题")

    selected_extractor = extractor or FundDataExtractor()
    contexts: dict[str, _PrefillContext] = {}
    succeeded_codes: list[str] = []
    failed_codes: list[str] = []
    for fund_code in fund_codes:
        try:
            bundle = await selected_extractor.extract(
                fund_code,
                report_year,
                force_refresh=force_refresh,
            )
        except Exception as exc:  # noqa: BLE001 - 预填底稿需要逐只基金保留失败信息。
            contexts[fund_code] = _PrefillContext(bundle=None, error_message=f"{type(exc).__name__}: {exc}")
            failed_codes.append(fund_code)
            continue
        contexts[fund_code] = _PrefillContext(bundle=bundle, error_message=None)
        succeeded_codes.append(fund_code)

    output_text = _prefill_template(template_text, contexts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    return GoldenPrefillResult(
        template_path=template_path,
        output_path=output_path,
        report_year=report_year,
        fund_codes=fund_codes,
        succeeded_fund_codes=tuple(succeeded_codes),
        failed_fund_codes=tuple(failed_codes),
    )


def _extract_fund_codes(template_text: str) -> tuple[str, ...]:
    """从模板二级标题中提取基金代码。

    Args:
        template_text: golden answer Markdown 模板全文。

    Returns:
        按模板顺序去重后的基金代码。

    Raises:
        无显式抛出。
    """

    fund_codes: list[str] = []
    for line in template_text.splitlines():
        match = _FUND_HEADING_PATTERN.match(line)
        if match is None:
            continue
        fund_code = match.group("code")
        if fund_code not in fund_codes:
            fund_codes.append(fund_code)
    return tuple(fund_codes)


def _prefill_template(template_text: str, contexts: dict[str, _PrefillContext]) -> str:
    """把模板中的表格行替换为预填行。

    Args:
        template_text: golden answer Markdown 模板全文。
        contexts: 基金代码到预填上下文的映射。

    Returns:
        已预填的 Markdown 文本。

    Raises:
        无显式抛出。
    """

    output_lines: list[str] = []
    current_fund_code: str | None = None
    notice_inserted = False
    for line in template_text.splitlines():
        if not notice_inserted and line.startswith("## "):
            output_lines.append(_GOLDEN_PREFILL_NOTICE)
            output_lines.append("")
            notice_inserted = True
        heading_match = _FUND_HEADING_PATTERN.match(line)
        if heading_match is not None:
            current_fund_code = heading_match.group("code")
            output_lines.append(line)
            context = contexts.get(current_fund_code)
            if context is not None and context.error_message is not None:
                output_lines.append("")
                output_lines.append(f"> 预填失败：`{context.error_message}`")
            continue
        output_lines.append(_prefill_line(line, current_fund_code, contexts))
    return "\n".join(output_lines) + "\n"


def _prefill_line(line: str, fund_code: str | None, contexts: dict[str, _PrefillContext]) -> str:
    """预填单行 Markdown 表格。

    Args:
        line: 原始 Markdown 行。
        fund_code: 当前基金代码。
        contexts: 基金代码到预填上下文的映射。

    Returns:
        替换后的 Markdown 行。

    Raises:
        无显式抛出。
    """

    if fund_code is None or not line.startswith("|"):
        return line
    row_match = _TABLE_ROW_PATTERN.match(line)
    if row_match is None:
        return line
    field = row_match.group("field").strip()
    sub_field = row_match.group("sub_field").strip()
    if field in {"field", "---"} or sub_field == _SKIPPED_CELL:
        return line
    context = contexts.get(fund_code)
    if context is None or context.bundle is None:
        return line
    prefill_value = _resolve_prefill_value(context.bundle, field, sub_field)
    if prefill_value is None:
        return line
    return (
        f"| {field} | {sub_field} | {_escape_markdown_cell(prefill_value.expected_value)} | "
        f"{prefill_value.confidence} | {_escape_markdown_cell(prefill_value.source)} |"
    )


def _resolve_prefill_value(bundle: StructuredFundDataBundle, field: str, sub_field: str) -> _PrefillValue | None:
    """从结构化数据包解析单个模板字段的预填值。

    Args:
        bundle: 结构化基金数据包。
        field: 模板字段名。
        sub_field: 模板子字段名。

    Returns:
        可预填时返回单元格值；缺失或无法映射时返回 `None`。

    Raises:
        无显式抛出。
    """

    extracted_field = _field_from_bundle(bundle, field)
    if extracted_field is None:
        return None
    raw_value = _sub_field_value(extracted_field, field, sub_field)
    if raw_value is None:
        return None
    source = _source_from_anchor(_anchor_for_sub_field(extracted_field, sub_field))
    confidence = _confidence_for_value(extracted_field, raw_value, source)
    return _PrefillValue(expected_value=str(raw_value), confidence=confidence, source=source)


def _field_from_bundle(
    bundle: StructuredFundDataBundle,
    field: str,
) -> ExtractedField[object] | None:
    """按模板字段名读取结构化字段。

    Args:
        bundle: 结构化基金数据包。
        field: 模板字段名。

    Returns:
        对应 `ExtractedField`；无法映射时返回 `None`。

    Raises:
        无显式抛出。
    """

    if field == "classified_fund_type":
        return bundle.basic_identity
    candidate = getattr(bundle, field, None)
    if isinstance(candidate, ExtractedField):
        return candidate
    return None


def _sub_field_value(
    extracted_field: ExtractedField[object],
    field: str,
    sub_field: str,
) -> object | None:
    """从 `ExtractedField.value` 中读取子字段值。

    Args:
        extracted_field: 带证据的字段。
        field: 模板字段名。
        sub_field: 模板子字段名。

    Returns:
        子字段值；缺失、空值或未披露时返回 `None`。

    Raises:
        无显式抛出。
    """

    mapped_value = value_mapping(extracted_field.value)
    if mapped_value is None:
        return None
    if field == "classified_fund_type" and sub_field == "fund_type":
        return mapped_value.get("classified_fund_type")
    value_key = _SUB_FIELD_ALIASES.get((field, sub_field), sub_field)
    value = mapped_value.get(value_key)
    if value in (None, ""):
        return None
    return value


def _anchor_for_sub_field(extracted_field: ExtractedField[object], sub_field: str) -> EvidenceAnchor | None:
    """为子字段选择最贴近的证据锚点。

    Args:
        extracted_field: 带证据的字段。
        sub_field: 模板子字段名。

    Returns:
        row_locator 命中的锚点；不存在时返回首个锚点；完全无锚点时返回 `None`。

    Raises:
        无显式抛出。
    """

    for anchor in extracted_field.anchors:
        if anchor.row_locator == sub_field:
            return anchor
    return extracted_field.anchors[0] if extracted_field.anchors else None


def _source_from_anchor(anchor: EvidenceAnchor | None) -> str:
    """把证据锚点格式化为人工可读 source。

    Args:
        anchor: 证据锚点。

    Returns:
        source 字符串；无锚点时返回 `manual_required`。

    Raises:
        无显式抛出。
    """

    if anchor is None:
        return "manual_required"
    if anchor.source_kind != "annual_report":
        return anchor.source_kind
    parts = [f"年报{anchor.document_year}" if anchor.document_year is not None else "年报"]
    if anchor.section_id is not None:
        parts.append(anchor.section_id)
    if anchor.page_number is not None:
        parts.append(f"page-{anchor.page_number}")
    if anchor.table_id is not None:
        parts.append(anchor.table_id)
    if anchor.row_locator is not None:
        parts.append(anchor.row_locator)
    return " ".join(parts)


def _confidence_for_value(
    extracted_field: ExtractedField[object],
    value: object,
    source: str,
) -> str:
    """根据抽取模式、证据锚点和文本长度给出预填置信度。

    Args:
        extracted_field: 带证据的字段。
        value: 已预填的值。
        source: 格式化后的 source。

    Returns:
        `high / medium / low / manual_required` 之一。

    Raises:
        无显式抛出。
    """

    if source == "manual_required":
        return "manual_required"
    if extracted_field.extraction_mode in {"estimated", "derived"}:
        return "medium"
    if extracted_field.extraction_mode == "missing":
        return "manual_required"
    if len(str(value)) > 120:
        return "medium"
    if "page-" in source:
        return "high"
    return "medium"


def _escape_markdown_cell(value: str) -> str:
    """转义 Markdown 表格单元格中的竖线和换行。

    Args:
        value: 原始单元格文本。

    Returns:
        可写入 Markdown 表格的文本。

    Raises:
        无显式抛出。
    """

    return value.replace("|", "\\|").replace("\n", " ")
