# Evidence Confirm Productionization RR-09 A3 Coarse-reference / Bond-risk Anchor Fix Plan

Verdict token:

`RR_09_A3_FIX_PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope

Gate: `RR-09 A3 Coarse-reference / Bond-risk Anchor Fix Planning Gate`.

This is a planning-only artifact. It does not authorize implementation, live/PDF execution, product CLI execution, provider/LLM calls, checklist support, report-body rendering, quality-gate semantic changes, tag, release or readiness promotion.

Accepted input:

- A2-S2 evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a2-value-match-diagnostic-evidence-20260624.md`.
- A2-S2 controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a2-controller-judgment-20260624.md`.
- Current control truth: `docs/current-startup-packet.md` and `docs/implementation-control.md`.
- Current source code facts:
  - `fund_agent/fund/evidence_confirm_sources.py` owns annual-report reference materialization from already-loaded `ParsedAnnualReport`.
  - `fund_agent/fund/chapter_facts.py` owns projection from `StructuredFundDataBundle` to `ChapterFactProjection`.
  - `fund_agent/fund/extractors/models.py` defines `BondRiskEvidenceAnchorRef` and `BondRiskEvidenceValue`.

## Goal

Turn the A2-S2 deterministic V2 residual classification into implementation-ready slices that move R1-R4 toward strict deterministic V2 pass without weakening Evidence Confirm.

The target behavior after later accepted implementation and separate live/PDF re-evidence:

1. `structured.bond_risk_evidence` group/internal anchors can be projected into chapter-level annual-report anchors when the extractor value carries valid `BondRiskEvidenceValue.anchors`.
2. Existing section/table coarse-reference fallback remains available for source-support continuity, but current value-match failures are narrowed where the already-loaded `ParsedAnnualReport` contains a safe row/table excerpt that actually carries the relevant fact value.
3. V2 thresholds, proof predicates, source-truth admission, ECQ/quality-gate status semantics and product runtime behavior remain unchanged.

## Motivation

A2-S2 accepted these facts:

- R1-R4 load through EID `single_source_only`, fallback disabled/unused, metadata admitted.
- Reference materialization now passes with nonzero references.
- Strict deterministic V2 still fails for all four samples.
- The dominant classification is `coarse_reference_insufficient`; R3 also has `bond_risk_group_anchor_projection_gap`.

Therefore the next fix must improve projection/materialization precision. It must not reinterpret V2 failure as product fact falsity, and must not relax V2.

## Success Signals

No-live implementation acceptance should require all of the following before any live/PDF re-evidence:

- Existing A1-C behavior remains: semantic row locators that cannot be made row-precise still materialize safe section/table references with informational downgrade issues.
- Bond-risk `BondRiskEvidenceValue.anchors` are converted into valid `ChapterEvidenceAnchor` entries for chapters that include `bond_risk_evidence`, and the `structured.bond_risk_evidence` fact references those chapter anchor IDs.
- The writer prompt no longer needs to warn that bond-risk internal anchors are categorically not `ChapterEvidenceAnchor` after the projection conversion is implemented.
- Materializer narrowing never searches arbitrary PDF text, cache paths, source helpers or raw parser artifacts. It only uses the already-loaded `ParsedAnnualReport.sections`, `ParsedAnnualReport.tables`, chapter anchors and fact values passed in memory.
- No-live tests prove both happy paths and fail-closed paths.
- Release/readiness remains `NOT_READY`.

## Non-goals

- No live/PDF command.
- No product CLI command, including B1 `017641 / 2024`.
- No provider/LLM command.
- No threshold relaxation in `confirm_projection_evidence_v2`.
- No ECQ or quality-gate semantic change.
- No checklist Evidence Confirm support.
- No report-body Evidence Confirm rendering.
- No fallback source policy change.
- No direct source/PDF/cache/helper access outside `FundDocumentRepository`.
- No extractor broad rewrite, parser replacement, Docling productionization or candidate artifact promotion.
- No tag, release, readiness promotion, push or PR external-state mutation.

## First-principles Judgment

The current blocker is not "lack of evidence objects" anymore. A1-C changed the system from zero references to coarse references. The current failure is that V2 value-match operates on same-anchor proof references; if the proof reference is a broad section or table excerpt that does not contain the exact value token in the expected shape, deterministic V2 must fail.

The minimal correct fix is not to make V2 lenient. The fix is to either:

- provide a better same-source, same-anchor excerpt that V2 can verify; or
- keep the failure/warning when the available in-memory report representation cannot safely prove a narrower excerpt.

For R3, the bond-risk failure has a separate root cause: `chapter_facts.py` intentionally keeps `BondRiskEvidenceValue.anchors` inside `value` and sets `evidence_anchor_ids=()`. That design made sense when group anchors were not trusted as chapter anchors, but A2-S2 now proves it blocks deterministic V2 missing-evidence for a current bond-fund sample. The next implementation should convert validated group anchor refs into normal chapter anchors inside the Fund projection layer.

## Direct Code Evidence

`fund_agent/fund/chapter_facts.py`:

- `_anchors_for_field()` returns `()` for `bond_risk_evidence`.
- `_project_bond_risk_evidence_fact()` returns an available fact with `evidence_anchor_ids=()` and `missing_detail="bond_risk_evidence 组级锚点引用保留在 value.anchors 内，未展开为 ChapterEvidenceAnchor"`.
- `_dedupe_chapter_anchors()`, `_chapter_anchor_from_raw()`, `_anchor_key()` and `_anchor_id_for()` already provide the local pattern for stable chapter anchor projection.

`fund_agent/fund/evidence_confirm_sources.py`:

- `_anchor_excerpt()` dispatches to section/table/row materialization.
- `_semantic_row_locator_table_excerpt()` and `_semantic_row_locator_section_excerpt()` intentionally degrade unsupported semantic row locators to coarse table/section excerpts.
- `_table_row_excerpt()` already supports exact `row-N` row materialization.
- The module docstring and runner only allow already-loaded `ParsedAnnualReport`; this boundary must remain.

`fund_agent/fund/extractors/models.py`:

- `BondRiskEvidenceAnchorRef` carries `anchor_id`, `section_id`, `page_number`, `table_id`, `row_locator` and `evidence_role`.
- `BondRiskEvidenceValue` carries `anchors`, `groups`, and satisfied/missing/weak/ambiguous group IDs.

`tests/fund/test_chapter_facts.py`:

- `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded()` currently asserts the pre-A3 behavior and should be replaced by projection tests for expanded group anchors.

`tests/fund/test_evidence_confirm_sources.py`:

- Existing materializer tests cover exact row excerpts, section excerpts, semantic locator degradation and V2 anchor precision warnings.

## Affected Files

Planned implementation files:

- `fund_agent/fund/chapter_facts.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_facts.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `tests/fund/test_chapter_writer.py`

Possible docs update if code behavior changes:

- `fund_agent/fund/README.md`

Control/evidence artifacts for the later implementation gate:

- `docs/reviews/evidence-confirm-productionization-rr-09-a3-implementation-evidence-20260624.md`
- code review / controller judgment artifacts under `docs/reviews/`

## Public Contract / Schema Changes

No public CLI, Service, Host, quality-gate, Evidence Confirm V2 schema, ECQ schema or report-body contract change is planned.

The only internal projection behavior change is:

- `structured.bond_risk_evidence` facts may gain `evidence_anchor_ids` when `BondRiskEvidenceValue.anchors` can be converted into chapter-level `annual_report` anchors.

This is an internal Fund projection contract improvement within existing `chapter_fact_projection.v1`; it does not require changing the schema version because the existing schema already allows facts to reference chapter anchors.

## Implementation Slices

### Slice A3-S1: Bond-risk Group Anchor Projection

Objective:

Convert `BondRiskEvidenceValue.anchors` into `ChapterEvidenceAnchor` entries and attach their generated IDs to the `structured.bond_risk_evidence` fact.

Allowed files:

- `fund_agent/fund/chapter_facts.py`
- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_facts.py`
- `tests/fund/test_chapter_writer.py`
- `fund_agent/fund/README.md` if behavior documentation changes.

Implementation decisions:

- Add a private helper in `chapter_facts.py` to convert each `BondRiskEvidenceAnchorRef` to `EvidenceAnchor`:
  - `source_kind="annual_report"`.
  - `document_year=value.report_year`.
  - `section_id=anchor_ref.section_id`.
  - `page_number=anchor_ref.page_number`.
  - `table_id=anchor_ref.table_id`.
  - `row_locator=anchor_ref.row_locator`.
  - `note` includes safe role/group context only, not raw excerpts.
- Update `_anchors_for_field()` so `bond_risk_evidence` returns converted anchors only when the field value is a valid `BondRiskEvidenceValue`.
- Update `_project_bond_risk_evidence_fact()` to use `anchor_ids_by_key` and attach projected anchor IDs.
- Keep fail-closed behavior:
  - non-bond / missing bond-risk evidence remains missing or not-applicable with no anchors;
  - malformed value types do not create anchors;
  - if a value is available but produces no valid anchors, keep `missing_reason="evidence_missing"` rather than silently passing.
- Update `chapter_writer.py` prompt/unknown-anchor messaging:
  - remove the categorical statement that all bond-risk internal anchors are not `ChapterEvidenceAnchor`;
  - keep fail-closed unknown-anchor handling for stale/internal IDs that are still not in `chapter.evidence_anchors`.

Expected no-live tests:

- Replace `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded()` with a test proving:
  - bond-risk group anchors are projected into `chapter.evidence_anchors`;
  - the bond-risk fact has nonempty `evidence_anchor_ids`;
  - every referenced ID exists in `chapter.evidence_anchors`;
  - projected anchors preserve section/page/table/row locator identity.
- Add a negative test proving missing/non-bond bond-risk evidence still produces no anchors and remains not applicable/missing.
- Update writer tests so allowed projected bond-risk anchors can be referenced, while unknown stale group IDs still fail closed.

Completion signal:

- Focused tests pass:
  - `uv run pytest tests/fund/test_chapter_facts.py tests/fund/test_chapter_writer.py`
- Static check passes:
  - `uv run ruff check fund_agent/fund/chapter_facts.py fund_agent/fund/chapter_writer.py tests/fund/test_chapter_facts.py tests/fund/test_chapter_writer.py`
  - `git diff --check`

Stop condition:

- Stop after implementation evidence and review. Do not run live/PDF re-evidence in this slice.

### Slice A3-S2: Coarse-reference Materializer Narrowing

Objective:

Reduce `coarse_reference_insufficient` for fee, NAV/benchmark performance, manager alignment and manager strategy text by producing narrower proof references only when the in-memory `ParsedAnnualReport` can safely identify a row or bounded table excerpt that contains the fact value.

Allowed files:

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md` if behavior documentation changes.

Implementation decisions:

- Do not change V2 value-match tokenization or thresholds.
- Do not create a parallel matcher. Reuse V2 deterministic primitives from `fund_agent.fund.evidence_confirm` (`_material_tokens`, `_normalize_text`, `_token_matches_excerpt`) inside the Fund layer, following the accepted `evidence_confirm_value_diagnostics.py` pattern.
- Keep exact `row-N` as the preferred proof path.
- Add a bounded semantic row narrowing helper for the existing semantic row-locator paths:
  - input: `ChapterEvidenceAnchor`, candidate `ParsedTable`, and an anchor-to-fact map derived only from `ChapterFactProjection`;
  - output: exact row excerpt only when exactly one available non-derived fact references the anchor and all V2 material tokens for that fact are found in exactly one table row under V2 normalization/matching;
  - otherwise preserve the A1-C table/section downgrade and informational issue.
- Build `anchor_id -> facts` inside `build_annual_report_evidence_confirm_references()` from the already-passed projection; do not add new public request fields unless implementation review proves the helper cannot stay private.
- A narrowing candidate must fail closed or degrade to the existing coarse reference when:
  - no available non-derived fact references the anchor;
  - more than one available non-derived fact references the anchor;
  - the referenced fact has no V2 material token;
  - multiple rows match;
  - no row matches;
  - only a subset of the fact's V2 material tokens match a row;
  - table headers/rows are malformed beyond current deterministic formatting support;
  - the anchor has no compatible `table_id` and section text cannot safely identify a unique row-like excerpt.
- Do not classify a coarse reference as pass simply because the broader section/table contains some related word. The excerpt must contain the deterministic V2 value token source used by the fact.

Expected no-live tests:

- Existing A1-C tests remain valid:
  - semantic row locator can still degrade to table/section;
  - degradation still emits informational issue;
  - V2 anchor precision warning remains for true degraded locators.
- New tests:
  - semantic locator plus compatible table narrows to a single row when exactly one row contains the relevant fact value;
  - shared-anchor ambiguity keeps table downgrade and does not pick a row for one of several facts;
  - partial token match keeps table downgrade and does not pretend row precision;
  - no match keeps table/section downgrade and value-match can still fail under V2;
  - source/provenance negative tests remain unchanged.

Completion signal:

- Focused tests pass:
  - `uv run pytest tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py`
- Static check passes:
  - `uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py`
  - `git diff --check`

Stop condition:

- Stop after no-live implementation evidence and review. Live/PDF R1-R4 re-evidence must be a separate authorization gate.

### Slice A3-S3: Post-fix Re-evidence Authorization Precheck

Objective:

After A3-S1/S2 no-live implementation, produce an authorization precheck that states exactly what live/PDF re-evidence would run and what remains out of scope.

Allowed files:

- `docs/reviews/evidence-confirm-productionization-rr-09-a3-live-pdf-authorization-precheck-20260624.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Implementation decisions:

- The precheck must not run live/PDF commands.
- It must request exact user authorization for R1-R4 repository-bounded live/PDF re-evidence.
- It must keep B1 `017641 / 2024` product CLI re-evidence separate unless explicitly combined by the user.

Completion signal:

- Static artifact checks pass:
  - `git diff --check`
  - `rg -n 'A3|R1-R4|B1|NOT_READY' docs/reviews/evidence-confirm-productionization-rr-09-a3-live-pdf-authorization-precheck-20260624.md docs/current-startup-packet.md docs/implementation-control.md`

## Validation Matrix

| Requirement | Planned validation |
|---|---|
| Bond-risk group anchors become auditable chapter anchors | `tests/fund/test_chapter_facts.py` verifies projected anchors and fact references. |
| Stale/internal bond-risk IDs still fail closed | `tests/fund/test_chapter_writer.py` verifies unknown-anchor rejection remains. |
| Row/table narrowing does not weaken V2 | `tests/fund/test_evidence_confirm_sources.py` verifies exact row, degrade, ambiguous and no-match behavior. |
| Existing V2 source/proof boundaries remain | `tests/fund/test_evidence_confirm.py` focused suite remains green. |
| No direct source/PDF/cache/helper access added | Existing static import tests plus code review of touched modules. |
| No product or release semantics changed | No CLI/Service/Host/quality-gate files in allowed implementation write set. |

## Docs Decision

If A3-S1 changes bond-risk projection behavior, update `fund_agent/fund/README.md` to state the current internal behavior: `BondRiskEvidenceValue.anchors` can be converted to chapter evidence anchors for Evidence Confirm, while still remaining Fund-layer typed evidence.

If A3-S2 changes materializer behavior, update `fund_agent/fund/README.md` to state that semantic row locators may be narrowed to row-level proof only under deterministic single-row conditions; otherwise they remain table/section downgrades with precision warnings.

Do not update root README, Service docs, Host docs, CLI docs or release docs in this plan because no public product interface changes.

## Risks And Residuals

| Risk | Classification | Planned handling |
|---|---|---|
| Real R1-R4 tables may not contain enough row structure to narrow references | assigned to A3-S2 implementation evidence and later live/PDF re-evidence | Preserve coarse fallback and classify remaining failures rather than weakening V2. |
| Bond-risk group anchor conversion may expose many anchors across chapters 0/6/7 | current slice risk | Deduplicate with existing chapter anchor key logic; tests must verify stable references. |
| Writer tests currently encode old "not expanded" bond-risk contract | current slice risk | Update prompt and tests only after projection behavior changes; keep unknown-anchor fail-closed. |
| B1 runtime product CLI residual remains open | separate work unit | Requires explicit B1 authorization. |
| Release/readiness remains unproven | separate release-boundary gate | Keep `NOT_READY`. |

## Open Questions

No blocking open question for planning. The main uncertainty is empirical: whether no-live narrowing will be enough to make live R1-R4 strict V2 pass. That must be answered only after implementation and separate authorized live/PDF re-evidence.

## Why This Is Not Over-designed

The plan uses existing local seams:

- `chapter_facts.py` already owns projection from extractor values to `ChapterEvidenceAnchor`.
- `evidence_confirm_sources.py` already owns materializer logic.
- `chapter_writer.py` already owns allowed-anchor prompt and fail-closed unknown-anchor diagnostics.

It does not introduce a new schema, registry, parser abstraction, external source path, provider path, product mode or quality-gate layer. The only new logic is targeted conversion/narrowing at the exact two locations identified by A2-S2.

## Completion Report Format

The later implementation evidence must report:

- changed files;
- exact no-live commands and results;
- behavior before/after for bond-risk projection;
- materializer narrowing behavior and remaining degradation cases;
- explicit statement that V2, ECQ, quality gate, product CLI, checklist, report body, provider default, tag, release and readiness were not changed;
- next entry point for live/PDF R1-R4 re-evidence and/or B1 runtime product CLI re-evidence.

Completion token:

`RR_09_A3_FIX_PLAN_READY_FOR_REVIEW_NOT_READY`
