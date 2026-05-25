# Release Maintenance ReportEvidenceBundle Typed Model / Projection — Implementation Plan Review (AgentDS)

> Date: 2026-05-25
> Reviewer: AgentDS (adversarial plan review)
> Gate: `typed ReportEvidenceBundle model/projection implementation plan review`
> Verdict: **PASS_WITH_FINDINGS**

## Reviewed Target

- **Artifact**: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`
- **Scope**: implementation plan only — no code, tests, renderer, FQ0-FQ6, Host/Agent runtime, or fixture promotion

## Truth Sources Audited

| Source | Sections / focus |
|---|---|
| `AGENTS.md` | Module boundaries, hard constraints, fund analysis principles, fallback strategy |
| `docs/implementation-control.md` | Startup Packet, Current Gate, Next Entry Point, Open Residuals, Accepted Decisions |
| `docs/design.md` | §2.1 architecture, §5.4/5.4.1/5.4.2/5.4.3 report-quality design, §7.2/7.3/7.4 quality gate, §12 plan review checklist |
| S2 bundle candidate plan | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md` |
| S2 controller judgment | `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-controller-judgment-20260525.md` |
| `fund_agent/fund/data_extractor.py` | `StructuredFundDataBundle` fields, `FundDataExtractor`, `_classified_fund_type()` |
| `fund_agent/fund/extractors/models.py` | `EvidenceAnchor`, `ExtractedField`, `ExtractionMode`, `EvidenceSourceKind` |
| `fund_agent/fund/fund_type.py` | `FundType` domain, `classify_fund_type()` |
| `fund_agent/fund/template/contracts.py` | `TemplateLensRule`, `ChapterContract`, `resolve_preferred_lens()` |
| `fund_agent/fund/template/lens_application.py` | `LensApplicationPlan`, `build_lens_application_plan()`, `LensFocusLabels` |
| `fund_agent/fund/quality_gate.py` | Quality gate status constants, `QualityGateIssue` |
| `fund_agent/fund/extraction_score.py` | Field priority mapping, score domain |
| `tests/fund/test_extraction_snapshot.py` | Fake bundle construction pattern |
| `tests/fund/test_golden_prefill.py` | `basic_identity.value["classified_fund_type"]` access pattern |

## Assumptions Tested

1. **Frozen dataclass pattern matches current code** — CONFIRMED. `StructuredFundDataBundle`, `ExtractedField`, `EvidenceAnchor`, `TemplateLensRule`, `QualityGateIssue` all use `@dataclass(frozen=True, slots=True)`.

2. **`classified_fund_type` lives in `basic_identity.value["classified_fund_type"]`** — CONFIRMED. `data_extractor.py:_classified_fund_type()` reads from `basic_identity.value.get("classified_fund_type")`. Tests in `test_golden_prefill.py` construct `basic_identity=ExtractedField(value={"classified_fund_type": "active_fund"}, ...)`.

3. **Current `FundType` domain is 6 values** — CONFIRMED. `FundType = Literal["index_fund", "active_fund", "bond_fund", "enhanced_index", "qdii_fund", "fof_fund"]` in `fund_type.py:15-22`.

4. **`EvidenceSourceKind` is `annual_report | external_api | derived`** — CONFIRMED. `extractors/models.py:11`. The plan's mapping table in §Anchor Domains correctly maps these three values.

5. **`build_lens_application_plan()` is a pure function** — CONFIRMED. `lens_application.py:105-132` reads only from in-memory `_FOCUS_LABELS_BY_FUND_TYPE` dict and `resolve_preferred_lens()` (which reads from in-memory CHAPTER_CONTRACT). No IO, no side effects.

6. **Production extraction goes through `FundDocumentRepository`** — CONFIRMED. `data_extractor.py:137` defaults to `FundDocumentRepository()`, line 161 calls `self._repository.load_annual_report()`.

7. **`nav_data` is `NavDataResult`, not `ExtractedField`** — CONFIRMED. `StructuredFundDataBundle.nav_data: NavDataResult` at `data_extractor.py:110`. No `extraction_mode` or `anchors` tuple on `NavDataResult`.

8. **Projection boundary: no repository/PDF/cache call** — VERIFIABLE via the plan's `rg` validation command and test 20.

## Findings

### F-01-未修复-中-Incomplete Dataclass Field Specifications

- **位置**: §Proposed Dataclasses
- **问题类型**: 不可直接实施
- **当前写法**: The plan names 12 dataclasses (`ReportSourceDocument` through `ReportDataGapOverride`) but only specifies partial field lists for 3 of them: `ReportFact` (source_anchor_ids + data_gap_refs), `ReportScoreIssueLink` (10 fields listed), and `ReportEvidenceProjectionContext` (~13 fields listed with descriptions). The remaining 9 classes have no field-level specification in the implementation plan itself.
- **反例/失败场景**: The implementer opens `report_evidence.py`, writes `@dataclass(frozen=True, slots=True) class ReportEvidenceAnchor: ...` and doesn't know which fields to include. The S2 bundle candidate plan (§Evidence Anchors) lists 11 fields for `ReportEvidenceAnchor`, but the implementation plan doesn't replicate or reference those specifications. The implementer must independently cross-reference a 536-line S2 plan to find field definitions scattered across multiple sections.
- **为什么有问题**: The plan claims to be "code-generation-ready" but omits field-level definitions for 75% of its dataclasses. The implementer must reconstruct field lists from:
  - Algorithm steps (e.g., Step 2 gives partial `ReportSourceDocument` fields)
  - S2 bundle plan (separate artifact, different structure)
  - Domain Literal lists (which define value domains but not field-to-domain mappings)
  This creates risk of field omission, naming drift, or inconsistency with the S2 contract.
- **直接证据**:
  - Plan §Proposed Dataclasses lists 12 class names followed by "Important field rules:" with rules for only 3 classes.
  - S2 plan §Source Documents table lists 8 fields for source document records, but plan Step 2 only mentions 7 fields (missing `document_type` from the projection step, though it's set as a literal `annual_report`).
  - S2 plan §Evidence Anchors table lists 11 fields; plan §Anchor Domains defines `ReportAnchorSourceKind` and `SourceStrength` but doesn't map them to dataclass fields.
- **影响**: 实施 Agent 跑偏（field mismatch between projection code and S2 contract）；后续返工（controller rejects implementation for field gaps）
- **建议改法和验证点**:
  1. Add a concise field specification table for each dataclass, or
  2. Add an explicit reference: "For complete field definitions of `ReportSourceDocument`, `ReportEvidenceAnchor`, `ReportDataGap`, `DerivedCalculation`, `ReportQualityContext`, see S2 bundle candidate plan §Source Documents / §Evidence Anchors / §Data Gaps / §Derived Calculations / §Quality Context."
  3. Verify each dataclass has at minimum: (a) a list of field names, (b) their types, (c) which are required vs defaulted.
- **修复风险**: 低 — adding field reference tables or explicit cross-references is editorial.
- **严重程度**: 中 — implementer can recover by reading the S2 plan, but the implementer shouldn't need to synthesize from two artifacts for a plan that claims code-generation-readiness.

### F-02-未修复-低-ReportEvidenceProjectionContext Field Optionality Undefined

- **位置**: §Proposed Dataclasses, `ReportEvidenceProjectionContext` field list
- **问题类型**: 不可直接实施
- **当前写法**: Lists ~13 fields with descriptions like "Required or defaulted fields should include: run_id, corpus_id, fund_type_slot, ..." but never distinguishes which fields are required constructor arguments vs optional with defaults.
- **反例/失败场景**: Implementer writes `ReportEvidenceProjectionContext(run_id=..., corpus_id=...)` and gets a TypeError because `fact_review_status` has no default. Or implementer defaults everything and callers forget to pass critical fields like `source_boundary`, which then silently defaults to a wrong value.
- **为什么有问题**: The plan explicitly says the context "must be an explicit typed context, not a free dict." But without required-vs-optional clarity, the constructor contract is ambiguous.
- **直接证据**: Plan text: "Required or defaulted fields should include: run_id, corpus_id, fund_type_slot, document_identity_status, source_boundary, source_failure_category, fallback_used, review_artifact_refs, fact_review_status, schema_revision_status, quality_context, data_gap_overrides, score_issue_links" — 13 fields listed with no required/optional split.
- **影响**: 实施 Agent 跑偏（wrong defaults, missing validation）；后续返工
- **建议改法和验证点**: Annotate each field as `required` or `optional (default=X)`. At minimum: `run_id`, `corpus_id`, `source_boundary`, `source_failure_category` should be required; `fund_type_slot`, `fallback_used`, `review_artifact_refs`, `data_gap_overrides`, `score_issue_links` can default to `None`/`()`.
- **修复风险**: 低
- **严重程度**: 低

### F-03-未修复-低-chapter_id Type Ambiguity Between int and str in Lens Projection

- **位置**: §Step 4 Project Preferred Lens
- **问题类型**: 不可直接实施
- **当前写法**: Step 4 says to call `build_lens_application_plan(classified_fund_type)` which returns `LensApplicationPlan` with `chapter_id: int` (0-7), then "Convert the returned dataclasses into serializable frozen projection records: ... chapter_id as chapter_0 ... chapter_7".
- **反例/失败场景**: Implementer converts `chapter_id=0` to `chapter_id="chapter_0"` for `ReportPreferredLensChapter`, but then Step 5's gap chapter_ids use the same `chapter_0` format while the ChapterRef domain has both numeric-like strings and `report_level`. The int→string mapping `{0: "chapter_0", 1: "chapter_1", ...}` is trivial but unspecified — implementer might use `f"chapter_{chapter_id}"` or a lookup dict, and the plan doesn't say which.
- **为什么有问题**: Minor but real: the `ChapterRef` domain (Step 3) lists `"chapter_0"` through `"chapter_7"` plus `"report_level"`, confirming the string format, but the conversion function from `int` to this format is an implementation detail that should be mentioned.
- **直接证据**: `lens_application.py:49` — `chapter_id: int`; plan §Step 4 — "chapter_id as chapter_0 ... chapter_7"
- **影响**: 实施 Agent 轻微跑偏（trivial to fix but wastes a round trip）
- **建议改法和验证点**: Note: "Use `f'chapter_{chapter_id}'` to convert int chapter_id to ChapterRef string format."
- **修复风险**: 低
- **严重程度**: 低

### F-04-未修复-低-Test 10 Ambiguity Between ValueError and rejected Bundle

- **位置**: §Test Plan, test 10 (`test_extraction_mode_missing_with_non_null_value_rejects_bundle`)
- **问题类型**: 测试缺口
- **当前写法**: "Assert review_status=="rejected" or ValueError, depending on implementation choice. Prefer returning rejected bundle if all validation issues are represented; prefer ValueError only if the model cannot be constructed safely."
- **反例/失败场景**: Two different implementers write different behaviors. One returns a `rejected` bundle with a validation issue marker; the other raises `ValueError` during construction. The test passes in both cases, hiding a behavioral difference that callers (future Service orchestration) would need to handle differently. If a Service caller expects to always receive a `ReportEvidenceBundle` (even rejected), the `ValueError` path would crash.
- **为什么有问题**: The plan is supposed to be code-generation-ready, not leave design decisions to the implementer. The preference ("Prefer returning rejected bundle") is stated but not encoded as the requirement.
- **直接证据**: Plan test 10 description.
- **影响**: 实施 Agent 做不同选择（behavioral inconsistency）；后续返工（Service integration breaks）
- **建议改法和验证点**: Choose one: either always return rejected bundle (consistent with Step 11 which says `review_status="rejected"` for "extraction mode / value consistency has a hard contradiction") or always raise `ValueError` for truly unconstructable states. The Step 11 derivation table already says this case produces `rejected`, so returning a rejected bundle is the consistent choice.
- **修复风险**: 低
- **严重程度**: 低

### F-05-未修复-低-Anchor Dedup Requires Two-Pass Normalization Not Explicitly Sequenced

- **位置**: §Step 6 Map Anchors and §Step 9 Deterministic Anchor ID Hashing
- **问题类型**: 不可直接实施
- **当前写法**: Step 6 says "Deduplicate anchors by normalized locator object, not by object identity." Step 9 specifies the locator object normalization and hashing. But the plan presents them as sequential steps (6 then 9), while dedup in Step 6 actually requires the normalization logic from Step 9.
- **反例/失败场景**: Implementer follows steps linearly: tries to dedup in Step 6 without having the normalized locator object definition from Step 9. Either they define normalization twice (DRY violation) or they restructure the code to compute normalized locator objects before dedup and before ID assignment.
- **为什么有问题**: The sequential step numbering implies a linear pipeline, but anchor processing has an inherent two-phase dependency: (1) normalize locator objects → (2) dedup by normalized object → (3) hash for IDs → (4) resolve collisions. The plan's structure obscures this.
- **直接证据**: Plan §Step 6 says "Deduplicate anchors by normalized locator object" before §Step 9 defines what "normalized locator object" means.
- **影响**: 实施 Agent 轻微跑偏（implementation structure may need refactoring）
- **建议改法和验证点**: Add a note in Step 6: "Normalization uses the locator object definition from Step 9; compute normalized objects first, then dedup, then assign IDs."
- **修复风险**: 低
- **严重程度**: 低

### F-06-未修复-低-ReportDataGapOverride Has No Field Specification

- **位置**: §Proposed Dataclasses and §Step 8
- **问题类型**: 不可直接实施
- **当前写法**: `ReportDataGapOverride` is listed as a dataclass and used in Step 8 ("Explicit S1 turnover-style gap supplied by ReportDataGapOverride") and test 9, but no fields are ever defined.
- **反例/失败场景**: Implementer writes `@dataclass(frozen=True, slots=True) class ReportDataGapOverride: pass` or guesses fields from the Step 8 example. The test 9 gap id `gap:004393:2024:not_reviewed:manager.turnover_rate:not_reviewed_in_current_slice` implies the override carries at minimum `gap_kind`, `field_path`, `failure_category`, `reason_code`, `chapter_ids`, and `required_report_wording`, but this is never stated.
- **为什么有问题**: A class used in both the algorithm and a required test has zero field specification.
- **直接证据**: Plan lists `ReportDataGapOverride` in the dataclass list; Step 8 references it; test 9 uses it; no field definition anywhere.
- **影响**: 实施 Agent 跑偏（invents wrong fields）
- **建议改法和验证点**: Define `ReportDataGapOverride` fields: at minimum `gap_kind`, `field_path`, `failure_category`, `reason_code`, `chapter_ids`, `required_report_wording`.
- **修复风险**: 低
- **严重程度**: 低

### F-07-未修复-信息-DerivedCalculation Model Defined But Explicitly Not Populated

- **位置**: §Derived Calculation Domains and §Minimal Implementation Slice
- **问题类型**: 切片过粗
- **当前写法**: Domains for `CalculationFormulaName`, `CalculationStatus` are defined. The implementation slice says "The minimal slice may define calculation records and validation, but it should not populate broad calculations beyond explicit score issue linkage or test-local examples."
- **反例/失败场景**: Implementer writes the `DerivedCalculation` dataclass and validation helpers, then the test coverage tool reports uncovered branches because no real calculation population happens. The 80% coverage target may be at risk if significant validation code exists for a feature that's intentionally not used.
- **为什么有问题**: The tension between "define the model" and "don't populate it" is real. Either the calculation model should be deferred to a later slice (cleaner), or the plan should acknowledge the coverage gap explicitly.
- **直接证据**: Plan §Derived Calculation Domains and §Minimal Implementation Slice: "Do not implement: ... broad derived calculations"
- **影响**: 覆盖率缺口（uncovered calculation validation branches）
- **建议改法和验证点**: Either (a) defer `DerivedCalculation` and its domains to a later slice, or (b) add an explicit coverage residual: "Calculation model definition and validation helpers may not reach full branch coverage in this slice; document uncovered branches and owner before gate acceptance."
- **修复风险**: 低
- **严重程度**: 信息 — not a correctness issue, but a coverage/maintainability note for the implementation gate.

## Architecture Boundary Review

**Verdict: PASS.** The plan correctly places all new code in Agent-layer `fund_agent/fund/report_evidence.py`. No Service, renderer, Host, or Agent runtime leakage detected.

- Cross-module import of `build_lens_application_plan()` from `fund_agent.fund.template.lens_application` is legitimate (same layer, same package).
- No `FundDocumentRepository`, PDF, cache, source helper, or download helper access from the projection layer.
- No `extra_payload` / `extra_payloads` / `**kwargs` / free dict catchalls.
- No `dayu.host` / `dayu.engine` import or introduction.
- No renderer or FQ0-FQ6 behavior change.

## Overcoupling Review

**Verdict: PASS.** The plan keeps `ReportEvidenceBundle` as a projection wrapper over `StructuredFundDataBundle` without coupling it to extraction, rendering, quality gate execution, or Host/Agent lifecycle. The projection function signature (`bundle: StructuredFundDataBundle, context: ReportEvidenceProjectionContext`) enforces explicit dependency direction.

## Overengineering Review

**Verdict: PASS with note.** The domain definitions are thorough. 12 dataclasses for a "minimal slice" is substantial but justified by the S2 contract's scope (facts, anchors, gaps, quality context, score linkage, lens projection, review status). The `DerivedCalculation` model is the only part that could be deferred (see F-07).

## Test Sufficiency Assessment

**Verdict: ADEQUATE.** 20 tests cover:
- Happy path: facts projection, lens projection, multi-anchor, scoring_ready
- Edge cases: missing/illegal fund type, slot membership, anchor hash stability/collision
- Data gaps: missing extraction, mode/value contradictions, traceability gaps
- Exclusions: nav_data, ad_hoc corpus
- Review status: priority ordering, deferred states
- Score validation: gap refs, pass+blocking conflict, N/A/chapter_summary semantics
- Boundary: no repository/source helper calls

Gap noted: no explicit test for `classified_fund_type` value being present in `basic_identity.value` but the dict itself not being a mapping (Step 3 edge case). However, this is covered by the implementation logic in Step 3 and test 3's key-removal test.

## Validation Commands

Commands executed against the plan artifact:

```text
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|fund_agent/fund/report_evidence.py|frozen|type_slot_membership_status|source_boundary|source_failure_category|review_status|data_gap_refs|sha256|nav_data|FundDocumentRepository|extra_payload|dayu\.host|dayu\.engine|renderer|FQ0-FQ6" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
```

Result: All expected terms present. No `extra_payload`, `dayu.host`, or `dayu.engine` found in any expansion context. `FundDocumentRepository` appears only in boundary/stop-condition statements, not as an operational call.

```text
git diff --check
```

Result: passes (no whitespace errors).

## Open Questions

None. All review lenses have been applied and findings documented.

## Residual Risks

| Residual | Risk | Suggested tracking |
|---|---|---|
| Dataclass field specs require S2 cross-reference | Implementer may miss or misalign fields | Implementation gate should verify each dataclass field list against S2 plan before acceptance |
| `DerivedCalculation` coverage gap | Uncovered validation branches may block 80% target | Record uncovered branches in implementation review; accept explicitly if deferred |
| `accepted_baseline` domain exists but not derivable | Future code might accidentally derive it | Test 15 verifies `scoring_ready`; the plan's Step 11 and the explicit validation that "accepted_baseline is attempted before a curated-fixture gate" → `rejected` covers this |
| README sync gate scope | `AGENTS.md` says `fund_agent/fund/` changes trigger README update | Plan already flags this as a controller-owned residual; acceptable |

## Conclusion

**PASS_WITH_FINDINGS**

The plan is substantially code-generation-ready. The projection algorithm, domain definitions, ID formats, review status derivation, and test cases are concrete and internally consistent. File ownership respects AGENTS.md module boundaries. No architecture violation, no boundary leakage, no Host/Agent runtime creep.

Six low/medium findings identified:
- F-01 (中): Incomplete dataclass field specifications — implementer must cross-reference S2 plan
- F-02 (低): `ReportEvidenceProjectionContext` field optionality undefined
- F-03 (低): chapter_id int→string conversion ambiguity
- F-04 (低): Test 10 ambiguity between ValueError and rejected bundle
- F-05 (低): Anchor dedup two-pass normalization not explicitly sequenced
- F-06 (低): `ReportDataGapOverride` has no field specification

None of these findings block the implementation gate. All are fixable with minor plan clarifications or can be resolved by the implementer with a single cross-reference to the S2 bundle plan. The plan's stop conditions, validation commands, and boundary assertions are sufficient to catch any material deviation during implementation.
