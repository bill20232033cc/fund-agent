# QDII Replacement Fallback 021539 Evidence Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement fallback candidate evidence plan gate for 021539`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement post-019172 disposition decision accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback candidate evidence plan gate for 021539; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `bdae33c docs: accept qdii post 019172 disposition` |

This plan gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan prepares a future bounded public evidence run for exactly `021539` / report_year `2024`.

Pre-evidence state:

| Field | Accepted value |
|---|---|
| `fund_code` | `021539` |
| `report_year` | `2024` |
| Candidate name | `华安法国CAC40ETF发起式联接(QDII)A` |
| CSV category | `海外股票类` |
| Source provenance | `provenance_unknown` |
| Quality state | `quality_unknown` |
| Promotion disposition | `not_promoted` |

The plan preserves `096001`, `040046`, and `019172` as source-provenance eligible but quality `block`, terminal `quality_blocked_after_provenance`, and `promotion_disposition=not_promoted`.

The plan includes the required hard stop: if a later accepted `021539` evidence gate quality-blocks after eligible provenance, automatic QDII probing stops and the next step must be a new disposition gate.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-review-glm-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS F1: `evidence plan` naming ambiguity recurs | **accepted as low; no patch required** | The plan and Startup Packet explicitly prohibit evidence until reviewed acceptance. Future naming can be tightened, but this artifact is not ambiguous in substance. |
| DS F2: quality classification guidance is detailed and could look pre-scripted | **accepted as low; no patch required** | The guidance is framed as future evidence instructions and remains tied to generated public outputs. Future evidence must still classify actual outputs independently. |
| GLM F1: `096001` P0 detail compressed | **accepted as low; no patch required** | The preserved-state summary keeps the P0 field, terminal state, and promotion state; exact failure detail remains available in accepted evidence artifacts. |
| GLM F2: `040046` `issue_count=7` omitted from preserved-state summary | **accepted as low; no patch required** | The key accepted blockers and terminal state are preserved; issue count is not needed for this plan gate's correctness. |

No blocking or material finding remains. No plan patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement fallback 021539 evidence gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Run only the bounded public evidence sequence for `021539` / 2024 if CLI preflight matches the accepted plan.
- Interpret generated public `summary.md` and `snapshot.jsonl` for source provenance; do not rely on stdout-only provenance.
- Interpret source provenance before score, quality, replacement usefulness, or promotion language.
- Stop fail-closed on `schema_drift`, `identity_mismatch`, or `integrity_error`.
- Keep every terminal outcome `promotion_disposition=not_promoted`.
- Preserve `096001`, `040046`, and `019172` accepted states; do not rerun them.
- Do not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, `019172`, or any later candidate in the evidence gate.
- If quality blocks after eligible provenance, record that automatic QDII probing stops and a new disposition gate is required.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Planning worker and reviews reported `git diff --check` exit code 0.
- Controller ran `git diff --check`; it passed with no output.
- This accepted checkpoint changes docs/review/control artifacts only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `021539` source provenance and quality unknown | `QDII replacement fallback 021539 evidence gate` | Run only the accepted bounded public evidence path and classify from public generated outputs. |
| Automatic QDII probing stop condition | `QDII replacement fallback 021539 evidence gate` | If quality-blocked after eligible provenance, record stop and route to new disposition gate. |
| Prior QDII candidates remain quality-blocked | future QDII disposition / diagnosis gate | Do not promote `096001`, `040046`, or `019172`. |
| QDII-FOF / `013308` / bond QDII exclusions | future taxonomy or asset-class fitness gate | Do not use without explicit reviewed controller authorization. |
