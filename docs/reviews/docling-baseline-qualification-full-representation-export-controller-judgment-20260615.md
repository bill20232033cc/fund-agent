# Docling Baseline Qualification Full Representation Export Controller Judgment - 2026-06-15

Gate: `Full Representation Export Evidence Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the full representation export evidence gate.

Evidence artifacts:

- `docs/reviews/docling-baseline-qualification-full-representation-export-evidence-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-adapter-fix-evidence-20260615.md`

Review artifacts:

- `docs/reviews/docling-baseline-qualification-full-representation-export-adapter-fix-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-adapter-fix-review-mimo-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-evidence-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-evidence-review-mimo-20260615.md`

Generated candidate representation artifacts:

- `reports/representation-json/full-representation-export-manifest-20260615.json`
- S1 `004393/2025` read-only reference JSONs.
- S4/S5/S6 Docling full candidate JSONs.
- S4/S5/S6 pdfplumber full candidate JSONs.
- S4/S5/S6 EID HTML render blocked JSONs.

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-controller-judgment-20260615.md`

Binding constraints preserved:

- EID single-source/no fallback remains current production source policy.
- No Eastmoney, fund-company website, CNINFO or non-EID fallback was used.
- Docling/pdfplumber/EID HTML render artifacts remain candidate-only.
- EID HTML render is not raw XML/XBRL truth.
- No field correctness, source truth, taxonomy compatibility, parser replacement, readiness or release claim is accepted.
- No `FundDocumentRepository`, source policy, production cache, Service, UI, Host, renderer, quality gate, extractor, `EvidenceAnchor` or `CHAPTER_CONTRACT` behavior changed.

## 3. Controller Findings

Accepted evidence facts:

- S4/S5/S6 Docling local artifact route produced full candidate JSONs with page, heading/section, table and cell locators.
- S4/S5/S6 pdfplumber route produced full candidate JSONs with page, section and table/cell counts.
- S4/S5/S6 EID HTML render remains blocked because accepted render artifacts were not in scope.
- S1 `004393/2025` representation JSONs remained read-only references and were not rewritten.
- The in-gate Docling adapter fix was reviewed and accepted after it mapped `texts[*].label`, `tables[*].data.table_cells` and `prov` page/bbox metadata.

Comparative structural evidence:

- Docling produced richer heading/section candidate counts for S4/S5/S6 than pdfplumber.
- Docling produced table cell counts in the same order of magnitude as pdfplumber for S4/S5/S6.
- Docling preserved bbox metadata in candidate heading/table/cell locators.
- pdfplumber preserved the existing section-catalog-oriented section shape.

## 4. Review Disposition

| Finding | Source | Controller disposition | Reason |
|---|---|---|---|
| Docling adapter fix maps current Docling `export_to_dict()` structure. | DS + MiMo adapter fix reviews | ACCEPT | Reviews confirmed `texts[*].label`, nested `tables[*].data.table_cells`, and `prov` page/bbox are mapped without production-boundary changes. |
| `--allow-overwrite` rerun within same gate. | DS + MiMo reviews | ACCEPT | Overwrite affected only same-gate known-defective candidate outputs after adapter fix; S1 references and production cache were not overwritten. |
| Full evidence stays at candidate structural coverage level. | DS + MiMo evidence reviews | ACCEPT | Reviews confirmed no field correctness, source truth, taxonomy, parser replacement, readiness or release claim was made. |
| Next gate should not be production implementation. | DS + MiMo evidence reviews | ACCEPT | Candidate representation schema/design must be defined before production integration or parser replacement. |

## 5. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Docling heading/section candidates include abundant layout-level headings and may include TOC/furniture. | Accepted residual | Candidate representation schema/design gate must define filtering and semantic section tree rules. |
| Field/value correctness is not proven. | Deferred | Field-family correctness pilot gate after candidate schema/design. |
| EID HTML render remains blocked for S4/S5/S6. | Deferred | Separate bounded EID HTML render discovery/evidence gate if needed. |
| S2/S3 provenance/hash issues remain unresolved. | Deferred | Separate provenance/disposition gate only. |
| Release/readiness remains `NOT_READY`. | Accepted residual | No readiness/release/PR claim. |

## 6. Validation

Accepted validation:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
git diff --check
```

Results:

- `26 passed in 2.27s`
- `All checks passed!`
- `git diff --check` passed

## 7. Final Verdict

`VERDICT: ACCEPT_FULL_REPRESENTATION_STRUCTURAL_EVIDENCE_READY_FOR_CANDIDATE_SCHEMA_DESIGN_GATE_NOT_READY`

Next recommended gate:

`Candidate Representation Schema / Design Planning Gate`

Do not proceed directly to production implementation, parser replacement, field correctness promotion, readiness, release or PR.
