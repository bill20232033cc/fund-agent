# P14-S1 Index Profile / Tracking Error Quality-Denominator Plan（2026-05-22）

## Verdict

`HANDOFF_READY_FOR_PLAN_REVIEW`

P14-S1 只把 P13 已交付的 `index_profile` / `tracking_error` 结构化字段接入现有质量分母机制，不扩大抽取来源、不计算跟踪误差、不新增外部指数数据。

核心实现选择：

- `ExtractionMode` 保持 `direct / derived / estimated / missing` 不变。
- 用 `classified_fund_type` + 适用性矩阵在 snapshot / score / gate 层表达 `not_applicable`。
- `index_profile` 和 `tracking_error` 加入 FQ2 P1 质量分母，但只对 `index_fund` / `enhanced_index` 适用；非适用基金从 P1 coverage / traceability / missing-field 分母中排除。
- `COMPARABLE_SUB_FIELDS_BY_FIELD` 增加稳定标量子字段。
- golden answer JSON 增加 1 只真实 index golden 覆盖：优先使用现有 strict golden 中的 `001548`，不使用 `510300` 写入生产 golden，因为 `510300` 不在当前 `docs/code_20260519.csv` / strict golden answer 集合中；`510300` 继续用于 P1 sample matrix regression。
- enhanced_index 用最小 deterministic test fixture 覆盖，不写入生产 golden answer。

## Goal / Motivation

P13 已经实现：

- `StructuredFundDataBundle.index_profile`;
- `StructuredFundDataBundle.tracking_error`;
- direct annual-report tracking-error extraction;
- renderer/audit/risk-check consumption;
- snapshot observability。

P13 未实现：

- FQ2 `FIELD_PRIORITY_BY_NAME` / `ExtractionScore` priority；
- snapshot `COMPARABLE_SUB_FIELDS_BY_FIELD` / `comparable_values`；
- `GoldenAnswerRecord` / strict golden answer JSON correctness。

P14-S1 的目标是让 P13 新字段进入现有质量闭环，使 direct-disclosure regression 能被 snapshot / score / quality gate / golden correctness 发现，同时保持 Fund Capability ownership 和 deterministic MVP 边界。

## Source Evidence

- `AGENTS.md`
  - 生产年报访问必须经 `FundDocumentRepository`。
  - 基金类型判断优先，指数 / 指数增强基金必须应用对应 `preferred_lens`。
  - 审计、证据锚点、基金类型、章节映射和规则归 Fund Capability。
- `docs/design.md`
  - 当前主链路是 deterministic `UI -> Service -> Fund Capability`。
  - 不依赖外部 Dayu Host/Engine/tool loop 或 LLM 写作。
  - 指数基金 preferred lens 包含跟踪误差、费率、规模流动性；指数增强包含超额收益来源、跟踪误差。
- `docs/implementation-control.md`
  - 当前 gate 是 `P14-S1 index_profile / tracking_error quality-denominator plan-review`。
  - Success signal 是精确定义 FQ2 priority、comparable sub-field、golden correctness、not-applicable、fixture 和 validation。
- `docs/reviews/post-p13-follow-up-planning-20260522.md`
  - P14-S1 必须绑定实际机制：`FIELD_PRIORITY_BY_NAME` / `ExtractionScore`、`COMPARABLE_SUB_FIELDS_BY_FIELD` / `comparable_values`、`GoldenAnswerRecord` / golden answer JSON。
- `docs/reviews/post-p13-follow-up-plan-review-controller-judgment-20260522.md`
  - P14-S1 被接受为下一 gate，且明确禁止 calculated tracking error、external adapter、methodology / constituents extraction、QDII subtype redesign、E1/E2/E3、Evidence Confirm、Dayu runtime、RR-13 和 repo-audit work。
- Current code facts:
  - `fund_agent/fund/extraction_snapshot.py` 已把 `index_profile` / `tracking_error` 放进 `SNAPSHOT_FIELD_ORDER`，但 `COMPARABLE_SUB_FIELDS_BY_FIELD` 还不包含这两个字段。
  - `fund_agent/fund/extraction_score.py` 的 `FIELD_PRIORITY_BY_NAME` 还不包含这两个字段，未知字段 priority 为 `UNMAPPED`。
  - `fund_agent/fund/extractors/models.py` 的 `ExtractionMode` 当前只有 `direct / derived / estimated / missing`。
  - `fund_agent/fund/quality_gate.py` 只对 P0/P1 `status=fail` 触发 FQ2，P1 为 warn。
  - `reports/golden-answers/golden-answer.json` 已包含 `001548`，`docs/code_20260519.csv` 也包含 `001548`；`510300` 只在 sample docs / integration fixture 中出现，不在当前 selected-fund CSV / strict golden answer 中。
  - `tests/fixtures/fund/extractors/profile/index_enhanced_profile.txt` 已有 `161725` enhanced-index profile fixture，但 P1 sample matrix 目前没有 enhanced-index case。

## Plan-review Findings Incorporated

This revision incorporates controller-accepted plan-review fixes before implementation:

- MiMo F-1: Slice B now spells out `_build_fund_quality_row()` data flow and requires `_missing_fields_by_priority()` to receive or derive equivalent `classified_fund_type` context.
- MiMo F-2: Slice A now permits minimal snapshot typing loosening for dataclass `ExtractedField` values and requires dict/dataclass normalization before `.get` access.
- GLM F1: Slice A expected assertions now define bool comparable serialization as `str(True) == "True"` and `str(False) == "False"`.
- GLM F2: Slice D now requires the `161725` enhanced-index builder to include `§1` / `§2` for classification and index profile plus `§3` direct tracking-error disclosure.

## Non-goals

- 不重新打开 P13 direct-disclosure extractor / renderer / audit implementation。
- 不计算 tracking error，不引入 fund/index time series。
- 不新增 external index series adapter。
- 不抽取 index methodology 或 constituents。
- 不做 QDII subtype redesign；当前 P14-S1 只认 `index_fund` / `enhanced_index` 为适用。
- 不引入 E1/E2/E3、Evidence Confirm、LLM writing、RepairContract。
- 不引入 Dayu runtime、Host、Engine 或 tool loop。
- 不修改 RR-13 duplicate `016492`。
- 不读取或修改 `docs/repo-audit-20260521.md`。
- 不改变 CLI 用户入口或 `fund-analysis analyze` product contract。

## Exact Scope Decisions

### 1. FQ2 / ExtractionScore

Decision:

- Add `index_profile` and `tracking_error` to `FIELD_PRIORITY_BY_NAME` as `P1`.
- Make that P1 priority conditional by fund type in scoring logic:
  - applicable fund types: `index_fund`, `enhanced_index`;
  - non-applicable fund types: `active_fund`, `bond_fund`, `qdii_fund`, `fof_fund`;
  - unknown / missing `classified_fund_type`: include record in scoring, because applicability cannot be proven and silent exclusion would hide classification failures.

State transitions:

| Input record | Applicable? | Field score counter | Fund P1 missing fields | Fund quality missing rate |
|---|---|---|---|---|
| `field_name=index_profile`, `classified_fund_type=index_fund`, value present | yes | counted covered / traceable by current values | not missing | counted in total |
| `field_name=tracking_error`, `classified_fund_type=index_fund`, value present | yes | counted covered / traceable by current values | not missing | counted in total |
| same fields, `classified_fund_type=enhanced_index` | yes | counted | counted if missing | counted in total |
| same fields, `classified_fund_type=active_fund/bond_fund/qdii_fund/fof_fund` | no | excluded from FQ2 counters | excluded | excluded from total/missing |
| same fields, `classified_fund_type` missing/conflicting/unknown | unknown | counted as P1 | counted if missing | counted in total |

Implementation area:

- `fund_agent/fund/extraction_score.py`
  - Add constants:
    - `INDEX_QUALITY_FIELD_NAMES = ("index_profile", "tracking_error")`
    - `INDEX_QUALITY_APPLICABLE_FUND_TYPES = ("index_fund", "enhanced_index")`
  - Add helper:
    - `_is_index_quality_field(field_name: str) -> bool`
    - `_is_non_applicable_index_quality_record(record: Mapping[str, object]) -> bool`
    - `_scorable_records(records: Sequence[Mapping[str, object]]) -> tuple[Mapping[str, object], ...]`
  - Use helper in:
    - `score_snapshot_records()`
    - `_score_records_for_single_fund()`
    - `_missing_fields_by_priority()`
    - `_build_fund_quality_row()` missing field count / total field count path
  - Do not change `quality_gate.py` FQ2 severity rules. P1 remains warn if applicable records fail.

Rationale:

- P0 would over-block product readiness for fields that are important but still direct-disclosure only.
- P2 would under-protect a core `preferred_lens` variable for index/enhanced-index funds.
- Static P1 without applicability filtering would incorrectly penalize active/bond/QDII/FOF funds.

### 2. Not-applicable Semantics

Decision:

- Do not expand `ExtractionMode`.
- Keep `ExtractedField(..., extraction_mode="missing", note="非指数基金不适用...")` for non-index paths.
- Express non-applicability in quality layer via `classified_fund_type` applicability matrix, not in extractor model.

Trade-off:

- Expanding `ExtractionMode` with `not_applicable` would touch `extractors/models.py`, all extractor consumers, renderer/audit/risk tests, snapshot normalization, and likely type hints across the repo. That is too broad for this quality-denominator slice.
- Keeping enum unchanged has one risk: non-index missing values could be counted as quality failures. P14-S1 must fix this by excluding non-applicable index-quality fields from score / fund_score / fund_quality denominator.

Required invariant:

- `ExtractionMode` remains exactly:

```python
ExtractionMode = Literal["direct", "derived", "estimated", "missing"]
```

### 3. Comparable Sub-fields

Add exact comparable sub-fields:

```python
COMPARABLE_SUB_FIELDS_BY_FIELD["index_profile"] = (
    "benchmark_text",
    "benchmark_identity_status",
    "benchmark_index_name",
    "benchmark_index_code",
    "methodology_availability",
    "constituents_availability",
    "source_tier",
)

COMPARABLE_SUB_FIELDS_BY_FIELD["tracking_error"] = (
    "value_text",
    "period_label",
    "annualized",
    "source_type",
    "calculation_method",
    "benchmark_identity_status",
    "benchmark_index_name",
    "benchmark_index_code",
    "frequency",
    "input_period_complete",
)
```

Selection rationale:

- Include only stable scalar fields already present on `IndexProfileValue` / `TrackingErrorValue`.
- Exclude `Decimal` `value` from comparable values because `value_text` preserves disclosed user-visible value and avoids decimal formatting churn.
- Exclude tuple/list fields such as `benchmark_component_text` and `missing_reasons` because `_comparable_scalar()` deliberately rejects nested structures.
- Exclude `methodology_summary`, `methodology_source_title`, `constituents_summary`, `constituents_as_of_date`, `provenance_note`, `period_start`, `period_end`, `fund_series_source`, `index_series_source`, `observation_count`, `annualization_factor` because P14-S1 must not imply methodology/constituents extraction or calculated series support.

Implementation area:

- `fund_agent/fund/extraction_snapshot.py`
  - Update `COMPARABLE_SUB_FIELDS_BY_FIELD`.
  - Update `_comparable_values_for_field()` to support dataclass values via `dataclasses.asdict()` or a small helper `_value_mapping(value: object) -> Mapping[str, object] | None`.
  - Preserve current dict-field behavior.
  - Keep nested values excluded by `_comparable_scalar()`.

### 4. Golden Answer JSON Correctness

Decision:

- Add production strict golden coverage for existing `001548` only.
- Do not add `510300` to production golden answer JSON because it is not in current `docs/code_20260519.csv` or `reports/golden-answers/golden-answer.json`.
- Do not add enhanced-index production golden record in this slice because no selected-fund / strict-golden enhanced-index fixture is currently present. Cover enhanced-index via deterministic tests.

Production golden additions:

Append these records to the existing `001548` fund in `reports/golden-answers/golden-answer-prefill-reviewed.md` and rebuild `reports/golden-answers/golden-answer.json` through the existing golden-build path:

| fund_code | field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|---|
| `001548` | `index_profile` | `benchmark_identity_status` | `identified` | `medium` | `年报2024 §2 benchmark` |
| `001548` | `index_profile` | `benchmark_index_name` | `上证50指数` | `medium` | `年报2024 §2 benchmark` |
| `001548` | `index_profile` | `methodology_availability` | `benchmark_only` | `medium` | `年报2024 §2 benchmark` |
| `001548` | `index_profile` | `constituents_availability` | `benchmark_only` | `medium` | `年报2024 §2 benchmark` |

Do not add `tracking_error` production golden records unless implementation proves from the existing reviewed annual-report source that `001548` has a direct disclosed tracking error in current extractor output. If not proven, `tracking_error` correctness is covered by unit tests and sample matrix only in P14-S1.

Required golden tooling changes:

- `fund_agent/fund/golden_prefill.py`
  - `_field_from_bundle()` currently types fields as `ExtractedField[dict[str, object]]`; update helper typing and `_sub_field_value()` so dataclass values from `IndexProfileValue` / `TrackingErrorValue` can be resolved.
  - Use `dataclasses.asdict()` or attribute lookup; keep dict behavior unchanged.
  - Add `_SUB_FIELD_ALIASES` only if needed; no alias is required for chosen P14 subfields.
- `docs/golden-answer-template.md`
  - Add `index_profile` rows under existing `001548` section only.
  - Do not add tracking_error template rows unless production source is proven.
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
  - Add reviewed rows for `001548` with the values above.
- `reports/golden-answers/golden-answer.json`
  - Rebuild using the existing golden answer service / CLI after reviewed markdown is updated.

If implementation discovers that `001548` current extractor output does not match the proposed values, stop before editing production golden files and report the blocker to controller. Do not invent expected values.

### 5. Fixture Strategy

Existing fixtures to use:

- `tests/fund/integration/test_p1_sample_matrix.py`
  - Keep using `510300` for index_fund disclosed tracking_error path.
  - Existing expectation: `510300.tracking_error.extraction_mode == "direct"`.
- `tests/fixtures/fund/extractors/profile/index_enhanced_profile.txt`
  - Existing enhanced-index profile fixture with `161725`.
- `tests/fixtures/fund/extractors/performance/performance_with_tracking_error.txt`
  - Existing disclosed tracking-error fixture.
- `tests/fixtures/fund/extractors/performance/performance_with_tracking_error_ambiguous.txt`
  - Existing conflicting / target-like tracking-error fixture.

Minimal new deterministic fixture:

- Add enhanced-index case to `tests/fund/integration/test_p1_sample_matrix.py` if current matrix cannot exercise `enhanced_index` end-to-end.
- Recommended code: `161725`.
- Build report text by extending the current `_build_report()` or adding a specific enhanced-index fixture builder that includes:
  - `基金类别：指数型证券投资基金`
  - fund name containing `增强`
  - benchmark text with `沪深300指数收益率×95%＋银行活期存款利率（税后）×5%`
  - `报告期年化跟踪误差：1.23%`
- Update expected passed cell count deterministically.

Do not use live network or real PDFs in tests for this slice.

## Affected Files / Ownership

Allowed production files:

- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/golden_prefill.py`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `docs/golden-answer-template.md`

Allowed tests:

- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_golden_prefill.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/integration/test_p1_sample_matrix.py`

Allowed docs:

- `fund_agent/fund/README.md`
- `tests/README.md`
- Implementation artifact under `docs/reviews/`

Explicitly not allowed:

- `docs/design.md`
- `docs/implementation-control.md` unless controller separately assigns control-doc update
- root `README.md`
- `docs/repo-audit-20260521.md`
- source CSV / RR-13 data
- Service/UI/API contract files unless a test proves a thin service wrapper import breaks after Capability changes; if that happens, stop and ask controller before expanding scope.

## Implementation Slices

### Slice A — Snapshot Comparable Values

Objective:

Add stable comparable sub-fields for `index_profile` and `tracking_error`.

Allowed files:

- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/test_extraction_snapshot.py`

Exact changes:

- Add the two `COMPARABLE_SUB_FIELDS_BY_FIELD` entries listed above.
- Add helper to normalize dataclass or dict structured values to a mapping.
- `_comparable_values_for_field()` must normalize dict/dataclass values before any `.get` access. It may not assume `ExtractedField.value` is always `dict[str, object]`.
- If `_build_extracted_field_record()` or an equivalent snapshot helper currently types extracted fields as `ExtractedField[dict[str, object]]`, loosening that signature to `ExtractedField[object]`, `ExtractedField[dict[str, object] | IndexProfileValue | TrackingErrorValue]`, or an equivalent protocol/union is allowed as a minimal snapshot typing adjustment. This is not a model-scope expansion and must not change `ExtractedField` or `ExtractionMode`.
- Keep `_comparable_scalar()` behavior: only scalar non-empty values are included.
- Update existing test that currently asserts empty comparable values for `index_profile` / `tracking_error`.
- Add tests:
  - index profile dataclass emits the selected scalar comparable sub-fields;
  - tracking error dataclass emits selected scalar comparable sub-fields, including bool values as deterministic text via existing scalar conversion;
  - nested tuple/list fields are not emitted;
  - missing dataclass value emits `{}`.

Non-goals:

- Do not alter extraction logic.
- Do not add methodology / constituents extraction.
- Do not change snapshot schema keys.

Validation:

```text
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py -q
```

Expected assertions:

- `records_by_name["index_profile"].comparable_values` includes selected fields for an index fixture.
- `records_by_name["tracking_error"].comparable_values` includes `value_text`, `period_label`, `annualized`, `source_type`, `calculation_method`, `benchmark_identity_status`, `frequency`, `input_period_complete` when value exists.
- Bool comparable sub-fields serialize through existing scalar conversion: `True` becomes `"True"` and `False` becomes `"False"`. Any golden `expected_value` for bool sub-fields must use those exact strings, not lowercase JSON-style booleans.
- Non-applicable / missing values remain `{}`.

Stop condition:

- If dataclass comparable extraction requires changing extractor model types, stop and report; do not widen model scope.

### Slice B — Conditional FQ2 Priority And Applicability

Objective:

Make `index_profile` / `tracking_error` P1 for applicable fund types without penalizing non-index funds.

Allowed files:

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py` only if tests prove no way to preserve FQ2 semantics within `extraction_score.py`; preferred path does not edit quality gate.
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py` only for regression assertions around existing P1 warn behavior.

Exact changes:

- Add both fields to `FIELD_PRIORITY_BY_NAME` as `P1`.
- Add applicability helper constants/functions in `extraction_score.py`.
- Apply the scorable-record filter consistently:
  - field-level `score_snapshot_records()`;
  - single-fund `_score_records_for_single_fund()`;
  - `_missing_fields_by_priority()`;
  - `_build_fund_quality_row()` missing/total count.
- `_build_fund_quality_row()` data flow must remain code-fact aligned:
  - first obtain `classified_fund_type` via the existing `_unique_optional_text(records, "classified_fund_type")`;
  - then pass that resolved value into the index-quality scorable-record filtering used for `missing_field_count` and `total_field_count`;
  - compute missing/total counts from the filtered records, not the original records, so non-applicable `index_profile` / `tracking_error` rows do not inflate missing rate.
- `_missing_fields_by_priority()` must receive `classified_fund_type`, receive pre-filtered records, or otherwise use equivalent context so it excludes non-applicable index-quality fields consistently with `_build_fund_quality_row()` and `_score_records_for_single_fund()`.
- Keep unknown/missing fund type scorable.
- Do not change `quality_gate.py` severity mapping: P1 fail remains FQ2 warn.

Tests:

- `test_score_snapshot_records_computes_coverage_traceability_status_and_priority`
  - include applicable `index_profile` / `tracking_error` rows and assert priority `P1`.
  - assert `FIELD_PRIORITY_BY_NAME` covers all scored fields, including new fields.
- Add `test_score_snapshot_records_excludes_index_quality_fields_for_non_index_funds`.
  - records for active/bond/QDII/FOF with missing `index_profile` / `tracking_error` do not reduce aggregate coverage or appear as P1 failed fields.
- Add `test_score_fund_records_counts_index_quality_missing_only_for_index_and_enhanced`.
  - applicable index/enhanced missing fields appear in `p1_failed_fields`.
  - active fund missing fields do not appear.
- Add/adjust fund_quality test:
  - non-index missing `index_profile` / `tracking_error` are excluded from missing field count and missing rate.
  - index/enhanced missing fields count.
- Add quality gate regression:
  - P1 `tracking_error` fail in `field_scores` still emits FQ2 warn, not block.

Validation:

```text
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Expected assertions:

- `index_profile` / `tracking_error` no longer appear as `UNMAPPED` in score rows.
- Non-index fields are excluded rather than counted as missing.
- Unknown fund type remains conservative and can fail P1.

Stop condition:

- If conditional filtering requires changing score JSON schema, stop and report. P14-S1 should avoid schema changes unless controller accepts them.

### Slice C — Golden Prefill / Strict Golden Correctness

Objective:

Make golden correctness able to cover selected `index_profile` sub-fields and keep `tracking_error` golden production coverage explicitly out unless proven.

Allowed files:

- `fund_agent/fund/golden_prefill.py`
- `docs/golden-answer-template.md`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `tests/fund/test_golden_prefill.py`
- `tests/fund/test_golden_answer.py` only if strict schema tests need a fixture update.
- `tests/fund/test_extraction_score.py`

Exact changes:

- Update `golden_prefill.py` to resolve dataclass values.
- Add test using fake `IndexProfileValue` and `TrackingErrorValue` to prove prefill can resolve:
  - `index_profile.benchmark_identity_status`;
  - `index_profile.benchmark_index_name`;
  - `index_profile.methodology_availability`;
  - `tracking_error.value_text` in test-only template.
- Add `001548` `index_profile` rows to golden template / reviewed markdown.
- Rebuild `reports/golden-answers/golden-answer.json` using existing golden-build workflow.
- Add correctness tests:
  - `index_profile` golden records match when snapshot comparable values match;
  - mismatch blocks through correctness mismatch path;
  - a `tracking_error` golden record is `CORRECTNESS_UNAVAILABLE` when not in production golden or not comparable in fixture as applicable;
  - unavailable / not-in-denominator behavior remains non-blocking unless mismatch.

Production golden rows:

Use only the `001548` rows listed in the Exact Scope Decisions section. Values are `medium` confidence unless implementer verifies exact PDF pages and can safely promote to `high`.

Validation:

```text
.venv/bin/python -m pytest tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py -q
```

Expected assertions:

- `reports/golden-answers/golden-answer.json` remains strict schema valid.
- `record_count` increases by the exact number of accepted new records.
- Golden correctness compares `index_profile` rows when snapshot exposes comparable values.

Stop condition:

- If `001548` source evidence cannot support the planned expected values, do not modify production golden files; instead implement only unit-test golden records and report the production golden blocker.

### Slice D — Integration Fixture Matrix

Objective:

Cover index_fund and enhanced_index applicable paths without live sources.

Allowed files:

- `tests/fund/integration/test_p1_sample_matrix.py`
- `tests/fund/test_extraction_snapshot.py` if helper fixtures need reuse.

Exact changes:

- Keep `510300` as index_fund disclosed tracking-error sample.
- Add `161725` enhanced_index sample if not already covered end-to-end.
- The `161725` enhanced-index fixture builder must include:
  - `§1` with fund name/code/category text sufficient for classification;
  - `§2` with benchmark / product text sufficient for `index_profile`;
  - `§3` with direct tracking-error disclosure sufficient for `tracking_error`, for example `报告期年化跟踪误差：1.23%`.
- Ensure sample matrix asserts:
  - `510300.classified_fund_type == "index_fund"` and tracking error direct;
  - `161725.classified_fund_type == "enhanced_index"` and tracking error direct from the constructed `§3` disclosure;
  - non-index samples keep tracking error missing and do not imply FQ2 failure in Slice B tests.
- Update passed-cell count deterministically.

Validation:

```text
.venv/bin/python -m pytest tests/fund/integration/test_p1_sample_matrix.py -q
```

Expected assertions:

- Matrix remains fully deterministic.
- Repository/nav provider calls remain ordered and explicit.
- No real network/PDF access.

Stop condition:

- If enhanced-index classification depends on production classifier changes, stop; P14-S1 should only adjust fixture text/test expectations, not classifier logic.

### Slice E — Docs Sync And Implementation Artifact

Objective:

Sync developer docs to current code after tests pass.

Allowed files:

- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`

Exact changes:

- Update `fund_agent/fund/README.md`:
  - snapshot no longer says `index_profile` / `tracking_error` are only observability fields;
  - document P1 conditional quality denominator for index/enhanced-index only;
  - document comparable sub-fields and golden correctness scope at high level.
- Update `tests/README.md`:
  - snapshot tests now cover comparable values for these fields;
  - extraction score tests now cover applicability filtering;
  - golden prefill/answer tests now cover dataclass fields.
- Write implementation artifact with:
  - changed files;
  - implemented slices;
  - validation commands/results;
  - docs decision;
  - residual risks and owners.

Validation:

```text
git diff --check HEAD
```

Stop condition:

- Do not update root README because no user-facing command changes.
- Do not update `docs/design.md` because no architecture or template structure changes.
- Do not update `docs/implementation-control.md` unless controller separately asks for control-doc state update.

## Full Validation Matrix

Implementation must run at minimum:

```text
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py -q
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
.venv/bin/python -m pytest tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py -q
.venv/bin/python -m pytest tests/fund/integration/test_p1_sample_matrix.py -q
.venv/bin/python -m pytest tests/fund/test_quality_gate_integration.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py -q
.venv/bin/python -m ruff check fund_agent tests
.venv/bin/python -m pytest -q
git diff --check HEAD
```

Expected baseline:

- Full suite must have no regression from P13 closeout `424 passed`. If test count changes because new tests are added, implementation report must state exact new pass count and why it differs.
- `ruff` passes.
- `git diff --check HEAD` passes.

## Review Gates

Plan review must check:

- no `ExtractionMode` enum expansion;
- no calculated tracking error / external adapter / methodology / constituents scope;
- no QDII subtype redesign;
- `FIELD_PRIORITY_BY_NAME` no longer leaves the two fields ambiguous;
- non-index not-applicable records are not silently counted as failures;
- comparable sub-fields are exact and scalar-only;
- golden production rows are supported by existing reviewed sources or guarded by stop condition;
- enhanced-index fixture availability is explicit.

Code review must check:

- applicability filtering is applied consistently to field score, fund score and fund_quality;
- correctness unavailable vs mismatch semantics remain intact;
- production golden JSON remains strict-schema valid;
- no direct PDF/cache/source access is introduced in score/golden/quality code;
- docs match current code behavior.

Aggregate deepreview must run after implementation slices pass.

## Risks / Residuals

| Risk | Classification | Owner / destination |
|---|---|---|
| `tracking_error` production golden for `001548` may not have direct disclosure evidence | Stop-condition risk | Controller / future golden evidence slice if not proven |
| FQ2 conditional filtering could hide unknown fund type if over-filtered | Must fix in P14-S1 | Slice B: unknown type must remain scorable |
| `001548` index profile expected values may differ from real reviewed source | Stop-condition risk | Slice C implementer must verify before editing golden files |
| Enhanced-index production golden absent | Deferred | Future selected-fund/golden expansion phase |
| Calculated tracking error remains absent | Deferred | Future data-source/calculation phase |
| External index adapter / methodology / constituents remain absent | Deferred | Future source-contract phases |
| QDII index subtype remains unmodeled | Deferred | Future subtype-design phase |
| E1-E3 / Evidence Confirm absent | Deferred | Future audit architecture phase |
| RR-13 duplicate `016492` | Excluded | User / App source |
| `docs/repo-audit-20260521.md` | Excluded | Controller / user |

## Open Questions

No blocking open questions for implementation if plan review accepts the chosen approach.

Non-blocking assumptions:

- `001548` has sufficient reviewed annual-report evidence for index profile benchmark-derived rows. If implementation cannot verify this from current reviewed artifacts, Slice C must stop before production golden edits.
- `510300` remains sample-matrix only because it is not part of current selected-fund CSV / strict golden answer.

## Completion Report Format

Implementation agent must write:

```text
docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md
```

Report must include:

- current gate and plan artifact path;
- slices completed;
- changed files;
- exact behavior decisions implemented;
- validation commands and exact outputs;
- docs updated;
- residual risks with owner/destination;
- explicit confirmation that no prohibited scope was touched;
- stop status: `ready_for_code_review` or blocker details.

## Recommended Next Gate

Proceed to:

```text
P14-S1 plan review
```

Plan review artifacts should be written under:

```text
docs/reviews/p14-s1-plan-review-*-20260522.md
```
