# Controller Judgment — Repository-Level Deepreview

## Scope

- **Input artifacts**:
  - `docs/reviews/agentds-repo-deepreview-20260523.md`
  - `docs/reviews/agentglm-repo-deepreview-20260523.md`
- **Judgment date**: 2026-05-23
- **Controller action**: 合并两份仓库级 deepreview，去重、校正优先级，并给出下一步修复切片。
- **No code changes**: 本文档只记录判断，不修改生产代码、测试或配置。

## Executive Judgment

- AgentDS 的 25 个 findings 覆盖面更完整，且严重/高风险项经 controller 抽样核实后基本成立。
- AgentGLM 的 2 个 findings 中：
  - `F-02 _load_index_batch 串行 await` 与 AgentDS `F-20 温度计批量查询串行执行` 是同一问题，合并为一个低/中优先级性能修复。
  - `F-01 ThermometerService 直接实例化 Capability data 内部实现` 是独立的模块边界问题，AgentDS 未单独列出，应纳入修复 backlog。
- 两份 review 均报告测试通过，且均未声明 blocker。Controller 判断：当前不需要冻结发布，但应优先修复审计完整性、类型防御、层边界和 CI 门禁。

## Accepted Findings

### P0 — 下一轮应优先修复

1. **C2 must_not_cover 缺少反向完整性校验**
   - Source: AgentDS F-1
   - Status: accepted
   - Rationale: `contract_rules.py` 对 `required_output_items` 有双向覆盖校验，但 `must_not_cover` 只验证规则是否存在于 manifest，不验证 manifest 条目是否全部有覆盖路由。该问题直接影响 CHAPTER_CONTRACT fail-closed 能力。

2. **Ch0 required_output_items 共享 marker**
   - Source: AgentDS F-2
   - Status: accepted
   - Rationale: "一句话这是什么基金" 与 "基金简介" 共享 `基金：` marker，renderer 也只输出一条 bullet，C2 无法独立区分两项。

3. **bool 被当作数值输入**
   - Source: AgentDS F-3, F-4
   - Status: accepted
   - Rationale: Python `bool` 是 `int` 子类，`parse_ratio`、analysis 层 `_parse_decimal`、quality gate 数值读取均缺少统一 bool guard。应作为同源类型防御问题一次修复。

4. **UI 层直接 import Capability 类型**
   - Source: AgentDS F-5
   - Status: accepted
   - Rationale: `fund_agent/ui/cli.py` 直接从 `fund_agent.fund.data.thermometer_types` import 类型并做 `isinstance` 分发，违反 AGENTS.md UI 只依赖 Application/Service 接口的边界。

5. **CI 未强制覆盖率门禁**
   - Source: AgentDS F-6
   - Status: accepted
   - Rationale: `.github/workflows/ci.yml` 只运行 `uv run pytest -q`，与 AGENTS.md 和 `tests/README.md` 的覆盖率目标不一致。

### P1 — 应在 P0 后修复或专项确认

6. **Ch0 最大风险和升级/降级字段结构性不可满足**
   - Source: AgentDS F-15, F-16
   - Status: accepted
   - Rationale: renderer 当前硬编码输出数据不足，未消费已有 risk/checklist 结果。该问题影响模板第 0 章 must_answer 完整性，但需要先确认输入结构。

7. **年报来源错误分类与 fallback 追溯不足**
   - Source: AgentDS F-9, F-10, F-18
   - Status: accepted
   - Rationale: 这些问题同属 AnnualReportSource failure classification / provenance。应合并为一次 documents source 语义修复，重点保持 fail-closed。

8. **Quality gate watch 区间静默与 FQ3 阈值语义**
   - Source: AgentDS F-12, F-13
   - Status: accepted with product confirmation
   - Rationale: 静态代码证据成立，但阈值是否调整为 0.7 需要业务确认。watch 状态至少应有 WARN/INFO。

9. **Developer override 冲突默认 blocker**
   - Source: AgentDS F-14
   - Status: accepted
   - Rationale: 若 override 是受控人工复核机制，审计 issue 不应默认 blocker。建议降为 reviewable。

10. **ThermometerService 默认实现耦合 Capability data 内部类**
    - Source: AgentGLM F-01
    - Status: accepted
    - Rationale: Service 已有 Protocol，但默认构造直接 import 具体 cache/source。建议在 Capability data 公共入口提供默认工厂。

### P2 — Backlog / 低风险修复

11. **温度计批量查询串行执行**
    - Source: AgentDS F-20, AgentGLM F-02
    - Status: accepted, deduplicated
    - Rationale: 两份 review 指向同一代码。可用 `asyncio.gather` 修复，但当前最大批量较小，优先级低于正确性和边界问题。

12. **清盘规模中文量词解析不足**
    - Source: AgentDS F-7
    - Status: accepted
    - Rationale: 需要增加中文量词解析测试，避免 `千万` 被误按 `万` 解析。

13. **风格/仓位 bucket first-match-wins**
    - Source: AgentDS F-8
    - Status: accepted with design confirmation
    - Rationale: 多风格命中时应返回 ambiguous/balanced，但具体归类策略需与 preferred_lens 行为对齐。

14. **外部 I/O timeout、并发写保护、重复表格解析**
    - Source: AgentDS F-11, F-23, F-25
    - Status: accepted
    - Rationale: 属于稳定性和维护性问题，应在后续专项中处理，不建议混入 P0 审计修复。

15. **基金类型识别顺序与设计文档不一致**
    - Source: AgentDS F-22
    - Status: needs decision
    - Rationale: 代码与 `docs/design.md` 口径冲突。需先判定指数/QDII/FOF 优先级的真实业务意图，再改代码或文档。

16. **Alpha 归因恒 insufficient_data**
    - Source: AgentDS F-24
    - Status: accepted, larger feature
    - Rationale: 这是模板第 2 章分析完整性缺口，不适合作为小修补处理，需要数据链路设计。

## Rejected Or Deferred Severity Adjustments

- AgentDS F-3 标为"严重"，controller 接受问题但建议修复排期中与 F-4 作为同源类型防御一起处理。当前触发概率低，但修复成本低，因此仍列入 P0。
- AgentGLM F-02 标为"低"，AgentDS F-20 标为"中"。Controller 采用 P2 backlog：问题成立，但当前最大批量较小，不应抢占审计完整性和边界修复。
- AgentDS 声明"无 blocker"被 controller 接受。当前没有证据表明这些问题会立刻导致数据损坏或安全风险。

## Recommended Fix Slices

### Slice A — C2 Contract Audit Integrity

- Fix: AgentDS F-1, F-2
- Files likely touched:
  - `fund_agent/fund/audit/contract_rules.py`
  - `fund_agent/fund/template/renderer.py` or template manifest/config if choosing contract merge
  - focused tests under `tests/`
- Stop condition:
  - C2 validates every `must_not_cover` via explicit programmatic rule or explicit non-programmatic coverage route.
  - Ch0 required items no longer share indistinguishable markers unless the contract intentionally merges them.

### Slice B — Numeric Type Guards

- Fix: AgentDS F-3, F-4
- Files likely touched:
  - `fund_agent/fund/analysis/_ratios.py`
  - `fund_agent/fund/analysis/risk_check.py`
  - `fund_agent/fund/analysis/checklist.py`
  - `fund_agent/fund/quality_gate.py`
  - focused tests under `tests/`
- Stop condition:
  - bool inputs are rejected consistently with `ValueError`.
  - Existing numeric string / int / float / Decimal behavior remains unchanged.

### Slice C — Layer Boundary Cleanup

- Fix: AgentDS F-5, AgentGLM F-01
- Files likely touched:
  - `fund_agent/ui/cli.py`
  - `fund_agent/services/__init__.py`
  - `fund_agent/services/thermometer_service.py`
  - `fund_agent/fund/data/__init__.py`
  - README updates if public import paths change
- Stop condition:
  - UI imports thermometer result types only through Service/Application-facing API.
  - Service no longer directly imports concrete Capability data cache/source internals for default construction.

### Slice D — CI Coverage Gate

- Fix: AgentDS F-6
- Files likely touched:
  - `.github/workflows/ci.yml`
  - possibly `pyproject.toml` coverage config
  - `tests/README.md` only if command semantics change
- Stop condition:
  - CI runs pytest with coverage collection and a documented fail-under threshold.

## Next Controller Recommendation

Start with **Slice A** and **Slice B**. They are small, correctness-oriented, and directly reinforce the repository's stated hard constraints. Slice C is also low risk but touches layering and public import surfaces, so it should be handled after the audit/type fixes or in a separate implementation worker.
