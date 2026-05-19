# P4-S4 Control-Doc Reconciliation

## 结论

裁决：P4-S4 的当前实现事实已满足 `docs/implementation-control-p4.md` 第 7.3 和第 7.4 的骨架验收目标。下一 gate 应从 `P4-S4 implementation` 更新为 `P4 aggregate deepreview`。

本裁决只做 control-doc reconciliation，不接受当前工作树中未完成的 `style_positioning` 字段契约改动作为 P4-S4 证据。

## 证据

- `fund_agent/fund/golden_prefill.py` 已实现 correctness golden answer 预填底稿，只通过 `FundDataExtractor.extract(...)` 获取结构化数据，不直接读取 PDF/cache。
- `fund_agent/fund/golden_answer.py` 已实现人工审核 Markdown 到 strict JSON 的构建与校验，校验 `expected_value`、`confidence`、`source` 和 skipped fields。
- `fund_agent/fund/quality_gate.py` 已实现只消费 `score.json` 的质量 gate：P0 fail 触发 block，P1 fail 触发 warn，correctness 未接入记录 `FQ0/info`。
- `fund_agent/ui/cli.py` 已暴露 `golden-prefill`、`golden-build`、`quality-gate` 三个薄 CLI 入口。
- `fund_agent/services/golden_prefill_service.py`、`fund_agent/services/golden_answer_service.py`、`fund_agent/services/quality_gate_service.py` 已把 UI 参数收敛为显式请求对象，不使用 `extra_payload`。
- `README.md`、`fund_agent/fund/README.md`、`tests/README.md` 已描述当前 P4-S4 用户入口、Capability 边界和测试定位。
- `docs/implementation-control-p4.md` 状态日志已记录 `P4-S4 pre-label handoff` 和 `P4-S4 quality gate skeleton` 均 passed。

## 验收项对照

| 验收项 | 裁决 |
|---|---|
| `fund-analysis golden-prefill` 生成 silver label 底稿 | accepted |
| `fund-analysis golden-build` 构建 strict JSON 并校验人工审核字段 | accepted |
| correctness 自动比对不提前接入 | accepted |
| quality gate 只消费 `score.json` | accepted |
| P0 fail 阻断，P1 fail 警告 | accepted |
| correctness 未接入时仅记录 info | accepted |
| 不读取 PDF/cache，不调用 LLM，不改变报告生成主链路 | accepted |

## 残余风险

- correctness 自动比对仍等待用户完成人工审核后的 `golden-answer.json`，owner：后续 correctness slice。
- `docs/implementation-control-p4.md` 第 9 节写着 “P4-S4 前必须做 P4 aggregate deepreview”，但状态日志显示 P4-S4 骨架已先行落地。裁决为接受现状，并把下一 gate 设为 `P4 aggregate deepreview`，用于补齐 phase-level 独立审查。
- 当前 worktree 存在未完成的 `style_positioning` 字段契约改动，owner：后续独立字段契约 slice；该改动不属于本次 P4-S4 reconciliation。

## 下一步

进入 `P4 aggregate deepreview`。按 phaseflow 规则，aggregate deepreview 需要从 `AgentMiMo`、`AgentDS`、`AgentGLM` 中至少任选两者形成独立 review；controller 负责整合、裁决 findings，并把 residual risks 写回总控文档。
