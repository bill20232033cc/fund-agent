"""Gate 2 章节写作 primitive 测试，覆盖基金分析模板第 0-7 章。"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.chapter_writer import (
    ChapterRepairContext,
    ChapterLLMRequest,
    ChapterLLMResponse,
    build_chapter_prompt,
    build_chapter_writer_input,
    write_chapter,
)
from fund_agent.fund.evidence_availability import derive_evidence_availability
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.fund.template.typed_contracts import (
    RequiredOutputItem,
    load_typed_template_contract_manifest,
)
from tests.fund.test_chapter_facts import _bundle, _field

CH2_PERFORMANCE_REASON = (
    "第 2 章同源已复核净值增长率与业绩基准证据不足时只能输出证据缺口，"
    "不得编造近 1/3/5 年收益数值。"
)
CH2_SYNTHESIS_REASON = (
    "第 2 章同源已复核 R、B 与 C 证据不足时只能输出下一步最小验证问题，"
    "不得输出具体 R=A+B-C 数字闭环。"
)


class _FakeChapterLLMClient:
    """测试用章节写作 fake client。

    Attributes:
        text: 返回给 writer 的章节 Markdown。
    """

    def __init__(
        self,
        text: str,
        *,
        model_name: str | None = "fake-writer",
        finish_reason: str = "stop",
    ) -> None:
        """初始化 fake client。

        Args:
            text: 固定返回文本。
            model_name: 模型名称。
            finish_reason: 模型结束原因。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.text = text
        self.model_name = model_name
        self.finish_reason = finish_reason
        self.requests: list[ChapterLLMRequest] = []

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """返回固定章节文本。

        Args:
            request: writer 构造的请求。

        Returns:
            fake LLM 响应。

        Raises:
            无显式抛出。
        """

        self.requests.append(request)
        return ChapterLLMResponse(
            text=self.text,
            model_name=self.model_name,
            finish_reason=self.finish_reason,
        )


def test_build_writer_input_selects_single_chapter_from_projection() -> None:
    """验证 writer input 从 Gate 1 投影选择唯一章节，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节选择或 schema 信息错误时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(1, 2))

    input_data = build_chapter_writer_input(projection, chapter_id=1)

    assert input_data.projection_schema_version == "chapter_fact_projection.v1"
    assert input_data.fund_code == "110011"
    assert input_data.report_year == 2024
    assert input_data.chapter.chapter_id == 1
    with pytest.raises(ValueError):
        build_chapter_writer_input(projection, chapter_id=3)


def test_writer_prompt_contains_contract_lens_item_rules_and_fact_ids() -> None:
    """验证 prompt 包含章节契约、lens、ITEM_RULE、fact 和 anchor，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 缺少关键输入时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)

    prompt = build_chapter_prompt(input_data)

    assert prompt.chapter_id == 1
    assert "这只基金到底是什么产品" in prompt.title
    assert prompt.must_answer
    assert prompt.must_not_cover
    assert prompt.required_output_items
    assert prompt.allowed_fact_ids
    assert prompt.allowed_anchor_ids
    assert "chapter_1_index_constituents" in prompt.deleted_item_rule_ids
    assert "preferred_lens" in prompt.user_prompt
    assert "删除的 ITEM_RULE 只禁止对应 optional/conditional 段落标题和专属段落" in prompt.user_prompt
    assert "不得因此省略 required_output marker" in prompt.user_prompt


def test_writer_prompt_marks_non_asserted_facets_as_not_asserted() -> None:
    """验证候选 facet 只作为未断言信息进入 prompt，见模板 preferred_lens。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选 facet 缺少未断言约束时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)

    prompt = build_chapter_prompt(input_data)

    assert "主动权益基金（价值风格）" in prompt.user_prompt
    assert "未断言" in prompt.user_prompt
    assert input_data.chapter.facet_resolution.facets == ()


def test_writer_prompt_requires_body_sections_and_required_output_markers() -> None:
    """验证 writer prompt 明确固定结构和 required output marker，见模板第 1-6 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当输出协议未进入 prompt 时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)

    prompt = build_chapter_prompt(input_data)

    assert "### 结论要点" in prompt.user_prompt
    assert "### 详细情况" in prompt.user_prompt
    assert "### 证据与出处" in prompt.user_prompt
    assert "<!-- required_output:<exact required output item> -->" in prompt.user_prompt
    assert "可判定为<facet>" in prompt.user_prompt


def test_writer_prompt_contains_missing_marker_exact_contract_near_allowed_reasons() -> None:
    """验证 missing marker guidance 使用 explicit contract block，见模板数据缺口语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 未降低 missing marker 污染风险时抛出。
    """

    projection = project_chapter_facts(
        replace(_bundle(), index_profile=ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture")),
        chapter_ids=(1,),
    )
    input_data = build_chapter_writer_input(projection, chapter_id=1)

    prompt = build_chapter_prompt(input_data)

    assert "MISSING_MARKER_CONTRACT:" in prompt.user_prompt
    assert "ALLOWED_MISSING_REASONS: field_missing" in prompt.user_prompt
    assert "MISSING_MARKER_EXACT_FORM:" in prompt.user_prompt
    assert "<!-- missing:{reason} -->" in prompt.user_prompt
    assert "Replace {reason} with exactly one token from ALLOWED_MISSING_REASONS." in prompt.user_prompt
    assert "Do not output {reason}, <reason>, or any placeholder." in prompt.user_prompt
    assert "Do not add spaces around the colon." in prompt.user_prompt
    assert "Do not change case, translate missing, or use a fullwidth colon." in prompt.user_prompt
    assert "Do not wrap the marker in backticks or code fences." in prompt.user_prompt
    assert "可用缺口原因：" not in prompt.user_prompt
    assert "allowed missing marker：`<!-- missing:<reason> -->`" not in prompt.user_prompt


def test_required_output_missing_evidence_renders_gap_marker() -> None:
    """验证 typed required output 缺证可通过 approved gap 输出满足，见模板第 3 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺证输出未按 typed gap 行为接受时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    availability = derive_evidence_availability(projection)
    typed_items = (_typed_required_output_item(3, "ch3.required_output.item_05"),)
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=3,
        typed_required_output_items=typed_items,
        evidence_availability=availability,
    )
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown_for_prompt(input_data, build_chapter_prompt(input_data), anchor_id)

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "drafted"
    assert result.stop_reason == "none"
    assert result.draft is not None
    assert "<!-- required_output:ch3.required_output.item_05 -->" in result.draft.markdown
    assert "证据不足" in result.draft.markdown


def test_required_output_delete_if_not_applicable_requires_typed_reason() -> None:
    """验证 delete_if_not_applicable 必须携带 typed reason。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 静默删除未 fail-closed 时抛出。
    """

    projection = project_chapter_facts(
        replace(
            _bundle(),
            manager_alignment=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="not_applicable fixture",
            ),
        ),
        chapter_ids=(3,),
    )
    item = replace(
        _typed_required_output_item(3, "ch3.required_output.item_06"),
        when_evidence_missing="delete_if_not_applicable",
        missing_evidence_reason=None,
    )

    with pytest.raises(ValueError, match="typed reason"):
        build_chapter_prompt(
            build_chapter_writer_input(
                projection,
                chapter_id=3,
                typed_required_output_items=(item,),
                evidence_availability=derive_evidence_availability(projection),
            )
        )


def test_required_output_minimum_verification_question_satisfies_missing_evidence() -> None:
    """验证缺证 required output 可通过 approved 最小验证问题输出满足。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 最小验证问题降级未被接受时抛出。
    """

    projection = project_chapter_facts(
        replace(
            _bundle(),
            manager_alignment=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="fixture missing",
            ),
        ),
        chapter_ids=(3,),
    )
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=3,
        typed_required_output_items=(_typed_required_output_item(3, "ch3.required_output.item_06"),),
        evidence_availability=derive_evidence_availability(projection),
    )
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown_for_prompt(input_data, build_chapter_prompt(input_data), anchor_id)

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "drafted"
    assert result.stop_reason == "none"
    assert result.draft is not None
    assert "<!-- required_output:ch3.required_output.item_06 -->" in result.draft.markdown
    assert "下一步最小验证问题" in result.draft.markdown


def test_chapter_2_missing_performance_renders_evidence_gap() -> None:
    """验证第 2 章收益证据缺失时渲染证据缺口，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺证时未进入 evidence gap 路径时抛出。
    """

    projection = project_chapter_facts(
        replace(
            _bundle(),
            nav_benchmark_performance=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="fixture missing",
            ),
        ),
        chapter_ids=(2,),
    )
    typed_items = (_typed_required_output_item(2, "ch2.required_output.item_01"),)
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=2,
        typed_required_output_items=typed_items,
        evidence_availability=derive_evidence_availability(projection),
    )
    prompt = build_chapter_prompt(input_data)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown_for_prompt(input_data, prompt, anchor_id)
    client = _FakeChapterLLMClient(text)

    result = write_chapter(input_data, llm_client=client)

    assert result.status == "drafted"
    assert result.stop_reason == "none"
    assert result.draft is not None
    assert "<!-- required_output:ch2.required_output.item_01 -->" in result.draft.markdown
    assert "证据不足" in result.draft.markdown
    assert len(client.requests) == 1
    plan = prompt.required_output_evidence_plan[0]
    assert plan.action == "render_evidence_gap"
    assert plan.availability_status == "missing"
    assert plan.missing_evidence_reason == CH2_PERFORMANCE_REASON
    assert f"原因={CH2_PERFORMANCE_REASON}" in prompt.user_prompt


def test_chapter_2_missing_synthesis_renders_minimum_verification_question() -> None:
    """验证第 2 章综合闭环缺证时渲染下一步最小验证问题。"""

    projection = project_chapter_facts(
        replace(
            _bundle(),
            fee_schedule=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="fixture missing",
            ),
        ),
        chapter_ids=(2,),
    )
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=2,
        typed_required_output_items=(_typed_required_output_item(2, "ch2.required_output.item_07"),),
        evidence_availability=derive_evidence_availability(projection),
    )
    prompt = build_chapter_prompt(input_data)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown_for_prompt(input_data, prompt, anchor_id)

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "drafted"
    assert result.stop_reason == "none"
    assert result.draft is not None
    assert "<!-- required_output:ch2.required_output.item_07 -->" in result.draft.markdown
    assert "下一步最小验证问题" in result.draft.markdown
    assert "Alpha 为 2.10%" not in result.draft.markdown
    plan = prompt.required_output_evidence_plan[0]
    assert plan.action == "render_minimum_verification_question"
    assert plan.availability_status == "missing"
    assert plan.missing_evidence_reason == CH2_SYNTHESIS_REASON


def test_chapter_2_missing_availability_envelope_remains_fail_closed() -> None:
    """验证第 2 章 typed item 缺少 EvidenceAvailability envelope 时 fail-closed。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=2,
        typed_required_output_items=(_typed_required_output_item(2, "ch2.required_output.item_01"),),
        evidence_availability=None,
    )
    client = _FakeChapterLLMClient("provider must not be called")

    with pytest.raises(ValueError, match="EvidenceAvailability"):
        write_chapter(input_data, llm_client=client)
    assert client.requests == []


def test_chapter_2_missing_gap_without_gap_phrase_uses_specific_issue_id() -> None:
    """验证第 2 章缺证降级输出不合格时使用 gap-specific issue id。"""

    projection = project_chapter_facts(
        replace(
            _bundle(),
            nav_benchmark_performance=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="fixture missing",
            ),
        ),
        chapter_ids=(2,),
    )
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=2,
        typed_required_output_items=(_typed_required_output_item(2, "ch2.required_output.item_01"),),
        evidence_availability=derive_evidence_availability(projection),
    )
    prompt = build_chapter_prompt(input_data)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = (
        "### 结论要点\n"
        "<!-- required_output:ch2.required_output.item_01 -->\n"
        "- 近 1/3/5 年净值增长率：已根据结构化事实说明。\n"
        "### 详细情况\n"
        "本章只使用结构化 facts，不使用候选 facet 作为断言。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
    )

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "missing_required_output_marker"
    assert any(
        issue.issue_id == "writer:required_output_gap_missing:ch2.required_output.item_01"
        for issue in result.issues
    )
    assert all(
        issue.issue_id != "writer:required_output_block:ch2.required_output.item_01"
        for issue in result.issues
    )
    assert prompt.required_output_evidence_plan[0].action == "render_evidence_gap"


def test_writer_prompt_contains_typed_required_output_ids_not_freeform_fallbacks() -> None:
    """验证 typed writer prompt 使用 stable required output ids 而非自由文本 fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: prompt 未使用 typed item id 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=3,
        typed_required_output_items=(_typed_required_output_item(3, "ch3.required_output.item_05"),),
        evidence_availability=derive_evidence_availability(projection),
    )

    prompt = build_chapter_prompt(input_data)

    assert "<!-- required_output:ch3.required_output.item_05 -->" in prompt.user_prompt
    assert "ch3.required_output.item_05 | 风格稳定性判断" in prompt.user_prompt
    assert "action=render_evidence_gap" in prompt.user_prompt
    assert prompt.required_output_items == ("ch3.required_output.item_05",)
    assert "<!-- required_output:风格稳定性判断 -->" not in prompt.user_prompt


def test_existing_missing_marker_contract_remains_strict() -> None:
    """验证 typed required output path 不放松 existing missing marker contract。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法 missing marker 被 typed path 接受时抛出。
    """

    projection = project_chapter_facts(
        replace(_bundle(), turnover_rate=ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture")),
        chapter_ids=(3,),
    )
    input_data = build_chapter_writer_input(
        projection,
        chapter_id=3,
        typed_required_output_items=(_typed_required_output_item(3, "ch3.required_output.item_05"),),
        evidence_availability=derive_evidence_availability(projection),
    )
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown_for_prompt(input_data, build_chapter_prompt(input_data), anchor_id)
    text = text + "\n<!-- missing:{reason} -->\n"

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "llm_contract_violation"
    assert any(issue.issue_id.startswith("writer:invalid_missing_marker") for issue in result.issues)


def test_writer_prompt_without_missing_reasons_forbids_missing_marker() -> None:
    """验证缺口原因为空时 prompt 明确禁止输出 missing marker。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空缺口原因章节仍诱导 missing marker 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    chapter = replace(projection.chapters[0], missing_reasons=())
    input_data = build_chapter_writer_input(replace(projection, chapters=(chapter,)), chapter_id=1)

    prompt = build_chapter_prompt(input_data)

    assert "MISSING_MARKER_CONTRACT:" in prompt.user_prompt
    assert "ALLOWED_MISSING_REASONS: none" in prompt.user_prompt
    assert "Do not output any missing marker in this chapter." in prompt.user_prompt
    assert "MISSING_MARKER_EXACT_FORM:" not in prompt.user_prompt


def test_writer_prompt_contains_l1_numerical_closure_anchor_rule() -> None:
    """验证第 2 章 writer prompt 含 L1 数字闭环锚点规则，见模板第 2章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 L1 修复指导缺失时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(2,)), chapter_id=2)

    prompt = build_chapter_prompt(input_data)

    assert "第2章 L1 数字闭环安全输出契约" in prompt.user_prompt
    assert "同句或上下2行" in prompt.user_prompt
    assert "不写具体百分比，改写为数据不足/下一步最小验证问题" in prompt.user_prompt
    assert "`### 结论要点` 和 `### 证据与出处` 不得重复无邻近 anchor" in prompt.user_prompt
    assert "来源标签、年报章节名或出处列表不能替代" in prompt.user_prompt
    assert "不得近似或编造" in prompt.user_prompt


def test_non_ch2_writer_prompt_omits_l1_numerical_closure_anchor_rule() -> None:
    """验证非第 2 章不注入 R=A+B-C 专属数字闭环约束。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非第 2 章 prompt 含第 2 章专属规则时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)

    prompt = build_chapter_prompt(input_data)

    assert "第2章 L1 数字闭环安全输出契约" not in prompt.user_prompt
    assert "`### 结论要点` 和 `### 证据与出处` 不得重复无邻近 anchor" not in prompt.user_prompt


def test_compact_prompt_payload_preserves_fact_and_anchor_contract() -> None:
    """验证 compact writer payload 保留事实/锚点边界且不允许引用省略明细。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    chapter = projection.chapters[0]
    large_fact = replace(
        chapter.facts[0],
        value={
            "fund_name": "示例基金",
            "metrics": {"return": "1.23%", "benchmark": "0.45%"},
            "rows": tuple({"period": str(index), "value": index} for index in range(180)),
        },
    )
    compact_input = build_chapter_writer_input(
        replace(projection, chapters=(replace(chapter, facts=(large_fact, *chapter.facts[1:])),)),
        chapter_id=2,
        prompt_payload_mode="compact",
    )
    full_input = build_chapter_writer_input(
        replace(projection, chapters=(replace(chapter, facts=(large_fact, *chapter.facts[1:])),)),
        chapter_id=2,
        prompt_payload_mode="full",
    )

    compact_prompt = build_chapter_prompt(compact_input)
    full_prompt = build_chapter_prompt(full_input)

    assert len(compact_prompt.user_prompt) < len(full_prompt.user_prompt)
    assert large_fact.fact_id in compact_prompt.user_prompt
    assert large_fact.source_field_id in compact_prompt.user_prompt
    assert '"status": "available"' in compact_prompt.user_prompt
    assert "evidence_anchor_ids" in compact_prompt.user_prompt
    assert "value_available_but_detail_compacted" in compact_prompt.user_prompt
    assert "prompt_budget_compaction" in compact_prompt.user_prompt
    assert "top_level_scalar_fields" in compact_prompt.user_prompt
    assert "top_level_list_lengths" in compact_prompt.user_prompt
    assert "top_level_nested_dict_keys" in compact_prompt.user_prompt
    assert "不得引用、复述或推断被省略的 raw detail" in compact_prompt.user_prompt
    assert "section_id" in compact_prompt.user_prompt
    assert "table_id" in compact_prompt.user_prompt
    assert "row_locator" in compact_prompt.user_prompt
    assert "第2章 L1 数字闭环安全输出契约" in compact_prompt.user_prompt
    assert "不写具体百分比，改写为数据不足/下一步最小验证问题" in compact_prompt.user_prompt
    assert "<!-- required_output:<exact required output item> -->" in compact_prompt.user_prompt
    assert "候选 facet 禁止断言形式" in compact_prompt.user_prompt


def test_writer_prompt_cost_diagnostic_is_safe_and_componentized() -> None:
    """验证 writer prompt-cost diagnostic 只含安全成本字段。"""

    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(1,)),
        chapter_id=1,
        prompt_payload_mode="compact",
    )

    prompt = build_chapter_prompt(input_data)
    diagnostic = prompt.prompt_cost_diagnostic

    assert diagnostic is not None
    assert diagnostic.schema_version == "chapter_prompt_cost_diagnostic_payload.v1"
    assert diagnostic.chapter_id == 1
    assert diagnostic.operation == "writer"
    assert diagnostic.system_prompt_chars == len(prompt.system_prompt)
    assert diagnostic.user_prompt_chars == len(prompt.user_prompt)
    assert diagnostic.approx_prompt_tokens == (len(prompt.system_prompt) + len(prompt.user_prompt) + 3) // 4
    assert diagnostic.component_costs.protocol_chars > 0
    assert diagnostic.component_costs.contract_chars > 0
    assert diagnostic.component_costs.facts_chars > 0
    assert diagnostic.component_costs.anchors_chars > 0
    assert diagnostic.fact_cost_rows
    assert diagnostic.anchor_cost_rows
    diagnostic_text = repr(diagnostic)
    assert prompt.system_prompt not in diagnostic_text
    assert prompt.user_prompt not in diagnostic_text
    assert "Authorization" not in diagnostic_text
    assert "Bearer" not in diagnostic_text


def test_writer_blocks_unknown_fund_type() -> None:
    """验证基金类型 unknown 时 writer fail-closed，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unknown 基金类型未阻断时抛出。
    """

    projection = project_chapter_facts(
        replace(_bundle(), basic_identity=_field({"classification_basis": ("fixture",)}, "basic_identity")),
        chapter_ids=(1,),
    )
    input_data = build_chapter_writer_input(projection, chapter_id=1)

    result = write_chapter(input_data, llm_client=None)

    assert result.status == "blocked"
    assert result.stop_reason == "fund_type_unknown"
    assert result.draft is None


def test_writer_blocks_chapter_zero_and_seven_without_accepted_conclusions() -> None:
    """验证第 0/7 章缺 accepted conclusions 时阻断，见模板第 0/7 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0/7 章被错误写作时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(0, 7))

    for chapter_id in (0, 7):
        result = write_chapter(
            build_chapter_writer_input(projection, chapter_id=chapter_id),
            llm_client=None,
        )
        assert result.status == "blocked"
        assert result.stop_reason == "chapter_requires_accepted_conclusions"


def test_prompt_only_does_not_create_fake_draft_and_uses_prompt_only_stop_reason() -> None:
    """验证 prompt_only 不伪造草稿，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt_only 生成 fake draft 或原因错误时抛出。
    """

    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(1,)),
        chapter_id=1,
        mode="prompt_only",
    )

    result = write_chapter(input_data, llm_client=None)

    assert result.status == "blocked"
    assert result.stop_reason == "prompt_only"
    assert result.draft is None


def test_writer_blocks_llm_mode_without_client_after_preflight_passes() -> None:
    """验证 llm 模式且 preflight 通过但无 client 时返回 llm_unavailable。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 client 被假通过时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)

    result = write_chapter(input_data, llm_client=None)

    assert result.status == "blocked"
    assert result.stop_reason == "llm_unavailable"
    assert result.draft is None


def test_writer_blocks_evidence_missing_critical_fact_by_required_by() -> None:
    """验证 required_by 关键 fact 缺锚点时阻断，见模板第 3 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当关键缺锚点 fact 被放行时抛出。
    """

    projection = project_chapter_facts(
        replace(
            _bundle(),
            manager_strategy_text=ExtractedField(
                value={"strategy_summary": "精选个股"},
                anchors=(),
                extraction_mode="direct",
                note=None,
            ),
        ),
        chapter_ids=(3,),
    )

    result = write_chapter(build_chapter_writer_input(projection, chapter_id=3), llm_client=None)

    assert result.status == "blocked"
    assert result.stop_reason == "evidence_anchor_missing"


def test_writer_blocks_evidence_missing_numeric_source_field() -> None:
    """验证数值/source field 缺锚点时阻断，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当数值缺锚点 fact 被放行时抛出。
    """

    projection = project_chapter_facts(
        replace(
            _bundle(),
            fee_schedule=ExtractedField(
                value={"management_fee": 1.2},
                anchors=(),
                extraction_mode="direct",
                note=None,
            ),
        ),
        chapter_ids=(2,),
    )

    result = write_chapter(build_chapter_writer_input(projection, chapter_id=2), llm_client=None)

    assert result.status == "blocked"
    assert result.stop_reason == "evidence_anchor_missing"


def test_write_chapter_with_fake_llm_returns_draft_with_allowed_anchors() -> None:
    """验证 fake LLM 可生成带授权 anchor 的草稿，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法 marker 未生成草稿时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id)

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "drafted"
    assert result.stop_reason == "none"
    assert result.draft is not None
    assert result.draft.used_anchor_ids == (anchor_id,)


def test_writer_parses_valid_anchor_and_missing_markers() -> None:
    """验证 writer 精确解析 anchor 和 missing marker，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 marker 未按契约解析时抛出。
    """

    projection = project_chapter_facts(
        replace(_bundle(), index_profile=ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture")),
        chapter_ids=(1,),
    )
    input_data = build_chapter_writer_input(projection, chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id) + "\n<!-- missing:field_missing -->\n数据不足。"

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.draft is not None
    assert result.draft.used_anchor_ids == (anchor_id,)
    assert result.draft.declared_missing_reasons == ("field_missing",)


def test_writer_rejects_invalid_anchor_marker_spacing_or_case() -> None:
    """验证非法 anchor marker 格式被阻断，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 marker 被接受时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    text = _valid_chapter_markdown(input_data, input_data.chapter.evidence_anchors[0].anchor_id)
    text = text.replace("<!-- anchor:", "<!-- ANCHOR:")

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "llm_contract_violation"


@pytest.mark.parametrize(
    "marker",
    (
        "<!-- missing :field_missing -->",
        "<!-- Missing:field_missing -->",
        "<!-- missing：field_missing -->",
        "<!-- missing:{reason} -->",
    ),
)
def test_writer_rejects_invalid_missing_marker_syntax(marker: str) -> None:
    """验证污染后的 missing marker 语法仍 fail-closed，见模板数据缺口语义。

    Args:
        marker: 待验证的非法 missing marker。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 missing marker 被接受时抛出。
    """

    projection = project_chapter_facts(
        replace(_bundle(), index_profile=ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture")),
        chapter_ids=(1,),
    )
    input_data = build_chapter_writer_input(projection, chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id) + f"\n{marker}\n数据不足。"

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "llm_contract_violation"
    assert result.draft is None
    assert any(issue.issue_id.startswith("writer:invalid_missing_marker") for issue in result.issues)


def test_writer_rejects_empty_llm_response() -> None:
    """验证 LLM 空响应 fail-closed，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空响应未阻断时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(""))

    assert result.status == "blocked"
    assert result.stop_reason == "llm_empty_response"


def test_writer_rejects_response_over_max_output_chars_without_truncation() -> None:
    """验证超长响应按 hard post-check 阻断且不截断，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当超长响应被截断接受时抛出。
    """

    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(1,)),
        chapter_id=1,
        max_output_chars=10,
    )

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient("超过十个字符的章节文本"))

    assert result.status == "blocked"
    assert result.stop_reason == "response_too_long"
    assert result.draft is None


@pytest.mark.parametrize("finish_reason", ("length", "content_filter"))
def test_writer_blocks_incomplete_finish_reason_without_accepting_partial_text(
    finish_reason: str,
) -> None:
    """验证输出不完整或内容过滤时不接受部分文本，见模板第 1 章。

    Args:
        finish_reason: fake provider 结束原因。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不完整输出被接受时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id)

    result = write_chapter(
        input_data,
        llm_client=_FakeChapterLLMClient(text, finish_reason=finish_reason),
    )

    assert result.status == "blocked"
    assert result.stop_reason == "response_incomplete"
    assert result.draft is None


def test_writer_blocks_missing_required_body_section_before_audit() -> None:
    """验证缺固定结构段落在 writer parser 阶段阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺结构段落未被分类阻断时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id).replace("### 详细情况\n", "")

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "missing_required_structure"


def test_writer_blocks_missing_required_output_marker_before_audit() -> None:
    """验证缺 required output marker 在 writer parser 阶段阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 marker 未被分类阻断时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    item = input_data.chapter.contract.required_output_items[0]
    text = _valid_chapter_markdown(input_data, anchor_id).replace(
        f"<!-- required_output:{item} -->\n",
        "",
    )

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "missing_required_output_marker"


def test_writer_rejects_forbidden_trading_advice() -> None:
    """验证禁用交易建议被 writer 阻断，见模板第 7 章边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当禁用交易建议被接受时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id) + "\n建议买入。"

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "llm_contract_violation"


def test_writer_rejects_unknown_anchor_reference() -> None:
    """验证未知 anchor marker 被阻断，见模板证据锚点规范。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知 anchor 被接受时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    text = _valid_chapter_markdown(input_data, "unknown-anchor")

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "unknown_anchor"


def test_writer_rejects_unknown_missing_reason_marker() -> None:
    """验证未知 missing marker 被阻断，见模板数据缺口语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知 missing reason 被接受时抛出。
    """

    input_data = build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(1,)), chapter_id=1)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown(input_data, anchor_id) + "\n<!-- missing:unknown_reason -->"

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "llm_contract_violation"


def test_writer_reports_bond_risk_internal_anchor_message() -> None:
    """验证债券风险内部组级锚点错误消息明确，见模板第 6 章核心风险。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误消息未说明组级锚点未展开时抛出。
    """

    projection = project_chapter_facts(_bundle(fund_type="bond_fund"), chapter_ids=(6,))
    input_data = build_chapter_writer_input(projection, chapter_id=6)
    text = _valid_chapter_markdown(input_data, "bond-risk:110011:2024:duration_rate_risk:1")

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert "组级锚点未展开" in result.issues[0].message


def test_ch6_prompt_forbids_synthesized_bond_risk_anchor_ids() -> None:
    """验证第 6 章 prompt 明确禁止合成债券风险内部锚点，见模板第 6 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 未说明内部锚点不可引用时抛出。
    """

    projection = project_chapter_facts(_bundle(fund_type="bond_fund"), chapter_ids=(6,))
    input_data = build_chapter_writer_input(projection, chapter_id=6)

    prompt = build_chapter_prompt(input_data)

    assert "禁止根据 fact_id、source_field_id、source_field_name 或 fact value 自行合成 anchor id" in prompt.user_prompt
    assert "bond_risk_evidence 内部/组级 anchors 不是 ChapterEvidenceAnchor" in prompt.user_prompt
    assert "只有“允许 anchors”列表中的 anchor_id 可引用" in prompt.user_prompt
    assert "允许 anchors" in prompt.user_prompt


def test_writer_rejects_synthesized_bond_risk_source_field_anchor() -> None:
    """验证第 6 章合成的 bond_risk_evidence anchor 仍被 fail-closed 阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合成锚点被错误接受时抛出。
    """

    projection = project_chapter_facts(_bundle(fund_type="bond_fund"), chapter_ids=(6,))
    input_data = build_chapter_writer_input(projection, chapter_id=6)
    synthesized_anchor_id = "chapter-anchor:110011:2024:ch6:structured.bond_risk_evidence"
    text = _valid_chapter_markdown(input_data, synthesized_anchor_id)

    result = write_chapter(input_data, llm_client=_FakeChapterLLMClient(text))

    assert result.status == "blocked"
    assert result.stop_reason == "unknown_anchor"
    assert "组级锚点未展开" in result.issues[0].message


def test_repair_context_is_rendered_into_writer_prompt_without_extra_payload() -> None:
    """验证 typed repair context 进入 prompt，且不使用 extra payload。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重写上下文未显式渲染时抛出。
    """

    repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("programmatic:C2:item",),
        previous_messages=("缺少 required output marker",),
        required_corrections=("补齐 required output marker。",),
    )
    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(1,)),
        chapter_id=1,
        repair_context=repair_context,
    )

    prompt = build_chapter_prompt(input_data)

    assert prompt.user_prompt.startswith("先遵守输出协议，后写内容：")
    assert "每个 required_output_items 先复制 exact marker" in prompt.user_prompt
    assert "每个 required item 后写 1-3 句" in prompt.user_prompt
    assert "attempt_index=1" in prompt.user_prompt
    assert "programmatic:C2:item" in prompt.user_prompt
    assert "补齐 required output marker" in prompt.user_prompt
    assert "extra_payload" not in ChapterLLMRequest.__dataclass_fields__


def test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt() -> None:
    """验证第 5 章 repair attempt 渲染 forbidden phrase 局部清单，见模板第 5 章当前阶段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 未渲染第 5 章 forbidden phrase repair 清单时抛出。
    """

    repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("llm:parse_failure",),
        previous_messages=("auditor 行协议解析失败。",),
        required_corrections=("修复 auditor line protocol 输出。",),
    )
    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(5,)),
        chapter_id=5,
        repair_context=repair_context,
    )

    prompt = build_chapter_prompt(input_data)

    assert "第5章 forbidden phrase repair 必须改写规则" in prompt.user_prompt
    assert "交易动作建议" in prompt.user_prompt
    assert "仓位动作" in prompt.user_prompt
    assert "收益预测" in prompt.user_prompt
    assert "基金经理动机推断" in prompt.user_prompt
    assert "值得持有 / 需要关注 / 建议替换" in prompt.user_prompt
    assert "下一步最小验证问题" in prompt.user_prompt
    assert "extra_payload" not in ChapterLLMRequest.__dataclass_fields__


def test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair() -> None:
    """验证第 5 章 forbidden phrase repair 清单不泄漏到初始 attempt 或其他章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 5 章 repair 清单在非目标场景泄漏时抛出。
    """

    repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("llm:parse_failure",),
        previous_messages=("auditor 行协议解析失败。",),
        required_corrections=("修复 auditor line protocol 输出。",),
    )

    initial_ch5 = build_chapter_prompt(
        build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(5,)), chapter_id=5)
    )
    ch1_repair = build_chapter_prompt(
        build_chapter_writer_input(
            project_chapter_facts(_bundle(), chapter_ids=(1,)),
            chapter_id=1,
            repair_context=repair_context,
        )
    )
    ch6_repair = build_chapter_prompt(
        build_chapter_writer_input(
            project_chapter_facts(_bundle(), chapter_ids=(6,)),
            chapter_id=6,
            repair_context=repair_context,
        )
    )

    assert "第5章 forbidden phrase repair 必须改写规则" not in initial_ch5.user_prompt
    assert "第5章 forbidden phrase repair 必须改写规则" not in ch1_repair.user_prompt
    assert "第5章 forbidden phrase repair 必须改写规则" not in ch6_repair.user_prompt


def test_invalid_anchor_repair_context_renders_exact_marker_correction() -> None:
    """验证 invalid anchor repair context 渲染精确 marker 修正文本。"""

    repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("writer:invalid_anchor_marker:17",),
        previous_messages=("anchor marker 格式非法。",),
        required_corrections=(
            "使用精确 anchor marker 语法 `<!-- anchor:<anchor_id> -->`；"
            "只使用 allowed anchor IDs；删除 malformed 或 synthesized anchor comments；"
            "bond_risk_evidence 内部/组级 anchors 未列入 allowed anchors 时不得引用。",
        ),
    )
    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(6,)),
        chapter_id=6,
        repair_context=repair_context,
    )

    prompt = build_chapter_prompt(input_data)

    assert "attempt_index=1" in prompt.user_prompt
    assert "writer:invalid_anchor_marker:17" in prompt.user_prompt
    assert "`<!-- anchor:<anchor_id> -->`" in prompt.user_prompt
    assert "allowed anchor IDs" in prompt.user_prompt
    assert "malformed 或 synthesized anchor comments" in prompt.user_prompt
    assert "bond_risk_evidence" in prompt.user_prompt
    assert "extra_payload" not in ChapterLLMRequest.__dataclass_fields__


def test_ch2_l1_repair_context_renders_local_anchor_placement_checklist() -> None:
    """验证第 2 章 L1 repair attempt 渲染局部锚点放置清单，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 未渲染 L1 专用清单时抛出。
    """

    repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("programmatic:L1:line:10:fixture",),
        previous_messages=("R=A+B-C 数字闭环缺少邻近 anchor marker。",),
        required_corrections=("修复第2章 R=A+B-C 数字闭环。",),
    )
    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(2,)),
        chapter_id=2,
        repair_context=repair_context,
    )

    prompt = build_chapter_prompt(input_data)

    assert "第2章 L1 repair 必须改写规则" in prompt.user_prompt
    assert "先删除上一轮无邻近 anchor 的具体数字闭环断言" in prompt.user_prompt
    assert "只有确认 allowed `<!-- anchor:<anchor_id> -->` 支撑该具体数值时" in prompt.user_prompt
    assert "同一句或上下2行" in prompt.user_prompt
    assert "R/A/B/C/A-C" in prompt.user_prompt
    assert "不确定时写数据不足或下一步最小验证问题，且不写具体百分比" in prompt.user_prompt
    assert "输出前逐行自查 R/A/B/C/A-C/Alpha/Beta/Cost/%" in prompt.user_prompt
    assert "缺少邻近 allowed anchor 的行必须改写为缺口或验证问题" in prompt.user_prompt
    assert "extra_payload" not in ChapterLLMRequest.__dataclass_fields__


def test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context() -> None:
    """验证第 2 章 L1 repair checklist 不泄漏到初始 attempt、其他章节或非 L1 repair。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 checklist 在非目标场景泄漏时抛出。
    """

    l1_repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("programmatic:L1:line:10:fixture",),
        previous_messages=("R=A+B-C 数字闭环缺少邻近 anchor marker。",),
        required_corrections=("修复第2章 R=A+B-C 数字闭环。",),
    )
    non_l1_repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("programmatic:C2:item",),
        previous_messages=("缺少 required output marker。",),
        required_corrections=("补齐 required output marker。",),
    )

    initial_ch2 = build_chapter_prompt(
        build_chapter_writer_input(project_chapter_facts(_bundle(), chapter_ids=(2,)), chapter_id=2)
    )
    ch1_l1_repair = build_chapter_prompt(
        build_chapter_writer_input(
            project_chapter_facts(_bundle(), chapter_ids=(1,)),
            chapter_id=1,
            repair_context=l1_repair_context,
        )
    )
    ch2_non_l1_repair = build_chapter_prompt(
        build_chapter_writer_input(
            project_chapter_facts(_bundle(), chapter_ids=(2,)),
            chapter_id=2,
            repair_context=non_l1_repair_context,
        )
    )

    assert "第2章 L1 repair 必须改写规则" not in initial_ch2.user_prompt
    assert "第2章 L1 repair 必须改写规则" not in ch1_l1_repair.user_prompt
    assert "第2章 L1 repair 必须改写规则" not in ch2_non_l1_repair.user_prompt


def test_llm_request_carries_typed_repair_context() -> None:
    """验证 LLM request 携带 typed repair context。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 request 未携带重写上下文时抛出。
    """

    repair_context = ChapterRepairContext(
        attempt_index=1,
        previous_issue_ids=("llm:parse_failure",),
        previous_messages=("行协议错误",),
        required_corrections=("按 auditor 行协议修复。",),
    )
    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(1,)),
        chapter_id=1,
        repair_context=repair_context,
    )
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    client = _FakeChapterLLMClient(_valid_chapter_markdown(input_data, anchor_id))

    result = write_chapter(input_data, llm_client=client)

    assert result.status == "drafted"
    assert client.requests[0].repair_context == repair_context


def test_writer_does_not_import_repository_source_service_dayu_or_openai() -> None:
    """静态验证 writer 不导入仓库、来源、Service、dayu 或 provider SDK。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当模块 import 越界时抛出。
    """

    imports = _imports_for(Path("fund_agent/fund/chapter_writer.py"))
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


def _valid_chapter_markdown(input_data: object, anchor_id: str) -> str:
    """构造满足最小结构和 required items 的章节 Markdown。

    Args:
        input_data: `ChapterWriterInput`。
        anchor_id: 要嵌入的 anchor id。

    Returns:
        测试用章节 Markdown。

    Raises:
        AttributeError: 当输入不是 writer input 时抛出。
    """

    chapter = input_data.chapter
    required_lines = "\n".join(
        f"<!-- required_output:{item} -->\n- {item}: 已根据结构化事实说明。"
        for item in chapter.contract.required_output_items
    )
    return (
        "### 结论要点\n"
        f"{required_lines}\n"
        "### 详细情况\n"
        "本章只使用结构化 facts，不使用候选 facet 作为断言。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
    )


def _valid_chapter_markdown_for_prompt(input_data: object, prompt: object, anchor_id: str) -> str:
    """按当前 prompt.required_output_items 构造测试章节 Markdown。

    Args:
        input_data: `ChapterWriterInput`。
        prompt: `ChapterWriterPrompt`。
        anchor_id: 要嵌入的 anchor id。

    Returns:
        测试用章节 Markdown。

    Raises:
        AttributeError: 输入对象不符合 writer prompt/input 契约时抛出。
    """

    required_lines = "\n".join(
        f"<!-- required_output:{item} -->\n- {item}: 证据不足，当前缺少已复核证据，不能据此判断。下一步最小验证问题：复核年报披露。"
        for item in prompt.required_output_items
    )
    return (
        "### 结论要点\n"
        f"{required_lines}\n"
        "### 详细情况\n"
        "本章只使用结构化 facts，不使用候选 facet 作为断言。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
    )


def _typed_required_output_item(chapter_id: int, item_id: str) -> RequiredOutputItem:
    """按 typed item id 读取 required output item。

    Args:
        chapter_id: 公开章节编号。
        item_id: typed required output item id。

    Returns:
        匹配的 `RequiredOutputItem`。

    Raises:
        AssertionError: 未找到对应 item 时抛出。
    """

    chapter = load_typed_template_contract_manifest().chapters[chapter_id]
    for item in chapter.required_output_items:
        if item.item_id == item_id:
            return item
    raise AssertionError(f"missing typed required output item: {item_id}")


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
