# Release Maintenance Phase Roadmap Consolidation Implementation Review — AgentDS

日期：2026-05-29

审查者：AgentDS，独立 implementation reviewer。未启动 `/gateflow`，未实现代码，未修改生产代码，未修改被审查 artifact，未 commit/push/PR/merge/release/promote。

## Review Scope

审查目标（三个已变更文件）：

- `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`（新增 roadmap artifact）
- `docs/reviews/release-maintenance-phase-roadmap-consolidation-implementation-evidence-20260529.md`（新增实现证据）
- `docs/implementation-control.md`（最小更新前部控制面）

审查依据：

- Accepted plan: `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`
- Plan reviews: MiMo `PASS with findings (non-blocking)` + DS `PASS`
- Implementation evidence: `docs/reviews/release-maintenance-phase-roadmap-consolidation-implementation-evidence-20260529.md`
- Truth sources: `AGENTS.md`, `docs/design.md`, both JSON manifests, all referenced controller judgments

## Validation Evidence

### V1: git diff --check

```bash
git diff --check -- docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md \
  docs/reviews/release-maintenance-phase-roadmap-consolidation-implementation-evidence-20260529.md \
  docs/implementation-control.md
```

结果：无输出，通过（无空白/格式错误）。

### V2: Forbidden path diff

```bash
git diff -- reports/golden-answers \
  docs/reviews/fixture-promotion-state-manifest-20260529.json \
  docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json \
  fund_agent tests scripts pyproject.toml uv.lock
```

结果：无输出，确认所有禁止路径（生产代码、测试、runtime、manifest、reports）无 diff。

### V3: 变更范围确认

`git diff --stat` 只输出 `docs/implementation-control.md`（24 insertions, 26 deletions）。Roadmap 和 implementation evidence 为新增 untracked 文件，不在 tracked diff 中。无意外变更。

### V4: JSON manifest 有效性

两个 manifest JSON 均通过 `python -m json.tool` 校验。

## Focus Area Findings

### F1: Five Route Taxonomy Correctness

**Verdict: PASS**

Roadmap artifact 严格按 plan 定义的五条路线组织（§Route Taxonomy, plan lines 108-201）：

| Route | Roadmap Section | 与 Plan 一致 |
|---|---|---|
| Route 1: Minimum Golden V1 Readiness | Lines 56-67 | ✅ |
| Route 2: Deferred Coverage | Lines 69-77 | ✅ |
| Route 3: Source / Provenance Hardening | Lines 79-99 | ✅ |
| Route 4: Future Host / Agent / Dayu Architecture | Lines 101-118 | ✅ |
| Route 5: Artifact / Manifest Lifecycle | Lines 120-128 | ✅ |

无跨路线污染。每条路线的内容与 truth sources 一致。

### F2: 006597 Bond Blocker Closed But Not Promotion-Ready

**Verdict: PASS**

Roadmap 在三处正确处理了 006597 的双重状态：

1. Solved Blockers 表（roadmap line 39）：`bond_risk_evidence_missing / drawdown_stress` → `Closed as resolved context`，引用 drawdown controller judgment。
2. Remaining Minimum V1 Blockers（roadmap lines 49-50）：`bond blocker is closed, but strict correctness and fixture candidacy are unresolved`，明确区分 closed vs unresolved。
3. Route 1 006597 entry（roadmap line 64）：`if controller accepts the untracked follow-up evidence, run a same-fund unavailable field review gate; if not, rerun strict correctness`，不声称 promotion-ready。

Residual table 006597 row（line 143）：`blocks_minimum_v1=true, blocks_full_v1=true`，`current_state` 明确包含 `Untracked follow-up evidence says rerun hit same-fund unavailable stop condition but remains unaccepted`。

全链路无 `promotion_allowed=true` 或 "ready" 表述。

### F3: Next Entry Split 004393 / 004194 / 006597

**Verdict: PASS**

旧泛化标签 `004393 / 004194 / 006597 strict correctness follow-up gate` 已被完全替换：

- Roadmap Recommended Next Entry（lines 185-194）：按基金拆分为 5 步独立 gate，006597 路径根据 controller 是否接受 untracked evidence 分叉。
- Implementation-control header（line 9）：`下一入口按 fund 拆分为 004393 partial coverage decision、004194 P0 coverage 或 index_profile-only fixture decision、006597 same-fund unavailable field review 或 strict correctness rerun`。
- Startup Packet Next entry point（line 32）：同上拆分。
- Next Entry Point 章节（line 126）：独立声明，含 006597 分叉条件。
- Allowed scope（lines 132-134）：三个 fund 各有独立 bullet 描述 scope。

Untracked follow-up evidence 被显式标注为 `unaccepted/untracked workspace evidence`（roadmap line 33, implementation-control header line 9, control doc line 122），未 stage、未作为 controller truth。

**Plan review finding resolution**：
- MiMo Finding 1（Medium, next gate order 未反映 006597 follow-up 已 blocked）：Roadmap line 33 明确承认 `006597 rerun triggered the same-fund unavailable field review stop condition`。Residual table line 143 记录 `Untracked follow-up evidence says rerun hit same-fund unavailable stop condition`。已解决。
- MiMo Finding 2（Low, control-doc 应引用更新后 gate state）：Implementation-control line 32 的 next entry point 已拆分为三个独立 fund gate。已解决。

### F4: QDII / FOF / 110020 / 017641 Deferred Status

**Verdict: PASS**

Roadmap Route 2（lines 72-77）四项 deferred items：

| Item | Roadmap Claim | blocks_minimum_v1 | blocks_full_v1 | 与 Manifest 一致 |
|---|---|---|---|---|
| QDII candidates (4 funds) | deferred, blocks full v1 | false | true | ✅ |
| 017641 | replacement, quality block, deferred | false | true | ✅ |
| FOF_SLOT | taxonomy/data gap, deferred | false | true | ✅ |
| 110020 | reviewed candidate only, deferred | false | true | ✅ |

Residual table 对应行（lines 146-148）全部 `blocks_minimum_v1=false, blocks_full_v1=true`。

Roadmap lines 77-78 保留手动 coverage policy / fact-freeze gate 要求：`These rows require manual coverage policy or fact-freeze gates before implementation work.` 与 QDII probing stopped 裁决一致。

### F5: Route 3 Explicit blocks_minimum_v1 / blocks_full_v1

**Verdict: PASS**

Plan review DS O2（LOW）要求 Route 3 每个 residual 都有显式 blocks 赋值。Residual table lines 150-155 中六个 Route 3 项：

| Item | blocks_minimum_v1 | blocks_full_v1 |
|---|---|---|
| source_query_params split | false | false |
| CSRC EID source generalization | false | true |
| Parser/schema drift and duplicate-date detection | false | true |
| Endpoint caching/SLA | false | true |
| Strict bool parsing for source metadata | false | false |
| Multi-anchor snapshot projection | false | false |

全部显式标注，无 "generally" 集合表述。**DS O2 已落实。**

### F6: Facet Inference / ITEM_RULE Routing Design Residual

**Verdict: PASS**

Roadmap Route 4 lines 110-118 包含完整的 facet inference residual：

- fund_type vs facet 边界：`fund_type is the coarse standard type used by preferred_lens and ITEM_RULE; facets are narrower evidence-based traits and must not be inferred by LLM guessing`（line 112）。与 `AGENTS.md` evidence 要求（line 87）和 `design.md` 确定性原则一致。
- Candidate facets 枚举：Bond（short-duration, credit-rating 等）、Index（ETF-linked 等）、QDII（QDII-FOF, FX 等）、FOF（pure FOF, holding look-through）。使用 "candidate" 措辞，不声称已接受 taxonomy。**DS O1 已妥善处理。**
- 确定性推断：`must be deterministic and evidence-based, consuming structured annual-report/source facts and exposing missing/ambiguous states`（line 114）。
- Routing 影响：`ITEM_RULE, must_answer, must_not_cover, preferred_lens, evidence requirements and deletion/render decisions`（line 115）。
- Ownership：`Agent/Fund, because fund_agent/fund owns fund type, CHAPTER_CONTRACT, ITEM_RULE, preferred_lens and evidence audit`（line 116）。与 `AGENTS.md` 归属规则（lines 137-138）一致。
- 不实现：`No facet inference implementation is authorized in this gate`（line 118）。

### F7: Implementation-Control Update Is Minimal and Compressed

**Verdict: PASS**

`git diff --stat` 显示 24 insertions / 26 deletions，净减少 2 行。

变更仅限前部控制面：

| 区域 | 变更 |
|---|---|
| 版本/日期/当前状态 header | v2.1→v2.2，日期 05-27→05-29，状态更新为 roadmap consolidation |
| Startup Packet 表 | Current gate、Next entry point、Latest checkpoint 更新 |
| Current Roadmap Pointer（新增） | 指向 roadmap 和 implementation evidence |
| Accepted Artifacts 表 | 新增 2 行（plan + plan reviews） |
| Current Decision Summary | 新增 1 条 roadmap consolidation bullet |
| Next Entry Point | 从旧泛化标签拆分为三 fund 独立 gate |
| Allowed Scope | 从组合 bullet 拆分为三 fund 独立 bullet |
| Open Residuals | 从 15 行详细 residual 压缩为 5 行 route-based summary |

**未修改区域**：Historical Evidence Index、Design/Control Alignment Rules、Resume Checklist、Recent Active Gate Ledger 表内容均未变更。Open Residuals 压缩后的细节已完整迁移至 roadmap artifact 的 20 行 residual table。

删除的 `Revalidate 006597 preflight` bullet 是正确的：bond blocker 已 closed，revalidation 逻辑已包含在 006597 独立 gate 中而非通用前置步骤。

### F8: Non-Mutation Compliance

**Verdict: PASS**

| 禁止变更类别 | 验证 |
|---|---|
| 生产代码、测试、runtime、score、quality gate、snapshot、renderer、Service/UI、Host/Agent/dayu | `git diff` 无输出 ✅ |
| golden answers、golden fixtures | `git diff` 无输出 ✅ |
| JSON manifests、reports | `git diff` 无输出 ✅ |
| `pyproject.toml`、`uv.lock`、scripts | `git diff` 无输出 ✅ |
| `promotion_allowed=true` | 全链路未出现 ✅ |
| PR、push、merge、release | git status 无相关操作 ✅ |

## Additional Observations

### O1 (INFO): Strict Correctness Follow-up Artifacts Remain Untracked

Workspace 中存在 8 个 untracked strict correctness follow-up artifacts（plan/evidence/reviews/decision），已在 roadmap line 33 和 control doc line 122 中被正确标注为 unaccepted/untracked workspace evidence。这些文件仍然是 untracked（git status 显示 `??`），未被 stage。

如果 controller 接受这些 evidence，006597 下一步为 same-fund unavailable field review；如果不接受，则需要 rerun strict correctness。两种路径在 roadmap 和 control doc 中均有明确记录。

### O2 (INFO): Ruff / Pytest Skipped with Reason

Implementation evidence line 39 明确声明 skip ruff/pytest 的原因：本 gate 只改 Markdown/control-plane 文档，未触碰 Python、测试、runtime、manifest schema 等。这与 plan 的 Validation Matrix（plan lines 295-297）一致。

## Verdict

**PASS — 无阻塞发现。**

三个审查目标文件均符合 accepted plan 的全部要求：

- 五条路线分类正确，与所有 truth sources 一致。
- 006597 bond blocker closed / not promotion-ready 双重状态在所有位置精确一致。
- 004393 / 004194 / 006597 下一步已按基金拆分，untracked follow-up evidence 被正确标注为 unaccepted workspace evidence。
- QDII / FOF / 110020 / 017641 全部 `blocks_minimum_v1=false, blocks_full_v1=true`，无误报 ready。
- Route 3 每个 residual 都有显式 `blocks_minimum_v1` 和 `blocks_full_v1`。
- Facet inference / ITEM_RULE routing residual 完整呈现，ownership 归属 Agent/Fund，明确不在此 gate 实现。
- Implementation-control 更新为净减少 2 行的压缩更新，仅触及前部控制面，Open Residuals 从 15 行压缩为 5 行 route-based summary。
- Plan review 两个 findings（MiMo F1/F2）和两个 observations（DS O1/O2）均已妥善处理。
- 无生产代码、golden、manifest、runtime、promotion 变更。
- git diff --check 通过，禁止路径 diff 为空，JSON manifest 有效。

## Self-Check

- 审查依据：accepted plan、两份 plan review、implementation evidence、roadmap artifact、implementation-control diff、两个 JSON manifest、`AGENTS.md`、`docs/design.md`。
- 每条 finding 标注了具体文件位置和行号。
- 未修改任何文件（除本 review artifact）。
- 未启动 `/gateflow`，未实现代码，未 commit/push/PR。
- 审查结论：PASS，handoff-ready for controller acceptance。

Self-check: pass.
