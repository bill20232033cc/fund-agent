# Gate C First Report-Quality Improvement Slice Plan

> Date: 2026-05-26
> Worker: AgentCodex planning specialist
> Scope: code-generation-ready implementation plan only. No source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, run-output, commit, push, PR, destructive git, annual-report fetch, annual-report parse, `FundDocumentRepository`, PDF/cache/source helper, downloader, or source-adapter work was performed in this gate.

## Truth Sources

- `AGENTS.md`
- `docs/design.md` current design sections, especially current architecture boundary and `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §5.4.3.
- `docs/implementation-control.md` Startup Packet / Current Truth Guardrails / Current Gate / Next Entry Point.
- Gate A: `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md`.
- Gate B: `docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md`.
- Quasi-real evidence and controller judgments:
  - `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md`
  - `docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md`
- Current implementation facts inspected read-only:
  - `fund_agent/fund/template/contracts.py`
  - `fund_agent/fund/template/item_rules.py`
  - `fund_agent/fund/audit/contract_rules.py`
  - `fund_agent/fund/report_evidence.py`
  - `fund_agent/fund/report_quality_validation.py`
  - `tests/fund/template/test_contracts.py`
  - `tests/fund/audit/test_audit_programmatic.py`
  - `tests/fund/test_report_evidence.py`
  - `tests/fund/test_report_quality_validation.py`
  - `docs/fund-analysis-template-draft.md`

## Decision

Select the first improvement slice:

`active_fund` Chapter 3 turnover / style-consistency data-gap wording contract.

The implementation should make the Chapter 3 contract explicitly say:

1. For active funds, stability / style-consistency / style-drift claims require reviewed turnover-rate or reviewed style-change evidence.
2. If turnover-rate or style-change evidence is unavailable, missing, or not reviewed in the current slice, the report-quality contract must require explicit insufficiency wording.
3. The same gap must produce a next minimum validation question instead of an unsupported stable-process or style-consistency conclusion.
4. `N/A` / data-gap wording must not be treated as a pass. It is a constrained explanation that keeps the claim from being made.

This is not a renderer rewrite. It is a Fund-layer contract hardening slice that makes the next code-generation task precise and testable before any product-output change.

## Exact Wording And Route Decisions

Implementation must use a narrow modify/extend strategy for Chapter 3:

- Modify two existing `must_answer` entries.
- Add one new semantic `must_not_cover` entry.
- Add one new `required_output_items` entry.
- Do not add new chapter ids, new chapter titles, new lens keys, new fund types, renderer markers, extraction fields, or validator schema fields unless a focused failing test proves the current model cannot preserve the wording.

Update order is mandatory:

1. Update `docs/fund-analysis-template-draft.md` Chapter 3 `CHAPTER_CONTRACT` first as the human template truth.
2. Mirror the same wording into `fund_agent/fund/template/contracts.py` as the machine truth.
3. Update `fund_agent/fund/audit/contract_rules.py` coverage routes to match the machine-truth strings.

Exact Chapter 3 wording changes:

| Field | Action | Old string | New string |
|---|---|---|---|
| `must_answer` | Modify | `言行一致性判断：说的和做的一样吗？` | `言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。` |
| `must_answer` | Modify | `风格稳定性判断：跨期风格是否漂移？` | `风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。` |
| `must_not_cover` | Add | N/A | `不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。` |
| `required_output_items` | Add | N/A | `换手率/风格变化证据缺口说明与下一步最小验证问题` |

The new `required_output_items` entry must use these output markers in `ContractRequiredItemRule`:

```python
("换手率/风格变化证据缺口说明：", "下一步最小验证问题：")
```

The data-gap wording must preserve the validated same-source anchor `当前 slice 未复核换手率，不能据此判断风格稳定` and extend it narrowly to style-change / style-consistency / next validation:

```text
当前 slice 未复核换手率，不能据此判断风格稳定、风格一致或言行一致；下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，风格稳定性和言行一致性判断是否仍成立？
```

Implementation should embed that full sentence in `ReportDataGapOverride.required_report_wording` and assert it is preserved in the projected data-gap output. Do not add a separate next-validation-question field unless the existing `required_report_wording` path demonstrably cannot carry the wording.

Audit route decisions are fixed for the implementation gate:

- The new semantic `must_not_cover` entry must be covered by adding one `ContractMustNotCoverCoverageRule` to `_MUST_NOT_COVER_COVERAGE_RULES` with `coverage_kind="narrative_guidance"`.
- Do not use `ContractForbiddenContentRule` for this entry. There is no stable low-false-positive forbidden marker for unsupported style-stability/style-consistency claims in narrative text.
- Update the two affected `ContractMustAnswerCoverageRule.question_text` values to the new `must_answer` strings above.
- Keep their `coverage_kind="covered_by_required_item"` and route them to the existing judgment item plus the new data-gap item:
  - new `言行一致性判断...` question → `("言行一致性判断", "换手率/风格变化证据缺口说明与下一步最小验证问题")`
  - new `风格稳定性判断...` question → `("风格稳定性判断", "换手率/风格变化证据缺口说明与下一步最小验证问题")`
- Add one `ContractRequiredItemRule` for `换手率/风格变化证据缺口说明与下一步最小验证问题` with the two markers listed above.

## Evidence Basis

Gate A selected `004393` / 2024 / `active_fund` as the clean near-term candidate and identified its known Chapter 3 turnover/style-consistency gap as the main active-fund risk.

Gate B classified the minimum active-fund verifier case as Chapter 3 manager holding traceability pass plus turnover/style-consistency gap issue, with `chapter_contract` as the first owner. It deferred `data/source extraction` unless the accepted wording requires turnover or style-change evidence.

The quasi-real evidence run accepted one manually assembled bundle with no validator issue and two score issue rows:

- manager holding traceability: pass;
- turnover-rate fact coverage: material issue, field `turnover_rate`, data gap `not_reviewed_in_current_slice`, next owner `chapter_contract`.

The controller judgment accepted that validator schema is not the blocker and explicitly recommended the next gate as active-fund Chapter 3 turnover/style-consistency contract wording.

Current code confirms the gap:

- `fund_agent/fund/template/contracts.py` Chapter 3 currently requires actual investment behavior from annual report §8 including turnover rate, and requires consistency / style-stability / manager-holding judgments.
- The current contract does not explicitly say that missing or unreviewed turnover/style-change evidence must block stability/style-consistency claims and force insufficiency plus next minimum validation wording.
- `fund_agent/fund/audit/contract_rules.py` maps Chapter 3 questions to required output items, but has no explicit coverage route for the missing-evidence wording constraint.
- `tests/fund/test_report_evidence.py` already has a narrow data-gap override test with wording text `当前 slice 未复核换手率，不能据此判断风格稳定`, so the chosen slice has same-source implementation precedent.

Evidence is sufficient. This plan should not output `needs-more-evidence`.

## Why This Slice First

This is the smallest high-value fix because it addresses the only material quasi-real report-quality issue currently accepted by the evidence chain. It improves real report safety by preventing a common false inference: treating absent turnover/style-change evidence as proof of stable style or consistent process.

It also preserves the deterministic MVP. The contract can be hardened and tested in the Fund layer without changing current `fund-analysis analyze`, current renderer output, current FQ0-FQ6 behavior, Service/CLI defaults, Host/Agent runtime, or durable baseline state.

## Alternatives Not Selected

| Alternative | Decision | Reason |
|---|---|---|
| Renderer large change | Do not select | The accepted evidence says the next owner is `chapter_contract`, not product rendering. Changing renderer now would alter product output before the contract says exactly what wording must be enforced. |
| LLM audit / repair loop | Do not select | `docs/design.md` §5.4 marks this as accepted future design, not current production behavior. It would require a separate architecture and execution gate. |
| Host/Agent runtime | Do not select | Current deterministic main path has not opened Host/Agent gate. Any Host work must use `dayu.host`; any Agent execution kernel work must use `dayu.engine`. This slice needs neither. |
| Durable baseline promotion | Do not select | Gate A/B and quasi-real evidence all say no candidate is `scoring_ready` or `accepted_baseline`; scratch and quasi-real inputs are not fixtures. |
| Service/CLI/FQ0-FQ6 integration | Do not select | The accepted validator evidence is consumer-contract evidence only. No product-flow integration gate is open. |
| Data extraction first | Do not select | The controller explicitly deferred extraction until the Chapter 3 contract decides the exact evidence requirement. Existing evidence proves a wording/claim-safety issue, not extractor root cause. |
| Validator schema hardening | Do not select | Quasi-real bundle and JSONL validation returned no validator issues and no fail-closed state. Schema is not the current blocker. |
| Fund-type slot classification clarity | Do not select | Gate A keeps QDII/FOF and fallback issues as residuals, but the first clean candidate issue is active-fund Chapter 3. Fund-type taxonomy is a later gate. |
| Evidence anchor completeness broad slice | Do not select | Manager holding traceability passed in the quasi-real input. Broad anchor work would not target the accepted material issue. |
| Generic data-gap / N/A wording across all chapters | Do not select | Too broad for first slice. Implement the narrow active-fund Chapter 3 wording contract first, then generalize only if follow-up evidence shows repeated cross-chapter failures. |

## Implementation Scope For Next Code Gate

Allowed implementation files:

| File | Required change |
|---|---|
| `docs/fund-analysis-template-draft.md` | Update Chapter 3 `CHAPTER_CONTRACT` first as human template truth, using the exact wording table above. Do not rewrite narrative sections or examples. |
| `fund_agent/fund/template/contracts.py` | Mirror the exact Chapter 3 `must_answer`, `must_not_cover`, and `required_output_items` wording from the template draft. Keep chapter count and ids unchanged. |
| `fund_agent/fund/audit/contract_rules.py` | Update the two affected `ContractMustAnswerCoverageRule.question_text` values, add the new `ContractRequiredItemRule`, and add one `ContractMustNotCoverCoverageRule` in `_MUST_NOT_COVER_COVERAGE_RULES` with `coverage_kind="narrative_guidance"`. Do not add `ContractForbiddenContentRule` or renderer markers in this slice. |
| `tests/fund/template/test_contracts.py` | Add focused tests proving Chapter 3 active-fund contract contains the turnover/style-change evidence precondition, insufficiency wording, and next-minimum-validation requirement. Update exact expected strings only where contract wording changed. |
| `tests/fund/audit/test_audit_programmatic.py` | Update expected coverage counts and add a focused test that coverage manifest includes the new Chapter 3 wording route and remains fail-closed. |
| `tests/fund/test_report_evidence.py` | Strengthen the existing turnover data-gap override test so required report wording explicitly says no style-stability/style-consistency claim may be made and names the next minimum validation question. Do not change projection behavior unless the existing model cannot carry the wording. |
| `tests/fund/test_report_quality_validation.py` | Optional only if the selected wording requires stronger `N/A` / data-gap consumer semantics. Do not harden validator schema unless a failing test proves the current validator cannot preserve the selected wording contract. |
| `fund_agent/fund/README.md` | Minimal sync only if Fund source changes require documentation update. State current contract behavior, not future renderer behavior. |
| `docs/design.md` | Only update if the implementation changes template structure or accepted design truth. A narrow wording clarification that restates §5.4.3 missing-fact downgrade may not require design change; if changed, keep it as current contract fact and avoid future-system claims. |

Explicitly out of scope:

- `fund_agent/fund/template/renderer.py`
- `fund_agent/services/`
- `fund_agent/ui/`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/documents/`
- `FundDocumentRepository`
- PDF/cache/source helpers, downloaders, source adapters, extractors
- `fund_agent/host/`, `fund_agent/agent/`, `dayu.host`, `dayu.engine`
- tracked reports, curated fixtures, durable baseline files, ignored run-output promotion
- default `fund-analysis analyze` / `fund-analysis checklist` behavior

If implementation discovers that the contract cannot be tested without touching renderer, FQ0-FQ6, Service/CLI, extraction, or repository code, stop and request controller/review裁决 instead of widening the slice.

## Code-Generation-Ready Steps

1. Re-read current gate truth.
   - Commands:
     - `git status --short`
     - `sed -n '1,260p' docs/implementation-control.md`
     - `sed -n '430,565p' docs/design.md`
     - `sed -n '450,540p' docs/fund-analysis-template-draft.md`

2. Patch Chapter 3 contract wording.
   - In `docs/fund-analysis-template-draft.md`, update the Chapter 3 `CHAPTER_CONTRACT` block first.
   - Modify the existing `must_answer` entries exactly as listed in `Exact Wording And Route Decisions`.
   - Add the exact new `must_not_cover` entry listed above.
   - Add the exact new `required_output_items` entry listed above.
   - Do not add a separate required item for style-change; the single new item covers both turnover and style-change evidence gaps.
   - Keep `_EXPECTED_CHAPTER_IDS`, chapter ids, titles, lens keys, and supported fund types unchanged.

3. Mirror the template draft.
   - In `fund_agent/fund/template/contracts.py`, mirror the exact Chapter 3 contract strings from the template draft.
   - Do not rewrite other chapters, lenses, narrative sections, or report examples.

4. Update audit coverage routes.
   - In `fund_agent/fund/audit/contract_rules.py`, update the two affected `ContractMustAnswerCoverageRule.question_text` strings to match the new manifest strings.
   - Keep both updated `ContractMustAnswerCoverageRule` entries on `coverage_kind="covered_by_required_item"` and route each to the existing judgment item plus `换手率/风格变化证据缺口说明与下一步最小验证问题`.
   - Add one `ContractRequiredItemRule` for `换手率/风格变化证据缺口说明与下一步最小验证问题` with markers `("换手率/风格变化证据缺口说明：", "下一步最小验证问题：")`.
   - Add one `ContractMustNotCoverCoverageRule` in `_MUST_NOT_COVER_COVERAGE_RULES` for the new semantic `must_not_cover` item with `coverage_kind="narrative_guidance"`.
   - Do not add a `ContractForbiddenContentRule`.

5. Update focused tests.
   - `tests/fund/template/test_contracts.py`
     - Add `test_active_fund_chapter_3_contract_requires_reviewed_turnover_or_style_change_before_stability_claim()`.
     - Assert Chapter 3 `must_answer` / `must_not_cover` / `required_output_items` contain the new wording.
     - Assert the active-fund lens remains `priority="core"` and no non-active fund lens is removed.
   - `tests/fund/audit/test_audit_programmatic.py`
     - Update expected coverage counts if contract item count changes.
     - Add an assertion that the new semantic `must_not_cover` wording is present in the coverage manifest with `coverage_kind="narrative_guidance"`.
     - Keep fail-closed tests for missing/duplicate/unknown coverage passing.
   - `tests/fund/test_report_evidence.py`
     - Extend `test_extraction_mode_missing_produces_data_gap_ref()` or add a new test to assert `ReportDataGapOverride.required_report_wording` for `manager.turnover_rate` preserves:
       - insufficiency wording;
       - no unsupported style-stability/style-consistency claim;
       - next minimum validation question.
     - Use the exact required wording from `Exact Wording And Route Decisions`.
     - Do not require a new extraction field unless the current `ReportDataGapOverride` cannot carry the wording.
   - `tests/fund/test_report_quality_validation.py`
     - Only add a test if the wording is serialized into score issue / gap records and current validator fails to preserve or validate it. Otherwise leave validator schema unchanged.

6. Minimal docs sync after tests.
   - If `fund_agent/fund/` source changes are made, update `fund_agent/fund/README.md` minimally to mention the current Chapter 3 active-fund data-gap wording contract.
   - If the implementation only clarifies wording and does not change chapter structure, record in the implementation artifact why `docs/design.md` did not need a structural update.
   - If `docs/design.md` is updated, keep it aligned to current code fact, not future renderer/LLM behavior.

## Acceptance Commands For Implementation Gate

Run the smallest focused commands first:

```text
uv run pytest tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
uv run ruff check fund_agent/fund/template/contracts.py fund_agent/fund/audit/contract_rules.py tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
git diff --check
```

If `tests/fund/test_report_quality_validation.py` is touched:

```text
uv run pytest tests/fund/test_report_quality_validation.py
uv run ruff check fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py
```

Optional adjacent regression after focused tests pass:

```text
uv run pytest tests/fund/template tests/fund/audit tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Boundary checks:

```text
git diff --name-only
git diff -- fund_agent/fund/template/renderer.py fund_agent/services fund_agent/ui fund_agent/fund/quality_gate.py fund_agent/fund/extraction_score.py fund_agent/fund/documents
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|FQ0|FQ6" fund_agent/fund/template/contracts.py fund_agent/fund/audit/contract_rules.py tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
```

Expected result:

- Focused tests pass.
- Ruff passes.
- `git diff --check` passes.
- Diff contains no renderer, FQ0-FQ6, Service/CLI, repository/source-helper, Host/Agent/dayu, fixture, or tracked report changes.

## Stop Conditions

Stop and return to controller/review if any condition occurs:

- The implementation needs to change renderer output to make the contract meaningful.
- The implementation needs to call annual-report fetch/parse, `FundDocumentRepository`, PDF/cache/source helpers, downloaders, source adapters, or production extractors.
- The implementation needs to change Service/CLI defaults, `fund-analysis analyze`, `fund-analysis checklist`, FQ0-FQ6, `quality_gate.py`, or `extraction_score.py`.
- The implementation needs Host/Agent runtime, `dayu.host`, `dayu.engine`, tool loop, session/run lifecycle, or ToolTrace.
- The current `ReportDataGapOverride` / score issue model cannot carry the wording without schema changes that would affect existing validator consumers.
- Tests reveal the accepted evidence was insufficient to distinguish contract wording failure from extraction correctness.
- The proposed wording would imply a direct investment recommendation, future return forecast, manager motive/personality claim, or unsupported causality.

If a stop condition triggers, the implementation gate should output `needs-more-evidence` or a controller裁决 request, not widen scope.

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Contract wording becomes too broad and blocks legitimate Chapter 3 judgments. | Keep wording narrow: active-fund stability/style-consistency claims only; manager holding traceability remains separate. |
| Exact Chinese string changes break audit coverage counts. | Update coverage routes and tests in the same implementation gate; preserve fail-closed manifest validation. |
| Data-gap wording is mistaken for renderer output change. | State clearly in implementation artifact and README sync that this is a contract / evidence-bundle wording requirement, not current renderer behavior unless renderer is later authorized. |
| The slice silently becomes validator schema work. | Only touch validator tests/schema if current consumer cannot preserve the selected wording; otherwise leave validator unchanged because quasi-real validation already passed. |
| The slice triggers design-doc overreach. | Update `docs/design.md` only for current code fact or structural template change; do not describe future LLM audit or 0-10 chapter flow as implemented. |

## Residuals After This Slice

- Renderer still may not emit the new wording in current product reports until a later renderer/report-writing gate authorizes product output changes.
- Turnover/style-change extraction may still be incomplete; open extraction only after the accepted contract proves the exact evidence requirement and a same-source failure points to extractor root cause.
- Durable baseline remains blocked until reviewed facts, source recovery/replacement, clean validator results, and a curated-fixture gate are accepted.
- Fallback-blocked index/QDII candidates and pure FOF coverage remain separate corpus/source/taxonomy residuals.
- LLM audit, Host/Agent runtime, Service/CLI integration, and FQ0-FQ6 integration remain future gates.

## Validation Performed In This Planning Gate

Read-only / document-only commands used:

```text
git status --short
rg --files docs fund_agent tests | rg 'design.md|implementation-control.md|release-maintenance-small-baseline|quasi|evidence|validator|template|item|contract|README'
sed -n '1,260p' AGENTS.md
sed -n '1,260p' docs/implementation-control.md
sed -n '1,320p' docs/design.md
sed -n '1,260p' docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md
sed -n '1,320p' docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md
sed -n '1,340p' docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md
sed -n '1,300p' docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md
sed -n '1,280p' docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md
sed -n '1,260p' docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md
rg -n "chapter_3|turnover|style|consistency|manager|active_fund|N/A|data_gap|must_answer|must_not_cover|ITEM_RULE|gap|not_reviewed|unavailable|insufficient|next minimum|validation" fund_agent/fund/template fund_agent/fund/audit fund_agent/fund/report_evidence.py fund_agent/fund/report_quality_validation.py tests/fund docs/fund-analysis-template-draft.md
sed -n '1,280p' fund_agent/fund/template/contracts.py
sed -n '1,300p' fund_agent/fund/template/item_rules.py
sed -n '1,300p' tests/fund/template/test_contracts.py
sed -n '320,560p' fund_agent/fund/template/contracts.py
sed -n '450,540p' docs/fund-analysis-template-draft.md
sed -n '1,300p' fund_agent/fund/audit/contract_rules.py
sed -n '820,930p' tests/fund/audit/test_audit_programmatic.py
sed -n '250,540p' tests/fund/test_report_evidence.py
sed -n '360,460p' tests/fund/test_report_quality_validation.py
sed -n '430,620p' docs/design.md
test -e docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md; printf '%s\n' $?
```

Result:

- Existing unrelated untracked artifact remains: `docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md`.
- Target artifact did not exist before this Gate C plan.
- Accepted evidence is sufficient to select the active-fund Chapter 3 turnover/style-consistency data-gap wording contract as the first improvement slice.
- No source, tests, README, product flow, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, repository/source, fixture, or run-output command was executed.
