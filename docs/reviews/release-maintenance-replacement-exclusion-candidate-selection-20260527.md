# Release Maintenance: Replacement / Exclusion Candidate Selection Decision

> Worker: AgentCodex decision worker, not controller
> Date: 2026-05-27
> Gate: `replacement/exclusion candidate selection gate for QDII/index/FOF coverage`
> Scope: decision artifact only; accepted evidence only; no new evidence, implementation, promotion, control-doc update, GitHub mutation, or next-gate entry

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `baseline coverage disposition decision plan accepted locally` |
| Startup Packet next entry point | `replacement/exclusion candidate selection gate for QDII/index/FOF coverage; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `replacement/exclusion candidate selection gate for QDII/index/FOF coverage` |
| Latest accepted checkpoint | `b919e5e docs: accept baseline coverage disposition plan` |
| Truth sources replayed | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Next Entry Point; accepted plan and review artifacts |
| Accepted plan | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-controller-judgment-20260527.md` |

This is the Startup Packet next entry point, not a gate switch. This worker is producing the requested candidate disposition decision artifact only. The controller remains responsible for accepting, recording, or opening any later gate.

## 2. Allowed Disposition Values

This artifact uses only the accepted values from the previous controller judgment:

| Value | Meaning in this artifact |
|---|---|
| `include_for_later_review` | Keep the candidate as reviewed input for a later gate, without promotion. |
| `replace` | Current candidate is not suitable for v1 coverage; find or approve a replacement through a later evidence gate. |
| `exclude_from_v1` | Exclude the slot from v1 scope only if the controller accepts that reduced scope. |
| `needs_taxonomy_gate` | Slot cannot be resolved until fund-type / taxonomy precedence is decided. |
| `needs_evidence_gate` | Slot cannot be resolved until a later accepted evidence gate produces direct accepted evidence. |

No additional disposition value is introduced.

## 3. Candidate Disposition Matrix

| Slot / candidate | Current state | Accepted evidence | Disposition | Owner | Revisit condition | Why not promote |
|---|---|---|---|---|---|---|
| Index slot / `110020` / 2024 | `reviewed_coverage_candidate_input_accepted`; `index_fund`; quality `warn`; `promotion_disposition=not_promoted` | Complete eligible fallback after primary `unavailable`: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`. Residuals remain: methodology / constituents sufficiency, `turnover_rate` P1 warning, strict golden absence, reviewed fact freeze. | `include_for_later_review` | Controller to assign future index reviewed-fact / index-evidence reviewer before any fixture or golden step. | Revisit only after an accepted index reviewed fact freeze / evidence sufficiency gate proves methodology, constituents, and reviewed fact identity are adequate, and strict golden absence is dispositioned. | Accepted evidence explicitly says not baseline/golden ready; quality is only `warn`, strict golden is absent, and reviewed fact freeze remains unresolved. |
| QDII slot / `017641` / 2024 | `qdii_fund`; complete eligible fallback; quality `block`; terminal `disclosure_data_gap_not_baseline_ready`; `promotion_disposition=not_promoted` | Public evidence confirms `manager_strategy_text` remains missing with no value, no anchor, and no locator; P0 quality block persists. Accepted controller judgment says this is not an authorized extractor fix or policy change. | `replace` | Controller to open / assign QDII replacement candidate evidence gate. | Revisit after an accepted QDII replacement candidate has source-safe provenance, same-year public evidence, no P0 disclosure quality block, and explicit no-promotion review. If no replacement exists, controller may separately decide `exclude_from_v1`. | Current candidate has a P0 `manager_strategy_text` quality block and terminal disclosure data gap; promoting it would convert a known missing required fact into baseline truth. |
| FOF slot | No pure `fof_fund` representative accepted; slot remains `data_gap` / `taxonomy_pending` | Prior FOF attempts remain data gaps; QDII-FOF candidates such as `007721` / `017970` cannot count as pure `fof_fund` without an accepted taxonomy decision or repository-safe pure FOF candidate. | `needs_taxonomy_gate` | Controller to open / assign FOF taxonomy / pure FOF candidate gate. | Revisit after the controller accepts either a pure FOF entry contract and candidate path, or an explicit `FOF deferred from golden v1` decision with owner and revisit trigger. | There is no accepted pure FOF candidate and no accepted taxonomy decision allowing QDII-FOF evidence to satisfy pure FOF coverage. |
| Carry-forward evaluated candidate / `004393` / 2024 | Accepted clean evaluated active-fund candidate; quality `warn`; not `scoring_ready`; not durable baseline | Small baseline corpus v1 and later controller judgment accepted it as evaluated evidence only. | `include_for_later_review` | Controller / future baseline preflight owner. | Revisit only in a durable baseline or golden preflight after all coverage and fixture-promotion prerequisites are met. | This gate does not promote carry-forward candidates; accepted evidence says no sample is `accepted_baseline`, `scoring_ready`, or durable fixture. |
| Carry-forward evaluated candidate / `004194` / 2024 | Accepted clean evaluated enhanced-index candidate; quality `warn`; not `scoring_ready`; not durable baseline | Small baseline corpus v1 and later controller judgment accepted it as evaluated evidence only. | `include_for_later_review` | Controller / future baseline preflight owner. | Revisit only in a durable baseline or golden preflight after all coverage and fixture-promotion prerequisites are met. | This gate does not promote carry-forward candidates; accepted evidence says no sample is `accepted_baseline`, `scoring_ready`, or durable fixture. |
| Bond / `006597` / 2024 | Separate follow-up / golden blocker; `bond_fund`; quality improved to `warn`, not `pass`; not golden-ready | Bond-lens applicability improvement is accepted, but `bond_risk_evidence_missing.baseline_blocking=true` remains; residual P1 gaps include `holder_structure`, `share_change`, and `turnover_rate`; positive bond-risk evidence is absent. | `needs_evidence_gate` | Controller to open / assign separate bond positive-risk evidence gate; not part of QDII/index/FOF replacement scope. | Revisit after an accepted positive bond-risk evidence contract or accepted bond exclusion/deferral decision resolves `baseline_blocking=true`. | Bond remains a golden blocker while positive bond-risk evidence is absent; it cannot be silently promoted through this QDII/index/FOF disposition gate. |

## 4. Recommendation: Next Cursor

Choose exactly one next cursor:

`QDII replacement candidate evidence gate`

First-principles basis:

- The current matrix already preserves `110020` as `include_for_later_review`, so index reviewed fact freeze is downstream and should not run before the controller confirms the broader coverage path.
- `017641` has an accepted terminal state of `disclosure_data_gap_not_baseline_ready`; the least ambiguous action is replacement, because current evidence proves the row cannot safely represent QDII coverage.
- FOF remains important, but it is a taxonomy / scope question first. Running QDII replacement evidence is narrower, directly tied to a concrete failed candidate, and does not require changing taxonomy or v1 scope assumptions.
- Bond positive-risk evidence is a separate follow-up and remains a golden blocker, but it is outside the QDII/index/FOF replacement gate.
- Durable baseline / golden preflight remains non-entry because multiple blockers still exist.

The next cursor is therefore QDII replacement evidence, not promotion. If that gate cannot find an accepted replacement, the controller should record QDII `exclude_from_v1` or open a reduced-scope decision gate instead of weakening quality or source rules.

## 5. Explicit Blockers To Golden Answer Corpus v1 / Durable Baseline Fixture Gate

Do not enter `golden answer corpus v1` or durable baseline fixture gate while any blocker below remains:

- `017641` has P0 `manager_strategy_text` quality block and terminal `disclosure_data_gap_not_baseline_ready`.
- No accepted QDII replacement candidate exists.
- Pure FOF remains `data_gap` / `taxonomy_pending`; QDII-FOF cannot count as pure FOF without accepted taxonomy.
- `110020` lacks methodology / constituents sufficiency, strict golden coverage, and reviewed fact freeze.
- `006597` still has `bond_risk_evidence_missing.baseline_blocking=true` and residual P1 evidence gaps.
- `004393` and `004194` are carry-forward evaluated candidates only; no accepted durable fixture or golden promotion plan exists.
- No separate fixture / golden promotion gate has accepted exact rows, reviewed facts, source provenance, denominator status, and two independent reviews.

## 6. Non-Goals / Prohibitions

This gate explicitly forbids:

- Running extraction, `analyze`, `checklist`, quality, evidence, source-probing, or report-generation CLI commands.
- Code, tests, configs, README, `AGENTS.md`, `docs/design.md`, or `docs/implementation-control.md` changes.
- Renderer, FQ0-FQ6, Service, CLI, source strategy, `FundDocumentRepository`, source-helper, direct PDF/cache, Host, Agent, or Dayu work.
- Baseline, golden, clean-denominator, report-quality corpus, fixture, or candidate promotion.
- Taxonomy implementation, extractor implementation, fallback semantic changes, or quality threshold weakening.
- GitHub mutation, commit, push, PR, merge, external issue/comment, or branch mutation.
- Entering the recommended next cursor from this worker artifact.

## 7. Review Matrix

| Review / judgment | Artifact | Result | Decision carried into this matrix |
|---|---|---|---|
| Independent plan review 1 | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-review-mimo-20260527.md` | `PASS_WITH_FINDINGS` | Accept carry-forward clarification for `004393` / `004194`; require owners and revisit conditions in this disposition matrix. |
| Independent plan review 2 | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-review-glm-20260527.md` | `PASS_WITH_FINDINGS` | Accept explicit bond follow-up / golden blocker handling; preserve FOF taxonomy residual and no-promotion discipline. |
| Controller judgment | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-controller-judgment-20260527.md` | `ACCEPTED LOCALLY` | Accepted next entry point is this replacement/exclusion candidate selection gate; required output is disposition matrix with owners, revisit conditions, carry-forward state, bond follow-up, and no promotion. |

No re-review is triggered by this worker artifact because it follows the accepted controller judgment requirements and does not introduce implementation, evidence, or promotion.

## 8. Validation

Required validation:

```bash
git diff --check
```

| Command | Exit code | Result |
|---|---:|---|
| `git diff --check` | `0` | passed |
