# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.0
> **日期**: 2026-05-25
> **设计真源**: `docs/design.md` (v2.2)
> **规则真源**: `AGENTS.md`
> **历史快照**: `docs/archive/implementation-control-history-20260525.md`
> **当前状态**: release maintenance；Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation accepted locally；下一入口需单独开 renderer/report-writing output-changing gate 或 audit-output ergonomics gate

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
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate | `Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation accepted locally` |
| Next entry point | `future explicit gate: renderer/report-writing output emission or report-writing audit ergonomics; no product-flow integration authorized` |
| Latest accepted gate checkpoint | `chapter contract sidecar + dev-only audit local accepted HEAD` |
| Design truth | `docs/design.md` (v2.2) |
| Control truth | `docs/implementation-control.md` |
| Historical control snapshot | `docs/archive/implementation-control-history-20260525.md` |
| External repo state | PR 18 merged at `2026-05-25T14:44:05Z`; PR 19 merged at `2026-05-25T15:43:35Z`; `origin/main` points to `44ea955` |

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
| Report-quality validator dry-run evidence | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md` |
| Report-quality validator dry-run evidence review: MiMo | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-review-mimo-20260525.md` |
| Report-quality validator dry-run evidence review: GLM | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-review-glm-20260525.md` |
| Report-quality validator dry-run evidence re-review: MiMo | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-rereview-mimo-20260525.md` |
| Report-quality validator dry-run evidence controller judgment | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-controller-judgment-20260525.md` |
| Release-readiness reconciliation | `docs/reviews/release-readiness-reconciliation-20260525.md` |
| Release acceptance packaging / PR readiness | `docs/reviews/release-acceptance-packaging-pr-readiness-20260525.md` |
| Overnight release-readiness closeout | `docs/reviews/overnight-release-readiness-closeout-20260525.md` |
| Post-merge local reconciliation / artifact disposition | `docs/reviews/post-merge-local-reconciliation-artifact-disposition-20260525.md` |
| Report-quality validator integration decision plan | `docs/reviews/release-maintenance-report-quality-validator-integration-decision-plan-20260525.md` |
| Report-quality validator integration plan review | `docs/reviews/plan-review-20260525-235520.md` |
| Report-quality validator integration plan re-review | `docs/reviews/plan-rereview-20260525-235615.md` |
| Report-quality validator quasi-real bundle evidence | `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md` |
| Report-quality validator quasi-real bundle controller judgment | `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md` |
| Report-quality validator quasi-real retrospective controller judgment | `docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md` |
| Small baseline corpus candidate selection | `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md` |
| Small baseline evaluation plan / verifier design | `docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md` |
| First report-quality improvement slice plan | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md` |
| First improvement slice plan review: MiMo | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-mimo-20260526.md` |
| First improvement slice plan review: GLM | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-glm-20260526.md` |
| First improvement slice plan re-review: MiMo | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-rereview-mimo-20260526.md` |
| First improvement slice plan re-review: GLM | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-rereview-glm-20260526.md` |
| First improvement slice plan controller judgment | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-controller-judgment-20260526.md` |
| First improvement slice implementation review: MiMo | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-review-mimo-20260526.md` |
| First improvement slice implementation review: GLM | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-review-glm-20260526.md` |
| First improvement slice implementation controller judgment | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-controller-judgment-20260526.md` |
| Small baseline real evaluation run | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` |
| Small baseline validator fix evidence | `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md` |
| Validator fix review: MiMo | `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-mimo-20260526.md` |
| Validator fix review: GLM | `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-glm-20260526.md` |
| Validator fix re-review: MiMo | `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-mimo-20260526.md` |
| Validator fix re-review: GLM | `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-glm-20260526.md` |
| Dev-only report-quality eval tool | `docs/reviews/release-maintenance-small-baseline-real-evaluation-dev-tool-20260526.md` |
| Small baseline real evaluation controller judgment / readiness | `docs/reviews/release-maintenance-small-baseline-real-evaluation-controller-judgment-20260526.md` |
| Small baseline final aggregate review: MiMo | `docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-mimo-20260526.md` |
| Small baseline final aggregate review: GLM | `docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-glm-20260526.md` |
| Deepreview controller judgment evidence-chain artifact | `docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md` |
| Escalation readiness check | `docs/reviews/release-maintenance-escalation-readiness-check-20260526.md` |
| Escalation readiness re-review: MiMo | `docs/reviews/release-maintenance-escalation-readiness-rereview-mimo-20260526.md` |
| Escalation readiness re-review: GLM | `docs/reviews/release-maintenance-escalation-readiness-rereview-glm-20260526.md` |
| Chapter contract / report-writing upgrade design plan | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-review-mimo-20260526.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-review-glm-20260526.md` |
| Plan re-review: MiMo | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-rereview-mimo-20260526.md` |
| Plan re-review: GLM | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-rereview-glm-20260526.md` |
| Chapter contract / report-writing upgrade controller judgment | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-controller-judgment-20260526.md` |
| Chapter contract sidecar implementation plan | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md` |
| Sidecar implementation plan review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-mimo-20260526.md` |
| Sidecar implementation plan review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-glm-20260526.md` |
| Sidecar implementation plan controller judgment | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-controller-judgment-20260526.md` |
| Sidecar implementation evidence | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md` |
| Sidecar implementation review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-mimo-20260526.md` |
| Sidecar implementation review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-glm-20260526.md` |
| Sidecar implementation re-review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview-mimo-20260526.md` |
| Sidecar implementation re-review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview-glm-20260526.md` |
| Sidecar implementation targeted re-review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview2-glm-20260526.md` |
| Sidecar implementation controller judgment | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md` |

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
- Report-quality validator dry-run evidence accepted commit `1087c57` proves the validator can be consumed over a synthetic valid bundle and single-bundle JSONL, returns stable summary counts, pointers, run id, schema version, and representative issues, and still excludes product-flow integration.
- Dry-run evidence residuals remain non-blocking: multi-bundle JSONL, exact unknown-upstream message assertions, non-scoring-ready `chapter_summary/report_level` policy, `nav_data`, derived calculations, durable baseline, fallback recovery, FOF taxonomy, real corpus evidence, and Host/Agent/Dayu runtime.
- Release-readiness reconciliation accepted the current deterministic MVP path as locally release-ready: `fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block` exits 0 with `quality_gate_status: warn`; `fund-analysis checklist 004393 --report-year 2024` exits 0; `fund-analysis thermometer --json` exits 0; full pytest, ruff, and `git diff --check` pass; no tracked scratch report / scoring-run / quality-gate-run / JSONL / cache output was introduced; renderer, FQ0-FQ6 quality gate, Service, CLI, Host/Agent packages, and Dayu runtime dependencies remain unchanged.
- Release acceptance packaging / PR readiness accepted the current branch as locally ready to push for a release-readiness PR, subject to user authorization. Evidence: branch `codex/v0-release-readiness-plan` has no upstream, no open PR, PR 15 is closed, PR 17 is merged; `origin/main..HEAD` contains release evidence and Fund-only new capabilities; product commands, full pytest, ruff, `git diff --check`, boundary checks, and tracked scratch checks pass.
- After explicit user authorization, branch `codex/v0-release-readiness-plan` was pushed to origin and draft PR 18 was opened against `main`. First post-create poll: state `OPEN`, draft `true`, mergeable `MERGEABLE`, CI `test` `IN_PROGRESS`.
- PR 18 CI follow-up: `test` check completed with `SUCCESS`; PR remains `OPEN`, draft `true`, and `MERGEABLE`.
- After explicit user authorization in prior turns, PR 18 was marked ready for review and squash-merged into `main`. Read-only closeout evidence confirms PR 18 state `MERGED`, merge commit `c74223aefa1fe2c0ff66dd55bd8f17e5145c12c1`, and `origin/main` at `c74223a`.
- After explicit user authorization, PR 19 was marked ready for review and squash-merged into `main`. Read-only closeout evidence confirms PR 19 state `MERGED`, merge commit `44ea95554f7b3f8fa48b62902dfb1a3469b3e471`, and `origin/main` at `44ea955`.
- Local reconciliation accepted `codex/local-reconciliation` as the safe working baseline from `origin/main`; local `main` remains divergent and must not be reset, rebased, or used as the work baseline without explicit user decision. Ignored `reports/data-source-runs/` and `reports/scoring-runs/` outputs remain scratch evidence. The untracked report-quality validator integration decision plan remains a candidate artifact, not accepted truth.
- Report-quality validator integration decision plan is accepted after plan review and targeted re-review. The next evidence run must use a manually assembled quasi-real bundle labeled `quasi_real_review_evidence`, derived from accepted S0/S1/S2 review evidence and current validator serialization shape. It must not fetch or parse annual reports, call production extractors, call `FundDocumentRepository`, PDF/cache/source helpers, downloaders, or source adapters, and must not claim `repository_verified`, `scoring_ready`, or `accepted_baseline`.
- Report-quality validator quasi-real bundle evidence run is accepted locally. `validate_report_quality_bundle()` consumed 1 quasi-real bundle and `validate_report_quality_jsonl()` consumed a 3-line JSONL with 1 bundle record and 2 score-issue records; both returned no validator issues and no fail-closed state. The evidence remains quasi-real, not repository-verified, not scoring-ready, and not baseline. Failure-category decision: validator schema is not the blocker; next gate should be active-fund chapter 3 turnover/style-consistency contract wording before any data extraction, renderer, Service/CLI, FQ0-FQ6, durable baseline, Host/Agent, or Dayu work.
- Retrospective verification accepted the prior quasi-real closeout process: AgentMiMo returned `PASS` for Gate 0 control-state sanity, AgentGLM returned `PASS_WITH_FINDINGS` for Gate 1 / Gate 2 evidence and failure-category review, and all findings were informational. Future corpus / chapter-contract gates should preserve the provenance chain for S0-derived `identity_status="verified_annual_report"` so it is not misread as a new repository verification claim.
- Small baseline corpus candidate selection accepted 7 planning rows from existing accepted evidence only: clean near-term evaluation candidates `004393` / active, `004194` / enhanced index, and `006597` / bond; fallback-blocked planning candidates `110020` / index and `017641` / QDII pending upstream failure-category recovery or replacement; FOF remains a `data_gap` with `007721` and `017970` recorded as QDII-FOF/type-gap evidence, not fulfilled pure FOF coverage. No sample is `scoring_ready` or `accepted_baseline`.
- Small baseline evaluation plan / verifier design is accepted as planning-only. The future offline loop must use explicit manifests, reviewed inputs, `ReportEvidenceBundle` / JSONL serialization, `validate_report_quality_bundle()` / `validate_report_quality_jsonl()`, scratch output under `/tmp/fund-agent-small-baseline-eval-20260526/` or ignored `reports/scoring-runs/small-baseline-eval-20260526/`, and a tracked summary artifact. It must keep fallback-blocked index/QDII rows out of the clean denominator, keep FOF as `data_gap`, and must not call default `analyze` / `checklist` or change renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixtures, or product flow.
- First improvement slice plan/review accepted `active_fund` Chapter 3 turnover/style-consistency data-gap wording contract as the minimal first implementation slice. The patched plan closed MiMo material findings by specifying exact Chinese contract wording, fixed audit route decisions, explicit modify/add decisions, and template-draft-first update order. Gate D must first verify whether adding a new `ContractRequiredItemRule` would affect default runtime audit behavior; if it would require renderer/product-flow changes, implementation must stop or defer that rule to a later renderer/report-writing gate.
- First improvement slice implementation accepted the safe option: Chapter 3 active-fund contract wording and `narrative_guidance` `must_not_cover` coverage were hardened, `ReportDataGapOverride.required_report_wording` now preserves insufficiency and next-minimum-validation wording, and no new runtime `ContractRequiredItemRule` was added because current renderer output cannot satisfy that marker without a later renderer/report-writing gate. Focused tests, adjacent tests, ruff, `git diff --check`, boundary checks, and two independent code reviews passed.
- Small baseline real evaluation accepted three clean fund-type slots: `004393` / active, `004194` / enhanced index, and `006597` / bond. Each sample produced scratch `ReportEvidenceBundle`, per-sample JSONL, validator summary, and failure-category localization under `/tmp/fund-agent-small-baseline-real-eval-20260526/`; `110020` / index and `017641` / QDII remain fallback-blocked, and FOF remains a data-gap/type-taxonomy residual. No sample is `scoring_ready`, `accepted_baseline`, or durable fixture.
- The first concrete quality fix accepted for this gate is the multi-bundle JSONL validator consumer fix. `validate_report_quality_jsonl()` now assigns standalone `record_type="score_issue"` rows to the nearest preceding bundle, keeps bundle-before-score ownership fail-closed via `RQV_SCORE_ISSUE_ORPHANED`, and still rejects cross-bundle anchor/gap references. The Gate A combined JSONL now validates with `total_records=9`, `blocking_count=0`, and `failed_closed=false`.
- Gate C accepted `scripts/report_quality_eval.py` as a maintainer-only/dev-only wrapper over explicit JSONL and bundle JSON inputs. It is not registered as a product CLI entry point and does not change `fund-analysis analyze`, `fund-analysis checklist`, Service defaults, renderer, FQ0-FQ6, Host/Agent/dayu, document repository, source helpers, `nav_data`, or durable fixtures.
- Chapter contract / report-writing upgrade design plan is accepted locally. Gate A synthesized Top 5 evidence-backed report-quality issues and separated chapter-contract, writing-template, data-extraction, and validator-consumer categories. Gate B accepted a dev-only executable sidecar/wrapper over existing `ChapterContract`, not a replacement and not a parallel truth source. Gate C selected the minimal first implementation slice: Fund-layer executable constraints plus dev-only report-writing audit centered on active-fund Chapter 3 claim safety, with no renderer, Service/CLI, FQ0-FQ6, Host/Agent/dayu, source-helper, product-entrypoint, or default behavior changes.
- The accepted implementation plan fixes the audit module path to `fund_agent/fund/report_writing_audit.py`, stores `required_evidence`, `allowed_na_reason`, `failure_behavior`, and overlay severity in `fund_agent/fund/template/chapter_contract_constraints.py` as sidecar data, integrates active Chapter 3 gap wording with `ReportDataGapOverride.required_report_wording`, keeps Chapter 2/6 deferred extraction-dependent requirements informational/config-only, targets >=80% per-file coverage for new modules, and treats `scripts/report_quality_eval.py` integration as optional/deferrable.
- Fund-layer CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation is accepted locally. `fund_agent/fund/template/chapter_contract_constraints.py` wraps the existing 0-7 chapter manifest and adds the first material active-fund Chapter 3 turnover/style-consistency evidence requirement; `fund_agent/fund/report_writing_audit.py` consumes explicit `ReportEvidenceBundle` / records / chapter draft surrogates and outputs deterministic issues and summaries. The accepted behavior requires resolvable evidence anchors for satisfying facts, explicit insufficient-evidence wording and next minimum validation question for compatible `data_gap`, fail-closed records input handling, and no renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/source-helper integration.

### Current Non-Goals

- Do not change current v0 renderer or current 8-chapter output.
- Do not change FQ0-FQ6 quality gate behavior.
- Do not claim LLM audit / Evidence Confirm / repair loop is implemented.
- Do not create Host/Agent packages or introduce `dayu.host` / `dayu.engine` before an explicit gate.
- Do not introduce calculated index series, external index adapters beyond accepted thermometer data-source protocols, methodology extraction, constituents extraction, QDII subtype redesign, unsupported coverage targets, or quality-gate weakening.
- Do not promote local scoring, writing, or data-source run outputs into tracked fixtures without a later reviewed gate.

## Next Entry Point

No product-flow integration is authorized by the accepted sidecar gate. The next explicit gate should be one of:

- `renderer/report-writing output emission gate`: decide whether and how the current v0 renderer or a future chapter writer should emit active-fund Chapter 3 insufficiency wording; this must be opened separately because it changes user-visible output.
- `report-writing audit ergonomics gate`: improve occurrence-level issue ids, broader records ingestion, or additional chapter/fund-type constraints without changing product defaults.

Any next gate must start from `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md`, `docs/design.md` §3.2, and the current Startup Packet.

Do not integrate this dev-only audit into renderer, Service, CLI, FQ0-FQ6, source helpers, `FundDocumentRepository`, Host/Agent/dayu runtime, product entry points, scratch fixture promotion, or product default behavior without a separate reviewed gate.

Do not push, create PR, mark ready, merge, close PRs, edit unrelated PRs, delete branches, or perform additional GitHub mutations without explicit user authorization. Do not modify Service, CLI, renderer, `quality_gate.py`, `extraction_score.py`, tracked reports, fixtures, repository/PDF/cache/source helpers, `FundDocumentRepository`, Host/Agent/dayu, `nav_data`, derived calculations, durable baseline, report-quality validator integration, or product-flow behavior unless a later explicit gate authorizes that scope.

## Open Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| S0 corpus transition triggers | Completed in S0 | S0 defined trigger, actor, and minimum evidence for `candidate -> repository_verified -> fact_prefill_generated -> fact_prefill_reviewed -> scoring_ready -> accepted_baseline` |
| FOF corpus coverage | S1 / fund-type taxonomy gate | S0 recorded QDII-FOF as `data_gap`; second pass must find pure `fof_fund` or open QDII-FOF taxonomy / precedence design |
| Fallback upstream failure category | S1 entry gate / source reliability evidence | Recover original upstream failure category for `110020`, `017641`, and `017970`, or exclude / replace the fallback candidate before durable baseline selection |
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
| Report-quality validator dry-run evidence | Completed in implementation | `1087c57` accepted synthetic single-bundle dry-run evidence; no source/test/product-flow changes |
| Report-quality validator integration decision | Completed in planning | `11cde1d` accepted the manually assembled `quasi_real_review_evidence` next run path without product-flow integration |
| Report-quality validator quasi-real evidence | Completed in evidence run | `05d037b` accepted one quasi-real bundle plus single-bundle JSONL validation; next decision is chapter-contract wording before extraction or integration |
| Small baseline corpus candidate selection | Completed in candidate selection | Accepted clean evaluation-plan candidates `004393`, `004194`, `006597`; fallback-blocked `110020`, `017641`; FOF data-gap attempts `007721`, `017970`; no durable baseline promotion |
| Small baseline evaluation plan / verifier design | Completed in planning | Offline explicit-manifest evaluator design accepted; durable baseline remains blocked until reviewed facts, source recovery or replacement, clean validator results, and a separate curated-fixture gate |
| First improvement slice plan/review | Completed in planning | Accepted active-fund Chapter 3 turnover/style-consistency data-gap wording contract; Gate D must preflight runtime audit behavior before adding any required item rule |
| First improvement slice implementation | Completed in implementation | Accepted safe-option contract hardening; no renderer/FQ0-FQ6/Service/CLI/default behavior change; runtime required item deferred |
| Small baseline real evaluation | Completed in evidence run | Accepted three clean slots and scratch-only bundle / JSONL / validator evidence; no `scoring_ready`, durable baseline, or product-flow integration |
| Multi-bundle JSONL validator consumer | Completed in implementation | Accepted nearest-preceding-bundle score_issue ownership fix; duplicate-index issue duplication remains low residual |
| Dev-only report-quality eval tool | Completed in implementation | `scripts/report_quality_eval.py` is maintainer-only and explicit-input only; no product CLI integration |
| Renderer/report-writing contract emission | next chapter contract / report-writing design gate | Decide whether active-fund Chapter 3 accepted gap wording requires renderer/report-writing changes; stop if FQ0-FQ6 or default Service/CLI changes would be required without explicit reviewed scope |
| Chapter contract / report-writing design plan | Completed in design/plan/review | Accepted Fund-layer sidecar + dev-only report-writing audit plan; first implementation slice must not change renderer/product flow |
| Fund-layer CHAPTER_CONTRACT sidecar + dev-only report-writing audit | Completed in implementation | Accepted Fund-layer sidecar and dev-only audit; no renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/source-helper integration |
| Report-writing audit duplicate occurrence ids | future audit-output ergonomics gate | Current deterministic `issue_id` values are class ids; add draft locator or occurrence ordinal only in a separate output-schema gate |
| Report-writing audit records-mode breadth | future audit-output ergonomics gate | Current records helper is fail-closed and narrow to active-fund Chapter 3; broaden only after schema/design review |
| Product renderer emission of active Chapter 3 insufficiency wording | future output-changing renderer/report-writing gate | Open only after dev-only audit evidence proves the exact minimal output change required |
| `nav_data` mapping | future `nav_data` source-contract slice | Keep excluded from initial facts projection until a safe mapping contract exists |
| Document identity vs fund-type slot membership | Completed in S1 schema draft | S1 split document verification from type-slot membership so `verified_as_annual_report_but_type_gap` cannot become scoring-ready FOF evidence |
| Review-state terminal states | Completed in S1 schema draft / future implementation validation | S1 defined rejected / deferred / expired semantics; S2 or later implementation must add executable value-domain validation if schema becomes code |
| `fq_gate_status` citation | S1 / S2 | Cite existing quality gate final judgment contract semantics for `pass`, `warn`, `block`, `not_run` |
| PR 15 stale disposition | Completed by external state | Current GitHub state reports PR 15 as closed; no local action required |
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
| `report-quality validator dry-run evidence implementation` | accepted locally | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`, `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-controller-judgment-20260525.md` | AgentCodex evidence; AgentMiMo `PASS_WITH_FINDINGS`; AgentGLM `PASS`; MiMo targeted re-review `PASS`; validation evidence-only artifact / single-bundle JSONL / boundary rg / diff check; commit `1087c57` | integration decision planning, multi-bundle JSONL, message-specific test hardening, `nav_data` mapping, derived calculations, durable baseline, Host/Agent/dayu, fallback recovery, FOF taxonomy | `report-quality validator integration decision planning` |
| `report-quality validator integration decision planning` | accepted locally | `docs/reviews/release-maintenance-report-quality-validator-integration-decision-plan-20260525.md`, `docs/reviews/plan-review-20260525-235520.md`, `docs/reviews/plan-rereview-20260525-235615.md` | Planning chose a manual `quasi_real_review_evidence` evidence loop; review F1 closed by locking input provenance and forbidding production extraction/repository access; commit `11cde1d` | quasi-real evidence run, multi-bundle JSONL, durable baseline, Service/CLI/FQ0-FQ6, Host/Agent/dayu, fallback recovery, FOF taxonomy | `report-quality validator quasi-real bundle evidence run` |
| `report-quality validator quasi-real bundle evidence run` | accepted locally | `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`, `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md` | `validate_report_quality_bundle()` consumed 1 quasi-real bundle; `validate_report_quality_jsonl()` consumed 3 JSONL records; focused tests / ruff / diff check passed; commit `05d037b` | active-fund chapter 3 turnover/style-consistency wording, multi-bundle JSONL, durable baseline, source reliability, FOF taxonomy | `active-fund chapter 3 turnover/style-consistency contract wording plan` |
| `report-quality validator quasi-real retrospective verification` | accepted locally | `docs/reviews/release-maintenance-report-quality-quasi-real-retrospective-controller-judgment-20260526.md` | AgentMiMo `PASS`; AgentGLM `PASS_WITH_FINDINGS`; no blocking or material findings; informational provenance observation accepted | provenance wording in future corpus/chapter-contract gates, untracked unrelated review artifact disposition | `small baseline corpus candidate selection + first report-quality improvement slice` |
| `small baseline corpus candidate selection` | accepted locally | `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md` | AgentCodex selected 7 candidate/data-gap rows from accepted evidence only; `git diff --check` passed; no source/test/product-flow changes | fallback recovery or replacement for index/QDII, pure FOF coverage, fact-review/scoring-ready freeze, chapter 3 turnover contract | `baseline evaluation plan / verifier design` |
| `baseline evaluation plan / verifier design` | accepted locally | `docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md` | AgentCodex designed an offline explicit-input evaluator loop with scratch-only outputs and failure-category mapping; `git diff --check` passed; no source/test/product-flow changes | reviewed fact availability for `004194` / `006597`, source recovery or replacement, pure FOF coverage, durable fixture gate | `first improvement slice selection plan/review` |
| `first improvement slice selection plan/review` | accepted locally | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md`, `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-controller-judgment-20260526.md` | AgentCodex plan; AgentMiMo and AgentGLM `PASS_WITH_FINDINGS`; plan patched; MiMo re-review `PASS`; GLM re-review `PASS_WITH_FINDINGS`; mandatory Gate D preflight accepted | runtime audit rule behavior, renderer/product-flow boundary, README/design sync, durable baseline, source recovery, FOF taxonomy | `active-fund chapter 3 turnover/style-consistency data-gap wording contract implementation` |
| `active-fund chapter 3 turnover/style-consistency data-gap wording contract implementation` | accepted locally | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-controller-judgment-20260526.md` | AgentCodex implementation; focused tests `83 passed`; adjacent tests `190 passed`; ruff / diff check / boundary checks passed; AgentMiMo and AgentGLM `PASS_WITH_FINDINGS`; safe option accepted | renderer/report-writing marker emission, runtime required item, extraction evidence, fallback recovery, FOF taxonomy, durable baseline | `small baseline real evaluation run + first concrete quality fix + dev-only reporting tool` |
| `small baseline real evaluation run + first concrete quality fix + dev-only reporting tool` | accepted locally | `docs/reviews/release-maintenance-small-baseline-real-evaluation-controller-judgment-20260526.md`, `docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-mimo-20260526.md`, `docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-glm-20260526.md` | AgentCodex evidence / implementation; Gate A validated three clean fund-type slots; Gate B fixed combined JSONL validator ownership; Gate C added maintainer-only script; MiMo final review `PASS`, GLM final review `PASS_WITH_FINDINGS`; focused / adjacent tests, ruff, diff check passed | duplicate-index residual, index/QDII fallback recovery, FOF data-gap, durable baseline blocked, active Chapter 3 renderer/report-writing emission | `escalation readiness check; if complete, chapter contract implementation + report writing quality upgrade design gate` |
| `chapter contract implementation + report writing quality upgrade design plan` | accepted locally | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-controller-judgment-20260526.md` | Gate A evidence synthesis, Gate B executable contract design, Gate C minimal report-writing upgrade slice, Gate D plan reviews and controller judgment accepted; local commit `aeea2be` | implementation of Fund-layer sidecar and dev-only audit | `Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation gate` |
| `Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation` | accepted locally | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md` | Implementation, two code reviews, fixes, re-reviews, targeted re-review, focused tests `19 passed`, adjacent tests `147 passed`, ruff and boundary checks passed; accepted local HEAD recorded by `git log` | duplicate occurrence ids, records-mode breadth, coverage probe blocked by local numpy import issue, future renderer/report-writing emission | `future explicit renderer/report-writing output gate or audit-output ergonomics gate` |

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
