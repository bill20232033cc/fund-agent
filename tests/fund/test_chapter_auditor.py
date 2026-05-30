"""Gate 2 章节审计 primitive 测试，覆盖基金分析模板第 0-7 章。"""

from __future__ import annotations

import ast
from pathlib import Path

from fund_agent.fund.chapter_auditor import (
    ChapterAuditInput,
    ChapterAuditLLMRequest,
    ChapterAuditLLMResponse,
    audit_chapter,
    audit_chapter_llm,
    audit_chapter_programmatic,
)
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    build_chapter_writer_input,
)
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
) -> ChapterAuditInput:
    """构造章节审计输入。

    Args:
        chapter_id: 模板章节编号。
        markdown_suffix: 附加 Markdown。
        used_anchor_ids: 显式草稿 anchor ids。

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
    markdown = _valid_markdown(writer_input, anchor_ids[0] if anchor_ids else "") + markdown_suffix
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
    required_lines = "\n".join(f"- {item}: 已根据结构化事实说明。" for item in chapter.contract.required_output_items)
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
