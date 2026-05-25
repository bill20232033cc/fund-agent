# Release Maintenance Report-Quality Baseline S1 Dry-Run Evidence — MiMo Review

> Date: 2026-05-25
> Reviewer: AgentMiMo
> Gate: `report-quality-baseline S1 dry-run evidence collection`
> Reviewed artifact: `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md`
> Ignored outputs inspected but not tracked: `reports/scoring-runs/s1-dry-run-20260525/manifest.json`, `score-records.jsonl`, `summary.md`

## Step Self-Check

- Truth sources read: `AGENTS.md`; `docs/design.md` §5.4, §5.4.1, §5.4.2, §5.4.3, §6.1, §6.5; `docs/implementation-control.md` Startup Packet / Next Entry Point / Open Residuals / Active Gate Ledger.
- Accepted chain read: S0 corpus-selection evidence and controller judgment; accepted S1 score-schema fixture draft and controller judgment.
- Boundary: this is a review of an S1 dry-run evidence artifact. No source code, tests, renderer, FQ0-FQ6, Host/Agent package, `dayu.host`, `dayu.engine`, PR, push, commit, or fixture promotion.

## Verdict

**PASS_WITH_FINDINGS**

The dry-run evidence artifact satisfies its gate requirements: it uses accepted S1 schema core fields, produces at least one narrow `pass` and one localized `issue` record, preserves denominator semantics, excludes unsafe fallback/FOF candidates, and does not promote fixtures or enter S2. The document correctly scopes `004393/chapter_3/manager_holding` as a narrow pass and does not claim whole-chapter or durable-baseline status. Four minor findings are identified below, none of which block acceptance.

## Findings

### F-1 [minor] Validation does not inspect actual JSONL record content

**Location**: §Validation, lines 128-149

The Validation section runs `jq -c .` and `python -m json.tool` to confirm JSONL/JSON structural validity, and `wc -l` to confirm 2 records. It also runs `rg` to confirm schema field names exist in the tracked Markdown artifact. However, no command extracts or checks that the two JSONL records under `reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl` actually contain the required core fields (`corpus_id`, `fund_code`, `chapter_id`, `dimension`, `status`, `issues`, etc.) or that field values match the prose description.

This means the tracked artifact asserts schema compliance by prose description, while the actual schema-shaped evidence (the ignored JSONL) is validated only for JSON syntax, not field presence or value correctness.

**Impact**: Low. The dry-run is evidence collection, not executable validation. The prose description of the two records is sufficiently detailed to reconstruct the intended JSONL content. However, adding a `jq` or `python -c` command that extracts key fields from the JSONL and confirms them would strengthen the evidence chain.

**Recommendation**: Non-blocking. Future dry runs should add a content-level check, e.g. `jq -c '.status, .dimension, .chapter_id, .fund_code' reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl`, to show the actual records match the prose.

### F-2 [minor] `data_gap_refs` naming convention is not explicitly defined in the S1 schema draft

**Location**: §Localized Issue Rationale, line 83

The issue record uses `data_gap_refs=["gap:004393.2024.turnover_rate.not_reviewed_in_current_slice"]`. The S1 schema draft (`release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md`) defines `data_gap_refs` as "List of data gap ids" but does not define a canonical naming convention for gap ids. The dry-run uses a structured `gap:{fund}.{year}.{field}.{reason}` format, which is reasonable but not anchored in the accepted schema.

**Impact**: Low. The format is self-documenting and consistent within this dry run. If a later gate formalizes gap id naming, this record should be updated to match.

**Recommendation**: Non-blocking. Note this as a naming convention candidate for S2 implementation or the next schema revision.

### F-3 [minor] Tracked artifact validation uses `rg` against the Markdown, not against the ignored JSONL

**Location**: §Validation, lines 133-134

The first `rg` command confirms that accepted schema core fields are present in the tracked Markdown artifact (`docs/reviews/...s1-dry-run-evidence-20260525.md`). This proves the prose document mentions the fields, but does not prove the ignored JSONL records use them. This is related to F-1 but is a distinct observation about the validation approach.

**Impact**: Low. The tracked Markdown is the authoritative evidence artifact for this gate; the ignored JSONL is scratch. Validating the Markdown for field-name presence is the correct focus for a tracked artifact gate.

**Recommendation**: Non-blocking. Acknowledge that the tracked Markdown is the reviewed artifact and the ignored JSONL is supplementary scratch only.

### F-4 [info] No real all-N/A chapter exercised for `skipped` / `chapter_summary` semantics

**Location**: §Denominator / N/A / Skipped / Chapter Summary Semantics, line 93; §Open Gaps / Residual Risks, line 125

The document explicitly acknowledges this gap: "No real all-N/A chapter was emitted; `chapter_summary` / `skipped` semantics are documented but not exercised as a JSONL record." This is appropriate for a minimal dry run using a single fund with applicable dimensions.

**Impact**: None for this gate. The semantics are correctly documented and consistent with the S1 schema draft.

**Recommendation**: Informational only. A later dry run should exercise this if needed, but it does not block S1 evidence acceptance.

## Review Lens Results

### 1. Dry-run uses accepted S1 schema core fields and produces localized records

**PASS.** The "Schema Fields Used" section (lines 37-43) lists all accepted core fields from the S1 schema draft. The two records (pass and issue) are described with complete field sets. The validation confirms `jq` and `json.tool` pass on the JSONL, and `rg` confirms field names in the tracked artifact.

### 2. `004393` / `chapter_3` / `manager_holding` pass is narrow, not whole-chapter

**PASS.** The "Pass Record Rationale" section (lines 53-66) explicitly states: "It does not claim the whole chapter passes, does not claim report-quality scoring is implemented, and does not promote the row to a durable baseline." The `evidence_anchor_refs` correctly point to the specific reviewed row at `golden-answer-prefill-reviewed.md:37` and `年报2024 §9 page-63 page-63-table-2 manager_holding`.

### 3. `turnover_rate` issue is based on reviewed evidence with correct field/chapter/dimension/data_gap/next_gate

**PASS.** The issue record (lines 69-84) is based on the reviewed row at `golden-answer-prefill-reviewed.md:36`, which explicitly marks `turnover_rate` as "当前 slice 不处理". The field is correctly localized to `turnover_rate`, `chapter_3`, `fact_coverage` dimension, and a data_gap ref. The `next_gate_recommendation=data_extraction` is appropriate because the row indicates the field is not currently handled (an extraction gap), not that the chapter contract should be revised. The document also acknowledges (line 122) that the reviewer should confirm whether `data_extraction` or `chapter_contract` is the better next gate, which is correct uncertainty disclosure.

Cross-reference: the S1 schema draft example (line 212) says `data_extraction` if turnover is required by the chapter claim; otherwise `chapter_contract`. The claim `chapter_3_manager_consistency_say_vs_do` is a core active-fund consistency claim where turnover evidence is expected, supporting `data_extraction`.

### 4. Denominator / N/A / skipped / chapter_summary semantics are self-consistent; no invalid records emitted

**PASS.** The semantics table (lines 88-93) correctly defines:
- `pass` and `issue`: included in applicable denominator.
- `blocked`: not emitted because identity, type-slot, and reviewed-row refs were sufficient.
- `N/A`: not used because the selected chapter has applicable dimensions.
- `skipped`: only valid for all-N/A chapter summaries with `dimension=chapter_summary`.
- `chapter_summary`: not emitted because `004393` chapter 3 has applicable `pass` and `issue` records.

No invalid `skipped` or `chapter_summary` JSONL record is produced. The semantics are consistent with the S1 schema draft (lines 111-123).

### 5. Ignored outputs are in `reports/scoring-runs` and git-ignored; tracked artifact does not promote JSON fixtures

**PASS.** `git check-ignore -v` confirms `.gitignore:22:reports/scoring-runs/` covers the directory and all three output files. The tracked artifact is a Markdown file under `docs/reviews/`, not a JSON fixture. No fixture promotion language appears anywhere in the document.

### 6. Fallback candidates `110020`/`017641`/`017970` and FOF `data_gap` are excluded from durable baseline

**PASS.** The "Excluded Fallback Candidates" section (lines 97-103) explicitly excludes all three candidates with the correct reason: `unknown_upstream_failure_category`. The "FOF Data_Gap" section (lines 105-107) correctly notes that `007721` and `017970` are classified as `qdii_fund`, not pure `fof_fund`, and FOF remains unrepresented. Both are consistent with S0 controller judgment decisions.

### 7. Non-goals are not violated

**PASS.** The document scope header (line 6) explicitly excludes renderer, FQ0-FQ6, Host/Agent, `dayu.host`, `dayu.engine`, PR, push, commit, durable baseline, and fixture promotion. None of these appear in the artifact content.

## Open Residuals

| Residual | Owner / gate | Required handling |
|---|---|---|
| JSONL content-level validation not performed | Future dry runs / S2 | Add `jq` or `python -c` commands to verify field presence in ignored JSONL records |
| `data_gap_refs` naming convention not formalized | S2 schema implementation | Define canonical gap-id format when schema becomes code |
| `turnover_rate` next gate (`data_extraction` vs `chapter_contract`) depends on chapter-claim applicability | Reviewer / controller | Confirm `data_extraction` is correct for the `manager_consistency_say_vs_do` claim; document acknowledges this |
| No real all-N/A chapter exercised | Later dry run if needed | Exercise `skipped` / `chapter_summary` JSONL record if a real all-N/A chapter is available |
| Fallback upstream failure categories remain unknown | Source reliability evidence gate | Recover category or keep candidates excluded before durable baseline |
| FOF remains unrepresented | Fund-type taxonomy gate | Find pure `fof_fund` or open QDII-FOF precedence gate |

## Required Fixes Before Controller Acceptance

None. All findings are minor or informational. The artifact satisfies its gate requirements.

## Recommendation

**Recommend proceeding to controller judgment.** The dry-run evidence artifact demonstrates that the accepted S1 schema can localize one narrow `pass` and one material `issue` to fund, chapter, dimension, field, evidence refs, data_gap refs, source boundary, and next gate, while preserving denominator semantics and excluding unsafe fallback/FOF candidates. The four minor findings do not block acceptance and can be addressed in future dry runs or S2 implementation.
