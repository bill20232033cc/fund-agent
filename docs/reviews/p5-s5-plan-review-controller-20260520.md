# Controller Plan Review - P5-S5 Share Change Hardening - 2026-05-20

## Verdict

NEEDS PATCH.

The plan correctly identifies the implementation smell: current share-change extraction uses first non-empty value after the label, which is an implicit column-order rule. However, one proposed branch still risks indirect inference.

## Findings

### P5-S5-PR1 - Do not infer A/C share class from `fund_code` last character

Severity: blocking

The plan allows “infer share class from the last character of `fund_code`” if headers include explicit class labels. That is not data-same-source in this codebase. A fund code alone does not reliably encode A/C class across fund companies, and the current extractor does not have a fund-code-to-share-class registry or product name source in scope.

Patch requirement:

- Remove fund-code-last-character inference entirely from P5-S5.
- Allowed resolution rules:
  - Single value column after project column.
  - Exact fund code appears in a value column header.
  - Explicit A-class fallback only when there is exactly one `A类` value column, no exact-code match, and no conflicting total/code-specific column.
- Ambiguous multi-value tables must return `missing`.

### P5-S5-PR2 - Define total-column behavior explicitly

Severity: medium

Some tables may include total columns plus A/C columns. The plan mentions totals as a risk but does not define behavior.

Patch requirement:

- A header containing `合计`, `总计`, `基金份额总额`, or `总份额` should not be selected as a class-specific fallback.
- If a single value column exists and it is a total column, it is still acceptable because no class split exists in that table shape.
- If total and A/C columns coexist without exact-code match, the A-class fallback is allowed only when exactly one A-class column exists and the total column is ignored for fallback ambiguity.

### P5-S5-PR3 - Metadata values must be stable enum-like strings

Severity: low

The plan proposes metadata strings but does not list all reason values.

Patch requirement:

Use stable reason values:

- `single_value_column`
- `fund_code_header_match`
- `single_a_class_fallback`

Ambiguous cases should not produce metadata because the field is missing.

## Required Plan Patch

Patch the plan with PR1/PR2/PR3, then re-review.

Next gate: `P5-S5 plan re-review`.
