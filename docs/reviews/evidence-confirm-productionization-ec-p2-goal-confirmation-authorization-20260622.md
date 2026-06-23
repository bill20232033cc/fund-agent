# Evidence Confirm Productionization EC-P2 Goal Confirmation And Authorization

## Gate

- Work unit: `Evidence Confirm Productionization Program`
- Slice: `EC-P2 Repository-bounded Live Source/PDF Evidence Gate`
- Current gate: `goal confirmation / live sample authorization`
- Artifact: `docs/reviews/evidence-confirm-productionization-ec-p2-goal-confirmation-authorization-20260622.md`
- Branch: `evidence-confirm-productionization`
- Upstream PR: PR-40 (`https://github.com/bill20232033cc/fund-agent/pull/40`)

## Verdict

`GOAL_CONFIRMED_PENDING_USER_LIVE_SAMPLE_AND_COMMAND_AUTHORIZATION_NOT_READY`

## First-principles Judgment

EC-P2 is a valid next work unit because EC-P1A proved only the no-live materializer over already supplied `ParsedAnnualReport` objects. It did not prove that the materializer can be driven from the production document repository, did not exercise live source/PDF acquisition, and did not classify live source failure branches.

The next smallest evidence-bearing step is not Service/UI/quality-gate integration. It is a repository-bounded Fund-layer path that calls `FundDocumentRepository.load_annual_report()` and then feeds the returned `ParsedAnnualReport` into the existing EC-P1A materializer.

## Goal

Prove that live annual-report source/PDF evidence can enter Evidence Confirm through the repository boundary only:

1. Add or plan a Fund-layer runner/facade that accepts an injected repository or default repository.
2. Ensure the runner calls only `FundDocumentRepository.load_annual_report()` for annual-report access.
3. Cover fake-repository positive and failure branches before live execution.
4. Run exactly one explicitly authorized controlled live positive sample after plan/review acceptance.
5. Record source provenance as current EID single-source with no fallback.
6. Stop on ambiguous live failure classification rather than silently falling back.

## Recommended Initial Live Sample

| Field | Value |
|---|---|
| Fund code | `004393` |
| Report year | `2025` |
| Report type | `annual_report` |
| Rationale | Existing accepted evidence already uses `004393 / 2025` as a controlled current-year route in nearby evidence chains, and it is the smallest active-fund sample for proving source/PDF entry without broadening to multiple fund types. |

The EC-P2 accepted plan requires one controlled positive sample first. Multi-sample execution is explicitly deferred until the single-sample positive path is accepted.

## Required User Authorization

EC-P2 cannot enter execution without explicit user authorization for both sample matrix and live/PDF command boundary.

Recommended authorization text:

```text
同意 EC-P2：sample 004393/2025，授权 repository-bounded live/PDF 命令。
```

Authorized command boundary, if approved:

- Only through `FundDocumentRepository.load_annual_report("004393", 2025, force_refresh=True)`.
- No direct PDF/cache/source helper calls outside repository internals.
- No provider/LLM commands.
- No Service/UI/Host/renderer/quality-gate behavior change.
- No source fallback behavior change.
- No PR mark-ready, reviewer request, merge, release, or readiness claim.

## Direct Code / Control Evidence

| Evidence | Meaning |
|---|---|
| `docs/reviews/evidence-confirm-productionization-program-plan-20260622.md` EC-P2 section | EC-P2 objective is to prove materializer through `FundDocumentRepository.load_annual_report()` on explicitly authorized live samples. |
| `fund_agent/fund/documents/repository.py` | `FundDocumentRepository.load_annual_report()` is async and returns `ParsedAnnualReport` without exposing local PDF path upward. |
| `fund_agent/fund/evidence_confirm_sources.py` | EC-P1A materializer consumes already supplied `ParsedAnnualReport` and does not instantiate repository or access PDF/cache/source helpers. |
| `docs/design.md` source policy sections | Current annual-report production default is EID single-source, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`. |
| `docs/reviews/evidence-confirm-productionization-ec-p1a-final-closeout-20260622.md` | EC-P1A closed no-live materializer only; live source/PDF Evidence Confirm remains EC-P2 residual. |

## Non-goals

EC-P2 goal confirmation does not authorize or implement:

- semantic entailment Evidence Confirm;
- deterministic production facade composition;
- Service/UI/renderer/quality-gate consumption;
- production default-on policy;
- multi-sample live matrix;
- provider/LLM execution;
- source fallback behavior changes;
- `EvidenceSourceKind` or public `EvidenceAnchor` expansion;
- PR mark-ready, reviewer request, merge, release, or readiness.

## Success Signal For EC-P2 Planning

A code-generation-ready EC-P2 plan should specify:

- exact fake repository protocol and fake positive/failure cases;
- runner/facade input/output contract;
- how `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error` are classified;
- the single live command shape and safe scalar evidence output;
- stop condition for any classification ambiguity;
- tests and evidence artifact path;
- no changes to Service/UI/Host/renderer/quality-gate.

## Blocking Open Questions

| Question | Status | Required decision |
|---|---|---|
| Which initial live sample matrix is authorized? | blocking | Recommended: `004393 / 2025 / annual_report` only. |
| Are repository-bounded live/network/PDF commands authorized for EC-P2? | blocking | Recommended: authorize only `FundDocumentRepository.load_annual_report("004393", 2025, force_refresh=True)` through reviewed EC-P2 plan/execution gates. |

Until both are explicitly approved, EC-P2 must not enter plan dispatch or live command execution.

## Next Step

Wait for explicit user authorization. If authorization is granted, dispatch EC-P2 plan gate to a planning worker with this artifact, `docs/design.md`, `docs/implementation-control.md`, and `docs/reviews/evidence-confirm-productionization-program-plan-20260622.md` as inputs.
