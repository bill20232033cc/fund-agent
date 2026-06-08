# Code Review

## Scope

- Mode: role-scoped independent implementation/evidence review
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: `main`
- Output file: `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-code-review-mimo-20260608.md`
- Included scope:
  - `tests/fund/test_small_golden_set_parser_mechanics.py`
  - `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-implementation-evidence-20260608.md`
- Excluded scope: production code, extractors, fixtures (read-only), providers, config, control docs, startup packet
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Review Detail

### 1. Scope Boundary: Parser/Fixture Mechanics Only

Option 2 stays strictly within parser/fixture mechanics. The test file does not import or exercise any extractor, provider, source, repository, PDF, fallback or network module. It reads only:

- `docs/reviews/mvp-small-golden-set-manifest-20260608.json` (Slice A manifest, read-only)
- `tests/fixtures/fund/small_golden_set/<fund_code>_2024/expected_fields.json` (Slice B fixtures, read-only)

No source truth, annual-report correctness, matched identity, exact/numeric correctness or extractor changes are claimed or attempted. Evidence document `mvp-small-golden-set-extractor-correctness-slice-c-option2-implementation-evidence-20260608.md` explicitly states this boundary and lists residuals correctly.

### 2. Import Boundary

`test_parser_mechanics_test_file_uses_only_standard_library_imports` (line 396–416) statically inspects the test file's own source text and asserts that all import roots are in `{"__future__", "dataclasses", "json", "pathlib", "typing"}`. Verified: no production, repository, provider, source, fallback or network module is imported. The set `ALLOWED_IMPORT_ROOTS` matches the actual imports exactly.

### 3. Five-Row Fixture Boundary

`test_parser_mechanics_reads_only_exact_five_local_fixture_rows` (line 275–296) asserts:

- Manifest row set equals `{"004393", "110020", "004194", "006597", "017641"}`
- Fixture row set equals the same
- Fixture directory set equals `{f"{fc}_2024" for fc in ...}`
- Each row has `report_year=2024`

This is fail-closed: any extra or missing row/directory breaks the test.

### 4. Fail-Closed Metadata

`test_parser_mechanics_preserves_fixture_fail_closed_metadata` (line 299–320) asserts every row preserves:

- `promotion_allowed=false`
- `fallback_invocation=prohibited`
- `fixture_source_kind=synthetic`
- `source_identity.status=unmatched_synthetic`
- `source_identity.matched_source_document=false`
- `source_identity.fallback_used=false`
- `exact_numeric_correctness_allowed=false`

No escape hatch exists.

### 5. Manifest Status Preservation

`test_parser_mechanics_preserves_manifest_field_statuses` (line 323–346) cross-checks every field group's `manifest_status` against the Slice A manifest and verifies `fixture_status == manifest_status`. It also explicitly checks `017641 holdings=unavailable` and `risk=deferred_policy`.

### 6. No Exact/Numeric Assertion Kinds

`test_parser_mechanics_never_uses_exact_or_numeric_assertion_kinds` (line 349–364) asserts every field group's `assertion_kind` is `availability_status` and is not in `{"exact", "normalized_text", "numeric_percent"}`.

### 7. Explicit Degradation (No Silent Success)

`test_parser_mechanics_degrades_unsupported_fields_explicitly` (line 367–393) validates the `_derive_parser_status` helper output:

- Every `parser_status` is in `{"unavailable", "not_applicable", "deferred_policy"}`
- No `parser_status` is in `{"expected", "success", "matched"}`
- Every `reason` is non-empty
- `deferred_policy` fixture → `deferred_policy` parser status with `fixture_status_deferred_policy` reason
- `unavailable` fixture → `unavailable` parser status with `fixture_status_unavailable` reason
- `expected` fixture (all unmatched synthetic) → `unavailable` parser status with `unsupported_unmatched_synthetic_fixture` reason

The `_derive_parser_status` helper (line 225–248) is clean: it dispatches on fixture status first, then source identity status, then exact/numeric flag, with a final fallback. No branch silently returns a success status.

### 8. Helper Avoids Silent Success and Production Imports

The helper (`_derive_parser_status`, `_parse_field_mechanics`, `_parse_all_field_mechanics`) uses only standard library modules and produces only `unavailable`/`not_applicable`/`deferred_policy` outputs. No production, repository, provider or source module is imported.

### 9. Validation Commands

Evidence document reports three validation commands:

1. `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py -q` — 21 passed in 0.04s
2. `uv run ruff check tests/fund/test_small_golden_set_parser_mechanics.py` — All checks passed
3. `git diff --check -- tests/fund/test_small_golden_set_parser_mechanics.py docs/reviews/...` — no output

All local deterministic only. No live/network/provider/repository commands.

### 10. Changed File Scope

Only two files changed:

- `tests/fund/test_small_golden_set_parser_mechanics.py` (new test)
- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-implementation-evidence-20260608.md` (new evidence)

No production code, extractor, fixture JSON, provider/runtime/config, reports/golden, control doc, design doc, startup packet, README or quality gate file was changed. Scope is within the reconciliation plan's Option 2 allowed files.

## Open Questions

无。

## Residual Risk

- `EXPECTED_STATUS_BY_FUND` is duplicated between `test_small_golden_set_parser_mechanics.py` and `test_small_golden_set_fixture_shape.py` / `test_small_golden_set_manifest.py`. If the manifest is updated, all three copies must be kept in sync. This is a maintainability observation, not a correctness defect for the current mini-slice.
- `_derive_parser_status` line 246–248 has two unreachable branches when all current fixtures are unmatched synthetic with `exact_numeric_correctness_allowed=false`. The `unsupported_exact_numeric_correctness_disabled` and `unsupported_option2_no_correctness_claim` paths exist as defensive forward-compatibility. This is acceptable for a mechanics-only slice; if fixtures ever become matched, these branches provide correct fallback behavior.

## Verdict

PASS
