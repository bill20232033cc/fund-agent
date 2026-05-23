# P16-S2.1 Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED_READY_FOR_NARROW_BENCHMARK_TEXT_NORMALIZATION_IMPLEMENTATION`

Controller accepts `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` without requiring plan revision.

The next gate is:

```text
P16-S2.1 benchmark_text newline normalization implementation
```

This implementation may touch only the profile extractor benchmark path, focused profile tests, and the implementation artifact unless a stop condition is triggered.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` | Decision plan under review |
| `docs/reviews/p16-s2-1-plan-review-mimo-20260522.md` | Independent plan review |
| `docs/reviews/p16-s2-1-plan-review-glm-20260522.md` | Independent plan review |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` | P16-S2 blocker evidence |
| `docs/reviews/p16-s2-code-review-controller-judgment-20260522.md` | Accepted P16-S2 blocker judgment |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |

Excluded inputs remain excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, and `docs/repo-audit-20260521.md`.

## First-principles Judgment

Narrow benchmark-text normalization is the correct next implementation path. The embedded newlines in `017644` and `019918` are PDF table-cell layout artifacts, not semantic benchmark components. Preserving them as production golden expected values would either break reviewed Markdown table parsing or force a second JSON-only golden truth path. Normalizing at the Fund Capability profile extractor benchmark boundary keeps evidence同源, preserves annual-report anchors, and avoids masking correctness issues downstream in snapshot, score, renderer, or quality-gate layers.

The alternative raw-newline path is rejected for this phase because it optimizes for parser artifact fidelity over stable structured evidence. If future requirements need true multiline golden expected values, that must be designed as a separate golden schema/comparable phase.

## Reviewer Verdicts

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted; findings become implementation constraints |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted; findings become implementation constraints |

Both reviewers confirmed:

- normalization belongs in `fund_agent/fund/extractors/profile.py`, not in parser internals, golden, snapshot, score, renderer, service, or quality gate;
- raw newline expected values are unsafe for the current reviewed Markdown / golden-build path;
- tests must cover affected `017644` / `019918` and unaffected `004194` / `005313` / `019923`;
- `benchmark_identity_status=composite`, `benchmark_index_name=None`, anchors, and benchmark-only availability must remain unchanged.

## Finding Dispositions

| Finding | Source | Disposition | Controller ruling |
|---|---|---|---|
| Simpler newline removal may be preferable to complex ASCII-token spacing | MiMo F-1, GLM F1 | Accepted as implementation guidance | Implementation should use the narrowest rule that passes the five required cases. For this phase, removing embedded newlines in benchmark text is acceptable if unaffected cases remain byte-for-byte unchanged. |
| Anchor note must be normalized with benchmark_text | MiMo F-2, GLM F2 | Accepted as hard implementation constraint | Implementation must ensure the evidence anchor note derived from the benchmark row consumes the same normalized value as `benchmark_text`. Because `_MatchedField` is frozen, implementation must handle this explicitly rather than mutating in place. |

## Implementation Gate Constraints

The next implementation handoff must require:

1. Modify only the profile extractor benchmark path, preferably in `fund_agent/fund/extractors/profile.py`.
2. Normalize embedded newlines for `benchmark_text` before both benchmark value and benchmark anchor note are built.
3. Preserve punctuation variants, ordinary non-newline spacing, table anchors, `benchmark_identity_status=composite`, `benchmark_index_name=None`, `benchmark_component_text` semantics, `methodology_availability=benchmark_only`, `constituents_availability=benchmark_only`, and `source_tier=benchmark_context`.
4. Add focused tests for affected newline shapes and unaffected no-op shapes.
5. Do not edit production golden files in P16-S2.1.
6. Do not add `tracking_error`, synthesize benchmark index names, change parser/source/repository fallback behavior, or introduce external data.
7. Produce an implementation artifact explaining source/test changes, validation results, and whether P16-S2 golden implementation may resume.

## Control Update

`docs/implementation-control.md` should record P16-S2.1 plan acceptance and set the next entry point to P16-S2.1 normalization implementation.

## Validation

Controller validation before commit:

```bash
git diff --check HEAD
```
