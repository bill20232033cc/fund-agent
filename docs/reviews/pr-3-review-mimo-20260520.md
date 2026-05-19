# PR 3 Deep Review — P4 Quality Closed Loop

> **Reviewer**: AgentMiMo
> **Date**: 2026-05-20
> **PR**: https://github.com/bill20232033cc/fund-agent/pull/3
> **Base**: main
> **Head**: p4-quality-closed-loop (commit `0c955fd`)
> **Scope**: P4 quality closed loop implementation and PR inclusion set only

---

## 1. Validation Commands

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/ -q` | `171 passed` in 0.73s |
| `.venv/bin/python -m ruff check .` | All checks passed |
| `git diff --check main...HEAD` | No whitespace errors |
| Excluded items grep | No excluded items found in PR diff |
| `golden-answer.json` presence | Confirmed in PR |

---

## 2. Key Behavior Verification

### 2.1 score.json contains field_scores, fund_scores, golden_set, correctness

**PASS.** `extraction_score.py:_score_json_payload()` (lines 1139-1151) emits all four top-level keys. `ExtractionScoreResult` dataclass (lines 246-273) carries all four as typed fields. Test `test_run_extraction_score_writes_score_outputs` asserts presence of `fund_scores`, `correctness`, and `golden_set` in the written JSON.

### 2.2 quality gate consumes score.json and blocks P0 field fail, per-fund P0 fail, and correctness mismatch

**PASS.** `quality_gate.py:_evaluate_score_payload()` (lines 144-174) processes `field_scores`, `fund_scores`, and `correctness`:

- P0 field fail → `FQ2/block` (lines 281-293)
- Per-fund P0 fail → `FQ2F/block` (lines 323-356)
- Correctness mismatch → `FQ1/block` (lines 222-258)

Four dedicated tests cover each path:
- `test_run_quality_gate_blocks_failed_p0_fields`
- `test_run_quality_gate_blocks_single_fund_p0_failure_even_when_field_aggregate_passes`
- `test_run_quality_gate_blocks_correctness_mismatch_as_fq1`
- `test_run_quality_gate_keeps_fq0_info_without_golden_answer`

### 2.3 Strict golden answer JSON loaded through explicit golden_answer_path; skipped/unavailable rows excluded from denominator

**PASS.** `extraction_score.py:compare_snapshot_correctness()` (lines 504-565) accepts explicit `golden_answer_path` parameter. When `None`, returns `status=unavailable` with zero counts. Skipped records only increment `skipped_records` (line 552), never enter `comparable_records` denominator (lines 546-548). Unavailable records (snapshot does not expose the golden sub-field) also excluded from denominator. Test `test_compare_snapshot_correctness_perfect_match_and_skipped_denominator` asserts `comparable_records=1`, `skipped_records=1`, `accuracy_rate=1.0`.

### 2.4 style_positioning belongs to product_profile, not manager_strategy_text

**PASS.** `profile.py:_build_product_profile()` (lines 346-383) extracts `style_positioning` and places it inside the `product_profile` value dict (line 376). Renderer at line 279 reads `style_positioning` from `profile` (product_profile), while `strategy_summary` is read from `strategy` (manager_strategy_text) — the two are cleanly separated.

### 2.5 Service/UI remain thin; domain logic stays in fund capability

**PASS.** `extraction_score_service.py` is 92 lines: validates request shape (suffix checks) and delegates to `run_extraction_score()`. CLI commands in `cli.py` are thin Typer wrappers that construct request objects and call service methods. All scoring, golden answer parsing, quality gate evaluation, and correctness comparison logic lives in `fund_agent/fund/`.

### 2.6 Control docs say ready-to-open-draft-PR / draft PR gate; residual risks have owners

**PASS.** `implementation-control.md` line 35-36: current gate = `ready-to-open-draft-PR`, next gate = `draft PR gate`. `implementation-control-p4.md` line 5: status = `ready-to-open-draft-PR`. Residual risks P4-R8 (quality gate analyze integration), P4-R9 (FQ rule branches), RR-15, RR-16 all have explicit deferred owner slices.

---

## 3. Scope Hygiene

**PASS.** `git diff main...HEAD --name-only | grep -E '(reports/extraction-snapshots/|scripts/|launchd/|report-004393|p2-full-retrospective|pr-1-review-mimo)'` returns no matches. All excluded items confirmed absent from PR.

Included items match `docs/reviews/p4-pr-scope-hygiene-reconciliation-20260520.md`: `reports/golden-answers/*` as curated correctness fixture is present in PR.

---

## 4. Findings

### F-LOW-1: Large volume of review artifacts in PR diff

**Severity**: LOW (info)
**Evidence**: 18 new review markdown files under `docs/reviews/` are included in the PR (~2,100 lines of the +6,847 total). These are within the accepted PR scope per `p4-pr-scope-hygiene-reconciliation-20260520.md`, but they inflate the diff and make PR review harder.
**Recommendation**: Accepted for this PR. Future PRs could consider batching review artifacts into a single squashed summary or excluding intermediate review artifacts.

### F-LOW-2: golden-answer.json is 2,023 lines of curated fixture

**Severity**: LOW (info)
**Evidence**: `reports/golden-answers/golden-answer.json` is 2,023 lines. It is a curated correctness fixture with `schema_version`, `funds`, and flat `records` arrays. Structure validated against `golden_answer.py:load_golden_answer_json()` schema expectations.
**Recommendation**: Accepted. This is the correctness ground truth for the quality closed loop.

---

## 5. Residual Risks (Accepted, Not Blockers)

| ID | Risk | Owner |
|---|---|---|
| P4-R8 / RR-15 | quality gate `analyze` integration deferred | quality gate integration slice |
| P4-R9 | FQ1 App category conflict, FQ4, FQ5 branches not implemented | quality gate rules slice |
| RR-16 | correctness denominator expansion (only `classified_fund_type.fund_type` currently comparable) | snapshot sub-field exposure slice |

---

## 6. Recommendation

**PASS** — PR 3 is ready for draft-PR-pass.

All six key expected behaviors verified. 171 tests pass. Lint clean. No whitespace errors. No excluded items leaked into PR. No blocking findings. Three accepted residual risks all have explicit deferred owners documented in control docs.

---

> **Artifact path**: `docs/reviews/pr-3-review-mimo-20260520.md`
