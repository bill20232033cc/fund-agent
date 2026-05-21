# P13 Aggregate Deepreview（2026-05-22）

## Scope

- Mode: current changes
- Branch: `feat/p13-tracking-error-direct-disclosure`
- Base: `main`
- Output file: `docs/reviews/p13-aggregate-deepreview-mimo-20260522.md`
- Included scope: P13 complete branch changes from main through current HEAD (commit `2172691`), plus unstaged `docs/implementation-control.md` update (commit hash sync, archive summary)
- Excluded scope: `docs/repo-audit-20260521.md`（untracked, out-of-scope per all prior gates）
- Parallel review coverage: 无；单 reviewer 全链路 aggregate 走读
- Reference artifacts:
  - `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`
  - `docs/reviews/next-phase-selection-controller-judgment-20260522.md`
  - `docs/reviews/p13-s1-plan-review-controller-judgment-20260522.md`
  - `docs/reviews/p13-tracking-error-code-review-controller-judgment-20260522.md`
  - `docs/reviews/p13-tracking-error-code-review-mimo-20260522.md`、`docs/reviews/p13-tracking-error-code-review-glm-20260522.md`
  - `docs/reviews/p13-tracking-error-code-rereview-mimo-20260522.md`、`docs/reviews/p13-tracking-error-code-rereview-glm-20260522.md`
- Controller validation（recorded）: `pytest` 424 passed in 1.34s; `ruff check fund_agent tests` passed; `git diff --check HEAD` passed

## Findings

未发现实质性问题。

## Aggregate Risk Assessment

### 1. Phase Scope Compliance

P13-S1 plan review controller judgment accepted a narrow direct-disclosure scope. Implementation matches:

- direct annual-report tracking-error extraction only ✓
- explicit typed `IndexProfileValue` and `TrackingErrorValue` fields, no `extra_payload` ✓
- product authority via Fund Capability structured data ✓
- developer override only as lower-priority developer-mode fallback ✓
- no calculated index series, external index adapter, methodology/constituents extraction ✓
- no E1/E2/E3, Evidence Confirm, LLM, Dayu runtime ✓
- no RR-13 data or `docs/repo-audit-20260521.md` changes ✓

Evidence: `docs/reviews/p13-tracking-error-direct-disclosure-implementation-20260522.md` scope section; `data_extractor.py:191-249` (`_tracking_error_for_fund_type` only gates `index_fund`/`enhanced_index`); `performance.py:341-761` (`_extract_tracking_error` only reads `ParsedAnnualReport` §3/§2); no imports of `dayu`, `evidence_confirm`, or external index adapters in any changed file.

### 2. No Dayu/LLM/E1-E3/Evidence Confirm

No changed file imports or references `dayu-agent`, `dayu.host`, `dayu.engine`, LLM writing, Evidence Confirm, or E1/E2/E3 execution paths. The audit additions (`_audit_tracking_error_source_guard`, `_audit_index_profile_source_guard`) are deterministic C2 programmatic guards only.

Evidence: `grep -r "dayu\|evidence_confirm\|llm_audit\|e1_\|e2_\|e3_" fund_agent/` yields no hits in changed files; `audit_programmatic.py` new functions only check structured field presence and anchor source_kind.

### 3. No Calculated Index Series/Methodology/Constituents

`TrackingErrorValue` reserves `fund_series_source`, `index_series_source`, `observation_count`, `annualization_factor` fields but all remain `None` for direct disclosure. `IndexProfileValue.methodology_availability` and `constituents_availability` default to `"benchmark_only"` for Tier 1; renderer renders `数据不足` for both; audit guards reject benchmark-only evidence supporting methodology/constituents claims.

Evidence: `models.py:137-189` (TrackingErrorValue field declarations); `profile.py:530-536` (`_build_index_profile` sets `methodology_availability="benchmark_only"`, `constituents_availability="benchmark_only"`); `renderer.py:2222-2268` (`_index_profile_methodology_text`/`_index_profile_constituents_text` return insufficient for benchmark_only); `audit_programmatic.py:611-806` (`_audit_index_profile_source_guard` checks `direct_disclosure`/`source_reference`).

### 4. FundDocumentRepository Boundary

Tracking error extraction reads only from `ParsedAnnualReport` (provided by `FundDocumentRepository`). Service resolves via `resolve_tracking_error_for_risk()` consuming `structured_data.tracking_error`. No direct PDF cache, file system, or download helper access from Service/UI/renderer.

Evidence: `performance.py:341-761` (`_extract_tracking_error` takes `ParsedAnnualReport` only); `fund_analysis_service.py:375-381` (Service calls `resolve_tracking_error_for_risk` with `structured_data.tracking_error`); no `FundDocumentRepository` bypass in renderer or audit code.

### 5. Service/UI Boundaries

Service layer consumes `resolve_tracking_error_for_risk()` with explicit `tracking_error_field` from structured data and `developer_override` gated by `resolved_contract.mode == "developer_override"`. Renderer reads `input_data.structured_data.tracking_error` directly. No direct source access from Service or UI.

Evidence: `fund_analysis_service.py:375-381`; `renderer.py:663-697` (`_render_tracking_error_segment` reads from `input_data.structured_data.tracking_error`); `_has_renderable_tracking_error` checks extraction_mode and value presence.

### 6. Quality Gate Snapshot Policy

`index_profile` and `tracking_error` added to `SNAPSHOT_FIELD_ORDER` as observability fields. Tests verify `comparable_values == {}` for both, confirming they do not enter FQ2 denominator, golden correctness denominator, or comparable value set.

Evidence: `extraction_snapshot.py:30-42` (field order additions); `test_extraction_snapshot.py:185-186` (`assert records_by_name["index_profile"].comparable_values == {}` and `assert records_by_name["tracking_error"].comparable_values == {}`).

### 7. Prior Review Findings Closure

All 3 prior code review findings closed:

| Finding | Source | Status | Evidence |
|---|---|---|---|
| renderer `assert` for runtime validation | MiMo | closed | `renderer.py:686-687` — explicit `if value is None: return _render_tracking_error_insufficient(anchors)`; test `test_render_template_report_defensively_handles_missing_tracking_error_value` |
| composite benchmark split only `+`/`＋` | GLM F1 | closed | `profile.py:592` — `re.split(r"[＋+×*]\|和\|及", ...)`; test `test_extract_profile_splits_composite_benchmark_with_chinese_and_multiply_separators` |
| table+text same value treated as ambiguous | GLM F2 | closed | `performance.py:361-364` — `_select_consistent_tracking_error_match` compares parsed values; tests for same-value and conflicting-value |

Evidence: `docs/reviews/p13-tracking-error-code-rereview-mimo-20260522.md` PASS; `docs/reviews/p13-tracking-error-code-rereview-glm-20260522.md` PASS.

### 8. Documentation Sync

- `fund_agent/fund/README.md`: 12→14 structured data fields, snapshot 14→16 fields, risk-check tracking_error authority description updated. ✓
- `tests/README.md`: test_profile, test_performance, test_risk_check, test_audit_programmatic, test_renderer, test_extraction_snapshot descriptions synced. ✓
- `docs/implementation-control.md`: commit hash updated to `2172691`, P13 archive summary expanded, gate/entry-point/current-phase updated. ✓
- `docs/design.md`: no changes needed (P13 implementation stays within existing design boundaries). ✓

### 9. Test Coverage

| Area | Tests | Coverage |
|---|---|---|
| tracking error extraction | 7 | direct disclosure, target filter, ambiguous fail-closed, standard deviation exclusion, table extraction, table+text same value, table+text conflicting |
| index profile extraction | 4 | pure index (identified), enhanced index (composite), non-index (missing), composite separator split |
| risk check authority | 4 | structured data priority, developer override fallback, product mode ignores override, QDII not applicable |
| audit source guards | 3 | tracking error without structured field, tracking error with structured field, benchmark-only methodology misuse |
| renderer | 3 | structured data replacement, defensive missing value, benchmark-only insufficient |
| snapshot | 1 | comparable_values empty for index_profile and tracking_error |
| integration regression | 1 | P1 sample matrix 38 cells, 510300 direct / 110011 missing / 000171 missing |
| adjacent regression | existing | full suite 424 passed |

Total: 23 new tests added, all passing within full suite of 424.

### 10. Residual Owners

| Residual | Owner | Gate |
|---|---|---|
| Calculated tracking error from fund/index time series | future P13 follow-up or new phase | source-contract design required |
| External index series adapter | future phase | identity/cache/failure taxonomy design required |
| Index methodology and constituents extraction | future source-contract phase | only replace `数据不足` when source contract accepted |
| QDII tracking-error applicability | future subtype-design phase | QDII subtype design required |
| `index_profile`/`tracking_error` snapshot promotion to comparable/golden/FQ2 | future quality-gate phase | explicit acceptance required |
| `_build_extracted_field_record` type annotation accuracy | future cleanup | `ExtractedField[dict[str, object]]` signature vs typed value runtime |

### 11. Draft PR Readiness

Implementation accepted by controller judgment. All findings closed. Tests pass. Docs synced. Branch has 1 committed change (`2172691`) plus unstaged `docs/implementation-control.md` update. Ready for accepted implementation commit and draft PR per phaseflow.

## Open Questions

- 无。

## Residual Risk

- `_build_extracted_field_record` in `extraction_snapshot.py` declares `extracted_field: ExtractedField[dict[str, object]]` but receives `ExtractedField[IndexProfileValue]` / `ExtractedField[TrackingErrorValue]`. Current behavior correct (typed value passes through `getattr`); type annotation inaccuracy is low-risk maintainability debt.
- Composite benchmark separator split (`profile.py:592`) uses inline regex `r"[＋+×*]|和|及"` rather than referencing `_COMPOSITE_BENCHMARK_SEPARATORS` tuple. If separators list is extended, the split pattern must be updated in sync. Low risk given current stable separator set.

## Verdict

**PASS**

P13 direct tracking-error disclosure implementation严格遵循 accepted plan scope。显式类型字段、FundDocumentRepository 边界、跟踪误差 authority 迁移、renderer/audit/risk 行为、quality gate observability-only 策略均按计划正确实现。3 个 prior code review finding 全部 closed 并有对应测试验证。文档已同步。无 Dayu/LLM/E1-E3/Evidence Confirm/calculated index series/methodology/constituents scope creep。424 测试全通过，ruff 通过。分支 ready for accepted implementation commit and draft PR.
