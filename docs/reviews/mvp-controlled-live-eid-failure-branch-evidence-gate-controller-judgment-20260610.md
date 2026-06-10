# Controlled Live EID Failure-Branch Evidence Gate Controller Judgment - 2026-06-10

## Judgment

ACCEPT_WITH_RESIDUAL.

This gate accepted the recorded evidence outcome for the single authorized controlled live EID attempt. The live attempt did not produce accepted safe JSON stdout and did not prove live EID failure branches. It is accepted only as a faithful, reviewed record that the authorized command was consumed once and ended in `blocked_helper_serialization_error_after_acquisition`.

No further live command, retry, fallback probe, provider/LLM probe, additional row, fixture projection, golden/readiness promotion, score-loop, release, PR action, push or merge is authorized by this judgment.

## Basis

- `AGENTS.md`: production annual-report access must go through `FundDocumentRepository`; fallback/source policy must remain explicit and fail-closed; Eastmoney, CNINFO and fund-company routes cannot silently re-enter current production source policy.
- `docs/design.md`: current operational source policy is EID single-source MVP; non-EID sources remain future/deferred candidates, not current fallback.
- `docs/implementation-control.md` and `docs/current-startup-packet.md`: the current entry point after downstream integration implementation was controlled live EID failure-branch evidence only with separate explicit live authorization.
- Plan controller judgment: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-controller-judgment-20260610.md` authorized exactly one command: `uv run python scripts/controlled_live_eid_failure_branch_observation.py`.
- Evidence artifact: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-20260610.md`.
- Evidence reviews:
  - `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-review-ds-20260610.md`: `PASS`.
  - `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-review-mimo-20260610.md`: `PASS_WITH_FINDINGS`, with only low/informational findings.

## Accepted Facts

| Fact | Classification |
|---|---|
| The authorized live command was executed exactly once for `006597 / 2024`. | repo/process fact |
| The command exited with code `1`. | repo/process fact |
| stdout was empty. | repo/process fact |
| stderr ended in `AttributeError: 'AnnualReportSourceMetadata' object has no attribute 'identity_status'`. | repo/process fact |
| The traceback reached `_safe_report_payload(report)`. | repo/process fact |
| The helper script calls `_safe_report_payload(report)` only after `repository.load_annual_report()` returns without entering the surrounding `except` block. | repo fact |
| Therefore, the narrow post-acquisition inference is sound: the repository call returned a `report` object before the gate-local helper crashed during safe scalar serialization. | controller inference |
| Because stdout was empty and exit code was non-zero, this is not accepted live success evidence. | controller judgment |
| Because the natural failure category was not produced by EID/FDR acquisition, this is not live failure-branch proof. | controller judgment |
| Accepted no-live checkpoint `ac6bbe9` remains accepted code-behavior proof for `not_found`, `unavailable`, `schema_drift`, `identity_mismatch` and `integrity_error`. | truth-doc fact / accepted checkpoint |

## Finding Disposition

| Finding | Source | Disposition | Controller rationale |
|---|---|---|---|
| Evidence correctly records single live command consumption and no retry authorization. | DS review / MiMo review | ACCEPT | This matches the plan judgment boundary and prevents accidental second live execution under the consumed authorization. |
| stdout empty and exit code `1` mean there is no accepted safe JSON evidence. | DS review / MiMo review | ACCEPT | The gate cannot claim `accepted_live_window_no_failure_observed` without the planned safe scalar output. |
| Post-acquisition wording could explain the traceback inference chain more explicitly. | MiMo F1, low | ACCEPT_WITH_REWRITE | The evidence artifact is acceptable as-is; this judgment supplies the missing explicit inference chain without changing reviewed evidence after review. |
| Helper script reads non-existent `identity_status` and `integrity_status`. | DS review / MiMo F2 | ACCEPT_AS_RESIDUAL | This is a gate-local helper defect, not a production source-policy defect. Repair and any retry require a new reviewed plan and separate live authorization. |
| Evidence artifact covers non-events and does not endorse forbidden fallback/provider/LLM/non-EID actions. | DS review / MiMo F3 | ACCEPT | This preserves EID single-source MVP and prevents old fallback routes from re-entering current design. |

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| `controlled_live_eid_helper_repair_and_retry`: helper attempted to serialize `identity_status` and `integrity_status`, which are not current `AnnualReportSourceMetadata` fields. | future controlled live evidence gate owner | New reviewed plan required before changing the helper and requesting a separate live retry authorization. |
| Live natural occurrence of `not_found`, `unavailable`, `schema_drift`, `identity_mismatch` and `integrity_error` remains unobserved in this gate. | future evidence owner | Keep no-live checkpoint `ac6bbe9` as accepted code-behavior proof; do not claim live natural proof. |
| Non-EID sources remain outside current source policy. | controller | Eastmoney, CNINFO, fund-company official website/CDN and other non-EID routes stay deferred candidates/historical evidence routes only. |

## Validation

Accepted evidence validation:

```bash
git status --short
git status --branch --short
git diff --check
```

Plan checkpoint:

```text
7ebd06d gateflow: accept controlled live EID failure branch plan
```

This judgment should be followed by control-doc sync and a local accepted checkpoint that records the blocked live evidence outcome and next entry.

## Next Entry Recommendation

Recommended mainline next entry:

```text
controlled live EID helper repair and retry planning gate
```

This is a planning/control gate first. It must not run live EID until the helper repair plan is reviewed, accepted, checkpointed, and separately authorized for a new controlled live retry.

Deferred entries:

- `control-doc compression / artifact hygiene gate`
- `CI quality warn-only planning gate`
- broader live EID failure-branch evidence beyond one controlled row
- fallback/source-provider redesign
- golden/readiness promotion
