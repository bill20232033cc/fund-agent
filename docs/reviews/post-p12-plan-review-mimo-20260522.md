# Post-P12 Planning Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Post-P12 planning 的核心推荐（release/maintenance closeout 优先于直接开 P13 产品能力）方向正确，residual tracking 覆盖完整，Dayu/LLM 边界守卫清晰。但存在 1 个 HIGH 和 3 个 MEDIUM findings 需要在 closeout 执行前或执行中修正。

## 审查对象

`docs/reviews/post-p12-planning-20260522.md`

## 对照文件

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/p12-main-branch-closeout-20260522.md`
- `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md`
- `docs/repo-audit-20260521.md`

---

## 按审查重点逐项裁决

### 1. release/maintenance closeout 是否比立即开 P13 更合理

**裁决：方向正确，但 closeout 本身存在冗余。**

P12 main-branch closeout（`p12-main-branch-closeout-20260522.md`）已裁决 `CLOSED_ON_MAIN`，记录了 residuals、repo-audit exclusion 和 next entry point。再做一次 "release/maintenance closeout" 在功能上与已有 closeout artifact 高度重叠。

但考虑到以下两点，一个轻量级 reconciliation 仍有一定价值：
- control doc 的 `Active Gate Ledger` 需要追加 post-P12 planning gate 行
- repo-audit 的未处理 suggestions（见 Finding #1）需要显式记录

推荐：closeout scope 应收窄为 control doc ledger 更新 + repo-audit 残余项记录，不应重复 P12 closeout 已完成的 main-branch readiness 证据收集。

### 2. closeout allowed files / validation / review gates 是否足够具体

**裁决：基本足够，但存在 3 个具体缺口（Finding #2/#3/#4）。**

allowed/disallowed 文件清单（§6）明确且合理。但以下缺口可能导致执行偏差。

### 3. residual owners 是否充分

**裁决：覆盖完整，但 RR-13 缺少升级路径（Finding #5）。**

residual table 覆盖了所有 P12 aggregate judgment 中的残余项。owner 分配合理。RR-13 "user/App source" 的 human-owned 裁决正确——代码不应自动修改源数据。

### 4. 是否明确不引入 Dayu/LLM runtime，不让 Service/UI 直接读 document sources

**裁决：完全清晰。**

§5 Non-goals 第 3/4 条明确禁止。与 AGENTS.md 硬约束、design.md §1.2/§2.2、implementation-control.md Startup Packet 的 Non-goal reminder 完全一致。无 finding。

### 5. 是否需要 blocking user decision，plan 是否错误地继续

**裁决：plan 正确识别了 repo-audit 删除需要用户批准（§6、§7 Step 2），没有错误继续。**

但 plan 对 repo-audit 建议的处理存在事实错误（Finding #1）。

---

## Findings

### Finding #1 — HIGH：repo-audit 建议状态描述不准确

**位置**：§2 Direct Evidence 第 8 段、§7 Step 2 第 3 点

**声称**：
> "其 remaining suggestions 主要是 repo/doc hygiene，而不是当前产品安全 blocker"
>
> "Its suggestions are either already handled by later P10/P11/P12 work, non-blocking repo/doc hygiene candidates, or out of scope"

**反证**：`docs/repo-audit-20260521.md` 中以下 suggestions 并未被 P10/P11/P12 处理：

| repo-audit ID | 内容 | 当前状态 |
|---|---|---|
| D-1 | design.md 缺少项目结构树 | **未修复**，P10/P11/P12 均未补充 |
| D-8 / C-5 | `fund/tools/__init__.py` 仍存在（design.md 称已移除） | **未确认**，repo-audit 标记为中等严重度 |
| C-9 | reviews/ 目录 200+ 文件，占文件树 40%+ | **未处理**，repo-audit 标记为中等严重度 |

**影响**：closeout artifact 若采纳 plan 的口径，会错误地将上述未处理项记录为"已由后续工作覆盖"，掩盖真实的 repo-hygiene 债务。

**建议修正**：Step 2 应改为：
- repo-audit 中**部分**建议已被 P10/P11/P12 覆盖（如三源分歧、PR#5 状态、fund_type/section_catalog 一致性）
- **部分**建议仍为 open repo/doc hygiene candidates（D-1 项目结构树、D-8/C-5 tools 目录、C-9 reviews 膨胀）
- 这些 open items 不阻塞 maintenance closeout，但应作为显式 residual 记录并分配给未来 repo-hygiene phase

---

### Finding #2 — MEDIUM：allowed files 缺少 `docs/implementation-control.md` 的 Active Gate Ledger 更新

**位置**：§6 Scope / Allowed Files

**问题**：plan §6 将 `docs/implementation-control.md` 列为 "optional ... only after controller accepts the closeout"，但没有明确说明需要更新哪些内容。

对照 `implementation-control.md` 的 Active Gate Ledger 格式，每次 gate 状态变化都需要追加行。post-P12 planning gate 完成后，应追加：

```
| `post-P12 planning` | accepted | `docs/reviews/post-p12-planning-20260522.md` | local docs-only plan | [review results] | release/maintenance closeout | closeout |
```

同时 Startup Packet 的 `Latest accepted planning artifact` 也应更新。

**建议修正**：§6 应将 `docs/implementation-control.md` 从 optional 升级为 closeout 的 required allowed file，并明确需要更新 Active Gate Ledger 行和 Startup Packet 字段。

---

### Finding #3 — MEDIUM："maintenance-ready" 状态无定义

**位置**：§4 Recommended Next Gate、§7 Step 4

**问题**：plan 多次引用 "maintenance-ready" 作为 release lane 的终止状态，但从未定义其验收条件。

对照 implementation-control.md 的 gate 格式，每个 gate 都需要明确的 validation 和 exit criteria。"maintenance-ready" 如果没有定义，controller 无法判断何时停止。

**建议修正**：应补充 "maintenance-ready" 的最小定义：
- main branch 无 tracked uncommitted changes
- full suite 当前 baseline 通过（403 passed 或更高）
- ruff 和 diff check 通过
- 所有 open residuals 有明确 owner
- control doc gate ledger 与实际状态一致

---

### Finding #4 — MEDIUM：validation 缺少 `git diff --name-only` 检查

**位置**：§7 Step 1、§8 Validation Commands

**问题**：validation commands 包含 `git status --short`、`pytest`、`ruff check`、`git diff --check HEAD`，但缺少 `git diff --name-only` 来验证 closeout 实际修改了哪些文件。

对比 P12 aggregate deepreview controller judgment 的验证方式（`git diff --name-only ba77e02..HEAD`），closeout 也应该显式检查只修改了 allowed files。

**建议修正**：§7 Step 1 和 §8 的 validation commands 应补充：
```bash
git diff --name-only HEAD
```
并添加 expected assertion：输出的文件列表应 only 包含 §6 中的 allowed files。

---

### Finding #5 — LOW：RR-13 缺少用户不响应时的升级路径

**位置**：§3 Candidate Comparison、§9 Residual Tracking

**问题**：RR-13 duplicate `016492` 正确保持 human-owned，但 plan 没有说明如果用户长期不响应该如何处理。

当前 RR-13 从 P4 开始就保持 human-owned（见 implementation-control.md P4-P5-P9 记录），已跨越 8 个 phase。虽然不阻塞当前 closeout，但应在 residual table 中增加备注：如果用户在下一次产品 phase 启动前仍未裁决，应将此问题作为 P13 planning 的显式 blocking input。

---

## 验证项（无 finding）

| 审查项 | 结论 |
|---|---|
| 是否正确避免重开 P12 | ✅ §5 第 1 条明确 |
| Dayu/LLM/runtime 边界 | ✅ §5 第 3/4 条与 AGENTS.md、design.md 一致 |
| Service/UI 不直接读 document sources | ✅ §5 第 4 条明确 |
| repo-audit 不自动发布/删除 | ✅ §6、§7 Step 2 正确要求用户批准 |
| residual table 覆盖完整性 | ✅ 与 P12 aggregate judgment residual list 一致 |
| 不修改 source/test/README/design | ✅ §6 disallowed files 清单正确 |
| controller handoff prompt 具体性 | ✅ §11 格式完整，步骤明确 |

---

## 修正建议汇总

| 优先级 | Finding | 修正动作 |
|---|---|---|
| HIGH | #1 repo-audit 建议状态不准确 | Step 2 改为区分"已覆盖"和"仍 open"的 suggestions，open 项作为 residual 记录 |
| MEDIUM | #2 allowed files 缺 control doc | §6 将 `docs/implementation-control.md` 升级为 required，并明确更新内容 |
| MEDIUM | #3 maintenance-ready 无定义 | §4 或 §7 补充最小验收条件 |
| MEDIUM | #4 缺 git diff --name-only | §7/§8 补充 diff name-only 检查和 expected assertion |
| LOW | #5 RR-13 升级路径 | §9 residual table 增加长期不响应备注 |

---

## 结论

Post-P12 planning 的核心方向正确：不立即开 P13 高风险产品能力，先收口当前 release lane 状态。5 个 findings 均可在 closeout 执行前或执行中修正，不阻塞整体流程。建议 controller 在执行 closeout 时逐项对照上述 findings 修正 artifact 内容。
