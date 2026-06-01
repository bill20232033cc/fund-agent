# release-maintenance share_change focused implementation evidence - 2026-05-27

## Scope

- Gate: `share_change focused implementation`.
- Plan: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-20260527.md`.
- Controller judgment: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-controller-judgment-20260527.md`.

This implementation stayed within the authorized narrow scope. It did not modify renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, source fallback, direct PDF/cache/source helpers, golden corpus, durable fixtures, package config, or GitHub state.

## Changed files

| File | Change |
| --- | --- |
| `fund_agent/fund/extractors/holdings_share_change.py` | Generalized deterministic share-class evidence from A/C-only handling to supported A-Z share labels; allowed §2 subordinate fund name / trading-code mapping tables even when they are not embedded in the broader fund identity table; preserved exact fund-code header priority and fail-closed ambiguity behavior. |
| `tests/fund/extractors/test_holdings_share_change.py` | Added focused synthetic `ParsedAnnualReport` / `ParsedTable` tests for A/C/E/F bond share-class selection, subordinate-row-only §2 mapping, and duplicate same-class §10 ambiguity. |

No `fund_agent/fund/extractors/models.py` change was needed because existing `ExtractedField.value` already carries `share_class_column` and `share_class_selection_reason`.

No README update was needed because the change is private extractor behavior and does not alter public commands or documented Fund package workflow.

## Behavior summary

Implemented behavior:

- A §10 share-change value column is selected only when deterministic evidence ties it to the requested `fund_code`.
- Existing exact `fund_code` header selection remains the highest-priority deterministic path.
- Same-source §2 subordinate fund name / trading-code rows can now map the requested `fund_code` to a unique share-class label beyond A/C, such as E/F classes, before selecting a unique matching §10 value column.
- §2 mapping tables that contain subordinate fund name/code rows are accepted as share-class evidence even if they do not include the broader `基金名称` / `基金主代码` identity rows.
- Duplicate matching share-class columns still fail closed.
- The extractor still rejects default A-class, first-column, total-share, and other-code fallback behavior.

Out of scope and unchanged:

- `holdings_snapshot`, `turnover_rate`, `holder_structure`, `investor_return`, and `nav_data`.
- Snapshot field comparability, score priorities, quality-gate thresholds, quality-gate severity, and CLI defaults.

## Review-fix M1/F1

Material review finding M1/F1 identified that bare `endswith(label)` became too broad after A-Z share-class generalization. English suffixes such as ETF, LOF, and NAV could be misread as F/V share-class labels.

Fix:

- Tightened bare suffix matching so a trailing class label is accepted only when the previous character is not a Latin letter.
- Kept explicit `A类` / `A份额` style matching unchanged.
- Added focused tests proving ETF/LOF/NAV-like headers do not trigger share-class detection or unsafe selection.
- Added a positive regression proving Chinese fund-name suffixes such as `债券A` still work.

## Validation

| Command | Result |
| --- | --- |
| `uv run pytest tests/fund/extractors/test_holdings_share_change.py` | pass; 23 passed after M1/F1 fix |
| `uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_holdings_share_change.py` | pass |
| `uv run fund-analysis extraction-snapshot --run-id share-change-focused-006597-2024 --fund-code 006597 --report-year 2024` | pass, exit 0 |
| `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/share-change-focused-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/share-change-focused-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | pass, exit 0 |
| `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/share-change-focused-006597-2024/score.json` | pass command execution, exit 0; gate status remains `block` |
| `git diff --check` | pass, exit 0 after M1/F1 fix |

Scratch/public output paths:

- `/tmp/fund-agent-share-change-focused-20260527/`
- `reports/extraction-snapshots/share-change-focused-006597-2024/`

## 006597 post-run outcome

Public extraction run succeeded:

- `snapshot.jsonl`: 16 records.
- `errors.jsonl`: 0 records.
- `share_change` row remains `extraction_mode="missing"`, `value_present=false`, `anchor_present=false`.
- `share_change` note remains: `§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别`.

Public score/gate outcome:

- `score.md`: `share_change` remains P1 fail with 0.0% coverage / traceability.
- `score.md`: 006597 P1 failed fields remain `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`.
- `quality_gate.md`: status remains `block`; issues remain 7.
- `quality_gate.md`: FQ4 remains block due missing-field rate 35.7% against 35.0% threshold.

Interpretation:

- The implementation broadens deterministic same-source share-class mapping and preserves fail-closed behavior.
- The real 006597 parsed public extraction output still does not provide enough deterministic evidence, under current allowed public paths, to select a unique §10 share-change column.
- No wrong-column fallback was introduced. The remaining 006597 gap should be treated as `needs_more_evidence` or a follow-up diagnostic/design question, not as a reason to weaken FQ gates.

## Blocker status

Execution blocker: none. Required tests and public CLI commands completed.

Residual data blocker: yes for 006597. The actual public rerun still cannot deterministically select `share_change` without additional evidence about the parsed §2/§10 table relationship. Under the current no direct PDF/cache/source-helper constraint, the implementation correctly preserves explicit ambiguity instead of guessing.

## Closeout validation

- `git diff --check`: pass, exit 0.
