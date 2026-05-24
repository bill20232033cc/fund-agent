# Release Maintenance 004393 Quality Gate S1 Re-Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance 004393 S1 re-review`
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S1 - P0 Extraction And Comparable Fields`
- Implementation artifact: `docs/reviews/release-maintenance-004393-quality-gate-s1-implementation-20260524.md`
- Fix artifact: `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-fix-20260524.md`
- Re-review artifacts:
  - `docs/reviews/release-maintenance-004393-quality-gate-s1-rereview-mimo-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-s1-rereview-glm-20260524.md`
- Controller conclusion: `accepted locally`

## Re-Review Summary

| Reviewer | Conclusion | Controller disposition |
|---|---|---|
| MiMo | `PASS` | Accept |
| GLM | `PASS` | Accept |

Both targeted re-reviews confirm the S1 fix closes the controller-accepted findings from `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-controller-judgment-20260524.md`.

## Finding Closure

| ID | Required fix | Controller judgment |
|---|---|---|
| `004393-S1-C1` | Bound fee table fallback to direct target `7.4.10.2.x` subsection evidence; broad labels alone must not trigger extraction; add adversarial tests. | Closed. `_extract_fee_from_fallback_tables()` now tracks target subsection context per table, `_fee_row_context()` opens context only on the exact target subsection, and tests cover unrelated broad-label fee rows plus cross-subsection collision. |
| `004393-S1-C2` | Avoid guessed parser-section anchors for table fallback; use bounded context or conservative semantic subsection anchors. | Closed. Table-derived fee fallback now anchors to `§7.4.10.2.1` / `§7.4.10.2.2`; tests assert the target subsection anchors. |

## Accepted S1 Behavior

- `basic_identity` now exposes comparable `management_company`, `custodian`, and `inception_date` values when disclosed in `§2`.
- `fee_schedule` keeps direct `§2` values as highest precedence and only falls back to parser-visible `7.4.10.2.1` / `7.4.10.2.2` evidence when each fee side is missing.
- Text fallback may use the parser section containing the located target subsection heading.
- Table fallback uses conservative semantic subsection anchors because `ParsedTable` does not carry physical parser-section metadata.
- S1 did not change Host/Agent packages, golden answers, source CSVs, config/runtime behavior, README, or turnover applicability policy.

## Validation

Controller and reviewers ran the required focused validation:

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
git diff --check
```

Observed result:

- `66 passed`
- ruff passed
- `git diff --check` passed

## Residuals

- `ParsedTable` still lacks physical parser-section metadata. This is acceptable for S1 because the accepted fix uses target subsection semantic anchors rather than fabricated parser sections.
- `turnover_rate` disclosure applicability remains a future policy/schema/gate-denominator candidate, not part of S1.
- S2 remains responsible for `holdings_snapshot`, `share_change`, and benchmark correctness normalization under the already accepted plan.

## Next Action

Update `docs/implementation-control.md`, commit S1 accepted-local state, then continue to `release-maintenance 004393 S2 P1 extraction and benchmark correctness implementation`.
