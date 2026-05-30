# Controller Judgment: bond-lens score applicability implementation

> Controller: Codex
> Date: 2026-05-27
> Gate: `bond-lens score applicability implementation gate`
> Latest accepted checkpoint before gate: `02741e0`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering implementation | `bond-lens score applicability design accepted locally` |
| Next entry point implemented | `bond-lens score applicability implementation gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted design artifacts |

## Decision

Accepted.

The implementation satisfies the accepted design: exact `bond_fund` equity-shaped `holdings_snapshot` is removed from stock-holdings scoring denominator only with paired `bond_risk_evidence.v1` replacement issue output. FQ0-FQ6 policy semantics and thresholds are unchanged; `bond_risk_evidence_missing` projects to existing warn-level FQ2F. Unknown or conflicted fund types remain fail-closed.

## Files Changed

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-evidence-20260527.md`
- `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-review-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-review-glm-20260527.md`
- `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-rereview-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-rereview-glm-20260527.md`

## Review Summary

| Reviewer | Initial verdict | Re-review | Controller disposition |
|---|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | `PASS` | Accepted. Finding 01 fixed; finding 02 deferred as future compatibility observation. |
| AgentGLM | `PASS_WITH_FINDINGS` | `PASS` | Accepted. Shared issue-id validation observation fixed; other observations remain non-material. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| issue_id validation only checked prefix/suffix | MiMo F1 / GLM O3 | Accepted and fixed | `_validate_score_applicability_issue_id()` now reconstructs the full deterministic id including `report_year` and requires exact equality; focused wrong-year test added. |
| unknown future `issue_code` silently ignored | MiMo F2 | Deferred | Current implementation emits only `bond_risk_evidence_missing`. Future score-applicability code expansion must update quality gate projection or add an info-level fallback. |
| raw_total_field_count means "before bond applicability" not global raw | GLM O1 | Accepted as documented residual | Current field-applicability decision explains bond delta, not every previous applicability filter. This is acceptable for exact bond-fund gate. |
| repeated records-by-fund grouping | GLM O2 | Rejected as non-material | Non-hot path; no correctness or maintainability impact at current scale. |

## Validation

| Command / check | Result |
|---|---|
| `uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | `72 passed` |
| `uv run pytest tests/fund/test_quality_gate.py -q` | `30 passed` after targeted fix |
| `uv run ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py` | passed |
| `uv run ruff check fund_agent/fund/quality_gate.py tests/fund/test_quality_gate.py` | passed after targeted fix |
| `git diff --check` | passed |
| 006597 public snapshot/score/quality-gate evidence | passed; gate status `warn`, not `pass` |

006597 evidence summary:

- Before: raw `missing_field_count / total_field_count = 5 / 14 = 35.71%`, FQ4 block.
- After: applicable `4 / 13 = 30.77%`, FQ4 warn.
- Replacement issue id: `score-applicability:006597:2024:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1`.
- Quality gate includes `FQ2F/warn` with `reason=bond_risk_evidence_missing`.
- `baseline_blocking=true` is emitted in score JSON, but durable baseline/golden promotion remains future-gate blocked.

## Scope Guard

No changes were made to renderer, Service/CLI behavior, Host/Agent packages, Dayu runtime, `FundDocumentRepository`, source strategy/helpers/cache/downloaders, extractor logic, `fund_type.py`, golden/baseline fixtures, FQ0-FQ6 thresholds/policy, `extra_payload`, or GitHub state.

## Residual Risks

- Positive `bond_risk_evidence.v1` extraction/evidence input is not implemented. Current exact `bond_fund` snapshots without reviewed bond-risk evidence correctly emit `bond_risk_evidence_missing`.
- `baseline_blocking=true` is output but not yet consumed by a durable baseline/golden gate.
- `006597` still has non-holdings P1 gaps: `holder_structure`, `share_change`, and `turnover_rate`.
- Future score-applicability issue codes must either project to quality gate or explicitly document why they are ignored.

## Next Entry Point

`baseline coverage recovery decision gate`

Next work should decide whether to recover/replace index/QDII/FOF coverage candidates or continue bond evidence hardening. Do not enter `golden answer corpus v1` until coverage/source/fund-type blockers and bond-risk evidence residuals are resolved.
