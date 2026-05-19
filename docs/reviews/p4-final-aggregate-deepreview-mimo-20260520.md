# P4 Final Aggregate Deepreview - AgentMiMo - 2026-05-20

## Verdict

**PASS with 1 blocking finding (fixable) and 5 non-blocking findings.**

The blocking finding is `ruff format --check` failure on 3 P4 source files. This must be fixed before draft PR. All P4 functional contracts, layer boundaries, and acceptance criteria are met.

---

## Commands Run

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/fund/extractors/test_profile.py tests/fund/extractors/test_manager_ownership.py tests/fund/analysis/test_consistency_check.py tests/fund/template/test_renderer.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py -q` | **70 passed** in 0.48s |
| `.venv/bin/python -m ruff check` (8 P4 source files) | **All checks passed** |
| `.venv/bin/python -m ruff format --check` (8 P4 source files) | **FAIL**: `extraction_snapshot.py`, `profile.py`, `renderer.py` would be reformatted |
| `git diff --check` | **passed** (no whitespace errors) |
| `python3 -c "import json; ..."` on `reports/golden-answers/golden-answer.json` | Valid: `schema_version=fund-agent.golden-answer.v1`, `fund_count=6`, `record_count=121` |
| `grep -c "fund-analysis" README.md` | 25 references, 0 `zhixing` references |
| `ls docs/implementation-control-p4.md` | Exists |
| `ls docs/golden-answer-template.md` | Exists |

---

## Findings

### F1 [BLOCKING] ruff format violation on 3 P4 source files

**Severity**: BLOCKING (must fix before draft PR)
**Files**: `fund_agent/fund/extraction_snapshot.py`, `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/template/renderer.py`
**Evidence**: `.venv/bin/python -m ruff format --check` reports "Would reformat" on all 3 files.
**Impact**: PR CI would fail if ruff format check is enabled. Also contradicts correctness slice code review acceptance which included "ruff format check passed" -- these files may have been modified after that acceptance.
**Fix**: Run `.venv/bin/python -m ruff format` on these 3 files.

### F2 [MEDIUM] Missing @pytest.mark.asyncio in test_golden_prefill.py

**Severity**: MEDIUM
**File**: `tests/fund/test_golden_prefill.py:103`
**Evidence**: `test_run_golden_prefill_writes_prefilled_markdown` is `async def` but lacks `@pytest.mark.asyncio` decorator. All other async test files in the project consistently use this marker. The test currently passes (70 passed), suggesting pytest-asyncio `auto` mode is active, but the inconsistency is a maintenance risk if mode changes.
**Impact**: Test could silently skip if pytest-asyncio mode changes from `auto` to `strict`.
**Owner**: Test hygiene cleanup slice.

### F3 [MEDIUM] Hard dependency on real CSV in unit tests

**Severity**: MEDIUM
**File**: `tests/fund/test_extraction_score.py:141,299`
**Evidence**: `test_run_extraction_score_writes_score_outputs` and `test_select_minimal_golden_set_uses_only_csv_codes_and_excludes_money_market` pass `source_csv=Path("docs/code_20260519.csv")` as a real file path. If the CSV is moved or renamed, these unit tests fail for reasons unrelated to the code under test.
**Impact**: Fragile test coupling to repo file layout.
**Owner**: Test hardening slice (can be deferred; CSV is stable P4 input).

### F4 [MEDIUM] Untested extraction modes "estimated" and "partial"

**Severity**: MEDIUM
**File**: `tests/fund/test_extraction_snapshot.py:314-354`
**Evidence**: `_field()` helper only constructs `extraction_mode="direct"` or `"missing"`. The snapshot schema defines `"estimated"` and `"partial"` as valid modes (control doc section 4.5), but no test exercises these modes in `build_snapshot_records`.
**Impact**: Snapshot mode normalization logic for estimated/partial paths is untested.
**Owner**: Test coverage expansion slice.

### F5 [LOW] Dead code from P4-S3a fix

**Severity**: LOW (informational)
**File**: `fund_agent/fund/extraction_snapshot.py:43,1046-1047`
**Evidence**: `_KNOWN_FAILURE_004393_NOTE` constant and the note injection logic check `classified_fund_type == "index_fund"` for fund 004393. Since P4-S3a fixed classification to `active_fund`, this condition can never be true. The code is harmless but dead.
**Impact**: None; cleanup opportunity.
**Owner**: Cleanup slice.

### F6 [LOW] Confidence validation asymmetry in golden_answer.py

**Severity**: LOW (informational)
**File**: `fund_agent/fund/golden_answer.py:399` vs `golden_answer.py:609`
**Evidence**: JSON loader validates `confidence` without `.lower()` normalization, while Markdown parser normalizes via `.lower()`. Hand-edited JSON with `"High"` would be rejected by the loader. This is defensible strictness (build pipeline always produces lowercase) but could confuse manual editors.
**Impact**: Minor DX friction for manual golden answer editing.
**Owner**: None needed; defensible design choice.

---

## Focus Question Answers

### Q1: Are P4 success signals actually met by current code, tests, docs, and control docs?

**YES.** All P4 acceptance criteria are verified:

| Criterion | Evidence |
|---|---|
| Snapshot generation (P4-S1) | `extraction_snapshot.py` implements 14-field `SnapshotRecord`, outputs `snapshot.jsonl`/`summary.md`/`errors.jsonl` to `reports/extraction-snapshots/<run_id>/`. Tests at `test_extraction_snapshot.py:108,166,225`. |
| Field-level scoring (P4-S2) | `extraction_score.py` computes coverage/traceability with pass=0.90/watch=0.70 thresholds. Outputs `score.json`/`score.md` with `field_scores` and `fund_scores`. Tests at `test_extraction_score.py:30,71,107`. |
| Fund type fix (P4-S3a) | `extractors/profile.py` classifies 004393 as `active_fund`. Tests at `test_profile.py:360,401`. |
| High-impact extractor fixes (P4-S3b) | `manager_ownership.py`, `performance.py`, `holdings_share_change.py` improved. Snapshot/score verified 100% coverage on slice fields. |
| Quality gate skeleton (P4-S4) | `quality_gate.py` blocks P0 fail, warns P1 fail, triggers FQ1/block on correctness mismatch. Tests at `test_quality_gate.py:16,92,135,186`. |
| Per-fund blocking | `fund_scores` in score.json; quality gate FQ2F blocks single-fund P0 fail. Tests at `test_quality_gate.py:92`, `test_extraction_score.py:107`. |
| Golden answer chain | `golden_answer.py` validates strict JSON (schema_version, confidence, source). `golden-answer.json` has 6 funds, 121 records. Tests at `test_golden_answer.py:53,87`. |
| Correctness comparison | `extraction_score.py` compares snapshot-exposed fields against golden answer. FQ1/block on mismatch. Tests at `test_extraction_score.py:193,236`, `test_quality_gate.py:135`. |
| style_positioning contract | Correctly in `product_profile` (section 2), not `manager_strategy_text`. `profile.py:359-371`, `renderer.py:277`. Tests at `test_profile.py:308`, `test_consistency_check.py:59,205`. |

### Q2: Are deferred risks truly non-blocking and assigned to concrete owners?

**YES.** All 6 deferred items from readiness reconciliation have owners:

| Item | Owner | Assessment |
|---|---|---|
| P4-R8: quality gate not attached to `analyze` | `quality gate integration slice` | Non-blocking; skeleton works standalone via CLI. |
| P4-R9: FQ1 App-category branch, FQ4, FQ5 | `quality gate rules slice` | Non-blocking; FQ1 correctness mismatch branch works. |
| RR-16: correctness denominator narrow | `snapshot sub-field exposure slice` | Non-blocking; current 1-field comparison is correct for available data. |
| 016492 duplicate CSV row | user/App source reconciliation | Non-blocking; duplicate is flagged in summary. |
| share_change multi-share-class | future extractor hardening | Non-blocking; current output is usable. |
| Failed funds absent from fund_scores | snapshot failure accounting | Non-blocking; failures are recorded in errors.jsonl. |

None of these are accidentally dropped -- they are explicitly tracked in `implementation-control-p4.md` section 8 risk table and readiness reconciliation deferred items table.

### Q3: Are score.json and quality_gate.json contracts coherent after fund_scores and correctness additions?

**YES.** Verified:
- `score.json` contains `field_scores` (field-level) + `fund_scores` (per-fund) + `golden_set` + `correctness`. All fields match control doc section 5.3.
- `quality_gate.json` consumes `score.json`, evaluates FQ1 (correctness mismatch), FQ2 (field-level P0/P1 fail), FQ2F (per-fund P0/P1 fail). Status aggregation: block > warn > pass.
- Thresholds: pass=0.90, watch=0.70 for both coverage and traceability. Match control doc exactly.
- Field priority mapping: P0 (6 fields), P1 (6 fields), P2 (2 fields). Match control doc section 5.2 exactly.

### Q4: Are layer boundaries respected?

**YES.** Verified:
- **Service layer** (`extraction_score_service.py`, `extraction_snapshot_service.py`, etc.): Thin request/validation/delegation pattern. No domain logic.
- **UI layer** (`cli.py`): All 6 P4 commands construct request, call Service, echo paths. No domain logic.
- **Capability layer** (`fund_agent/fund/`): All domain logic (snapshot, score, golden answer, quality gate, extractors) lives here.
- **No direct filesystem access violations**: CSV/JSONL I/O is explicitly permitted for snapshot/score/golden answer. PDF/cache access goes through `FundDataExtractor`. `renderer.py` consumes structured results only.

### Q5: Do README/control docs match current behavior?

**YES** (with one pre-existing issue):
- `README.md`: Correctly describes `fund-analysis` CLI (25 references, 0 `zhixing`). Accurate installation, usage, and capability descriptions.
- `docs/implementation-control-p4.md`: Status log entries match actual accepted commits and review artifacts.
- `fund_agent/fund/README.md`: Accurate, one minor omission (`section_catalog.py` undocumented in pdf/ section).
- `tests/README.md`: All referenced test files exist, commands are valid.
- `CLAUDE.md`: Describes `zhixing` project (pre-fund-agent design). This is a pre-existing issue not introduced by P4. Not blocking for P4 scope.

### Q6: Is draft PR readiness blocked by worktree scope hygiene?

**PARTIALLY.** Three issues must be resolved before draft PR:
1. **F1 (BLOCKING)**: `ruff format --check` fails on 3 files. Fix: run `ruff format`.
2. **PR inclusion set**: 28 modified files + 30 untracked files. Untracked includes:
   - P4 review artifacts (`docs/reviews/p4-*`, `correctness-*`): Include.
   - Runtime outputs (`reports/`, `report-004393.md`): Exclude from PR.
   - Scripts/launchd (`scripts/`, `launchd/`): Exclude from PR (not P4 scope).
   - Historical reviews (`docs/reviews/p2-full-retrospective-*`, `code-review-20260517-*`): Exclude from PR.
3. **`uv.lock`**: Contains `pytest-cov`/`coverage` lock changes matching `pyproject.toml` dev dependency. Include as separate scope item per readiness reconciliation guidance.

---

## Residual Risks (accepted, non-blocking)

| Risk | Status | Owner |
|---|---|---|
| P4-R8: quality gate not in `analyze` chain | Deferred | quality gate integration slice |
| P4-R9: FQ4/FQ5 rules not implemented | Deferred | quality gate rules slice |
| RR-16: correctness denominator narrow | Deferred | snapshot sub-field exposure slice |
| RR-17: PR scope hygiene | Deferred until F1 fix | controller |
| Real CSV dependency in unit tests | Accepted | test hardening slice |
| Missing asyncio marker in test_golden_prefill | Accepted | test hygiene cleanup |
| Dead code from P4-S3a fix | Accepted | cleanup slice |
| `ruff format` drift on 3 files | **Must fix** | controller |

---

## Recommendation

**PASS.** P4 functional readiness is confirmed. All acceptance criteria are met, contracts are coherent, layer boundaries are respected, deferred risks are tracked with owners, and control docs match current behavior.

**Before draft PR**: Fix F1 (`ruff format` on 3 files) and define PR inclusion set to exclude runtime outputs, scripts, and unrelated historical artifacts.
