# Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Plan - 2026-06-17

Gate: `Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Planning Gate`
Role: planning worker
Prior evidence commit: `028f0b8`
Status: `PLAN_READY_FOR_REVIEW_NOT_READY`
Release/readiness: `NOT_READY`

## Goal

Plan a narrow diagnostic gate to explain why the accepted Docling dedicated extractor produced zero direct candidate-field matches across four accepted current-schema Docling candidate envelopes.

The diagnostic must identify whether the mismatch is caused by:

- representation projection missing normalized section IDs;
- table family remaining `unknown`;
- row/column label paths not being populated;
- extractor rules depending on synthetic fixture shapes;
- current envelope truncation;
- or another observed shape mismatch.

## Motivation

The candidate-field no-live evidence gate produced:

- runnable samples: 4;
- target field slots: 92;
- direct slots: 0;
- missing slots: 92;
- candidate anchors: 0;
- blocked old S1 full JSON: 1.

This blocks field contract stabilization and production integration planning. The next move must be diagnostic, not rule changes by guesswork.

## Direct Code and Data Evidence

Extractor matching currently depends on:

- section filters such as `("§2",)`, `("§3",)`, `("§4",)`, `("§7",)`, `("§8",)`, `("§10",)`;
- key-value labels in table rows or text blocks;
- `row_label_path` and `column_header_path` for performance, manager, and holdings fields.

Preliminary probe on the four runnable envelopes found:

- S1: 25 sections, 670 text blocks, 95 tables, 3493 cells; table sections all `None`; text sections all `None`; table family all `unknown`; sampled label paths empty.
- S4: 229 sections, 737 text blocks, 96 tables, 2759 cells; table sections all `None`; text sections all `None`; table family all `unknown`; sampled label paths empty.
- S5: 208 sections, 856 text blocks, 121 tables, 7060 cells; table sections all `None`; text sections all `None`; table family all `unknown`; sampled label paths empty.
- S6: 222 sections, 840 text blocks, 124 tables, 5940 cells; table sections all `None`; text sections all `None`; table family all `unknown`; sampled label paths empty.

This explains the observed zero direct coverage without implying source absence or Docling impossibility.

## Non-goals

This planning gate will not:

- implement remediation;
- change extractor rules;
- change representation projection;
- generate fresh Docling conversions;
- access PDF/cache/source helpers directly;
- run live/network/provider/LLM/golden/readiness/release/PR commands;
- compare extracted values with source truth;
- authorize parser replacement, baseline promotion, or production integration.

## Proposed Diagnostic Gate

Next executable gate:

`Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Evidence Gate`

Allowed write set:

- `reports/docling-dedicated-extractor-real-envelope-mismatch-diagnostic/20260617/real_envelope_shape_matrix.json`
- `docs/reviews/docling-dedicated-extractor-real-envelope-mismatch-diagnostic-evidence-20260617.md`
- `docs/reviews/docling-dedicated-extractor-real-envelope-mismatch-diagnostic-controller-judgment-20260617.md`
- review artifacts under `docs/reviews/` if reviewers are used.

## Diagnostic Matrix Requirements

For each runnable sample, record:

- document identity;
- counts of sections, text blocks, tables, cells;
- section ID distribution for text blocks and tables;
- top heading texts and whether any can normalize to `§2/§3/§4/§7/§8/§10`;
- table family distribution;
- percentage of cells with non-empty `row_label_path`;
- percentage of cells with non-empty `column_header_path`;
- sample rows containing target labels:
  - `基金名称`, `基金代码`, `基金管理人`, `基金托管人`;
  - `投资目标`, `投资范围`, `业绩比较基准`, `风险收益特征`;
  - `管理费`, `托管费`;
  - `净值增长率`, `业绩比较基准收益率`;
  - `姓名`, `任职日期`;
  - `股票名称`, `债券名称`, `基金名称`, `公允价值`, `占基金资产净值比例`;
- matcher failure classification per target field:
  - `section_id_absent`;
  - `label_absent`;
  - `label_present_but_section_blocked`;
  - `row_column_paths_absent`;
  - `table_family_unknown`;
  - `deferred_by_plan`;
  - `other`.

## Root-cause Decision Rules

The diagnostic controller judgment must classify each candidate cause:

- `primary_cause`;
- `contributing_cause`;
- `not_supported`;
- `needs_more_evidence`.

A remediation plan is allowed only when at least one primary cause is backed by matrix evidence.

## Success Signal

The diagnostic evidence gate passes when it can answer:

1. Does zero coverage primarily come from missing section IDs?
2. Are target labels present anywhere in the projected envelope?
3. Are target labels blocked only because section filters expect `§N` IDs?
4. Are table row/column label paths absent across the corpus?
5. Which smallest remediation slice should run next?

## Expected Next Gate After Diagnostic

If primary cause is `section_id_absent`, next gate should plan section-context normalization for real envelopes.

If primary cause is `row_column_paths_absent`, next gate should plan row/column label derivation from candidate table cells.

If primary cause is `label_absent`, next gate should inspect representation export fidelity before extractor changes.

If multiple primary causes exist, remediation must be sliced in this order:

1. section context normalization;
2. row/column label derivation;
3. field-specific matcher refinement.

## Boundary

All outputs remain:

- candidate-only;
- `source_truth_status="not_proven"`;
- release/readiness `NOT_READY`.

VERDICT: `PLAN_READY_FOR_REVIEW_NOT_READY`
