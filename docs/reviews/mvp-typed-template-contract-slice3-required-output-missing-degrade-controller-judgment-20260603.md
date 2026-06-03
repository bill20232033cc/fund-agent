# MVP typed template contract Slice 3 required-output missing/degrade controller judgment

## Controller Self-Check

- Role: controller; implementation and review were delegated to tmux workers.
- Gate: `MVP typed template contract Slice 3 required-output missing/degrade implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope boundary: typed `RequiredOutputItem.when_evidence_missing` behavior in Fund-layer writer input/adapter using `EvidenceAvailability`, tests, README sync and review artifacts only.
- Explicit non-goals preserved: no live provider probe, no provider/default/runtime/budget/endpoint change, no Agent runtime/tool-loop implementation, no score/golden/readiness/promotion change, no deterministic fallback, no stdout partial report, no direct document/PDF/cache/source-helper access, no `extra_payload` business params, no edits to `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md` or `docs/fund-analysis-template-draft.md` during implementation.

## Accepted Artifacts

- Implementation evidence: `docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-implementation-evidence-20260603.md`.
- DS code review: `docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-code-review-ds-20260603.md`.
- MiMo code review: `docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-code-review-mimo-20260603.md`.
- Controller judgment: this file.

## Accepted Implementation

Slice 3 is accepted.

The implementation adds an additive typed writer path:

- `ChapterWriterInput.typed_required_output_items`.
- `ChapterWriterInput.evidence_availability`.
- `RequiredOutputEvidencePlan`.

Default writer behavior remains unchanged when typed required-output items are absent. The typed path uses stable markers such as `<!-- required_output:ch3.required_output.item_05 -->` instead of free-form required-output text markers.

The four required missing-evidence behaviors are accepted:

- `render_evidence_gap`: missing evidence can satisfy the required output only when the marker segment contains approved evidence-gap wording.
- `render_minimum_verification_question`: missing evidence can satisfy the required output only when the marker segment contains approved minimum-verification wording.
- `delete_if_not_applicable`: deletion is allowed only for `not_applicable` evidence status with a typed reason.
- `block`: writer preflight emits a fail-closed `missing_required_facts` issue before calling the LLM client; no deterministic fallback is introduced.

`EvidenceAvailability` now covers the Slice 2 residual `ch3.required_output.item_01` through `structured.basic_identity`. This is same-source and stays inside Fund-layer typed availability derivation.

## Validation

Controller reran:

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py tests/fund/template/test_typed_contracts.py
```

Result: `57 passed in 0.62s`.

```bash
uv run ruff check fund_agent/fund tests/fund
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/README.md fund_agent/fund/chapter_writer.py fund_agent/fund/evidence_availability.py fund_agent/fund/template/typed_contracts.py tests/README.md tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-implementation-evidence-20260603.md
```

Result: exited `0`.

Secret/prompt leak scan was run over touched implementation, tests, README and evidence files. Hits were existing field names, safe diagnostics assertions and README safety descriptions only; no API key, bearer token, raw provider response, raw request/response JSON, prompt body leak, draft body leak or provider config value was found.

## Review Disposition

DS review result: PASS, no blocking findings.

MiMo review result: PASS-with-risks, no blocking findings.

Non-blocking observations are accepted as residuals, not Slice 3 blockers:

- `ch3.required_output.item_01` has availability but no degrade behavior. This is acceptable because current `basic_identity` is structurally available, and absence would fail closed rather than silently degrade. Future wiring may add explicit behavior if `basic_identity` becomes optional.
- Degrade phrase matching is substring/segment based. This is acceptable for Slice 3 writer output validation; Slice 4 owns polarity-aware and allowed-context programmatic audit for positive or quasi-positive Ch3 claims.
- `_required_output_evidence_plan()` is computed twice in the current write path. The computation is pure and cheap; caching is optional future cleanup.
- `block` reuses `missing_required_facts` and degrade failures reuse `missing_required_output_marker`. Stable issue ids distinguish typed required-output cases; Service stop-reason taxonomy changes are out of scope.
- Future `MissingEvidenceBehavior` variants would fall through to `block`. This is fail-closed and protected by typed contract validation.

## Controller Decision

Accepted locally. The implementation satisfies the Slice 3 acceptance criteria from the typed template implementation plan:

- missing evidence can satisfy required output only through approved gap or verification wording;
- silent deletion is rejected unless `delete_if_not_applicable` has `not_applicable` status and a typed reason;
- `block` produces typed fail-closed behavior before provider/client success path;
- existing writer marker and missing-marker contracts remain strict;
- provider/runtime/default/live probe/Agent runtime/score/golden/readiness non-goals are preserved.

## Next Gate

Start `MVP typed template contract Slice 4 Ch3-first evidence-conditional must_not_cover implementation gate`.

Slice 4 must implement typed `MustNotCoverClause` / `EvidenceAvailability` programmatic audit for Ch3 first, using the Slice 0 calibration for label, explicit evidence-gap statement, quote and anchor-caption allowed contexts. It must keep existing programmatic blockers always-on and must not enter provider runtime, live probe, Agent runtime/tool-loop, score-loop, golden/readiness or template truth replacement.
