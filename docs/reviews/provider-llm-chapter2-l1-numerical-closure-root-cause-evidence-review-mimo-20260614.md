# Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Evidence Review (MiMo)

Date: 2026-06-14

Reviewer: AgentMiMo

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Root-cause Evidence Gate`

Artifact reviewed: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-20260614.md`

## 1. Scope

This review checks whether the evidence artifact directly supports its verdict, especially:

- Worker obeyed no-live/read boundary and avoided prohibited Chapter 3 evidence/review artifacts.
- Commands listed are allowed and sufficient; selector drift or unexpected jq failure handling.
- H3 accepted root cause is not overclaimed; direct metadata/code/test evidence supports ROOT_CAUSE_ACCEPTED.
- H1/H2 rejections are supported without reading forbidden bodies.
- H4 correctly left as needs more evidence.
- H5 correctly contributing only, not content root cause.
- NOT_READY preserved.

## 2. Findings

### F1. jq exit code misattributed — minor factual error

Severity: LOW

Evidence Section 3 states:

> `jq '{chapter_prompt_contract_diagnostics, chapter_runtime_diagnostics, issues, diagnostic_consistency_status}'` -> exit 5 because `issues` is an array containing a string, not only objects.

Verified: this jq command succeeds with exit 0. The `issues` field is `["2:repair_budget_exhausted:programmatic:L1:line:26:02ea024a63"]` — a homogeneous string array that jq renders without error in an object construction context. The evidence then says it "Retried safe structural query" with a more elaborate jq that also exits 0.

Impact: The retry produced correct data and the substantive metadata claims are accurate. The incorrect exit-5 attribution is a minor factual error that does not affect any hypothesis disposition. The evidence correctly recorded the safe structural query result.

### F2. All safe metadata claims verified — PASS

Verified against direct jq extraction from `summary.json`, `chapter-02.json`, and `manifest.json`:

- `first_failed.chapter_id=2`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure`, `attempt_count=2` — correct.
- Attempt 0: `writer_status=drafted`, `writer_finish_reason=stop`, `writer_response_chars=2484`, `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`, 5 anchor ids, 3 fact ids, `audit_status=fail`, one `programmatic:L1` at `line:10`, `audit_repair_hint=patch`, repair `action=regenerate` — all correct.
- Attempt 1: `writer_status=drafted`, `writer_finish_reason=stop`, `writer_response_chars=1799`, `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`, 4 anchor ids, 2 fact ids, `audit_status=fail`, one `programmatic:L1` at `line:26`, repair `action=stop`, `stop_reason=repair_budget_exhausted` — all correct.
- Both prompt-contract diagnostics: `required_output_missing_count=0`, `required_structure_missing_count=0`, `unknown_anchor_count=0`, `invalid_marker_count=0`, `primary_subcategory=l1_numerical_closure`, `diagnostic_consistency_status=consistent` — all correct.
- Both runtime diagnostics: `allowed_anchor_count=null`, `allowed_fact_count=null` — correct.
- Manifest: `schema_version=llm_incomplete_run_artifact_manifest.v1`, `orchestration_status=partial`, `final_assembly_status=incomplete`, `first_failed=null` — correct.

### F3. Test counts and pass/fail verified — PASS

Verified via live `--collect-only` and focused `-k` runs:

| Test file | Collect-only count | Evidence claim | Match |
| --- | --- | --- | --- |
| `test_chapter_writer.py` | 44 | 44 | yes |
| `test_chapter_auditor.py` | 49 | 49 | yes |
| `test_chapter_orchestrator.py` | 80 | 80 | yes |
| `test_repair_policy.py` | 5 | 5 | yes |
| `test_chapter_facts.py` | 13 | 13 | yes |
| `test_llm_run_artifacts.py` | 8 | 8 | yes |

Focused test results all match:

| Selector | Pass count | Deselected | Evidence claim | Match |
| --- | --- | --- | --- | --- |
| writer: `required_output_block or l1_numerical_closure or tracking_error` | 3 | 41 | 3/41 | yes |
| auditor: `required_output or l1 or deleted_item_rule or ch2_deleted` | 13 | 36 | 13/36 | yes |
| auditor: `programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework` | 4 | 45 | 4/45 | yes |
| orchestrator: `l1_prompt_contract_serialization or l1_repair_context or l1_failure_after_repair_budget_exhausted` | 3 | 77 | 3/77 | yes |
| repair_policy: `repair_budget_exhausted` | 1 | 4 | 1/4 | yes |
| orchestrator: `l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted` | 4 | 76 | 4/76 | yes |

No-matching-tests claims also verified:

- `test_chapter_facts.py -k "chapter_2 or tracking_error"`: 0 collected, 13 deselected — correct.
- `test_llm_run_artifacts.py -k "l1 or repair_budget_exhausted or writer_used"`: 0 collected, 8 deselected — correct.

### F4. No-live/read boundary compliance — PASS

Evidence Section 2 lists:

- `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md` — allowed control truth.
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-20260614.md` and `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-controller-judgment-20260614.md` — accepted plan artifacts, explicitly allowed.
- `docs/design.md` relevant sections — allowed by plan Section 6.
- `docs/fund-analysis-template-draft.md` Chapter 2 canonical JSON and template excerpt — allowed by plan Section 6.
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` — controller judgment is explicitly allowed by plan Section 6.
- Safe metadata via jq from `summary.json`, `chapters/chapter-02.json`, `manifest.json` — allowed.
- Narrow code reads from plan Section 6 named functions — all six files and all listed functions verified to exist.

Prohibited Chapter 3 artifacts NOT listed in Section 2:

- `provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md` — not read.
- `provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-ds-20260614.md` — not read.
- `provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-mimo-20260614.md` — not read.

Commands are all within allowed set: `git status --short`, `git diff --check`, `jq` safe metadata, `uv run pytest --collect-only -q`, `uv run pytest -k`. No forbidden commands observed.

### F5. H1 rejection supported — PASS

Evidence correctly shows:

- Chapter 2 canonical JSON has seven required-output items, all `when_evidence_missing="block"`.
- `_deleted_item_rule_ids()` returns only item-rule decisions with `status=="delete"`, separate from required-output behavior.
- Safe metadata: `required_output_missing_count=0` on both attempts.
- `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]` maps to optional conditional tracking-error content under `ITEM_RULE`, not required-output markers.
- Focused writer/auditor tests passed for required-output blocking, L1, and deleted-item-rule scenarios.

The distinction between optional ITEM_RULE deletion and required-output omission is well-supported by code and metadata. H1 rejection is correct.

### F6. H2 rejection supported — PASS

Evidence correctly shows:

- Writer prompt at `chapter_writer.py:1254`: "若写公式/百分比闭合断言，必须让 allowed anchor marker 与该断言同句或上下2行"
- Auditor `_audit_numerical_closure()` at `chapter_auditor.py:1302`: builds context from `lines[max(0, index - 2) : min(len(lines), index + 3)]` — 2 lines before through 2 lines after.
- The writer contract and auditor implementation match: same sentence or within 2 surrounding lines.
- Focused L1 tests passed: same-line/nearby anchor, missing anchor, A-C, missing-wording percentage, formula-framework cases.

The L1 rule is a valid enforcement of the accepted Chapter 2 contract, not an over-strict or mismatched implementation. H2 rejection is correct.

### F7. H3 accepted root cause supported — PASS

Evidence correctly shows the repair decision chain:

- `decide_repair()` at `repair.py:126`: `if audit_result.status in ("blocked", "fail") and repair_hint in ("patch", "regenerate"):` → `action="regenerate"`.
- Both `decide_repair()` and `_decide_repair()` stop when `remaining_budget <= 0`.
- Attempt 0: L1 blocker + `patch` hint → mapped to whole-chapter `regenerate`.
- Attempt 1: L1 blocker still present + `patch` hint → `stop` with `repair_budget_exhausted`.
- Anchor usage dropped from 5 to 4; fact usage dropped from 3 to 2 — regression, not improvement.
- Focused repair/orchestrator tests passed for budget exhaustion and L1 subcategory preservation.

The root cause statement is precise and not overclaimed: "Chapter 2 failed because a contract-valid L1 numerical-closure blocker persisted after the current repair policy converted a patch hint into whole-chapter regenerate; the regenerated attempt still emitted an unanchored numerical closure and exhausted the one-regenerate budget."

This does NOT authorize repair budget calibration. Budget changes remain a separate gate. H3 acceptance is correct.

### F8. H4 needs more evidence — PASS

Evidence correctly shows:

- Writer used some facts/anchors and declared no missing reasons.
- `allowed_anchor_count=null` and `allowed_fact_count=null` in runtime diagnostics — cannot prove full allowed set.
- No matching `chapter_2` or `tracking_error` projection tests in `test_chapter_facts.py`.
- H4 is NOT accepted as root cause because the terminal failure is L1 unanchored output, not `missing_required_facts` / `fact_gap`.
- H4 is NOT fully rejected because allowed totals and required-output linkage are absent from safe diagnostics.

The "needs more evidence" disposition is correct and well-justified.

### F9. H5 contributing cause — PASS

Evidence correctly shows:

- Serialization maps Chapter 2 to `prompt_contract/l1_numerical_closure` with correct safe counts and issue prefixes.
- It does NOT expose `allowed_anchor_count`, `allowed_fact_count`, or required-output-to-fact/anchor linkage.
- Code verification confirms `allowed_anchor_count` and `allowed_fact_count` are serialized in `llm_run_artifacts.py:797-798` and `chapter_orchestrator.py:257-258`, but runtime values are `null`.
- H5 contributed to evidence ambiguity but did not cause the runtime decision.
- H5 is correctly NOT accepted as content root cause.

### F10. NOT_READY preserved — PASS

Evidence Section 7 explicitly states: "Release/readiness remains `NOT_READY`." Section 9 verdict: `ROOT_CAUSE_ACCEPTED_READY_FOR_NO_LIVE_FIX_GATE_NOT_READY`. No readiness, release, MVP, provider/LLM path or PR readiness claims observed.

### F11. EID single-source/no-fallback preserved — PASS

Evidence Section 1 boundary: "Preserved EID single-source/no-fallback and `NOT_READY`." No fallback, source policy, or provider defaults changes observed.

## 3. Disposition Summary

| Finding | Severity | Impact on verdict |
| --- | --- | --- |
| F1: jq exit code misattributed (claimed exit 5, actual exit 0) | LOW | Non-blocking; retry produced correct data, substantive claims unaffected |
| F2-F11: All other checks | PASS | Verified against safe metadata, code, and live test re-runs |

## 4. Final Verdict

VERDICT: PASS_WITH_FINDINGS

The evidence artifact is accepted. The single finding (F1) is a minor factual error in jq exit code attribution that does not affect any hypothesis disposition, metadata claim, or boundary compliance. All safe metadata claims are verified correct. All test counts and pass/fail results are verified correct. The no-live/read boundary was fully respected. H1/H2 rejections, H3 acceptance, H4 needs-more-evidence, and H5 contributing-cause dispositions are all supported by direct evidence. NOT_READY and EID single-source/no-fallback are preserved.
