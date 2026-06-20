PLAN_REVIEW_PASS_WITH_FINDINGS

## Findings

### F1 [CRITICAL] Slice 2 错误复用 product_essence selector，导致 family ownership 混乱

**Plan 引用**: Implementation Slices → Slice 2，第 129–131 行：
> Reuse existing product-essence risk-characteristic selection: call `_select_product_essence_values(intermediate, context)`; use only output path `risk_characteristic_text.risk_characteristic_text`

**证据**: `fund_disclosure_processor.py:3666–3698` 中 `_select_product_essence_values()` 收集全部 `_PRODUCT_ESSENCE_LABELS`（覆盖 basic_identity、product_profile、benchmark、risk_characteristic_text 四个 top-level 共约 15 条 output path），只为 `core_risk.v1` 取其中一条 `risk_characteristic_text.risk_characteristic_text`。

**问题**:
- `_select_product_essence_values()` 是 product_essence 族所有的 selector，其函数签名、返回值类型 `_ProductEssenceValueCandidate`、内部调用的 `_collect_product_essence_table_candidates` / `_collect_product_essence_paragraph_candidates` 全部绑定 product_essence 的 label 集合和 resolution 逻辑。
- 让 `core_risk.v1` 调用 product_essence 族所有的 selector 会：
  a) 浪费计算：为 `core_risk` 收集 basic_identity、product_profile、benchmark 等无关候选值；
  b) 制造跨族耦合：未来 product_essence 的 selector 行为变更会意外影响 core_risk；
  c) 语义混乱：`_select_product_essence_values` 返回的是 `_ProductEssenceValueCandidate` 类型，core_risk 不应依赖 product_essence 的内部类型。

**修正要求**: 将 risk_characteristic_text 的 table/paragraph 候选收集和 resolution 逻辑抽取为共享的、族中立的私有函数（例如 `_collect_risk_characteristic_table_candidates()` + `_select_risk_characteristic_value()`），product_essence 和 core_risk 共同调用，而不是让 core_risk 整体调用 `_select_product_essence_values()`。`_build_risk_characteristic_text_value()` 的共享 helper 思路正确，但 selector 层面也需要同样的族中立重构。

---

### F2 [HIGH] Gate 名称 `core_risk.v1 Source-truth Direct Extraction` 与实现范围严重不匹配

**Plan 引用**: Goal / Non-goal / Success Signal，第 5–8 行。

**证据**: Plan 的 public contract 只提取 `risk_characteristic_text`（1/5 candidate roles），其余 4 个 role（liquidation_or_scale_risk、tracking_error_or_deviation_risk、turnover_or_style_drift_risk、concentration_risk）全部保持 candidate-only/deferred。而 gate 标签 `core_risk.v1 Source-truth Direct Extraction` 读起来像是完成了全部 core_risk 族 source-truth。

**问题**: 后续读者（controller、reviewer、未来 gate owner）在 `docs/implementation-control.md` 和 commit history 中看到 `core_risk.v1 source-truth direct extraction accepted` 时，会误以为 5 个 candidate role 均已提取。虽然 Non-goals 第 26 行明确列出了不做的项，但 gate 名称没有传达这个范围限制。

**修正要求**:
- 将 gate 标签改为 `core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`，或
- 在 Public Contract 开头增加强制性 gate-scope 声明：`本 gate 仅实现 core_risk.v1 五个 candidate role 中的 risk_characteristic 单一 subvalue；其余四个 role 保持 candidate-only/deferred。完整 core_risk.v1 source truth 需要后续独立 gate。`
- 该 scope 声明必须写入 `docs/design.md` 和 `docs/implementation-control.md` 的 docs-sync slice。

---

### F3 [HIGH] Deferred candidate roles 在 direct extraction 路径中无公开缺口语义

**Plan 引用**: Candidate role disposition，第 63–71 行；Direct route candidate evidence，第 109–112 行。

**证据**:
- Plan 规定 proof-positive 路径 `candidate_evidence=()`（第 111 行），这意味着四个 deferred role 在 direct extraction 成功时完全不可见——既不在 value 中，也不在 candidate_evidence 中，也不在 gaps 中。
- 对比 `investor_experience.v1`：deferred role（subscription_redemption、income_distribution）虽不在 required top-level，但在 design.md:6 中被显式标注为「仍只作为 candidate locator roles，不进入 public value」。core_risk 的 plan 缺少同等力度的公开声明。
- 对比 `_product_essence_source_truth_gaps()`（第 4213–4268 行）：当 required top-level 缺失时产生 `field_family_partial` gap。但 core_risk 只有一个 required subvalue（risk_characteristic_text），如果它存在，status 就是 `accepted`，gaps 为空——消费者无法区分「core_risk.v1 已完整覆盖」和「只覆盖了 1/5 role」。

**修正要求**:
- 在 Public Contract 中增加 deferred roles 的显式声明（模仿 design.md:6 对 subscription_redemption/income_distribution 的标注方式）。
- 在 `_core_risk_source_truth_gaps()` 中为每个 deferred role 增加 `gap_code="deferred_role"` 且 `required=False` 的 gap 条目，或增加独立的 `deferred_roles` 元数据字段。
- 在 Test Matrix 中增加一条：proof-positive accepted 时，gaps 包含四个 `deferred_role` 条目。

---

### F4 [MEDIUM] Facade fallback 死代码激活未显式承认

**Plan 引用**: Facade projection，第 73–78 行。

**证据**: `data_extractor.py:742–754` 中 `core_risk.v1 → only risk_characteristic_text fallback` 今天处于死代码状态，因为 `core_risk.v1` 当前永远返回 candidate-only/missing（`fund_disclosure_processor.py:1028` 直接走 `_select_core_risk_candidate_evidence`）。Plan 正确指出「Existing projection may be used only as currently implemented」，但未承认：一旦 core_risk.v1 实现 source-truth direct extraction 并可返回 `accepted` + `risk_characteristic_text`，这段死代码将首次进入活跃路径。

**问题**: 该 fallback 路径从未经过真实 core_risk.v1 值的集成测试——既有的 data_extractor 测试（`tests/fund/test_data_extractor.py:720-987`）中 core_risk family marker 没有 projected public bundle field。Slice 4 的 facade 测试可以填补这个缺口，但 plan 未明确指出这是该路径的首次激活。

**修正要求**: 在 Slice 4 描述中增加声明：`本 slice 的 facade 测试是 data_extractor.py:742-754 fallback 路径的首次激活验证；既有测试中该路径为死代码。` 不需要改变 plan 结构，只需增加这一承认。

---

### F5 [MEDIUM] `_select_core_risk_values()` 未充分指定

**Plan 引用**: Slice 2，第 128–131 行。

**问题**: Plan 列出 helper 名称 `_select_core_risk_values()` 但不说明其内部实现策略。第 129 行的「Reuse existing product-essence risk-characteristic selection」既可能是调用 `_select_product_essence_values()` 后取子集（错误，见 F1），也可能是复制 product_essence 的 table/paragraph 收集逻辑到 core_risk（重复代码），也可能是提取共享 helper（正确方案）。

**修正要求**: 在 Slice 2 中显式指定 `_select_core_risk_values()` 的调用链：应调用共享的 `_collect_risk_characteristic_table_candidates()` / `_collect_risk_characteristic_paragraph_candidates()`，只收集 `risk_characteristic_text.risk_characteristic_text` 一个 output path 的候选值，返回类型为族中立的 `_RiskCharacteristicValueCandidate`。与 F1 的修正合并处理。

---

### F6 [LOW] 缺少 risk_characteristic_text 歧义路径的 core_risk 专项测试

**Plan 引用**: Test Matrix → Processor tests，第 181–193 行。

**证据**: `_product_essence_source_truth_gaps()`（第 4213–4268 行）为 ambiguous_paths 产生 `ambiguous_table_or_locator` gap。Plan 的 `_core_risk_source_truth_gaps()` 应遵循相同模式，但 Test Matrix 中没有「risk_characteristic_text 在 core_risk 上下文中歧义时返回 missing + ambiguous_table_or_locator gap」的测试用例。

**问题**: 不同族对歧义可能有不同容忍度——product_essence 有多条 output path，一条歧义不一定导致 overall missing；core_risk 只有一条 output path，歧义直接导致 overall missing。这个行为差异需要显式测试。

**修正要求**: Test Matrix 增加一条：`proof-positive risk-characteristic ambiguous → status="missing", value={}, anchors=(), gap_code="ambiguous_table_or_locator", candidate_evidence=()`。

---

### F7 [LOW] Forbidden files 遗漏 `docs/fund-analysis-template-draft.md`

**Plan 引用**: Allowed / Forbidden Files And Modules，第 235–242 行。

**问题**: 虽然 plan 不涉及模板修改，但 `docs/fund-analysis-template-draft.md` 包含 CHAPTER_CONTRACT 机制和 TEMPLATE_CONTRACT_MANIFEST_JSON，其中 Chapter 6 对应 core_risk。作为模板真源文件，应显式列入 forbidden 清单以避免在 planning gate 中被意外修改。

**修正要求**: 在 Forbidden files 列表中增加 `docs/fund-analysis-template-draft.md`。

---

## Residual Risks / Open Questions

1. **共享 helper 重构对 product_essence 的回退风险**：当 `_build_risk_characteristic_text_value()` 从 product_essence 内部逻辑抽取为共享 helper 时，product_essence 的既有测试（`test_fund_disclosure_processor.py` 中 product_essence 相关 case）必须全部通过且 shape 不变。Plan 第 250 行将此列为 residual risk，但未要求实现 gate 在合并前运行完整 product_essence 测试套件。**建议**: 在 Validation Matrix 中增加 `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k "product_essence"` 作为必过命令。

2. **`_CORE_RISK_REQUIRED_TOP_LEVEL` 常量设计**：Plan 说只有 `risk_characteristic_text` 一个 required subvalue，status 无 `partial`（第 57–58 行）。但如果后续 gate 增加第二个 subvalue，这个设计需要重写 status 逻辑。当前的 `accepted | missing` 二元状态是刻意的简化还是为实现便利？**建议**: 在 plan 中注明「status 二元化是当前 scope 的刻意设计，后续增加 subvalue 需重写 `_core_risk_status()`」，避免未来 reviewer 认为这是 bug。

3. **Candidate boundary 路径下 deferred role 候选证据的行为**：Plan 说 candidate boundary → `contract_status="blocked"`，candidate evidence 保持 candidate-only（第 104–107 行）。此时 deferred role（liquidation/scale 等）的候选证据是否仍然出现在 `_select_core_risk_candidate_evidence()` 中？当前代码（`fund_disclosure_processor.py:7570–7850`）会为所有 5 个 role 选择候选证据，这个行为在 plan 中没有被改变——确认这是预期行为。**建议**: 在 candidate boundary 测试用例中增加 deferred role candidate evidence 存在性验证。

---

## Evidence Summary

Review 基于以下真源：

| 真源 | 关键行/节 | 用途 |
|---|---|---|
| `AGENTS.md` | 全文 | 执行规则真源，Gate 分类、模块边界 |
| `docs/design.md:5-8` | FDD source-truth 当前状态 | 确认 core_risk.v1 未实现，5 族已实现 |
| `docs/design.md:674-678` | FDD proof-positive 契约 | 确认 admission proof 机制和 candidate evidence 身份 |
| `docs/implementation-control.md:10-11` | current_stage.v1 gate scope | 确认 core_risk.v1 未被授权并行实现 |
| `docs/current-startup-packet.md:23-27` | next entry point | 确认 core_risk.v1 是下一入口但未授权 |
| `fund_disclosure_processor.py:42-49` | `_FAMILY_ORDER` | 确认 core_risk.v1 在族顺序中 |
| `fund_disclosure_processor.py:658-727` | `_CORE_RISK_MATCH_GROUPS` | 确认 5 个 candidate role 的现有定义 |
| `fund_disclosure_processor.py:980-1069` | `_field_families_for_intermediate()` | 确认 core_risk 当前走 candidate-only，5 族走 direct |
| `fund_disclosure_processor.py:1121-1158` | `_extract_product_essence_source_truth()` | 确认 source-truth extraction 的标准模式 |
| `fund_disclosure_processor.py:3666-3698` | `_select_product_essence_values()` | 发现 F1：product_essence 族所有 selector 全量收集 |
| `fund_disclosure_processor.py:4008-4047` | `_build_product_essence_value()` | 确认 risk_characteristic_text 的当前 shape |
| `fund_disclosure_processor.py:4213-4288` | `_product_essence_source_truth_gaps()` / `_product_essence_status()` | 确认 gap/status 模式 |
| `fund_disclosure_processor.py:6380-6456` | `_investor_experience_source_truth_gaps()` / `_investor_experience_status()` | 确认 deferred role 在 gap 中的处理模式 |
| `data_extractor.py:708-754` | `_active_processor_result_to_bundle()` | 确认 facade fallback 死代码路径 |

---

## Stop Condition Status

本 review artifact 是此 gate 写入的唯一文件。未修改 plan、代码、tests、docs/control、startup packet 或任何其他文件。未 commit、未 push、未进入 implementation。
