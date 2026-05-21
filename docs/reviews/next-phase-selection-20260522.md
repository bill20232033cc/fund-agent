# Next Phase Selection Plan（2026-05-22）

## 1. Gate / Role

- **Role**: AgentCodex planning specialist, not implementer.
- **Current gate**: `maintenance-ready`.
- **Next entry point**: `next phase selection`.
- **Design truth**: `docs/design.md`.
- **Control truth**: `docs/implementation-control.md`.
- **Closeout truth**: `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`.
- **Accepted post-P12 plan**: `docs/reviews/post-p12-planning-20260522.md`.
- **Output file for this task**: `docs/reviews/next-phase-selection-20260522.md` only.

This artifact selects the next gated work unit. It does not implement, stage, commit, push, open a PR, or modify source/tests/README/design/control/repo-audit files.

## 2. Decision

Recommended next gate:

```text
P13-S1 tracking-error / index-data source contract plan-review
```

This is the smallest best-practice next gate because the highest-value product gap is real index-fund data, but the safe first move is not immediate implementation. P13-S1 should produce a code-generation-ready implementation plan for the Fund Capability data contract: what source is authoritative, what fields enter structured data, how calculation provenance is represented, and where the deterministic renderer can stop saying `数据不足`.

Selected scope is **planning/design only**. Implementation may start only after P13-S1 plan review accepts exact files, tests, fixtures, and stop conditions.

## 3. Evidence

| Evidence | Implication |
|---|---|
| `docs/implementation-control.md` Startup Packet says current gate is `maintenance-ready`, next entry point is `next phase selection`, and open residuals include future P13 tracking-error/index-data, future E1-E3/Evidence Confirm, repo-hygiene D-1/D-8-C5/C-9, and RR-13. | A phase must be selected before implementation. |
| `docs/design.md` keeps the production chain deterministic: UI -> Service -> Fund Capability; annual-report access must go through `FundDocumentRepository`; Dayu Host/Engine/tool loop is not a production dependency. | P13 must live inside Fund Capability boundaries and cannot add Service/UI direct source access or Dayu runtime. |
| `docs/design.md` preferred_lens says index funds prioritize tracking error, fees, scale/liquidity; enhanced index funds prioritize excess return source and tracking error. | Tracking-error/index data is directly tied to the fund-type-first analysis contract. |
| `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md` records that index methodology, constituents, and tracking error remain deterministic `数据不足` placeholders until extractors exist. | P13 has a concrete user-visible gap left by P12. |
| `docs/reviews/post-p12-release-maintenance-closeout-20260522.md` recommends a future P13 design/plan for tracking-error/index-data with explicit source contracts, while keeping E1-E3 separate. | The closeout already points to P13 as the safest product lane after maintenance-ready. |
| `docs/design.md` marks E1/E2/E3 and Evidence Confirm as v2 audit layers. | Audit architecture should not be mixed into P13 data extraction. |
| `docs/repo-audit-20260521.md` keeps D-1, D-8/C-5, and C-9 as repo/doc hygiene candidates. | Repo hygiene is valid but lower product value than removing index-data placeholders. |
| RR-13 duplicate `016492` is recorded as user/App-source owned. | RR-13 is not agent-implementable and must not be auto-fixed. |

## 4. Candidate Comparison

| Candidate | Value | Scope / risk | Boundary fit | Selection |
|---|---:|---:|---|---|
| **P13 tracking-error / index-data capability** | High: removes user-visible `数据不足` for index/enhanced-index reports and supports preferred_lens. | Medium-high if implemented directly; low if first gate is source-contract planning. | Strong if kept in Fund Capability and `FundDocumentRepository`. | **Selected as P13-S1 plan-review only**. |
| **E1-E3 / Evidence Confirm audit architecture** | High: improves evidence-to-claim correctness. | High: v2 architecture, possible LLM/repair semantics, PDF search confirmation, new audit contracts. | Needs separate design; must not borrow Dayu runtime. | Defer to future audit architecture phase. |
| **Repo-hygiene from repo-audit D-1, D-8/C-5, C-9** | Medium: improves maintainability and handoff clarity. | Medium: touches design/control/review organization and may publish stale repo-audit facts. | Good as docs-only phase, but lower product impact. | Defer unless product work is blocked by repo confusion. |
| **RR-13 duplicate `016492` handling** | Medium: source-pool correctness. | High without human truth; unsafe for agent inference. | Not implementable by code alone. | Keep human-owned; use only as blocker if P13 needs selected-pool identity. |

## 5. Recommended P13-S1 Scope

P13-S1 should create a reviewed implementation plan, not code. The plan must answer:

1. Which data is needed to replace current placeholders:
   - tracking error value and period;
   - tracking-error source or calculation inputs;
   - benchmark/index identity used for calculation;
   - index methodology summary if disclosed;
   - index constituents or constituent source reference if available.
2. Which source path is authoritative:
   - annual report / prospectus / index announcement via `FundDocumentRepository`;
   - existing NAV adapter only if it already has explicit provenance;
   - any new external index series adapter only after source, cache, identity, and failure taxonomy are designed.
3. Which structured contract changes are required:
   - add explicit fields to Fund Capability data models rather than `extra_payload`;
   - preserve evidence anchors for every numeric judgment;
   - keep missing paths as `missing` / `insufficient_data`, not inferred values.
4. How renderer/audit should consume data:
   - renderer may replace `数据不足` only when structured data has provenance;
   - programmatic audit should verify anchor presence and no benchmark anchor is misused as proof of methodology/constituents/tracking error;
   - no E1/E2/E3 semantic evidence matching in P13.
5. How tests prove correctness:
   - deterministic fixture for index fund;
   - deterministic fixture for enhanced index;
   - missing-source path remains `数据不足`;
   - identity mismatch / schema drift / integrity error fail closed if new document/source lookup is added.

## 6. Non-goals

- Do not implement code in this next-phase selection gate.
- Do not introduce LLM writing, LLM audit, Evidence Confirm, RepairContract execution, Dayu Host, Dayu Engine, Dayu tool loop, or external Dayu runtime.
- Do not let UI, Service, Engine, renderer, or quality gate call concrete document sources, PDF cache helpers, or download helpers directly.
- Do not put explicit parameters in `extra_payload`.
- Do not treat benchmark text as evidence for tracking error, index methodology, or constituents.
- Do not alter RR-13 source data or infer which duplicate `016492` row is correct.
- Do not edit, stage, publish, delete, or normalize `docs/repo-audit-20260521.md`.
- Do not combine P13 with repo-hygiene D-1/D-8/C-5/C-9.
- Do not update `docs/design.md` or `docs/implementation-control.md` during this selection gate.

## 7. Allowed / Disallowed Files

For this selection task:

- Allowed: `docs/reviews/next-phase-selection-20260522.md`.
- Disallowed: every other file.

For the recommended P13-S1 plan-review gate:

- Allowed:
  - `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`
  - optional plan-review artifacts under `docs/reviews/`
- Disallowed:
  - `fund_agent/`
  - `tests/`
  - README files
  - `docs/design.md`
  - `docs/implementation-control.md`
  - `docs/repo-audit-20260521.md`
  - RR-13 source data, including selected-fund CSV rows

For a later P13 implementation gate, file permissions must be re-declared by the accepted P13-S1 plan. The likely ownership is Fund Capability only, with tests. Service/UI changes are disallowed unless the plan proves a public contract needs a typed field and review accepts it.

## 8. Code-Generation-Ready Plan Requirements For P13-S1

The P13-S1 plan must include these concrete implementation slices before any code is generated:

| Slice | Required planning output | Boundary rule |
|---|---|---|
| Source contract | Source list, identity checks, failure taxonomy, cache/provenance model, and fallback eligibility. | All document access through `FundDocumentRepository`. |
| Data model | Explicit typed fields for tracking error, period, benchmark/index identity, methodology, constituents, and evidence anchors. | No `extra_payload` parameter hiding. |
| Extraction/calculation | Decision whether to extract disclosed tracking error or calculate from fund/index time series; formula and input provenance. | No silent estimation; missing inputs remain `insufficient_data`. |
| Renderer integration | Exact replacement rules for current `数据不足` bullets in Chapter 1 and Chapter 2. | Renderer consumes structured Capability data only. |
| Programmatic audit | Deterministic checks for anchor presence and source-type misuse. | No E1/E2/E3 semantic audit. |
| Tests | Targeted unit/integration matrix and fixtures. | Cover index, enhanced-index, and missing-data paths. |
| Docs sync for later implementation | README/design/control update triggers if public contract or design facts change. | Not part of P13-S1 planning gate unless explicitly allowed later. |

## 9. Review Criteria

P13-S1 plan review must reject the plan if any of these are true:

- It starts implementation instead of planning.
- It allows Service/UI direct access to document sources, PDF cache, concrete source adapters, or download helpers.
- It adds Dayu Host/Engine/tool loop/runtime dependency.
- It introduces LLM writing or Evidence Confirm execution.
- It mixes repo-hygiene or RR-13 resolution into P13.
- It relies on benchmark anchors to prove tracking error, methodology, or constituents.
- It omits missing-data behavior for current placeholders.
- It omits failure taxonomy for any new source or external index series lookup.
- It does not define exact future allowed files and tests.

P13-S1 plan review should pass only if the implementation can be handed to a coding agent without requiring architectural guessing.

## 10. Validation Commands

For this selection artifact:

```bash
git diff --name-only HEAD
git diff --check HEAD
```

Expected:

- `git diff --name-only HEAD` includes only `docs/reviews/next-phase-selection-20260522.md`.
- `docs/repo-audit-20260521.md` may remain untracked but must not be modified, staged, or deleted.

For P13-S1 plan-review:

```bash
git status --short
git diff --name-only HEAD
git diff --check HEAD
```

Expected:

- Only P13-S1 planning/review artifacts are changed.
- No source/test/README/design/control/repo-audit/RR-13 files are changed.

For later P13 implementation, the accepted P13-S1 plan must define targeted pytest commands. Minimum expected validation should include:

```bash
pytest tests/fund/template tests/fund/audit
pytest tests/fund/extractors tests/fund/analysis
ruff check fund_agent tests
git diff --check HEAD
```

Full `pytest` should be required before implementation acceptance if public data models, renderer output, or audit behavior changes.

## 11. Residual Owners

| Residual | Owner / destination | Handling |
|---|---|---|
| P13 tracking-error / index-data capability | Future P13 Fund Capability planning and implementation | Selected next as P13-S1 plan-review only. |
| E1-E3 / Evidence Confirm | Future audit architecture phase | Defer; keep separate from P13 data capability. |
| Repo-hygiene D-1 project structure tree | Future repo-hygiene phase | Defer; do not edit design now. |
| Repo-hygiene D-8/C-5 `fund/tools` fact check | Future repo-hygiene phase | Defer; do not delete or normalize now. |
| Repo-hygiene C-9 `docs/reviews/` growth | Future repo-hygiene phase | Defer; requires archival policy. |
| RR-13 duplicate `016492` | User / App source | Preserve as human-owned; if P13 needs selected-pool identity, stop and request user decision. |
| `docs/repo-audit-20260521.md` | Controller / user | Keep excluded; future repo-hygiene may explicitly publish/archive/delete with approval. |

## 12. Stop Conditions

Stop the next gate and return to controller if:

- implementation starts before a P13-S1 plan review is accepted;
- any file outside the allowed P13-S1 planning artifacts must change;
- RR-13 source truth is required to proceed;
- `docs/repo-audit-20260521.md` would need editing, staging, deletion, or publication;
- the plan cannot keep document/source access inside Fund Capability and `FundDocumentRepository`;
- a reviewer requests mixing E1-E3/Evidence Confirm with P13 tracking-error/index-data;
- validation shows unexpected source/test/README/design/control changes.

## 13. Controller Handoff

Recommended next prompt:

```text
Gate: P13-S1 tracking-error / index-data source contract plan-review.

Use `docs/reviews/next-phase-selection-20260522.md` as the accepted next-phase selection input.

Create `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`.
Do not modify source/tests/README/design/control/repo-audit/RR-13 data.

The plan must define explicit Fund Capability source contracts for tracking error, index methodology, and constituents; require all document access through `FundDocumentRepository`; keep Service/UI out of source internals; avoid Dayu runtime, LLM writing, Evidence Confirm, and E1-E3 execution; and preserve missing-data behavior until real structured data exists.

Stop if RR-13 source truth, repo-audit publication/deletion, Service/UI source access, or audit-architecture mixing becomes necessary.
```
