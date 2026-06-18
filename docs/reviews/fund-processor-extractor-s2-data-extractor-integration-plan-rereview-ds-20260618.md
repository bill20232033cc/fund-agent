# Fund Processor/Extractor S2 DataExtractor Integration Plan Re-Review (AgentDS)

> Date: 2026-06-18
> Role: AgentDS independent plan re-reviewer
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration Planning Gate
> Gate: S2 plan re-review gate after plan fix
> Review target: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md` (fixed)
> Prior reviews: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-review-mimo-20260618.md`, `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-review-ds-20260618.md`
> Fix evidence: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-fix-evidence-20260618.md`
> Artifact status: re-review only, not implementation, not readiness

## Verdict

**PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY**

两个 MiMo 阻塞发现（F1, F2）已关闭。六个 controller 修复要求全部验证通过。DS 非阻塞发现已充分处理或残差化。修复未引入新的边界违规、越权、矛盾或欠明确的实现决策。固定 plan 保持 code-generation-ready，可进入 implementation gate。

本 re-review 未实现代码、未修改源文件/测试/control docs/design docs、未提交、未推送、未打开 PR、未进入 implementation。

---

## Review Questions

### Q1: Are MiMo blocking findings F1 and F2 closed?

**YES, both closed.**

**F1 (core_risk.v1 fallback projection rules incomplete) → 关闭**

Plan 第 122-126 行现已明确：
- 仅 `risk_characteristic_text` 可作为 fallback，触发条件为 `product_essence.v1` 同名字段 `extraction_mode == "missing"` 且 `core_risk.v1` 有 public value
- `holder_structure`、`turnover_rate`、`holdings_snapshot`、`tracking_error` 标注为 informational/redundant，各自指明 primary family 归属，禁止隐式合并
- 新增 `current_stage.v1` 条目，标注为 informational/redundant，S2 不单独从中投影 bundle 字段

代码验证：`active_annual.py:170-189` 确认 `core_risk.v1` 的 5 个字段全部与 primary family 重复；`active_annual.py:156-169` 确认 `current_stage.v1` 的 4 个字段也已由 primary family 拥有。映射正确，无歧义。

**F2 (processor.extract() unexpected exception propagation not explicit) → 关闭**

Plan 第 160-162 行（Fail-closed Rules）新增条目：
- `processor.extract()` 内部非预期异常（TypeError/KeyError/AttributeError）必须向上抛出或转换为 typed fail-closed error
- 不得静默吞掉异常
- 不得 fallback 到 direct extractor path 为 active_fund 组装 bundle
- Repository failure 传播与 NAV 降级语义保持不变

代码验证：`contracts.py:365-376` 的 `FundProcessorProtocol.extract()` 协议已允许实现抛出 `ValueError`；`active_annual.py:246-263` 已通过 `_blocked_result()` 处理已知 fail-closed 路径。修复补上了窄 extractor 意外异常的契约缺口。

### Q2: Are DS nonblocking findings adequately addressed or residualized?

**YES. 所有 7 个 DS 发现均已充分处理或残差化。**

| DS Finding | Severity | Disposition | Evidence |
|---|---|---|---|
| F1: source_kind underspecified | nonblocking | **已处理** — Fix 3 将 `source_kind` 设为确定性静态值 `"annual_report"`，禁止从 candidate/fallback 派生 | plan:84-85 |
| F2: tracking_error layer overlay | nonblocking | **残差化** — plan 保留 "仍必须经过 `_tracking_error_for_fund_type()`"，未解释 facade 覆盖 processor 输出的层叠关系。不阻塞实现 | plan:110 |
| F3: bootstrap vs processor consistency | nonblocking | **残差化** — 两者消费同一份 in-memory `ParsedAnnualReport`，确定性 extractor 保证一致性；S3 消除 | plan:63-64, 230-231 |
| F4: field family anchor to field anchor | nonblocking | **残差化** — 投影细节留给 implementation worker；plan 写 "使用该 `FundFieldFamilyResult.anchors`"（全量映射）作为合理默认 | plan:129 |
| F5: core_risk fallback edge case | nonblocking | **已处理** — 并入 Fix 1，明确判断条件为 `extraction_mode == "missing"` | plan:122-123 |
| F6: test attribution strategy | nonblocking | **已处理** — Fix 4 要求注入自定义 registry/marker processor 证明字段归属 | plan:206-207 |
| F7: non-active non-bond smoke test | needs-more-evidence | **已处理** — Fix 5 添加推荐条目，不作为阻塞条件 | plan:212-213 |

### Q3: Does the fixed plan remain code-generation-ready for implementation gate?

**YES.**

固定 plan 满足所有 code-generation-readiness 条件：

- **投影规则完备**：六个字段族到 bundle 字段的映射全部明确，包括 fallback 规则（仅 `risk_characteristic_text`）、informational/redundant 标注（`core_risk.v1` 的 4 个字段 + `current_stage.v1` 的 4 个字段）
- **Fail-closed 契约完整**：覆盖 unsupported/blocked/input type mismatch/unsafe source provenance/candidate intermediate **以及** processor.extract() 意外异常
- **Source_kind 确定性**：`"annual_report"` 静态值，不从 candidate/fallback 派生
- **测试策略可验证**：marker processor 注入策略可从根源证明 processor path 被实际使用
- **非 active 路径显式残差**：五种基金类型的 direct path 封装为命名 helper，行为保留
- **写入集精确**：4 个允许文件，11 类禁止路径，不足时 stop-and-block
- **约束全部保留**：NOT_READY/candidate-only/no parser replacement/FundDocumentRepository 边界/NAV 降级/repository failure 传播全部不变

### Q4: Did fix introduce any new boundary violation, overreach, contradiction, or under-specified implementation decision?

**NO.**

逐项验证：

| 检查维度 | 结果 | 证据 |
|---|---|---|
| 边界违规 | 无 | 约束保留表（fix evidence:67-77）确认 8 项约束全部保持；`git diff` 确认仅修改 plan artifact 内 5 处位置 |
| 越权 | 无 | 修复均在允许写入集内（plan artifact + fix evidence artifact）；未修改源文件/测试/control docs/design docs |
| 矛盾 | 无 | Fix 1 的 `current_stage.v1` informational 声明与 Fix 1 的 `core_risk.v1` informational 声明一致；Fix 4 的 marker processor 注入策略与 Fix 2 的 fail-closed 规则不冲突 |
| 欠明确 | 无 | 每项修复都给出了具体规则、触发条件和禁止行为；implementation worker 无需自行解释歧义 |

额外验证：`git diff --check` 确认 whitespace clean，无意外变更。

---

## Finding Disposition Table

| ID | Source | Original Severity | Fix Reference | Status | Notes |
|---|---|---|---|---|---|
| MiMo-F1 | MiMo review | blocking | Fix 1 | **CLOSED** | core_risk.v1 全部 5 字段投影规则已明确；current_stage.v1 补充声明 |
| MiMo-F2 | MiMo review | blocking | Fix 2 | **CLOSED** | processor.extract() 意外异常传播契约已明确 |
| MiMo-F3 | MiMo review | nonblocking | Fix 1 (extension) | **CLOSED** | current_stage.v1 已标注为 informational/redundant |
| MiMo-F4 | MiMo review | nonblocking | — | **RESIDUALIZED** | _classified_fund_type() 返回 None 的隐含残差；当前行为正确，不阻塞 |
| MiMo-F5 | MiMo review | nonblocking | Fix 3 | **CLOSED** | source_kind 改为确定性静态值 |
| DS-F1 | DS review | nonblocking | Fix 3 | **CLOSED** | 同上 |
| DS-F2 | DS review | nonblocking | — | **RESIDUALIZED** | tracking_error facade overlay 层叠关系留给 implementation artifact 记录 |
| DS-F3 | DS review | nonblocking | — | **RESIDUALIZED** | bootstrap/processor 一致性假设；同源 in-memory report 保证确定性 |
| DS-F4 | DS review | nonblocking | — | **RESIDUALIZED** | anchor 分配策略留给 implementation worker |
| DS-F5 | DS review | nonblocking | Fix 1 | **CLOSED** | 并入 core_risk fallback 规则澄清 |
| DS-F6 | DS review | nonblocking | Fix 4 | **CLOSED** | marker processor 注入测试策略 |
| DS-F7 | DS review | needs-more-evidence | Fix 5 | **CLOSED** | 推荐 index_fund 冒烟测试，不作为阻塞条件 |

---

## Residual Risks

| Risk | Severity | Owner | Mitigation |
|---|---|---|---|
| tracking_error facade overlay 层叠关系未在 plan 中解释 | 极低 | S2 implementation worker | 实现 artifact 中记录 facade 覆盖 processor 输出的预期行为 |
| Field family anchor 到 field anchor 的分配策略（全量/筛选） | 低 | S2 implementation worker | plan 默认全量映射；后续可按需细化 |
| Bootstrap 分类与 processor 内部 extract_profile 一致性（理论极端） | 极低 | S3 gate owner | 同源 in-memory report 保证确定性；S3 precomputed context 消除 |
| S2 实现发现 exact write set 不足 | 中 | S2 implementation worker | plan 已设 stop condition：写 blocker note，不静默扩 scope |
| 非 active 基金类型（index/enhanced/qdii/fof/unclassified）测试覆盖仅推荐 | 低 | S2 reviewer | 代码路径完全不变（封装为命名 helper）；bond 必测 + index_fund 推荐冒烟 |
| 临时重复 `extract_profile()` 性能开销 | 极低 | S3 gate owner | 仅 memory 重复，无 I/O 重复 |

---

## Review Completeness Statement

本 re-review 执行了以下验证：

- 逐项比对 controller 六项 fix 要求与 plan diff 的实际修改内容，确认一一对应
- 逐项比对 fix evidence 约束保留表与 plan 当前文本、`AGENTS.md` 边界、`design.md` v2.20 Processor/Extractor 边界，确认无退化
- 逐项比对 MiMo F1/F2 的修复规则与 `active_annual.py` 的 `FIELD_FAMILY_MAPPINGS`、`_FAMILY_ORDER`、`_blocked_result()` 和 `contracts.py` 的协议定义，确认代码一致性
- 逐项比对 DS F1-F7 的处置策略与原 review 建议、controller fix 要求，确认无遗漏或过度修复
- `git diff` 验证仅修改 plan artifact 的 5 处位置，零意外变更，whitespace clean
- 固定 plan 全文通读确认无新增矛盾、歧义或边界违规

本 re-review 未执行、也不授权执行：live/source acquisition、PDF/FDR/Docling conversion、provider/LLM、analyze/checklist/golden/readiness/release、PR/push/merge 或任何超出 re-review artifact 写入范围的命令。

Review artifact path: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-rereview-ds-20260618.md`
