# Release Maintenance Next Candidate Plan Re-Review — MiMo

> **审查对象**: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`（修订版）
> **Fix artifact**: `docs/reviews/release-maintenance-next-candidate-plan-fix-20260524.md`
> **Controller judgment**: `docs/reviews/release-maintenance-next-candidate-plan-review-controller-judgment-20260524.md`
> **审查类型**: re-review against C1-C9 accepted findings
> **审查日期**: 2026-05-24
> **结论**: **PASS**

---

## 逐项验证

### C1 — dayu-agent pyproject baseline 定义模糊

- **Controller 要求**: 本地 baseline 为 `docs/design.md` §9.1 + 当前 `pyproject.toml`；外部 dayu-agent 需记录 URL/commit/provenance；增加具体验证命令
- **修订计划核查**:
  - Line 35: 本地 baseline 明确为 `docs/design.md` §9.1 + 当前 `pyproject.toml`，列出具体工程要求 ✅
  - Line 36: 外部 dayu-agent 要求记录"精确 URL、commit/revision、获取时间、摘要内容或完整片段" ✅
  - Line 156-157: dependency gate trigger 引用"local baseline: `docs/design.md` §9.1 plus current `pyproject.toml`" ✅
  - Line 179-183: Dependency gate 命令集包含 `rg -n "dayu" pyproject.toml`、`uv lock --check`、setuptools 检查、import smoke ✅
- **Fix artifact 核查**: Fix artifact line 21 与修订计划一致 ✅
- **最终状态**: **已修复**

### C2 — Decision artifact 缺少模板结构

- **Controller 要求**: 为 `release-maintenance-host-agent-boundary-decision-20260524.md` 增加最小章节骨架
- **修订计划核查**: Line 61-75 列出 13 个必需章节：`Gate/Scope`、`Direct Evidence`、`Current-State Decision`、`Host Gate Entry Criteria`、`Agent Execution Gate Entry Criteria`、`Dependency Gate Status`、`Future Gate Skeletons`、`Validation Plan`、`Review Checklist`、`Stop Conditions`、`Decision Absorption Path`、`Completion Report Format`、`Handoff Status` ✅
- **最终状态**: **已修复**

### C3 — rg 验证只覆盖存在性

- **Controller 要求**: 声明 rg 命令为存在性检查，语义正确性由 plan review / re-review 覆盖
- **修订计划核查**: Line 116-118 Validation note："All `rg` commands in this plan are programmatic existence checks only. They prove required terms or guardrails are present in the artifact; they do not prove the decision is semantically correct. Semantic correctness, boundary fit, and evidence quality are covered by the plan review / re-review gates." ✅
- **最终状态**: **已修复**

### C4 — 决策落地路径缺失

- **Controller 要求**: 增加 Decision absorption path，说明被接受的决策如何进入真源
- **修订计划核查**:
  - Line 201-202: Slice 4 增加 "Decision absorption path describing how an accepted decision is recorded: controller records it in control tracking, or opens a separate docs/control update only if the accepted decision changes current truth" ✅
  - Line 73: Required artifact section skeleton 包含 `## Decision Absorption Path` ✅
  - Line 281: Completion Report Format 包含 `Decision absorption path:` 字段 ✅
- **最终状态**: **已修复**

### C5 — Stop condition 报告格式缺失

- **Controller 要求**: 增加最小停止报告格式：触发条件、上下文/证据、建议 scope 调整、是否需要用户决定
- **修订计划核查**: Line 251-256 Stop report format 包含：`Triggered condition:`、`Context / evidence:`、`Suggested scope adjustment:`、`User decision required: yes / no` ✅
- **最终状态**: **已修复**

### C6 — code-generation-ready 措辞不适用于纯文档交付物

- **Controller 要求**: 将 code-generation-ready 替换或限定为 plan-review-ready decision plan
- **修订计划核查**: Line 5 "plan-review-ready 决策计划。本 work unit 是 document-only boundary decision，不授权代码生成、Host/Agent 实现、依赖修改或包结构变更" ✅
- **最终状态**: **已修复**

### C7 — Slice 2 缺少可执行验证命令

- **Controller 要求**: 为 dependency-gate-blocked、no placeholder packages、no extra_payload 增加 rg 验证命令
- **修订计划核查**: Line 164 增加 `rg -n "dependency gate remains blocked|blocked until implementation imports|no fund_agent/host|no fund_agent/agent|extra_payload|local baseline|docs/design.md.*9\\.1|external dayu-agent|URL|commit|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` ✅
- **最终状态**: **已修复**

### C8 — Completion validation 字段缺少通过标准

- **Controller 要求**: Validation run 应记录每条命令、预期断言、退出码或观测通过信号
- **修订计划核查**: Line 280 "Validation run: list each command, expected assertion, exit code or observed pass signal, and any skipped validation with reason." ✅
- **最终状态**: **已修复**

### C9 — design.md §12 checklist 不完整

- **Controller 要求**: 增加年报访问路径（FundDocumentRepository / FundDataExtractor）和 License/repo hygiene 检查项
- **修订计划核查**:
  - Line 236: "Confirms production annual-report access remains through `FundDocumentRepository` / `FundDataExtractor` only." ✅
  - Line 237: "Confirms License/repo hygiene is preserved and not weakened by test or metadata relaxation." ✅
- **最终状态**: **已修复**

---

## 新引入变更检查

| 变更 | 是否引入新 blocker |
|------|-------------------|
| Validation note (line 116-118) | 否。明确 rg 局限性，降低误判风险 |
| Artifact section skeleton (line 61-75) | 否。增加结构但未扩展 scope |
| External dayu-agent provenance 要求 (line 36, 157) | 否。仅约束未来 dependency gate，不增加当前 work unit 范围 |
| Stop report format (line 251-256) | 否。最小格式，不增加实现负担 |
| Dependency gate 命令集 (line 179-183) | 否。只约束未来 gate 的验证方式 |

未发现新 blocker。

---

## 总结

| Finding | 最终状态 |
|---------|---------|
| C1 dayu-agent baseline 定义 | 已修复 |
| C2 artifact 模板结构 | 已修复 |
| C3 rg 验证局限性声明 | 已修复 |
| C4 决策落地路径 | 已修复 |
| C5 stop condition 报告格式 | 已修复 |
| C6 code-generation-ready 措辞 | 已修复 |
| C7 Slice 2 验证命令 | 已修复 |
| C8 validation pass 标准 | 已修复 |
| C9 review checklist 补全 | 已修复 |

**结论**: **PASS**。C1-C9 全部已修复，未引入新 blocker。修订计划可 handoff 至下一 gate。
