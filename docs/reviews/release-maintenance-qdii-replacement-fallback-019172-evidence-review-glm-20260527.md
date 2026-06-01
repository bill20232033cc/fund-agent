# QDII Replacement Fallback 019172 Evidence — Review (AgentGLM)

> Date: 2026-05-27
> Reviewer: AgentGLM
> Gate: `QDII replacement fallback 019172 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-20260527.md`
> Verdict: **PASS**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement fallback 019172 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 019172 evidence gate` |
| Evidence artifact gate | `QDII replacement fallback 019172 evidence gate` |

This review confirms the evidence follows the Startup Packet next entry point, not a gate switch.

## Review Against Criteria

### Criterion 1: Only 019172 / 2024 bounded public evidence

**Confirmed.**

- Section 2 candidate identity is `019172` / `2024` only.
- Section 9 explicitly confirms: did not run `096001`, `040046`, `017641`, or any later fallback candidate.
- Section 9 confirms: did not run `analyze` or `checklist`.
- No reference to other candidates' evidence, data, or quality results is used to justify `019172` conclusions.

### Criterion 2: Follows Startup Packet next entry point, not gate switch

**Confirmed.**

- Section 1 states: "This evidence run follows the Startup Packet next entry point. It is not a gate switch."
- The artifact gate (`QDII replacement fallback 019172 evidence gate`) matches the Startup Packet next entry point.
- Latest accepted checkpoint is `dafc72f docs: accept qdii fallback 019172 evidence plan`, consistent with the accepted plan controller judgment.

### Criterion 3: Provenance is read from generated public summary.md + snapshot.jsonl, not stdout-only

**Confirmed.**

- Section 5 table records both files as existing and read.
- Every provenance field in the tuple includes a "Public source" column citing `snapshot.jsonl` and/or `summary.md`.
- I independently verified `snapshot.jsonl` contains all claimed provenance fields: `source_provenance_schema_version=repository_source_provenance.v1`, `source_strategy=primary_then_fallback`, `resolved_source_name=eastmoney`, `fallback_used=true`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_provenance_reason=fallback_used_primary_failure_category_eligible`.

### Criterion 4: Provenance interpretation is correct and fail-closed categories absent

**Confirmed.**

- `primary_failure_category=unavailable` — verified from `snapshot.jsonl`.
- `fallback_eligibility=eligible`, `source_provenance_status=complete` — verified.
- No `schema_drift`, `identity_mismatch`, or `integrity_error` in any generated public output — verified.
- Interpretation that provenance is eligible under `unavailable` + `eligible` + `complete` is correct per the accepted plan's eligibility criteria.

### Criterion 5: Score/quality run only after eligible provenance

**Confirmed.**

- Section 4 command order: snapshot (exit 0) → score (exit 0) → quality-gate (exit 0).
- Section 5 establishes provenance eligibility before Section 6 records score and quality results.
- Structural ordering is correct.

### Criterion 6: Quality evidence records quality_gate_status, issue_count, P0/P1, manager_strategy_text, FQ4, FQ0/FQ5 consistently

**Confirmed.**

| Recorded field | Evidence value | Verified against generated output |
|---|---|---|
| `quality_gate_status` | `block` | `quality_gate.json` status=block; `quality_gate.md` status=block |
| `issue_count` | 9 | `quality_gate.json` issues list length=9; `quality_gate.md` shows 9 rows |
| P0 block issues | FQ2/FQ3 `manager_strategy_text`, FQ2F `019172` P0 | `quality_gate.md` rows match |
| P1 warn issues | FQ2 `turnover_rate`/`holdings_snapshot`/`share_change`, FQ2F `019172` P1 | `quality_gate.md` rows match |
| `manager_strategy_text` | P0, fail, 0.0%/0.0%, extraction_mode=missing | `snapshot.jsonl` confirmed extraction_mode=missing, value_present=false, anchor_present=false |
| FQ4 | block, 35.7% > 35.0% | `quality_gate.md` FQ4 row matches; 5/14 = 35.71% |
| FQ0 | info, not configured | `quality_gate.md` FQ0 row matches |
| FQ5 | resolved, `海外股票类` matched `qdii_fund` | `quality_gate.md` FQ5 row matches |

All values cross-verified against generated public outputs.

### Criterion 7: Terminal classification follows accepted matrix

**Confirmed.**

- Terminal classification: `quality_blocked_after_provenance`.
- Promotion disposition: `not_promoted`.
- The accepted plan matrix row for "Provenance eligible, quality P0 block on `manager_strategy_text`" maps to `quality_blocked_after_provenance` — correct.
- FQ4 is also blocking (`35.7% > 35.0%`) but P0 fails first; both blockers are recorded. Classification is materially correct.

### Criterion 8: false_positive_suspicion=true has public evidence basis and does not bypass block

**Confirmed.**

- Evidence basis: `snapshot.jsonl` for `index_profile` records `extraction_note: "非指数基金不适用指数画像"` while `classification_basis` includes "指数基金身份或策略证据" with explicit passive-index strategy text. This is a concrete contradiction in generated public output.
- Evidence basis: `snapshot.jsonl` for `manager_strategy_text` records `extraction_mode=missing` and note about §4 disclosure gap. Verified from generated file.
- Section 8 explicitly states: "This suspicion does not change the accepted policy outcome." Terminal classification remains `quality_blocked_after_provenance`.
- No code, extractor, taxonomy, renderer, FQ0-FQ6, Service/CLI, golden, or baseline changes are authorized. Correct.

### Criterion 9: Scratch reports ignored; no forbidden changes

**Confirmed.**

- Section 9 lists all exclusion confirmations.
- Generated outputs under `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/` are `.gitignore`-covered.
- Pre-existing untracked files listed and declared untouched.

### Criterion 10: git diff --check passed

**Confirmed.**

- Evidence Section 10 records exit code 0.
- I independently ran `git diff --check` and it passed with no output.

## Findings

No blocking or material findings.

### Low Findings

**L1: summary.md 16 records vs score.md 14 fields discrepancy**

`summary.md` lists 16 field coverage rows while `score.md` counts 14 scored fields. This is the same discrepancy pattern accepted as DS low in the `040046` evidence review, caused by applicability-excluded fields (`index_profile`, `tracking_error`) present in snapshot but excluded from scoring. The evidence uses score's `field_count=14` for FQ4 calculation, which is correct. No terminal classification impact.

## Verdict

**PASS**. The evidence artifact is complete, internally consistent, follows the accepted plan, reads provenance from generated public files, correctly interprets eligible provenance before quality, correctly classifies as `quality_blocked_after_provenance` / `not_promoted`, and records false-positive suspicion with public evidence basis without bypassing the block.
