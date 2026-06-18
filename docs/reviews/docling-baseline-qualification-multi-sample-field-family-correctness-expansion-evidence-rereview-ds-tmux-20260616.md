# Docling Multi-sample Field-family Correctness Expansion Evidence Re-review (DS tmux) - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Expansion Evidence Gate`
Role: AgentDS targeted evidence re-review worker — Fix 1 and Fix 2 closure only
Release/readiness: `NOT_READY`

## Scope

Re-review only the closure of the two required fixes from the DS evidence review (2026-06-16). Do not re-execute evidence, call FDR/PDF/live/EID, or review findings beyond Fix 1 and Fix 2. Do not implement or commit.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-review-ds-tmux-20260616.md` | Prior DS evidence review specifying Fix 1 and Fix 2 |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md` | Evidence markdown under re-review (Fix 2 target) |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Evidence JSON under re-review (Fix 1 target) |

## Fix Closure

### Fix 1: S1 fact candidate_artifact paths corrected to `_full.json`

**Required:** Replace all 21 occurrences of `_current_envelope.json` with `_full.json` in `facts[].candidate_artifact`.

**Verified closure:**

- All 21 S1 facts (F001–F020, F025) carry `"candidate_artifact": "reports/representation-json/004393_2025_docling_full.json"`. No `_current_envelope.json` string remains in `facts[]`.
- `evidence_notes[0]` records the fix with `note_id: "s1_candidate_artifact_path_fix"`, `status: "applied"`, `old_path` → `new_path`, and `affected_fact_count: 21`.
- The path now matches `input_artifacts[0].input_artifact_path` and the manifest entry for S1 docling.

**Status: CLOSED.**

### Fix 2: FundDocumentRepository non-attempt documented for S4/S5/S6

**Required:** Add a note in evidence markdown §4 explaining why `FundDocumentRepository(force_refresh=False)` was not attempted.

**Verified closure:**

The evidence markdown §4 (Same-source Reference Proof) paragraph after the reference table now reads:

> `FundDocumentRepository(force_refresh=False)` was not attempted for S4/S5/S6 in this evidence pass because this gate was executed as no-live/no-PDF/no-FDR evidence. The accepted plan allows blocking when no-live reference proof cannot be established without source/cache internals, direct PDF paths, `force_refresh=True`, or live acquisition. This evidence therefore records `no_no_live_reference_proof` instead of probing repository behavior.

This documents:
- Gate execution mode (no-live/no-PDF/no-FDR).
- Plan authorization for blocking under these constraints.
- The specific boundary: source/cache internals, direct PDF paths, `force_refresh=True`, and live acquisition are all prohibited.
- The evidence's chosen response: record `no_no_live_reference_proof` instead of probing.

The JSON corroborates: all S4/S5/S6 `repository_load` blocks show `attempted: false`, `reference_blocker_reason_or_null: "no_no_live_reference_proof"`, and `commands_not_run` includes `FundDocumentRepository load`.

**Status: CLOSED.**

## Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| FDR pathway remains untested for no-live reference availability | Controller / next gate | The next gate should either explicitly attempt FDR with `force_refresh=False` and record the result, or explicitly accept that FDR is out of scope for all no-live evidence gates. |
| S4/S5/S6 reference proof deferred | Next evidence gate | Requires either accepted same-source reference artifacts or explicit controller authorization to attempt FDR. |

## Verdict

```text
VERDICT: FIXES_CLOSED_EVIDENCE_ACCEPTABLE_BLOCKED_NOT_READY
```

**Basis:**

Both required fixes are fully applied:

1. Fix 1: All 21 S1 `candidate_artifact` paths now point to `004393_2025_docling_full.json`, aligned with `input_artifacts` verification and the manifest. The fix is recorded in `evidence_notes` with before/after paths and count.

2. Fix 2: Evidence markdown §4 now documents a clear three-part rationale for FDR non-attempt — gate scope exclusion, plan-authorized blocking when source/cache internals are inaccessible, and the decision to record `no_no_live_reference_proof` rather than probe repository behavior.

No new defects introduced. NOT_READY and blocking stance preserved. The residual FDR pathway question remains for the controller or next gate to decide.
