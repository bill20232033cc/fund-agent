# P19-S3 Thermometer-to-`valuation_state` Integration Plan（2026-05-23）

## Verdict

本计划建议 P19-S3 进入实现，但必须收窄范围：只把可确定映射到 P19-S1/S2 已支持指数的 A 股指数基金 / 指数增强基金自动映射为检查清单第 6 题 `valuation_state`；主动基金、债券基金、QDII、FOF、无基准、复合基准不确定、多个指数混合或未支持指数，全部返回 `unavailable` 灰灯。

第一性原理判断：自动估值状态会改变 `fund-analysis analyze` 的最终检查清单和最终判断派生路径，因此它不是 UI 便利功能，而是分析输入来源变更。P19-S3 的最小安全实现应先保证“显式输入优先、自动输入可追踪、不可用不强判、基金类型先行、Service/Capability 边界清楚”，而不是扩大覆盖率。

## Current Code Facts

- `FundAnalysisService.analyze()` 当前在 [fund_agent/services/fund_analysis_service.py](/Users/maomao/fund-agent/fund_agent/services/fund_analysis_service.py:391) 直接把 `request.valuation_state` 传给 `run_checklist()`。
- `FundAnalysisRequest.valuation_state` 当前默认是 `"unavailable"`，见 [fund_agent/services/fund_analysis_service.py](/Users/maomao/fund-agent/fund_agent/services/fund_analysis_service.py:138)。这会把“用户显式输入 unavailable”和“CLI 默认没有输入”混在一起。
- CLI `analyze` 当前 `--valuation-state` 默认 `"unavailable"`，见 [fund_agent/ui/cli.py](/Users/maomao/fund-agent/fund_agent/ui/cli.py:93)，因此 UI 层也无法表达“缺省时尝试自动温度计”。
- `run_checklist()` 第 6 题只消费 `valuation_state` 字符串，锚点为空，见 [fund_agent/fund/analysis/checklist.py](/Users/maomao/fund-agent/fund_agent/fund/analysis/checklist.py:416)。这不足以满足 `docs/design.md` §11.7 “自动映射必须在审计输入中保留温度值、数据日期、来源、指数代码、回溯窗口和 unavailable 原因”。
- `ThermometerService` 已支持 `ThermometerRequest.index_code/index_codes`，单指数返回 `ThermometerReading`，well-formed unsupported index 返回 item-level unavailable，不读 cache 绕过支持性校验，见 [fund_agent/services/thermometer_service.py](/Users/maomao/fund-agent/fund_agent/services/thermometer_service.py:200)。
- `ThermometerReading` 已包含 `valuation_state_candidate`、温度、PE/PB 分位、数据日期、lookback、source、cached/stale、unavailable reason，见 [fund_agent/fund/data/thermometer_types.py](/Users/maomao/fund-agent/fund_agent/fund/data/thermometer_types.py:53)。
- 当前 P19-S2 支持指数只有 `000300` 沪深300、`000905` 中证500，见 [fund_agent/fund/data/thermometer_source.py](/Users/maomao/fund-agent/fund_agent/fund/data/thermometer_source.py:22)。
- `IndexProfileValue.benchmark_index_code` 当前代码事实仍为 `None`，`index_profile` 主要保留 benchmark text / index name / component text，见 [fund_agent/fund/extractors/profile.py](/Users/maomao/fund-agent/fund_agent/fund/extractors/profile.py:671)。P19-S3 不能假设 P1 已有可用指数代码。

## Goals

- `fund-analysis analyze` 在用户没有显式传入 `--valuation-state` 时，尝试基于温度计自动解析检查清单第 6 题估值状态。
- 用户显式传入 `--valuation-state low/fair/high/unavailable` 时，必须完全优先，且不得调用温度计。
- 自动映射失败、基金类型不适用、指数不支持、温度计不可用或映射不确定时，统一得到 `ValuationState.UNAVAILABLE`，检查清单第 6 题灰灯，不输出红/黄/绿强判。
- 自动映射必须以 `ValuationStateResolution` 作为结构化真源进入 `TemplateRenderInput` 和 `ProgrammaticAuditInput`；`ChecklistItem.anchors/reason` 只是渲染投影，R1 审计不得从 reason 文本反推来源。结构化真源必须保留 index code/name、temperature、PE/PB percentile、data_date、lookback、source、cached/stale、unavailable_reason 和 disclaimer。
- 保持 UI → Service → Capability 边界：UI 只传显式参数；Service 编排抽取、质量 gate、映射和温度计调用；Capability 负责基金类型/基准映射、估值解析模型、检查清单和审计规则。

## Non-goals

- 不支持全 A 市场温度计；`wind_all_a` 仍等待 P19-S5 / all-A PE source gate。
- 不支持 QDII、债券、FOF 或非 A 股市场温度。
- 不把主动基金业绩基准温度默认当作基金估值状态；主动基金估值与持仓风格、行业暴露和基金经理交易不同源，P19-S3 先返回 `unavailable`。
- 不用有知有行公开页面 `FundThermometerAdapter` 作为 `analyze` 生产真源或 fallback。
- 不输出买入、卖出、仓位比例或短期择时信号。
- 不引入 Dayu Host/Engine/tool loop、LLM 写作、外部 runtime、`extra_payload` 或新付费数据源。

## Design Boundary

| Layer | P19-S3 responsibility | Must not do |
|---|---|---|
| UI | `fund_agent/ui/cli.py` 把 `--valuation-state` 解析为可区分“显式输入/未输入”的请求字段；可新增显式 `--thermometer-cache-dir`。 | 不解析基金类型，不匹配 benchmark，不调用 `ThermometerService`、akshare、cache 或 calculator。 |
| Service | `FundAnalysisService` 在抽取和 quality gate 后、`run_checklist()` 前解析 valuation state；注入温度计 provider 以便测试；保留 resolution 到 result。 | 不在 Service 中硬编码指数 alias、基金类型规则或审计格式；不访问 akshare / PDF / cache 文件细节。 |
| Capability analysis | 新增 valuation resolution / index target mapping 类型与规则；`run_checklist()` 消费 valuation resolution 并产生第 6 题锚点。 | 不做 IO，不调用 `ThermometerService`。 |
| Capability data | 继续由 `ThermometerService` 经 `ThermometerDataSource` / cache 取得 `ThermometerReading`。 | 不参与 checklist/final judgment。 |
| Capability audit/template | `TemplateRenderInput` 和 `ProgrammaticAuditInput` 显式携带 `ValuationStateResolution`；renderer 从 resolution 渲染报告主体/附录/免责标注，programmatic audit 从 resolution 校验证据完整性。 | 不重新计算温度，不调用外部数据；R1 不解析 `ChecklistItem.reason` 判断来源。 |

## Data Flow

```text
CLI analyze
  -> FundAnalysisRequest(
       valuation_state=None | explicit ValuationState,
       thermometer_cache_dir=None | Path,
       force_refresh=...
     )
  -> FundAnalysisService.analyze()
     -> _resolve_analyze_contract()
     -> _validate_request()
     -> FundDataExtractor.extract()
     -> run_quality_gate_for_bundle()
        - block: raise before thermometer call
     -> _extract_fund_type()
     -> resolve_valuation_state_for_analyze()
        - explicit valuation_state: build explicit resolution, no thermometer call
        - no explicit state:
            -> Capability maps fund_type + index_profile/benchmark to ValuationIndexTarget
            -> unsupported/ambiguous/missing: unavailable resolution, no thermometer call
            -> mapped index: ThermometerService.run(ThermometerRequest(index_code=...))
            -> ThermometerReading -> ValuationStateResolution
     -> run_checklist(..., valuation_resolution=...)
     -> derive_final_judgment()
     -> render_template_report(TemplateRenderInput(..., valuation_state_resolution=...))
     -> run_programmatic_audit(ProgrammaticAuditInput(..., valuation_state_resolution=...))
```

Placement after quality gate is intentional: if `quality_gate_policy=block` would reject the report, `analyze` should not perform extra external thermometer IO.

## Type And Interface Changes

### Service request/result

Change `FundAnalysisRequest`:

```python
valuation_state: ValuationState | None = None
thermometer_cache_dir: Path | None = None
```

Meaning:

- `None`: user did not explicitly provide valuation state; auto resolution is allowed.
- `"low" / "fair" / "high" / "unavailable"`: explicit user input; no thermometer call.

This is an intentional public contract change for P19-S3. Before P19-S3, omitted CLI/Service valuation input meant `unavailable` gray and no external thermometer IO. After P19-S3, omitted valuation input means “try automatic self-owned thermometer when the fund/index identity is safely supported.” The opt-out / legacy gray path is explicit:

- CLI: `fund-analysis analyze <fund_code> --valuation-state unavailable`
- Service: `FundAnalysisRequest(..., valuation_state="unavailable")`

Both opt-out forms must suppress thermometer calls exactly like explicit `low/fair/high`.

Change CLI `analyze`:

- `valuation_state: str | None = typer.Option(None, "--valuation-state", ...)`
- parse only when not `None`;
- keep invalid values as exit 2 via `typer.BadParameter`;
- CLI help must state: “不传则尝试自建温度计自动估值；传 unavailable 则手动灰灯且不调用温度计”；
- optional new `--thermometer-cache-dir Path` forwards to request for reproducible smoke/tests.

Change `FundAnalysisResult`:

```python
valuation_state_resolution: ValuationStateResolution
```

This gives tests and future UI a structured way to inspect whether valuation came from explicit input, thermometer, or unavailable mapping.

### Structured provenance truth

Choose `ValuationStateResolution` as the single structured truth. Do not add free-form-only metadata to `ChecklistItem` and do not let R1 infer source from checklist reason text.

Required propagation:

- `FundAnalysisResult.valuation_state_resolution`
- `TemplateRenderInput.valuation_state_resolution`
- `ProgrammaticAuditInput.valuation_state_resolution`

`ChecklistItem.anchors` remains useful for report evidence collection, but it is a projection of `ValuationStateResolution.anchors`. If checklist item reason, anchors and resolution disagree, `ProgrammaticAuditInput.valuation_state_resolution` wins for audit, and R1 should flag the inconsistency.

### Service dependency injection

Extend `FundAnalysisService.__init__`:

```python
def __init__(
    self,
    extractor: _FundDataExtractor | None = None,
    thermometer_service: _ThermometerService | None = None,
) -> None: ...
```

Protocol:

```python
class _ThermometerService(Protocol):
    async def run(
        self, request: ThermometerRequest
    ) -> ThermometerSnapshot | ThermometerReading | ThermometerBatchResult: ...
```

Production default uses `ThermometerService()`. Tests inject a fake and assert call/no-call behavior.

### Capability valuation model

Add `fund_agent/fund/analysis/valuation_state.py`:

```python
ValuationStateSource = Literal[
    "explicit_user_input",
    "self_owned_thermometer",
    "unavailable_mapping",
    "unavailable_thermometer",
]

ValuationIndexTargetStatus = Literal[
    "mapped",
    "unsupported_fund_type",
    "missing_benchmark",
    "ambiguous_benchmark",
    "unsupported_index",
]
```

Dataclasses:

- `ValuationIndexMappingRule`: `index_code`, `index_name`, `aliases`, `supported_fund_types`
- `ValuationIndexTarget`: `status`, `index_code`, `index_name`, `reason`, `anchors`
- `ValuationStateResolution`: `state`, `source`, `reason`, `anchors`, `disclaimer_required`, plus optional thermometer fields (`index_code`, `index_name`, `temperature`, `pe_percentile`, `pb_percentile`, `data_date`, `lookback_start`, `lookback_end`, `thermometer_source`, `cached`, `stale`, `unavailable_reason`, `disclaimer`)

Minimum provenance fields:

- `source`
- `state`
- `reason`
- `anchors`
- for `source="self_owned_thermometer"` and `state != "unavailable"`: `index_code`, `index_name`, `temperature`, `pe_percentile`, `pb_percentile`, `data_date`, `lookback_start`, `lookback_end`, `thermometer_source`, `cached`, `stale`, `disclaimer`
- for `source="unavailable_thermometer"`: `index_code` when known, `unavailable_reason`, `thermometer_source` when known, `disclaimer`
- for `source="explicit_user_input"`: no thermometer fields required; must carry a `derived` user-input anchor

Public functions:

- `resolve_valuation_index_target(fund_type, index_profile, benchmark) -> ValuationIndexTarget`
- `build_explicit_valuation_resolution(state) -> ValuationStateResolution`
- `build_unavailable_valuation_resolution(target_or_reason) -> ValuationStateResolution`
- `build_thermometer_valuation_resolution(reading: ThermometerReading) -> ValuationStateResolution`

### Checklist contract

Prefer updating `run_checklist()` to consume a resolution object:

```python
def run_checklist(..., valuation_resolution: ValuationStateResolution | None = None, ...) -> ChecklistResult:
```

Compatibility inside Capability can derive `valuation_state` from the resolution. If `valuation_resolution is None`, keep existing explicit `valuation_state` path for low-risk migration in unit tests, but Service should use the new argument.

`_check_valuation()` should use:

- `resolution.state` for signal/status;
- `resolution.anchors` for `ChecklistItem.anchors`;
- source-specific reason text:
  - explicit: “用户显式输入当前估值状态为 ...”
  - thermometer available: “自建温度计显示 ...，温度 ...，指数 ...，数据日 ...”
  - unavailable: “自动估值不可用：...”

### Evidence anchors and disclaimer

Use existing `EvidenceAnchor.source_kind` values:

- explicit user input: `source_kind="derived"`, `section_id="user_input"`, `row_locator="valuation_state"`
- thermometer available: `source_kind="external_api"`, `section_id="thermometer"`, `table_id=reading.source`, `row_locator=f"{reading.index_code}:{reading.data_date}"`, `note` contains temperature, PE/PB percentile, state, lookback, cached/stale, disclaimer.
- unavailable mapping/thermometer: `source_kind="derived"` or `external_api` when a thermometer reading exists but unavailable; `note` must include unavailable reason.

Renderer already supports non-annual anchors, so no custom appendix format is required unless tests expose wording gaps.

Disclaimer is not optional anchor decoration. When an automatic path actually calls the self-owned thermometer and receives either an available, stale-cache, or unavailable thermometer reading, the report body or stable evidence section must contain an equivalent user-visible statement:

```text
本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。
计算方法：等权 PE/PB 中位数历史分位数综合。
与有知有行官方温度计可能存在合理偏差，仅供投资前风险检查参考。
```

Unsupported fund type / missing benchmark / ambiguous benchmark paths that do not call thermometer do not need this disclaimer, but must explain why valuation is gray/unavailable.

The rendered disclaimer must not contain project forbidden trading-advice terms such as `买入`, `卖出`, `仓位比例`, or `收益预测`. Use equivalent wording that does not trigger `_validate_report_wording()`, such as the statement above.

## Mapping Rules

P19-S3 support is intentionally narrow and config-driven.

### Supported fund types

| Fund type | P19-S3 auto mapping | Reason |
|---|---:|---|
| `index_fund` | Yes, if benchmark maps to exactly one supported index. | Product objective is tracking the index. |
| `enhanced_index` | Yes, if benchmark maps to exactly one supported index. | Beta exposure is still anchored to a target index; alpha is analyzed elsewhere. |
| `active_fund` | No, return `unavailable`. | Benchmark valuation is not same-source evidence for active holdings valuation. Future support needs holdings/style exposure mapping. |
| `bond_fund` | No, return `unavailable`. | A 股 equity PE/PB thermometer is not applicable. |
| `qdii_fund` | No, return `unavailable`. | P19 excludes non-A-share market temperature. |
| `fof_fund` | No, return `unavailable`. | FOF valuation requires child-fund exposure, not one broad index. |

### Supported indices

P19-S3 only supports P19-S1/S2 accepted coverage:

| Index | Code | Alias examples |
|---|---|---|
| 沪深300 | `000300` | `沪深300`, `沪深 300`, `沪深300指数`, `CSI 300` |
| 中证500 | `000905` | `中证500`, `中证 500`, `中证500指数`, `CSI 500` |

Rules must live in one Capability mapping config/dataclass tuple, not scattered string checks in Service.

### Benchmark decision rules

1. If `index_profile.value.benchmark_index_code` is present and supported, map directly.
2. Else inspect `index_profile.value.benchmark_index_name`, `index_profile.value.benchmark_text`, and `benchmark_component_text`.
3. Normalize each benchmark component, not the full raw string only:
   - trim whitespace;
   - remove spaces between Chinese/ASCII index tokens;
   - normalize full-width punctuation;
   - strip return-rate suffixes only when they are pure benchmark measurement suffixes, such as `指数收益率`, `收益率`, `价格指数收益率`, `全收益指数收益率`.
4. Match only component-level exact index identity. Substring alias matching is forbidden.
5. Allowed identity forms for P19-S3 are limited to:
   - `沪深300`, `沪深300指数`, `CSI300`, `CSI 300`
   - `中证500`, `中证500指数`, `CSI500`, `CSI 500`
6. If exactly one supported equity index component has exact identity and all other components are cash/bond/non-equity benchmark components, map to that supported index.
7. If no supported exact identity is found, return `unsupported_index` or `missing_benchmark`.
8. If more than one supported equity index exact identity is found, return `ambiguous_benchmark`.
9. If a supported alias is embedded inside a longer equity index name, return `unsupported_index` or `ambiguous_benchmark`; do not strip style/strategy/sector modifiers.
10. If any unsupported equity index component appears beside a supported component, return `ambiguous_benchmark`; do not choose the supported component by weight.
11. If component parsing is uncertain, return `ambiguous_benchmark`.

Unsupported and ambiguous outcomes are not errors. They become `ValuationState.UNAVAILABLE` with a gray checklist item.

### Negative identity examples

The following benchmark components must not map to `000300` / `000905` even though they contain a supported alias:

| Benchmark component | Required outcome | Reason |
|---|---|---|
| `沪深300价值指数收益率` | `unsupported_index` | style-derived index, not broad CSI 300 body. |
| `沪深300成长指数收益率` | `unsupported_index` | style-derived index. |
| `沪深300红利低波动指数收益率` | `unsupported_index` | dividend/low-vol strategy index. |
| `沪深300低波指数收益率` | `unsupported_index` | low-vol strategy index. |
| `沪深300等权重指数收益率` | `unsupported_index` | equal-weight variant. |
| `沪深300行业中性指数收益率` | `unsupported_index` | strategy/industry-neutral variant. |
| `中证500质量成长指数收益率` | `unsupported_index` | quality/growth strategy index. |
| `中证500价值指数收益率` | `unsupported_index` | style-derived index. |
| `中证500低波动指数收益率` | `unsupported_index` | low-vol strategy index. |
| `中证500等权重指数收益率` | `unsupported_index` | equal-weight variant. |
| `中证500医药卫生指数收益率` | `unsupported_index` | sector variant. |
| `沪深300指数收益率*50% + 中证500指数收益率*50%` | `ambiguous_benchmark` | two supported equity indices; no single index temperature. |
| `沪深300指数收益率*80% + 中证全债指数收益率*20%` | map `000300` | one supported equity index plus bond component is acceptable. |
| `中证500质量成长指数收益率*95% + 银行活期存款利率*5%` | `unsupported_index` | equity component is an unsupported derived index even with cash component. |

Implementation tests must include these exact examples or equivalent fixtures. The matcher should prefer fail-closed `unavailable` over coverage when unsure.

## Failure Semantics

| Scenario | Behavior | Exit / audit |
|---|---|---|
| User passes explicit `--valuation-state high` | Use `high`; no thermometer call. | analyze continues; valuation item red with derived user-input anchor. |
| User passes explicit `--valuation-state unavailable` | Use `unavailable`; no thermometer call. | analyze continues; valuation item gray. |
| User omits `--valuation-state`; mapped thermometer available | Use `reading.valuation_state_candidate`. | analyze continues; evidence anchor must include thermometer fields. |
| Fund type unsupported for auto mapping | `unavailable`. | analyze continues; gray item with mapping reason. |
| Benchmark missing/ambiguous/unsupported | `unavailable`. | analyze continues; gray item with reason and available benchmark anchors. |
| `ThermometerReading.unavailable=True` | `unavailable`. | analyze continues; gray item with unavailable reason. |
| `ThermometerCalculationError` or equivalent self-owned thermometer calculation/data-quality exception during auto path | `unavailable` with precise reason. | analyze continues; gray item; Service test required. |
| Unexpected impossible return type from thermometer provider | Raise `ValueError`. | fail closed as programming contract error. |
| Quality gate `block` before valuation | Raise existing quality gate error; do not call thermometer. | CLI exit 2 as today. |
| Invalid CLI valuation value | CLI validation error. | exit 2. |

Important: automatic thermometer failure must never be converted to `low/fair/high` by fallback to public-page data. Stale self-owned cache may be used only through existing `ThermometerService` self-owned index path and must keep `cached=True`, `stale=True` in evidence.

The auto integration layer may catch only expected self-owned thermometer data/calculation exceptions, such as `ThermometerCalculationError` or an explicitly named project exception with equivalent semantics. It must not catch broad `Exception`. Programming contract errors remain fail-closed, including a provider returning `ThermometerSnapshot`, `ThermometerBatchResult`, `None`, or a reading whose `valuation_state_candidate` is outside `low/fair/high/unavailable`.

## Audit And Evidence Plan

Update programmatic audit under existing checklist rule family (`R1`) rather than creating a new rule code in P19-S3. This is an evidence completeness extension of R1, not a new audit rule family.

R1 must use `ProgrammaticAuditInput.valuation_state_resolution` as the source of truth. It must not infer source from `ChecklistItem.reason`.

Add checks in `_audit_checklist_rules()` or a helper called from R1:

- checklist must still contain exactly 7 items;
- valuation item must exist;
- `valuation_item.signal/status` must match `valuation_state_resolution.state`;
- `valuation_item.anchors` must equal or be a superset of `valuation_state_resolution.anchors`;
- if `resolution.source == "self_owned_thermometer"` and `resolution.state != "unavailable"`:
  - required structured fields must be non-empty: `index_code`, `index_name`, `temperature`, `pe_percentile`, `pb_percentile`, `data_date`, `lookback_start`, `lookback_end`, `thermometer_source`, `cached`, `stale`, `disclaimer`;
  - at least one resolution anchor must have `source_kind="external_api"`;
  - the external anchor must identify the same index/data date/source as the structured fields;
  - report-rendered provenance must include disclaimer.
- if `resolution.source == "explicit_user_input"`:
  - thermometer fields are not required;
  - at least one `derived` user-input anchor is required.
- if `resolution.source in {"unavailable_mapping", "unavailable_thermometer"}`:
  - `resolution.state` must be `unavailable`;
  - `reason` or `unavailable_reason` must be non-empty;
  - if thermometer was called and unavailable, disclaimer is required and thermometer source/index should be preserved when known.

Renderer coverage:

- Chapter 7 already renders checklist items and `_collect_checklist_anchors()`.
- Add/adjust tests so thermometer and unavailable valuation anchors appear in `## 证据与出处` through the existing non-annual anchor renderer.
- Add report-output tests that assert the disclaimer text appears when `ValuationStateResolution.disclaimer_required=True`, not merely inside an anchor note.
- Add renderer tests that the disclaimer does not trigger `_validate_report_wording()` and does not weaken the existing forbidden-term validation for `买入` / `卖出` / `仓位比例` / `收益预测`.

## Implementation Slices

### Slice 1: Valuation Resolution Types And Mapping

Files:

- `fund_agent/fund/analysis/valuation_state.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_valuation_state.py`

Work:

- Define mapping rules for `000300` and `000905`.
- Implement fund-type gate and component-level exact benchmark identity matching; substring alias matching is forbidden.
- Build explicit/unavailable/thermometer resolution constructors.
- Unit-test supported, unsupported, missing and ambiguous mappings, including the negative identity examples listed above.

### Slice 2: Checklist Evidence Integration

Files:

- `fund_agent/fund/analysis/checklist.py`
- `tests/fund/analysis/test_checklist.py`

Work:

- Let `run_checklist()` accept `valuation_resolution`.
- Update `_check_valuation()` to use resolution anchors/reason.
- Preserve existing direct `valuation_state` behavior for tests not yet migrated.
- Add tests for thermometer low/fair/high signals, explicit input, unavailable gray, and anchors.
- Add tests that checklist output is only a projection of resolution and does not invent thermometer provenance.

### Slice 3: FundAnalysisService Orchestration

Files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_fund_analysis_service.py`

Work:

- Change request default to `valuation_state=None`.
- Add thermometer provider injection and optional `thermometer_cache_dir`.
- Resolve valuation after quality gate and fund type extraction, before checklist.
- Add `valuation_state_resolution` to result and pass the same object to `TemplateRenderInput` / `ProgrammaticAuditInput`.
- Tests must assert explicit input suppresses thermometer calls, default auto calls only for supported index/enhanced mappings, unsupported types do not call thermometer, quality gate block does not call thermometer, and unavailable reading produces gray.
- Add Service tests where fake thermometer raises `ThermometerCalculationError` or equivalent self-owned calculation/data-quality exception: auto path must return unavailable gray and preserve precise reason.
- Add Service tests where fake thermometer returns an impossible type (`ThermometerSnapshot`, `ThermometerBatchResult`, `None`) or invalid candidate: analyze must fail closed with `ValueError`.

### Slice 4: CLI Analyze Contract

Files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Work:

- Make `--valuation-state` default `None` so absence means auto.
- Keep explicit `--valuation-state unavailable` as a manual gray override.
- Add optional `--thermometer-cache-dir`.
- Update CLI help to document the intentional default change and opt-out path.
- Update CLI tests to assert request fields, explicit unavailable suppresses auto, help mentions auto/opt-out semantics, and invalid valuation exits 2.

### Slice 5: Audit/Renderer Evidence

Files:

- `fund_agent/fund/audit/audit_programmatic.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `tests/fund/template/test_renderer.py`

Work:

- Add R1 checks for valuation item evidence completeness.
- Add `valuation_state_resolution` to `TemplateRenderInput` and `ProgrammaticAuditInput`.
- Add renderer/audit tests for external_api thermometer anchors, unavailable derived anchors, and disclaimer output when thermometer was called.
- Add R1 tamper tests: automatic non-unavailable resolution without external anchor fails; missing lookback/data_date/temperature/source fails; automatic high with only derived anchor fails; explicit high without thermometer fields passes.

### Slice 6: Docs

Files:

- `README.md`
- `fund_agent/README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Work:

- Root README: document `fund-analysis analyze` default auto valuation behavior, explicit override, and unsupported gray semantics.
- Root README and CLI examples must call out this intentional public contract change: omitted `--valuation-state` now allows auto; `--valuation-state unavailable` restores old manual gray/no-thermometer behavior.
- Fund README: document valuation resolution model and supported P19-S3 scope.
- Developer README: mention Service orchestration boundary.
- Tests README: mention new valuation mapping/audit test layer.

## Test Matrix

| Area | Case | Expected |
|---|---|---|
| Mapping | `index_fund` + 沪深300 benchmark | target `000300` mapped |
| Mapping | `enhanced_index` + 中证500 benchmark | target `000905` mapped |
| Mapping | `active_fund` + 沪深300 benchmark | unavailable, no thermometer |
| Mapping | `bond_fund` / `qdii_fund` / `fof_fund` | unavailable, no thermometer |
| Mapping | missing benchmark | unavailable reason `missing_benchmark` |
| Mapping | multiple supported indices | unavailable reason `ambiguous_benchmark` |
| Mapping | unsupported index name | unavailable reason `unsupported_index` |
| Mapping | `沪深300价值指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `沪深300成长指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `沪深300红利低波动指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `沪深300等权重指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `中证500质量成长指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `中证500低波动指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `中证500等权重指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `中证500医药卫生指数收益率` | unsupported/unavailable, no thermometer |
| Mapping | `沪深300指数收益率*50% + 中证500指数收益率*50%` | ambiguous/unavailable, no thermometer |
| Mapping | `沪深300指数收益率*80% + 中证全债指数收益率*20%` | target `000300` mapped |
| Checklist | thermometer `low` | valuation item green/pass with external_api anchor |
| Checklist | thermometer `fair` | valuation item yellow/watch with external_api anchor |
| Checklist | thermometer `high` | valuation item red/block with external_api anchor |
| Checklist | unavailable resolution | valuation item gray/insufficient_data with reason |
| Checklist | explicit `high` resolution | red/block with derived user-input anchor; no thermometer provenance required |
| Service | explicit `valuation_state="high"` | no thermometer call; result source explicit |
| Service | explicit `valuation_state="unavailable"` | no thermometer call; gray |
| Service | absent valuation + mapped index | one `ThermometerRequest(index_code=...)` |
| Service | absent valuation + unsupported fund type | no thermometer call; gray |
| Service | thermometer unavailable reading | gray; audit passes |
| Service | fake thermometer raises `ThermometerCalculationError` | gray unavailable, analyze continues, precise reason retained |
| Service | fake thermometer returns `ThermometerSnapshot`/batch/`None` | fail closed with `ValueError` |
| Service | quality gate block | no thermometer call |
| Service | `force_refresh=True` | forwarded to thermometer request only when auto call happens |
| CLI | no `--valuation-state` | request valuation_state `None` |
| CLI | help text | documents default auto and explicit unavailable opt-out |
| CLI | `--valuation-state low` | request valuation_state `"low"` |
| CLI | `--valuation-state unavailable` | request explicit unavailable; suppress auto |
| CLI | invalid valuation | exit 2 |
| Audit | auto valuation without resolution | R1 issue |
| Audit | auto valuation without external_api anchor | R1 issue |
| Audit | auto valuation resolution missing temperature/data_date/source/lookback | R1 issue |
| Audit | auto valuation uses only derived anchor | R1 issue |
| Audit | explicit high lacks thermometer fields | passes R1 if source is explicit and user-input anchor exists |
| Renderer | report appendix includes thermometer anchor | non-annual anchor rendered |
| Renderer | thermometer was called | report contains disclaimer text outside fragile reason-only inference |
| Renderer | disclaimer wording | does not contain forbidden trading-advice terms and does not trigger `_validate_report_wording()` |

Targeted validation command:

```text
.venv/bin/python -m pytest \
  tests/fund/analysis/test_valuation_state.py \
  tests/fund/analysis/test_checklist.py \
  tests/services/test_fund_analysis_service.py \
  tests/ui/test_cli.py \
  tests/fund/audit/test_audit_programmatic.py \
  tests/fund/template/test_renderer.py -q

.venv/bin/python -m ruff check fund_agent tests
git diff --check
```

Final validation should run full suite:

```text
.venv/bin/python -m pytest -q
```

## Exit Criteria

- `fund-analysis analyze` absent `--valuation-state` attempts auto valuation only for supported index/enhanced mappings.
- The default change from `unavailable` to `None` is documented as an intentional public contract change in code comments/help/README; `--valuation-state unavailable` and `FundAnalysisRequest(valuation_state="unavailable")` restore the old manual gray/no-thermometer behavior.
- Explicit `--valuation-state` always wins and suppresses thermometer calls, including explicit `unavailable`.
- Unsupported fund type, unsupported/ambiguous/missing benchmark and thermometer unavailable all produce `ValuationState.UNAVAILABLE` and gray checklist第 6 题.
- Benchmark identity matching is component-level exact matching only; substring alias matching is forbidden and negative derived/strategy/style/sector/equal-weight/low-vol examples are tested.
- Available thermometer mapping changes第 6 题 signal according to `low/fair/high` and can influence final judgment through existing checklist/final-judgment rules.
- `ValuationStateResolution` is the structured truth in `FundAnalysisResult`, `TemplateRenderInput` and `ProgrammaticAuditInput`; R1 does not infer valuation source from reason text.
- Report evidence appendix includes valuation source details for explicit, thermometer and unavailable paths.
- When self-owned thermometer was called, CLI/report output contains the required independent-methodology disclaimer, not only an anchor note.
- Rendered disclaimer wording avoids forbidden trading-advice terms and passes existing report wording validation without weakening the forbidden-term guard.
- Programmatic audit fails if an automatic non-unavailable valuation lacks structured thermometer provenance, external_api anchor, index/date/temperature/PE/PB/source/lookback, or uses only a derived anchor.
- Expected self-owned thermometer calculation/data-quality exceptions in the auto path become unavailable gray with a precise reason; impossible provider return types and programming contract errors still fail closed.
- No use of `FundThermometerAdapter` public-page data in analyze integration.
- No all-A / PB-only / QDII / bond / FOF thermometer support is introduced.
- Targeted tests, full pytest, ruff and diff-check pass.
- README updates match implemented behavior and do not describe future unsupported coverage as current behavior.

## Residual Risks

- Benchmark text mapping remains weaker than a true index identity extractor because current `benchmark_index_code` is not populated. P19-S3 mitigates by supporting only exact configured aliases and returning unavailable on ambiguity.
- Active fund valuation remains unresolved. This is an intentional safety tradeoff; using broad benchmark temperature would be same-source weak and could create false confidence.
- Live akshare availability and schema stability remain external-data risks. P19-S3 must rely on existing self-owned index `ThermometerService` unavailable/stale-cache semantics and fixture tests, not live tests.
- Stale cache evidence may be misunderstood as fresh. P19-S3 must carry `cached` and `stale` flags into `ValuationStateResolution`, report evidence and reason text.
- `ValuationStateResolution` adds a new structured input to renderer/audit. The resolution object is the single source after Service resolution; checklist reason/anchors are projections and must not become a competing truth.
- Default `FundAnalysisRequest(fund_code=...)` now allows automatic thermometer IO after quality gate. This is intentional for P19-S3 but remains a public behavior change that README/help/tests must make explicit.
- Enhanced-index mapping remains conservative: only exact supported broad-index identity plus cash/bond components maps automatically; strategy/enhanced/derived target index names stay unavailable until a dedicated index identity extractor improves confidence.
