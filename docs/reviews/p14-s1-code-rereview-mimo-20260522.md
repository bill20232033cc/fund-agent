# P14-S1 Targeted Re-Review: GLM F-1 / F-2 Fix Verification

Date: 2026-05-22

## Scope

- Mode: targeted re-review of GLM code review findings F-1 and F-2 after Codex fix pass
- Branch: `docs/post-p13-follow-up-planning`
- Base: `main`
- Reference artifacts:
  - `docs/reviews/p14-s1-code-review-mimo-20260522.md`
  - `docs/reviews/p14-s1-code-review-glm-20260522.md`
  - `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md` (Fix Pass section)
- Output file: `docs/reviews/p14-s1-code-rereview-mimo-20260522.md`

## F-1 Verification: `_build_fund_score_row` fund-level type resolution

### Claim

GLM F-1 stated that `_build_fund_score_row` used `_scorable_records(records)` with default parameters (record-level fallback), while `_build_fund_quality_row` used `_unique_optional_text` to resolve fund-level `classified_fund_type` first. This meant conflicting fund types could cause `fund_score` and `fund_quality` to disagree on index-quality field applicability.

### Evidence

**Fix confirmed.** `_build_fund_score_row` now mirrors `_build_fund_quality_row`'s data flow:

1. `extraction_score.py:1116-1119`: resolves fund-level type via `_unique_optional_text(records, "classified_fund_type")`.

2. `extraction_score.py:1120-1124`: passes resolved value to `_scorable_records(records, classified_fund_type=classified_fund_type, use_record_fund_type=False)`.

3. `extraction_score.py:1125-1130`: also passes resolved value to `_score_records_for_single_fund(scorable_records, ..., classified_fund_type=classified_fund_type, use_record_fund_type=False)`.

4. `_score_records_for_single_fund` signature (line 1158-1159) now accepts `classified_fund_type` and `use_record_fund_type` parameters, and passes them through to `_scorable_records` (line 1177-1180).

**Regression test added.** `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` (line 346-382):

- Creates conflicting records: `basic_identity` with `classified_fund_type="active_fund"`, `index_profile` with `classified_fund_type="bond_fund"`.
- `_unique_optional_text` returns `None` (conflict).
- Both `fund_score.p1_failed_fields` and `fund_quality.missing_p1_fields` assert `("index_profile",)`.
- `fund_score.records == 2` confirms index_profile was NOT excluded from scoring.

### Verdict

**F-1 CLOSED.** `_build_fund_score_row` and `_build_fund_quality_row` now use identical fund-level type resolution. Conflicting fund types produce conservative behavior in both paths: index_profile / tracking_error are retained in scoring rather than excluded.

## F-2 Verification: `_value_mapping` shared helper extraction

### Claim

GLM F-2 stated that `_value_mapping` was duplicated in `extraction_snapshot.py` and `golden_prefill.py`, violating the AGENTS.md rule "重复逻辑必须抽取为公共函数/类".

### Evidence

**Fix confirmed.** New module `fund_agent/fund/_value_utils.py` contains the single definition:

- `value_mapping(value: object) -> Mapping[str, object] | None` (public name, not private `_value_mapping`)
- Handles `None`, `Mapping`, and `is_dataclass` → `asdict()` cases
- Module docstring explicitly states: "本模块只服务 `fund_agent.fund` 内部...不依赖 Service、Engine、Runtime 或 UI 层"

**Import verification:**

- `extraction_snapshot.py:22`: `from fund_agent.fund._value_utils import value_mapping`
- `golden_prefill.py:16`: `from fund_agent.fund._value_utils import value_mapping`
- No local `def _value_mapping` remains in either file (confirmed via grep).

**Boundary compliance:** `_value_utils.py` lives inside `fund_agent/fund/` (Capability layer). No Service, Engine, Runtime, or UI dependency introduced. No public API surface change.

### Verdict

**F-2 CLOSED.** Duplicate `_value_mapping` extracted to single `value_mapping` in `fund_agent/fund/_value_utils.py`. Both consumers import from the shared module. No cross-layer dependency introduced.

## Non-Change Constraints

| Constraint | Status | Evidence |
|---|---|---|
| ExtractionMode unchanged | PASS | `extractors/models.py` not modified; `ExtractionMode = Literal["direct", "derived", "estimated", "missing"]` |
| No production tracking_error golden | PASS | `golden-answer.json` only added 4 `index_profile` records for 001548; no `tracking_error` rows |
| `docs/repo-audit-20260521.md` untouched | PASS | Fix pass changed files list does not include this file |

## Test / Docs Consistency

- Targeted test suite: **53 passed** (52 from initial review + 1 new F-1 conflict regression test)
- Full suite baseline: 428 passed (implementation artifact records 428 after fix pass)
- `ruff check`: passed (per implementation artifact Fix Pass validation)
- `git diff --check HEAD`: passed (per implementation artifact Fix Pass validation)
- Implementation artifact Fix Pass section documents both fixes and changed files

## Open Questions

- 无。

## Residual Risk

- 无新增残余风险。F-1 和 F-2 修复均为纯重构/对齐，不改变任何运行时行为。

## Conclusion

**PASS**

GLM code review findings F-1 和 F-2 均已正确关闭，未引入回归。

- F-1: `_build_fund_score_row` 现在与 `_build_fund_quality_row` 使用相同的 fund-level `_unique_optional_text` 类型解析和 `_scorable_records` 过滤路径；冲突类型下两条路径均保守保留 index_profile / tracking_error。新增回归测试覆盖。
- F-2: `_value_mapping` 已抽取为 `fund_agent/fund/_value_utils.value_mapping` 共享 helper，snapshot 和 golden_prefill 均从该模块 import，无本地重复定义，无跨层依赖。
- ExtractionMode 未扩展，无新增 production tracking_error golden，docs/repo-audit 未触碰。
