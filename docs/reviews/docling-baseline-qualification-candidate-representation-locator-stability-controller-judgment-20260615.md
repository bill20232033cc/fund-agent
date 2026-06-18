# Candidate Representation Locator Stability Controller Judgment - 2026-06-15

Gate: `Candidate Representation Locator Stability Evidence Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the evidence gate that evaluates locator stability for already generated candidate representation JSON.

Reviewed evidence:

- `docs/reviews/docling-baseline-qualification-candidate-representation-locator-stability-evidence-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-candidate-representation-locator-stability-evidence-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-locator-stability-evidence-review-mimo-20260615.md`

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-controller-judgment-20260615.md`

## 3. Accepted Evidence Facts

- Current-schema projectable evidence covers 3 Docling PDF candidate samples, 3 pdfplumber PDF candidate samples, and 3 blocked EID HTML render candidate samples.
- `004393_2025` JSON artifacts are not accepted locator-stability proof in this gate because they are legacy or route-specific schemas outside the current candidate envelope.
- Docling current-schema samples show:
  - 659 sections
  - 341 tables
  - 15,759 cells
  - 100% cell page locator rate
  - 100% cell bbox locator rate
  - 100% cell row/column locator rate
  - 1,843 header-flag cells
- pdfplumber current-schema samples show:
  - 22 sections
  - 317 tables
  - 14,999 cells
  - 100% cell page locator rate
  - 0% cell bbox locator rate
  - 100% cell row/column locator rate
  - 0 header-flag cells
- EID HTML current-schema samples remain blocked artifacts with no table-bearing candidate representation in this gate.

## 4. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Distinguish projected-hash availability from native source JSON hash coverage. | MiMo review | ACCEPT_WITH_REWRITE | Evidence was revised to avoid treating derived projection hashes as source-native hash proof. Locator stability conclusion rests on page/bbox/row-column locator coverage. |
| Include replayable validation script. | MiMo + DS reviews | ACCEPT_WITH_REWRITE | Evidence was revised to include the counting script body. |
| Input scope and 004393 residual handling are honest. | DS review | ACCEPT | 004393 legacy/route-specific artifacts are excluded from proof and recorded as residual. |
| Docling/pdfplumber/EID classifications are metric-supported. | DS + MiMo reviews | ACCEPT | Metrics support Docling stable candidate, pdfplumber partial candidate, EID blocked for this gate. |
| Non-proof boundaries are preserved. | DS + MiMo reviews | ACCEPT | Evidence does not claim field correctness, source truth, taxonomy compatibility, parser replacement, readiness, release, or production integration. |

## 5. Controller Decision

Docling is accepted as the baseline candidate for locator stability evidence.

This decision means:

- Docling may be used as the primary candidate route in the next baseline decision/design gate.
- pdfplumber remains a partial comparator/fallback candidate for page + row/column table extraction.
- EID HTML render remains blocked in this gate and requires separate envelope mapping evidence before comparison.

This decision does not mean:

- Docling field values are correct.
- Docling is source truth.
- Docling replaces the production parser.
- Production code may consume candidate internals.
- Release/readiness status changes.

## 6. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| 004393 current-envelope artifact is missing. | Deferred | Optional no-live artifact-refresh gate before 004393-specific correctness work. |
| EID HTML full table-bearing artifact is route-specific, not current candidate envelope. | Deferred | Separate EID HTML candidate envelope mapping gate. |
| Field correctness remains unproven. | Deferred | Field-family correctness pilot after baseline decision. |
| Production integration remains unauthorized. | Deferred | Separate production design/implementation gate. |
| Release/readiness remains `NOT_READY`. | Accepted residual | No release/readiness/PR claim. |

## 7. Validation

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 8. Final Verdict

`VERDICT: ACCEPT_DOCLING_BASELINE_CANDIDATE_FOR_LOCATOR_STABILITY_NOT_READY`

Next recommended gate:

`Docling Baseline Candidate Decision Gate`

Do not proceed to production integration, parser replacement, field correctness promotion, readiness, release or PR from this gate.
