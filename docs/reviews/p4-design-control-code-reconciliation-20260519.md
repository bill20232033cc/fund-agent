# P4 Design / Control / Code Reconciliation - 2026-05-19

结论：`docs/design.md`、`docs/implementation-control-p4.md` 与当前代码事实在 P4 aggregate fix 后达到“当前 gate 可 re-review”的一致状态。P4 质量闭环已具备字段级与单基金级 coverage / traceability 阻断能力；`analyze` 主链路接入、FQ1/FQ4/FQ5 与 correctness 自动比对仍是明确 deferred risks，不能视为已完成。

## 审查对象

- 设计真源：`docs/design.md`
- P4 控制真源：`docs/implementation-control-p4.md`
- 当前代码事实：
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_quality_gate.py`
  - `README.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## 已对齐项

| 项 | design.md | implementation-control-p4.md | 当前代码事实 | 裁决 |
|---|---|---|---|---|
| 模块边界 | Capability 负责基金领域知识、分析引擎、审计规则 | P4 snapshot/score/gate 默认放在 `fund_agent/fund/`，CLI/Service 只做薄入口 | `extraction_score.py` 与 `quality_gate.py` 位于 Capability；Service 测试只验证显式参数转发 | aligned |
| 证据可审计 | 每条断言关联年报章节，计算可追溯 | P4 用 coverage / traceability 衡量字段值与证据锚点 | score 同时输出字段级 `coverage_rate` / `traceability_rate` 与单基金 `fund_scores` | aligned |
| 质量阻断 | MVP 程序审计先行，v2 再引入 LLM/证据复核 | P4-S4 skeleton 只消费 `score.json`，不读 PDF/cache，不调用 LLM | `run_quality_gate()` 只读 score JSON；correctness 未接入仅 FQ0/info | aligned |
| 单基金可用性 | design.md 未细化 P4 per-fund gate，但北极星要求避免内容不可用报告误导用户 | P4-R7 要求 per-fund summary 与 P0 fail 阻断 | `score.json` 新增 `fund_scores`；`quality_gate` 对单基金 P0 fail 生成带 `fund_code` 的 block | aligned after fix |
| 用户文档 | design.md 以代码事实为准 | 控制文档要求状态回写 | README / fund README / tests README 已同步当前 score/gate 契约 | aligned |

## Fix 代码事实

P4 aggregate fix 接受的 blocking finding 是：字段聚合分数可能 pass，但单只基金仍存在 P0 失败，导致质量 gate 无法阻断“内容不可用”的单基金报告。

当前实现：

- `ExtractionScoreResult` 新增 `fund_scores`。
- `score_fund_records()` 按 `fund_code` 聚合 snapshot 记录，输出每只基金的 `p0_status`、`p1_status`、`status`、`p0_failed_fields`、`p1_failed_fields`。
- `score.json` 与 `score.md` 同时输出 `field_scores` 与 `fund_scores`。
- `QualityGateIssue` 新增 `fund_code`。
- `run_quality_gate()` 保持旧 `field_scores` 兼容，同时消费可选 `fund_scores`。
- 单基金 `p0_status=fail` 触发 `FQ2F/block`，issue 保留 `fund_code`。
- 单基金 `p1_status=fail` 触发 `FQ2F/warn`。

新增测试覆盖：

- `tests/fund/test_extraction_score.py::test_score_fund_records_exposes_single_fund_p0_failure_when_aggregate_can_pass`
- `tests/fund/test_quality_gate.py::test_run_quality_gate_blocks_single_fund_p0_failure_even_when_field_aggregate_passes`

## 剩余风险裁决

| 风险 | 裁决 | Owner / 下一步 |
|---|---|---|
| P4-R7 / RR-14：缺少 per-fund 阻断粒度 | fixed, pending re-review | P4 aggregate re-review 验证后可关闭 |
| P4-R8 / RR-15：quality gate 未接入 `analyze` 主链路 | deferred, tracked | 后续 `quality gate integration slice`；当前 P4-S4 skeleton 明确不改变报告主链路 |
| P4-R9：FQ1/FQ4/FQ5 未实现 | deferred, tracked | 后续 `quality gate rules slice` |
| P4-R10：correctness 自动比对未实现 | deferred, tracked | 用户完成人工审核 golden JSON 后进入 `correctness slice` |
| `docs/design.md` 仍描述 Host/Engine 复用 Dayu 的目标架构 | accepted with caveat | design.md 已写明 MVP 实现以当前代码与实施总控为准；不作为 P4 blocker |

## 验证

- `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py -q`：`12 passed`
- `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py -q`：`20 passed`
- `.venv/bin/ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py`：passed
- `git diff --check`（本轮修改文件）：passed

## Gate 裁决

当前 gate：`P4 aggregate fix implemented`

下一 gate：`P4 aggregate re-review`

re-review 重点：

1. `fund_scores` 是否足以代表单基金报告可用性，是否需要额外输出每个 P0 字段的 per-fund coverage / traceability 明细。
2. `quality_gate` 的 `FQ2F` 是否应保留为独立规则码，或归并到 FQ2 并用 `fund_code` 区分粒度。
3. `analyze` 主链路接入是否仍可延后，还是应在 ready-to-open-draft-PR 前形成明确后续 slice artifact。
