"""Docling source-truth residual closure helper 的 no-live 单元测试。"""

from __future__ import annotations

import builtins

import pytest

from fund_agent.fund.documents.candidates import source_truth_residual_closure as closure
from fund_agent.fund.documents.candidates.source_truth_residual_closure import (
    RepositoryReferenceBundle,
    RepositoryReferenceCell,
    close_source_truth_residuals,
)


def _anchor(
    *,
    section_id: str,
    table_id: str | None = "docling_table_1",
    row_locator: str | None = "cell:r0:c1:idx1",
    source_kind: str = "annual_report",
    candidate_source_kind: str = "docling_pdf_candidate",
    source_truth_status: str = "not_proven",
) -> dict[str, object]:
    """构造 candidate-only anchor fixture。

    Args:
        section_id: 候选章节。
        table_id: 候选表格 ID。
        row_locator: 候选行定位。
        source_kind: 模拟 EvidenceAnchor.source_kind 的年报语义来源。
        candidate_source_kind: candidate processor route 身份。
        source_truth_status: candidate source truth 状态。

    Returns:
        JSON-like anchor 字典。

    Raises:
        无显式抛出。
    """

    return {
        "section_id": section_id,
        "page_number": 5,
        "table_id": table_id,
        "row_locator": row_locator,
        "candidate_only": True,
        "source_kind": source_kind,
        "candidate_source_kind": candidate_source_kind,
        "source_truth_status": source_truth_status,
        "field_correctness_status": "not_proven",
    }


def _row(
    *,
    fact_id: str,
    field_name: str,
    value: str,
    section_id: str,
    sample_id: str = "S1",
    fund_code: str = "004393",
    row_disposition: str = "ambiguous_source_body_match",
    table_id: str | None = "docling_table_1",
    row_locator: str | None = "cell:r0:c1:idx1",
    anchor_extra: dict[str, object] | None = None,
) -> dict[str, object]:
    """构造 source_truth_matrix residual row fixture。

    Args:
        fact_id: fact id。
        field_name: 字段名。
        value: 归一化候选值。
        section_id: 候选章节。
        sample_id: 样本 ID。
        fund_code: 基金代码。
        row_disposition: 上游 residual disposition。
        table_id: 候选表格 ID。
        row_locator: 候选行定位。
        anchor_extra: anchor 额外覆盖字段。

    Returns:
        JSON-like residual row。

    Raises:
        无显式抛出。
    """

    anchor = _anchor(section_id=section_id, table_id=table_id, row_locator=row_locator)
    if anchor_extra:
        anchor.update(anchor_extra)
    return {
        "sample_id": sample_id,
        "fact_id": fact_id,
        "fund_code": fund_code,
        "document_year": 2025,
        "field_name": field_name,
        "candidate_anchor": anchor,
        "normalized_candidate": value,
        "row_disposition": row_disposition,
        "residual_reason": "test residual",
    }


def _cell(
    *,
    value: str,
    row_label_path: tuple[str, ...],
    section_id: str = "§2",
    column_header_path: tuple[str, ...] = ("项目", "值"),
    table_context: tuple[str, ...] = ("基金概况",),
    table_id: str = "source_table_1",
    repository_source_name: str = "eid",
) -> RepositoryReferenceCell:
    """构造 repository-mediated reference cell fixture。

    Args:
        value: 单元格值。
        row_label_path: 行标签路径。
        section_id: 年报章节。
        column_header_path: 列表头路径。
        table_context: 表格上下文。
        table_id: 表格 ID。
        repository_source_name: 仓库来源名。

    Returns:
        仓库引用单元格。

    Raises:
        无显式抛出。
    """

    return RepositoryReferenceCell(
        fund_code="004393",
        document_year=2025,
        repository_source_name=repository_source_name,
        source_mode="single_source_only",
        fallback_used=False,
        section_id=section_id,
        page_number=5,
        table_id=table_id,
        row_index=0,
        column_index=1,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        raw_text=value,
        normalized_text=value,
        table_context=table_context,
    )


def _bundle(*cells: RepositoryReferenceCell, metadata_ok: bool = True) -> RepositoryReferenceBundle:
    """构造 repository reference bundle fixture。

    Args:
        *cells: 仓库引用单元格。
        metadata_ok: metadata guard 是否通过。

    Returns:
        仓库引用 bundle。

    Raises:
        无显式抛出。
    """

    return RepositoryReferenceBundle(
        sample_id="S1",
        fund_code="004393",
        document_year=2025,
        metadata_ok=metadata_ok,
        metadata_reason=None if metadata_ok else "unsafe metadata",
        cells=cells,
    )


def _matrix(*rows: dict[str, object]) -> dict[str, object]:
    """构造 source_truth_matrix fixture。

    Args:
        *rows: residual rows。

    Returns:
        JSON-like matrix。

    Raises:
        无显式抛出。
    """

    return {"rows": list(rows), "input_artifacts": [{"path": "accepted/source_truth_matrix.json"}]}


def _close_one(row: dict[str, object], bundle: RepositoryReferenceBundle) -> dict[str, object]:
    """执行 helper 并返回第一行结果字典。

    Args:
        row: residual row fixture。
        bundle: 仓库引用 bundle fixture。

    Returns:
        第一行输出字典。

    Raises:
        AssertionError: 输出行数不是 1 时抛出。
    """

    result = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": bundle},
    ).to_dict()
    assert result["summary"]["rows_total"] == 1
    return result["rows"][0]


def test_identity_code_disambiguates_main_code_from_trading_code() -> None:
    """验证 fund_code 只闭合到基金主代码，不闭合到交易代码。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    result = _close_one(
        row,
        _bundle(
            _cell(value="004393", row_label_path=("交易代码",)),
            _cell(value="004393", row_label_path=("基金主代码",)),
            _cell(value="004393", row_label_path=("下属分级基金的交易代码",)),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_row_label_path"] == ["基金主代码"]
    assert result["fund_layer_status"] == "semantic_rule_satisfied"


def test_identity_name_closes_only_on_labeled_profile_row() -> None:
    """验证 fund_name 只闭合到 §2 基金名称行。"""

    row = _row(fact_id="S4-F001", field_name="fund_name", value="安信基金", section_id="§2")
    result = _close_one(
        row,
        _bundle(
            _cell(value="安信基金", row_label_path=("页眉",)),
            _cell(value="安信基金", row_label_path=("基金名称",)),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_row_label_path"] == ["基金名称"]


def test_manager_and_custodian_close_on_labeled_profile_rows() -> None:
    """验证管理人与托管人只用 §2 已标注行闭合。"""

    manager = _row(
        fact_id="S6-F037",
        field_name="manager",
        value="易方达基金管理有限公司",
        section_id="§2",
    )
    custodian = _row(
        fact_id="S6-F038",
        field_name="custodian",
        value="中国建设银行股份有限公司",
        section_id="§2",
    )
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(manager, custodian),
        repository_reference_rows={
            "S1": _bundle(
                _cell(value="易方达基金管理有限公司", row_label_path=("封面",)),
                _cell(value="易方达基金管理有限公司", row_label_path=("基金管理人",)),
                _cell(value="中国建设银行股份有限公司", row_label_path=("页脚",)),
                _cell(value="中国建设银行股份有限公司", row_label_path=("基金托管人名称",)),
            )
        },
    ).to_dict()

    rows = {item["field_name"]: item for item in matrix["rows"]}
    assert rows["manager"]["closure_disposition"] == "disambiguated_source_body_match"
    assert rows["manager"]["matched_row_label_path"] == ["基金管理人"]
    assert rows["custodian"]["closure_disposition"] == "disambiguated_source_body_match"
    assert rows["custodian"]["matched_row_label_path"] == ["基金托管人名称"]


def test_portfolio_parent_child_split_uses_row_label_not_value_only() -> None:
    """验证权益投资与股票子项同值时按行标签分流。"""

    equity = _row(
        fact_id="S6-F049",
        field_name="equity_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    stock = _row(
        fact_id="S6-F050",
        field_name="stock_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(equity, stock),
        repository_reference_rows={
            "S1": _bundle(
                _cell(
                    value="149698325.51",
                    row_label_path=("权益投资",),
                    section_id="§8",
                    table_context=("基金资产组合",),
                ),
                _cell(
                    value="149698325.51",
                    row_label_path=("其中：股票",),
                    section_id="§8",
                    table_context=("基金资产组合",),
                ),
            )
        },
    ).to_dict()

    rows = {item["field_name"]: item for item in matrix["rows"]}
    assert rows["equity_investment_amount"]["matched_row_label_path"] == ["权益投资"]
    assert rows["stock_investment_amount"]["matched_row_label_path"] == ["其中：股票"]


def test_fixed_income_rejects_fair_value_hierarchy_and_accepts_portfolio_row() -> None:
    """验证固定收益投资拒绝公允价值层级行，只接受组合表行。"""

    row = _row(
        fact_id="S4-F015",
        field_name="fixed_income_investment_amount",
        value="12106715596.39",
        section_id="§8",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="12106715596.39",
                row_label_path=("第二层次",),
                section_id="§8",
                table_context=("公允价值层级",),
            ),
            _cell(
                value="12106715596.39",
                row_label_path=("固定收益投资",),
                section_id="§8",
                table_context=("基金资产组合",),
            ),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_row_label_path"] == ["固定收益投资"]


def test_benchmark_guard_keeps_investment_objective_context_residual() -> None:
    """验证 benchmark 不被投资目标上下文强行闭合。"""

    row = _row(
        fact_id="S6-F041",
        field_name="benchmark",
        value="紧密跟踪业绩比较基准",
        section_id="§2",
        row_disposition="semantic_assignment_residual",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="紧密跟踪业绩比较基准",
                row_label_path=("投资目标",),
                table_context=("投资目标",),
            )
        ),
    )

    assert result["closure_disposition"] == "semantic_assignment_residual"
    assert result["fund_layer_status"] == "semantic_rule_rejected"


def test_investment_objective_without_same_source_body_stays_mismatch() -> None:
    """验证 S5-F023 没有同源正文 proof 时保持 source_body_mismatch。"""

    row = _row(
        fact_id="S5-F023",
        field_name="investment_objective",
        value="在严格控制风险的前提下追求回报",
        section_id="§2",
        row_disposition="source_body_mismatch",
    )
    result = _close_one(row, _bundle())

    assert result["closure_disposition"] == "source_body_mismatch"
    assert result["source_layer_status"] == "same_source_text_absent"


def test_unresolved_expense_duplicate_remains_semantic_equivalent_residual() -> None:
    """验证销售服务费 C 本期重复行不会被强制唯一闭合。"""

    row = _row(
        fact_id="F015",
        field_name="sales_service_fee_C_current_year",
        value="75815.59",
        section_id="§7",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="75815.59",
                row_label_path=("销售服务费",),
                section_id="§7",
                column_header_path=("C类", "本期"),
                table_context=("销售服务费",),
                table_id="fee_1",
            ),
            _cell(
                value="75815.59",
                row_label_path=("销售服务费",),
                section_id="§7",
                column_header_path=("C类", "本报告期"),
                table_context=("销售服务费",),
                table_id="fee_2",
            ),
        ),
    )

    assert result["closure_disposition"] == "semantic_equivalent_duplicate_residual"
    assert result["fund_layer_status"] == "semantic_rule_unresolved"


def test_manager_holding_range_a_requires_fund_share_class_label() -> None:
    """验证基金经理持有 A 类区间只接受基金份额类别表头。"""

    row = _row(
        fact_id="F030",
        field_name="manager_holding_range_A",
        value="10万份至50万份",
        section_id="§10",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="10万份至50万份",
                row_label_path=("本基金基金经理持有本开放式基金",),
                section_id="§10",
                column_header_path=("beta",),
                table_context=("基金经理持有",),
                table_id="manager_holding_1",
            ),
            _cell(
                value="10万份至50万份",
                row_label_path=("本基金基金经理持有本开放式基金",),
                section_id="§10",
                column_header_path=("混合A",),
                table_context=("基金经理持有",),
                table_id="manager_holding_2",
            ),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_column_header_path"] == ["混合A"]


@pytest.mark.parametrize(
    ("share_class", "header"),
    [
        ("A", "A"),
        ("A", "A类"),
        ("A", "混合A"),
        ("A", "债券A"),
        ("C", "C"),
        ("C", "C类"),
    ],
)
def test_share_class_context_accepts_fund_share_labels(
    share_class: str,
    header: str,
) -> None:
    """验证份额类别 guard 接受基金份额标签。"""

    assert closure._has_share_class_context((header,), share_class) is True


@pytest.mark.parametrize("header", ["beta", "alpha", "clinic"])
def test_share_class_context_rejects_arbitrary_latin_suffix_words(header: str) -> None:
    """验证短份额类别 guard 不接受任意英文尾字母。"""

    assert closure._has_share_class_context((header,), header[-1].upper()) is False


def test_decimal_separator_placement_is_preserved_during_value_match() -> None:
    """验证数值归一化保留小数点位置并仍支持千分位逗号。"""

    assert closure._normalize_for_match("149,698,325.51") == "149698325.51"
    assert closure._normalize_for_match("149698325.51") != closure._normalize_for_match(
        "1496.9832551"
    )


def test_decimal_placement_difference_does_not_close_source_body_match() -> None:
    """验证仅小数点位置不同的数值不会命中同源正文。"""

    row = _row(
        fact_id="S6-F049",
        field_name="equity_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="1496.9832551",
                row_label_path=("权益投资",),
                section_id="§8",
                table_context=("基金资产组合",),
            ),
        ),
    )

    assert result["closure_disposition"] == "source_body_mismatch"
    assert result["source_layer_status"] == "same_source_text_absent"


def test_locator_context_conflict_blocks_locator_layer() -> None:
    """验证 candidate 章节与字段规则冲突时 fail-closed。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§8")
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "blocked_locator_unavailable"
    assert result["processed_layer_status"] == "locator_context_conflict"


def test_unknown_field_name_returns_blocked_rule_missing() -> None:
    """验证未知字段名不会进入语义闭合。"""

    row = _row(
        fact_id="F999",
        field_name="unknown_field",
        value="004393",
        section_id="§2",
    )
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={},
    ).to_dict()

    result = matrix["rows"][0]
    assert result["closure_disposition"] == "blocked_rule_missing"
    assert result["fund_layer_status"] == "semantic_rule_missing"


def test_boundary_fields_keep_repository_processor_and_anchor_kind_separate() -> None:
    """验证 repository source、processor route、EvidenceAnchor.source_kind 不混同。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="004393",
                row_label_path=("基金主代码",),
                repository_source_name="eid",
            )
        ),
    )

    assert result["matched_repository_source_name"] == "eid"
    assert result["candidate_processor_source_kind"] == "docling_pdf_candidate"
    assert result["evidence_anchor_source_kind"] == "annual_report"
    assert result["matched_repository_source_name"] != result["evidence_anchor_source_kind"]


def test_output_guard_flags_are_preserved() -> None:
    """验证输出矩阵保留所有 non-proof guard flags。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": _bundle(_cell(value="004393", row_label_path=("基金主代码",)))},
    ).to_dict()

    assert matrix["not_baseline_promotion"] is True
    assert matrix["not_parser_replacement"] is True
    assert matrix["not_release_readiness"] is True
    assert matrix["not_full_field_correctness"] is True
    assert matrix["not_raw_pdf_bbox_truth"] is True
    assert matrix["candidate_only"] is True


def test_candidate_boundary_guard_rejects_truth_claims() -> None:
    """验证 candidate anchor 越过 not_proven guard 时 fail-closed。"""

    row = _row(
        fact_id="F002",
        field_name="fund_code",
        value="004393",
        section_id="§2",
        anchor_extra={"source_truth_status": "proven"},
    )
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "blocked_candidate_metadata_violation"
    assert result["processed_layer_status"] == "candidate_metadata_violation"


@pytest.mark.parametrize(
    "anchor_extra",
    [
        {"source_kind": "docling_pdf_candidate"},
        {"evidence_anchor_source_kind": "docling_pdf_candidate"},
    ],
)
def test_evidence_anchor_source_kind_guard_rejects_non_annual_report(
    anchor_extra: dict[str, object],
) -> None:
    """验证 EvidenceAnchor.source_kind 非 annual_report 时 fail-closed。"""

    row = _row(
        fact_id="F002",
        field_name="fund_code",
        value="004393",
        section_id="§2",
        anchor_extra=anchor_extra,
    )
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "blocked_candidate_metadata_violation"
    assert result["processed_layer_status"] == "candidate_metadata_violation"


def test_pure_helper_boundary_does_not_read_or_call_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证 pure helper 在 open 被禁用时仍只处理已加载输入。"""

    def _blocked_open(*args: object, **kwargs: object) -> object:
        """在测试中阻断任何文件读取。

        Args:
            *args: 位置参数。
            **kwargs: 关键字参数。

        Returns:
            不返回。

        Raises:
            AssertionError: 任何 open 调用都会抛出。
        """

        raise AssertionError("pure helper must not read files")

    monkeypatch.setattr(builtins, "open", _blocked_open)
    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert not hasattr(closure, "FundDocumentRepository")
    assert not hasattr(closure, "load_annual_report")


def test_missing_reference_bundle_blocks_reference_layer() -> None:
    """验证缺失 repository reference bundle 时返回 blocked_reference_unavailable。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={},
    ).to_dict()

    result = matrix["rows"][0]
    assert result["closure_disposition"] == "blocked_reference_unavailable"
    assert result["source_layer_status"] == "blocked_reference_unavailable"
