# MVP typed template contract implementation planning controller judgment

## Judgment

ACCEPTED WITH HARD PRECONDITIONS.

The `MVP typed template contract implementation planning gate` plan is accepted as a plan-only checkpoint. It is code-generation-ready for the next planning/evidence slice sequence, but it does not authorize implementation yet.

## Accepted Artifacts

- Plan: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`
- DS review: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-review-ds-20260603.md`
- MiMo review: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-review-mimo-20260603.md`

Both independent reviews returned PASS with no blocking findings.

## Controller Disposition

The plan is accepted because it directly advances the phase objective from prompt patching toward typed template/audit/evidence contracts while preserving the current runtime boundaries:

- public chapter ids remain `0-7`;
- Ch2 performance / attribution / cost are internal typed subcontracts only;
- `EvidenceAvailability` is same-source and derived from `ChapterFactProjection`;
- `audit_focus` remains semantic-only and cannot disable programmatic blockers;
- deterministic `analyze/checklist` defaults remain unchanged;
- incomplete `--use-llm` remains fail-closed with no deterministic fallback;
- provider-runtime, PASS-only live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness and template truth replacement remain out of scope.

The accepted slice order is:

1. Slice 0 calibration/precondition gate.
2. Slice 1 additive typed contract schema sidecar.
3. Slice 2 same-source `EvidenceAvailability`.
4. Slice 3 `RequiredOutputItem.when_evidence_missing`.
5. Slice 4 Ch3-first evidence-conditional `must_not_cover`.
6. Slice 5 bounded semantic `audit_focus`.
7. Slice 6 Ch0 consumes Ch7 / fail-closed readiness.
8. Slice 7 Service facade wiring behind explicit typed path.
9. Slice 8 docs/control truth sync after implementation acceptance.

## Hard Preconditions From Review

These are accepted as mandatory entry criteria for later slices:

1. Slice 0 must define the output form of the calibration artifact. It must either provide a reusable fixture/test-data module path for later tests or explicitly state that Slice 4 owns the programmatic encoding while Slice 0 is the accepted reference document.
2. Slice 0 must define deterministic `allowed_contexts` matching rules for `required_label`, `evidence_gap_statement`, `quote` and `anchor_caption`. The matching rules must not depend on LLM judgment.
3. Before Slice 4 implementation, the exact current code path that emits `programmatic:C2:言行一致` must be identified from same-source code and retained evidence. The controller must decide whether typed `MustNotCoverClause` extends, migrates or replaces the relevant existing path.
4. Slice 4 must explicitly handle existing `_MUST_NOT_COVER_COVERAGE_RULES` / current narrative-guidance behavior and avoid duplicate or conflicting enforcement paths.
5. Slice 3 must preserve and formalize the existing active-fund Ch3 renderer evidence-aware degradation behavior; typed missing/degrade semantics must not create a divergent parallel rule.
6. Slice 1 adapter mapping from current natural-language contract strings to typed ids must use explicit reviewed mapping, not fuzzy matching. Any unmapped current item must fail closed.
7. Any change to C2 issue id format, such as moving from phrase-hash ids to stable `clause_id`, must include diagnostic serializer / retained artifact impact analysis before implementation.
8. Slice 6 must decide whether to extend current `FinalChapter7Summary` or introduce a new typed Ch7 bundle before code changes.

## Next Gate

Start `MVP typed template contract Slice 0 calibration/precondition gate`.

Allowed next scope:

- planning/evidence artifact only;
- Chinese assertion polarity / quasi-positive fixture taxonomy;
- deterministic `allowed_contexts` matching specification;
- Ch3 current C2 code-path/root-cause evidence plan or direct code-path evidence;
- required-output `block` criteria;
- explicit fixture artifact shape for future tests.

Not authorized:

- source implementation;
- test implementation;
- template truth replacement;
- provider-runtime or PASS-only live probe;
- Agent runtime implementation;
- score-loop;
- auditor relaxation or fail-open behavior;
- deterministic fallback for incomplete LLM results.

## Validation

Controller validation for this judgment should remain docs-only:

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-implementation-planning-controller-judgment-20260603.md
```

Secret-safety statement: this judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
