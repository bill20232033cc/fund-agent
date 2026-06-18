# Controller Judgment: 004393 / 2025 Controlled Source-body Verification Access Preflight

Date: 2026-06-13

Gate: `004393 / 2025 Controlled Source-body Verification Gate`

Judgment artifact:
`docs/reviews/mvp-004393-2025-controlled-source-body-verification-access-preflight-20260613.md`

Review inputs:

- `docs/reviews/mvp-004393-2025-controlled-source-body-verification-access-preflight-review-mimo-20260613.md`
- `docs/reviews/mvp-004393-2025-controlled-source-body-verification-access-preflight-review-ds-20260613.md`

Verdict: `ACCEPT_ACCESS_PREFLIGHT_BLOCKED_NOT_READY`

## 1. Controller Scope

This controller judgment closes only the access-preflight step for the current
source-body verification gate.

It does not authorize tracked golden answer edits, fixture promotion, live
EID/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release/PR actions,
cleanup, push, merge, or any source/test/runtime behavior change.

No source-body verification is accepted by this judgment.

## 2. Accepted Facts

| Fact | Status | Basis |
|---|---|---|
| `FundDocumentRepository.load_annual_report(..., force_refresh=False)` is not a cache-only public contract. | `ACCEPTED` | Preflight PF1; MiMo review; DS review A1 |
| A cache miss or stale/non-EID cache can fall through to `fetch_pdf()` or `fetch_pdf_path()`. | `ACCEPTED` | `fund_agent/fund/documents/repository.py`; `tests/fund/documents/test_repository.py`; MiMo review |
| No public repository no-new-live/cache-only method exists for this gate. | `ACCEPTED` | Preflight PF2; MiMo review; DS review A2 |
| Current gate authorization does not permit calling `load_annual_report("004393", 2025)` when a live/source/PDF fall-through remains possible. | `ACCEPTED` | `AGENTS.md`; `docs/current-startup-packet.md`; `docs/implementation-control.md`; tracked golden write planning judgment |
| Direct local PDF/data-artifact proof remains outside this gate. | `ACCEPTED` | `AGENTS.md`; current startup/control docs; prior data artifact disposition |
| The seven accepted rows remain candidate-only and `NOT_VERIFIED_SOURCE_BODY`. | `ACCEPTED` | Preflight row status; same-year reviewed golden content controller judgment |

## 3. Reviewer Finding Disposition

| Review finding | Controller disposition | Rationale |
|---|---|---|
| MiMo: no material findings; access preflight correctly blocks source-body verification without no-new-live proof or live authorization. | `ACCEPT` | MiMo directly verifies the repository fall-through chain, public API surface, repository-boundary rule and current control truth. |
| DS F1: run `repository._cache.get_pdf_entry(DocumentKey("004393", 2025))` as a zero-risk cache availability check before blocking. | `REJECT_FOR_THIS_GATE`; `DEFER_TO_CACHE_ONLY_CONTRACT_GATE` | The suggestion is technically useful as a design input, but it uses a private cache member rather than a public repository contract. Current control truth requires repository-bounded access, and the source-body gate may not rely on private cache probing to authorize later body access. |
| DS F2: distinguish `load_parsed_report()` body access from `get_pdf_entry()` metadata-only cache probing. | `ACCEPT_WITH_REWRITE` | The distinction is valid. Controller records it here as a future contract-design distinction, but it does not change the current gate verdict because no public no-new-live repository API exists. |
| DS F3: prefer cache availability check before live authorization. | `ACCEPT_AS_DEFERRED_CANDIDATE`; `REJECT_AS_CURRENT_STEP` | A public cache-only repository contract would be cleaner than live access, but implementing or relying on that contract is a separate source/runtime contract gate. This access-preflight artifact cannot create that contract. |
| DS F4: add residual owner table. | `ACCEPT` | The owner table is added below. |

## 4. Residual Owner Table

| Residual | Owner | Destination |
|---|---|---|
| Seven accepted candidate rows still need source-body verification before tracked strict golden truth. | Golden content/source owner | Next authorized source-body verification gate |
| No public no-new-live/cache-only repository contract exists. | Fund documents/repository owner | `Repository Cache-only Access Design / Implementation Gate`, if selected |
| Live source-body verification requires explicit separate authorization. | User + controller/evidence owner | `004393 / 2025 Controlled Live EID Source-body Verification Sub-slice`, if authorized |
| Private cache metadata probing may be useful but is not an accepted current-gate proof path. | Controller + Fund documents owner | Cache-only contract planning evidence, not this gate |
| Release/readiness remains unproven. | Release owner | Future readiness gate only |

## 5. Controller Decision

The access preflight is accepted as a blocking preflight:

```text
Repository-bounded no-new-live source-body access is not currently proven.
```

Therefore the current gate cannot proceed to source-body verification through
`FundDocumentRepository.load_annual_report("004393", 2025)` under the existing
authorization.

DS's cache-metadata path is not accepted as an immediate execution step because
it would use `repository._cache`, a private implementation detail, rather than a
public repository contract. It is accepted only as a deferred candidate for a
separate cache-only repository contract gate.

## 6. Next Entry

Recommended next entry:

```text
Controlled live EID source-body verification authorization decision
```

If the user explicitly authorizes live EID/network/PDF/FDR access for this
bounded sub-slice, the next gate may verify only the seven accepted candidate
rows for `004393 / 2025` through `FundDocumentRepository`.

If live authorization is not granted, the non-live alternative is:

```text
Repository Cache-only Access Design / Implementation Gate
```

That gate would design and review a public no-new-live repository contract
before any source-body verification uses cached annual-report content.

## 7. Boundary Confirmation

This judgment did not perform or authorize:

- tracked golden answer content edits;
- fixture promotion edits;
- source/test/runtime behavior changes;
- `FundDocumentRepository.load_annual_report()` execution;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- direct local PDF/data-artifact body reads;
- cleanup, archive, push, merge or external-state actions.
