# P4 Control Plan Review Controller Judgment

> 日期：2026-05-19
> 审查对象：`docs/implementation-control-p4.md`
> 外部 review：`docs/reviews/p4-control-plan-review-mimo-20260519.md`、`docs/reviews/p4-control-plan-review-glm-20260519.md`
> 裁决：PASS after doc fix；可进入 `P4-S1 implementation`。

## 1. Verdict

MiMo 和 GLM 均认可 P4 控制文档的方向：先建立质量闭环，再扩功能；P4-S1 到 P4-S4 的顺序也成立。

两边都指出 P4-S1 前需要补充文档约束：

- MiMo：snapshot schema 缺少 `field_group -> field_name` 映射，`field_name` 命名来源不清。
- GLM：snapshot 生成与现有 `FundDataExtractor` / `StructuredFundDataBundle` 的衔接未定义；AGENTS 模块边界未显式写入 P4-S1 实现约束。

Controller 已接受这些 findings，并直接修订 `docs/implementation-control-p4.md`。

## 2. Accepted Findings

### A1. 补齐 field_group / field_name 映射

裁决：采纳并已修复。

修复内容：

- 明确 `field_name` 使用代码同源的 snake_case 标识符。
- 新增第一版字段映射，包括 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule`、`classified_fund_type`、`nav_benchmark_performance`、`investor_return`、`manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure`、`holdings_snapshot`、`share_change`、`nav_data`。

### A2. 明确 snapshot 与现有 façade 的衔接

裁决：采纳并已修复。

修复内容：

- P4-S1 默认复用 `FundDataExtractor.extract(...)` 与 `StructuredFundDataBundle`。
- 若字段级粒度不足，只能在 Capability 层补 snapshot adapter，不得绕过统一文档仓库接口。
- P4-S1 不以重写 extractor 为目标，发现 façade 丢失粒度时记录到后续 slice。

### A3. 明确模块边界和参数约束

裁决：采纳并已修复。

修复内容：

- 年报访问必须通过 `FundDocumentRepository` 或 `FundDataExtractor`。
- snapshot 核心能力默认放在 Capability 层。
- CLI / scripts 只能做薄入口。
- `fund_code`、`report_year`、`source_csv`、`run_id`、输出目录等必须显式传递。
- 禁止把显式参数塞入 `extra_payload`。
- 禁止为了 known failure 美化结果而覆盖 extractor 真实输出。

## 3. Deferred Findings

### D1. `004393` root cause 进一步细化

GLM 指出 `004393` 误判可能不仅来自 benchmark 指数词，还包括 `_INDEX_NAME_KEYWORDS` 中“价值”等宽泛关键词、`fund_category` 提取失败等因素。

裁决：延后到 P4-S3。

理由：P4-S1 不修分类器；P4-S3 修复前必须写最小复现测试和代码级 root cause。

### D2. 抽样策略进一步精确化

裁决：延后到 P4-S1 implementation。

理由：P4 控制文档已规定 016492 重复标红、004393 固定进入 known failure。具体按类别抽样名单可在实现时由 CLI 参数或默认策略产生。

### D3. errors.jsonl schema

裁决：延后到 P4-S1 implementation。

理由：当前控制文档只要求输出错误文件；具体字段可随实现确定，但不得缺少 fund_code、error_type、error_message。

## 4. Final Recommendation

`docs/implementation-control-p4.md` 当前已经满足进入 P4-S1 implementation 的计划条件。

下一步：

1. 将当前文档状态视为 P4-S1 accepted plan。
2. 若需要严格 gateflow，可先提交 plan artifact，再进入 implementation。
3. P4-S1 implementation 应只做 extraction snapshot + quality gate MVP，不修 `004393` 分类器。

剩余风险：

- `016492` 重复仍需用户核对 App 源数据。
- `004393` root cause 需在 P4-S3 做代码级确认。
- dayu-agent 依赖清理仍是 cleanup item，不阻塞 P4-S1。
