# Controller Judgment - Markdown / Golden Answer Schema Build-tooling Plan

Date: 2026-06-13

Gate: `Markdown / Golden Answer Schema Build-tooling Planning Gate`

Verdict: `ACCEPT_WITH_NONBLOCKING_RESIDUALS_NOT_READY`

## 1. Controller Scope Check

This was a planning-only gate. It did not authorize source, tests, runtime
behavior, golden answer content, tracked golden answer JSON, reviewed golden
answer Markdown, fixture promotion state, release/readiness state, PR state or
cleanup changes. It did not run live EID, network, PDF, FDR, provider, LLM,
analyze, checklist, golden-build, readiness, release, PR, push or merge
commands.

Controller work in this gate was limited to:

- reading current control/design/golden-answer facts;
- obtaining a planning-worker plan;
- writing the plan artifact;
- collecting MiMo-style and DS-style plan reviews; and
- writing this controller judgment.

Release/readiness remains `NOT_READY`.

## 2. Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Execution and boundary truth |
| `docs/design.md` | Golden Answer identity and pipeline design truth |
| `docs/current-startup-packet.md` | Current gate/control snapshot |
| `docs/implementation-control.md` | Control truth and gate objective |
| `docs/golden-answer-instructions.md` | Current operator workflow |
| `docs/golden-answer-template.md` | Current reviewed Markdown template |
| `fund_agent/fund/golden_answer.py` | Current parser/build/loader facts |
| `tests/fund/test_golden_answer.py` | Current parser/loader test coverage |
| `tests/fund/test_golden_readiness_preflight.py` | Current year-aware preflight coverage |
| `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-controller-judgment-20260613.md` | Accepted source-authority input |
| `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-plan-20260613.md` | Plan artifact |
| `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-plan-review-mimo-20260613.md` | MiMo review |
| `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-plan-review-ds-20260613.md` | DS review |

## 3. Accepted Plan Decisions

| Decision | Disposition | Basis |
|---|---|---|
| Use a fund-level fenced `golden-answer-metadata` block directly below each fund heading | ACCEPT | `report_year` is a fund-block-level identity property; this keeps the current heading parser and five-column row table stable while adding structured metadata. |
| Missing metadata means legacy 2024 | ACCEPT | Current reviewed Markdown is legacy 2024; preserving this default avoids tracked content churn and matches existing JSON loader compatibility. |
| Keep strict JSON payload shape unchanged | ACCEPT | Strict JSON already supports fund-level and record-level `report_year`; no schema-version bump is needed for this implementation slice unless implementation discovers a new incompatibility. |
| Reject heading-encoded year as default | ACCEPT | It mixes display title and identity metadata, expands heading regex churn and is less explicit than a metadata block. |
| Reject row-level `report_year` table column as default | ACCEPT | It duplicates a fund-level fact across rows and would change the stable five-column table contract. |
| Reject source-text year inference | ACCEPT | Human evidence text is not machine identity; inferring from `年报2025` would couple source prose to correctness keys. |
| Do not edit tracked golden answer content in implementation gate | ACCEPT | The accepted source-authority decision requires build-tooling before content write; this plan is not a content gate. |
| Route next to implementation gate | ACCEPT | The plan is code-generation-ready after review; next work is parser/build-tooling implementation, not 2025 content entry. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| MiMo-style review | `ACCEPT_WITH_NONBLOCKING_RESIDUALS_NOT_READY` | ACCEPTED. The only material residual is clarification of preflight integration optionality. |
| DS-style review | `ACCEPT_WITH_RESIDUALS_NOT_READY` | ACCEPTED. No blocker or required rewrite. |

Controller amendment:

- Future implementation must preserve existing preflight year coverage.
- A build-from-metadata preflight integration test is required only if
  parser/build tests alone do not prove that metadata-built strict JSON works
  with the year-aware preflight path.
- If the same `fund_code/report_year` appears in multiple Markdown heading
  blocks, implementation must either fail fast or document and test the allowed
  behavior. Silent ambiguous merging is not accepted.

## 5. Accepted Implementation Handoff

Primary next entry:

```text
Markdown / Golden Answer Schema Build-tooling Implementation Gate
```

Allowed implementation write set:

- `fund_agent/fund/golden_answer.py`
- `tests/fund/test_golden_answer.py`
- `tests/fund/test_golden_readiness_preflight.py` only if needed
- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`
- `fund_agent/fund/README.md`
- `tests/README.md` only if test workflow description changes
- root `README.md` only if user-facing `golden-build` workflow examples need
  the metadata schema
- `docs/design.md` only after implementation/tests pass, to record current
  implemented fact
- implementation/review/controller artifacts under `docs/reviews/`
- controller closeout sync in `docs/current-startup-packet.md` and
  `docs/implementation-control.md`

Implementation requirements:

- Support fenced block language `golden-answer-metadata`.
- Support minimal key-value syntax `report_year: <int>`.
- Resolve report year per fund block.
- Default missing metadata to `LEGACY_GOLDEN_ANSWER_REPORT_YEAR`.
- Emit resolved report year into fund-level and record-level strict JSON.
- Validate duplicate, malformed, unknown-key, late or unclosed metadata.
- Validate duplicate Markdown build identities by
  `(fund_code, report_year, field_name, sub_field)` across the whole Markdown
  document.
- Preserve existing strict JSON loader behavior.
- Use temporary paths for any build smoke tests; do not run `golden-build`
  against tracked outputs.

Validation commands for implementation gate:

```bash
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
```

```bash
uv run ruff check fund_agent/fund/golden_answer.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
```

```bash
git diff --check
```

## 6. Stop Conditions For Next Gate

Stop and return to controller if:

- implementation requires editing tracked `reports/golden-answers/*.md` or
  `reports/golden-answers/*.json`;
- implementation requires adding `004393 / 2025` expected values or sources;
- fixture promotion state or schema becomes necessary;
- the schema choice becomes ambiguous again;
- implementation requires a CLI-level `--report-year` option for
  `golden-build`;
- validation requires live EID, network, PDF, FDR, provider, LLM, analyze,
  checklist, readiness, release or PR commands;
- any path tries to reuse 2024 golden rows as 2025 correctness evidence.

## 7. Deferred Entries

- `004393 / 2025 same-year reviewed evidence/content planning gate`
- `004393 / 2025 same-year reviewed evidence/content intake gate`
- strict golden 2025 answer content implementation gate
- fixture promotion state evidence gate
- fixture promotion state schema/parser planning gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate
- PR/release external-state gate

## 8. Validation

Controller closeout for this planning gate requires:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

No source/test/runtime validation is required for this planning gate because no
source, test, runtime, golden content or fixture promotion file is authorized
for change.
