# 004393 / 2025 Same-year Evidence Intake + Source-authority Decision Gate

Date: 2026-06-13

Gate: `004393 / 2025 same-year evidence intake + source-authority decision gate`

Verdict: `DECISION_FOR_REVIEW_NOT_READY`

## 1. Scope

This is a no-live evidence and decision gate.

It does not modify source, tests, runtime behavior, golden answer JSON, reviewed
Markdown, fixture promotion state, release/readiness state, PR state or cleanup
state. It does not run live EID, network, PDF, FDR, provider, LLM, analyze,
checklist, golden-build, readiness, release, PR, push or merge commands.

The gate answers:

1. whether accepted same-year `004393 / 2025` strict golden rows currently
   exist; and
2. what source-authority route must govern any future 2025 strict golden answer
   write.

## 2. Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`
- `fund_agent/fund/golden_answer.py`
- `reports/golden-answers/golden-answer.json`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `docs/reviews/mvp-strict-golden-2025-answer-evidence-controller-judgment-20260613.md`
- tracked historical `004393 / 2025` probe-only artifacts:
  - `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
  - `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`
  - `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md`

## 3. Fact Separation

### Repo Facts

- `build_golden_answer_json()` reads reviewed Markdown and writes strict JSON.
- `parse_golden_answer_markdown()` assigns Markdown rows to
  `LEGACY_GOLDEN_ANSWER_REPORT_YEAR=2024`.
- The current Markdown table has five columns:
  `field`, `sub_field`, `expected_value`, `confidence`, `source`.
- Current reviewed Markdown does not have an explicit `report_year` column,
  heading syntax or metadata block.
- The strict JSON loader can read explicit `report_year` at fund and record
  level, requires fund/record year equality, and deduplicates by
  `(fund_code, report_year, field_name, sub_field)`.
- `reports/golden-answers/golden-answer.json` and
  `reports/golden-answers/golden-answer-prefill-reviewed.md` are tracked files.

### Truth-doc Facts

- `docs/design.md` defines the Golden Answer pipeline as:
  `GoldenPrefillService` -> manual review -> `GoldenAnswerService` -> correctness
  comparison.
- `docs/design.md` defines strict golden identity as
  `fund_code + report_year + field_name + sub_field`.
- `docs/design.md` says old JSON missing `report_year` only means accepted 2024
  compatibility and cannot be reused across years.
- `docs/golden-answer-instructions.md` and `docs/golden-answer-template.md` are
  2024-oriented and describe 2024 annual-report PDF source rows.

### Accepted Artifact Facts

- The accepted strict-golden 2025 answer evidence gate found no `004393 / 2025`
  identity in current loader/default semantics.

### Accepted Residuals

- `004393 / 2025` remains absent from strict golden answer coverage.
- Historical `004393 / 2025` product smoke / annual-period evidence proves
  bounded product-path availability only. It is not same-year reviewed golden
  material.
- Fixture promotion remains unresolved and current fixture promotion parser is
  year-blind.
- Release/readiness remains `NOT_READY`.

## 4. Same-year Evidence Intake Result

No accepted same-year `004393 / 2025` strict golden rows are available in the
current tracked evidence chain.

The tracked historical `004393 / 2025` row is explicitly probe-only:

```text
release-maintenance-small-baseline-corpus-v1-plan-20260527.md:
`004393` / 2025 as a probe-only report-year availability row.
```

```text
release-maintenance-small-baseline-corpus-v1-run-20260527.md:
Keep probe-only. Next action: separate 2025 repository identity + fact-review
gate if 2025 is desired. No; report-year coverage missing and probe-only.
```

```text
release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md:
`004393` / 2025 remains probe-only, not baseline or golden material.
```

Decision:

- Historical probe-only artifacts are `review input`, not golden truth.
- Existing product-path live evidence for `004393 / 2021-2025` remains product
  availability/provenance evidence only, not strict golden `expected_value`
  evidence.
- No current artifact can be promoted into 2025 strict golden rows without a
  separate reviewed evidence intake gate.

## 5. Future Same-year Evidence Requirements

Any future `004393 / 2025` strict golden answer row must include:

| Required item | Requirement |
|---|---|
| fund identity | `fund_code=004393` and `report_year=2025` |
| row identity | `field_name` and `sub_field` from the current snapshot/golden comparable contract |
| expected value | exact value intended for correctness comparison |
| confidence | `high`, `medium` or `low` |
| source | same-year, reviewable source string; must not be `manual_required`, blank, `—`, or a 2024 source |
| evidence owner | reviewer/controller artifact that accepted the row |
| lineage | direct same-year source evidence, not historical probe-only status |

Disallowed as row source:

- 2024 golden rows;
- historical `004393 / 2025` probe-only smoke output;
- arbitrary untracked report residue;
- product narrative output without row-level `expected_value` / `source`
  review;
- fixture promotion state;
- quality gate `year_not_covered` info by itself.

## 6. Source-authority Decision

Decision: `REVIEWED_MARKDOWN_BUILD_PIPELINE_REQUIRED_FOR_TRACKED_GOLDEN_WRITES`

Rationale:

- The design truth names a reproducible pipeline:
  prefill -> manual review -> Markdown-to-JSON service -> correctness.
- The current CLI/service surface contains `golden-build`, and
  `build_golden_answer_json()` writes strict JSON from reviewed Markdown.
- JSON-only writes would bypass the current human-review source artifact and can
  create divergence between `golden-answer-prefill-reviewed.md` and
  `golden-answer.json`.
- Existing strict JSON loader support for explicit `report_year` is a read/load
  capability. It is not, by itself, authority to hand-edit tracked JSON for 2025
  rows.

Therefore:

- JSON-only authority is rejected for tracked golden answer writes in this route.
- A future JSON-only route would require a separate design/controller exception
  gate with explicit residuals; it is not the default.
- Before writing `004393 / 2025` rows, the project must plan how reviewed
  Markdown expresses `report_year` and how `golden-build` reproduces the strict
  JSON.

## 7. Finding Disposition

| Finding | Disposition | Rationale |
|---|---|---|
| Accepted same-year `004393 / 2025` rows currently exist | REJECTED | Current tracked evidence has no accepted same-year `expected_value` / `source` rows. |
| Historical `004393 / 2025` product smoke can seed golden rows | REJECTED | Historical artifacts explicitly mark it probe-only and not golden material. |
| 2024 golden rows can be reused for 2025 correctness | REJECTED | Design truth forbids cross-year reuse. |
| JSON-only authority can directly govern tracked 2025 golden writes | REJECTED | It bypasses the accepted reviewed Markdown -> build JSON pipeline. |
| Current strict JSON loader can represent explicit 2025 identities | ACCEPTED_AS_CODE_CAPABILITY | Loader support exists, but it is not write authority. |
| Reviewed Markdown needs year-bearing schema/build-tooling before 2025 rows | ACCEPTED | Current Markdown parser assigns all Markdown rows to legacy 2024. |
| Immediate strict golden 2025 implementation gate | REJECTED | Same-year reviewed evidence rows and year-bearing build path are absent. |

## 8. Next Entry Recommendation

Primary next entry:

```text
Markdown / Golden Answer Schema Build-tooling Planning Gate
```

Purpose of next gate:

- Plan the minimal year-bearing reviewed Markdown schema.
- Decide whether year appears in the fund heading, a metadata block or a table
  column.
- Preserve legacy 2024 compatibility.
- Define tests for same fund across 2024 and 2025.
- Keep golden answer content edits out of scope.

Deferred entries:

- `004393 / 2025 same-year reviewed evidence intake gate`
- strict golden 2025 answer implementation gate
- fixture promotion state evidence gate
- fixture promotion state schema/parser planning gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate
- PR/release external-state gate

## 9. Validation

This decision artifact is intended to be limited to `docs/reviews/` controller
evidence. Controller closeout must still verify the actual working tree and
intended write set with:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

No source/test/runtime validation is required for this decision artifact because
this gate does not authorize source, test, runtime, golden answer or fixture
promotion changes.
