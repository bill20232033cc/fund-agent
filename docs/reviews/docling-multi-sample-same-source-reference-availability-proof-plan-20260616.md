# Docling Multi-sample Same-source Reference Availability Proof Plan - 2026-06-16

Gate: `Docling Multi-sample Same-source Reference Availability Proof Gate`
Role: planning worker only
Release/readiness: `NOT_READY`
Verdict: `PLAN_READY_FOR_EVIDENCE_GATE_NOT_READY`

## 1. Goal

Write an evidence-worker-ready plan to decide whether expansion samples S4/S5/S6 have no-live same-source reference availability sufficient to resume a later Docling field-family correctness review.

This plan does not prove field correctness. It only defines the bounded proof routes and stop conditions for reference availability.

## 2. Scope

In scope:

- Determine, per sample, whether an already accepted same-source reference artifact exists.
- If such an artifact exists, bind it to the sample identity and record path/hash only as accepted-artifact proof.
- If no accepted artifact exists, decide whether the next evidence gate may attempt a bounded `FundDocumentRepository(force_refresh=False)` route.
- Preserve candidate-only and `NOT_READY` state.

Out of scope:

- No Docling conversion.
- No pdfplumber export.
- No PDF body read, page crop review, manual reference review, or direct PDF path inspection.
- No source helper, cache internals, direct source adapter, EID/live/network/PDF acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge command.
- No source/test/runtime/control/design changes.
- No production parser replacement, `FundDocumentRepository` behavior change, source policy change, `EvidenceAnchor` schema change, Service/UI/Host/renderer/quality-gate integration, source-truth claim, full correctness claim, taxonomy compatibility claim, readiness/release claim.

## 3. Truth Inputs

Required control inputs:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Required prior gate inputs:

- `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-controller-judgment-20260616.md`
- `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md`
- `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json`

Repository semantic input:

- `fund_agent/fund/documents/repository.py`, only for planning `FundDocumentRepository(force_refresh=False)` semantics.

Accepted facts from those inputs:

- S1 `004393 / 2025` remains a bounded accepted pilot through an accepted same-source reviewed-facts artifact.
- S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024` have local Docling/pdfplumber candidate JSON artifacts present and hashed in the previous gate.
- S4/S5/S6 were blocked before fact selection because no accepted no-live same-source reference artifact or no-live repository metadata proof was established.
- Existing candidate JSONs are not source truth and are not field-correctness proof.
- Candidate `field_correctness_status` remains `not_proven`; release/readiness remains `NOT_READY`.

## 4. Sample Matrix

| Sample | Fund code | Report year | Report type | Prior candidate availability | Current reference proof status to determine |
| --- | --- | ---: | --- | --- | --- |
| `S4` | `006597` | 2024 | annual report | Docling full JSON and pdfplumber full JSON present in previous evidence | Need no-live same-source reference availability proof or blocker |
| `S5` | `017641` | 2024 | annual report | Docling full JSON and pdfplumber full JSON present in previous evidence | Need no-live same-source reference availability proof or blocker |
| `S6` | `110020` | 2024 | annual report | Docling full JSON and pdfplumber full JSON present in previous evidence | Need no-live same-source reference availability proof or blocker |

## 5. Proof Route Decision Tree

The evidence worker must process each sample independently in this order.

### Route A: Accepted Same-source Reference Artifact

1. Look only for accepted artifacts already inside the reviewed evidence chain.
2. An artifact is eligible only if it explicitly binds all of:
   - `fund_code`
   - `document_year`
   - `report_type=annual_report`
   - same-source identity, preferably EID `single_source_only`, `fallback_enabled=false`, `fallback_used=false`
   - reference availability for the same annual-report source, not a Docling/pdfplumber candidate output alone
3. If eligible, record:
   - `reference_availability_status=available_via_accepted_artifact`
   - `no_live_proof_route=accepted_same_source_reference_artifact`
   - artifact path and SHA-256
   - same-source identity fields
   - residual that this proves reference availability only, not field correctness
4. If path exists but body lacks one of the identity fields above, status is `blocked_identity_unproven`, not available.
5. If only Docling/pdfplumber candidate JSON exists, status is `blocked_candidate_only`, not available.

Static artifact candidates may include only already accepted reviewed-facts/reference artifacts under:

- `reports/representation-json/`
- `docs/reviews/`

The evidence worker must not scan or use source/cache internals, candidate helper internals, direct PDF paths, or unreviewed residue as proof.

### Route B: Bounded Repository Metadata Proof

Route B is allowed only after Route A fails for a sample and only if controller/user explicitly authorizes a bounded repository attempt for this gate.

Repository semantics from `fund_agent/fund/documents/repository.py`:

- `force_refresh=False` first attempts parsed-report cache through `load_parsed_report()`.
- It accepts the cached parsed report only if metadata satisfies current EID single-source policy: `source=="eid"`, `fallback_used is False`, `primary_failure_category is None`, `selected_source=="eid"`, `source_mode=="single_source_only"`, `fallback_enabled is False`.
- If parsed cache misses, it may check a PDF cache entry.
- If no valid PDF cache entry exists, it calls loader `fetch_pdf()` or `fetch_pdf_path()` with `force_refresh=False`.
- After PDF path resolution, it calls `parse_pdf()`.

Therefore, `FundDocumentRepository(force_refresh=False)` is not inherently a no-live/static proof route. It is bounded only when the evidence worker can prove the call will stop at an already accepted parsed-report cache hit without triggering PDF acquisition or PDF parsing.

Route B has a pre-execution proof circularity under the current constraints. The evidence worker cannot prove that `FundDocumentRepository(force_refresh=False)` will hit parsed cache without either inspecting cache internals, which is forbidden by this plan, or executing `load_annual_report()`, which may proceed to PDF cache lookup, PDF acquisition, or parsing. Therefore, unless a prior gate has already established parsed-cache metadata proof for the exact `(fund_code, document_year)` identity, Route B is inexecutable in this gate and must stop with `blocked_repository_route_requires_authorization`. The recommended follow-up is a separate Cache Metadata Contract Gate, or explicit authorization for metadata-only `cache.load_parsed_report(document_key)` inspection limited to `metadata.source` envelope fields.

Route B allowed outcome:

- `reference_availability_status=available_via_repository_parsed_cache_metadata`
- `no_live_proof_route=bounded_fdr_force_refresh_false_parsed_cache_hit`
- `repository_attempted=true`
- metadata fields prove EID single-source/no-fallback identity
- evidence worker accesses and records only `metadata.source` envelope fields
- no PDF path, PDF body, cache internals, parser output body, or live/source helper output is included
- parsed report body content must not be inspected, serialized, diffed, compared, or otherwise used for correctness verification, fact extraction, field comparison, or any other purpose

Route B mandatory stop outcome:

- If the planned call would need PDF cache lookup, loader `fetch_pdf()` / `fetch_pdf_path()`, `parse_pdf()`, any network/source adapter, direct PDF path inspection, or source/cache internals, stop before running it.
- If no prior gate has already established parsed-cache metadata proof for the exact `(fund_code, document_year)` identity, stop before running Route B.
- Record `reference_availability_status=blocked_repository_route_requires_authorization`
- Record `blocker_reason=fdr_force_refresh_false_may_fetch_or_parse_pdf_without_prior_parsed_cache_hit_proof`
- Return control to controller/user for explicit authorization or a separate cache-only contract gate.

## 6. Explicitly Forbidden Routes

The evidence worker must not use:

- source helper APIs or source adapter internals
- cache internals or direct cache database/file inspection
- direct PDF paths, direct PDF file metadata as source proof, or PDF body read
- `force_refresh=True`
- EID/live/network/PDF acquisition
- Docling conversion
- pdfplumber export
- manual reference review/page crop review
- provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands
- unaccepted untracked residue as proof

## 7. Evidence Artifact Schema

The evidence worker must produce one Markdown evidence artifact and, if it writes machine-readable evidence, one JSON sidecar under `reports/representation-json/`. The Markdown artifact is required; JSON sidecar is optional unless controller asks for it.

Required per-sample fields:

| Field | Required value rules |
| --- | --- |
| `sample_id` | `S4`, `S5`, or `S6` |
| `fund_code` | Exact fund code |
| `document_year` | Exact report year |
| `report_type` | `annual_report` |
| `reference_availability_status` | One of `available_via_accepted_artifact`, `available_via_repository_parsed_cache_metadata`, `blocked_no_accepted_artifact`, `blocked_identity_unproven`, `blocked_candidate_only`, `blocked_repository_route_requires_authorization`, `blocked_not_authorized` |
| `no_live_proof_route` | One of `accepted_same_source_reference_artifact`, `bounded_fdr_force_refresh_false_parsed_cache_hit`, `none` |
| `blocker_reason` | Required for any `blocked_*` status |
| `same_source_identity` | Object/section with `source`, `selected_source`, `source_mode`, `fallback_enabled`, `fallback_used`, `primary_failure_category`, and identity status |
| `accepted_reference_artifact_path` | Required only for `available_via_accepted_artifact` |
| `accepted_reference_artifact_sha256` | Required only for `available_via_accepted_artifact` |
| `repository_attempted` | `false` unless Route B is explicitly authorized |
| `repository_force_refresh` | `false` if Route B is explicitly authorized; otherwise `null` |
| `hash_path_scope` | `accepted_artifact_only`; never direct PDF/cache path unless a later gate explicitly changes scope |
| `residuals` | Must preserve not source truth, not field correctness, not full correctness, not parser replacement, not readiness |

Required aggregate fields:

- `gate`
- `release_readiness=NOT_READY`
- `commands_run`
- `commands_not_run`
- `samples`
- `route_summary`
- `stop_conditions_triggered`
- `verdict`
- `next_gate_recommendation`

Allowed verdicts:

- `AVAILABLE_REFERENCE_MATRIX_READY_FOR_CORRECTNESS_REVIEW_NOT_READY`: all S4/S5/S6 have accepted no-live reference availability proof.
- `PARTIAL_REFERENCE_MATRIX_BLOCKED_NOT_READY`: at least one, but not all, expansion samples have proof.
- `BLOCKED_NO_NO_LIVE_REFERENCE_PROOF_NOT_READY`: no S4/S5/S6 sample has proof under the authorized route.
- `BLOCKED_REPOSITORY_ROUTE_REQUIRES_AUTHORIZATION_NOT_READY`: Route A fails and Route B would require FDR/PDF acquisition or parsing authorization.

## 8. Evidence Worker Procedure

1. Run preflight status only:
   - `git status --short`
2. Confirm the previous evidence JSON exists:
   - `test -f reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json`
3. For each sample, evaluate Route A first:
   - Check only accepted evidence-chain artifacts for same `fund_code` / `document_year` / `annual_report` identity.
   - Hash only accepted artifact paths that qualify.
   - Do not use candidate full JSON presence as reference proof.
4. If Route A proves all samples, write evidence artifact with `AVAILABLE_REFERENCE_MATRIX_READY_FOR_CORRECTNESS_REVIEW_NOT_READY`.
5. If Route A does not prove a sample, do not attempt FDR by default.
6. If controller/user has explicitly authorized Route B:
   - Attempt Route B only if a prior gate has already established parsed-cache metadata proof for the exact `(fund_code, document_year)` identity, or if this gate has explicit authorization for metadata-only `cache.load_parsed_report(document_key)` inspection.
   - If metadata-only `cache.load_parsed_report(document_key)` inspection is explicitly authorized, access and record only `metadata.source` envelope fields.
   - Do not inspect, serialize, diff, compare, or otherwise use parsed report body content for correctness verification, fact extraction, field comparison, or any other purpose.
   - Attempt only a bounded repository path that can prove parsed-cache metadata without live/source/PDF acquisition.
   - Stop before any path that would require `fetch_pdf()`, `fetch_pdf_path()`, `parse_pdf()`, direct PDF path inspection, source adapter, cache internals, or network.
7. If Route B is not authorized or cannot be proven no-live before execution, write blocked status and stop.
8. Run only final artifact validation commands listed below.

## 9. Validation Commands

Allowed validation commands for the evidence worker after writing the artifact:

```text
git status --short
git diff -- docs/reviews/<evidence-artifact>.md
git diff --check -- docs/reviews/<evidence-artifact>.md
test -f docs/reviews/<evidence-artifact>.md
test -f reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
shasum -a 256 <accepted-reference-artifact-paths-only>
```

`shasum -a 256 <accepted-reference-artifact-paths-only>` is conditionally applicable only when Route A discovers at least one accepted reference artifact path. If all samples are blocked and no accepted reference artifact path exists, record this command as not applicable and do not run it with an empty or invalid path.

If a JSON sidecar is written:

```text
git diff -- reports/representation-json/<evidence-sidecar>.json
git diff --check -- reports/representation-json/<evidence-sidecar>.json
test -f reports/representation-json/<evidence-sidecar>.json
shasum -a 256 reports/representation-json/<evidence-sidecar>.json
```

No other validation command is authorized by this plan.

## 10. Stop Conditions

Stop and write the corresponding blocked status when any of the following occurs:

- No accepted same-source reference artifact exists for a sample.
- Candidate JSON is present but no accepted reference artifact or repository metadata proof exists.
- Same-source identity cannot be tied to exact `fund_code`, `document_year`, and annual-report source.
- Route B is not explicitly authorized.
- `FundDocumentRepository(force_refresh=False)` may proceed beyond an already accepted parsed-cache metadata hit.
- Any route requires source helper, cache internals, direct PDF path, `force_refresh=True`, PDF body read, Docling conversion, pdfplumber export, manual review, live/network/EID/PDF acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge.
- Any evidence would imply source truth, full field correctness, production parser replacement, or readiness.

## 11. Review Gate

Recommended review after evidence artifact:

- Review only the produced evidence artifact and optional JSON sidecar.
- Review questions:
  - Did the evidence worker keep Route A before Route B?
  - Did any sample use candidate JSON as reference proof?
  - Did any FDR route exceed parsed-cache metadata proof or require acquisition/parsing?
  - Are blocked statuses explicit and sample-specific?
  - Does the artifact preserve `NOT_READY` and avoid source truth/full correctness/readiness claims?

## 12. Exact Next Gate Recommendation

If all S4/S5/S6 have accepted no-live reference availability proof:

```text
Docling Multi-sample Field-family Correctness Expansion Reviewability Decision Gate
```

That gate may decide whether to resume correctness review, but must still avoid declaring source truth, full correctness, production replacement, or readiness.

If any S4/S5/S6 sample is blocked:

```text
Controller Decision Gate: authorize bounded repository parsed-cache proof, open separate cache-only contract gate, or keep multi-sample correctness blocked
```

If `FundDocumentRepository(force_refresh=False)` might fetch or parse PDF:

```text
Stop. Require controller/user authorization before any repository attempt, or open a separate bounded repository/cache contract gate.
```

## 13. Completion Report Format

Evidence worker completion report must include:

- Artifact path
- Verdict
- Per-sample `reference_availability_status`
- Whether Route B was attempted
- Commands run
- Commands explicitly not run
- Residuals
- Next gate recommendation
- `Self-check: pass` or `Self-check: blocked - <reason>`
