# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 2 Code Review Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 2 Manager Roster / Strategy / Turnover Values`
- Plan artifact: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Plan controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-controller-judgment-20260620.md`
- Slice 1 accepted commit: `e6df71b`
- Implementation evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-implementation-evidence-20260620.md`
- Initial code reviews:
  - AgentDS: `docs/reviews/code-review-20260620-095003.md`
  - AgentMiMo: `docs/reviews/code-review-20260620-095109.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-fix-evidence-20260620.md`
- Targeted re-reviews:
  - AgentDS: `docs/reviews/code-review-20260620-095926.md`
  - AgentMiMo: `docs/reviews/code-review-20260620-100152.md`
- Controller verdict: `ACCEPT_SLICE2_READY_FOR_SLICE3_IMPLEMENTATION_NOT_READY`

## Decision

Accept Slice 2 implementation after fix and targeted re-review.

Slice 2 implements proof-positive `manager_profile.v1` direct extraction for exactly three public top-level values:

- `portfolio_managers`
- `manager_strategy_text`
- `turnover_rate`

It preserves fail-closed source-truth admission, direct-route `candidate_evidence=()`, public partial/missing semantics, existing `EvidenceAnchor` shape, existing gap taxonomy, and no-leakage to `current_stage.v1` / `core_risk.v1`. It does not implement `manager_alignment`, `holdings_snapshot`, facade regression, docs sync, other field families, parser replacement, source-kind expansion, upper-layer consumption, readiness or release.

## Review Disposition

| Finding | Source | Controller disposition | Evidence |
|---|---|---|---|
| Roster broad heading / `heading_path` self-authorization | DS F1 | accepted and fixed | `code-review-20260620-095926.md`, `code-review-20260620-100152.md` both verify fixed |
| Strategy body text false positive | DS F2 / MiMo 001 | accepted and fixed | targeted re-reviews verify heading-path gated matching |
| Missing-key test assertion used `dict.get()` | MiMo 002 | accepted and fixed | targeted re-reviews verify explicit key absence checks |
| Roster same-name conflict / identical duplicate coverage | DS F3/F4 / MiMo 003 | accepted and fixed | targeted re-reviews verify new conflict and duplicate tests |
| Strategy ambiguity test | MiMo optional | deferred-with-owner | deferred to future manager-profile refinement; fix did not invent new strategy ambiguity semantics |

No accepted finding remains open for Slice 2. No new blocker was reported by targeted re-review.

## Controller Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
148 passed in 0.62s
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
git diff --check
<no output>
```

## Accepted Behavior

- `manager_profile.v1` proof-positive direct route emits `partial` direct values for roster, strategy/outlook and turnover when stable allowed sources are present.
- `portfolio_managers` requires same-row manager role context and rejects broad-heading-only non-manager rows.
- `manager_strategy_text` is heading-path gated and does not match arbitrary body text containing strategy tokens under unrelated headings.
- `turnover_rate` requires disclosed percent literal; basis-only does not emit `turnover_rate`.
- Conflicting turnover and roster values are omitted with `ambiguous_table_or_locator` gaps.
- Identical roster duplicate values keep the first locator and do not create ambiguity.
- Unstable locators are skipped.
- `manager_alignment` and `holdings_snapshot` remain unimplemented and deferred to Slice 3.
- `current_stage.v1`, `core_risk.v1`, `investor_experience.v1` and other field families remain public missing for FDD source-truth direct extraction.

## Residual Risks

| Risk | Owner | Destination |
|---|---|---|
| `manager_alignment` source-truth value absent | Implementation worker | Slice 3 |
| `holdings_snapshot` source-truth value absent | Implementation worker | Slice 3 |
| Facade projection for manager-profile FDD source-truth values remains unproven | Implementation worker | Slice 4 |
| `docs/design.md` and `fund_agent/fund/README.md` not yet synced for manager-profile current facts | Implementation worker | Slice 4 |
| Strategy ambiguity semantics beyond heading-gated concatenation | Future refinement owner | Future manager-profile refinement gate |
| Real-report field correctness remains unproven | Future evidence worker | Separate evidence gate |
| `holdings_snapshot` overlap with `current_stage.v1` / `core_risk.v1` remains unresolved | Future field-family gates | Future planning gates |

## Next Entry Point

`FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Implementation Gate - Slice 3 Alignment / Holdings Snapshot / Anchor-Gap Hardening`

Release/readiness remains `NOT_READY`.
