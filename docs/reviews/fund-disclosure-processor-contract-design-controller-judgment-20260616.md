# Fund Disclosure Processor Contract Design Controller Judgment - 2026-06-16

Gate: `Fund Disclosure Processor Contract Design Controller Judgment`
Role: controller
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Inputs Reviewed

Design artifact:

- `docs/reviews/fund-disclosure-processor-contract-design-20260616.md`

Plan review loop:

- `docs/reviews/plan-review-20260616-222112.md`
- `docs/reviews/plan-review-20260616-222153.md`

Current upstream accepted evidence:

- `docs/reviews/docling-baseline-support-source-truth-evidence-controller-judgment-20260616.md`
- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`

## 2. Controller Decision

Accept the Fund Disclosure Processor Contract design as a future design input for the next Docling source-truth residual closure planning gate.

Accepted design facts:

- The project-owned disclosure processor contract is `source -> processed -> fund`.
- The contract is fund-disclosure-specific and must not copy company financial-statement result contracts.
- The first implementation/evidence target remains the existing annual-report Docling residual set, not quarterly/prospectus expansion.
- `repository_source_name`, `processor_profile` / `processor_source_kind`, and `EvidenceAnchor.source_kind` are separate concepts.
- For annual-report anchor candidates, `EvidenceAnchor.source_kind` semantics remain `annual_report`; repository source identity such as `eid` and processor route identity such as `docling_pdf_candidate` may only be preserved in candidate metadata, note fields or proof-row metadata.
- The 17 residual rows must be closed through locator and fund-semantic proof rules, not parser agreement or raw value equality alone.

## 3. Review Finding Disposition

| Finding | Source | Controller disposition |
| --- | --- | --- |
| F1: `source_kind` overload could mislead implementation into mixing repository source, processor route and EvidenceAnchor source semantics. | `docs/reviews/plan-review-20260616-222112.md` | Accepted and fixed in the design artifact before controller acceptance. |

Re-review result:

```text
docs/reviews/plan-review-20260616-222153.md -> pass
```

## 4. What This Judgment Does Not Accept

This judgment does not accept:

- source code changes;
- test changes;
- README or `docs/design.md` truth-source changes;
- `FundDocumentRepository` behavior changes;
- public `EvidenceAnchor` schema changes;
- direct PDF/cache/source-helper access;
- Docling conversion;
- live/network/EID/provider/LLM/analyze execution;
- official source policy changes;
- Docling source-truth closure;
- full field correctness;
- Docling baseline qualification;
- production parser replacement;
- release readiness;
- PR readiness.

## 5. Next Entry Point

Next gate:

```text
Docling Source-truth Residual Closure Planning Gate
```

Purpose:

- convert the accepted `source -> processed -> fund` contract into a handoff-ready no-live residual closure plan;
- target only the 17 residual rows from `source_truth_matrix.json`;
- define per-row locator and fund-semantic closure rules;
- preserve `NOT_READY`;
- keep baseline qualification blocked until residuals are closed or explicitly retained as irreducible residuals.

Required next-gate guardrails:

- Use only accepted same-source evidence and repository-mediated references.
- Do not read PDF/cache/source-helper bodies directly.
- Do not treat Docling, pdfplumber or parser agreement as source truth.
- Do not close `S6-F041 / benchmark` without benchmark-labeled source context.
- Keep `S5-F023 / investment_objective` blocked unless source/processed/fund triage proves a same-source body match under the accepted contract.

## 6. Residual Risks

| Risk | Owner | Tracking destination |
| --- | --- | --- |
| Later implementation overfits to current matrix rows instead of reusable proof-row contract. | residual closure planning owner | `Docling Source-truth Residual Closure Planning Gate` |
| Quarterly/prospectus support is named but not specified. | Fund documents owner | future Fund disclosure document-kind expansion gate |
| Baseline support still lacks full source-truth closure and full field correctness. | baseline qualification owner | later evidence gates after residual closure |

## 7. Validation To Run Before Local Checkpoint

Required local sanity check:

```bash
git diff --check
```

## 8. Verdict

```text
VERDICT: ACCEPT_FUND_DISCLOSURE_PROCESSOR_CONTRACT_DESIGN_FOR_RESIDUAL_CLOSURE_NOT_READY
```
