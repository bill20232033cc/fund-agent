# P4-S3a Code Review Controller Judgment

> 日期：2026-05-19
> Gate：`P4-S3a review judgment`
> 审查对象：`004393` 基金类型误判修复
> 裁决：PASS；P4-S3a 可接受，下一步进入 P4-S3b 高影响 extractor 缺口修复。

## 总体裁决

P4-S3a 的目标是先关闭 `004393` 被误判为 `index_fund` 的高优先级分类问题，不在同一 slice 中扩展 `§3/§4/§8/§9/§10` extractor。

本次实现满足验收条件：

- 新增最小复现测试，锁定 `004393` 风格混合基金不因业绩比较基准中的指数词误判为 `index_fund`。
- 分类器不使用基金代码特判。
- 业绩比较基准不再单独触发指数基金分类。
- 真实 `004393` snapshot 已显示 `classified_fund_type=active_fund`，且 known failure note 不再出现。
- true index / enhanced index / bond / QDII 既有分类测试仍通过。

## Root Cause 裁决

controller 复核确认 root cause 为三因素叠加：

1. `004393` 当前解析结果中 `fund_category` 为空。
2. 旧分类器把 `fund_name + benchmark` 拼接后用于指数关键词匹配。
3. 旧 `_INDEX_NAME_KEYWORDS` 同时包含宽泛风格词 `价值` 和基准指数词 `沪深300` / `中证` 等，导致“安信企业价值优选混合 + 沪深300基准”进入 `index_fund` 分支。

修复后指数身份判断只使用名称/类别中的指数身份词，或投资目标/范围/策略中的显式指数策略证据；业绩比较基准仅作为依据说明。

## Review Findings 裁决

| 来源 | Finding | Severity | Controller 裁决 | 处理 |
|---|---|---:|---|---|
| MiMo | 未发现实质性问题；建议说明 `classification_text` 中 benchmark 不用于指数判断 | INFO | accepted as readability follow-up | 当前不阻塞；若后续继续维护分类器，可补命名/注释 |
| GLM | `紧密跟踪` 策略关键词可能误伤“紧密跟踪市场动态”的主动基金 | Medium | accepted and fixed | 已收窄为 `紧密跟踪标的指数` / `紧密跟踪指数`，并新增回归测试 |

Targeted re-review：

- MiMo：PASS，确认 F1 closed，145 tests passed。
- GLM：PASS，确认 F1 closed，无新 finding。

## Controller 自验

已运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
# 15 passed

.venv/bin/python -m ruff check fund_agent/fund/fund_type.py tests/fund/extractors/test_profile.py
# All checks passed

git diff --check
# passed
```

真实缓存复核：

```text
FundTypeClassification(classified_fund_type='active_fund', classification_basis=('基金类别：未披露', '未命中指数/QDII/FOF/债券规则，按主动权益基金处理'))
```

真实 snapshot 复核：

```text
reports/extraction-snapshots/p4-s3a-004393-rereview/summary.md
| 004393 | 安信企业价值优选混合A | 国内股票类 | succeeded | active_fund |  |
```

## 残余风险

- P4-S3a 只修复分类误判，不修复 `004393` 在 `fee_schedule`、`nav_benchmark_performance`、`manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure`、`holdings_snapshot`、`share_change` 等字段上的缺失。
- `004393` 的 P0 status 仍为 `fail`。这是 P4-S3b 的直接输入，不应在本 slice 中掩盖。
- 当前分类器仍是 `§1/§2` 启发式规则；若基金名称/类别缺失且策略文本低质量，仍可能回退为 `active_fund`。后续可通过 correctness golden answer 继续收窄。

## 下一步

P4-S3a accepted。下一 gate 为 `P4-S3b implementation`：基于 P4-S2/P4-S3a snapshot/score，优先修复高影响 extractor 缺口，尤其是 `004393` 的 `fee_schedule`、`§3` 表现、`§4` 管理人文本、`§8` 换手/持仓、`§9` 持有人/持有披露和 `§10` 份额变动。
