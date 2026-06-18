# MVP typed template contract Slice 1 typed schema sidecar controller judgment

## Judgment

ACCEPTED WITH NON-BLOCKING RESIDUAL RISK.

The `MVP typed template contract Slice 1 typed schema sidecar implementation gate` is accepted locally. The implementation adds an additive Fund-layer typed contract schema sidecar and focused tests without replacing template truth or changing current runtime behavior.

This judgment does not authorize provider/runtime/default changes, live PASS-only probe, Agent runtime implementation, score-loop, golden/readiness changes, template truth replacement, auditor relaxation, deterministic fallback, or stdout partial-report behavior.

## Accepted Artifacts

- Implementation evidence: `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-implementation-evidence-20260603.md`
- DS review: `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-code-review-ds-20260603.md`
- MiMo review: `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-code-review-mimo-20260603.md`

MiMo returned PASS with no blocking findings. DS returned PASS-WITH-RISKS with one non-blocking naming risk.

## Accepted Implementation

Touched implementation and documentation files:

- `fund_agent/fund/template/typed_contracts.py`
- `fund_agent/fund/template/__init__.py`
- `tests/fund/template/test_typed_contracts.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

The accepted implementation:

- adds schema/version literals for `typed_chapter_contract.v1`;
- adds typed schema objects for `TypedChapterContract`, `TypedTemplateContractManifest`, `MustAnswerClause`, `MustNotCoverClause`, `EvidencePredicate`, `RequiredOutputItem`, `MissingEvidenceBehavior`, `TemplateLensRule`, `ChapterInternalSubcontract` and `AuditFocusLiteral`;
- projects current `contracts.py` manifest into typed contracts through explicit reviewed exact string mapping;
- preserves public chapter ids exactly as `0-7`;
- keeps Ch2 `performance`, `attribution` and `cost` as internal subcontracts under public `chapter_id=2`;
- declares Ch0 `consumes_chapter_conclusions=(7,)` and `independent_action_source=False`;
- treats `audit_focus` as closed-set semantic-only data and does not use it to disable programmatic blockers;
- validates fail-closed for schema version, chapter ids, duplicate ids, dependency ids, required output item ids, clause id prefixes, evidence statuses, allowed contexts, Ch2 internal subcontracts and preferred lens shape;
- leaves current manifest, renderer, auditor, deterministic `analyze/checklist`, `--use-llm` fail-closed behavior and provider/runtime/default behavior unchanged.

## Controller Disposition Of Findings

| Finding | Reviewer | Controller disposition | Owner |
|---|---|---|---|
| `typed_contracts.TemplateLensRule` and `contracts.TemplateLensRule` are separate same-name classes. Package-level `TemplateLensRule` still resolves to the existing contracts class, so there is no current public import regression; future callers could confuse the two classes. | DS and MiMo | Accepted as non-blocking residual. No Slice 1 fix is required because the accepted Slice 1 plan explicitly asked for a typed `TemplateLensRule` object and current package-level behavior is unchanged. Before Service facade wiring or any broad package-level typed API consumption, a later gate should either rename the typed class to `TypedTemplateLensRule` or reuse the contracts class deliberately. | Slice 2/Slice 7 controller and reviewers |
| `get_typed_chapter_contract()` reloads and revalidates the full manifest per call. | DS | Accepted as non-blocking residual. Current Slice 1 is schema/test sidecar only and not a hot runtime path. Caching can be considered when typed contracts enter Service/Agent execution. | Future wiring gate |

## Validation

Controller independently reran:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py
uv run ruff check fund_agent/fund/template tests/fund/template
git diff --check -- docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-implementation-evidence-20260603.md fund_agent/fund/README.md fund_agent/fund/template/__init__.py fund_agent/fund/template/typed_contracts.py tests/README.md tests/fund/template/test_typed_contracts.py
```

Results:

- `18 passed`
- `ruff` all checks passed
- `git diff --check` exited `0`

Secret scan over touched files and review artifacts found only existing safety-statement text in README/review docs and no secret values.

## Next Gate

Start `MVP typed template contract Slice 2 same-source EvidenceAvailability implementation gate`.

Allowed next scope:

- Fund-layer `EvidenceAvailability`, `RequirementAvailability`, `AvailabilityStatus`, `EvidenceRequirementId` and safe gap references;
- pure same-source derivation from `ChapterFactProjection` / `ChapterFactInput` facts, anchors, missing reasons and existing gap structures;
- distinct `available`, `missing`, `unavailable`, `not_applicable` and `unreviewed` states;
- requirement-sensitive availability ids for Ch3 manager strategy, turnover, holdings snapshot, cross-period style evidence and manager alignment;
- Ch2 requirement ids under public chapter 2 typed subcontracts;
- tests proving no repository/PDF/cache/source-helper/Service/Host/provider/retained-report/filesystem reads.

Not authorized in Slice 2:

- changing current renderer/auditor behavior;
- changing deterministic `analyze/checklist` defaults;
- changing `--use-llm` fail-closed behavior;
- provider/runtime/default/budget/endpoint changes;
- live PASS-only probe;
- Agent runtime/tool-loop;
- score-loop, golden/readiness, promotion or quality-gate semantic changes;
- multi-year annual evidence runtime loading.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text or raw parsed annual-report text.
