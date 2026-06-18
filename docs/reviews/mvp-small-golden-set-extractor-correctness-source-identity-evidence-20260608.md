# MVP Small Golden Set / Extractor Correctness Source Identity Evidence

## Scope

Gate: `small golden set extractor correctness implementation gate` Slice C Option 1 source identity acquisition mini-slice.

This artifact records row-level source identity evidence only. It does not change golden/readiness/quality gate promotion semantics, does not implement extractor correctness, does not modify extractors, and does not authorize exact/numeric correctness assertions.

Accepted provenance rule for this mini-slice:

- Valid: accepted review artifacts, control-truth referenced artifacts, committed fixture/manifest metadata, or newly documented evidence whose provenance origin is itself pre-existing and safe.
- Invalid: arbitrary untracked workspace residue, synthetic fixture text, generated reports or LLM output without source-document provenance, live repository/PDF/network/fallback/provider activity, or inference from fund code/year alone.

## Candidate Provenance Reviewed

Control and current-gate artifacts:

- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/design.md`
- `docs/reviews/mvp-small-golden-set-manifest-20260608.json`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-a-implementation-evidence-20260608.md`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-fixture-retention-evidence-20260608.md`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-b-controller-judgment-20260608.md`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-reconciliation-plan-20260608.md`
- `tests/fixtures/fund/small_golden_set/*/expected_fields.json`

Additional accepted historical candidates inspected:

- `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md`
- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md`

## Row Decisions

| fund_code | report_year | current fixture_source_kind | current source_identity_status | candidate accepted provenance paths | direct proof observed | decision | residual reason |
|---|---:|---|---|---|---|---|---|
| `004393` | 2024 | `synthetic` | `unmatched_synthetic` | Slice A/B artifacts; `release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md` | The 004393 S0 judgment accepts parser-visible same-source facts, but explicitly records `metadata.source=null`, `fallback_used` unavailable, `parsed_cache_hit=true`, and says S0 cannot prove source identity, refreshed-source provenance, or `fallback_used=false`. No source document title/id or safe source identifier is accepted for this row. | unmatched | `source_identity_provenance_insufficient`; accepted artifact explicitly forbids using the evidence to claim source/fallback correctness. |
| `110020` | 2024 | `synthetic` | `unmatched_synthetic` | Slice A/B artifacts; `release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` | The 110020 judgment records coverage-candidate input with `source_strategy=primary_then_fallback`, `resolved_source_name=eastmoney`, `fallback_used=true`, and `source_provenance_status=complete`. It does not provide source document title/id or source-safe document identifier for a matched annual report fixture, and it remains not promoted. | unmatched | `source_identity_provenance_insufficient`; historical fallback-used provenance is not a current no-fallback matched fixture identity and lacks required document identity fields. |
| `004194` | 2024 | `synthetic` | `unmatched_synthetic` | Slice A/B artifacts; `release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md`; `release-maintenance-004194-p0-coverage-index-profile-decision-controller-judgment-20260529.md` | The 004194 decision accepts five narrow `index_profile.*` matched score rows with anchor `年报2024 §2 page-5 page-5-table-1 benchmark`. It does not accept a source document title/id or safe source identifier, resolved share class identity for this mini-slice, or full P0 fixture readiness. | unmatched | `source_identity_provenance_insufficient`; benchmark-context score match is not a complete source document identity. |
| `006597` | 2024 | `synthetic` | `unmatched_synthetic` | Slice A/B artifacts; `release-maintenance-006597-strict-correctness-rerun-controller-judgment-20260529.md`; control-truth referenced LLM artifacts for `006597 / 2024` | The 006597 strict-correctness judgment accepts score rerun outcomes and comparable/unavailable rows, but report outputs are generated ignored evidence and not tracked fixtures or promotion artifacts. It does not provide source document title/id or safe source identifier for a matched annual report fixture. Control-truth LLM artifacts are generated run outputs, not source-document provenance for fixture identity. | unmatched | `source_identity_provenance_insufficient`; accepted score/run evidence does not establish matched annual-report document identity. |
| `017641` | 2024 | `synthetic` | `unmatched_synthetic` | Slice A/B artifacts; `release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | The 017641 judgment records public-output facts and a complete eligible fallback tuple with `fallback_used=true`, but terminal classification is `disclosure_data_gap_not_baseline_ready`; no source document title/id or source-safe annual-report identifier is accepted for fixture matching. | unmatched | `source_identity_provenance_insufficient`; historical fallback tuple and data-gap evidence are not a no-fallback matched fixture identity. |

## Boundary Statement

No row is upgraded to `matched`. All five rows remain `fixture_source_kind=synthetic`, `source_identity.status=unmatched_synthetic`, `matched_source_document=false`, `fallback_used=false`, `fallback_invocation=prohibited`, `promotion_allowed=false`, and `exact_numeric_correctness_allowed=false` in fixture metadata.

This mini-slice does not change golden/readiness/quality gate promotion semantics and does not implement extractor correctness. It only records that Option 1 found no sufficient accepted/pre-existing offline provenance for the five current rows.

No command invoked live LLM, retry, endpoint/DNS/curl/socket probe, `FundDocumentRepository` live access, PDF download, source fallback, provider, akshare or EID.

## Validation

Validation commands and exact results are recorded in `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option1-implementation-evidence-20260608.md`.
