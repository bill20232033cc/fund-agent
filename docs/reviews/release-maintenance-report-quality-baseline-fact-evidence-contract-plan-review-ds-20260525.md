# Release Maintenance Report-Quality Baseline / Fact-Evidence Contract Plan Review (DS)

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract candidate selection / plan-review`
> Reviewer: AgentDS (independent plan reviewer)
> Reviewed artifact: `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md`

## Verdict

**PASS_WITH_FINDINGS** — 5 findings, none blocking.

## Scope

This review covers the plan artifact only, assessed against:

- `AGENTS.md` hard constraints
- `docs/design.md` §5.4–§5.4.3 (accepted future design direction)
- `docs/implementation-control.md` Startup Packet / Current gate / Next entry point
- Accepted artifacts: chapter-audit pipeline design implementation (2026-05-24), methodology coverage matrix plan and implementation (2026-05-25)

This review does not: change the plan, change code, commit, push, or open a PR.

## Executive Summary

The plan correctly defines a small baseline corpus selection approach, a report-quality scoring schema, a Fact/Evidence input contract, and a concrete data-source vs template-writing decision standard. It respects all hard constraints: four-layer boundary, no renderer/quality-gate/Host/Agent changes, FundDocumentRepository boundary for facts, explicit parameter discipline, fallback taxonomy, and artifact policy. Five findings below: one MEDIUM ambiguity that should be resolved before code implementation, and four LOW completeness gaps.

---

## Findings

### Finding 1 — MEDIUM — Score record `source_boundary` field undefined

- **Location**: plan line 141
- **Evidence**: The score record shape lists `source_boundary` as a field, but the plan never defines its value domain, purpose, or relationship to `source_kind` (EvidenceAnchor, line 262) or `extraction_mode` (facts, line 228).
- **Risk**: Implementation ambiguity — future implementer doesn't know whether this refers to repository boundary classification, source system identity, or something else.
- **Recommendation**: Define `source_boundary` as an enum or literal set before code implementation. Suggested values: `repository_derived` (facts from extractors/FundDocumentRepository), `derived_calculation`, `external_official`, `manual_review`. Not consistent across dimensions — e.g., `evidence_traceability` scoring uses `missing_anchor`, which has a different source_boundary semantics than `wrong_value`.
- **Blocking**: No. Resolvable in the implementation gate's dataclass design.

### Finding 2 — LOW — `evidence_anchor_id` (singular) in score record vs `source_anchor_ids` (plural) in facts

- **Location**: plan lines 141 (`evidence_anchor_id`) vs 227 (`source_anchor_ids`)
- **Evidence**: Score record uses singular `evidence_anchor_id`, suggesting one-to-one. Fact record uses plural `source_anchor_ids`, suggesting one-to-many. Evidence bundle uses `evidence_anchors` (plural collection). These naming inconsistencies will surface during dataclass design.
- **Risk**: Low. A fact may have multiple anchors (e.g., fee rate confirmed by both §1 and §2). A score issue may reference one specific anchor that failed. The semantics differ, so different cardinalities are correct, but the naming convention drift (`evidence_anchor_id` vs `source_anchor_ids` vs `evidence_anchors`) should be harmonized.
- **Recommendation**: Normalize to one prefix (`evidence_anchor_*` or `source_anchor_*`) and distinguish by cardinality suffix (`_id` vs `_ids`).
- **Blocking**: No.

### Finding 3 — LOW — `ReportEvidenceBundle.review_status` overlaps with per-fact `review_status`

- **Location**: plan lines 209 (bundle-level `review_status`) vs 229 (fact-level `review_status`)
- **Evidence**: Both levels carry `review_status`. The plan does not state whether bundle-level status is derived from fact-level statuses (e.g., bundle is `reviewed` only when all facts are `reviewed`) or independently set.
- **Risk**: If implementers set bundle-level status independently, scoring may consume a bundle marked `reviewed` while individual facts inside it are still `generated`.
- **Recommendation**: Add a derivation rule: bundle `review_status` is the minimum status across all contained facts, anchors, and calculations; or add an explicit invariant in the implementation gate.
- **Blocking**: No.

### Finding 4 — LOW — `StructuredFundDataBundle` (current) to `ReportEvidenceBundle` (future) relationship unaddressed

- **Location**: plan Slice 3 (lines 188–307)
- **Evidence**: The plan defines `ReportEvidenceBundle` as the future evidence input. Current code already has `StructuredFundDataBundle` in `fund_agent/fund/data_extractor.py`, which aggregates profile/performance/manager/holdings/share-change/nav data. The plan does not address whether `ReportEvidenceBundle` subsumes, wraps, or replaces `StructuredFundDataBundle`, nor whether the existing bundle should evolve toward the new contract.
- **Risk**: If the two bundles diverge into parallel representations of the same facts, future implementation will face a migration or dual-path maintenance problem.
- **Recommendation**: In the implementation gate, explicitly decide: (a) `ReportEvidenceBundle` consumes `StructuredFundDataBundle` as its fact source, (b) `StructuredFundDataBundle` evolves into `ReportEvidenceBundle` over time, or (c) they serve different gates and coexist. Decision (a) is most consistent with the plan's stated boundary (facts come from current extractors / FundDocumentRepository).
- **Blocking**: No.

### Finding 5 — LOW — `fq_gate_status` values not cross-referenced with code

- **Location**: plan line 300
- **Evidence**: Plan lists `fq_gate_status` values as `pass, warn, block, not_run`. From `docs/design.md` §7.4, the `QualityGateResult` has these semantics; `not_run` is a Service-level derivation when gate isn't executed (e.g., fund not in selected pool). The plan's value set is consistent with design, but the plan does not cite the source for these values.
- **Risk**: If the gate result type evolves independently, `fq_gate_status` in `quality_context` could desync. Low risk because quality gate semantics are contract-hardened.
- **Recommendation**: Add a one-line citation to `docs/design.md` §7.4 or the quality gate final judgment contract implementation artifact.
- **Blocking**: No.

---

## Positive Confirmations

The following constraints are satisfied with evidence:

### Architecture (four-layer boundary)
- Plan §Current Architecture Boundary (lines 24–39) explicitly states `UI -> Service -> Host -> Agent`.
- Lines 36–38 correctly gate any future Host to `dayu.host` and Agent execution to `dayu.engine`.
- Lines 344–345 explicitly forbid creating `fund_agent/host` or `fund_agent/agent` in this gate.
- Verified: `fund_agent/host/` and `fund_agent/agent/` directories do not exist on disk; plan correctly scopes them out.

### Renderer and quality gate immutability
- Lines 340–341: no renderer changes.
- Lines 120–121, 342: scoring schema is observational, must not replace FQ0-FQ6.
- Verified against `docs/design.md` §5.4: scoring is additive, not replacement.

### FundDocumentRepository boundary
- Lines 79–88 explicitly forbid direct PDF/cache/source-adapter access outside repository.
- Line 232: facts must come from current extractors or FundDocumentRepository-derived sources.
- Verified: `FundDocumentRepository` exists at `fund_agent/fund/documents/repository.py:267`.

### Fallback taxonomy
- Lines 77, 290: fallback only for `not_found` / `unavailable`; fail closed for `schema_drift` / `identity_mismatch` / `integrity_error`.
- Consistent with `AGENTS.md` lines 209–219 and `docs/design.md` §6.1.

### Explicit parameter discipline
- Line 39: explicit business parameters must be typed fields, not `extra_payload` / `extra_payloads`.
- Line 211: all business fields in `ReportEvidenceBundle` must be explicit typed fields.
- Verified: zero `extra_payload` / `extra_payloads` usage exists in codebase as actual parameter passing — all 8 occurrences are docstring reminders stating the prohibition.

### Methodology matrix alignment
- Plan §Slice 2 (lines 177–186) cites `docs/design.md` §5.4.3 for every dimension.
- Morningstar dimensions are coverage lenses only, no medal/star/rating output.
- Fund type priority changes scoring denominator.
- Evidence source hierarchy preserved.
- Missing facts degrade to `未披露` / `数据不足` / `下一步最小验证问题`.

### 8-to-0-10 boundary
- Plan §Slice 5 (lines 327–338) correctly treats this as a future gate.
- Lines 340–341: no current renderer rewrite.
- Line 337: exact split remains a later design gate.

### Artifact policy
- Lines 107–116: local runs stay in ignored `reports/*-runs/`, `reports/smoke/`, or temp dirs.
- Durable artifacts limited to this plan, review artifacts, and separately approved curated fixtures.

### Engineering baseline
- Plan review checklist line 362 mentions pyproject.toml baseline checks.
- Verified: `pyproject.toml` at repo root satisfies Python `>=3.11`, setuptools, explicit dependencies, optional `test`/`dev` separation, pytest/ruff/black tool entries. `[tool.setuptools.package-data]` section is absent but this plan introduces no non-Python assets, so no declaration is needed at this gate.
- No `dayu.host` / `dayu.engine` dependency declared; consistent with current deterministic path.

### Decision standard executability
- Plan §Slice 4 (lines 309–325) provides a concrete decision matrix with 9 failure-pattern rows, each mapping to a specific next gate.
- Tie-breaker (line 325): data-source/extraction correctness precedes template writing — a polished template on wrong facts worsens decision safety.
- Each failure pattern has a distinct root-cause interpretation and next gate, making it executable rather than subjective.

### Fact/Evidence contract field sufficiency
- `facts` (10 fields): fact_id, category, value, raw_value_ref, unit, period, source_anchor_ids, extraction_mode, review_status, failure_category. Sufficient for scoring `extraction_correctness` and `fact_coverage`.
- `derived_calculations` (8 fields): calculation_id, formula_name, input_fact_ids, input_anchor_ids, output_value, assumptions, calculation_status, degradation. Sufficient for `R=A+B-C` and thermometer attribution.
- `evidence_anchors` (9 fields): anchor_id, source_kind, document_year, section_id, page_number, table_id, row_locator, source_strength, note. Sufficient for `evidence_traceability` scoring.
- `data_gaps` (9 fields): gap_id, related_fact_id, chapter_ids, failure_category, fallback_allowed, fallback_used, degradation_text, blocks_scoring_dimensions. Sufficient for explicit gap tracking.
- `quality_context` (6 fields): fq_gate_status, fq_issues, programmatic_audit_status, report_quality_scores, known_residuals, judgment_constraint. Sufficient for confidence/warning/blocking semantics.

---

## Recommendation

Accept the plan for implementation. Resolve Finding 1 (`source_boundary` definition) during the implementation gate's dataclass design. Findings 2–5 are editorial and can be resolved inline during implementation without a separate plan amendment.

No blocking findings. Proceed to implementation gate per the plan's Executable Next Gate Proposal (lines 366–378), starting with S0 corpus-selection evidence.

---

## Validation

```text
rg -n "report-quality baseline|Fact / Evidence|ReportEvidenceBundle|FundDocumentRepository|extra_payload|dayu.host|dayu.engine|CHAPTER_CONTRACT|0-10|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-ds-20260525.md
```

No `pytest` or `ruff` needed — this artifact changes no executable code.
