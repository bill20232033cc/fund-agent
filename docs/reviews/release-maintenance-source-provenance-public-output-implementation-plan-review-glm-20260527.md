# Source Provenance Public Output Implementation Plan Review (GLM)

> **Date**: 2026-05-27
> **Reviewer role**: AgentGLM independent plan review
> **Review target**: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-20260527.md`
> **Truth sources**: `AGENTS.md`; `docs/design.md` v2.2 §6.1 已接受的未来设计；`docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
> **Checkpoint**: `918f65d docs: accept source provenance design`
> **Verdict**: **PASS_WITH_FINDINGS**

---

## Summary

计划整体结构完整、additive 目标清晰、保守映射规则正确、forbidden scope 完备。主要发现集中在 `StructuredFundDataBundle` 新增 required field 引起的 fixture churn 风险——计划列出的需修改测试文件不完整，实际影响 7 个测试文件 + 约 12 处 `dataclasses.replace()` 调用。计划已设有 stop condition 但未给出推荐的安全降级形状。

---

## Findings

### F1 [HIGH] StructuredFundDataBundle required field 引起的 fixture churn 范围被低估

**计划声明**（Implementation Slice step 2）：

> Add `source_provenance: PublicSourceProvenance` to `StructuredFundDataBundle`.
> Update all fake bundle builders in tests to include the new field.

**代码事实**：

`StructuredFundDataBundle` 是 `@dataclass(frozen=True, slots=True)`，当前有 17 个 required 字段，无默认值。经全量搜索，直接构造该 dataclass 的位置有 **8 处**，分布在 **7 个测试/生产文件**：

| # | 文件 | 构造方式 |
|---|------|---------|
| 1 | `fund_agent/fund/data_extractor.py:180` | 生产代码，keyword |
| 2 | `tests/services/test_fund_analysis_service.py:193` | `_bundle()` helper，keyword |
| 3 | `tests/fund/test_golden_prefill.py:116` | `_FakeExtractor.extract()`，keyword |
| 4 | `tests/fund/test_extraction_snapshot.py:216` | 内联构造，keyword |
| 5 | `tests/fund/test_extraction_snapshot.py:594` | `_build_bundle()` helper，keyword |
| 6 | `tests/fund/test_report_evidence.py:652` | `_build_bundle()` helper，keyword |
| 7 | `tests/fund/analysis/test_r_abc.py:112` | `_bundle()` helper，keyword |
| 8 | `tests/fund/template/test_renderer.py:296` | `_bundle()` helper，keyword |

此外还有约 **12 处** `dataclasses.replace()` 调用分布在这些文件及 `test_quality_gate_integration.py` 中，同样依赖字段名稳定。

**计划 "Exact Files to Inspect / Modify" 部分**仅列出修改以下测试文件：

- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- 可选：`tests/fund/test_report_evidence.py`

**缺失 3 个必须修改的文件**：

- `tests/services/test_fund_analysis_service.py`
- `tests/fund/test_golden_prefill.py`
- `tests/fund/analysis/test_r_abc.py`
- `tests/fund/template/test_renderer.py`（可选 report-evidence slice 未选时也必须修改）
- `tests/fund/test_quality_gate_integration.py`（replace() 调用点）

**计划的 stop condition** 说：

> 如果 churn 变得广泛，停下来评估 optional default-field approach。

这个 stop condition 方向正确，但计划没有给出推荐的安全降级形状。考虑到实际 churn 比 plan 预估的大（7 文件 vs plan 隐含的 3-4 文件），建议在实施前明确选择以下方案之一：

**推荐方案**：在 dataclass 中为 `source_provenance` 提供一个安全的默认值，使用 `NOT_APPLICABLE` 常量作为 default_factory：

```python
_NOT_APPLICABLE_PROVENANCE = PublicSourceProvenance(
    source_provenance_schema_version=PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
    source_strategy="primary_then_fallback",
    resolved_source_name=None,
    fallback_used=False,
    primary_failure_category=None,
    fallback_eligibility="not_applicable",
    source_provenance_status="not_applicable",
    source_provenance_reason="source_metadata_absent_no_fallback_evidence",
)

@dataclass(frozen=True, slots=True)
class StructuredFundDataBundle:
    # ... existing fields ...
    source_provenance: PublicSourceProvenance = field(
        default_factory=lambda: _NOT_APPLICABLE_PROVENANCE
    )
```

这样：
- 生产代码 `FundDataExtractor.extract()` 总是显式从 `report.metadata.source` 计算 provenance，覆盖默认值
- 现有 7 个测试文件中不关心 provenance 的 fixture 自动获得安全保守默认值，无需修改
- 只需修改专门测试 provenance 的 test 文件（`test_source_provenance.py`、`test_data_extractor.py`、`test_extraction_snapshot.py`）
- 不引入 `None` 语义，不掩盖 fallback-backed unknowns

**如果选择 required field 方案**，则必须更新 "Exact Files to Modify" 列表，补全全部 7 个测试文件和 ~12 处 replace() 调用点。

**severity 理由**：遗漏的文件数量导致实施时可能意外遗漏修改点，引发 CI 大面积失败。stop condition 虽然能捕获，但会浪费实施轮次。

---

### F2 [MEDIUM] Summary provenance 输出格式未具体指定

**计划声明**（Implementation Slice step 3）：

> `write_snapshot_summary(...)` should add a compact source provenance section or columns in Fund Results: resolved source, fallback flag, eligibility/status, reason.

这段描述只给了列名方向，没有给出：
- 具体是在 "Fund Results" 表中增加列，还是在表后新增独立 section
- 精确的列顺序和 header 文本
- 当 provenance 为 not_applicable 时的输出（空字符串？`N/A`？`not_applicable`？）
- failed funds 没有 provenance 时的输出策略（plan 提到 "failed funds have no provenance unless the failure record is later extended, which is out of scope for v1"，但 summary 中应如何展示未说明）

**建议**：在实施前在 plan 中补充 summary 输出的 mockup 或精确列定义。否则实施者需要在 snapshot 逻辑中做格式决策，增加 review 往返。

---

### F3 [MEDIUM] SnapshotRecord 8 个新增字段的默认值策略未明确

**计划声明**：

> `_snapshot_record(...)` should copy values from `bundle.source_provenance` into every field-level record.

当前 `SnapshotRecord` 是 `@dataclass(frozen=True, slots=True)`，全部 17 个字段都是 required。计划提议新增 8 个字段。

**需明确**：
- 8 个新增字段是否有默认值？如果没有，则 `SnapshotRecord` 的所有构造点（目前只有 `_snapshot_record()` 集中构造函数）也需更新。由于 `_snapshot_record()` 是唯一的集中构造入口，且使用 keyword args，churn 风险低于 bundle，但仍需确认。
- 旧 JSONL 行（无 provenance 字段）被 score reader 读取时，score code 是否需要处理这些字段缺失？计划在 score compatibility tests 中提到了这点，但没有说明 score reader 的具体容错方式。

**建议**：确认 SnapshotRecord 新增字段全部提供默认值（从 `_snapshot_record()` 中直接从 bundle 拷贝，snapshot 构造流程保证 bundle 总有 provenance），并在 plan 中注明 `build_snapshot_records()` 入口保证 bundle 非空。

---

### F4 [LOW] source_strategy 单值类型可简化文档

`SourceStrategy = Literal["primary_then_fallback"]` 只有一个值。这是合理的 v1 预留扩展点，但 plan 可以加一句说明这是 intentionally single-valued for v1，避免 review 者疑惑。

---

## Verification Checklist

| Review focus | Result |
|---|---|
| Slice 是否 minimal and additive | **PASS** — 四步切片（projection → bundle threading → snapshot → score compat）清晰 additive，不触碰来源编排、renderer、quality gate 核心逻辑 |
| StructuredFundDataBundle constructor churn | **FINDING F1** — churn 范围被低估，需选择 default-field 或补全文件列表 |
| Preserve no source helper / downloader / cache / PDF access | **PASS** — plan 显式禁止 import sources.py、source internals、cache、PDF adapter；projection 只消费 `AnnualReportSourceMetadata` |
| Preserve no FundDocumentRepository strategy change | **PASS** — Repository 不在修改文件列表中 |
| fallback_used=true + missing category → unknown_public_metadata_absent | **PASS** — conservative mapping rules 正确；plan 的 projection 规则和测试用例覆盖了这个 case |
| Snapshot JSONL/summary and score compat tests | **PARTIAL PASS** — 测试用例设计充分，但 summary 格式未具体化（F2） |
| Avoid renderer / FQ0-FQ6 / default analyze/checklist / Host/Agent/dayu / fund_type/extractor / golden/baseline | **PASS** — forbidden scope 完备覆盖所有禁区；stop conditions 正确 |
| Exact files/tests and stop conditions code-generation-ready | **PARTIAL PASS** — projection module 和 snapshot 修改足够具体；bundle threading 的文件列表不完整（F1）；summary 格式不完整（F2） |

---

## Recommended Plan Revisions

1. **[F1, HIGH]** 选择以下方案之一并更新 plan：
   - **方案 A（推荐）**：为 `source_provenance` 提供 `NOT_APPLICABLE` 默认值，将 fixture churn 限制在 3 个测试文件
   - **方案 B**：保持 required field，补全 "Exact Files to Modify" 列表，加入 `tests/services/test_fund_analysis_service.py`、`tests/fund/test_golden_prefill.py`、`tests/fund/analysis/test_r_abc.py`、`tests/fund/template/test_renderer.py`、`tests/fund/test_quality_gate_integration.py`
2. **[F2, MEDIUM]** 补充 summary provenance section 的精确输出格式（列名、顺序、not_applicable 显示方式、failed fund 处理）
3. **[F3, MEDIUM]** 明确 SnapshotRecord 8 个新字段的默认值策略，确认 `build_snapshot_records()` 是唯一的 SnapshotRecord 构造入口

---

## Verdict

**PASS_WITH_FINDINGS** — 计划设计方向正确、conservative mapping rules 完备、forbidden scope 覆盖充分。F1 的 bundle churn 风险需要在实施前做出明确选择（default-field vs 补全文件列表），F2/F3 的格式细节可在实施过程中收敛但不影响整体架构安全性。无 BLOCKED 级发现。
