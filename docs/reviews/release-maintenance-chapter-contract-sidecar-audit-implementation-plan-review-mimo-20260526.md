# Implementation Plan Review: Chapter Contract Sidecar + Dev-only Report-writing Audit

> Date: 2026-05-26
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md`
> Truth sources: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted design plan `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md`, controller judgment `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-controller-judgment-20260526.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## Evidence Checked

| Check | Source | Result |
|---|---|---|
| Implementation file paths exist or are correctly new | `fund_agent/fund/template/` listing, `fund_agent/fund/` listing | `chapter_contract_constraints.py` and `report_writing_audit.py` do not exist yet; test files do not exist yet. Correct: plan says "Add". |
| Existing `ChapterContract` is frozen dataclass | `contracts.py:46` | Confirmed: `@dataclass(frozen=True, slots=True)`. Plan correctly states "Do not modify the frozen ChapterContract dataclass." |
| `load_template_contract_manifest()` returns 8 chapters 0-7 | `contracts.py:764` + `_EXPECTED_CHAPTER_IDS = tuple(range(8))` | Confirmed. Plan correctly requires sidecar chapter ids to match. |
| `ReportEvidenceBundle` has `data_gaps`, `facts`, `evidence_anchors`, `score_issue_links` | `report_evidence.py:610-652` | Confirmed. Plan correctly identifies these as audit inputs. |
| `ReportDataGap` has `required_report_wording` field | `report_evidence.py:366` | Confirmed. Plan correctly requires Chapter 3 audit to consume/reference this. |
| `ReportDataGapOverride` has `required_report_wording` field | `report_evidence.py:562` | Confirmed. Plan correctly ties override wording to audit. |
| `DataGapReasonCode` includes `not_reviewed_in_current_slice` | `report_evidence.py:135` | Confirmed. Plan's allowed gap reasons are compatible. |
| `DataGapReasonCode` includes `unsupported_stability_claim` | `report_evidence.py:142` | Confirmed. Existing domain already covers the stability claim gap. |
| `report_quality_validation.py` exists and is separate from audit | File listing | Confirmed. Plan correctly keeps validator on schema/content integrity, audit on semantic claim safety. |
| `scripts/report_quality_eval.py` exists as maintainer-only | File listing + header | Confirmed. Plan correctly marks it optional/deferrable. |
| Existing template test files | `tests/fund/template/` listing | `test_contracts.py`, `test_item_rules.py`, `test_lens_application.py`, `test_renderer.py` exist. Plan adds `test_chapter_contract_constraints.py` — no conflict. |
| Controller judgment accepts sidecar design | Controller judgment §Gate B | Confirmed: "dev-only executable sidecar over existing ChapterContract, not a replacement and not a parallel truth source." |
| Controller judgment accepts first slice scope | Controller judgment §Gate C | Confirmed: "Fund-layer executable CHAPTER_CONTRACT sidecar plus dev-only report-writing audit, centered on active-fund Chapter 3 claim safety." |
| Controller judgment closes all prior findings | Controller judgment §Review Findings Judgment | Confirmed: all 14 findings accepted and closed, MiMo/GLM re-reviews both `PASS`. |
| `docs/design.md` §3.2 describes CHAPTER_CONTRACT mechanism | `design.md:146-163` | Confirmed. Plan correctly scopes design.md sync to narrow current-code-fact update. |
| `AGENTS.md` prohibits renderer/Service/CLI/FQ0-FQ6 changes without gate | `AGENTS.md` boundary rules | Confirmed. Plan's prohibited files list aligns. |
| `implementation-control.md` Next Entry Point matches plan gate | `implementation-control.md:208` | Confirmed: "Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation gate." |

---

## Findings Ordered by Severity

### F1 [Minor] `FailureCategory` literal domain in plan includes `deferred_extraction_requirement` but existing `report_evidence.py` domain does not

**Location**: Plan §2.2, suggested `FailureCategory` literal.

**Evidence**: Plan defines `FailureCategory` with `"deferred_extraction_requirement"` as one of 7 values. Existing `GapFailureCategory` in `report_evidence.py:117-132` does not include this value. The sidecar's `FailureCategory` is a new domain specific to the writing audit, not the same as `GapFailureCategory`. This is acceptable — the sidecar defines its own failure categories for audit output, separate from the evidence bundle gap categories.

**Disposition**: Informational. No action required. The plan correctly distinguishes sidecar audit failure categories from evidence bundle gap failure categories. Implementation worker should document this distinction in the module docstring.

### F2 [Minor] `RequirementSeverity` includes `config_only` but `ReportWritingAuditIssue.severity` does not

**Location**: Plan §2.2 vs §3.3.

**Evidence**: Plan §2.2 defines `RequirementSeverity = Literal["blocking", "material", "informational", "config_only"]`. Plan §3.3 defines `ReportWritingAuditIssue.severity` as `Literal["blocking", "material", "minor", "informational"]` — no `"config_only"`. Chapter 2/6 deferred requirements use `severity="informational"` or `severity="config_only"` in the sidecar, but when emitted as audit issues, they map to `"informational"`. The plan does not explicitly state this mapping.

**Disposition**: Minor ambiguity. Implementation worker should either: (a) add `"config_only"` to `ReportWritingAuditIssue.severity`, or (b) explicitly map `config_only` sidecar requirements to `informational` audit issues. The plan's intent is clear (deferred requirements produce informational findings only), but the severity mapping should be explicit in implementation.

### F3 [Minor] `ChapterDraftSurrogate.markdown` claim detection strategy not specified

**Location**: Plan §3.2, chapter draft surrogate input.

**Evidence**: Plan defines `ChapterDraftSurrogate` with `markdown: str` and `claim_tags: tuple[str, ...]`. For the active Chapter 3 first slice, the audit must detect "stability / style consistency / 言行一致 positive claim" in the draft. The plan does not specify whether claim detection is keyword-based, tag-based, or hybrid. The test `test_active_chapter_3_turnover_missing_blocks_stability_claim` says the draft "asserts '风格稳定' or '言行一致'" — suggesting keyword detection — but the plan does not commit to this approach.

**Disposition**: Minor. Implementation worker needs to make a concrete choice. Keyword-based detection for a small set of Chinese phrases is reasonable for a dev-only audit. The plan should have stated this explicitly, but the test guidance provides enough signal for implementation.

### F4 [Informational] `fund_agent/fund/quality_gate_integration.py` not listed in prohibited files

**Location**: Plan §1.4 "Files Explicitly Out of Scope."

**Evidence**: Plan §1.4 lists `fund_agent/fund/quality_gate.py` but not `fund_agent/fund/quality_gate_integration.py`. The design plan §3.2 prohibited files list also omits it. However, `implementation-control.md:224` and the controller judgment both explicitly prohibit changing `quality_gate.py` and quality gate behavior. `quality_gate_integration.py` is a quality gate integration module — modifying it would violate the "not change FQ0-FQ6" constraint.

**Disposition**: Informational. The omission is harmless because the plan's boundary rg command (`rg -n "quality_gate"` in the acceptance commands) would catch any import from quality_gate modules. Implementation worker should not touch this file regardless.

### F5 [Informational] `docs/design.md` sync scope references §3.2 but the design plan says §5.4

**Location**: Plan §1.3, controller judgment §Gate C.

**Evidence**: The controller judgment says "revise §3.2 to state that CHAPTER_CONTRACT now has a dev-only sidecar/wrapper audit layer." The design plan §2.6 says the same. This is consistent. The implementation plan's §1.3 says "若实现成功且 controller 允许文档同步，最小同步只可能是 `fund_agent/fund/README.md` 和 `docs/design.md` 的 current-code-fact 更新" — which is correct but less specific than the controller judgment about which section. Not a blocking issue.

**Disposition**: Informational. Implementation worker should follow the controller judgment's specific instruction to update §3.2.

### F6 [Informational] `ReportEvidenceBundle.fund_type_slot` can be `None` but sidecar requires `FundType | Literal["default"]`

**Location**: Plan §2.2 `fund_type_slot` field vs `report_evidence.py:645`.

**Evidence**: `ReportEvidenceBundle.fund_type_slot: FundType | None = None`. The sidecar's `ChapterExecutableConstraint.fund_type_slot: FundType | Literal["default"]` does not include `None`. When the audit consumes a bundle with `fund_type_slot=None`, the sidecar must fall back to `"default"` constraints. The plan's §2.3 says "All chapters 0-7 must have at least one default ChapterExecutableConstraint" — which handles this case. The audit function should resolve `None` to `"default"` before matching.

**Disposition**: Informational. Implementation worker should add explicit `None -> "default"` resolution in the audit function. The plan's design supports this but does not call it out explicitly.

---

## Adversarial Failure Pass

| Challenge | Evidence | Disposition |
|---|---|---|
| Could the sidecar become a parallel truth source for chapter titles? | Plan §2.1: "sidecar is wrapper over existing ChapterContract, not replacement, not parallel truth source." Test `test_sidecar_wraps_existing_chapter_contract_without_parallel_truth` verifies. | Safe. |
| Could Chapter 2/6 deferred requirements produce false positive material findings? | Plan §2.3/§4.2: "severity informational/config only," "deferred=True," "tests only assert configuration exists and is not material/blocking." | Safe. |
| Could the audit accidentally import renderer or quality gate? | Plan §3.1 explicit "must not" list. Acceptance command `rg` checks for forbidden imports. | Safe. |
| Could the sidecar fail to preserve existing 8 chapter ids? | Test `test_sidecar_covers_all_chapter_ids_0_to_7` loads both manifests and asserts match. | Safe. |
| Could `ChapterDraftSurrogate` become a new rendering path? | Plan §3.2: "This is not product renderer output and not a new rendering path." It is a test/dev helper only. | Safe. |
| Could the audit produce findings that leak into product quality gate? | Plan §3.1: "emit findings only." Plan §1.4 prohibits touching quality_gate.py. No wiring into FQ0-FQ6. | Safe. |
| Could `scripts/report_quality_eval.py` integration change product CLI? | Plan §1.3: "optional and deferrable," "Do not register product CLI." | Safe. |
| Could the first slice fail to cover active Chapter 3 material behavior? | Plan §4.1 specifies 4 detection cases with expected results. Tests §5.1 cover all 4 cases. | Safe. |
| Could stop conditions miss a boundary violation? | Plan §7 lists 8 stop conditions covering renderer, FQ0-FQ6, Service/CLI, FundDocumentRepository, Host/Agent/dayu, parallel extraction, chapter id preservation, and doc-before-code. | Comprehensive. |

---

## Overcoupling Check

The plan does not introduce coupling between the sidecar/audit and any product-flow module. The sidecar wraps existing `ChapterContract` by reference (chapter ids, must_answer/must_not_cover strings), not by inheritance or direct mutation. The audit consumes `ReportEvidenceBundle` as an explicit input, not by reaching into extraction or document layers. No new dependencies on renderer, Service, CLI, Host, Agent, dayu, or document repository.

---

## Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready. All 6 findings are minor or informational. None block implementation. The plan correctly:

- Defines implementation files (2 source, 2 test) with clear scope
- Specifies sidecar as wrapper over existing `ChapterContract`, not parallel truth
- Defines dev-only audit inputs (`ReportEvidenceBundle`, JSONL, `ChapterDraftSurrogate`) and outputs (`ReportWritingAuditResult`) clearly
- Limits first material slice to active_fund chapter_3 claim safety
- Maintains strict no-modify boundary for renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/FundDocumentRepository
- Provides sufficient acceptance commands (focused tests, adjacent tests, ruff, whitespace, boundary diff, boundary rg)
- Lists comprehensive stop conditions (8 conditions)

The implementation worker should address F2 (explicit severity mapping for `config_only` -> `informational`) and F3 (claim detection strategy) during implementation. F1, F4, F5, F6 are informational observations that do not require plan changes.
