# QDII Replacement Fallback 040046 Evidence Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement fallback candidate evidence plan gate for 040046`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement candidate evidence accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback candidate evidence plan gate for 040046; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `c6a5042 docs: accept qdii replacement evidence` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan selects exactly one fallback evidence candidate:

| Field | Accepted planned value |
|---|---|
| `fund_code` | `040046` |
| `report_year` | `2024` |
| Fund name | `华安纳斯达克100ETF联接(QDII)A` |
| CSV category | `海外股票类` |
| Current provenance | `provenance_unknown` |
| Current quality | `quality_unknown` |
| Promotion state | `promotion_disposition=not_promoted` |

The plan preserves the accepted `096001` state: source-provenance eligible but quality `block`, terminal `quality_blocked_after_provenance`, and `not_promoted`. It does not rerun or weaken `096001`.

The future `040046` evidence gate must use the accepted public CLI shape, read provenance from generated public files (`summary.md` and `snapshot.jsonl`), interpret provenance before quality, stop on fail-closed source categories, and keep every terminal state `promotion_disposition=not_promoted`.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-review-ds-20260527.md` | `PASS` |
| AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-review-glm-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS: no blocking/material findings | **accepted** | DS verified Startup Packet alignment, single-candidate discipline, 096001 preservation, public CLI/path conventions, provenance-before-quality ordering, terminal matrix, and exclusions. |
| GLM: no blocking/material findings | **accepted** | GLM independently confirmed the same plan properties and noted the generated-output provenance rule directly addresses the 096001 evidence review failure. |
| DS/GLM residual: `040046` may repeat QDII P0 quality failures | **accepted as evidence-gate residual** | The evidence gate will classify outcomes without promotion; root-cause diagnosis requires a later separate gate. |
| DS/GLM residual: provenance may fail or remain unknown | **accepted as evidence-gate residual** | The future evidence gate has explicit stop states for fail-closed, missing, incomplete, or ineligible provenance. |

No blocking or material finding remains. No plan patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement fallback 040046 evidence gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Run evidence only for `040046` / 2024.
- Use public CLI preflight and explicit public command paths only.
- Keep generated outputs under ignored `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527`.
- Read source provenance from generated public `summary.md` and `snapshot.jsonl`, not stdout-only.
- Interpret source provenance before score/quality and stop on fail-closed categories.
- Run score and quality gate only after eligible provenance.
- Record P0/P1 issues, `manager_strategy_text`, false-positive suspicion, terminal classification, and `promotion_disposition=not_promoted`.
- Do not run `019172` or later fallback rows.
- Preserve exclusions for `017641`, QDII-FOF, `013308`, and bond QDII candidates.
- Produce a tracked evidence summary, two independent evidence reviews, controller judgment, and control-doc update.

Do not modify code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Planning worker reported `git diff --check` passed.
- AgentDS and AgentGLM completed independent plan reviews.
- This gate is docs/review/control only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `040046` provenance unknown | QDII replacement fallback 040046 evidence gate | Prove from public generated files or stop not promoted. |
| `040046` quality unknown | QDII replacement fallback 040046 evidence gate | Run score/quality only after eligible provenance; record terminal state. |
| Possible repeated QDII P0 `nav_benchmark_performance` gap | future QDII diagnosis or replacement decision gate | Do not diagnose or fix in evidence gate; classify and keep not promoted. |
| Possible P0 `manager_strategy_text` gap | future QDII diagnosis or replacement decision gate | Classify from public evidence; no extractor/policy change in evidence gate. |
| `019172` remains contingency-only | future fallback plan gate if `040046` fails | Do not run without a new accepted plan. |
