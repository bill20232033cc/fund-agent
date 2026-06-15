# Docling Baseline Qualification Closeout / Truth-doc Sync Controller Judgment - 2026-06-15

Gate: `Docling Baseline Qualification Closeout / Truth-doc Sync Gate`  
Role: controller  
Release/readiness: `NOT_READY`

## 1. Scope

This gate synchronizes truth documents after the accepted `004393 Field-family Correctness Pilot Evidence Gate`.

Updated files:

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

No source code, tests, runtime behavior, repository behavior, source policy, parser behavior, Service/Host/UI/renderer/quality-gate behavior, LLM route, readiness, release, PR, push, merge, cleanup, archive, or delete action is authorized or performed.

## 2. Accepted Inputs

| Artifact / checkpoint | Accepted fact |
| --- | --- |
| `5a189c6` | Candidate representation schema implementation accepted as no-live candidate internals. |
| `b04bd82` | Candidate locator stability evidence accepted; Docling stable as candidate locator baseline across current-schema samples. |
| `ff64968` | Docling accepted only as candidate-layer structural locator baseline, not source truth/readiness/production. |
| `1e055fa` | `004393 / 2025` current-envelope refresh accepted for Docling, pdfplumber and blocked EID HTML render outputs. |
| `9286511` | `004393 / 2025` locator stability evidence accepted. |
| `2bdaa6f` | `004393` field-family correctness pilot plan accepted. |
| `afebc92` | `004393` field-family correctness pilot evidence accepted: Docling selected facts matched same-source repository-loaded PDF bbox crop excerpts in 21/21 reviewed facts; pdfplumber mismatch limited to 4 comparator locator/crop checks; EID HTML blocked/deferred for this sample. |

## 3. Truth-doc Updates

| File | Update |
| --- | --- |
| `docs/design.md` | Clarifies that Docling candidate internals are current no-live candidate-layer facts and that `004393 / 2025` selected field-family pilot passed. Keeps production parser as `pdfplumber + locate_sections + 自研 extractor`; rejects source truth, full correctness, parser replacement and readiness claims. |
| `docs/current-startup-packet.md` | Moves current mainline to this docs-only closeout gate, records the accepted `afebc92` checkpoint, and routes next entry to either multi-sample field-family correctness expansion or production integration planning after sync acceptance. |
| `docs/implementation-control.md` | Updates current status, truth guardrails, current gate, current inputs, next entry point, long-run queue and resume checklist to reflect the accepted bounded pilot while preserving `NOT_READY`. |

## 4. Boundary Decisions

| Claim | Decision | Reason |
| --- | --- | --- |
| Docling is a candidate-layer structural locator baseline. | ACCEPT | Accepted by locator and baseline decision gates. |
| Docling passes selected `004393 / 2025` field-family correctness pilot. | ACCEPT_WITH_LIMIT | Accepted for 21 selected same-source checked facts only. |
| Docling is current production parser. | REJECT | Production parser remains `pdfplumber + locate_sections + 自研 extractor`. |
| Docling output is source truth. | REJECT | Candidate `field_correctness_status` remains `not_proven`; source truth is not proven. |
| Field correctness is fully proven. | REJECT | Only bounded selected facts were reviewed. |
| pdfplumber generally fails. | REJECT | Only four selected comparator locator/crop checks mismatched. |
| EID HTML render field correctness is proven. | REJECT | EID HTML remains blocked/deferred for this sample. |
| Release/readiness can advance. | REJECT | This is a docs-only closeout; release/readiness remains `NOT_READY`. |

## 5. Validation

Commands:

```text
git diff --check
rg -n 'Docling Baseline Qualification Acquisition Status Planning Gate|Current mainline is `Docling Baseline Qualification Acquisition Status Planning Gate`' docs/current-startup-packet.md docs/implementation-control.md
```

Expected:

- `git diff --check` passes.
- `rg` returns no current-mainline residue for the superseded acquisition-status gate.

## 6. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| Broader sample correctness remains unproven. | accepted residual | `Docling Multi-sample Field-family Correctness Expansion Gate` |
| Production repository integration remains unplanned. | accepted residual | `FundDisclosureDocument Candidate Source Production Integration Planning Gate` |
| EID HTML current-envelope mapping remains blocked/deferred. | accepted residual | `EID HTML Current-envelope Mapping Gate` |
| Candidate artifacts are not source truth/readiness proof. | accepted residual | Preserve in all future gates. |
| Workspace still contains unrelated dirty `AGENTS.md` and historical untracked residue. | accepted residual | Separate artifact disposition / user-owned change handling only. |

## 7. Final Verdict

`VERDICT: ACCEPT_TRUTH_DOC_SYNC_FOR_004393_DOCLING_BOUNDED_PILOT_NOT_READY`

Recommended next gate:

`Docling Multi-sample Field-family Correctness Expansion Gate`

Rationale: before production integration planning, the project should test whether the 004393 bounded result generalizes across additional funds/years and field families.
