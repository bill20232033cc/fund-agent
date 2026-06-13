# AgentDS Evidence Review: Chapter 2 L1 Numerical Closure Root-cause Evidence

Date: 2026-06-14
Role: AgentDS evidence reviewer
Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Root-cause Evidence Gate`
Evidence under review: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-20260614.md`

## 1. Review Scope

This review verifies whether the evidence artifact directly supports its verdict, with mandatory checks on boundary compliance, command validity, hypothesis disposition correctness, and NOT_READY preservation.

## 2. Evidence Reviewed

- Evidence artifact: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-20260614.md`
- Accepted plan: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-20260614.md`
- Accepted plan controller judgment: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-controller-judgment-20260614.md`
- `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- Safe metadata verified via independent `jq` on `summary.json`, `chapters/chapter-02.json`, `manifest.json`
- Narrow code reads verified: `_audit_numerical_closure()`, `_audit_item_rule_deleted_sections()`, `_ch2_numerical_closure_contract_prompt()`, `_deleted_item_rule_ids()`, `_allowed_anchor_ids()`, `decide_repair()`
- No forbidden bodies, sources, live commands, or prohibited Chapter 3 item 01 evidence/review artifacts were read by this reviewer.

## 3. Mandatory Boundary Check: No-live/Read Compliance

| Check | Result |
|---|---|
| No code/test/control/design/README edits | PASS — git status shows pre-existing residue only; no new edits |
| No stage/commit/push/PR | PASS — no git write commands executed |
| No live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release commands | PASS — all commands are jq, git status/diff, pytest collect-only/focused |
| Did not read writer draft Markdown, repair Markdown, auditor feedback Markdown | PASS — evidence explicitly declares this; safe metadata confirms no body path accessed |
| Did not read raw prompts, provider payloads, report bodies, source/cache/PDF bodies | PASS — evidence explicitly declares this |
| Did not read prohibited Chapter 3 item 01 evidence/review artifacts | PASS — only the controller judgment was read, which is explicitly allowed by plan Section 6 |
| Preserved EID single-source/no-fallback | PASS — evidence explicitly declares this; no fallback invocation |
| Preserved NOT_READY | PASS — Section 7 residuals and Section 9 verdict both state NOT_READY |

**Boundary finding**: The evidence artifact Section 2 lists `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` as evidence reviewed (line 31). This is the controller judgment, not the evidence artifact or DS/MiMo review. The plan Section 6 explicitly permits reading the controller judgment. The evidence cites it only for the accepted fact that Chapter 3 item 01 no longer reproduces the original code bug. This is within allowed reads and does not constitute a boundary violation.

## 4. Command Audit

### 4.1 Allowed command classes

| Category | Commands | Exit | Assessment |
|---|---|---|---|
| Preflight | `git status --short`, `git diff --check` | 0, 0 | Allowed; used for scope ownership only, not readiness |
| Safe metadata jq (summary.json) | `jq '{schema_version,...}'` | 0 | Allowed; extracts only control fields |
| Safe metadata jq (chapter-02.json, attempts) | `jq '[.attempts[] \| ...]'` | 0 | Allowed; extracts attempt-level metadata, excludes draft/feedback file paths from selection |
| Safe metadata jq (chapter-02.json, diagnostics) | `jq '{chapter_prompt_contract_diagnostics,...}'` | 5 | Allowed; exit 5 correctly recorded. Worker explains `issues` array contains string, not objects. No body read. |
| Safe metadata jq retry | `jq` with type-aware issues projection | 0 | Allowed; correct error recovery, types issues for safe extraction |
| Safe metadata jq (manifest.json) | `jq '{schema_version,...}'` | 0 | Allowed |
| Pytest collect-only | 5 files × `--collect-only -q` | 0 each | Allowed; no test execution, only name discovery |
| Pytest focused no-live | 6 `-k` selectors with specific filters | 0 each | Allowed; all tests passed, selectors use pre-collected names |

### 4.2 Command findings

**jq exit 5 recovery (finding, non-blocking)**: The third jq command failed with exit 5 because `issues` is an array containing strings, not only objects. The worker correctly recorded the exit status, explained the cause, and retried with a type-aware query. This is proper error handling. The fact that `issues` contains non-object entries is itself a minor diagnostic serialization observation relevant to H5, but the evidence does not explicitly connect this to H5. This does not affect hypothesis disposition correctness.

**Focused test selectors**: All `-k` selectors were preceded by `--collect-only` prechecks. Selectors that had no matching tests (`test_chapter_facts.py -k "chapter_2 or tracking_error"`, `test_llm_run_artifacts.py -k "l1 or repair_budget_exhausted or writer_used"`) were correctly recorded as "no matching existing tests" rather than treated as passing evidence. This follows the plan requirement precisely.

**No selector drift observed**: Selector names derive from the plan's expected test names (e.g., `required_output_block`, `l1_numerical_closure`, `programmatic_audit_fails_l1`, `repair_budget_exhausted`). The collect-only precheck prevents silent mismatches.

## 5. Hypothesis Disposition Verification

### 5.1 H1: Required-output omission vs optional ITEM_RULE deletion — REJECTED

**Code verification**:
- `_deleted_item_rule_ids()` (chapter_writer.py:1183-1198): returns only decisions with `status == "delete"`. Does not interact with required-output markers.
- `_audit_item_rule_deleted_sections()` (chapter_auditor.py:1202-1230): emits C2 only if a deleted ITEM_RULE section still appears in draft. Does not flag required-output omission.
- These are independent audit paths from L1 numerical closure and required-output checking.

**Metadata verification**:
- `required_output_missing_count=0` on both attempts — independently confirmed from `summary.json` prompt_contract_diagnostics.
- `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]` on both attempts — independently confirmed from `chapters/chapter-02.json`.
- The evidence correctly distinguishes deleted optional ITEM_RULE from required-output markers.

**Verdict**: H1 rejection is **directly supported** by code and metadata evidence without requiring forbidden body reads. The `chapter_2_tracking_error_analysis` deletion is an optional ITEM_RULE decision, not a required-output omission.

### 5.2 H2: L1 rule strictness or contract mismatch — REJECTED

**Code verification**:
- `_ch2_numerical_closure_contract_prompt()` (chapter_writer.py:1238-1258): writer contract says "若写公式/百分比闭合断言，必须让 allowed anchor marker 与该断言同句或上下2行" and "结论要点 不要重复未带 anchor 的 R/A/B/C/A-C 具体百分比"
- `_audit_numerical_closure()` (chapter_auditor.py:1284-1312): iterates draft lines, checks numerical closure regex + numeric text regex, builds context from `max(0, index-2)` through `min(len(lines), index+3)`, emits blocking L1 when `<!-- anchor:` absent
- The auditor's ±2 line context window **exactly matches** the writer contract's "同句或上下2行" (same sentence or within two surrounding lines) specification.

**Metadata verification**:
- Both attempts fail on one `programmatic:L1` issue each (line:10, line:26), with `required_output_missing_count=0` and `required_structure_missing_count=0`.
- The L1 issue message is: "R=A+B-C / A=R-B / A-C 数字闭环断言缺少邻近 anchor marker。" — this is precisely the contract-specified enforcement.

**Verdict**: H2 rejection is **directly supported**. The L1 rule is a valid enforcement of the accepted Chapter 2 contract, not an over-strict implementation. The writer contract and auditor enforcement use the same proximity boundary.

### 5.3 H3: Repair regenerate strategy preserving/worsening L1 — ACCEPTED ROOT CAUSE

**Code verification**:
- `decide_repair()` (agent/repair.py:54-141): when `remaining_budget <= 0` → stop with `repair_budget_exhausted` (line 118-125). When `repair_hint in ("patch", "regenerate")` with budget remaining → `action=regenerate` with reason "MVP 暂无 typed patch API，将 patch/regenerate 映射为预算内整章重写" (line 126-134, confirmed verbatim).
- This confirms the evidence claim that patch hints are mapped to whole-chapter regenerate.

**Metadata verification**:
- Attempt 0: L1 at line:10, `source_repair_hint=patch`, repair `action=regenerate`, reason matches code
- Attempt 1: L1 at line:26 (different location, same type), `source_repair_hint=patch`, repair `action=stop`, `stop_reason=repair_budget_exhausted`
- Anchor usage dropped 5→4, fact usage dropped 3→2
- The second attempt still produces the same type of L1 violation despite the regenerate

**Scope check**: The evidence correctly adds "This does not authorize repair budget calibration. Budget changes remain a separate gate." This is an important scope guard that prevents H3 acceptance from being interpreted as authorization for budget changes.

**Root cause formulation**: "Chapter 2 failed because a contract-valid L1 numerical-closure blocker persisted after the current repair policy converted a patch hint into whole-chapter regenerate; the regenerated attempt still emitted an unanchored numerical closure and exhausted the one-regenerate budget." This is precise, evidence-backed, and does not overclaim.

**Verdict**: H3 acceptance as root cause is **directly supported** by code, metadata, and test evidence. No overclaiming detected.

### 5.4 H4: Evidence/fact/anchor availability insufficiency — NEEDS MORE EVIDENCE

**Code verification**:
- Safe metadata shows facts/anchors were available and used (5 anchors, 3 facts in attempt 0; 4 anchors, 2 facts in attempt 1)
- `writer_declared_missing_reasons=[]` on both attempts
- Runtime diagnostics show `allowed_anchor_count=null` and `allowed_fact_count=null`
- No existing projection tests for `chapter_2` or `tracking_error` in `test_chapter_facts.py`

**Disposition check**: H4 is correctly not accepted as root cause (terminal failure is L1 unanchored output, not `missing_required_facts`). It is correctly not fully rejected (allowed fact/anchor totals and required-output linkage are absent from safe diagnostics). This is the appropriate disposition given available evidence.

**Verdict**: H4 as "needs more evidence" is **correctly scoped**. Full rejection or acceptance would require diagnostic additions or authorized synthetic tests that are outside this evidence gate.

### 5.5 H5: Diagnostic serialization incompleteness — ACCEPTED CONTRIBUTING CAUSE

**Code verification**:
- Safe metadata correctly maps the failure to `prompt_contract/l1_numerical_closure` with `diagnostic_consistency_status=consistent`
- But `allowed_anchor_count=null` and `allowed_fact_count=null` in runtime diagnostics
- No required-output-to-fact/anchor linkage available in safe metadata

**Disposition check**: H5 is correctly classified as contributing cause only. The evidence explicitly states: "H5 contributed to evidence ambiguity but did not cause the runtime decision. The runtime decision itself was correctly mapped to L1 budget exhaustion." This is the correct distinction between contributing diagnostic gap and content root cause.

**Verdict**: H5 as contributing cause is **correctly scoped**. The evidence does not treat diagnostic incompleteness as content root cause.

## 6. Cross-cutting Checks

### 6.1 Chapter 3 item 01 boundary

The evidence cites only the accepted controller judgment fact that Chapter 3 item 01 no longer reproduces the original code bug, and Chapter 3 now fails closed as fact-gap. No Chapter 3 draft content, conclusion, or evidence body was read. This is within the allowed boundary.

### 6.2 PR 22 panel text

The evidence does not mention or treat PR 22 panel text as residue or blocker. Compliant.

### 6.3 repair budget scope guard

The evidence explicitly states H3 does not authorize budget changes, and Section 8 (Next Gate Recommendation) constrains the next gate to preserve current L1 contract and not change budget. Compliant.

### 6.4 NOT_READY

Explicitly preserved in Section 7 (Residuals), Section 8 (Next Gate Recommendation), and Section 9 (Final Verdict). Compliant.

## 7. Findings Summary

| # | Finding | Severity | Disposition |
|---|---|---|---|
| F1 | Evidence reads Ch3 item 01 controller judgment — allowed by plan Section 6 | None | Informational only; no boundary violation |
| F2 | jq exit 5 on `issues` query — correctly handled with retry; the string-typed issues are a minor H5-relevant observation not explicitly connected | Low | Non-blocking; does not affect hypothesis disposition |
| F3 | Focused test `-k` selectors correctly prechecked with `--collect-only`; selectors with no matches recorded as "no matching existing tests" | None | Compliant with plan requirement |
| F4 | H3 root cause scope guard ("does not authorize repair budget calibration") is present and correct | None | Prevents over-interpretation |
| F5 | H4 "needs more evidence" is correctly not used as a blocker for proceeding to fix planning | None | Appropriate disposition |
| F6 | `allowed_anchor_count=null` and `allowed_fact_count=null` in runtime diagnostics — correctly flagged as H5 diagnostic gap | None | Informational; routes to future diagnostic gate |

No findings rise to the level of blocking or requiring evidence amendment.

## 8. Final Verdict

**VERDICT: PASS**

The evidence artifact directly supports its verdict with verifiable code, metadata, and test evidence. All five hypotheses are correctly disposed. No-live/read boundaries are respected. Commands are allowed and sufficient, with proper error handling for the jq exit 5 case. NOT_READY is preserved. H3 is correctly scoped as root cause without overclaiming repair budget authority. H1/H2 rejections are proven without forbidden body reads. H4 is correctly left as needs more evidence. H5 is correctly classified as contributing cause only.
