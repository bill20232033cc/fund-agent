# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.0
> **日期**: 2026-05-25
> **设计真源**: `docs/design.md` (v2.2)
> **规则真源**: `AGENTS.md`
> **历史快照**: `docs/archive/implementation-control-history-20260525.md`
> **当前状态**: release maintenance；report-quality validator dry-run evidence plan 已本地接受；下一入口为 report-quality validator dry-run evidence implementation

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
| Current gate | `release-maintenance report-quality validator dry-run evidence plan accepted locally` |
| Next entry point | `report-quality validator dry-run evidence implementation` |
| Latest accepted commit | `7990b8f docs: accept report quality validator dry-run plan` |
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
| S1 dry-run evidence | `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md` |
| S1 dry-run review: MiMo | `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-review-mimo-20260525.md` |
| S1 dry-run review: DS | `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-review-ds-20260525.md` |
| S1 dry-run controller judgment | `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-controller-judgment-20260525.md` |
| S2 bundle candidate plan | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md` |
| S2 plan review: MiMo | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-review-mimo-20260525.md` |
| S2 plan review: DS | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-review-ds-20260525.md` |
| S2 plan re-review: MiMo | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-rereview-mimo-20260525.md` |
| S2 plan re-review: DS | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-rereview-ds-20260525.md` |
| S2 plan controller judgment | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-controller-judgment-20260525.md` |
| ReportEvidenceBundle implementation plan | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md` |
| Implementation plan review: MiMo | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-review-mimo-20260525.md` |
| Implementation plan review: DS | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-review-ds-20260525.md` |
| Implementation plan re-review: MiMo | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-rereview-mimo-20260525.md` |
| Implementation plan re-review: DS | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-rereview-ds-20260525.md` |
| Implementation plan controller judgment | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-controller-judgment-20260525.md` |
| ReportEvidenceBundle implementation review: MiMo | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-mimo-20260525.md` |
| ReportEvidenceBundle implementation review: GLM | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-glm-20260525.md` |
| ReportEvidenceBundle implementation re-review: MiMo | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-rereview-mimo-20260525.md` |
| ReportEvidenceBundle implementation re-review: GLM | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-rereview-glm-20260525.md` |
| ReportEvidenceBundle implementation controller judgment | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-controller-judgment-20260525.md` |
| Report-quality scoring JSONL content validation plan | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md` |
| Report-quality validation plan review: MiMo | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-mimo-20260525.md` |
| Report-quality validation plan review: GLM | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-glm-20260525.md` |
| Report-quality validation plan re-review: MiMo | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-rereview-mimo-20260525.md` |
| Report-quality validation plan re-review: GLM | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-rereview-glm-20260525.md` |
| Report-quality validation plan controller judgment | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-controller-judgment-20260525.md` |
| Report-quality validation implementation review: MiMo | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-mimo-20260525.md` |
| Report-quality validation implementation review: GLM | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-glm-20260525.md` |
| Report-quality validation implementation re-review: MiMo | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-rereview-mimo-20260525.md` |
| Report-quality validation implementation re-review: GLM | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-rereview-glm-20260525.md` |
| Report-quality validation implementation controller judgment | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md` |
| Report-quality validator dry-run evidence plan | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md` |
| Report-quality validator dry-run plan review: MiMo | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-review-mimo-20260525.md` |
| Report-quality validator dry-run plan review: GLM | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-review-glm-20260525.md` |
| Report-quality validator dry-run plan re-review: MiMo | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-rereview-mimo-20260525.md` |
| Report-quality validator dry-run plan re-review: GLM | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-rereview-glm-20260525.md` |
| Report-quality validator dry-run plan controller judgment | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-controller-judgment-20260525.md` |

### Current Decisions

- Report quality must first become observable through a small representative baseline corpus, report-quality scoring schema, and Fact/Evidence input contract.
- Data-source / extraction iteration vs template / writing iteration must be selected from scoring failure categories, not from subjective report taste.
- S0 should attempt FOF, but must not block if no repository-verified FOF annual report is available; missing FOF must be recorded as a `data_gap`.
- S0 accepted active, index, enhanced index, bond, and QDII candidates as repository evidence; FOF remains a `data_gap` because current QDII-FOF candidates classify as `qdii_fund`.
- S1 must recover the upstream failure category for fallback candidates (`110020`, `017641`, `017970`) before durable baseline selection, or exclude those candidates.
- First scoring implementation remains issue-based; `N/A` dimensions are excluded from denominators, and all-`N/A` chapters are `skipped`, not `passing`.
- S1 accepted schema uses issue-based observations, separates document identity from fund-type slot membership, requires `na_reason` for `N/A`, reserves `chapter_summary` for skipped chapter summaries, and excludes `unknown` / `probe_only` source boundaries from durable baseline selection.
- S1 dry-run accepted one narrow pass and one material localized issue from `004393` / 2024 / `chapter_3`; it proves minimal issue localization only, not durable baseline readiness.
- S1 dry-run outputs under `reports/scoring-runs/s1-dry-run-20260525/` are ignored scratch evidence; no JSON fixture or durable baseline was promoted.
- The turnover-rate gap's immediate next action is `chapter_contract` first: require explicit gap wording and prohibit unsupported stability inference; choose `data_extraction` later only if an accepted chapter contract requires turnover / style-change evidence for the claim.
- S2 accepted `ReportEvidenceBundle` as a projection wrapper over `StructuredFundDataBundle`; it must not replace the extraction bundle or create a parallel extraction path.
- S2 accepted directly implementable contract decisions for `classified_fund_type`, `preferred_lens`, `corpus_id`, source boundaries, review-status progression / priority, anchor ids, `data_gap_refs`, score issue ids, and negative validation cases.
- S2 excludes `nav_data` from the initial facts projection because `NavDataResult` is not an `ExtractedField`; a later `nav_data` source-contract slice must define a safe mapping before projecting it as report facts.
- S2 accepted the active-fund Chapter 3 turnover stability wording constraint: stability / style-consistency claims require reviewed turnover or style-change evidence, otherwise the report must state insufficiency and next minimum validation question.
- Implementation plan accepted the first code slice as `fund_agent/fund/report_evidence.py`, `tests/fund/test_report_evidence.py`, and minimal `fund_agent/fund/README.md` sync if source changes require it.
- First code slice must use frozen slotted dataclasses, explicit Literal domains, explicit `ReportEvidenceProjectionContext`, deterministic ids, projection from `StructuredFundDataBundle`, preferred-lens projection, validation helpers, and derived review status.
- First code slice must exclude `nav_data` facts, broad derived calculation population, renderer/FQ0-FQ6 changes, fixture promotion, durable baseline selection, Host/Agent runtime, and Dayu runtime.
- `fact_prefill_reviewed` uses a Markdown evidence table under `docs/reviews/` until a later curated-fixture gate accepts JSON fixtures.
- ReportEvidenceBundle implementation accepted commit `209cc25` adds typed model/projection, focused tests, README sync, implementation reviews, re-reviews, and controller judgment.
- Implementation review accepted GLM F1 after fix: duplicate `classified_fund_type` gaps now merge duplicate references so the final missing-type gap preserves `related_fact_id="fact:fund_type.classified_fund_type"` and the classified fact references that gap.
- Implementation review residuals are non-blocking: projection-context guard tests, review-status fallback-state tests, unknown extraction-mode fallback test, and turnover-rate override path asymmetry documentation can be handled in later robustness/scoring-validation work.
- Report-quality scoring JSONL content validation plan accepted commit `e40a394` defines a pure Fund capability validator over `ReportEvidenceBundle` / JSONL serialization, keeps FQ0-FQ6 unchanged, and excludes renderer, Service, CLI, Host/Agent, Dayu, `nav_data`, durable baseline, and fixtures.
- The validation plan requires canonical `scoring_ready` precondition handling, `ReportSourceDocument` fallback consistency, `N/A` and `chapter_summary` semantics, enum-domain checks, id-reference checks, and fact/gap/issue/anchor link integrity.
- Report-quality scoring JSONL content validation implementation accepted commit `9f9bbf5` adds `fund_agent/fund/report_quality_validation.py`, focused tests, README sync, implementation reviews, re-reviews, and controller judgment.
- Implementation review fixes aligned blocking data-gap semantics with `report_evidence.py`, removed duplicate `chapter_summary/report_level` emission, and collapsed fallback / fail-closed cascading issue output.
- Report-quality validator dry-run evidence plan accepted commit `7990b8f` defines a single-bundle, synthetic, non-fixture dry-run evidence slice for proving validator consumer-contract behavior before any Service/CLI/renderer/FQ0-FQ6 or durable baseline integration.
- The dry-run plan requires explicit `bundle_record_count == 1`, representative issues for fallback conflict, fail-closed source, `chapter_summary`, `N/A`, forward ref, backlink completeness, and `scoring_ready` precondition, plus boundary checks proving no product-flow integration.

### Current Non-Goals

- Do not change current v0 renderer or current 8-chapter output.
- Do not change FQ0-FQ6 quality gate behavior.
- Do not claim LLM audit / Evidence Confirm / repair loop is implemented.
- Do not create Host/Agent packages or introduce `dayu.host` / `dayu.engine` before an explicit gate.
- Do not introduce calculated index series, external index adapters beyond accepted thermometer data-source protocols, methodology extraction, constituents extraction, QDII subtype redesign, unsupported coverage targets, or quality-gate weakening.
- Do not promote local scoring, writing, or data-source run outputs into tracked fixtures without a later reviewed gate.

## Next Entry Point

`report-quality validator dry-run evidence implementation`

The next gate may implement only the accepted dry-run evidence slice from `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`.

Allowed tracked output:

- `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`

Allowed temporary inputs:

- `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`
- an untracked `/tmp` one-off script if inline Python becomes unreadable

The implementation must invoke `validate_report_quality_bundle()` on an in-memory valid bundle and `validate_report_quality_jsonl()` on a single-bundle scratch JSONL. Evidence must include commands, exit codes, scratch paths, `bundle_record_count == 1`, bundle/score-issue line numbers, summary counts, `error_code_counts`, run id, schema version, representative issues, interpretation, and boundary checks.

The implementation must stop before source code, tests, README files, tracked reports, fixtures, Service, CLI, renderer, `quality_gate.py` FQ0-FQ6, `extraction_score.py`, PDF/cache/source helper access, `FundDocumentRepository`, `extra_payload`, Host/Agent/dayu, `nav_data` projection, derived-calculation generation, durable baseline, real data acquisition, or product-flow integration.

## Open Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| S0 corpus transition triggers | Completed in S0 | S0 defined trigger, actor, and minimum evidence for `candidate -> repository_verified -> fact_prefill_generated -> fact_prefill_reviewed -> scoring_ready -> accepted_baseline` |
| FOF corpus coverage | S1 / fund-type taxonomy gate | S0 recorded QDII-FOF as `data_gap`; second pass must find pure `fof_fund` or open QDII-FOF taxonomy / precedence design |
| Fallback upstream failure category | S1 entry gate / source reliability evidence | Recover original upstream failure category for `110020`, `017641`, and `017970`, or exclude the fallback candidate before durable baseline selection |
| S1 score schema details | Completed in S1 schema draft | `source_boundary`, issue-based output, `N/A` denominator semantics, `chapter_summary`, terminal states, and score issue localization are accepted as draft schema |
| S1 dry-run evidence | Completed in S1 dry-run | Accepted ignored scoring-run output plus tracked Markdown review evidence; no fixture or durable baseline was promoted |
| Fact/Evidence contract shape | Completed in S2 bundle plan | Accepted `ReportEvidenceBundle` wraps/projects from `StructuredFundDataBundle`; no parallel extraction path |
| Anchor naming and review status derivation | Completed in S2 bundle plan / future implementation validation | S2 accepted namespaced ids, `sha256` locator hash, `data_gap_refs`, S0-aligned progression, and restrictive priority order |
| Turnover-rate stability gap | Completed in S2 bundle plan / future chapter-contract implementation | S2 accepted narrow active-fund Chapter 3 wording constraint before extraction work |
| JSONL content validation | Completed in implementation | `9f9bbf5` added pure validator module, focused tests, README sync, review artifacts, and controller judgment |
| Typed model file placement | Completed in implementation | `209cc25` added `fund_agent/fund/report_evidence.py`, `tests/fund/test_report_evidence.py`, and minimal `fund_agent/fund/README.md` sync |
| Bundle immutability | Completed in implementation | `ReportEvidenceBundle` and related records use frozen slotted dataclasses and tuple fields |
| `type_slot_membership_status` value domain | Completed in implementation | Executable enum/domain and derivation cover `matches_slot`, `type_gap`, `taxonomy_pending`, `unknown`, and `not_applicable` |
| Projection guard / fallback test hardening | future robustness or scoring validation slice | Add tests for context validation guards, review-status fallback states, and unknown extraction-mode fallback when those paths become consumer-critical |
| Report-quality content validator | Completed in implementation | Pure validator module and tests accepted at `9f9bbf5`; no CLI/Service/FQ0-FQ6 integration |
| Report-quality validator dry-run evidence | current implementation gate | Implement accepted single-bundle synthetic dry-run evidence artifact under `docs/reviews/`; no source/test/product-flow changes |
| `nav_data` mapping | future `nav_data` source-contract slice | Keep excluded from initial facts projection until a safe mapping contract exists |
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
| `report-quality-baseline S1 dry-run evidence` | accepted locally | `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-controller-judgment-20260525.md` | AgentCodex evidence; AgentMiMo and AgentDS `PASS_WITH_FINDINGS`; controller accepted minimal pass / issue localization; commit `1b1a30d` | S2 bundle shape, anchor/gap naming, JSONL content validation, turnover chapter-contract handling, fallback category, FOF data_gap | `fact-evidence-contract S2 bundle candidate planning` |
| `fact-evidence-contract S2 bundle candidate planning` | accepted locally | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md`, `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-controller-judgment-20260525.md` | AgentCodex plan; AgentMiMo and AgentDS `PASS_WITH_FINDINGS`; plan patched; both re-reviews `PASS`; commit `bac54ba` | typed model file placement, immutability, `type_slot_membership_status`, `nav_data` mapping, fallback category, FOF data_gap, fixture gate | `typed ReportEvidenceBundle model/projection implementation plan review` |
| `typed ReportEvidenceBundle model/projection implementation plan review` | accepted locally | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`, `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-controller-judgment-20260525.md` | AgentCodex plan; AgentMiMo and AgentDS `PASS_WITH_FINDINGS`; plan patched; both re-reviews `PASS`; commit `81191c3` | code implementation, coverage, README sync, `nav_data` mapping, fallback category, FOF data_gap, fixture gate | `ReportEvidenceBundle typed model/projection implementation` |
| `ReportEvidenceBundle typed model/projection implementation` | accepted locally | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-controller-judgment-20260525.md`, `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-mimo-20260525.md`, `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-glm-20260525.md` | AgentCodex implementation; AgentMiMo `PASS_WITH_FINDINGS`; AgentGLM `PASS_WITH_FINDINGS`; GLM F1 fixed; both re-reviews `PASS`; validation 23 focused tests / 93% coverage / 40 adjacent tests / ruff / boundary rg / diff check; commit `209cc25` | JSONL content validation, guard/fallback hardening, `nav_data` mapping, fallback category, FOF data_gap, fixture gate | `report-quality scoring JSONL content validation plan` |
| `report-quality scoring JSONL content validation plan` | accepted locally | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-controller-judgment-20260525.md` | AgentCodex plan; AgentMiMo and AgentGLM `PASS_WITH_FINDINGS`; plan patched; both re-reviews `PASS`; commit `e40a394` | validator implementation, `nav_data` mapping, derived calculations, durable baseline, Host/Agent/dayu, fallback recovery, FOF taxonomy | `report-quality scoring JSONL content validation implementation` |
| `report-quality scoring JSONL content validation implementation` | accepted locally | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md`, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-mimo-20260525.md`, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-glm-20260525.md` | AgentCodex implementation; AgentMiMo and AgentGLM `PASS_WITH_FINDINGS`; fixes completed; both re-reviews `PASS`; validation 25 focused tests / 92.34% coverage / 81 adjacent tests / ruff / boundary rg / diff check; commit `9f9bbf5` | dry-run evidence planning, multi-bundle JSONL, message-specific test hardening, `nav_data` mapping, derived calculations, durable baseline, Host/Agent/dayu, fallback recovery, FOF taxonomy | `report-quality validator dry-run evidence planning` |
| `report-quality validator dry-run evidence planning` | accepted locally | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`, `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-controller-judgment-20260525.md` | AgentCodex plan; AgentMiMo and AgentGLM `PASS_WITH_FINDINGS`; plan patched; both re-reviews `PASS`; commit `7990b8f` | dry-run evidence implementation, multi-bundle JSONL, message-specific test hardening, `nav_data` mapping, derived calculations, durable baseline, Host/Agent/dayu, fallback recovery, FOF taxonomy | `report-quality validator dry-run evidence implementation` |

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
