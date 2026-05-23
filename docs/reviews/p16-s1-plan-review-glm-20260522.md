# P16-S1 Plan Review — AgentGLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

P16-S1 计划在第一性原理正确性、候选列表与 CSV 行锚定、排序规则、stop budget、Repository/Extractor 边界、来源失败分类、`tracking_error` 直接披露契约、no-golden 序列化和 residual owner 分配上均符合 AGENTS.md、design.md、implementation-control.md 和 controller judgment 的要求。三项非阻断 findings 如下。

## Review Inputs

| Input | Role |
|---|---|
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | Plan under review |
| `AGENTS.md` | Agent execution rules |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/post-p15-follow-up-plan-review-controller-judgment-20260522.md` | P16-S1 entry constraints |
| `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md` | Accepted P15-S1A negative evidence result |
| `docs/code_20260519.csv` | Selected-fund source |

## Findings

### F1 — `index_profile.source_tier` 术语未在 design.md 字段名中显式定义

| Field | Value |
|---|---|
| Severity | INFO |
| Evidence | Plan §Evidence Contract: `index_profile` 列出 `index_profile.source_tier` / provenance marker 作为可接受子字段，但 design.md §6.2 只定义 `index_profile` 作为 profile extractor 输出的整体字段，未拆分为 `index_name`、`benchmark_context`、`source_tier` 等子字段。`ExtractionMode`（`direct`/`derived`/`estimated`/`missing`）是已有概念，但 `source_tier` 不是 design.md 已定义的字段名。 |
| Impact | 不阻断。Plan 已声明该子字段是 "metadata, not a standalone golden value" 且必须绑定到与 accepted value 相同的 complete annual-report anchor。Implementation 阶段将通过实际 extractor 输出验证这些子字段映射关系；如 extractor 输出结构与 plan 描述不符，implementation agent 应在 evidence artifact 中记录实际字段名和映射关系。 |
| Required disposition | Implementation artifact 应将 `index_profile` 子字段映射到实际 extractor 输出字段名。如果 `source_tier` 在代码中不存在对应字段，implementation 应使用实际字段名并记录与 plan 的偏差。 |

### F2 — 分类矩阵缺少 fund-type mismatch 显式分类路径

| Field | Value |
|---|---|
| Severity | INFO |
| Evidence | Plan §Required Per-candidate Record 要求 `classified_fund_type` 必须为 `enhanced_index` 才能 golden-candidate eligibility，但 §Evidence Classification Matrix 没有为 "source identity matched 但 structured extraction 返回非 `enhanced_index`" 的情况定义专用分类。现有矩阵覆盖了 source blocker（`not_found`/`unavailable`/`schema_drift`/`identity_mismatch`/`integrity_error`）和 field-level blocker，但未覆盖 fund type 与预期不符的场景。 |
| Impact | 不阻断。Plan 已声明 `classified_fund_type` 必须来自 "Structured extraction / annual-report identity source, not CSV name alone"（Per-candidate Record 表），且 fund name 含"增强"按 design.md §6.5 规则 2 应映射到 `enhanced_index`。五只候选名称均含"指数增强"，fund type mismatch 概率极低。Implementation 阶段如遇到实际 mismatch，应将其记录为 per-candidate blocker 并跳过该候选的 golden eligibility，不编辑 golden rows。 |
| Required disposition | Implementation artifact 应在 per-candidate record 中记录实际 `classified_fund_type`。如实际类型非 `enhanced_index`，该候选不应进入 golden eligibility，但 evidence classification 仍可继续（因为 P16-S1 的产品目标是覆盖所有五个候选）。 |

### F3 — 排序原理未显式回应 controller judgment 的 "shortest evidence loop" 指导

| Field | Value |
|---|---|
| Severity | INFO |
| Evidence | Controller judgment（post-P15 follow-up plan review）F1 disposition 要求 "P16-S1 plan must define an explicit candidate evaluation order and the ordering principle. The default should prefer shortest evidence loop and highest production value while still covering all five candidates." Plan §Candidate Ordering Rationale 采用 CSV 稳定行序 + 指数族分组（1000 → 2000），但未显式讨论 "shortest evidence loop" 或 "highest production value" 如何影响排序。 |
| Impact | 不阻断。Plan 的排序原理是保守且可审计的：不引入外部事实（规模、成立日等），保持 CSV 行序避免不可审计偏好，按指数族分组减少证据形态变量。由于 stop budget 要求覆盖全部 5 个候选（不论顺序），排序只影响实施顺序而非最终覆盖。Controller 指导中的 "shortest evidence loop" 在当前信息约束下无法可靠实现（没有候选证据可用性的先验知识），保守行序是合理替代。 |
| Required disposition | 无需修改 plan。Implementation 可按 plan 定义的顺序执行；如果 implementation 过程中发现某候选有已知 source blocker（如年报不可用），implementation artifact 应记录该 blocker 并继续下一个候选，不需要回到 plan 重新排序。 |

## Correctness Checks

### 候选列表与 CSV 行锚定

| Plan 声称 | CSV 验证 | 结果 |
|---|---|---|
| `004194` 招商中证1000指数增强A, row 38 | Row 38: `招商中证1000指数增强A,004194,国内股票类` | 匹配 |
| `005313` 万家中证1000指数增强A, row 39 | Row 39: `万家中证1000指数增强A,005313,国内股票类` | 匹配 |
| `017644` 博道中证1000指数增强A, row 40 | Row 40: `博道中证1000指数增强A,017644,国内股票类` | 匹配 |
| `019918` 招商中证2000指数增强A, row 41 | Row 41: `招商中证2000指数增强A,019918,国内股票类` | 匹配 |
| `019923` 华泰柏瑞中证2000指数增强A, row 42 | Row 42: `华泰柏瑞中证2000指数增强A,019923,国内股票类` | 匹配 |

五个候选的 fund code、fund name、CSV row 均与 `docs/code_20260519.csv` 一致。CSV 类别为 "国内股票类"，不是 "enhanced_index"；plan 正确要求 `classified_fund_type` 必须来自 structured extraction，不以 CSV name/category 作为 fund type 证据。

### FundDocumentRepository / FundDataExtractor 边界

- Plan 限制年报访问为 `FundDocumentRepository.load_annual_report()` 和 `FundDataExtractor.extract()` ✓
- 禁止路径列表完整覆盖 filesystem 直读、source adapter 直调、Service/UI/Engine 编排、外部搜索 ✓
- 与 AGENTS.md "对基金文档的存取都应该只通过统一的文档仓库接口" 一致 ✓
- 与 design.md §2.2 执行链路和 §6.1 文档仓库层边界一致 ✓

### 来源失败分类与 fail-closed 处理

- 五类 taxonomy 与 AGENTS.md 年报来源 fallback 策略表完全一致 ✓
- `not_found`/`unavailable` 允许 repository-owned fallback ✓
- `schema_drift`/`identity_mismatch`/`integrity_error` fail closed ✓
- Fallback 成功保留 `metadata.fallback_used=True` ✓
- Fail-closed 不允许 fallback rescue 或 golden edits ✓
- 与 P8-S3 source fallback policy 和 P15-S1A 实践一致 ✓

### `index_profile` benchmark-context 子字段契约

- 三个可接受子字段（`index_name`、`benchmark_context`、`source_tier`/provenance）均有明确的 acceptable evidence、required anchor/provenance 和 not-accepted 列表 ✓
- 明确排除 methodology、constituents、weights、provider details、rebalance frequency、index code、external adapter output ✓
- 与 controller judgment F2（"P16-S1 plan must enumerate which `index_profile` subfields can accept benchmark-context evidence"）一致 ✓
- 与 design.md §6.2 profile extractor 产出 `index_profile` 从 §1/§2 benchmark/profile context 的描述一致 ✓
- 注意 F1：子字段名需要在 implementation 阶段与实际 extractor 输出对齐

### `tracking_error` 直接披露契约

- 要求 observed value、period label、annualization support、`source_type="direct_disclosure"`、`calculation_method="disclosed"`、value_parse_status、complete anchor、provenance ✓
- Fail-closed 列表覆盖 target/limit text、manager narrative、benchmark-only、standard-deviation-only、ambiguous/unparseable、incomplete anchor、schema_drift/identity_mismatch/integrity_error、calculated/external/inferred ✓
- Raw mentions 可 inventory 但不可转为 accepted evidence 除非满足全部 direct-disclosure 要求 ✓
- 与 P15-S1A 实践（`001548` 12 个 keyword hit 全部被分类为 target/limit/narrative）完全一致 ✓
- 与 controller judgment F3（explicit source blocker handling）和 design.md §7.4 golden answer 中 "tracking_error 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加" 一致 ✓

### No-golden 序列化

- Plan 多次声明 "下一步仍然不是 golden implementation" ✓
- Evidence acquisition handoff 要求 plan-review 被接受后才能创建 evidence artifact ✓
- Golden implementation handoff 要求 reviewed evidence artifact 接受至少一个候选后才能打开 ✓
- `001548` production `tracking_error` 保持 blocked 除非新的 direct observed evidence ✓
- `161725` 保持 fixture-only，不作为 production selected-fund evidence ✓
- 与 implementation-control.md Active Residuals 和 Active Gate Ledger 中 P15-S1A 的 accepted blocker 一致 ✓

### Residual owner 分配

- `001548` production `tracking_error` golden rows: blocked by P15-S1A ✓
- `161725` enhanced-index tracking-error coverage: test fixture only ✓
- Enhanced-index production golden expansion: P16-S1 future evidence acquisition ✓
- Source metadata retry for `001548`: future evidence retry if selected ✓
- Extractor early-return scope: future extractor-improvement phase if false negative proven ✓
- Index methodology/constituents: future source-contract phase, out of scope ✓
- Calculated tracking error / external index adapters: future calculation/data-source phase, out of scope ✓
- E1-E3 / Evidence Confirm: future audit architecture phase, out of scope ✓
- RR-13 duplicate `016492`: User / App source, untouched ✓
- 每个 residual 有明确 destination 和 status ✓

### Scope creep 检查

- Plan 不引入新 runtime 架构 ✓
- 不引入 Dayu runtime、Host、Engine、tool loop ✓
- 不引入 LLM writing ✓
- 不引入 calculated tracking error 或 external index adapters ✓
- 不引入 methodology/constituents extraction ✓
- 不引入 QDII subtype redesign ✓
- 不引入 E1-E3 或 Evidence Confirm 执行 ✓
- Plan gate 只产出 plan artifact，不修改 source/test/golden/README/design/control/CSV/RR-13/external state ✓

### Validation signals

- Plan gate: only artifact created, `git diff --check HEAD` passes ✓
- Future evidence acquisition: 10 项验证信号覆盖 identity records、field separation、anchor requirements、source blocker taxonomy、no golden edits ✓
- Future golden gate: opens only after reviewed evidence, adds rows only from accepted selected-fund evidence, runs full validation suite ✓

## Summary

Plan 的第一性原理链条完整：P15-S1A 证明 `001548` 无 direct observed `tracking_error` 披露 → 不继续推 `001548` → 转向其余 5 只 selected-fund enhanced-index 候选 → 通过相同 Repository/Extractor 边界获取 evidence → 分别评估 `index_profile` benchmark-context 和 `tracking_error` direct disclosure → 只有通过全部契约的候选才能进入后续 golden gate。三项 INFO findings 均可在 implementation 阶段自然收口，不需要修改 plan。

## Reviewer Limitations

本 review 基于 plan 文本、AGENTS.md、design.md、implementation-control.md、controller judgment 和 CSV 文件进行。未对 `FundDataExtractor` 实际 extractor 输出结构、`index_profile` 实际子字段名称、或五只候选的实际年报可用性进行运行时验证。Implementation 阶段应通过 `FundDocumentRepository.load_annual_report()` 和 `FundDataExtractor.extract()` 实际调用来验证 plan 中的子字段映射和候选可用性假设。
