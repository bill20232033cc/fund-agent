# Release Maintenance 004393 Quality Gate S1 Code Review - GLM - 2026-05-24

## Scope

- Review role: S1 code review specialist B
- Reviewed diff: current workspace S1 implementation diff
- Review target files:
  - `fund_agent/fund/extractors/profile.py`
  - `tests/fund/extractors/test_profile.py`
  - `tests/fund/test_extraction_snapshot.py`
  - `docs/reviews/release-maintenance-004393-quality-gate-s1-implementation-20260524.md`
- Required conclusion: `PASS` / `PASS_WITH_FINDINGS` / `FAIL`

## Conclusion

`FAIL`

S1 stays inside the accepted file scope and the `basic_identity` comparable-value path is materially correct, but the `fee_schedule` table fallback is too broad and `_section_id_for_table()` can emit a section anchor that is unrelated to the matched table. These are S1 correctness and evidence-traceability defects, not style issues.

## Required Checks

| Check | Result | Evidence |
|---|---|---|
| S1 allowed files/scope | PASS | Workspace source/test changes are limited to `profile.py`, `tests/fund/extractors/test_profile.py`, and `tests/fund/test_extraction_snapshot.py`; the implementation artifact is review evidence. No golden, source CSV, README, Host, or Agent package changes were observed. |
| `management_company` / `custodian` / `inception_date` enter `basic_identity` comparable values | PASS | `profile.py` adds field/table labels and populates the keys in `_build_basic_identity()`; `extraction_snapshot.py` already whitelists those subfields; `tests/fund/test_extraction_snapshot.py` now asserts all three comparable values. |
| Missing optional identity labels do not make identity missing | PASS | `_build_basic_identity()` always returns a direct dict containing existing identity/classification fields even when the new optional matched fields are `None`. Existing fixture coverage also keeps `custodian` and `inception_date` absent while `basic_identity.value` remains present. |
| `fee_schedule` fallback robustness | FAIL | Table fallback scans all parser tables by broad labels and is not scoped to `7.4.10.2` or to the target subsection; see Finding F1. |
| `_section_id_for_table` reasonableness | FAIL | It returns the first non-empty section from `§7`, `§5`, `§2` rather than deriving the section from the matched table; see Finding F2. |
| Tests cover failure path and direct/fallback precedence | PARTIAL | Tests cover no-fee missing path, direct-over-fallback precedence, and partial direct/fallback combination. They do not cover false-positive fee table rows, cross-subsection label collisions, or table anchor section correctness. |
| Ruff/pytest commands sufficient | PASS | The accepted S1 required commands were run and passed; command scope matches the plan. |

## Findings

### F1 - `fee_schedule` table fallback can extract unrelated fee rates as management/custody fees

- Severity: High
- Location: `fund_agent/fund/extractors/profile.py:274-305`, `fund_agent/fund/extractors/profile.py:336-352`

The table fallback iterates every table in `report.tables` and accepts a row if it contains either the exact subsection number or any broad semantic label:

- `management_fee`: `基金管理费`, `管理费`
- `custody_fee`: `基金托管费`, `托管费`

There is no check that the table belongs to `7.4.10.2`, no table-local subsection context, and no guard that `custody_fee` is found under `7.4.10.2.2` rather than another subsection. Once a broad label matches, `_extract_scalar_fee_rate()` returns the first percentage in that row.

What can go wrong:

- A table row for another fund or another fee schedule containing `管理费` and a percentage can become this fund's `management_fee`.
- A row with a custody-related phrase inside or near a management-fee table can satisfy the custody rule because `托管费` alone is enough.
- The implementation avoids pure RMB occurrence amounts because it only extracts `%`, but it still accepts unrelated percentage disclosures such as other funds' fee rates or non-target management/custody percentage rows.

Why this is in the same data path:

`_build_fee_schedule()` calls `_extract_fee_from_fallback_subsection()` only when the direct `§2` side is missing. If text fallback does not find a subsection heading, `_extract_fee_from_fallback_tables()` scans all tables and can return a `_MatchedField` that becomes the public `fee_schedule.value` and evidence anchor.

Tests currently prove the happy table fallback and the no-fee text failure path, but they do not include adversarial rows such as:

- a table outside `7.4.10.2` with `其他基金管理费率 0.60%`;
- a `7.4.10.2.1 基金管理费` table row that mentions `托管费` but discloses only the management fee;
- a valid `7.4.10.2` heading in raw text plus an unrelated later table with a broader `管理费`/`托管费` percentage.

Suggested fix:

Constrain table fallback to direct subsection evidence. A safe shape is to require either the target subsection number in the row/table context or a preceding/parser-visible table context that establishes the target `7.4.10.2.x` subsection, then extract only from rows in that bounded context. Broad labels should not be sufficient by themselves.

### F2 - `_section_id_for_table()` can fabricate the wrong evidence section for fallback table anchors

- Severity: Medium
- Location: `fund_agent/fund/extractors/profile.py:396-413`, `fund_agent/fund/extractors/profile.py:298-304`

`_section_id_for_table()` ignores the matched table's page, index, row text, and surrounding raw-text offset. It simply returns the first non-empty section among `§7`, `§5`, and `§2`.

What can go wrong:

- If a report has any non-empty parser `§7`, a fallback fee table parsed under `§5` will be anchored to `§7`.
- If a report has no `§7` but has `§5`, a table that actually came from another parser section can still be anchored to `§5`.
- This gives downstream traceability and evidence-confirm logic a section id that can point to content unrelated to the value.

Why this is in the same data path:

When `_extract_fee_from_fallback_tables()` returns a match, it writes `section_id=_section_id_for_table(report, table)`. `_build_anchor()` then exposes that section id as the evidence anchor for `fee_schedule`. The table-id/page can be correct while the section id is wrong.

Tests do not catch this because `test_extract_profile_fee_schedule_fallback_reads_74102_table_semantics()` asserts only `table_id` and `page_number`, not `section_id`, and the fixture has only `§5` as the extra non-empty section.

Suggested fix:

Derive the table section from parser metadata if available, or from an explicit bounded subsection/table context established during fallback matching. If that is not available, use a conservative semantic anchor such as `§7.4.10.2` rather than choosing an unrelated existing parser section.

## Non-Finding Notes

- `basic_identity` implementation is aligned with S1: labels were added, `_build_basic_identity()` includes the three new keys, and snapshot comparable extraction already had the whitelist.
- Direct/fallback precedence for `fee_schedule` is correct for the direct values covered by the tests: existing `§2` values are not overwritten, and partial direct plus fallback is supported.
- The implementation does not modify golden rows, source CSVs, README files, Host/Agent packages, or quality-gate denominator behavior.

## Validation Commands

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
```

Result: exit code `0`; `63 passed`.

```bash
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
```

Result: exit code `0`; `All checks passed!`.

```bash
git diff --check
```

Result: exit code `0`; no output.

## Final Judgment

`FAIL`

Do not accept S1 as-is. Fix the table fallback bounding and table anchor derivation, then add adversarial tests for false-positive table rates, cross-subsection custody/management collisions, and section-id correctness.
