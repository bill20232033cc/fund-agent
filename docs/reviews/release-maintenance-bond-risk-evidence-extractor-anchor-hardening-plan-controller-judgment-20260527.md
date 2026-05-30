# Bond Risk Evidence Extractor / Anchor Hardening Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Decision: **ACCEPTED LOCALLY FOR IMPLEMENTATION**

## Step Self-Check

- Current gate / role: plan acceptance; controller role only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, repo review `docs/reviews/repo-review-20260527-225303.md`, accepted bond positive-risk evidence artifact and controller judgment, updated plan, two plan reviews, plan fix, and targeted re-review.
- Scope boundary: accept plan artifacts only; no code/test implementation, no golden promotion, no QDII/FOF/110020/release-readiness/Host/Agent/dayu/PR/push/merge work.
- Stop conditions: no blocking open question; dirty scope is understood as pre-existing untracked review/memory files plus this gate's new plan artifacts.
- Evidence and validation: plan review loop completed; `git diff --check` passed before judgment.
- Next action: create accepted plan local commit with only this gate's plan/review/fix/judgment artifacts staged, then enter implementation gate.

## Preflight State

| Item | State |
|---|---|
| Branch | `codex/local-reconciliation` |
| Baseline before this plan gate | latest local HEAD before plan artifacts: `e0b2892 docs: accept bond positive risk evidence` |
| Worktree scope | existing untracked `--help`, repo/comprehensive review artifacts, `docs/tmux-agent-memory-store.md`; plus this gate's new plan artifacts |
| Protected branch status | not protected trunk |

## Accepted Plan Artifact

Accepted plan:

- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`

Plan status after fix/re-review: handoff-ready and code-generation-ready.

Core accepted implementation direction:

- Add explicit positive `bond_risk_evidence.v1` records in the Fund Agent-layer capability, not in UI/Service/Host.
- Keep production annual-report access through `FundDocumentRepository`; extractor consumes already loaded `ParsedAnnualReport`.
- Add stable group-level anchors with deterministic ids and row-level table locators where required.
- Preserve evidence-strength distinctions: qualitative drawdown-control and leverage-strategy text remain weak unless accepted metric/table/proxy evidence exists.
- Update score applicability so `bond_risk_evidence_missing.baseline_blocking=true` stops only when the positive contract is actually satisfied; partial evidence emits dynamic missing groups while `required_evidence_groups` remains the seven-group contract.
- Do not weaken FQ0-FQ6, do not promote golden corpus, and do not touch QDII/FOF/110020/release readiness/Host/Agent/dayu/PR/push/merge.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-mimo-20260527.md` | `PASS` |
| AgentDS | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentDS targeted re-review | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-rereview-ds-20260527.md` | all findings `已修复` |

## Finding Judgment

| Finding | Controller judgment | Fix / re-review status |
|---|---|---|
| DS 01: `bond_risk_evidence` field priority not registered | **accepted** | Fixed in plan: `bond_risk_evidence` is P1; coverage is `contract_status != "missing"`; traceability requires at least one stable group-level annual-report anchor; re-review `已修复`. |
| DS 02: non-bond extraction boundary underspecified | **accepted** | Fixed in plan: extractor receives explicit `classified_fund_type`; non-bond/unknown returns missing/not-applicable without scanning seven groups; no `extra_payload`; re-review `已修复`. |
| DS 03: required vs missing evidence group invariant should be explicit | **accepted** | Fixed in plan: `required_evidence_groups` always equals all seven contract groups; `missing_evidence_groups` is dynamic unsatisfied subset; re-review `已修复`. |
| MiMo residual: snapshot schema extension decision | **accepted as implementation watch item** | Covered by plan Slice 4 stop condition and additive-field preference; controller must stop if implementation cannot avoid prose parsing or public-contract ambiguity. |
| MiMo residual: real `006597` drawdown/leverage may remain weak | **accepted as validation residual** | Implementation must report partial state honestly and must not claim blocker resolved unless all seven groups satisfy the accepted contract. |
| MiMo residual: new/modified module coverage target | **accepted as review target** | Full validation remains project coverage command; single-file coverage gaps must be documented if below target. |

No finding remains unclassified.

## Implementation Gate Handoff

Approved slice order from plan:

1. Model contract.
2. Extractor.
3. Bundle integration.
4. Snapshot projection.
5. Score applicability.
6. Real `006597` path.
7. Documentation.

Controller implementation handoff must assign only the next slice unless the approved plan explicitly allows combining adjacent work. Every implementation worker must produce an implementation artifact before review.

## Required Validation Before Implementation Acceptance

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- real network/PDF smoke through `FundDocumentRepository` loading `006597` / `2024`
- rerun `006597` / `2024` `extraction-snapshot`
- rerun `extraction-score`
- rerun `quality-gate`

Acceptance for the bond blocker requires current evidence, not intent:

- Score must not contain blocking `bond_risk_evidence_missing.baseline_blocking=true` only if all seven groups satisfy the accepted contract.
- Snapshot/score must expose positive `bond_risk_evidence.v1` or equivalent accepted structured contract.
- Weak evidence stays weak; qualitative drawdown/leverage text cannot become strong quantitative evidence.
- Golden corpus v1 must not be promoted in this gate.

## Artifact Disposition For Accepted Plan Commit

Stage these files only:

- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-ds-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-fix-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-rereview-ds-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-controller-judgment-20260527.md`

Do not stage:

- `--help`
- unrelated repo/comprehensive review artifacts
- `docs/tmux-agent-memory-store.md`
- generated reports or cache files

## Decision

Plan gate is accepted locally. Proceed to accepted plan commit, then implementation gate. No push, PR, merge, mark-ready, approval, or golden promotion is authorized.
