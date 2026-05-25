# Release Maintenance Report-Quality Baseline S1 Dry-Run Evidence

> Date: 2026-05-25  
> Worker: AgentCodex specialist evidence worker  
> Gate: `report-quality-baseline S1 dry-run evidence collection`  
> Scope: dry-run evidence only; no source code, tests, renderer, FQ0-FQ6, Host/Agent package, `dayu.host`, `dayu.engine`, PR, push, commit, durable baseline, or fixture promotion.

## Step Self-Check

- Truth sources read: `AGENTS.md`; `docs/design.md` §5.4, §5.4.1, §5.4.2, §5.4.3, §6.1, §6.5; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger.
- Accepted chain read: S0 corpus-selection evidence and controller judgment; accepted S1 score-schema fixture draft and controller judgment.
- Boundary: this is an S1 dry-run evidence artifact. The ignored outputs under `reports/scoring-runs/s1-dry-run-20260525/` are not durable baseline, no fixture promotion, and not S2 code implementation.
- Source discipline: no production annual-report access was performed in this dry run. It consumes existing reviewed rows and accepted review artifacts only.

## Inputs

| Input source | Path / refs | Use |
|---|---|---|
| Accepted S1 schema | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md` | Record fields, value domains, issue object shape, denominator semantics |
| S1 controller judgment | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-controller-judgment-20260525.md` | Confirms next gate is dry-run evidence collection, not S2 implementation |
| S0 corpus evidence | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md` | Confirms `004393` / 2024 as S0-clean `active_fund`; identifies excluded fallback candidates and FOF data_gap |
| S0 controller judgment | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-controller-judgment-20260525.md` | Confirms fallback candidates require category recovery or exclusion before durable baseline |
| Reviewed rows | `reports/golden-answers/golden-answer-prefill-reviewed.md:30`, `:36`, `:37` | `004393` active_fund classification, turnover gap, and manager holding anchor |

## Ignored Outputs

| Output | Purpose | Tracked? |
|---|---|---|
| `reports/scoring-runs/s1-dry-run-20260525/manifest.json` | Machine-readable-ish input manifest and exclusions | No; git ignored |
| `reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl` | Two schema-shaped dry-run records | No; git ignored |
| `reports/scoring-runs/s1-dry-run-20260525/summary.md` | Human-readable ignored summary | No; git ignored |

These files are scratch evidence only. They are not product functionality, not durable baseline, no fixture promotion, and not S2 code implementation.

## Schema Fields Used

The dry-run records use the accepted core fields:

`score_run_id`, `corpus_id`, `fund_code`, `report_year`, `fund_type_slot`, `classified_fund_type`, `document_identity_status`, `type_slot_membership_status`, `source_boundary`, `source_failure_category`, `review_state`, `chapter_id`, `dimension`, `status`, `issues`, `evidence_anchor_refs`, `data_gap_refs`, `ignored_run_path`, `next_gate_recommendation`, `field_path`, `reviewer_note`, and `na_reason`.

The dry run also exercises per-issue fields:

`issue_id`, `severity`, `field_path`, `claim_id`, `contract_item_id`, `problem`, `expected`, `observed_ref`, `evidence_anchor_refs`, `data_gap_refs`, and `next_gate_recommendation`.

## Dry-Run Records

| Record | Fund / year | Chapter | Dimension | Status | Evidence / gap refs | Next gate |
|---|---|---|---|---|---|---|
| Pass record | `004393` / 2024 | `chapter_3` | `evidence_traceability` | `pass` | `reports/golden-answers/golden-answer-prefill-reviewed.md:37`; `年报2024 §9 page-63 page-63-table-2 manager_holding` | `review_acceptance` |
| Localized issue record | `004393` / 2024 | `chapter_3` | `fact_coverage` | `issue` | `reports/golden-answers/golden-answer-prefill-reviewed.md:36`; `gap:004393.2024.turnover_rate.not_reviewed_in_current_slice` | `data_extraction` |
| Semantics note | `004393` / 2024 | `chapter_3` | `chapter_summary` | not emitted | `chapter_3` has applicable records, so no `skipped` record is emitted | n/a |

### Pass Record Rationale

The pass record is deliberately narrow: it only says the reviewed `manager_alignment.manager_holding` row has traceable evidence for active-fund chapter 3 manager-alignment analysis. It does not claim the whole chapter passes, does not claim report-quality scoring is implemented, and does not promote the row to a durable baseline.

Record fields:

- `source_boundary=manual_review`
- `source_failure_category=none`
- `review_state=fact_prefill_reviewed`
- `document_identity_status=verified_annual_report`
- `type_slot_membership_status=matches_slot`
- `evidence_anchor_refs=["reports/golden-answers/golden-answer-prefill-reviewed.md:37", "年报2024 §9 page-63 page-63-table-2 manager_holding"]`
- `data_gap_refs=[]`

### Localized Issue Rationale

The issue record is based on the reviewed row where `turnover_rate` is explicitly `当前 slice 不处理`. For an `active_fund`, chapter 3 is the manager / process / "说 vs 做" chapter, so turnover or style-change evidence may be needed before a report can make a stable-process claim. Because the row is not reviewed as an extracted fact, the dry run records a `fact_coverage` issue rather than inventing a value.

Issue object:

| Field | Value |
|---|---|
| `issue_id` | `s1-dry-run-004393-ch3-turnover-gap` |
| `severity` | `material` |
| `field_path` | `turnover_rate` |
| `claim_id` | `chapter_3_manager_consistency_say_vs_do` |
| `contract_item_id` | `active_fund.chapter_3.manager_consistency` |
| `problem` | Reviewed prefill explicitly marks `turnover_rate` as current slice not handled. |
| `expected` | Reviewed turnover / style-change evidence with anchors, or explicit data_gap wording and no unsupported stability claim. |
| `observed_ref` | `reports/golden-answers/golden-answer-prefill-reviewed.md:36` |
| `data_gap_refs` | `gap:004393.2024.turnover_rate.not_reviewed_in_current_slice` |
| `next_gate_recommendation` | `data_extraction` |

## Denominator / N/A / Skipped / Chapter Summary Semantics

- `pass`: applicable and included in a later applicable denominator.
- `issue`: applicable and included in a later applicable denominator; it must not be hidden as `N/A`.
- `blocked`: not emitted in this dry run because identity, type slot, and reviewed-row refs were sufficient for the two applicable records.
- `N/A`: excluded from denominator and must carry `na_reason` or equivalent `reviewer_note`; this dry run does not use an `N/A` record because the selected chapter has applicable dimensions.
- `skipped`: only valid for all-`N/A` chapter summaries with `dimension=chapter_summary`; it is not passing.
- `chapter_summary`: not emitted in the ignored JSONL because `004393` chapter 3 has applicable `pass` and `issue` records. This artifact records the semantics without creating an invalid skipped record.

## Excluded Fallback Candidates

| Candidate | S1 dry-run treatment | Reason |
|---|---|---|
| `110020` / 2024 | excluded from durable baseline | Eastmoney fallback was observed in S0, but upstream category remains `unknown_upstream_failure_category` |
| `017641` / 2024 | excluded from durable baseline | Eastmoney fallback was observed in S0, but upstream category remains `unknown_upstream_failure_category` |
| `017970` / 2024 | excluded from durable baseline | `unknown_upstream_failure_category` plus FOF type-gap / taxonomy-pending status |

If a future source reliability gate recovers any fallback category as `not_found` or `unavailable`, the candidate can be reconsidered. If it recovers `schema_drift`, `identity_mismatch`, or `integrity_error`, the candidate must fail closed.

## FOF Data_Gap

FOF data_gap remains open. S0 found `007721` and `017970` as QDII-FOF annual-report candidates, but current classification evidence treats them as `qdii_fund`, not pure `fof_fund`. This dry run does not treat QDII-FOF as satisfying the `fof_fund` slot and does not include a FOF denominator.

## Next Gate Recommendation

Recommendation: proceed to independent review of this S1 dry-run evidence.

Reason: the dry run demonstrates that the accepted schema can localize one narrow `pass` and one material `issue` to fund, chapter, dimension, field, evidence refs, data_gap refs, source boundary, and next gate, while preserving denominator semantics and excluding unsafe fallback / FOF candidates.

Do not enter S2 code implementation until this evidence is reviewed and the controller accepts the dry-run behavior.

## Open Gaps / Residual Risks

| Gap | Risk | Required handling |
|---|---|---|
| Dry-run uses reviewed Markdown rows rather than executable scorer output | Good enough for S1 evidence, but not a product scorer | Review this artifact first; S2 may later implement typed validation if accepted |
| `turnover_rate` issue depends on chapter-claim applicability | If the report does not claim process stability from turnover, the issue should be downgraded to explicit data_gap wording | Reviewer should confirm whether `data_extraction` or `chapter_contract` is the better next gate |
| Fallback upstream categories remain unknown | `110020`, `017641`, and `017970` cannot enter durable baseline | Source reliability evidence must recover category or keep them excluded |
| FOF remains unrepresented | Baseline cannot claim all fund-type lenses are covered | Find pure FOF or open taxonomy / QDII-FOF precedence gate |
| No real all-N/A chapter was emitted | `chapter_summary` / `skipped` semantics are documented but not exercised as a JSONL record | Later dry run should include a real all-N/A chapter only if needed |

## Validation

Commands run:

```text
git check-ignore -v reports/scoring-runs/s1-dry-run-20260525/ reports/scoring-runs/s1-dry-run-20260525/manifest.json reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl reports/scoring-runs/s1-dry-run-20260525/summary.md
rg -n "corpus_id|fund_code|report_year|fund_type_slot|classified_fund_type|document_identity_status|type_slot_membership_status|source_boundary|source_failure_category|review_state|chapter_id|dimension|status|issues|evidence_anchor_refs|data_gap_refs|ignored_run_path|next_gate_recommendation" docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md
rg -n 'reports/scoring-runs|unknown_upstream_failure_category|FOF data_gap|not durable baseline|no fixture promotion|not S2 code implementation|N/A|skipped|chapter_summary' docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md
jq -c . reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl
python -m json.tool reports/scoring-runs/s1-dry-run-20260525/manifest.json
wc -l reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl
git diff --check
```

Actual result:

- `git check-ignore -v` passed and confirmed `.gitignore:22:reports/scoring-runs/` covers the dry-run directory and all three output files.
- First `rg` passed and confirmed accepted schema core fields are present in this tracked artifact.
- Second `rg` passed and confirmed `reports/scoring-runs`, `unknown_upstream_failure_category`, FOF data_gap, `not durable baseline`, `no fixture promotion`, `not S2 code implementation`, `N/A`, `skipped`, and `chapter_summary` are present.
- `jq -c .` passed for both JSONL score records.
- `python -m json.tool` passed for `manifest.json`.
- `wc -l` confirmed `score-records.jsonl` contains 2 records.
- `git diff --check` passed with no output.
