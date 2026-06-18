# QDII Replacement Candidate Evidence Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement candidate evidence plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement candidate enumeration plan accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate evidence plan gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `461ff08 docs: accept qdii replacement enumeration plan` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan defines the next evidence gate for exactly one candidate: `096001` / 2024 / 大成标普500等权重指数(QDII)A人民币.

The candidate remains `source_provenance=provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted`. This plan does not make `096001` source-safe, quality-passing, scoring-ready, baseline-ready, golden-ready, accepted as a replacement, or promoted.

The future evidence gate must run public CLI preflight first, then only the planned public `extraction-snapshot`, `extraction-score`, and `quality-gate` path if flags match. Source provenance must be interpreted before quality. Fail-closed source categories must stop the gate. Every terminal outcome remains `promotion_disposition=not_promoted`.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-review-mimo-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| MiMo F1: `reports/` ignored-output status not explicitly stated | **accepted as evidence-gate preflight requirement** | The future evidence artifact must confirm generated output paths remain ignored or otherwise not staged. |
| MiMo F2: `--force-refresh` rationale not explained | **accepted as evidence-gate documentation requirement** | The future evidence artifact must record that `--force-refresh` is intentional to avoid stale metadata masking source provenance. |
| MiMo F3: expected output paths are plausible but unverified | **accepted as evidence-gate recording requirement** | The future evidence artifact must record actual generated paths and not assume `golden_set.json` or any optional path exists. |
| DS F1: `golden_set.json` may not be generated without `--golden-answer-path` | **accepted as evidence-gate recording requirement** | The future runner must record actual output paths and must not treat missing `golden_set.json` as a failure unless the public CLI contract requires it. |
| DS F2: `quality-gate --score-path` stale default risk | **accepted as command requirement** | The future evidence gate must pass `--score-path` explicitly and must not rely on CLI defaults. |
| DS F3: `--golden-answer-path` omitted from preflight criteria | **accepted as non-blocking** | This evidence gate intentionally does not run strict golden comparison. Golden answer corpus remains blocked until a separate gate. |
| DS review process note: review mentions actual CLI help output despite plan-only no-command handoff | **accepted as process deviation; not used as acceptance evidence** | CLI help is not fund evidence, but the handoff forbade `fund-analysis` commands. Controller acceptance relies on the plan text, existing accepted artifacts, and reviewer judgments, not on any new CLI-help fact. Future review handoffs should repeat that no public CLI command, including help, may be run unless explicitly authorized. |

No blocking or material finding remains. No plan patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement candidate evidence gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state that this follows the accepted next entry point, not a gate switch.
- Run public CLI help/preflight first and stop with `terminal_classification=cli_flag_mismatch_not_run` if flags differ.
- Run evidence only for `096001` / 2024 unless the controller explicitly changes the candidate in a later gate.
- Use only public CLI commands planned in the accepted evidence plan:
  - `uv run fund-analysis extraction-snapshot ... --fund-code 096001 --report-year 2024 --source-csv docs/code_20260519.csv --force-refresh`
  - `uv run fund-analysis extraction-score ...`
  - `uv run fund-analysis quality-gate ...`
- Pass explicit paths, especially `--score-path`; do not rely on stale CLI defaults.
- Keep generated outputs in ignored report paths and record actual generated paths in a tracked summary artifact.
- Interpret public source provenance before quality or promotion language.
- Stop on fail-closed source categories: `schema_drift`, `identity_mismatch`, `integrity_error`.
- Treat missing/incomplete public provenance as not eligible, not as fallback permission.
- Interpret `manager_strategy_text` P0 only after provenance is eligible.
- Record terminal classification and `promotion_disposition=not_promoted` for every outcome.
- Do not run fallback candidates in this gate.

Do not modify code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- The planning worker reported `git diff --check` passed.
- AgentMiMo and AgentDS completed independent plan reviews.
- This gate is docs/review/control only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `096001` source provenance unknown | QDII replacement candidate evidence gate | Prove or reject using public provenance tuple before quality interpretation. |
| `096001` quality unknown, especially `manager_strategy_text` P0 | QDII replacement candidate evidence gate | Interpret only after eligible provenance; keep not promoted on block. |
| Actual generated path set may differ from plan examples | QDII replacement candidate evidence gate | Record actual paths and keep scratch outputs ignored/untracked. |
| CLI default path risk | QDII replacement candidate evidence gate | Pass explicit `--score-path` and output paths. |
| `013308` naming/category conflict, QDII-FOF taxonomy, bond QDII asset-class mismatch | Future taxonomy/controller gates | Keep out of this evidence gate. |
