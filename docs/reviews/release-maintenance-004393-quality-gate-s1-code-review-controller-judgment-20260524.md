# Release Maintenance 004393 Quality Gate S1 Code Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance 004393 S1 code review`
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S1 - P0 Extraction And Comparable Fields`
- Implementation artifact: `docs/reviews/release-maintenance-004393-quality-gate-s1-implementation-20260524.md`
- Code reviews:
  - `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-mimo-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-glm-20260524.md`
- Controller conclusion: `fix required`

## Review Summary

| Reviewer | Conclusion | Controller disposition |
|---|---|---|
| MiMo | `PASS_WITH_FINDINGS` | Accept table-fallback bounding finding |
| GLM | `FAIL` | Accept table-fallback and anchor findings |

Both reviewers agree that `basic_identity` changes are aligned with S1, and both identify the same material issue in `fee_schedule` table fallback. GLM additionally identifies an evidence-anchor section derivation issue in the same table fallback path.

## Accepted Findings

| ID | Source | Finding | Controller decision | Required fix |
|---|---|---|---|---|
| `004393-S1-C1` | MiMo Medium finding, GLM F1 | `fee_schedule` table fallback scans all parser tables and accepts broad `管理费` / `托管费` labels plus any percentage, without requiring `7.4.10.2.1` / `7.4.10.2.2` subsection context. | Accepted. This can create false P0 fee coverage from unrelated fee-rate rows and violates the accepted S1 requirement to search by `7.4.10.2` subsection/table semantics. | Bound table fallback to direct target-subsection evidence. Broad labels alone are not sufficient. Add adversarial tests proving unrelated earlier fee-rate rows and cross-subsection label collisions do not win over the target `7.4.10.2.x` disclosure. |
| `004393-S1-C2` | GLM F2 | `_section_id_for_table()` returns the first non-empty section among `§7`, `§5`, and `§2`, not the section or semantic context of the matched table. | Accepted. Evidence anchors must not fabricate an unrelated section id. | Derive section id from a bounded subsection/table context when possible. If the parser cannot tie a table to a section, use conservative semantic anchor `§7.4.10.2` or target subsection context instead of guessing from unrelated existing sections. Add tests for section-id correctness. |

## Rejected / Non-Blocking Notes

- `basic_identity.management_company`, `custodian`, and `inception_date` extraction is accepted as directionally correct pending re-review after the fee fallback fix.
- Direct `§2` fee precedence, partial direct+fallback combination, and no-fee missing behavior are accepted as covered by current focused tests.
- S1 did not change golden rows, source CSVs, README, Host/Agent packages, or turnover denominator behavior; this stays within current scope.

## Required Fix Scope

The fix agent may edit only:

- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-fix-20260524.md`

It may touch `tests/fund/test_extraction_snapshot.py` only if existing assertions require mechanical updates, but no such update is expected.

The fix must not edit golden files, README, source CSV, `docs/implementation-control.md`, `fund_agent/host`, `fund_agent/agent`, config, runtime outputs, or unrelated source/tests.

## Required Validation

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
git diff --check
```

## Next Action

Dispatch an S1 fix worker. After the fix, run targeted re-review from two independent reviewers before accepting the slice.
