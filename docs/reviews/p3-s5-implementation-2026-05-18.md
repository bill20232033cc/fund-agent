# P3-S5 Implementation - Evidence Anchor Integration

## Verdict

Implemented.

P3-S5 now verifies that each deterministic CLI end-to-end sample report carries chapter-level body evidence lines and appendix-level source anchors for the key annual-report data used by the 8-chapter report.

## Scope

- Strengthened `tests/fund/integration/test_p3_cli_e2e_matrix.py`.
- Added test-only helpers:
  - `_body_evidence_lines(...)`
  - `_appendix_evidence_lines(...)`
  - `_assert_complete_evidence_contract(...)`
- The P3 CLI matrix now asserts for every sample report:
  - exactly 8 body evidence lines, matching template chapters 0-7
  - every body evidence line references `年报2024§`
  - no body evidence line says the current chapter lacks anchors
  - appendix evidence lines contain no `- [M...]` missing-anchor placeholders
  - appendix evidence covers key annual-report source anchors for `§2`, `§3`, `§4`, `§8`, `§9`, and `§10`

## Validation

Executed:

```bash
.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
```

Result:

```text
1 passed
```

## Boundary Check

- No production code was changed.
- UI still only performs CLI parsing and output.
- Service still orchestrates the real analysis path.
- Evidence extraction and rendering remain in Capability / template code.
- The test continues to use the unified document repository interface via a fake repository; it does not read fund documents directly from the filesystem.

## Residual Risk

The P3 matrix uses deterministic fake reports to avoid network and PDF side effects. This is appropriate for the evidence contract gate, but it does not replace a later real PDF/network smoke run.
