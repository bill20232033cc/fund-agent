"""Gate 2 章节审计 primitive 测试，覆盖基金分析模板第 0-7 章。"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

from fund_agent.fund.template.typed_contracts import (
    RequiredOutputItem,
    SUPPORTED_AUDIT_FOCUS,
    get_typed_chapter_contract,
)
from fund_agent.fund.chapter_auditor import (
    ChapterAuditInput,
    ChapterAuditLLMRequest,
    ChapterAuditLLMResponse,
    DEFAULT_AUDIT_FOCUS,
    audit_chapter,
    audit_chapter_llm,
    audit_chapter_programmatic,
)
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    build_chapter_writer_input,
)
from fund_agent.fund.evidence_availability import derive_evidence_availability
from tests.fund.test_chapter_facts import _bundle


class _FakeAuditLLMClient:
    """测试用章节 LLM 审计 fake client。

    Attributes:
        raw_text: 固定返回的行协议文本。
    """

    def __init__(self, raw_text: str, *, model_name: str | None = "fake-auditor") -> None:
        """初始化 fake auditor。

        Args:
            raw_text: 固定返回文本。
            model_name: 模型名称。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.raw_text = raw_text
        self.model_name = model_name
        self.requests: list[ChapterAuditLLMRequest] = []

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        """返回固定审计响应。

        Args:
            request: 审计请求。

        Returns:
            fake LLM 审计响应。

        Raises:
            无显式抛出。
        """

        self.requests.append(request)
        return ChapterAuditLLMResponse(
            raw_text=self.raw_text,
            model_name=self.model_name,
            finish_reason="stop",
        )


def test_programmatic_audit_passes_minimal_valid_chapter() -> None:
    """验证最小合法章节通过程序审计，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法章节未通过程序审计时抛出。
    """

    input_data = _audit_input()

    result = audit_chapter_programmatic(input_data)

    assert result.status == "pass"
    assert result.issues == ()


def test_programmatic_audit_fails_placeholder_text() -> None:
    """验证模板占位符残留被阻断，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当占位符未触发 P2 时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n[基金类型] X.XX%")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "P2" for issue in result.issues)


def test_programmatic_audit_fails_unknown_anchor() -> None:
    """验证未知 anchor 引用被程序审计阻断，见模板证据锚点规范。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知 anchor 未触发 E1 时抛出。
    """

    input_data = _audit_input(used_anchor_ids=("unknown-anchor",))

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "E1" for issue in result.issues)


def test_programmatic_audit_fails_deleted_item_rule_section() -> None:
    """验证 ITEM_RULE 删除段落出现在草稿时触发 C2，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当被删除段落未阻断时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n#### 指数编制规则与成分股\n跟踪指数：沪深300")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any("ITEM_RULE" in issue.message for issue in result.issues)


def test_ch2_deleted_item_rule_does_not_block_required_stability_wording() -> None:
    """验证 Ch2 required output 的稳定性讨论不被删除段落规则误伤。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法稳定性缺口被 ITEM_RULE 阻断时抛出。
    """

    input_data = _audit_input(chapter_id=2, markdown_suffix="\n多年度超额收益稳定性判断仍受披露数据不足限制。")

    result = audit_chapter_programmatic(input_data)

    assert not any("chapter_2_alpha_yearly_breakdown" in issue.item_rule_ids for issue in result.issues)


def test_ch2_deleted_item_rule_still_blocks_deleted_segment_heading() -> None:
    """验证 Ch2 被删除的分年度拆解段落标题仍触发 C2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当删除段落标题未被阻断时抛出。
    """

    input_data = _audit_input_with_deleted_item_rule(
        chapter_id=2,
        rule_id="chapter_2_alpha_yearly_breakdown",
        markdown_suffix="\n#### 超额收益分年度拆解\n逐年拆解。",
    )

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any("chapter_2_alpha_yearly_breakdown" in issue.item_rule_ids for issue in result.issues)


def test_programmatic_audit_fails_forbidden_trading_advice() -> None:
    """验证禁用交易建议触发 C1，见模板投资建议边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当交易建议未触发 C1 时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n建议买入。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "C1" for issue in result.issues)


def test_programmatic_audit_fails_must_not_cover_phrase() -> None:
    """验证 must_not_cover 明确禁止主题被程序审计阻断，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 must_not_cover 命中未触发 C2 时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n这里展开基金经理选股能力的分析。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any("must_not_cover" in issue.message for issue in result.issues)


def test_ch6_pressure_test_exception_does_not_trigger_must_not_cover() -> None:
    """验证 Ch6 must_not_cover 的“除非”例外不会误禁压力测试。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当压力测试例外被误判为禁区时抛出。
    """

    input_data = _audit_input(
        chapter_id=6,
        markdown_suffix="\n压力测试方面：当前数据不足，只能作为下一步风险验证问题。",
    )

    result = audit_chapter_programmatic(input_data)

    assert not any("压力测试" in issue.message for issue in result.issues)


def test_ch6_must_not_cover_still_blocks_current_stage_repetition() -> None:
    """验证 Ch6 must_not_cover 仍阻断真正的当前阶段事实复述。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当真实 forbidden phrase 未被阻断时抛出。
    """

    input_data = _audit_input(chapter_id=6, markdown_suffix="\n这里复述当前阶段事实。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any("复述当前阶段事实" in issue.message for issue in result.issues)


def test_ch3_required_label_allowed_under_missing_evidence() -> None:
    """验证第 3 章缺证时 required label 加缺口说明不会被误判为 C2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 required label 允许上下文被误阻断时抛出。
    """

    body_line = (
        "言行一致性判断：证据不足，当前缺少已复核的换手率或跨期风格变化证据，不能据此判断言行一致。\n"
        "风格稳定性判断：证据不足，当前缺少已复核的换手率或跨期风格变化证据，不能据此判断风格稳定。"
    )

    result = audit_chapter_programmatic(_ch3_typed_audit_input(body_line))

    assert not any("ch3.must_not_cover.item_04" in issue.issue_id for issue in result.issues)


def test_ch3_explicit_evidence_gap_statement_allowed() -> None:
    """验证第 3 章显式证据缺口句允许提及一致性/稳定性边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺口句被误阻断时抛出。
    """

    body_line = (
        "证据不足，当前缺少已复核的换手率或跨期风格变化证据，不能据此判断风格稳定、风格一致或言行一致。"
    )

    result = audit_chapter_programmatic(_ch3_typed_audit_input(body_line))

    assert not any("ch3.must_not_cover.item_04" in issue.issue_id for issue in result.issues)


def test_ch3_positive_consistency_claim_blocks_when_actual_behavior_unreviewed() -> None:
    """验证实际行为证据未复核时正向言行一致判断触发 typed C2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正向判断未阻断时抛出。
    """

    result = audit_chapter_programmatic(_ch3_typed_audit_input("言行一致性判断：言行一致。"))

    assert result.status == "fail"
    assert any(issue.issue_id == "programmatic:C2:ch3.must_not_cover.item_04" for issue in result.issues)


def test_ch3_positive_consistency_claim_blocks_without_evidence_availability() -> None:
    """验证缺少 EvidenceAvailability 时第 3 章正向一致性判断 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 availability 导致 silent pass 时抛出。
    """

    result = audit_chapter_programmatic(
        _ch3_typed_audit_input(
            "言行一致性判断：言行一致。",
            include_evidence_availability=False,
        )
    )

    assert result.status == "fail"
    assert any(issue.issue_id == "programmatic:C2:ch3.must_not_cover.item_04" for issue in result.issues)


def test_ch3_positive_claim_after_anchor_marker_blocks_when_actual_behavior_unreviewed() -> None:
    """验证 anchor marker 同行正文不能绕过 typed C2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 marker 同行正向结论被当作 metadata 跳过时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    availability = derive_evidence_availability(projection)
    writer_input = build_chapter_writer_input(
        projection,
        chapter_id=3,
        evidence_availability=availability,
    )
    anchor_id = writer_input.chapter.evidence_anchors[0].anchor_id
    result = audit_chapter_programmatic(
        _ch3_typed_audit_input(
            f"<!-- anchor:{anchor_id} --> 言行一致性判断：言行一致。",
        )
    )

    assert result.status == "fail"
    assert any(issue.issue_id == "programmatic:C2:ch3.must_not_cover.item_04" for issue in result.issues)


def test_ch3_quasi_positive_consistency_claim_blocks_when_style_evidence_missing() -> None:
    """验证风格证据缺失或未复核时准正向稳定性判断触发 typed C2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当准正向判断未阻断时抛出。
    """

    result = audit_chapter_programmatic(_ch3_typed_audit_input("风格稳定性判断：未见明显不一致，整体变化不大。"))

    assert result.status == "fail"
    assert any(issue.issue_id == "programmatic:C2:ch3.must_not_cover.item_04" for issue in result.issues)


def test_audit_focus_cannot_disable_programmatic_must_not_cover() -> None:
    """验证 audit_focus 不能关闭 typed programmatic must_not_cover。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 audit_focus 省略边界导致 C2 未触发时抛出。
    """

    input_data = _ch3_typed_audit_input("风格稳定性判断：基本稳定。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.issue_id == "programmatic:C2:ch3.must_not_cover.item_04" for issue in result.issues)


def test_per_chapter_audit_focus_is_passed_to_llm_request() -> None:
    """验证 typed per-chapter audit_focus 会传入 LLM request。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LLM request 未收到闭集 focus id 时抛出。
    """

    typed_contract = get_typed_chapter_contract(3)
    client = _FakeAuditLLMClient("PASS|chapter|no issues")
    input_data = _ch3_typed_audit_input("证据不足，不能据此判断言行一致。")
    input_data = ChapterAuditInput(
        writer_input=input_data.writer_input,
        draft=input_data.draft,
        typed_chapter_contract=typed_contract,
        run_programmatic=False,
        run_llm=True,
    )

    result = audit_chapter_llm(input_data, llm_client=client)

    assert result.status == "pass"
    request = client.requests[0]
    assert request.audit_focus == typed_contract.audit_focus
    assert set(request.audit_focus) <= set(SUPPORTED_AUDIT_FOCUS)
    assert "manager_consistency, evidence_anchors" in request.user_prompt


def test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary() -> None:
    """验证 focus 缺少 must_not_cover_boundary 时程序 C2 仍触发。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 typed focus 影响程序审计阻断时抛出。
    """

    typed_contract = get_typed_chapter_contract(3)
    input_data = _ch3_typed_audit_input("风格稳定性判断：基本稳定。")
    input_data = ChapterAuditInput(
        writer_input=input_data.writer_input,
        draft=input_data.draft,
        typed_chapter_contract=typed_contract,
        run_programmatic=True,
        run_llm=False,
    )

    result = audit_chapter_programmatic(input_data)

    assert "must_not_cover_boundary" not in typed_contract.audit_focus
    assert result.status == "fail"
    assert any(issue.issue_id == "programmatic:C2:ch3.must_not_cover.item_04" for issue in result.issues)


def test_invalid_typed_audit_focus_blocks_without_calling_client() -> None:
    """验证非法 typed audit_focus 会 fail-closed 且不调用 LLM client。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 focus 泄漏到 client 或未 blocked 时抛出。
    """

    typed_contract = replace(get_typed_chapter_contract(3), audit_focus=("disable_programmatic",))  # type: ignore[arg-type]
    client = _FakeAuditLLMClient("PASS|chapter|no issues")
    input_data = _ch3_typed_audit_input("证据不足，不能据此判断言行一致。")
    input_data = ChapterAuditInput(
        writer_input=input_data.writer_input,
        draft=input_data.draft,
        typed_chapter_contract=typed_contract,
    )

    result = audit_chapter_llm(input_data, llm_client=client)

    assert result.status == "blocked"
    assert client.requests == []
    assert result.issues[0].issue_id == "llm:audit_focus_invalid"
    assert result.issues[0].layer == "llm"
    assert result.issues[0].rule_code == "LLM_UNAVAILABLE"
    assert result.issues[0].severity == "blocking"
    assert result.issues[0].location == "typed_chapter_contract.audit_focus"


def test_mismatched_typed_audit_focus_blocks_without_calling_client() -> None:
    """验证章节不匹配的 typed contract 会 blocked 且不调用 LLM client。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节不匹配仍调用 client 或未 blocked 时抛出。
    """

    typed_contract = get_typed_chapter_contract(2)
    client = _FakeAuditLLMClient("PASS|chapter|no issues")
    input_data = _ch3_typed_audit_input("证据不足，不能据此判断言行一致。")
    input_data = ChapterAuditInput(
        writer_input=input_data.writer_input,
        draft=input_data.draft,
        typed_chapter_contract=typed_contract,
    )

    result = audit_chapter_llm(input_data, llm_client=client)

    assert result.status == "blocked"
    assert client.requests == []
    assert result.issues[0].issue_id == "llm:audit_focus_invalid"
    assert result.issues[0].message == "typed audit_focus 无法安全投影为闭集 LLM 审计关注点。"


def test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact() -> None:
    """验证候选 facet 被写成断言事实时触发 C2，见 preferred_lens。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 non_asserted facet 被误接受时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n这只基金是主动权益基金（价值风格）。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any("候选 facet" in issue.message for issue in result.issues)


def test_non_asserted_facet_candidate_disclaimer_passes() -> None:
    """验证候选/未断言 facet 说明不会被误杀。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 disclaimer 被错误阻断时抛出。
    """

    input_data = _audit_input(
        markdown_suffix="\n候选/未断言信息：主动权益基金（价值风格）仅为候选标签，"
        "当前结构化证据不足，不能写成本基金属于该 facet。",
    )

    result = audit_chapter_programmatic(input_data)

    assert not any("候选 facet" in issue.message for issue in result.issues)


def test_non_asserted_facet_reports_first_blocking_occurrence_per_unique_facet() -> None:
    """验证同一候选 facet 多次断言只报告第一条但仍阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当去重或阻断语义错误时抛出。
    """

    input_data = _audit_input(
        markdown_suffix="\n这只基金是主动权益基金（价值风格）。\n本基金属于主动权益基金（价值风格）。",
    )

    result = audit_chapter_programmatic(input_data)
    facet_issues = tuple(issue for issue in result.issues if "候选 facet" in issue.message)

    assert result.status == "fail"
    assert len(facet_issues) == 1


def test_programmatic_audit_requires_required_output_marker_not_bare_item_text() -> None:
    """验证裸 required output 文案不能替代 exact marker。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当裸文案错误通过 C2 时抛出。
    """

    input_data = _audit_input()
    item = input_data.writer_input.chapter.contract.required_output_items[0]
    markdown = input_data.draft.markdown.replace(f"<!-- required_output:{item} -->\n", "")
    input_data = _audit_input(markdown_override=markdown)

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any("required output item marker" in issue.message for issue in result.issues)


def test_programmatic_audit_passes_required_output_marker_protocol() -> None:
    """验证 exact required output marker 存在时不触发 marker C2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法 marker 被误阻断时抛出。
    """

    result = audit_chapter_programmatic(_audit_input())

    assert not any("required output item marker" in issue.message for issue in result.issues)


def test_programmatic_audit_passes_typed_ch1_required_output_id_markers() -> None:
    """验证 typed 第 1 章使用 stable item id marker 时通过 C2 marker 审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 typed marker 被 legacy marker 规则误阻断时抛出。
    """

    result = audit_chapter_programmatic(_typed_audit_input(chapter_id=1))

    assert not any("required output item marker" in issue.message for issue in result.issues)


def test_programmatic_audit_fails_missing_typed_required_output_id_marker() -> None:
    """验证 typed marker 缺失时仍 fail-closed，见模板第 1 章 CHAPTER_CONTRACT。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 typed marker 被错误放行时抛出。
    """

    typed_contract = get_typed_chapter_contract(1)
    omitted_item_id = typed_contract.required_output_items[0].item_id

    result = audit_chapter_programmatic(
        _typed_audit_input(chapter_id=1, omitted_required_output_item_id=omitted_item_id)
    )

    assert result.status == "fail"
    assert any(
        issue.rule_code == "C2" and omitted_item_id in issue.message
        for issue in result.issues
    )


def test_programmatic_audit_legacy_path_still_requires_legacy_required_output_marker() -> None:
    """验证 legacy path 不接受 typed item id marker 代替原文 marker。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy marker 规则被 typed path 改动放松时抛出。
    """

    legacy_input = _audit_input()
    typed_contract = get_typed_chapter_contract(1)
    legacy_items = legacy_input.writer_input.chapter.contract.required_output_items
    typed_lines = "\n".join(
        f"<!-- required_output:{item.item_id} -->\n- {item.text}: 已根据结构化事实说明。"
        for item in typed_contract.required_output_items
    )
    legacy_lines = "\n".join(
        f"<!-- required_output:{item} -->\n- {item}: 已根据结构化事实说明。"
        for item in legacy_items
    )
    markdown = legacy_input.draft.markdown.replace(legacy_lines, typed_lines)
    legacy_input = _audit_input(markdown_override=markdown)

    result = audit_chapter_programmatic(legacy_input)

    assert result.status == "fail"
    assert any("required output item marker" in issue.message for issue in result.issues)


def test_programmatic_audit_fails_l1_formula_without_nearby_anchor_marker() -> None:
    """验证 R=A+B-C 数字闭环断言缺邻近 marker 时触发 L1。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 marker 数字闭环断言未触发 L1 时抛出。
    """

    input_data = _audit_input(markdown_suffix="\nA=R-B，因此 Alpha 为 2.10%。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_allows_l1_formula_with_nearby_anchor_marker() -> None:
    """验证 R=A+B-C 数字闭环断言有邻近 marker 时不触发 L1。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当带 marker 数字闭环断言被误阻断时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n<!-- anchor:annual:110011:2024:basic_identity:1 -->\nA=R-B，因此 Alpha 为 2.10%。")

    result = audit_chapter_programmatic(input_data)

    assert not any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_blocks_l1_a_minus_c_without_nearby_anchor_marker() -> None:
    """验证 A-C 百分比闭环缺邻近 marker 时仍触发 L1，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 A-C 未锚定百分比断言被错误放行时抛出。
    """

    input_data = _audit_input(markdown_suffix="\nA-C 后的净超额为 1.20%。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_blocks_l1_missing_wording_with_concrete_unanchored_percentage() -> None:
    """验证缺口措辞不能包装具体无锚点闭环百分比，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当“数据不足”包裹的具体百分比被错误放行时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n数据不足，但 A=R-B 因此 Alpha 为 2.10%。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_allows_l1_formula_framework_without_concrete_percentage() -> None:
    """验证仅解释公式框架且不含具体百分比时不触发 L1，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非数值闭环说明被误判为 L1 时抛出。
    """

    input_data = _audit_input(markdown_suffix="\n这里只说明 R=A+B-C 是归因框架，不填写具体百分比。")

    result = audit_chapter_programmatic(input_data)

    assert not any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_blocks_ch2_source_section_unanchored_numeric_closure() -> None:
    """验证第 2 章出处段无锚点复述公式百分比时仍触发 L1。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当出处段无锚点数字闭环被错误放行时抛出。
    """

    input_data = _audit_input(
        markdown_suffix=(
            "\n### 证据与出处\n"
            "净值增长率2.57%来源于年报§3，基准收益率3.42%来源于年报§3，"
            "因此无法完成完整R=A+B-C数字闭环。"
        )
    )

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_allows_ch2_source_section_numeric_closure_with_nearby_anchor() -> None:
    """验证第 2 章出处段有邻近锚点时不因数字闭环触发 L1。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当出处段已锚定数字闭环被误阻断时抛出。
    """

    input_data = _audit_input(
        markdown_suffix=(
            "\n### 证据与出处\n"
            "<!-- anchor:annual:110011:2024:basic_identity:1 -->\n"
            "净值增长率2.57%来源于年报§3，基准收益率3.42%来源于年报§3，"
            "因此无法完成完整R=A+B-C数字闭环。"
        )
    )

    result = audit_chapter_programmatic(input_data)

    assert not any(issue.rule_code == "L1" for issue in result.issues)


def test_programmatic_audit_blocks_chapter5_cross_period_assertion_when_missing() -> None:
    """验证第 5 章缺跨期数据时阻断确定性跨期断言。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当跨期断言未触发 C2 时抛出。
    """

    input_data = _audit_input(chapter_id=5, markdown_suffix="\n过去一年变化不大，风格稳定。")

    result = audit_chapter_programmatic(input_data)

    assert result.status == "fail"
    assert any(issue.repair_hint == "needs_more_facts" for issue in result.issues)


def test_programmatic_audit_allows_chapter5_cross_period_gap_or_question_wording() -> None:
    """验证第 5 章缺跨期数据时允许缺口或问题式表达。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺口表达被误阻断时抛出。
    """

    input_data = _audit_input(
        chapter_id=5,
        markdown_suffix="\n数据不足，无法判断风格稳定。下一步验证风格是否稳定。",
    )

    result = audit_chapter_programmatic(input_data)

    assert not any("跨期断言" in issue.message for issue in result.issues)


def test_audit_blocks_when_llm_required_but_unavailable() -> None:
    """验证 run_llm=True 且无 client 时 blocked，见模板第 0-7 章 LLM 审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 LLM client 被假通过时抛出。
    """

    result = audit_chapter(_audit_input(), llm_client=None)

    assert result.status == "blocked"
    assert result.accepted is False
    assert result.llm.status == "blocked"


def test_llm_audit_unavailable_is_blocked() -> None:
    """验证 LLM 审计 client 缺失返回 LLM_UNAVAILABLE。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unavailable 未阻断时抛出。
    """

    result = audit_chapter_llm(_audit_input(), llm_client=None)

    assert result.status == "blocked"
    assert result.issues[0].rule_code == "LLM_UNAVAILABLE"


def test_llm_audit_fake_pass_combines_with_programmatic_pass() -> None:
    """验证 fake LLM PASS 与程序审计通过时 accepted。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 PASS 行协议未被接受时抛出。
    """

    result = audit_chapter(_audit_input(), llm_client=_FakeAuditLLMClient("PASS|chapter|no issues"))

    assert result.status == "pass"
    assert result.accepted is True
    assert result.repair_hint == "none"


def test_llm_audit_informational_only_passes_with_programmatic_pass() -> None:
    """验证 informational-only LLM issue 不阻断 acceptance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 INFO 行被误阻断时抛出。
    """

    result = audit_chapter(_audit_input(), llm_client=_FakeAuditLLMClient("INFO|chapter|readable"))

    assert result.status == "pass"
    assert result.accepted is True
    assert result.llm.issues[0].severity == "informational"


def test_llm_audit_parse_failure_is_blocked() -> None:
    """验证 LLM 审计行协议解析失败 blocked，不 silent pass。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 parse failure 被假通过时抛出。
    """

    result = audit_chapter(_audit_input(), llm_client=_FakeAuditLLMClient("free text"))

    assert result.status == "blocked"
    assert result.accepted is False
    assert result.llm.issues[0].rule_code == "C1"
    assert "PASS|chapter|no issues" in result.llm.issues[0].message


def test_llm_audit_line_with_extra_separator_is_parse_failure() -> None:
    """验证 LLM audit 行协议必须恰好三段，message 内不能夹带额外分隔符。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当额外分隔符被错误接受时抛出。
    """

    result = audit_chapter(
        _audit_input(),
        llm_client=_FakeAuditLLMClient("BLOCKING|chapter|reason|extra"),
    )

    assert result.status == "blocked"
    assert result.llm.issues[0].issue_id == "llm:parse_failure"


def test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol() -> None:
    """验证 LLM 审计 prompt 明确 pass 与 issue 行协议。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 协议不完整时抛出。
    """

    client = _FakeAuditLLMClient("PASS|chapter|no issues")

    result = audit_chapter_llm(_audit_input(), llm_client=client)

    assert result.status == "pass"
    request = client.requests[0]
    assert "PASS|chapter|no issues" in request.user_prompt
    assert "唯一 pass 响应必须精确为一行" in request.user_prompt
    assert "BLOCKING|<location>|<message>" in request.user_prompt
    assert "第一段只能是 BLOCKING / REVIEWABLE / INFO" in request.user_prompt
    assert "不得输出 SEVERITY 占位词" in request.user_prompt
    assert "不得包含 `|`" in request.user_prompt
    assert "`<!-- missing:<reason> -->` 是 approved evidence-gap marker" in request.user_prompt
    assert "不要仅因缺少事实、缺少 anchor 或缺少外部来源而阻断" in request.user_prompt
    assert "把缺失数据写成确定性结论" in request.user_prompt
    assert "禁止输出空行以外的额外文本" in request.user_prompt
    assert request.audit_focus == DEFAULT_AUDIT_FOCUS


def test_llm_audit_blocks_markdown_or_explanatory_prefix() -> None:
    """验证解释性前缀或 Markdown 行协议解析失败并 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当自由文本被错误接受时抛出。
    """

    result = audit_chapter_llm(
        _audit_input(),
        llm_client=_FakeAuditLLMClient("审计结果：\nPASS|chapter|no issues"),
    )

    assert result.status == "blocked"
    assert result.issues[0].issue_id == "llm:parse_failure"


def test_llm_audit_fake_issue_prevents_acceptance() -> None:
    """验证 LLM reviewable issue 阻止 acceptance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 reviewable issue 被 accepted 时抛出。
    """

    result = audit_chapter(
        _audit_input(),
        llm_client=_FakeAuditLLMClient("REVIEWABLE|证据|证据支撑不足"),
    )

    assert result.status == "fail"
    assert result.accepted is False
    assert result.repair_hint == "patch"


def test_audit_repair_hint_uses_highest_priority() -> None:
    """验证 repair_hint 聚合取最高优先级。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当聚合优先级错误时抛出。
    """

    result = audit_chapter(
        _audit_input(chapter_id=5, markdown_suffix="\n过去一年变化不大。"),
        llm_client=_FakeAuditLLMClient("REVIEWABLE|证据|证据支撑不足"),
    )

    assert result.status == "fail"
    assert result.repair_hint == "needs_more_facts"


def test_auditor_does_not_import_repository_source_service_dayu_or_openai() -> None:
    """静态验证 auditor 不导入仓库、来源、Service、dayu 或 provider SDK。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当模块 import 越界时抛出。
    """

    imports = _imports_for(Path("fund_agent/fund/chapter_auditor.py"))
    forbidden_fragments = (
        "documents",
        "repository",
        "cache",
        "pdf",
        "source",
        "downloader",
        "parser",
        "service",
        "dayu",
        "openai",
        "httpx",
    )
    assert all(not any(fragment in module for fragment in forbidden_fragments) for module in imports)


def _audit_input(
    *,
    chapter_id: int = 1,
    markdown_suffix: str = "",
    used_anchor_ids: tuple[str, ...] | None = None,
    markdown_override: str | None = None,
) -> ChapterAuditInput:
    """构造章节审计输入。

    Args:
        chapter_id: 模板章节编号。
        markdown_suffix: 附加 Markdown。
        used_anchor_ids: 显式草稿 anchor ids。
        markdown_override: 显式覆盖 Markdown。

    Returns:
        测试用 `ChapterAuditInput`。

    Raises:
        AssertionError: 当投影缺少 anchor 时抛出。
    """

    writer_input = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(chapter_id,)),
        chapter_id=chapter_id,
    )
    anchor_ids = used_anchor_ids
    if anchor_ids is None:
        anchor_ids = (writer_input.chapter.evidence_anchors[0].anchor_id,)
    markdown = markdown_override or (_valid_markdown(writer_input, anchor_ids[0] if anchor_ids else "") + markdown_suffix)
    draft = ChapterDraft(
        chapter_id=writer_input.chapter.chapter_id,
        title=writer_input.chapter.title,
        markdown=markdown,
        used_fact_ids=tuple(fact.fact_id for fact in writer_input.chapter.facts[:1]),
        used_anchor_ids=anchor_ids,
        declared_missing_reasons=(),
        deleted_item_rule_ids=tuple(
            decision.rule_id
            for decision in writer_input.chapter.item_rule_projection.decisions
            if decision.status == "delete"
        ),
        model_name="fake-writer",
        finish_reason="stop",
    )
    return ChapterAuditInput(writer_input=writer_input, draft=draft)


def _audit_input_with_deleted_item_rule(
    *,
    chapter_id: int,
    rule_id: str,
    markdown_suffix: str,
) -> ChapterAuditInput:
    """构造指定 ITEM_RULE 为 delete 的章节审计输入。

    Args:
        chapter_id: 模板章节编号。
        rule_id: 要强制设为删除状态的 ITEM_RULE id。
        markdown_suffix: 附加 Markdown。

    Returns:
        测试用 `ChapterAuditInput`。

    Raises:
        AssertionError: 当目标规则不存在时抛出。
    """

    base_input = _audit_input(chapter_id=chapter_id, markdown_suffix=markdown_suffix)
    decisions = []
    found = False
    for decision in base_input.writer_input.chapter.item_rule_projection.decisions:
        if decision.rule_id == rule_id:
            decisions.append(replace(decision, status="delete"))
            found = True
        else:
            decisions.append(decision)
    assert found
    item_rule_projection = replace(
        base_input.writer_input.chapter.item_rule_projection,
        decisions=tuple(decisions),
    )
    chapter = replace(base_input.writer_input.chapter, item_rule_projection=item_rule_projection)
    writer_input = replace(base_input.writer_input, chapter=chapter)
    draft = replace(base_input.draft, deleted_item_rule_ids=(rule_id,))
    return ChapterAuditInput(writer_input=writer_input, draft=draft)


def _typed_audit_input(
    *,
    chapter_id: int,
    omitted_required_output_item_id: str | None = None,
) -> ChapterAuditInput:
    """构造 typed required-output marker 审计输入。

    Args:
        chapter_id: 模板章节编号。
        omitted_required_output_item_id: 可选要省略的 typed required output item id。

    Returns:
        测试用 typed `ChapterAuditInput`。

    Raises:
        AssertionError: 当投影缺少 anchor 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(chapter_id,))
    availability = derive_evidence_availability(projection)
    typed_contract = get_typed_chapter_contract(chapter_id)
    writer_input = build_chapter_writer_input(
        projection,
        chapter_id=chapter_id,
        typed_required_output_items=typed_contract.required_output_items,
        evidence_availability=availability,
    )
    anchor_id = writer_input.chapter.evidence_anchors[0].anchor_id
    markdown = _typed_valid_markdown(
        writer_input,
        typed_contract.required_output_items,
        anchor_id,
        omitted_required_output_item_id=omitted_required_output_item_id,
    )
    draft = ChapterDraft(
        chapter_id=writer_input.chapter.chapter_id,
        title=writer_input.chapter.title,
        markdown=markdown,
        used_fact_ids=tuple(fact.fact_id for fact in writer_input.chapter.facts[:1]),
        used_anchor_ids=(anchor_id,),
        declared_missing_reasons=(),
        deleted_item_rule_ids=tuple(
            decision.rule_id
            for decision in writer_input.chapter.item_rule_projection.decisions
            if decision.status == "delete"
        ),
        model_name="fake-writer",
        finish_reason="stop",
    )
    return ChapterAuditInput(writer_input=writer_input, draft=draft)


def _ch3_typed_audit_input(body_line: str, *, include_evidence_availability: bool = True) -> ChapterAuditInput:
    """构造带 EvidenceAvailability 的第 3 章 typed 审计输入。

    Args:
        body_line: 第 3 章详细情况中的待审计文本。
        include_evidence_availability: 是否显式传入同源证据可用性；False 用于 fail-closed 回归测试。

    Returns:
        第 3 章审计输入。

    Raises:
        AssertionError: 当投影缺少 anchor 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    availability = derive_evidence_availability(projection) if include_evidence_availability else None
    writer_input = build_chapter_writer_input(
        projection,
        chapter_id=3,
        evidence_availability=availability,
    )
    anchor_id = writer_input.chapter.evidence_anchors[0].anchor_id
    markdown = _ch3_markdown(body_line, writer_input=writer_input, anchor_id=anchor_id)
    draft = ChapterDraft(
        chapter_id=writer_input.chapter.chapter_id,
        title=writer_input.chapter.title,
        markdown=markdown,
        used_fact_ids=tuple(fact.fact_id for fact in writer_input.chapter.facts[:1]),
        used_anchor_ids=(anchor_id,),
        declared_missing_reasons=(),
        deleted_item_rule_ids=tuple(
            decision.rule_id
            for decision in writer_input.chapter.item_rule_projection.decisions
            if decision.status == "delete"
        ),
        model_name="fake-writer",
        finish_reason="stop",
    )
    return ChapterAuditInput(writer_input=writer_input, draft=draft)


def _ch3_markdown(
    body_line: str,
    *,
    writer_input: object | None = None,
    anchor_id: str = "",
) -> str:
    """构造第 3 章合法结构 Markdown。

    Args:
        body_line: 第 3 章详细情况正文。
        writer_input: 可选 writer input；为空时临时构造。
        anchor_id: 可选证据 anchor id。

    Returns:
        测试用第 3 章 Markdown。

    Raises:
        AttributeError: writer input 类型不符合预期时抛出。
    """

    if writer_input is None:
        projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
        writer_input = build_chapter_writer_input(projection, chapter_id=3)
        anchor_id = writer_input.chapter.evidence_anchors[0].anchor_id
    return _valid_markdown(writer_input, anchor_id).replace(
        "本章只使用已断言事实，并把候选 facet 写成未断言。",
        body_line,
    )


def _valid_markdown(writer_input: object, anchor_id: str) -> str:
    """构造满足程序审计的最小章节 Markdown。

    Args:
        writer_input: `ChapterWriterInput`。
        anchor_id: 证据锚点 ID。

    Returns:
        测试用 Markdown。

    Raises:
        AttributeError: 当输入不是 writer input 时抛出。
    """

    chapter = writer_input.chapter
    required_lines = "\n".join(
        f"<!-- required_output:{item} -->\n- {item}: 已根据结构化事实说明。"
        for item in chapter.contract.required_output_items
    )
    evidence = ""
    if anchor_id:
        evidence = (
            f"<!-- anchor:{anchor_id} -->\n"
            "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
        )
    return (
        "### 结论要点\n"
        f"{required_lines}\n"
        "### 详细情况\n"
        "本章只使用已断言事实，并把候选 facet 写成未断言。\n"
        "### 证据与出处\n"
        f"{evidence}"
    )


def _typed_valid_markdown(
    writer_input: object,
    typed_required_output_items: tuple[RequiredOutputItem, ...],
    anchor_id: str,
    *,
    omitted_required_output_item_id: str | None = None,
) -> str:
    """构造使用 typed item id marker 的最小章节 Markdown。

    Args:
        writer_input: `ChapterWriterInput`。
        typed_required_output_items: typed required output items。
        anchor_id: 证据锚点 ID。
        omitted_required_output_item_id: 可选要省略的 typed item id。

    Returns:
        测试用 Markdown。

    Raises:
        AttributeError: 当输入不是 writer input 时抛出。
    """

    chapter = writer_input.chapter
    required_lines = "\n".join(
        f"<!-- required_output:{item.item_id} -->\n- {item.text}: 已根据结构化事实说明。"
        for item in typed_required_output_items
        if item.item_id != omitted_required_output_item_id
    )
    evidence = ""
    if anchor_id:
        evidence = (
            f"<!-- anchor:{anchor_id} -->\n"
            "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
        )
    return (
        "### 结论要点\n"
        f"{required_lines}\n"
        "### 详细情况\n"
        f"本章只使用已断言事实，并把候选 facet 写成未断言。章节：{chapter.title}\n"
        "### 证据与出处\n"
        f"{evidence}"
    )


def _imports_for(source_path: Path) -> set[str]:
    """读取 Python 文件导入模块集合。

    Args:
        source_path: Python 源码路径。

    Returns:
        import module 集合。

    Raises:
        SyntaxError: 当源码无法解析时抛出。
    """

    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.add(node.module)
    return imports
