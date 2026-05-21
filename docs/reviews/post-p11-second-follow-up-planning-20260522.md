# Post-P11 Follow-up Planning（2026-05-22）

- **Previous accepted phase**: P11 control doc hygiene / recovery ergonomics
- **Current gate**: `P11-S2 accepted`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Accepted baseline**: `ba77e02`

## Current State

P11 is accepted. The control document now has a concise Startup Packet, Active Gate Ledger, Phase History Index, explicit evidence-preservation rules, unique archive anchors, and deduplicated historical summary rows.

Active residuals are now limited to:

- RR-13 duplicate `016492`, owned by user/App source.
- Local `docs/repo-audit-20260521.md`, kept excluded unless later scope explicitly accepts publication.

Neither residual should block product development.

## Candidate Backlog After P11

| Candidate | Type | Decision | Rationale |
|---|---|---|---|
| P12 ITEM_RULE deterministic compliance | Product / Capability | Recommended next phase | ITEM_RULE has manifest/evaluator/FQ5 applicability facts, but renderer/audit compliance is not yet enforced. This is the smallest product-safety improvement after P11. |
| RR-13 duplicate `016492` source reconciliation | Human data decision | Keep human-owned | Requires user/App source truth; controller must not auto-edit CSV. |
| `docs/repo-audit-20260521.md` publication | Artifact disposition | Keep excluded | It is an audit input/local draft, not an accepted project artifact. |
| LLM audit / Evidence Confirm / RepairContract | v2 architecture | Defer | Design marks these as v2; introducing LLM repair now would violate deterministic MVP boundaries. |
| Runtime / Host / Tool loop | Architecture | Defer | Design says no external Dayu runtime or tool loop; no current product need justifies a runtime phase. |

## First Principles

The design goal is a deterministic, evidence-backed fund analysis main path. P9 closed the product request/final judgment contract. P10 closed release-readiness. P11 closed controller recovery cost. The next product risk should therefore be chosen where the current deterministic contract is already partially present but not yet enforced end-to-end.

ITEM_RULE is exactly that gap:

- `fund_agent/fund/template/item_rules.py` defines conditional template segments and a deterministic evaluator.
- `fund_agent/fund/extraction_score.py` already includes ITEM_RULE decisions in FQ5 template applicability facts.
- `fund_agent/fund/README.md` still states that ITEM_RULE is not connected to renderer, audit, Service/UI/CLI, or quality gate compliance.
- Current renderer tests cover `preferred_lens` application but not ITEM_RULE output deletion/presence behavior.

The best next phase is to make ITEM_RULE compliance deterministic without expanding into v2 LLM audit.

## Recommended Phase

**Next phase: P12 ITEM_RULE deterministic compliance.**

First gate:

```text
P12-S1 ITEM_RULE renderer/audit compliance plan/review
```

## Accepted Scope For P12-S1 Planning

The plan should define a minimal implementation slice that:

- Keeps ITEM_RULE ownership in Fund Capability `fund_agent/fund/template`.
- Decides how renderer should consume ITEM_RULE decisions for conditional segments without guessing facets from prose.
- Adds deterministic checks that conditional segments are present when triggered and absent when deleted.
- Keeps FQ5 as template applicability, unless the plan justifies a narrow metadata extension; do not make FQ5 claim full report semantic correctness.
- Keeps Service/UI/CLI behavior stable unless a narrow contract field is required and reviewed.
- Adds focused tests for active/index/enhanced fund behavior and non-triggered segment deletion.
- Updates Fund README and tests README only where current behavior changes.

## Non-goals

- Do not introduce LLM audit, Evidence Confirm, RepairContract, prompt scene runtime, Host, Engine, or tool loop.
- Do not infer fine-grained style facets from report text or fund names.
- Do not change product CLI arguments or final judgment policy.
- Do not alter annual-report source fallback, FundDocumentRepository boundaries, or quality gate block semantics.
- Do not auto-resolve RR-13 duplicate `016492`.
- Do not publish or modify `docs/repo-audit-20260521.md`.

## Residual Risks And Owners

| Risk | Owner / Destination | Status |
|---|---|---|
| RR-13 duplicate `016492` | User / App source | Human-owned, non-blocking |
| `docs/repo-audit-20260521.md` | Controller / user | Excluded local artifact |
| ITEM_RULE semantic completeness beyond deterministic segments | Future v2 audit | Deferred |
| Fine-grained active style facets | Future design slice | Deferred unless source data contract exists |

## Controller Decision

Proceed to `P12-S1 ITEM_RULE renderer/audit compliance plan/review`.

This is a planning gate. Implementation must not begin until the plan is reviewed and accepted.

## Next Entry Point

```text
P12-S1 ITEM_RULE renderer/audit compliance plan/review
```
