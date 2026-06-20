# Code Review: return_attribution.v1 Source-Truth Slice 4 — Facade/Test/Docs Sync

## Metadata

- **Work unit**: FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction
- **Gate**: Implementation Gate — Slice 4: Facade/Test/Docs Sync
- **Role**: AgentDS review-only
- **Accepted checkpoint**: `ca05704`
- **Date**: 2026-06-20
- **Verdict**: `CODE_REVIEW_PASS_NOT_READY`

## Scope

Review only the working tree diff of this slice: 3 modified files, 0 production source changes.

## Finding 1 — Facade Regression (PASS)

`test_explicit_disclosure_source_truth_return_attribution_projects_to_bundle` 正确验证：

- 构造 proof-positive `FundDisclosureSourceTruthAdmissionProof`（六项验证全 True）
- 通过 `_source_truth_disclosure_intermediate()` 提供含费率、净值/基准表现、跟踪误差单元格的 FDD 内容 stub
- 使用 `FundProcessorRegistry.create_default()` 即默认 `FundDisclosureDocumentProcessor`
- 经显式 opt-in facade route 调用 `extract("110011", 2024, disclosure_intermediate=...)`

断言验证：
- `fee_schedule.value` = `{"management_fee": "1.50%", "custody_fee": "0.25%"}`，`extraction_mode="direct"`
- `nav_benchmark_performance.value` = `{"nav_growth_rate": "8.00%", "benchmark_return_rate": "6.00%"}`，`extraction_mode="direct"`
- anchors 全部为 `source_kind="annual_report"`，`row_locator` 均以 `field=` 开头
- 无 candidate evidence 混入 bundle value；无 `candidate` source_kind

结论：facade regression 真实验证了 proof-positive FDD return_attribution.v1 到 StructuredFundDataBundle 的显式 opt-in 投影。

## Finding 2 — tracking_error 处理 (PASS)

测试 stub 虽在 `_source_truth_disclosure_intermediate` 中提供了 tracking_error 单元格数据（`"1.23%"`），但断言：

```python
assert bundle.tracking_error.value is None
assert bundle.tracking_error.extraction_mode == "missing"
assert bundle.tracking_error.note == "非指数基金不适用跟踪误差"
```

原因：当前 active_fund facade 保持非指数基金不暴露跟踪误差的既有规则。即便 processor 内部可能提取了 tracking_error 原始数据（evidence document 声称 source-truth 存在于 processor output），bundle 投影层仍按非指数基金语义屏蔽。测试未将 tracking_error missing 当成 blocker，也未对 active_fund 声明 tracking_error 可用性。

结论：无误导。测试正确反映当前 facade 契约。

## Finding 3 — Docs 同步 (MINOR FINDING)

### 已正确同步

| 位置 | 内容 | 状态 |
|------|------|------|
| `docs/design.md` line 674 | "product_essence.v1 与 return_attribution.v1 已实现" | 正确 |
| `docs/design.md` line 678 | "其它四个字段族...仍未实现" | 正确 |
| `docs/design.md` line 1150 | 决策表更新为两字段族 | 正确 |
| `fund_agent/fund/README.md` line 79 | "product_essence.v1 与 return_attribution.v1 有 FDD source-truth" | 正确 |
| `fund_agent/fund/README.md` line 115 | "例外是 proof-positive product_essence.v1 与 return_attribution.v1" | 正确 |
| `fund_agent/fund/README.md` line 119 | 同上 | 正确 |

两文档在所有已修改位置均准确声明：candidate evidence 为 candidate_only / not_proven / NOT_READY；不声明 parser replacement 或 readiness。

### 未同步（stale header）

`docs/design.md` 第 6 行 **状态补充** 仍为旧文本：

> 当前仅 `product_essence.v1` 有 FDD source-truth direct extraction；`return_attribution.v1`、`manager_profile.v1`... 的 FDD source-truth extraction 仍未实现。

`docs/design.md` 第 8 行 **变更摘要**（v2.29）同样：

> 只有 `product_essence.v1` 在 proof-positive FDD 输入下实现 direct source-truth extraction

这两个头部区域在 detail 段落同步更新时被遗漏，与第 674/678/1150 行的当前事实矛盾。`README.md` 无此问题。

严重度：低。不影响实现正确性，不引入新的错误声明（header 仅过于保守，未将未实现字段写成已实现）。后续 gate 应修正。

## Finding 4 — 边界越界检查 (PASS)

Working tree diff 仅涉及三个文件：

- `tests/fund/test_data_extractor.py` — 测试
- `docs/design.md` — 设计文档
- `fund_agent/fund/README.md` — 包文档

逐项检查：

| 边界 | 是否触碰 | 证据 |
|------|----------|------|
| 生产源代码 | 否 | diff 无任何 `fund_agent/fund/**/*.py` 生产代码 |
| source/repository | 否 | 无 repository/source/fallback/cache 相关改动 |
| schema | 否 | 无 dataclass/schema/类型定义改动 |
| public contract | 否 | 无 processor contract/EvidenceAnchor/EvidenceSourceKind 扩展 |
| 其它 field family | 否 | 未改动 product_essence/manager_profile/investor_experience/core_risk/current_stage 实现 |
| 上层消费 | 否 | 无 Service/UI/Host/renderer/quality gate/LLM prompt 改动 |
| candidate module 导入 | 否 | `test_explicit_disclosure_intermediate_uses_protocol_not_candidate_import` 仍通过；stub 类不依赖 concrete candidate |

测试新增 `_DisclosureCell`、`_DisclosureTable` 两个 `@dataclass(frozen=True, slots=True)` stub，均为测试专用，不导入任何 concrete candidate 模块。`_source_truth_admission_proof()` 使用 contracts 中的 `FundDisclosureSourceTruthAdmissionProof`，不依赖 candidate schema。

## Finding 5 — 验证命令可信性 (PASS)

重现在本机执行结果：

```text
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
→ 170 passed in 0.89s
```

```text
uv run ruff check tests/fund/test_data_extractor.py
→ All checks passed!
```

```text
git diff --check -- tests/fund/test_data_extractor.py docs/design.md fund_agent/fund/README.md
→ exit=0 (无空白错误)
```

与 implementation evidence 声明完全一致。测试数 170 匹配，无新增失败，无 ruff 告警。

## Residual Risk Summary

1. **design.md header staleness**（owner: 后续 gate）— 状态补充和变更摘要行未同步 return_attribution.v1 已实现事实
2. **Real-report field correctness**（owner: evidence gate）— stub 值仅为构造数据，不代表真实年报提取正确性
3. **跟踪误差 processor 内部行为**（owner: future facade semantics gate）— 测试仅验证 bundle 投影层行为，不验证 processor 内部是否提取了 tracking_error source-truth
4. **其它四个字段族**（owner: separate future gates）— 本 slice 未实现，仍为 missing
5. **Processor 内部逐字段分解测试**— 本 slice 仅 facade 回归，未增加 processor 内部 fee_schedule/nav_benchmark_performance/tracking_error 的单元级提取正确性测试

## Verdict

`CODE_REVIEW_PASS_NOT_READY`

三个文件变更在给定 scope 内正确：facade regression 真实验证 return_attribution.v1 投影链路，tracking_error 未被误导为 blocker，docs 主体准确（仅 header 有一处 stale 需后续修正），无边界越界。验证命令全部复现通过。release/readiness 保持 NOT_READY 状态正确。
