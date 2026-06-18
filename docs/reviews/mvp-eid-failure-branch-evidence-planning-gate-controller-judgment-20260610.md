# Controller Judgment: EID failure-branch evidence planning gate

## Judgment

Accepted as planning artifact.

## Basis

- User explicitly ordered EID failure-branch evidence planning after downstream integration planning.
- Current control truth names EID failure-branch evidence planning as the next entry.
- The plan is no-live, code-generation-ready for a later evidence gate and preserves current EID single-source policy.
- Plan review reports no blocking findings.

## Accepted Planning Decisions

- Future evidence should prove all five failure categories: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`.
- Future evidence should use existing no-live seams: `httpx.MockTransport`, fake sources and direct parser/helper tests.
- `not_found` and `unavailable` should be documented as terminal under current single-source mode, not as actual fallback invocations.
- `schema_drift`, `identity_mismatch` and `integrity_error` should be documented as fail-closed categories.
- Any missing boundary assertions should be added as focused no-live tests before writing final evidence.

## Preserved Boundaries

- No live EID/network/PDF/FDR/repository acquisition.
- No fallback invocation or fallback source activation.
- No provider/live LLM/config/default/runtime/budget change.
- No fixture projection, golden/readiness promotion, downstream implementation, release, PR, merge or mark-ready action.

## Next Entry

Recommended next entry is the no-live EID failure-branch evidence implementation gate, unless the user redirects to downstream implementation or another phase.
