# Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence Controller Judgment

Date: 2026-06-15

Gate: `Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence Gate`

Role: controller

Verdict: `ACCEPT_EVIDENCE_READY_FOR_HYBRID_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_PLANNING_GATE_NOT_READY`

Readiness state: `NOT_READY`

## 1. Scope

This judgment closes the current evidence gate. It accepts the evidence artifact:

- `docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-20260615.md`

Reviewed by:

- DS review: `docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-review-ds-20260615.md`
- MiMo review: `docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-review-mimo-20260615.md`

This judgment does not authorize source, test, runtime, repository, parser, source policy, Service, Host, UI, renderer, quality gate, provider, LLM, readiness, release, PR, push, merge, stage or commit changes.

## 2. Accepted Current Facts

| Fact | Controller disposition |
|---|---|
| Docling Route A has the strongest same-report full-document representation signal for `004393 / 2025` among allowed evidence. | Accepted as candidate representation evidence only. |
| EID XBRL HTML render has a strong structured disclosure locator signal where official render pages are available. | Accepted as route-family candidate locator evidence only. |
| No accepted same-report EID HTML render artifact for `004393 / 2025` exists in the allowed input set. | Accepted residual. |
| Current pdfplumber/PDF path remains accepted production operational baseline. | Accepted current code/design fact. |
| No accepted same-report full-document pdfplumber representation artifact for `004393 / 2025` exists in the allowed input set. | Accepted residual. |
| No single route is sufficiently proven for exclusive adoption. | Accepted. |
| Hybrid planning is supported as the next planning action, not implementation or production replacement. | Accepted. |

## 3. Findings Disposition

| Source | Finding | Disposition | Rationale |
|---|---|---|---|
| DS | Evidence artifact could explicitly reference phaseflow queue item 11. | ACCEPT_AS_NONBLOCKING_RESIDUAL | The controller judgment and control sync can carry this clarification; artifact revision is not required. |
| DS | Pdfplumber reliability label is long/stylistically inconsistent. | REJECT_AS_STYLE_ONLY | The label is precise and does not create semantic ambiguity. |
| DS | Artifact does not discuss whether the specific `004393 / 2025` HTML render URL is constructible from known URL patterns. | DEFER | Constructing or proving a same-report EID HTML URL belongs to a bounded discovery/evidence gate, not this no-live evidence closeout. |
| MiMo | Section 6 residual table could explicitly list the two key same-report availability gaps. | ACCEPT_AS_NONBLOCKING_RESIDUAL | The gaps are already recorded in Section 2 and Section 5; controller accepts them as residuals without requiring rewrite. |
| MiMo | Verdict label is novel and could use a one-line definition. | ACCEPT_AS_NONBLOCKING_RESIDUAL | The verdict is clear from Section 5 and is normalized by this controller judgment verdict. |

No blocking findings remain.

## 4. Blocked Claims

The following claims remain blocked or explicitly unproven:

- `not_raw_xml_download_proof`
- `not_field_correctness_proof`
- `not_taxonomy_compatibility_proof`
- `not_source_truth`
- `not_readiness_proof`
- `no_repository_behavior_change`
- `no_parser_replacement`

HTML render, Docling JSON/Markdown and local benchmark outputs remain candidate representation inputs only. Fund facts still require accepted extractor/projection, `EvidenceAnchor` and fail-closed validation gates before entering CHAPTER_CONTRACT, audit or report generation.

## 5. Accepted Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Same-report `004393 / 2025` EID HTML render artifact absent. | Fund documents/source research owner | Deferred bounded discovery/evidence gate if hybrid planning requires exact HTML proof. |
| Same-report `004393 / 2025` full pdfplumber representation baseline absent. | Fund documents/parser owner | Deferred no-live baseline materialization gate or included as a planning decision. |
| Ordinary non-REIT annual/interim HTML render coverage unproven. | Fund documents/source research owner | Deferred coverage evidence gate. |
| Docling model artifact provenance remains benchmark-only. | Fund documents/parser owner | Deferred provenance acceptance gate before production use. |
| Docling section/paragraph mapping depth remains incomplete. | Fund documents/parser owner | Deferred mapping evidence/implementation gate. |
| Candidate `EvidenceAnchor` note/source-kind schema remains undecided. | Fund documents/schema owner | Deferred schema/projection decision gate. |
| Field correctness and taxonomy compatibility remain unproven. | Fund documents/extractor owner | Separate validation/taxonomy gates only. |

## 6. Final Decision

The evidence gate is accepted.

The accepted evidence supports the following route decision:

- Do not choose EID HTML only.
- Do not choose Docling only.
- Do not choose pdfplumber only.
- Proceed to hybrid candidate-source planning while preserving current production behavior.

Primary next gate:

`Hybrid FundDisclosureDocument Candidate Source Planning Gate`

This next gate is a refinement of the deferred FundDisclosureDocument candidate source planning/implementation-planning path in the control queue. It must decide whether the next concrete slice is:

1. a narrow same-report extraction projection pilot; or
2. a broader candidate source schema/projection planning slice.

## 7. Deferred Entries

- Same-report `004393 / 2025` EID HTML render discovery/evidence gate.
- Ordinary non-REIT annual/interim HTML render coverage gate.
- Docling model artifact provenance acceptance gate.
- Docling fixture-integrity hardening gate.
- Pdfplumber same-report baseline materialization gate.
- Candidate `EvidenceAnchor` note/source-kind schema decision gate.
- Extractor projection over candidate document representation planning gate.
- Raw XML endpoint proof gate only if a public endpoint is discovered.
- Field correctness validation gate.
- Taxonomy compatibility gate.
- Readiness/release/PR gates.

## 8. Validation

Required validation for this closeout:

- `git diff --check`

Result: pending at artifact write time; controller must run it after writing this judgment and any scoped control sync.

## 9. Final Verdict

`VERDICT: ACCEPT_EVIDENCE_READY_FOR_HYBRID_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_PLANNING_GATE_NOT_READY`

