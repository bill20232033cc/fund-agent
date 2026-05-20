# Post-P6 Follow-up Plan Review Controller Judgment - 2026-05-20

## Verdict

Post-P6 follow-up plan is accepted.

Plan artifact:

- `docs/reviews/post-p6-follow-up-planning-20260520.md`

## Reviewed Scope

The plan compares post-P6 candidates after deterministic template contract hardening:

- P7 annual report source migration
- RR-16 contract-aware correctness denominator expansion
- P6-S6 / `016492` human source reconciliation
- v2 Evidence Confirm / LLM audit
- ITEM_RULE renderer/audit integration
- template content/lens refinements

## Findings

No blocking findings.

## Controller Judgment

The plan correctly selects `P7 annual report source migration` as the next phase, with first gate:

```text
P7-S1 EID source research spike plan/review
```

Rationale:

- P4/P5 made extraction quality measurable and quality-gated.
- P6 made template contracts deterministic.
- The next root reliability dependency is document source trust, provenance, and fallback behavior.
- P7 can improve the foundation for future correctness expansion, Evidence Confirm, and LLM audit without changing Service/UI boundaries.
- P7-S1 is correctly scoped as research/planning before implementation, because the EID public access path, identifiers, rate limits, and schema drift behavior must be verified before code changes.

## Boundary Checks

- The plan keeps source-specific logic behind `FundDocumentRepository`.
- The plan does not propose Service/UI awareness of EID, Eastmoney, akshare, 天天基金, or PDF URLs.
- The plan does not bypass the repository boundary or direct fund document filesystem access.
- The plan does not put explicit parameters in `extra_payload`.
- The plan keeps `016492` duplicate reconciliation human-owned.
- The plan defers Evidence Confirm / LLM audit until source metadata is reliable.

## Residual Risks

Accepted and tracked:

- P6-S6 / RR-13 duplicate `016492` remains user/App-source owned.
- RR-16 correctness denominator expansion remains a future contract-aware correctness slice after source/provenance hardening.
- RR-7 item-level Evidence Confirm remains v2 scope.
- LLM audit E1/E2/E3/C1/semantic C2 remains v2 scope.
- ITEM_RULE renderer/audit integration and template content refinements remain future template/audit work.

## Next Gate

`P7-S1 EID source research spike plan/review`

No source code should change until P7-S1 plan is reviewed and accepted.
