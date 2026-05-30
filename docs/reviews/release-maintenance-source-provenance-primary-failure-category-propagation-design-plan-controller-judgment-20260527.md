# Controller Judgment: source provenance primary-failure-category propagation design plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `source provenance primary-failure-category propagation design gate`
> Latest accepted checkpoint before gate: `722cc6c docs: accept source provenance evidence classification`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this plan | `source provenance bounded evidence classification accepted locally` |
| Reviewed gate | `source provenance primary-failure-category propagation design gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The plan is accepted as the code-generation-ready basis for a later implementation gate. The core design is to persist the primary source failure category at the repository source-decision boundary, in `AnnualReportSourceMetadata`, and let the existing public `source_provenance` projection expose it through already-existing snapshot fields. This keeps fallback eligibility same-source with `FundDocumentRepository` source orchestration and avoids inference from extraction success, score output, quality status, renderer text, source name, or cache hit state.

The accepted implementation slice must stay minimal:

- move `AnnualReportSourceFailureCategory` ownership to `fund_agent/fund/documents/models.py`;
- add optional `primary_failure_category` to `AnnualReportSourceMetadata`;
- populate it only in `AnnualReportSourceOrchestrator` success-after-primary-failure fallback path;
- project it via `fund_agent/fund/source_provenance.py` using the accepted `effective_category` precedence rule;
- keep old metadata / cache rows compatible and keep missing category as `unknown_public_metadata_absent`.

## Review Summary

| Reviewer | Initial verdict | Re-review verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `PASS` | `PASS` | Accepted. Low implementation notes were incorporated. |
| AgentGLM | `pass-with-risks` | `pass` | Accepted. F1/F2/F3 were fixed in the plan. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| Type ownership could create circular import or duplicate Literal drift | GLM F1 | Accepted and fixed | Plan now moves `AnnualReportSourceFailureCategory` to `documents/models.py` and makes `sources.py` import it from there. |
| Projection precedence between metadata and keyword override was ambiguous | GLM F2 | Accepted and fixed | Plan now specifies `effective_category` pseudocode and truth-table tests; metadata non-`None` category wins. |
| Plan used wrong source orchestrator class name | GLM F3 | Accepted and fixed | Plan now uses `AnnualReportSourceOrchestrator`. |
| `to_dict()` / deserialization / `_mark_fallback_used` details needed precision | MiMo low notes | Accepted and fixed | Plan now names the exact dict key, `_normalize_failure_category()` pattern, and exact `_mark_fallback_used(..., *, primary_failure_category=...)` signature. |

## Accepted Implementation Boundaries

Allowed in the next implementation gate:

- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/source_provenance.py`
- focused tests under `tests/fund/documents/` and `tests/fund/`
- `fund_agent/fund/README.md`, `tests/README.md`, and `docs/design.md` sync only if implementation changes current behavior documentation
- `docs/implementation-control.md` only by controller after review / acceptance

Forbidden unless a later accepted plan expands scope:

- source strategy, source ordering, helper/downloader/PDF/cache semantics, or fail-closed fallback categories;
- renderer, FQ0-FQ6, scoring policy, quality-gate thresholds, default analyze/checklist control flow;
- baseline/golden fixture promotion or clean denominator changes;
- Host/Agent packages, `dayu.host`, `dayu.engine`, tool-loop/runtime work;
- public classification inferred from extraction, score, quality, renderer, source name, or cache state.

## Required Implementation Verifiers

- focused document-source / cache / repository tests proving category persistence, old metadata compatibility, import safety, and fail-closed behavior;
- source provenance projection tests proving missing category remains unknown, metadata category wins over keyword override, keyword fallback remains test-only compatible, eligible categories classify eligible, and fail-closed categories classify fail-closed;
- extraction snapshot tests proving the eight public provenance fields remain stable and category values copy to all rows;
- score / quality no-change tests proving FQ0-FQ6-sensitive outputs do not change;
- `uv run ruff check fund_agent/fund tests/fund`;
- `git diff --check`.

## Residual Risks

- Old cached metadata with `fallback_used=true` and no category will remain `unknown_public_metadata_absent` until refreshed; this is accepted compatibility behavior, not an implementation failure.
- Multi-source chains beyond current primary + fallback strategy remain out of scope and require a future provenance-chain schema gate.
- `110020` / `017641` still require a post-implementation bounded evidence rerun before any corpus decision; this plan does not promote either row.

## Next Entry Point

`source provenance primary-failure-category propagation implementation gate`

The next gate may implement the accepted minimal slice only after Startup Packet replay and `$init-agents` / tmux handoff. It must complete implementation, focused validation, two independent code reviews, any required fixes / re-reviews, control-doc updates, and a local accepted commit before any evidence rerun or baseline/golden decision.
