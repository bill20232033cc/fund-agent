# Redemption Share Class Column Alignment Repair Plan — Controller Judgment

> Date: 2026-05-28
> Gate: `redemption share class column alignment repair gate`
> Controller: Codex
> Status: **accepted for implementation**

## Scope Decision

This gate is a narrow repair gate for `redemption_share_pressure` column alignment only.

Allowed implementation scope:

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- gate evidence artifacts under `docs/reviews/`

Out of scope:

- `drawdown_stress`
- `credit_risk` redesign
- generic `share_change` extractor
- schema, score policy, snapshot schema, quality gate semantics
- Service, UI, Host, Agent, dayu architecture
- QDII, FOF, `110020`, golden readiness, release readiness
- push, PR, merge, promotion

## Dirty Scope Decision

The current workspace contains uncommitted implementation from the previous narrow false-negative gate. That gate stopped at validation failure before accepted implementation commit.

Controller classification:

- Reusable baseline: current dirty diff in `fund_agent/fund/extractors/bond_risk_evidence.py` and `tests/fund/extractors/test_bond_risk_evidence.py`, including accepted/re-reviewed `credit_risk`, drawdown boundary preservation, §2 mapping, §10 table selection, row matching, Decimal parsing, arithmetic checks, metric formatting, and existing tests.
- Failure evidence: previous narrow-gate implementation/review/fix/re-review artifacts and validation failure judgment.
- Current repair artifacts: this gate's plan, plan reviews, plan fix, re-reviews, and this controller judgment.
- Unrelated untracked files: `--help`, unrelated comprehensive/repo review artifacts, and `docs/tmux-agent-memory-store.md`; these must not be staged in this gate.

The implementation worker must build on the current reusable dirty diff and add the missing repair. It must not discard the previous diff blindly and must not assume the current diff already contains the repair.

## Root Cause Accepted

Real `006597 / 2024` §10 share-change table, reproduced through `FundDocumentRepository`, has unlabeled class value columns:

```python
headers=(
    "基金合同生\n效日（2018\n年12月3日）\n基金份额总\n额",
    "191,879,496.71",
    "46,593,432.66",
    "-",
    "-",
)
```

The value columns do not contain A/C/E/F labels or fund codes. The previous implementation required each class to match a header by fund code or class label, so it fail-closed with:

```text
na_reason=share_class_column_count_mismatch
```

The repair must add a conservative unlabeled positional alignment path. For `006597`, §2 mapping order is:

```text
A=006597, C=006598, E=014217, F=022176
```

When §10 headers are fully unlabeled and value-column count equals class count, columns 1..4 may align to A/C/E/F only if all guardrails pass.

## Required Guardrails

Implementation must preserve fail-closed behavior:

- explicit header matching remains preferred when labels/codes exist
- mixed explicit/unlabeled signal fails closed
- positional alignment is allowed only for fully unlabeled class columns
- row-label column precondition must pass
- required rows must be present and unique
- all aligned values must parse
- per-class arithmetic must reconcile
- aggregate arithmetic must reconcile
- §2 ending-share cross-check must reconcile
- missing anchors or missing cross-check must stay `ambiguous`

The §2 ending-share cross-check must use the same profile table that contains:

- `下属分级基金的基金简称`
- `下属分级基金的交易代码`
- `报告期末下属分级基金的份额总额`

It must exclude the current §10 table by `(page_number, table_index)` and must not use generic `期末基金份额总额` rows from arbitrary tables.

Real §2 table evidence for `006597 / 2024`:

- page 5 table 0 row 9: A/C/E/F fund short names
- page 5 table 0 row 10: `006597 / 006598 / 014217 / 022176`
- page 5 table 0 row 11: `5,711,224,267.09 / 4,760,029,015.27 / 25,795,859.12 / 52,531,021.84`

## Plan Review Result

Artifacts:

- Plan: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md`
- DS review: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-review-ds-20260528.md`
- MiMo review: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-review-mimo-20260528.md`
- Plan fix: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-fix-20260528.md`
- DS re-review: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-rereview-ds-20260528.md`
- MiMo re-review: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-rereview-mimo-20260528.md`

Controller accepts both re-review verdicts:

- DS: **PASS**
- MiMo: **PASS**

All accepted plan findings are closed or explicitly accepted as residual:

- §2 cross-check circularity closed
- real §2 table shape added
- current dirty-diff gap made explicit
- `headers[0]` row-label precondition added
- `_share_change_value_columns` contract clarified
- metric string assertions corrected for `_format_decimal`
- fail-closed tests expanded
- redemption row sign semantics clarified

## Implementation Authorization

Implementation may proceed under the accepted plan.

The implementation worker must stop and return to controller if:

- the real §2 profile table cannot be found through `ParsedAnnualReport`
- unlabeled positional alignment would require guessing column meaning
- reliable all-class A/C/E/F aggregation cannot be achieved
- any change requires schema, score, snapshot, quality gate, Service/UI/Host/Agent/dayu, golden, or release work
- any validation fails

## Expected Outcome

If implementation succeeds:

- `redemption_share_pressure` moves from `ambiguous` to `accepted`
- `bond_risk_satisfied_groups` includes `redemption_share_pressure`
- `bond_risk_ambiguous_groups` no longer includes `redemption_share_pressure`
- `drawdown_stress` remains weak
- score `missing_evidence_groups` should drop to only `["drawdown_stress"]`
- quality gate may remain `warn` because drawdown is a real residual

This gate stops at accepted local validation and controller judgment, not PR readiness.
