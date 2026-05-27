# QDII Replacement Candidate Enumeration Plan

> Date: 2026-05-27
> Worker: AgentCodex planning worker, not controller
> Gate: `QDII replacement candidate enumeration plan gate`
> Scope: plan artifact only. No evidence run.
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement candidate selection plan accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate enumeration plan gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement candidate enumeration plan gate` |
| Latest accepted checkpoint | `8526223 docs: accept qdii replacement selection plan` |
| Accepted controller judgment | `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-controller-judgment-20260527.md` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Next Entry Point |

This is the Startup Packet next entry point, not a gate switch. This worker is producing the requested enumeration plan artifact only. The controller remains responsible for review handoff, controller judgment, control-doc update after judgment, and any later evidence authorization.

## 2. Enumeration Method

The candidate universe is `docs/code_20260519.csv`, not an approved replacement list. I scanned all 56 CSV rows using the CSV columns `基金名称`, `基金代码`, and `类别`.

Rows entered the table below only when the full scan found at least one QDII-relevant signal:

- fund name contains `QDII`;
- fund name contains `QDII-FOF`;
- CSV category is `海外股票类` or `海外债券/稳健类`;
- fund name contains overseas index/product context while the CSV category conflicts with the name signal.

Rows outside those signals are not QDII replacement candidates for this gate. They include domestic active/index/enhanced-index rows, domestic bond rows, money-market rows, and the gold row. No external search, source probe, extraction, analyze, checklist, quality gate, direct PDF/cache/helper access, or source adapter access was used.

Source provenance is intentionally conservative. A candidate is marked source-safe only if an accepted artifact already provides the public provenance tuple. Otherwise it is `provenance_unknown`, even if an accepted artifact previously loaded a repository annual report.

## 3. Candidate-Order Table

| fund_name | fund_code | csv_category | qdii_name_signal | qdii_fof_signal | taxonomy_status | asset_class_context | source_provenance_status_from_accepted_artifacts_or_provenance_unknown | candidate_order | rationale | owner | revisit_condition |
|---|---|---|---|---|---|---|---|---:|---|---|---|
| 大成标普500等权重指数(QDII)A人民币 | `096001` | 海外股票类 | yes | no | eligible_for_future_evidence_plan | Overseas equity QDII index; closest visible portfolio role to failed S&P 500 QDII slot, while not the same failed code. | provenance_unknown | 1 | Best future evidence candidate because the name and CSV category both support non-FOF equity QDII, and the S&P 500 context is closest to `017641`. Risks remain unresolved until evidence. | Future evidence worker after controller acceptance | Revisit if public provenance is not primary-success or eligible-fallback, if quality gate blocks P0, or if controller rejects S&P 500 equal-weight as representative replacement. |
| 华安纳斯达克100ETF联接(QDII)A | `040046` | 海外股票类 | yes | no | eligible_for_future_evidence_plan | Overseas equity QDII index/ETF feeder. | provenance_unknown | 2 | Clear non-FOF QDII name and overseas-stock CSV category; good fallback if `096001` fails provenance or P0 quality. | Future evidence worker after controller acceptance | Revisit if provenance remains unknown/fail-closed or P0 quality appears. |
| 摩根纳斯达克100指数(QDII)人民币A | `019172` | 海外股票类 | yes | no | eligible_for_future_evidence_plan_with_same-manager-family_risk | Overseas equity QDII index. | provenance_unknown | 3 | Clear non-FOF QDII and overseas-stock category, but same visible fund-family prefix as failed `017641`, so it may share disclosure-template risk. This is a risk flag only, not evidence. | Future evidence worker after controller acceptance | Revisit if controller prefers same-family replacement, or if higher-ranked candidates fail. |
| 华安法国CAC40ETF发起式联接(QDII)A | `021539` | 海外股票类 | yes | no | eligible_for_future_evidence_plan | Overseas equity QDII regional index/ETF feeder. | provenance_unknown | 4 | Clear QDII and overseas-stock category; less close to S&P 500 slot than top candidates because market exposure is France. | Future evidence worker after controller acceptance | Revisit after higher-ranked overseas equity index QDII candidates fail or if controller wants regional diversification coverage. |
| 华安三菱日联日经225ETF发起式联接(QDII)A | `020712` | 海外股票类 | yes | no | eligible_for_future_evidence_plan | Overseas equity QDII regional index/ETF feeder. | provenance_unknown | 5 | Clear QDII and overseas-stock category; less close to S&P 500 slot because market exposure is Japan. | Future evidence worker after controller acceptance | Revisit after higher-ranked candidates fail or if Japan equity QDII coverage is accepted as representative. |
| 摩根欧洲动力策略股票(QDII)A | `006282` | 海外股票类 | yes | no | eligible_for_future_evidence_plan_but_active_equity | Overseas active equity QDII. | provenance_unknown | 6 | Clear QDII and overseas-stock category, but active strategy is less analogous to failed index QDII slot. | Future evidence worker after controller acceptance | Revisit if controller accepts active overseas equity QDII as the replacement context. |
| 摩根日本精选股票(QDII)A | `007280` | 海外股票类 | yes | no | eligible_for_future_evidence_plan_but_active_equity | Overseas active equity QDII. | provenance_unknown | 7 | Clear QDII and overseas-stock category, but active strategy and Japan exposure make it less directly comparable. | Future evidence worker after controller acceptance | Revisit if index-like candidates fail and active QDII is accepted for this slot. |
| 建信富时100指数A(人民币) | `539003` | 海外股票类 | no | no | taxonomy_unknown_name_lacks_qdii | Overseas equity index by CSV category/name, but no explicit QDII token in fund name. | provenance_unknown | 8 | CSV category indicates overseas stock; name implies FTSE 100 exposure. Because the name lacks explicit QDII, it needs taxonomy confirmation before evidence priority. | Controller / future taxonomy decision before evidence | Revisit only if public fund-type classification or controller slot decision confirms QDII eligibility. |
| 华安国际龙头(DAX)ETF联接A | `000614` | 海外股票类 | no | no | taxonomy_unknown_name_lacks_qdii | Overseas equity index/ETF feeder by CSV category/name, but no explicit QDII token. | provenance_unknown | 9 | Overseas-stock CSV category and DAX context are relevant, but explicit QDII naming is absent. | Controller / future taxonomy decision before evidence | Revisit only after QDII slot eligibility is confirmed without changing taxonomy implementation. |
| 易方达恒生科技ETF联接(QDII)A | `013308` | 国内股票类 | yes | no | naming_category_conflict | QDII name signal conflicts with domestic-stock CSV category; Hong Kong technology exposure implied by name. | provenance_unknown | 10 | Mandatory conflict flag: QDII name but domestic-stock CSV category. It must not silently enter the evidence path until the controller accepts the conflict handling. | Controller / future taxonomy decision before evidence | Revisit after public classification or controller judgment explains why `国内股票类` does or does not disqualify it. |
| 易方达中短期美元债债券(QDII)A(人民币份额) | `007360` | 海外债券/稳健类 | yes | no | qdii_bond_lower_priority | Overseas bond QDII. | provenance_unknown | 11 | Clear QDII but bond asset class is not a like-for-like replacement for failed overseas-equity S&P 500 QDII. | Controller / future evidence worker | Revisit only if controller accepts QDII bond as satisfying this QDII slot despite asset-class mismatch. |
| 富国全球债券(QDII)人民币A | `100050` | 海外债券/稳健类 | yes | no | qdii_bond_lower_priority | Overseas bond QDII. | provenance_unknown | 12 | Clear QDII but bond asset class is not like-for-like for equity QDII replacement. | Controller / future evidence worker | Revisit only if controller accepts QDII bond replacement fitness. |
| 天弘标普500发起(QDII-FOF)A | `007721` | 海外股票类 | yes | yes | excluded_qdii_fof_taxonomy_pending | QDII-FOF; overseas equity fund-of-funds context. | provenance_unknown; accepted S0 artifact confirms annual-report load/type gap, not complete source provenance | excluded | Explicitly excluded unless a separate taxonomy gate accepts QDII-FOF for this QDII replacement slot. Existing accepted artifacts treat QDII-FOF as FOF data-gap/type-gap evidence, not pure FOF coverage. | Taxonomy gate owner / controller | Revisit only after taxonomy gate accepts QDII-FOF for the relevant slot and a future evidence plan proves source provenance. |
| 摩根海外稳健配置混合(QDII-FOF)人民币A | `017970` | 海外债券/稳健类 | yes | yes | excluded_qdii_fof_taxonomy_pending | QDII-FOF; overseas mixed/bond-stable allocation context. | provenance_unknown; accepted S0 artifact confirms annual-report load/type gap with fallback source unknown in that artifact, not complete source provenance | excluded | Explicitly excluded unless a separate taxonomy gate accepts QDII-FOF. Also not like-for-like for equity QDII replacement. | Taxonomy gate owner / controller | Revisit only after taxonomy gate and source provenance evidence are accepted. |
| 摩根标普500指数(QDII)人民币A | `017641` | 海外股票类 | yes | no | excluded_failed_current_candidate | Overseas equity QDII index; current failed candidate. | accepted complete eligible fallback provenance: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`; quality accepted as `block` | excluded | Excluded by accepted disposition: `replace`, `not_promoted`, terminal `disclosure_data_gap_not_baseline_ready` due to P0 `manager_strategy_text` disclosure data gap. | Controller | Revisit only if a separate accepted gate introduces new same-source public evidence and reopens the quality classification. |

## 4. Exclusions

`017641` is excluded. Its accepted state is provenance-complete but quality-blocked, with terminal classification `disclosure_data_gap_not_baseline_ready`; it remains `replace` and `not_promoted`.

QDII-FOF candidates are excluded unless a separate taxonomy gate accepts QDII-FOF for this QDII replacement slot. This specifically excludes:

- `007721` / 天弘标普500发起(QDII-FOF)A;
- `017970` / 摩根海外稳健配置混合(QDII-FOF)人民币A.

The accepted S0 corpus evidence records these as QDII-FOF/type-gap or FOF data-gap context. That is not an accepted replacement authorization and not complete source-provenance proof for this gate.

Bond QDII candidates (`007360`, `100050`) are not excluded from the table because they are QDII, but they are deliberately ranked below equity QDII candidates and require controller acceptance of asset-class replacement fitness before evidence.

## 5. Naming / Category Conflict Flags

`013308` is explicitly flagged as `naming_category_conflict`: the fund name contains `QDII`, while the CSV category is `国内股票类`. This table does not resolve the conflict. A future taxonomy/controller decision must explain whether the name signal, public fund-type classification, or CSV category controls before `013308` can be selected for evidence.

Rows such as `539003` and `000614` have overseas-stock category and overseas index context but no explicit `QDII` token in the name. They remain `taxonomy_unknown_name_lacks_qdii`, not source-safe replacement candidates.

## 6. Source Provenance Constraint

Accepted source provenance is available only for `017641`, and that row is excluded because quality blocks it. All other candidate rows are `provenance_unknown` for this plan, because no accepted artifact currently proves a complete public source-provenance tuple for them.

This plan therefore does not claim any replacement candidate is source-safe. Future evidence must prove one of:

- primary source success; or
- fallback with eligible `primary_failure_category` (`not_found` or `unavailable`) and complete public provenance fields.

Any `schema_drift`, `identity_mismatch`, or `integrity_error` category remains fail-closed and must stop the evidence gate.

## 7. Recommendation

Recommend selecting `096001` as the single candidate for the next future evidence gate, subject to controller review and judgment.

Reason: among the non-excluded candidates, `096001` has the cleanest visible fit for replacing an equity S&P 500 QDII slot: explicit QDII name, overseas-stock CSV category, non-FOF taxonomy signal, and S&P 500 index context. It avoids the known failed code `017641` and avoids the QDII-FOF taxonomy residual.

Unresolved risks:

- source provenance is `provenance_unknown`;
- quality status is unknown;
- `manager_strategy_text` may still be P0-blocking;
- future CLI flags and exact command paths must be verified before execution;
- no candidate is promoted or accepted for baseline/golden/corpus use by this plan.

If `096001` fails source provenance or P0 quality in a later accepted evidence gate, the next fallback order is `040046`, then `019172`, then the remaining equity QDII rows in the table. Bond QDII and conflict rows require explicit controller/taxonomy acceptance before use.

## 8. Future Evidence Gate Plan Requirements

This section lists requirements for a future plan. It is not command execution authorization.

The future evidence plan must include:

- exact public CLI commands for one selected candidate only, starting with `096001` unless controller judgment changes the selection;
- explicit pre-run verification of current CLI flags for `extraction-snapshot`, `extraction-score`, and `quality-gate`;
- `--report-year 2024`, the selected `--fund-code`, `docs/code_20260519.csv`, and ignored report output directories;
- source provenance stop checks before any quality or promotion interpretation;
- quality stop checks for P0, especially `manager_strategy_text`;
- artifact path for tracked evidence summary, proposed as `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`;
- recording of exact commands, exit codes, generated ignored paths, selected CSV row identity, public provenance tuple, quality status, P0/P1 issues, terminal classification, and `promotion_disposition=not_promoted`;
- `git diff --check` closeout validation.

The future evidence plan must stop if:

- candidate source provenance is missing, regresses, or is fail-closed;
- candidate taxonomy is ambiguous or conflicts with the accepted QDII slot;
- quality gate blocks P0;
- evidence requires direct PDF/cache/source-helper/downloader/source-adapter access;
- evidence requires changing source strategy, fallback semantics, `FundDocumentRepository`, renderer, FQ0-FQ6, Service/CLI, extractor, taxonomy, Host/Agent/dayu, tests, code, design, or control docs;
- any worker attempts promotion to durable baseline, clean denominator, fixture, golden answer corpus, report-quality corpus, or scoring-ready state.

## 9. Stop Conditions And Non-Goals

Stop conditions for this enumeration plan:

- do not run evidence;
- do not run `fund-analysis extraction-snapshot`;
- do not run `fund-analysis extraction-score`;
- do not run `fund-analysis quality-gate`;
- do not run `fund-analysis analyze`;
- do not run `fund-analysis checklist`;
- do not probe source adapters, direct annual-report PDFs, cache, download helpers, source helpers, or external web sources;
- do not change code, tests, `docs/design.md`, `docs/implementation-control.md`, README, renderer, FQ0-FQ6, Service, CLI, source strategy, `FundDocumentRepository`, Host, Agent, dayu runtime, taxonomy, extractor, or quality policy;
- do not promote any row to durable baseline, clean denominator, fixture, golden answer corpus, report-quality corpus, accepted baseline, or scoring-ready state;
- do not commit, push, open PR, merge, delete branch, or mutate GitHub state.

## 10. Review Matrix

The controller must use `init-agents` / tmux discovery before actual handoff. This planning worker did not dispatch agents.

| Stage | Agent | Required artifact |
|---|---|---|
| Plan review 1 | AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-review-mimo-20260527.md` |
| Plan review 2 | AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-review-ds-20260527.md` |
| Controller judgment | Controller | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-controller-judgment-20260527.md` |

Review focus:

- confirm full CSV scan discipline and no implicit shortlist reuse from the previous artifact;
- confirm `017641` and QDII-FOF exclusions;
- confirm `013308` naming/category conflict flag;
- confirm source provenance is not invented for unknown candidates;
- confirm `096001` is only a recommended future evidence candidate, not an accepted replacement;
- confirm future evidence requirements are plan-only and preserve all non-goals.

## 11. Validation

| Command | Exit code | Result |
|---|---:|---|
| `python - <<'PY' ... csv.DictReader(open('docs/code_20260519.csv', encoding='utf-8-sig')) ... PY` | 0 | scanned 56 CSV rows and printed row identities for enumeration |
| `git diff --check` | 0 | passed |
