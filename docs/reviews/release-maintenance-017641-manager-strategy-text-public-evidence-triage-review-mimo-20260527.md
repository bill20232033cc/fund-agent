# 017641 Manager Strategy Text Public Evidence Triage — Review (AgentMiMo)

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Gate: `017641 manager_strategy_text public-only evidence triage gate`
> Artifact under review: `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-20260527.md`
> Accepted plan/judgment: `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-controller-judgment-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## 1. Command Fidelity

Evidence artifact claims 4 commands all exited 0. Independent verification:

| Command | Claimed exit | Verified exit | Output files exist |
|---|---:|---:|---|
| `extraction-snapshot` | 0 | 0 (accepted; ignored reports dir present) | `snapshot.jsonl`, `summary.md`, `errors.jsonl` ✓ |
| `extraction-score` | 0 | 0 (accepted; ignored reports dir present) | `score.json`, `score.md`, `golden_set.json` ✓ |
| `quality-gate` | 0 | 0 (accepted; ignored reports dir present) | `quality_gate.json`, `quality_gate.md` ✓ |
| `git diff --check` | 0 | 0 (independently re-run) | no whitespace errors ✓ |

**Result**: PASS. All 3 public CLI commands and `git diff --check` executed and exited 0.

---

## 2. Public-Only Discipline

- Only `uv run fund-analysis` public CLI commands and `git diff --check` were used.
- No direct PDF, cache, source-helper, or private API access.
- Generated outputs are under ignored `reports/extraction-snapshots/` path only.
- No code, renderer, FQ0-FQ6, Service/CLI, source strategy, FundDocumentRepository, Host/Agent/dayu, docs/design.md, or docs/implementation-control.md changes.
- `git diff --name-only HEAD` returns empty; no uncommitted changes.

**Result**: PASS.

---

## 3. Source Provenance Tuple

The evidence artifact lists 10 fields matching the accepted complete eligible fallback tuple. Independent verification against `snapshot.jsonl` row 0 (first row for `017641`):

| Field | Accepted | snapshot.jsonl | Match |
|---|---|---|---|
| `fund_code` | `017641` | `017641` | yes |
| `report_year` | `2024` | `2024` | yes |
| `classified_fund_type` | `qdii_fund` | `qdii_fund` | yes |
| `source_strategy` | `primary_then_fallback` | `primary_then_fallback` | yes |
| `resolved_source_name` | `eastmoney` | `eastmoney` | yes |
| `fallback_used` | `true` | `true` | yes |
| `primary_failure_category` | `unavailable` | `unavailable` | yes |
| `fallback_eligibility` | `eligible` | `eligible` | yes |
| `source_provenance_status` | `complete` | `complete` | yes |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `fallback_used_primary_failure_category_eligible` | yes |

**Result**: PASS. Tuple matches. No stop condition.

---

## 4. Field-Level Status (`manager_strategy_text`)

### 4a. snapshot.jsonl row

| Field | Artifact claim | Actual value | Match |
|---|---|---|---|
| `field_group` | `manager` | `manager` | yes |
| `field_name` | `manager_strategy_text` | `manager_strategy_text` | yes |
| `extraction_mode` | `missing` | `missing` | yes |
| `value_present` | `false` | `False` | yes |
| `anchor_present` | `false` | `False` | yes |
| `section_id` / `page` / `table_id` / `row_id` | `null` / `null` / `null` / `null` | `None` / `None` / `None` / `None` | yes |
| `comparable_values` | `{}` | `{}` | yes |
| `note` | `§4 未披露可规则化抽取的投资策略/后市展望` | `§4 未披露可规则化抽取的投资策略/后市展望` | yes |

### 4b. score.json field_scores

| Metric | Artifact claim | Actual (score.json field_scores) | Match |
|---|---|---|---|
| `records` | 1 | 1 | yes |
| `covered_records` | 0 | 0 | yes |
| `traceable_records` | 0 | 0 | yes |
| `coverage_rate` | 0.0 | 0.0 | yes |
| `traceability_rate` | 0.0 | 0.0 | yes |
| `status` | `fail` | `fail` | yes |
| `priority` | `P0` | `P0` | yes |

### 4c. score.json fund_scores (017641)

| Metric | Artifact claim | Actual (score.json fund_scores[0]) | Match |
|---|---|---|---|
| `p0_status` | `fail` | `fail` | yes |
| `p1_status` | `fail` | `fail` | yes |
| `status` | `fail` | `fail` | yes |
| `p0_failed_fields` | `manager_strategy_text` | `["manager_strategy_text"]` | yes |
| `p1_failed_fields` | `turnover_rate`, `holdings_snapshot` | `["turnover_rate", "holdings_snapshot"]` | yes |

**Note**: The evidence artifact presents fund-level fields (`p1_status`, `status`, `p0_failed_fields`, `p1_failed_fields`) under a section labeled "Fund-level score status" with source "score.json / score.md". In `score.json`, these fields exist inside the `fund_scores` list item, not at the top level. The top-level `score.json` only has `p0_status`. The artifact's attribution is technically imprecise but the values are correct. See Finding F1.

**Result**: PASS. Field-level status is genuinely derived from snapshot.jsonl / score.json / score.md, not just summary.

---

## 5. FQ2/FQ3/FQ2F Issue Records

Independent verification against `quality_gate.json`:

| rule_code | severity | field_name | priority | coverage_rate | traceability_rate | Message (abbreviated) | Match |
|---|---|---|---|---|---|---|---|
| `FQ2` | `block` | `manager_strategy_text` | `P0` | 0.0 | 0.0 | P0 必须字段 coverage/traceability 未达标 | yes |
| `FQ3` | `block` | `manager_strategy_text` | `P0` | 0.0 | 0.0 | P0 必须字段 证据锚点不足 | yes |
| `FQ2F` | `block` | `null` | `P0` | `null` | `null` | 基金 017641 存在 P0 字段失败 | yes |

Additional issues (P1 warnings, FQ0 info, FQ4 warn) also match quality_gate.json.

`errors.jsonl` is 0 bytes — confirmed. No failed-fund records in extraction.

**Result**: PASS. Exact FQ2/FQ3/FQ2F issue records support the accepted blocking cluster. No new unexplained P0/P1 outside the accepted cluster. P2 `nav_data` fail is outside the P0/P1 scope and does not constitute a new blocking finding.

---

## 6. Terminal Classification

Classification: `disclosure_data_gap_not_baseline_ready`

Evidence chain:
- `snapshot.jsonl`: `extraction_mode=missing`, no value, no anchor, note says §4 未披露可规则化抽取的投资策略/后市展望
- `score.json` / `score.md`: P0 coverage 0.0, traceability 0.0, status fail
- `quality_gate.json`: FQ2/FQ3/FQ2F P0 block confirmed
- Provenance: complete eligible fallback — not a source-provenance blocker
- Public outputs do not prove relevant disclosure exists and was missed by extractor
- Current design still treats `manager_strategy_text` as P0; no policy/taxonomy reclassification without a separate design plan

**Result**: PASS. Terminal classification is supported by public evidence. No promotion, baseline, golden, or fixture.

---

## 7. Promotion Disposition

`promotion_disposition=not_promoted`. No baseline, golden, fixture, or promotion artifacts created. No code/test/design/control changes. No GitHub mutation.

**Result**: PASS.

---

## 8. Non-Goal Compliance

No changes to: code, renderer, FQ0-FQ6, Service/CLI, source strategy, FundDocumentRepository, Host/Agent/dayu, docs/design.md, docs/implementation-control.md.

**Result**: PASS.

---

## Findings

### F1: Provenance tuple source attribution imprecise (non-blocking)

**Severity**: informational

**Evidence**: The evidence artifact's "Source Provenance Tuple Check" section presents provenance fields without explicitly stating which file they come from. The "Field-Level Status" section header says "Source: public `snapshot.jsonl`, `score.json`, and `score.md`." However, the full provenance tuple (all 10 fields including `source_strategy`, `fallback_used`, `primary_failure_category`, etc.) only exists in `snapshot.jsonl` — it does not exist in `score.json` top-level or in `score.md`. The `score.json` top-level keys are: `snapshot_path`, `source_csv`, `thresholds`, `field_count`, `fund_count`, `status_counts`, `p0_status`, `field_scores`, `fund_scores`, `fund_quality`, `field_applicability_decisions`, `score_applicability_issues`, `failed_funds`, `golden_set`, `correctness` — no provenance fields.

**Impact**: None on data correctness. The provenance tuple values are accurate and independently verified against snapshot.jsonl. The evidence worker likely read snapshot.jsonl to construct the provenance check, which is the correct source.

**Controller action**: No action required. If a future evidence worker repeats this gate, it should explicitly note snapshot.jsonl as the provenance source for clarity.

### F2: Fund-level score field location imprecise (non-blocking)

**Severity**: informational

**Evidence**: The evidence artifact presents `p1_status`, `status`, `p0_failed_fields`, `p1_failed_fields` under "Fund-level score status" with source "score.json / score.md". In `score.json`, these fields exist inside the `fund_scores` list item (not at the top level). The top-level `score.json` only has `p0_status=fail`; the other fund-level fields (`p1_status`, `status`, `p0_failed_fields`, `p1_failed_fields`) are at `score.json.fund_scores[0]` and in `score.md` Fund Scores table.

**Impact**: None on data correctness. All values are accurate.

**Controller action**: No action required. Minor documentation precision issue.

---

## Verdict

**PASS_WITH_FINDINGS**

Two informational findings (F1, F2) — both are source attribution precision issues with no impact on data correctness, terminal classification, or gate outcome. No blocking findings. No new unexplained P0/P1 outside the accepted cluster. The terminal classification `disclosure_data_gap_not_baseline_ready` and `promotion_disposition=not_promoted` are supported by public evidence.

No re-review required. Controller may accept as-is.
