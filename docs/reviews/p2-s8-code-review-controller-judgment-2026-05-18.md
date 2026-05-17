# P2-S8 Code Review Controller Judgment

> 日期：2026-05-18
> Controller：Codex
> Phase / Slice：P2 / P2-S8 程序审计
> Implementation artifact：`docs/reviews/p2-s8-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现新增：
  - `ProgrammaticAuditInput`
  - `AuditIssue`
  - `ProgrammaticAuditResult`
  - `run_programmatic_audit(...)`
- controller 本地边界检查确认：
  - 程序审计位于 `fund_agent/fund/audit/audit_programmatic.py`
  - 模块不读取 PDF、缓存文件、文档仓库或文件系统数据
  - P1/P2/P3 只消费报告 Markdown 结构和证据锚点标记
  - L1 消费 `RabcAttribution`，不从报告文字反推 R=A+B-C
  - R1/R2 消费 `ChecklistResult` 和显式最终判断，不从报告文字间接审计检查清单
  - 缺少必需输入时返回失败，不把未执行规则伪装成通过
- controller 本地验证：

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

## 2. Accepted Findings

### A1-已修复-高-缺少审计输入时会静默跳过规则并返回通过

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - `checked_rules` 固定声明执行 P1/P2/P3/L1/R1/R2，但原实现允许 `ProgrammaticAuditInput()` 空输入返回通过
  - 这会让程序审计 gate 失去阻断作用，尤其在 P2-S9/P3 接入时可能把未接入的结构化结果误判为合格
  - 按 `docs/design.md` 第 5.2 节，MVP 程序审计是阻断级审计，不能用缺省参数表达“规则通过”
- **修复**：
  - 新增 `_audit_required_inputs(...)`
  - 缺少 `report_markdown` 时触发 P1
  - 缺少 `rabc_attributions` 时触发 L1
  - 缺少 `checklist_result` 时触发 R1
  - 缺少 `final_judgment` 时触发 R2
  - 新增空输入和缺少最终判断回归测试
  - 同步更新 `fund_agent/fund/README.md`、`tests/README.md` 和 implementation artifact

## 3. Deferred Findings

### D1-未修复-中-模板渲染器尚未接入程序审计输入

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S9`
- **原因**：
  - P2-S8 已冻结审计契约和输入完整性要求
  - 报告 Markdown 的生成、8 章结构和审计输入装配属于模板渲染器 slice

### D2-未修复-中-证据锚点附录汇总尚未接入

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S10`
- **原因**：
  - P2-S8 当前只识别报告是否存在证据锚点或“证据与出处”标记
  - 附录格式 `年报[年份]§[章节]表[编号]行[行号]` 的系统化渲染应由证据锚点 slice 负责

### D3-未修复-低-E1/E2/E3/C1/C2、LLM 审计和证据复核未实现

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`v2 audit`
- **原因**：
  - `docs/design.md` 第 5.2 节只要求 MVP 落地 P1/P2/P3/L1/R1/R2
  - 证据精确性、证据与断言匹配、内容违规等需要 LLM/证据复核层，不属于本 slice

## 4. 当前 Gate 结论

- `P2-S8 controller code review` 结论：`pass-after-fix`
- 当前没有 blocker
- `P2-S8` 可推进到下一 gate：`P2-S9 implementation + review`
