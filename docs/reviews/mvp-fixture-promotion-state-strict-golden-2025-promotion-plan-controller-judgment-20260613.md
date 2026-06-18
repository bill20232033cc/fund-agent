# Controller Judgment - Fixture Promotion State / Strict Golden 2025 Promotion Planning Gate

Date: 2026-06-13

Gate: `Fixture promotion state / strict golden 2025 promotion planning gate`

Verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## Basis

- `AGENTS.md`: evidence must be traceable and same-source; production document
  access/source expansion/live/release work must not be implied by planning.
- `docs/design.md`: strict golden answer identity is
  `fund_code + report_year + field_name + sub_field`; legacy missing
  `report_year` is only the accepted 2024 compatibility path.
- `docs/current-startup-packet.md`: current active gate is this planning gate;
  fixture promotion and strict golden 2025 accepted answer promotion remain
  unresolved; release/readiness remains `NOT_READY`.
- `docs/implementation-control.md`: this gate is standard planning-only and
  must not edit golden answers, fixture promotion state, source/test/runtime
  behavior or readiness/release state.
- Plan:
  `docs/reviews/mvp-fixture-promotion-state-strict-golden-2025-promotion-plan-20260613.md`.
- MiMo review:
  `docs/reviews/mvp-fixture-promotion-state-strict-golden-2025-promotion-plan-review-mimo-20260613.md`.
- DS review:
  `docs/reviews/mvp-fixture-promotion-state-strict-golden-2025-promotion-plan-review-ds-20260613.md`.

## Judgment

The amended plan is accepted.

The original draft had two material blockers:

- it did not decide the 2025 strict golden answer source of authority problem:
  JSON-only accepted evidence vs reviewed Markdown/schema/build-tooling;
- it did not harden the fixture promotion identity problem: current preflight
  promotion state is fund-code-only and cannot safely express `004393 / 2025`
  promotion.

Both blockers were accepted and amended in the plan. The amended plan now:

- keeps the next step evidence-first;
- requires the 2025 strict golden evidence gate to answer the authority question
  before any write gate;
- forbids treating current fund-code-only `promoted_fixture` as 2025-specific
  promotion;
- splits fixture promotion follow-up into no-parser-change and schema/parser
  planning paths;
- preserves `NOT_READY`.

## Finding Disposition

| Finding | Source | Disposition | Rationale |
|---|---|---|---|
| Primary next entry should be `Strict golden 2025 answer evidence gate` | Plan, MiMo, DS | ACCEPT | Same-year strict golden answer identity must be established or rejected before fixture promotion state can be meaningful. |
| 2025 strict golden answer authority is unresolved | MiMo | ACCEPT_AS_BLOCKER_AMENDED | Current reviewed Markdown build path is legacy-2024 unless a separate schema/build-tooling route is accepted; the amended plan makes this a required evidence question. |
| Current fixture promotion parser is fund-code-only and year-blind | DS | ACCEPT_AS_BLOCKER_AMENDED | A fund-code-only `promoted_fixture` would not mean `004393 / 2025` only; the amended plan forbids that route. |
| Future fixture promotion write set was too broad | DS | ACCEPT_AS_BLOCKER_AMENDED | The amended plan separates no-parser-change manifest work from a future schema/parser planning gate. |
| Exact read-only identity enumeration should be allowed for the next evidence gate | MiMo, DS | ACCEPT_AS_AMENDMENT | The amended plan adds a concrete `uv run python -c ...` read-only command and output requirement. |
| Historical fixture promotion manifest is not runtime promotion approval | Plan, DS | ACCEPT | The plan preserves the 2025-05-29 manifest as control-plane state only. |

## Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Amended planning gate | ACCEPTED | Review blockers were incorporated and no planning boundary violation remains. |
| Direct strict golden answer write now | REJECTED | This gate is planning-only, and 2025 source authority must first be decided. |
| Direct fixture promotion state write now | REJECTED | This gate is planning-only, and current promotion identity is year-blind. |
| Use `promoted_fixture` for `004393` under current parser as 2025-specific approval | REJECTED | Current parser maps by fund code only. |
| Treat historical 2025-05-29 fixture manifest as promotion approval | REJECTED | Accepted judgment says it is control-plane-only and not a promotion manifest. |
| Release/readiness claim | REJECTED | Release/readiness remains `NOT_READY`. |
| Markdown/schema/build-tooling route | DEFERRED | Open only if the next evidence gate rejects JSON-only 2025 authority. |
| Fixture promotion schema/parser route | DEFERRED | Open only if 2025-specific promotion must be represented. |

## Residuals

| Residual | Owner | Current blocker? | Destination |
|---|---|---:|---|
| `004393 / 2025` strict golden answer coverage is not accepted | Golden answer owner | Yes | `Strict golden 2025 answer evidence gate` |
| 2025 strict golden answer authority is undecided | Golden answer / controller owner | Yes | `Strict golden 2025 answer evidence gate` |
| Current fixture promotion parser is year-blind | Fund golden/readiness owner | Yes for any 2025-specific promotion | Future fixture promotion evidence or schema/parser planning gate |
| Fixture promotion state remains unresolved | Release/readiness owner | Yes | Future fixture promotion state gate after strict golden 2025 answer evidence |
| Release/readiness remains `NOT_READY` | Release owner | Yes | Future release-readiness rollup gate |

## Next Entry

Primary next entry:

```text
Strict golden 2025 answer evidence gate
```

Deferred entries:

- Markdown / golden answer schema build-tooling planning gate
- strict golden 2025 answer implementation gate
- fixture promotion state evidence gate
- fixture promotion state schema/parser planning gate
- fixture promotion state implementation gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate
- PR/release external-state gate

No live, PR, merge, mark-ready, release external-state action, golden answer
edit, fixture promotion state edit, source/test/runtime behavior change or
cleanup is authorized by this judgment.
