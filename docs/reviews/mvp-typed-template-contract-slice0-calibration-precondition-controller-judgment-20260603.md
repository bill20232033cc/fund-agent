# MVP typed template contract Slice 0 calibration/precondition controller judgment

## Judgment

ACCEPTED.

The `MVP typed template contract Slice 0 calibration/precondition gate` is accepted as a calibration/evidence-only checkpoint. It satisfies the hard preconditions from the accepted typed-template implementation planning gate and may serve as the reviewed reference for the next typed-template implementation slices.

This judgment does not authorize provider/runtime/default changes, a live PASS-only probe, Agent runtime implementation, score-loop work, golden/readiness changes, template truth replacement, auditor relaxation, deterministic fallback, or stdout partial-report behavior.

## Accepted Artifacts

- Slice 0 evidence: `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`
- DS review: `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-review-ds-20260603.md`
- MiMo review: `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-review-mimo-20260603.md`

Both independent reviews returned PASS with no blocking findings.

## Controller Disposition

The Slice 0 evidence is accepted because it closes the preconditions that were blocking implementation handoff:

- Slice 0 output form is `reference markdown only`; future Slice 4 owns programmatic fixture/test-data encoding.
- Ch3 Chinese polarity taxonomy treats `未见明显不一致`, `基本一致`, `大体一致`, `倾向一致` and similar wording as quasi-positive claims that block under missing, unavailable or unreviewed evidence.
- `allowed_contexts` matching is deterministic and limited to `required_label`, `evidence_gap_statement`, `quote` and `anchor_caption`; no LLM judgment is allowed.
- Same-source evidence identifies the current `programmatic:C2:言行一致` path as `chapter_auditor.py` global phrase extraction from `must_not_cover`, not `_FORBIDDEN_CONTENT_RULES`.
- The artifact distinguishes the current `_MUST_NOT_COVER_COVERAGE_RULES` narrative-guidance declaration from the separate runtime phrase-extraction path, and requires Slice 4 to avoid duplicate enforcement.
- `RequiredOutputItem` behavior is split into render gap, block, and delete-if-not-applicable, with active-fund Ch3 labels preserved rather than silently deleted.
- Existing active-fund Ch3 renderer degradation is preserved as a current behavior to formalize, not bypass.
- Slice 1 adapter mapping must be explicit and reviewed; fuzzy, substring, embedding or LLM mapping is not accepted.
- Any future C2 issue-id migration must include diagnostic serializer and retained-artifact impact analysis before implementation.

## Accepted Residual Risks

These risks are non-blocking for accepting Slice 0 and are assigned to later slices:

| Risk | Disposition | Owner |
|---|---|---|
| Polarity taxonomy is a seed set, not an exhaustive Chinese synonym universe. | Slice 4 must encode parameterized fixtures and fail closed for unreviewed positive/quasi-positive variants. | Slice 4 implementation/review |
| Allowed-context edge cases may appear around multi-sentence gaps, nested quotes or mixed label/assertion lines. | Slice 4 tests must cover boundary examples from this artifact before accepting typed enforcement. | Slice 4 implementation/review |
| `_MUST_NOT_COVER_COVERAGE_RULES` validation may conflict with a new typed `MustNotCoverClause` path. | Slice 4 must update, migrate or supersede the relevant coverage declaration consistently. | Slice 4 implementation/review |
| C2 issue-id migration from phrase/hash to stable `clause_id` affects retained diagnostics. | Slice 4 must include serializer and retained-artifact compatibility analysis before issue-id changes. | Slice 4 implementation/review |
| Current active-fund Ch3 renderer default is coarse and treats active funds as missing reviewed style evidence. | Slice 2/3 may replace the coarse default with typed `EvidenceAvailability`, while preserving visible degradation when reviewed evidence is absent. | Slice 2/3 implementation/review |

## Next Gate

Start `MVP typed template contract Slice 1 typed schema sidecar implementation gate`.

Allowed next scope:

- additive Fund-layer typed contract schema sidecar;
- stable typed schema/version literals;
- typed objects such as `TypedChapterContract`, `MustAnswerClause`, `MustNotCoverClause`, `EvidencePredicate`, `RequiredOutputItem`, `MissingEvidenceBehavior`, `TemplateLensRule`, `ChapterInternalSubcontract` and `AuditFocusLiteral`;
- loader/projection that maps current 8 public chapters into typed contracts while preserving ids `0-7`;
- Ch2 internal subcontracts only under public `chapter_id=2`;
- Ch0 typed dependency on Ch7;
- semantic-only `audit_focus` data;
- fail-closed validation for ids, dependencies, required output item ids, clause ids and closed literals;
- focused tests for the additive schema sidecar and existing manifest non-mutation.

Not authorized in Slice 1:

- replacing `docs/fund-analysis-template-draft.md` or rewriting current template truth;
- changing current deterministic `analyze/checklist` defaults;
- changing current `--use-llm` fail-closed behavior;
- provider/runtime/default/budget/endpoint changes;
- live PASS-only probe;
- score-loop, golden/readiness, promotion or quality-gate semantic changes;
- Agent runner/tool-loop/ToolRegistry/ToolTrace implementation;
- multi-year annual evidence runtime implementation;
- direct document/PDF/cache/source-helper access outside the accepted repository boundary;
- business parameters through `extra_payload`, `**kwargs` or untyped payload bags.

## Validation

Controller validation for this judgment should remain docs-only:

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-review-ds-20260603.md docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-review-mimo-20260603.md docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-controller-judgment-20260603.md
```

Secret-safety statement: this judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text or raw parsed annual-report text.
