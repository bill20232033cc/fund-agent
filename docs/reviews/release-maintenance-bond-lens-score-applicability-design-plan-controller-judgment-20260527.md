# Controller Judgment: bond-lens score applicability design plan

> Controller: Codex
> Date: 2026-05-27
> Target plan: `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-20260527.md`
> Reviews: `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-review-mimo-20260527.md`, `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-review-glm-20260527.md`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `bond-lens contract + baseline coverage recovery plan accepted locally` |
| Reviewed next entry | `bond-lens score applicability design gate` |
| Latest accepted checkpoint before this judgment | `c09a4cb` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, current accepted artifacts |

## Decision

Accepted.

The design is accepted as the implementation basis for the next gate. It does not itself modify product behavior. The next entry point is `bond-lens score applicability implementation gate`, scoped to `fund_agent/fund/extraction_score.py`, `fund_agent/fund/quality_gate.py`, focused tests, and README sync only if behavior documentation changes.

The accepted implementation principle is:

- For exact `bond_fund`, equity-shaped `holdings_snapshot` must not count as a stock-holdings coverage denominator item.
- That exclusion is valid only with explicit `bond_risk_evidence.v1` replacement issue output.
- The replacement issue preserves FQ0-FQ6 semantics by projecting as warn-level FQ2F while remaining baseline/golden blocking.
- Unknown or conflicted fund types remain fail-closed and keep the conservative denominator.

## Review Summary

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted; findings are non-blocking implementation refinements. |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted; findings are non-blocking implementation refinements. |

## Finding Disposition

| Finding | Source | Controller status | Implementation requirement |
|---|---|---|---|
| `BondRiskEvidenceGroup` dataclass fields implied but not explicit | MiMo F1 / GLM F4 | Accepted | Implementation must define explicit fields: `group_id`, `required_evidence`, `allowed_na_reasons`, `failure_behavior`, plus severity/baseline metadata if consumed by issue generation. |
| `bond_risk_data_gap_declared` severity under-specified | MiMo F2 | Accepted as defaulting rule | First slice should default data-gap and partial bond-risk states to warn/baseline-blocking unless a later baseline gate explicitly accepts a group as non-blocking. |
| Optional `QualityGateIssue` extension underspecified | MiMo F3 | Deferred | First slice should avoid extending `QualityGateIssue` unless necessary; use existing `reason` / message fields for deterministic visibility. Any dataclass extension needs focused compatibility tests. |
| Raw/applicable denominator metadata location ambiguous | MiMo F4 / GLM F1 | Accepted | Prefer outputting detailed raw/applicable metadata in `field_applicability_decisions`; add a compact summary only if `quality_gate.py` needs it. Code comments must clarify that `FundQualityRow.missing_field_rate` is applicable-rate after fund-type applicability filtering. |
| `_scorable_records()` refactor risk across call sites | MiMo F5 | Accepted | Implementation should compose the existing index-applicability helper pattern, not replace the scoring pipeline wholesale. Preserve function signature unless tests prove a narrow signature change is safer. |
| Older `score.json` compatibility parsing | MiMo F6 | Accepted | `quality_gate.py` must treat missing `score_applicability_issues` as an empty list and keep existing score payloads valid. |
| `baseline_blocking` consumer undefined | GLM F2 | Deferred | Current baseline/golden promotion remains gate-blocked by control doc. Future golden/baseline gate must define the concrete consumer for `baseline_blocking`. |
| Local `BOND_FUND_TYPE` constant vs canonical `FundType` | GLM F3 | Accepted | Minimal implementation may use a local constant following existing local-constant style, with a comment linking it to the canonical `bond_fund` literal. Do not modify `fund_type.py` unless a later taxonomy gate accepts that scope. |
| First implementation emits `bond_risk_evidence_missing` for all current bond-fund snapshots | GLM F5 | Accepted | This is the correct fail-closed behavior while bond-risk extraction is out of scope. |

## Accepted Implementation Scope

Allowed:

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- adjacent focused quality-gate integration tests only if existing JSON consumers require them
- `fund_agent/fund/README.md` and `tests/README.md` only if behavior or test organization changes
- tracked implementation/review artifacts under `docs/reviews/`

Forbidden:

- Renderer changes.
- FQ0-FQ6 policy, threshold, or severity weakening.
- Service/CLI behavior changes.
- Host/Agent package creation or Dayu runtime integration.
- `FundDocumentRepository`, source strategy, source-helper, downloader, cache, or direct PDF access changes.
- Extractor logic changes.
- Golden corpus, durable baseline, or fixture promotion.
- Explicit parameters through `extra_payload`.
- GitHub mutation.

## Required Validation For Implementation Gate

- Focused extraction-score tests for bond-fund exclusion plus replacement issue, active fund regression, index/enhanced regression, unknown/conflicted fail-closed behavior, and deterministic issue ids.
- Focused quality-gate tests for optional `score_applicability_issues`, FQ2F warn projection, malformed issue fail-fast, missing-key backward compatibility, and FQ4 threshold preservation.
- 006597 / 2024 public snapshot/score/quality-gate evidence run showing before/after raw/applicable denominator and replacement issue id.
- `uv run ruff check` on touched files.
- `git diff --check`.

Full pytest is not required for the next narrow implementation gate unless implementation expands shared schema behavior beyond the accepted file scope or focused tests expose broader coupling.

## Next Entry Point

`bond-lens score applicability implementation gate`

The implementation gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent handoff. Implementation must go through worker implementation, two independent code reviews, controller judgment, control-doc update, validation, and a local accepted commit.
