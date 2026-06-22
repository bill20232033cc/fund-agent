# EC-P2 Live Sample Controller Judgment

Date: 2026-06-22

## Verdict

`ACCEPT_LIVE_EXECUTED_PATHWAY_PARTIAL_EVIDENCE_V2_WARN_NOT_READY`

## Accepted Inputs

- User authorization: `同意 EC-P2：sample 004393/2025，授权 repository-bounded live/PDF 命令。`
- No-live implementation controller judgment: `docs/reviews/evidence-confirm-productionization-ec-p2-implementation-controller-judgment-20260622.md`
- Live sample evidence: `docs/reviews/evidence-confirm-productionization-ec-p2-live-sample-evidence-20260622.md`

## Accepted Positive Facts

- The authorized live command was executed:
  - `uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh`
- Command exit code was `0`.
- Output was safe scalar JSON.
- `source_metadata_admitted=true`.
- `reference_count=1`.
- `field_correctness_proven=false`.

## Accepted Negative Facts

- `status="fail"`.
- `evidence_confirm_overall_status="warn"`.
- EC-P2 live sample cannot be accepted as pass.
- No readiness, release, golden, semantic entailment, full source-truth or PR state claim is proven.

## Decision

Accept the live run as bounded evidence that the repository-bounded pathway reaches source metadata admission and reference materialization for the authorized sample.

Do not accept EC-P2 as complete. The next gate must disposition the V2 `warn` / runner `fail` result before any EC-P2 pass, push, PR update, readiness or release claim.

## Next Gate

EC-P2 live warning disposition / fix planning.

Minimum decision required:

- If V2 `warn` is expected for section-smoke pathway evidence, plan and review a narrow aggregation/smoke-policy adjustment.
- If V2 `warn` is not acceptable, plan and review a smoke projection adjustment that can produce a V2 pass without asserting field correctness.

No further live/PDF execution should occur until that plan and no-live fix/review path is accepted.
