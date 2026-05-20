# P6 Aggregate Rereview Controller Acceptance - 2026-05-20

## Verdict

P6 aggregate fix is accepted. P6 is ready for ready-to-open-draft-PR reconciliation.

Review artifacts:

- Initial aggregate reviews:
  - `docs/reviews/p6-aggregate-deepreview-mimo-20260520.md`
  - `docs/reviews/p6-aggregate-deepreview-glm-20260520.md`
- Controller judgment:
  - `docs/reviews/p6-aggregate-deepreview-controller-judgment-20260520.md`
- Fix artifact:
  - `docs/reviews/p6-aggregate-fix-20260520.md`
- Targeted re-reviews:
  - `docs/reviews/p6-aggregate-rereview-mimo-20260520.md`
  - `docs/reviews/p6-aggregate-rereview-glm-20260520.md`

## Finding Closure

| Finding / risk | Controller decision | Re-review result |
|---|---|---|
| Shared evidence appendix heading | Fixed immediately | MiMo PASS / GLM PASS |
| `run_programmatic_audit` docstring missing C2 | Fixed immediately | MiMo PASS / GLM PASS |
| `locals()` guard in FQ5 contract applicability | Fixed immediately | MiMo PASS / GLM PASS |
| `preferred_lens_unresolved_chapter_ids` only first failure | Fixed by collecting all failed chapter ids while preserving field name | MiMo PASS / GLM PASS |
| `_SUPPORTED_FUND_TYPES` duplicated in contracts/item_rules | Fixed by deriving from `FundType` | MiMo PASS / GLM PASS |
| `TemplateLensRule.priority` lacks closed-set validation | Fixed with `core/high/medium/low` validation and test | MiMo PASS / GLM PASS |

## Verification

Controller verification after fix:

```text
.venv/bin/python -m pytest tests/fund/template/test_contracts.py tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
87 passed

.venv/bin/python -m pytest tests/ -q
246 passed

.venv/bin/python -m ruff check .
All checks passed!

git diff --check
passed
```

Reviewer verification:

- MiMo: `246 passed`, ruff clean, diff check clean.
- GLM: targeted `87 passed`, full suite `246 passed`, ruff clean, diff check clean.

## Deferred Risks

These remain tracked and do not block P6 PR readiness:

- P6-S6 / RR-13 `016492` duplicate App source reconciliation remains human-owned.
- RR-16 correctness denominator can be expanded in a future contract-aware correctness slice.
- RR-7 item-level Evidence Confirm remains v2 scope.
- LLM audit E1/E2/E3/C1/C2 remains v2 scope.
- Annual report source strategy remains P7 data-source migration.
- Template content refinements such as Chapter 2/4 lens expansion and Chapter 0 copy cleanup remain future content work.

## Next Gate

`P6 acceptance / ready-to-open-draft-PR reconciliation`
