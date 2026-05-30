# Controller Judgment: share_change Focused Implementation

> Date: 2026-05-27
> Controller: Codex
> Gate: `share_change focused implementation`
> Evidence: `docs/reviews/release-maintenance-share-change-focused-implementation-evidence-20260527.md`
> Reviews:
> - `docs/reviews/release-maintenance-share-change-focused-implementation-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-share-change-focused-implementation-review-glm-20260527.md`
> Targeted re-reviews:
> - `docs/reviews/release-maintenance-share-change-focused-implementation-rereview-mimo-20260527.md`
> - `docs/reviews/release-maintenance-share-change-focused-implementation-rereview-glm-20260527.md`
> Verdict: **ACCEPTED LOCALLY**

## Implementation Judgment

The implementation is accepted. It stayed within the authorized scope:

- changed `fund_agent/fund/extractors/holdings_share_change.py`;
- changed `tests/fund/extractors/test_holdings_share_change.py`;
- did not modify renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, source fallback, PDF/cache helpers, snapshot/score/quality gate, golden corpus, durable fixtures, package config, or GitHub state.

The extractor now generalizes deterministic share-class evidence beyond A/C while preserving fail-closed ambiguity. It can use same-source §2 subordinate fund name / trading-code rows to map a requested `fund_code` to a unique share-class label, then select a unique matching §10 value column. It still rejects default A-class, first non-empty column, total-share column, other-code column, and duplicate same-class columns.

## Review Findings Judgment

| Finding | Judgment | Controller rationale |
|---|---|---|
| MiMo M1 / GLM F1: A-Z bare suffix false positive for ETF/LOF/NAV | Accepted; fixed | `_endswith_bare_share_class_label()` now accepts bare trailing labels only when the preceding character is not a Latin letter. Tests cover ETF/LOF/NAV negative cases and Chinese fund-name suffix positive behavior. Both targeted re-reviews returned `PASS`. |
| GLM F2-F7 / MiMo non-finding criteria | Accepted | Reviewers confirmed split-table generalization, §2 subordinate mapping, tests, 006597 honest missing outcome, and scope boundaries. |

## 006597 Outcome

The post-implementation public rerun still reports `share_change` as `missing` for `006597` / 2024 with the explicit ambiguity note:

`§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别`

This is an accepted outcome. The implementation improved deterministic cases and preserved fail-closed behavior, but current public parsed evidence still cannot prove a unique 006597 §10 share-change column. Quality gate remains `block` due to out-of-scope fields and missing-field rate; no FQ rule was weakened.

## Validation

- `uv run pytest tests/fund/extractors/test_holdings_share_change.py`: `23 passed`
- `uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_holdings_share_change.py`: passed
- `uv run fund-analysis extraction-snapshot --run-id share-change-focused-006597-2024 --fund-code 006597 --report-year 2024`: passed
- `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/share-change-focused-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/share-change-focused-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json`: passed
- `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/share-change-focused-006597-2024/score.json`: passed command execution, status `block`, issues `7`
- `git diff --check`: passed

## Residuals

- `006597` remains blocked; `share_change` still needs more source/parser evidence for that real sample.
- `holdings_snapshot` remains a bond-lens contract gap.
- `turnover_rate` and `holder_structure` remain `needs_more_evidence`.
- `investor_return` and `nav_data` remain score/evidence-contract gaps.
- Golden corpus v1 remains ineligible.

## Next Entry Point

Proceed to `bond-lens contract design + baseline coverage recovery plan/review`.

Do not continue implementing extractor changes until a new reviewed plan selects either:

- additional same-source diagnostic evidence for `006597` share-change;
- bond-specific holdings/risk evidence contract design;
- index/QDII/FOF coverage recovery; or
- a separate score/evidence-contract slice.
