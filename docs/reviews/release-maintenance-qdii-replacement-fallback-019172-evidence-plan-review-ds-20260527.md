# QDII Replacement Fallback 019172 Evidence Plan — Independent Plan Review (DS)

> Date: 2026-05-27
> Reviewer: AgentDS (review / plan-review only; no implementation, no commit, no push, no PR)
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-20260527.md`
> Verdict: **PASS**

## Review Scope

This review checks the plan artifact against the 10 controller criteria for 019172 evidence plan review plus accepted truth sources: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, and all five accepted QDII replacement artifacts from the controller brief.

## 1. Plan-Only / No Evidence Run

| Check | Finding | Evidence |
|-------|---------|----------|
| Plan declares plan-only | PASS | §1: "Scope: plan artifact only. No evidence run." |
| Stop conditions forbid evidence CLI | PASS | §13: "do not run evidence; do not run fund-analysis extraction-snapshot; do not run fund-analysis extraction-score; do not run fund-analysis quality-gate" |
| Future commands scoped to future gate | PASS | §4: "it does not authorize running these commands in this plan gate"; §5: "This artifact does not authorize running them in this plan gate" |
| Contingency boundaries explicit | PASS | §10: "If 019172 fails in a later accepted evidence gate, the next candidate must be selected only through a new controller-authorized plan gate." |

**Conclusion**: Plan-only, no authorized evidence run. PASS.

## 2. Startup Packet Next Entry Point / Not Gate Switch

| Check | Finding | Evidence |
|-------|---------|----------|
| Startup Packet replay present and correct | PASS | §1 table: current phase `release maintenance`, current gate `QDII replacement fallback 040046 evidence accepted locally`, next entry point `QDII replacement fallback candidate evidence plan gate for 019172` — all match `docs/implementation-control.md` Startup Packet |
| Latest accepted checkpoint correct | PASS | §1: `8f93dcc docs: accept qdii fallback 040046 evidence` — matches `git log` HEAD |
| Not a gate switch | PASS | §1: "This plan follows the Startup Packet next entry point. It is not a gate switch." |
| Design/control truth sources cited | PASS | §1 table lists `docs/design.md` and `docs/implementation-control.md` with correct scope qualifiers |

**Conclusion**: Follows Startup Packet, not a gate switch. PASS.

## 3. Single Candidate: 019172 / 2024, Pre-Evidence Unknown

| Check | Finding | Evidence |
|-------|---------|----------|
| Only 019172 selected | PASS | §2: "The single planned fallback evidence candidate is" `019172` / `2024` |
| Pre-evidence provenance state | PASS | §2 table: `provenance_unknown` |
| Pre-evidence quality state | PASS | §2 table: `quality_unknown` |
| Pre-evidence promotion state | PASS | §2 table: `promotion_disposition=not_promoted` |
| No implicit source-safe/promotion claim | PASS | §2: "This plan does not make 019172 source-safe, scoring-ready, baseline-ready, golden-ready, accepted as a replacement, promoted, or approved for durable corpus use." |
| Selection basis correct | PASS | §2: "accepted enumeration fallback order after 096001 and 040046 both became quality-blocked after eligible provenance" — confirmed against enumeration plan §3 and accepted evidence artifacts |
| Truth-source contradiction checked | PASS | §2: "No truth-source contradiction was found in the required sources." |

**Conclusion**: Single candidate 019172/2024, correctly pre-evidence unknown. PASS.

## 4. Preserved 096001 / 040046 Accepted States

| Check | Finding | Evidence |
|-------|---------|----------|
| 096001 state preserved | PASS | §3 table: eligible complete public fallback provenance, `quality_gate_status=block`, terminal `quality_blocked_after_provenance`, `not_promoted`, P0 `nav_benchmark_performance` + FQ4 + P1 gaps — all match accepted 096001 controller judgment |
| 040046 state preserved | PASS | §3 table: eligible complete public fallback provenance, `quality_gate_status=block`, terminal `quality_blocked_after_provenance`, `not_promoted`, FQ4 structural block with P0 pass + P1 gaps — all match accepted 040046 controller judgment |
| Not rerun or weakened | PASS | §3: "These accepted states are preserved and must not be rerun or weakened in this plan gate." |
| Blockers/residuals listed | PASS | §3 table explicitly records accepted blockers for both rows |

**Conclusion**: Both accepted states preserved correctly with provenance tuple, quality classification, terminal state, and blockers. PASS.

## 5. Generated-Output Provenance Reading (No stdout-only)

| Check | Finding | Evidence |
|-------|---------|----------|
| Explicit file-reading requirement | PASS | §6: "The future runner must read public provenance from generated output files, not from CLI stdout alone." |
| Required files named | PASS | §6 lists `summary.md` and `snapshot.jsonl` as required public files |
| Provenance tuple fields specified | PASS | §6 table: 8 fields including `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason` |
| stdout vs files discrepancy rule | PASS | §6: "If stdout and generated files disagree, the generated public files control, and the discrepancy must be recorded" |
| stdout-only in not-eligible list | PASS | §7: "stdout-only provenance interpretation without reading generated summary.md and snapshot.jsonl" listed as not eligible |

**Conclusion**: Explicitly requires generated-file provenance reading, prohibits stdout-only. PASS.

## 6. Terminal Matrix — FQ4 / Non-P0 Structural Quality Block Row

| Check | Finding | Evidence |
|-------|---------|----------|
| Explicit FQ4/non-P0 + P0 pass row | PASS | §9 terminal matrix row: "Provenance eligible + FQ4 or other non-P0 structural quality block + P0 pass → `quality_blocked_after_provenance` → `not_promoted`" |
| Rationale documented | PASS | §8: "This row is explicit because accepted 040046 evidence had P0 pass but quality blocked on FQ4; future 019172 evidence must not treat P0 pass as replacement readiness." |
| Matrix completeness | PASS | §9: 12 rows covering CLI mismatch, snapshot failure, provenance missing/incomplete/fail-closed/ineligible, score failure, quality-gate failure, P0 block (manager_strategy_text and other), FQ4/non-P0 structural block, warn, and pass |
| Row distinctness | PASS | FQ4/non-P0 row is additive, not duplicative of P0-block or provenance rows |

**Conclusion**: Terminal matrix includes the required FQ4/non-P0 structural quality block + P0 pass row. PASS.

## 7. 019172 / 017641 Same Fund-Family Prefix Risk

| Check | Finding | Evidence |
|-------|---------|----------|
| Risk flag recorded | PASS | §2 table: "this is a risk flag only, not evidence and not a blocker" |
| Not evidence or blocker | PASS | §10: "The visible fund-family prefix risk for 019172 and 017641 is only a disclosure-template risk flag. It does not prove that 019172 will fail, and it does not block the planned evidence gate." |
| Future evidence scoped to 019172 only | PASS | §10: "The future evidence gate must confirm or reject any quality concern using public generated outputs from 019172 only." |

**Conclusion**: Fund-family prefix correctly recorded as risk flag only, not evidence or blocker. PASS.

## 8. Exclusions: 017641, QDII-FOF, 013308, Bond QDII

| Check | Finding | Evidence |
|-------|---------|----------|
| 017641 excluded | PASS | §10: excluded with accepted rationale `disclosure_data_gap_not_baseline_ready` / `not_promoted` |
| QDII-FOF excluded | PASS | §10: "QDII-FOF candidates remain excluded unless a taxonomy gate accepts QDII-FOF for this replacement slot" |
| 013308 excluded | PASS | §10: pending due to QDII name vs `国内股票类` CSV category conflict; "must not silently enter evidence" |
| Bond QDII excluded | PASS | §10: "lower priority and require controller acceptance of asset-class replacement fitness" |
| No contingency overreach | PASS | §10: "This plan authorizes no contingency evidence execution." |

**Conclusion**: All four exclusion categories preserved with rationale and revisit conditions. PASS.

## 9. Unauthorized Changes — Code / Renderer / FQ0-FQ6 / Service / CLI / Host / Agent / Dayu / Golden / Baseline

| Check | Finding | Evidence |
|-------|---------|----------|
| Stop conditions cover all forbidden changes | PASS | §13: 11-item stop list covering code, tests, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden, baseline |
| Non-goals exclude all forbidden actions | PASS | §13: 14-item non-goal list covering durable-baseline, scoring-ready, golden, replacement, taxonomy conflict, QDII-FOF, bond QDII, source strategy redesign, diagnosis of prior blockers |
| Future evidence boundaries explicit | PASS | §11 requires future evidence to confirm no changes to code, tests, renderer, FQ0-FQ6, Service/CLI defaults, source strategy, taxonomy, extractor, Host/Agent/dayu, fixtures, reports promotion, design doc, or control doc |
| Preflight guard against help-as-evidence | PASS | §4: "Help output must not be treated as evidence about fund data, source provenance, extraction quality, or promotion readiness." |

**Conclusion**: No unauthorized changes authorized. PASS.

## 10. Next Action Follows Startup Packet Next Entry Point

| Check | Finding | Evidence |
|-------|---------|----------|
| Next action is correct gate | PASS | §12 review matrix: controller judgment → control-doc update → subsequent evidence gate. This follows Startup Packet: plan → review → controller judgment → evidence gate. |
| No reconciliation artifact needed | PASS | This plan gate is the Startup Packet next entry point; no deviation requiring reconciliation |

**Conclusion**: Next action follows Startup Packet. No reconciliation artifact required. PASS.

## 11. Additional Quality Checks

### 11.1 Plan Gate Validation Limited to git diff --check

| Check | Finding | Evidence |
|-------|---------|----------|
| Only git diff --check | PASS | §14: "This plan gate validation is limited to: git diff --check" |
| No other validation authorized | PASS | §14: "No other validation, evidence command, fund-analysis command, help command, code execution for extraction, or CLI probing is part of this planning worker scope." |

### 11.2 Provenance-Before-Quality Ordering

| Check | Finding | Evidence |
|-------|---------|----------|
| Ordering enforced | PASS | §7: "Source provenance must be interpreted before score, quality status, replacement usefulness, or any promotion language." |
| P0-before-provenance guard | PASS | §8: "If quality blocks P0 before provenance is eligible, do not use quality_blocked_after_provenance; classify by provenance first." |
| Fail-closed categories correct | PASS | §7 lists `schema_drift`, `identity_mismatch`, `integrity_error` |
| Eligible categories correct | PASS | §7: primary success or fallback with exactly `not_found` or `unavailable` |
| Not-eligible list comprehensive | PASS | §7: 8-item not-eligible list covering missing category, incomplete tuple, unknown fallback, internal-only, stdout-only, command-success-only |

### 11.3 Preflight Discipline

| Check | Finding | Evidence |
|-------|---------|----------|
| No help in plan gate | PASS | §13: "do not run any `fund-analysis --help` command in this planning task" |
| Flag mismatch stop | PASS | §4: if any flag changed, "stop and record `terminal_classification=cli_flag_mismatch_not_run`" |
| Help output role limited | PASS | §4: five acceptance criteria for preflight help, none authorizing inference about fund data or quality |

### 11.4 019172 Specific Concerns

| Check | Finding | Evidence |
|-------|---------|----------|
| Manager strategy text P0 handling | PASS | §8 covers both `quality_blocked_after_provenance` and `disclosure_data_gap_not_baseline_ready` paths, with explicit public-evidence requirement |
| Future evidence artifact expectations comprehensive | PASS | §11: 15-item expectation list covering identity, pre-state, preserved states, commands, provenance, quality, P0/P1, FQ4, terminal classification, scope confirmations, git diff |

## Findings

### Blocking

None.

### Material

None.

### Low

| # | Finding | Evidence | Recommended handling |
|---|---------|----------|----------------------|
| L1 | §13 `--help` prohibition for plan gate and §4 future-evidence `--help` preflight are in the same artifact; a fast reader could conflate the plan-gate prohibition with the future-evidence authorization | §13: "do not run any `fund-analysis --help` command in this planning task" vs §4 planned preflight `--help` for future evidence gate | No patch needed. The distinction between plan-gate (now) and future evidence gate (later) is explicit in §4 and §5 headers. Controller judgment can note this is correctly scoped. |
| L2 | §11 future evidence expectations line: "no code, tests, renderer, FQ0-FQ6, Service/CLI defaults, source strategy, taxonomy, extractor, Host/Agent/dayu, fixtures, reports promotion, design doc, or control doc were changed" — comprehensive but long; a future reader might miss "reports promotion" buried in the list | §11 final confirmation item | Low residual. The list is complete. No patch needed. |

## Summary

The plan artifact satisfies all 10 controller criteria for 019172 evidence plan review:

1. Plan-only, no evidence run authorized
2. Follows Startup Packet next entry point, not a gate switch
3. Single candidate 019172/2024, pre-evidence provenance_unknown/quality_unknown/not_promoted
4. 096001 and 040046 accepted states preserved with correct provenance tuples, quality classifications, and blockers
5. Generated-output provenance reading required (summary.md + snapshot.jsonl), stdout-only prohibited
6. Terminal matrix includes explicit eligible-provenance + FQ4/non-P0 structural quality block + P0 pass → quality_blocked_after_provenance row
7. 019172-017641 same fund-family prefix 摩根 correctly recorded as risk flag only, not evidence or blocker
8. All four exclusions preserved: 017641, QDII-FOF, 013308, bond QDII
9. No unauthorized code/renderer/FQ0-FQ6/Service/CLI/FundDocumentRepository/source strategy/taxonomy/extractor/Host/Agent/Dayu/golden/baseline changes authorized
10. Next action follows Startup Packet next entry point; no reconciliation artifact required

Provenance-before-quality ordering is enforced. Fail-closed categories (schema_drift, identity_mismatch, integrity_error) are correctly gated. Preflight discipline is explicit. Future evidence artifact expectations are comprehensive.

Two low findings: plan-gate --help prohibition proximity to future-evidence --help preflight (no fix needed), and a long confirmation list (no fix needed).

## Verdict

**PASS** — No blocking or material findings. The plan is ready for controller judgment. The two low findings do not require patching or re-review.
