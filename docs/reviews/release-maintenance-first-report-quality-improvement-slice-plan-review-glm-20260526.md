# Gate C First Report-Quality Improvement Slice Plan Review — AgentGLM

> Date: 2026-05-26
> Reviewer: AgentGLM
> Review type: Gate C plan review (read-only, no source/test/README/control-doc modification, no commit/push/PR)
> Target: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md`

## Truth Sources Used

- `AGENTS.md`
- `docs/design.md` v2.2 — especially §5.4 / §5.4.1 / §5.4.2 / §5.4.3
- `docs/implementation-control.md` v2.0 — Startup Packet / Current Truth Guardrails / Current Gate / Next Entry Point
- Gate A: `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md`
- Gate B: `docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md`
- Quasi-real evidence: `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`
- Quasi-real controller judgment: `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md`
- Retrospective controller judgment: `docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md`
- Source code inspected read-only:
  - `fund_agent/fund/template/contracts.py` — Chapter 3 contract confirmed: 6 `must_answer`, 3 `must_not_cover`, 6 `required_output_items`; no explicit missing-evidence blocking clause
  - `fund_agent/fund/audit/contract_rules.py` — Chapter 3 rules confirmed: all 6 are `covered_by_required_item`; no `evidence_confirm` or `structured_data_availability` route; no missing-evidence wording coverage
  - `fund_agent/fund/report_evidence.py` — `ReportDataGapOverride` confirmed: has `required_report_wording: str` but no dedicated next-validation-question field
  - `tests/fund/test_report_evidence.py` — Existing data-gap test confirmed: uses `ReportDataGapOverride(field_path="turnover_rate", required_report_wording="当前 slice 未复核换手率，不能据此判断风格稳定")`; test only asserts gap_id existence, not projected `required_report_wording` content
  - `docs/fund-analysis-template-draft.md` — Chapter 3 CHAPTER_CONTRACT confirmed: 6 must_answer, 3 must_not_cover, 6 required_output_items; no missing-evidence wording constraint

## Verdict

**PASS_WITH_FINDINGS**

All five review dimensions pass. Findings are informational only. No blocking or material issues found.

## Review Dimensions

### 1. Slice Selection: Is active_fund Chapter 3 turnover/style-consistency data-gap wording contract the minimum high-value slice for the current phase?

**PASS.**

Evidence chain is sufficient and same-source:

| Evidence source | What it proves | Same-source? |
|---|---|---|
| Gate A | `004393` / 2024 / `active_fund` is the clean near-term candidate; Chapter 3 turnover/style-consistency gap is the main active-fund risk | Yes — reads accepted Gate A artifact |
| Gate B | Minimum active-fund verifier case is Chapter 3 manager holding traceability pass + turnover/style-consistency gap; first owner is `chapter_contract` | Yes — reads accepted Gate B artifact |
| Quasi-real bundle evidence | Turnover-rate fact coverage: material issue, field `turnover_rate`, data gap `not_reviewed_in_current_slice`, next owner `chapter_contract` | Yes — reads accepted quasi-real evidence |
| Quasi-real controller judgment | Explicitly recommended next gate as active-fund Chapter 3 turnover/style-consistency contract wording | Yes — reads accepted controller judgment |
| Source code verification | Chapter 3 contract currently asks "风格稳定性判断" and mentions "换手率" as parenthetical, but has no explicit wording that missing/unreviewed evidence must block stability claims | Yes — direct code read |
| Existing test precedent | `test_extraction_mode_missing_produces_data_gap_ref` already uses wording text `当前 slice 未复核换手率，不能据此判断风格稳定` | Yes — direct test read |

This is the only material quasi-real report-quality issue currently accepted by the evidence chain. The plan correctly identifies it as the smallest high-value fix because:

- It addresses exactly one accepted material issue (turnover/style-consistency data gap).
- It is a Fund-layer contract hardening slice that does not require renderer, extraction, or product-flow changes.
- It has same-source implementation precedent (existing `ReportDataGapOverride` test).
- No other slice candidate would be smaller or higher value given the accepted evidence.

The alternatives table correctly rejects 9 alternatives with evidence-grounded reasoning. Each rejection traces back to accepted Gate A/B/controller-judgment conclusions.

### 2. Implementation Specificity: Is the plan specific enough for an implementation agent to execute without re-design?

**PASS.**

The plan provides:

| Specificity dimension | Provided in plan | Assessment |
|---|---|---|
| Target files | 9 files listed with explicit change descriptions | Sufficient |
| Contract intent | 4-point semantic description of what Chapter 3 must enforce | Sufficient — direction is clear, exact Chinese wording delegated to implementation |
| Implementation constraints | "Keep `_EXPECTED_CHAPTER_IDS`, chapter ids, titles, lens keys, and supported fund types unchanged" | Sufficient |
| Audit coverage route | "Prefer `narrative_guidance` for semantic claim-safety wording" | Sufficient — matches existing pattern in `contract_rules.py` line 271-275 |
| Test names | Named test function: `test_active_fund_chapter_3_contract_requires_reviewed_turnover_or_style_change_before_stability_claim()` | Sufficient |
| Test assertions | Specified at level of "assert Chapter 3 `must_answer` / `must_not_cover` / `required_output_items` contain the new wording" | Sufficient |
| Acceptance commands | Exact `pytest`, `ruff`, `git diff --check` commands | Sufficient |
| Boundary checks | Exact `rg` commands to verify no leakage into excluded files | Sufficient |
| Stop conditions | 7 explicit stop conditions | Sufficient |

The implementation agent has enough guidance from:
1. The plan's 4-point contract intent
2. The existing code precedent (`ReportDataGapOverride` with `required_report_wording`)
3. The existing test precedent (`test_extraction_mode_missing_produces_data_gap_ref` with wording `当前 slice 未复核换手率，不能据此判断风格稳定`)
4. The existing `narrative_guidance` pattern in `contract_rules.py`

No re-design is needed at implementation time.

### 3. Scope Exclusion: Does the plan correctly exclude renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, durable baseline, and production extraction?

**PASS.**

The plan's scope exclusion is thorough and correct:

| Excluded scope | Plan section | Correct? |
|---|---|---|
| renderer.py | Explicitly out of scope list | Yes |
| FQ0-FQ6 / quality_gate.py | Explicitly out of scope list | Yes |
| Service/CLI defaults | Explicitly out of scope list | Yes |
| Host/Agent/dayu | Explicitly out of scope list | Yes |
| Durable baseline | Explicitly out of scope list | Yes |
| Production extraction | Explicitly out of scope list | Yes |
| FundDocumentRepository | Explicitly out of scope list | Yes |
| PDF/cache/source helpers | Explicitly out of scope list | Yes |
| Fixtures / tracked reports | Explicitly out of scope list | Yes |
| Default analyze/checklist behavior | Explicitly out of scope list | Yes |

The boundary check commands include `rg` patterns for `dayu.host`, `dayu.engine`, `FundDocumentRepository`, `quality_gate`, `FQ0`, `FQ6`, and excluded directories. The stop conditions correctly require returning to controller/review if any excluded area must be touched.

This aligns with `AGENTS.md` Current Non-Goals and `docs/implementation-control.md` Next Entry Point constraints.

### 4. Test Matrix and README/Design Sync: Does the plan satisfy AGENTS.md requirements?

**PASS.**

Test matrix:

| Test file | Plan specifies | AGENTS.md compliance |
|---|---|---|
| `tests/fund/template/test_contracts.py` | New test with specific assertions for Chapter 3 active-fund contract changes | Sufficient — covers contract integrity |
| `tests/fund/audit/test_audit_programmatic.py` | Coverage count update + new `narrative_guidance` assertion | Sufficient — covers audit rule completeness |
| `tests/fund/test_report_evidence.py` | Strengthen existing turnover data-gap override test with insufficiency wording and next-validation-question assertions | Sufficient — covers evidence/gap integrity |
| `tests/fund/test_report_quality_validation.py` | Optional only if wording serialization requires it | Appropriate — plan correctly identifies this as conditional |

README/design sync:

| Doc | Plan specifies | AGENTS.md compliance |
|---|---|---|
| `fund_agent/fund/README.md` | Minimal sync if Fund source changes require it | Compliant — matches AGENTS.md §触发更新规则 |
| `docs/design.md` | Only update if implementation changes template structure or accepted design truth | Compliant — matches AGENTS.md design truth discipline |
| `docs/fund-analysis-template-draft.md` | Mirror Chapter 3 CHAPTER_CONTRACT block with same semantic wording | Compliant — keeps human template and machine contract aligned |

The plan correctly records that a narrow wording clarification may not require `docs/design.md` structural update, and specifies recording the rationale in the implementation artifact if no design change is needed.

### 5. Blocker/Material Ambiguity: Is there ambiguity that would prevent safe implementation, especially around the wording-only contract risk?

**PASS_WITH_INFORMATIONAL_FINDINGS.** No blocker or material ambiguity found. See findings below.

The core risk — that wording-only contract change does not directly improve real report output — is explicitly acknowledged and correctly scoped:

- Section "Why This Slice First" states: "It improves real report safety by preventing a common false inference."
- Section "Risks And Mitigations" row 3 explicitly addresses "Data-gap wording is mistaken for renderer output change."
- Section "Residuals After This Slice" explicitly states: "Renderer still may not emit the new wording in current product reports until a later renderer/report-writing gate authorizes product output changes."

This risk is correctly handled as a residual, not a blocker. The contract hardening makes the next code-generation task precise and testable, which is the stated gate objective.

## Findings

### F1 — Informational: `ReportDataGapOverride` has no structured next-validation-question field

**Observation:** `ReportDataGapOverride` has `required_report_wording: str` but no dedicated field for a next-validation-question. The plan says "add or refine a required output item equivalent to: data insufficiency and next minimum validation question when turnover/style-change evidence is missing or unreviewed." If the next-validation-question text needs to be projected as a separate structured field, the current `ReportDataGapOverride` cannot carry it without embedding it as a convention inside `required_report_wording`.

**Plan's handling:** The plan explicitly says "Do not require a new extraction field unless the current `ReportDataGapOverride` cannot carry the wording." This is an acceptable delegation to implementation.

**Recommendation:** Implementation agent should embed both insufficiency wording and next-validation-question text in `required_report_wording` as a single composed string, matching the existing pattern. If a later gate needs the next-validation-question as a separate queryable field, that would be a separate `ReportDataGapOverride` schema extension with its own review.

### F2 — Informational: Existing data-gap test does not assert projected `required_report_wording` content

**Observation:** `test_extraction_mode_missing_produces_data_gap_ref` constructs a `ReportDataGapOverride` with `required_report_wording="当前 slice 未复核换手率，不能据此判断风格稳定"`, but only asserts that the gap_id exists and is back-referenced from the fact. It does not assert that `required_report_wording` is projected into the resulting `ReportDataGap` or that the wording text is preserved.

**Plan's handling:** The plan says "Strengthen the existing turnover data-gap override test so required report wording explicitly says no style-stability/style-consistency claim may be made and names the next minimum validation question."

**Recommendation:** Implementation agent should add an assertion that the projected `ReportDataGap` preserves the `required_report_wording` value. If `ReportDataGap` does not currently carry `required_report_wording` as a projected field, the implementation gate should add that projection and its test.

### F3 — Informational: Plan's suggested contract intent is English; implementation agent will produce Chinese wording

**Observation:** The plan provides English-language contract intent descriptions (e.g., "stability / style-consistency claims require reviewed turnover-rate or reviewed style-change evidence"). The implementation agent will need to translate these into exact Chinese contract strings in `contracts.py`, `contract_rules.py`, and `fund-analysis-template-draft.md`.

**Assessment:** This is acceptable. The implementation agent has sufficient guidance from:
1. The existing Chinese contract strings in Chapter 3 (e.g., "风格稳定性判断：跨期风格是否漂移？")
2. The existing test precedent wording ("当前 slice 未复核换手率，不能据此判断风格稳定")
3. The existing `narrative_guidance` pattern in `contract_rules.py`

No ambiguity results; Chinese wording choices are implementation-time decisions guided by existing patterns.

### F4 — Informational: Provenance wording for quasi-real evidence identity status

**Observation:** The retrospective controller judgment accepted AgentGLM's informational finding that future gates should preserve provenance wording for S0-derived `identity_status="verified_annual_report"` so it is not misread as a new repository verification claim. The plan references the quasi-real evidence but does not explicitly address provenance labeling.

**Assessment:** Non-blocking. The plan is a contract-wording gate, not an evidence-generation gate. If the implementation gate produces new evidence bundles, provenance labeling should follow the retrospective guidance.

## Open Questions

None. All material questions are resolved by the accepted evidence chain and the plan's explicit scope boundaries.

## Residual Risks

| Risk | Severity | Mitigation in plan | Assessment |
|---|---|---|---|
| Wording-only contract does not change real report output | Informational | Explicitly stated in Residuals section; renderer change is a separate future gate | Adequate — this is the correct sequencing |
| Exact Chinese wording choices may break audit coverage counts | Informational | Step 4 says "Update coverage routes and tests in the same implementation gate" | Adequate — same-gate alignment |
| `ReportDataGapOverride` may need schema extension for structured next-validation-question | Informational | Plan says "Do not require a new extraction field unless current model cannot carry the wording" | Adequate — defers schema change unless proven necessary |
| Contract wording becomes too broad and blocks legitimate Chapter 3 judgments | Informational | Plan says "Keep wording narrow: active-fund stability/style-consistency claims only; manager holding traceability remains separate" | Adequate — scope is constrained to the accepted issue |

## Controller Recommendation

Accept this plan as Gate C. The plan is:

1. **Evidence-grounded:** Slice selection traces directly through Gate A → Gate B → quasi-real evidence → controller judgment → source code verification.
2. **Minimal:** It is the smallest possible fix addressing the only accepted material quasi-real issue.
3. **Specific enough for implementation:** File targets, contract intent, test guidance, acceptance commands, boundary checks, and stop conditions are all provided.
4. **Correctly scoped:** All excluded areas (renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, durable baseline, extraction) are explicitly listed and protected by boundary checks.
5. **Honest about residual risk:** The plan does not claim product-visible improvement; it claims contract hardening that makes the next task precise.

Four informational findings should be tracked by the implementation agent:
- F1: Use `required_report_wording` composition for next-validation-question text
- F2: Assert projected `required_report_wording` preservation in data-gap tests
- F3: Chinese wording choices guided by existing contract patterns
- F4: Provenance labeling if implementation produces new evidence bundles

## Validation

Read-only commands used in this review:

```text
cat docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md
cat AGENTS.md
cat docs/design.md
cat docs/implementation-control.md
cat docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md
cat docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md
cat docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md
cat docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md
# Source code verification via sub-agent:
# fund_agent/fund/template/contracts.py (Chapter 3 contract)
# fund_agent/fund/audit/contract_rules.py (Chapter 3 coverage rules)
# fund_agent/fund/report_evidence.py (ReportDataGapOverride)
# tests/fund/test_report_evidence.py (data-gap override test)
# docs/fund-analysis-template-draft.md (Chapter 3 CHAPTER_CONTRACT)
```

No source, test, README, control-doc, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, tracked report, commit, push, PR, or destructive git operation was performed.
