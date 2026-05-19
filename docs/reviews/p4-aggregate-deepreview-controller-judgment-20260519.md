# P4 Aggregate Deepreview Controller Judgment

## 裁决

结论：FAIL，需要进入 `P4 aggregate fix`，不能进入 `ready-to-open-draft-PR`。

三份 review 结论如下：

| Reviewer | Artifact | 结论 |
|---|---|---|
| AgentMiMo | `docs/reviews/p4-aggregate-deepreview-mimo-20260519-2108.md` | PASS with conditions |
| AgentCodex | `docs/reviews/p4-aggregate-deepreview-codex-20260519.md` | FAIL for aggregate quality-loop readiness |
| AgentDS | `docs/reviews/p4-aggregate-deepreview-ds-20260519.md` | FAIL for quality-loop effectiveness |

Controller 裁决采用 Codex/DS 的核心 finding：当前 P4-S4 skeleton 满足“只消费 score.json、P0 fail block、P1 fail warn”的局部验收，但不满足 P4 北极星“防止形式合格、内容不可用的报告误导用户”的 aggregate 标准。

## Findings 裁决

### F1. score / quality gate 缺少 per-fund 粒度

裁决：accepted，blocking。

当前 `extraction_score.py` 只按 `(field_group, field_name)` 聚合所有基金记录，`quality_gate.py` 只消费聚合后的 `field_scores`。这可以衡量字段级总体抽取质量，但不能判断某一只基金的报告是否可用。多基金 run 中，单只基金 P0 缺失可能被其它基金的覆盖率掩盖。

要求修复：

- `score.json` 增加 per-fund quality summary。
- `quality_gate` 必须能基于 per-fund P0/P1 状态生成 issue。
- P0 per-fund fail 应触发 block，并在 issue 中保留 `fund_code`。
- 新增测试覆盖“多基金聚合 pass，但单只基金 P0 fail 仍 block”的场景。

### F2. quality gate 未接入 `analyze` 主链路

裁决：accepted as design gap，not immediate code blocker for this fix slice。

理由：`docs/implementation-control-p4.md` 第 7.3 明确要求当前 skeleton “不改变报告生成主链路”。因此不能把“未接入 analyze”判为当前 skeleton 实现 bug。但从 P4 北极星看，它是明确 residual risk，必须写回控制文档并指定 owner。

当前 fix slice 不直接接入 `analyze`，但必须：

- 在控制文档中明确主链路集成是后续 `quality gate integration slice` 的 owner。
- 在 `quality_gate` 输出中保留足够 fund-level 信息，保证后续接入 `analyze` 不需要重做 score schema。

### F3. FQ1/FQ4/FQ5 未实现

裁决：accepted as deferred。

当前 P4-S4 skeleton 只承诺 FQ0/FQ2/FQ3。FQ1/FQ4/FQ5 作为后续 quality gate rules slice 追踪，不阻塞本次 fix。

### F4. correctness 自动比对未实现

裁决：accepted as deferred。

`golden-prefill` 和 `golden-build` 已完成标注前链路；correctness 自动比对依赖用户完成人工审核后的 `golden-answer.json`，进入后续 correctness slice。

### F5. 004393 known_failure note 死代码

裁决：accepted as cleanup。

P4-S3a 已修复 `004393` 类型误判，旧 known_failure note 可后续改为通用 App 类别与系统类型冲突检测。不阻塞本次 fix。

### F6. quality_gate / golden_answer 测试覆盖不足

裁决：accepted as test hardening。

per-fund gate 的新增测试必须随 F1 修复落地。其余 golden answer 边界测试可进入后续 test hardening。

### F7. `_normalize_extraction_mode` 未知模式静默降级

裁决：accepted as low-risk cleanup。

当前 extractor 模式集合稳定，不阻塞。后续可记录 unknown mode 到 note。

### F8. `golden_prefill` confidence 长度启发式

裁决：accepted as low-risk cleanup。

该输出是 silver label，不影响 correctness 评分。后续可配置化或移除长度阈值。

## 当前 Gate

- 当前 gate：`P4 aggregate fix`
- Fix scope：per-fund score / quality gate blocking
- 不进入 draft PR readiness

## Residual Risks / Owners

| ID | 风险 | 状态 | Owner |
|---|---|---|---|
| P4-AGG-R1 | score/gate 缺少 per-fund 状态 | blocking fix | P4 aggregate fix |
| P4-AGG-R2 | quality gate 未接入 `analyze` 主链路 | deferred design gap | quality gate integration slice |
| P4-AGG-R3 | FQ1/FQ4/FQ5 未实现 | deferred | quality gate rules slice |
| P4-AGG-R4 | correctness 自动比对未实现 | deferred | correctness slice after reviewed golden JSON |
| P4-AGG-R5 | 004393 known_failure note 死代码 | cleanup | extractor refinement |
| P4-AGG-R6 | quality_gate / golden_answer 边界测试不足 | partial fix / deferred | P4 aggregate fix + test hardening |
| P4-AGG-R7 | `_normalize_extraction_mode` 未知模式静默降级 | cleanup | extraction snapshot cleanup |
| P4-AGG-R8 | `golden_prefill` confidence 长度启发式缺乏依据 | cleanup | golden prefill cleanup |

## 下一步

进入 `P4 aggregate fix`，实现 per-fund score / quality gate。修复完成后至少运行：

```bash
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py -q
```

随后派发 re-review，重点验证 F1 是否关闭，以及 control docs 是否正确追踪 F2-F8。
