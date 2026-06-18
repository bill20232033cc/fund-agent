# FundDisclosureDocument S5 Facade Integration Aggregate Deepreview (MiMo)

Date: 2026-06-19

Reviewer: AgentMiMo

Gate: `FundDisclosureDocument S5 Facade Integration Aggregate Deepreview Gate`

Accepted slice commit: `c290d73`

Accepted plan commit: `7bc4621`

## 验证证据

### 完整证据链审查

1. **Plan → Implementation 一致性**
   - Plan (`docs/reviews/funddisclosuredocument-s5-facade-integration-plan-20260618.md`) 定义了 3 个写入文件和 19 个测试用例。
   - Implementation evidence (`docs/reviews/funddisclosuredocument-s5-facade-integration-implementation-evidence-20260619.md`) 确认仅修改了 plan 允许的 3 个文件。
   - Controller judgment (`docs/reviews/funddisclosuredocument-s5-facade-integration-plan-controller-judgment-20260619.md`) 接受了所有 8 个 plan finding。
   - Code review controller judgment (`docs/reviews/funddisclosuredocument-s5-facade-integration-code-review-controller-judgment-20260619.md`) 接受了实现，deferred 1 个非阻断观察。

2. **默认 parsed_annual_report.v1 生产路径保留**
   - `data_extractor.py:310-362`：`disclosure_intermediate=None` 时，代码路径完全不变——load report → validate identity → NAV → classify fund type → active_fund via `parsed_annual_report.v1` → non-active via direct legacy。
   - 测试验证：`test_default_active_fund_still_uses_parsed_annual_report_processor_path`（L1052）、`test_default_extract_does_not_resolve_fund_disclosure_processor`（L1071）。

3. **显式 fund_disclosure_document.v1 opt-in 路由**
   - `data_extractor.py:320-325`：pre-NAV 四字段身份校验（fund_code / report_year / document_kind / intermediate_kind）。
   - `data_extractor.py:334-342`：仅当 `disclosure_intermediate is not None` 时路由到 `_extract_active_fund_disclosure_via_processor`。
   - `data_extractor.py:465-469`：非 active_fund fail-closed，不 fallback legacy。
   - `data_extractor.py:471-478`：dispatch key `intermediate_kind="fund_disclosure_document.v1"`、`source_kind="annual_report"`。
   - `data_extractor.py:489-495`：blocked/unsupported 和 source_provenance None 均 raise RuntimeError。

4. **Fail-closed 语义**
   - 逐项验证 plan failure matrix 全部 16 行，实现均覆盖：
     - Report identity mismatch: L315-318
     - Disclosure identity mismatch: L664-705
     - Non-active fund type: L465-469
     - Processor blocked/unsupported: L489-493
     - source_provenance is None: L494-495 + processor admission blocked
     - Registry no FDD processor: `UnsupportedFundProcessorError` propagation
     - Processor result identity mismatch: L622-661
     - All failure_class values (schema_drift / identity_mismatch / integrity_error / unavailable / not_found): delegated to processor admission helper
   - 无 fallback 路径：non-active disclosure 不走 direct legacy；processor 失败不回退 parsed annual。

5. **候选/source/provenance/identity 边界**
   - `data_extractor.py` 仅从 `fund_agent.fund.processors.contracts` 导入 `FundDisclosureDocumentIntermediate` Protocol。
   - AST guard 测试（L1119-1142）确认无 `fund_agent.fund.documents.candidates` 导入。
   - forbidden-diff 检查全部为空。
   - `source_provenance` 和 `candidate_boundary` 通过 `FundProcessorInput` 显式传递。

6. **无 Service/UI/Host/renderer/quality-gate/LLM 直接消费**
   - forbidden-diff 确认无 `fund_agent/services`、`fund_agent/ui`、`fund_agent/host`、`fund_agent/agent` 文件修改。

7. **无 source truth / parser replacement / S6+ extraction / EvidenceAnchor 扩展 / readiness/release 声明**
   - README 更新仅描述 S5 显式 opt-in facade 边界，保留 candidate-only / `not_proven` / `NOT_READY`。
   - 实现不修改 `EvidenceSourceKind`、`EvidenceAnchor`、source failure taxonomy。
   - 实现不实现 S6+ field-family extraction。

8. **测试验证**
   - 独立运行确认：`test_data_extractor.py` 34 passed、`processors/` 57 passed、`documents/` 57 passed。
   - ruff check / format 通过。
   - git diff --check 通过。

### Plan Review 证据链

- DS review (`plan-review-20260619-000634.md`)：3 个 minor findings，全部 accepted/fixed。
- MiMo review (`plan-review-20260619-000638.md`)：2 medium + 1 low findings，全部 addressed。
- MiMo targeted re-review (`plan-review-20260619-001232.md`)：全部 7 accepted findings closed。
- DS targeted re-review (`plan-review-20260619-001234.md`)：全部 7 accepted findings closed。

### Code Review 证据链

- DS code review (`code-review-20260619-065058.md`)：未发现实质性问题。
- MiMo code review (`code-review-20260619-065051.md`)：未发现实质性问题。3 个非阻断观察项。
- Controller judgment 接受实现，deferred 1 个非阻断观察。

## 发现

未发现实质性问题。

c290d73 实现与已接受 plan 完全一致：
- 默认 `disclosure_intermediate=None` 路径行为未变。
- 显式 `fund_disclosure_document.v1` 路由仅通过显式参数激活。
- 所有 fail-closed 条件均有实现覆盖和测试验证。
- 边界完整：无 forbidden 文件修改、无 candidate 导入泄漏、无 upper-layer 消费。
- 测试覆盖充分：19 个 S5 测试 + 已有回归测试全部通过。

## 残余风险

| 残余 | Owner | 目标 |
|---|---|---|
| S6+ actual field-family extraction from `FundDisclosureDocument` 缺失 | Fund extractor owner + controller | Future S6+ field-family extraction planning gate |
| EvidenceAnchor projection strategy for candidate section/table/cell locators 缺失 | Fund documents / extractor owner | Future EvidenceAnchor projection design/evidence gate |
| Source truth, full field correctness, raw XML/taxonomy proof, unit/date semantics and cross-year correctness 未证明 | Fund documents evidence owner | Separate evidence gates |
| Concrete candidate path remains blocked by candidate-only boundary | Fund extractor owner | Intentional S5 residual until source truth / field correctness gates |
| Non-active fund processors 未实现 | Fund processor owner | Separate fund-type processor gates |
| Default production parser remains `parsed_annual_report.v1` path | Controller | Intentional boundary, not a defect |
| Release/readiness remains `NOT_READY` | Release owner / controller | Separate release/readiness gates |
| `source_provenance` explicit check after processor extraction (deferred observation) | Processor contract owner | Future processor-contract/failure-semantics gate if needed |

## 结论

AGGREGATE_DEEPREVIEW_PASS_NOT_READY

Artifact path: `docs/reviews/funddisclosuredocument-s5-facade-integration-aggregate-deepreview-mimo-20260619.md`
