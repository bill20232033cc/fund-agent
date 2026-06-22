"""Evidence Confirm no-live 语义蕴含复核测试。"""

from __future__ import annotations

import ast
import inspect
from dataclasses import replace

import fund_agent.fund.evidence_confirm_semantic as semantic_module
from fund_agent.fund.chapter_facts import (
    ChapterFactEntry,
    ChapterFactInput,
    project_chapter_facts,
)
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmReference,
    confirm_chapter_evidence_v2,
)
from fund_agent.fund.evidence_confirm_semantic import (
    EVIDENCE_CONFIRM_SEMANTIC_SCHEMA_VERSION,
    EvidenceEntailmentJudgment,
    EvidenceEntailmentRequest,
    EvidenceSemanticClaim,
    confirm_semantic_entailment,
)
from tests.fund.test_chapter_facts import _bundle


class _FakeEntailmentClient:
    """测试用语义蕴含 client。"""

    def __init__(self, judgment: object) -> None:
        """保存待返回 judgment。

        Args:
            judgment: 调用 ``judge()`` 时返回的对象。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.judgment = judgment
        self.requests: list[EvidenceEntailmentRequest] = []

    def judge(self, request: EvidenceEntailmentRequest) -> object:
        """记录请求并返回预设 judgment。

        Args:
            request: 语义蕴含请求。

        Returns:
            预设 judgment。

        Raises:
            无显式抛出。
        """

        self.requests.append(request)
        return self.judgment


class _RaisingEntailmentClient:
    """测试用异常 client。"""

    def __init__(self) -> None:
        """初始化调用记录。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.requests: list[EvidenceEntailmentRequest] = []

    def judge(self, request: EvidenceEntailmentRequest) -> EvidenceEntailmentJudgment:
        """记录请求后抛出异常。

        Args:
            request: 语义蕴含请求。

        Returns:
            不返回。

        Raises:
            RuntimeError: 始终抛出，验证 fail-closed。
        """

        self.requests.append(request)
        raise RuntimeError("secret provider details must not leak")


def test_semantic_entailed_passes_after_deterministic_v2_pass() -> None:
    """验证 deterministic V2 通过后 entailed claim 产生 pass。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(
            status="entailed",
            reason_code="entailed_by_excerpt",
            message="bounded excerpt supports claim",
        )
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert result.schema_version == EVIDENCE_CONFIRM_SEMANTIC_SCHEMA_VERSION
    assert result.overall_status == "pass"
    assert result.claim_results[0].status == "entailed"
    assert result.claim_results[0].severity == "info"
    assert result.claim_results[0].matched_anchor_ids == fact.evidence_anchor_ids
    assert len(client.requests) == 1
    assert client.requests[0].excerpt_texts == ("年报披露换手率为 120%。",)


def test_semantic_contradicted_blocks() -> None:
    """验证 contradicted claim 产生 fail。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(
            status="contradicted",
            reason_code="contradicted_by_excerpt",
            message="claim contradicts excerpt",
        )
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率没有披露。"),),
        client=client,
    )

    assert result.overall_status == "fail"
    assert result.claim_results[0].status == "contradicted"
    assert result.claim_results[0].severity == "block"
    assert result.claim_results[0].reason_code == "contradicted_by_excerpt"


def test_semantic_insufficient_warns() -> None:
    """验证 insufficient claim 产生 warn。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(
            status="insufficient",
            reason_code="insufficient_excerpt_support",
        )
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率显著升高。"),),
        client=client,
    )

    assert result.overall_status == "warn"
    assert result.claim_results[0].status == "insufficient"
    assert result.claim_results[0].severity == "warn"


def test_semantic_not_applicable_for_blank_claim_without_client_call() -> None:
    """验证空 claim 不调用 client 并返回 not_applicable。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(status="entailed", reason_code="entailed_by_excerpt")
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "   "),),
        client=client,
    )

    assert result.overall_status == "not_applicable"
    assert result.claim_results[0].status == "not_applicable"
    assert result.claim_results[0].reason_code == "missing_claim"
    assert client.requests == []


def test_semantic_does_not_call_client_when_deterministic_value_match_fails() -> None:
    """验证 value_match fail 时 semantic client 不会被调用。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报只披露管理费率 1.20%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(status="entailed", reason_code="entailed_by_excerpt")
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert result.overall_status == "fail"
    assert result.claim_results[0].status == "insufficient"
    assert result.claim_results[0].severity == "block"
    assert result.claim_results[0].reason_code == "deterministic_gate_failed"
    assert client.requests == []


def test_semantic_does_not_call_client_when_candidate_only_reference_fails_proof_boundary() -> None:
    """验证 candidate-only proof_boundary fail 时 semantic client 不会被调用。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            candidate_only=True,
        ),
    )
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(status="entailed", reason_code="entailed_by_excerpt")
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert result.overall_status == "fail"
    assert result.claim_results[0].reason_code == "deterministic_gate_failed"
    assert client.requests == []


def test_semantic_malformed_client_result_fails_closed() -> None:
    """验证非法 client 返回 fail-closed。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(object())

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert result.overall_status == "fail"
    assert result.claim_results[0].status == "insufficient"
    assert result.claim_results[0].severity == "block"
    assert result.claim_results[0].reason_code == "malformed_client_result"
    assert len(client.requests) == 1


def test_semantic_client_exception_fails_closed_without_exception_message() -> None:
    """验证 client 异常 fail-closed 且不泄漏异常详情。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _RaisingEntailmentClient()

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert result.overall_status == "fail"
    assert result.claim_results[0].reason_code == "client_exception"
    assert result.claim_results[0].message == "semantic entailment client 抛出异常。"
    assert "secret provider details" not in (result.claim_results[0].message or "")
    assert len(client.requests) == 1


def test_semantic_anchor_precision_warn_keeps_warn_severity_for_entailed() -> None:
    """验证 deterministic anchor_precision warn 会保留 semantic warn gate。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            page_number=None,
            row_locator=None,
        ),
    )
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(status="entailed", reason_code="entailed_by_excerpt")
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert evidence_result.overall_status == "warn"
    assert result.overall_status == "warn"
    assert result.claim_results[0].status == "entailed"
    assert result.claim_results[0].severity == "warn"
    assert len(client.requests) == 1


def test_semantic_not_applicable_stays_info_under_anchor_precision_warn() -> None:
    """验证 not_applicable 不被 anchor_precision warn 抬升为 warning。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            page_number=None,
            row_locator=None,
        ),
    )
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(status="not_applicable", reason_code="not_applicable")
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率披露为 120%。"),),
        client=client,
    )

    assert evidence_result.overall_status == "warn"
    assert result.overall_status == "not_applicable"
    assert result.claim_results[0].status == "not_applicable"
    assert result.claim_results[0].severity == "info"
    assert len(client.requests) == 1


def test_semantic_aggregate_warns_when_claim_insufficient() -> None:
    """验证 aggregate status 能表示 insufficient warning。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),)
    evidence_result = confirm_chapter_evidence_v2(chapter, references)
    client = _FakeEntailmentClient(
        EvidenceEntailmentJudgment(
            status="insufficient",
            reason_code="insufficient_excerpt_support",
        )
    )

    result = confirm_semantic_entailment(
        evidence_result=evidence_result,
        references=references,
        claims=(_claim(fact, "换手率明显高于同类。"),),
        client=client,
    )

    assert result.overall_status == "warn"
    assert result.claim_results[0].severity == "warn"


def test_semantic_module_import_isolated_from_service_provider_host_renderer_quality_gate() -> None:
    """验证 semantic 模块没有导入跨层依赖。"""

    source = inspect.getsource(semantic_module)
    tree = ast.parse(source)
    imported_modules = set()
    forbidden_prefixes = (
        "fund_agent.services",
        "fund_agent.host",
        "fund_agent.ui",
        "fund_agent.config",
        "fund_agent.fund.documents",
        "fund_agent.fund.pdf",
        "fund_agent.fund.template.renderer",
        "fund_agent.fund.quality_gate",
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported_modules
        for prefix in forbidden_prefixes
    )


def _chapter_and_fact(source_field_id: str) -> tuple[ChapterFactInput, ChapterFactEntry]:
    """读取只含目标 fact 的测试章节。

    Args:
        source_field_id: 目标 source field id。

    Returns:
        只含目标 fact 的章节和 fact。

    Raises:
        AssertionError: 测试 fixture 未包含目标 fact 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    chapter = projection.chapters[0]
    fact = next(item for item in chapter.facts if item.source_field_id == source_field_id)
    anchor_ids = set(fact.evidence_anchor_ids)
    anchors = tuple(anchor for anchor in chapter.evidence_anchors if anchor.anchor_id in anchor_ids)
    return replace(chapter, facts=(fact,), evidence_anchors=anchors), fact


def _claim(fact: ChapterFactEntry, claim_text: str) -> EvidenceSemanticClaim:
    """构造测试 semantic claim。

    Args:
        fact: 章节事实。
        claim_text: claim 文本。

    Returns:
        semantic claim。

    Raises:
        无显式抛出。
    """

    return EvidenceSemanticClaim(
        claim_id=f"claim:{fact.fact_id}",
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        claim_text=claim_text,
        anchor_ids=fact.evidence_anchor_ids,
    )


def _reference(
    anchor_id: str,
    *,
    excerpt_text: str,
    reference_kind: str = "annual_report_excerpt",
    source_kind: str = "annual_report",
    document_year: int | None = 2024,
    page_number: int | None = 12,
    section_id: str | None = "§2",
    table_id: str | None = None,
    row_locator: str | None = None,
    candidate_only: bool = False,
    source_truth_status: str = "proven",
) -> EvidenceConfirmReference:
    """构造测试 reference。

    Args:
        anchor_id: anchor id。
        excerpt_text: 同源摘录。
        reference_kind: reference kind。
        source_kind: source kind。
        document_year: 文档年份。
        page_number: 页码。
        section_id: 章节。
        table_id: 表格 id。
        row_locator: 行定位。
        candidate_only: 是否 candidate-only。
        source_truth_status: source truth 状态。

    Returns:
        Evidence Confirm reference。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmReference(
        anchor_id=anchor_id,
        reference_kind=reference_kind,  # type: ignore[arg-type]
        source_kind=source_kind,
        document_year=document_year,
        section_id=section_id,
        page_number=page_number,
        table_id=table_id,
        row_locator=row_locator,
        excerpt_text=excerpt_text,
        candidate_only=candidate_only,
        source_truth_status=source_truth_status,  # type: ignore[arg-type]
    )
