"""FundDisclosureDocument candidate-only 内部 schema。

本模块只定义 Fund documents 内部候选文档表示，供后续 Processor/Extractor gate
在受控边界内消费。它不投影 ``EvidenceAnchor``，不替换生产 parser，不改变
``FundDocumentRepository``、Service/UI/Host/renderer 或 quality gate 行为。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal, Self, get_args

from fund_agent.fund.documents.candidates.models import LocatorStability
from fund_agent.fund.documents.models import AnnualReportSourceFailureCategory
from fund_agent.fund.processors.contracts import CandidateBoundaryStatus
from fund_agent.fund.source_provenance import (
    PublicSourceProvenance,
    source_provenance_to_dict,
)

FundDisclosureSourceArtifactKind = Literal["eid_xbrl_html_render_candidate.v1"]
FundDisclosureSourceKind = Literal["eid_xbrl_html_render_candidate"]
FundDisclosureDocumentKind = Literal["annual_report"]
FundDisclosureIntermediateKind = Literal["fund_disclosure_document.v1"]
FundDisclosureBlockType = Literal[
    "paragraph",
    "heading",
    "note",
    "list_item",
    "caption",
    "footnote",
]

_SOURCE_ARTIFACT_TO_KIND: dict[str, str] = {
    "eid_xbrl_html_render_candidate.v1": "eid_xbrl_html_render_candidate",
}
_LOCATOR_STABILITY_VALUES = frozenset(get_args(LocatorStability))


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentIdentity:
    """候选文档 artifact 身份与 fetch/render 元数据。

    Args:
        无。

    Attributes:
        source_artifact_kind: 候选来源 artifact kind，不能当作 processor intermediate kind。
        source_kind: 无版本短来源名。
        fund_code: 6 位基金代码。
        fund_id: EID 平台 fund id。
        instance_id: EID 公告实例 ID。
        report_year: 年报年份。
        report_type_code: EID 报告类型代码。
        report_type_label: EID 报告类型描述。
        report_send_date: EID 发送日期。
        source_list: 候选来源 URL 列表。
        index_url: EID 公告列表 URL。
        instance_view_url: EID 公告详情 URL。
        render_url: HTML render URL。
        redirect_location: redirect 目标。
        content_type: HTTP Content-Type。
        content_length: HTTP Content-Length。
        content_hash: render body SHA-256。
        fetched_at: ISO-8601 抓取时间。
        render_status: render 状态。
        navigation_present: 是否存在 navigation。
        candidate_only: candidate-only 边界。
        field_correctness_status: 字段正确性状态。
        source_truth_status: 来源真源状态。
        parser_replacement_authorized: parser replacement 授权状态。
        readiness_status: readiness 状态。

    Raises:
        ValueError: 身份字段、hash 或 candidate boundary 非法时抛出。
    """

    source_artifact_kind: FundDisclosureSourceArtifactKind
    source_kind: FundDisclosureSourceKind
    fund_code: str
    fund_id: str | None
    instance_id: str | None
    report_year: int
    report_type_code: str | None
    report_type_label: str | None
    report_send_date: str | None
    source_list: tuple[str, ...] | None
    index_url: str | None
    instance_view_url: str | None
    render_url: str | None
    redirect_location: str | None
    content_type: str | None
    content_length: int | None
    content_hash: str | None
    fetched_at: str | None
    render_status: str | None
    navigation_present: bool
    candidate_only: Literal[True] = True
    field_correctness_status: Literal["not_proven"] = "not_proven"
    source_truth_status: Literal["not_proven"] = "not_proven"
    parser_replacement_authorized: Literal[False] = False
    readiness_status: Literal["not_ready"] = "not_ready"

    def __post_init__(self) -> None:
        """校验候选身份和边界字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段违反当前 gate 契约时抛出。
        """

        if self.source_artifact_kind not in _SOURCE_ARTIFACT_TO_KIND:
            raise ValueError("source_artifact_kind 必须是已认可的 candidate artifact kind")
        if self.source_kind != _SOURCE_ARTIFACT_TO_KIND[self.source_artifact_kind]:
            raise ValueError("source_kind 必须匹配 source_artifact_kind 的无版本短名")
        _validate_fund_code(self.fund_code)
        _validate_positive_int(self.report_year, "report_year")
        if self.content_length is not None and self.content_length < 0:
            raise ValueError("content_length 不能为负数")
        _validate_sha256_or_none(self.content_hash, field_name="content_hash")
        _validate_identity_boundary(self)

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复身份对象。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            ``FundDisclosureDocumentIdentity`` 实例。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["source_list"] = _tuple_or_none(values.get("source_list"))
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentNavigationNode:
    """候选文档 navigation 节点。"""

    node_id: str
    title_text: str
    title_normalized: str
    level: int
    parent_node_id: str | None
    child_node_ids: tuple[str, ...]
    section_id: str | None
    locator_stability: LocatorStability
    order_index: int

    def __post_init__(self) -> None:
        """校验 navigation 节点字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段非法时抛出。
        """

        _validate_non_empty(self.node_id, "node_id")
        _validate_non_empty(self.title_text, "title_text")
        _validate_positive_int(self.level, "level")
        _validate_non_negative_int(self.order_index, "order_index")
        _validate_locator_stability(self.locator_stability)

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复 navigation 节点。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            navigation 节点。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["child_node_ids"] = _tuple(values.get("child_node_ids"))
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentSection:
    """候选文档 section locator。"""

    section_id: str
    heading_text_raw: str
    heading_text_normalized: str
    heading_path: tuple[str, ...]
    heading_level: int | None
    start_page_or_offset: int | None
    end_page_or_offset: int | None
    child_section_ids: tuple[str, ...]
    locator_stability: LocatorStability
    normalization_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        """校验 section locator。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段非法时抛出。
        """

        _validate_non_empty(self.section_id, "section_id")
        _validate_non_empty(self.heading_text_raw, "heading_text_raw")
        if self.heading_level is not None:
            _validate_positive_int(self.heading_level, "heading_level")
        _validate_optional_non_negative_int(self.start_page_or_offset, "start_page_or_offset")
        _validate_optional_non_negative_int(self.end_page_or_offset, "end_page_or_offset")
        if (
            self.start_page_or_offset is not None
            and self.end_page_or_offset is not None
            and self.start_page_or_offset > self.end_page_or_offset
        ):
            raise ValueError("start_page_or_offset 不能大于 end_page_or_offset")
        _validate_locator_stability(self.locator_stability)

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复 section。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            section locator。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["heading_path"] = _tuple(values.get("heading_path"))
        values["child_section_ids"] = _tuple(values.get("child_section_ids"))
        values["normalization_notes"] = _tuple(values.get("normalization_notes"))
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentParagraphBlock:
    """候选文档段落级 block。"""

    block_id: str
    block_type: FundDisclosureBlockType
    section_id: str | None
    heading_path: tuple[str, ...]
    text_raw: str
    text_normalized: str
    content_hash: str
    locator_stability: LocatorStability
    normalization_applied: tuple[str, ...]

    def __post_init__(self) -> None:
        """校验段落级 block。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段非法时抛出。
        """

        _validate_non_empty(self.block_id, "block_id")
        _validate_non_empty(self.text_raw, "text_raw")
        _validate_sha256(self.content_hash, "content_hash")
        _validate_locator_stability(self.locator_stability)

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复段落级 block。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            段落级 block。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["heading_path"] = _tuple(values.get("heading_path"))
        values["normalization_applied"] = _tuple(values.get("normalization_applied"))
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentCellLocator:
    """候选表格单元格 locator。"""

    cell_id: str
    table_id: str
    render_url: str | None
    section_anchor: str | None
    heading_path: tuple[str, ...]
    table_index_under_section: int | None
    row_index: int
    column_index: int
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_text: str
    cell_text_normalized: str
    cell_hash: str
    is_header_cell: bool
    locator_stability: LocatorStability
    normalization_applied: tuple[str, ...]

    def __post_init__(self) -> None:
        """校验单元格 locator。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段非法时抛出。
        """

        _validate_non_empty(self.cell_id, "cell_id")
        _validate_non_empty(self.table_id, "table_id")
        _validate_optional_non_negative_int(
            self.table_index_under_section, "table_index_under_section"
        )
        _validate_non_negative_int(self.row_index, "row_index")
        _validate_non_negative_int(self.column_index, "column_index")
        _validate_sha256(self.cell_hash, "cell_hash")
        _validate_locator_stability(self.locator_stability)

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复单元格 locator。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            单元格 locator。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["heading_path"] = _tuple(values.get("heading_path"))
        values["row_label_path"] = _tuple(values.get("row_label_path"))
        values["column_header_path"] = _tuple(values.get("column_header_path"))
        values["normalization_applied"] = _tuple(values.get("normalization_applied"))
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentTableBlock:
    """候选表格 block。"""

    table_id: str
    section_id: str | None
    heading_text: str | None
    heading_path: tuple[str, ...]
    table_index_under_section: int | None
    table_caption_or_nearby_heading: str | None
    header_rows: tuple[int, ...]
    body_rows: tuple[int, ...]
    row_count: int
    column_count: int
    merged_header_detected: bool
    cells: tuple[FundDisclosureDocumentCellLocator, ...]
    locator_stability: LocatorStability
    extraction_note: str | None

    def __post_init__(self) -> None:
        """校验表格 block。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段非法时抛出。
        """

        _validate_non_empty(self.table_id, "table_id")
        _validate_optional_non_negative_int(
            self.table_index_under_section, "table_index_under_section"
        )
        _validate_positive_int(self.row_count, "row_count")
        _validate_positive_int(self.column_count, "column_count")
        _validate_locator_stability(self.locator_stability)
        for row_index in (*self.header_rows, *self.body_rows):
            if row_index < 0 or row_index >= self.row_count:
                raise ValueError("header_rows/body_rows 必须落在 row_count 范围内")
        for cell in self.cells:
            if cell.table_id != self.table_id:
                raise ValueError("cell.table_id 必须匹配 table_id")
            if cell.row_index >= self.row_count or cell.column_index >= self.column_count:
                raise ValueError("cell row/column index 必须落在 table shape 内")

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        data = asdict(self)
        data["cells"] = [cell.to_dict() for cell in self.cells]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复表格 block。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            表格 block。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["heading_path"] = _tuple(values.get("heading_path"))
        values["header_rows"] = _tuple_int(values.get("header_rows"))
        values["body_rows"] = _tuple_int(values.get("body_rows"))
        values["cells"] = tuple(
            FundDisclosureDocumentCellLocator.from_dict(item)
            for item in _tuple_dict(values.get("cells"))
        )
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FundDisclosureDocumentFailure:
    """候选文档内部失败记录。"""

    failure_code: str
    failure_message: str
    source_stage: str
    canonical_failure_class: AnnualReportSourceFailureCategory | None

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复失败记录。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            失败记录。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        return cls(**data)  # type: ignore[arg-type]


def _default_candidate_boundary() -> CandidateBoundaryStatus:
    """构造默认 candidate-only 边界状态。

    Args:
        无。

    Returns:
        ``CandidateBoundaryStatus`` 默认安全值。

    Raises:
        无显式抛出。
    """

    return CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
        parser_replacement_authorized=False,
        readiness_status="not_ready",
    )


@dataclass(frozen=True, slots=True)
class FundDisclosureDocument:
    """FundDisclosureDocument candidate-only 中间态。

    本对象满足 ``FundDisclosureDocumentIntermediate`` Protocol，但只暴露最小 processor
    边界字段。section/table/cell 仍是 Fund documents 内部候选结构，不可被上层直接消费。
    """

    identity: FundDisclosureDocumentIdentity
    navigation_nodes: tuple[FundDisclosureDocumentNavigationNode, ...]
    sections: tuple[FundDisclosureDocumentSection, ...]
    paragraph_blocks: tuple[FundDisclosureDocumentParagraphBlock, ...]
    table_blocks: tuple[FundDisclosureDocumentTableBlock, ...]
    failures: tuple[FundDisclosureDocumentFailure, ...] = ()
    source_provenance: PublicSourceProvenance | None = None
    candidate_boundary: CandidateBoundaryStatus = field(default_factory=_default_candidate_boundary)
    failure_class: AnnualReportSourceFailureCategory | None = None
    document_kind: FundDisclosureDocumentKind = "annual_report"
    intermediate_kind: FundDisclosureIntermediateKind = "fund_disclosure_document.v1"

    @property
    def fund_code(self) -> str:
        """返回基金代码。

        Args:
            无。

        Returns:
            6 位基金代码。

        Raises:
            无显式抛出。
        """

        return self.identity.fund_code

    @property
    def report_year(self) -> int:
        """返回年报年份。

        Args:
            无。

        Returns:
            年报年份。

        Raises:
            无显式抛出。
        """

        return self.identity.report_year

    def __post_init__(self) -> None:
        """校验顶层候选文档边界。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 顶层固定字段、边界或引用关系非法时抛出。
        """

        if self.document_kind != "annual_report":
            raise ValueError("FundDisclosureDocument.document_kind 必须固定为 annual_report")
        if self.intermediate_kind != "fund_disclosure_document.v1":
            raise ValueError(
                "FundDisclosureDocument.intermediate_kind 必须固定为 fund_disclosure_document.v1"
            )
        if self.candidate_boundary is None:
            raise ValueError("FundDisclosureDocument 必须携带 CandidateBoundaryStatus")
        section_ids = {section.section_id for section in self.sections}
        table_ids = {table.table_id for table in self.table_blocks}
        for node in self.navigation_nodes:
            if node.section_id is not None and node.section_id not in section_ids:
                raise ValueError("navigation node 指向未知 section_id")
        for paragraph in self.paragraph_blocks:
            if paragraph.section_id is not None and paragraph.section_id not in section_ids:
                raise ValueError("paragraph block 指向未知 section_id")
        for table in self.table_blocks:
            if table.section_id is not None and table.section_id not in section_ids:
                raise ValueError("table block 指向未知 section_id")
            for cell in table.cells:
                if cell.table_id not in table_ids:
                    raise ValueError("cell locator 指向未知 table_id")

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典，不包含 PDF、HTML 或 credential。

        Raises:
            无显式抛出。
        """

        return {
            "identity": self.identity.to_dict(),
            "navigation_nodes": [node.to_dict() for node in self.navigation_nodes],
            "sections": [section.to_dict() for section in self.sections],
            "paragraph_blocks": [block.to_dict() for block in self.paragraph_blocks],
            "table_blocks": [table.to_dict() for table in self.table_blocks],
            "failures": [failure.to_dict() for failure in self.failures],
            "source_provenance": (
                source_provenance_to_dict(self.source_provenance)
                if self.source_provenance is not None
                else None
            ),
            "candidate_boundary": asdict(self.candidate_boundary),
            "failure_class": self.failure_class,
            "document_kind": self.document_kind,
            "intermediate_kind": self.intermediate_kind,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """从 JSON 兼容字典恢复候选文档。

        Args:
            data: ``to_dict()`` 输出形状。

        Returns:
            ``FundDisclosureDocument`` 实例。

        Raises:
            ValueError: 字段非法时由构造函数抛出。
        """

        values = dict(data)
        values["identity"] = FundDisclosureDocumentIdentity.from_dict(_dict(values.get("identity")))
        values["navigation_nodes"] = tuple(
            FundDisclosureDocumentNavigationNode.from_dict(item)
            for item in _tuple_dict(values.get("navigation_nodes"))
        )
        values["sections"] = tuple(
            FundDisclosureDocumentSection.from_dict(item)
            for item in _tuple_dict(values.get("sections"))
        )
        values["paragraph_blocks"] = tuple(
            FundDisclosureDocumentParagraphBlock.from_dict(item)
            for item in _tuple_dict(values.get("paragraph_blocks"))
        )
        values["table_blocks"] = tuple(
            FundDisclosureDocumentTableBlock.from_dict(item)
            for item in _tuple_dict(values.get("table_blocks"))
        )
        values["failures"] = tuple(
            FundDisclosureDocumentFailure.from_dict(item)
            for item in _tuple_dict(values.get("failures"))
        )
        source_provenance = values.get("source_provenance")
        values["source_provenance"] = (
            PublicSourceProvenance(**_dict(source_provenance))
            if source_provenance is not None
            else None
        )
        values["candidate_boundary"] = CandidateBoundaryStatus(
            **_dict(values.get("candidate_boundary"))
        )
        return cls(**values)  # type: ignore[arg-type]


def _validate_identity_boundary(identity: FundDisclosureDocumentIdentity) -> None:
    """校验 identity 内联边界字段不越权。

    Args:
        identity: 候选身份对象。

    Returns:
        无返回值。

    Raises:
        ValueError: 边界字段非法时抛出。
    """

    if not identity.candidate_only:
        raise ValueError("identity 必须保持 candidate_only=True")
    if identity.field_correctness_status != "not_proven":
        raise ValueError("identity 不得声明 field correctness")
    if identity.source_truth_status != "not_proven":
        raise ValueError("identity 不得声明 source truth")
    if identity.parser_replacement_authorized:
        raise ValueError("identity 不得授权 parser replacement")
    if identity.readiness_status != "not_ready":
        raise ValueError("identity 不得声明 readiness")


def _validate_fund_code(fund_code: str) -> None:
    """校验 6 位基金代码。

    Args:
        fund_code: 基金代码。

    Returns:
        无返回值。

    Raises:
        ValueError: 非 6 位数字时抛出。
    """

    if not (fund_code.isdigit() and len(fund_code) == 6):
        raise ValueError("fund_code 必须是 6 位数字")


def _validate_positive_int(value: int, field_name: str) -> None:
    """校验正整数。

    Args:
        value: 待校验值。
        field_name: 字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 非正整数时抛出。
    """

    if value <= 0:
        raise ValueError(f"{field_name} 必须为正整数")


def _validate_non_negative_int(value: int, field_name: str) -> None:
    """校验非负整数。

    Args:
        value: 待校验值。
        field_name: 字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 为负数时抛出。
    """

    if value < 0:
        raise ValueError(f"{field_name} 不能为负数")


def _validate_optional_non_negative_int(value: int | None, field_name: str) -> None:
    """校验可空非负整数。

    Args:
        value: 待校验值。
        field_name: 字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 非空且为负数时抛出。
    """

    if value is not None:
        _validate_non_negative_int(value, field_name)


def _validate_non_empty(value: str, field_name: str) -> None:
    """校验非空字符串。

    Args:
        value: 待校验字符串。
        field_name: 字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 空字符串时抛出。
    """

    if not value:
        raise ValueError(f"{field_name} 不能为空")


def _validate_sha256(value: str, field_name: str) -> None:
    """校验 SHA-256 hex 字符串。

    Args:
        value: hash 字符串。
        field_name: 字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: hash 为空、长度错误或包含非 hex 字符时抛出。
    """

    if not value:
        raise ValueError(f"{field_name} 不能为空")
    if len(value) != 64:
        raise ValueError(f"{field_name} 必须是 64 位 SHA-256 hex")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field_name} 必须是 hex 字符串") from exc


def _validate_sha256_or_none(value: str | None, *, field_name: str) -> None:
    """校验可空 SHA-256 hex 字符串。

    Args:
        value: hash 字符串或 ``None``。
        field_name: 字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 非空 hash 非法时抛出。
    """

    if value is not None:
        _validate_sha256(value, field_name)


def _validate_locator_stability(value: str) -> None:
    """校验 locator stability 使用既有闭合 literal。

    Args:
        value: locator stability。

    Returns:
        无返回值。

    Raises:
        ValueError: 值不在既有 literal 中时抛出。
    """

    if value not in _LOCATOR_STABILITY_VALUES:
        raise ValueError("locator_stability 必须使用既有 LocatorStability literal")


def _tuple(value: object) -> tuple[str, ...]:
    """把 JSON list/tuple 恢复为字符串 tuple。

    Args:
        value: JSON 字段值。

    Returns:
        字符串 tuple。

    Raises:
        无显式抛出。
    """

    return tuple(value or ())  # type: ignore[arg-type]


def _tuple_or_none(value: object) -> tuple[str, ...] | None:
    """把 JSON list/tuple 恢复为可空字符串 tuple。

    Args:
        value: JSON 字段值。

    Returns:
        字符串 tuple 或 ``None``。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    return tuple(value)  # type: ignore[arg-type]


def _tuple_int(value: object) -> tuple[int, ...]:
    """把 JSON list/tuple 恢复为整数 tuple。

    Args:
        value: JSON 字段值。

    Returns:
        整数 tuple。

    Raises:
        无显式抛出。
    """

    return tuple(value or ())  # type: ignore[arg-type]


def _tuple_dict(value: object) -> tuple[dict[str, object], ...]:
    """把 JSON list/tuple 恢复为 dict tuple。

    Args:
        value: JSON 字段值。

    Returns:
        dict tuple。

    Raises:
        无显式抛出。
    """

    return tuple(value or ())  # type: ignore[return-value, arg-type]


def _dict(value: object) -> dict[str, object]:
    """把 JSON object 恢复为 dict。

    Args:
        value: JSON 字段值。

    Returns:
        字典；空值返回空字典。

    Raises:
        无显式抛出。
    """

    return dict(value or {})  # type: ignore[arg-type]
