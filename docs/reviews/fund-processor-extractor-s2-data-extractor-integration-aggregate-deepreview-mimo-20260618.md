# Fund Processor/Extractor S2 DataExtractor Integration Aggregate Deepreview

> Date: 2026-06-18
> Role: AgentMiMo, independent aggregate deepreview reviewer
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration
> Gate: Aggregate Deepreview Gate
> Branch: post-merge/pr22-origin-main
> Accepted slice commit: `02b9ca9`
> Base: `02b9ca9^..02b9ca9`

## Scope

- Accepted slice commit diff: `02b9ca9^..02b9ca9`（13 files, +1662/-48 lines）
- Accepted S2 plan/review/fix artifacts: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-*20260618.md`（15 artifacts）
- Key code: `fund_agent/fund/data_extractor.py`, `tests/fund/test_data_extractor.py`, `fund_agent/fund/README.md`, `fund_agent/fund/processors/contracts.py`, `fund_agent/fund/processors/registry.py`, `fund_agent/fund/processors/active_annual.py`
- Input docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## Verdict

**PASS_NOT_READY**

S2 implementation slice is accepted. No blocking defects found. Release/readiness remains `NOT_READY`.

## Findings

未发现实质性问题。

## Verification Results

### Q1: active_fund annual ParsedAnnualReport default facade 真实通过 FundProcessorRegistry / ActiveFundAnnualProcessor 投影 StructuredFundDataBundle

**PASS。** `FundDataExtractor.extract()` L321-330 按 `classified_fund_type == "active_fund"` 分派到 `_extract_active_fund_via_processor()`，该方法 L362-377 构造 `FundProcessorDispatchKey`，通过 `self._processor_registry.resolve(dispatch_key)` 获取 `ActiveFundAnnualProcessor`，调用 `processor.extract(processor_input)` 得到 `FundProcessorResult`，再通过 `_active_processor_result_to_bundle()` 投影为 `StructuredFundDataBundle`。测试 `test_active_fund_uses_processor_path_with_marker_values` 注入 `_MarkerActiveFundProcessor`（返回已知 marker 值），验证 bundle 字段包含 marker 值而非 direct extractor 结果，证明字段确实来自 processor 路径。

### Q2: repository report identity mismatch 在 NAV load 和 processor dispatch 前 fail-closed

**PASS。** `FundDataExtractor.extract()` L308-312 在 `load_annual_report()` 返回后立即校验 `report.key.fund_code != fund_code or report.key.year != report_year`，不匹配时抛出 `RuntimeError("Report identity mismatch: ...")`。此时 NAV load（L313）和 processor dispatch（L322）均未执行。测试 `test_data_extractor_rejects_report_identity_mismatch_before_nav` 请求 `fund_code="999999"` 但仓库返回 `"110011"`，验证 `pytest.raises(RuntimeError, match="Report identity mismatch")` 且 `nav_provider.calls == []`。

### Q3: processor result identity mismatch、unsupported/blocked 是否 fail-closed，且不 fallback 到 direct extractor

**PASS。** 三重 fail-closed：
1. `UnsupportedFundProcessorError`：registry 无可用 processor 时 `registry.py` L123-127 抛出。测试 `test_active_fund_unsupported_registry_fails_closed` 注册 `_NeverSupportProcessor`（永不支持），验证 `pytest.raises(UnsupportedFundProcessorError, match="unsupported_processor")`。
2. `RuntimeError` blocked/unsupported：`data_extractor.py` L378-383 检查 `result.contract_status in ("unsupported", "blocked")`，抛出 `RuntimeError`。
3. `RuntimeError` identity mismatch：`_validate_processor_result_identity()` L511-554 校验 5 个身份字段（fund_code, report_year, fund_type, report_type, input_intermediate_kind），任一不匹配抛出 `RuntimeError("Processor result identity mismatch: ...")`。测试 `test_active_fund_processor_mismatched_identity_fails_closed` 注册 `_MismatchedIdentityProcessor`（fund_code="999999"），验证 `pytest.raises(RuntimeError, match="Processor result identity mismatch")`。

上述三类均不 fallback 到 direct extractor 路径。

### Q4: non-active/unclassified direct legacy residual 保持，不被 active processor 误覆盖

**PASS。** `FundDataExtractor.extract()` L332-339：`classified_fund_type != "active_fund"` 时走 `_extract_bundle_direct_legacy_path()`，该函数 L410-468 保持 S1 行为（调用窄 extractor 编排 bundle）。测试 `test_index_fund_direct_path_smoke_test` 使用 `classified_fund_type="index_fund"` 的 `_index_annual_report()`，验证 bundle 正常返回且 `basic_identity.value["classified_fund_type"] == "index_fund"`。

### Q5: AGENTS 边界检查

**PASS。** 逐项验证：
- 不得直接消费 Docling/raw full JSON/EID HTML/pdfplumber source truth：代码只消费 `ParsedAnnualReport`，不接触 Docling/HTML/pdfplumber。
- 不得绕过 `FundDocumentRepository`：`extract()` 通过 `self._repository.load_annual_report()` 访问年报，repository 默认为 `FundDocumentRepository()`。
- 不得 Service/UI/Host/renderer/quality gate 直接 parser 调用：S2 变更只在 `fund_agent/fund/` 内部。
- 不得 extra_payload 参数：无 `extra_payload` 使用。
- 不得 readiness/release/parser replacement/source truth claim：代码和 README 均声明 `NOT_READY`。

### Q6: tests 覆盖关键 failure path 和 regression surface

**PASS。** `tests/fund/test_data_extractor.py` 覆盖：
- `test_data_extractor_degrades_nav_failure_without_blocking_annual_report`：NAV 失败降级
- `test_data_extractor_does_not_mask_repository_failure`：仓库失败不被 NAV 吞掉
- `test_data_extractor_rejects_report_identity_mismatch_before_nav`：report identity mismatch fail-closed
- `test_active_fund_uses_processor_path_with_marker_values`：processor 路径覆盖验证
- `test_active_fund_unsupported_registry_fails_closed`：registry 无可用 processor fail-closed
- `test_active_fund_processor_mismatched_identity_fails_closed`：processor result identity mismatch fail-closed
- `test_index_fund_direct_path_smoke_test`：非 active direct legacy path 保持
- 债券/NAV 系列/来源 provenance 等既有测试保持通过

`tests/fund/processors/` 覆盖 registry 和 active_annual processor 单元测试。总计 30 passed。

### Q7: 控制文档和 artifact 一致性

**PASS with residual.** `fund_agent/fund/README.md` 已更新 S2 wording（"该 processor 已在 S2 接入 FundDataExtractor.extract() 默认生产 facade"）。`docs/design.md` 和 top-level `fund_agent/README.md` 仍含 S1-era wording（processor 未接入默认 facade）。该 residual 已在 controller judgment 中记录为后续 truth-sync/bookkeeping gate 处理项，不阻塞当前 gate。

## Open Questions

无。

## Residual Risk

| Residual | Owner | Blocker? |
|---|---|---|
| `docs/design.md` 和 top-level `fund_agent/README.md` S1 wording residual | Controller / truth-sync owner | 不阻塞；留给后续 truth-sync/bookkeeping gate |
| Non-active fund processors 未实现 | Future Fund processor owner | 不阻塞当前 active_fund S2 |
| `index_profile` 仍来自 bootstrap `extract_profile()` | S3 planning owner | 不阻塞当前 S2 |
| Active path 内存重复 `extract_profile()` 调用 | S3 planning owner | 不阻塞当前 S2 |
| `_field_from_family()` 使用 `ExtractedField[Any]` | Future typing hardening owner | 不阻塞当前 S2 |
| Field-level anchors 仍为 family-level | Future extraction contract owner | 不阻塞当前 S2 |

## Coverage / Commands Run

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py` | 30 passed in 0.72s |
| `uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py` | All checks passed! |
| `git diff --check 02b9ca9^..02b9ca9` | no output |
| `git show 02b9ca9 --stat` | 13 files, +1662/-48 lines |
| `git diff 02b9ca9^..02b9ca9 --name-only` | verified all changed files |

## Release / Readiness

**NOT_READY。** S2 aggregate deepreview gate 通过，但 release/readiness 状态不变。不授权 parser replacement、source truth、full field correctness、golden promotion、release readiness、PR、push 或 merge。
