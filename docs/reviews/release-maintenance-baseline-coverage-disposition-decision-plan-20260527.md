# Release Maintenance: Baseline Coverage Disposition Decision Plan

> Worker: AgentCodex planning worker, not controller
> Date: 2026-05-27
> Gate: `baseline coverage disposition decision gate`
> Scope: plan artifact only; no new evidence, no implementation, no promotion, no `docs/implementation-control.md` update

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `017641 manager_strategy_text public evidence triage accepted locally` |
| Current requested gate | `baseline coverage disposition decision gate` |
| Next entry point | `baseline coverage disposition decision gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint | `71f1aa4 docs: accept 017641 public evidence triage` |
| Current truth sources replayed | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; current accepted artifacts |
| Current architecture guardrail | Dayu four-layer target `UI -> Service -> Host -> Agent`; current deterministic production path remains UI -> Service -> `fund_agent/fund` Agent-layer fund capability |

This gate is a decision/planning gate. It reconciles already accepted public evidence for baseline/golden readiness and chooses the next cursor. It must not run new evidence, change code, promote fixtures, mutate GitHub state, or enter the next gate.

## 2. Accepted Evidence Reconciliation

| Coverage slot | Accepted evidence state | Baseline/golden disposition |
|---|---|---|
| `110020` / 2024 / `index_fund` | Reviewed coverage candidate input accepted. Public provenance is complete eligible fallback after primary `unavailable`: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`. Quality gate is `warn`. Terminal state is `reviewed_coverage_candidate_input_accepted`; `promotion_disposition=not_promoted`. | Not baseline/golden ready. Methodology / constituents evidence remains insufficient; `turnover_rate` P1 warning remains; strict golden is absent; reviewed fact freeze is still a residual. |
| `017641` / 2024 / `qdii_fund` | Complete eligible fallback after primary `unavailable`. Public evidence confirms `manager_strategy_text` remains missing with no value, no anchor, and no locator. Quality gate is `block` on P0 `manager_strategy_text`; terminal state is `disclosure_data_gap_not_baseline_ready`; `promotion_disposition=not_promoted`. | Excluded from baseline/golden readiness. This is not an authorized extractor fix or policy change; later work must either replace/exclude this row or open a separate same-source evidence / implementation path. |
| `006597` / 2024 / `bond_fund` | Bond-lens applicability improved: equity-shaped `holdings_snapshot` no longer creates a stock-holdings denominator block for exact `bond_fund` when paired with explicit `bond_risk_evidence.v1` replacement issue output. Quality moved to `warn`, not `pass`. | Not golden ready. `bond_risk_evidence_missing.baseline_blocking=true` remains, and residual P1 gaps such as `holder_structure`, `share_change`, and `turnover_rate` remain. Positive bond-risk evidence is still absent. |
| FOF slot | Prior FOF attempts remain `data_gap` / `taxonomy_pending`. Current QDII-FOF candidates cannot be counted as pure `fof_fund` coverage without an accepted taxonomy decision or a repository-safe pure FOF candidate. | Not covered. FOF remains a representative coverage blocker before durable baseline/golden corpus entry. |

Reconciled blocker set:

- Source/fallback safety for `110020` is no longer the primary blocker, but reviewed baseline suitability is still incomplete.
- QDII coverage through `017641` is blocked by public P0 disclosure / quality evidence.
- Bond coverage through `006597` is observable but baseline-blocked until positive bond-risk evidence or an accepted residual disposition exists.
- Pure FOF representative coverage is absent.
- No sample may be promoted from this gate; all relevant rows remain `not_promoted`.

## 3. Candidate Next Cursor Options

### Option A: Replacement / Exclusion Candidate Selection Gate For QDII / Index / FOF Coverage

Purpose: decide which currently blocked or incomplete representative slots should be replaced, excluded from the first durable baseline scope, or carried as reviewed-but-not-promoted candidates.

Entry conditions:

- Startup Packet and accepted artifacts are replayed without running new evidence.
- Candidate universe is limited to already accepted evidence unless the next controller explicitly opens a later evidence gate.
- `110020` enters only as reviewed index candidate input with residuals.
- `017641` enters only as QDII `disclosure_data_gap_not_baseline_ready`.
- FOF enters as `data_gap` / `taxonomy_pending`, not fulfilled coverage.

Stop conditions:

- Any attempt to promote `110020`, `017641`, FOF attempts, or local outputs to durable baseline, fixture, clean denominator, report-quality corpus, or golden corpus.
- Any direct PDF/cache/source-helper/FundDocumentRepository source-strategy access.
- Any plan that tries to fix extractor behavior, weaken FQ0-FQ6, change fund-type taxonomy, or change Service/CLI/renderer behavior.
- Any candidate inclusion without explicit blocker disposition and review owner.

Expected output:

- A controller-reviewable candidate disposition matrix: `include_for_later_review`, `replace`, `exclude_from_v1`, `needs_taxonomy_gate`, or `needs_evidence_gate`.
- Explicit target for each uncovered slot before golden corpus v1 can be reconsidered.

### Option B: FOF Taxonomy / Pure FOF Candidate Gate

Purpose: resolve whether the baseline should require a pure FOF candidate now, and if so how to select one without counting QDII-FOF rows as pure FOF.

Entry conditions:

- Controller chooses FOF absence as the dominant next blocker.
- Either an approved pure FOF candidate list exists for a later evidence gate, or the work is explicitly taxonomy/design-only.
- Current `docs/design.md` fund-type priority and `fof_fund` lens remain the truth source.

Stop conditions:

- Counting `007721`, `017970`, or any QDII-FOF row as pure FOF solely from existing evidence.
- Changing `fund_type.py` or taxonomy behavior without a separate accepted design/implementation gate.
- Promoting any FOF candidate or generated output.

Expected output:

- A pure FOF entry contract or an explicit `FOF deferred from golden v1` decision with owner and revisit condition.

### Option C: Bond Positive-Risk Evidence Gate

Purpose: resolve `006597` bond baseline blocking by designing or collecting positive bond-risk evidence rather than only excluding equity-shaped holdings.

Entry conditions:

- Accepted bond-lens implementation state is used as the starting point: quality `warn`, explicit `bond_risk_evidence_missing`, and `baseline_blocking=true`.
- The next gate is plan/review first and separates positive evidence requirements from score-applicability behavior.
- Future evidence, if authorized later, must use public paths and same-source logic.

Stop conditions:

- Treating `bond_risk_evidence_missing` as a harmless N/A.
- Entering golden/baseline while `baseline_blocking=true` persists.
- Improving `006597` only by suppressing evidence requirements or weakening quality thresholds.

Expected output:

- A positive bond-risk evidence contract or accepted exclusion/deferral decision for bond golden readiness.

### Option D: Durable Baseline Fixture Gate Or Golden Corpus v1

Purpose: eventually promote reviewed representative samples into durable baseline fixtures or golden corpus v1.

Entry conditions:

- Only enter if prerequisites are truly met: source-safe provenance, reviewed fact freeze, representative fund-type coverage, no unresolved quality block, no baseline-blocking replacement issue, explicit fixture/golden promotion plan, and two independent plan reviews.
- Current accepted evidence does not satisfy these conditions.

Stop conditions:

- Any remaining coverage/source/quality/fund-type/fixture-promotion blocker.
- Any attempt to use local scratch outputs or `not_promoted` rows as durable fixtures.

Expected output:

- Deferred. This option is explicitly non-entry for the current cursor.

### Option E: Data Extraction Priority Fixes

Purpose: implement or plan extractor fixes only when same-source evidence proves the failure is an extractor gap rather than disclosure absence, policy gap, taxonomy gap, or baseline fixture gap.

Entry conditions:

- Same-source evidence directly proves an extractor gap.
- A later implementation plan/review gate defines exact files, tests, fixture policy, quality impact, and stop conditions.
- The work remains inside `fund_agent/fund` Agent-layer fund capability boundaries unless a separate architecture gate authorizes otherwise.

Stop conditions:

- Inferring root cause from indirect quality status alone.
- Implementing extraction fixes in this plan-only gate.
- Touching source strategy, fallback semantics, Service/CLI, renderer, FQ0-FQ6, Host/Agent/dayu, or baseline/golden fixtures.

Expected output:

- Deferred unless a prior accepted evidence artifact proves a same-source extractor gap. For this gate, no new extraction fix is authorized.

## 4. Controller Recommendation

Choose exactly one next cursor:

`replacement/exclusion candidate selection gate for QDII/index/FOF coverage`

First-principles justification:

- The goal before any golden corpus work is not to maximize the number of probed rows; it is to establish a source-safe, fund-type-representative, quality-acceptable candidate set with explicit residual ownership.
- The dominant unresolved problem is now disposition, not evidence generation. `110020` is eligible only as reviewed index candidate input, `017641` is QDII data-gap / quality-blocked, FOF is absent, and `006597` is bond baseline-blocked. Entering a focused disposition gate prevents repeated probing of rows that already have accepted terminal states.
- This cursor preserves fail-closed source semantics and avoids overfitting implementation work to unsuitable baseline candidates. It lets the controller choose replacement, exclusion, or deferral before spending more effort on extractor or fixture work.
- It is narrower and safer than golden corpus v1, because it explicitly forbids promotion. It is broader than a single FOF or bond gate, because it first decides whether the baseline target should replace or exclude blocked QDII/index/FOF slots and how those decisions affect the overall readiness matrix.

The recommended gate should produce a durable decision matrix, not new evidence. After that matrix is reviewed and accepted, the controller can open one of the narrower follow-up gates: pure FOF candidate evidence, QDII replacement evidence, index reviewed-fact freeze, or bond positive-risk evidence.

## 5. Explicit Non-Entry

Do not enter `golden answer corpus v1` while any of these blockers remain:

- Coverage is not source-safe and representative across required fund-type slots.
- `017641` has a P0 `manager_strategy_text` quality block and terminal `disclosure_data_gap_not_baseline_ready`.
- Pure FOF remains `data_gap` / taxonomy residual.
- `006597` has `bond_risk_evidence_missing.baseline_blocking=true` and other residuals.
- `110020` lacks methodology / constituents sufficiency, strict golden coverage, and reviewed fact freeze.
- Durable fixture promotion has not been accepted by a separate plan/review/controller judgment.

## 6. Explicit Prohibition

This gate forbids:

- Code changes.
- Renderer work.
- FQ0-FQ6 changes.
- Service/CLI changes.
- FundDocumentRepository/source strategy/source-helper/PDF/cache direct access.
- Host/Agent/dayu work.
- Baseline, golden, clean-denominator, report-quality corpus, or fixture promotion.
- New evidence runs.
- GitHub mutation, push, PR, merge, branch deletion, or commit.
- Editing `docs/implementation-control.md`.

## 7. Review Matrix

The controller should use `$init-agents` / tmux flow before assigning reviews. Per `init-agents`, review / re-review work should go to two independent review agents from `AgentMiMo`, `AgentDS`, and `AgentGLM`; discover pane ids immediately before sending and clear only for a new assigned task.

| Review track | Reviewer | Required focus | Expected artifact |
|---|---|---|---|
| Independent plan review 1 | `AgentMiMo` | Check Startup Packet replay, accepted evidence reconciliation, no-promotion discipline, stop conditions, and whether the recommended cursor follows from accepted evidence. | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-review-mimo-20260527.md` |
| Independent plan review 2 | `AgentGLM` or `AgentDS` | Challenge first-principles cursor choice, missing blockers, fund-type/taxonomy logic, fail-closed source semantics, and golden non-entry. | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-review-glm-20260527.md` or DS equivalent |
| Controller judgment | Controller | Accept, reject, or require patch/re-review; select next entry point; record residual owners; update control doc only after review acceptance if authorized by controller role. | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-controller-judgment-20260527.md` |

Controller judgment should explicitly answer:

- Does the plan accurately carry forward `110020`, `017641`, `006597`, and FOF accepted states?
- Is `replacement/exclusion candidate selection gate for QDII/index/FOF coverage` the single best next cursor?
- Are durable baseline / golden corpus v1 entry conditions still unmet?
- Are all implementation, source, fixture, GitHub, and control-doc mutations prohibited for this gate?

## 8. Validation For This Plan-Only Gate

Required validation:

```bash
git diff --check
```

No tests, CLI evidence runs, renderer checks, source probing, or GitHub checks are required because this gate is plan-only and code changes are forbidden.

Validation result to be filled by the worker after writing this artifact:

| Command | Exit code | Result |
|---|---:|---|
| `git diff --check` | `0` | passed |
