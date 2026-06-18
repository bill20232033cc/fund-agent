# Controller Judgment - 004393 / 2025 Same-year Evidence Intake + Source-authority Decision

Date: 2026-06-13

Gate: `004393 / 2025 same-year evidence intake + source-authority decision gate`

Verdict: `ACCEPT_WITH_REQUIRED_REWRITES_NOT_READY`

## 1. Controller Scope Check

This was a no-live evidence and decision gate. It did not authorize source,
test, runtime behavior, golden answer JSON, reviewed Markdown, fixture
promotion state, release/readiness state, PR state or cleanup changes. It did
not authorize live EID, network, PDF, FDR, provider, LLM, analyze, checklist,
golden-build, readiness, release, PR, push or merge commands.

Controller work in this gate was limited to:

- writing the same-year evidence/source-authority decision artifact;
- collecting MiMo-style and DS-style reviews;
- applying review-required rewrites to the decision artifact;
- writing this controller judgment; and
- syncing current control docs if accepted.

Release/readiness remains `NOT_READY`.

## 2. Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Execution and source-truth boundary |
| `docs/design.md` | Design truth for Golden Answer identity and pipeline |
| `docs/current-startup-packet.md` | Current gate/control snapshot |
| `docs/implementation-control.md` | Control truth and gate objective |
| `docs/golden-answer-instructions.md` | Current reviewed-row instructions |
| `docs/golden-answer-template.md` | Current reviewed-row template |
| `fund_agent/fund/golden_answer.py` | Current Markdown parser / strict JSON loader facts |
| `reports/golden-answers/golden-answer.json` | Current tracked strict golden payload |
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Current tracked reviewed Markdown source |
| `docs/reviews/mvp-strict-golden-2025-answer-evidence-controller-judgment-20260613.md` | Accepted prior evidence input |
| `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md` | Historical probe-only input |
| `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md` | Historical probe-only input |
| `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md` | Historical probe-only input |
| `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-20260613.md` | Decision artifact |
| `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-review-mimo-20260613.md` | MiMo review |
| `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-review-ds-20260613.md` | DS review |

## 3. Accepted Findings

| Finding | Disposition | Basis |
|---|---|---|
| Accepted same-year `004393 / 2025` strict golden rows currently exist | REJECTED | Current tracked JSON/Markdown evidence and accepted prior controller judgment do not include `004393 / 2025`; historical 2025 artifacts are probe-only. |
| Historical `004393 / 2025` product smoke can seed strict golden rows | REJECTED | The 20260527 plan/run/controller artifacts explicitly classify it as probe-only / not golden material. |
| 2024 golden rows can be reused for 2025 correctness | REJECTED | `docs/design.md` defines strict golden identity as `fund_code + report_year + field_name + sub_field` and forbids cross-year reuse. |
| JSON-only authority can directly govern tracked 2025 golden writes by default | REJECTED | Design truth defines reviewed Markdown -> strict JSON -> correctness; current build code writes JSON from reviewed Markdown. JSON loader year support is not write authority. |
| Strict JSON loader can represent explicit 2025 identities | ACCEPTED_AS_CODE_CAPABILITY | `golden_answer.py` can read explicit `report_year` and validates fund/record year equality. |
| Reviewed Markdown needs year-bearing schema/build-tooling before 2025 rows | ACCEPTED | Current Markdown parser assigns reviewed Markdown rows to legacy 2024 and current reviewed Markdown has no report-year-bearing schema. |
| Immediate strict golden 2025 implementation gate | REJECTED | Same-year reviewed rows and year-bearing reviewed Markdown/build path are both absent. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| MiMo-style review | `ACCEPT_WITH_NONBLOCKING_AMENDMENT_NOT_READY` | ACCEPTED. Validation wording was rewritten to state intended write set and controller closeout verification instead of whole-worktree fact. |
| DS-style review | `ACCEPT_WITH_REQUIRED_REWRITE_NOT_READY` | ACCEPTED. The prior strict-golden evidence conclusion was moved from `Repo Facts` to `Accepted Artifact Facts`. |

No blocking finding remains after the rewrites.

## 5. Controller Judgment

The decision artifact is accepted as the current controller judgment for this
gate.

Accepted current facts:

- Current tracked strict golden evidence does not contain accepted same-year
  `004393 / 2025` rows.
- Historical `004393 / 2025` product-path evidence remains probe-only and
  cannot be promoted into strict golden truth.
- The default authority for future tracked golden answer writes is the reviewed
  Markdown -> build strict JSON pipeline.
- JSON-only write authority is not accepted as the default route for tracked
  2025 golden answer rows.
- Future `004393 / 2025` strict golden content work must first plan a
  year-bearing reviewed Markdown schema/build path or pass a separate explicit
  design/controller exception gate.

Residuals:

- Same-year `004393 / 2025` reviewed `expected_value` / `source` rows remain
  absent.
- Golden answer content edits remain unauthorized.
- Fixture promotion remains year-blind and unresolved.
- Release/readiness remains `NOT_READY`.

## 6. Next Entry

Primary next entry:

```text
Markdown / Golden Answer Schema Build-tooling Planning Gate
```

Purpose:

- plan the minimal reviewed Markdown schema for report-year-bearing golden
  answer rows;
- decide whether report year belongs in heading syntax, a metadata block or a
  table column;
- preserve legacy 2024 compatibility;
- define tests for same fund across 2024 and 2025; and
- keep golden answer content edits out of scope.

Deferred entries:

- `004393 / 2025 same-year reviewed evidence intake gate`
- strict golden 2025 answer implementation gate
- fixture promotion state evidence gate
- fixture promotion state schema/parser planning gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate
- PR/release external-state gate

## 7. Validation

Controller closeout requires:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

No source/test/runtime validation is required for this decision gate because no
source, test, runtime, golden answer or fixture promotion file is authorized for
change.
