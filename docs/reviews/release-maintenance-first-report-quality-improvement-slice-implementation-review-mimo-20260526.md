# Gate D Implementation Review: AgentMiMo — 2026-05-26

## Scope

Review target: current uncommitted diff for `active_fund` Chapter 3 turnover/style-consistency data-gap wording contract implementation.

No source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, report output, commit, push, PR, or destructive git work was performed in this review.

## Truth Sources Consulted

- `AGENTS.md`
- `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §5.4.3
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
- Accepted plan: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md`
- Controller judgment: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-controller-judgment-20260526.md`

## Verdict

**PASS_WITH_FINDINGS**

## Findings

### F1 (Minor, Non-blocking): Template draft includes `required_output_items` entry but runtime contract defers it

**Location**: `docs/fund-analysis-template-draft.md` (Chapter 3 `required_output_items`), `tests/fund/template/test_contracts.py:283`

The accepted plan (step 2) says to add `换手率/风格变化证据缺口说明与下一步最小验证问题` to `required_output_items` in the template draft. The diff correctly adds it to `docs/fund-analysis-template-draft.md` but does NOT add it to `fund_agent/fund/template/contracts.py` runtime `required_output_items`. The test at line 283 explicitly asserts `not in chapter.required_output_items`.

This is the correct safe-option application per the controller judgment's mandatory Gate D preflight: adding a `ContractRequiredItemRule` that current renderer cannot satisfy would make `run_programmatic_audit()` fail in default `fund-analysis analyze`. The implementation correctly defers the runtime rule to a later renderer/report-writing gate.

The minor gap is that the template draft (human truth) is now stricter than the runtime contract (machine truth) for `required_output_items`. A future implementer copying template entries to runtime might inadvertently add the deferred item. The test guards against this, but the asymmetry should be noted.

**Recommendation**: No action required for this gate. The test correctly enforces the boundary. Document the template-vs-runtime asymmetry in the next renderer/report-writing gate planning.

### F2 (Informational): No `must_answer_coverages` count assertion in coverage manifest test

**Location**: `tests/fund/audit/test_audit_programmatic.py:901`

The existing test asserts `len(coverage_manifest.must_not_cover_coverages) == 25` (updated from 24), but there is no corresponding count assertion for `must_answer_coverages`. The two modified `must_answer` entries change `question_text` in-place without changing the count. If a coverage rule were accidentally removed or duplicated, the count assertion would not catch it.

The test does verify the specific new strings are present (lines 931-946), which provides targeted coverage. The `fails_closed` tests also guard manifest integrity.

**Recommendation**: Non-blocking. Consider adding a `must_answer_coverages` count assertion in a future robustness pass.

## Review Checklist

### 1. Does implementation match accepted exact wording and safe-option preflight?

**PASS.** All four wording changes match the plan's exact strings:

| Plan entry | Diff location | Match |
|---|---|---|
| `must_answer` modify: `言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。` | `contracts.py:369`, `contract_rules.py:429`, `template-draft.md` | Exact |
| `must_answer` modify: `风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。` | `contracts.py:370`, `contract_rules.py:435`, `template-draft.md` | Exact |
| `must_not_cover` add: `不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。` | `contracts.py:377`, `contract_rules.py:278`, `template-draft.md` | Exact |
| `required_report_wording` in report_evidence test | `test_report_evidence.py:277-281` | Exact |

The safe-option preflight is correctly applied:
- No `ContractRequiredItemRule` added to runtime (`test_audit_programmatic.py:926-930` asserts absence)
- `must_answer` coverage routes keep existing `required_item_texts` tuples unchanged
- `ContractMustNotCoverCoverageRule` added with `coverage_kind="narrative_guidance"`, not `ContractForbiddenContentRule`

### 2. Does it avoid product default behavior changes?

**PASS.** No new runtime `ContractRequiredItemRule` that current renderer cannot satisfy. No renderer, FQ0-FQ6, Service/CLI, or product-flow changes. Boundary `rg` confirms no forbidden references (`dayu.host`, `dayu.engine`, `FundDocumentRepository`, etc.) in changed source files.

### 3. Are tests sufficient and aligned with AGENTS.md rules?

**PASS.** All new tests follow AGENTS.md requirements:
- Chinese docstrings with `Args`, `Returns`, `Raises` sections
- Test function names describe the contract being verified
- Focused assertions on exact wording, lens priority, and fund-type coverage
- Fail-closed guard test (`test_active_fund_chapter_3_gap_contract_does_not_add_unconditional_required_item`) prevents safe-option regression
- Report evidence test asserts `required_report_wording` preservation through projection

All 83 focused tests pass. Ruff clean. `git diff --check` clean.

### 4. Template/contracts sync, audit coverage, required_report_wording preservation

**PASS.** Template draft → contracts.py → contract_rules.py update order is preserved. Wording is identical across all three files. `required_report_wording` in `ReportDataGapOverride` preserves the full insufficiency + next-validation-question sentence. Audit coverage manifest updates from 24 → 25 `must_not_cover_coverages` with correct `narrative_guidance` kind.

### 5. Boundary: no renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/repository/source/fixture/report output changes

**PASS.** Changed files exactly match the plan's allowed list:

```
docs/fund-analysis-template-draft.md
fund_agent/fund/README.md
fund_agent/fund/audit/contract_rules.py
fund_agent/fund/template/contracts.py
tests/fund/audit/test_audit_programmatic.py
tests/fund/template/test_contracts.py
tests/fund/test_report_evidence.py
```

No out-of-scope files touched. `git diff -- renderer/services/ui/quality_gate/extraction_score/documents` is empty.

## Open Questions

None. The implementation matches the accepted plan with no ambiguity.

## Residual Risks

| Risk | Severity | Owner |
|---|---|---|
| Template draft `required_output_items` is stricter than runtime contract; future implementer might copy deferred item to runtime | Low | Next renderer/report-writing gate |
| No `must_answer_coverages` count assertion in coverage manifest test | Informational | Future robustness pass |
| Renderer still does not emit the new wording in product reports | Expected | Future renderer/report-writing gate |
| Turnover/style-change extraction may still be incomplete | Expected | Future data/source extraction gate |

## Controller Recommendation

**Accept.** The implementation correctly applies the accepted plan and mandatory safe-option preflight. The two findings are minor/informational and do not block acceptance. The diff is clean, tests pass, boundaries are preserved, and the contract wording hardening achieves its goal: preventing unsupported style-stability/style-consistency/言行一致 claims when turnover or style-change evidence is missing or unreviewed.
