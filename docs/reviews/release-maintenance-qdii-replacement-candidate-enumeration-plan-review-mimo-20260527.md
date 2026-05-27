# QDII Replacement Candidate Enumeration Plan — Review (AgentMiMo)

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Gate: `QDII replacement candidate enumeration plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md`
> Required review artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-review-mimo-20260527.md`
> Verdict: **PASS**

## Startup Packet Replay

| Item | Plan states | Control doc states | Match |
|---|---|---|---|
| Current gate | `QDII replacement candidate selection plan accepted locally` (§1) | `QDII replacement candidate selection plan accepted locally` (line 28) | yes |
| Next entry point | `QDII replacement candidate enumeration plan gate` (§1) | `QDII replacement candidate enumeration plan gate` (line 29, line 418) | yes |
| Latest accepted checkpoint | `8526223 docs: accept qdii replacement selection plan` (§1) | Matches git log `8526223` | yes |
| Accepted controller judgment | Selection plan controller judgment (§1) | Accepted artifacts table line 321 | yes |

The plan correctly replays the Startup Packet. This gate equals the current Startup Packet next entry point. No blocking gate-switch discrepancy.

## CSV Scan Discipline

The plan claims a full scan of `docs/code_20260519.csv` (56 rows) using columns `基金名称`, `基金代码`, and `类别` (§2).

Independent verification confirms 56 CSV rows total. The QDII-relevant rows identified by independent scan are:

| Code | QDII name | QDII-FOF | Overseas cat | In plan table | Disposition |
|---|---|---|---|---|---|
| `096001` | yes | no | yes | yes | candidate #1 |
| `040046` | yes | no | yes | yes | candidate #2 |
| `019172` | yes | no | yes | yes | candidate #3 |
| `021539` | yes | no | yes | yes | candidate #4 |
| `020712` | yes | no | yes | yes | candidate #5 |
| `006282` | yes | no | yes | yes | candidate #6 |
| `007280` | yes | no | yes | yes | candidate #7 |
| `539003` | no | no | yes | yes | candidate #8 |
| `000614` | no | no | yes | yes | candidate #9 |
| `013308` | yes | no | no | yes | candidate #10 (conflict flagged) |
| `007360` | yes | no | yes | yes | candidate #11 |
| `100050` | yes | no | yes | yes | candidate #12 |
| `007721` | yes | yes | yes | yes | excluded (QDII-FOF) |
| `017970` | yes | yes | yes | yes | excluded (QDII-FOF) |
| `017641` | yes | no | yes | yes | excluded (failed candidate) |

All 14 QDII-signal rows and 1 excluded-failed row are accounted for. The remaining 41 CSV rows have no QDII name signal, no QDII-FOF signal, and no overseas category — they are correctly excluded from the candidate table. No implicit shortlist reuse from the previous selection plan artifact is visible. Scan discipline is sound.

## Required Table Content

| Required column | Present | Notes |
|---|---|---|
| Source row identity (fund_name, fund_code) | yes | First two columns |
| QDII/QDII-FOF taxonomy status | yes | `taxonomy_status` column with descriptive enum values |
| CSV category / asset-class context | yes | `csv_category` and `asset_class_context` columns |
| Source provenance status or `provenance_unknown` | yes | Column present; all non-excluded rows are `provenance_unknown`; `017641` correctly states accepted complete eligible fallback provenance |
| Candidate order rationale | yes | `candidate_order` and `rationale` columns |
| Owner | yes | `owner` column |
| Revisit condition | yes | `revisit_condition` column |

All required columns are present and populated.

## Exclusions

- **`017641`**: Excluded. Plan states accepted complete eligible fallback provenance, quality `block`, terminal classification `disclosure_data_gap_not_baseline_ready`, disposition `replace` / `not_promoted` (§3 row, §4). Consistent with accepted artifacts.
- **QDII-FOF (`007721`, `017970`)**: Excluded unless separate taxonomy gate accepts QDII-FOF for the QDII slot (§4). Both rows correctly marked `excluded_qdii_fof_taxonomy_pending`. Consistent with accepted S0 corpus evidence that treats QDII-FOF as type-gap evidence, not pure FOF coverage.

## Conflict Handling

`013308` is explicitly flagged as `naming_category_conflict`: QDII name signal conflicts with `国内股票类` CSV category (§3 row, §5). The plan does not resolve the conflict and does not silently promote `013308` into the evidence path. A future taxonomy/controller decision is required. This satisfies the mandatory conflict-flag requirement from the accepted selection plan controller judgment (DS F2).

`539003` and `000614` are correctly flagged as `taxonomy_unknown_name_lacks_qdii` — overseas-stock CSV category but no explicit QDII token in the fund name (§5).

## Source Provenance Discipline

No unknown candidate is claimed source-safe, scoring-ready, golden-ready, or baseline-ready. Section 6 explicitly states:

> "This plan therefore does not claim any replacement candidate is source-safe."

All non-excluded candidates are `provenance_unknown`. Only `017641` has accepted provenance, and it is excluded. This satisfies the review requirement.

## Future Evidence Gate Sequencing

Section 8 defines requirements for a future evidence plan — it is not command execution authorization. The plan recommends selecting `096001` as the single candidate for the next future evidence gate (§7), subject to controller review. The future evidence plan must:

- Start with exact CLI commands for one selected candidate only;
- Verify current CLI flags before execution;
- Include source provenance stop checks and quality stop checks;
- Record promotion_disposition=not_promoted;
- Stop on provenance regression, taxonomy ambiguity, P0 quality block, or any promotion attempt.

This correctly sequences plan-before-evidence and does not authorize direct evidence execution or promotion.

## Boundary Compliance

No production code, renderer, FQ0-FQ6, Service/CLI, FundDocumentRepository, source helpers, PDF/cache access, Host/Agent/dayu, taxonomy implementation, extractor implementation, baseline/golden fixture promotion, GitHub mutation, push, PR, merge, or branch deletion is authorized or performed by this plan. Section 9 explicitly lists all stop conditions and non-goals. Boundary compliance is clean.

## 096001 as Single Future Evidence Candidate

**Yes**, `096001` may be used as the single candidate for the next future evidence plan gate, without treating it as source-safe or promoted. The plan recommends it (§7) with explicit unresolved risks: source provenance is `provenance_unknown`, quality status is unknown, `manager_strategy_text` may be P0-blocking, and no candidate is promoted or accepted for baseline/golden/corpus use. This is a recommendation for the next plan gate, not an acceptance or promotion.

## Accepted Strengths

1. Conservative source-provenance handling: no candidate is claimed source-safe without accepted evidence.
2. Clear fallback ordering: `096001` → `040046` → `019172` → remaining equity QDII, with bond QDII and conflict rows requiring explicit controller acceptance.
3. Well-structured future evidence gate requirements (§8) with explicit stop conditions preserving all non-goals.
4. Correct preservation of all accepted dispositions: `017641` = replace/not-promoted, `110020` = include-for-later-review, FOF = needs-taxonomy-gate, `004393`/`004194` = include-for-later-review.
5. `013308` naming/category conflict explicitly flagged, not silently promoted.
6. QDII-FOF candidates excluded with clear revisit condition tied to future taxonomy gate.

## Findings

No material findings. No blocking issues.

### F1 (Informational): Validation section completeness

Section 11 records a Python scan command with exit code 0 and "scanned 56 CSV rows", but does not list the specific QDII-signal rows found. Independent verification confirms all 14 QDII-signal rows are in the table, so this is informational only — the scan result is correct even though the validation evidence is sparse.

### F2 (Informational): `013308` conflict resolution timeline

The plan correctly flags `013308` as `naming_category_conflict` and defers resolution to a future taxonomy/controller decision (§5). However, it does not specify whether this conflict must be resolved before the next evidence gate or can remain deferred while other candidates proceed. Since the plan recommends `096001` as the single evidence candidate and `013308` is candidate #10, this has no near-term impact, but a future gate may need to address this explicitly.

## Required Fixes Before Acceptance

None.

## Residual Risks Suitable for Controller Doc

1. `013308` naming/category conflict remains unresolved; future taxonomy gate or controller judgment needed before it can enter evidence path.
2. All non-excluded candidates (except `017641`) are `provenance_unknown`; evidence gate for `096001` may fail at source-provenance stage.
3. `manager_strategy_text` P0 risk applies to any QDII candidate using the same disclosure template — `019172` shares the `摩根` fund-family prefix with `017641` and is flagged with `eligible_for_future_evidence_plan_with_same-manager-family_risk`.
4. Bond QDII candidates (`007360`, `100050`) require explicit asset-class replacement fitness acceptance from controller before evidence.
