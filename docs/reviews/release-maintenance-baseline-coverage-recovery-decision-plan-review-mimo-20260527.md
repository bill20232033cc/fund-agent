# Plan Review: Baseline Coverage Recovery Decision Plan

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-baseline-coverage-recovery-decision-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Truth Sources Consulted

- `AGENTS.md` — 硬约束、模块边界、fallback 策略、禁止事项
- `docs/design.md` (v2.2) — 当前设计章节、来源失败分类、§5.4.3 覆盖矩阵、§12 Plan Review 边界检查
- `docs/implementation-control.md` — Startup Packet、Current Gate、Next Entry Point、Open Residuals、Active Gate Ledger
- bond-lens score applicability implementation controller judgment (`02741e0`)
- baseline coverage / source recovery / taxonomy + bond triage evidence controller judgment

## Review Findings

### F1 [Informational] — §5 allowed commands scope needs precision

Plan §5 "Suggested commands" table lists `extraction-snapshot` as a later evidence-gate command. While the plan correctly scopes this to "only if accepted plan authorizes evidence run," the `extraction-snapshot` command internally calls `FundDataExtractor.extract()` which invokes `FundDocumentRepository` and potentially downloads PDFs. This is not a violation because the plan explicitly gates it behind authorization, but a future implementation worker should be reminded that `extraction-snapshot` is not a lightweight read-only probe — it triggers real repository access and caching.

**Disposition**: Informational. The plan's "only if accepted plan" qualifier is sufficient. No plan change required.

### F2 [Informational] — §6 golden/golden exclusion condition 4 could be sharper

§6 condition 4 states: "Holder/share/turnover residuals are classified with reviewed evidence or accepted policy, not inferred from missing output." This is correct but slightly broad. The accepted triage evidence already classified `share_change` as `extractor_gap` (implementation completed, real 006597 still missing) and `holdings_snapshot` as `bond_lens_contract_gap` (implementation completed). Only `turnover_rate` and `holder_structure` remain `needs_more_evidence`. The condition as written is safe, but a future golden gate reviewer might benefit from noting that some residuals already have accepted classifications and implementation attempts.

**Disposition**: Informational. The condition's conservative wording is correct for a decision plan. No change required.

### F3 [Informational] — §4 Decision could more explicitly state 006597 non-blocking status

The decision §4 says "006597 is no longer hard-blocked by the equity-shaped holdings denominator, but it is still not baseline-safe." This is correct per the accepted bond-lens implementation evidence (006597 gate status is `warn`, not `block`; `baseline_blocking=true` emitted). However, the plan does not explicitly note that 006597's quality gate status moved from `block` to `warn` — which is a meaningful state change. The §2 recap table (line 53) says "quality gate is `warn`, not `pass`" which is accurate, but a reader might not realize this was previously `block`.

**Disposition**: Informational. The §2 recap is factually correct. No change required.

## Checklist Results

| Check | Result | Notes |
|---|---|---|
| Truth hierarchy respected | PASS | Plan reads AGENTS.md, design.md, control doc as primary truth; accepted artifacts as supporting evidence |
| 006597 warn != baseline-ready | PASS | §2 line 68 explicitly states "warn is not the same as baseline readiness" |
| `baseline_blocking=true` preserved | PASS | §5 stop condition 6 and §6 golden exclusion prevent promotion |
| Source fallback fail-closed | PASS | §5 stop conditions correctly limit eligible to `not_found`/`unavailable` |
| FundDocumentRepository boundary | PASS | §1 forbidden and §5 stop condition 1 prohibit direct PDF/cache/source-helper |
| QDII-FOF != pure FOF | PASS | §3.2 and §5 stop condition 5 require taxonomy gate |
| No renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu changes | PASS | §1 forbidden section and §5 forbidden files are explicit |
| One minimal next gate chosen | PASS | §4 selects index/QDII source recovery with clear reasoning |
| Other options deferred with evidence | PASS | §4 "why not" section provides direct evidence for each deferral |
| Entry criteria specific | PASS | §5 entry criteria are concrete and verifiable |
| Allowed files specific | PASS | §5 allowed files are bounded |
| Stop conditions specific | PASS | §5 stop conditions cover all critical failure modes |
| No GitHub mutation | PASS | §1 scope declaration |
| §12 design.md boundary checks respected | PASS | No four-layer, pyproject, Host/Agent, or license violations |

## Verdict

**PASS_WITH_FINDINGS**

All three findings are informational. The plan correctly selects index/QDII source recovery as the next smallest safe gate. It does not treat 006597 `warn` as baseline-ready, preserves `baseline_blocking=true`, respects source fallback fail-closed semantics, maintains FundDocumentRepository boundaries, and does not count QDII-FOF as pure FOF. Entry criteria, allowed files, commands, and stop conditions are sufficiently specific for a decision gate. The deferral reasoning for pure FOF, bond positive-risk evidence, holder/turnover triage, and durable baseline preflight is evidence-based.

No re-review required.
