# Strict Golden 2025 Answer Evidence Gate Evidence

Date: 2026-06-13

Gate: `Strict golden 2025 answer evidence gate`

Verdict: `EVIDENCE_FOR_REVIEW_NOT_READY`

## 1. Scope

This is a no-live, read-only evidence gate.

It did not modify source, tests, runtime behavior, golden answer JSON, reviewed
Markdown, fixture promotion state, release/readiness state, PR state or cleanup
state. It did not run live EID, network, PDF, FDR, provider, LLM, analyze,
checklist, readiness, release, PR, push or merge commands.

## 2. Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-fixture-promotion-state-strict-golden-2025-promotion-plan-controller-judgment-20260613.md`
- `reports/golden-answers/golden-answer.json`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `fund_agent/fund/golden_answer.py`
- `fund_agent/fund/golden_readiness_preflight.py`
- historical tracked small-baseline artifacts only for 2025 status classification:
  - `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
  - `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`
  - `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md`

## 3. Artifact Identity

```text
shasum -a 256 reports/golden-answers/golden-answer.json reports/golden-answers/golden-answer-prefill-reviewed.md
9a21493d02c2fc5bcb8c9e314569fa99b014a2efd2a1963b49e41ffc1097bd71  reports/golden-answers/golden-answer.json
c93237ee7868665ee212ccbb4f998ec683cc47acef32057250ee86d1a0de6cc6  reports/golden-answers/golden-answer-prefill-reviewed.md
```

```text
wc -c reports/golden-answers/golden-answer.json reports/golden-answers/golden-answer-prefill-reviewed.md
  140962 reports/golden-answers/golden-answer.json
   49491 reports/golden-answers/golden-answer-prefill-reviewed.md
  190453 total
```

Both files are tracked:

```text
git ls-files reports/golden-answers/golden-answer.json reports/golden-answers/golden-answer-prefill-reviewed.md
reports/golden-answers/golden-answer-prefill-reviewed.md
reports/golden-answers/golden-answer.json
```

## 4. Strict Golden Identity Enumeration

Command:

```bash
uv run python -c 'from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; funds=load_golden_answer_json(Path("reports/golden-answers/golden-answer.json")); print("\n".join(f"{f.fund_code},{f.report_year},{len(f.records)}" for f in sorted(funds, key=lambda x: (x.fund_code, x.report_year))))'
```

Output:

```text
000216,2024,20
001548,2024,24
004194,2024,5
004393,2024,21
005313,2024,5
006597,2024,20
007360,2024,20
007721,2024,20
017644,2024,5
019918,2024,5
019923,2024,5
```

Direct finding:

- `004393,2025` is absent.
- `004393,2024` is present with 21 records.
- Under current loader/default semantics, the tracked strict golden answer JSON
  enumerates 11 fund/year identities, all as `2024`. The raw JSON does not need
  explicit `report_year` fields for legacy 2024 rows.

## 5. Golden Answer Source Authority Evidence

### Repo Fact

`fund_agent/fund/golden_answer.py` currently has two different year-handling
paths:

- Markdown parse/build path assigns rows to `LEGACY_GOLDEN_ANSWER_REPORT_YEAR`
  and constructs duplicate keys as `(fund_code, 2024, field_name, sub_field)`.
- Strict JSON loader accepts `report_year` on fund and record objects, requires
  fund/record year equality, and deduplicates by
  `(fund_code, report_year, field_name, sub_field)`.
- Missing JSON `report_year` falls back to the legacy 2024 year.

Relevant code facts:

```text
LEGACY_GOLDEN_ANSWER_REPORT_YEAR = 2024
parse_golden_answer_markdown(): key = (current_code, LEGACY_GOLDEN_ANSWER_REPORT_YEAR, field, sub_field)
parse_golden_answer_markdown(): GoldenAnswerRecord(... report_year=LEGACY_GOLDEN_ANSWER_REPORT_YEAR ...)
_append_current_fund(): report_year=LEGACY_GOLDEN_ANSWER_REPORT_YEAR
_parse_golden_answer_json_record(): record_report_year must equal fund_report_year
_parse_golden_answer_json_record(): key = (fund_code, fund_report_year, field_name, sub_field)
_json_optional_report_year(): missing report_year returns LEGACY_GOLDEN_ANSWER_REPORT_YEAR
```

### Truth-doc Fact

`docs/design.md` states:

- strict golden comparison identity is
  `fund_code + report_year + field_name + sub_field`;
- old JSON missing `report_year` is only loaded as accepted 2024 corpus;
- same fund across different years may coexist;
- missing same-year golden coverage is `year_not_covered`;
- other-year golden must not be used for mismatch comparison.

### Reviewed Markdown Fact

Tracked `reports/golden-answers/golden-answer-prefill-reviewed.md` contains
`## 004393 安信企业价值优选混合A（国内股票类）`, and the cited rows for that fund
use `年报2024` sources. The tracked `reports/golden-answers/` directory has no
`004393.*2025`, `2025.*004393` or `年报2025` match.

Command:

```bash
git grep -n -E "004393.*2025|2025.*004393|年报2025" -- reports/golden-answers
```

Output:

```text
<no matches; command exited 1>
```

## 6. Historical Tracked Evidence Classification

Tracked historical artifacts contain `004393 / 2025` references, but they classify
that path as probe-only rather than accepted baseline/golden material:

```text
docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md:
`004393` / 2025 as a probe-only report-year availability row.

docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md:
Keep probe-only. Next action: separate 2025 repository identity + fact-review
gate if 2025 is desired. No; report-year coverage missing and probe-only.

docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md:
`004393` / 2025 remains probe-only, not baseline or golden material.
```

Disposition:

- These historical tracked artifacts support the absence classification.
- They do not provide accepted same-year strict golden answer rows.
- They do not authorize writing `reports/golden-answers/golden-answer.json`.
- Historical probe-only artifacts and untracked workspace residue cannot supply
  same-year reviewed `expected_value` / `source` rows.

## 7. Fixture Promotion Boundary

Current `golden_readiness_preflight.py` is year-aware for strict golden coverage
but year-blind for fixture promotion state:

- strict golden coverage loads `(fund_code, report_year)`;
- missing fixture promotion state emits `fixture_promotion_absent`;
- fixture promotion state resolves `promotion_state = fixture_states.get(artifact.fund_code)`;
- current parser cannot represent `004393 / 2025`-only promotion.

Disposition:

- Fixture promotion state remains unresolved.
- No fixture promotion gate should open until strict golden 2025 answer authority
  is decided.
- If later promotion must be year-specific, a schema/parser planning gate is
  required before implementation.

## 8. Evidence Questions

| Question | Evidence | Disposition |
|---|---|---|
| Does tracked strict golden answer contain `004393 / 2025`? | Identity enumeration output in section 4. | `ABSENT` |
| Is absence expected under current truth? | Design identity rules, previous planning judgment and tracked historical probe-only artifacts. | `ACCEPTED_RESIDUAL` |
| What is the authoritative upstream for 2025 strict golden rows? | Markdown path is legacy 2024; JSON loader supports explicit years. | `UNDECIDED`; cannot open write gate yet. |
| Is JSON-only authority accepted now? | No accepted same-year reviewed source rows were found or reviewed in this gate. | `NOT_ACCEPTED_FOR_IMMEDIATE_WRITE`; future authority remains `UNDECIDED`. |
| Is Markdown/build-tooling support required before writing 2025 rows? | Required only if a later controller judgment rejects JSON-only authority or requires reviewed Markdown as reproducible upstream. | `CONDITIONAL_DEFERRED` |
| Can strict golden 2025 answer implementation start immediately? | Same-year accepted evidence and source authority are not accepted. | `NO` |
| Can fixture promotion implementation start immediately? | Strict golden 2025 answer unresolved; current fixture promotion parser is year-blind. | `NO` |

## 9. Validation

The following validation is parser/read-only sanity evidence only. It does not
prove source authority and does not authorize any golden answer write.

```text
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
25 passed in 0.58s
```

```text
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
All checks passed!
```

## 10. Next Entry Recommendation

Primary next entry:

```text
004393 / 2025 same-year evidence intake + source-authority decision gate
```

Rationale:

The evidence proves current tracked strict golden answer JSON does not contain
`004393 / 2025`, and historical tracked references classify `004393 / 2025` as
probe-only rather than accepted golden material. This gate did not find accepted
same-year reviewed rows, and it did not decide whether future 2025 rows should
be authorized by JSON-only accepted evidence or by a reviewed Markdown/build
pipeline. Therefore the next step must first intake or identify same-year
reviewed evidence and make a source-authority decision.

Conditional route:

- Open `Markdown / Golden Answer Schema Build-tooling Planning Gate` only if the
  next evidence/decision gate rejects JSON-only authority or requires reviewed
  Markdown to remain the reproducible upstream for 2025 rows.

Deferred entries:

- Markdown / Golden Answer Schema Build-tooling Planning Gate
- strict golden 2025 answer implementation gate
- fixture promotion state evidence gate
- fixture promotion state schema/parser planning gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate
- PR/release external-state gate

Release/readiness remains `NOT_READY`.
