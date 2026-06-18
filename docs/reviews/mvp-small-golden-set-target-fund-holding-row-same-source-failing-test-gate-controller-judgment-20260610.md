# MVP Small Golden Set Target Fund Holding Row Same-Source Failing Test Gate Controller Judgment - 2026-06-10

## Judgment

Accepted for implementation.

## Basis

- Current control truth names `target_fund_holding_row.v1` same-source failing-test gate as the next valid entry.
- The plan is code-generation-ready and test-only.
- Plan review reports no blocking findings.

## Approved Scope

- Replace the remaining generic target-fund xfail with a named strict xfail.
- Use only the accepted retained excerpt oracle for `110020 / 2024 / target_etf_holding`.
- Update `tests/README.md` if needed.
- Produce implementation evidence and code review before accepted implementation commit.

## Preserved Boundaries

- No production extractor changes.
- No source/fallback/PDF/FDR/network/live LLM/provider/runtime/config behavior.
- No fixture projection, golden/readiness promotion or downstream integration.
