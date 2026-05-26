# Coverage Replacement / Source Provenance Design Plan

> Date: 2026-05-27
> Role: AgentCodex planner
> Gate: `coverage replacement candidate selection or source provenance output design gate`
> Latest accepted checkpoint: `e41c829 docs: accept index qdii recovery evidence`
> Scope: planning handoff only. No code, tests, extraction evidence, `docs/design.md`, `docs/implementation-control.md`, commit, push, or PR changes are authorized.

## Startup Packet Replay

| Item | Current state |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `index/QDII source recovery evidence accepted locally` |
| Next entry point | `coverage replacement candidate selection or source provenance output design gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint | `e41c829 docs: accept index qdii recovery evidence` |
| Current truth | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts |

Allowed in this gate:

- Choose between additive public-output source fallback provenance design and controller-approved replacement-candidate selection for index/QDII coverage.
- Keep `110020` / 2024 and `017641` / 2024 outside the clean denominator unless a later accepted gate recovers eligible provenance or verifies replacements.
- Write a tracked planning summary artifact under `docs/reviews/`.

Forbidden in this gate:

- Implement code, update tests, update `docs/design.md`, update `docs/implementation-control.md`, run new extraction/snapshot/score/quality-gate evidence, commit, push, or open/modify PRs.
- Change `FundDocumentRepository` source strategy, fallback fail-closed semantics, renderer, FQ0-FQ6, Service CLI default behavior, Host/Agent/dayu, extractors, `fund_type.py`, golden fixtures, or baseline fixtures.
- Directly access PDFs, cache contents, source helpers, downloaders, or source adapters.
- Use ad hoc web/search to discover replacement candidates.

## Accepted Evidence Baseline

Checkpoint `e41c829` accepted the index/QDII source recovery evidence:

| Row | Accepted public evidence | Upstream failure category recovered? | Terminal state | Clean denominator |
|---|---|---:|---|---|
| `110020` / 2024 | Public CLI snapshot / score / quality-gate completed; classified `index_fund`; gate `warn` | No | `unrecoverable_safe_path`; replacement subgate `not_run_no_approved_candidates` | excluded |
| `017641` / 2024 | Public CLI snapshot / score / quality-gate completed; classified `qdii_fund`; gate `block` | No | `unrecoverable_safe_path`; replacement subgate `not_run_no_approved_candidates` | excluded |

The critical evidence result is negative: public outputs proved the current CLI can complete bounded runs, but they did not expose the original upstream failure category that made prior fallback-backed rows unsafe for durable baseline selection.

## First-Principles Decision

Durable golden/baseline promotion requires representative rows whose document identity, fund-type slot, field evidence, and source safety are all reviewable from accepted public artifacts. For fallback-backed candidates, source safety is not a downstream quality-gate property. It depends on the original primary-source failure category:

- `not_found` and `unavailable` may fallback.
- `schema_drift`, `identity_mismatch`, and `integrity_error` must fail closed.

The current evidence cannot support golden/baseline promotion because the public artifacts do not show which category occurred before fallback. A successful later extraction is only indirect evidence that a document was obtained; it is not direct evidence that the fallback was allowed. Using it as a baseline proof would collapse the fail-closed source contract into "the run succeeded", which is exactly the unsafe inference the repository fallback taxonomy exists to prevent.

No approved replacement candidates exist. Therefore replacement selection cannot move the gate forward without inventing candidates through ad hoc search or by probing unapproved rows, both of which are explicitly forbidden. The shortest safe path is to design additive public source provenance output so future evidence gates can recover or reject fallback-backed rows from public artifacts without touching private source helpers or weakening repository semantics.

## Selected Path

Recommended path: **additive public-output contract for repository source fallback provenance**.

Rejected for this gate: **controller-approved replacement-candidate selection path**.

Reason: replacement selection is valid only if candidates are controller-supplied or derived from already accepted artifacts. The current checkpoint explicitly says replacement subgate is `not_run_no_approved_candidates`. With no approved candidates, doing replacement work now would either be a no-op or violate the no ad hoc web/search and no direct PDF/cache/helper constraints.

## Minimal Public Output Contract

The future implementation gate should expose source provenance as additive metadata on public extraction outputs. Minimum contract:

| Field | Required meaning |
|---|---|
| `source_provenance_schema_version` | Stable version string, initially `repository_source_provenance.v1`. |
| `source_strategy` | Public strategy label, e.g. `primary_then_fallback`; descriptive only, not a strategy change. |
| `resolved_source_name` | Public source label for the document actually used, e.g. `eid` / `eastmoney` if already available through repository metadata. |
| `fallback_used` | Boolean copied from repository source metadata when available. |
| `primary_failure_category` | One of `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, or `null` when no primary failure occurred or metadata is unavailable. |
| `fallback_eligibility` | Derived public value: `eligible`, `fail_closed`, `not_applicable`, or `unknown_public_metadata_absent`. |
| `source_provenance_status` | Row-level status: `complete`, `incomplete`, or `not_applicable`. |
| `source_provenance_reason` | Short deterministic reason for incomplete / fail-closed / unknown states. No raw exception dump. |

Contract rules:

- Additive only: existing public output keys, exit codes, default CLI behavior, and FQ0-FQ6 policy must remain unchanged.
- Public only: expose reviewed source provenance fields in snapshot / summary / score-compatible public artifacts; do not require consumers to inspect PDFs, cache files, source helpers, downloader internals, or exceptions.
- Conservative by default: missing provenance for fallback-backed rows must classify as unknown/incomplete, not eligible.
- If `fallback_used=true` and `primary_failure_category` is `null` or unavailable because current metadata does not persist the failure category, `fallback_eligibility` MUST be `unknown_public_metadata_absent`, not `eligible`. This cannot be relaxed except by a later accepted gate that threads `AnnualReportSourceFailure.category` through metadata and public output.
- Fail-closed preserving: `schema_drift`, `identity_mismatch`, and `integrity_error` must remain non-eligible and must not be hidden by downstream score or quality-gate success.
- Multi-source chains must have their `primary_failure_category` selection rule specified in the future implementation gate. If the public output cannot determine the applicable primary failure category for the chain, conservative `unknown_public_metadata_absent` applies.
- No fixture promotion: output contract implementation may produce scratch evidence only until a later reviewed baseline/golden gate accepts candidates.

## Future Implementation File Scope

Based on current design truth, the smallest plausible implementation surface is:

| Area | Expected scope |
|---|---|
| Agent/Fund public model | Add provenance projection fields to the extraction snapshot / score public records only where repository metadata is already available. |
| Agent/Fund provenance projection | Own a pure projection function in `fund_agent/fund` that maps `AnnualReportSourceMetadata` / public repository metadata to additive public provenance fields. This function must be deterministic, side-effect-free, and must not reach into source helpers. |
| Document repository metadata consumption | Read existing `AnnualReportSourceMetadata` / repository result metadata; do not change source orchestration, fallback decisions, or source adapters. |
| Service public output | Consume the Agent/Fund projection result and include additive provenance fields in `ExtractionSnapshotService` output and any summary artifact generated from that output. Service must not invert dependencies into source internals or access source helpers. |
| Score compatibility | Preserve old score JSON compatibility; if scoring consumes provenance, it must treat missing keys conservatively and should not change FQ thresholds. |
| README sync | Only if public output shape or maintainer workflow documentation changes; keep docs current-code only. |

Explicit non-scope:

- No changes to `FundDocumentRepository` source strategy or fallback eligibility decisions.
- No changes to source helpers, downloaders, cache layout, PDF access, or source-specific adapters.
- No renderer, report-writing, FQ0-FQ6 policy, default `fund-analysis analyze` / `checklist`, Host/Agent/dayu, golden fixture, baseline fixture, or corpus promotion changes.

## Future Test Scope

The future implementation gate should require focused tests for:

- Fallback eligible categories map to public `fallback_eligibility="eligible"`.
- Fail-closed categories map to public `fallback_eligibility="fail_closed"` and never become clean evidence through downstream success.
- No-fallback primary success maps to `fallback_used=false`, `primary_failure_category=null`, and `not_applicable`.
- Consistency assertion: rows with `source_provenance_status="not_applicable"` must have `fallback_eligibility="not_applicable"` and `fallback_used=false`.
- Missing legacy provenance keys remain compatible and classify as unknown/incomplete, not eligible.
- Fallback-backed rows with `fallback_used=true` and missing / unavailable `primary_failure_category` classify as `fallback_eligibility="unknown_public_metadata_absent"`, not eligible.
- Public summary / JSONL output includes provenance without changing existing required keys.
- Existing public CLI defaults, exit-code semantics, FQ0-FQ6 thresholds, renderer output, and Service control flow remain unchanged.

## Future Acceptance Commands

A later implementation gate should define exact commands, but minimum acceptance should include:

- Focused unit tests for provenance projection and compatibility.
- Focused service/public-output tests for extraction snapshot summary / JSONL shape.
- Existing extraction score and quality-gate compatibility tests.
- `uv run ruff check .`
- `git diff --check`
- Bounded public CLI evidence for `110020 --report-year 2024` and `017641 --report-year 2024` only after the output contract implementation is accepted for review; generated outputs must remain under ignored report paths.

The future bounded evidence must classify each row from public provenance fields only. If provenance remains missing, the rows stay excluded. If provenance shows eligible primary failure categories, the rows may proceed only to the next reviewed evidence gate; they still must not be promoted directly to golden/baseline.

## Replacement Selection Path Conditions

Replacement selection should be reopened only when at least one candidate source exists:

- Controller explicitly supplies candidate fund code, report year, target slot, and rationale.
- A previously accepted artifact already contains a candidate with repository-verifiable identity and matching fund-type slot.

Approval conditions before evidence:

- Candidate has explicit fund code and report year.
- Candidate targets the missing `index_fund` or `qdii_fund` slot.
- Candidate source is accepted-artifact-derived or controller-supplied, not web/search discovered.
- Evidence run uses public Fund paths only; no direct PDF/cache/source-helper access.
- Candidate remains outside the clean denominator until repository identity, fund type, source provenance, and quality outputs are reviewed.

## Residual Risks

- Source provenance output may require threading existing repository metadata through public snapshot outputs; if the current public extraction boundary has no repository metadata object, the implementation gate must stop and redesign the public contract rather than reaching into source helpers.
- Even with provenance, `017641` currently has quality-gate `block`; provenance alone would not make it baseline-ready.
- `110020` quality-gate `warn` is not enough for durable golden/baseline promotion without source provenance and later reviewed fact/golden decisions.
- Pure FOF coverage remains unresolved.
- Bond baseline-blocking residuals remain separate from this gate.
- Golden/baseline promotion remains blocked until coverage, source/fund-type, bond, FOF, and reviewed-fact blockers are resolved in later accepted gates.
