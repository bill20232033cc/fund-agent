# Docling Controlled Same-source Reference Acquisition Plan - 2026-06-16

Gate: `Docling Controlled Same-source Reference Acquisition Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`
Plan status: `HANDOFF_READY_FOR_REVIEW_NOT_READY`

## Goal

Define a bounded evidence route to acquire or revalidate same-source EID annual-report reference proof for:

| Sample | Fund code | Year | Current blocker |
| --- | --- | ---: | --- |
| S4 | `006597` | 2024 | metadata-only facade returned `unsafe_metadata`, reason `selected_source_not_eid` |
| S5 | `017641` | 2024 | metadata-only facade returned `unsafe_metadata`, reason `source_not_eid` |
| S6 | `110020` | 2024 | metadata-only facade returned `unsafe_metadata`, reason `source_not_eid` |

The plan exists because Docling candidate JSON artifacts for S4/S5/S6 cannot be used for multi-sample field-family correctness review until the repository/source reference for each sample is proven to be the same EID single-source annual report.

## Non-goals

- Do not run acquisition in this planning gate.
- Do not compare Docling extracted values to reference facts.
- Do not perform manual correctness review.
- Do not promote Docling to global baseline.
- Do not replace production parser.
- Do not change `FundDocumentRepository`, cache behavior, source policy, parser behavior, EvidenceAnchor schema, Service, Host, UI, renderer, quality gate or provider/LLM route.
- Do not reintroduce Eastmoney, fund-company website, CNINFO or any non-EID fallback.
- Do not claim EID public annual reports are unavailable if acquisition fails.
- Do not claim source truth, full field correctness, taxonomy compatibility, readiness, release, PR or merge readiness.

## Direct Evidence Inputs

| Artifact | Use |
| --- | --- |
| `AGENTS.md` | Rule, source and repository boundary truth |
| `docs/design.md` | Docling candidate-layer and Fund documents boundary truth |
| `docs/current-startup-packet.md` | Current gate and accepted checkpoint surface |
| `docs/implementation-control.md` | Control truth and current non-goals |
| `docs/reviews/docling-baseline-qualification-scope-decision-controller-judgment-20260616.md` | User-selected option 2 route |
| `docs/reviews/docling-same-source-reference-cache-metadata-evidence-controller-judgment-20260616.md` | Accepted S4/S5/S6 unsafe metadata blocker |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Candidate sample identity only; not correctness proof |

## Target Evidence Gate

Next gate after plan acceptance:

```text
Docling Controlled Same-source Reference Acquisition Evidence Gate
```

Evidence deliverable:

```text
docs/reviews/docling-controlled-same-source-reference-acquisition-evidence-20260616.md
```

## Allowed Evidence Actions

Evidence worker may use exactly one of these bounded routes, in this order:

1. **Repository facade metadata re-check**
   - Call `FundDocumentRepository.get_annual_report_reference_metadata(fund_code, year)` for S4/S5/S6.
   - If all samples return `available` with EID single-source metadata, record proof and stop.

2. **Repository annual-report acquisition through accepted boundary**
   - If metadata remains `missing` or `unsafe_metadata`, call `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=True)` only for S4/S5/S6.
   - This is the only planned live/PDF/source acquisition command family.
   - The evidence worker must not call cache internals, downloader internals, source helpers, PDF paths, filesystem PDF reads, parser internals or non-repository acquisition APIs.
   - `load_annual_report()` may fetch and parse the annual report as a repository side effect. The evidence worker must not inspect, quote, compare, serialize or use the returned parsed body, sections, tables, text, anchors or PDF path. Its only accepted use is to trigger repository-owned acquisition through the public boundary; proof must come from the subsequent metadata facade re-check.

3. **Post-acquisition metadata proof**
   - After each bounded repository acquisition attempt, call `get_annual_report_reference_metadata(fund_code, year)` again.
   - Accept same-source reference proof only if metadata returns `available` and the allowed proof fields match the required identity.

## Required Proof Fields

For each sample, evidence must record:

- `sample_id`
- `fund_code`
- `document_year`
- `report_type` or document kind
- repository method used
- command line or script path used by evidence worker
- acquisition status
- post-acquisition metadata status
- `selected_source`
- `source`
- `source_mode`
- `fallback_enabled`
- `fallback_used`
- `primary_failure_category` if unavailable
- `metadata_identity_hash`
- safe document identity fields from `AnnualReportReferenceMetadataResult`
- exception class and message if failed

Accepted same-source proof requires:

```text
metadata_status = available
selected_source = eid
source = eid
source_mode = single_source_only
fallback_enabled = false
fallback_used = false
fund_code matches requested fund_code
document_year matches requested year
report/document kind is annual report or accepted annual-report equivalent
metadata_identity_hash is present
```

Returned `ParsedAnnualReport` content from `load_annual_report()` is not an accepted proof surface for this gate.

## Stop Rules

Evidence worker must stop and report `BLOCKED_NOT_READY` for a sample if any of these occur:

- repository acquisition requires auth, captcha, manual browser state or external credentials;
- repository acquisition routes to non-EID source;
- fallback is enabled or used;
- metadata remains `unsafe_metadata` after acquisition;
- metadata indicates `schema_drift`, `identity_mismatch` or `integrity_error`;
- repository public return object lacks enough safe identity/provenance metadata to verify same-source proof;
- command would require direct cache internals, downloader internals, source helper calls, PDF path access, filesystem PDF body reads, parser execution, Docling conversion or pdfplumber export;
- command would need Eastmoney, fund-company website, CNINFO or any other non-EID fallback;
- evidence worker would need to compare Docling extracted field values to reference values before same-source proof is accepted.

## Validation Commands

Planning gate validation:

```text
git diff --check
git status --short
git status --branch --short
```

Evidence gate allowed validation after writing evidence:

```text
git diff --check
git status --short
git status --branch --short
```

No pytest or ruff is required unless the evidence worker changes code, which this plan does not authorize.

## Review Focus

Reviewers must check:

- the plan does not reintroduce Eastmoney, fund-company website, CNINFO or fallback;
- the plan uses `FundDocumentRepository` public boundary only;
- the plan does not treat unsafe metadata as proof;
- the plan does not prove field correctness, taxonomy compatibility, source truth, readiness or parser replacement;
- the plan separates acquisition proof from later correctness review;
- stop rules fail closed on `schema_drift`, `identity_mismatch`, `integrity_error`, fallback or non-EID source;
- the evidence artifact shape is sufficient for controller acceptance without inventing schema during execution.

## Expected Outcomes

| Outcome | Meaning | Next gate |
| --- | --- | --- |
| `ACCEPT_ALL_REFERENCES_AVAILABLE_NOT_READY` | S4/S5/S6 all have accepted EID single-source reference metadata | Resume multi-sample Docling field-family correctness evidence gate |
| `ACCEPT_PARTIAL_REFERENCES_AVAILABLE_NOT_READY` | Some samples pass and some remain blocked | Narrow multi-sample correctness to passing samples or plan replacement samples |
| `ACCEPT_BLOCKED_REFERENCE_ACQUISITION_NOT_READY` | No sample can be proven through accepted repository boundary | Keep multi-sample correctness blocked; decide whether to narrow to `004393 / 2025` or revisit source/document representation route |

## Final Handoff

Proceed to plan review. If review passes, controller may accept this plan and route to `Docling Controlled Same-source Reference Acquisition Evidence Gate`.
