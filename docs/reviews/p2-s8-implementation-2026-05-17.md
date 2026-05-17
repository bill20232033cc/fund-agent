# P2-S8 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S8 implementation`
> slice：`P2-S8 实现程序审计（P1/P2/P3/L1/R1/R2）`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/audit/audit_programmatic.py` 内实现 MVP 程序审计。
- 覆盖 `docs/design.md` 第 5.2 节中 MVP 标记为实现的 P1/P2/P3/L1/R1/R2。
- 对故意注入错误和输入缺失写单元测试：
  - 必需输入缺失
  - 章节缺失
  - 章节内容过短
  - 证据锚点缺失
  - R=A+B-C 不闭合
  - 检查清单信号与规则不一致
  - 最终判断与检查清单信号矛盾

### Non-Goals

- 不实现 E1/E2/E3/C1/C2 或 L2。
- 不实现 LLM 审计和证据复核。
- 不读取年报、PDF、缓存文件或文档仓库。
- 不接入模板渲染器或 CLI 端到端流程。

## Changed Files

- `fund_agent/fund/audit/audit_programmatic.py`
- `fund_agent/fund/audit/__init__.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `ProgrammaticAuditInput`
   - `report_markdown` 用于 P1/P2/P3
   - `rabc_attributions` 用于 L1
   - `checklist_result` 用于 R1/R2
   - `final_judgment` 用于 R2
2. 新增 `AuditIssue`
   - 输出规则码、阻断级别、问题说明和位置
3. 新增 `ProgrammaticAuditResult`
   - 输出是否通过、问题列表和已执行规则
4. 新增 `run_programmatic_audit(...)`
   - 必需输入缺失：缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时直接返回失败
   - P1：检查必要章节标题
   - P2：检查章节内容长度
   - P3：检查证据与出处或证据锚点
   - L1：检查 R=A+B-C 闭合
   - R1：检查 7 问题数量、汇总信号和单题状态
   - R2：检查最终判断与检查清单信号一致性

## Boundary Closure

- 程序审计位于 `Capability / fund_agent/fund/audit`，未越界进入 UI、Service、Runtime 或 Engine。
- P1/P2/P3 只审已渲染报告 Markdown 的结构。
- L1/R1/R2 消费结构化结果，不靠报告文字间接判断计算或检查清单规则。
- 缺少必需输入时不静默跳过对应规则，也不把未执行规则记录为通过。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py -q
.venv/bin/python -m pytest tests/fund/analysis tests/fund/audit -q
.venv/bin/python -m ruff check fund_agent/fund tests/fund/analysis tests/fund/audit
```

结果：

```text
9 passed
49 passed
All checks passed!
```

## Residual Risks

### Fixed Later Slice

- `P2-S9` owner：模板渲染器尚未接入程序审计输入。
- `P2-S10` owner：证据锚点渲染和附录汇总尚未接入。

### Later Phase

- `P3-S4` owner：端到端报告通过程序审计尚未验证。
- v2 audit owner：E1/E2/E3/C1/C2、LLM 审计和证据复核尚未实现。

### User Decision

- 无。

## Completion Status

- `P2-S8` implementation completion signal：`reached`
- 判断依据：
  - P1/P2/P3/L1/R1/R2 均已实现
  - 缺少必需输入会阻断审计
  - 故意注入错误均有测试覆盖
  - 结构化计算审计未依赖报告文字
  - 核心路径和防御路径均通过验证
