# Code Review

## Scope

- Mode: current changes
- Branch: main
- Base: main (workspace unstaged changes)
- Output file: `docs/reviews/p4-s3a-code-review-glm-20260519.md`
- Included scope:
  - `fund_agent/fund/fund_type.py` (classifier logic, keyword constants, new `_has_index_identity_evidence`, profile field extraction)
  - `tests/fund/extractors/test_profile.py` (new 004393 repro test)
  - `fund_agent/fund/README.md` (documentation update)
  - `docs/reviews/p4-s3a-implementation-20260519.md` (implementation artifact)
- Excluded scope: `§3/§4/§8/§9/§10` extractors, snapshot/score CLI, integration tests
- Parallel review coverage: 无

## Verdict: PASS

改动正确修复了 004393 误判，无基金代码特判，保留所有已有正确分类，文档准确。存在一项中等严重程度发现：`_INDEX_STRATEGY_KEYWORDS` 中 `紧密跟踪` 可在非指数基金策略文本中产生误判，已用对抗模拟复现。该发现不影响 004393 修复本身，建议后续迭代收窄。

## Findings

### F1-未修复-中-紧密跟踪策略关键词可在主动基金中触发指数基金误判

- **入口/函数**: `classify_fund_type` → `_has_index_identity_evidence` → `_contains_any(strategy_text, _INDEX_STRATEGY_KEYWORDS)`
- **文件(行号)**: `fund_agent/fund/fund_type.py:254`
- **输入场景**: 主动管理基金投资目标为 `紧密跟踪市场动态，灵活调整投资组合`，基金名称无指数身份关键词，基金类别为空或 `混合型`
- **实际分支**: `_contains_any(strategy_text, _INDEX_STRATEGY_KEYWORDS)` 命中 `紧密跟踪` → `_has_index_identity_evidence` 返回 `True` → 进入 `index_fund` 分支
- **预期行为**: 该基金无指数身份关键词（名称/类别不含 `指数/ETF/交易型开放式/联接`），策略文本仅为一般性"紧密跟踪市场"，应被分类为 `active_fund`
- **实际行为**: 返回 `index_fund`，导致后续 `preferred_lens` 和分析路径错误
- **直接证据**: 对抗模拟输入 `investment_objective="紧密跟踪市场动态，灵活调整投资组合"` + `fund_name="XX灵活配置混合型证券投资基金"` + `fund_category=""` → 输出 `index_fund`。根因：`_INDEX_STRATEGY_KEYWORDS` 包含 `紧密跟踪`，该词在 `fund_type.py:31` 定义，在 `fund_type.py:254` 被子串匹配触发
- **影响**: 误分类导致 `preferred_lens` 错误，下游分析使用指数基金模板而非主动权益模板。实际发生概率较低——中国基金年报投资目标中"紧密跟踪"几乎专用于指数基金描述，但主动基金使用"紧密跟踪市场变化/行业动态"并非不可能
- **建议改法和验证点**: 将 `紧密跟踪` 收窄为 `紧密跟踪标的` 或 `紧密跟踪指数`，使匹配更精准；或在 `_has_index_identity_evidence` 中要求策略关键词命中时至少同时命中一个指数指向词（如 `指数/标的/基准`）。验证：在测试中添加 investment_objective 含"紧密跟踪"但无指数语义的主动基金用例
- **修复风险（低）**: 收窄关键词可能遗漏极少数使用"紧密跟踪该指数"而非"跟踪指数"措辞的真实指数基金，但 `跟踪指数` 已覆盖绝大多数场景
- **严重程度（中）**: 可用合理输入复现的错误分类路径，但真实年报中发生概率低

## Open Questions

- 无

## Residual Risk

- `紧密跟踪` 误判风险：F1 已描述，建议 P4-S3b 或后续迭代收窄
- `_INDEX_STRATEGY_KEYWORDS` 其余五个词（`标的指数`、`跟踪指数`、`复制法`、`完全复制`、`抽样复制`）均为强指数特异词，当前未发现误判风险
- 无 FOF 基金显式测试用例（既有问题，非本次引入）
- 当前测试 004393 未包含 `investment_strategy` 字段；真实 004393 解析报告含 `资产配置、股票基本面分析、估值分析、港股通、债券等主动管理策略`，该文本不含策略关键词，不会改变分类结果，但测试覆盖更完整会更好
