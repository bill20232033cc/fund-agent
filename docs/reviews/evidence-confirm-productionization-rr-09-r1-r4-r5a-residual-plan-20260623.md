# Evidence Confirm Productionization RR-09 R1-R4 / R5a Residual Plan

Verdict token:

`RR_09_R1_R4_R5A_RESIDUAL_PLAN_READY_NOT_READY`

## 1. Scope

This plan supersedes only the open RR-09 residual routing after:

- Branch F accepted `QualityGateBlockedError` / CLI safe Evidence Confirm summary propagation.
- R5a static evidence narrowed `017641 / 2024` from an unclassified QDII block to a generic P0 `manager_strategy_text` coverage/traceability block.

The plan does not implement code, run live/PDF/provider/LLM commands, mutate PR/remote state, tag, release, or claim release/readiness.

Release/readiness remains `NOT_READY`.

## 2. Current Facts

### R1-R4

Four RR-S2 product CLI samples still emitted `evidence_confirm_status=fail` under default `warn` policy:

| Residual | Sample | Product CLI fact count | Failed facts | Current status |
|---|---:|---:|---:|---|
| R1 | `004393 / 2025` | 53 | 34 | open |
| R2 | `004194 / 2024` | 53 | 35 | open |
| R3 | `006597 / 2024` | 53 | 32 | open |
| R4 | `110020 / 2024` | 53 | 39 | open |

Accepted evidence proves only product-level failure counts, not the fact-level root cause. Competing root causes remain:

- H1: true structural anchor/projection precision gap.
- H2: deterministic V2 false-positive pattern.
- H3: projection or source attachment defect.

No branch may reclassify R1-R4 as accepted product behavior until a fact-level diagnostic distinguishes H1/H2/H3.

### R5a

Accepted R5a static evidence proves:

- `017641 / 2024` classified as `qdii_fund`.
- preferred_lens resolved.
- App category matched.
- `failed_funds=[]`.
- FQ4 was `warn`, not `block`.
- blocking issues were generic P0 `manager_strategy_text` coverage/traceability:
  - `FQ2/block`
  - `FQ3/block`
  - `FQ2F/block`

Therefore R5a is not accepted as an expected QDII limitation. It must route to one of two explicit decisions:

1. keep `manager_strategy_text` P0 for QDII and improve extraction/anchors, or
2. make an explicit product/field applicability decision that changes P0 applicability for QDII.

## 3. Non-goals

- No release/readiness promotion.
- No checklist Evidence Confirm support.
- No report-body Evidence Confirm rendering.
- No provider-backed semantic production default.
- No fallback/source policy change.
- No direct PDF/cache/source-helper access outside `FundDocumentRepository`.
- No direct Service/UI/Host/renderer/quality-gate consumption of Docling/pdfplumber/EID HTML render internals.
- No stealth quality-gate relaxation.
- No V2 threshold weakening to reduce failures without fact-level evidence.
- No PR, push, merge, tag, or release action.

## 4. Workstream A: R1-R4 Fact-level Diagnostic

### Goal

Produce bounded fact-level evidence for at least one representative sample, and preferably all four RR-S2 failing samples, showing the dominant Evidence Confirm failing dimensions and whether each failure is true unsupported evidence or a code/projection defect.

Evidence disposition is sample-specific. A single-sample diagnostic may prove the diagnostic method, classify that one sample, and decide the next diagnostic/fix step. It must not close or reclassify unexamined R1-R4 samples.

Closing or reclassifying all R1-R4 requires fact-level diagnostic coverage for all four RR-S2 failing samples, or an explicit table that leaves each unexamined sample open.

### Authorization Boundary

This workstream has two modes.

#### A0: no-live static preparation

Allowed without additional live/PDF authorization:

- inspect `fund_agent/fund/evidence_confirm.py`
- inspect `fund_agent/fund/chapter_facts.py`
- inspect service/CLI summary projection code
- run existing no-live tests:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short
uv run pytest tests/services/test_fund_analysis_service.py -q --tb=short
uv run pytest tests/services/test_quality_gate_service.py -q --tb=short
```

A0 may define a diagnostic script shape, but must not load product samples.

#### A1: repository-bounded product diagnostic

Requires explicit user authorization before execution because it loads annual reports through `FundDocumentRepository` and may perform EID network/PDF processing.

Allowed only after authorization:

```bash
uv run fund-analysis analyze <fund_code> --report-year <year> --valuation-state unavailable --force-refresh
```

or a narrow Python diagnostic that:

- uses `FundDocumentRepository` as the only annual-report access boundary,
- uses the same product projection path as `fund-analysis analyze`,
- emits no raw PDF text, no excerpts, no cache paths, no provider payloads, and no direct source-helper output.

The diagnostic output must be safe aggregate/fact metadata only:

- sample id,
- checked fact count,
- failed fact count,
- failing dimension counts,
- field ids or chapter ids,
- anchor source kind/status,
- redacted value type/class,
- root-cause classification per failure bucket: `true_anchor_precision_gap`, `v2_false_positive`, `projection_attachment_defect`, `undetermined`.

### Acceptance Criteria

R1-R4 can leave "material release blocker" only if the accepted diagnostic proves one of:

- Branch A1-A: dominant failures are true anchor/projection precision gaps, `warn` remains honest product behavior, and user-visible summary semantics are documented.
- Branch A1-B: dominant failures include a narrow V2 false-positive pattern; route to a targeted scoring fix.
- Branch A1-C: dominant failures come from projection/source attachment defects; route to targeted projection/extractor anchor fix.

This acceptance is per sample unless the diagnostic covers all four samples. A diagnostic covering only `004393 / 2025`, for example, can only disposition R1; R2-R4 remain open unless separately diagnosed or explicitly carried as open residuals.

If authorization is not granted, R1-R4 remain open and release/readiness remains `NOT_READY`.

## 5. Workstream B: R5a Manager-strategy QDII Residual

### Current Code Surface

Static code evidence identifies the current surface:

- `fund_agent/fund/extraction_score.py` maps `manager_strategy_text` to `P0`.
- `fund_agent/fund/processors/fund_disclosure_processor.py` selects `manager_strategy_text` from stable strategy/outlook paragraphs via `_select_manager_profile_strategy_text`.
- `fund_agent/fund/chapter_facts.py` projects `manager_strategy_text` into chapter facts.
- `tests/fund/test_data_extractor.py` has source-truth facade coverage for strategy/outlook paragraphs.
- `tests/fund/test_extraction_score.py` / `tests/fund/test_quality_gate.py` cover scoring and quality-gate behavior.

### B1: Extraction / Anchor Hardening Path

Choose this path if `manager_strategy_text` remains mandatory P0 for QDII.

Implementation scope:

- improve QDII-compatible strategy/outlook paragraph matching or source-truth admission,
- preserve anchors and `source_field_path`,
- keep `manager_strategy_text` field shape unchanged:

```python
{
    "strategy_summary": ...,
    "market_outlook": ...,
}
```

Likely files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `fund_agent/fund/extractors/profile.py` only if facade fallback/projection needs alignment
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `fund_agent/fund/README.md` only if public Fund package behavior changes

Required tests:

```bash
uv run pytest tests/fund/test_data_extractor.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q --tb=short
uv run pytest tests/services/test_fund_analysis_service.py -q --tb=short
```

Optional authorized re-evidence, only after explicit live/PDF authorization:

```bash
uv run fund-analysis analyze 017641 --report-year 2024 --valuation-state unavailable --force-refresh
```

Acceptance requires proving that the block changes because `manager_strategy_text` is now covered and traceable, not because quality-gate semantics were weakened.

### B2: Product / Field Applicability Decision Path

Choose this path only if product ownership decides `manager_strategy_text` should not be P0/blocking for QDII.

This is a product policy change, not a bug fix. It requires a reviewed decision artifact before implementation.

Implementation scope after decision:

- adjust field priority/applicability in `fund_agent/fund/extraction_score.py` or the quality-gate projection layer,
- keep QDII preferred_lens and app-category checks intact,
- add tests proving only QDII `manager_strategy_text` applicability changes,
- document user-visible semantics: QDII reports may lack standard manager strategy/outlook disclosure and should surface an explicit gap/warn, not silently pass.

Required tests:

```bash
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q --tb=short
uv run pytest tests/services/test_quality_gate_service.py -q --tb=short
```

Forbidden in B2:

- changing global P0 priority for non-QDII funds,
- hiding missing `manager_strategy_text`,
- downgrading traceability checks globally,
- using R5a to claim R1-R4 resolved.

## 6. Sequencing

1. Accept or reject this plan through plan review.
2. If accepted, choose the next executable gate:
   - A1 diagnostic authorization for R1-R4, or
   - B1 extraction/anchor implementation, or
   - B2 product applicability decision.
3. Do not combine A1 live diagnostic with B1/B2 implementation in the same gate unless the user explicitly authorizes that combined scope.
4. Keep R5b closed; do not reopen Branch F unless a regression appears.
5. Keep release/readiness `NOT_READY` until R1-R4 and R5a are either accepted with evidence or fixed and re-evidenced.

## 7. Stop Conditions

Stop and return to controller if any of these occur:

- live/PDF/provider/LLM access is needed but not explicitly authorized,
- a proposed fix requires direct PDF/cache/source-helper access outside `FundDocumentRepository`,
- a proposed fix changes quality-gate semantics without a product decision artifact,
- R1-R4 diagnostic output would need raw excerpts, file paths, cache paths, provider payloads, or source-helper internals,
- a test failure indicates a broader Service/UI/Host/Agent boundary issue.

## 8. Validation for This Plan Artifact

Plan-only validation:

```bash
git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-r1-r4-r5a-residual-plan-20260623.md
```

No source tests are required for this plan artifact unless a reviewer requests additional static checks.

## 9. Result

This plan is ready for review. It preserves the current proof boundary:

- R1-R4 remain open until fact-level diagnostic evidence exists.
- R5a remains open until `manager_strategy_text` QDII extraction/anchor work or product applicability decision is accepted.
- R5b remains closed.
- release/readiness remains `NOT_READY`.

Completion token:

`RR_09_R1_R4_R5A_RESIDUAL_PLAN_READY_NOT_READY`
