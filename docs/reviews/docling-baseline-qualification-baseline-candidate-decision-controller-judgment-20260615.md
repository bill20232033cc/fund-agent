# Docling Baseline Qualification Baseline Candidate Decision Controller Judgment - 2026-06-15

Gate: `Docling Baseline Candidate Decision Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This controller decision decides whether Docling can become the baseline candidate route for the candidate representation layer after no-live structural locator evidence.

This gate does not:

- change production parser behavior
- replace `FundDocumentRepository`
- modify public `EvidenceAnchor`
- expose candidate internals to Service, Host, UI, renderer, or quality gate
- claim field correctness
- claim source truth
- claim taxonomy compatibility
- claim release/readiness
- run live/provider/LLM/PDF conversion/analyze/checklist/release/PR commands

## 2. Evidence Reviewed

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-locator-stability-controller-judgment-20260615.md`

## 3. Accepted Facts

| Fact | Status |
| --- | --- |
| Built-in candidate handlers exist for Docling, pdfplumber, and EID HTML render, but remain candidate-internal. | Accepted |
| Full representation export evidence exists for current-schema samples `006597_2024`, `017641_2024`, and `110020_2024`. | Accepted |
| Candidate schema/projection exists and preserves route-specific locators. | Accepted |
| Docling has stable candidate locator evidence across 3 current-schema samples: 15,759 cells, 100% page locator, 100% bbox locator, 100% row/column locator, and 1,843 header-flag cells. | Accepted |
| pdfplumber has partial locator evidence: 14,999 cells, 100% page and row/column locator, but 0% bbox and 0 header-flag cells. | Accepted |
| EID HTML render is blocked for the current-schema samples in this candidate envelope path. | Accepted |
| `004393_2025` artifacts are legacy or route-specific and are not current-envelope locator-stability proof. | Accepted residual |

## 4. Decision

Docling is accepted as the baseline candidate route for the Fund documents candidate representation layer.

Meaning of this decision:

- Future candidate representation design/evidence gates may treat Docling as the primary baseline candidate for structural locator work.
- pdfplumber remains the comparator and partial candidate route, especially for page + row/column table extraction. This is not production source/parser fallback authorization.
- EID HTML render remains a separate candidate route that needs current-envelope mapping before comparable evaluation.
- 004393-specific validation should first refresh or wrap artifacts into the current candidate envelope.

Non-meaning of this decision:

- Docling is not accepted as source truth.
- Docling is not accepted as field correctness proof.
- Docling is not accepted as a production parser replacement.
- Docling candidate internals are not allowed to be consumed by Service, Host, UI, renderer, quality gate, or public APIs.
- Release/readiness remains `NOT_READY`.

## 5. Deferred / Rejected Options

| Option | Decision | Reason |
| --- | --- | --- |
| Promote Docling directly to production parser baseline. | REJECT | Production integration and parser replacement are out of scope and require separate design/implementation gates. |
| Treat pdfplumber as equal baseline for layout-rich locator work. | REJECT_FOR_NOW | pdfplumber lacks bbox and header-flag evidence in the accepted sample set. |
| Treat EID HTML render as comparable full candidate representation now. | REJECT_FOR_NOW | Current-schema EID HTML entries are blocked; 004393 route-specific HTML JSON is not current envelope proof. |
| Use 004393 legacy Route A JSON as current baseline proof. | REJECT | It lacks the current candidate envelope schema. |
| Regenerate or wrap 004393 into current envelope. | DEFER | Appropriate next evidence/prep gate before 004393-specific correctness work. |

## 6. Next Gate Recommendation

Recommended next gate:

`004393 Current-envelope Candidate Artifact Refresh Planning Gate`

Purpose:

- make the user-designated fund `004393` / 安信企业价值优选混合A available under `candidate_annual_report_representation.v1`;
- avoid relying on legacy Route A JSON for future baseline/correctness claims;
- preserve no-live / no-production / no-readiness boundaries.

Deferred later gates:

- `Field-family Correctness Pilot Planning Gate`
- `EID HTML Candidate Envelope Mapping Gate`
- `Production FundDisclosureDocument Integration Design Gate`
- `Release/Readiness Rollup Gate`

## 7. Residuals

| Residual | Status | Owner |
| --- | --- | --- |
| Field correctness is unproven. | Accepted residual | Future correctness pilot |
| Source truth is unproven. | Accepted residual | Future source-truth gate if needed |
| Parser replacement is unauthorized. | Accepted residual | Future production design gate |
| 004393 current-envelope candidate JSON is missing. | Deferred | Next planning gate |
| Release/readiness remains `NOT_READY`. | Accepted residual | Controller |

## 8. Validation

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 9. Final Verdict

`VERDICT: ACCEPT_DOCLING_AS_CANDIDATE_LAYER_BASELINE_FOR_STRUCTURAL_LOCATORS_NOT_READY`

Next entry:

`004393 Current-envelope Candidate Artifact Refresh Planning Gate`
