# Re-Review: Chapter Contract Implementation + Report Writing Quality Upgrade Design Plan

> Date: 2026-05-26
> Reviewer: AgentGLM
> Review type: narrow re-review — confirm finding closure after plan patch
> Target: `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md` (patched version)
> Initial reviews: MiMo (`*-review-mimo-20260526.md`), GLM (`*-review-glm-20260526.md`)
> Constraints: read-only; no source/test/plan artifact modification; no git add/commit/push; no GitHub mutation

## Finding Closure Table

### MiMo Findings

| ID | Finding | Closure status | Patch evidence |
|---|---|---|---|
| MiMo-M1 | Audit module file placement ambiguous — two candidate paths, no decision criterion | **CLOSED** | §2.2 line 79: "The default audit module path is fixed: `fund_agent/fund/report_writing_audit.py`." §3.2 line 192: "Default and only planned audit module path." |
| MiMo-M2 | `docs/design.md` update creates documentation debt tracking gap — no owner or acceptance criteria | **CLOSED** | §2.6 lines 161-163: owner is "the next implementation agent"; narrow scope is "revise §3.2 to state that CHAPTER_CONTRACT now has a dev-only sidecar/wrapper audit layer"; acceptance criterion is "the design text describes only current code facts from the implementation diff and keeps future renderer/product-flow integration explicitly future-scoped or absent." |
| MiMo-M3 | Test coverage target not explicitly stated for new modules | **CLOSED** | §3.4 line 270: "newly added modules `chapter_contract_constraints.py` and `report_writing_audit.py` should each target ≥80% test coverage. If local tooling cannot report per-file coverage in the focused command, the implementation artifact must state the measured alternative and residual risk." |
| MiMo-m1 | `audit_chapter_contract` vs `run_programmatic_audit` relationship not stated | **CLOSED** | §2.2 lines 90-96: explicit "Boundary against existing audit/validator paths" table with input/responsibility/non-responsibility for each of the three functions. |
| MiMo-m2 | Optional items (scripts/test_scripts) should be marked deferrable | **CLOSED** | §3.2 lines 196-197: "Existing maintainer-only script. Optional and deferrable... Deferring this flag must not block the gate." |
| MiMo-m3 | Overlay severity rule uses "core" without defining the term | **CLOSED** | §2.4 line 134: "`core` means a sidecar `EvidenceRequirement` whose absence can change the chapter conclusion for that fund type. It is not inferred from prose alone; it must be encoded explicitly on the sidecar requirement, normally mirroring `TemplateLensRule.priority='core'` when that requirement is directly tied to the preferred lens." |
| MiMo-m4 | Plan does not mention `ReportDataGapOverride.required_report_wording` integration | **CLOSED** | §2.5 line 145: "Integrate Chapter 3 active-fund data-gap checks with existing `ReportDataGapOverride.required_report_wording`." §3.4 line 268: explicit test requirement for this integration. |

### GLM Findings

| ID | Finding | Closure status | Patch evidence |
|---|---|---|---|
| GLM-M1 | Proposed `chapter_contract_constraints.py` overlaps existing contract modules without binding relationship decision | **CLOSED** | §2.2 lines 70-78 "Binding decision": `contracts.py` remains single machine source for all existing fields; `ChapterContract` frozen dataclass is not modified; new fields (`required_evidence`, `allowed_na_reason`, `failure_behavior`) go in sidecar model; sidecar must reference existing chapter ids and stable strings; sidecar validation must fail closed if it disagrees with manifest. |
| GLM-M2 | `audit_chapter_contract()` boundary against existing audit/validator paths needs explicit definition | **CLOSED** | §2.2 lines 90-96: boundary table with three rows — `audit_chapter_contract()` (semantic constraints over bundle + optional Markdown), `run_programmatic_audit()` (renderer markers over rendered report), `validate_report_quality_bundle()`/`validate_report_quality_jsonl()` (schema/content integrity). Each has explicit non-responsibility. |
| GLM-M3 | `required_evidence`/`allowed_na_reason` not fields on existing frozen `ChapterContract` | **CLOSED** | §2.2 line 76: "Do not modify the frozen `ChapterContract` dataclass to add `required_evidence`, `allowed_na_reason`, or `failure_behavior`." Line 77: "Store ... in the new sidecar model." Explicitly chooses sidecar/wrapper approach, not modification. |
| GLM-M4 | Chapters 2/6 skeleton constraints could create false positives before extraction gates | **CLOSED** | §2.3 lines 113-117 "Deferred extraction-dependent handling": Ch2 enhanced-index and Ch6 bond requirements are "configuration-side requirements" that "may emit only informational/config findings, not material end-to-end audit failures" until extraction gates exist. §3.4 line 269 confirms overlay tests for these are "configuration tests only." |
| GLM-m1 | `scripts/report_quality_eval.py` should be labeled as existing file, not new | **CLOSED** | §3.2 line 196: "Existing maintainer-only script. Optional and deferrable." |
| GLM-m2 | Top 5 item #5 classification should be `validator consumer` not generic `evidence anchors` | **CLOSED** | §1.2 line 51: classification now reads `validator consumer / evidence-link integrity`. |
| GLM-m3 | Preferred-lens overlay tests should be configuration tests for deferred extraction cases | **CLOSED** | §3.4 line 269: "Enhanced-index and bond overlay tests are configuration tests only in this slice; they should assert the sidecar marks the right requirements and deferred informational/config severity, not reproduce end-to-end extraction failures." |

## New Findings Introduced by Patch

None. The patch addresses all 14 findings without introducing new issues.

The sidecar binding decision (§2.2 lines 70-78) is architecturally sound: it preserves the existing frozen `ChapterContract` as the single machine source, adds a validated wrapper layer for executable audit semantics, and enforces fail-closed consistency between the two. The deferred extraction handling (§2.3 lines 113-117) correctly limits the first slice to active-fund Chapter 3 material behavior. The three-path audit boundary table is clear and non-overlapping.

## Verdict: PASS

All 14 findings (MiMo M1-M3/m1-m4, GLM M1-M4/m1-m3) are closed by the plan patch. The patched plan provides:

1. A binding decision on sidecar architecture that avoids dual-contract truth.
2. Clear three-way audit boundary separation.
3. Explicit coverage targets for new modules.
4. Deferred extraction handling that prevents false positives.
5. Defined terminology for overlay severity.
6. `ReportDataGapOverride` integration point.
7. Explicit design-doc update ownership and acceptance criteria.

The plan is ready for the implementation gate.
