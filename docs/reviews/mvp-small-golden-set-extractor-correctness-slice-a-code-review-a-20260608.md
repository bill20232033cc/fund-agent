# Small Golden Set / Extractor Correctness Slice A Code Review A

## Initial Verdict

`BLOCKED`.

## Findings

- `[blocking] [A-SCHEMA-001]` `tests/fund/test_small_golden_set_manifest.py:156` - Schema guard did not close allowed key sets. Tests checked required values and a few forbidden correctness keys, but did not assert exact top-level, row and `source_document_identity` key sets, and did not forbid source excerpt/raw text fields. Minimal fix: add allowed key-set assertions and recursively forbid `source_excerpt`, `source_text`, `raw_text`, `excerpt` and equivalent fields.
- `[blocking] [A-DOCSTRING-001]` `tests/fund/test_small_golden_set_manifest.py:156` - Test functions used one-line docstrings instead of full Chinese docstrings with parameters, returns and exceptions, while `AGENTS.md` requires complete function docstrings. Minimal fix: complete docstrings or record an accepted test-docstring exception.

## Targeted Re-review

Verdict: `PASS`.

Findings:

- `A-SCHEMA-001`: `FIXED`.
- `A-DOCSTRING-001`: `FIXED`.

Open questions: none.
