# Markdown / Golden Answer Schema Build-tooling Plan

Date: 2026-06-13

Gate: `Markdown / Golden Answer Schema Build-tooling Planning Gate`

Verdict: `PLAN_FOR_REVIEW_NOT_READY`

## 1. Scope

This is a planning-only gate.

It does not modify source, tests, runtime behavior, golden answer content,
tracked golden answer JSON, reviewed golden answer Markdown, fixture promotion
state, release/readiness state, PR state or cleanup state. It does not run live
EID, network, PDF, FDR, provider, LLM, analyze, checklist, golden-build,
readiness, release, PR, push or merge commands.

Goal:

- Plan a year-bearing reviewed Markdown schema so `golden-build` can generate
  strict JSON with explicit `report_year`.
- Preserve strict correctness identity as
  `fund_code + report_year + field_name + sub_field`.
- Preserve existing legacy 2024 reviewed Markdown compatibility.

Non-goals:

- Do not write `004393 / 2025` expected values, sources or reviewed rows.
- Do not edit `reports/golden-answers/golden-answer-prefill-reviewed.md`.
- Do not edit `reports/golden-answers/golden-answer.json`.
- Do not change extractor, score, quality gate, runtime, FDR, PDF, provider,
  LLM, analyze or checklist behavior.
- Do not change fixture promotion state or schema.
- Do not claim release/readiness.
- Do not use arbitrary untracked residue as proof.

## 2. Current Facts

### Repo Facts

- `parse_golden_answer_markdown()` currently parses fund sections from headings
  matching `## <fund_code> <title>`.
- Current reviewed Markdown rows are five-column rows:
  `field | sub_field | expected_value | confidence | source`.
- Markdown parsing assigns all reviewed Markdown rows to
  `LEGACY_GOLDEN_ANSWER_REPORT_YEAR = 2024`.
- `_append_current_fund()` currently stores the same legacy 2024 report year at
  fund level.
- `build_golden_answer_json()` writes strict JSON from reviewed Markdown.
- `load_golden_answer_json()` already accepts explicit `report_year` at fund and
  record level.
- The strict JSON loader validates record `report_year` equals fund
  `report_year`.
- The strict JSON loader deduplicates by
  `(fund_code, report_year, field_name, sub_field)`.
- Existing tests already prove legacy JSON without `report_year` defaults to
  2024 and same fund code can coexist across different report years in strict
  JSON.

### Truth-doc Facts

- `docs/design.md` defines Golden Answer as:
  `GoldenPrefillService` -> manual review -> `GoldenAnswerService` ->
  correctness comparison.
- `docs/design.md` defines the correctness oracle identity key as
  `fund_code + report_year + field_name + sub_field`.
- `docs/design.md` says old JSON missing `report_year` only means current 2024
  corpus compatibility and does not allow cross-year reuse.

### Accepted Artifact Facts

- `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-controller-judgment-20260613.md`
  rejects JSON-only authority as the default tracked golden answer write route.
- The same controller judgment requires a year-bearing reviewed Markdown /
  golden-build path before future `004393 / 2025` strict golden rows.

## 3. Recommended Schema

Decision:

```text
Use a fund-level fenced metadata block directly below each fund heading.
```

Recommended format:

````markdown
## 004393 安信企业价值优选混合A（国内股票类）

```golden-answer-metadata
report_year: 2025
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_code | 004393 | high | 年报2025 §2 page-5 |
````

Rules:

- `report_year` is fund-block metadata, not row-level metadata.
- The metadata block must appear after the fund heading and before the first
  data table row.
- A fund block may contain at most one `golden-answer-metadata` block.
- `report_year` must parse as an integer.
- Missing metadata preserves legacy 2024 behavior.
- The `source` text remains human-review evidence text. It must not be used to
  infer machine identity.

## 4. Rejected Schema Options

| Option | Disposition | Rationale |
|---|---|---|
| Add year to heading, such as `## 004393 / 2025 ...` | REJECT | Heading currently owns fund-code parsing and human title display. Mixing year into it creates regex/title churn and couples identity metadata to display text. |
| Add `report_year` table column | REJECT | Report year is fund-block-level truth. A row-level column duplicates the same fact across rows, increases manual-edit noise, changes the table contract from 5 to 6 columns and creates avoidable row-level mismatch states. |
| Infer year from `source`, such as `年报2025` | REJECT | Source is review evidence text, not machine identity. Inferring identity from source would mix provenance description with correctness key semantics. |
| JSON-only content write | REJECT | Prior accepted source-authority decision rejects JSON-only as default tracked write authority. |

## 5. Backward Compatibility

- Existing reviewed Markdown without metadata continues to parse as 2024.
- Existing tracked reviewed Markdown and strict JSON do not need content edits in
  the build-tooling implementation gate.
- Legacy strict JSON without `report_year` continues to load as 2024.
- New metadata only affects the fund block where it appears.
- Same `fund_code` may appear in separate 2024 and 2025 Markdown blocks only if
  their resolved identity keys differ by `report_year`.
- Duplicate same-year `fund_code + field + sub_field` must fail before strict
  JSON output is accepted.

## 6. Implementation Slices

### Slice A - Fund Parser / Build Tooling

Target:

- `fund_agent/fund/golden_answer.py`

Implementation decisions:

- Add parser support for fenced block language `golden-answer-metadata`.
- Parse only a minimal key-value syntax:
  - supported key: `report_year`
  - syntax: `report_year: 2025`
- Track `current_report_year` per fund block.
- Default `current_report_year` to `LEGACY_GOLDEN_ANSWER_REPORT_YEAR` when no
  metadata is present.
- Pass the resolved report year into `_append_current_fund()`.
- Build each `GoldenAnswerRecord.report_year` from the resolved fund-block
  report year.
- Keep strict JSON payload shape unchanged: fund-level and record-level
  `report_year`.
- Reject duplicate metadata blocks in the same fund block.
- Reject malformed metadata block content, non-integer `report_year`, unknown
  metadata keys and unclosed metadata fences.
- Reject metadata appearing after table data rows in the same fund block.
- Add Markdown-build duplicate detection across the full document using
  `(fund_code, report_year, field_name, sub_field)`, not only within the current
  heading block.

Non-targets:

- No expected changes to `fund_agent/services/golden_answer_service.py`.
- No expected changes to `fund_agent/ui/cli.py`.
- No `--report-year` CLI option; report year belongs in reviewed Markdown.
- No edits to tracked `reports/golden-answers/*.md` or
  `reports/golden-answers/*.json`.

### Slice B - Fund Tests

Targets:

- `tests/fund/test_golden_answer.py`
- `tests/fund/test_golden_readiness_preflight.py` only if needed for integration
  proof

Required tests:

- Explicit metadata Markdown emits fund-level and record-level
  `report_year=2025`.
- Legacy Markdown without metadata still emits `report_year=2024`.
- Same fund code can appear as legacy 2024 and explicit 2025 with the same
  `field/sub_field` because the identity differs by year.
- Same fund/year/field/sub_field duplicated across Markdown blocks fails.
- Duplicate metadata block fails.
- Malformed `report_year` fails.
- Unknown metadata key fails.
- Metadata after table data row fails.
- Existing strict JSON mismatch test remains or is added: record `report_year`
  not equal to fund `report_year` fails.
- Optional preflight integration: strict JSON built from metadata Markdown covers
  a 2025 snapshot, while 2024-only strict golden remains
  `year_not_covered` for 2025.

### Slice C - Operator Schema Docs

Targets:

- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`

Implementation decisions:

- Document the `golden-answer-metadata` block and `report_year` rule.
- Explain that missing metadata means legacy 2024 only for existing reviewed
  corpus.
- Show metadata under each fund heading in the template.
- Remove or rewrite 2024-only operator wording where it would conflict with
  year-aware reviewed rows.
- Do not fill any golden answer content.
- Do not change annual-report source acquisition policy in this docs slice.

### Slice D - Current-fact Docs Sync

Targets:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md` if the test workflow description changes
- root `README.md` only if current user-facing `golden-build` workflow needs
  the metadata example

Timing:

- Update `docs/design.md` only after implementation and tests pass, so the
  schema is documented as current implemented fact rather than future design.
- Update Fund README because `fund_agent/fund/golden_answer.py` behavior changes.
- Controller owns `docs/current-startup-packet.md` and
  `docs/implementation-control.md` closeout sync after review acceptance.

## 7. Validation Matrix

Implementation gate should run:

```bash
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
```

```bash
uv run ruff check fund_agent/fund/golden_answer.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
```

If docs are updated, implementation closeout should also run:

```bash
git diff --check
```

Validation assertions:

| Area | Required result |
|---|---|
| Legacy Markdown | Missing metadata still emits 2024. |
| Explicit metadata | `report_year: 2025` emits 2025 at fund and record level. |
| Same fund across years | Same fund and same field/sub-field can coexist when years differ. |
| Duplicate identity | Same fund/year/field/sub-field fails. |
| Metadata validation | Duplicate, malformed, unknown-key, late or unclosed metadata fails. |
| Strict JSON year mismatch | Record/fund `report_year` mismatch fails. |
| Preflight coverage | Matching year is covered; other-year golden remains `year_not_covered`. |

No validation should run `golden-build` against tracked
`reports/golden-answers/golden-answer.json` in this planning gate. If the
implementation gate needs build smoke coverage, it must use temporary input and
output paths only.

## 8. Stop Conditions

Stop and return to controller if:

- implementation requires editing tracked golden answer content files under
  `reports/golden-answers/`;
- the implementation needs to add actual `004393 / 2025` expected values or
  sources;
- fixture promotion state or schema becomes necessary;
- the chosen schema becomes ambiguous between heading, metadata and table-column
  options;
- the implementation needs a `golden-build --report-year` or CLI-level report
  year option;
- tests require live EID, network, PDF, FDR, provider, LLM, analyze, checklist,
  readiness, release or PR commands;
- any route tries to reuse 2024 golden rows for 2025 correctness.

## 9. Next Gate Recommendation

Primary next entry:

```text
Markdown / Golden Answer Schema Build-tooling Implementation Gate
```

Allowed write set for the next gate:

- `fund_agent/fund/golden_answer.py`
- `tests/fund/test_golden_answer.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`
- `fund_agent/fund/README.md`
- `tests/README.md` if needed
- root `README.md` if needed
- `docs/design.md` after implementation/tests pass
- implementation/review/controller artifacts under `docs/reviews/`
- controller closeout sync in `docs/current-startup-packet.md` and
  `docs/implementation-control.md`

Explicitly disallowed in the next gate:

- tracked golden answer content edits under `reports/golden-answers/`;
- fixture promotion edits;
- live/provider/LLM/analyze/checklist/readiness/release/PR commands;
- cleanup/delete/archive/stage/commit/push/merge.

After implementation acceptance, route to a separate no-live same-year reviewed
evidence/content planning or intake gate for `004393 / 2025`. Do not proceed
directly from this planning gate into golden content write.
