# 017641 Manager Strategy Text Quality Triage Plan

> Worker: AgentCodex planning worker
> Date: 2026-05-27
> Gate: `017641 manager_strategy_text extraction/quality triage gate`
> Output type: plan artifact only
> Promotion disposition: `not_promoted`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `017641 manager_strategy_text extraction/quality triage gate` |
| Next entry point | `017641 manager_strategy_text extraction/quality triage gate`; controller must use `$init-agents` / tmux multi-agent flow for plan review and judgment |
| Latest checkpoint | `110020 reviewed coverage candidate evidence accepted locally`; use latest branch HEAD for exact commit hash |
| Design truth | `docs/design.md` v2.2 current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |
| Worker role | Planning worker only, not controller |

Allowed in this gate:

- Produce this plan artifact for `017641` / 2024 `manager_strategy_text` FQ2/FQ3 P0 triage.
- Use accepted artifacts and public CLI output paths as evidence references.
- Define a later public-only evidence triage gate and its command / artifact / review matrix.
- Classify possible terminal paths before any implementation: extractor implementation plan, disclosure/data gap, policy/taxonomy issue, replacement/exclusion, or reject/exclude.

Forbidden in this gate:

- Do not implement extractor changes.
- Do not weaken, bypass, or reclassify FQ0-FQ6 quality gate behavior.
- Do not edit `docs/implementation-control.md`.
- Do not promote `017641` to durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus.
- Do not modify renderer, FQ0-FQ6, Service, CLI, default `analyze` / `checklist`, source strategy, `FundDocumentRepository`, Host, Agent, Dayu runtime, golden fixtures, or baseline fixtures.
- Do not directly inspect PDF files, cache files, source helper internals, source dumps, or downloaded artifacts. Production annual report access must remain through public CLI paths backed by `FundDocumentRepository`.
- Do not commit, push, open PRs, or mutate branches.

## Accepted Evidence Summary

Accepted evidence for `017641` / 2024:

| Field | Accepted state |
|---|---|
| `fund_code` | `017641` |
| `report_year` | 2024 |
| `fund_type_slot` | `qdii_fund` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |
| `quality_gate_status` | `block` |
| Blocking issues | `FQ2 manager_strategy_text P0`; `FQ3 manager_strategy_text P0`; `FQ2F P0 field failure` |
| Additional public issues | `FQ2/warn turnover_rate`; `FQ2/warn holdings_snapshot`; `FQ2F/warn P1 fields`; `FQ0/info strict golden not configured`; `FQ4/warn high missing-field rate` |
| Terminal state | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |

Evidence chain:

- `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`
- `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md`

## Root-Cause Triage Principles

Root cause must be logic/data same-source:

- A claim that `manager_strategy_text` is an extractor bug must be supported by public production-path output showing the target field is absent or malformed while same-source public extraction evidence proves the relevant source material or anchor exists.
- A claim that it is a disclosure/data gap must be supported by public production-path output showing the required field and relevant anchors are unavailable through the repository-backed extraction path, without inferring from unrelated fields.
- A policy/taxonomy issue must be supported by a mismatch between current QDII field applicability / quality policy and public evidence. It cannot be inferred merely because a QDII document blocks.
- A replacement/exclusion decision must be based on accepted public evidence that `017641` remains unusable for the intended coverage slot, not on subjective convenience.

Forbidden evidence shortcuts:

- No indirect evidence such as "other QDII funds usually disclose this" or "Eastmoney fallback likely missed it".
- No subjective guess about manager commentary, source quality, or disclosure norms.
- No direct PDF/cache/source-helper inspection.
- No Service/UI/renderer behavior probing to infer document truth.
- No use of generated reports as durable fixtures or golden truth.

Allowed evidence route:

- Public CLI commands only, through existing repository-backed paths.
- Existing accepted artifacts only.
- Generated outputs must stay under ignored report paths and be summarized into tracked review artifacts.

## Decision Candidates

| Candidate | Entering condition | Evidence required | Stop condition | Forbidden scope |
|---|---|---|---|---|
| Public-only evidence triage gate | Current accepted state: source provenance complete, eligible fallback, quality `block` on `manager_strategy_text`, but no same-source root cause yet | Public `extraction-snapshot --force-refresh`, `extraction-score`, `quality-gate`; field-level rows for `manager_strategy_text`; public source provenance tuple; quality issue details; artifact summarizing field status, anchors, missing reasons, and terminal classification | Any command fails; provenance regresses from complete eligible tuple; output requires private PDF/cache/source-helper inspection to decide; reviewer returns `BLOCK`; evidence cannot distinguish root cause | No code changes; no extractor implementation; no FQ policy changes; no renderer/Service/CLI/default behavior changes; no promotion |
| `manager_strategy_text` extractor implementation plan gate | Public-only evidence proves extractor gap: same production source path exposes relevant manager strategy/discussion evidence or anchor, but field extraction fails or projects an empty/invalid value | Evidence artifact from prior public triage; field contract for `manager_strategy_text`; exact Fund-layer ownership; tests scoped to extractor behavior; proof FQ thresholds unchanged | Evidence shows disclosure/data gap or policy issue instead; implementation would require source strategy/PDF/cache helper changes; scope touches renderer/FQ0-FQ6/Service defaults; no reviewer consensus | No implementation in planning artifact; no source strategy change; no quality gate weakening; no direct PDF/cache access; no golden/baseline promotion |
| Disclosure / data-gap classification gate | Public-only evidence shows no public production-path material sufficient to populate `manager_strategy_text`, or public output can only prove absent/unreviewable disclosure | Public field-level absence, missing anchor status, provenance tuple, quality issue summary, and explicit data-gap rationale | Evidence shows relevant source text exists but extractor misses it; evidence is indirect; replacement candidate exists and is approved as better path | No extractor implementation; no reclassifying P0 as pass/warn without accepted quality-policy gate; no treating data gap as clean QDII coverage |
| Policy / taxonomy issue gate | Public-only evidence shows `manager_strategy_text` should not be required for this QDII subtype or current FQ2/FQ3 policy is overbroad for a documented fund-type slot | Public fund-type classification, field applicability evidence, current FQ issue semantics, and a design argument tied to QDII lens / field contract | Evidence points to missing disclosure or extractor failure; changing policy would hide a necessary evidence gap; policy change would affect non-QDII rows without separate plan | No FQ0-FQ6 weakening in this gate; no broad taxonomy redesign; no `fund_type.py` changes without separate accepted plan; no golden/baseline promotion |
| Replacement / exclusion path | Public-only evidence shows `017641` remains blocked and cannot become usable within current bounded release-maintenance scope, or no root-cause-safe remediation is justified | Accepted exclusion reason; candidate-slot impact; proof no promotion; if replacement is proposed, controller-approved candidate list and public source/quality evidence plan | Approved replacement evidence is unavailable; exclusion would be used to silently satisfy coverage; root cause remains undecided but implementation is being proposed | No unapproved replacement probing; no counting QDII-FOF or wrong taxonomy slot as QDII evidence; no durable baseline/golden changes |
| Reject / exclude current evidence | Public evidence or review finds that existing 017641 row cannot be trusted for this gate despite accepted provenance, or gate scope was violated | Reviewer `BLOCK`, provenance mismatch, command-bound violation, or evidence contradiction | Contradiction is resolved by accepted public evidence without scope expansion | No partial promotion; no manual cleanup of generated outputs as proof; no branch mutation |

## Recommended Minimal Next Step

Recommendation: run a public-only evidence triage gate before any extractor implementation plan.

Reasoning:

- Accepted evidence proves the second-stage blocker: `017641` is no longer source-provenance-blocked, but quality-blocked on `manager_strategy_text`.
- It does not yet prove the root cause. FQ2/FQ3/FQ2F P0 tells us the field is missing or failing quality, not whether the source disclosure exists, whether the extractor failed, whether QDII applicability is wrong, or whether the row should be replaced.
- AGENTS.md requires root cause to be logic/data same-source. Jumping directly to implementation would guess the cause from quality symptoms, which is indirect evidence.
- A public-only triage gate is the shortest safe path because it reuses the existing public CLI production route through `FundDocumentRepository`, preserves source/fallback semantics, and can terminate into extractor plan, data-gap classification, policy/taxonomy gate, or replacement/exclusion without weakening quality gate.

Therefore the next controller handoff should be:

`017641 manager_strategy_text public-only evidence triage gate`

Expected terminal classifications:

- `extractor_gap_requires_implementation_plan`
- `disclosure_data_gap_not_baseline_ready`
- `policy_taxonomy_issue_requires_design_plan`
- `replacement_or_exclusion_required`
- `reject_exclude_due_to_evidence_violation`

All terminal states keep `promotion_disposition=not_promoted`.

## Public-Only Evidence Triage Matrix

Commands are proposed for the next evidence worker gate only. They should not be run as part of this plan artifact.

| Step | Command | Required output | Purpose |
|---|---|---|---|
| 1 | `uv run fund-analysis extraction-snapshot --run-id manager-strategy-text-triage-017641-2024-20260527 --report-year 2024 --fund-code 017641 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/manager-strategy-text-triage-017641-2024-20260527 --force-refresh` | `snapshot.jsonl`, `summary.md`, `errors.jsonl` under ignored report path | Recreate public repository-backed extraction and source provenance without stale metadata |
| 2 | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/manager-strategy-text-triage-017641-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/manager-strategy-text-triage-017641-2024-20260527 --errors-path reports/extraction-snapshots/manager-strategy-text-triage-017641-2024-20260527/errors.jsonl` | `score.json`, `score.md`, `golden_set.json` under ignored report path | Localize `manager_strategy_text` score / traceability / correctness issue state from public outputs |
| 3 | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/manager-strategy-text-triage-017641-2024-20260527/score.json --output-dir reports/extraction-snapshots/manager-strategy-text-triage-017641-2024-20260527` | `quality_gate.json`, `quality_gate.md` under ignored report path | Confirm FQ2/FQ3/FQ2F P0 status and detect regressions |
| 4 | Public-output inspection only, summarized in the evidence artifact | Tracked Markdown artifact, no tracked generated JSON/report files | Extract only field-level facts needed for root-cause classification |

Required tracked evidence artifact:

`docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-20260527.md`

The evidence artifact must include:

- Startup Packet replay and public-only command log.
- Source provenance tuple and row-consistency check.
- `manager_strategy_text` field-level status from public `snapshot.jsonl` / `score.json` / `score.md`.
- Exact FQ2/FQ3/FQ2F issue records from public `quality_gate.json` / `quality_gate.md`.
- Errors file status.
- Classification into exactly one terminal state.
- Explicit `promotion_disposition=not_promoted`.
- Statement that generated outputs are ignored and not accepted as durable fixtures.

Review matrix:

| Review role | Scope |
|---|---|
| AgentMiMo evidence review | Verify command fidelity, public-only discipline, provenance tuple, field-level `manager_strategy_text` classification, terminal-state choice, no promotion |
| AgentGLM evidence review | Challenge root-cause inference, especially extractor gap vs disclosure/data gap vs policy/taxonomy issue; verify no indirect evidence and no PDF/cache/source-helper access |
| Controller judgment | Accept, reject, or request rerun; choose next gate among implementation plan, data-gap classification, policy/taxonomy design, replacement/exclusion, or reject/exclude |

Stop conditions for the evidence gate:

- Any public command exits non-zero.
- `fallback_used`, `primary_failure_category`, `fallback_eligibility`, or `source_provenance_status` differs from the accepted complete eligible tuple.
- Public outputs do not expose enough field-level information to classify root cause without private inspection.
- Any reviewer reports direct PDF/cache/source-helper access, source strategy mutation, quality-gate weakening, or promotion attempt.
- New P0/P1 issue appears outside the accepted `manager_strategy_text` blocking cluster and cannot be explained by the evidence artifact.

## Explicit Non-Entry Statements

- Do not enter `golden answer corpus v1`.
- Do not promote `017641` to durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus.
- Do not change renderer, FQ0-FQ6, Service, CLI, default `analyze`, default `checklist`, source strategy, `FundDocumentRepository`, Host, Agent, Dayu runtime, `fund_type.py`, golden fixtures, or baseline fixtures.
- Do not implement `manager_strategy_text` extraction in this gate.
- Do not use direct PDF/cache/source-helper access to classify root cause.

## Plan Closeout

This plan recommends a public-only evidence triage gate as the minimal next step. Direct extractor implementation is deferred until same-source public evidence proves an extractor gap. If public evidence instead proves disclosure/data gap, policy/taxonomy mismatch, or replacement need, the next gate must follow that classification rather than implement extraction.
