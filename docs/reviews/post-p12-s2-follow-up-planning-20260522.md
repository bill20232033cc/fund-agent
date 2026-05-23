# Post-P12-S2 Follow-up Planning（2026-05-22）

- **Role**: AgentCodex planning specialist
- **Gate**: `post-P12-S2 follow-up planning`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **P12 accepted commits**: `79fb3e3`, `aad094f`, `c757036`, `617ca58`, `a9c1ac5`, `24a35b4`, `c44f063`
- **Output only**: 本 artifact 只规划下一步；不改 source/test/README/control doc，不 commit、不 push、不建 PR。

## 1. Goal / Motivation

判断 P12 是否应继续开新 slice，还是关闭 `ITEM_RULE deterministic compliance` phase 并进入 aggregate review。

推荐选择 **A：关闭 P12 功能开发，进入 `P12 aggregate deepreview` 前置**。

第一性原理判断：P12 的原始目标不是“补齐所有指数基金数据”，而是让已经机器化的 ITEM_RULE 在最终 renderer/audit 路径中可观察、可验证、可审计。P12-S1 已让 renderer 生成 ITEM_RULE 决策与固定段落，并让程序审计 C2 消费同一决策验证 render/delete compliance；P12-S2 已修复局部证据边界只展示首个锚点的问题。继续把真实 tracking-error、指数编制方法或成分股抽取塞进 P12，会改变数据来源、抽取契约和计算口径，已经不是 ITEM_RULE deterministic compliance 的最小闭环。

## 2. Direct Evidence

- `docs/implementation-control.md` Startup Packet 记录当前 gate 为 `P12-S2 ITEM_RULE multi-anchor evidence boundary accepted`，Next entry point 为 `post-P12-S2 follow-up planning`。
- `docs/implementation-control.md` P12 Current Phase Notes 明确 P12 goal 是让 ITEM_RULE deterministic compliance 在 final renderer/audit path 中 observable，同时保持 Fund Capability ownership 和 deterministic MVP boundaries。
- `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md` 接受 P12-S1：renderer 从 `classified_fund_type` + `facets=()` 生成 ITEM_RULE decisions/context；确定性段落只在目标章节 body 渲染；C2 消费 renderer-produced decisions/context 并只检查匹配 `RenderedChapterBlock.body_markdown`。
- `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md` 同时裁决 tracking-error / index methodology / constituents 为 scoped residual，不阻塞 P12-S1。
- `docs/reviews/p12-s2-code-review-controller-judgment-20260522.md` 接受 P12-S2：`_item_rule_evidence_bullet()` 渲染全部去重锚点；空锚点文本保持不变；测试覆盖 concrete benchmark + R=A+B-C anchors、empty-anchor、duplicate-anchor、single-anchor/no-extra-chapter-evidence。
- `docs/reviews/p12-s2-code-review-controller-judgment-20260522.md` 明确 P12-S2 未改变 ITEM_RULE decisions/context、C2 audit、FQ5/quality gate、Service/UI/CLI、Engine/runtime、FundDocumentRepository 或 Dayu boundaries。
- `docs/design.md` 当前设计真源限定 deterministic MVP 主链路为 UI -> Service -> Fund Capability，不依赖 LLM 写作或外部 Dayu Host/Engine；`FundDocumentRepository` 是生产年报入口；ITEM_RULE 属于基金类型优先后的模板契约机制。
- `docs/repo-audit-20260521.md` 是较旧 P8 baseline 的仓库审核候选输入，当前 control doc 明确它 excluded/untracked；其建议主要为 repo hygiene / 文档结构 / 旧状态核对，不是 P12 ITEM_RULE deterministic compliance 的未闭合 product-safety blocker。
- 当前 `git log --oneline -8` 显示 P12 commits 已在当前 `main` 上；若 aggregate review 使用默认 `main` 作为 base 会得到空 diff，因此 P12 aggregate review 需要显式使用 P12 前基线 `ba77e02`。

## 3. Candidate Comparison

| Candidate | Fit to P12 goal | Product-safety value now | Scope / risk | Decision |
|---|---:|---:|---:|---|
| Close P12 and run aggregate deepreview | 高 | 高：验证 S1/S2 组合后无跨 slice 回归 | 中：需要显式 base `ba77e02`，避免 main 上空 diff | **Selected** |
| Real tracking-error extractor/calculator | 低到中 | 高，但属于新数据能力 | 高：需定义数据源、日频序列、指数净值、计算口径、schema、缓存和审计 | Defer to future extractor/calculation phase |
| Real index methodology / constituents extraction | 低到中 | 高，但属于新 documents/extractor 能力 | 高：需招募说明书/指数公告来源、表格解析、identity 校验和 fallback | Defer to future documents/extractor phase |
| Long-anchor truncation/grouping | 低 | 低：当前 fixture 和实现没有 large anchor set 问题 | 中：需 UX/Markdown contract policy | Defer to future evidence-display UX slice when real long lists appear |
| Chapter-mismatched ITEM_RULE audit noise cleanup | 低 | 低：当前 fail-closed，不隐藏问题 | 低 | Defer as maintainability cleanup |
| Future ITEM_RULE dispatch extensibility | 低 | 中，仅当新增 ITEM_RULE 时有收益 | 中：当前无新增规则需求，容易过早抽象 | Defer to future rule-addition slice |
| RR-13 duplicate `016492` | 不属于 P12 | 中 | 高：需要 user/App source truth | Keep human-owned |
| Publish/include `docs/repo-audit-20260521.md` | 不属于 P12 | 低到中 | 中：旧 baseline、当前 excluded/untracked | Keep excluded; not part of P12 |
| Repo-audit hygiene items: structure tree, reviews archive, version bump, type-ignore, magic numbers | 不属于 P12 | 低到中 | 中：repo/docs hygiene, not current product-safety blocker | Defer to future hygiene phase if controller selects it |

## 4. Recommended Next Gate

Proceed to:

```text
P12 aggregate deepreview
```

Because P12 commits are already on `main`, the aggregate review base must be explicit:

```text
base = ba77e02
review range = ba77e02..HEAD
```

Rationale for `ba77e02`: it is the accepted P11-S2 summary dedupe baseline immediately before P12 planning commits. Reviewing against current `main` would be empty because P12-S1/S2 accepted commits have already landed on `main`.

If aggregate deepreview passes, the next controller action should be:

```text
P12 aggregate deepreview acceptance / ready-to-open-draft-PR reconciliation
```

Controller must reconcile the branch reality before claiming draft-PR readiness: if P12 is already pushed to `main`, there may be no draft PR to open for these commits; the artifact should record that fact rather than invent a PR gate.

## 5. Non-goals

- Do not open another P12 implementation slice unless aggregate deepreview finds a P12 regression that must be fixed before closeout.
- Do not implement tracking-error, index methodology, constituents extraction, daily NAV/index series, or new source fallback.
- Do not introduce LLM audit, Evidence Confirm, RepairContract, Host, Engine, tool loop, prompt scene registry, or Dayu runtime.
- Do not modify Service/UI/CLI, quality gate semantics, `FundDocumentRepository`, document sources, PDF/cache helpers, or source repository internals.
- Do not resolve RR-13 duplicate `016492`.
- Do not publish, stage, or edit `docs/repo-audit-20260521.md`.
- Do not update `docs/design.md` or `docs/implementation-control.md` in this planning artifact; controller owns control-doc update after aggregate outcome.

## 6. Scope

Aggregate deepreview target:

- Full P12 diff from `ba77e02..HEAD`, including:
  - P12 planning and review artifacts;
  - `fund_agent/fund/template/item_rules.py` changes from P12-S1 if any;
  - `fund_agent/fund/template/renderer.py` ITEM_RULE decision plumbing, fixed segment rendering, and multi-anchor evidence boundary;
  - `fund_agent/fund/audit/audit_programmatic.py` C2 ITEM_RULE compliance checks;
  - `tests/fund/template/test_item_rules.py`, `tests/fund/template/test_renderer.py`, `tests/fund/audit/test_audit_programmatic.py`;
  - `fund_agent/fund/README.md` and `tests/README.md` P12 sync;
  - P12 implementation/review/controller artifacts under `docs/reviews/`.

Explicit exclusions:

- `docs/repo-audit-20260521.md` remains untracked/excluded input.
- RR-13 source data and selected-fund CSV rows remain untouched.
- Non-P12 historical cleanup and repo hygiene are out of aggregate review scope except as residual-tracking checks.

Aggregate review focus:

- Does P12 fully satisfy ITEM_RULE deterministic renderer/audit compliance without semantic overclaiming?
- Do renderer and audit consume one decision source, avoiding divergent inference?
- Are identity missing / identity present / unsupported fund-type paths fail-closed as accepted?
- Are conditional segment render/delete semantics chapter-scoped and marker-based?
- Does multi-anchor display preserve provenance without implying tracking error, index methodology, or constituents are proven?
- Are FQ5/quality gate semantics still limited to applicability metadata?
- Did any change cross into Service/UI/CLI/Engine/runtime/documents/source repository/Dayu boundaries?
- Are tests sufficient across render matrix, audit failure paths, evidence boundary paths, and docs sync?
- Are all residuals assigned to owner/destination?

## 7. Validation / Review Gates

Before or during aggregate review, controller should verify:

```bash
git diff --name-only ba77e02..HEAD
git diff --check ba77e02..HEAD
pytest tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py
pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
ruff check fund_agent/fund/template fund_agent/fund/audit tests/fund/template tests/fund/audit
pytest
```

Expected validation signals:

- Targeted template/audit suite includes P12-S1/S2 coverage and passes.
- Adjacent extraction-score / quality-gate suite passes, confirming FQ5 semantics were not expanded by renderer/audit changes.
- Full suite passes at or above current control-doc baseline `403 passed`.
- `git diff --name-only ba77e02..HEAD` confirms P12 scope and excludes `docs/repo-audit-20260521.md`.

Reviewer handoff:

- Ask at least two independent reviewers, preferably AgentMiMo and AgentGLM, to run P12 aggregate deepreview against `ba77e02..HEAD`.
- Reviewers must not re-plan P12 or propose new extractor scope as a blocker unless they identify a direct regression against P12's accepted deterministic compliance goal.
- Findings should be classified as accepted/rejected/deferred by controller. Accepted findings enter fix/re-review before P12 closeout.

Stop conditions:

- Aggregate diff unexpectedly includes `docs/repo-audit-20260521.md`, RR-13 source data, Service/UI/CLI/Engine/runtime/documents/source repository, or unrelated repo-hygiene changes.
- Reviewers find renderer/audit decision divergence, missing fail-closed behavior, audit scanning global Markdown instead of chapter body, or FQ5 overclaiming renderer compliance.
- Validation fails and failure is not clearly unrelated.
- Reviewer availability prevents two durable independent review artifacts; controller must record limitation or ask user for risk exception before proceeding.
- Branch/PR status is unclear because P12 commits are already on `main`; controller must reconcile before any ready-to-open-draft-PR claim.

## 8. Residual Tracking / Owners

| Residual | Current decision | Owner / destination |
|---|---|---|
| Real tracking-error extraction/calculation | Defer; not part of ITEM_RULE deterministic compliance | Future extractor/calculation phase in Fund Capability, likely documents/extractors + analysis contract |
| Real index methodology / constituents data | Defer; requires new source and extraction design | Future documents/extractor phase through `FundDocumentRepository` boundaries |
| Evidence sufficiency / evidence-claim matching | Defer; multi-anchor is provenance display only | Future E1/E2/E3 audit or Evidence Confirm work |
| Long-anchor truncation/grouping | Defer until real large anchor sets appear | Future evidence-display UX slice |
| Future ITEM_RULE expansion dispatch/tests | Defer until new manifest entries exist | The future slice that adds ITEM_RULEs |
| Chapter-mismatch duplicate C2 noise | Defer; current behavior fail-closed | Future maintainability cleanup if issue noise becomes material |
| RR-13 duplicate `016492` | Preserve human-owned | User / App source |
| `docs/repo-audit-20260521.md` | Keep excluded/untracked | Controller / user; future repo-hygiene phase may explicitly accept or discard |
| Repo-audit hygiene suggestions | Defer outside P12 | Future repo/docs hygiene phase, not P12 closeout blocker |

## 9. Open Questions

No blocking product or architecture questions.

Non-blocking controller questions:

- Because P12 accepted commits are already on `main`, should the next post-aggregate step be a draft-PR readiness artifact, or a main-branch closeout artifact that records no PR gate is applicable?
- Which two reviewers are available for durable aggregate artifacts? If only one independent reviewer is available, controller must record a risk exception or ask the user.

These do not block starting `P12 aggregate deepreview` because the review base and scope are explicit.

## 10. Controller Handoff

Recommended controller prompt:

```text
Gate: P12 aggregate deepreview.

Review target: full P12 diff from base `ba77e02` to current `HEAD`.

Context:
- P12-S1 accepted ITEM_RULE renderer/audit compliance.
- P12-S2 accepted multi-anchor ITEM_RULE evidence boundary.
- P12 goal is deterministic ITEM_RULE compliance in final renderer/audit path, not real tracking-error/index-methodology/constituents extraction.

Scope:
- Review `fund_agent/fund/template`, `fund_agent/fund/audit`, relevant tests, README sync, and P12 artifacts changed in `ba77e02..HEAD`.
- Confirm no Service/UI/CLI/Engine/runtime/documents/source repository/quality gate semantic drift.
- Confirm `docs/repo-audit-20260521.md` and RR-13 source data remain excluded.

Validation to record:
- `git diff --name-only ba77e02..HEAD`
- `git diff --check ba77e02..HEAD`
- `pytest tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py`
- `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py`
- `ruff check fund_agent/fund/template fund_agent/fund/audit tests/fund/template tests/fund/audit`
- `pytest`

Output:
- `docs/reviews/p12-aggregate-deepreview-<reviewer>-20260522.md`
- controller judgment artifact after reviews
```

Completion criteria for this follow-up decision:

- P12 should not open another planned product-safety slice before aggregate review.
- If aggregate review finds accepted findings, run fix/re-review within P12.
- If aggregate review passes, close P12 functional development and proceed to acceptance / ready-to-open-draft-PR reconciliation with branch-status handling.
