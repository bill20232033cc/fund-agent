# Controller Judgment - Strict Golden 2025 Answer Evidence Gate

Date: 2026-06-13

Gate: `Strict golden 2025 answer evidence gate`

Verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## Basis

- `AGENTS.md`: evidence must be traceable, same-source and must not use indirect
  or arbitrary residue proof.
- `docs/design.md`: strict golden identity is
  `fund_code + report_year + field_name + sub_field`; legacy missing
  `report_year` is only accepted as 2024 compatibility and cannot be reused
  across years.
- `docs/current-startup-packet.md`: current gate before closeout was
  `Strict golden 2025 answer evidence gate`; release/readiness remains
  `NOT_READY`.
- `docs/implementation-control.md`: current gate objective was to prove whether
  tracked strict golden answer coverage includes `004393 / 2025` and decide
  source-authority status without writing golden answers or fixture promotion
  state.
- Evidence artifact:
  `docs/reviews/mvp-strict-golden-2025-answer-evidence-20260613.md`.
- MiMo review:
  `docs/reviews/mvp-strict-golden-2025-answer-evidence-review-mimo-20260613.md`.
- DS review:
  `docs/reviews/mvp-strict-golden-2025-answer-evidence-review-ds-20260613.md`.

## Judgment

The evidence gate is accepted with amendments.

Accepted direct evidence:

- Under current `load_golden_answer_json()` loader/default semantics, tracked
  `reports/golden-answers/golden-answer.json` enumerates `004393,2024,21` and
  does not enumerate `004393,2025`.
- The raw strict golden JSON does not need explicit `report_year` for legacy
  2024 rows; the `2024` identity is loader/default semantics, not a raw-field
  assertion.
- Tracked `reports/golden-answers/` has no `004393.*2025`, `2025.*004393` or
  `年报2025` match.
- Historical tracked `004393 / 2025` artifacts classify the row as probe-only,
  not baseline/golden material.
- Current reviewed Markdown build path is legacy-2024; strict JSON loader can
  represent explicit years, but this gate did not accept any same-year reviewed
  2025 rows.

Controller amendment:

The original evidence draft over-routed directly to
`Markdown / Golden Answer Schema Build-tooling Planning Gate`. DS correctly
identified that the evidence only proves absence and lack of immediate write
authority. It does not prove that Markdown/schema/build-tooling must be the next
gate. The next gate must first decide same-year evidence intake and source
authority.

Release/readiness remains `NOT_READY`.

## Finding Disposition

| Finding | Source | Disposition | Rationale |
|---|---|---|---|
| `004393 / 2025` is absent from current strict golden answer runtime semantics | Evidence, MiMo, DS | ACCEPT | Enumeration output contains `004393,2024,21` only; no `004393,2025`. |
| Existing strict golden identities are 2024 under loader/default semantics | DS, MiMo | ACCEPT_WITH_WORDING_AMENDMENT | Raw JSON lacks explicit year fields for legacy rows; wording must avoid implying raw explicit 2024 fields. |
| Historical `004393 / 2025` artifacts are probe-only | Evidence, DS | ACCEPT | They support absence classification but do not supply same-year reviewed rows. |
| JSON-only authority is not accepted for immediate write | Evidence, MiMo, DS | ACCEPT | No accepted same-year reviewed `expected_value` / `source` rows were found or reviewed. |
| Future JSON-only authority is rejected absolutely | DS | REJECT | Future authority remains undecided; a later evidence/decision gate may accept or reject it. |
| Direct Markdown/schema/build-tooling planning as primary next entry | DS | REJECT_AS_OVERROUTED | Current evidence does not prove build-tooling is required before same-year evidence intake and authority decision. |
| pytest/ruff prove source authority | MiMo, DS | REJECT | They are parser/read-only sanity checks only. |
| Arbitrary untracked residue used as proof | DS | REJECT_FINDING | Evidence used tracked golden files, tracked historical artifacts and code; target artifact self-status is not proof. |

## Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Evidence gate | ACCEPTED_WITH_AMENDMENTS | Core absence evidence is accepted; next-entry wording was corrected. |
| Immediate strict golden 2025 answer implementation | REJECTED | Same-year reviewed evidence and source authority are not accepted. |
| Immediate fixture promotion implementation | REJECTED | Strict golden 2025 answer remains unresolved and fixture promotion parser remains year-blind. |
| Treat 2025 probe-only artifacts as golden rows | REJECTED | Historical artifacts explicitly keep `004393 / 2025` probe-only. |
| Treat 2024 golden rows as 2025 correctness evidence | REJECTED | Design truth forbids cross-year reuse. |
| Markdown/schema/build-tooling planning | DEFERRED_CONDITIONAL | Open only if the next decision gate rejects JSON-only authority or requires reviewed Markdown as reproducible upstream. |

## Residuals

| Residual | Owner | Current blocker? | Destination |
|---|---|---:|---|
| Same-year `004393 / 2025` reviewed evidence rows are absent | Golden answer / evidence owner | Yes | `004393 / 2025 same-year evidence intake + source-authority decision gate` |
| Future 2025 golden answer source authority is undecided | Golden answer / controller owner | Yes | `004393 / 2025 same-year evidence intake + source-authority decision gate` |
| Reviewed Markdown build path is legacy-2024 | Golden answer tooling owner | Conditional | Markdown/schema/build-tooling planning gate if required by next decision |
| Fixture promotion state remains unresolved and year-blind | Fund golden/readiness owner | Yes for promotion | Future fixture promotion evidence or schema/parser planning gate |
| Release/readiness remains `NOT_READY` | Release owner | Yes | Future release-readiness rollup gate |

## Next Entry

Primary next entry:

```text
004393 / 2025 same-year evidence intake + source-authority decision gate
```

Deferred entries:

- Markdown / Golden Answer Schema Build-tooling Planning Gate
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
