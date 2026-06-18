# Provider/LLM Chapter 2 L1 Numerical Closure No-live Diagnostic Evidence — MiMo Review

Date: 2026-06-14

Role: AgentMiMo

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Diagnostic Evidence Gate`

## Scope

Independent review of `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-20260614.md`.

Review questions:

1. Does the evidence satisfy controller amendments from `557fd6c`?
2. Are the no-live commands and safe-read boundaries compliant?
3. Is the conclusion `READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY` supported?
4. Are there blocker findings, overclaims, or missing residuals?

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-20260614.md` | Evidence artifact under review. |
| `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-controller-judgment-20260614.md` | Controller judgment defining 7 binding amendments. |
| `AGENTS.md` | Execution rule source. |
| `docs/current-startup-packet.md` | Current gate scope and control truth. |
| `docs/implementation-control.md` | Implementation control doc. |
| `fund_agent/fund/chapter_writer.py` | Source code for Chapter 2 L1 repair checklist assembly. |
| Safe metadata JSON: `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json` | Prior run metadata. |
| Safe metadata JSON: `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/summary.json` | Current run metadata. |

No forbidden files were read.

## Findings

### F1 [CRITICAL]: Evidence artifact swaps prior/current run labels in metadata comparison

The evidence artifact's "Prior vs current metadata comparison" table labels run `4a531cbe94604e47` (directory `T201900Z`) as "prior" and `605e381de24f4abb` (directory `T211325Z`) as "current". Safe metadata verification proves the opposite:

| Field | T201900Z (`4a531cbe`, labeled "prior") | T211325Z (`605e381d`, labeled "current") |
|---|---|---|
| `first_failed.chapter_id` | 3 | 2 |
| `first_failed.stop_reason` | `missing_required_facts` | `repair_budget_exhausted` |
| Chapter 2 status | `accepted`, `stop_reason=none` | `failed`, `stop_reason=repair_budget_exhausted` |
| Chapter 3 status | `blocked`, `stop_reason=missing_required_facts` | `accepted` |

T211325Z is the **later** run (21:13 UTC > 20:19 UTC) where Chapter 2 is accepted and Chapter 3 is the first blocker. T201900Z is the **earlier** run where Chapter 2 fails first. This matches the control-doc sequence: `765c616` (Chapter 2 accepted, Chapter 3 first blocker) happened before `2f8dce9` (Chapter 2 again fails first).

The artifact's comparison data itself is internally consistent — the two columns correctly describe two different patterns. But the prior/current labels are reversed. This means:

- The "prior run" column actually describes the **current** failing run (`2f8dce9`).
- The "current run" column actually describes the **prior** passing run (`765c616`).

**Impact on findings:** F1 ("repair-effectiveness failure, not clean-baseline regression") uses the comparison correctly but attributes it to the wrong run direction. F2/F3/F4 are independent of the run labeling and remain valid. The conclusion narrative ("Chapter 2 L1 regressed after `1b9cd00`") is directionally correct per control docs but is derived from a swapped-label comparison table.

**Impact on verdict:** The labeling error does not invalidate the no-live diagnostic conclusions (checklist assembly is intact, Chapter 3 path is independent, L1 fail-closed is preserved) because those are proven by code inspection and focused tests, not by the metadata comparison. However, the metadata comparison section must be corrected before this artifact can serve as accepted evidence.

### F2 [LOW]: No-live command boundary is compliant

The evidence artifact ran only:

- `git status`, `git diff --check` — standard safe status commands.
- `sed`/`rg` read-only inspections over allowed control, review, source and test files.
- `jq` over the four allowed metadata JSON files.
- Focused pytest with `-k` filters on `test_chapter_writer.py`, `test_chapter_orchestrator.py`, `test_chapter_auditor.py`.

No live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands were run. No forbidden files were read. This is compliant with controller amendment 6.

### F3 [LOW]: Controller amendments coverage

| Amendment | Addressed? | Notes |
|---|---|---|
| 1. Compare attempt-level L1 patterns | Yes | F1 and metadata comparison table address this (with F1 labeling issue). |
| 2. Verify `1b9cd00` did not change Chapter 2 repair prompt assembly | Partially | F3 proves Chapter 3 required-output paths are separate from Chapter 2 L1 checklist. F2 proves checklist renders in current code. No explicit git diff against `1b9cd00` was performed (acknowledged in artifact). |
| 3. Prove checklist reaches writer under no-live | Yes | F2 with focused writer/orchestrator tests proves this. Source code verification confirms `_ch2_l1_repair_guidance_prompt()` at `chapter_writer.py:1286-1316`. |
| 4. Preserve L1 rule | Yes | F4 proves fail-closed behavior. |
| 5. Do not change repair budget defaults | Yes | No budget changes observed. |
| 6. No live/provider/network commands | Yes | See F2 above. |
| 7. Preserve EID single-source/no-fallback and NOT_READY | Yes | Stated and preserved throughout. |

### F4 [LOW]: Source code verification confirms checklist assembly

Independent verification of `chapter_writer.py` confirms:

- `_ch2_l1_repair_guidance_prompt()` (line 1286) renders checklist only when `chapter.chapter_id == 2` AND `_has_l1_numerical_closure_repair_issue()` returns `True`.
- `_has_l1_numerical_closure_repair_issue()` (line 1268) checks `repair_context.previous_issue_ids` for prefix `programmatic:L1`.
- The repair context fragment assembly at line 737-745 joins both `_repair_context_prompt()` and `_ch2_l1_repair_guidance_prompt()`.
- The Chapter 3 required-output typed path (`_required_output_evidence_plan()`) does not touch `_has_l1_numerical_closure_repair_issue()` or `_ch2_l1_repair_guidance_prompt()`.

This supports F2 and F3 findings independently.

## Residuals

| Residual | Status | Notes |
|---|---|---|
| Prior/current run label swap in metadata comparison | Must fix | F1; does not invalidate code-level findings but invalidates the comparison table's narrative direction. |
| Byte-for-byte git diff against `1b9cd00` | Acknowledged | Artifact states this was not authorized; current-state code inspection is sufficient for this gate. |
| Attempt-level writer body shape | Unproven by design | Correctly stated as residual. |
| LLM ignored checklist vs checklist wording too weak | Unproven | Correctly classified as residual for fix-planning gate. |

## Verdict

**PASS_WITH_FINDINGS**

The evidence artifact satisfies the core diagnostic objectives: the Chapter 2 L1 repair checklist assembly is intact in current code, the Chapter 3 required-output policy path does not interfere with Chapter 2 L1 repair, L1 fail-closed semantics are preserved, and no-live boundaries were respected. The conclusion `READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY` is supported by the code-level and test-level evidence.

The critical finding (F1) is a metadata comparison labeling error that must be corrected before this artifact is accepted by the controller. The underlying data comparison is correct; only the prior/current direction labels are swapped. This does not affect the technical conclusions about checklist assembly, path independence, or L1 preservation, but it would mislead any reader relying on the comparison table's narrative direction.
