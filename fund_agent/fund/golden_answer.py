"""Correctness golden answer Markdown 转 JSON、strict JSON 读取与校验能力。

本模块属于 Capability 层，只处理人工审核后的 golden answer Markdown
结构化、strict JSON 读取与校验，不读取 PDF、cache 或底层解析文件，也不执行
correctness 评分。Correctness 比对见 `extraction_score.py`，对应模板字段质量
闭环。
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

DEFAULT_GOLDEN_REVIEWED_MARKDOWN: Final[Path] = Path(
    "reports/golden-answers/golden-answer-prefill.md"
)
DEFAULT_GOLDEN_ANSWER_JSON: Final[Path] = Path("reports/golden-answers/golden-answer.json")
GOLDEN_ANSWER_SCHEMA_VERSION: Final[str] = "fund-agent.golden-answer.v1"
_FUND_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^##\s+(?P<code>\d{6})\s+(?P<title>.+?)\s*$"
)
_ALLOWED_CONFIDENCE: Final[frozenset[str]] = frozenset({"high", "medium", "low"})
_SKIPPED_CELL: Final[str] = "—"


@dataclass(frozen=True, slots=True)
class GoldenAnswerRecord:
    """单条 correctness golden answer 真值记录。

    Attributes:
        fund_code: 基金代码。
        field_name: snapshot / extractor 字段名。
        sub_field: 字段内部子键。
        expected_value: 人工审核后的期望值。
        confidence: 人工标注置信度，取值为 `high / medium / low`。
        source: 人工确认的数据来源。
    """

    fund_code: str
    field_name: str
    sub_field: str
    expected_value: str
    confidence: str
    source: str


@dataclass(frozen=True, slots=True)
class GoldenAnswerFund:
    """单只基金的 golden answer 汇总。

    Attributes:
        fund_code: 基金代码。
        title: Markdown 二级标题中的基金名称与类别文本。
        records: 该基金的有效真值记录。
        skipped_fields: 模板中明确跳过的字段标识。
    """

    fund_code: str
    title: str
    records: tuple[GoldenAnswerRecord, ...]
    skipped_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GoldenAnswerBuildResult:
    """golden answer JSON 构建结果。

    Attributes:
        input_path: 输入 Markdown 路径。
        output_path: 输出 JSON 路径。
        fund_count: 基金数量。
        record_count: 有效真值记录数量。
        skipped_count: 跳过字段数量。
    """

    input_path: Path
    output_path: Path
    fund_count: int
    record_count: int
    skipped_count: int


class GoldenAnswerValidationError(ValueError):
    """golden answer Markdown 校验失败。

    Attributes:
        errors: 校验错误列表，每条包含具体基金和字段上下文。
    """

    def __init__(self, errors: tuple[str, ...]) -> None:
        """初始化校验异常。

        Args:
            errors: 校验错误列表。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.errors = errors
        super().__init__("\n".join(errors))


@dataclass(frozen=True, slots=True)
class _ParsedFund:
    """Markdown 中解析出的单只基金中间结构。"""

    fund_code: str
    title: str
    records: tuple[GoldenAnswerRecord, ...]
    skipped_fields: tuple[str, ...]
    errors: tuple[str, ...]


def build_golden_answer_json(
    *,
    input_path: Path = DEFAULT_GOLDEN_REVIEWED_MARKDOWN,
    output_path: Path = DEFAULT_GOLDEN_ANSWER_JSON,
) -> GoldenAnswerBuildResult:
    """把人工审核后的 Markdown 转换为 strict golden answer JSON。

    Args:
        input_path: 人工审核后的 Markdown 路径。
        output_path: 输出 JSON 路径。

    Returns:
        JSON 构建结果。

    Raises:
        FileNotFoundError: 输入 Markdown 不存在时抛出。
        GoldenAnswerValidationError: Markdown 内容未通过 strict 校验时抛出。
        OSError: 输出 JSON 写入失败时抛出。
    """

    markdown_text = input_path.read_text(encoding="utf-8")
    funds = parse_golden_answer_markdown(markdown_text)
    payload = _json_payload(input_path=input_path, funds=funds)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return GoldenAnswerBuildResult(
        input_path=input_path,
        output_path=output_path,
        fund_count=len(funds),
        record_count=sum(len(fund.records) for fund in funds),
        skipped_count=sum(len(fund.skipped_fields) for fund in funds),
    )


def load_golden_answer_json(golden_answer_path: Path) -> tuple[GoldenAnswerFund, ...]:
    """读取并校验 strict golden answer JSON。

    Args:
        golden_answer_path: `golden-build` 产出的 strict JSON 路径。

    Returns:
        golden answer 基金记录元组。

    Raises:
        FileNotFoundError: JSON 文件不存在时抛出。
        GoldenAnswerValidationError: JSON schema、字段类型或行内容非法时抛出。
        json.JSONDecodeError: JSON 内容非法时抛出。
    """

    payload = json.loads(golden_answer_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise GoldenAnswerValidationError(("golden answer JSON 顶层必须是 object",))
    errors: list[str] = []
    schema_version = payload.get("schema_version")
    if schema_version != GOLDEN_ANSWER_SCHEMA_VERSION:
        errors.append(f"schema_version 必须是 {GOLDEN_ANSWER_SCHEMA_VERSION}")
    raw_funds = payload.get("funds")
    if not isinstance(raw_funds, list):
        errors.append("funds 必须是 JSON array")
        raw_funds = []

    funds: list[GoldenAnswerFund] = []
    seen_keys: set[tuple[str, str, str]] = set()
    for fund_index, raw_fund in enumerate(raw_funds):
        if not isinstance(raw_fund, dict):
            errors.append(f"funds[{fund_index}] 必须是 JSON object")
            continue
        parsed_fund, fund_errors = _parse_golden_answer_json_fund(raw_fund, fund_index, seen_keys)
        errors.extend(fund_errors)
        if parsed_fund is not None:
            funds.append(parsed_fund)
    if errors:
        raise GoldenAnswerValidationError(tuple(errors))
    if not funds:
        raise GoldenAnswerValidationError(("golden answer JSON 至少需要 1 只基金",))
    return tuple(funds)


def parse_golden_answer_markdown(markdown_text: str) -> tuple[GoldenAnswerFund, ...]:
    """解析并校验 golden answer Markdown。

    Args:
        markdown_text: 人工审核后的 Markdown 全文。

    Returns:
        校验通过后的基金记录。

    Raises:
        GoldenAnswerValidationError: 发现空 expected value、非法 confidence、
            缺失 source、重复字段或缺少基金标题时抛出。
    """

    parsed_funds: list[_ParsedFund] = []
    current_code: str | None = None
    current_title = ""
    current_records: list[GoldenAnswerRecord] = []
    current_skipped: list[str] = []
    current_errors: list[str] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for line_number, line in enumerate(markdown_text.splitlines(), start=1):
        heading_match = _FUND_HEADING_PATTERN.match(line)
        if heading_match is not None:
            _append_current_fund(
                parsed_funds,
                current_code,
                current_title,
                current_records,
                current_skipped,
                current_errors,
            )
            current_code = heading_match.group("code")
            current_title = heading_match.group("title")
            current_records = []
            current_skipped = []
            current_errors = []
            seen_keys = set()
            continue
        if current_code is None or not line.startswith("|"):
            continue
        row = _parse_table_row(line)
        if row is None:
            continue
        if len(row) != 5:
            current_errors.append(
                f"line {line_number} fund {current_code}: Markdown 表格必须为 5 列"
            )
            continue
        field, sub_field, expected_value, confidence, source = (cell.strip() for cell in row)
        if _is_header_or_separator(field, sub_field):
            continue
        if _is_skipped_row(sub_field, expected_value):
            current_skipped.append(_skipped_field_label(field, sub_field))
            continue
        key = (current_code, field, sub_field)
        row_context = f"line {line_number} fund {current_code} {field}.{sub_field}"
        if key in seen_keys:
            current_errors.append(f"{row_context}: 重复 golden answer 行")
            continue
        seen_keys.add(key)
        row_errors = _validate_active_row(
            row_context, field, sub_field, expected_value, confidence, source
        )
        if row_errors:
            current_errors.extend(row_errors)
            continue
        current_records.append(
            GoldenAnswerRecord(
                fund_code=current_code,
                field_name=field,
                sub_field=sub_field,
                expected_value=_unescape_markdown_cell(expected_value),
                confidence=confidence,
                source=_unescape_markdown_cell(source),
            )
        )

    _append_current_fund(
        parsed_funds,
        current_code,
        current_title,
        current_records,
        current_skipped,
        current_errors,
    )
    if not parsed_funds:
        raise GoldenAnswerValidationError(("未找到任何 `## 000000 基金名称` 格式的基金标题",))

    errors: list[str] = []
    funds: list[GoldenAnswerFund] = []
    for parsed_fund in parsed_funds:
        errors.extend(parsed_fund.errors)
        if not parsed_fund.records:
            errors.append(f"fund {parsed_fund.fund_code}: 至少需要 1 条有效 golden answer 行")
        funds.append(
            GoldenAnswerFund(
                fund_code=parsed_fund.fund_code,
                title=parsed_fund.title,
                records=parsed_fund.records,
                skipped_fields=parsed_fund.skipped_fields,
            )
        )
    if errors:
        raise GoldenAnswerValidationError(tuple(errors))
    return tuple(funds)


def _parse_golden_answer_json_fund(
    raw_fund: dict[str, object],
    fund_index: int,
    seen_keys: set[tuple[str, str, str]],
) -> tuple[GoldenAnswerFund | None, tuple[str, ...]]:
    """解析 strict JSON 中的单只基金。

    Args:
        raw_fund: JSON 中的基金对象。
        fund_index: 基金数组下标。
        seen_keys: 全局已见 `(fund_code, field_name, sub_field)` 集合。

    Returns:
        解析后的基金对象；如果阻断字段非法则返回 `None` 和错误列表。

    Raises:
        无显式抛出。
    """

    errors: list[str] = []
    fund_code = _json_required_text(raw_fund, "fund_code", f"funds[{fund_index}]", errors)
    title = _json_required_text(raw_fund, "title", f"funds[{fund_index}]", errors)
    raw_records = raw_fund.get("records")
    if not isinstance(raw_records, list):
        errors.append(f"funds[{fund_index}].records 必须是 JSON array")
        raw_records = []
    raw_skipped = raw_fund.get("skipped_fields", [])
    if not isinstance(raw_skipped, list) or any(not isinstance(item, str) for item in raw_skipped):
        errors.append(f"funds[{fund_index}].skipped_fields 必须是字符串数组")
        raw_skipped = []

    records: list[GoldenAnswerRecord] = []
    if fund_code:
        for record_index, raw_record in enumerate(raw_records):
            context = f"funds[{fund_index}].records[{record_index}]"
            if not isinstance(raw_record, dict):
                errors.append(f"{context} 必须是 JSON object")
                continue
            parsed_record, record_errors = _parse_golden_answer_json_record(
                raw_record, context, fund_code, seen_keys
            )
            errors.extend(record_errors)
            if parsed_record is not None:
                records.append(parsed_record)
    if fund_code and not records:
        errors.append(f"fund {fund_code}: 至少需要 1 条有效 golden answer 行")
    if errors or not fund_code or not title:
        return None, tuple(errors)
    return (
        GoldenAnswerFund(
            fund_code=fund_code,
            title=title,
            records=tuple(records),
            skipped_fields=tuple(str(item) for item in raw_skipped),
        ),
        tuple(errors),
    )


def _parse_golden_answer_json_record(
    raw_record: dict[str, object],
    context: str,
    fund_code: str,
    seen_keys: set[tuple[str, str, str]],
) -> tuple[GoldenAnswerRecord | None, tuple[str, ...]]:
    """解析 strict JSON 中的单条 golden answer 记录。

    Args:
        raw_record: JSON 中的记录对象。
        context: 错误上下文。
        fund_code: 所属基金代码。
        seen_keys: 全局已见键集合。

    Returns:
        解析后的记录；字段非法时返回 `None` 和错误列表。

    Raises:
        无显式抛出。
    """

    errors: list[str] = []
    record_fund_code = _json_required_text(raw_record, "fund_code", context, errors)
    field_name = _json_required_text(raw_record, "field_name", context, errors)
    sub_field = _json_required_text(raw_record, "sub_field", context, errors)
    expected_value = _json_required_text(raw_record, "expected_value", context, errors)
    confidence = _json_required_text(raw_record, "confidence", context, errors)
    source = _json_required_text(raw_record, "source", context, errors)
    if record_fund_code and record_fund_code != fund_code:
        errors.append(f"{context}.fund_code 必须等于所属基金 {fund_code}")
    if confidence and confidence not in _ALLOWED_CONFIDENCE:
        errors.append(f"{context}.confidence 必须是 high / medium / low")
    if source in {_SKIPPED_CELL, "manual_required"}:
        errors.append(f"{context}.source 必须填写可复核来源，不能是 manual_required")
    key = (fund_code, field_name, sub_field)
    if all(key) and key in seen_keys:
        errors.append(f"{context}: 重复 golden answer 行 {fund_code} {field_name}.{sub_field}")
    elif all(key):
        seen_keys.add(key)
    if errors:
        return None, tuple(errors)
    return (
        GoldenAnswerRecord(
            fund_code=fund_code,
            field_name=field_name,
            sub_field=sub_field,
            expected_value=expected_value,
            confidence=confidence,
            source=source,
        ),
        tuple(errors),
    )


def _json_required_text(
    raw_object: dict[str, object],
    key: str,
    context: str,
    errors: list[str],
) -> str:
    """读取 strict JSON object 中的必需文本字段。

    Args:
        raw_object: JSON object。
        key: 字段名。
        context: 错误上下文。
        errors: 错误列表，会被原地追加。

    Returns:
        去空格后的文本；缺失或非法时返回空字符串。

    Raises:
        无显式抛出。
    """

    value = raw_object.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{key} 必须是非空字符串")
        return ""
    return value.strip()


def _append_current_fund(
    parsed_funds: list[_ParsedFund],
    fund_code: str | None,
    title: str,
    records: list[GoldenAnswerRecord],
    skipped_fields: list[str],
    errors: list[str],
) -> None:
    """把当前基金中间结果加入列表。

    Args:
        parsed_funds: 结果列表。
        fund_code: 当前基金代码。
        title: 当前基金标题。
        records: 有效记录列表。
        skipped_fields: 跳过字段列表。
        errors: 当前基金错误列表。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    if fund_code is None:
        return
    parsed_funds.append(
        _ParsedFund(
            fund_code=fund_code,
            title=title,
            records=tuple(records),
            skipped_fields=tuple(skipped_fields),
            errors=tuple(errors),
        )
    )


def _parse_table_row(line: str) -> tuple[str, ...] | None:
    """解析 Markdown 表格行，支持转义竖线。

    Args:
        line: Markdown 表格行。

    Returns:
        单元格元组；非表格行返回 `None`。

    Raises:
        无显式抛出。
    """

    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in stripped[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            current.append(char)
            continue
        if char == "|":
            cells.append("".join(current))
            current = []
            continue
        current.append(char)
    cells.append("".join(current))
    return tuple(cells)


def _is_header_or_separator(field: str, sub_field: str) -> bool:
    """判断表格行是否为表头或分隔行。

    Args:
        field: 第一列。
        sub_field: 第二列。

    Returns:
        表头或分隔行返回 `True`。

    Raises:
        无显式抛出。
    """

    return field in {"field", "---"} or sub_field == "---"


def _is_skipped_row(sub_field: str, expected_value: str) -> bool:
    """判断表格行是否为明确跳过项。

    Args:
        sub_field: 子字段列。
        expected_value: 期望值列。

    Returns:
        模板跳过行返回 `True`。

    Raises:
        无显式抛出。
    """

    return sub_field == _SKIPPED_CELL or expected_value == _SKIPPED_CELL


def _skipped_field_label(field: str, sub_field: str) -> str:
    """构造跳过字段标签。

    Args:
        field: 字段名。
        sub_field: 子字段名。

    Returns:
        可读跳过字段标签。

    Raises:
        无显式抛出。
    """

    return field if sub_field == _SKIPPED_CELL else f"{field}.{sub_field}"


def _validate_active_row(
    row_context: str,
    field: str,
    sub_field: str,
    expected_value: str,
    confidence: str,
    source: str,
) -> tuple[str, ...]:
    """校验有效 golden answer 行。

    Args:
        row_context: 错误上下文。
        field: 字段名。
        sub_field: 子字段名。
        expected_value: 期望值。
        confidence: 置信度。
        source: 来源。

    Returns:
        错误列表；为空表示通过。

    Raises:
        无显式抛出。
    """

    errors: list[str] = []
    if not field:
        errors.append(f"{row_context}: field 不能为空")
    if not sub_field:
        errors.append(f"{row_context}: sub_field 不能为空")
    if not expected_value:
        errors.append(f"{row_context}: expected_value 不能为空")
    normalized_confidence = confidence.lower()
    if normalized_confidence not in _ALLOWED_CONFIDENCE:
        errors.append(f"{row_context}: confidence 必须是 high / medium / low")
    if not source or source in {_SKIPPED_CELL, "manual_required"}:
        errors.append(f"{row_context}: source 必须填写可复核来源，不能是 manual_required")
    return tuple(errors)


def _unescape_markdown_cell(value: str) -> str:
    """还原 Markdown 表格单元格转义。

    Args:
        value: 原始单元格值。

    Returns:
        还原后的文本。

    Raises:
        无显式抛出。
    """

    return value.replace("\\|", "|").strip()


def _json_payload(input_path: Path, funds: tuple[GoldenAnswerFund, ...]) -> dict[str, object]:
    """构造 golden answer JSON payload。

    Args:
        input_path: 输入 Markdown 路径。
        funds: 已校验基金记录。

    Returns:
        可序列化 JSON payload。

    Raises:
        无显式抛出。
    """

    flat_records = [asdict(record) for fund in funds for record in fund.records]
    return {
        "schema_version": GOLDEN_ANSWER_SCHEMA_VERSION,
        "source_markdown": str(input_path),
        "fund_count": len(funds),
        "record_count": len(flat_records),
        "funds": [
            {
                "fund_code": fund.fund_code,
                "title": fund.title,
                "records": [asdict(record) for record in fund.records],
                "skipped_fields": list(fund.skipped_fields),
            }
            for fund in funds
        ],
        "records": flat_records,
    }
