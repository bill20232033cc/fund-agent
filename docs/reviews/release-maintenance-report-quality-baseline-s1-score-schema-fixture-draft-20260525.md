# Release Maintenance Report-Quality Baseline S1 Score-Schema Fixture Draft

> Date: 2026-05-25  
> Worker: AgentCodex specialist evidence/planning worker  
> Gate: `report-quality-baseline S1 score-schema fixture draft`  
> Scope: observational schema and reviewed dry-run fixture plan only; no source code, tests, renderer, FQ0-FQ6, Host/Agent package, `dayu.host`, `dayu.engine`, PR, push, or commit work.

## Step Self-Check

- Truth sources read: `AGENTS.md`; `docs/design.md` §5.4, §5.4.1, §5.4.2, §5.4.3, §6.1, §6.5; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger.
- Accepted chain read: S0 corpus-selection evidence, S0 controller judgment, and accepted report-quality baseline / Fact-Evidence contract plan controller judgment dated 2026-05-25.
- Boundary: S1 defines a schema and fixture plan only. It does not promote ignored run outputs into tracked fixtures, does not change current v0 8-chapter renderer, does not change FQ0-FQ6, does not enter S2 code implementation, and does not create Host/Agent runtime work.
- Current premise: report-quality scoring is observational. It helps choose between source/extraction work and template/writing work; it is not a product quality gate and does not output a weighted total.

## Objective

Define a first report-quality scoring record that can localize issues to fund, chapter, field, evidence anchor, data gap, source boundary, and next gate. The schema must make S0 evidence safer to review before durable baseline selection, especially where document identity, fund-type slot membership, fallback source category, and manual review state differ.

## Canonical Scoring Dimensions

The `dimension` field uses these values, directly covering `docs/design.md` §5.4.1:

| Dimension value | 中文维度 | What it checks | Primary next-gate bias |
|---|---|---|---|
| `fact_coverage` | 事实覆盖度 | Required facts for CHAPTER_CONTRACT / ITEM_RULE / preferred_lens exist, or explicit data gaps are recorded. | Source, extractor, or data-gap declaration. |
| `extraction_correctness` | 抽取正确性 | Extracted or manually reviewed facts match the annual report, official source, or reviewed correction. | Extractor / table parsing / normalization. |
| `evidence_traceability` | 证据可追溯性 | Key numbers and judgments bind to `EvidenceAnchor`, derived calculation inputs, or reviewed manual evidence. | Evidence Store / anchor generation. |
| `chapter_contract_completeness` | 章节契约完整性 | Current v0 8-chapter output answers required items and avoids prohibited items. | CHAPTER_CONTRACT / chapter plan / rule audit. |
| `final_judgment_consistency` | 最终判断一致性 | Final judgment only consumes accepted prior chapter conclusions and quality context. | Final judgment contract / assembly audit. |
| `investment_advice_boundary` | 投资建议边界 | Wording avoids buy/sell commands, return forecasts, position sizing, and unsupported causality. | Wording audit / later LLM audit. |
| `readability_actionability` | 可读性与行动性 | Reader sees concise rationale and next minimal validation question, not only field dumps. | Template / writing iteration. |
| `chapter_summary` | 章节汇总 | Reserved for `skipped` chapter summary records only. | No next gate unless the skip reason itself is disputed. |

Fund type controls applicability. For example, manager consistency is core for `active_fund`, while tracking evidence is core for `index_fund` and `enhanced_index`. The scoring dimension value domain is the seven canonical dimensions plus `chapter_summary`, and `chapter_summary` is valid only when `status=skipped`. A dimension may be `N/A` for a chapter/fund-type pair only with a reason.

## Score Record Schema Draft

Each record is an issue-oriented observation. A run may emit multiple records for the same chapter and dimension when failures localize to different fields or anchors.

| Field | Required | Value domain / shape | Meaning |
|---|---:|---|---|
| `corpus_id` | yes | Stable string, e.g. `rqb-s0-20260525` | Corpus identity from accepted S0 evidence. |
| `fund_code` | yes | 6-digit fund code string | Fund under review. |
| `report_year` | yes | integer year | Annual report year. |
| `fund_type_slot` | yes | `active_fund`, `index_fund`, `enhanced_index`, `bond_fund`, `qdii_fund`, `fof_fund` | Intended baseline coverage slot. |
| `classified_fund_type` | yes | Current `FundType` literal or `unknown` | Actual classifier result from repository-derived report facts. |
| `document_identity_status` | yes | See status table below | Whether the annual-report document identity is verified. |
| `type_slot_membership_status` | yes | See status table below | Whether the classified fund type satisfies the intended slot. |
| `source_boundary` | yes | See source boundary domain below | Boundary through which the fact, calculation, or review evidence entered scoring. |
| `source_failure_category` | yes | `none`, `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `data_gap`, `unknown_upstream_failure_category`, `not_applicable` | Source or data-gap category; fallback records must not hide upstream category. |
| `review_state` | yes | `candidate`, `repository_verified`, `fact_prefill_generated`, `fact_prefill_reviewed`, `scoring_ready`, `accepted_baseline`, `rejected`, `deferred`, `expired` | Current lifecycle state. Terminal states are allowed in schema but do not imply S0 used them. |
| `chapter_id` | yes | Current v0 chapter id: `chapter_0` to `chapter_7`, or `report_level` | Localizes issue to current renderer chapter; future 0-10 mapping is out of scope. |
| `dimension` | yes | One canonical dimension above | Quality dimension being observed. |
| `status` | yes | `pass`, `issue`, `blocked`, `N/A`, `skipped` | Per-record result. `skipped` is only for all-N/A chapter summary records. |
| `issues` | yes | List of issue objects | Localized issue details; empty only for `pass`, `N/A`, or `skipped`. |
| `evidence_anchor_refs` | yes | List of anchor ids or reviewed Markdown anchor refs | Evidence that supports the fact, issue, or pass decision. |
| `data_gap_refs` | yes | List of data gap ids | Explicit missing, conflicted, or unsafe facts. |
| `ignored_run_path` | yes | Path under `reports/scoring-runs/` | Local dry-run output path; ignored scratch, not tracked fixture. |
| `next_gate_recommendation` | yes | `source_reliability`, `data_extraction`, `evidence_anchor`, `chapter_contract`, `final_judgment_contract`, `wording_audit`, `writing_iteration`, `manual_review`, `fund_type_taxonomy`, `stop_before_durable_baseline`, `review_acceptance` | Recommended next gate or stop action. |

Optional record-level fields may include `score_run_id`, `field_path`, `claim_id`, `contract_item_id`, `severity`, `source_artifact_refs`, `reviewer_note`, `na_reason`, and `observed_value_ref`. They are optional because S1 is a draft and should not overfit before a reviewed dry run. However, every `N/A` record must record the reason through `na_reason` or an equivalent `reviewer_note`.

### Document Identity vs Type-Slot Membership

The schema intentionally splits `document_identity_status` from `type_slot_membership_status`.

| Field | Value | Meaning |
|---|---|---|
| `document_identity_status` | `verified_annual_report` | `FundDocumentRepository` returned the requested fund code, year, and annual-report kind. |
| `document_identity_status` | `unverified` | Identity has not yet been checked through the repository boundary. |
| `document_identity_status` | `mismatch` | Fund code, year, share class, or report type conflicts with the request. |
| `document_identity_status` | `source_failed` | Source failed before identity could be verified. |
| `document_identity_status` | `verified_as_annual_report_but_type_gap` | Annual report identity is verified, but fund-type slot membership is not satisfied. This is a document state, not FOF readiness. |
| `type_slot_membership_status` | `matches_slot` | `classified_fund_type` satisfies `fund_type_slot`. |
| `type_slot_membership_status` | `type_gap` | Document is valid, but current classifier does not satisfy the slot. |
| `type_slot_membership_status` | `taxonomy_pending` | Membership depends on a future taxonomy or precedence decision. |
| `type_slot_membership_status` | `unknown` | Classification evidence is unavailable. |
| `type_slot_membership_status` | `not_applicable` | Record is report-level or source-level and not tied to a fund-type slot. |

Consequence: `verified_as_annual_report_but_type_gap` must not be interpreted as scoring-ready FOF. S0 `007721` and `017970` can prove annual-report access, but they remain `type_gap` / `taxonomy_pending` for the `fof_fund` slot until a pure FOF is found or a QDII-FOF precedence gate accepts new semantics.

### Review State Terminal Semantics

`rejected`, `deferred`, and `expired` are terminal review_state values for S1 schema clarity:

| Terminal state | Minimum transition semantic | Reversible? | Denominator / durable baseline behavior |
|---|---|---|---|
| `rejected` | May enter from `candidate`, `repository_verified`, `fact_prefill_generated`, `fact_prefill_reviewed`, or `scoring_ready` when identity, type-slot, source category, reviewed fact, or score issue evidence is invalid. | Not reversible in the same run; a later run must create a new record or corpus revision. | Excluded from durable baseline; included only in rejection evidence, not scoring denominators. |
| `deferred` | May enter from any non-terminal state when evidence is incomplete but potentially recoverable, such as pending manual review or source category recovery. | Reversible by an explicit later review decision. | Excluded from durable baseline and denominators until moved to a non-terminal reviewed state. |
| `expired` | May enter from `candidate`, `repository_verified`, `fact_prefill_generated`, `fact_prefill_reviewed`, or `scoring_ready` when the corpus revision, report year, schema, or reviewed evidence has been superseded. | Not reversible; refresh through a new run or corpus revision. | Excluded from durable baseline and denominators. |

`accepted_baseline` is not terminal in the same sense: it is an accepted state for durable consideration, but a later curated-fixture gate may supersede it with a new corpus revision.

## `source_boundary` Value Domain

`source_boundary` records where the scoring input came from. It is not a confidence score.

| Value | Meaning | Durable baseline eligibility |
|---|---|---|
| `repository_derived` | Fact or anchor is derived from `FundDocumentRepository` or public Fund APIs that themselves use it. | Eligible after identity, type-slot, and manual review states pass. |
| `derived_calculation` | Value is calculated from reviewed input facts and inherits their anchors. | Eligible only when input facts and anchors are reviewed. |
| `external_official` | Official regulator, exchange, index provider, or other accepted official source outside the fund annual report. | Eligible when source identity and date are explicit. |
| `manual_review` | Human reviewer accepted, corrected, or deferred a field in a tracked review artifact under `docs/reviews/`. | Eligible as review evidence; machine fixture promotion still needs later gate. |
| `unknown` | Boundary is missing or cannot be reconstructed. | Not eligible for durable baseline selection. |
| `probe_only` | Local feasibility probe or ignored scratch output. | Not eligible for durable baseline selection. |

`unknown` and `probe_only` may appear in S1 dry-run records to preserve uncertainty, but they must be excluded before `accepted_baseline`.

In scoring context, `source_failure_category=data_gap` means the source/document boundary is available but a specific fact or field is not disclosed, not reviewed, conflicted, or cannot be safely derived. It is not equivalent to document-level `not_found`, where the target annual report itself is absent from a normally responding source.

## Status, N/A, and Issue Semantics

S1 does not output weighted total. The mandatory output is localized `issues` and `next_gate_recommendation`.

| `status` | Meaning | Denominator behavior |
|---|---|---|
| `pass` | Dimension is applicable and currently satisfies the draft contract. | Included in applicable denominator if a later summary is produced. |
| `issue` | Applicable dimension has a non-blocking localized issue. | Included. |
| `blocked` | Applicable dimension cannot be scored safely because identity, source category, anchor, or reviewed fact is insufficient. | Included as blocked when chapter is otherwise applicable. |
| `N/A` | Dimension is not applicable to this fund type / chapter, with reason recorded in `na_reason` or an equivalent `reviewer_note`. | Excluded from denominator. |
| `skipped` | Chapter summary only: every dimension for the chapter is `N/A`; the `dimension` value must be `chapter_summary`. | Not passing; excluded from pass rate and reported as skipped. |

All-N/A chapters are `skipped`, not `passing`. A chapter with unresolved identity, type-slot, source-category, or fact-review prerequisites is `blocked`, not `N/A`. A `skipped` chapter summary record must use `dimension=chapter_summary` and point to the underlying `N/A` records or their reviewer notes.

`issues` objects must be structured as:

```text
issue_id
severity: blocking | material | minor
field_path
claim_id
contract_item_id
problem
expected
observed_ref
evidence_anchor_refs
data_gap_refs
next_gate_recommendation
```

`severity` is required inside each issue object. Record-level `severity` remains optional and may be used later as a roll-up, but it must not replace per-issue severity.

## S0 Corpus Applicability Rules

S0 accepted repository evidence, not a scoring baseline. S1 must apply these rules before durable baseline selection:

| S0 candidate | S1 handling |
|---|---|
| `004393` active, `004194` enhanced index, `006597` bond | Eligible for reviewed dry-run examples where `fact_prefill_reviewed` rows exist and document identity / type-slot status remain clean. |
| `110020` index | Repository-verified S0 evidence only. It used fallback with `unknown_upstream_failure_category`; recover original category or exclude before durable baseline selection. |
| `017641` QDII | Repository-verified S0 evidence only. It used fallback with `unknown_upstream_failure_category`; recover original category or exclude before durable baseline selection. |
| `007721` QDII-FOF in FOF slot | Annual report may be verified, but current classifier and reviewed golden rows say `qdii_fund`; record as FOF `data_gap`, not scoring-ready FOF. |
| `017970` QDII-FOF in FOF slot | Annual report may be verified, but current classifier says `qdii_fund`; also fallback has `unknown_upstream_failure_category`; exclude from durable FOF baseline unless both taxonomy and source category are resolved. |

The fallback candidates `110020`, `017641`, and `017970` must not rely on an implicit assumption that fallback was compliant. Their `unknown_upstream_failure_category` must be restored to `not_found` or `unavailable`, or the candidate must be excluded. If the category restores to `schema_drift`, `identity_mismatch`, or `integrity_error`, fail closed.

## Reviewed Dry-Run Fixture Plan

The reviewed dry run is a plan for evidence collection, not a tracked fixture promotion.

| Step | Output | Location | Tracked? | Review requirement |
|---|---|---|---|---|
| Select one minimal reviewed example | Small input manifest naming corpus id, fund, chapter, field paths, and reviewed evidence refs | `reports/scoring-runs/s1-dry-run-20260525/manifest.json` | No | Controller or reviewer confirms it uses only S0-accepted evidence. |
| Produce score records | JSONL or Markdown summary with draft schema fields | `reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl` | No | Human reviewer checks issue localization and denominator semantics. |
| Record human review evidence | Markdown summary of accepted / corrected / rejected score issues | `docs/reviews/` future S1 review artifact | Yes | Review artifact may be tracked; local machine output stays ignored. |
| Decide readiness | Controller judgment | `docs/reviews/` future S1 controller judgment | Yes | If accepted, next gate is S1 review/controller judgment, not S2 implementation. |

Ignored run outputs under `reports/scoring-runs/` must remain scratch. Tracked artifacts retain only schema, plan, and artificial/manual review evidence. No fixture is promoted until a later curated-fixture gate accepts exact JSON fixture shape and review criteria.

### JSON-Like Dry-Run Record Example

This is an illustrative S1 record using S0 corpus evidence and existing reviewed rows. It does not claim a full scorer has run.

```json
{
  "corpus_id": "rqb-s0-20260525",
  "fund_code": "004393",
  "report_year": 2024,
  "fund_type_slot": "active_fund",
  "classified_fund_type": "active_fund",
  "document_identity_status": "verified_annual_report",
  "type_slot_membership_status": "matches_slot",
  "source_boundary": "manual_review",
  "source_failure_category": "none",
  "review_state": "fact_prefill_reviewed",
  "chapter_id": "chapter_3",
  "dimension": "evidence_traceability",
  "status": "pass",
  "issues": [],
  "evidence_anchor_refs": [
    "golden-answer-prefill-reviewed.md#004393.manager_alignment.manager_holding",
    "年报2024 §9 page-63 page-63-table-2 manager_holding"
  ],
  "data_gap_refs": [],
  "ignored_run_path": "reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl",
  "next_gate_recommendation": "review_acceptance"
}
```

The same fund can also demonstrate issue localization without pretending the scorer has completed:

| Field | Example value |
|---|---|
| `field_path` | `turnover_rate` |
| `chapter_id` | `chapter_3` |
| `dimension` | `fact_coverage` |
| `status` | `issue` |
| `issues.problem` | Existing reviewed prefill says `当前 slice 不处理`; active-fund chapter 3 manager consistency may need turnover / style-change evidence if the chapter claims stable process based on "说 vs 做". |
| `evidence_anchor_refs` | `golden-answer-prefill-reviewed.md#004393.turnover_rate` |
| `data_gap_refs` | `gap:004393.2024.turnover_rate.not_reviewed_in_current_slice` |
| `source_boundary` | `manual_review` |
| `next_gate_recommendation` | `data_extraction` if turnover is required by the chapter claim; otherwise `chapter_contract` to ensure the report states the gap instead of inferring style stability. |

This localizes the issue to a field, chapter, dimension, reviewed evidence row, and next gate. It is not a full report-quality score and it is not an accepted baseline.

## Stop Conditions Before Durable Baseline Selection

Stop before durable baseline selection if any of the following remain true:

1. `source_failure_category` for fallback candidates `110020`, `017641`, or `017970` remains `unknown_upstream_failure_category`.
2. A fallback category restores to `schema_drift`, `identity_mismatch`, or `integrity_error`.
3. FOF coverage still has no repository-verified pure `fof_fund`, and no accepted fund-type taxonomy / QDII-FOF precedence gate exists.
4. `fact_prefill_reviewed` evidence is insufficient for the selected chapter fields.
5. `document_identity_status` is not `verified_annual_report` for included scoring records.
6. `type_slot_membership_status` is not `matches_slot`, unless the record is explicitly a `data_gap` or taxonomy review issue and excluded from baseline denominator.
7. Any record uses `source_boundary=unknown` or `source_boundary=probe_only` as if it were durable evidence.

## Next Step Recommendation

This S1 draft should enter independent review. If accepted, the next gate is S1 review/controller judgment to decide whether the schema and dry-run plan are accepted. It is not S2 code implementation.

Only after S1 review/controller judgment accepts the schema should the controller decide whether to authorize a dry-run evidence collection or move to a separate S2 bundle candidate gate.

## Residual Risks

| Risk | Impact | Owner / next handling |
|---|---|---|
| Source category recovery may require a source reliability probe | Fallback candidates cannot enter durable baseline. | S1 review/controller judgment or source reliability evidence gate. |
| FOF remains a data gap | Baseline cannot claim all fund-type lenses are represented. | S1 second pass or fund-type taxonomy gate. |
| Manual reviewed evidence is uneven | Dry-run should prefer `004393`, `004194`, or `006597`; broader scoring must wait. | Manual review / fact prefill review. |
| Schema may be too verbose for implementation | S2 should reduce to typed essentials only after review accepts issue localization behavior. | S2 bundle candidate, not this gate. |
| Schema value-domain validation is not executable in this draft | `rg` can prove terms exist, but cannot validate enum exhaustiveness, `N/A` reason presence, terminal transitions, or `chapter_summary` constraints. | S2 / later implementation should add value-domain validation tests if schema becomes code. |

## Validation

Commands run:

```text
rg -n 'corpus_id|fund_code|report_year|fund_type_slot|classified_fund_type|document_identity_status|type_slot_membership_status|source_boundary|source_failure_category|review_state|chapter_id|dimension|status|issues|evidence_anchor_refs|data_gap_refs|ignored_run_path|next_gate_recommendation' docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md
rg -n 'fact_coverage|extraction_correctness|evidence_traceability|chapter_contract_completeness|final_judgment_consistency|investment_advice_boundary|readability_actionability|chapter_summary' docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md
rg -n 'repository_derived|derived_calculation|external_official|manual_review|unknown|probe_only|N/A|skipped|na_reason|terminal|data_gap|not equivalent to document-level `not_found`|unknown_upstream_failure_category|reports/scoring-runs|renderer|FQ0-FQ6|Host/Agent|dayu.host|dayu.engine|S2 code implementation|value-domain validation' docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md
git diff --check
```

Actual result:

- First `rg` passed and confirmed all required schema fields are present.
- Second `rg` passed and confirmed all seven scoring dimensions plus `chapter_summary` are present.
- Third `rg` passed and confirmed `source_boundary` values, `N/A` / `skipped` semantics, `na_reason`, terminal state wording, `data_gap` clarification, `unknown_upstream_failure_category`, `reports/scoring-runs`, non-goal boundary terms, and `value-domain validation` residual are present.
- `git diff --check` passed with no output.
