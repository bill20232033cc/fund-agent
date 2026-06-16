# Docling Multi-sample Field-family Correctness Expansion Evidence Local Review - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Evidence Gate`
Reviewer: local fallback reviewer
Release/readiness: `NOT_READY`

## Scope

This review covers:

- `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md`
- `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json`

Subagent review was attempted through the available subagent channel, but the
spawn call returned `agent thread limit reached`. This review therefore does
not claim MiMo, DS or ProCodex participation.

## Review Result

```text
VERDICT: PASS_WITH_RESIDUALS_NOT_READY
```

## Findings

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| R1 | Medium | The evidence reuses the prior blocked evidence paths and overwrites their working-tree content. This is acceptable only if the controller explicitly records that the new evidence supersedes the prior blocked evidence at the same path and that the old blocked state remains recoverable by checkpoint history. | ACCEPT_RESIDUAL |
| R2 | Medium | Reference excerpts come from `FundDocumentRepository(..., force_refresh=False)` parsed table rows, not visual screenshots or raw PDF crop images. This is stronger than candidate self-agreement but weaker than visual/crop review. | ACCEPT_RESIDUAL |
| R3 | Medium | `manager_alignment` is intentionally blocked for S4/S5/S6. The evidence does not hide this; each sample has one blocked family while five table-heavy families pass. | ACCEPT_RESIDUAL |
| R4 | Low | pdfplumber comparator is not re-opened for S4/S5/S6, so the artifact cannot compare Docling vs pdfplumber correctness for the expansion samples. | ACCEPT_RESIDUAL |

## Pass Checks

| Check | Result |
| --- | --- |
| No readiness/source-truth/parser-replacement claim | PASS |
| JSON contains guard fields `not_source_truth`, `not_production_parser_replacement`, `not_full_field_correctness`, `not_readiness_proof` | PASS |
| S4/S5/S6 use accepted EID single-source/no-fallback reference metadata plus `force_refresh=False` repository load | PASS |
| Candidate facts are compared to repository-loaded reference excerpts, not only to candidate JSON or parser-vs-parser agreement | PASS |
| Three expansion samples are reviewable and each records five passed field families | PASS |
| Mismatches are zero in the reviewed fact set | PASS |
| EID HTML remains `blocked_deferred` | PASS |
| No source/test/runtime behavior change | PASS |

## Residuals

- Local fallback review only; no independent MiMo/DS review was obtained.
- The prior blocked evidence content is superseded in the working tree at the
  same path; controller must record this as intentional if accepted.
- The evidence is still candidate-layer evidence only. It is not source truth,
  full field correctness, parser replacement or readiness proof.
