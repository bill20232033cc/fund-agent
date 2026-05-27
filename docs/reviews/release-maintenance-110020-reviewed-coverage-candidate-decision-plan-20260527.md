# Release Maintenance: 110020 Reviewed Coverage Candidate Decision Plan

> Worker: AgentCodex planning worker, not controller  
> Date: 2026-05-27  
> Gate: `110020 reviewed coverage candidate decision gate`  
> Scope: plan artifact only; no implementation, no promotion, no `docs/implementation-control.md` update

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `110020 reviewed coverage candidate decision gate` |
| Worker role | planning worker, not controller |
| Next entry point | decide whether `110020` / 2024 may enter a later reviewed coverage candidate evidence gate; route this plan to independent review and controller judgment |
| Latest checkpoint | `post-provenance coverage recovery decision plan accepted locally`; exact commit should be read from current branch HEAD by controller if needed |
| Truth sources replayed | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts listed below |
| Accepted artifacts used | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`; `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md` |

Allowed scope:

- Decide whether accepted public evidence is sufficient to use `110020` / 2024 as input to a later reviewed coverage candidate evidence gate.
- Identify unresolved risks that the later evidence gate must validate before any baseline or golden decision.
- Define public-only commands, artifacts, reviews, validation, and stop conditions for that later evidence gate.
- Keep every state as `not_promoted`.

Forbidden scope:

- No code implementation.
- No renderer, FQ0-FQ6, Service, CLI default `analyze` / `checklist`, source strategy, `FundDocumentRepository`, source helper, extractor, cache, PDF, Host/Agent/dayu, fixture, baseline, clean denominator, or golden changes.
- No direct PDF/cache/source-helper inspection.
- No durable baseline, clean denominator, fixture, report-quality corpus, or golden promotion.
- No GitHub mutation, push, PR, merge, branch deletion, or commit.

## Accepted Evidence Summary

Accepted public provenance / quality state for `110020` / 2024:

| Field | Accepted state |
|---|---|
| `fund_code` | `110020` |
| `report_year` | `2024` |
| `fund_type_slot` | `index_fund` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| `source_provenance_status` | `complete` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |
| `quality_gate_status` | `warn` |
| `terminal_state` | `provenance_eligible_for_next_review` |
| `promotion_disposition` | `not_promoted` |

Accepted evidence basis:

- Public `extraction-snapshot --force-refresh`, `extraction-score`, and `quality-gate` commands exited 0 in the source-provenance rerun.
- Public row consistency passed: 16 snapshot rows, one unique provenance tuple, and zero public `errors.jsonl` records.
- Independent rerun reviews returned `PASS`, and controller accepted the classification.
- The previous source blocker is resolved only for review eligibility: fallback is now public, complete, and eligible because the primary failure category is `unavailable`.

This state is not a baseline, clean denominator, fixture, or golden state. It means only that `110020` may be reviewed as an index slot coverage candidate under a separate evidence gate.

## Unresolved Risks

`110020` still carries the following unresolved risks:

| Risk | Current evidence | Decision impact |
|---|---|---|
| `turnover_rate` P1 warn | Public quality notes cite `FQ2` warn for `turnover_rate` and `FQ2F` warn for `110020` P1 field failure. | Blocks any unqualified baseline/golden promotion; later evidence gate must decide whether this is acceptable for an index slot or requires data/evidence follow-up. |
| Strict golden not configured | Public quality notes cite `FQ0` info because strict golden answer was not configured. | Carried-forward residual. Correctness cannot be reviewed until same-year strict golden coverage is established; the score must not be treated as strict correctness proof. |
| Reviewed fact readiness | No accepted reviewed-fact freeze exists for `110020` index-lens facts. | Later gate must validate which facts are reviewed, which are gaps, and which cannot enter durable artifacts. |
| No fixture-promotion gate | No separate fixture/golden promotion gate has accepted `110020`. | Any durable baseline, clean denominator, fixture, or golden action must stop. |
| Index slot methodology / constituents / tracking evidence | Current accepted evidence proves provenance and quality `warn`; it does not prove index methodology, constituents, tracking quality, or index-lens evidence sufficiency. | Later evidence gate must inspect public snapshot/score/gate outputs and record whether index-profile / tracking-error / benchmark-methodology evidence is sufficient, insufficient, or out of scope for this candidate. |

## Index-Lens Evidence Sufficiency Definition

`110020` / 2024 is treated as an `index_fund` candidate. The later evidence gate must include an independent `index_evidence_assessment` section and classify each row below as `sufficient`, `insufficient`, or `out_of_scope`, with a short reason and source pointer. This assessment is evidence review only; it does not promote the row.

| Evidence item | Required assessment | Sufficient means | Insufficient means | Out of scope means |
|---|---|---|---|---|
| `index_profile` | Must assess public snapshot / score evidence for index identity, index target, and index-specific profile fields. | Public extracted facts identify the tracked index / benchmark context with traceable evidence and no contradictory type signal. | Index identity, benchmark context, or evidence anchor is missing, contradictory, or only inferable from indirect text. | Only allowed if the field is demonstrably not applicable to the accepted `index_fund` slot; this should be rare and must be justified. |
| `tracking_error` | Must assess reviewed tracking evidence as a specific prerequisite for this index fund candidate. | Public output contains direct observed tracking-error disclosure or an accepted reviewed evidence statement with traceable anchor; the gate can explain whether tracking quality is reviewable. | Tracking-error evidence is missing, unanchored, inferred indirectly, or not reviewed. This does not automatically reject the candidate, but it must remain a carried-forward blocker for any baseline/golden preflight. | Only allowed if design/controller judgment explicitly decides tracking-error evidence is not applicable to this candidate; absent that decision, classify missing tracking evidence as `insufficient`, not `out_of_scope`. |
| Benchmark methodology / constituents / tracking evidence | Must assess whether public evidence supports index methodology / constituent / tracking-specific statements needed by the index lens. | Public facts or anchors support the relevant methodology / constituents / tracking claim, or the artifact records a reviewed fact source for it. | Evidence is absent, generic benchmark text is being overread, or the claim would require direct PDF/cache/source-helper inspection. | Allowed only for a claim that the evidence gate explicitly excludes from the current candidate review scope while carrying it as a residual. |

The evidence gate must not collapse these three items into a single generic "index evidence ok" statement. `tracking_error` reviewed evidence is a concrete prerequisite for treating `110020` as a mature index fund coverage candidate in any later baseline/golden preflight.

## Decision Candidates

### Candidate A: Accept `110020` as next reviewed coverage candidate evidence gate input

Meaning: accept `110020` / 2024 as input to a later evidence gate, not as a promoted corpus member.

Entry conditions:

- Accepted public provenance remains complete: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`.
- Accepted fund-type slot remains `index_fund`.
- Accepted public quality status remains `warn`, not `block`.
- The later gate explicitly treats `110020` as an index slot coverage candidate under review, not as durable baseline / clean denominator / fixture / golden material.
- The later gate starts from accepted artifacts and uses only public CLI output if fresh evidence is needed.

Validation evidence:

- Cite accepted source-provenance rerun artifact and controller judgment.
- Re-run only public CLI commands if controller authorizes fresh evidence: `extraction-snapshot --force-refresh`, `extraction-score`, and `quality-gate`.
- Record `turnover_rate` P1 warn, strict-golden absence, reviewed fact readiness, fixture-promotion absence, and index-lens evidence status in the evidence artifact.
- Include the `index_evidence_assessment` table for `index_profile`, `tracking_error`, and benchmark-methodology / constituents / tracking evidence, with `sufficient` / `insufficient` / `out_of_scope` classification and reasons.

Stop condition:

- Stop if the evidence gate attempts promotion, changes production behavior, changes source strategy/fallback semantics, touches direct PDF/cache/source helper paths, or hides the `warn` risks.
- Stop if fresh public evidence changes `quality_gate_status` to `block` or provenance to anything other than complete eligible fallback.
- Stop and report if fresh public evidence introduces new P0/P1 warnings or blocks beyond the known `turnover_rate` P1 warn, `FQ2F` P1 field failure warn, and `FQ0` strict-golden-not-configured info.
- Stop if `source_strategy`, `resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, or `source_provenance_reason` changes from the accepted tuple unless the controller explicitly accepts the changed evidence state.

### Candidate B: Defer `110020` pending more evidence

Meaning: do not use `110020` as the next reviewed candidate yet; require a narrower evidence-gathering or fact-review plan first.

Entry conditions:

- The controller decides the unresolved risks are too material for candidate evidence review, especially strict golden absence or index-lens fact readiness.
- The next action can be scoped to public evidence only, without implementation or source/cache/PDF inspection.
- Defer decision is explicit and does not silently replace `110020` with another row.

Validation evidence:

- Identify the exact missing public evidence: e.g. strict golden coverage, reviewed index facts, methodology / constituents / tracking evidence, or turnover-risk disposition.
- Provide an evidence-only artifact plan for the missing piece before reopening candidate acceptance.

Stop condition:

- Stop if deferral turns into extractor/source implementation without accepted plan/review.
- Stop if deferral tries to bypass candidate review by entering golden corpus v1 directly with other partial rows.

### Candidate C: Reject / exclude `110020`

Meaning: exclude `110020` from the reviewed coverage candidate path.

Entry conditions:

- Public evidence shows provenance is no longer complete/eligible, quality becomes `block`, or index-lens facts are materially unsuitable for the coverage slot.
- A same-source evidence review demonstrates that unresolved risks are not merely warnings but make the row unusable for reviewed coverage.
- Replacement path is explicitly separate and does not reuse `110020` artifacts as durable fixtures.

Validation evidence:

- Cite the public command output or accepted review artifact that changed the state.
- Record terminal state such as `excluded_after_review`, with `promotion_disposition=not_promoted`.

Stop condition:

- Stop if rejection is based on indirect evidence, subjective report taste, or unstated preference for a different candidate.
- Stop if rejection triggers source strategy changes, fallback weakening, or direct PDF/cache/source helper inspection.

## Recommendation

Recommend Candidate A: accept `110020` / 2024 as the next reviewed coverage candidate evidence gate input, with `promotion_disposition=not_promoted`.

Why this is the minimum next step:

- The previous blocker was unknown fallback provenance; accepted public evidence now resolves it as `primary_failure_category=unavailable` and `fallback_eligibility=eligible`.
- Quality is `warn`, not `block`, so the row is fit for a reviewed evidence gate that can inspect residual warnings.
- The step is reversible and bounded: it only authorizes evidence review, not corpus promotion or product behavior changes.

Why not enter `golden answer corpus v1`:

- Strict golden is not configured for `110020`.
- Reviewed facts are not frozen.
- `turnover_rate` P1 warn remains unresolved.
- Index methodology / constituents / tracking evidence sufficiency is not yet reviewed.
- No fixture-promotion gate exists.
- Broader corpus blockers remain: QDII quality, pure FOF coverage / taxonomy, bond positive-risk evidence, and representative clean coverage targets.

## Acceptance Matrix For The Recommended Evidence Gate

If controller accepts this plan, the next evidence gate should remain public-only and not-promoted:

| Step | Required action | Required output | Acceptance condition | Stop condition |
|---|---|---|---|---|
| Startup replay | Re-read current Startup Packet, design current sections, and this accepted plan. | Evidence artifact section with phase/gate/latest checkpoint/allowed/forbidden. | Scope remains `110020` / 2024 candidate evidence only. | Stop if the gate expands to baseline/golden/fixture promotion or implementation. |
| Public snapshot | `uv run fund-analysis extraction-snapshot --run-id 110020-reviewed-coverage-candidate-2024-20260527 --report-year 2024 --fund-code 110020 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527 --force-refresh` | Ignored run directory with `snapshot.jsonl`, `summary.md`, `errors.jsonl`. | Exit 0; public rows retain complete eligible provenance; errors are recorded if any; artifact records `docs/code_20260519.csv` path plus git identity/version note. Plan-revision observed CSV state: repo HEAD `188f150cf27c6b3792a92ed11ebedb164b485ebb`, CSV last commit `7596c5ece4894166d5479ee764fc8641a23cfc0d`, `git status --short docs/code_20260519.csv` clean, mtime `May 19 00:28:41 2026`, size `3213 bytes`. | Stop if provenance tuple changes from accepted values, source strategy / resolved source changes, command requires direct cache/PDF/source-helper access, output would need tracked fixture promotion, or CSV identity cannot be recorded. |
| Public score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527 --errors-path reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/errors.jsonl` | Public `score.json`, `score.md`, `golden_set.json` in ignored run directory. | Score output explicitly records strict golden coverage state and P1/P0 field results; strict golden absence is recorded as carried-forward residual, not correctness proof. | Stop if score is interpreted as strict correctness proof without configured same-year golden coverage, or if new P0/P1 warnings/blocks appear beyond known `turnover_rate` P1 warn, `FQ2F` P1 field failure warn, and `FQ0` strict-golden info. |
| Public quality gate | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/score.json --output-dir reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527` | Public `quality_gate.json`, `quality_gate.md`. | Quality remains `warn` or better; all warnings are listed, not hidden; warning set is compared against known accepted warnings. | Stop if quality becomes `block`, new P0/P1 warnings are introduced without explicit report, or if the plan weakens FQ0-FQ6 semantics. |
| Index evidence assessment | Evaluate `index_profile`, `tracking_error`, and benchmark-methodology / constituents / tracking evidence from public snapshot/score/gate outputs and accepted artifacts. | `index_evidence_assessment` section in the evidence artifact. | Each item receives `sufficient`, `insufficient`, or `out_of_scope` with reason and source pointer; `tracking_error` reviewed evidence is treated as a concrete prerequisite for mature index candidate status. | Stop if the artifact omits any item, merges them into a generic index status, treats missing tracking evidence as sufficient, or relies on direct PDF/cache/source-helper inspection. |
| Evidence artifact | Write `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-20260527.md`. | Tracked summary artifact only; generated run outputs remain ignored. | Artifact records fund type slot, provenance tuple, quality state, CSV identity/version note, unresolved risks, index evidence assessment, terminal state, and `promotion_disposition=not_promoted`. | Stop if artifact promotes durable baseline / clean denominator / fixture / golden or fails to carry forward strict-golden and reviewed-fact residuals. |
| Independent reviews | Route to two independent reviewers, e.g. MiMo + GLM, then controller judgment. | Review artifacts and controller judgment under `docs/reviews/`. | Reviews confirm public-only evidence, no promotion, no boundary violation, explicit unresolved-risk disposition, and complete index evidence assessment. | Stop if any reviewer returns `BLOCK` until fixed and re-reviewed; stop if fewer reviews are accepted without explicit controller risk acceptance, or if any material finding remains unresolved. |
| Validation | Run `git diff --check` after artifact-only changes. | Validation result recorded in controller/evidence artifact. | Whitespace check passes; only tracked review artifacts changed. | Stop if code, docs/control, source, fixture, baseline, golden, or generated outputs are changed. |

The evidence gate terminal states should be one of:

| Terminal state | Meaning | Promotion disposition |
|---|---|---|
| `reviewed_coverage_candidate_input_accepted` | `110020` may be considered by a later baseline/golden preflight after unresolved risks are carried forward. | `not_promoted` |
| `deferred_pending_reviewed_facts` | Candidate is not rejected, but reviewed facts or index-lens evidence are insufficient. | `not_promoted` |
| `excluded_after_review` | Public evidence makes the row unsuitable for the index coverage slot. | `not_promoted` |

## Explicit Non-Goals

- Do not change code.
- Do not change renderer, FQ0-FQ6, Service, CLI default `analyze` / `checklist`, source strategy, `FundDocumentRepository`, source helper, extractor, cache, or PDF behavior.
- Do not directly access PDF/cache/source helper internals.
- Do not create Host/Agent packages or integrate `dayu.host` / `dayu.engine`.
- Do not promote `110020` to durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus.
- Do not update `docs/implementation-control.md`.
- Do not commit, push, create PR, merge, delete branches, or perform any GitHub mutation.

## Handoff Recommendation

Controller should route this plan to independent plan review. If accepted, enter `110020 reviewed coverage candidate evidence gate` as a public-only evidence gate, and keep `110020` / 2024 at `promotion_disposition=not_promoted`.
