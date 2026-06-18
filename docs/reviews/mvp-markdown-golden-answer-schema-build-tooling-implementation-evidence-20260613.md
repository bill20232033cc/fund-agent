# MVP Markdown Golden Answer Schema Build-tooling Implementation Evidence - 2026-06-13

## Gate

- Gate: Markdown / Golden Answer Schema Build-tooling Implementation Gate
- Basis:
  - `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-plan-20260613.md`
  - `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-plan-controller-judgment-20260613.md`
- Status: implementation evidence ready for review

## Scope Boundary

- No live EID / network / PDF / FDR / provider / LLM / analyze / checklist / readiness / release / PR command was run.
- No tracked golden answer content under `reports/golden-answers/*` was modified.
- No fixture promotion file was modified.
- No source acquisition policy or fallback design was modified.
- No stage / commit / push / PR was performed.

## Implemented Changes

### `fund_agent/fund/golden_answer.py`

- Added a reviewed Markdown fund-level fenced metadata block:

  ````markdown
  ```golden-answer-metadata
  report_year: 2025
  ```
  ````

- Missing metadata preserves the existing legacy reviewed corpus behavior and parses as `report_year=2024`.
- The parser now writes `report_year` to both `GoldenAnswerFund` and `GoldenAnswerRecord`.
- Duplicate identity is checked across `fund_code + report_year + field_name + sub_field`.
- Same fund code across different years is allowed.
- Duplicate fund blocks for the same `fund_code + report_year` fail validation.
- Invalid metadata fails validation:
  - metadata before a fund heading
  - metadata after the first table
  - duplicate metadata block
  - unclosed metadata fence
  - unknown metadata key
  - duplicate metadata key
  - non-integer `report_year`
  - missing `report_year`
- `source` remains a human evidence description and is not used to infer machine identity.

### `tests/fund/test_golden_answer.py`

- Added coverage for:
  - explicit `golden-answer-metadata` `report_year`
  - `build_golden_answer_json()` end-to-end output of explicit metadata `report_year`
  - same fund code across different years
  - duplicate same-fund same-year block rejection
  - invalid metadata variants
  - late metadata rejection
  - unclosed metadata rejection
- Existing strict JSON loader and legacy 2024 behavior remain covered.

### Operator And Truth Documentation

- `docs/golden-answer-instructions.md`
  - Replaced 2024-only source wording with `report_year`-scoped annual report wording.
  - Added fund-level metadata instructions.
  - Clarified that legacy reviewed Markdown without metadata is only 2024-compatible.
- `docs/golden-answer-template.md`
  - Added `golden-answer-metadata` blocks with `report_year: 2024` to each current template fund section.
  - Kept expected values empty; no reviewed golden content was added.
- `docs/design.md`
  - Recorded the implemented reviewed Markdown metadata path as current fact.
  - Clarified that `source` text cannot infer machine identity.
- `fund_agent/fund/README.md`
  - Documented the build-tooling behavior, duplicate checks, and no-PDF/cache boundary.
- `tests/README.md`
  - Documented test coverage for metadata, legacy compatibility, and fail-fast validation.
- `README.md`
  - Added user-facing note for reviewed Markdown metadata and strict identity.

## Validation

```text
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
..................................                                       [100%]
34 passed in 0.77s
```

```text
uv run ruff check fund_agent/fund/golden_answer.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
All checks passed!
```

```text
git diff --check
<no output>
```

## Residuals

| Residual | Status | Owner / Next Gate |
|---|---|---|
| Same-year `004393 / 2025` reviewed evidence/content is still not accepted | Deferred | Separate no-live reviewed evidence/content gate |
| Tracked `reports/golden-answers/*` content remains unchanged in this gate | Accepted boundary | Future content gate only |
| Live EID evidence remains outside this gate | Deferred | Controlled live gate only if separately authorized |

## Reviewer Questions

1. Does the implementation satisfy the accepted plan's Markdown-first write authority without creating JSON-only content authority?
2. Does the parser preserve legacy 2024 behavior while making future same-fund multi-year records explicit?
3. Are metadata validation and duplicate identity checks sufficient for the next reviewed content gate?
4. Did documentation drift into source acquisition policy or fallback design?

## Recommended Next Step

Proceed to implementation review by two independent reviewers, then controller judgment. If accepted, sync `docs/current-startup-packet.md` and `docs/implementation-control.md` and set the next entry to a no-live same-year reviewed evidence/content planning gate for `004393 / 2025`.
