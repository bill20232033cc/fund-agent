# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.0
> **日期**: 2026-05-25
> **设计真源**: `docs/design.md` (v2.2)
> **规则真源**: `AGENTS.md`
> **历史快照**: `docs/archive/implementation-control-history-20260525.md`
> **当前状态**: release maintenance；report-quality baseline S1 score-schema fixture draft 已本地接受；下一入口为 S1 dry-run evidence collection

---

## Startup Packet

### Current Truth Guardrails

本节是每个总控 / 子 Agent 恢复任务时必须先读取并复述的当前执行口径。

- 当前真源只包括 `AGENTS.md`、`docs/design.md` 当前设计章节、本文档 Startup Packet 和当前 gate。
- `docs/reviews/` 与 `docs/archive/implementation-control-history-20260525.md` 只作为证据链；旧六层、Application、Runtime/Engine 表述只作为历史证据，不得作为当前架构依据。
- 当前架构按 Dayu 四层 `UI -> Service -> Host -> Agent` 设计；当前确定性生产主链路仍是 UI -> Service -> `fund_agent/fund` Agent 层基金能力的过渡实现。
- 未开独立 Host/Agent gate 前，不得创建占位 `fund_agent/host` 或 `fund_agent/agent` 包；确需 Host 时必须使用 `dayu.host`，确需 Agent 执行内核 / tool loop / runner / ToolRegistry / ToolTrace 时必须使用 `dayu.engine`。
- 后续 plan/review 必须显式检查四层边界、Dayu Host/Agent 依赖纪律、显式参数 / 禁止 `extra_payload`、`dayu-agent` pyproject 工程基线和当前 gate 非目标。

| Field | State |
|---|---|
| Branch | `codex/v0-release-readiness-plan` |
| Current phase | `release maintenance` |
| Current gate | `release-maintenance report-quality baseline S1 score-schema fixture draft accepted locally` |
| Next entry point | `report-quality-baseline S1 dry-run evidence collection` |
| Latest accepted commit | `f22f47e docs: accept report-quality s1 schema draft` |
| Design truth | `docs/design.md` (v2.2) |
| Control truth | `docs/implementation-control.md` |
| Historical control snapshot | `docs/archive/implementation-control-history-20260525.md` |
| External repo state | PR 17 squash-merged at `99df84c`; PR 15 remains open non-draft/DIRTY and needs explicit stale disposition authorization |

## Current Gate

### Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Chapter-audit report pipeline design implementation | `docs/reviews/release-maintenance-chapter-audit-report-pipeline-design-implementation-20260524.md` |
| Methodology coverage matrix plan | `docs/reviews/release-maintenance-methodology-coverage-matrix-plan-20260525.md` |
| Methodology coverage matrix implementation | `docs/reviews/release-maintenance-methodology-coverage-matrix-implementation-20260525.md` |
| Report-quality baseline / Fact-Evidence contract plan | `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-mimo-20260525.md` |
| Plan review: DS | `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-ds-20260525.md` |
| Plan controller judgment | `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-controller-judgment-20260525.md` |
| S0 corpus-selection evidence | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md` |
| S0 review: MiMo | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-mimo-20260525.md` |
| S0 review: DS | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-ds-20260525.md` |
| S0 re-review: MiMo | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-rereview-mimo-20260525.md` |
| S0 re-review: DS | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-rereview-ds-20260525.md` |
| S0 controller judgment | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-controller-judgment-20260525.md` |
| S1 score-schema fixture draft | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md` |
| S1 review: MiMo | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-review-mimo-20260525.md` |
| S1 review: DS | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-review-ds-20260525.md` |
| S1 re-review: MiMo | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-rereview-mimo-20260525.md` |
| S1 re-review: DS | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-rereview-ds-20260525.md` |
| S1 controller judgment | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-controller-judgment-20260525.md` |

### Current Decisions

- Report quality must first become observable through a small representative baseline corpus, report-quality scoring schema, and Fact/Evidence input contract.
- Data-source / extraction iteration vs template / writing iteration must be selected from scoring failure categories, not from subjective report taste.
- S0 should attempt FOF, but must not block if no repository-verified FOF annual report is available; missing FOF must be recorded as a `data_gap`.
- S0 accepted active, index, enhanced index, bond, and QDII candidates as repository evidence; FOF remains a `data_gap` because current QDII-FOF candidates classify as `qdii_fund`.
- S1 must recover the upstream failure category for fallback candidates (`110020`, `017641`, `017970`) before durable baseline selection, or exclude those candidates.
- First scoring implementation remains issue-based; `N/A` dimensions are excluded from denominators, and all-`N/A` chapters are `skipped`, not `passing`.
- S1 accepted schema uses issue-based observations, separates document identity from fund-type slot membership, requires `na_reason` for `N/A`, reserves `chapter_summary` for skipped chapter summaries, and excludes `unknown` / `probe_only` source boundaries from durable baseline selection.
- Next S1 dry-run must produce ignored `reports/scoring-runs/` output plus tracked Markdown review evidence; it must not promote JSON fixtures or start S2 code implementation.
- `fact_prefill_reviewed` uses a Markdown evidence table under `docs/reviews/` until a later curated-fixture gate accepts JSON fixtures.

### Current Non-Goals

- Do not change current v0 renderer or current 8-chapter output.
- Do not change FQ0-FQ6 quality gate behavior.
- Do not claim LLM audit / Evidence Confirm / repair loop is implemented.
- Do not create Host/Agent packages or introduce `dayu.host` / `dayu.engine` before an explicit gate.
- Do not introduce calculated index series, external index adapters beyond accepted thermometer data-source protocols, methodology extraction, constituents extraction, QDII subtype redesign, unsupported coverage targets, or quality-gate weakening.
- Do not promote local scoring, writing, or data-source run outputs into tracked fixtures without a later reviewed gate.

## Next Entry Point

`report-quality-baseline S1 dry-run evidence collection`

S1 dry-run evidence collection must apply the accepted schema to a minimal reviewed example and produce:

- ignored local run outputs under `reports/scoring-runs/s1-dry-run-20260525/`;
- a tracked Markdown review artifact under `docs/reviews/` summarizing accepted / corrected / rejected score issues;
- at least one localized score issue or pass record using the accepted schema fields;
- explicit denominator, `N/A`, `skipped`, and `chapter_summary` behavior if applicable;
- confirmation that `unknown` / `probe_only` source boundaries and `unknown_upstream_failure_category` records are excluded from durable baseline selection.

Stop before durable baseline selection and before S2 code work if dry-run issue localization is weak, source category recovery is unresolved, FOF remains unrepresented, or fact-prefill review evidence is insufficient.

## Open Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| S0 corpus transition triggers | Completed in S0 | S0 defined trigger, actor, and minimum evidence for `candidate -> repository_verified -> fact_prefill_generated -> fact_prefill_reviewed -> scoring_ready -> accepted_baseline` |
| FOF corpus coverage | S1 / fund-type taxonomy gate | S0 recorded QDII-FOF as `data_gap`; second pass must find pure `fof_fund` or open QDII-FOF taxonomy / precedence design |
| Fallback upstream failure category | S1 entry gate / source reliability evidence | Recover original upstream failure category for `110020`, `017641`, and `017970`, or exclude the fallback candidate before durable baseline selection |
| S1 score schema details | Completed in S1 schema draft | `source_boundary`, issue-based output, `N/A` denominator semantics, `chapter_summary`, terminal states, and score issue localization are accepted as draft schema |
| S1 dry-run evidence | S1 dry-run evidence collection | Produce ignored scoring-run output plus tracked Markdown review evidence; do not promote fixtures |
| Fact/Evidence contract shape | S2 bundle candidate | Decide `ReportEvidenceBundle` relation to current `StructuredFundDataBundle`; avoid parallel extraction paths unless explicitly justified |
| Anchor naming and review status derivation | S1 / S2 | Normalize anchor id naming; define bundle-level status derivation from contained facts, anchors, calculations, and gaps |
| Document identity vs fund-type slot membership | Completed in S1 schema draft | S1 split document verification from type-slot membership so `verified_as_annual_report_but_type_gap` cannot become scoring-ready FOF evidence |
| Review-state terminal states | Completed in S1 schema draft / future implementation validation | S1 defined rejected / deferred / expired semantics; S2 or later implementation must add executable value-domain validation if schema becomes code |
| `fq_gate_status` citation | S1 / S2 | Cite existing quality gate final judgment contract semantics for `pass`, `warn`, `block`, `not_run` |
| PR 15 stale disposition | User authorization only | Do not close/comment/mutate GitHub state without explicit authorization |
| Host/Agent boundary debt | Future explicit Host/Agent gate | Host must use `dayu.host`; Agent execution must use `dayu.engine`; no placeholder packages |

## Active Gate Ledger

| Gate | Status | Artifact | Validation / judgment | Residual owner | Next action |
|---|---|---|---|---|---|
| `release-maintenance chapter-audit report pipeline design implementation` | accepted locally | `docs/reviews/release-maintenance-chapter-audit-report-pipeline-design-implementation-20260524.md` | Design promotes measurable report-quality baseline before data-script or template iteration; no source/test/runtime changes | concrete corpus/schema/mapping decisions | report-quality baseline / Fact-Evidence plan |
| `release-maintenance methodology coverage matrix design` | accepted locally | `docs/reviews/release-maintenance-methodology-coverage-matrix-plan-20260525.md`, `docs/reviews/release-maintenance-methodology-coverage-matrix-implementation-20260525.md` | `docs/design.md` §5.4.3 adds Morningstar x 有知有行 x fund type x CHAPTER_CONTRACT matrix; validation `rg` and `git diff --check` passed | concrete scoring schema and baseline corpus | report-quality baseline / Fact-Evidence plan |
| `release-maintenance report-quality baseline / Fact-Evidence contract plan/review` | accepted locally | `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-controller-judgment-20260525.md` | AgentCodex plan; AgentMiMo and AgentDS `PASS_WITH_FINDINGS`; controller accepted S0/S1/S2 sequence and resolved open questions | S0/S1/S2 details above | `report-quality-baseline S0 corpus-selection evidence` |
| `report-quality-baseline S0 corpus-selection evidence` | accepted locally | `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-controller-judgment-20260525.md` | AgentCodex evidence; AgentMiMo and AgentDS `PASS_WITH_FINDINGS`; review fix completed; both re-reviews `PASS`; commit `c73e594` | S1 fallback category, FOF data_gap, score schema details | `report-quality-baseline S1 score-schema fixture draft` |
| `report-quality-baseline S1 score-schema fixture draft` | accepted locally | `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-controller-judgment-20260525.md` | AgentCodex draft; AgentMiMo and AgentDS `PASS_WITH_FINDINGS`; review fix completed; both re-reviews `PASS`; commit `f22f47e` | S1 dry-run evidence, fallback source category, FOF data_gap, future value-domain validation | `report-quality-baseline S1 dry-run evidence collection` |

## Historical Evidence Index

The detailed pre-split control record is preserved verbatim at:

- `docs/archive/implementation-control-history-20260525.md`

Use that archive only for evidence reconstruction. It is not current gate truth and must not override this Startup Packet or `docs/design.md` current design sections.

Historical material retained there includes:

- P0-P19 phase definitions, detailed gate logs, PR/commit records, validation counts, and residual histories.
- Superseded six-layer / Application / Runtime/Engine wording.
- Long-form release-maintenance PR 16 / PR 17 / 004393 quality gate / P19 thermometer records.
- Original detailed control record and status update log.

## Design / Control Alignment Rules

1. `AGENTS.md` is the highest-priority execution rule source.
2. `docs/design.md` remains the design truth for architecture, boundaries, current product behavior, Dayu non-dependency, `FundDocumentRepository` source boundaries, report-quality design, and thermometer design.
3. `docs/implementation-control.md` remains the control truth for current phase, current gate, accepted artifacts, residual owners, and next entry point.
4. Historical archive entries are evidence only. If archive content contradicts Startup Packet or `docs/design.md`, treat the archive content as superseded unless a new controller judgment says otherwise.
5. Any future control-doc update should prefer a new `docs/reviews/` artifact plus a short control-doc reference over appending long logs.

## Resume Checklist

When resuming:

1. Read `AGENTS.md`.
2. Read `docs/design.md` current relevant sections.
3. Read this Startup Packet.
4. Confirm `Current phase`, `Current gate`, and `Next entry point`.
5. Confirm the next action is controller work or specialist work.
6. If specialist work is required, delegate through the current gate handoff; do not write the specialist plan directly unless explicitly authorized.
7. Preserve deterministic MVP boundaries and do not introduce Host/Agent/runtime work outside an explicit gate.
