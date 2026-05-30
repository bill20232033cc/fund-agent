# Baseline Coverage Recovery Decision Plan

> Date: 2026-05-27
> Worker: AgentCodex planning worker
> Gate: `baseline coverage recovery decision gate`
> Scope: plan artifact only. No evidence run, no implementation, no commit, no push, no PR.
> Output path: `docs/reviews/release-maintenance-baseline-coverage-recovery-decision-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Phase | `release maintenance` |
| Current gate | `baseline coverage recovery decision gate` |
| Latest accepted checkpoint | `5812a1e` |
| Design truth | `docs/design.md` current design sections only |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger |
| Evidence chain | `docs/reviews/` accepted artifacts and `docs/archive/` only as supporting evidence |
| Current architecture | `UI -> Service -> Host -> Agent`; current deterministic path remains UI -> Service -> `fund_agent/fund` |
| Next entry point from control doc | decide the next smallest safe gate after bond-lens score applicability |

Allowed in this planning gate:

- Create this one tracked plan artifact.
- Read truth sources and accepted artifacts.
- Run only read-only / formatting validation commands, including `git diff --check`.
- Decide the next gate, entry criteria, allowed files, commands, stop conditions, and review matrix.

Forbidden in this planning gate:

- No evidence run, broad corpus collection, implementation, commit, push, PR, GitHub mutation, or control/design doc update.
- No renderer, FQ0-FQ6 policy, Service, CLI, Host, Agent, Dayu, source strategy, source helper, extractor, golden fixture, or baseline fixture changes.
- No direct PDF/cache reads; no bypass of `FundDocumentRepository`.
- No treating QDII-FOF as pure FOF without a taxonomy gate.
- No treating `baseline_blocking=true` as ignorable.

Verifier matrix for this artifact:

| Check | Command | Expected |
|---|---|---|
| Artifact exists | `test -f docs/reviews/release-maintenance-baseline-coverage-recovery-decision-plan-20260527.md` | pass |
| Whitespace | `git diff --check` | pass |
| Scope check | `git diff -- docs/reviews/release-maintenance-baseline-coverage-recovery-decision-plan-20260527.md` | only this new artifact should be relevant to this task |

## 2. Current Coverage Recap

Accepted baseline evidence now says:

| Candidate | Current state | Gate implication |
|---|---|---|
| `004393` / 2024 active | quality gate `warn`; clean evaluated row, not durable baseline | useful evaluation evidence, not enough alone for golden |
| `004194` / 2024 enhanced index | quality gate `warn`; correctness covered in current strict golden rows | useful evaluation evidence, not enough alone for golden |
| `006597` / 2024 bond | after bond-lens score applicability, quality gate is `warn`, not `pass` | still not golden-eligible because replacement bond risk issue remains baseline-blocking |
| `110020` / 2024 index | fallback-blocked; upstream failure category unknown | cannot enter clean denominator until source failure is recovered or row replaced |
| `017641` / 2024 QDII | fallback-blocked; upstream failure category unknown | cannot enter clean denominator until source failure is recovered or row replaced |
| `007721` / 2024 FOF attempt | QDII-FOF / type-gap evidence, not pure FOF coverage | remains `data_gap` / taxonomy residual |
| `017970` / 2024 FOF attempt | QDII-FOF / type-gap plus fallback-blocked | double blocker: taxonomy and source fallback |
| `004393` / 2025 probe | probe-only; year-scoped golden non-coverage | not baseline/golden material |

`006597` specific residuals:

- `holdings_snapshot` equity-shaped denominator problem is resolved for exact `bond_fund` by excluding that field only when paired with explicit `bond_risk_evidence.v1`.
- `bond_risk_evidence_missing` is projected as warn-level `FQ2F` and carries `baseline_blocking=true`.
- `holder_structure`, `share_change`, and `turnover_rate` remain missing / unresolved residuals.
- `share_change` implementation improved deterministic cases but real `006597` still lacks a unique public same-source class selection and remains missing.
- `holder_structure` and `turnover_rate` remain `needs_more_evidence`, not implementation-ready root causes.

First-principles implication: `warn` is not the same as baseline readiness. A quality gate `warn` can allow product output, but a candidate with explicit baseline-blocking evidence debt should not become durable baseline or golden material until the baseline/golden consumer contract says how that debt is handled.

## 3. Candidate Next Gates

### 3.1 Index/QDII Source Recovery / Replacement

Goal: recover the upstream failure category for `110020` and `017641`, or replace them with repository-verified clean index/QDII candidates.

Benefits:

- Directly attacks coverage blockers for two missing fund-type slots.
- Aligns with source fallback design: fallback is safe only for `not_found` / `unavailable`; `schema_drift`, `identity_mismatch`, and `integrity_error` fail closed.
- Helps reach the representative 5-10 candidate target without pretending current fallback rows are safe.

Risks:

- If implemented as an ad hoc source-helper inspection, it would violate the repository boundary.
- Replacement search can become unbounded if not supplied with approved candidates and stop conditions.

Fit as next gate: high. It is the smallest gate that improves corpus representativeness while preserving fail-closed source semantics.

### 3.2 Pure FOF Candidate Recovery / Taxonomy Decision

Goal: either find a pure `fof_fund` candidate through repository-verified evidence, or open a taxonomy decision for QDII-FOF precedence.

Benefits:

- Closes the most visible fund-type coverage gap.
- Prevents the false-positive coverage error of counting QDII-FOF as pure FOF.

Risks:

- Current known attempts are QDII-FOF/type-gap rows; taxonomy work can expand into fund-type precedence design and tests.
- If mixed with source recovery, the gate may blur two independent root causes: type classification and source eligibility.

Fit as next gate: medium. Important, but less minimal than source recovery unless controller supplies a pure FOF candidate list or explicitly chooses taxonomy as the next decision.

### 3.3 Bond Positive-Risk Evidence Design

Goal: define positive `bond_risk_evidence.v1` facts, allowed N/A reasons, extraction/projection inputs, score behavior, and baseline/golden consumer behavior.

Benefits:

- Directly addresses `006597` `bond_risk_evidence_missing.baseline_blocking=true`.
- Prevents a false pass where equity-shaped evidence is merely suppressed without a bond-specific replacement.
- Aligns with `bond_fund` preferred lens: credit risk, duration, leverage/liquidity, drawdown, redemption pressure, convertible/equity exposure.

Risks:

- It is a design gate with likely follow-up implementation; it does not improve index/QDII/FOF coverage.
- If it attempts extraction before evidence contract review, it may turn missing public output into unsupported rules.

Fit as next gate: high as a targeted design gate, but it improves one already-covered bond slot rather than the broader corpus coverage deficit.

### 3.4 `006597` Holder Structure / Turnover Rate Evidence Triage

Goal: gather reviewed same-source evidence or policy proof for `holder_structure` and `turnover_rate`.

Benefits:

- Addresses residual P1 gaps on the bond row.
- Could decide whether these fields are extractor gaps, disclosure gaps, or fund-type applicability gaps.

Risks:

- Current accepted classification is `needs_more_evidence`; no implementation is authorized.
- A real evidence triage may require annual report access through repository and tracked evidence discipline, which is more than a decision-only plan.

Fit as next gate: medium-low for immediate next step. It is useful after either source coverage is improved or bond positive-risk design clarifies what makes `006597` baseline-safe.

### 3.5 Durable Baseline / Golden Preflight

Goal: check whether the current evaluated rows can enter durable baseline or golden corpus planning.

Benefits:

- Would move toward long-term scoring assets if safe.

Blockers:

- Clean coverage remains too narrow: active, enhanced index, bond only.
- Index and QDII remain fallback-blocked.
- FOF remains a data gap / taxonomy residual.
- `006597` still carries `bond_risk_evidence_missing.baseline_blocking=true`.
- `006597` also still has holder/share/turnover residuals.

Fit as next gate: rejected. Entering preflight now would convert unresolved source/type/evidence debt into fixture pressure.

## 4. Decision

Recommended next gate: `index/QDII source recovery and replacement decision gate`.

Reasoning from first principles:

- The baseline problem is currently dominated by insufficient safe coverage, not by lack of a fixture pipeline. A durable baseline needs representative, source-safe rows before it needs fixture promotion.
- `006597` is no longer hard-blocked by the equity-shaped holdings denominator, but it is still not baseline-safe. Continuing bond work first would improve one row while leaving two fund-type slots source-blocked and FOF unresolved.
- Index and QDII are core representative slots. Their blocker is crisp and governed by an existing design contract: recover fallback failure category or replace candidate; eligible failures are only `not_found` / `unavailable`.
- This gate can stay decision-sized: it can define a bounded source-recovery/replacement plan, candidate acceptance rules, and stop conditions without implementation or evidence collection in the current artifact.

Why not the other options:

- Not pure FOF first: current evidence has QDII-FOF ambiguity, so pure FOF work likely needs either new candidate discovery or taxonomy design. That is important, but less immediately bounded unless a candidate list is supplied.
- Not bond positive-risk first: necessary before `006597` can become baseline/golden material, but it does not solve the missing index/QDII coverage and should not be used to justify golden entry.
- Not holder/turnover triage first: accepted artifacts classify both as `needs_more_evidence`; without an accepted evidence path, this is more likely to overfit a single bond row than recover corpus coverage.
- Not durable baseline/golden preflight: entry conditions are false today because source, fund-type, and baseline-blocking evidence residuals remain open.

Sequencing note: index/QDII source recovery and later bond positive-risk evidence design are complementary. Together they reduce the major coverage blockers, but source recovery is first because its failure taxonomy is already governed by a stable fail-closed contract.

## 5. Next Gate Plan

Gate name: `index/QDII source recovery and replacement decision gate`.

Objective: decide a bounded, repository-safe path to either recover fallback eligibility for `110020` and `017641` or exclude/replace them before any durable baseline/golden gate.

Entry criteria:

- Startup Packet replay confirms branch, checkpoint `5812a1e`, current gate, and forbidden surfaces.
- Accepted artifacts for small baseline v1, baseline triage, share_change, and bond-lens score applicability have been read.
- This decision plan itself must complete MiMo review, GLM review, and controller judgment before the next gate can be authorized.
- The next gate must also be plan-before-evidence: it must produce its own plan artifact and pass MiMo + GLM review + controller judgment before any source recovery evidence run begins.
- The worker can use only `FundDocumentRepository`-based public/product paths in any later evidence gate.
- Candidate replacement list must be controller-supplied or derived from already accepted artifacts; no ad hoc browsing/search in implementation workers unless a later plan explicitly authorizes it.

Allowed files for the next gate:

- Planning/review artifacts under `docs/reviews/`.
- If a later accepted evidence gate is opened, tracked summary artifact under `docs/reviews/` only.
- Scratch outputs under `/tmp/...` or ignored `reports/...` paths.

Forbidden files and surfaces:

- No renderer, FQ0-FQ6 policy, Service, CLI, Host, Agent, Dayu, source strategy, source helper, extractor, `fund_type.py`, golden fixture, or baseline fixture changes.
- No `docs/design.md` or `docs/implementation-control.md` changes in the planning worker step unless controller separately authorizes bookkeeping.
- No direct PDF/cache/source-helper reads.
- No GitHub mutation.

Suggested commands for a later accepted evidence gate, not for this artifact:

| Purpose | Command shape | Constraint |
|---|---|---|
| Repository-path availability probe | `uv run fund-analysis extraction-snapshot --run-id <run-id> --fund-code <code> --report-year 2024` | only if accepted plan authorizes evidence run |
| Source scoring if snapshot exists | `uv run fund-analysis extraction-score --snapshot-path <snapshot.jsonl> --errors-path <errors.jsonl> --golden-answer-path reports/golden-answers/golden-answer.json` | summary only; no fixture promotion |
| Quality gate if score exists | `uv run fund-analysis quality-gate --score-path <score.json>` | record status and issue ids |
| Closeout | `git diff --check` | required |

Stop conditions:

- Stop if recovering the original upstream failure category requires direct source-helper, PDF, cache, or downloader access.
- Stop if failure category is `schema_drift`, `identity_mismatch`, or `integrity_error`; fail closed and do not allow Eastmoney fallback to mask it.
- Stop if the only available index/QDII evidence is fallback with unknown upstream failure category.
- Stop if replacement candidates are not controller-approved or repository-verified.
- Stop if QDII-FOF is proposed as pure FOF coverage without a taxonomy gate.
- Stop if any candidate with `baseline_blocking=true` is proposed for durable baseline/golden promotion.

Review/validation matrix:

| Review target | MiMo focus | GLM focus |
|---|---|---|
| Startup replay | exact checkpoint/scope/forbidden surfaces | consistency with control doc next entry |
| Source recovery plan | fail-closed fallback taxonomy and repository boundary | no indirect evidence or source-helper bypass |
| Replacement criteria | no ad hoc candidate promotion; explicit acceptance/exclusion states | fund-type slot correctness and reviewed identity |
| Golden exclusion | no durable fixture path; no baseline/golden promotion | `baseline_blocking=true` remains blocking |
| Commands | bounded, reproducible, scratch-only outputs | no evidence run in planning artifact |

## 6. Golden / Baseline Gate Exclusion

Do not enter `golden answer corpus v1` or durable baseline preflight until all conditions below are true:

- Index and QDII rows are either recovered with eligible upstream failure categories or replaced by repository-verified clean candidates.
- FOF is either a pure `fof_fund` repository-verified row or a taxonomy gate has explicitly accepted how QDII-FOF is counted.
- `006597` has no unresolved `baseline_blocking=true` issue, or a future baseline/golden consumer contract explicitly defines why and how that issue is excluded from baseline promotion.
- Holder/share/turnover residuals are classified with reviewed evidence or accepted policy, not inferred from missing output.
- Candidate rows have reviewed fact inputs, clean source boundaries, separated golden-covered vs year-not-covered status, and no fail-closed source issue.

If a future controller proposes durable baseline/golden preflight anyway, the preflight must first prove it is read-only, promotion-free, and cannot write fixtures. It must also prove every excluded candidate stays outside the clean denominator with an explicit reason.

## 7. MiMo / GLM Review Checklist

- Does the plan keep the current truth hierarchy: `AGENTS.md`, current `docs/design.md`, and control doc Startup Packet / Next Entry Point above historical artifacts?
- Does it avoid treating product `warn` as baseline/golden readiness?
- Does it keep `bond_risk_evidence_missing.baseline_blocking=true` blocking for baseline/golden promotion?
- Does it preserve source fallback semantics: only `not_found` / `unavailable` are fallback-eligible?
- Does it prohibit direct PDF/cache/source-helper access and require repository-safe paths?
- Does it avoid counting QDII-FOF as pure FOF coverage?
- Does it avoid changing renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, source strategy/helpers, extractors, golden, or baseline fixtures?
- Does it choose one minimal next gate and clearly explain why the other options are deferred?
- Does it define entry criteria, allowed files, commands, stop conditions, and validation?
- Does it avoid GitHub mutation and fixture promotion?

## 8. Validation For This Artifact

This artifact is planning-only. It was created after reading the requested control sections, accepted artifacts, and current design sections. No evidence run, source code, tests, README, design doc, control doc, fixture, commit, push, PR, or GitHub mutation is part of this artifact.

Closeout validation required from this worker:

- `git diff --check`
- MiMo plan review artifact.
- GLM plan review artifact.
- Controller judgment artifact.

No next gate may start from this artifact alone. The controller must explicitly accept this plan and update the control document before authorizing `index/QDII source recovery and replacement decision gate`.
