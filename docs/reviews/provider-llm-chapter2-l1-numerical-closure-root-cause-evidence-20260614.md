# Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Evidence

Date: 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Root-cause Evidence Gate`.

Role: AgentCodex evidence worker, not controller.

Objective: classify Chapter 2 `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure` across H1-H5 using no-live evidence only.

Boundaries held:

- Wrote exactly this evidence artifact.
- No code, test, control, design or README edits.
- No stage, commit, push or PR.
- No live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release command.
- Did not read writer draft Markdown, repair Markdown, auditor feedback Markdown, raw prompts, provider payloads, report bodies, source/cache/PDF bodies or prohibited Chapter 3 item 01 evidence/review artifacts.
- Preserved EID single-source/no-fallback and `NOT_READY`.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-controller-judgment-20260614.md`
- `docs/design.md` relevant CHAPTER_CONTRACT, Route C, L1 and repair-budget sections only.
- `docs/fund-analysis-template-draft.md` Chapter 2 canonical JSON and Chapter 2 template excerpt only.
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- Safe metadata via `jq` from:
  - `reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/summary.json`
  - `reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json`
  - `reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/manifest.json`
- Narrow code reads from plan Section 6 named functions/classes only:
  - `fund_agent/fund/chapter_writer.py`: `_deleted_item_rule_ids()`, `_allowed_anchor_ids()`, `_ch2_numerical_closure_contract_prompt()`
  - `fund_agent/fund/chapter_auditor.py`: `_audit_item_rule_deleted_sections()`, `_audit_numerical_closure()`, `_aggregate_repair_hint()`
  - `fund_agent/agent/repair.py`: `AgentRepairDecision`, `decide_repair()`, `repair_context_from_audit()`
  - `fund_agent/services/chapter_orchestrator.py`: `ChapterRepairDecision`, `serialize_chapter_prompt_contract_diagnostics()`, `_audit_prompt_contract_diagnostic()`, `_decide_repair()`, `_repair_context_from_audit()`, `_stop_reason_from_repair_decision()`, `_prompt_contract_diagnostic_payload()`
  - `fund_agent/services/llm_run_artifacts.py`: `write_llm_incomplete_run_artifacts()`, `_build_chapter_payload()`, `_repair_decision_payload()`, `_chapter_matrix_row()`, `_prompt_contract_diagnostic_payload()`
  - `fund_agent/fund/chapter_facts.py`: `project_chapter_facts()`, `_chapter_field_specs()`, `_project_chapter()`, `_item_rule_decisions_for_chapter()`

## 3. Commands Run

Preflight:

- `git status --short` -> exit 0. Existing modified/untracked residue observed before this artifact, including `AGENTS.md`, `README.md`, `docs/design.md`, multiple `docs/reviews/` artifacts, `reports/`, `reviews/`, scripts and local data. This is scope evidence only, not readiness evidence.
- `git diff --check` -> exit 0.

Safe metadata:

- `jq '{schema_version,fund_code,report_year,orchestration_status,final_assembly_status,first_failed,chapter_matrix,prompt_contract_diagnostics}' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/summary.json` -> exit 0.
- `jq '[.attempts[] | {attempt_index, writer_status, writer_stop_reason, writer_finish_reason, writer_max_output_chars, writer_response_chars, writer_deleted_item_rule_ids, writer_used_anchor_ids, writer_used_fact_ids, writer_declared_missing_reasons, audit_status, audit_repair_hint, programmatic_issues: [.programmatic_issues[]? | {rule_id, severity, location, message, repair_hint}], repair_decision}]' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json` -> exit 0.
- `jq '{chapter_prompt_contract_diagnostics, chapter_runtime_diagnostics, issues, diagnostic_consistency_status}' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json` -> exit 5 because `issues` is an array containing a string, not only objects. No body file was read.
- Retried safe structural query: `jq '{chapter_prompt_contract_diagnostics, chapter_runtime_diagnostics, issues_type: (.issues|type), issues_count: (.issues|length), issues_safe: [.issues[]? | if type == "object" then {rule_id, severity, location, message, repair_hint} else {type: type, value: .} end], diagnostic_consistency_status}' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json` -> exit 0.
- `jq '{schema_version, run_id, fund_code, report_year, status, orchestration_status, final_assembly_status, first_failed, output_paths}' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/manifest.json` -> exit 0.

Collect-only prechecks:

- `uv run pytest tests/fund/test_chapter_writer.py --collect-only -q` -> exit 0, 44 tests collected.
- `uv run pytest tests/fund/test_chapter_auditor.py --collect-only -q` -> exit 0, 49 tests collected.
- `uv run pytest tests/services/test_chapter_orchestrator.py --collect-only -q` -> exit 0, 80 tests collected.
- `uv run pytest tests/agent/test_repair_policy.py --collect-only -q` -> exit 0, 5 tests collected.
- `uv run pytest tests/fund/test_chapter_facts.py --collect-only -q` -> exit 0, 13 tests collected.
- `uv run pytest tests/services/test_llm_run_artifacts.py --collect-only -q` -> exit 0, 8 tests collected.

Focused no-live pytest:

- `uv run pytest tests/fund/test_chapter_writer.py -k "required_output_block or l1_numerical_closure or tracking_error"` -> exit 0, 3 passed, 41 deselected.
- `uv run pytest tests/fund/test_chapter_auditor.py -k "required_output or l1 or deleted_item_rule or ch2_deleted"` -> exit 0, 13 passed, 36 deselected.
- `uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework"` -> exit 0, 4 passed, 45 deselected.
- `uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_prompt_contract_serialization or l1_repair_context or l1_failure_after_repair_budget_exhausted"` -> exit 0, 3 passed, 77 deselected.
- `uv run pytest tests/agent/test_repair_policy.py -k "repair_budget_exhausted"` -> exit 0, 1 passed, 4 deselected.
- `uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted"` -> exit 0, 4 passed, 76 deselected.

No matching existing tests after collect-only:

- `tests/fund/test_chapter_facts.py -k "chapter_2 or tracking_error"`: no matching existing test names observed in collect-only output; not run.
- `tests/services/test_llm_run_artifacts.py -k "l1 or repair_budget_exhausted or writer_used"`: no matching existing test names observed in collect-only output; not run.

## 4. Accepted Runtime Facts

- Accepted prior controller judgment confirms the exact `004393 / 2025` bounded run exited `1`, final assembly remained incomplete, Chapter 3 item 01 no longer reproduced provider-before `ValueError` / `code_bug`, and the next blocker is Chapter 2.
- `summary.json` safe metadata:
  - `schema_version=llm_incomplete_run_summary.v1`
  - `fund_code=004393`
  - `report_year=2025`
  - `orchestration_status=partial`
  - `final_assembly_status=incomplete`
  - `first_failed.chapter_id=2`
  - `first_failed.status=failed`
  - `first_failed.stop_reason=repair_budget_exhausted`
  - `first_failed.failure_category=prompt_contract`
  - `first_failed.failure_subcategory=l1_numerical_closure`
  - `first_failed.attempt_count=2`
- Chapter 2 attempt 0 safe metadata:
  - `writer_status=drafted`
  - `writer_finish_reason=stop`
  - `writer_max_output_chars=12000`
  - `writer_response_chars=2484`
  - `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`
  - used 5 anchor ids and 3 fact ids.
  - `writer_declared_missing_reasons=[]`
  - `audit_status=fail`
  - one blocking programmatic issue at `line:10`: L1 numerical closure assertion lacks nearby anchor marker.
  - `audit_repair_hint=patch`
  - repair decision: `action=regenerate`, `source_repair_hint=patch`, reason says MVP has no typed patch API and maps patch/regenerate to whole-chapter rewrite within budget.
- Chapter 2 attempt 1 safe metadata:
  - `writer_status=drafted`
  - `writer_finish_reason=stop`
  - `writer_max_output_chars=12000`
  - `writer_response_chars=1799`
  - `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`
  - used 4 anchor ids and 2 fact ids.
  - `writer_declared_missing_reasons=[]`
  - `audit_status=fail`
  - one blocking programmatic issue at `line:26`: L1 numerical closure assertion lacks nearby anchor marker.
  - repair decision: `action=stop`, `source_repair_hint=patch`, `stop_reason=repair_budget_exhausted`.
- Chapter prompt-contract diagnostics are consistent:
  - both attempts have `primary_subcategory=l1_numerical_closure`
  - both attempts have `issue_id_prefix_counts={"programmatic:L1": 1}`
  - both attempts have `required_output_missing_count=0`
  - both attempts have `required_structure_missing_count=0`
  - both attempts have `unknown_anchor_count=0`
  - both attempts have `invalid_marker_count=0`
  - `diagnostic_consistency_status=consistent`
- Chapter runtime diagnostics expose auditor operation rows but `allowed_anchor_count=null` and `allowed_fact_count=null` for both attempts.
- `manifest.json` safe metadata records `schema_version=llm_incomplete_run_artifact_manifest.v1`, `run_id=host_run_3870105453bd4f26`, `orchestration_status=partial`, `final_assembly_status=incomplete`; it does not duplicate `first_failed`.

## 5. Hypothesis Disposition Table

| Hypothesis | Disposition | Evidence basis |
| --- | --- | --- |
| H1 required-output omission vs optional ITEM_RULE deletion | rejected | Safe diagnostics show `required_output_missing_count=0` on both attempts. Chapter 2 canonical JSON makes all seven required-output items `when_evidence_missing="block"`. Focused writer/auditor tests passed required-output blocking and marker enforcement. Deleted `chapter_2_tracking_error_analysis` maps to optional conditional tracking-error content, not required-output markers. |
| H2 L1 rule strictness or contract mismatch | rejected | Chapter 2 writer prompt requires formula/percentage closure assertions to have allowed anchor markers in the same sentence or within two surrounding lines. `_audit_numerical_closure()` enforces the same two-line context by requiring `<!-- anchor:` near numerical closure text. Focused L1 auditor tests passed same-line/nearby anchor, missing anchor, A-C, missing-wording percentage and formula-framework cases. |
| H3 repair regenerate strategy preserving/worsening L1 | accepted root cause | Attempt 0 produced a valid L1 blocker and `patch` hint, but current repair policy mapped patch to whole-chapter regenerate. Attempt 1 still produced a single L1 blocker, used fewer anchors/facts and then stopped as `repair_budget_exhausted`. Focused repair/orchestrator tests passed budget exhaustion and L1 subcategory preservation. This is the accepted no-live root cause for the terminal Chapter 2 failure: contract-valid L1 violation persisted through current whole-chapter regenerate repair and exhausted the one-regenerate budget. |
| H4 evidence/fact/anchor availability insufficiency | needs more evidence | Safe runtime shows some facts/anchors were used and no missing reasons were declared, but allowed fact/anchor totals and required-output-to-evidence linkage are not serialized. Existing `test_chapter_facts.py` collect-only output had no matching `chapter_2` or `tracking_error` projection test. H4 is not accepted as root cause, but cannot be fully rejected without a later no-live diagnostic/projection evidence gate or authorized synthetic tests. |
| H5 diagnostic serialization incompleteness | accepted contributing cause | Serialization correctly maps Chapter 2 to `prompt_contract/l1_numerical_closure` with safe counts and issue prefixes, and redacts body/prompt/provider payloads. It does not expose allowed fact/anchor counts or required-output linkage, so it cannot fully separate H4 from writer/repair behavior using safe metadata alone. |

## 6. Direct Evidence By Hypothesis

### H1: Required-output omission vs optional ITEM_RULE deletion

Rejected.

Direct evidence:

- Chapter 2 canonical JSON has seven required-output items, `ch2.required_output.item_01` through `item_07`, and every one declares `when_evidence_missing="block"`.
- `chapter_writer._deleted_item_rule_ids()` returns only item-rule decisions with `status=="delete"`; this is separate from required-output behavior.
- `chapter_auditor._audit_item_rule_deleted_sections()` only checks that deleted ITEM_RULE sections are absent; it emits C2 only if a deleted optional section still appears.
- Chapter 2 template excerpt places tracking-error analysis under conditional `ITEM_RULE` for index/enhanced-index funds.
- Safe metadata records `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]` on both attempts, while prompt-contract diagnostics record `required_output_missing_count=0` on both attempts.
- Focused tests passed:
  - writer required-output block and L1 prompt tests: 3 passed.
  - auditor required-output / L1 / deleted-item-rule tests: 13 passed.

Conclusion: the observed deletion is optional ITEM_RULE deletion evidence, not required-output omission evidence.

### H2: L1 rule strictness or contract mismatch

Rejected.

Direct evidence:

- `docs/design.md` states canonical template JSON is the authored CHAPTER_CONTRACT truth source, and Route C writer/auditor primitives enforce marker and audit contracts.
- Chapter 2 writer prompt says: if writing formula/percentage closure assertions, allowed anchor marker must be in the same sentence or within two surrounding lines; conclusion and evidence sections must not repeat unanchored R/A/B/C/A-C concrete percentages.
- `_audit_numerical_closure()` iterates draft lines, detects numerical closure plus numeric text, builds context from two lines before through two lines after, and emits blocking L1 when `<!-- anchor:` is absent.
- The implementation therefore matches the accepted writer contract boundary, rather than adding a stricter unstated rule.
- Focused L1 tests passed:
  - `tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework"`: 4 passed.
  - `tests/services/test_chapter_orchestrator.py -k "l1_prompt_contract_serialization or l1_repair_context or l1_failure_after_repair_budget_exhausted"`: 3 passed.

Conclusion: the L1 failure is a valid enforcement of the accepted Chapter 2 contract, not a rule/contract mismatch.

### H3: Repair regenerate strategy preserving/worsening L1

Accepted root cause.

Direct evidence:

- Attempt 0:
  - one `programmatic:L1` issue at `line:10`
  - `source_repair_hint=patch`
  - repair decision `action=regenerate`
  - repair reason: no typed patch API; patch/regenerate are mapped to whole-chapter rewrite while budget remains.
- Attempt 1:
  - one `programmatic:L1` issue at `line:26`
  - `source_repair_hint=patch`
  - repair decision `action=stop`
  - `stop_reason=repair_budget_exhausted`
  - anchor usage dropped from 5 to 4; fact usage dropped from 3 to 2.
- `fund_agent/agent/repair.py::decide_repair()` and `fund_agent/services/chapter_orchestrator.py::_decide_repair()` both stop when `remaining_budget <= 0`; otherwise `patch` / `regenerate` map to `regenerate`.
- `_repair_context_from_audit()` records previous issue ids, sanitized messages and required corrections, but the current runtime safe metadata does not show a successful localized patch; it shows a second whole-chapter draft that still violates L1.
- Focused tests passed:
  - `tests/agent/test_repair_policy.py -k "repair_budget_exhausted"`: 1 passed.
  - `tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted"`: 4 passed.

Accepted root cause statement: Chapter 2 failed because a contract-valid L1 numerical-closure blocker persisted after the current repair policy converted a patch hint into whole-chapter regenerate; the regenerated attempt still emitted an unanchored numerical closure and exhausted the one-regenerate budget.

This does not authorize repair budget calibration. Budget changes remain a separate gate.

### H4: Evidence/fact/anchor availability insufficiency

Needs more evidence.

Direct evidence:

- Safe metadata proves the writer had and used some same-run evidence:
  - attempt 0 used 5 anchor ids and 3 fact ids.
  - attempt 1 used 4 anchor ids and 2 fact ids.
  - both attempts declared no missing reasons.
- `project_chapter_facts()` projects facts and evidence anchors from `StructuredFundDataBundle`; `_project_chapter()` deduplicates anchors, projects facts, ensures fact anchor refs exist, and records missing reasons.
- Runtime diagnostics for Chapter 2 show `allowed_anchor_count=null` and `allowed_fact_count=null`, so safe metadata cannot prove the full allowed set or required-output linkage.
- Collect-only found no matching existing `tests/fund/test_chapter_facts.py -k "chapter_2 or tracking_error"` tests; no focused projection test was run for H4.

Conclusion: H4 is not accepted as root cause because the observed terminal failure is L1 unanchored writer output, not `missing_required_facts` / `fact_gap`. It is not fully rejected because allowed fact/anchor totals and required-output evidence linkage are absent from safe diagnostics.

### H5: Diagnostic serialization incompleteness

Accepted contributing cause.

Direct evidence:

- `serialize_chapter_prompt_contract_diagnostics()` and `_prompt_contract_diagnostic_payload()` output safe scalar/count fields and explicitly avoid prompts, drafts, provider responses, audit raw responses, API keys and headers.
- `_audit_prompt_contract_diagnostic()` maps `programmatic:L1` prefix counts into `l1_numerical_closure_count` and selects `primary_subcategory=l1_numerical_closure`.
- `write_llm_incomplete_run_artifacts()` refuses accepted final reports and writes incomplete-run diagnostics under allowlist/redaction logic.
- `_build_chapter_payload()` serializes chapter status, stop reason, failure category/subcategory, safe issues, attempts, prompt-contract diagnostics and runtime diagnostics.
- Safe runtime artifact proves correct high-level mapping:
  - `failure_category=prompt_contract`
  - `failure_subcategory=l1_numerical_closure`
  - `diagnostic_consistency_status=consistent`
- It also proves diagnostic gaps:
  - `allowed_anchor_count=null`
  - `allowed_fact_count=null`
  - no required-output-to-fact/anchor linkage.
- Collect-only found no matching existing `tests/services/test_llm_run_artifacts.py -k "l1 or repair_budget_exhausted or writer_used"` tests; no focused artifact serialization test was run for those fields.

Conclusion: H5 contributed to evidence ambiguity but did not cause the runtime decision. The runtime decision itself was correctly mapped to L1 budget exhaustion.

## 7. Residuals

- Release/readiness remains `NOT_READY`.
- Full LLM completion, content quality, additional samples, provider acceptance, PR and release state remain unproven.
- Chapter 3 remains accepted only as fact-gap fail-closed in the prior bounded evidence; no Chapter 3 draft/conclusion is accepted here.
- H4 remains partially open because safe metadata lacks allowed fact/anchor counts and required-output linkage.
- H5 requires a future diagnostic implementation gate if controller wants safe `allowed_fact_count`, `allowed_anchor_count`, per-required-output availability and required-output-to-anchor linkage.
- Repair budget calibration, typed patch API, source policy, fallback, annual-period LLM route, provider defaults and readiness/release remain outside this gate.

## 8. Next Gate Recommendation

Proceed to a no-live fix implementation planning gate for Chapter 2 L1 repair behavior, scoped to the accepted H3 root cause.

Minimum recommended constraints for that next gate:

- Preserve current L1 contract: formula/percentage closure assertions need nearby allowed anchor marker.
- Do not weaken L1 or remove the blocker.
- Do not change EID single-source/no-fallback.
- Do not change provider defaults, annual-period LLM route, source policy, fallback or release/readiness state.
- Consider safe diagnostic additions for H4/H5, but keep them separate from any content repair behavior unless explicitly authorized.

## 9. Final Verdict

VERDICT: ROOT_CAUSE_ACCEPTED_READY_FOR_NO_LIVE_FIX_GATE_NOT_READY
