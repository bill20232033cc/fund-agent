# P5-S2 Quality Gate Rules Plan - 2026-05-20

## Verdict

P5-S2 plan patched after controller review.

本 slice 目标是关闭 P4-R9：补齐 FQ1 App 类别冲突分支、FQ4 数据不足比例、FQ5 `preferred_lens_resolvability`。实现范围必须保持在 Capability 层，继续只消费 `score.json` 和 snapshot/score 已有数据，不把基金质量规则上移到 Service 或 CLI。

下一 gate：`P5-S2 plan re-review`。

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4 control doc: `docs/implementation-control-p4.md`
- P5-S1 acceptance: `docs/reviews/p5-s1-acceptance-reconciliation-20260520.md`
- Existing Capability code:
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`
  - `fund_agent/fund/fund_type.py`

## First Principles

报告质量 gate 的职责不是“补写报告”，而是在输入质量或语义契约已经不可信时阻断或标记报告可用性。P5-S2 要增加的是可解释、可测试、数据同源的规则，不能用经验口径猜测基金类型，也不能直接读取报告 Markdown 去数中文短语。

规则输入必须来自同一质量链路：

- `score.json.field_scores`：字段 coverage / traceability。
- `score.json.fund_scores`：单基金 P0/P1 状态与 App 类别。
- `score.json.correctness`：strict golden answer correctness。
- P5-S2 新增 `score.json.fund_quality`：从 snapshot records 同源派生的基金类型、App 类别冲突、preferred_lens 匹配和数据不足比例。

## Scope

### 1. Extraction score 输出基金质量派生信息

在 `fund_agent/fund/extraction_score.py` 中新增结构化输出 `fund_quality`，每只基金一行，建议字段：

| 字段 | 含义 |
|---|---|
| `fund_code` | 基金代码 |
| `fund_name` | 基金名称 |
| `app_category` | App 类别 |
| `classified_fund_type` | 系统识别基金类型 |
| `app_category_status` | `match / conflict / unknown` |
| `preferred_lens_status` | `match / mismatch / unknown` |
| `preferred_lens_key` | 由标准基金类型解析出的模板 lens key |
| `missing_field_count` | `value_present=False` 的字段数 |
| `total_field_count` | 参与评分字段数 |
| `missing_field_rate` | `missing_field_count / total_field_count` |
| `missing_p0_fields` | 缺失的 P0 字段 |
| `missing_p1_fields` | 缺失的 P1 字段 |
| `reason` | 人类可读原因 |

`fund_quality` 必须从 `score_fund_records(...)` 已消费的 snapshot records 同源派生，不读取 PDF、cache、报告 Markdown、Service 返回值或 CLI 输出。

同一基金的基金级字段必须按全部 snapshot records 做唯一性检查：

- `fund_name`、`app_category`、`classified_fund_type` 多行一致时才作为确定值输出。
- 多个非空 `app_category` 或 `classified_fund_type` 冲突时，不能取第一行；必须在 `reason` 中列出冲突值。
- `classified_fund_type` 冲突时，`preferred_lens_status=mismatch`。
- `app_category` 冲突时，`app_category_status=unknown`。

### 2. FQ1 App 类别冲突分支

当前 FQ1 已覆盖 correctness mismatch。P5-S2 增加 App 类别冲突分支：

- App 类别映射必须配置化，放在 Capability 层常量或小型配置结构中，不散落在条件分支里。
- 仅在 App 类别可明确映射为允许的标准基金类型集合时判断。
- `classified_fund_type` 不在允许集合时触发 `FQ1/block`。
- 类别缺失、无法映射或基金类型缺失时输出 `unknown`，不阻断，避免间接证据误杀。

首版建议映射：

| App 类别 | 允许基金类型 |
|---|---|
| 国内股票类 | `active_fund / index_fund / enhanced_index` |
| 国内债券类 | `bond_fund` |
| 海外股票类 | `qdii_fund` |
| 海外债券/稳健类 | `qdii_fund / bond_fund / fof_fund` |
| 黄金类 | `qdii_fund / fof_fund / index_fund / enhanced_index` |
| 货币基金类 | unknown；当前 golden set 已排除，P5-S2 不新增货币基金分类 |

这个映射是质量 gate 判断，不替代 `fund_type.py` 的年报分类逻辑。

### 3. FQ4 数据不足比例

FQ4 不应读取最终报告 Markdown 中“数据不足”的字面次数；那会把渲染措辞和质量规则耦合。首版按 snapshot 字段缺失率判断：

- 单基金 `missing_field_rate >= 0.35` 触发 `FQ4/block`。
- 单基金 `missing_field_rate >= 0.20` 且 `< 0.35` 触发 `FQ4/warn`。
- 只统计 P0/P1/P2 snapshot 字段；未知字段可计入分母但 priority 记录为 `UNMAPPED`。
- FQ2/FQ2F 已覆盖 P0/P1 fail；FQ4 的价值是捕捉“低优先级或整体字段大量缺失导致报告整体不可用”的横向质量问题。

阈值必须显式常量化，测试覆盖边界值。

### 4. FQ5 preferred_lens resolvability

P5-S2 不接入完整 CHAPTER_CONTRACT parser，也不让 Service 传入 lens。首版将 FQ5 明确定义为 `preferred_lens_resolvability`：质量链路中基金类型是否能支持模板 preferred_lens 的确定选择。

需要新增配置化 `preferred_lens_key` 映射并覆盖 6 个标准基金类型：

| classified_fund_type | preferred_lens_key |
|---|---|
| `index_fund` | `index_fund` |
| `active_fund` | `active_equity_fund` |
| `bond_fund` | `bond_fund` |
| `enhanced_index` | `enhanced_index` |
| `qdii_fund` | `qdii_fund` |
| `fof_fund` | `fof_fund` |

首版判断：

- `classified_fund_type` 在标准集合且能解析 `preferred_lens_key`：`match`。
- `classified_fund_type` 不在标准集合或缺失：`mismatch`，触发 `FQ5/block`。
- App 类别可明确映射但与 `classified_fund_type` 冲突：`mismatch`，触发 `FQ5/block`，原因写为“类型冲突导致 lens 选择不可信”。这会和 FQ1 App 类别冲突同时出现，但 FQ5 只表达 lens resolvability，不宣称已经校验最终报告中的实际 lens。
- App 类别 unknown 但 `classified_fund_type` 有效：`match`，因为 Service 已能按标准基金类型选择 preferred_lens。

后续若模板资产中落地机器可读 `CHAPTER_CONTRACT`，再把 FQ5 升级为实际 contract lens 校验；本 slice 不做未来设计。

### 5. QualityGateIssue metadata schema

为避免把结构化判断塞进自然语言 message，P5-S2 需要扩展 `QualityGateIssue` 的可选字段：

| 字段 | 用途 |
|---|---|
| `app_category` | FQ1/FQ5 输出 App 类别 |
| `classified_fund_type` | FQ1/FQ5 输出系统基金类型 |
| `preferred_lens_key` | FQ5 输出解析到的 lens key |
| `observed_rate` | FQ4 输出缺失率 |
| `threshold` | FQ4 输出触发阈值 |

FQ4 不复用 `coverage_rate` 表示缺失率，避免字段语义混乱。

## Non-Goals

- 不修改 `FundAnalysisService` 的 quality gate 接入策略；P5-S1 已完成。
- 不读取或解析最终报告 Markdown。
- 不引入 LLM 审计。
- 不修改 `fund_type.py` 的分类规则。
- 不扩大 correctness denominator；P5-S3 单独负责。
- 不处理失败基金只在 `errors.jsonl` 的 accounting；P5-S4 单独负责。

## Implementation Slices

1. `extraction_score.py`
   - 新增 `FundQualityRow` dataclass。
   - 新增从 snapshot records 派生 `fund_quality` 的函数。
   - 将 `fund_quality` 写入 `score.json` 与 `score.md`。
   - 保持现有 `field_scores` / `fund_scores` schema 兼容。

2. `quality_gate.py`
   - 读取并校验可选 `fund_quality`。
   - 新增 FQ1 App 类别冲突 issue。
   - 新增 FQ4 缺失率 issue。
  - 新增 FQ5 preferred_lens resolvability issue。
   - 对旧 score.json 缺少 `fund_quality` 保持兼容：输出 `FQ0/info` 或跳过新增规则，不抛 fatal。

3. Tests
   - `tests/fund/test_extraction_score.py`
     - `fund_quality` 输出基金类型、App 类别状态、preferred_lens 状态、缺失率和缺失字段。
     - App 类别 unknown 不阻断。
   - `tests/fund/test_quality_gate.py`
     - FQ1 App 类别冲突触发 block。
     - FQ4 warn/block 阈值边界。
     - FQ5 基金类型缺失或非法触发 block。
     - 旧 score.json 缺少 `fund_quality` 不 fatal。

4. Docs
   - 更新 `fund_agent/fund/README.md`：说明 `fund_quality`、FQ1/FQ4/FQ5 当前规则输入与边界。
   - 更新 `tests/README.md`：新增 P5-S2 quality gate rules 测试维护口径。

## Acceptance Criteria

- `score.json` 包含稳定 `fund_quality` 数组。
- FQ1 同时支持 correctness mismatch 和 App 类别冲突。
- FQ4 基于 snapshot 缺失率触发 warn/block，不依赖报告 Markdown 文案。
- FQ5 能在基金类型缺失、非法或与 App 类别明确冲突时阻断。
- 旧 score.json 缺少 `fund_quality` 时 quality gate 仍可运行。
- Targeted tests、full suite、ruff、diff check 通过。

## Risks And Tracking

| Risk | Decision |
|---|---|
| App 类别映射过窄误伤真实基金 | 首版只对明确类别判断；unknown 不阻断；映射集中配置并测试 |
| FQ4 与 FQ2/FQ2F 重叠 | 接受重叠；FQ4 表达整体数据不足，FQ2/FQ2F 表达字段优先级失败 |
| FQ5 没有机器可读 CHAPTER_CONTRACT | 首版按标准基金类型是否能确定 preferred_lens 判断；contract parser 留到模板资产机器化后 |
| FQ5 首版不是最终报告 lens 校验 | 明确命名为 `preferred_lens_resolvability`；后续机器可读 CHAPTER_CONTRACT 后再升级 |
| 货币基金未纳入标准类型 | 保持 unknown，不新增分类标签，不阻断 |

## Gate Decision

当前 gate 从 `P5-S2 plan review` 推进为 `P5-S2 plan patched after controller review`。

下一步进入 `P5-S2 plan re-review`。
