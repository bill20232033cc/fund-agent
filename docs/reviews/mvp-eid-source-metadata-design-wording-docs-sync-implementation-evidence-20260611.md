# EID Source Metadata Design Wording Docs-Sync Implementation Evidence - 2026-06-11

## Scope

Docs-only implementation for accepted planning checkpoint `daf5de7`.

Changed file:

- `docs/design.md`

No source code, tests, runtime behavior, control docs or startup packet were changed in this implementation step.

## Implemented Change

Patched the `缓存策略 -> 来源元数据` bullet in `docs/design.md`.

The stale wording claimed annual-report `AnnualReportSourceMetadata` supports `identity status` and `integrity status`.

The updated wording now states:

- `AnnualReportSourceMetadata` is an annual-report source provenance container.
- Current annual-report source metadata fields include `selected_source`, `source_mode`, `fallback_enabled`, `fallback_used`, EID URL/identifier fields, `primary_failure_category`, and `discovery_contract_version`.
- `identity_mismatch` / `integrity_error` are source failure categories and validation outcomes, not `AnnualReportSourceMetadata` status fields.
- Hidden fallback metadata must not be used to disguise an EID source.

## Boundary Confirmation

This implementation did not:

- modify `fund_agent/`
- modify `tests/`
- modify `docs/implementation-control.md`
- modify `docs/current-startup-packet.md`
- add `identity_status` or `integrity_status` to `AnnualReportSourceMetadata`
- run tests
- run live EID / network / PDF / FDR / `FundDocumentRepository` / helper command
- run fallback, non-EID source, provider/LLM, extractor, `analyze`, `checklist`, golden/readiness, score-loop, release, push, PR or merge
- imply Stage B proved all live failure branches
- reintroduce Eastmoney, CNINFO or fund-company fallback as current production behavior

## Validation

Commands run:

```bash
rg -n "identity status|integrity status|identity_status|integrity_status|AnnualReportSourceMetadata|来源元数据|accepted_live_window_no_failure_observed|ac6bbe9|Eastmoney|CNINFO|基金公司|fund-company" docs/design.md
sed -n '650,682p' docs/design.md
git diff --check -- docs/design.md docs/reviews/mvp-eid-source-metadata-design-wording-docs-sync-implementation-evidence-20260611.md
```

Expected interpretation:

- `identity_status` may still appear in the NAV section of `docs/design.md`; that is separate NAV repository domain wording and is not annual-report source metadata drift.
- Annual-report source metadata wording no longer claims `identity status` / `integrity status` fields.

## Residuals

- None for the targeted annual-report source metadata wording patch.
- Broader cleanup of historical ledger wording, if desired, should remain a separate no-live docs/control hygiene gate.
