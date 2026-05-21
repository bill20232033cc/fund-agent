# P13-S1 Tracking Error / Index Data Source Contract Plan（2026-05-22）

## 1. Gate / Role

- **Role**: AgentCodex planning specialist, not implementer.
- **Current gate**: `P13-S1 tracking-error / index-data source contract plan-review`.
- **Design truth**: `docs/design.md`.
- **Control truth**: `docs/implementation-control.md`.
- **Selection truth**: `docs/reviews/next-phase-selection-20260522.md`.
- **Controller constraints**: `docs/reviews/next-phase-selection-controller-judgment-20260522.md`.
- **Plan reviews used**: `docs/reviews/next-phase-selection-plan-review-mimo-20260522.md`, `docs/reviews/next-phase-selection-plan-review-glm-20260522.md`.
- **Output file for this gate**: `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` only.

This artifact is a code-generation-ready plan for a future implementation gate. It does not implement code, modify tests, update README/design/control, stage files, commit, push, open a PR, edit `docs/repo-audit-20260521.md`, or touch RR-13 source data.

## 2. Controller Constraints Answered First

| Required question | P13-S1 answer |
|---|---|
| `tracking_error` authority and service override migration | Product authority must move to Fund Capability structured data. Current `--tracking-error` remains a developer-only fallback and must be lower priority than extracted/calculated Capability data. Future implementation must add an explicit resolver with precedence: `direct_disclosure` > `calculated_from_series` > `developer_override` > `missing`; developer override is only legal in `developer_override` mode and must never be treated as product evidence. |
| Disclosed-vs-calculated tracking error path | First implementation slice should support disclosed tracking error extraction only when the value is directly disclosed in annual report text/table accessible through `FundDocumentRepository`. Calculated tracking error is a separate slice gated by fund/index series source contracts, formula, identity checks, cache, and provenance. If calculation prerequisites are not met, renderer and risk checks keep `missing` / `insufficient_data`. |
| External index series adapter upper bound | P13 first implementation must not build a broad external index data platform. If calculation is selected later, the upper bound is one read-only Capability data adapter for daily index level/return series, keyed by explicit index identity and benchmark mapping, with its own cache/provenance/failure taxonomy. It must not fetch methodology, constituents, all-index search, real-time quotes, or Service/UI-facing source APIs. |
| Methodology / constituents availability tiering | Methodology and constituents are tiered optional data. Benchmark text alone is Tier 1 and may only prove benchmark identity/reference. It must not replace methodology/constituents `数据不足`. Only Tier 2+ direct disclosure from repository-managed documents, or a separately accepted Tier 3 source contract, may replace those placeholders. |
| Positive acceptance criteria | This plan defines slice inputs/outputs, owned files, boundary rules, validation commands, review pass conditions, stop conditions, and residual owners. Future implementation is accepted only when each selected slice has typed fields, deterministic tests, missing-data behavior, and provenance-preserving renderer/audit/risk consumption. |
| Pure index fixture strategy | Use artificial deterministic text/table fixtures by default; do not download live documents during tests. Add a pure `index_fund` fixture, reuse/enrich existing `enhanced_index` fixture, and add missing-data fixtures. Real document excerpts are optional only if manually committed as minimal fixtures through repository-shaped `ParsedAnnualReport` objects, not through network or RR-13 data. |

## 3. Finding Disposition From P13-S1 Plan Reviews

| Review finding | Disposition in this revision |
|---|---|
| MiMo 01: `ExtractedField.extraction_mode` and `TrackingErrorValue.source_type` semantic gap | Closed by Section 8.4. `ExtractionMode` is not expanded. Product bundle `tracking_error` uses only `direct/derived/missing`; developer override is resolved outside `ExtractedField` in `ResolvedTrackingErrorForRisk`. |
| MiMo 02: renderer input pipe undefined | Closed by Section 10. Renderer must read `input_data.structured_data.index_profile` and `input_data.structured_data.tracking_error`; `TemplateRenderInput` shape stays unchanged unless a future review explicitly accepts a change. |
| MiMo 03 / GLM F1: `ResolvedTrackingErrorForRisk` fields and `run_risk_checks` migration undefined | Closed by Section 11.1. A concrete dataclass contract is defined, and `run_risk_checks` migrates to a single resolved-object path with no equal raw-scalar authority. |
| MiMo 04: composite benchmark could invite forbidden calculation | Closed by Sections 9.1, 9.3, 12 Slice C, and 15. Composite benchmark is accepted as structured context but calculated tracking error must return `missing` until a weighted composite contract exists. |
| MiMo 05: ambiguity fixture missing | Closed by Section 13. Ambiguous target/observed mixed text fixture is required and must return `missing` with `tracking_error_ambiguous`. |
| GLM F2: quality gate snapshot/FQ2/comparable_values policy missing | Closed by Section 11.3 and Slice H. First implementation records new fields in snapshot as non-comparable observability fields and does not add them to FQ2/comparable_values/golden denominator. |
| GLM F3: non-index `index_profile` behavior missing | Closed by Section 9.1. Non-index funds still receive an `ExtractedField(value=None, extraction_mode="missing")` for bundle shape consistency. |
| GLM F4: QDII tracking applicability undefined | Closed by Section 9.1. Current P13 applies tracking-error extraction only to `index_fund` and `enhanced_index`; `qdii_fund` remains not applicable until a later QDII subtype design. |

## 4. Goal

P13 should remove the user-visible `数据不足` gap for index and enhanced-index tracking-error analysis only when the project has traceable structured data. The smallest safe implementation target after this plan is:

1. Add an explicit Fund Capability data contract for index tracking error and index disclosure metadata.
2. Extract directly disclosed tracking error from repository-managed annual report content.
3. Route that structured field into renderer and risk checks without Service/UI/source leakage.
4. Preserve `数据不足` when the data is absent, ambiguous, calculated prerequisites are missing, or only benchmark text is available.

The plan deliberately treats tracking error as the priority. Index methodology and constituents remain optional tiered outputs and must not block the tracking-error slice.

## 5. Direct Evidence From Docs And Code

| Evidence | Source | Planning implication |
|---|---|---|
| Current main chain is deterministic UI -> Service -> Fund Capability; no LLM writing or external Dayu runtime. | `docs/design.md:22`, `docs/design.md:44-56` | P13 must not introduce Dayu Host/Engine/tool loop, LLM writing, or external runtime dependency. |
| Production document access goes through `FundDocumentRepository`; Service/UI do not read PDF/cache/source helpers. | `docs/design.md:62-70`, `docs/design.md:287` | Any annual report/prospectus/index document path must be exposed through repository/Capability contracts, not direct Service/UI calls. |
| Index funds and enhanced index funds prioritize tracking error in `preferred_lens`. | `docs/design.md:131-140` | Tracking-error data is a product-significant gap, not cosmetic renderer text. |
| Risk rule says tracking error over 2% is an index-fund veto condition. | `docs/design.md:184-192` | Risk checks need authoritative provenance, not ad hoc CLI values. |
| E1/E2/E3 and Evidence Confirm remain v2. | `docs/design.md:224-241` | P13 audit work must stay deterministic and not execute semantic evidence confirmation. |
| Existing data source table has annual report PDF, fund NAV, fund basic info, thermometer, selected pool; it does not define index series, methodology, or constituents source. | `docs/design.md:275-287` | External index series and methodology/constituents require explicit new source contracts before use. |
| Current `StructuredFundDataBundle` has profile/performance/manager/holdings/nav fields but no tracking-error/index fields. | `fund_agent/fund/data_extractor.py:63-99` | Future implementation needs explicit typed fields; no `extra_payload`. |
| Current renderer hardcodes index methodology, constituents, and tracking error as `数据不足`. | `fund_agent/fund/template/renderer.py:495-515`, `fund_agent/fund/template/renderer.py:569-593` | Renderer replacement rules must consume new structured fields only. |
| Current risk check receives `tracking_error` as an explicit parameter and returns `insufficient_data` when absent. | `fund_agent/fund/analysis/risk_check.py:173-210`, `fund_agent/fund/analysis/risk_check.py:485-540` | Future implementation must migrate source authority from Service override to Capability data while preserving insufficient-data behavior. |
| Current Service passes `resolved_contract.tracking_error` into `run_risk_checks`. | `fund_agent/services/fund_analysis_service.py:370-378` | Service override migration is required; otherwise two authority paths will coexist. |
| Current CLI exposes `--tracking-error` as a developer override and gates it behind `--dev-override`. | `fund_agent/ui/cli.py:81-83`, `fund_agent/ui/cli.py:688-760` | The CLI option can remain developer-only but must not be product authority. |
| `FundDocumentRepository` currently exposes only `load_annual_report()`. | `fund_agent/fund/documents/repository.py:267-318` | P13 first slice should use annual report only; any prospectus/index announcement method is a separate repository contract change. |
| Current fund NAV adapter only fetches fund NAV from akshare and has its own cache; it does not provide index NAV. | `fund_agent/fund/data/nav_data.py:38-76`, `fund_agent/fund/data/nav_data.py:99-122`, `fund_agent/fund/data/nav_data.py:184-222` | Calculated tracking error needs a new index series contract; it cannot be assumed from existing NAV support. |
| Existing fixtures include enhanced-index profile but no pure index profile fixture. | `tests/fixtures/fund/extractors/profile/index_enhanced_profile.txt`; no pure index fixture in `tests/fixtures/fund/extractors/profile/` | Future tests must add pure index fixture explicitly. |
| Control doc names this as the next gate and lists required P13-S1 planning constraints. | `docs/implementation-control.md:15-43`, `docs/implementation-control.md:96-105` | This plan must resolve constraints before implementation. |
| MiMo review flags extractability and methodology/constituents source scope. | `docs/reviews/next-phase-selection-plan-review-mimo-20260522.md` | Plan must separate direct disclosure, calculation, and optional index metadata. |
| GLM review flags service override migration, external adapter scope, and pure index fixtures. | `docs/reviews/next-phase-selection-plan-review-glm-20260522.md` | Plan must define authority precedence, adapter upper bound, and fixture strategy. |

## 6. Non-Goals

- Do not implement code in P13-S1.
- Do not modify `fund_agent/`, `tests/`, README files, `docs/design.md`, `docs/implementation-control.md`, `docs/repo-audit-20260521.md`, or RR-13 data in this planning gate.
- Do not auto-fix RR-13 duplicate `016492`.
- Do not introduce Dayu runtime, Host, Engine, tool loop, prompt scene registry, LLM writing, LLM audit, Evidence Confirm, E1/E2/E3 execution, or RepairContract execution.
- Do not let Service/UI/renderer/quality gate call concrete document sources, PDF cache, source helpers, download helpers, or external index adapters directly.
- Do not put explicit fields inside `extra_payload`; every field below must be typed and explicitly declared.
- Do not treat benchmark text as proof of tracking error, index methodology, or constituents.
- Do not infer tracking error from benchmark return, net value growth, or annual standard-deviation columns unless the calculated-series contract is implemented and accepted.
- Do not make index methodology or constituents required for P13 tracking-error acceptance.
- Do not add live network downloads to tests.

## 7. Source Contract

### 7.1 Source Classes

| Source class | Authority tier | Allowed in first implementation? | Contract |
|---|---:|---|---|
| Annual report direct disclosure | Tier A | Yes | Use existing `FundDocumentRepository.load_annual_report()` and extract only directly disclosed tracking-error text/table cells. |
| Prospectus / fund legal documents | Tier B | No, unless a future implementation gate explicitly adds repository methods | Must be accessed through `FundDocumentRepository`, with document identity, cache, provenance, and source failure taxonomy. |
| Calculated from fund NAV + index series | Tier C | No for the first direct-disclosure slice; optional later slice | Requires explicit fund NAV identity, index identity, date alignment, frequency, formula, minimum observations, cache, and failure taxonomy. |
| Developer override | Tier D | Only as dev-mode fallback | Explicit field from `FundAnalysisDeveloperOverrides.tracking_error`; lower authority than Capability data; never product evidence. |
| Benchmark text only | Not authority | Yes as context only | May identify the benchmark reference but cannot prove tracking-error value, methodology, or constituents. |

### 7.2 Source Failure Taxonomy

Reuse the annual-report taxonomy for repository-managed documents:

| Category | Meaning | Fallback |
|---|---|---|
| `not_found` | Source responds normally but target fund/document/year is absent | Eligible |
| `unavailable` | Network, timeout, service, or local dependency temporarily unavailable | Eligible |
| `schema_drift` | Response/table/field shape deviates from source contract | Fail closed |
| `identity_mismatch` | Returned candidate conflicts with fund code, document year, report type, benchmark/index identity, or requested period | Fail closed |
| `integrity_error` | Content type, file header, write integrity, date series integrity, or row-level numeric integrity fails | Fail closed |

For the first direct-disclosure implementation, extraction misses are not source failures. They produce `tracking_error.extraction_mode="missing"` with a note such as `年报未直接披露跟踪误差`.

For any future external index series adapter, define adapter-local equivalents before code:

- `index_not_found`: map to `not_found`.
- `index_unavailable`: map to `unavailable`.
- `index_schema_drift`: map to `schema_drift`.
- `index_identity_mismatch`: map to `identity_mismatch`.
- `index_series_integrity_error`: map to `integrity_error`.

### 7.3 External Index Series Adapter Upper Bound

If later accepted, the adapter must be limited to:

- Capability-owned module under `fund_agent/fund/data/`.
- One read-only method such as `load_index_series(index_id, start_date, end_date, *, force_refresh=False)`.
- Return daily date/value or date/return records only.
- Explicit source metadata: provider name, provider symbol, requested period, returned period, cached flag, fetched_at/update timestamp.
- Explicit identity checks: benchmark text to index identity mapping must be deterministic and reviewable; ambiguous benchmark baskets must return `missing`, not best-effort guessing.
- Cache format scoped to index series only; no cross-source search cache.
- No methodology scraping, constituents scraping, real-time quotes, all-index discovery, portfolio analytics, or UI/Service APIs.

If these upper bounds are insufficient to calculate tracking error, stop and split external index infrastructure into a later phase.

## 8. Data Model Contract

All fields are explicit typed fields. No explicit parameter may be hidden inside `extra_payload`.

### 8.1 New Structured Bundle Fields

Future implementation should extend `StructuredFundDataBundle` with:

```python
index_profile: ExtractedField[IndexProfileValue]
tracking_error: ExtractedField[TrackingErrorValue]
```

`index_profile` carries benchmark/index context and optional methodology/constituents. `tracking_error` carries the numeric tracking-error observation used by renderer and risk checks.

### 8.2 `IndexProfileValue`

```python
@dataclass(frozen=True, slots=True)
class IndexProfileValue:
    benchmark_text: str | None
    benchmark_identity_status: Literal["identified", "composite", "ambiguous", "missing"]
    benchmark_index_name: str | None
    benchmark_index_code: str | None
    benchmark_component_text: tuple[str, ...]
    methodology_availability: Literal[
        "direct_disclosure",
        "source_reference",
        "benchmark_only",
        "missing",
    ]
    methodology_summary: str | None
    methodology_source_title: str | None
    constituents_availability: Literal[
        "direct_disclosure",
        "source_reference",
        "benchmark_only",
        "missing",
    ]
    constituents_summary: str | None
    constituents_as_of_date: str | None
    source_tier: Literal["annual_report", "prospectus", "index_document", "benchmark_context", "missing"]
    missing_reasons: tuple[str, ...]
```

Rules:

- `benchmark_text` may be copied from existing `benchmark.value["benchmark_text"]`.
- `benchmark_identity_status="composite"` is required for blended benchmarks such as equity index plus cash deposit or bond index. Composite benchmark cannot be silently collapsed to one index.
- `methodology_availability="benchmark_only"` and `constituents_availability="benchmark_only"` must render as insufficient for methodology/constituents.
- `benchmark_index_code` is optional and must not be guessed from fund code.
- For non-index fund types, `index_profile` is still present on the bundle as `ExtractedField(value=None, extraction_mode="missing", anchors=(), note="非指数基金不适用指数画像")`; never make the bundle field itself optional.

### 8.3 `TrackingErrorValue`

```python
@dataclass(frozen=True, slots=True)
class TrackingErrorValue:
    value: Decimal
    value_text: str
    unit: Literal["ratio"]
    period_label: str
    period_start: str | None
    period_end: str | None
    annualized: bool
    source_type: Literal[
        "direct_disclosure",
        "calculated_from_series",
    ]
    calculation_method: Literal[
        "disclosed",
        "annualized_stddev_active_return",
    ]
    benchmark_identity_status: Literal["identified", "composite", "ambiguous", "missing"]
    benchmark_index_name: str | None
    benchmark_index_code: str | None
    fund_series_source: str | None
    index_series_source: str | None
    observation_count: int | None
    frequency: Literal["daily", "weekly", "monthly", "annual_report_period"]
    annualization_factor: Decimal | None
    input_period_complete: bool
    provenance_note: str
```

Rules:

- `value` must be normalized as a decimal ratio, e.g. `0.015` for `1.5%`.
- `value_text` preserves source formatting for renderer.
- `period_label` is mandatory because tracking error without period is not comparable.
- `annualized` is mandatory because annualized and non-annualized values are not interchangeable.
- `observation_count` and `annualization_factor` are required for calculated values and must be `None` only for direct disclosure.
- `source_type` deliberately excludes `developer_override`. Developer override is not an extracted Capability field and must not be stored in `StructuredFundDataBundle.tracking_error`.

### 8.4 Extraction Modes, Source Types, And Developer Override

Use existing `ExtractedField` semantics:

| Mode | Meaning |
|---|---|
| `direct` | Direct annual report/prospectus/document disclosure. |
| `derived` | Calculated from fund/index time series with complete provenance. |
| `estimated` | Not allowed for tracking error in P13; use `missing` instead. |
| `missing` | Data absent, ambiguous, conflict, or source contract unavailable. |

Explicit mapping:

| `ExtractedField.extraction_mode` | `TrackingErrorValue.source_type` | Where allowed | Meaning |
|---|---|---|---|
| `direct` | `direct_disclosure` | `StructuredFundDataBundle.tracking_error` | Observed tracking error directly disclosed in repository-managed document. |
| `derived` | `calculated_from_series` | `StructuredFundDataBundle.tracking_error` only after Slice G is accepted | Tracking error calculated from fund/index series with full provenance. |
| `missing` | no `TrackingErrorValue` value | `StructuredFundDataBundle.tracking_error` | Missing, ambiguous, composite benchmark for calculation, not applicable, or source contract unavailable. |
| `estimated` | not allowed | nowhere in P13 | Tracking error must not be estimated. |
| no `ExtractedField` mode | `developer_override` in `ResolvedTrackingErrorForRisk.source_type` only | Risk-check resolver only | Developer override is a dev-only scalar fallback and never product evidence. |

Decision:

- Do not expand `ExtractionMode` in P13.
- Do not wrap developer override inside `ExtractedField[TrackingErrorValue]`.
- Do not render developer override in the product report.
- Do not attach annual-report anchors to developer override.
- If a developer override is used for risk-check fixtures, `ResolvedTrackingErrorForRisk.is_product_evidence` must be `False` and `anchors=()`.

Anchor rules:

- Direct disclosure anchors use `source_kind="annual_report"` and exact section/table/row locator when available.
- Calculated values use `source_kind="derived"` anchors plus provenance notes that include formula and source names; source inputs must also be traceable.
- Benchmark anchors may be attached to `index_profile` as context, but must not be reused as proof of tracking error, methodology, or constituents.

## 9. Extraction / Calculation Decision Tree

### 9.1 Authority Resolution

```text
Start with fund_type from classified_fund_type.

Always construct index_profile as ExtractedField[IndexProfileValue].

If fund_type not in {index_fund, enhanced_index}:
  index_profile = ExtractedField(value=None, extraction_mode="missing", anchors=(), note="非指数基金不适用指数画像");
  tracking_error = ExtractedField(value=None, extraction_mode="missing", anchors=(), note="非指数基金不适用跟踪误差");
  risk_check tracking_error item remains pass/not_applicable for non-index types.

If fund_type == qdii_fund:
  current P13 treats tracking_error as not_applicable, because current FundType does not distinguish QDII index products from QDII active products;
  future QDII subtype design may opt specific QDII index products into tracking-error extraction.

If direct annual-report disclosure exists:
  tracking_error = ExtractedField(value=TrackingErrorValue(source_type="direct_disclosure"), extraction_mode="direct");
  use annual-report anchors;
  risk_check consumes this value.

Else if calculated-series contract is implemented and all inputs pass identity/integrity checks:
  tracking_error = ExtractedField(value=TrackingErrorValue(source_type="calculated_from_series"), extraction_mode="derived");
  use derived provenance plus source input anchors/provenance;
  risk_check consumes this value.

Else if benchmark identity is composite or ambiguous and only calculated path could provide tracking error:
  tracking_error = ExtractedField(value=None, extraction_mode="missing", anchors=(), note="复合或模糊基准暂不计算跟踪误差");
  renderer keeps 数据不足;
  risk_check returns insufficient_data for index/enhanced-index.

Else if developer_override is provided and request mode is developer_override:
  do not mutate StructuredFundDataBundle.tracking_error;
  resolve developer override only inside ResolvedTrackingErrorForRisk;
  renderer must not present developer override as product evidence.

Else:
  tracking_error = ExtractedField(value=None, extraction_mode="missing");
  renderer keeps 数据不足;
  risk_check returns insufficient_data for index/enhanced-index.
```

Acceptance for composite benchmark:

- Composite benchmark is a valid `index_profile.benchmark_identity_status`; it is not a source failure.
- Directly disclosed observed tracking error may still be consumed because the fund report itself supplies the value.
- Calculated tracking error must return `missing` for composite/ambiguous benchmarks until a weighted composite benchmark contract is accepted.

### 9.2 Direct Disclosure Extraction

Future direct-disclosure extractor should search annual report `§3` first, then relevant `§2` product/profile text if disclosed. It may use table parsing before free text because tracking error often appears in performance tables near standard deviation fields.

Accepted direct patterns must distinguish:

- Tracking error value: `跟踪误差 1.23%`, `年化跟踪误差 1.23%`, `日均跟踪偏离度 ... 跟踪误差 ...`.
- Tracking-error target/limit: `力争将跟踪误差控制在 ...` is not an observed value unless the text clearly says actual observed tracking error.
- Standard deviation columns: `份额净值增长率标准差` and `业绩比较基准收益率标准差` are not tracking error and must not be interpreted as tracking error.
- Benchmark return: `业绩比较基准收益率` is not tracking error.

If the extractor cannot distinguish actual observed tracking error from target/limit text, return `missing` with `missing_reasons=("tracking_error_ambiguous",)`.

### 9.3 Calculated Path Formula

Only implement after a separate implementation gate accepts the index series source contract.

Formula:

```text
fund_return_t = fund_nav_t / fund_nav_(t-1) - 1
index_return_t = index_level_t / index_level_(t-1) - 1
active_return_t = fund_return_t - index_return_t
tracking_error = stddev(active_return_t) * sqrt(annualization_factor)
```

Minimum contract:

- Same date calendar or deterministic join policy.
- Period must align with `report_year` unless explicitly labeled otherwise.
- Minimum observation count must be configured; below minimum returns `missing`.
- Annualization factor must be explicit and tied to frequency.
- Composite benchmark calculation is not allowed until a weighted composite benchmark contract exists.
- Fund NAV from current `FundNavDataAdapter` is not enough; the index side must be explicit.

### 9.4 Methodology / Constituents Tiering

| Tier | Data available | Renderer behavior |
|---|---|---|
| Tier 0 missing | No benchmark/index data | Render `数据不足` for benchmark, methodology, and constituents. |
| Tier 1 benchmark context | Existing annual-report benchmark text only | Render benchmark reference; methodology and constituents stay `数据不足`. |
| Tier 2 direct disclosure | Annual report/repository-managed document directly summarizes methodology or constituents | Render disclosed summary with anchors. |
| Tier 3 source reference | Accepted index document/source contract provides reference metadata but not full contents | Render source reference only; do not invent methodology/constituents. |
| Tier 4 external structured constituents | Separately accepted source contract provides dated constituent data | Render dated constituent summary with source/provenance. |

P13 first implementation may stop at Tier 1 for methodology/constituents while implementing tracking-error direct disclosure.

## 10. Renderer Consumption Rules

Renderer remains a Capability consumer of `TemplateRenderInput` and `StructuredFundDataBundle`; it must not call repository, document sources, PDF helpers, NAV adapters, or index adapters.

Renderer input pipe:

- Use `input_data.structured_data.index_profile` for Chapter 1 index methodology/constituents and benchmark context.
- Use `input_data.structured_data.tracking_error` for Chapter 2 tracking-error analysis.
- Preserve current `TemplateRenderInput` shape. Do not add top-level `index_profile` or `tracking_error` fields to `TemplateRenderInput` unless a future review proves `StructuredFundDataBundle` cannot carry the contract.
- Existing tests should update `_bundle()` helpers to populate the two new `ExtractedField` fields, matching the current pattern for `benchmark` and `nav_benchmark_performance`.

### 10.1 Chapter 1 `指数编制规则与成分股`

Replace only the relevant bullet:

- `业绩基准引用`: use `input_data.structured_data.index_profile.value.benchmark_text` when present, otherwise existing `benchmark_text`; evidence can be benchmark anchor.
- `编制方法`: replace `数据不足` only when `methodology_availability in {"direct_disclosure", "source_reference"}` and methodology value/source is present.
- `成分股`: replace `数据不足` only when `constituents_availability in {"direct_disclosure", "source_reference"}` and value/source is present.

Hard rule: benchmark anchors cannot be used as evidence for methodology/constituents. If only benchmark exists, renderer must keep the current insufficient text.

### 10.2 Chapter 2 `跟踪误差分析`

Replace `跟踪误差：数据不足` only when `tracking_error.extraction_mode in {"direct", "derived"}` and `tracking_error.value` is present with non-empty provenance.

Suggested output shape:

```text
#### 跟踪误差分析
- 跟踪误差：{value_text}（{period_label}，{annualized_text}，来源：{source_type_text}）。
- 后续最小验证：{next_minimum_verification_text}
- 证据边界：{anchors_or_provenance}
```

Rules:

- `developer_override` is not present in `input_data.structured_data.tracking_error`; renderer ignores it by construction.
- If direct disclosure lacks period or annualization status, renderer may show the value only with an explicit caveat if the data model marks those fields; otherwise keep `数据不足`.
- If calculated value exists, renderer must identify calculation method and input sources.

## 11. Risk Check, Audit, And Quality Gate Consumption Rules

### 11.1 Risk Check

Future implementation should introduce a Capability helper that resolves the risk-check input from structured tracking-error data and developer override:

```python
RiskTrackingErrorSource = Literal[
    "direct_disclosure",
    "calculated_from_series",
    "developer_override",
    "missing",
    "not_applicable",
]

RiskTrackingErrorAuthority = Literal[
    "capability_structured_data",
    "developer_override",
    "missing",
    "not_applicable",
]

@dataclass(frozen=True, slots=True)
class ResolvedTrackingErrorForRisk:
    value: Decimal | None
    value_text: str | None
    source_type: RiskTrackingErrorSource
    authority: RiskTrackingErrorAuthority
    field_extraction_mode: Literal["direct", "derived", "missing", "not_applicable"]
    anchors: tuple[EvidenceAnchor, ...]
    provenance_note: str
    missing_reason: str | None
    conflict_note: str | None
    is_product_evidence: bool

resolve_tracking_error_for_risk(
  tracking_error_field: ExtractedField[TrackingErrorValue],
  developer_override: str | None,
  developer_override_enabled: bool,
  fund_type: FundType,
) -> ResolvedTrackingErrorForRisk
```

The helper belongs in `fund_agent/fund/analysis/` or another Capability module, not UI.

Resolver precedence:

1. Non-index fund types return `source_type="not_applicable"`, `authority="not_applicable"`, `value=None`, `field_extraction_mode="not_applicable"`, `is_product_evidence=False`.
2. `tracking_error_field.extraction_mode in {"direct", "derived"}` with value present returns `authority="capability_structured_data"`, `is_product_evidence=True`, and ignores developer override for product authority.
3. If structured data is missing and developer override is present in developer mode, parse override and return `source_type="developer_override"`, `authority="developer_override"`, `anchors=()`, `is_product_evidence=False`.
4. Otherwise return `source_type="missing"`, `authority="missing"`, `value=None`, `missing_reason` from field note or resolver default.

Migration target:

- Use one path with no dual authority: migrate `run_risk_checks` from raw scalar `tracking_error: Decimal | str | int | float | None` to resolved object `tracking_error: ResolvedTrackingErrorForRisk`.
- Do not keep an equal fallback raw scalar parameter in `run_risk_checks`; any scalar developer override must be parsed before the call by `resolve_tracking_error_for_risk`.
- Product mode consumes Capability data only.
- Developer override only fills missing data in developer mode and never overrides extracted/calculated Capability data.
- If extracted/calculated value conflicts with developer override, product analysis uses extracted/calculated value; resolver may populate `conflict_note`, but `run_risk_checks` consumes the Capability value.
- `RiskCheckItem.anchors` for tracking error should use `ResolvedTrackingErrorForRisk.anchors`; developer override produces empty anchors and product renderer still ignores it.

### 11.2 Programmatic Audit

P13 audit remains deterministic. It may add checks such as:

- If Chapter 2 tracking-error bullet is not `数据不足`, there must be a `tracking_error` structured field with `direct` or `derived` mode.
- If tracking-error source is `direct`, at least one annual-report anchor must exist.
- If tracking-error source is `derived`, formula/source provenance must exist.
- If methodology/constituents bullets are not `数据不足`, they must have `index_profile` availability Tier 2+ or Tier 3+.
- Benchmark anchors may satisfy benchmark reference only; they must not satisfy tracking-error, methodology, or constituents proof.

Audit must not:

- execute E1/E2/E3 semantic evidence matching;
- call PDF search or Evidence Confirm;
- use LLMs;
- repair report text.

### 11.3 Quality Gate Snapshot / FQ2 / Comparable Values

First implementation policy:

- Add `index_profile` and `tracking_error` to extraction snapshot as observable fields only if the snapshot layer already has a fixed field registry that must mirror `StructuredFundDataBundle`.
- Do not add `index_profile` or `tracking_error` subfields to `comparable_values` in P13 first implementation.
- Do not add these fields to FQ2 coverage denominator, golden answer correctness denominator, or FQ0 strict preconditions in P13 first implementation.
- Existing quality gate status for funds without tracking-error golden data must not change solely because the new fields exist.
- Snapshot records should preserve `value`, `extraction_mode`, anchors, and note for debugging, but scoring treats them as non-comparable until a later golden-answer update phase.

Rationale:

- Tracking-error extraction is new and fixture-driven; immediately adding it to comparable/golden scoring would change gate behavior without a maintained golden source.
- Keeping it observable but non-comparable preserves provenance and avoids hidden regressions in renderer/risk tests.
- A later quality gate phase may promote `tracking_error.value_text`, `period_label`, `annualized`, `source_type`, and selected `index_profile` fields into `comparable_values` after golden-answer fixtures exist.

Validation:

- Existing quality gate / extraction snapshot tests continue to pass.
- Add or update a focused snapshot test only if implementation changes snapshot field enumeration.
- Assert `comparable_values` for `index_profile` and `tracking_error` is absent or empty in P13 first implementation.

## 12. Future Implementation Slices With File Ownership

These slices are for the future implementation gate. P13-S1 itself changes only this plan artifact.

### Slice A: Typed Models And Bundle Contract

- **Owner**: Fund Capability data/extractor contract.
- **Files likely changed**:
  - `fund_agent/fund/extractors/models.py`
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/extractors/` or `tests/fund/test_data_extractor.py` if present/created
- **Inputs**: existing `ExtractedField`, `StructuredFundDataBundle`, benchmark field.
- **Outputs**: explicit `IndexProfileValue`, `TrackingErrorValue`, and bundle fields.
- **Boundary**: no Service/UI source access; no `extra_payload`; do not expand `ExtractionMode`.
- **Acceptance**: bundle construction compiles; tests prove missing defaults, non-index `index_profile` missing behavior, typed field access, and developer override absence from `StructuredFundDataBundle.tracking_error`.

### Slice B: Direct Tracking-Error Extraction

- **Owner**: Fund Capability extractors.
- **Files likely changed**:
  - `fund_agent/fund/extractors/performance.py`
  - `fund_agent/fund/extractors/models.py`
  - `tests/fund/extractors/test_performance.py`
  - `tests/fixtures/fund/extractors/performance/*.txt`
- **Inputs**: `ParsedAnnualReport` from `FundDocumentRepository`.
- **Outputs**: `tracking_error: ExtractedField[TrackingErrorValue]`.
- **Boundary**: annual report only; no external index adapter; no calculation.
- **Acceptance**: direct disclosed value extracted with anchor; target/limit text, ambiguous mixed target/observed text, and standard-deviation columns do not become tracking error; missing path remains missing.

### Slice C: Index Profile Tier-1 Contract

- **Owner**: Fund Capability profile/index extractor.
- **Files likely changed**:
  - `fund_agent/fund/extractors/profile.py` or new `fund_agent/fund/extractors/index_profile.py`
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/extractors/test_profile.py`
  - `tests/fixtures/fund/extractors/profile/index_fund_profile.txt`
- **Inputs**: existing benchmark field and classification result.
- **Outputs**: `index_profile` with benchmark context and methodology/constituents Tier 0/1.
- **Boundary**: benchmark context only; no methodology/constituents claims unless direct source exists.
- **Acceptance**: pure index and enhanced index get benchmark context; non-index funds get missing `index_profile`; methodology/constituents remain insufficient when only benchmark exists; composite benchmark is accepted as context but does not enable calculated tracking error.

### Slice D: Service Migration For Risk Check

- **Owner**: Service orchestration plus Fund Capability risk helper.
- **Files likely changed**:
  - `fund_agent/fund/analysis/risk_check.py`
  - `fund_agent/services/fund_analysis_service.py`
  - `tests/fund/analysis/test_risk_check.py`
  - `tests/services/test_fund_analysis_service.py` if existing, otherwise closest service integration test
- **Inputs**: structured `tracking_error`, current developer override object.
- **Outputs**: risk checks consume `ResolvedTrackingErrorForRisk` only.
- **Boundary**: Service coordinates explicit fields; it does not parse sources or inspect repository internals.
- **Acceptance**: product mode uses extracted tracking error; missing extracted value keeps insufficient data; developer override is lower-priority dev fallback resolved before `run_risk_checks`; no equal raw-scalar tracking-error authority remains in `run_risk_checks`; conflict behavior tested.

### Slice E: Renderer Integration

- **Owner**: Fund Capability template renderer.
- **Files likely changed**:
  - `fund_agent/fund/template/renderer.py`
  - `tests/fund/template/test_renderer.py`
- **Inputs**: `input_data.structured_data.index_profile` and `input_data.structured_data.tracking_error`.
- **Outputs**: Chapter 1/2 replacements only when structured data is present.
- **Boundary**: renderer consumes structured fields only; no `TemplateRenderInput` shape change unless future review explicitly accepts it.
- **Acceptance**: index/enhanced-index reports replace tracking-error placeholder for direct data; active fund does not render index segments; benchmark-only path keeps methodology/constituents insufficient.

### Slice F: Deterministic Audit Rules

- **Owner**: Fund Capability programmatic audit.
- **Files likely changed**:
  - `fund_agent/fund/audit/contract_rules.py`
  - `fund_agent/fund/audit/audit_programmatic.py`
  - `fund_agent/fund/template/renderer.py` only if audit input needs explicit structured context
  - `tests/fund/audit/test_audit_programmatic.py`
  - `tests/fund/template/test_renderer.py`
- **Inputs**: rendered chapter blocks and structured field availability.
- **Outputs**: deterministic C2/P-style checks for source misuse.
- **Boundary**: no E1/E2/E3, no PDF search, no LLM.
- **Acceptance**: audit catches tracking-error text without structured data and methodology/constituents text backed only by benchmark anchors.

### Slice H: Snapshot Observability Without FQ2 Promotion

- **Owner**: Fund Capability quality gate / extraction snapshot, only if needed by bundle field enumeration.
- **Files likely changed**:
  - `fund_agent/fund/extraction_snapshot.py`
  - `tests/fund/test_extraction_snapshot.py` or the current snapshot test file
- **Inputs**: new `index_profile` and `tracking_error` fields.
- **Outputs**: snapshot observability records without `comparable_values` promotion.
- **Boundary**: no FQ2 denominator change; no golden answer schema change in P13 first implementation.
- **Acceptance**: existing quality gate status does not change solely due to new fields; new fields are absent from or empty in `comparable_values`.

### Slice G: Optional Calculated Tracking Error

- **Owner**: Future P13 follow-up only; not first implementation unless review explicitly accepts expanded scope.
- **Files likely changed**:
  - `fund_agent/fund/data/index_series.py`
  - `fund_agent/fund/analysis/tracking_error.py`
  - `tests/fund/data/test_index_series.py`
  - `tests/fund/analysis/test_tracking_error.py`
- **Inputs**: fund NAV series, index series, benchmark identity.
- **Outputs**: `TrackingErrorValue(source_type="calculated_from_series")`.
- **Boundary**: one adapter, no methodology/constituents, no UI/Service source access.
- **Acceptance**: deterministic fixture series produces expected value; insufficient observations, identity mismatch, composite benchmark, and unavailable index source return missing/fail-closed as appropriate.

## 13. Fixture Strategy

Use artificial deterministic fixtures as the default. They are smaller, stable, and avoid network or source-truth ambiguity.

Required fixtures for future implementation:

| Fixture | Purpose |
|---|---|
| `tests/fixtures/fund/extractors/profile/index_fund_profile.txt` | Pure index fund classification and benchmark context. |
| Existing `index_enhanced_profile.txt` enriched only if needed | Enhanced index classification path. |
| New performance fixture with directly disclosed observed tracking error | Positive extraction path. |
| New performance fixture with tracking-error target/limit only | Negative extraction path. |
| New performance fixture with ambiguous target and observed-looking tracking-error text mixed together | Ambiguity fail-safe path; must return `missing` with `tracking_error_ambiguous`. |
| New performance fixture with standard-deviation columns only | Prevent false positive from standard deviation. |
| New performance fixture with no tracking-error text | Missing path. |
| New performance fixture with composite benchmark and no direct tracking-error disclosure | Composite benchmark calculated-path missing behavior. |
| Optional in-memory daily fund/index series fixture | Calculated path only if Slice G is accepted. |

Rules:

- Tests construct `ParsedAnnualReport` directly or via existing fixture helpers.
- No live `FundDocumentRepository` downloads in tests.
- No RR-13 selected-pool CSV dependency.
- If a real document excerpt is used, store the minimal excerpt as a fixture and cite why artificial text is insufficient.

## 14. Tests And Validation Commands

### 14.1 P13-S1 Planning Gate Validation

Run after this artifact is created:

```bash
git status --short
git diff --name-only HEAD
git diff --check HEAD
```

Expected:

- Only `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` is modified/created.
- `docs/repo-audit-20260521.md` may remain untracked but is not edited, staged, deleted, or normalized.

### 14.2 Future Implementation Targeted Tests

Minimum targeted commands for direct-disclosure implementation:

```bash
pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_profile.py
pytest tests/fund/analysis/test_risk_check.py
pytest tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py
ruff check fund_agent tests
git diff --check HEAD
```

If Service migration is included:

```bash
pytest tests/fund/integration tests/services
```

If calculated tracking error is included:

```bash
pytest tests/fund/data/test_nav_data.py tests/fund/data/test_index_series.py tests/fund/analysis/test_tracking_error.py
```

Before implementation acceptance:

```bash
pytest
ruff check fund_agent tests
git diff --check HEAD
```

Full-suite pass count should be recorded by the future implementation artifact.

## 15. Positive Acceptance Criteria

A future implementation plan/code review may pass only if all selected slices satisfy these conditions:

1. Every new structured value is an explicit typed field, not an `extra_payload` entry.
2. Product-mode tracking error authority is Capability structured data, not Service-level override.
3. Developer override remains developer-only and has explicit precedence/conflict behavior.
4. Direct disclosure path has positive, negative, ambiguity, and missing tests.
5. Renderer reads new fields through `input_data.structured_data.index_profile` and `input_data.structured_data.tracking_error`; `TemplateRenderInput` shape remains unchanged unless explicitly justified and reviewed.
6. Renderer replaces `数据不足` only when structured data and provenance exist.
7. Risk check consumes `ResolvedTrackingErrorForRisk` through one resolved-object path and preserves `insufficient_data` for missing index/enhanced-index values.
8. `run_risk_checks` has no equal raw-scalar product authority for tracking error after migration.
9. QDII remains tracking-error not-applicable in P13 until a later subtype design opts QDII index products in.
10. Composite benchmark without direct disclosure returns missing for calculated tracking error and is covered by a fixture.
11. Non-index funds receive missing `index_profile` and missing/not-applicable tracking-error fields without optional bundle fields.
12. Quality gate snapshot policy is explicit: first implementation does not promote new fields into FQ2/comparable_values/golden denominator.
13. Benchmark anchors are not accepted as proof for tracking error, methodology, or constituents.
14. Methodology/constituents tiering is implemented or explicitly preserved as missing; benchmark-only does not upgrade them.
15. Any calculated-series path has source identity, formula, cache/provenance, minimum observation, and failure-taxonomy tests.
16. No Service/UI/renderer/quality gate direct source access is introduced.
17. No Dayu runtime, LLM writing, Evidence Confirm, or E1-E3 execution is introduced.
18. Tests cover pure `index_fund`, `enhanced_index`, active/non-index deletion path, ambiguity path, composite benchmark missing path, and missing-data path.
19. README/design/control updates are performed only in a later implementation gate when the actual public contract changes, not in P13-S1.

## 16. Review Criteria

Plan/code review must reject future implementation if:

- It starts from calculation before defining index series identity/source/cache/provenance.
- It lets benchmark return or standard-deviation columns masquerade as tracking error.
- It lets benchmark text prove methodology or constituents.
- It leaves both Service override and Capability extraction as equal product authorities.
- It hides explicit values in `extra_payload`.
- It stores developer override inside `StructuredFundDataBundle.tracking_error`.
- It changes `TemplateRenderInput` shape without explicit accepted justification.
- It leaves quality gate FQ2/comparable_values behavior implicit for the new fields.
- It introduces broad external index data infrastructure under the tracking-error slice.
- It adds live network fixture dependencies.
- It touches RR-13 data or `docs/repo-audit-20260521.md`.
- It updates design/control/README without an implementation-backed reason.
- It mixes E1/E2/E3 or Evidence Confirm into deterministic P13 audit.

Review should pass when the selected implementation can be regenerated from this plan without architectural guessing and the targeted tests prove both positive and fail-safe behavior.

## 17. Stop Conditions

Stop and return to controller if any of these occur:

- The only way to get tracking error is a broad external index data platform rather than the bounded adapter described above.
- Direct disclosure patterns cannot distinguish observed tracking error from target/limit text.
- Benchmark identity is composite or ambiguous and calculation would require unplanned weighted benchmark logic.
- Methodology/constituents require scraping index-company documents not covered by an accepted source contract.
- Product behavior requires Service/UI direct access to documents, source adapters, PDF cache, or download helpers.
- RR-13 source truth is needed.
- `docs/repo-audit-20260521.md` needs editing, staging, deletion, or publication.
- A reviewer requires E1/E2/E3, Evidence Confirm, LLM audit, or Dayu runtime as part of P13.
- Future validation shows unexpected source/test/README/design/control changes outside the accepted implementation scope.

## 18. Residual Owners

| Residual | Owner / destination | Handling |
|---|---|---|
| Direct tracking-error extraction | Future P13 implementation | Implement first if plan review accepts this artifact. |
| Service override migration | Future P13 implementation | Migrate product authority to Capability data; keep developer override lower-priority and dev-only. |
| Calculated tracking error from fund/index series | Future P13 follow-up or separate data-source phase | Requires bounded index series adapter and calculation contract before implementation. |
| Index methodology extraction | Future index document/source contract phase | Tiered optional; not a P13 first-slice blocker. |
| Index constituents extraction | Future index document/source contract phase | Tiered optional; not a P13 first-slice blocker. |
| E1/E2/E3 / Evidence Confirm | Future audit architecture phase | Keep separate from P13 deterministic data capability. |
| RR-13 duplicate `016492` | User / App source | Preserve human-owned; do not auto-fix. |
| `docs/repo-audit-20260521.md` | Controller / user | Keep excluded unless a later scope explicitly accepts publication/deletion/editing. |
| Repo-hygiene D-1/D-8-C5/C-9 | Future repo-hygiene phase | Do not mix into P13. |

## 19. Handoff Prompt For Future Implementation

```text
Gate: P13 tracking-error direct-disclosure implementation.

Use docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md as the accepted source-contract plan.

Implement only the selected direct-disclosure slices unless the controller explicitly accepts calculated-series scope:
- typed StructuredFundDataBundle fields for index_profile and tracking_error;
- direct annual-report tracking-error extraction via FundDocumentRepository-provided ParsedAnnualReport;
- pure index/enhanced/non-index/QDII-not-applicable/ambiguity/composite/missing fixtures;
- risk-check authority migration from service override to ResolvedTrackingErrorForRisk with no equal raw scalar authority;
- renderer replacement of tracking-error placeholder only via input_data.structured_data.tracking_error with structured provenance;
- snapshot observability without FQ2/comparable_values promotion for new fields;
- deterministic audit guards against benchmark-anchor misuse.

Do not modify RR-13 data or docs/repo-audit-20260521.md.
Do not add Dayu runtime, LLM, Evidence Confirm, E1-E3 execution, or Service/UI direct source access.
Stop if external index series, methodology, or constituents require a broader source contract.
```
