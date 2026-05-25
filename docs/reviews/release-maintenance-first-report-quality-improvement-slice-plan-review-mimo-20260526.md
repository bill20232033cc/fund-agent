# Gate C Plan Review: First Report-Quality Improvement Slice Plan

> Date: 2026-05-26
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md`
> Scope: plan review only. No source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixtures, run-output, commit, push, PR, or destructive git work.

## Truth Sources Consulted

- `AGENTS.md`
- `docs/design.md` v2.2 §3.2, §5.2, §5.4, §5.4.1, §5.4.3
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Current Decisions / Open Residuals
- Gate A: `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md`
- Gate B: `docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md`
- Quasi-real evidence: `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md`
- Quasi-real retrospective: `docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md`
- Current code (read-only):
  - `fund_agent/fund/template/contracts.py` — Chapter 3 contract at lines 361-437
  - `fund_agent/fund/audit/contract_rules.py` — Chapter 3 required_item_rules at lines 160-165, must_not_cover coverage rules, must_answer coverage rules at lines 413-423
  - `tests/fund/test_report_evidence.py` — existing turnover data-gap override test at lines 258-287
  - `docs/fund-analysis-template-draft.md` — Chapter 3 CHAPTER_CONTRACT at lines 463-522

---

## Verdict

**PASS_WITH_FINDINGS**

---

## Review Scope Confirmation

The five review questions asked by the controller:

| # | Question | Verdict |
|---|----------|---------|
| 1 | Is the active_fund Chapter 3 turnover/style-consistency data-gap wording contract directly supported by Gate A/B/quasi-real evidence? | **Yes** |
| 2 | Is the plan code-generation-ready (files, functions, tests, commands, stop conditions)? | **Partially** — see F1, F2, F3 |
| 3 | Does the plan stay in-scope and avoid renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, durable baseline, production extraction? | **Yes** |
| 4 | Is the root cause bound to same-source evidence, not indirect evidence? | **Yes** |
| 5 | Are there blocker/material ambiguities, especially dual truth sources, audit coverage route, README/design sync rules? | **Material** — see F2, F3, F4 |

---

## Findings

### F1 — Material: Plan specifies intent but not exact contract wording strings

The plan says:

> "replace or extend the `must_answer` entries ... so active-fund style-consistency claims require reviewed turnover or style-change evidence"
> "add a `must_not_cover` item equivalent to: do not infer style stability or言行一致性 from missing, unavailable, or unreviewed turnover/style-change evidence"
> "add or refine a required output item equivalent to: data insufficiency and next minimum validation question"

This describes the *semantic goal* but not the *exact Chinese strings* that the implementer must insert into `contracts.py` and `docs/fund-analysis-template-draft.md`. The plan is a Gate C *implementation plan*, not a Gate B *design-only* artifact. For it to be code-generation-ready, it must either:

(a) specify the exact wording to add/modify, or
(b) specify a narrow wording protocol (e.g., "use the exact phrase `当前 slice 未复核换手率/风格变化，不能据此判断风格稳定或言行一致；数据不足时必须输出下一步最小验证问题`") with clear insertion points.

Without this, two implementers could produce materially different contract strings, and the audit coverage route mapping would be ambiguous.

**Severity**: Material
**Recommendation**: Add an "Exact Wording" subsection that specifies the literal `must_answer` additions/modifications, `must_not_cover` addition, and `required_output_items` addition. The existing test at `test_report_evidence.py:277` (`required_report_wording="当前 slice 未复核换手率，不能据此判断风格稳定"`) provides a validated wording anchor that should be referenced.

### F2 — Material: Audit coverage route for new must_not_cover is underspecified

The plan says:

> "Add a new `ContractMustNotCoverCoverageRule` if the new `must_not_cover` item is semantic and not reliably checkable by fixed marker. Do not add a `ContractForbiddenContentRule` unless there is a stable forbidden marker with low false-positive risk. The likely correct route is `narrative_guidance`."

This is directionally correct but leaves the implementer uncertain about:

1. Whether to add to `_FORBIDDEN_CONTENT_RULES` (programmatic marker) or `_MUST_NOT_COVER_COVERAGE_RULES` (narrative_guidance). The plan says "likely `narrative_guidance`" but does not commit.
2. The `_validate_must_not_cover_coverage_rules()` function cross-checks that every `must_not_cover` item is covered by *either* a `ContractForbiddenContentRule` *or* a `ContractMustNotCoverCoverageRule`. If a new `must_not_cover` item is added to the contract, one of these two lists must be updated or the fail-closed validation will break.
3. The `contract_rules.py` validation logic at lines 658-701 enforces this completeness check. The plan should confirm which list to update.

**Severity**: Material
**Recommendation**: Commit to `narrative_guidance` (the plan already says "likely correct route") and state explicitly: "Add one `ContractMustNotCoverCoverageRule` entry to `_MUST_NOT_COVER_COVERAGE_RULES` in `contract_rules.py` with `coverage_kind='narrative_guidance'` and a rationale explaining why the new prohibition cannot be reliably checked by fixed marker."

### F3 — Material: `must_answer` / `required_output_items` coverage route update is vague

Step 4 says:

> "In `fund_agent/fund/audit/contract_rules.py`, update affected `ContractMustAnswerCoverageRule` strings to match the new manifest strings."

But it does not specify *which* existing Chapter 3 `must_answer` coverage rules change. Looking at current code:

- Line 421: `ContractMustAnswerCoverageRule(3, "言行一致性判断：说的和做的一样吗？", "covered_by_required_item", ("言行一致性判断",))`
- Line 422: `ContractMustAnswerCoverageRule(3, "风格稳定性判断：跨期风格是否漂移？", "covered_by_required_item", ("风格稳定性判断",))`

If the plan modifies the `must_answer` text for "风格稳定性判断" to add the turnover/style-change evidence precondition, the coverage rule's `question_text` must change to match. If the plan adds a *new* `must_answer` question (not just modifies existing ones), a new coverage rule must be added. If the plan adds a *new* `required_output_item`, a new `ContractRequiredItemRule` with a marker must be added to `_REQUIRED_ITEM_RULES`.

The plan should specify: does it modify existing items, or add new ones? This determines whether the implementer patches existing rules or adds new entries.

**Severity**: Material
**Recommendation**: State explicitly whether the implementation modifies the existing "风格稳定性判断" must_answer/required_output_items text, or adds new items. If modifying, list the exact old and new strings. If adding, provide the new item text, its marker, and its coverage route.

### F4 — Minor: Dual truth-source sync protocol is acknowledged but not operationalized

The plan correctly identifies `contracts.py` and `docs/fund-analysis-template-draft.md` as dual truth sources and says to "mirror the same Chapter 3 CHAPTER_CONTRACT block with exactly the same semantic wording." However:

1. The `contracts.py` source is machine-consumed (dataclass tuples), while the template draft is human-readable Markdown comments.
2. The `validate_template_contract_manifest()` function in `contracts.py` validates internal consistency but does *not* cross-validate against the template draft.
3. There is no automated check that the two are in sync.

The plan should state which is the *authoritative* source for the implementation gate. `AGENTS.md` says `docs/fund-analysis-template-draft.md` contains the CHAPTER_CONTRACT mechanism, and `contracts.py` says it sources from the template draft. So the template draft is the human truth, and `contracts.py` is the machine truth. The plan should specify: update the template draft *first*, then mirror into `contracts.py`.

**Severity**: Minor
**Recommendation**: Add one sentence: "Update `docs/fund-analysis-template-draft.md` Chapter 3 CHAPTER_CONTRACT first (human truth), then mirror the same wording into `contracts.py` (machine truth)."

### F5 — Minor: `docs/design.md` update decision is ambiguous

The plan says:

> "Only update if the implementation changes template structure or accepted design truth. A narrow wording clarification that restates §5.4.3 missing-fact downgrade may not require design change."

Adding new `must_answer` / `must_not_cover` / `required_output_items` to Chapter 3 *is* a template structure change, even if narrow. `docs/design.md` §3.2 describes the CHAPTER_CONTRACT mechanism and lists its fields. If the implementation adds a new evidence-precondition pattern to `must_answer` or `must_not_cover`, the design doc's description of Chapter 3 contract behavior (§5.4.3) should note this as current fact.

However, the plan's conservative approach ("may not require design change") is acceptable if the implementation artifact explicitly justifies the skip. This is informational, not blocking.

**Severity**: Minor
**Recommendation**: In the implementation artifact, if `docs/design.md` is not updated, record the justification: "Narrow wording addition to existing Chapter 3 contract; §5.4.3 missing-fact downgrade pattern already covers the general case; no new mechanism or structural change."

---

## Scope Compliance

| Boundary | Status | Evidence |
|----------|--------|----------|
| Renderer (`fund_agent/fund/template/renderer.py`) | Not touched | Plan explicitly excludes |
| FQ0-FQ6 (`fund_agent/fund/quality_gate.py`, `extraction_score.py`) | Not touched | Plan explicitly excludes |
| Service/CLI defaults | Not touched | Plan explicitly excludes |
| Host/Agent/dayu | Not touched | Plan explicitly excludes |
| Durable baseline / fixtures | Not touched | Plan explicitly excludes |
| Production extraction / `FundDocumentRepository` | Not touched | Plan explicitly excludes |
| PDF/cache/source helpers, downloaders, source adapters | Not touched | Plan explicitly excludes |
| Default `fund-analysis analyze` / `fund-analysis checklist` behavior | Not touched | Plan explicitly excludes |

The plan's out-of-scope list is comprehensive and correctly aligned with the control doc's Current Non-Goals.

---

## Evidence Chain Assessment

The plan's evidence chain is direct and sufficient:

1. **Gate A** → selected `004393`/2024/`active_fund` as clean candidate; identified Chapter 3 turnover/style-consistency gap as main active-fund risk.
2. **Gate B** → classified the minimum active-fund verifier case as Chapter 3 manager holding traceability pass plus turnover/style-consistency gap issue; assigned `chapter_contract` as first owner; deferred `data/source extraction`.
3. **Quasi-real evidence** → one manually assembled bundle with no validator issues and two score issue rows: manager holding traceability (pass), turnover-rate fact coverage (material issue, field `turnover_rate`, data gap `not_reviewed_in_current_slice`, next owner `chapter_contract`).
4. **Controller judgment** → explicitly recommended the next gate as active-fund Chapter 3 turnover/style-consistency contract wording.
5. **Current code** → `contracts.py` Chapter 3 requires turnover rate and consistency/style-stability judgments but has no explicit wording for missing/unreviewed evidence blocking stability claims.
6. **Same-source precedent** → `test_report_evidence.py:277` already tests the exact data-gap override pattern with `required_report_wording="当前 slice 未复核换手率，不能据此判断风格稳定"`.

The root cause (unsupported stability/style-consistency claims when turnover evidence is missing/unreviewed) is bound to direct quasi-real evidence, not indirect inference. The plan correctly rejects the `needs-more-evidence` path.

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | What are the exact Chinese strings for the new/modified `must_answer`, `must_not_cover`, and `required_output_items`? | **Open** — plan should specify or reference a validated wording anchor |
| 2 | Does the implementation modify existing Chapter 3 items or add new ones? | **Open** — determines whether audit coverage rules are patched or extended |
| 3 | Is the new `must_not_cover` routed through `ContractForbiddenContentRule` (programmatic marker) or `ContractMustNotCoverCoverageRule` (narrative_guidance)? | **Open** — plan says "likely narrative_guidance" but should commit |
| 4 | Which is the authoritative source for the implementation: template draft or `contracts.py`? | **Open** — minor; plan should specify update order |

---

## Residual Risks

| Residual | Severity | Required handling |
|----------|----------|-------------------|
| Contract wording becomes too broad and blocks legitimate Chapter 3 judgments. | Low | Keep wording narrow: active-fund stability/style-consistency claims only; manager holding traceability remains separate. Plan already states this. |
| Exact Chinese string changes break audit coverage counts. | Low | Update coverage routes and tests in the same implementation gate; preserve fail-closed manifest validation. Plan already states this. |
| Renderer still may not emit the new wording in current product reports. | Low | Expected residual; later renderer/report-writing gate will authorize product output changes. Plan correctly identifies this. |
| `docs/fund-analysis-template-draft.md` and `contracts.py` drift apart after the implementation. | Low | Update template draft first, then mirror; record in implementation artifact. |
| The slice could accidentally become validator schema work. | Low | Plan correctly guards against this: only touch validator tests if current consumer cannot preserve the wording. |

---

## Controller Recommendation

**Accept the plan with targeted amendments.** The plan's selection, evidence basis, scope boundaries, stop conditions, and acceptance commands are sound. The findings are all addressable without re-opening the gate:

1. **F1** (exact wording): Add an "Exact Wording" subsection or reference the validated anchor at `test_report_evidence.py:277`.
2. **F2** (audit route): Commit to `narrative_guidance` for the new `must_not_cover` item and state which list in `contract_rules.py` to update.
3. **F3** (coverage route detail): Specify whether existing items are modified or new items are added, and provide the exact old/new strings.
4. **F4** (update order): Add one sentence specifying template-draft-first-then-contracts.py order.
5. **F5** (design doc): Informational only; no action required if implementation artifact records justification.

These amendments can be applied to the plan artifact directly, or they can be deferred to the implementation gate as explicit decisions documented in the implementation artifact. The controller should decide whether to amend the plan or accept with findings-as-implementation-guidance.

If the controller accepts with findings-as-implementation-guidance, the implementation gate should treat F1-F4 as mandatory pre-implementation decisions and record them in the implementation artifact before writing code.
