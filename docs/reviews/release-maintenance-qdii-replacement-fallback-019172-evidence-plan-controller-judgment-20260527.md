# QDII Replacement Fallback 019172 Evidence Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement fallback candidate evidence plan gate for 019172`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement fallback 040046 evidence accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback candidate evidence plan gate for 019172; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `8f93dcc docs: accept qdii fallback 040046 evidence` |

This plan gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan prepares a future bounded evidence run for exactly `019172` / report_year `2024`.

Pre-evidence state:

| Field | Accepted value |
|---|---|
| `fund_code` | `019172` |
| `report_year` | `2024` |
| Candidate name | `摩根纳斯达克100指数(QDII)人民币A` |
| CSV category | `海外股票类` |
| Source provenance | `provenance_unknown` |
| Quality state | `quality_unknown` |
| Promotion disposition | `not_promoted` |

Preserved prior states:

- `096001` / 2024 remains source-provenance eligible but quality `block`, terminal `quality_blocked_after_provenance`, and `promotion_disposition=not_promoted`.
- `040046` / 2024 remains source-provenance eligible but quality `block`, terminal `quality_blocked_after_provenance`, and `promotion_disposition=not_promoted`.

The plan adds the required explicit terminal-matrix row for eligible provenance plus FQ4 or another non-P0 structural quality block with P0 pass. The terminal classification remains `quality_blocked_after_provenance`; promotion remains `not_promoted`.

The `019172` / `017641` shared visible fund-family prefix `摩根` is accepted only as a disclosure-template risk flag. It is not evidence, not a blocker, and not a reason to infer source or quality state.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-review-ds-20260527.md` | `PASS` |
| AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-review-glm-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS L1: plan-gate `--help` prohibition sits near future-evidence `--help` preflight plan | **accepted as low; no patch required** | The plan clearly distinguishes current plan-gate prohibitions from future evidence-gate preflight. This is readability risk only. |
| DS L2: one future evidence confirmation list is long | **accepted as low; no patch required** | The list is complete and does not create scope ambiguity. |
| GLM findings | **none** | GLM returned `PASS` with no blocking, material, or low findings. |

No blocking or material finding remains. No plan patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement fallback 019172 evidence gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Run only the bounded public evidence sequence for `019172` / 2024 if CLI preflight matches the accepted plan.
- Interpret generated public `summary.md` and `snapshot.jsonl` for source provenance; do not rely on stdout-only provenance.
- Interpret source provenance before score, quality, replacement usefulness, or promotion language.
- Stop fail-closed on `schema_drift`, `identity_mismatch`, or `integrity_error`.
- Keep every terminal outcome `promotion_disposition=not_promoted`.
- Preserve `096001` and `040046` accepted states; do not rerun them.
- Do not run later fallback candidates in the evidence gate.
- Preserve exclusions for `017641`, QDII-FOF candidates, `013308`, and bond QDII candidates.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- AgentCodex plan worker reported `git diff --check` exit code 0.
- Controller reran `git diff --check`; it passed with no output.
- This accepted checkpoint changes docs/review/control artifacts only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `019172` source provenance and quality unknown | `QDII replacement fallback 019172 evidence gate` | Run only the accepted bounded public evidence path and classify from public generated outputs. |
| Same visible fund-family prefix with failed `017641` | `QDII replacement fallback 019172 evidence gate` | Treat only as risk flag; require `019172` generated public evidence for any quality conclusion. |
| `096001` and `040046` quality-blocked after eligible provenance | future QDII replacement decision / diagnosis gate | Do not promote; preserve accepted quality blocks and residuals. |
| QDII replacement still not found | after `019172` evidence gate | If `019172` is not acceptable, open a new candidate-selection or taxonomy decision gate before later rows. |
| FOF / `013308` / bond QDII exclusions | future taxonomy or asset-class fitness gate | Do not use these rows without explicit reviewed controller authorization. |
