# QDII Replacement Post-019172 Disposition Decision — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement post-019172 disposition decision gate`
> Decision artifact: `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement fallback 019172 evidence accepted locally` |
| Startup Packet next entry point | `QDII replacement post-019172 disposition decision gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `d2fdbdb docs: accept qdii fallback 019172 evidence` |

This decision gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Decision

The accepted disposition is to run one more plan-first QDII replacement gate for exactly `021539` / 2024.

Rationale:

- `096001`, `040046`, and `019172` all have eligible public fallback provenance but quality `block` and `promotion_disposition=not_promoted`.
- Three quality blocks are a structural warning, but they do not prove the next accepted non-FOF overseas equity QDII row will fail.
- The accepted enumeration order puts `021539` after the three failed candidates.
- A single-candidate plan-first gate respects enumeration order while preventing blind probing.
- If `021539` later quality-blocks after eligible provenance, automatic QDII probing must stop and a new disposition gate must choose between QDII diagnosis, taxonomy / asset-class fitness, or recording QDII coverage blocked.

Accepted next entry point:

`QDII replacement fallback candidate evidence plan gate for 021539`

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-review-glm-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS F1: one stop condition is forward-looking plan-gate guidance | **accepted as low; no patch required** | The next plan gate must restate the command/direct-access boundary. Keeping it here as early guardrail is harmless and useful. |
| DS F2: `evidence plan gate` naming can be misread as evidence authorization | **accepted as low; mitigated by control wording** | The accepted next entry point remains a plan gate; Startup Packet and handoff must explicitly prohibit evidence until reviewed acceptance. |
| DS F3: validation section does not state why ruff/pytest are unnecessary | **accepted as low; no patch required** | This was a decision-only docs artifact. `git diff --check` is sufficient; no source/test change occurred. |
| GLM findings | **none** | GLM confirmed DS findings remain low and do not affect correctness. |

No blocking or material finding remains. No decision patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement fallback candidate evidence plan gate for 021539`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Produce a plan artifact before any evidence run.
- Select exactly one candidate: `021539` / report_year `2024`.
- Treat `021539` as `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted` until a reviewed evidence gate proves otherwise.
- Preserve `096001`, `040046`, and `019172` as source-provenance eligible but quality `block`, terminal `quality_blocked_after_provenance`, and `promotion_disposition=not_promoted`.
- Do not run evidence in the plan gate.
- Do not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, or `019172` in the plan gate.
- Preserve fail-closed source semantics: `schema_drift`, `identity_mismatch`, and `integrity_error` stop; only `not_found` / `unavailable` can make fallback eligible.
- Preserve generated-public-output provenance discipline; no stdout-only or internal-file provenance.
- If a later accepted `021539` evidence gate quality-blocks after eligible provenance, stop automatic QDII probing and open a new disposition gate.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Decision worker reported `git diff --check` exit code 0.
- No evidence command, `fund-analysis` command, code/test change, product-flow change, promotion, commit, push, or GitHub mutation was authorized by the worker.
- This accepted checkpoint changes docs/review/control artifacts only.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| QDII replacement candidate quality blocks across three attempts | `021539` plan gate then possible evidence gate | Only one more plan-first candidate is accepted; stop automatic probing if it also quality-blocks. |
| `096001`, `040046`, `019172` quality-blocked after eligible provenance | future QDII disposition / diagnosis gate | Do not promote; preserve blockers and residuals. |
| QDII-FOF / `013308` / bond QDII exclusions | future taxonomy or asset-class fitness gate | Do not use without explicit reviewed controller authorization. |
| Golden/baseline blocked by QDII coverage | future baseline/golden gate | Do not enter golden answer corpus v1 until QDII disposition and other coverage blockers are resolved or explicitly excluded. |
