# Post-MVP / P4 第一性原理行动计划

> 日期：2026-05-19
> 状态：planning draft
> 输入事实：MVP 已合入 `main`；`docs/code_20260519.csv` 已提供有知有行 App 精选基金池 56 条记录；人工测试 `004393` 生成报告，但暴露基金类型误判和核心字段大量缺失。

## 1. 第一性原理

这个项目的最终目标不是“能生成一篇 Markdown”，而是让普通基金投资者得到一份可复核、可审计、不会误导决策的基金体检报告。

从这个目标倒推，当前系统必须先满足三个底层条件：

1. 年报数据提取必须可度量。
   如果不知道每个字段提取对不对、缺失率多少、错误集中在哪些基金类型，后续分析和报告都只是把不可靠输入包装成更像样的文本。

2. 基金类型判断必须先可靠。
   模板要求先识别基金类型，再应用 `preferred_lens`。如果主动混合基金被误判为指数基金，后续 R=A+B-C、风险项、检查清单和最终判断都会沿着错误路径执行。

3. 报告审计必须阻断低质量输入。
   当前程序审计可以检查 8 章结构、证据附录、计算闭合和检查清单一致性，但它不会因为“关键字段大量 missing”或“基金类型明显错”而阻断报告。这会造成“形式合格、内容不可用”的风险。

因此，P4 不应优先扩功能，而应优先建立质量闭环：先让真实精选基金池的提取质量被量化，再用量化结果驱动 extractor、分类器和审计规则迭代。

## 2. 当前事实

### 2.1 已完成

- MVP 已完成并合入 `main`。
- CLI `fund-analysis analyze FUND_CODE` 可生成 8 章 Markdown 报告。
- 当前程序审计覆盖 P1/P2/P3/L1/R1/R2。
- `docs/code_20260519.csv` 已提供有知有行 App 精选基金池：
  - 56 条记录
  - 55 个唯一基金代码
  - `016492` 重复，需要人工确认
- 已新增 `scripts/selected_funds_smoke.py`，可对精选基金池做 dry-run、抽样 smoke 和执行记录。

### 2.2 新暴露问题

人工测试 `004393 安信企业价值优选混合A` 的报告后发现：

- 报告结构基本合格：8 章、证据附录、证据行、无禁用交易措辞。
- 语义不合格：基金类型被识别为 `index_fund`。
- 关键字段大量缺失：`§3` 表现、`§4` 管理人表述、`§8` 持仓/换手、`§9` 利益一致性、`§10` 份额变动等未稳定命中。
- 现有程序审计没有阻断这类“形式合格但内容低质量”的报告。

直接 root cause 初步判断：

- 基金类型分类器把业绩基准里的“沪深300指数”等指数词误当成基金本身的指数特征。
- 真实年报章节和表格格式异构超出当前 3 只工程样本覆盖范围。
- 当前质量 gate 更偏结构完整性，不够覆盖字段级 extraction quality。

## 3. 当前最该做什么

P4 的第一阶段目标应定义为：

> 建立精选基金池真实年报提取质量评分与报告质量阻断机制，让每一次 extractor 迭代都有可量化的通过率，而不是依赖人工肉眼抽查单篇报告。

这比直接修单个 `004393` 更重要。单点修复可以作为第一批测试用例，但不能替代评分体系。

## 4. 分步骤计划

### Step 1：冻结精选基金池输入

目标：

- 把 `docs/code_20260519.csv` 确认为 P4 初始精选基金池真源。
- 明确 CSV 字段含义：基金名称、基金代码、App 分类。
- 修正或记录 `016492` 重复问题。

产出：

- `docs/selected-funds-quality-plan.md` 或在本文件后续修订中记录字段说明。
- 若确认重复代码是录入错误，修正 CSV；若暂不能确认，保留重复并在 quality gate 中标记。

验收：

- CSV 可被脚本读取。
- 基金代码均为 6 位数字。
- 类别分布可统计。
- 重复代码有明确处理状态。

### Step 2：建立 extraction snapshot

目标：

- 对精选基金池每只基金运行统一的结构化提取，不先生成自然语言报告。
- 输出机器可读 snapshot，记录每个字段的提取值、状态、证据锚点和来源章节。

建议 snapshot 字段：

- `fund_code`
- `fund_name`
- `app_category`
- `classified_fund_type`
- `classification_basis`
- `field_name`
- `extraction_mode`: `direct / estimated / missing / partial`
- `value_present`
- `anchor_present`
- `section_id`
- `table_id`
- `row_id`
- `notes`

产出：

- `reports/extraction-snapshots/<run-id>/snapshot.jsonl`
- `reports/extraction-snapshots/<run-id>/summary.md`

验收：

- 能对至少 1 只基金生成 snapshot。
- 能对按类别抽样基金生成 snapshot。
- 失败不影响后续基金继续记录。

### Step 3：定义字段级评分规则

目标：

- 把“提取质量如何评判”变成可执行规则，而不是口头判断。

第一版评分不必追求复杂，先分三类：

- Coverage：字段是否提取到。
- Traceability：字段是否有可定位证据锚点。
- Correctness：与人工 golden answer 是否一致。

字段重要性建议：

- P0 必须字段：
  - 基金名称
  - 基金代码
  - 基金类型
  - 业绩比较基准
  - 净值增长率
  - 基准收益率
  - 基金规模
  - 管理费/托管费
  - 基金经理/管理人
- P1 关键字段：
  - 投资目标/投资策略
  - 换手率
  - 持有人结构
  - 从业人员/基金经理持有
  - 前十大持仓
  - 份额期初/期末/净变动
- P2 增强字段：
  - 投资者实际收益率
  - 行业分布
  - 跨期变化

建议第一版 gate：

- 基金类型正确率：100% on golden set。
- P0 字段 coverage：>= 90% on golden set。
- P0 字段 traceability：>= 90% on golden set。
- 任一基金若 `classified_fund_type` 与 App 类别明显冲突，则该基金报告不得进入“产品可用”状态。

产出：

- `reports/extraction-scores/<run-id>/scores.jsonl`
- `reports/extraction-scores/<run-id>/summary.md`

### Step 4：建立 golden set

目标：

- 从 56 条精选基金中先选一小批人工核对样本，作为 extractor 迭代的基准。

建议第一批 6 只，按类别覆盖：

- 黄金类：1 只
- 海外股票类：1 只
- 海外债券/稳健类：1 只
- 国内股票类：2 只，其中必须包含 `004393`
- 国内债券类：1 只
- 货币基金类：1 只是否纳入由用户决定；货币基金与当前模板适配度较低，可先作为 edge case

人工标注不需要一次做全量。第一版只标 P0 必须字段，等评分工具跑通后再扩展 P1/P2 字段。

产出：

- `docs/golden-extraction-fields.md`：字段定义和人工标注规则。
- `tests/fixtures/fund/golden/*.json` 或 `docs/golden/*.jsonl`：人工 golden answer。

### Step 5：修复第一批高影响 extraction bug

优先级：

1. 修复基金类型误判。
   规则应区分“基金名称/类别/投资目标表明跟踪指数”和“业绩基准含指数”。主动混合基金使用股票指数作为 benchmark 是正常现象，不能因此判为指数基金。

2. 扩展真实年报表格抽取。
   针对 `004393` 的 §3/§4/§8/§9/§10 缺失，先做 snapshot 取证，再按字段逐个补 extractor。

3. 引入低质量报告阻断。
   当 P0 必须字段或基金类型 gate 不通过时，CLI 应明确输出“数据质量不足，不能生成可用报告”或把报告标记为 smoke failure，而不是生成看似正常的报告。

验收：

- `004393` 不再被识别为 `index_fund`。
- 第一批 golden set 的 P0 coverage / traceability 达到 gate。
- 低质量输入可被质量 gate 识别。

### Step 6：升级报告审计

目标：

- 在现有 P1/P2/P3/L1/R1/R2 基础上，增加报告质量 gate。

建议新增规则：

- FQ1：基金类型与 App 类别 / golden answer 冲突。
- FQ2：P0 必须字段缺失过多。
- FQ3：关键字段无证据锚点。
- FQ4：报告中“数据不足”比例超过阈值。
- FQ5：`preferred_lens` 与基金类型不匹配。

这些规则属于 extraction quality / report quality，不应混入 UI 层。实现位置应优先在 Capability 或 Service orchestration 边界内裁决，不让 UI 直接判断基金语义。

## 5. 与 Dayu-Agent 思路的对齐

Dayu Fins 的关键经验不是“多写几条正则”，而是建立稳定的数据处理与质量评估链路：

- 文档读取、处理、仓储和工具返回语义收敛到统一服务。
- 离线处理和在线工具消费同一份可追溯数据。
- 通过 snapshot / score / hard gate 观察大样本通过率，持续定位低分字段和低分样本。

本项目应采用同样思路：

- 年报只通过 `FundDocumentRepository` 进入系统。
- 结构化抽取先生成 snapshot。
- score 只基于 snapshot 和 golden answer。
- 报告生成只消费已通过质量 gate 的结构化数据，或显式标记低质量。

## 6. 不应立即做的事

暂不优先做：

- 温度计接入最终报告。理由：估值信号接入前，基础年报提取质量尚不可量化。
- 扩展更多自然语言模板。理由：会放大底层字段缺失和误分类。
- 直接跑完整 56 只并人工读报告。理由：没有评分工具时，人工读报告无法形成可复用回归资产。
- 先修所有单点 extractor。理由：没有 snapshot/score，很难判断修复是否泛化。

## 7. 建议的下一步

下一步进入 P4 plan review 前，建议先形成 P4-S1：

> P4-S1：Selected Fund Extraction Snapshot + Quality Gate MVP

P4-S1 范围：

- 读取 `docs/code_20260519.csv`。
- 对指定基金或按类别抽样基金生成 extraction snapshot。
- 输出字段级 coverage / traceability summary。
- 支持 later golden answer 对比，但第一版可以先只做 coverage / traceability。
- 把 `004393` 作为首个已知 failure case 固定进测试或 smoke artifact。

P4-S1 不做：

- 不修所有 extractor。
- 不接温度计到报告。
- 不做 LLM 审计。
- 不做全量 56 只强制通过。

## 8. Open Questions

1. `docs/code_20260519.csv` 中 `016492` 重复如何处理？
   - 选项 A：用户修正 CSV 后再进入 strict gate。
   - 选项 B：P4-S1 允许重复，但在 summary 中标红。

2. 第一批 golden set 选哪些基金？
   - 建议先选 6 只覆盖主要类别，并包含 `004393`。

3. 货币基金是否纳入 P4-S1？
   - 当前 8 章模板更偏权益/债券/指数基金。货币基金可以先作为 edge case，不纳入第一批质量通过率。

4. P4-S1 是否要求真实 network/PDF 全量运行？
   - 建议不要求。先支持指定代码和分层抽样，等 snapshot/score 稳定后再扩大样本。

## 9. Controller Recommendation

建议现在不要继续新增分析功能，而是把 P4 第一阶段定义为“质量系统”：

1. 先做 snapshot。
2. 再做 score。
3. 再修 `004393` 这类高影响 bug。
4. 再把质量 gate 接入报告生成或 smoke CLI。

这样才能把项目从“能生成报告”推进到“知道报告哪里可靠、哪里不可靠，并能持续变好”。
