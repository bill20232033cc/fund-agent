# Controller Judgment: S6-D Manager Profile Candidate Selector Implementation

## Gate

- Gate: `FundDisclosureDocument S6-D Manager Profile Candidate Selector Implementation Gate`
- Classification: `heavy implementation gate`
- Work unit type: feature slice inside the Fund Processor/Extractor route

## Inputs Reviewed

- Accepted plan: `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-plan-20260619.md`
- Plan controller judgment: `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-plan-controller-judgment-20260619.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-implementation-evidence-20260619.md`
- Code review: `docs/reviews/code-review-20260619-113101.md`
- Implementation diff:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
  - `fund_agent/fund/README.md`
  - `docs/design.md`

## Decision

`ACCEPT_S6D_MANAGER_PROFILE_CANDIDATE_SELECTOR_IMPLEMENTATION_NOT_READY`

The implementation is accepted for local checkpoint commit. It adds exactly one new field-family selector, `manager_profile.v1`, inside `FundDisclosureDocumentProcessor` and keeps the result as candidate-only locator evidence.

## Accepted Facts

- `manager_profile.v1` candidate evidence is attached only to `FundFieldFamilyResult.candidate_evidence`.
- Public field-family state remains `status="missing"`, `extraction_mode="missing"`, `value={}`, and `anchors=()`.
- Candidate records remain `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.
- Role order is `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holdings_snapshot`.
- Source order is sections, paragraph blocks, table blocks, then table cells.
- Source paths are stable and family-local dedupe is by exact `source_field_path`.
- The accepted limit is 16 manager-profile records.
- Controller guard amendments A1/A2 are implemented:
  - `portfolio_managers` generic roster tokens require `基金经理` or `管理人` in the allowed source-level guard context.
  - `manager_alignment` generic holding tokens require `基金经理`, `从业人员`, or `基金管理人` in the allowed source-level guard context.
  - positive and negative guard tests are present.
- `docs/design.md` and `fund_agent/fund/README.md` were synchronized to current code facts without source-truth, parser-replacement, readiness, release, or upper-layer consumption claims.

## Review Disposition

MiMo code review `docs/reviews/code-review-20260619-113101.md` final verdict is `PASS` with no material findings. A transient false-positive finding about missing `从业人员持有` was corrected after source-level verification; current implementation includes all three `manager_alignment` generic tokens.

## Validation Accepted

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result: exit code 0; `56 passed`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
```

Result: exit code 0; `All checks passed!`.

```bash
git diff --check
```

Result: exit code 0; no output.

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Result: exit code 0; no output.

## Explicit Non-Readiness

This accepted implementation does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, PR readiness, or upper-layer consumption. Release/readiness remains `NOT_READY`.

## Residual Risks

- Token false positives can still occur because locator matching is not semantic field correctness. Candidate-only status bounds the risk.
- `holdings_snapshot` locator overlap with future `current_stage.v1` / `core_risk.v1` selectors remains a future selector-planning concern.
- `turnover_rate` remains negative-guarded rather than positive-context guarded, as accepted by S6-D plan controller amendment A3.

## Next Entry Point

`FundDisclosureDocument S6-D Accepted Slice Commit Gate`, then `FundDisclosureDocument S6-E Single-family Candidate Evidence Selector Planning Gate`.

S6-E planning must choose exactly one remaining field family from `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1`, or explicitly block with reasons. It must not implement any selector before a reviewed plan is accepted.
