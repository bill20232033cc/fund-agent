# EID Source Metadata Design Wording Docs-Sync Plan Controller Judgment - 2026-06-11

## Judgment

ACCEPT.

The plan is accepted for a later docs-only implementation gate.

## Basis

- `AGENTS.md`: `docs/design.md` is the design truth and must distinguish current implemented fact from future/candidate wording.
- `docs/current-startup-packet.md`: next entry is `EID source metadata design wording docs-sync planning gate`, no-live/docs-only.
- `docs/implementation-control.md`: current accepted Stage B evidence is bounded as `accepted_live_window_no_failure_observed`; `ac6bbe9` remains accepted no-live failure-category proof.
- Plan artifact: `docs/reviews/mvp-eid-source-metadata-design-wording-docs-sync-plan-20260611.md`.
- DS plan review: `docs/reviews/mvp-eid-source-metadata-design-wording-docs-sync-plan-review-ds-20260611.md`, verdict `PASS`, blocking findings `0`.
- MiMo plan review: `docs/reviews/mvp-eid-source-metadata-design-wording-docs-sync-plan-review-mimo-20260611.md`, verdict `PASS`, blocking findings `0`.

## Accepted Current Facts

- `AnnualReportSourceMetadata` in `fund_agent/fund/documents/models.py` has no `identity_status` or `integrity_status` fields.
- `identity_mismatch` and `integrity_error` are annual-report source failure categories / validation outcomes, not annual-report source metadata status fields.
- NAV `identity_status` belongs to the separate NAV repository domain and must not be moved into annual-report source metadata wording.
- Current annual-report source policy remains EID single-source:
  - `selected_source=eid`
  - `source_mode=single_source_only`
  - `fallback_enabled=false`
- Eastmoney, CNINFO and fund-company routes remain deferred source candidates / historical evidence routes, not current production fallback.
- Stage B live retry checkpoint `f0a1459` is accepted only as `accepted_live_window_no_failure_observed` for one successful `006597 / 2024` live window.
- Checkpoint `ac6bbe9` remains accepted no-live code-behavior proof for modeled EID failure categories.

## Accepted Implementation Scope

Allowed implementation file:

```text
docs/design.md
```

Allowed implementation target:

- Patch only the `缓存策略 -> 来源元数据` bullet around the annual-report `AnnualReportSourceMetadata` wording.

Accepted wording intent:

- Replace the stale claim that annual-report `AnnualReportSourceMetadata` supports `identity status` and `integrity status`.
- Describe current annual-report metadata as a provenance/policy container with current fields such as `selected_source`, `source_mode`, `fallback_enabled`, `fallback_used`, EID URL/identifier fields, `primary_failure_category`, and `discovery_contract_version`.
- State that `identity_mismatch` / `integrity_error` are source failure categories / validation outcomes, not `AnnualReportSourceMetadata` status fields.
- Preserve the hidden-fallback prohibition.

## Prohibited Scope

The later implementation gate must not:

- modify source code
- modify tests
- modify runtime behavior
- modify `docs/implementation-control.md`
- modify `docs/current-startup-packet.md`
- add `identity_status` or `integrity_status` to `AnnualReportSourceMetadata`
- run tests
- run live EID/network/PDF/FDR/`FundDocumentRepository`/helper command
- run fallback, non-EID source, provider/LLM, extractor, `analyze`, `checklist`, golden/readiness, score-loop, release, push, PR or merge
- imply Stage B proved all live failure branches
- imply Eastmoney/CNINFO/fund-company fallback is current production behavior

## Finding Disposition

| Finding | Source | Disposition | Controller rationale |
|---|---|---|---|
| No material findings. | DS review | ACCEPT | DS confirmed stale wording, model facts, NAV separation, bounded Stage B evidence, no-fallback policy and no-live validation scope. |
| No material findings. | MiMo review | ACCEPT | MiMo confirmed exact patch scope, field set, failure-category distinction and no-live/docs-only implementation boundary. |

## Required Validation For Later Implementation

Allowed commands only:

```bash
rg -n "identity status|integrity status|identity_status|integrity_status|AnnualReportSourceMetadata|来源元数据|accepted_live_window_no_failure_observed|ac6bbe9|Eastmoney|CNINFO|基金公司|fund-company" docs/design.md
sed -n '650,682p' docs/design.md
git diff --check -- docs/design.md
```

The `rg` command may still find `identity_status` in the NAV section of `docs/design.md`; that is expected and must not be treated as annual-report metadata drift.

## Next Entry

Recommended next entry:

```text
EID source metadata design wording docs-sync implementation gate
```

This next gate is no-live/docs-only and may patch only `docs/design.md` plus required implementation/review/judgment artifacts.
