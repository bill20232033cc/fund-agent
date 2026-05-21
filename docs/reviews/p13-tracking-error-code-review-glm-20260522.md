# Code Review

## Scope

- Mode: current changes
- Branch: `feat/p13-tracking-error-direct-disclosure`
- Base: `main`
- Output file: `docs/reviews/p13-tracking-error-code-review-glm-20260522.md`
- Included scope:
  - `fund_agent/fund/extractors/models.py` — `IndexProfileValue`, `TrackingErrorValue` typed models
  - `fund_agent/fund/extractors/profile.py` — `index_profile` extraction, composite benchmark detection
  - `fund_agent/fund/extractors/performance.py` — direct tracking-error extraction from `§3/§2`
  - `fund_agent/fund/extractors/__init__.py` — public export expansion
  - `fund_agent/fund/data_extractor.py` — `StructuredFundDataBundle` fields, fund-type applicability gate
  - `fund_agent/fund/analysis/risk_check.py` — `ResolvedTrackingErrorForRisk`, `resolve_tracking_error_for_risk`, `run_risk_checks` migration
  - `fund_agent/fund/analysis/__init__.py` — public export expansion
  - `fund_agent/fund/template/renderer.py` — tracking-error and index-profile renderer consumption
  - `fund_agent/fund/audit/audit_programmatic.py` — tracking-error and index-profile source guard audits
  - `fund_agent/fund/extraction_snapshot.py` — snapshot field order, observable-only policy
  - `fund_agent/services/fund_analysis_service.py` — Service resolver call
  - `fund_agent/fund/README.md`, `tests/README.md` — documentation sync
  - Tests and fixtures under `tests/fund/`
- Excluded scope: `docs/repo-audit-20260521.md` (out-of-scope untracked)
- Parallel review coverage: 无；单 reviewer 全链路走读

## Findings

### F1-未修复-低-复合基准拆分仅处理 `+`/`＋`，遗漏 `和`/`及`/`×`/`*` 分隔符

- **入口/函数**: `_benchmark_components`
- **文件(行号)**: `fund_agent/fund/extractors/profile.py:588-595`
- **输入场景**: 业绩比较基准包含 `和`/`及`/`×`/`*` 分隔符但不包含 `+`/`＋`，例如 `"沪深300指数和中证500指数"`
- **实际分支**: `_COMPOSITE_BENCHMARK_SEPARATORS` 存在性检查命中 `"和"`，进入 split 分支；`re.split(r"[＋+]", benchmark_text)` 因无 `+`/`＋` 不拆分，返回 `(benchmark_text,)` 单元素元组
- **预期行为**: 按 plan Section 9.1 要求，含多分隔符的复合基准应返回多组成部分并标记 `benchmark_identity_status="composite"`
- **实际行为**: `components` 为单元素，`_benchmark_identity_status` 返回 `"identified"`，`_benchmark_index_name` 提取部分指数名
- **直接证据**: `_COMPOSITE_BENCHMARK_SEPARATORS` 声明 6 种分隔符（`profile.py:74`），但 `re.split` 模式（`profile.py:592`）仅覆盖 `[＋+]`
- **影响**: 复合基准被误判为单一基准，`benchmark_identity_status` 和 `benchmark_index_name` 不准确。当前 Tier 1 实现中不影响跟踪误差计算或审计行为（无计算路径），但对后续 composite benchmark 扩展构成回归风险
- **建议改法和验证点**: 将 `re.split(r"[＋+]", ...)` 扩展为 `re.split(r"[＋+×*]|和|及", ...)` 或等价模式，与 `_COMPOSITE_BENCHMARK_SEPARATORS` 保持一致。添加含 `和`/`×` 分隔符的 profile fixture 验证 `benchmark_identity_status="composite"`
- **修复风险（低）**: 仅修改 split 模式和增加测试，不影响 extractor 主链路和其他字段

### F2-未修复-低-表格和正文同时命中同一跟踪误差值时误判为 ambiguous

- **入口/函数**: `_extract_tracking_error`
- **文件(行号)**: `fund_agent/fund/extractors/performance.py:361-362`
- **输入场景**: 年报 §3 同时在表格和正文中披露相同的实际跟踪误差值，例如表格行 "跟踪误差 0.53%" 和正文 "年化跟踪误差为0.53%"
- **实际分支**: `table_match is not None and text_match is not None` 为 True，返回 `_missing_tracking_error("tracking_error_ambiguous")`
- **预期行为**: 两来源一致时应保留直接披露结果而非 fail-closed
- **实际行为**: 返回 `missing`，renderer 保持"数据不足"，risk check 返回 `insufficient_data`
- **直接证据**: `performance.py:361-362`，`if table_match is not None and text_match is not None: return _missing_tracking_error("tracking_error_ambiguous")`
- **影响**: 已直接披露跟踪误差的基金被降级为 missing，产品报告中出现不必要的"数据不足"。实际年报中表格和正文重复披露相同值的情况不算罕见
- **建议改法和验证点**: 在 `table_match is not None and text_match is not None` 分支中，比较两者的解析值（`_parse_percent_ratio`）：值相等时保留 table_match（有更精确锚点），不等时才返回 ambiguous。添加 `table_text_same_value` fixture
- **修复风险（低）**: 仅在已命中双路径时增加值比较，不影响单路径或真正 ambiguous 场景的 fail-closed 行为

## Open Questions

- 无

## Residual Risk

- `index_profile` 和 `tracking_error` 的 snapshot 记录在 `_build_extracted_field_record` 中通过 `getattr(bundle, field_name)` 获取，函数签名声明 `extracted_field: ExtractedField[dict[str, object]]`，但实际传入 `ExtractedField[IndexProfileValue]` / `ExtractedField[TrackingErrorValue]`。当前行为正确（`_comparable_values_for_field` 对无白名单字段返回空映射；`_has_present_value` 对非 None dataclass 返回 True），但类型注解不准确。建议后续统一 `_build_extracted_field_record` 的签名或增加针对 typed value 的分支
- calculated tracking error、methodology extraction、constituents extraction 仍为后续 scope，当前 Tier 1 composite/identified 不等不影响产品行为
- QDII 跟踪误差适用性保持 not_applicable，直到 QDII subtype design 存在

## Verdict

**PASS_WITH_FINDINGS**

两个 finding 均为低严重度，不影响产品安全性、数据完整性或审计正确性。F1 在当前 Tier 1 scope 内不触发实际回归（大多数真实基准使用 `+`/`＋`）；F2 是保守 fail-closed 场景，不会导致错误值进入报告。两者均建议在后续 P13 follow-up 或 composite benchmark 扩展时修复。

实现整体严格遵循 `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` 和 controller judgment：

- 所有新增字段为显式 typed fields，无 `extra_payload`（plan Section 15.1）✓
- Product authority 来自 Capability structured data（plan Section 11.1）✓
- Developer override 仅 developer mode fallback，不进入 bundle（plan Section 8.4）✓
- Renderer 只读 `input_data.structured_data.tracking_error`，`TemplateRenderInput` shape 不变（plan Section 10）✓
- `run_risk_checks` 无等权 raw-scalar authority（plan Section 15.8）✓
- QDII 保持 not_applicable（plan Section 15.9）✓
- Snapshot observable-only，不进 FQ2/comparable denominator（plan Section 11.3）✓
- Benchmark anchors 不作为 tracking error/methodology/constituents 证据（plan Section 15.13，audit guards 执行）✓
- 无 Dayu runtime、LLM writing、Evidence Confirm、E1-E3（plan Section 6）✓
- 无 Service/UI 直接源访问（plan Section 6）✓
- 无 RR-13 或 repo-audit 变更（plan Section 6）✓
