# Docling Dedicated Extractor Template-field Mapping Plan — AgentDS Review — 2026-06-17

Status: `PLAN_REVIEW_COMPLETE_NOT_READY`
Role: AgentDS plan reviewer
Review target: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md`

## Review Method

- Read plan target.
- Read authoritative rules: `AGENTS.md`, `docs/design.md` (Docling/FundDataExtractor/candidate sections), `docs/implementation-control.md` (current active gate).
- Read source-of-truth code: `fund_agent/fund/documents/candidates/representation_models.py`, `fund_agent/fund/documents/candidates/__init__.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/data_extractor.py`.
- Applied adversarial pass: what breaks if this plan is executed as written?

## Finding 1 — Direction transition: GENUINE, NOT BLOCKED

The plan explicitly stops the baseline-qualification/residual-closure route and switches to direct Docling + dedicated extractor development. The motivation cites accepted residual-closure evidence `edf1c68` as proof the old route is blocked.

**Verified**: `edf1c68` exists in git history as "gateflow: accept docling reference bundle residual closure reevidence."

**Verified**: The user has explicitly redirected away from baseline qualification per the review context.

The plan does **not** reference the current `Docs/reviews/implementation-control.md` active gate (`Docling Field Correctness Comparative Evidence Gate`). The controller will need to explicitly close or suspend the current active gate when accepting this plan. This is a handoff gap but not a plan-level blocker — the plan correctly states its new direction and the controller can handle the transition.

**Verdict**: Pass. The directional change is genuine and motivated by accepted evidence.

## Finding 2 — FundDataExtractor boundary: CORRECT, NOT A BLOCKER

The plan states: "No implementation change to FundDataExtractor in this gate."

**Verified against design.md constraints**:

- Line 662: Docling "只能作为 extractor / projection 的输入层；不得跳过自研 extractor、章节事实投影、EvidenceAnchor 校验或 fail-closed 分类直接喂给 Service、Host、renderer、quality gate 或 LLM prompt。"
- Line 666: "Docling 或其它文档中间层必须封装在 FundDocumentRepository / Fund documents 层内部。"
- Line 78: `FundDataExtractor.extract()` is the P1 production structured extraction entry point.

The plan correctly isolates the new extractor inside `fund_agent/fund/documents/candidates/` — inside Fund documents candidate internals, not in the production extraction path. Not touching `FundDataExtractor` prevents Docling from becoming a de facto parser replacement before the extractor has field-level no-live evidence.

The plan's rationale is sound: "direct production integration would make Docling a parser replacement path before the dedicated extractor has field-level no-live evidence." Integration is deferred to a later gate after the extractor contract is proven.

**Verdict**: Pass. This is the correct boundary under current design.md constraints.

## Finding 3 — Target fields and output contract: CONCRETE ENOUGH

**Target fields**: 16 field groups mapped to specific source sections (§2, §3, §4, §7, §8, §10) with explicit output types. Missing fields must be explicitly emitted as `extraction_mode="missing"`.

**Output contract**:

- `CandidateTemplateField`, `CandidateTemplateFieldAnchor`, `DoclingTemplateFieldExtractionResult` are fully specified with frozen/slots dataclasses.
- Public function `extract_docling_template_fields()` has typed signature.
- Invariants are listed: reject non-Docling sources, reject non-candidate-proof documents, one field per target path, missing requires explicit note, direct requires at least one anchor.
- Matching rules are classified into 4 rule families with normalization described.

**Minor concern**: The field table says `investment_objective` and `investment_scope` source is "§2 profile/objective text **or** key-value table." The "or" leaves matching priority ambiguous — the implementation will need to decide fallback order. This is an implementation detail, not a plan defect.

**Minor concern**: `CandidateTemplateFieldAnchor.source_kind` is `Literal["annual_report"]` — the same literal as production `EvidenceAnchor.source_kind`. The candidate-only distinction is carried by the parent `CandidateTemplateField.candidate_only` and `source_truth_status`, not by the anchor type. An implementation could accidentally treat candidate anchors as production anchors if the parent field's status is ignored. The plan should emphasize this type-level distinction in the implementation gate.

**Verdict**: Pass. Contract is concrete enough for implementation.

## Finding 4 — File ownership: CORRECT

Proposed files:

| File | Owner | Verdict |
|------|-------|---------|
| `fund_agent/fund/documents/candidates/template_field_extraction.py` | Fund documents candidate internals | Correct — matches existing `candidates/` package boundary |
| `tests/fund/documents/test_docling_template_field_extraction.py` | Test mirror | Correct |
| `docs/reviews/...implementation-evidence...` | Review artifact | Correct |
| `fund_agent/fund/documents/candidates/__init__.py` | Optional export | Correct — existing `__init__.py` exists and declares candidate-only scope |

**Verified against AGENTS.md module boundaries**: The new code "理解基金类型、财报章节" and maps Docling representation to template fields — this belongs in Agent layer `fund_agent/fund`. The plan does not leak into Service/Host/UI layers.

**Verified against existing code**: `fund_agent/fund/documents/candidates/` already contains `representation_models.py`, `representation_projection.py`, `evidence_anchor_mapping.py` etc. The new file is consistent with existing module organization.

**Verdict**: Pass.

## Finding 5 — Scope sizing: REASONABLE

3 slices across 16 field groups:

1. Slice 1 — Contract + field registry + validation helpers (infrastructure, no field logic)
2. Slice 2 — Profile + fee fields (8 fields, key-value + label matching)
3. Slice 3 — Performance + manager + holdings (8 fields, table-family guarded + fail-closed rules)

Each slice has explicit allowed changes and test requirements. The matching rules are deterministic (no LLM), so each slice is self-contained and testable with synthetic data.

**Verdict**: Pass. The scope is well-decomposed and not too large for one implementation gate.

## Finding 6 — Preserves NOT_READY / no source truth / no parser replacement: CORRECT

Verified all explicit constraints:

- `candidate_only=true` — in `CandidateTemplateField` and `DoclingTemplateFieldExtractionResult`
- `source_truth_status=not_proven` — enforced at type level (`Literal["not_proven"]`)
- Release/readiness remains `NOT_READY` — stated in non-goals
- No parser replacement — stated in non-goals, FundDataExtractor not modified
- No live/network/provider/LLM — stated in non-goals
- No design/control/readme update — stated in Docs Decision
- Validation commands are no-live only: `pytest`, `ruff`, `git diff --check`

**Verdict**: Pass.

## Residual Observations (non-blocking)

1. **No consumption path**: The extractor produces `DoclingTemplateFieldExtractionResult` but nothing consumes it. The implementation gate will produce code with zero production impact. The plan acknowledges this as a residual risk and defers integration. The controller should confirm this isolation-first approach is acceptable for this gate.

2. **Anchor type-level candidate distinction**: `CandidateTemplateFieldAnchor` uses `source_kind: Literal["annual_report"]` — same literal as production `EvidenceAnchor`. The implementation should enforce that candidate anchors are never treated as production anchors at the type or validation level, not just documentation.

3. **Plan doesn't close/suspend current active gate**: The current `implementation-control.md` active gate is `Docling Field Correctness Comparative Evidence Gate`. The controller will need to explicitly transition when accepting this plan.

## Verdict

PLAN_REVIEW_PASS_NOT_READY
