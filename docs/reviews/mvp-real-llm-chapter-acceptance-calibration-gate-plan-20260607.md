# MVP Real LLM Chapter Acceptance Calibration Gate Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM chapter acceptance calibration gate`
- Classification: `heavy`
- Role of this artifact: plan only; not implementation, review, evidence execution, PR, push, release, provider/default/runtime change, or live LLM retry.
- Entry authorization: user authorized entering this gate after `post-config live smoke evidence disposition / control sync gate`.

Classification rationale under `AGENTS.md`: this gate can affect CHAPTER_CONTRACT enforcement, accepted draft/conclusion eligibility, fail-closed final assembly, quality semantics, and live LLM evidence routing. Use `heavy`.

## 2. Current Truth Inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- Accepted disposition: `docs/reviews/mvp-post-config-live-smoke-evidence-disposition-20260607.md`
- Same-source retained artifact: `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/`

Preflight at plan time:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace includes the previous control-sync docs, this gate plan artifact, unrelated tracked `pyproject.toml`, and multiple unrelated untracked files.
- This gate must not stage, clean, delete, or use unrelated dirty files.

## 3. Evidence Summary

Latest post-config live smoke:

- readiness: passed using typed config loader;
- command: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`;
- command count: exactly one;
- exit code: `1`;
- retained artifact: `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/manifest.json`;
- orchestration status: `blocked`;
- final assembly status: `incomplete`;
- body chapter accepted draft/conclusion: none.

Chapter matrix:

| Chapter | Status | Stop reason | Category | Subcategory | First routing |
|---|---|---|---|---|---|
| 1 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | Slice 1A |
| 2 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `l1_numerical_closure` | later numerical-closure calibration |
| 3 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | later after Ch1 protocol result |
| 4 | `blocked` | `repair_budget_exhausted` | `audit_parse` | null | separate auditor line-protocol gate |
| 5 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | later after Ch1 protocol result |
| 6 | `blocked` | `unknown_anchor` | `prompt_contract` | `unknown_anchor` | separate anchor projection/allowed-anchor gate |

Ch1 same-source detail:

- attempt 0 writer drafted; programmatic issues: six C2 missing required-output markers; LLM issue: duplicate anchor id reused for two items.
- attempt 1 writer drafted; programmatic issues still six C2 missing required-output markers; no LLM issue remained.
- terminal category: `prompt_contract`; terminal stop reason: `repair_budget_exhausted`.

Local code evidence:

- `build_fund_llm_execution_request()` sets `ChapterOrchestrationPolicy(typed_template_path="typed_template_contract")`.
- `_typed_required_output_items()` returns typed `RequiredOutputItem` for all chapters when typed path is active.
- `chapter_writer.py` emits prompt marker requirements and parser checks typed required-output item ids when `typed_required_output_items` is present.
- `chapter_auditor.py::_audit_contract_markers()` still checks `input_data.writer_input.chapter.contract.required_output_items` legacy text markers, not `writer_input.typed_required_output_items` / prompt marker items.
- Existing tests cover typed required-output propagation for Ch2/Ch3, but not Ch1 typed marker acceptance in programmatic audit.

Working hypothesis:

The first fixable Ch1 root cause is a writer/auditor marker-protocol mismatch in the typed template path: writer prompt/parser allow typed item id markers, while programmatic auditor still requires legacy required-output text markers. This makes a draft that follows typed markers fail C2 marker audit.

This is a hypothesis for Slice 1A only. It does not explain Ch2 L1 numerical closure, Ch4 audit parse, or Ch6 unknown anchor.

## 4. Non-Goals

Forbidden in this gate unless a later reviewed plan explicitly opens a new slice:

- no live LLM rerun;
- no provider/default/runtime/budget/timeout/model/base-url/config change;
- no endpoint probe, DNS/socket/curl/PASS-only probe, retry, or fallback command;
- no deterministic fallback;
- no quality gate, final judgment, score-loop, golden/readiness, fixture, promotion, snapshot, PR, push or release change;
- no Agent runtime, dayu runtime, multi-year evidence runtime, or Host lifecycle expansion;
- no template JSON rewrite in `docs/fund-analysis-template-draft.md`;
- no relaxation of fail-closed semantics, repair budget, required-output coverage, anchor validation, L1 numerical closure, auditor parse protocol, or must_not_cover rules.

## 5. Implementation Slices

### Slice 1A: Ch1 Typed Required-Output Marker Protocol Alignment

Objective:

Make programmatic audit accept the same typed required-output marker protocol that writer prompt/parser use under `typed_template_path="typed_template_contract"`, while preserving legacy behavior when typed items are absent.

Allowed files:

- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_auditor.py` if existing helper coverage belongs there
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-implementation-evidence-20260607.md`
- package README only if public/current behavior changes need documentation; likely not required for this narrow internal contract alignment

Exact implementation decisions:

1. In `chapter_auditor.py`, update `_audit_contract_markers()` so the expected marker set is derived from the writer input marker protocol:
   - if `input_data.writer_input.typed_required_output_items` is non-empty, require markers for `item.item_id` from those typed items;
   - otherwise preserve existing legacy `chapter.contract.required_output_items` marker checks.
2. Do not accept bare required-output text as a marker substitute.
3. Do not make markers optional.
4. Do not change `_required_output_marker()` syntax.
5. Do not alter LLM auditor line protocol or repair-budget behavior.
6. Keep issue rule `C2`, severity, and repair hint semantics stable.
7. Do not implement `delete_if_not_applicable` filtering in Slice 1A. Current Ch1 same-source evidence and canonical template entries do not require deleted typed required-output semantics. If a future template entry needs deleted-item marker filtering, open a separate writer/auditor marker-obligation sharing contract gate instead of copying writer private action logic into the auditor.

Required tests:

- Add a deterministic test proving typed Ch1 required-output id markers pass programmatic audit under `typed_template_path="typed_template_contract"`.
- Add or update a regression proving legacy marker checks still require legacy text markers when typed items are absent.
- Add a negative typed-path test proving missing one typed marker still triggers C2.
- Add a focused orchestration test that Ch1 under typed path does not fail solely because typed markers are used instead of legacy required-output text markers.

Validation commands:

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Acceptance criteria:

- Ch1 typed required-output id markers are accepted by programmatic audit.
- Missing typed markers still fail closed with C2.
- Legacy contract marker behavior is unchanged when typed items are absent.
- No provider/runtime/default, quality gate, final judgment, score-loop, golden/readiness, template JSON, Agent runtime, Host runtime or README behavior is changed.

Stop conditions:

- If `_audit_contract_markers()` cannot access enough typed writer-input information without broad API changes, stop and return to controller.
- If fixing typed marker alignment would require editing `docs/fund-analysis-template-draft.md`, stop and return to controller.
- If tests reveal the writer is not actually emitting typed markers in Ch1 despite typed inputs, stop and split a writer-prompt/parser slice instead of modifying auditor acceptance broadly.
- If implementation discovers a current Ch1 typed required-output item whose safe action should be deleted, stop and return to controller; do not design marker-obligation sharing inside this slice.

### Slice 1B: Evidence Recheck Without Live Provider

Objective:

After Slice 1A, use deterministic/fake LLM tests and retained artifact inspection to verify that the Ch1 root cause classification is updated locally. Do not run a live provider smoke.

Allowed files:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-implementation-evidence-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Expected evidence:

- targeted tests pass;
- implementation evidence records that Ch1 marker-protocol mismatch is fixed locally;
- residuals remain open for Ch2, Ch4, Ch6 and possibly Ch3/Ch5 pending later evidence.

Stop condition:

- If Slice 1A cannot prove the local marker-protocol fix deterministically, do not update control docs to imply Ch1 is fixed.

## 6. Deferred Follow-Up Gates

These are explicitly out of Slice 1A:

- Ch2 `l1_numerical_closure`: separate numerical closure calibration; must not relax `_audit_numerical_closure()` without same-source evidence and review.
- Ch4 `audit_parse`: separate auditor line-protocol prompt/protocol gate; must not silently pass parse failures.
- Ch6 `unknown_anchor`: separate anchor projection / group-anchor conversion or allowed-anchor contract gate.
- Ch3/Ch5 `code_bug_other`: revisit after Slice 1A to determine whether they share the marker-protocol root cause or need separate evidence.
- Typed `delete_if_not_applicable` marker-obligation sharing: separate future contract gate if a real current template item requires it.

## 7. Review Requirements

Plan review must check:

- whether Slice 1A is narrow enough and follows root-cause evidence;
- whether auditor typed marker acceptance can be implemented without weakening fail-closed behavior;
- whether tests cover typed positive, typed negative and legacy behavior;
- whether the plan avoids live provider reruns and provider/default/runtime changes;
- whether Ch2/Ch4/Ch6 are correctly deferred.

Required reviewer verdict format:

- `PASS`
- `PASS_WITH_NON_BLOCKING_OBSERVATIONS`
- `BLOCKED_WITH_REQUIRED_FIXES`

## 8. Controller Judgment Requirements

Before implementation, controller must decide:

- whether the plan is accepted;
- whether reviewer findings require plan fixes;
- whether Slice 1A is authorized;
- whether any documentation/control sync is allowed after implementation evidence;
- whether a live provider rerun remains forbidden until a separate evidence gate.

## 9. Completion Report Format

Implementation evidence must report:

- files changed;
- exact root cause accepted or rejected;
- tests run and results;
- whether fail-closed semantics are preserved;
- residuals and next gate recommendation;
- explicit statement that no live LLM command was run.
