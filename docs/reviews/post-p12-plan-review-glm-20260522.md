# Post-P12 Planning Review — AgentGLM（2026-05-22）

- **Reviewer**: AgentGLM
- **Review target**: `docs/reviews/post-p12-planning-20260522.md`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Closeout truth**: `docs/reviews/p12-main-branch-closeout-20260522.md`
- **Aggregate truth**: `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md`
- **Repo audit input**: `docs/repo-audit-20260521.md`
- **Agent rules**: `AGENTS.md`

## Verdict

`PASS_WITH_FINDINGS`

Plan 推荐合理、证据充分、边界守卫完整。发现 2 个非阻断 finding，不影响 plan 可执行性。

## Challenge 1: release/maintenance closeout 是否比立即开 P13 更合理？

**结论：推荐合理，PASS。**

证据链：

1. **Scope/风险不对称**：P12 aggregate 双 PASS、`403 passed`，release lane 处于 clean state。tracking-error/index methodology/constituents 真数据能力需新增数据源、schema、cache、计算口径、source fallback 和 tests（Plan §3 Candidate Comparison 明确标注 scope/risk 高）。E1-E3/Evidence Confirm 属于 v2 audit layer，可能引入 LLM/修复合同（Plan §3 标注需重新设计边界）。在 clean release lane 上先做 closeout、再由后续 phase 明确选择 P13 方向，风险收益比优于直接跳入高 scope 产品能力。

2. **Closeout 有实质内容**：不是空操作——需要 main-branch readiness evidence（Plan §7 Step 1: pytest/ruff/diff check）、repo-audit 显式 disposition record（Step 2）、residual owner reconciliation（Step 3）和 next-lane recommendation（Step 4）。这些是 P12 closeout artifact（`docs/reviews/p12-main-branch-closeout-20260522.md`）未覆盖的 release-lane 收口。

3. **Repo-audit 不适合在当前 closeout 中发布**：`docs/repo-audit-20260521.md` 是 P8-era 审核输入，基于 commit `d5d54ae8`，当时仓库状态为"P8 closed, PR#5 open"（repo-audit §0）。当前仓库已推进到 P12 closed on main，repo-audit 多项发现已被后续工作覆盖或过时（如 D-7/P2-4/P2-5 等），且包含三源分歧描述（repo-audit §1）已由 P11 control-doc recovery 解决。Plan 正确判断发布可能制造历史事实混淆。

4. **"Stop at maintenance-ready"是合法选项**：Plan §4 Step 4 明确推荐"Current release lane can stop at maintenance-ready if validation passes"，不强制进入 P13。这避免了在 closeout 中隐式启动新产品 phase 的风险。

## Challenge 2: closeout allowed files、validation、review gates 是否足够具体？

**结论：PASS，有 1 个非阻断 finding。**

### 防护机制评估

Plan §6 Scope/Allowed Files 采用双层设计：

- **Planning artifact 自身**：只允许 `docs/reviews/post-p12-planning-20260522.md`
- **推荐的 next closeout gate**：白名单 `docs/reviews/` 下 artifact + `docs/implementation-control.md`（仅在 controller accept 后）
- **显式黑名单**：source code、tests、README（除非 review 发现 stale statement）、`docs/design.md`、`docs/repo-audit-20260521.md`、RR-13 source data

Plan §5 Non-goals 八条明确禁止项覆盖：不重开 P12、不实现新数据抽取、不引入 LLM/Evidence Confirm/Dayu runtime、不修改 Service/UI/CLI、不修改 FundDocumentRepository、不 auto-resolve RR-13、不发布 repo-audit、不添加 release automation。

Plan §8 validation commands 具体：`git status --short`、`pytest`、`ruff check`、`git diff --check HEAD`。

Plan §11 controller handoff 包含 stop-if 条件："Stop if validation fails, if tracked source/test changes are required, if repo-audit disposition requires deletion/publication, or if RR-13 source data would need automatic modification."

### Finding F1（LOW）：validation assertion 允许"unrelated failure"继续

Plan §8 Validation assertions：

> Full suite and ruff pass, **or any failure is explicitly unrelated and assigned**.

这个"or"子句允许 closeout 在测试失败时继续，只要失败被声明为"unrelated"。对于 docs-only closeout，这实际上合理（docs 变更不应引入新 test failure），但措辞可能被滥用——"unrelated"的判定标准未定义，没有要求独立 reviewer 确认 unrelated 性质。

**建议**：将"or"子句改为"如果 full suite 或 ruff 失败，closeout 必须停止并记录失败原因；只有 controller 显式确认失败与 closeout 无关后才能继续"。

**严重度**：LOW。当前 docs-only closeout 不太可能触发 unrelated failure，且 controller handoff 已包含 stop-if 覆盖。

## Challenge 3: residual owners 是否充分？

**结论：PASS。**

Plan §9 Residual Tracking 列出 9 项 residual，每项都有 Decision 和 Owner/destination：

| Residual | Owner 判定 | 评估 |
|---|---|---|
| Real tracking-error extraction/calculation | Future P13 Fund Capability extractor/calculation design | ✅ 正确归属 Capability 层，不放在 Service/UI |
| Real index methodology / constituents extraction | Future P13 documents/extractor design through `FundDocumentRepository` | ✅ 明确经 FundDocumentRepository，符合 AGENTS.md 和 design.md 约束 |
| Evidence sufficiency / E1-E3 / Evidence Confirm | Future audit architecture phase | ✅ 与 design.md §5.2 v2 标注一致，独立于数据抽取 phase |
| Long-anchor truncation/grouping | Future evidence-display UX slice | ✅ 有条件触发（only when real large anchor sets appear） |
| Future ITEM_RULE expansion | Future rule-addition slice | ✅ 有条件触发（only when new manifest entries exist） |
| Chapter-mismatch duplicate C2 noise | Future maintainability cleanup | ✅ 有条件触发（if issue volume becomes material） |
| RR-13 duplicate `016492` | User / App source | ✅ human-owned，Plan §5 明确不 auto-resolve |
| `docs/repo-audit-20260521.md` | Controller / user | ✅ excluded/untracked，需 future scope 或 user approval |
| Repo/doc hygiene suggestions | Future repo-hygiene phase if selected | ✅ 不在当前 closeout scope |

Tracking-error 和 index methodology 两项都明确标注必须经 `FundDocumentRepository` 和 Fund Capability 内部设计，不允许 Service/UI 直接读取。这符合 AGENTS.md "生产年报 PDF 访问必须经过 FundDocumentRepository" 硬约束和 design.md §2.2 "Service/UI 不直接读取 PDF、cache 或年报文件"。

## Challenge 4: 是否明确不引入 Dayu/LLM runtime，不让 Service/UI 直接读 document sources？

**结论：PASS。**

Plan 在多处显式排除：

- §5 Non-goals 第 3 条："Do not implement E1/E2/E3, LLM audit, Evidence Confirm, RepairContract, LLM writing, Host, Engine, tool loop, prompt scene registry, or Dayu runtime."
- §5 第 4 条："Do not modify Service/UI/CLI or let them directly read document repository internals."
- §5 第 5 条："Do not modify FundDocumentRepository, PDF/cache helpers, source fallback taxonomy, source repository internals, or quality gate semantics."
- §2 Direct Evidence 引用 design.md："LLM audit / Evidence Confirm 是 v2；Dayu Host/Engine/tool loop 不是当前生产依赖"
- §2 引用 AGENTS.md："生产年报访问经 FundDocumentRepository"
- §3 Candidate Comparison 表格中 tracking-error extractor 标注"必须在 Fund Capability 内设计"

这与 AGENTS.md §硬约束（"Dayu 只作为方法论和历史研究参考"、"生产年报 PDF 访问必须经过 FundDocumentRepository"）和 design.md §1.2（"确定性 MVP 主链路"、"不把外部 Dayu Host/Engine/tool loop 作为主链路依赖"）完全一致。

## Challenge 5: 是否需要 blocking user decision？若需要 plan 是否错误地继续？

**结论：PASS，有 1 个非阻断 finding。**

### Repo-audit 删除/发布

Plan 正确识别这是一个需要 user decision 的操作，且正确处理为不阻断：

- §5 Non-goals 第 8 条："Do not publish, stage, edit, or delete `docs/repo-audit-20260521.md` in this selected closeout unless the user separately authorizes deletion/disposal."
- §6 Scope："Closeout should not stage or publish the untracked repo-audit file. If the controller wants it removed from the filesystem, that is a separate destructive local cleanup decision requiring explicit user approval."
- §10 Open Questions："Whether the user wants to delete the local untracked repo-audit; deletion is outside this plan and should require explicit approval."
- §11 Controller Handoff stop-if 条件："Stop if...repo-audit disposition requires deletion/publication"

Plan 没有错误地继续执行需要 user decision 的操作——它明确把 repo-audit 处置排除在 closeout scope 之外。

### RR-13

Plan §5 明确不 auto-resolve，§9 标注 user/App source。无需 blocking decision，因为当前状态（保持 human-owned）是安全的默认行为。

### Finding F2（LOW）："No blocking open questions"措辞可能误导

Plan §10：

> No blocking open questions.

紧接着列出 3 个"Non-blocking choices for controller"。其中 repo-audit 删除确实不阻断 closeout（因为 plan 明确排除它），但"whether to update implementation-control.md immediately"实际上是一个 closeout 内部决策——如果 closeout 需要更新 control doc（Plan §6 允许），那么"立即还是延后"会影响 closeout artifact 内容。

**建议**：将 §10 第一句改为"没有阻断 closeout 执行的 open question"，避免与 control-doc 更新时机的内部决策混淆。

**严重度**：LOW。不影响 plan 可执行性，controller 能根据上下文正确判断。

## Findings Summary

| # | Severity | Area | Description |
|---|---|---|---|
| F1 | LOW | §8 Validation | "unrelated failure"继续条件缺少独立确认机制，建议改为 controller 显式确认 |
| F2 | LOW | §10 Open Questions | "No blocking open questions"措辞可能误导，建议限定为"no blocking questions for closeout execution" |

## Positive Observations

1. **Candidate comparison 表格**（§3）覆盖 7 个候选，评估维度（product/safety value、scope/risk、boundary fit）一致，decision 列给出明确理由。这是 post-phase planning 的良好实践。

2. **Controller handoff**（§11）包含具体的 stop-if 条件、completion report 格式和 step-by-step 指令，降低了 handoff 歧义。

3. **Non-goals**（§5）八条排除项与 AGENTS.md 和 design.md 的硬约束完全对齐，没有遗漏或弱化。

4. **证据溯源**（§2）引用了 7 个具体文档的对应条款，不是抽象主张。

## Conclusion

Plan 推荐的 release/maintenance closeout 是当前最低风险、最高确定性的下一步。所有 residual 都有 owner，Dayu/LLM/Service-UI 边界守卫完整，repo-audit 处置正确排除在 closeout scope 之外。2 个 LOW finding 不阻断执行，controller 可选择在 closeout 过程中采纳或忽略。
