# Controller Judgment: Research/User-owned/Tooling Residue Metadata Evidence

Date: 2026-06-12

Gate: `Research/user-owned/tooling residue metadata evidence gate`

Verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## Scope

This judgment accepts metadata-only evidence for the accepted research/user-owned/tooling candidate paths. It does not accept any file as source truth, design truth, template truth, release evidence or readiness proof. It does not read candidate bodies, run live/provider/PDF/LLM/analyze/readiness/release commands, authorize cleanup/archive/delete/ignore/import/promote, or change source/test/runtime behavior.

Release/readiness remains `NOT_READY`.

## Truth Inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Accepted plan: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-plan-20260612.md`
- Plan controller judgment: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-plan-controller-judgment-20260612-064354.md`
- Evidence: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-evidence-20260612.md`
- DS review: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-evidence-review-ds-20260612.md`
- MiMo review: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-evidence-review-mimo-20260612.md`

## Review Summary

| Reviewer | Verdict | Blocking findings | Controller disposition |
|---|---|---|---|
| DS | `ACCEPT` | none | Accept |
| MiMo | `ACCEPT` | none | Accept |

## Controller Disposition

| Requirement | Disposition | Evidence |
|---|---|---|
| Accepted command set only | ACCEPT | Evidence section 1; DS/MiMo re-runs |
| No candidate body reads | ACCEPT | Evidence sections 0, 1 and 7; reviewer attestations |
| Candidate path/root coverage | ACCEPT | Evidence sections 3 and 4; DS/MiMo count reconciliation |
| `reviews/` listing coverage | ACCEPT | 2 files listed and represented as rows |
| `基金年报/` listing coverage | ACCEPT | 5 PDF paths listed and represented as rows |
| Mandatory non-proof flags | ACCEPT | All 15 rows carry `body_read=false`, `not_source_truth`, `not_design_truth`, `not_template_truth`, `not_release_evidence`, `not_readiness_proof` |
| Excluded groups remain excluded | ACCEPT_WITH_RESIDUAL | `docs/reviews/`, `docs/audit/`, `reports/live-evidence/`, `reports/manual-llm-smoke/` remain visible but outside this gate |
| Controller amendments from planning judgment | ACCEPT | Reviews confirm top-level `reviews/`, source-like script, PDF corpus and truth-source risks are routed |
| Release/readiness state | ACCEPT | Remains `NOT_READY` |

## Accepted Metadata Facts

| Fact | Accepted scope |
|---|---|
| 8 accepted-plan candidate paths/roots are visible as untracked | Metadata-only, not content proof |
| 6 candidate paths are direct untracked files | Metadata-only |
| 2 candidate paths are untracked root directories: `reviews/`, `基金年报/` | Metadata-only |
| `reviews/` contains 2 listed files under authorized maxdepth | Path listing only |
| `基金年报/` contains 5 listed PDF paths under authorized maxdepth | Path listing only; not production access path |
| Evidence has 15 rows and all rows carry non-proof flags | Metadata classification accepted |

## Findings Disposition

| Finding / observation | Source | Controller disposition |
|---|---|---|
| Evidence acknowledges `docs/reviews/` visibility/count drift but does not provide a structured excluded-group count | DS N1, MiMo N1/N2 | ACCEPT_AS_RESIDUAL; route to top-level/review-audit follow-up before readiness |
| Top-level `reviews/` routing is correct | DS, MiMo | ACCEPT; route to top-level review/audit residue follow-up |
| `scripts/claude_mimo_simple.py` is source-like tooling residue | Evidence, DS, MiMo | ACCEPT; route to source-like tooling ownership gate if needed |
| `基金年报/` is user-owned PDF corpus, not production source path | Evidence, DS, MiMo | ACCEPT; route to corpus ingestion/disposition gate if needed |
| Design/template truth-source risks remain non-proof | Evidence, MiMo | ACCEPT; route to separate truth-source decision only if needed |

## Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Top-level `reviews/` files | metadata classified; not accepted as release evidence | Controller / review-artifact owner | Top-level review/audit residue follow-up gate |
| `docs/reviews/` count drift and remaining historical review residue | excluded but still visible | Controller / review-artifact owner | Review/audit residue follow-up before readiness |
| `scripts/claude_mimo_simple.py` source-like tooling | metadata classified; not runtime source | Controller / tooling owner | Source-like tooling ownership gate if needed |
| `基金年报/` PDF corpus | metadata classified; not production source path | User / document owner | PDF corpus ingestion/disposition gate if needed |
| spec/template-like docs | metadata classified; not design/template truth | Design/template owner | Truth-source decision gate if needed |
| release/readiness | `NOT_READY` | Release owner / controller | Future release-readiness re-evidence after residue disposition |

## Next Entry

Mainline next entry: `Top-level review/audit residue follow-up planning gate`.

Deferred entries:

- source-like tooling ownership gate for `scripts/claude_mimo_simple.py`
- user-owned PDF corpus ingestion/disposition gate
- user-owned template/spec truth-source decision gate
- cleanup/archive/delete/ignore policy gate
- release-readiness cleanliness re-evidence gate
- PR/push/merge/mark-ready/release gate

## Validation

Controller-side validation required before accepted checkpoint:

- `git status --short`
- `git status --branch --short`
- `git diff --check`

No live/provider/network/PDF/FDR/LLM/analyze/checklist/golden/readiness/release commands are authorized by this judgment.
