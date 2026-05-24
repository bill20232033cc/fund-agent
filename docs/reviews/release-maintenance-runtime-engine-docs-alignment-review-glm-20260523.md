# Runtime/Engine Docs-Only Alignment Review (GLM) — 2026-05-23

> **Reviewer**: GLM-5.1
> **Scope**: `docs/design.md`、`docs/implementation-control.md`、`fund_agent/README.md` 未提交 diff；新增 review artifacts 四份
> **Authority**: 用户提供的六层边界 `UI / Application / Runtime / Service / Engine / Capability`；Dayu 只参考，不引入外部 runtime
> **Design truth**: `docs/design.md` v2.2
> **Control truth**: `docs/implementation-control.md`

---

## 结论：pass-with-findings

无 blocker。五项 review focus 全部通过。2 条 non-blocking finding 供后续参考，不影响本次 acceptance。

---

## Review Focus 逐项裁决

### F1. design.md §9 目录树是否不再把不存在的 runtime/engine 画成当前磁盘事实

**PASS**

diff 已删除 §9 项目结构树中的两行：

```diff
-│   ├── runtime/                         # Runtime 层（目标包；当前未接入 Agent runtime）
-│   ├── engine/                          # Engine 层（目标包；当前未接入通用工具执行框架）
```

替代为树后独立段落（第 811 行）：

> Runtime / Engine 是目标边界，不是当前磁盘目录事实。当前生产路径故意保持为 UI → Application → Service → Fund Capability；在没有真实 session/run/cancel/resume/outbox、scene registry、tool loop、runner、ToolRegistry、ToolTrace 或 context budget 需求前，不创建 Runtime 或 Engine 占位包。

树只反映磁盘事实，Runtime/Engine defer decision 以 prose 记录在树后。DS review M1 和 GLM review M1 指出的问题已被修正。

### F2. README 是否清楚区分当前生产路径与六层目标边界

**PASS**

当前 `fund_agent/README.md` 结构清晰三层递进：

1. **当前生产路径**：`UI -> Application -> Service -> Fund Capability`（code block）
2. **目标边界与 defer 说明**："目标架构边界仍是 UI / Application / Runtime / Service / Engine / Capability 六层。当前没有 `Runtime` 或 `Engine` 通用包是有意 defer，不是遗漏"
3. **Dayu 参考 / 不依赖声明** + 具体触发条件

包边界表只列 `ui`/`application`/`services`/`fund`/`config` 五个实际存在的包。`config` 描述从"当前不提供 Host/Engine runtime 配置"改为"当前不提供 Runtime/Engine 配置"——更准确，不暗示存在 Host/Engine。

稳定边界新增条目："Runtime / Engine 是目标边界；当前不创建 `runtime` / `engine` 占位目录，后续必须由具体需求 gate 驱动。"

README 没有 把 Runtime/Engine 写成已实现。

### F3. implementation-control 是否准确记录 artifacts、gate、next entry point，且没有把 defer 写成 done implemented

**PASS**

关键更新点逐一验证：

| 字段 | 更新内容 | 准确性 |
|------|---------|--------|
| 当前状态 | "Runtime/Engine boundary decision plan 已通过 DS/GLM review 和 controller 裁决；Slice 1 docs-only alignment 已完成本地修改，等待 review/acceptance" | ✅ 准确反映当前真实状态，不说"已完成" |
| Current gate | "release maintenance Runtime/Engine boundary decision accepted; Slice 1 docs alignment pending review" | ✅ |
| Next entry point | "Runtime/Engine docs alignment review/acceptance or push authorization" | ✅ |
| Latest artifacts 行 | 新增四份 Runtime/Engine boundary decision artifacts | ✅ |
| 候选表新增行 | 状态为 "accepted; Slice 1 docs alignment pending review"，scope 清楚限制为 docs-only | ✅ 不是 done implemented |
| Product baseline | 追加 "Runtime/Engine boundary decision accepted, Slice 1 docs alignment completed locally and pending review/acceptance" | ✅ |
| Resume checklist | 更新 current truth 和新增 decision summary；移除一处 `AGENTS.md` 前缀改为 "the six-layer boundary" | ✅ 与 AGENTS.md 冲突处理一致 |

Defer 被准确记录为 defer，没有写成 done/implemented。

### F4. 是否未碰生产代码/测试/root README/AGENTS.md；是否未创建 runtime/engine

**PASS**

验证结果：

- `git diff --check` — 无 whitespace 错误
- `git diff --cached --name-status` — 无 staged 文件
- `ls fund_agent/runtime fund_agent/engine` — 目录不存在
- `git status --short -- fund_agent/runtime fund_agent/engine` — 无相关变更
- AGENTS.md 状态为 ` M`（本地已修改，未 staged）—— 本次 diff 未触碰 AGENTS.md
- diff 只涉及三个指定文件，无生产代码、测试或 root README 变更

### F5. 是否有残留四层 Dayu 目标或 dayu.host/dayu.engine 生产依赖口径

**PASS**

扫描结果：

- `rg "dayu\.host|dayu\.engine"` — 零命中。不存在 `dayu.host` / `dayu.engine` 生产依赖口径。
- `rg "UI -> Service -> Host -> Agent"` — 零命中。四层目标已从 diff 涉及范围移除。
- `rg "外部 Dayu runtime"` — 9 处命中，全部是否定/排除语境（"不依赖"、"不重新引入"、"未吸收"），无一处声称 Dayu runtime 是当前生产依赖。
- `rg "fund_agent/runtime|fund_agent/engine"` — 零命中。不存在对未创建包的路径引用。

implementation-control.md diff 将"四层 `UI -> Service -> Host -> Agent`"简化为"四层口径"，避免显式写出 Dayu 四层目标结构，减少误读风险。

---

## Non-Blocking Findings

### N1. design.md §12 Plan Review 检查清单仍引用 "`AGENTS.md` 六层边界"

**位置**: design.md 第 983 行

**内容**: "是否仍以 `AGENTS.md` 六层边界为规则真源，不重新引入外部 Dayu runtime 或三层口径"

**观察**: 本次 diff 在 design.md 头部将"已按 `AGENTS.md` 统一规则真源"改为"已按用户提供的六层边界"，但在 §12 检查清单中保留了 `AGENTS.md` 引用。两者语境不同——头部声明是权威来源声明（因本地冲突已改为用户提供的版本），§12 是 plan review 检查清单（应检查是否有合规真源）。在当前 AGENTS.md 冲突未解决前，两处表述都是合理的。

**建议**: 无需修改。当 AGENTS.md 冲突解决后，统一复查所有 `AGENTS.md` 引用即可。

**严重度**: Info。

### N2. implementation-control.md Resume Checklist 持续增长

**观察**: Resume checklist 已超过 400 行（单段），本次 diff 进一步追加内容。虽然信息准确，但可维护性在下降。这不是本次 diff 引入的新问题，而是持续积累的结构性债务。

**建议**: 后续 release maintenance 可考虑将 checklist 拆分为结构化字段表，而非单段长文。不在本次 scope 内。

**严重度**: Info。

---

## 新增 Artifacts 验证

| Artifact | 存在 | 内容一致性 |
|----------|------|-----------|
| `release-maintenance-runtime-engine-boundary-decision-plan-20260523.md` | ✅ | Plan 与 controller judgment 记录一致；defer decision、trigger conditions、scope/non-scope 清晰 |
| `release-maintenance-runtime-engine-boundary-decision-plan-review-ds-20260523.md` | ✅ | Verdict pass-with-risks；M1-M4 findings 与 Slice 1 执行结果对齐（M1 树已修正） |
| `release-maintenance-runtime-engine-boundary-decision-plan-review-glm-20260523.md` | ✅ | Verdict pass-with-risks；M1-M2 findings 与 Slice 1 执行结果对齐 |
| `release-maintenance-runtime-engine-boundary-decision-plan-review-controller-judgment-20260523.md` | ✅ | Accepted；finding disposition 与 DS/GLM review findings 对齐；next slice 指向 Slice 1 docs-only |

所有 artifacts 互相一致，与 implementation-control 记录的 artifact 路径一致。

---

## Constraint Compliance Summary

| 约束 | 结果 |
|------|------|
| 六层边界以用户提供的规则为权威 | ✅ |
| 当前生产路径为 UI → Application → Service → Capability | ✅ |
| Runtime/Engine defer 而非否认 | ✅ |
| Dayu 只参考，不引入外部 runtime | ✅ |
| 不修改生产代码/测试 | ✅ |
| 不创建 runtime/engine 包 | ✅ |
| 不修改/stage AGENTS.md | ✅ |
| 不 commit/push/PR | ✅ |
| FundDocumentRepository 边界不变 | ✅ |

---

## 最终判定

**pass-with-findings**

五项 review focus 全部通过。2 条 non-blocking finding（N1: §12 checklist `AGENTS.md` 引用一致性、N2: resume checklist 可维护性）均不影响本次 acceptance。Slice 1 docs-only alignment 的 diff 可以接受。
