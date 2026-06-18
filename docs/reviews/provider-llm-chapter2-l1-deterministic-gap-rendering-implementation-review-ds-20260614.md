# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Implementation Review (DS)

Date: 2026-06-14

Role: AgentDS reviewer, not controller

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate`

Verdict: `PASS_WITH_FINDINGS`

Release/readiness: `NOT_READY`

## 1. Scope

Reviewed the no-live implementation evidence and diffs for the narrow Chapter 2 `l1_numerical_closure` deterministic evidence-gap / minimum-verification route.

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command was run. No source/test/runtime/docs modification except this review artifact.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, module boundaries, template sync rule. |
| `docs/current-startup-packet.md` | Current active gate, checkpoint `97fb2e4`. |
| `docs/implementation-control.md` | Current control truth, gate scope, allowed/forbidden write sets. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-controller-judgment-20260614.md` | Controller plan judgment with binding amendments. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-implementation-evidence-20260614.md` | Implementation evidence artifact. |
| `git diff` for all six target files | Full diff of template and five test files. |

No report bodies, provider payloads, PDF/source/cache bodies or final report body were read.

## 3. Findings

### Finding 1 — MINOR: `test_chapter_auditor.py` not modified despite being in allowed write set

- **File/line**: `tests/fund/test_chapter_auditor.py` (no diff)
- **Evidence**: Implementation evidence §2 states this file "already covered safe Ch2 gap/minimum-verification pass and concrete unanchored percentage L1 fail."
- **Assessment**: The implementation worker asserts existing auditor tests suffice, and no production source changes altered auditor behavior. The claim is plausible but not independently verifiable within this review boundary (the auditor test body was not read, and the existing auditor tests were written for a prior gate with different `when_evidence_missing` values).
- **Severity**: Minor. Does not block gate acceptance; the orchestrator-level test `test_chapter_2_typed_available_facts_still_fail_l1_after_one_repair` exercises the full auditor path including `l1_numerical_closure` with the new template.
- **Recommendation**: Controller may accept as-is or request a targeted auditor-only test that explicitly proves Ch2 gap/minimum-verification L1 pass with the new `render_evidence_gap` / `render_minimum_verification_question` actions.

### Finding 2 — MINOR: Only `missing` availability status tested for gap behavior

- **File/line**: `tests/fund/test_chapter_writer.py:348-428`, `tests/services/test_chapter_orchestrator.py:2338-2382`
- **Evidence**: Both positive gap path tests use `extraction_mode="missing"` with `anchors=()`. Evidence §4 claims gap behavior applies for `missing`, `unavailable`, `unreviewed`, or `not_applicable`.
- **Assessment**: The template declares `when_evidence_missing` which covers all non-available statuses, but the no-live tests only exercise the `missing` path. `unavailable`, `unreviewed`, and `not_applicable` are not covered.
- **Severity**: Minor. The typed contract path discriminates on `EvidenceAvailability` status regardless of which non-available status applies; the gap rendering logic is identical for all non-available statuses. The existing `test_chapter_2_missing_availability_envelope_remains_fail_closed` covers the envelope-absent case.
- **Recommendation**: Accept as residual. Additional status coverage can be deferred to future bounded live evidence gate.

### Finding 3 — MINOR: Repair budget test uses explicit parameter, doesn't assert default

- **File/line**: `tests/services/test_chapter_orchestrator.py:2387-2415`
- **Evidence**: Test `test_chapter_2_typed_available_facts_still_fail_l1_after_one_repair` passes `max_repair_attempts=1` explicitly and asserts `len(writer.requests) == 2` (initial + one repair). No test asserts the module-level default value of `max_repair_attempts`.
- **Assessment**: Since zero production source files were touched (as confirmed by `git diff`), the module default cannot have changed. The risk of an undetected default change is zero.
- **Severity**: Minor. Informational only; does not affect gate verdict.
- **Recommendation**: No action needed.

### Finding 4 — INFO: "下一步最小验证问题" wording is uniform but not item-specific

- **File/line**: `docs/fund-analysis-template-draft.md` (items 03, 04, 07)
- **Evidence**: All three `render_minimum_verification_question` items (03, 04, 07) share the same domain reason pattern: "只能输出下一步最小验证问题，不得给出 Alpha 或稳定性结论" (03/04) or "不得输出具体 R=A+B-C 数字闭环" (07). The fake writer Markdown in tests uses a uniform "下一步最小验证问题：复核同源年报中的基金收益、基准收益和费用口径" for all items.
- **Assessment**: The uniform wording is intentional — the template declares the domain constraint, while the writer prompt instructs output mechanics. This aligns with controller amendment DS F2.
- **Severity**: Info. Confirms controller expectation.

## 4. Positive Verification

### 4.1 Allowed write set compliance — PASS

| Path | Allowed | Changed | Status |
|---|---|---|---|
| `docs/fund-analysis-template-draft.md` | Yes (7 Ch2 items only) | Yes | Only 7 `when_evidence_missing` + `missing_evidence_reason` changed; item ids/order/text/structure preserved |
| `tests/fund/template/test_typed_contracts.py` | Yes | Yes | Added Ch2 structure/reason assertions |
| `tests/fund/test_chapter_writer.py` | Yes | Yes | Added gap/minimum-verification, fail-closed envelope, gap issue-id tests |
| `tests/fund/test_chapter_auditor.py` | Yes | **Not changed** | Evidence says existing tests suffice (Finding 1) |
| `tests/services/test_chapter_orchestrator.py` | Yes | Yes | Added gap accepted path, available-fact L1 fail-closed path |
| `tests/agent/test_runner.py` | Yes | Yes | Added Ch2 positive, unsafe-output negative coverage |
| `tests/services/test_fund_analysis_service_llm.py` | Yes | Yes | Added Service final-assembly positive, negative coverage |
| `tests/fund/test_evidence_availability.py` | Yes | Not changed | Evidence says existing coverage suffices |

Production Python source: **not touched** — confirmed by `git diff`. No conditional source edits were needed.

Forbidden files: `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, root `README.md`, provider/default/runtime config — **none touched**.

### 4.2 Exact missing_evidence_reason assertions — PASS

All four reason groups are tested with exact string comparison in `test_chapter_2_missing_behavior_preserves_structure_and_exact_reasons` (`tests/fund/template/test_typed_contracts.py:254`):

| Items | Behavior | Reason constant | Correct? |
|---|---|---|---|
| 01, 02 | `render_evidence_gap` | `CH2_PERFORMANCE_REASON` | Yes — forbids fabricating 1/3/5 year return numbers |
| 03, 04 | `render_minimum_verification_question` | `CH2_ATTRIBUTION_REASON` | Yes — forbids Alpha/stability conclusions |
| 05, 06 | `render_evidence_gap` | `CH2_COST_REASON` | Yes — forbids fabricating fee rates, transaction costs |
| 07 | `render_minimum_verification_question` | `CH2_SYNTHESIS_REASON` | Yes — forbids outputting concrete R=A+B-C closure |

Reason constants are also inlined in writer tests (`tests/fund/test_chapter_writer.py:335-339`) and used in prompt-content assertions.

### 4.3 Chapter 2 item ids/order/text/structure unchanged — PASS

`test_chapter_2_missing_behavior_preserves_structure_and_exact_reasons` asserts:
- All 7 items with exact `(item_id, text, when_evidence_missing, missing_evidence_reason)` tuples
- Internal subcontract ids: `("performance", "attribution", "cost")`

The template diff confirms no changes to `id`, `text`, or item ordering — only `when_evidence_missing` and `missing_evidence_reason` changed.

### 4.4 Typed EvidenceAvailability gating — PASS

- Non-available status → gap/minimum-verification: Proven by `test_chapter_2_missing_performance_renders_evidence_gap` (writer), `test_chapter_2_missing_synthesis_renders_minimum_verification_question` (writer), `test_chapter_2_typed_missing_evidence_gap_path_accepts_without_repair` (orchestrator).
- Available facts with anchors remain `render`: Proven by `test_chapter_2_typed_available_facts_still_fail_l1_after_one_repair` — all evidence plans show `action == "render"`, and when writer emits unanchored percentage ("Alpha 为 2.10%"), auditor catches it as `l1_numerical_closure`.
- Missing `EvidenceAvailability` envelope → `ValueError`: Proven by `test_chapter_2_missing_availability_envelope_remains_fail_closed`.

### 4.5 Writer issue-id semantics preserved — PASS

- `writer:required_output_block:*` remains for available-fact block cases (unchanged template path, unchanged auditor code).
- `writer:required_output_gap_missing:*` used for non-available gap/verification defects: proven by `test_chapter_2_missing_gap_without_gap_phrase_uses_specific_issue_id` (writer) and the Service/Agent negative tests.

### 4.6 Repair budget unchanged — PASS

- `max_repair_attempts` default unchanged (no production source touched).
- One-repair semantics proven by `test_chapter_2_typed_available_facts_still_fail_l1_after_one_repair`: `max_repair_attempts=1`, `len(writer.requests) == 2`, `len(run.attempts) == 2`, `run.status == "failed"`, `run.stop_reason == "repair_budget_exhausted"`.

### 4.7 EID single-source/no-fallback unchanged — PASS

- No source file changes; no new source imports in tests.
- Template changes are Ch2-only contract semantics, not source policy.

### 4.8 Release/readiness preserved — PASS

- All evidence artifacts carry `NOT_READY`.
- No release/PR/merge claims.

### 4.9 Validation commands — PASS

Evidence reports:
```
260 passed in 1.42s
ruff: All checks passed!
git diff --check: passed with no output
```

No production source was touched, so ruff scope was correctly confined to test files.

### 4.10 Controller amendment compliance — PASS

| Amendment | Status | Evidence |
|---|---|---|
| DS F1: exact `missing_evidence_reason` specified | Done | 4 reason groups with exact text in template and tests |
| DS F2: reason vs mechanics mapping stated | Done | Evidence §3 explicitly states separation |
| DS F3: template structure preserved | Done | Test + diff confirm no id/order/text/structure change |
| DS F5: prompt header interaction verified | Done | Writer tests assert reason presence in `prompt.user_prompt` |
| MiMo F1: conditional source edits | Done | Zero source files changed; rule not triggered |
| MiMo F2: issue-id naming contract | Done | `writer:required_output_block:` preserved; `writer:required_output_gap_missing:` added for non-available |

## 5. Residuals

| Residual | Severity | Owner |
|---|---|---|
| `test_chapter_auditor.py` not changed (Finding 1) | Minor | Controller may accept or request targeted auditor test |
| Only `missing` status tested for gap (Finding 2) | Minor | Future bounded live evidence gate |
| Future LLM wording compliance unproven by no-live tests | Known | Future bounded live/provider evidence gate (per DS F4) |
| Exact live sample fact-absence vs present-but-ignored ambiguity | Known | Preserved by typed availability discriminator + available-fact L1 tests |

## 6. Recommendation for Controller

`PROCEED_TO_DISPOSITION_GATE`

The implementation faithfully executes the accepted plan within no-live boundaries. All seven controller amendments are satisfied. Three minor findings do not block: the auditor test gap (Finding 1) is covered by orchestrator-level L1 tests, the missing-status-only coverage (Finding 2) is inherent to no-live typed-contract testing, and the repair budget default non-assertion (Finding 3) is zero-risk when no source files changed.

Recommended next gate: controller disposition closing this implementation gate, accepting the evidence as `PASS_ACCEPTED_NO_LIVE_NOT_READY`, and routing the phaseflow to the next mainline entry.
