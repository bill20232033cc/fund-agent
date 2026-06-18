# MVP fund report template typed contract redesign design review fix evidence

## Worker Self-Check

- Role: scoped design fix worker only, not controller.
- Gate: `MVP fund report template typed contract redesign gate`.
- Fix target: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`.
- Source reviews: AgentMiMo findings 1-12 and AgentDS findings 1-8.
- Allowed files: this evidence artifact and the target design artifact only.
- Actions intentionally not taken: no Gateflow/Phaseflow controller start, no implementation, no code/test/prompt/template/provider/auditor/runtime/report/golden/quality-gate/score-loop changes, no truth-source edits, no commit, no push, no PR.

## Fix Summary

The design artifact was tightened so a later gate cannot misread candidate design as accepted implementation scope. The fixes clarify that typed contract work remains design-only, preserves current chapter ids `0-7`, keeps programmatic blockers fail-closed, and defers runtime/provider/structural/facet/evidence-bundle work to separate gates.

## Accepted Finding Clusters And Changes

- MiMo F1 / DS F3: `audit_focus` boundary and composition clarified. The design now states `audit_focus` only controls bounded LLM semantic audit emphasis and repair hint grouping. Evidence predicates control clause applicability, while `audit_focus` never disables programmatic participation. Programmatic checks for `data_availability_match`, `evidence_gap_declaration`, `cross_chapter_consistency`, and `first_class_facet_respect` are separate programmatic audit extension gates.
- MiMo F2 / DS F6: `EvidenceAvailability.source_strength_by_requirement` is no longer accepted as an implementable field. It is deferred unless a later gate defines strength levels, relationship to availability/data-tier flags, and audit semantics. Year-tier/data-tier availability for `1Y/3Y/5Y` and report-year coverage was added.
- MiMo F3 / MiMo F6: `allowed_contexts` behavior is bounded. Programmatic C2 is expected to use `allowed_contexts` for the retained Ch3 failure mode. `required_label`, `evidence_gap_statement`, `anchor_caption`, and `quote` are each constrained, and `quote` cannot be used to add or imply positive conclusions.
- MiMo F4: External draft D-2 timeout percentage/root-cause allocation is explicitly rejected as unsupported. Ch2/Ch4/Ch6 timeout evidence remains provider runtime gate evidence because retained diagnostics show `small_prompt_provider_timeout`.
- MiMo F5: Evidence-conditional `must_not_cover` scope is narrowed to the retained Ch3 failure mode. Broader applicability is marked plausible but requiring more calibration evidence.
- MiMo F7 / DS RR-4: `EvidenceAvailability` is defined as a derived supplemental availability view over same-source `ChapterFactProjection`, not a replacement unless later accepted by a separate gate.
- MiMo F8 / DS F4: Ch0/Ch7 safety now requires final assembly to fail closed if any required body chapter is not accepted. Ch0 must not mask unsafe Ch7, and future Ch2 split must revisit the Ch7 dependency chain.
- MiMo F9 / MiMo F10 / DS F2: Typed contract precision and Ch2 structural split are explicitly independent dimensions. Chapter ids remain `0-7`; Ch2 internal performance/attribution/cost units stay inside a single `ChapterContract(chapter_id=2)` and cannot appear as independent matrix rows or public chapters.
- MiMo F11: Partial availability behavior was added. Bounded conclusions may only cover available evidence and must name missing boundaries; positive or quasi-positive Ch3 conclusions remain blocked when required evidence is missing or unreviewed.
- MiMo F12 / DS F7: Overlapping `MustAnswerClause` fallback is deferred. `RequiredOutputItem.when_evidence_missing` is the accepted missing/degrade mechanism, and item-level `block` criteria are defined for unsafe missing evidence.
- DS F1: Chinese polarity/quasi-positive detection is now a mandatory precondition before implementation. Brittle global phrase matching is explicitly not accepted as the solution.
- DS F5: `first_class_facets` was removed from the accepted `ChapterContract` shape and deferred to a separate facet wiring/programmatic audit gate.
- DS F8: A `Handoff Criteria` section was added with accepted decisions, deferred/rejected items, mandatory preconditions before implementation, and likely next gate options.

## No Code Or Truth Changes

No source code, tests, runtime behavior, prompts, templates, provider settings, auditors, retained reports, score-loop, golden/quality gate, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, or `docs/fund-analysis-template-draft.md` were changed.

## Validation

Validation commands run:

```bash
git diff --check -- docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-fix-evidence-20260602.md
rg -n "AKIA|ASIA|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|Authorization:|Bearer |password|secret|api[_-]?key|x-api-key|cookie" docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-fix-evidence-20260602.md
git diff --no-index --check -- /dev/null docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md
git diff --no-index --check -- /dev/null docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-fix-evidence-20260602.md
```

Results:

- `git diff --check -- ...`: pass, no whitespace diagnostics.
- Secret-safety `rg`: pass, no matches.
- `git diff --no-index --check -- /dev/null <file>` for both allowed files: no whitespace diagnostics. Exit code is non-zero as expected for no-index comparison against `/dev/null`.

Secret-safety statement: this artifact and the edited design artifact contain no API key, Authorization header, Bearer token, cookie, password, private key, raw provider response, raw prompt body, or secret-bearing runtime payload. They reference only safe local artifact paths, safe diagnostic labels, and short design excerpts needed for review-fix traceability.

## Residual Risks And Open Questions

- The next controller must choose whether the next gate is Ch3-only contract-shape calibration or a broader typed contract schema plan with Ch3 as the first fixture.
- Chinese assertion polarity/quasi-positive detection still needs feasibility/calibration before implementation.
- Programmatic audit extensions for data availability matching, evidence-gap declarations, cross-chapter consistency, and facet respect remain separate gates.
- Provider runtime timeout investigation for Ch2/Ch4/Ch6 remains outside this design-fix scope.
- Any Ch2 structural split, 0+9/0+10 numbering, or public chapter count change remains deferred to a separate structural gate.
