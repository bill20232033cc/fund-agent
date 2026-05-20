# P6-S3 Implementation - 2026-05-20

## Verdict

P6-S3 implementation completed. The first deterministic programmatic `CHAPTER_CONTRACT` audit is now implemented in the Capability layer without LLM audit, PDF evidence re-search, ITEM_RULE, quality gate/FQ5 behavior changes, or Service/Engine/UI/CLI behavior changes.

## Step A Result

Scope:

- Added `fund_agent/fund/template/chapter_blocks.py`.
- Moved `RenderedChapterBlock`, `get_template_chapter_heading(...)`, `split_rendered_chapter_blocks(...)`, and private splitter helpers out of `renderer.py`.
- Updated `renderer.py` and `fund_agent/fund/template/__init__.py` imports.

Verification before Step B:

```bash
.venv/bin/python -m pytest tests/fund/template/test_renderer.py -q
```

Result:

- `22 passed in 0.38s`

No intentional renderer output behavior change was made in Step A.

## Step B Result

Implemented:

- Added deterministic audit rule definitions in `fund_agent/fund/audit/contract_rules.py`.
- Added explicit `ProgrammaticAuditInput.chapter_blocks`.
- Extended checked rules to `("P1", "P2", "P3", "C2", "L1", "R1", "R2")`.
- Added split fallback from `report_markdown` when explicit `chapter_blocks` are absent.
- Added P3 per-chapter minimum evidence line checks.
- Added deterministic C2 checks for:
  - chapter block metadata consistency
  - required_output_items marker presence
  - must_not_cover forbidden marker absence
- Updated renderer to pass `chapter_blocks` into audit input.
- Added only the accepted renderer-label-needed markers and explicit `数据不足` placeholders.
- Updated `docs/design.md`, `fund_agent/fund/README.md`, and `tests/README.md`.

## Files Changed

Source:

- `fund_agent/fund/template/chapter_blocks.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/template/__init__.py`
- `fund_agent/fund/audit/contract_rules.py`
- `fund_agent/fund/audit/audit_programmatic.py`

Tests:

- `tests/fund/audit/test_audit_programmatic.py`
- `tests/fund/template/test_renderer.py`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`

Docs:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Artifact:

- `docs/reviews/p6-s3-implementation-20260520.md`

## Verification

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
```

Result: `44 passed in 0.43s`

```bash
.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
```

Result: `23 passed in 0.52s`

```bash
.venv/bin/python -m pytest tests/ -q
```

Result: `227 passed in 0.63s`

```bash
.venv/bin/python -m ruff check .
```

Result: `All checks passed!`

```bash
git diff --check
```

Result: passed with no output.

## Scope Notes

- `audit_programmatic.py` does not import `renderer.py`; it imports shared chapter block helpers from `template/chapter_blocks.py`.
- No fund document filesystem, PDF, cache, or repository access was added.
- No `extra_payload` parameters were introduced.
- C2 remains deterministic marker/metadata conformance only; it does not perform semantic chapter-overreach scoring.
- P3 per-chapter evidence checks only verify evidence line format presence; evidence-to-claim support remains E1/E2/E3 future scope.

## Residual Risks

- Required item markers prove labels/placeholders exist, not answer quality.
- Forbidden marker checks are intentionally small and literal; semantic forbidden-topic checks remain v2.
- Renderer output now includes additional deterministic labels for auditability, which reviewers should verify are limited to the accepted marker matrix.
