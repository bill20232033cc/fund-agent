# 004393 / 2025 Same-year Reviewed Golden Content Plan

Date: 2026-06-13

Gate: `004393 / 2025 Same-year Reviewed Golden Content Planning Gate`

Verdict: `PLAN_FOR_REVIEW_NOT_READY`

## 1. Goal

Plan the next no-live reviewed same-year golden content/evidence intake for
`004393 / 2025`.

The next gate must use the accepted Markdown-first path:

````markdown
## 004393 安信企业价值优选混合A（国内股票类）

```golden-answer-metadata
report_year: 2025
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
````

Release/readiness remains `NOT_READY`.

## 2. Non-goals

- Do not implement source, test or runtime behavior.
- Do not edit tracked golden answer content under `reports/golden-answers/`.
- Do not write `reports/golden-answers/golden-answer-prefill-reviewed.md`.
- Do not write `reports/golden-answers/golden-answer.json`.
- Do not modify fixture promotion state or fixture promotion schema.
- Do not run live EID, network, PDF, FDR, provider, LLM, analyze, checklist,
  golden-build against tracked outputs, readiness, release, PR, push or merge
  commands.
- Do not delete, move, archive, cleanup, stage, commit or push.
- Do not use arbitrary untracked residue as proof.
- Do not reintroduce JSON-only write authority, source-text inference,
  Eastmoney / fund-company / CNINFO fallback, or same-year content acceptance in
  this planning gate.

## 3. Accepted Prior Facts

| Fact | Status |
|---|---|
| Strict golden identity is `fund_code + report_year + field_name + sub_field`. | Accepted design and implementation fact. |
| Legacy missing `report_year` means current reviewed 2024 compatibility only. | Accepted design and loader fact. |
| Other-year golden rows cannot be reused for same-year correctness. | Accepted design fact. |
| Current tracked strict golden answers do not contain `004393 / 2025`. | Accepted by strict golden 2025 answer evidence controller judgment. |
| Historical `004393 / 2025` rows are probe-only, not baseline/golden material. | Accepted by same-year source-authority decision. |
| JSON-only authority is rejected as the default tracked golden write route. | Accepted by same-year source-authority decision. |
| Reviewed Markdown can now declare fund-level `golden-answer-metadata` `report_year`. | Accepted by Markdown/golden schema build-tooling implementation judgment. |
| Missing metadata still resolves to legacy 2024. | Accepted by build-tooling implementation judgment. |
| Same fund code may appear across different years if `report_year` differs. | Accepted by code/tests and implementation judgment. |
| `source` text is human evidence description, not machine identity authority. | Accepted by design and implementation judgment. |

## 4. Still Not Accepted

| Item | Status |
|---|---|
| Any `004393 / 2025` reviewed `expected_value` / `source` row. | Not accepted. |
| Any tracked golden-answer content edit for `004393 / 2025`. | Not authorized. |
| Any fixture promotion for `004393 / 2025`. | Not accepted; current promotion state remains unresolved/year-blind. |
| Any release/readiness improvement from this line of work. | Not accepted; remains `NOT_READY`. |
| Historical 2025 probe rows as truth. | Rejected unless re-reviewed through this gate path. |
| Eastmoney, fund-company or CNINFO fallback as source authority. | Not authorized. |

## 5. Candidate Row Source Contract

Candidate row source preparation is a prerequisite for the evidence gate.

Required candidate row source artifact:

```text
docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md
```

Producer:

- `Candidate Row Source Preparation Gate` worker, or controller-authorized
  content/evidence owner working under the same no-live boundaries.

Start condition:

- The preparation gate may start only when the controller provides or authorizes
  a same-year `004393 / 2025` candidate-row source package.
- The evidence gate cannot start if the candidate row artifact is absent.
- The evidence gate cannot start if the candidate row artifact exists but
  contains no candidate rows.
- The evidence gate cannot start if the candidate row artifact lacks explicit
  `golden-answer-metadata` with `report_year: 2025`.

Required artifact format:

````markdown
# 004393 / 2025 Same-year Reviewed Golden Content Candidate Rows

Date: 2026-06-13

Source status: `CANDIDATE_ROWS_FOR_REVIEW_NOT_ACCEPTED`

## Candidate Rows

## 004393 安信企业价值优选混合A（国内股票类）

```golden-answer-metadata
report_year: 2025
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| classified_fund_type | fund_type | active_fund | high | 年报2025 §2 page-<locator> |
````

Rules:

- The artifact is reviewed Markdown candidate rows under `docs/reviews/`, not
  tracked golden content under `reports/golden-answers/`.
- Candidate rows are not accepted golden rows by themselves.
- The candidate artifact must preserve the five-column table shape:
  `field | sub_field | expected_value | confidence | source`.
- It must include explicit `golden-answer-metadata` `report_year: 2025`.
- It must not use JSON-only authority, source-text year inference, fallback
  source routes, fixture promotion state or arbitrary residue as proof.

## 6. Conditional Next Entry

If the candidate row artifact is absent or shape-invalid, next entry is:

```text
004393 / 2025 Candidate Row Source Preparation Gate
```

If the candidate row artifact exists, contains at least one candidate row and is
shape-valid under the Markdown-first `report_year: 2025` contract, next entry
is:

```text
004393 / 2025 Same-year Reviewed Golden Content Evidence Gate
```

## 7. Proposed Evidence Gate

Classification:

```text
standard
```

Rationale:

- It is a row-level evidence/content acceptance gate with no source/test/runtime
  implementation.
- It can affect future strict golden content and therefore is not `fast_path`.
- It does not itself change public contract, runtime behavior, fixture
  promotion, release/readiness or PR state, so `heavy` is not required unless
  the future gate expands scope.

Purpose:

- intake candidate `004393 / 2025` reviewed Markdown rows;
- verify each row against direct same-year evidence;
- decide row-by-row accept / defer / reject;
- preserve Markdown-first authority;
- preserve `NOT_READY`.

The next gate is not a tracked golden-answer write gate. It is a row acceptance
gate. Strict golden content implementation remains blocked until this evidence
gate accepts enough same-year rows and a later controller gate authorizes the
tracked `reports/golden-answers/` write.

## 8. Proposed Read Set For Evidence Gate

Required read set:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`
- `docs/reviews/mvp-strict-golden-2025-answer-evidence-20260613.md`
- `docs/reviews/mvp-strict-golden-2025-answer-evidence-controller-judgment-20260613.md`
- `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-20260613.md`
- `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-controller-judgment-20260613.md`
- `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-implementation-controller-judgment-20260613.md`
- `fund_agent/fund/golden_answer.py`
- `tests/fund/test_golden_answer.py`
- `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md`

Historical probe-only artifacts may be read only to confirm non-authority:

- `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
- `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`
- `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md`

Disallowed read-as-proof:

- arbitrary untracked `reports/`, `reviews/`, local PDFs or scratch residue;
- product narrative output without row-level review;
- 2024 golden rows as 2025 evidence;
- quality gate `year_not_covered` status by itself.

Read-only operator docs:

- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`

The evidence gate may read these files for row-shape rules but must not modify
them.

## 9. Proposed Write Set For Evidence Gate

Allowed write set:

- `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-evidence-20260613.md`
- `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-review-mimo-20260613.md`
- `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-review-ds-20260613.md`
- `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-controller-judgment-20260613.md`
  only if written by controller after reviews
- optional temporary smoke files under `/private/tmp` only, if build smoke is
  needed

Explicitly disallowed write set:

- `docs/golden-answer-instructions.md`
- `docs/golden-answer-template.md`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- fixture promotion state files
- source files
- tests
- runtime outputs under tracked report directories
- readiness, release or PR artifacts
- cleanup/disposition artifacts unrelated to this gate

If candidate rows need a durable reviewed input, keep them inside the evidence
artifact or a separate `docs/reviews/` candidate-row appendix. Do not place them
in tracked golden-answer content until a later implementation/write gate is
accepted.

Exact artifact name pattern:

| Artifact | Path |
|---|---|
| Candidate rows | `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md` |
| Evidence | `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-evidence-20260613.md` |
| MiMo review | `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-review-mimo-20260613.md` |
| DS review | `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-review-ds-20260613.md` |
| Controller judgment | `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-controller-judgment-20260613.md` |

## 10. Row Acceptance Criteria

Each candidate row must be evaluated independently.

Required row shape:

| Column | Requirement |
|---|---|
| fund block | Heading must be `004393` and the fund-level metadata must declare `report_year: 2025`. |
| field | Non-empty field name from the current comparable golden/snapshot contract. |
| sub_field | Non-empty sub-field name; `—` means skip row, not accepted content. |
| expected_value | Exact expected correctness value, copied or normalized only under a documented row-specific rule. |
| confidence | One of `high`, `medium`, `low`. |
| source | Direct same-year source line for 2025 annual-report evidence. |

Direct same-year evidence:

- The row must cite 2025 annual-report evidence for `004393`.
- The evidence must support the exact `expected_value` for that row.
- The evidence must be row-local; one row cannot inherit proof from another row
  unless the shared source line explicitly covers both values.
- 2024 rows, cross-year narrative facts, product smoke output, fixture state,
  preflight gaps or source availability facts cannot supply row truth.

Reviewed Markdown row shape:

- The fund block must use the accepted fenced `golden-answer-metadata` block.
- The table must remain the five-column reviewed Markdown shape:
  `field | sub_field | expected_value | confidence | source`.
- The row must be valid under `parse_golden_answer_markdown()` semantics.
- Duplicate `(004393, 2025, field, sub_field)` identities must be rejected.

`report_year: 2025` requirement:

- `report_year` must be explicit in the metadata block.
- Missing metadata is legacy 2024 and cannot be accepted for this gate.
- Do not infer `report_year` from heading text, source text or file name.

Source line format:

- Preferred format: `年报2025 §<章节> page-<页码>` plus table/row locator when
  applicable.
- Table evidence should include table and row information when the annual report
  has a stable table/row locator.
- If stable page numbering is unavailable, source must use the strongest stable
  locator available, for example `年报2025 §<章节> table-<表名或编号>
  row-<行标签>` or `年报2025 §<章节> paragraph-<可复核短标签>`. The evidence
  artifact must state why page numbering is unavailable and why the alternate
  locator is stable enough for review.
- Source must not be blank, `manual_required`, `—`, `年报2024`, probe-only,
  product-output-only or residue-only.
- Source prose is not machine identity; it is accepted only as human-review
  evidence text.

Confidence rules:

- `high`: direct 2025 annual-report text/table clearly states the value with no
  selection ambiguity.
- `medium`: the value is directly present but requires bounded judgment, such as
  selecting a period column or preserving a long text span.
- `low`: disclosure is ambiguous, partial or formatting-sensitive; low rows
  must be deferred unless the evidence artifact records row-specific rationale
  and the controller judgment explicitly acknowledges that exact low-confidence
  row.
- Any confidence outside `high / medium / low` is invalid.

Skip/defer/reject rules:

- Skip rows with `sub_field=—` or `expected_value=—`; they remain skipped
  template rows, not accepted content.
- Defer rows where same-year evidence is unavailable, not directly read, too
  ambiguous, or dependent on a future extractor/source contract.
- Reject rows sourced from 2024, probe-only artifacts, product smoke output,
  arbitrary residue, source fallback, fixture promotion state or inferred
  source text.
- Reject rows whose expected value is paraphrased when the field requires exact
  source text.
- Reject rows that require changing source acquisition, extractor behavior,
  score semantics or fixture promotion to become true.

Defer classes:

| Class | Use when | Required residual |
|---|---|---|
| `DEFER_NOT_READ` | The candidate row exists, but the evidence gate did not read or receive enough reviewable same-year evidence to decide it. | `same-year row pending direct read/review for <field>.<sub_field>`. |
| `DEFER_NOT_DISCLOSED` | The reviewed same-year evidence was checked and the value is not disclosed or not available in the cited 2025 annual-report material. | `same-year source does not disclose required value for <field>.<sub_field>`. |
| `DEFER_AMBIGUOUS` | The same-year evidence exists but supports multiple plausible values, unstable locators or uncertain normalization. | `same-year value ambiguous for <field>.<sub_field>; requires controller/source-owner clarification`. |

Zero-accepted-row disposition:

- The evidence gate may close with zero accepted rows as `NOT_READY`.
- Zero accepted rows cannot authorize tracked golden content writes.
- Zero accepted rows must route back to `004393 / 2025 Candidate Row Source
  Preparation Gate` or a source-owner clarification gate, with residuals split
  by `DEFER_NOT_READ`, `DEFER_NOT_DISCLOSED` and `DEFER_AMBIGUOUS`.

Minimum acceptance criterion for any later tracked content write:

- At least one row must be accepted by row identity and same-year evidence before
  a later tracked golden content write gate may be proposed.
- This is not an arbitrary coverage target; it is only the minimum condition for
  any content write to have a concrete accepted row to write.

## 11. Historical Probe-only Prohibition

Historical `004393 / 2025` probe rows are not truth.

They may only support this negative fact:

```text
004393 / 2025 existed historically as probe-only availability/status material,
not as accepted baseline or strict golden content.
```

They must not be used as accepted row evidence unless the next evidence gate
re-reads the underlying same-year evidence and accepts the exact row through the
Markdown-first `report_year: 2025` path.

## 12. Future Validation Matrix

The content/evidence gate is no-live and row-review oriented. Source/test/runtime
validation is not required unless a temporary build smoke is needed to prove row
shape.

| Validation | Command / Method | Path boundary | Required result |
|---|---|---|---|
| Row-shape inspection | Manual review in evidence artifact | `docs/reviews/` only | Every accepted row has five columns and explicit `report_year: 2025` metadata. |
| Duplicate identity check | Manual table or temporary parser smoke | `/private/tmp` only if scripted | No duplicate `(004393, 2025, field, sub_field)` rows. |
| Parser/build smoke, optional | Use Python API or `golden-build` only with temp input/output paths | `/private/tmp/.../reviewed.md` and `/private/tmp/.../golden-answer.json` | Metadata-built payload emits fund and record `report_year=2025`. |
| Temp artifact cleanup check, if smoke ran | Explicit path listing/removal confirmation inside evidence artifact | `/private/tmp` only | No temp smoke artifacts remain after the gate. |
| Tracked-output protection | Inspect intended write set | No `reports/golden-answers/` write | Tracked golden content remains unchanged. |
| Readiness boundary | Evidence artifact statement | `docs/reviews/` only | Verdict preserves `NOT_READY`. |

If optional build smoke is run, it must not use default output paths and must
not overwrite tracked `reports/golden-answers/golden-answer.json`. The evidence
artifact must also verify that no temp smoke artifacts remain after the smoke.

Evidence wording boundary:

- If the evidence gate does not read the 2025 annual-report body directly, it
  must not claim primary-source verification.
- In that case, it may only claim candidate-row source review against the
  candidate artifact and any accepted excerpts/locators present in the reviewed
  source package.
- Primary annual-report verification requires an explicitly authorized gate that
  reads the annual-report body through the approved evidence boundary.

Disallowed validation:

- live EID / network / PDF / FDR commands;
- provider / LLM commands;
- `analyze` / `checklist`;
- readiness / release / PR commands;
- tracked `golden-build` output writes;
- fixture promotion commands.

## 13. Review Plan

Required independent reviews:

- MiMo review: check row acceptance criteria, write/read boundaries, historical
  probe-only prohibition and `NOT_READY` preservation.
- DS review: independently challenge source authority, direct same-year evidence
  sufficiency, confidence classification, skip/defer rules and temp-path
  validation boundaries.

Reviewers must not implement, edit tracked golden content, promote fixtures or
run live/provider/runtime/readiness commands. Review output should be limited
to `docs/reviews/` review artifacts.

Reviewer row-editing prohibition:

- Reviewers must not edit candidate rows, accepted rows, expected values,
  confidence labels or source locators.
- Reviewers may only return findings and required changes in their review
  artifacts.

Parallelism:

- MiMo and DS reviews may run in parallel after the evidence artifact is final.
- They must be independent reviews; neither review should use the other review's
  findings as input before both are complete.
- Controller judgment may be written only after both MiMo and DS reviews are
  available.

## 14. Stop Conditions

Stop and return to controller if:

- candidate row source artifact is absent or contains no candidate rows;
- candidate row source artifact is not valid reviewed Markdown with explicit
  `golden-answer-metadata` `report_year: 2025`;
- a row requires reading arbitrary untracked residue as proof;
- row truth depends on 2024 golden content or historical probe-only status;
- source authority requires JSON-only writes;
- source authority requires inferring year from `source` text;
- evidence requires Eastmoney, fund-company, CNINFO or other fallback routes;
- validation requires live EID, network, PDF, FDR, provider, LLM, analyze,
  checklist, readiness, release or PR commands;
- accepting a row requires source/test/runtime behavior changes;
- accepting a row requires fixture promotion changes;
- any operation would write tracked `reports/golden-answers/` content;
- the gate would change release/readiness away from `NOT_READY`.

## 15. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Candidate row source artifact may be absent or shape-invalid. | Golden content/source owner | Candidate Row Source Preparation Gate. |
| Same-year `004393 / 2025` row values remain unaccepted. | Golden content/evidence owner | Next content evidence gate. |
| `DEFER_NOT_READ` rows remain undecided. | Golden content/evidence owner | Direct read/review follow-up for named rows. |
| `DEFER_NOT_DISCLOSED` rows remain unsupported by same-year disclosure. | Golden content/source owner | Source-owner clarification or row removal. |
| `DEFER_AMBIGUOUS` rows remain normalization/locator ambiguous. | Controller/source owner | Controller/source-owner clarification gate. |
| Tracked golden answer content remains unchanged. | Golden answer owner | Later tracked content implementation/write gate, only after row acceptance. |
| Fixture promotion remains unresolved and year-blind. | Fixture promotion owner | Separate fixture promotion design/evidence gate. |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup after content and promotion residuals close. |
| Historical probe-only 2025 material remains non-truth. | Controller/evidence owner | May be cited only as non-authority evidence. |

## 16. Recommended Next Entry

Conditional recommended next entry:

If candidate row source artifact is absent or shape-invalid:

```text
004393 / 2025 Candidate Row Source Preparation Gate
```

If candidate row source artifact is present, contains candidate rows and is
shape-valid:

```text
004393 / 2025 Same-year Reviewed Golden Content Evidence Gate
```

Implementation/content write remains blocked until that evidence gate accepts
row-level same-year content and a later controller-approved write gate authorizes
tracked golden answer updates.
