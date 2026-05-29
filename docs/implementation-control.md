# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.3
> **日期**: 2026-05-30
> **规则真源**: `AGENTS.md`
> **设计真源**: `docs/design.md`
> **控制真源**: `docs/implementation-control.md`
> **短启动入口**: `docs/current-startup-packet.md`
> **当前状态**: MVP fund analysis report generation phase；当前 gate 为 `MVP truth pivot and context compaction gate`；下一入口为 `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`。

---

## Startup Packet

本文件只保留当前控制面。详细恢复入口见 `docs/current-startup-packet.md`；历史 release-maintenance 长账本只作为证据链，不再作为当前 phase 或 next entry。

### Current Truth Guardrails

- `AGENTS.md` 是最高优先级执行规则真源；若与本文档或 `docs/design.md` 冲突，先调整方案/实现，再回写文档。
- 当前 phase 是 `MVP fund analysis report generation phase`；当前 gate 是 `MVP truth pivot and context compaction gate`，分类为 `heavy`。
- 当前实现仍是确定性 `fund-analysis analyze/checklist`：结构化抽取、确定性分析、模板渲染、程序审计和 FQ0-FQ6 quality gate。
- 当前生产路径仍是 UI -> Service -> `fund_agent/fund` 的过渡路径；尚未接入 Host/Agent 调度。
- Route C 是已接受的未来设计，不是当前实现；不得把 LLM chapter writer、LLM audit、chapter orchestrator、repair loop、`--use-llm`、Host scheduling、Agent runner/tool loop 或 dayu runtime 写成已实现事实。
- 目标架构保持 UI -> Service -> Host -> Agent。未来 Host 必须使用 `dayu.host`；未来 Agent engine/tool loop/runner/ToolRegistry/ToolTrace 必须使用 `dayu.engine`。
- Service 可以组装业务用例、prompt/ExecutionContract 语义、报告生成策略和未来 write-audit-repair loop；Fund 作为 Agent 层基金领域能力包，拥有基金类型识别、CHAPTER_CONTRACT / preferred_lens / ITEM_RULE、事实抽取、审计规则和证据锚点语义。
- 所有业务参数必须在 typed request / contract / config 中显式声明；禁止通过 `extra_payload` 传递显式参数。
- 生产年报访问必须通过 `FundDocumentRepository`；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。
- 年报来源 fallback 继续按 `not_found` / `unavailable` eligible，`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed。
- 本 gate 不改变 runtime、schema、score、snapshot、quality gate、golden fixture、golden answer、manifest、promotion state、模板或 `AGENTS.md`。

| Field | State |
|---|---|
| Branch baseline | `codex/local-reconciliation` |
| Current phase | `MVP fund analysis report generation phase` |
| Current gate | `MVP truth pivot and context compaction gate` |
| Current gate classification | `heavy` |
| Next entry point | `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate` |
| Next gate classification | `heavy` by default until controller reclassifies; Gate 1 defines Service <-> Agent/Fund contracts |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Short startup entry | `docs/current-startup-packet.md` |
| Accepted plan commit | `70184d3` |

## Current Gate

### Gate Objective

Pivot the active repository truth surface away from release-maintenance / golden-promotion blockers and back to the MVP fund analysis report generation mainline, without changing code behavior or promotion state.

### Current Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Source-of-truth plan | `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md` |
| Independent plan reviews | `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-glm-20260530.md` |
| Implementation evidence | `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` |
| Prior release-maintenance roadmap summary | `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` |
| Prior overnight closeout summary | `docs/reviews/overnight-release-maintenance-closeout-20260529.md` |
| Historical control snapshots | `docs/archive/implementation-control-history-20260525.md`; `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` |

The Current Accepted Artifacts table is intentionally short. Older release-maintenance artifacts remain available through the historical index and review artifacts, but are not active gate truth for this MVP phase.

### Current Decision Summary

- Route C is the accepted future route for MVP LLM report generation.
- Current deterministic `fund-analysis analyze/checklist` remains the only implemented report/checklist mainline.
- Next implementation work is Gate 1: define and implement the `facet_recognizer` plus `ChapterFactProvider` / `FundToolService` contract surface.
- Gate 1 component names are future Route C candidate names; they are not current code types unless Gate 1 later implements them.
- Golden / strict correctness / QDII / FOF / `110020` / fixture promotion blockers are residual product-quality work, not blockers for starting MVP report generation Gate 1.
- Host/Agent/dayu runtime integration is deferred to Route C Gate 5 and must not be preintroduced in Gates 1-4.

## Route C Future Route

| Gate | Future scope | Boundary |
|---|---|---|
| MVP Gate 1 | `facet_recognizer` + `ChapterFactProvider` / `FundToolService` contract and implementation | Agent/Fund owns fund-type/facet/fact/evidence semantics; Service owns typed invocation |
| MVP Gate 2 | `chapter_writer` + `chapter_auditor` | LLM writing/audit consumes structured facts, derived calculations, explicit data gaps and evidence anchors only |
| MVP Gate 3 | `chapter_orchestrator` | Service owns write-audit-repair policy; calls Agent/Fund capabilities through explicit contracts |
| MVP Gate 4 | `final_chapter_assembler`, chapter 0 assembly, CLI `--use-llm` | Opt-in LLM path; deterministic `analyze/checklist` remains available unless a later gate changes it |
| MVP Gate 5 | Optional dayu Host/Agent integration | Future Host uses `dayu.host`; future Agent engine/tool loop uses `dayu.engine` |

## Open Residuals

| Residual | Current disposition | Owner / next gate |
|---|---|---|
| Golden / strict correctness / fixture promotion | Residual only for MVP report generation; no promotion allowed without a separate accepted future gate | Future strict golden / fixture promotion gate |
| `004393` / `004194` / `006597` promotion readiness | `004393`, `004194`, `006597` are not promotion-prep-ready; `fixture_state=absent`; `promotion_allowed=false` | Future promotion-prep readiness owner |
| QDII / FOF / `110020` / `017641` coverage | Deferred from minimum v1 and not ready for full v1; not blockers for MVP Route C Gate 1 | Future QDII / FOF / index evidence policy gates |
| Release-maintenance long ledger | Preserved by archive and review links only; not active startup surface | Historical Evidence Index |
| Host/Agent/dayu runtime integration | Deferred to Route C Gate 5; no Host/Agent packages or dependencies before explicit gate | Future architecture gate |
| Current deterministic renderer quality | Remains current production behavior until `--use-llm` is explicitly implemented | Route C Gates 2-4 |
| Untracked unrelated workspace files | Not part of accepted evidence unless a later controller gate explicitly accepts them | Controller scope audit |

## Recent Active Gate Ledger

| Gate | Status | Summary | Next action |
|---|---|---|---|
| `MVP truth pivot and context compaction gate` | implemented docs-only / awaiting review | Control truth pivots to MVP report generation; Route C future route recorded; deterministic current implementation preserved; docs-only validation recorded | Stop after evidence and report; no push/PR/promotion; local gateflow checkpoint commit allowed after controller acceptance |
| `release-maintenance consolidation + overnight closeout` | accepted locally as historical evidence | All `promotion_allowed=false`; `004393` / `004194` / `006597` not promotion-prep-ready with `fixture_state=absent`; QDII / FOF / `110020` deferred; Host/Agent/dayu deferred; no score/quality/FQ0-FQ6/golden fixture/golden-answer/manifest/runtime promotion changes | Use Historical Evidence Index only; do not treat as current phase |

## Historical Evidence Index

Detailed historical control state is preserved outside the active startup surface:

- `docs/archive/implementation-control-history-20260525.md`
- `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
- `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`
- `docs/reviews/overnight-release-maintenance-closeout-20260529.md`

Use these files only to reconstruct evidence. They must not override this Startup Packet, the Current Gate table, or `docs/design.md` current implementation sections.

## Design / Control Alignment Rules

1. `AGENTS.md` remains the highest-priority execution rule source.
2. `docs/design.md` remains the design truth for current architecture, boundaries, current product behavior, accepted future Route C, Dayu discipline, `FundDocumentRepository` source boundary, report-quality design and thermometer design.
3. `docs/implementation-control.md` remains the control truth for current phase, current gate, accepted artifacts, residual owners and next entry point.
4. `docs/current-startup-packet.md` is the short resume entry for later phaseflow work; it must mirror this control surface, not replace it.
5. Historical archive/review entries are evidence only. If archive content contradicts Startup Packet or `docs/design.md`, treat archive content as superseded unless a later controller judgment says otherwise.
6. Future updates should prefer a new `docs/reviews/` artifact plus a short control-doc reference over appending long logs.

## Resume Checklist

1. Read `AGENTS.md`.
2. Read `docs/current-startup-packet.md`.
3. Read `docs/design.md` current implementation and Route C future design sections.
4. Confirm current phase, current gate and next entry in this file.
5. Confirm role: controller or specialist.
6. Confirm allowed files and non-goals before edits.
7. Classify the next gate per `AGENTS.md`; default heavier when uncertain.
8. Preserve deterministic MVP boundaries and do not introduce runtime, golden, promotion, Host/Agent/dayu or template changes outside an explicit accepted gate.
