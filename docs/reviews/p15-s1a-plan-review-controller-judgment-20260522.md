# P15-S1A Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED`

Controller 接受 P15-S1A `tracking_error` source-contract / evidence-acquisition plan：

```text
PROCEED_TO_EVIDENCE_ACQUISITION_IMPLEMENTATION
```

下一 gate 进入：

```text
P15-S1A tracking_error evidence-acquisition implementation
```

该 implementation 只能生成 reviewed evidence artifact，证明 `001548` 2024 年报是否存在 direct observed
`tracking_error` 披露；不得修改 production golden rows。

## Inputs

- Plan: `docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`
- MiMo plan review: `docs/reviews/p15-s1a-plan-review-mimo-20260522.md` — `PASS_WITH_FINDINGS`
- GLM plan review: `docs/reviews/p15-s1a-plan-review-glm-20260522.md` — `PASS_WITH_FINDINGS`
- Upstream blocker: `docs/reviews/p15-s1-production-tracking-error-golden-evidence-plan-20260522.md`
- Upstream controller judgment: `docs/reviews/p15-s1-plan-review-controller-judgment-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`

## Accepted Decision

P15-S1A is the correct next step because P15-S1 proved that current reviewed repository artifacts do not contain
direct observed `tracking_error` evidence for `001548`. The shortest safe path is to acquire or disprove the evidence
through the Fund Capability document boundary, then let a separate reviewed golden gate decide whether production rows
may be added.

The accepted implementation boundary is:

1. Access `001548` 2024 annual report only through `FundDocumentRepository` or `FundDataExtractor`.
2. Produce a reviewed evidence artifact with repository provenance, structured extraction result, keyword inventory,
   accepted/rejected candidates, anchors, stop-condition result, and golden decision.
3. Stop without golden edits unless a later controller judgment accepts `ACCEPTED_DIRECT_DISCLOSURE`.

## Finding Disposition

| Finding | Source | Decision | Implementation guardrail |
|---|---|---|---|
| Helper module naming should preserve reuse intent | MiMo F1 | accepted as INFO | If a helper is introduced, use explicit `fund_code` / `report_year` parameters even when the first invocation is fixed to `001548` / 2024. |
| `needs_extractor_or_anchor_fix` path needs owner/resolution clarity | MiMo F2 | accepted as INFO | Evidence artifact must assign owner and next gate when extractor/inventory conflict or incomplete anchor prevents acceptance. |
| Test ownership list should include `standard_deviation_only` and `unparseable` | MiMo F3 | accepted as LOW | Implementation tests must cover target/limit, benchmark-only, narrative-only, standard deviation, ambiguous, unparseable, and anchor-incomplete cases. |
| `force_refresh` boundary should be explicit | MiMo F4 | accepted as INFO | Any helper docstring or artifact must state `force_refresh` only controls repository cache behavior and does not alter evidence classification. |
| `anchor_incomplete` is not explicit in success-signal test list | GLM F1 | accepted as LOW | Add explicit anchor-incomplete rejection coverage if implementation adds classifier tests. |
| `load_annual_report()` exception / no-result path is not explicit in numbered steps | GLM F2 | accepted as LOW | Implementation must map repository exceptions/no-result into source failure categories and stop fail-closed. |
| `跟踪偏离度` may not equal `跟踪误差` in every context | GLM F3 | accepted as INFO | Artifact must record context judgment for any `跟踪偏离度` hit and must not treat daily deviation as observed tracking error without direct support. |
| Helper lifecycle is undecided between permanent module and one-off helper/test | GLM F4 | accepted as INFO | Implementation report must justify whether helper code is permanent, test-only, or artifact-only, and keep scope minimal. |

No finding requires plan revision before implementation.

## Implementation Guardrails

- P15-S1A implementation must not edit `reports/golden-answers/golden-answer-prefill-reviewed.md`,
  `reports/golden-answers/golden-answer.json`, `reports/golden-answers/golden-answer-prefill.md`,
  `docs/golden-answer-template.md`, or golden tooling.
- Annual-report/source access must remain behind `FundDocumentRepository` / `FundDataExtractor`; no Service, UI,
  Engine, renderer, quality gate, or golden tooling direct PDF/cache/source-adapter access.
- Reject benchmark-only, target/limit, manager narrative, standard deviation, calculated values, ambiguous candidates,
  unparseable values, and anchor-incomplete candidates for golden eligibility.
- Repository `not_found` / `unavailable` may be recorded as source blockers; `schema_drift`, `identity_mismatch`, and
  `integrity_error` must fail closed.
- Do not introduce calculated tracking error, external index adapters, methodology/constituents extraction,
  QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop.
- Do not touch RR-13, source CSV, `docs/repo-audit-20260521.md`, Service/UI/Engine contracts, renderer behavior,
  snapshot schema, `ExtractionMode`, or quality gate severity.

## Required Implementation Output

The implementation must create:

```text
docs/reviews/p15-s1a-tracking-error-evidence-acquisition-implementation-20260522.md
```

with verdict:

- `ACCEPTED_DIRECT_DISCLOSURE`, or
- `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`, or
- `BLOCKED_SOURCE_UNAVAILABLE_OR_FAIL_CLOSED`, if repository access prevents evidence review.

## Next Step

Update `docs/implementation-control.md`, commit accepted P15-S1A plan/review artifacts, then dispatch P15-S1A
evidence-acquisition implementation to AgentCodex.
