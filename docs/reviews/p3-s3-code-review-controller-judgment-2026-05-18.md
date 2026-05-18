# P3-S3 Code Review - Controller Judgment

## Verdict

PASS.

No blocking correctness, stability, or maintainability issues found in the P3-S3 diff.

## Findings

### INFO-1 - Interactive reviewers did not complete artifacts in time

AgentGLM and AgentMiMo were both asked to perform independent P3-S3 code review. Both entered review work, but GLM repeatedly paused on command confirmations and MiMo remained in a long thinking/compaction state without writing `docs/reviews/p3-s3-code-review-*.md` during this gate window.

This is recorded as process risk only. It does not change the code verdict because the controller review and local validation completed successfully.

### INFO-2 - Text-line QDII detection is still weaker than table-path detection

`fund_agent/fund/fund_type.py` prioritizes `基金简称` over `基金名称` for table-based type classification, which covers the real P3-S3 root cause. If a future parser emits only colon-style text lines and includes both `基金名称：...` and `基金简称：...QDII...`, the current text-line extractor returns the first matching field and may miss the short-name QDII marker.

This is not blocking for P3-S3 because the real sample evidence and new tests target the `ParsedTable` path, and QDII also triggers from investment scope containing `境外` in the CLI matrix. It should be tightened in a later classifier cleanup.

## Review Notes

- Parsed report cache quality gate rejects low-quality cached payloads before returning them to `FundDocumentRepository`.
- `tests/fund/documents/test_cache.py` now includes an explicit unusable parsed report payload test.
- Repository cache tests were updated so cacheable fixture reports satisfy the new quality gate.
- `profile.py` now reads key-value pairs from both table headers and rows, preserving table/page metadata in `EvidenceAnchor`.
- `fund_type.py` now reads table-based classification fields, detects QDII from table short name or scope, and classifies bond fund names before checking mixed index benchmark text.
- `renderer.py` now consumes `benchmark_text`, matching the current `extract_profile()` contract.
- `tests/fund/integration/test_p3_cli_e2e_matrix.py` exercises Typer CLI, Service, `FundDataExtractor`, template rendering, and programmatic audit for `110011`, `510300`, and `000171`.

## Validation

Executed:

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/extractors/test_profile.py tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui -q
git diff --check
```

Results:

```text
33 passed
115 passed
git diff --check passed
```

## Residual Risk

P3-S3 matrix uses fake repository and fake NAV provider to isolate network/PDF nondeterminism, but it still runs the real CLI/Service/Capability/template/audit path. Real PDF parser quality remains a separate integration risk.
