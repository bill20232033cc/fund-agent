# Plan Review: QDII Replacement Fallback 019172 Evidence Plan — AgentGLM

> Date: 2026-05-27
> Reviewer: AgentGLM
> Role: plan review only; no implementation, no commit, no push, no PR
> Review target: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-20260527.md`
> Required source context verified: Startup Packet / Current Gate / Next Entry Point from `docs/implementation-control.md`; 040046 controller judgment; 040046 evidence; candidate evidence controller judgment; candidate evidence (096001); candidate enumeration plan

## Verdict: PASS

No blocking, material, or low findings.

---

## Review Criteria

### C1: plan-only, no evidence run authorized

**PASS.**

- Section 1 scope: "plan artifact only. No evidence run."
- Section 5: "These commands are future evidence commands only. This artifact does not authorize running them in this plan gate."
- Section 13 stop conditions: "do not run evidence", "do not run fund-analysis extraction-snapshot", "do not run fund-analysis extraction-score", "do not run fund-analysis quality-gate", and five additional `fund-analysis` subcommand prohibitions.
- Section 13 also prohibits running any `--help` command in this planning task, confirming this plan gate produces zero CLI interaction.

No evidence execution, CLI invocation, or command run is authorized.

### C2: follows Startup Packet next entry point, not a gate switch

**PASS.**

- `docs/implementation-control.md` Startup Packet next entry point: `QDII replacement fallback candidate evidence plan gate for 019172; must use init-agents / tmux multi-agent flow`
- Plan Section 1 this-artifact gate: `QDII replacement fallback candidate evidence plan gate for 019172`
- Plan Section 1 explicit statement: "This plan follows the Startup Packet next entry point. It is not a gate switch."
- 040046 controller judgment accepted next entry point: `QDII replacement fallback candidate evidence plan gate for 019172`
- All three sources agree on the same gate identity.

No gate switch detected.

### C3: only plans 019172 / 2024, entering with provenance_unknown / quality_unknown / not_promoted

**PASS.**

- Plan Section 2 single candidate: `fund_code=019172`, `report_year=2024`, `摩根纳斯达克100指数(QDII)人民币A`, `海外股票类`.
- Pre-evidence state: `provenance_unknown`, `quality_unknown`, `promotion_disposition=not_promoted` — all three recorded explicitly in Section 2.
- Section 2: "This plan does not make 019172 source-safe, scoring-ready, baseline-ready, golden-ready, accepted as a replacement, promoted, or approved for durable corpus use."
- No other candidate is planned for evidence. Section 10: "This plan does not authorize later equity QDII rows, QDII-FOF rows, conflict rows, or bond QDII rows."

### C4: preserves 096001 and 040046 accepted states as source-provenance eligible but quality_gate block / not_promoted

**PASS.**

- Plan Section 3 preserved-states table:
  - `096001`: `eligible complete public fallback provenance`, `quality_gate_status=block`, `quality_blocked_after_provenance`, `promotion_disposition=not_promoted`. Records P0 `nav_benchmark_performance`, FQ4 missing-field-rate, P1 gaps.
  - `040046`: `eligible complete public fallback provenance`, `quality_gate_status=block`, `quality_blocked_after_provenance`, `promotion_disposition=not_promoted`. Records FQ4 structural block with P0 pass, P1 gaps.
- Section 3 summary: "These accepted states mean 096001 and 040046 are source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted."
- Neither prior candidate's state is rerun, weakened, or reinterpreted in this plan.

Accepted evidence artifacts cross-verified:
- 096001 evidence: `quality_blocked_after_provenance`, `not_promoted`, P0 `nav_benchmark_performance` block, FQ4 `42.9%` — matches plan Section 3.
- 040046 evidence: `quality_blocked_after_provenance`, `not_promoted`, P0 pass, FQ4 `35.7%` > `35.0%` — matches plan Section 3.

### C5: future evidence must read generated public summary.md and snapshot.jsonl, prohibits stdout-only

**PASS.**

- Plan Section 6 title: "Generated-Output Provenance Reading"
- Section 6: "The future runner must read public provenance from generated output files, not from CLI stdout alone."
- Required files: `summary.md` and `snapshot.jsonl` — both listed explicitly.
- Section 6: "If stdout and generated files disagree, the generated public files control, and the discrepancy must be recorded for controller review."
- Section 6 also lists a required public provenance tuple of 8 fields, each requiring "exact public value" recording.
- Section 11 future artifact expectations: "Public provenance tuple read from generated summary.md and snapshot.jsonl, not stdout-only."
- Section 7 stop-check exclusions: "stdout-only provenance interpretation without reading generated summary.md and snapshot.jsonl" listed as not eligible.

This directly addresses the residual from the 096001 evidence review (where the initial artifact incorrectly used stdout-only provenance).

### C6: terminal matrix includes explicit FQ4 / non-P0 structural quality block + P0 pass row

**PASS.**

- Plan Section 9 terminal-state matrix includes row:
  - Condition: "Provenance eligible + FQ4 or other non-P0 structural quality block + P0 pass"
  - Terminal classification: `quality_blocked_after_provenance`
  - Promotion disposition: `not_promoted`
  - Required next action: "Record FQ4/non-P0 rule, threshold/evidence basis, and P0 pass; do not promote."
- Section 8 FQ4/non-P0 handling: "If source provenance is eligible, P0 passes, and quality blocks on FQ4 missing-field-rate or another non-P0 structural quality rule, classify as quality_blocked_after_provenance." With explicit rationale: "This row is explicit because accepted 040046 evidence had P0 pass but quality blocked on FQ4."

This directly addresses the residual from the 040046 controller judgment: "Terminal matrix lacks explicit FQ4 / non-P0 quality block row" — now resolved.

### C7: 019172 / 017641 same visible fund-family prefix 摩根 is only a risk flag

**PASS.**

- Plan Section 2 disclosure-template risk flag: "019172 and excluded 017641 share visible fund-family prefix 摩根; this is a risk flag only, not evidence and not a blocker"
- Plan Section 10: "The visible fund-family prefix risk for 019172 and 017641 is only a disclosure-template risk flag. It does not prove that 019172 will fail, and it does not block the planned evidence gate. The future evidence gate must confirm or reject any quality concern using public generated outputs from 019172 only."
- The risk flag is not used as evidence, not used as a blocker, and not used to pre-judge provenance or quality. The enumeration plan confirms candidate_order=3 with the same risk-flag framing.

### C8: exclusions complete — 017641, QDII-FOF, 013308, bond QDII

**PASS.**

Plan Section 10 preserved exclusions:

- **017641**: excluded because accepted evidence classified it as `disclosure_data_gap_not_baseline_ready` / `not_promoted`. Matches enumeration plan exclusion and accepted controller judgment.
- **QDII-FOF**: excluded unless a taxonomy gate accepts QDII-FOF for this replacement slot. Specifically excludes `007721` and `017970` per enumeration plan.
- **013308**: pending because QDII name conflicts with CSV category `国内股票类`; must not silently enter evidence before taxonomy/controller resolution. Matches enumeration plan `naming_category_conflict` flag.
- **Bond QDII**: lower priority and requires controller acceptance of asset-class replacement fitness before evidence. Matches enumeration plan treatment of `007360` and `100050`.

All four exclusion categories match the enumeration plan, accepted controller judgments, and accepted evidence states.

### C9: no unauthorized scope — code/test/renderer/FQ0-FQ6/Service/CLI/FundDocumentRepository/source strategy/taxonomy/extractor/Host/Agent/Dayu/golden/baseline

**PASS.**

- Plan Section 13 stop conditions: "do not edit docs/implementation-control.md, docs/design.md, code, tests, README, fixtures, reports, or generated ignored outputs"
- Plan Section 13: "do not change renderer, FQ0-FQ6, Service, CLI, default behavior, FundDocumentRepository, source strategy, source-helper fallback semantics, taxonomy, extractor, Host, Agent, dayu, golden files, baseline fixtures, or corpus state"
- Plan Section 13: "do not commit, push, open PR, merge, delete branch, or mutate GitHub state"
- Plan Section 14 non-goals: explicit list of all unauthorized changes including code, tests, README, design, control, renderer, FQ0-FQ6, Service, CLI, FundDocumentRepository, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden, baseline.
- Section 8 false-positive handling: "False-positive suspicion does not authorize code, extractor, taxonomy, source strategy, renderer, FQ0-FQ6, or quality-gate changes in this evidence path."

No authorization leakage detected.

### C10: plan gate validation limited to git diff --check

**PASS.**

- Plan Section 14: "This plan gate validation is limited to: git diff --check"
- Section 14: "No other validation, evidence command, fund-analysis command, help command, PDF/cache inspection, external web access, code execution for extraction, or CLI probing is part of this planning worker scope."

---

## Residual Notes

No residuals or open items require controller attention beyond the standard review/judgment flow already specified in plan Section 12.

The plan correctly addresses the residual from the 040046 controller judgment (explicit FQ4 terminal matrix row) and carries forward all accepted constraints without weakening prior candidate states.
