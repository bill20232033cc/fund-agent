# P16 Aggregate Deepreview — AgentMiMo（2026-05-22）

## Verdict

**PASS**

P16 从 post-P15 selection 到 P16-S2 resumed golden accepted 的全部实现和文档变更符合设计真源、实施总控和 deterministic MVP 约束。Evidence-to-golden chain 完整，golden 正确性 sound，scope 无越界。

---

## Review Scope

| Commit | Description |
|--------|-------------|
| `f80affc` | docs: accept post-P15 follow-up planning |
| `3dff291` | docs: accept P16 enhanced index evidence plan |
| `9de9bfb` | docs: accept P16 enhanced index evidence |
| `a9faeec` | docs: accept P16 index profile golden plan |
| `179447b` | docs: accept P16 golden blocker |
| `c1005e0` | docs: accept P16 newline normalization plan |
| `974615e` | fix: normalize benchmark text newlines |
| `65ac5a0` | docs: record P16 newline normalization commit |
| `121ad1f` | test: add enhanced index profile golden rows |
| `604e2d9` | docs: record P16 golden rows commit |

P16 artifacts reviewed:

- `docs/reviews/post-p15-follow-up-planning-20260522.md`
- `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md`
- `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md`
- `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md`
- `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md`
- `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md`
- `docs/reviews/p16-s2-code-review-controller-judgment-20260522.md`
- `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md`
- `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-implementation-20260522.md`
- `docs/reviews/p16-s2-1-code-review-controller-judgment-20260522.md`
- `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-resume-20260522.md`
- `docs/reviews/p16-s2-resume-code-review-controller-judgment-20260522.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- `reports/golden-answers/golden-answer.json`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `fund_agent/fund/extractors/profile.py`（normalization code）
- `fund_agent/fund/extractors/models.py`（IndexProfileValue dataclass）
- `fund_agent/fund/extraction_snapshot.py`（comparable sub-fields）
- `tests/fund/test_golden_answer.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/extractors/test_profile.py`

---

## 1. Design / Control Conformance

### 1.1 FundDocumentRepository Boundary

**PASS.** All annual-report access in P16-S1 evidence acquisition used `FundDocumentRepository.load_annual_report()` and `FundDataExtractor.extract()` only. P16-S2 and P16-S2.1 did not access annual reports directly. No Service/UI/Engine bypass was introduced.

### 1.2 Dayu Non-dependency

**PASS.** No Dayu Host/Engine/tool loop/API/runtime/dependency was introduced in any P16 commit. `pyproject.toml` remains clean.

### 1.3 No extra_payload

**PASS.** All parameters are explicitly declared in function signatures. No hidden extra_payload passing was introduced.

### 1.4 Capability Ownership

**PASS.** P16 changes are confined to:
- `fund_agent/fund/extractors/profile.py` — benchmark-path normalization (Capability extractor)
- `reports/golden-answers/` — golden answer artifacts (Capability quality gate input)
- `tests/fund/` — focused tests (Capability test boundary)
- `docs/reviews/` — review artifacts (control record)

No changes to Service, UI, Engine, renderer, or audit layers.

### 1.5 Deterministic MVP Boundaries

**PASS.** P16 preserved all deterministic MVP boundaries:
- No LLM audit or writing introduced
- No Evidence Confirm execution
- No Host/Engine/tool loop
- No external index adapters
- No calculated index series
- No methodology/constituents extraction beyond benchmark_only metadata
- No QDII subtype redesign

---

## 2. Evidence-to-Golden Chain Completeness

### 2.1 P16-S1: Evidence Acquisition

**PASS.** Five enhanced-index candidates (`004194`, `005313`, `017644`, `019918`, `019923`) were evaluated through `FundDocumentRepository` / `FundDataExtractor`. All five matched EID 2024 annual reports with `fallback_used=False`, all classified as `enhanced_index`. `index_profile` benchmark-context evidence accepted for all five. All `tracking_error` evidence correctly blocked (target/limit text and strategy narrative only, no direct observed disclosure). Controller verdict: `PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY`.

### 2.2 P16-S2: Initial Golden Implementation (blocked)

**PASS.** Implementation correctly stopped before golden edits when extractor output for `017644` and `019918` contained embedded newlines differing from accepted expected text. Blocker properly recorded.

### 2.3 P16-S2.1: Newline Normalization

**PASS.** Narrow normalization added in `fund_agent/fund/extractors/profile.py:343-399`:
- `_normalize_benchmark_text()` handles `\r\n`, `\r`, `\n` and adjacent horizontal whitespace
- `_normalize_benchmark_matched_field()` creates new `_MatchedField` (frozen object not mutated)
- Normalization applied to both `benchmark_text` and benchmark anchor note
- Only called in `_build_benchmark()` path (line 577)
- Five required cases verified: `017644` and `019918` normalized correctly; `004194`, `005313`, `019923` unchanged
- Composite semantics preserved: `benchmark_identity_status=composite`, `benchmark_index_name=None`

### 2.4 P16-S2 Resumed: Golden Rows

**PASS.** Exactly 25 planned `index_profile` scalar rows added for five candidates (5 rows each). Strict JSON rebuilt through `golden-build`: `fund_count=11`, `record_count=150`. No embedded newlines in any expected_value.

---

## 3. Golden Correctness / Quality Denominator

### 3.1 Strict JSON

**PASS.** Verified `reports/golden-answers/golden-answer.json`: 11 funds, 150 records total. No embedded newlines in any expected_value. All five enhanced-index candidates have exactly the 5 planned scalar rows.

### 3.2 Comparable Scalar Handling

**PASS.** `IndexProfileValue` is frozen dataclass. `COMPARABLE_SUB_FIELDS_BY_FIELD["index_profile"]` includes: `benchmark_text`, `benchmark_identity_status`, `benchmark_index_name`, `benchmark_index_code`, `methodology_availability`, `constituents_availability`, `source_tier`. For composite benchmarks, `_comparable_scalar()` correctly returns `None` for `benchmark_index_name=None` and `benchmark_index_code=None`, excluding them from the correctness denominator.

### 3.3 Composite No-Synthesis

**PASS.** No `benchmark_index_name` or `benchmark_component_text` golden rows were added for composite candidates. Tests explicitly verify forbidden fields are absent.

### 3.4 Quality FQ1

**PASS.** `tests/fund/test_quality_gate.py` verifies composite scalar mismatch blocks through FQ1. Quality gate correctly consumes comparable values.

### 3.5 Existing 001548 Preservation

**PASS.** `001548` retains 24 records including 4 `index_profile` rows (benchmark_text, benchmark_identity_status, benchmark_index_name, source_tier). Values unchanged from pre-P16 state. `fund_count` correctly grew from 6 to 11; `record_count` correctly grew from 125 to 150.

---

## 4. Scope / Risk — Non-Goals Verification

| Non-goal | Status | Evidence |
|----------|--------|----------|
| `tracking_error` rows | Not added | JSON verification: 0 tracking_error rows for all 5 candidates |
| `benchmark_index_name` rows | Not added for composite | JSON verification: absent for 004194/005313/017644/019918/019923 |
| `benchmark_component_text` rows | Not added | JSON verification: absent for all candidates |
| methodology/constituents detail | Not added | Only `methodology_availability` and `constituents_availability` scalar metadata |
| calculated index series | Not introduced | No new calculation code |
| external adapters | Not introduced | No new adapter code |
| LLM audit | Not introduced | No LLM-related code |
| Evidence Confirm execution | Not introduced | No confirm-related code |
| Source CSV / RR-13 edits | Not touched | `git status` confirms only untracked excluded files |

---

## 5. Documentation / Control Readiness

### 5.1 implementation-control.md

**PASS.** Control doc accurately records:
- Current gate: `P16 aggregate deepreview` (line 9, 19)
- All P16-S1, P16-S2, P16-S2.1, P16-S2 resumed gate transitions in Active Gate Ledger (lines 128-134)
- Correct verdicts: `PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY`, `BLOCKED_BEFORE_GOLDEN_EDIT_EXTRACTOR_TEXT_DIFF`, `ACCEPTED_READY_TO_RESUME_P16_S2_GOLDEN`, `ACCEPTED_READY_FOR_P16_AGGREGATE_DEEPREVIEW`
- Correct commit references: `974615e`, `121ad1f`
- Correct test counts: profile `22 passed`, full `433 passed` (S2.1), targeted `61 passed`, full `439 passed` (S2 resumed)
- Correct artifact paths for all P16 sub-gates
- Resume checklist correctly states aggregate review scope and constraints
- Active Residuals table correctly tracks enhanced-index expansion as aggregate review responsibility

### 5.2 README Non-Update

**PASS.** No P16 commit changed public CLI usage, package architecture, Engine/Fund contracts, config defaults, test organization, or documented template structure. README non-update is correct.

---

## 6. Testing Adequacy

### 6.1 Independent Verification

| Check | Result |
|-------|--------|
| `pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | `61 passed in 0.40s` |
| `pytest -q` (full suite) | `439 passed in 0.99s` |
| `ruff check fund_agent tests` | `All checks passed!` |
| `git diff --check HEAD` | Passed, exit 0 |
| Golden JSON verification | `fund_count=11`, `record_count=150`, no embedded newlines, 25 planned rows confirmed, 001548 preserved |

### 6.2 Test Coverage Assessment

P16-S2 resumed tests cover the full strict-golden-to-quality-gate denominator path:
- `test_golden_answer.py`: exact planned rows, forbidden field absence, no embedded newlines, 001548 preservation
- `test_extraction_snapshot.py`: composite IndexProfileValue serializes only comparable scalar values
- `test_extraction_score.py`: composite scalar correctness match/mismatch accounting
- `test_quality_gate.py`: composite scalar mismatch blocks through FQ1
- `test_profile.py` (P16-S2.1): affected/unaffected normalization, composite semantics, benchmark-only/source-tier preservation

---

## 7. Findings

No blocking or warning-level findings.

| # | Severity | Finding | Evidence | Disposition |
|---|----------|---------|----------|-------------|
| F1 | Info | Pre-existing embedded newlines in `001548` golden values (e.g., `fund_name`, `investment_objective`, `benchmark_text`) | `reports/golden-answers/golden-answer.json` lines for 001548 | Pre-P16 state, not introduced by P16. Not in scope for this gate. Future cleanup candidate if desired. |

---

## 8. Residual Risks

| Risk | Owner | Status |
|------|-------|--------|
| `tracking_error` production golden for 001548 and all 5 enhanced-index candidates | Future golden gate if direct observed evidence accepted | Blocked by P15-S1A / P16-S1 |
| `benchmark_index_name=null` and `benchmark_component_text` tuple semantics outside strict golden denominator | Future golden review if extractor semantics change | Intentionally excluded; covered by test assertions |
| Enhanced-index `index_profile` expansion beyond 5 candidates | Future phase if more candidates selected | 5 candidates cover current selected-fund enhanced-index set |
| Pre-existing 001548 embedded newlines | Future cleanup if desired | Not introduced by P16; not blocking |

---

## 9. Recommended Next Gate

P16 aggregate deepreview is accepted. The next safe gate is:

```text
P16 draft PR gate / PR review
```

This requires explicit user authorization. The draft PR should include all P16 commits from `f80affc` through `604e2d9` and the P16 aggregate review artifacts.

---

## Validation Commands

```bash
git log --oneline f80affc..604e2d9
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
```

All passed at time of review.
