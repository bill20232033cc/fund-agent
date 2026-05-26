# Controller Judgment: Small Baseline Corpus v1 Run

> Date: 2026-05-27
> Controller: Codex
> Gate: `small baseline corpus v1`
> Run artifact: `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`
> Reviews:
> - `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-review-glm-20260527.md`
> Verdict: **ACCEPTED LOCALLY**

## Startup Reconciliation

The Startup Packet next entry point was `small baseline corpus v1 plan/review`. Gate 4 was entered after local accepted commit `1aca29b` for core analyze/checklist reliability hardening.

The accepted active-fund Chapter 3 renderer minimal integration had already completed before this gate, so the current run did not repeat renderer work.

## Direct Evidence Summary

The bounded run evaluated eight candidate rows across seven unique fund codes:

- `004393` / 2024 / `active_fund`: product smoke, selected smoke, snapshot, score, and quality gate ran; quality gate `warn`.
- `004393` / 2025 / `active_fund`: probe-only product smoke ran; year-scoped golden non-coverage remained explicit and did not reuse 2024 rows.
- `004194` / 2024 / `enhanced_index`: selected smoke, snapshot, score, and quality gate ran; quality gate `warn`; correctness was `covered`, 5/5 comparable matches.
- `006597` / 2024 / `bond_fund`: selected smoke, snapshot, score, and quality gate ran; quality gate `block` from missing-field rate / bond-lens extraction gaps, not correctness mismatch.
- `110020` / 2024 / `index_fund`: kept visible as fallback-blocked excluded row.
- `017641` / 2024 / `qdii_fund`: kept visible as fallback-blocked excluded row.
- `007721` / 2024 / FOF attempt: kept visible as `data_gap` / `taxonomy_pending`.
- `017970` / 2024 / FOF attempt: kept visible as `data_gap` / `taxonomy_pending` / fallback-blocked.

Bulk outputs stayed in `/tmp/...` or ignored `reports/...` paths. The tracked artifact contains only summary, issue categories, and evidence paths.

## Review Findings Judgment

| Finding | Judgment | Controller rationale |
|---|---|---|
| MiMo I1: golden coverage broader than expected | Accepted as evidence | `004194` and `006597` have comparable golden rows in the current strict golden corpus; this improves evidence but does not make them baseline-ready. |
| MiMo I2: `006597` block is extraction gaps, not correctness mismatch | Accepted | The score had comparable matches, while quality gate blocked on missing-field rate; the next action is extraction/policy triage, not golden correction. |
| MiMo I3 / GLM F1: checklist CLI flag deviation | Accepted; non-blocking | `checklist` does not support `--dev-override` / `--quality-gate-policy`; the runner used the supported command and recorded the deviation. Future verifier matrices should not assume analyze/checklist flag parity. |
| GLM F2: `scripts/report_quality_eval.py` not run | Accepted; non-blocking | No explicit JSONL bundle was assembled in this gate. This is closed here as `not run: no explicit JSONL bundle input assembled`; no rerun is required because the gate's product smoke, snapshot, score, and quality-gate evidence were sufficient for corpus-routing. |
| GLM F3: golden-missing expectation corrected by evidence | Accepted | The run correctly replaced conservative plan expectations with observed same-year golden coverage for `004194` and `006597`. |
| GLM F4: `006597` kept in evaluation denominator but excluded from golden path | Accepted | Evaluation denominator and golden-ready denominator are distinct. `006597` remains observed evidence but is not suitable for golden promotion while quality gate blocks. |
| GLM F5-F8: scope, exclusion logic, probe-only handling, next recommendation | Accepted | Review confirms no scope drift and directly supports the next-entry decision. |

## Gate Decision

Gate 4 is accepted as an evidence run, but it does **not** satisfy entry conditions for `golden answer corpus v1`.

Reasons:

- clean evaluated coverage is only three candidates / three fund-type slots, below the 5-10 representative target;
- one evaluated clean candidate (`006597`) is quality-gate blocked;
- index and QDII remain fallback-blocked until source failure categories are recovered or candidates are replaced;
- pure FOF remains a `data_gap` / taxonomy residual;
- `004393` / 2025 remains probe-only, not baseline or golden material.

## Next Entry Point

Proceed to `baseline coverage / source recovery / taxonomy + bond extraction triage plan/review`.

Allowed next scope:

- plan/review only first;
- recover or replace fallback-blocked index/QDII candidates without weakening source fail-closed semantics;
- search or classify pure FOF coverage without counting QDII-FOF as pure FOF unless a taxonomy gate accepts it;
- triage `006597` missing-field block to decide whether it is extraction fix, field-applicability policy, or bond-lens evidence-anchor gap;
- keep current renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, source fallback, and golden corpus unchanged until an accepted plan authorizes a narrower implementation slice.

Do not enter `golden answer corpus v1` until the next gate proves sufficient clean coverage and no material source/fund-type blockers.

## Validation

- Product smoke, selected smoke, extraction snapshot, extraction score, and quality-gate commands are recorded in `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`.
- AgentMiMo evidence review verdict: `PASS`.
- AgentGLM evidence review verdict: `PASS_WITH_FINDINGS`; only non-blocking minor findings.
- `git diff --check`: passed in the run artifact.
