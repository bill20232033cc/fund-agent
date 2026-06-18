# Fund Processor/Extractor S2 DataExtractor Integration — Code Review (AgentCodex)

> Date: 2026-06-18
> Role: AgentCodex independent code reviewer
> Gate: S2 code review gate, second independent review
> Verdict: FAIL_NOT_READY

## Findings

### 1-未修复-高-active path masks document/processor identity drift

- **分类**: blocking
- **入口/函数**: `FundDataExtractor.extract()` -> `_extract_active_fund_via_processor()` -> `_active_processor_result_to_bundle()`
- **文件(行号)**: `fund_agent/fund/data_extractor.py:316`, `fund_agent/fund/data_extractor.py:357`, `fund_agent/fund/data_extractor.py:393`, `fund_agent/fund/data_extractor.py:567`
- **输入场景**: `repository.load_annual_report("999999", 2024)` 因 cache/source/repository bug 返回 `ParsedAnnualReport.key.fund_code="110011"`，或 injected/custom processor 返回与 dispatch key 不一致的 `FundProcessorResult.fund_code/report_year`。
- **实际分支**: bootstrap `extract_profile(report)` 分类为 `active_fund` 后进入 processor path；dispatch key 使用 `report.key.fund_code/report.key.year`，processor 也消费该 `report`，但 bundle top-level identity 使用外层请求参数 `fund_code/report_year`。
- **预期行为**: 身份事实必须来自同一个已加载年报/processor result，或在 repository/processor 身份不一致时 fail-closed。`identity_mismatch` 类错误不得被 façade 输出静默掩盖。
- **实际行为**: `StructuredFundDataBundle.fund_code/report_year` 会被写成请求参数，而字段值、anchors、source provenance 和 processor dispatch 事实来自返回的 `ParsedAnnualReport`。这会产生一个 top-level 标识为 A 基金、内部证据来自 B 基金的 bundle。
- **直接证据**: active 分支判定在 `data_extractor.py:316`；dispatch key 使用 `report.key.year` 与 `report.key.fund_code` 在 `data_extractor.py:357-364`；processor result 投影时传入外层 `fund_code/report_year` 在 `data_extractor.py:393-397`；bundle 写入这两个值在 `data_extractor.py:567-569`。旧 direct legacy path 仍使用 `report.key` 写 bundle identity，在 `data_extractor.py:438-440`，说明 S2 只改变了 active path 的身份来源。
- **影响**: 错误状态 / 静默失效。上游 `ChapterFactProvider`、snapshot、quality/scoring 或人工复核会把错误 top-level fund identity 当成当前结构化事实，导致跨基金证据串联，且 source provenance 无法暴露这个 mismatch。
- **建议改法和验证点**: 在 active path 使用 `report.key` 或 `FundProcessorResult` identity 作为 bundle identity，并显式校验 `result.fund_code/result.report_year/result.fund_type/result.report_type/result.input_intermediate_kind` 与 dispatch key 一致；不一致时抛出 typed fail-closed error，不进入 legacy direct path。新增 no-live test：fake repository 返回 mismatched `DocumentKey` 或 fake processor 返回 mismatched result identity，验证 active path fail-closed 或至少不以请求参数覆盖 source identity。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### 2-未修复-中-Fund README still states processor is not connected to default facade

- **分类**: blocking
- **入口/函数**: S2 implementation documentation sync
- **文件(行号)**: `fund_agent/fund/README.md:77`, `fund_agent/fund/README.md:111`
- **输入场景**: 开发者按 Fund 包 README 理解当前 `FundDataExtractor.extract()` 行为，或 controller 按 implementation evidence 判断 exact write set 是否完整。
- **实际分支**: implementation 修改了 `fund_agent/fund/data_extractor.py`，使 active fund 默认 façade 进入 `FundProcessorRegistry` / processor path；但 `fund_agent/fund/README.md` 未更新。
- **预期行为**: 按 `AGENTS.md` 文档同步规则和 accepted plan 的 conditional README write set，Fund 包当前行为发生变化时必须同步更新 `fund_agent/fund/README.md`，避免 README 与代码事实并存双重口径。
- **实际行为**: README 仍写“该 processor 尚未接入 `FundDataExtractor.extract()` 默认生产 facade”，且 `FundDataExtractor.extract()` 章节仍描述为直接聚合章节 extractor / `portfolio_managers`、`risk_characteristic_text` 透传，没有说明 active fund 已经经 registry/processor 投影、非 active 才走 residual legacy path。
- **直接证据**: README stale statement 在 `fund_agent/fund/README.md:77`；`FundDataExtractor.extract()` 当前说明在 `fund_agent/fund/README.md:111`；implementation diff 改动 active path 在 `fund_agent/fund/data_extractor.py:316-402`。
- **影响**: public contract drift / gate contract drift。S2 的核心产物是把默认 façade 接入 processor path；README 继续宣称未接入，会误导后续 S3 planning、测试编写和边界审查，并违反本仓库“以代码为准、README 不保留旧口径”的同步约束。
- **建议改法和验证点**: 更新 `fund_agent/fund/README.md`：明确 active fund annual `ParsedAnnualReport` 已经通过 `FundProcessorRegistry` / `ActiveFundAnnualProcessor` 投影 bundle；非 active/unclassified 仍是 S2 residual direct legacy path；`index_profile`、bond risk、NAV/source provenance residual 口径保持 NOT_READY。复跑 `git diff --check`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 3-未修复-低-core_risk fallback condition is narrower than accepted wording

- **分类**: nonblocking
- **入口/函数**: `_active_processor_result_to_bundle()`
- **文件(行号)**: `fund_agent/fund/data_extractor.py:539`, `fund_agent/fund/data_extractor.py:542`
- **输入场景**: `product_essence.v1.risk_characteristic_text` 投影结果没有 public value，且 `core_risk.v1` 含同名 public value。
- **实际分支**: fallback 条件检查 `risk_characteristic_text.value is None`，没有显式检查 `risk_characteristic_text.extraction_mode == "missing"`。
- **预期行为**: accepted plan 写明只有 product family 投影出的 `risk_characteristic_text` 为 `extraction_mode == "missing"` 且 core_risk 有 public value 时才 fallback。
- **实际行为**: 当前 `_field_from_family()` 对 absent family 或 absent/None field 都返回 `extraction_mode="missing"`，所以现有运行时等价；但条件没有固定住 plan 中的状态语义。
- **直接证据**: `_field_from_family()` 在缺 family/field 时返回 missing，见 `fund_agent/fund/data_extractor.py:483-497`；fallback 条件见 `fund_agent/fund/data_extractor.py:542`。
- **影响**: 当前无运行时错误；未来若 `_field_from_family()` 允许 value 为 `None` 但 `extraction_mode` 非 missing，此处会过早 fallback。
- **建议改法和验证点**: 将条件改为 `risk_characteristic_text.extraction_mode == "missing" and risk_characteristic_text.value is None`，并加一个 core_risk fallback focused test。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Scope

- **Mode**: current changes, targeted S2 code review gate
- **Branch**: `post-merge/pr22-origin-main`
- **Base**: current workspace diff / accepted S2 artifacts; no PR metadata inspected
- **Output file**: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-codex-20260618.md`
- **Included scope**:
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/test_data_extractor.py`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-controller-judgment-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-mimo-20260618.md`
  - Relevant processor contracts/registry/active annual implementation and Fund README statements
- **Excluded scope**:
  - No live/source/PDF/FDR/Docling conversion/provider/LLM/analyze/checklist/golden/readiness/release commands.
  - Did not review unrelated untracked residue outside this S2 target.
- **Parallel review coverage**: 无 subagent；main reviewer covered implementation path, contract path, tests, README drift, forbidden-path scan.

## Open Questions

- `fund_agent/README.md:35` also says the S1 processor is not connected to `FundDataExtractor.extract()` default facade. That file was outside the accepted implementation write set, so controller should decide whether to expand doc-sync scope or handle it in a follow-up doc/control gate.

## Residual Risk

- `index_profile` still comes from bootstrap `extract_profile()` for active funds; this matches accepted S2 residual.
- Active path still duplicates in-memory `extract_profile()` for classification and processor extraction; this matches accepted S2 residual.
- Non-active processors remain unimplemented and direct legacy path remains active for index/enhanced/bond/QDII/FOF/unclassified funds.
- Field-level anchors remain family-level in S2; no field-specific anchor filtering was verified beyond current contract.
- Tests prove marker attribution, unsupported registry fail-closed, NAV degradation, repository failure propagation, bond drawdown behavior, source provenance projection and index direct path. They do not yet cover active path identity mismatch or processor result identity mismatch.

## Commands Inspected/Run

```text
git branch --show-current
git status --short
sed -n '1,520p' /Users/maomao/.codex/skills/deepreview/SKILL.md
rg -n "Fund Processor/Extractor S2|data_extractor|fund-processor-extractor-s2|Docling architecture|FundProcessorRegistry" /Users/maomao/.codex/memories/MEMORY.md
git diff -- fund_agent/fund/data_extractor.py
git diff -- tests/fund/test_data_extractor.py
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md
sed -n '1,220p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-controller-judgment-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-mimo-20260618.md
nl -ba fund_agent/fund/data_extractor.py
nl -ba tests/fund/test_data_extractor.py
nl -ba fund_agent/fund/processors/contracts.py
nl -ba fund_agent/fund/processors/registry.py
nl -ba fund_agent/fund/processors/active_annual.py
nl -ba fund_agent/fund/README.md
rg -n "FundDataExtractor|Processor|FundProcessorRegistry|data_extractor|结构化|extract\\(" fund_agent/fund/README.md README.md fund_agent/README.md
rg -n "extra_payload|Docling|FundDisclosureDocument|docling|candidate|pdfplumber|EID|renderer|quality|service|host" fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
git diff --name-only HEAD -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md docs/design.md docs/implementation-control.md fund_agent/fund/README.md fund_agent/fund/documents/candidates fund_agent/service fund_agent/host fund_agent/agent fund_agent/render fund_agent/quality
git diff --cached --name-only
git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md
uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
```

Observed verification:

```text
uv run pytest ... -> 28 passed in 0.40s
uv run ruff check ... -> All checks passed!
git diff --check ... -> no output
git diff --cached --name-only -> no output
forbidden-path name-only scan -> fund_agent/fund/data_extractor.py, tests/fund/test_data_extractor.py
```
