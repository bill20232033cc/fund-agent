# P4-S2 Code Review Controller Judgment

> 日期：2026-05-19
> Gate：`P4-S2 review judgment`
> 审查对象：字段级 coverage / traceability scoring + minimal golden set selection
> Review artifacts：
> - `docs/reviews/p4-s2-code-review-mimo-20260519.md`
> - `docs/reviews/p4-s2-code-review-glm-20260519.md`
> 裁决：PASS；无 blocking finding；可进入 P4-S2 accepted / P4-S3。

## 总体裁决

MiMo 和 GLM 均给出 PASS，且均确认 P4-S2 前半段实现符合控制文档范围：

- 只消费 P4-S1 `snapshot.jsonl` 和精选基金池 CSV，不读取 PDF、cache、文档仓库或网络。
- 只实现 coverage / traceability 评分，不实现 correctness。
- `score.json` / `score.md` 明确标记 `correctness=not_implemented`。
- 字段优先级映射为代码内显式常量，覆盖当前 14 个 P4-S1 `field_name`。
- 评分阈值为显式常量和 `ScoreThresholds`，不是隐藏魔法数字。
- Golden set 只从 `docs/code_20260519.csv` 中选取，固定包含 `004393`，覆盖必需类别，排除货币基金类。
- UI 通过 Service 调用 Capability，没有直接依赖 Capability。
- 测试不触发真实网络或 PDF。

因此 P4-S2 implementation 可接受。

## Finding 裁决

| 来源 | Finding | Severity | Controller 裁决 | 处理 |
|---|---|---:|---|---|
| MiMo | CLI 测试只断言 `score_json:`，未断言 `score_md:` / `golden_set:` | INFO | accepted as test cleanup | 不阻塞；后续测试整理可补 |
| MiMo | Golden set 错误路径缺少显式测试 | INFO | accepted as test gap | 不阻塞；P4-S2 后半段人工 golden answer 时补负向样本更合适 |
| GLM | Golden set 测试依赖真实 CSV，CSV 变更会导致测试失败 | INFO | accepted by design | 这是 intentional coupling，用于保证 golden set 只来自真实精选基金池 |
| GLM | CLI 未暴露自定义 threshold 参数 | INFO | deferred | 当前默认阈值满足 MVP；若 P4-S4 quality gate 需要调参再开放 |
| GLM | 若输入 snapshot 完全缺少某个字段，score 不主动补 0 行 | INFO | accepted risk | P4-S2 依赖 P4-S1 snapshot schema；P4-S4 quality gate 可增加 schema completeness check |

## Controller 自验

- `.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q`
  - `17 passed in 0.47s`
- `.venv/bin/python -m ruff check fund_agent/fund/extraction_score.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py tests/fund/test_extraction_score.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py`
  - `All checks passed!`
- `.venv/bin/fund-analysis extraction-score --help`
  - passed
- `git diff --check`
  - passed

## 残余风险

- Correctness 评分仍未实现，按计划留给 P4-S2 后半段人工 golden answer。
- `nav_data` 没有年报锚点，traceability 会自然偏低；这是当前质量基线事实。
- Golden set 当前按 CSV 顺序 deterministic 选择，不代表业务最优样本；人工 golden answer 阶段可调整。
- Score 对输入 snapshot schema completeness 的防御有限；若后续需要阻断低质量报告，应在 P4-S4 增加 schema completeness gate。

## 下一步

P4-S2 可进入 accepted 状态。下一 gate 为 `P4-S3 implementation`：修复 `004393` 类型误判和高影响 extractor 缺口，且必须由 P4-S2 score 证明修复前后变化。
