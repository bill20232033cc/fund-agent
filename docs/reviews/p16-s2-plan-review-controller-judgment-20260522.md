# P16-S2 Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED_READY_FOR_INDEX_PROFILE_GOLDEN_IMPLEMENTATION`

Controller accepts `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` without requiring plan revision.

The next gate is:

```text
P16-S2 index_profile benchmark-context golden implementation
```

This implementation may add production golden rows only for accepted P16-S1 `index_profile` benchmark-context scalar evidence. It must not add any `tracking_error` rows.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` | Plan under review |
| `docs/reviews/p16-s2-plan-review-mimo-20260522.md` | Independent plan review |
| `docs/reviews/p16-s2-plan-review-glm-20260522.md` | Independent plan review |
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | Accepted P16-S1 evidence |
| `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md` | Accepted P16-S1 evidence judgment |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |

Excluded inputs remain excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, and `docs/repo-audit-20260521.md`.

## First-principles Judgment

The plan makes the correct product-quality tradeoff. P16-S1 proved that five selected enhanced-index funds have annual-report-backed `index_profile` benchmark-context evidence through `FundDocumentRepository` / `FundDataExtractor`, while all `tracking_error` candidates remain blocked. P14 made `index_profile` a conditional P1 quality field for enhanced-index funds, so adding production golden rows for the current comparable scalar shape directly improves the quality denominator without inventing evidence.

The composite benchmark decision is also correct. For these funds, `benchmark_index_name=null` is the extractor's fail-closed representation of composite benchmarks, not a gap to fill by inference. The future implementation must preserve `benchmark_identity_status=composite`, add only scalar rows currently supported by strict golden/comparable semantics, and avoid rows for `benchmark_index_name`, `benchmark_index_code`, `benchmark_component_text`, or any `tracking_error` field.

## Reviewer Verdicts

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted; findings do not require plan revision |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted; findings do not require plan revision |

Both reviewers confirmed:

- the 25 proposed rows match P16-S1 evidence exactly;
- `benchmark_index_name` exclusion matches current strict golden and comparable-path constraints;
- `benchmark_component_text` tuple coverage is correctly deferred to a future schema/comparable phase;
- `tracking_error` rows are correctly prohibited;
- stop conditions and review rejection criteria are sufficient.

## Finding Dispositions

| Finding | Source | Disposition | Controller ruling |
|---|---|---|---|
| Untracked/new file validation should include explicit whitespace/conflict-marker checks | MiMo F1 | Accepted | Future implementation artifact must run explicit checks for all new or newly tracked artifacts in addition to `git diff --check HEAD`. |
| Handoff prompt does not restate full file ownership list | MiMo F2 | Accepted as non-blocking | The plan's file ownership table is authoritative; future handoff must include the owned-file list explicitly. |
| Proposed rows match P16-S1 evidence | GLM F1 | Accepted as positive confirmation | Future implementation must use the exact 25 rows unless a stop condition is triggered. |
| `benchmark_index_name` exclusion is code-consistent | GLM F2 | Accepted as positive confirmation | Future implementation must not add `benchmark_index_name` rows or synthesize a single index name. |
| Existing-row regression success signal should be explicit | GLM F3 | Accepted | Future implementation must verify rebuilt JSON preserves pre-existing golden records unchanged, especially existing `001548 index_profile` rows. |
| `benchmark_component_text` tuple exclusion is correct | GLM F4 | Accepted as positive confirmation | Tuple/list golden semantics remain deferred; do not change comparable schema in P16-S2 implementation. |
| `tracking_error` prohibition aligns with all truth sources | GLM F5 | Accepted as positive confirmation | No `tracking_error` golden implementation may be opened from P16-S1 results. |

## Implementation Gate Constraints

The next implementation handoff must require:

1. Add only the 25 planned `index_profile` scalar rows for `004194`, `005313`, `017644`, `019918`, and `019923`.
2. Preserve exact P16-S1 benchmark text punctuation, source anchors, `benchmark_identity_status=composite`, `methodology_availability=benchmark_only`, `constituents_availability=benchmark_only`, and `source_tier=benchmark_context`.
3. Do not add rows for `benchmark_index_name`, `benchmark_index_code`, `benchmark_component_text`, methodology summaries, constituents details, `missing_reasons`, or any `tracking_error.*` field.
4. Rebuild `reports/golden-answers/golden-answer.json` through the existing golden-build path.
5. Add focused tests for strict Markdown/JSON acceptance, composite benchmark no-synthesis, comparable scalar serialization, correctness matching, and quality gate behavior.
6. Verify pre-existing golden records remain unchanged after rebuild, including existing `001548 index_profile` rows.
7. Run explicit whitespace/conflict-marker checks for all new or modified artifacts, plus `git diff --check HEAD`.
8. Stop before golden edits if current extractor output diverges from P16-S1 evidence, if active null/tuple golden assertions are required, or if any row would require inferred benchmark identity or `tracking_error` evidence.

## Control Update

`docs/implementation-control.md` should record plan acceptance, reviewer verdicts, this controller judgment, and set the next entry point to P16-S2 golden implementation.

## Validation

Controller validation before commit:

```bash
git diff --check HEAD
```
