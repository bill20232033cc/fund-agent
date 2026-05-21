# Post-P8 Planning - Controller Decision - 2026-05-21

## Inputs

- design_doc: `docs/design.md`
- control_doc: `docs/implementation-control.md`
- Current code baseline: `3a03ab8 fix: clarify stage and risk chapter contracts`
- Recent accepted follow-up commits:
  - `f65c14e` removes external `dayu-agent` runtime dependency.
  - `fba8024` refreshes `uv.lock` after dependency removal.
  - `3844a96` aligns `AGENTS.md` / `CLAUDE.md` entrypoints.
  - `3a03ab8` clarifies chapter 5/6 stage-risk contract boundaries.

The untracked source audit document `docs/fund-agent_仓库级综合审核报告_2026-05-21.docx` remains excluded from version control.

## Current Gate

`P8 closed` is accepted. The next gate is `P9-S1 analyze product contract plan/review`.

## Controller Decision

Start a new post-P8 phase:

| Phase | Name | First slice |
|---|---|---|
| P9 | Analyze product contract hardening | P9-S1 analyze user-minimal-input and dev-override contract plan/review |

Based on the design goal in `docs/design.md` - helping ordinary fund investors obtain an auditable pre-buy fund checkup - the first post-P8 priority should be product contract hardening, not repo hygiene or additional aggregate review.

The current `fund-analysis analyze` path still exposes too many manual inputs and keeps `final_judgment` as an explicit input contract. That is acceptable for deterministic MVP development, but it is misaligned with the product goal if left as the primary user path. The next phase should define which facts are user-owned, which facts are extracted from public documents, and which conclusions are derived from existing checks.

## Accepted Scope For P9-S1 Planning

P9-S1 should produce a code-generation-ready plan, not implementation.

The plan must define:

- Product-mode vs developer-override-mode `analyze` contract.
- Minimal user-owned inputs that cannot be derived from fund documents, such as fund code, report year, money horizon, investment amount, max tolerable loss, and explicit valuation state until thermometer-to-valuation mapping is designed.
- System-derived facts that should not remain required user inputs where the document/extractor pipeline already owns them, such as profile, fees, manager tenure, manager ownership, holdings, share changes, NAV/benchmark, risk checks and pressure test inputs.
- Final judgment derivation policy from checklist, risk checks, quality gate and explicit user overrides.
- CLI and Service boundary changes required to support the contract without moving fund-domain logic into UI.
- Backward-compatible developer override handling only if needed for tests/smoke, clearly separated from the user success path.
- Documentation and test update plan.

## Non-Goals For P9-S1

- Do not implement the contract in P9-S1.
- Do not remove deterministic MVP behavior without a reviewed migration plan.
- Do not introduce LLM writing, external Dayu runtime, Host/Engine/tool loop, or prompt scene registry.
- Do not make thermometer-derived valuation automatic until a same-source valuation rule is designed.
- Do not bypass `FundDocumentRepository` or put explicit parameters into `extra_payload`.

## Deferred Post-P8 Items

| Item | Decision |
|---|---|
| Repo hygiene | Defer to a separate slice after product contract planning. Includes CI, `.gitignore`, LICENSE and default path cleanup. |
| Quality gate / golden coverage ROI | Defer until product contract is defined, because gate policy and proof burden depend on the user/developer mode split. |
| Full aggregate deepreview | Not required before P9 planning. Phaseflow aggregate review is required before ready-to-open-draft-PR, not before a planning slice. |

## Agent Routing

- Planning specialist: Procodex / AgentCodex first. AgentOpus is an implementation/planning alternative when appropriate.
- If Procodex / AgentCodex has network or environment issues, AgentMiMo may be used as its planning or implementation substitute for the affected slice.
- Conflict rule: if AgentMiMo acts as planning or implementation substitute on a slice, it must not serve as an independent reviewer for the same slice. Use AgentDS and AgentGLM for review in that case.
- Review / re-review: choose two independent reviewers from AgentMiMo, AgentDS and AgentGLM, subject to the conflict rule above.

## Next Gate

`P9-S1 analyze product contract plan/review`.

Controller next action:

1. Update `docs/implementation-control.md` with this planning decision.
2. Prepare or dispatch a P9-S1 planning handoff to the planning specialist.
3. After plan delivery, run two independent plan reviews and write controller judgment.
