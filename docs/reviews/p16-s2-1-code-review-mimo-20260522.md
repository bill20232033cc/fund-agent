# P16-S2.1 Benchmark Text Newline Normalization Code Review — AgentMiMo（2026-05-22）

## Verdict

`PASS`

Implementation correctly and narrowly implements the accepted plan. No correctness, stability, or scope violations found. One minor observation recorded but does not rise to finding severity.

## Review Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` | Accepted plan |
| `docs/reviews/p16-s2-1-plan-review-controller-judgment-20260522.md` | Controller judgment with implementation constraints |
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-implementation-20260522.md` | Implementation artifact under review |
| `fund_agent/fund/extractors/profile.py` | Source changes (workspace diff) |
| `tests/fund/extractors/test_profile.py` | Test changes (workspace diff) |

Excluded inputs not read: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Scope Compliance

| Constraint | Status | Evidence |
|---|---|---|
| Only `profile.py` and `test_profile.py` modified | PASS | `git diff HEAD --name-only` shows exactly 2 source files |
| No golden file edits | PASS | No files under `reports/golden-answers/` changed |
| No design/control/CSV/RR-13 edits | PASS | Only `docs/reviews/p16-s2-1-code-review-mimo-20260522.md` added as artifact |
| No direct PDF/cache/source helper access | PASS | All verification through `FundDataExtractor` |
| No `tracking_error`, `benchmark_index_name` synthesis, external adapters | PASS | Implementation touches only newline normalization |
| No excluded input reads | PASS | Implementation artifact confirms exclusion |

## Normalization Helper Correctness

### `_BENCHMARK_NEWLINE_RUN_PATTERN` (line 75)

Pattern: `r"[ \t\f\v]*(?:\r\n|\r|\n)+[ \t\f\v]*"`

- Correctly matches `\r\n`, `\r`, `\n` sequences with optional surrounding horizontal whitespace
- Does not consume non-adjacent spaces, preserving ordinary spacing
- Uses non-capturing group for alternation — correct

### `_previous_non_space_char` / `_next_non_space_char` (lines 266–303)

- Correct boundary-aware character lookup
- Returns `None` at string boundaries — handled by `_is_ascii_word_char`

### `_benchmark_newline_replacement` (lines 322–340)

- Context-aware: replaces with space only when both flanking non-space chars are ASCII word chars
- Otherwise deletes — correct for CJK-punctuation boundaries
- Handles `017644` case (`利\n率` → `利率`) and `019918` case (`（税后）\n*5%` → `（税后）*5%`) correctly

### `_normalize_benchmark_text` (lines 343–363)

- Iterative match-and-replace with `finditer` — correct, no overlapping-match issues
- `.strip()` at end — safe for benchmark text which should not have leading/trailing whitespace
- Preserves non-newline spaces and punctuation variants — verified by unaffected cases

### `_normalize_benchmark_matched_field` (lines 366–396)

- Creates new `_MatchedField` object — does not mutate frozen original — correct
- Short-circuits when no normalization needed (line 380–381) — efficient
- `matched_line` normalization: first tries `replace(value, normalized_value, 1)` for surgical update; falls back to full `_normalize_benchmark_text(matched_line)` — correct fallback strategy
- Both `value` and `matched_line` (used for anchor note) consume the same normalized text — satisfies controller constraint F-2

### Integration Point (line 577)

`matched_field = _normalize_benchmark_matched_field(matched_field)` placed after `_extract_field` and before `ExtractedField` construction — correct boundary placement per plan.

## Test Coverage

| Requirement | Status |
|---|---|
| `017644` newline shape normalized | PASS — parametrized case |
| `019918` newline shape normalized | PASS — parametrized case |
| `004194` unaffected (byte-for-byte) | PASS — parametrized case |
| `005313` unaffected (byte-for-byte) | PASS — parametrized case |
| `019923` unaffected (byte-for-byte) | PASS — parametrized case |
| Anchor note synchronized with benchmark_text | PASS — `benchmark_anchor.note == f"业绩比较基准：{expected_benchmark_text}"` |
| `benchmark_identity_status=composite` | PASS — asserted for all 5 cases |
| `benchmark_index_name=None` | PASS — asserted for all 5 cases |
| `benchmark_component_text` consumes normalized text | PASS — compared against `_benchmark_components(expected_benchmark_text)` |
| `methodology_availability=benchmark_only` | PASS — asserted |
| `constituents_availability=benchmark_only` | PASS — asserted |
| `source_tier=benchmark_context` | PASS — asserted |
| Anchor metadata preserved | PASS — `section_id`, `page_number`, `table_id`, `row_locator` asserted |

## Validation Results

| Command | Result |
|---|---|
| `pytest tests/fund/extractors/test_profile.py -q` | 22 passed in 0.61s |
| `pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | 32 passed in 0.39s |
| `ruff check fund_agent tests` | All checks passed |
| `git diff --check HEAD` | No output (passed) |

## README Update Assessment

`fund_agent/fund/README.md` and `tests/README.md` were not modified. Assessment: correct. The normalization is an internal extractor behavior detail; the public Fund package contract, test organization, and running instructions are unchanged. No AGENTS.md doc sync rule is violated.

## Adversarial Failure Pass

| Attack vector | Result |
|---|---|
| Does normalization leak into non-benchmark fields? | No — helper called only in `_build_benchmark()` |
| Could `_normalize_benchmark_text` strip meaningful leading/trailing content? | `.strip()` only removes whitespace, not punctuation or CJK — safe for benchmark text |
| Could `matched_line.replace()` produce incorrect fallback? | Fallback to full `_normalize_benchmark_text(matched_line)` handles edge cases — correct |
| Could newlines in non-benchmark parsed text be affected? | No — `_first_non_empty_after()` and general table parsing untouched |
| Could the normalization alter punctuation variants (`×`/`*`, `＋`/`+`, `（）`/`()`)? | No — replacement only targets newline runs and flanking horizontal whitespace |

## Observation (Non-Finding)

`_normalize_benchmark_text` docstring references "见模板第 1 章产品本质" — an internal methodology reference. This is stylistic, not a correctness issue. No action required.

## Residuals

| Residual | Owner | Handling |
|---|---|---|
| Full tuple/null golden semantics for `benchmark_component_text` | Future golden schema phase | Out of P16-S2.1 scope |
| Broader PDF table text normalization policy | Future parser design if needed | P16-S2.1 authorizes only benchmark path |
| Docstring methodology reference style | Cosmetic | No action required |

## Required Disposition

None. Implementation is accepted as-is. P16-S2 golden implementation may resume.
