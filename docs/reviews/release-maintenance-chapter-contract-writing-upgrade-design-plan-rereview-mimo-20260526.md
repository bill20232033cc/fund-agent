# Re-Review: Chapter Contract Implementation + Report Writing Quality Upgrade Design Plan

> Date: 2026-05-26
> Reviewer: AgentMiMo
> Type: narrow re-review — verify finding closure after plan patch
> Target: `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md` (patched)
> Initial reviews:
> - `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-review-mimo-20260526.md`
> - `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-review-glm-20260526.md`
> Constraints: read-only; no source/test/plan modification; no git add/commit/push; no GitHub mutation

## 1. Finding Closure Table

### MiMo Initial Review Findings

| ID | Severity | Summary | Patch evidence in current plan | Status |
|---|---|---|---|---|
| M1 | Material | Audit module file placement ambiguous (two candidate paths) | §2.2: "The default audit module path is fixed: `fund_agent/fund/report_writing_audit.py`." §3.2 table: single path, no alternate. | **Closed** |
| M2 | Material | `docs/design.md` update decision — owner and acceptance criteria missing | §2.6: "Owner: the next implementation agent that adds the executable sidecar/audit code." Added acceptance criterion: "the design text describes only current code facts from the implementation diff and keeps future renderer/product-flow integration explicitly future-scoped or absent." | **Closed** |
| M3 | Material | Test coverage target not explicitly stated | §3.4: "Single-file coverage target: newly added modules ... should each target ≥80% test coverage. If local tooling cannot report per-file coverage in the focused command, the implementation artifact must state the measured alternative and residual risk." | **Closed** |
| m1 | Minor | `audit_chapter_contract` vs `run_programmatic_audit` relationship not stated | §2.2 new boundary table explicitly defines three paths: `audit_chapter_contract()` (report-writing semantic constraints over bundle), `run_programmatic_audit()` (renderer-level markers over rendered Markdown), `validate_report_quality_*()` (bundle/JSONL schema integrity). Non-responsibility column prevents overlap. | **Closed** |
| m2 | Minor | Optional scripts items not explicitly deferrable | §3.2: scripts entry now reads "Optional and deferrable: add a flag ... if capacity remains. Deferring this flag must not block the gate." Test scripts entry: "Optional and deferrable, only if the existing dev-only script flag is added." | **Closed** |
| m3 | Minor | Overlay severity rule uses "core" without defining the term | §2.4 overlay severity rule now defines: "`core` means a sidecar `EvidenceRequirement` whose absence can change the chapter conclusion for that fund type. It is not inferred from prose alone; it must be encoded explicitly on the sidecar requirement, normally mirroring `TemplateLensRule.priority='core'` when that requirement is directly tied to the preferred lens." | **Closed** |
| m4 | Minor | `ReportDataGapOverride.required_report_wording` integration not mentioned | §2.5 first slice: "Integrate Chapter 3 active-fund data-gap checks with existing `ReportDataGapOverride.required_report_wording`; the audit should verify that the accepted insufficiency wording and next-minimum-validation question are preserved when the gap is represented." §3.4 test coverage: "`ReportDataGapOverride.required_report_wording`: active Chapter 3 gap audit must consume or reference this wording path..." | **Closed** |

### GLM Initial Review Findings

| ID | Severity | Summary | Patch evidence in current plan | Status |
|---|---|---|---|---|
| GLM-M1 | Material | `chapter_contract_constraints.py` overlaps existing contracts without binding decision | §2.2 "Binding decision" section: "contracts.py remains the single machine source... Do not modify the frozen ChapterContract dataclass... Store required_evidence, allowed_na_reason, failure_behavior in the new sidecar model... Do not create a parallel contract truth. If the sidecar and existing manifest disagree on chapter ids/titles, the sidecar validation must fail closed in tests." | **Closed** |
| GLM-M2 | Material | `audit_chapter_contract()` boundary against existing audit/validator paths undefined | §2.2 new boundary table with three functions, each having Input / Responsibility / Non-responsibility columns. Explicitly prevents overlap. | **Closed** |
| GLM-M3 | Material | `required_evidence` and `allowed_na_reason` not on frozen `ChapterContract` — needs sidecar model | §2.2 binding decision: "Do not modify the frozen ChapterContract dataclass to add required_evidence, allowed_na_reason, or failure_behavior. Store ... in the new sidecar model." Explicit sidecar choice made. | **Closed** |
| GLM-M4 | Material | Chapter 2 and Chapter 6 skeleton constraints could create false positives | §2.3 new "Deferred extraction-dependent handling" section: Chapter 2 enhanced-index and Chapter 6 bond requirements are "configuration-side requirements in the first slice. Until a reviewed extraction/fact-coverage gate exists, they may emit only informational/config findings, not material end-to-end audit failures." | **Closed** |
| GLM-m1 | Minor | `scripts/report_quality_eval.py` should be noted as existing file, not new | §3.2: "Existing maintainer-only script. Optional and deferrable..." | **Closed** |
| GLM-m2 | Minor | Top 5 combined JSONL category should be `validator consumer / evidence-link integrity` | §1.2 Top 5 table, Rank 5 classification column: `validator consumer / evidence-link integrity` (was previously `evidence anchors`). | **Closed** |
| GLM-m3 | Minor | Preferred-lens overlay tests should be config tests for deferred extraction cases | §3.4: "Enhanced-index and bond overlay tests are configuration tests only in this slice; they should assert the sidecar marks the right requirements and deferred informational/config severity, not reproduce end-to-end extraction failures." | **Closed** |

## 2. New Findings Introduced by Patch

The patch introduced several new paragraphs and binding decisions. Reviewing them for new issues:

| Patch addition | Assessment |
|---|---|
| §2.2 binding decision (sidecar over existing manifest) | Sound. Correctly prevents parallel contract truth and mandates fail-closed validation. |
| §2.2 boundary table (three audit/validator paths) | Sound. Non-responsibility column prevents scope creep between paths. |
| §2.3 deferred extraction-dependent handling | Sound. Informational/config severity for Ch2 enhanced-index and Ch6 bond prevents false positives before extraction gates. |
| §2.4 `core` definition with `TemplateLensRule.priority` reference | Sound. Links sidecar severity to existing preferred_lens priority mechanism. |
| §2.5 `ReportDataGapOverride` integration | Sound. Connects new audit to existing gap wording infrastructure from Gate D implementation. |
| §2.6 owner and acceptance criteria for design.md update | Sound. Implementation-agent-owned with narrow code-facts-only scope. |
| §3.2 deferrable markers on scripts items | Sound. Reduces implementation pressure without blocking the gate. |
| §3.4 ≥80% coverage target with fallback clause | Sound. Aligns with AGENTS.md single-file coverage target. |

No new findings introduced by the patch.

## 3. Verdict

**PASS**

All MiMo findings (3 material, 4 minor) and all GLM findings (4 material, 3 minor) are closed by the plan patch. No new findings introduced. The patched plan is ready for implementation.
