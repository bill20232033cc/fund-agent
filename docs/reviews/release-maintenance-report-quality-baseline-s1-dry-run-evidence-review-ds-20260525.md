# Release Maintenance Report-Quality Baseline S1 Dry-Run Evidence Review — AgentDS

> Date: 2026-05-25
> Reviewer: AgentDS (phaseflow independent review agent)
> Gate: `report-quality-baseline S1 dry-run evidence collection`
> Review target: `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md`
> Verdict: **PASS_WITH_FINDINGS**

## Step Self-Check

- Truth sources read: `AGENTS.md`; `docs/design.md` §5.4/§5.4.1/§5.4.2/§5.4.3/§6.1/§6.5; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger.
- Accepted chain read: S1 score-schema fixture draft and controller judgment; S0 corpus-selection evidence and controller judgment.
- Ignored outputs inspected (not tracked): `reports/scoring-runs/s1-dry-run-20260525/manifest.json`, `score-records.jsonl`, `summary.md`.
- Boundary: review only; no file edits, commits, pushes, or PRs.

## Review Lenses and Findings

### Lens 1: Schema Core Fields and Localized Records

**Question**: Does the dry run use accepted S1 schema core fields and produce at least one localized pass or issue record?

**Evidence**:
- JSONL record 1 (pass): contains all required fields — `corpus_id`, `fund_code`, `report_year`, `fund_type_slot`, `classified_fund_type`, `document_identity_status`, `type_slot_membership_status`, `source_boundary`, `source_failure_category`, `review_state`, `chapter_id`, `dimension`, `status`, `issues`, `evidence_anchor_refs`, `data_gap_refs`, `ignored_run_path`, `next_gate_recommendation`. Optional fields present: `score_run_id`, `field_path`, `reviewer_note`.
- JSONL record 2 (issue): all required fields present plus complete per-issue fields: `issue_id`, `severity`, `field_path`, `claim_id`, `contract_item_id`, `problem`, `expected`, `observed_ref`, `evidence_anchor_refs`, `data_gap_refs`, `next_gate_recommendation`.
- Pass record localizes to `chapter_3` / `evidence_traceability` / `manager_alignment.manager_holding`.
- Issue record localizes to `chapter_3` / `fact_coverage` / `turnover_rate`.
- Both records use `source_boundary=manual_review` with `review_state=fact_prefill_reviewed`, matching the current S1 constraint that `fact_prefill_reviewed` evidence lives in Markdown under `docs/reviews/` until a later curated-fixture gate.

**Verdict**: PASS. Two localized records using accepted schema core fields, one pass and one issue, correctly scoped to field/chapter/dimension.

### Lens 2: Narrow Pass vs Whole-Chapter or Durable Baseline Claim

**Question**: Is the `004393` / `chapter_3` / `manager_holding` pass a narrow pass, without impersonating a whole-chapter pass or durable baseline?

**Evidence**:
- Record `dimension` is `evidence_traceability`, not `chapter_summary` or a whole-chapter aggregate.
- `field_path` is `manager_alignment.manager_holding` — single field, single dimension.
- `reviewer_note` in JSONL: "not durable baseline; no fixture promotion; not S2 code implementation."
- Evidence document §Pass Record Rationale (line 53–55): explicitly states the pass is deliberately narrow, does not claim the whole chapter passes, and does not promote to durable baseline.
- `next_gate_recommendation` is `review_acceptance`, not `accepted_baseline`.
- `review_state` is `fact_prefill_reviewed`, not `accepted_baseline`.

**Verdict**: PASS. Narrow pass properly scoped; no chapter-level or durable-baseline overclaim.

### Lens 3: Turnover Rate Issue — Evidence Source, Localization, and Next Gate

**Question**: Is the turnover_rate issue based on same-source reviewed evidence? Is it correctly localized to field/chapter/dimension/data_gap/next_gate? Should next_gate be `data_extraction` or `chapter_contract`?

**Evidence**:
- `observed_ref`: `reports/golden-answers/golden-answer-prefill-reviewed.md:36` — verified as the row where `turnover_rate` is explicitly "当前 slice 不处理" (line 36 of the reviewed prefill).
- Field localization: `field_path=turnover_rate`, `chapter_id=chapter_3`, `dimension=fact_coverage` — all correct. Chapter 3 is the manager/process/"说 vs 做" chapter; turnover/style-change evidence is relevant for active_fund manager consistency assessment.
- `data_gap_refs`: `gap:004393.2024.turnover_rate.not_reviewed_in_current_slice` — correctly identifies the gap.
- `claim_id`: `chapter_3_manager_consistency_say_vs_do` — appropriate for the dimension.
- `contract_item_id`: `active_fund.chapter_3.manager_consistency` — consistent with active_fund preferred_lens.

**Next gate assessment**: The dry run chose `next_gate_recommendation=data_extraction`. The accepted S1 schema draft (line 212) explicitly says: "`data_extraction` if turnover is required by the chapter claim; otherwise `chapter_contract` to ensure the report states the gap instead of inferring style stability." The dry-run evidence document itself acknowledges this ambiguity in Open Gaps (line 122): "If the report does not claim process stability from turnover, the issue should be downgraded to explicit data_gap wording."

The issue's `problem` text says: "chapter_3 cannot rely on turnover/style-change evidence unless the report states the gap." This phrasing leans toward `chapter_contract` — the fix could be a contract amendment (explicitly state the gap) rather than new data extraction. However, the S1 schema draft allows either path depending on whether the chapter claim requires turnover evidence. The ambiguity is transparently documented as an open gap.

**Verdict**: PASS_WITH_FINDING (F-1). The issue is correctly localized, based on same-source reviewed evidence. The `next_gate_recommendation` choice of `data_extraction` is defensible but the ambiguity with `chapter_contract` should be resolved before durable baseline selection. The evidence document already acknowledges this, so it is not a hidden defect.

### Lens 4: Denominator / N/A / Skipped / Chapter_Summary Semantics

**Question**: Are denominator, N/A, skipped, and chapter_summary semantics self-consistent? Was any invalid skipped/chapter_summary JSONL record emitted?

**Evidence**:
- JSONL contains exactly 2 records, both for `chapter_3`: one `pass` (`evidence_traceability`), one `issue` (`fact_coverage`).
- No `N/A` record emitted — correct, because chapter_3 has applicable dimensions for active_fund.
- No `skipped` record emitted — correct per schema: `skipped` requires all-N/A chapter with `dimension=chapter_summary`.
- No `chapter_summary` JSONL record emitted — correct, because chapter_3 is not all-N/A.
- The evidence document correctly documents the semantics (line 87–93): `pass` and `issue` are included in denominator; `N/A` is excluded and requires `na_reason`; `skipped` is only for all-N/A chapter summaries and is not passing.
- The `na_reason` field is mentioned in schema but not exercised, which is expected since no N/A record was emitted.

**Verdict**: PASS. Semantics are self-consistent; no invalid skipped/chapter_summary record was emitted.

### Lens 5: Ignored Outputs — Git Ignored, No Fixture Promotion

**Question**: Are ignored outputs under `reports/scoring-runs` and git-ignored? Does the tracked artifact avoid promoting JSON fixtures?

**Evidence**:
- `git check-ignore -v` confirmed: `.gitignore:22:reports/scoring-runs/` covers the directory and all three output files (`manifest.json`, `score-records.jsonl`, `summary.md`).
- The tracked artifact is `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md` — a Markdown review evidence document, not a JSON fixture.
- The evidence document explicitly states (line 33): "These files are scratch evidence only. They are not product functionality, not durable baseline, no fixture promotion, and not S2 code implementation."
- `manifest.json` self-declares: `"durability": "ignored scratch output; not durable baseline; no fixture promotion; not S2 code implementation"`.
- No JSON fixture was promoted into a tracked path.

**Verdict**: PASS. Ignored outputs correctly git-ignored; no fixture promotion occurred.

### Lens 6: Fallback Candidates and FOF Data_Gap Exclusion

**Question**: Are fallback candidates `110020`/`017641`/`017970` and FOF data_gap excluded from durable baseline?

**Evidence**:
- Evidence document §Excluded Fallback Candidates (line 95–103): all three explicitly excluded with reasons tied to `unknown_upstream_failure_category`.
- `manifest.json` confirms all three in `excluded_fallback_candidates` with explicit reasons.
- FOF data_gap documented (line 105–107): QDII-FOF candidates classified as `qdii_fund`, not pure `fof_fund`; FOF denominator not included.
- The dry run only uses `004393` (S0-clean, `active_fund`, `matches_slot`, `verified_annual_report`, `source_failure_category=none`).
- Stop conditions from S1 schema draft (lines 216–227) are all satisfied: no fallback candidate with unknown category entered scoring; FOF remains a gap; `004393` has `verified_annual_report` and `matches_slot`.

**Verdict**: PASS. Fallback candidates and FOF data_gap correctly excluded.

### Lens 7: Non-Goal Compliance

**Question**: Does the dry run violate any non-goals: renderer, FQ0-FQ6, Host/Agent, dayu.host/dayu.engine, S2 code implementation?

**Evidence**:
- No renderer code changed. The dry run is purely an evidence artifact.
- No FQ0-FQ6 quality gate behavior changed.
- No `fund_agent/host` or `fund_agent/agent` package created.
- No `dayu.host` or `dayu.engine` dependency introduced.
- No S2 code implementation started. The evidence document explicitly says (line 115): "Do not enter S2 code implementation until this evidence is reviewed and the controller accepts the dry-run behavior."
- The evidence document's scope declaration (line 6) correctly lists all non-goals.
- The `reviewer_note` in both JSONL records reiterates: "not S2 code implementation."

**Verdict**: PASS. All non-goals respected.

## Findings Summary

| ID | Severity | Lens | Finding | File/Line |
|----|----------|------|---------|-----------|
| F-1 | Minor | Lens 3 | `turnover_rate` issue `next_gate_recommendation` is `data_extraction`, but the S1 schema draft allows `chapter_contract` as an alternative. The evidence document acknowledges this ambiguity as an open gap (line 122). The choice is defensible but should be confirmed during controller judgment: if the chapter contract can simply state the gap without requiring new data, `chapter_contract` is the cheaper path. | Evidence doc line 84, 122; S1 schema draft line 212 |
| F-2 | Info | Lens 4 | `chapter_summary`/`skipped` semantics are documented but not exercised as a JSONL record. This is a known limitation of the minimal dry run (only one chapter, one fund). The evidence document acknowledges this as an open gap (line 125). Not a blocker. | Evidence doc line 125 |
| F-3 | Info | Lens 4 | `blocked` status not exercised — the dry run's single fund/chapter had clean identity, type-slot, and reviewed-row refs, so no record entered `blocked` state. `blocked` semantics are documented in schema but untested in this dry run. | Evidence doc line 90 |
| F-4 | Info | Lens 4 | `na_reason` field presence not exercised — no `N/A` record was emitted, so `na_reason` behavior on real N/A records is documented but unverified. | Evidence doc line 91 |

## Open Residuals

| Residual | Severity | Recommended handling |
|---|---|---|
| `next_gate_recommendation` for turnover gap (F-1) | Minor | Controller should confirm whether `data_extraction` or `chapter_contract` is correct. If the report does not currently claim process stability from turnover, `chapter_contract` (add explicit gap wording) is cheaper and should be preferred. |
| Unexercised `skipped`/`chapter_summary` semantics (F-2) | Info | Acceptable for S1 dry run. A later dry run with a real all-N/A chapter should be included only if needed to validate denominator behavior. |
| Unexercised `blocked` status (F-3) | Info | Acceptable. The dry run intentionally chose a clean candidate. Blocked semantics should be exercised when fallback candidates are reintroduced after source category recovery. |
| Unexercised `na_reason` (F-4) | Info | Acceptable. Will be exercised when a dimension is genuinely N/A for a fund type (e.g., `evidence_traceability` for a chapter with no applicable facts). |
| FOF data_gap | Known | Carried forward from S0; not a new finding. Requires pure FOF or taxonomy gate. |
| Fallback upstream categories | Known | Carried forward from S0; not a new finding. Requires source reliability evidence. |

## Validation

Commands run independently:

```text
git check-ignore -v reports/scoring-runs/s1-dry-run-20260525/ reports/scoring-runs/s1-dry-run-20260525/manifest.json reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl reports/scoring-runs/s1-dry-run-20260525/summary.md
cat reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl
wc -l reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl
cat reports/scoring-runs/s1-dry-run-20260525/manifest.json
```

Results:
- `git check-ignore -v`: all four paths covered by `.gitignore:22:reports/scoring-runs/`.
- JSONL: 2 valid JSON records, both parse correctly.
- `wc -l`: 2 records, matching the evidence document claim.
- `manifest.json`: valid JSON, confirms excluded fallback candidates and FOF data_gap.

Cross-checked `observed_ref` at `golden-answer-prefill-reviewed.md:36` — confirmed the row reads "当前 slice 不处理" for `turnover_rate`.
Cross-checked `evidence_anchor_refs` at `golden-answer-prefill-reviewed.md:37` — confirmed the row contains manager_holding data from 年报2024 §9.

## Required Fixes Before Controller Acceptance

No blocking fixes required. F-1 should be dispositioned by the controller (accept `data_extraction`, switch to `chapter_contract`, or defer to later gate). F-2 through F-4 are informational and expected for a minimal dry run.

## Recommendation

**Proceed to controller judgment.** The dry run demonstrates that the accepted S1 schema can localize one narrow pass and one material issue to fund, chapter, dimension, field, evidence refs, data_gap refs, source boundary, and next gate. Denominator semantics are preserved, unsafe fallback/FOF candidates are excluded, and all non-goals are respected.

The controller should specifically disposition F-1 (turnover `next_gate_recommendation`) and confirm whether the unexercised `skipped`/`blocked`/`na_reason` semantics are acceptable for this gate or require a supplementary dry run.
