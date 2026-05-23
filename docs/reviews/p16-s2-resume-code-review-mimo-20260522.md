# P16-S2 Resume Code Review — AgentMiMo（2026-05-22）

## Verdict

`PASS`

Implementation correctly adds exactly 25 planned `index_profile` scalar golden rows for 5 enhanced-index candidates, rebuilds strict JSON through `golden-build`, adds focused tests covering strict JSON / composite no-synthesis / comparable serialization / correctness match-mismatch / quality gate FQ1 / 001548 preservation, and preserves all existing golden records. No blocking findings.

## Inputs

| Artifact | Role |
|---|---|
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` | Accepted plan |
| `docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md` | Plan review judgment |
| `docs/reviews/p16-s2-1-code-review-controller-judgment-20260522.md` | P16-S2.1 code review judgment |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-resume-20260522.md` | Implementation artifact |
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Changed: reviewed Markdown |
| `reports/golden-answers/golden-answer.json` | Changed: strict JSON |
| `tests/fund/test_golden_answer.py` | Changed: golden answer tests |
| `tests/fund/test_extraction_snapshot.py` | Changed: snapshot tests |
| `tests/fund/test_extraction_score.py` | Changed: score tests |
| `tests/fund/test_quality_gate.py` | Changed: quality gate tests |

Excluded inputs not read: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Review Focus Results

### F1: 是否只添加 5 个 candidates 的 25 条计划内 rows

**PASS.** Reviewed Markdown diff appends exactly 5 fund sections (`004194`, `005313`, `017644`, `019918`, `019923`), each with exactly 5 `index_profile` scalar rows covering `benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier`. All 25 rows byte-for-byte match the plan-specified values and `confidence=high`. No other fund codes or field types added.

Verified: `python3` script confirmed ALL 25 ROWS MATCH PLAN EXACTLY against `golden-answer.json`.

### F2: 是否禁止并实际未添加非计划字段

**PASS.** `golden-answer.json` verification confirmed per candidate:
- `benchmark_index_name`, `benchmark_index_code`, `benchmark_component_text` — not present (hit set empty)
- `tracking_error` rows — 0 per candidate
- `missing_reasons` — not present
- No non-`index_profile` field_name rows for any new candidate

### F3: golden-answer.json 是否由 reviewed Markdown 合法重建

**PASS.**
- `fund_count=11` (6 existing + 5 new), `record_count=150` (125 existing + 25 new) — arithmetic verified: `len(funds)=11`, `sum(records)=150`, `len(top-level records)=150`, all consistent.
- `001548` existing rows preserved: direct dict-equality test in `test_reviewed_golden_answer_preserves_001548_index_profile_rows` asserts exact 4 rows (`benchmark_text`, `benchmark_identity_status`, `benchmark_index_name`, `source_tier`) with unchanged values.
- Existing 6 funds' record counts unchanged (004393=21, 000216=20, 007721=20, 007360=20, 006597=20, 001548=24).

### F4: 测试覆盖与 helper 宽松度

**PASS.** Test coverage meets plan requirements:

| Requirement | Test | Assessment |
|---|---|---|
| strict JSON acceptance | `test_reviewed_golden_answer_contains_only_planned_p16_s2_index_profile_rows` | Verifies exact 5 subfields per candidate, no forbidden fields, `confidence=high`, no embedded newlines |
| 001548 preservation | `test_reviewed_golden_answer_preserves_001548_index_profile_rows` | Dict-equality (not subset), catches additions |
| composite no-synthesis | `test_build_snapshot_records_omits_composite_index_null_and_tuple_values` | Asserts `benchmark_index_name`/`benchmark_index_code`/`benchmark_component_text` absent from `comparable_values` |
| comparable scalar serialization | same test + fixture `_build_bundle(include_composite_index_profile=True)` | Validates exact 5 scalar fields in `comparable_values` |
| correctness match | `test_compare_snapshot_correctness_matches_composite_index_profile_scalars` | 5/5 match, 0 mismatch, 0 unavailable |
| correctness mismatch | `test_compare_snapshot_correctness_flags_composite_index_scalar_mismatch` | `source_tier` mismatch detected, 4/5 match, 1 mismatch |
| quality gate FQ1 | `test_run_quality_gate_blocks_composite_index_profile_scalar_mismatch` | FQ1 block with correct `expected_value`/`actual_value` |

**Helper observation** (non-blocking): `_golden_answer_json_from_records` in `test_extraction_score.py` was generalized to infer `fund_code` from `records[0]` instead of hardcoding `"004393"`. This is a reasonable generalization — all callers pass explicit records with correct fund codes, and no test relies on the old hardcoded default. Does not introduce real regression risk.

### F5: 边界违规检查

**PASS.**
- No source code changes (`fund_agent/` untouched)
- No `FundDocumentRepository` / source boundary violations
- No Dayu runtime, Host, Engine, tool loop, or LLM dependency introduced
- No `extra_payload` additions
- No README changes required (implementation artifact's reasoning accepted: golden data rows only, no public contract changes)
- Phase scope respected: only `index_profile` scalar rows added, no `tracking_error`, methodology, constituents, or calculated fields

## Validation Results

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | `61 passed in 0.40s` |
| `.venv/bin/python -m ruff check fund_agent tests` | `All checks passed!` |
| `git diff --check HEAD` | exit 0, no whitespace errors |
| `.venv/bin/python -m pytest -q` | `439 passed in 0.94s` |
| Manual `golden-answer.json` structure verification | `fund_count=11`, `record_count=150`, 25 new rows match plan, 0 forbidden fields, `001548` preserved |

## Observations

| # | Severity | Finding | Evidence | Disposition |
|---|---|---|---|---|
| O1 | info | `_golden_answer_json_from_records` helper generalized to infer fund_code from first record | `test_extraction_score.py:1427` | Accepted as non-blocking; all callers provide explicit consistent records |

## Finding Dispositions

No blocking or warning-level findings. One info-level observation accepted as harmless helper generalization.
