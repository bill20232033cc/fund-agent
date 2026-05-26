# Plan Review: Chapter Contract Implementation + Report Writing Quality Upgrade Design Plan (GLM)

> Date: 2026-05-26
> Reviewer: AgentGLM
> Recorded by: AgentController from `agents:0.3` pane output after AgentGLM twice failed to write the requested artifact path
> Target: `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md`
> Verdict: PASS_WITH_FINDINGS

## Findings Ordered By Severity

### Blocker Findings

None.

### Material Findings

#### GLM-M1: Proposed `chapter_contract_constraints.py` overlaps existing contract modules without a binding relationship decision

Existing `fund_agent/fund/template/contracts.py` already defines `ChapterContract` with `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`. Existing `fund_agent/fund/audit/contract_rules.py` already defines `ContractRequiredItemRule`, `ContractForbiddenContentRule`, and `ContractMustAnswerCoverageRule` for all eight chapters.

The plan introduces `ChapterExecutableConstraint`, `EvidenceRequirement`, and `ChapterContractAuditFinding`, but does not bind them to existing modules. The implementation gate must decide before code generation whether the new structure extends existing dataclasses, wraps them, or deliberately remains a separate executable layer. Otherwise the project risks a parallel dual-contract system.

#### GLM-M2: `audit_chapter_contract()` boundary against existing audit and validator paths needs explicit definition

The repository already has `run_programmatic_audit()` for rendered Markdown structure/format checks and `validate_report_quality_bundle()` for evidence-bundle schema/content integrity checks. The proposed chapter contract writing audit is a third path.

Before implementation, the plan must state that the new audit checks report-writing semantic constraints over `ReportEvidenceBundle` and optional explicit Markdown, while existing programmatic audit checks renderer markers and existing validator checks bundle/JSONL integrity.

#### GLM-M3: `required_evidence` and `allowed_na_reason` are not fields on existing frozen `ChapterContract`

The plan defines per-chapter `required_evidence` and `allowed_na_reason`, but current `ChapterContract` is frozen and does not contain those fields. If the implementation does not modify `ChapterContract`, it needs a separate wrapper/sidecar model. This repeats GLM-M1 unless the plan explicitly chooses the sidecar model.

#### GLM-M4: Chapter 2 and Chapter 6 skeleton constraints could create false positives before extraction gates

The plan correctly classifies `004194` tracking error and `006597` bond risk lens issues as data extraction / reviewed-fact readiness problems. However, the Chapter 2 and Chapter 6 skeletons list full `required_evidence` sets. The implementation gate should mark deferred extraction-dependent skeleton requirements as informational or configuration-only until the corresponding extraction gate exists.

### Minor Findings

#### GLM-m1: `scripts/report_quality_eval.py` is an existing file

The plan lists `scripts/report_quality_eval.py` as optional allowed scope for adding a flag. It should explicitly say this is an optional modification to an existing maintainer-only script, not a new script.

#### GLM-m2: Top 5 item for combined JSONL is a validator consumer issue, not a report-writing issue

The combined JSONL `RQV_REF_MISSING=4` issue was already fixed in the validator consumer gate. It can remain in Top 5 as escalation evidence, but its category should be named `validator consumer / evidence-link integrity`, not a direct report-writing issue.

#### GLM-m3: Preferred-lens overlay tests should be configuration tests for deferred extraction cases

The test strategy says active, enhanced-index, and bond overlays should reproduce accepted small-baseline failure categories. For `004194` and `006597`, that could imply end-to-end finding reproduction before extraction evidence exists. It should be narrowed to overlay configuration correctness for enhanced-index and bond, while full material audit behavior is first enforced only for active Chapter 3.

#### GLM-m4: `docs/design.md` update deferral is correct

The plan correctly avoids updating `docs/design.md` during planning and limits the future sync to current-code facts after implementation passes.

## Evidence Checked

| Claim | Direct evidence? | Artifact |
|---|---|---|
| Three clean slots: `004393` active, `004194` enhanced index, `006597` bond | Yes | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` |
| Chapter 3 `turnover_rate` material issue and `chapter_contract` next owner | Yes | `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`; `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` |
| Runtime `ContractRequiredItemRule` deferred because renderer cannot satisfy marker | Yes | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-controller-judgment-20260526.md` |
| Combined JSONL `RQV_REF_MISSING=4` fixed to `blocking_count=0` | Yes | `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md` |
| Chapter 2 `tracking_error` material issue for `004194` | Yes | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` |
| Chapter 6 `risk.bond_lens` material issue for `006597` | Yes | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` |
| Escalation readiness accepted evidence criteria | Yes | `docs/reviews/release-maintenance-escalation-readiness-check-20260526.md` |

## Verdict

PASS_WITH_FINDINGS.

The plan is directionally correct and does not require product-flow, renderer, FQ0-FQ6, Service/CLI, Host/Agent, dayu runtime, or source-pipeline changes. The material findings are plan-clarity issues that should be patched before implementation starts, especially the relationship between the proposed executable contract layer and existing `ChapterContract` / programmatic audit / report-quality validator structures.
