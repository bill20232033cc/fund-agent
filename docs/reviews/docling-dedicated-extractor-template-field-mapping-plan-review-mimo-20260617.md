# Docling Dedicated Extractor Template-field Mapping Plan Review (MiMo) - 2026-06-17

Status: review artifact
Review target: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md`
Reviewer: AgentMiMo
Classification: heavy plan review

## Review Scope

Material blockers only. Six focus questions from user instruction.

## 1. Does the plan genuinely transition to the user's target?

**Verdict: YES, not blocked.**

Plan explicitly states: stop baseline-qualification residual-closure route, switch to direct development of a Docling-specialized extractor that maps candidate representation into template target fields. The first-principles judgment section (lines 29-34) correctly identifies that the old route is blocked by missing comparable producer diagnostics and proposes a different question: "Given a Docling candidate document representation, can we extract template target fields better than the current generic parser path for selected fields?"

This is a genuine pivot, not a candidate-only research detour. The deliverable is a usable extractor surface with concrete field coverage.

**Non-blocking observation:** The plan still uses heavy `candidate_only` / `source_truth_status=not_proven` language throughout. This is architecturally correct given current constraints, but the user should confirm whether they want the plan to also authorize a follow-up integration gate that connects the new extractor to `FundDataExtractor` or report generation, or whether that remains explicitly deferred.

## 2. Is not modifying FundDataExtractor in this gate a correct boundary or a blocker?

**Verdict: CORRECT BOUNDARY, not a blocker.**

Reasoning (lines 111-113): direct production integration would make Docling a parser replacement path before the dedicated extractor has field-level no-live evidence. This is sound:

- The new `CandidateTemplateField` / `CandidateTemplateFieldAnchor` types are deliberately NOT production `ExtractedField` / `EvidenceAnchor`. They live in `candidates/` and carry `candidate_only=True`.
- Connecting to `FundDataExtractor` prematurely would bypass the design constraint that fund facts must pass through self-owned extractor / EvidenceAnchor / fail-closed classification before report consumption (design.md line 666).
- The safe transition sequence is: build extractor contract -> get no-live field evidence -> authorize integration in a later gate.

**Non-blocking observation:** The plan does not specify what the future integration path looks like. A brief note on "how CandidateTemplateField maps to ExtractedField in a later gate" would reduce integration ambiguity, but this is not a blocker for the current gate.

## 3. Are target fields and output contract concrete enough for implementation?

**Verdict: MOSTLY CONCRETE, two gaps identified.**

Concrete elements:
- 16 target fields across 5 groups (`profile`, `manager`, `holdings`, `performance`) with source section/table mapping (lines 78-96).
- Three frozen dataclasses with explicit fields and types (lines 119-154).
- Public function signature with default target field paths (lines 159-165).
- Six explicit invariants (lines 168-175).
- Five deterministic matching rule families (lines 180-188).

**Gap 1 — `field_path` naming convention not specified:**
The plan maps target fields to `StructuredFundDataBundle` / `SNAPSHOT_FIELD_ORDER` subfields but does not define the exact `field_path` string values. Examples: is `basic_identity.fund_name` the literal `field_path`? Is `fee_schedule.management_fee` dot-notation? The `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` constant needs concrete values. This is resolvable during Slice 1 implementation but should be pinned down in the plan to avoid ambiguity across slices.

**Gap 2 — Boundary with existing `evidence_anchor_mapping.py` unclear:**
`evidence_anchor_mapping.py` already maps candidate blocks to `CandidateEvidenceAnchorMapping` with section/table/cell granularity. The new module goes deeper (field-level extraction within mapped sections). The plan should explicitly state the relationship: does `template_field_extraction.py` consume `CandidateEvidenceAnchorMapping` results, or does it operate independently on `CandidateRepresentationDocument`? The current plan implies the latter (line 159: takes `CandidateRepresentationDocument` as input), which means some section-resolution logic may be duplicated. Not a blocker, but should be a documented design decision.

## 4. Is file ownership correct under AGENTS/design boundaries?

**Verdict: CORRECT.**

- `fund_agent/fund/documents/candidates/template_field_extraction.py` — correct location for candidate-only extractor internals.
- `tests/fund/documents/test_docling_template_field_extraction.py` — correct test location.
- `__init__.py` modification only if export is required by tests — correct, minimal.
- No changes to `docs/design.md`, `docs/implementation-control.md`, READMEs, or release/readiness state — correct for a no-live candidate implementation gate.
- No changes to `FundDataExtractor`, `Service`, `UI`, `Host`, `renderer`, or `quality gate` — correct boundary.

## 5. Is the scope too large for one implementation slice?

**Verdict: SLICE 3 IS DENSE but not blocking.**

- Slice 1 (contract + registry): pure dataclass and validation — small, low risk.
- Slice 2 (profile + fee fields): 9 fields, key-value and label matching — moderate, well-scoped.
- Slice 3 (performance + manager + holdings skeleton): 7 fields covering performance table, tracking error, manager table, manager holding alignment, and first holdings rows with fail-closed hierarchy rules — this is the densest slice.

Slice 3 covers heterogeneous extraction logic (table parsing for performance, text discrimination for tracking error, table parsing for manager, cross-table alignment for manager holding, row-level hierarchy for holdings). If slice 3 proves too large during implementation, it can be split into 3a (performance + tracking error) and 3b (manager + holdings). The plan does not need to change for this — it's an implementation-time decision.

**Non-blocking observation:** `manager_strategy_text` is in `SNAPSHOT_FIELD_ORDER` (manager group) but is not listed in the plan's target field table. This is intentional (not covered in first slice) but should be noted in the explicit missing-field paths to avoid silent omission.

## 6. Does the plan preserve NOT_READY / no source truth / no parser replacement correctly?

**Verdict: YES, fully preserved.**

- `candidate_only=true` on all outputs (lines 48, 149, 173).
- `source_truth_status=not_proven` enforced on all types (lines 49, 150, 174).
- Release/readiness remains `NOT_READY` (line 55).
- Non-goals explicitly list: no baseline promotion, no production parser replacement, no source truth acceptance, no full field correctness claim (lines 38-48).
- Reject documents whose candidate/source truth/parser replacement status is not `not_proven` / `not_authorized` (line 171).
- No field may claim source truth or readiness (line 175).
- Docs/design/control not updated in implementation gate (lines 256-261).

## Material Blockers

**None identified.** The plan is implementable as written with the two gaps noted above (field_path naming convention, boundary with evidence_anchor_mapping.py) resolvable during Slice 1 implementation.

## Non-blocking Observations Summary

1. `field_path` naming convention should be pinned in the plan (not just during implementation).
2. Relationship with `evidence_anchor_mapping.py` should be explicitly stated (independent operation on `CandidateRepresentationDocument`, not consuming mapping results).
3. `manager_strategy_text` should be in the explicit missing-field paths list.
4. Slice 3 is dense; can be split at implementation time if needed.
5. No future integration path sketch for connecting to `FundDataExtractor` — acceptable for this gate but should appear in a later gate's plan.

---

PLAN_REVIEW_PASS_NOT_READY
