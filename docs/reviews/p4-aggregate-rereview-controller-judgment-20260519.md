# P4 Aggregate Re-Review Controller Judgment - 2026-05-19

结论：PASS。P4 aggregate deepreview 的 blocking finding 已关闭，P4 aggregate fix 可接受。

## 输入

- MiMo re-review：`docs/reviews/p4-aggregate-rereview-mimo-20260519.md`
- GLM re-review：`docs/reviews/p4-aggregate-rereview-glm-20260519.md`
- 原 blocking 裁决：`docs/reviews/p4-aggregate-deepreview-controller-judgment-20260519.md`
- 三方 reconciliation：`docs/reviews/p4-design-control-code-reconciliation-20260519.md`
- 字段契约收口：`docs/reviews/style-positioning-field-reconciliation-20260519.md`

## 裁决

### F1：score / quality gate 缺少 per-fund 阻断粒度

裁决：accepted fixed，关闭 P4 blocking。

理由：

- `ExtractionScoreResult` 与 `score.json` 已输出 `fund_scores`。
- `fund_scores` 包含 `fund_code / fund_name / app_category / records / p0_status / p1_status / status / p0_failed_fields / p1_failed_fields`。
- `quality_gate` 对单基金 P0 fail 生成带 `fund_code` 的 `FQ2F/block`。
- 测试已覆盖“字段聚合 pass，但单基金 P0 fail 仍 block”的核心失败场景。
- MiMo 与 GLM 均独立裁决 PASS。

### style_positioning 字段契约迁移

裁决：accepted，作为独立字段契约收口，不纳入 P4-R7 的通过证据。

理由：

- `style_positioning` 已从 `manager_strategy_text` 迁移到 `product_profile`。
- `check_consistency` 优先从 `product_profile` 判断投资风格，必要时回退到 `manager_strategy_text.strategy_summary`。
- `docs/golden-answer-template.md` 已同步到 `product_profile | style_positioning`。
- 相关 extractor、renderer、service 和 tests 已通过 MiMo/GLM sanity review。

### O1：单基金 P1 fail fund-level warn 缺少独立测试

裁决：accepted as low test hardening，非当前 gate blocker。

理由：

- 当前实现分支存在，GLM 走读确认 `_evaluate_fund_score()` 对 P1 fail 生成 `FQ2F/warn`。
- 现有字段级 P1 fail warn 已有测试，单基金 P0 block 核心阻断场景已有测试。
- 后续可在 test hardening slice 补充 `fund_scores` P1 warn 专项用例。

### 完全缺失基金不进入 fund_scores

裁决：accepted as snapshot-layer residual risk，非当前 gate blocker。

理由：

- 若 snapshot 生成阶段某只基金完全失败，该基金不会出现在 `snapshot.jsonl`，因此也不会出现在 `fund_scores`。
- 该问题属于 snapshot run failure accounting，不属于当前 `score.json` 内 per-fund gate fix。
- 后续如需要阻断 snapshot 失败基金，应在 snapshot / score run summary contract 中扩展失败基金输入。

## 剩余风险

| 风险 | 裁决 | Owner |
|---|---|---|
| P4-R7 / RR-14 per-fund 阻断粒度 | closed | N/A |
| P4-R8 / RR-15 quality gate 未接入 `analyze` 主链路 | deferred | `quality gate integration slice` |
| P4-R9 FQ1/FQ4/FQ5 未实现 | deferred | `quality gate rules slice` |
| P4-R10 correctness 自动比对未实现 | deferred | 用户完成 golden answer JSON 后的 `correctness slice` |
| 单基金 P1 warn 独立测试 | deferred low | test hardening |
| snapshot 完全失败基金不进入 `fund_scores` | deferred | snapshot failure accounting |

## 验证

Controller 本地验证：

- `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py tests/fund/extractors/test_profile.py tests/fund/extractors/test_manager_ownership.py tests/fund/analysis/test_consistency_check.py tests/fund/template/test_renderer.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py -q`：`63 passed`
- `.venv/bin/ruff check ...`：passed
- `git diff --check`：passed

Reviewer 验证：

- MiMo：full suite `166 passed`，ruff clean，diff check clean。
- GLM：P4 aggregate fix 主测试 `13 passed`，style-positioning 相关测试 `37 passed`，ruff clean，diff check clean。

## Gate

当前 gate：`P4 aggregate re-review accepted`

下一步：

1. 用户已授权继续处理 `reports/golden-answers/golden-answer-prefill-reviewed.md` 后续表格，可作为 correctness golden answer 人工底稿补全任务派发给 AgentCodex。
2. 完成后再决定是否进入 correctness JSON build / correctness slice，或先进入 draft PR readiness。
