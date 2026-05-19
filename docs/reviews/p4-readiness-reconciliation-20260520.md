# P4 Readiness Reconciliation - 2026-05-20

## Verdict

P4 functional readiness is accepted for final aggregate deepreview.

This is not yet a draft-PR-ready verdict. The next gate should be `P4 final aggregate deepreview`, followed by a scope hygiene pass before `ready-to-open-draft-PR`.

## Inputs

- Design truth: `docs/design.md`
- P4 control doc: `docs/implementation-control-p4.md`
- Global control doc: `docs/implementation-control.md`
- P4 aggregate fix/re-review controller judgment: `docs/reviews/p4-aggregate-rereview-controller-judgment-20260519.md`
- Correctness slice controller judgment: `docs/reviews/correctness-slice-code-review-controller-judgment-20260519.md`
- Style positioning reconciliation: `docs/reviews/style-positioning-field-reconciliation-20260519.md`
- Correctness golden answer completion: `docs/reviews/correctness-golden-answer-completion-20260519.md`

## Accepted Functional Scope

| Area | Readiness judgment |
|---|---|
| Snapshot | Accepted. P4-S1 established selected-fund extraction snapshot and summary artifacts. |
| Score | Accepted. P4-S2 scores coverage / traceability and emits `score.json` / `score.md` / `golden_set.json`. |
| Fund type fix | Accepted. P4-S3a fixed the `004393` `index_fund` misclassification and verified real snapshot output as `active_fund`. |
| High-impact extractor fixes | Accepted. P4-S3b improved the selected `004393` high-impact fields and documented remaining gaps. |
| Quality gate skeleton | Accepted. P4-S4 consumes `score.json`, blocks P0 fail, warns P1 fail, and emits quality gate artifacts. |
| Per-fund blocking | Accepted fixed. `fund_scores` prevents field aggregate averages from hiding single-fund P0 failure. |
| Golden answer chain | Accepted. Reviewed Markdown builds strict `fund-agent.golden-answer.v1` JSON. |
| Correctness comparison | Accepted. P4-R10 is closed; explicit golden mismatch can trigger `FQ1/block`. |
| `style_positioning` field contract | Accepted. Field is now `product_profile.style_positioning`, not `manager_strategy_text.style_positioning`. |

## Deferred Items

These items do not block current P4 functional readiness because they are explicitly outside the current P4 skeleton or require later contract expansion.

| Item | Judgment | Owner |
|---|---|---|
| P4-R8 / RR-15: quality gate not attached to `analyze` | Deferred, non-blocking | `quality gate integration slice` |
| P4-R9: App-category FQ1 branch, FQ4, FQ5 not implemented | Deferred, non-blocking | `quality gate rules slice` |
| RR-16: correctness denominator is narrow | Deferred, non-blocking | `snapshot sub-field exposure slice` |
| `016492` duplicate selected-fund CSV row | Deferred, non-blocking | user/App source reconciliation |
| `share_change` multi-share-class selection | Deferred, non-blocking | future extractor hardening |
| completely failed snapshot funds absent from `fund_scores` | Deferred, non-blocking | snapshot failure accounting |

## Worktree Scope Hygiene

The current worktree contains P4 code/doc changes plus untracked runtime/report artifacts and older review/script artifacts. This reconciliation does not classify all untracked files as P4 deliverables.

Before `ready-to-open-draft-PR`, the controller must decide the PR inclusion set explicitly:

- Include P4 source, tests, README/control docs, and accepted P4 review artifacts.
- Exclude or separately justify runtime output directories such as `reports/`, local launch scripts, and unrelated historical review files.
- Treat `uv.lock` as a separate scope item: it contains `pytest-cov` / `coverage` lock changes matching the current `pyproject.toml` dev dependency, but it is not part of the P4 correctness/quality-gate implementation itself.

## Validation Status

Most recent accepted validation for the P4 correctness/quality-gate surface:

- correctness slice tests: `28 passed`
- `ruff check`: passed
- `ruff format --check`: passed
- `git diff --check`: passed
- real 004393 smoke: correctness `available`, one comparable `classified_fund_type.fund_type` record, value matches `active_fund`; quality gate remains blocked by existing coverage gaps, not FQ1.

## Gate Decision

Current gate can move from `P4 readiness reconciliation` to `P4 final aggregate deepreview`.

`P4 final aggregate deepreview` should ask at least two independent reviewers to inspect the full P4 accepted scope after correctness and field-contract changes, with specific attention to:

- P4 deferred items are tracked and not accidentally dropped.
- `score.json` / `quality_gate.json` schemas remain coherent after `fund_scores` and correctness.
- Service/UI layers remain thin and do not contain fund-domain rules.
- README/control docs match current code behavior.
- PR inclusion set is clear enough to proceed to draft PR prep after review.
