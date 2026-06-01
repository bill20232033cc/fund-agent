# Plan Review: QDII Replacement Fallback 021539 Evidence Plan — AgentGLM

> Date: 2026-05-27
> Reviewer: AgentGLM (independent plan review, not controller, not evidence runner)
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-20260527.md`
> Verdict: **PASS**

## 1. Startup Packet Entry Point Verification

Plan Section 1 states gate `QDII replacement fallback candidate evidence plan gate for 021539`.

Cross-check against `docs/implementation-control.md` Startup Packet:

| Field | Control doc value | Plan artifact value | Match |
|---|---|---|---|
| Current phase | `release maintenance` | `release maintenance` | yes |
| Current gate | `QDII replacement post-019172 disposition decision accepted locally` | `QDII replacement post-019172 disposition decision accepted locally` | yes |
| Next entry point | `QDII replacement fallback candidate evidence plan gate for 021539; must use init-agents / tmux multi-agent flow` | `QDII replacement fallback candidate evidence plan gate for 021539` | yes |

The plan explicitly states "This plan follows the Startup Packet next entry point. It is not a gate switch." The `init-agents` requirement is preserved in Sections 1 and 14 as a controller obligation.

**Criterion 1: PASS.**

## 2. Plan-Only / No Evidence Authorized

Section 4 lists six prohibited `fund-analysis` subcommands. Section 15 restates all prohibitions including `--help` commands. No evidence command, `fund-analysis` invocation, PDF inspection, cache access, source-helper access, external web access, or provenance inference is authorized.

The plan artifact is plan-only throughout all 16 sections.

**Criterion 2: PASS.**

## 3. Single Candidate Identity And Pre-State

Section 2 identifies exactly one candidate:

| Field | Plan value | Enumeration plan value | Match |
|---|---|---|---|
| `fund_code` | `021539` | `021539` | yes |
| `report_year` | `2024` | `2024` | yes |
| Fund name | `华安法国CAC40ETF发起式联接(QDII)A` | `华安法国CAC40ETF发起式联接(QDII)A` | yes |
| CSV category | `海外股票类` | `海外股票类` | yes |
| Pre-state provenance | `provenance_unknown` | `provenance_unknown` | yes |
| Pre-state quality | `quality_unknown` | (not previously evaluated) | yes |
| Pre-state promotion | `not_promoted` | (not previously evaluated) | yes |

Section 2 explicitly states the plan does not make 021539 source-safe, scoring-ready, baseline-ready, golden-ready, accepted as replacement, promoted, or approved for durable corpus use.

**Criterion 3: PASS.**

## 4. Preserved Accepted States For 096001 / 040046 / 019172

### 096001

| Field | Plan Section 3 value | Accepted disposition / controller judgment value | Match |
|---|---|---|---|
| Source provenance | eligible complete public fallback provenance; `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback` | same provenance tuple | yes |
| Quality | `quality_gate_status=block` | `quality_gate_status=block`; `issue_count=10` | yes (compressed) |
| Terminal | `quality_blocked_after_provenance` | `quality_blocked_after_provenance` | yes |
| Promotion | `not_promoted` | `not_promoted` | yes |
| P0 blocker | `nav_benchmark_performance` | `nav_benchmark_performance` coverage / traceability and evidence-anchor failure | compressed, not contradicted |
| FQ4 | `42.9%` | `42.9%` | yes |
| P1 gaps | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | same fields | yes |

### 040046

| Field | Plan Section 3 value | Accepted disposition / controller judgment value | Match |
|---|---|---|---|
| Source provenance | eligible complete public fallback provenance; same tuple as 096001 | same | yes |
| Quality | `quality_gate_status=block` | `quality_gate_status=block`; `issue_count=7` | yes |
| Terminal | `quality_blocked_after_provenance` | `quality_blocked_after_provenance` | yes |
| Promotion | `not_promoted` | `not_promoted` | yes |
| Key distinction | "FQ4 missing-field-rate `35.7%` with P0 pass" | "No P0 failed fields; FQ4 missing-field-rate `35.7%` exceeds threshold `35.0%`" | yes |
| P1 gaps | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | same fields | yes |

### 019172

| Field | Plan Section 3 value | Accepted 019172 controller judgment value | Match |
|---|---|---|---|
| Source provenance | eligible complete public fallback provenance; same tuple | same | yes |
| Quality | `quality_gate_status=block`; `issue_count=9` | `quality_gate_status=block`; `issue_count=9` | yes |
| Terminal | `quality_blocked_after_provenance` | `quality_blocked_after_provenance` | yes |
| Promotion | `not_promoted` | `not_promoted` | yes |
| P0 blocker | `manager_strategy_text` coverage / traceability `0.0% / 0.0%` | P0 `manager_strategy_text` coverage / traceability `0.0% / 0.0%` | yes |
| FQ4 | `35.7%` | `35.7%` | yes |
| P1 gaps | `turnover_rate`, `holdings_snapshot`, `share_change` | same fields | yes |

All three preserved states are accurate. No rerun, weakening, or reinterpretation is introduced.

**Criterion 4: PASS.**

## 5. Forbidden Candidates

Section 4 paragraph 2 and Section 15 prohibit: `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, `019172`.

This matches the controller judgment's required constraint list exactly.

**Criterion 5: PASS.**

## 6. Public CLI And Generated-Output Provenance Discipline

Section 5 plans CLI preflight with three `--help` commands and specifies flag-mismatch stop behavior (`cli_flag_mismatch_not_run`).

Section 7 requires reading `summary.md` and `snapshot.jsonl` for provenance, not stdout-only. It requires recording where each provenance field was read from. If stdout and generated files disagree, generated public files control.

Section 8 requires source provenance interpretation before score, quality, or promotion. Fail-closed categories `schema_drift`, `identity_mismatch`, `integrity_error` stop the evidence path. Eligible fallback requires `primary_failure_category` exactly `not_found` or `unavailable` with public `fallback_eligibility=eligible` and complete public provenance.

The plan lists seven explicit non-eligible patterns that must not be treated as fallback permission.

**Criterion 6: PASS.**

## 7. Terminal Matrix Completeness

Section 10 terminal-state matrix rows:

| # | Condition | Covered |
|---|---|---|
| 1 | CLI help flag mismatch | yes |
| 2 | Snapshot command non-zero exit | yes |
| 3 | Public snapshot outputs missing after zero exit | yes |
| 4 | Public provenance missing or incomplete | yes |
| 5 | Fail-closed source (`schema_drift`, `identity_mismatch`, `integrity_error`) | yes |
| 6 | Ineligible or unknown fallback category | yes |
| 7 | Score command non-zero exit | yes |
| 8 | Quality-gate command non-zero exit | yes |
| 9 | P0 block on `manager_strategy_text` | yes |
| 10 | P0 block on another field | yes |
| 11 | FQ4 / non-P0 structural quality block + P0 pass | yes |
| 12 | Quality `warn` with P1 residuals only | yes |
| 13 | Quality `pass` | yes |

All 13 rows keep `promotion_disposition=not_promoted`. The FQ4/non-P0 row explicitly includes the P0-pass case, referencing accepted 040046 precedent.

**Criterion 7: PASS.**

## 8. Hard Stop After Quality Block

Section 11 states: if a later accepted 021539 evidence gate quality-blocks after eligible provenance, automatic QDII probing stops. The next step must be a new disposition gate choosing between QDII diagnosis, taxonomy/asset-class fitness, or recording coverage blocked.

Section 11 explicitly lists prohibited continuations: `020712`, active QDII, QDII-FOF, `013308`, bond QDII, and any later candidate.

**Criterion 8: PASS.**

## 9. Exclusions And Prohibitions Completeness

Section 12 preserves:

- `017641` excluded (eligible provenance but quality-blocked, not promoted).
- QDII-FOF excluded unless taxonomy gate accepts.
- `013308` pending (naming/category conflict).
- Bond QDII pending (asset-class fitness).

Section 15 lists comprehensive non-goals: no durable-baseline, scoring-ready, golden answer corpus, accepted replacement, taxonomy conflict resolution, QDII-FOF acceptance, bond QDII fitness, or QDII extraction/applicability diagnosis.

Prohibited actions in Section 15 include: no code, tests, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, source-helper, taxonomy, extractor, Host, Agent, Dayu, golden files, baseline fixtures, corpus state, commit, push, PR, merge, or GitHub mutation.

**Criterion 9: PASS.**

## 10. Validation

Section 16 specifies only `git diff --check`.

No ruff, pytest, or other validation tool is invoked or required for a plan-only artifact.

**Criterion 10: PASS.**

## Findings

### F1 — LOW — 096001 P0 detail compression

Section 3 preserves 096001's P0 blocker as "P0 `nav_benchmark_performance`" while the accepted disposition records "P0 `nav_benchmark_performance` coverage / traceability and evidence-anchor failure". The compressed form omits the specific failure mode (coverage / traceability / evidence-anchor) but does not contradict the accepted state and correctly preserves the P0 field name, FQ4 rate, P1 gaps, terminal classification, and promotion disposition.

No correctness impact. No patch required. The compression is acceptable in a preserved-state summary.

### F2 — LOW — 040046 issue_count not preserved

Section 3 preserves 040046 without `issue_count`. The accepted disposition records `issue_count=7`. This is a minor omission in the preserved-state summary; the key blocking factors (P0 pass, FQ4 35.7%, P1 gaps) are correctly preserved.

No correctness impact. No patch required.

## Verdict

**PASS**

All 10 review criteria are satisfied. Two LOW findings (P0 detail compression for 096001, missing issue_count for 040046) are cosmetic and do not affect the correctness, completeness, or safety of the plan. The plan accurately follows the Startup Packet next entry point, correctly identifies the single candidate 021539/2024 with proper pre-states, accurately preserves prior candidate terminal states, correctly forbids all excluded candidates, properly plans public CLI commands with flag-mismatch stop behavior, requires generated-file provenance reading before quality interpretation, includes a complete 13-row terminal matrix with explicit FQ4/non-P0 + P0-pass row, enforces hard stop after quality block, preserves all exclusions, and validates with `git diff --check` only.

No patch or re-review required.
