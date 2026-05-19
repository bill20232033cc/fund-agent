# P4 实施控制文档：精选基金池质量闭环

> **版本**: v0.1
> **日期**: 2026-05-19
> **状态**: P4-S3b accepted
> **设计真源**: `docs/design.md`
> **全局总控**: `docs/implementation-control.md`
> **P4 第一性原理计划**: `docs/post-mvp-p4-first-principles-plan.md`
> **P4 裁决记录**: `docs/reviews/p4-audit-input-controller-judgment-20260519-0144.md`
> **精选基金池输入**: `docs/code_20260519.csv`

---

## 1. P4 北极星

P4 的目标不是继续扩展报告功能，而是建立精选基金池真实年报提取质量闭环，让系统从“能生成报告”推进到“知道报告哪里可靠、哪里不可靠，并能持续变好”。

P4 必须优先解决三个底层问题：

1. 年报数据提取质量必须可度量。
2. 基金类型判断必须可靠，因为它决定 `preferred_lens` 和后续审计路径。
3. 报告审计必须能识别低质量输入，避免“形式合格、内容不可用”的报告误导用户。

当前已知 failure case：

- `004393 安信企业价值优选混合A` 曾被误判为 `index_fund`，P4-S3a 已修复为 `active_fund`。
- `004393` 仍存在 `§3/§4/§8/§9/§10` 多个关键字段缺失，P4-S3b 继续修复。

---

## 2. 当前 Gate

| 项目 | 状态 |
|---|---|
| 当前 phase | P4 |
| 当前 gate | `P4-S3b accepted` |
| 下一 gate | `P4-S4 implementation` |
| 当前分支 | `main` |
| P4 输入池 | `docs/code_20260519.csv` |
| 已知数据质量问题 | `016492` 重复；56 条记录、55 个唯一代码 |

P4-S1 进入 implementation 前置条件已完成：

- `docs/implementation-control-p4.md` 已通过 MiMo/GLM plan review 与 controller 裁决。
- `P4-S1` 的实现范围、验收条件和非目标明确。
- `016492` 重复处理口径明确：P4-S1 允许重复但 summary 必须标红；真实修正需用户核对 App 源数据。

---

## 3. Phase 切片

| Slice | 名称 | 状态 | 依赖 | 验收信号 |
|---|---|---|---|---|
| P4-S1 | Selected Fund Extraction Snapshot + Quality Gate MVP | ✅ accepted | P3 | 能对指定基金和分层抽样基金生成 snapshot 与 summary |
| P4-S2 | 字段级评分规则 + Golden Set 标注 | ✅ accepted | P4-S1 | P0 字段 coverage / traceability 可计算 |
| P4-S3a | 基金类型误判修复 | ✅ accepted | P4-S2 | `004393` 不再误判为 `index_fund`，snapshot 显示 `active_fund` |
| P4-S3b | 高影响 extractor 缺口修复 | ✅ accepted | P4-S3a | `004393` 的高影响缺失字段由 score 证明改进 |
| P4-S4 | 报告质量审计与阻断 | ⬜ pending | P4-S3 | 低质量输入可被 quality gate 标记或阻断 |

---

## 4. P4-S1：Selected Fund Extraction Snapshot + Quality Gate MVP

### 4.1 目标

建立第一版 extraction snapshot，让精选基金池真实年报提取结果变成可记录、可比较、可复核的结构化产物。

P4-S1 只解决“看清楚质量”的问题，不修所有 extractor。

### 4.2 范围

P4-S1 应完成：

- 读取 `docs/code_20260519.csv`。
- 校验基金池记录：
  - 基金名称非空
  - 基金代码为 6 位数字
  - App 类别非空
  - 重复代码在 summary 中标红
- 对指定基金生成 extraction snapshot。
- 对按类别抽样基金生成 extraction snapshot。
- snapshot 记录字段级提取状态、证据锚点和来源定位。
- 输出 `snapshot.jsonl` 与 `summary.md`。
- 支持失败继续记录，不让单只基金失败中断整个 run。

### 4.3 实现约束

P4-S1 snapshot 生成必须遵守当前项目边界：

- 年报访问必须通过 `FundDocumentRepository` 或 `FundDataExtractor` 进入统一文档仓库契约，禁止上层代码直接读取 `fund_agent/fund/pdf/*`、`cache/pdf/*` 或本地 PDF 文件。
- snapshot 生成核心能力默认放在 Capability 层（`fund_agent/fund/`），CLI / scripts 只能作为薄入口调用稳定接口；不得把基金文档解析和字段判断写在 UI 层。
- 输入参数必须显式传递，包括 `fund_code`、`report_year`、`source_csv`、`run_id` 和输出目录；禁止把这些显式参数塞进 `extra_payload` 或依赖隐式 cwd。
- P4-S1 优先复用现有 `FundDataExtractor.extract(...)` 与 `StructuredFundDataBundle` 作为 façade；若字段级粒度不足，允许在 Capability 层补充 snapshot adapter，但仍不得绕过统一文档仓库接口。
- snapshot 只记录当前 extractor 的真实输出，不得为了让 known failure “好看”而覆盖或修正字段值。

推荐实现路径：

1. 由 snapshot adapter 调用 `FundDataExtractor.extract(fund_code, report_year, force_refresh=...)`。
2. 将 `StructuredFundDataBundle` 拆解为字段级 `SnapshotRecord`。
3. 对 bundle 中仍保留 `ExtractedField` 的字段记录 `extraction_mode`、`value_present`、`anchor_present` 和首个锚点位置。
4. 对分类结果等 bundle 内派生字段记录为 profile 组下的字段，并保留 `classification_basis`。
5. 若 P4-S1 发现 façade 已丢失某些必要字段级证据，只记录为 P4-S2/P4-S3 follow-up，不在 P4-S1 绕过分层重写 extractor。

### 4.4 非目标

P4-S1 不做：

- 不修复 `004393` 类型误判。
- 不扩展所有 extractor。
- 不建立完整 golden answer。
- 不接入温度计到报告。
- 不引入 LLM 审计。
- 不把 quality gate 接入 CI。
- 不做完整 56 只强制通过。

### 4.5 Snapshot Schema 初版

每条 snapshot 记录至少包含：

| 字段 | 说明 |
|---|---|
| `run_id` | 本次运行 ID |
| `extraction_timestamp` | ISO-8601 时间 |
| `source_csv` | 精选基金池 CSV 路径 |
| `fund_code` | 基金代码 |
| `fund_name` | App 清单中的基金名称 |
| `app_category` | App 清单中的类别 |
| `report_year` | 年报年份 |
| `classified_fund_type` | 系统识别基金类型 |
| `classification_basis` | 类型识别依据 |
| `field_name` | 字段名 |
| `field_group` | 字段组，如 profile/performance/manager/holdings/share_change |
| `extraction_mode` | `direct / estimated / missing / partial` |
| `value_present` | 是否有非空值 |
| `anchor_present` | 是否有证据锚点 |
| `section_id` | 年报章节 |
| `page` | 页码，可为空 |
| `table_id` | 表格 ID，可为空 |
| `row_id` | 行 ID，可为空 |
| `note` | 降级、缺失或异常说明 |

`extractor_version` 暂不要求接复杂版本系统；若实现成本低，可记录当前 git commit 或 package version。

`field_name` 使用与代码同源的 snake_case 标识符，不使用自然语言字段名。自然语言字段等级在 P4-S2 中再映射到这些标识符。

第一版字段映射如下：

| field_group | field_name |
|---|---|
| profile | `basic_identity` |
| profile | `product_profile` |
| profile | `benchmark` |
| profile | `fee_schedule` |
| profile | `classified_fund_type` |
| performance | `nav_benchmark_performance` |
| performance | `investor_return` |
| manager | `manager_strategy_text` |
| manager | `turnover_rate` |
| manager | `manager_alignment` |
| holder | `holder_structure` |
| holdings | `holdings_snapshot` |
| share_change | `share_change` |
| nav | `nav_data` |

统计粒度约定：

- `snapshot.jsonl` 每行是 field-level 记录，但可以重复携带 run-level 和 fund-level 字段，便于流式处理。
- `summary.md` 至少输出 run-level、fund-level 和 per-field 三类统计。
- `source_csv` 使用相对 repo root 的路径，例如 `docs/code_20260519.csv`。

### 4.6 输出路径

建议输出：

- `reports/extraction-snapshots/<run-id>/snapshot.jsonl`
- `reports/extraction-snapshots/<run-id>/summary.md`
- `reports/extraction-snapshots/<run-id>/errors.jsonl`

这些输出属于运行产物，不要求纳入 Git。

### 4.7 验收条件

P4-S1 通过条件：

- 能对 `004393` 生成 snapshot。
- 能按类别各抽 1 只生成 snapshot。
- `summary.md` 显示：
  - 总记录数
  - 成功/失败基金数
  - 各 App 类别数量
  - 重复代码列表
  - 每个字段的 coverage / traceability 粗略统计
- snapshot 中 `004393` 的 `classified_fund_type=index_fund` 被记录为 known failure，而不是被静默覆盖。
- 单只基金失败时，run 能继续并记录错误。

### 4.8 建议测试

- CSV 校验测试：重复代码、缺失字段、非法代码。
- snapshot schema 测试：每条记录必含核心字段。
- `004393` known failure 测试：分类结果必须能被 snapshot 捕获。
- dry-run / no-network 测试：默认不触发真实 PDF/network。

---

## 5. P4-S2：字段级评分规则 + Golden Set 标注

### 5.1 目标

在 P4-S1 snapshot 基础上，建立第一版字段级评分规则和最小 golden set。

### 5.2 字段等级

P4-S2 前半段使用与 P4-S1 snapshot 同源的 `field_name` 标识符评分，不使用自然语言字段名作为程序输入。

P0 必须字段映射：

| field_name | 对应自然语言字段 |
|---|---|
| `basic_identity` | 基金名称、基金代码、基金规模、基金经理或管理人 |
| `classified_fund_type` | 基金类型 |
| `benchmark` | 业绩比较基准 |
| `nav_benchmark_performance` | 净值增长率、基准收益率 |
| `fee_schedule` | 管理费、托管费 |
| `manager_strategy_text` | 基金经理或管理人策略文本 |

P1 关键字段映射：

| field_name | 对应自然语言字段 |
|---|---|
| `product_profile` | 投资目标、投资范围、投资策略 |
| `turnover_rate` | 换手率 |
| `holder_structure` | 持有人结构 |
| `manager_alignment` | 从业人员或基金经理持有 |
| `holdings_snapshot` | 前十大持仓、行业分布 |
| `share_change` | 份额期初/期末/净变动 |

P2 增强字段映射：

| field_name | 对应自然语言字段 |
|---|---|
| `investor_return` | 投资者实际收益率 |
| `nav_data` | 净值序列数据 |

原自然语言清单保留为人工解释口径：

P0 必须字段：

- 基金名称
- 基金代码
- 基金类型
- 业绩比较基准
- 净值增长率
- 基准收益率
- 基金规模
- 管理费
- 托管费
- 基金经理或管理人

P1 关键字段：

- 投资目标
- 投资策略
- 换手率
- 持有人结构
- 从业人员或基金经理持有
- 前十大持仓
- 份额期初/期末/净变动

P2 增强字段：

- 投资者实际收益率
- 行业分布
- 跨期变化

### 5.3 第一版评分

第一版评分只要求：

- Coverage：字段是否提取到。
- Traceability：字段是否有证据锚点。
- Status：按显式阈值计算，coverage 和 traceability 均达到 90% 为 `pass`，均达到 70% 为 `watch`，其余为 `fail`。
- 输出：`score.json`、`score.md`，并包含字段级 `field_group / field_name / priority / records / coverage_rate / traceability_rate / status`。

Correctness 依赖人工 golden answer，P4-S2 后半段再引入。

### 5.4 Golden Set 初始规则

Golden set 必须从 `docs/code_20260519.csv` 中选择。

已确定：

- `004393` 必须纳入，作为国内股票类已知 failure case。

待确认：

- 黄金类 1 只
- 海外股票类 1 只
- 海外债券/稳健类 1 只
- 国内股票类至少 2 只，其中包含 `004393`
- 国内债券类 1 只
- 货币基金类是否纳入 P4-S2 由用户裁决；当前模板对货币基金适配度较低，可先作为 edge case

不得直接使用不在 CSV 中的代码作为“精选基金池 golden set”。

P4-S2 前半段当前实现口径：

- 从 CSV 文件顺序选择最小集合。
- 固定纳入 `004393`。
- 纳入黄金类、海外股票类、海外债券/稳健类、国内债券类各 1 只。
- 国内股票类至少 2 只，其中包含 `004393` 和额外 1 只。
- 暂不纳入货币基金类，作为 edge case 写入 `golden_set.json`。

---

## 6. P4-S3：基金类型误判修复 + 高影响 extractor 缺口修复

### 6.1 目标

用 P4-S2 的评分结果驱动修复，而不是凭单篇报告肉眼修正。

优先修复：

1. `004393` 被误判为 `index_fund`。已在 P4-S3a 修复。
2. 真实年报中 `§3/§4/§8/§9/§10` 关键字段缺失率高的问题。进入 P4-S3b。
3. App 类别与系统分类明显冲突的问题。P4-S3b / P4-S4 继续追踪。

### 6.2 验收

- 新增最小复现测试锁定 `004393` 不应被识别为 `index_fund`。
- 修复后 snapshot/score 能显示分类改善。
- 修复不得通过基金代码特判实现。
- 修复不得把业绩基准中的指数词简单等同于指数基金类型。

### 6.3 P4-S3a accepted：基金类型误判修复

实现与 review artifact：

- implementation: `docs/reviews/p4-s3a-implementation-20260519.md`
- code review:
  - `docs/reviews/p4-s3a-code-review-mimo-20260519.md`
  - `docs/reviews/p4-s3a-code-review-glm-20260519.md`
  - `docs/reviews/p4-s3a-rereview-mimo-20260519.md`
  - `docs/reviews/p4-s3a-rereview-glm-20260519.md`
- controller judgment: `docs/reviews/p4-s3a-code-review-controller-judgment-20260519.md`

P4-S3a 裁决：

- `004393` 误判 root cause 已用代码和已解析年报同源确认：旧规则把 `fund_name + benchmark` 用于指数关键词匹配，且关键词包含 `价值` / `沪深300` 等宽泛词。
- 新规则不再让业绩比较基准单独触发指数基金分类；指数身份必须来自基金名称/类别或投资目标/范围/策略中的显式指数策略证据。
- GLM 发现的 `紧密跟踪` 泛化误伤风险已修复：收窄为 `紧密跟踪标的指数` / `紧密跟踪指数`，并新增主动基金回归测试。
- 真实 snapshot `reports/extraction-snapshots/p4-s3a-004393-rereview/summary.md` 显示 `004393` 为 `active_fund`，且 known failure note 不再出现。

P4-S3a 验证：

- `.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q`：`15 passed`
- `.venv/bin/python -m ruff check fund_agent/fund/fund_type.py tests/fund/extractors/test_profile.py`：passed
- `git diff --check`：passed

### 6.4 P4-S3b accepted：高影响 extractor 缺口修复

实现与 review artifact：

- implementation: `docs/reviews/p4-s3b-implementation-20260519.md`
- code review:
  - `docs/reviews/p4-s3b-code-review-mimo-20260519.md`
  - `docs/reviews/p4-s3b-code-review-glm-20260519.md`
- targeted re-review:
  - `docs/reviews/p4-s3b-rereview-mimo-20260519-1300.md`
  - `docs/reviews/p4-s3b-rereview-glm-20260519.md`
- controller judgment: `docs/reviews/p4-s3b-code-review-controller-judgment-20260519.md`

P4-S3b 裁决：

- 已修复 `004393` 中有直接、语义清晰年报证据的 5 个高影响字段：
  - `nav_benchmark_performance`
  - `manager_strategy_text`
  - `manager_alignment`
  - `holder_structure`
  - `share_change`
- 未修复 `fee_schedule` 是正确边界：真实 `§6` 披露的是当期支付费用金额，不是管理费率/托管费率。
- Review 接受并经 targeted re-review 关闭 2 个中风险泛化问题：
  - 净值表现表头匹配排除“标准差”列，避免列序变化时抽错。
  - 跨页持有人结构 fallback 增加比例值校验，避免把份额列误作比例。
- `share_change` 多份额列选择策略 deferred；后续需要按基金代码/份额级别明确选择 A/C 列。

P4-S3b 验证：

- `.venv/bin/python -m pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py -q`：`24 passed`
- `.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py`：passed
- `git diff --check`：passed
- `reports/extraction-snapshots/p4-s3b-004393-controller-final/summary.md` 显示 5 个本 slice 字段均为 `100.0%` coverage / traceability。
- `reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.md` 显示 `pass=9`、`fail=5`、`p0_status=fail`。

仍缺失字段：

- P0：`fee_schedule`
- P1：`turnover_rate`
- P1：`holdings_snapshot`
- P2：`investor_return`
- P2：`nav_data` traceability

---

## 7. P4-S4：报告质量审计与阻断

### 7.1 目标

在现有 P1/P2/P3/L1/R1/R2 程序审计之外，增加 report quality gate，防止“形式合格、内容不可用”的报告进入产品可用状态。

### 7.2 候选规则

| 规则 | 含义 |
|---|---|
| FQ1 | 基金类型与 App 类别或 golden answer 明显冲突 |
| FQ2 | P0 必须字段缺失过多 |
| FQ3 | 关键字段无证据锚点 |
| FQ4 | 报告中“数据不足”比例超过阈值 |
| FQ5 | `preferred_lens` 与基金类型不匹配 |

FQ6 跨 run snapshot diff 延后到 P4-S4 末尾或 P5，不作为 P4-S1/P4-S2 前置。

---

## 8. 风险追踪

| ID | 风险 | 影响 | 缓解 |
|---|---|---|---|
| P4-R1 | `016492` 重复导致 strict gate 失败 | 中 | P4-S1 允许重复但标红；用户后续核对 App 源数据 |
| P4-R2 | Snapshot schema 过早复杂化 | 中 | P4-S1 只保留最小字段，后续按评分需要扩展 |
| P4-R3 | 直接修 `004393` 跳过质量基线 | 高 | P4-S3 前必须先完成 P4-S1/S2 |
| P4-R4 | Golden set 人工标注成本过高 | 中 | 第一版只标 P0 必须字段 |
| P4-R5 | 网络/PDF 波动污染评分 | 中 | Snapshot/score 离线优先，真实 smoke 单独记录 |
| P4-R6 | dayu-agent 硬依赖影响新环境安装 | 低/中 | P4 cleanup 评估 optional 化，不阻塞 P4-S1 |

---

## 9. Review 与 Gate 规则

P4 遵循 phaseflow / gateflow 多 Agent 约定：

- Plan review：至少派发 AgentMiMo 与 AgentGLM。
- Implementation review：每个 slice 完成后至少 controller review；高风险 slice 使用 MiMo/GLM 双 review。
- Aggregate review：P4-S4 前必须做 P4 aggregate deepreview。
- Controller 负责裁决 findings，并将 accepted / deferred / rejected / needs evidence 写回本文件。

当前待审核：

- `docs/implementation-control-p4.md`

预期 review artifact：

- `docs/reviews/p4-control-plan-review-mimo-20260519.md`
- `docs/reviews/p4-control-plan-review-glm-20260519.md`
- `docs/reviews/p4-control-plan-review-controller-judgment-20260519.md`

---

## 10. 状态更新日志

| 日期 | Gate | 状态 | 备注 |
|---|---|---|---|
| 2026-05-19 | P4 planning | 🟡 in progress | 用户提供 `docs/code_20260519.csv`；人工测试 `004393` 暴露类型误判和字段缺失；已形成 P4 第一性原理计划 |
| 2026-05-19 | P4-S1 plan review | ✅ passed | MiMo/GLM plan review 已完成，controller 裁决 PASS after doc fix；可进入 P4-S1 implementation |
| 2026-05-19 | P4-S1 implementation | 🟡 in progress | 下一步实现 Selected Fund Extraction Snapshot + Quality Gate MVP |
| 2026-05-19 | P4-S1 implementation | 🟡 in progress | 已新增 `fund_agent/fund/extraction_snapshot.py` capability、薄 CLI 入口和 dry-run 单元测试；等待代码审查前验证 |
| 2026-05-19 | P4-S1 code review | 🟡 in progress | Implementation artifact 已写入 `docs/reviews/p4-s1-implementation-20260519.md`；当前验证 `17 passed`、CLI help 与 dry-run smoke passed，等待 MiMo/GLM code review |
| 2026-05-19 | P4-S1 review judgment | ✅ passed | MiMo/GLM code review 均 PASS；controller 裁决 `docs/reviews/p4-s1-code-review-controller-judgment-20260519.md`；accepted commit=`c8a47f6`；P4-S1 accepted，下一 gate 为 P4-S2 |
| 2026-05-19 | P4-S2 implementation | 🟡 in progress | 默认先实现 Coverage / Traceability 评分；Correctness 和人工 golden answer 留到 P4-S2 后半段；货币基金先作为 edge case 不纳入最小 golden set |
| 2026-05-19 | P4-S2 code review | 🟡 in progress | Implementation artifact 已写入 `docs/reviews/p4-s2-implementation-20260519.md`；当前验证 `17 passed`、ruff passed、CLI help passed、diff check passed，等待 MiMo/GLM code review |
| 2026-05-19 | P4-S2 review judgment | ✅ passed | MiMo/GLM code review 均 PASS；controller 裁决 `docs/reviews/p4-s2-code-review-controller-judgment-20260519.md`；accepted commit=`47f2656`；P4-S2 accepted，下一 gate 为 P4-S3 |
| 2026-05-19 | P4-S3a review judgment | ✅ passed | `004393` 类型误判已修复；MiMo/GLM review + targeted re-review 均 PASS；controller 裁决 `docs/reviews/p4-s3a-code-review-controller-judgment-20260519.md`；accepted commit=`0b3fbc6`；真实 snapshot 显示 `active_fund`；下一 gate 为 P4-S3b |
| 2026-05-19 | P4-S3b review judgment | ✅ passed | `004393` 的 5 个高影响 extractor 缺口已修复；MiMo/GLM code review 与 targeted re-review 均 PASS，controller 接受并修复 2 个中风险泛化问题；裁决 `docs/reviews/p4-s3b-code-review-controller-judgment-20260519.md`；当前验证 `24 passed`、ruff passed、diff check passed；真实 snapshot/score 显示本 slice 5 字段 coverage / traceability 均为 `100.0%`；下一 gate 为 P4-S4 |
