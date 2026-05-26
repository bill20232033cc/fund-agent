# Plan Review: Chapter Contract Implementation + Report Writing Quality Upgrade Design Plan

> Date: 2026-05-26
> Reviewer: AgentMiMo
> Target: `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md`
> Review type: independent adversarial plan review
> Constraints: no source/test/plan artifact modification; no git add/commit/push; no GitHub mutation

## 1. Review Scope

Three gates reviewed:

- Gate A: Report-Quality Escalation Synthesis — are Top 5 issues backed by direct evidence?
- Gate B: CHAPTER_CONTRACT Executable Constraint Design — are constraints executable, not breaking v0 renderer?
- Gate C: Report Writing Quality Upgrade Plan — minimal slice, test strategy, prohibited boundary respected?

Truth sources consulted:

- `AGENTS.md` (rules authority)
- `docs/design.md` v2.2 (design truth)
- `docs/implementation-control.md` (control truth, current gate, accepted artifacts)
- Accepted evidence artifacts referenced by the plan (7 artifacts verified)
- Current code state of `contracts.py`, `report_evidence.py`, `report_quality_validation.py`, `renderer.py`, `report_quality_eval.py`

## 2. Findings

### 2.1 BLOCKER Findings

None.

### 2.2 MATERIAL Findings

#### M1: Audit module file placement is ambiguous — could delay implementation start

The plan (§3.2) lists two candidate paths for the audit module:

- `fund_agent/fund/report_writing_audit.py`
- `fund_agent/fund/template/chapter_contract_audit.py`

And says "pick one name." However, the lint command (§3.3) uses the first path, and the boundary check (§3.3) uses the second path as alternate. This means the implementation agent must make a binding decision before writing code, but the plan does not provide a decision criterion.

Recommendation: If the audit function operates over `ReportEvidenceBundle` (an Agent-layer fact/evidence model), it belongs at `fund_agent/fund/` level alongside `report_evidence.py` and `report_quality_validation.py`. If it operates over template contract structures, it belongs in `fund_agent/fund/template/`. Given that the plan describes `audit_chapter_contract(bundle, *, rendered_markdown=None)` operating over `ReportEvidenceBundle`, the `fund_agent/fund/report_writing_audit.py` path is the correct default.

Impact: Low-delay material — implementation agent wastes a turn deciding, or picks inconsistently with lint/boundary commands.

#### M2: `docs/design.md` update decision creates a documentation debt tracking gap

The plan (§2.6) correctly defers `docs/design.md` update until after code/tests pass. But it says "the next implementation gate should update docs/design.md" without specifying who owns that update or what the acceptance criteria are. The implementation scope table (§3.2) lists `docs/design.md` as an allowed file, but the stop conditions (§3.5) say stop if "docs/design.md would need to describe future behavior as current code fact."

These two statements are in tension: the plan allows design.md modification in the implementation scope, but the stop condition blocks it if the content is future-behavior. The boundary is: design.md update must describe the new code as "dev-only executable audit layer" (current code fact), not as "CHAPTER_CONTRACT now enforces X at runtime" (future behavior).

Impact: Non-blocking if the implementation agent understands the boundary, but the plan could be more explicit about the exact narrow update scope (e.g., "add one sentence to §3.2 stating dev-only executable audit exists with required_evidence, allowed_na_reason, failure_behavior; do not claim runtime, renderer, FQ0-FQ6, or LLM audit integration").

#### M3: Test coverage target not explicitly stated

AGENTS.md requires "单文件测试覆盖率目标为 ≥80%；这是新增或大幅修改模块的评审目标." The plan specifies focused tests and adjacent test suites but does not state an explicit coverage target for the new modules (`chapter_contract_constraints.py`, `report_writing_audit.py`). The CI gate is `--cov-fail-under=50` which is too low for new modules.

Impact: Minor risk that new modules ship below 80% without reviewer notice. The plan's test strategy is otherwise comprehensive.

### 2.3 MINOR Findings

#### m1: `audit_chapter_contract` vs existing `run_programmatic_audit` relationship not explicitly stated

The plan introduces `audit_chapter_contract(bundle, *, rendered_markdown=None, fund_type=None)` as a new Fund-layer audit function. The existing `run_programmatic_audit(input: ProgrammaticAuditInput) -> ProgrammaticAuditResult` already executes C2 contract rules over rendered Markdown.

The plan implies these are distinct (dev-only semantic audit vs runtime marker audit) but does not explicitly state the relationship. An implementation agent might try to integrate or deduplicate.

Suggested clarification: `audit_chapter_contract` checks report-writing-level semantic constraints (required evidence, data gaps, claim safety) over the evidence bundle, while `run_programmatic_audit` checks renderer-level literal markers over rendered Markdown. They are complementary, not overlapping.

#### m2: Optional items (§3.2 scripts/test_scripts) could be explicitly marked as deferrable

The plan lists `scripts/report_quality_eval.py` modification and `tests/scripts/test_report_quality_eval.py` as optional. This is fine, but could be more explicit: "Optional. Only add the chapter-audit summary flag if the implementation agent has capacity; defer without blocking the gate."

#### m3: Overlay severity rule (§2.4) uses "core" without defining the term

The fund-type overlay severity rule says "If the fund-type overlay marks a requirement as core..." but the overlay table (§2.4) does not use the word "core" — it uses phrases like "require," "cannot claim," "require both." The mapping from table language to the severity rule's "core" label is implicit.

#### m4: The plan does not mention `ReportDataGapOverride.required_report_wording` integration

The first improvement slice implementation (accepted at Gate D) introduced `ReportDataGapOverride.required_report_wording` to preserve insufficiency wording. The new audit function should consume or reference this structure when checking Chapter 3 active-fund gap wording. The plan does not explicitly mention this integration point.

## 3. Evidence Checked

### 3.1 Gate A Evidence Verification

| Claim | Evidence source | Verified? |
|---|---|---|
| Top 1: 004393 active chapter_3 turnover_rate explicit absence | quasi-real bundle evidence (issue:004393:2024:chapter_3:fact_coverage:turnover_rate:material, next owner chapter_contract) | Yes |
| Top 2: 004393 active chapter_3 renderer asymmetry | first improvement slice controller judgment (safe option, runtime required item deferred) | Yes |
| Top 3: 004194 enhanced_index chapter_2 tracking_error | small baseline controller judgment (failure category data/source extraction) | Yes |
| Top 4: 006597 bond chapter_6 risk.bond_lens | small baseline controller judgment (failure category data/source extraction) | Yes |
| Top 5: combined JSONL RQV_REF_MISSING=4 | small baseline controller judgment Gate B (fixed by nearest-preceding-bundle ownership) | Yes |
| Gate A conclusion: chapter contract before extraction/renderer | aligns with control doc current decisions and Gate D escalation decision | Yes |

All Top 5 claims trace directly to accepted evidence artifacts. No indirect evidence used.

### 3.2 Gate B Design Verification

| Claim | Truth source | Verified? |
|---|---|---|
| Design objective aligns with AGENTS.md CHAPTER_CONTRACT goal | AGENTS.md: "让一个会犯错、会走捷径、上下文有限、偏好模式匹配的推理器，在最低认知负担下稳定做对下一步动作" | Yes |
| Must not change renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu | plan §2.1, §2.5; control doc non-goals | Yes |
| Dev-only first slice | plan §2.2: "library-only...not wired into product CLI or quality gate defaults" | Yes |
| Chapter 3 active-fund turnover constraint fully implemented in first slice | plan §2.5; aligns with accepted first improvement slice contract wording | Yes |
| Base skeleton for chapters 0-7 | plan §2.5: "Add base skeleton constraints for Chapters 0-7" | Yes |
| preferred_lens/fund_type overlay table | plan §2.4; aligns with design.md §3.4 preferred_lens table | Yes |
| Future design correctly separated | plan §2.5 future design section; renderer promotion gated by audit evidence | Yes |
| docs/design.md update deferred | plan §2.6; correct sequencing (code-first, doc-after) | Yes |

### 3.3 Gate C Implementation Verification

| Claim | Truth source | Verified? |
|---|---|---|
| Smallest implementable slice | aligns with Gate D escalation decision: active chapter 3 claim safety is the highest-priority localized issue | Yes |
| No renderer change in first slice | plan §3.1; control doc non-goal "Do not change current v0 renderer" | Yes |
| Prohibited files list complete | plan §3.2; cross-checked against AGENTS.md module boundaries | Yes |
| Acceptance tests cover required scenarios | plan §3.4; covers 7 areas: completeness, anchors, forbidden advice, N/A, data_gap, judgment, preferred lens | Yes |
| Stop conditions align with AGENTS.md boundaries | plan §3.5; all stop conditions reference AGENTS.md constraints | Yes |
| Current code state verified | contracts.py, report_evidence.py, report_quality_validation.py, renderer.py, report_quality_eval.py all exist; proposed new files do not exist | Yes |

### 3.4 Boundary Compliance Check

| Boundary | Status | Evidence |
|---|---|---|
| UI -> Service -> Host -> Agent four-layer | PASS | New code is Fund-layer (Agent layer); no Service/UI/Host changes |
| renderer.py not modified | PASS | In prohibited files list |
| FQ0-FQ6 not modified | PASS | In prohibited files list |
| Service/CLI not modified | PASS | In prohibited files list |
| FundDocumentRepository not accessed | PASS | audit is pure over ReportEvidenceBundle |
| Host/Agent packages not created | PASS | In prohibited files list |
| dayu.host/dayu.engine not introduced | PASS | Boundary rg check in §3.3 |
| Product entry points not changed | PASS | pyproject.toml in prohibited files list |
| No scratch output promotion | PASS | Plan §3.2 prohibited files |

## 4. Verdict

**PASS_WITH_FINDINGS**

The plan is evidence-backed, correctly scoped, and respects all hard boundaries. Gate A's Top 5 issues are supported by direct evidence from accepted artifacts. Gate B's executable constraint design is a natural Fund-layer extension of the existing CHAPTER_CONTRACT mechanism that correctly defers runtime integration. Gate C selects the minimal slice targeting the highest-priority localized issue.

Three material findings (M1-M3) and four minor findings (m1-m4) are identified. None are blockers. M1 (file placement ambiguity) should be resolved before implementation starts. M2 and M3 are guidance improvements that reduce implementation friction.

The plan is ready for implementation with the recommended clarifications applied.
