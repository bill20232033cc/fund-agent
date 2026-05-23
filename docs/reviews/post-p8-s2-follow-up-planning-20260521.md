# Post-P8-S2 Follow-up Planning（2026-05-21）

## Current State

P8-S2 `renderer preferred_lens application` implementation and controller review are complete.

Accepted commits:

- `f55ef76`：P8-S2 renderer preferred_lens application plan/review
- `6dbf6ca`：P8-S2 renderer preferred_lens application implementation
- `1e0031b`：P8-S2 controller code review artifact and control-doc gate update

Latest verified baseline:

```text
targeted -> 67 passed
pytest -> 344 passed
ruff check -> passed
git diff --check -> passed
```

Tracked worktree was clean after the P8-S2 review commit. Existing untracked local/generated artifacts remain outside this gate.

## Residual Reconciliation

### Closed by P8-S1

`R1. must_answer Audit Consumption` is closed for deterministic contract-routing.

Current fact:

- `ContractAuditCoverageManifest` covers all 45 current `CHAPTER_CONTRACT.must_answer` questions.
- Coverage routes are explicit and separate from deterministic `ProgrammaticContractRules`.
- Non-programmatic routes do not claim semantic C2 proof.

Remaining future work:

- LLM semantic audit, evidence confirm, and structured-data availability remain future audit slices.
- C2 marker granularity is no longer a standalone blocker unless a concrete required item proves too broad in practice.

### Closed by P8-S2

`R2. Renderer preferred_lens Application` is closed for deterministic renderer application.

Current fact:

- `LensApplicationPlan` is Capability-owned in `fund_agent/fund/template/lens_application.py`.
- Renderer consumes the plan only in Chapter 0/1 deterministic slots.
- Raw `TemplateLensRule.statements` are trace data and are not rendered into final report Markdown.
- `TemplateRenderResult.lens_application_plan` exposes the application facts for tests and later audit.
- `ProgrammaticAuditInput` shape is unchanged.

Remaining future work:

- Broader lens-to-evidence requirements and renderer-compliance audit remain deferred design slices.
- P8-S2 does not make FQ5 prove renderer compliance; FQ5 remains template applicability.

## Next Highest Priority

`R3. EID Schema Error Fallback Policy` is now the next design item.

Current code facts:

- `AnnualReportSourceOrchestrator` lives in `fund_agent/fund/documents/sources.py`.
- Default source order is EID primary, Eastmoney fallback.
- `AnnualReportSourceFailure.category` currently only records `not_found` and `unavailable`.
- `AnnualReportSourceNotFoundError` and `AnnualReportSourceUnavailableError` are fallback-eligible.
- `AnnualReportSourceMismatchError` and `AnnualReportSourceSchemaError` fail closed immediately and block fallback.
- Existing tests already cover:
  - EID `not_found` -> fallback can be used.
  - EID `unavailable` -> fallback can be used.
  - EID `mismatch` -> fallback blocked.
  - EID `schema` -> fallback blocked.
  - fallback result metadata sets `fallback_used=True` when prior source failures occurred.

The current behavior is conservative, but the policy is implicit in exception control flow. It does not yet expose a table-driven taxonomy for `schema_drift`, `identity_mismatch`, or `integrity_error`, nor does it record a structured “fallback was blocked by official-source drift” decision.

## Controller Decision

Proceed to:

```text
P8-S3 source fallback policy design plan/review
```

This must be a design-first slice.

Rationale:

- 年报来源直接影响证据真源，不能用商业站 fallback 静默掩盖官方来源漂移或身份矛盾。
- 当前实现的 fail-closed 行为方向正确，但类别粒度不足，后续维护者难以判断新增异常是否可 fallback。
- 设计应先固定错误分类、fallback eligibility 和 provenance，再让 implementation agent 修改 source orchestration。

## P8-S3 Design Scope

Goal:

- Formalize source error taxonomy and fallback eligibility for annual report PDF retrieval.

Required design decisions:

1. Error taxonomy
   - `not_found`
   - `unavailable`
   - `schema_drift`
   - `identity_mismatch`
   - `integrity_error`

2. Fallback eligibility
   - which categories can continue to the next source
   - which categories must block fallback
   - whether eligibility depends on official primary source vs fallback source

3. Provenance
   - how to record fallback-used success
   - how to record fallback-blocked fail-closed decisions
   - whether metadata belongs in `AnnualReportSourceFailure`, `AnnualReportSourceAggregateError`, `AnnualReportSourceMetadata`, or a new policy decision model

4. Public boundary
   - all fund document access remains through `FundDocumentRepository`
   - source orchestration stays inside Fund Capability documents layer
   - no UI/Service/Engine changes unless needed to surface existing exception messages

5. Tests
   - table-driven policy tests
   - EID schema drift blocks fallback with structured category
   - EID identity mismatch blocks fallback with structured category
   - EID integrity error blocks fallback with structured category
   - EID not-found/unavailable still allow Eastmoney fallback
   - blocked fallback records source/category/message provenance

## Initial Preferred Approach For P8-S3 Plan

Keep source policy in the Fund Capability document source layer:

```text
fund_agent/fund/documents/sources.py
```

Likely implementation direction:

- Add an `AnnualReportSourceFailureCategory` literal or enum for the five accepted categories.
- Extend `AnnualReportSourceFailure.category` from two categories to the full taxonomy.
- Introduce a small policy helper such as `can_fallback_after_failure(source_name, category)` or a table constant.
- Map existing exceptions into structured categories:
  - `AnnualReportSourceNotFoundError` -> `not_found`
  - `AnnualReportSourceUnavailableError` -> `unavailable`
  - `AnnualReportSourceSchemaError` -> `schema_drift` by default
  - `AnnualReportSourceMismatchError` -> `identity_mismatch`
  - invalid PDF response / missing `%PDF-` -> `integrity_error`
- Preserve current conservative behavior:
  - `not_found` and `unavailable` may fallback.
  - `schema_drift`, `identity_mismatch`, and `integrity_error` block fallback.
- Add structured failure data to the raised exception when fallback is blocked, so logs/tests can distinguish “no source worked” from “official source drift blocked fallback.”

Non-goals:

- Do not change the default source order.
- Do not add a third source.
- Do not expose source orchestration outside `FundDocumentRepository`.
- Do not weaken EID fail-closed behavior to improve availability.
- Do not make Eastmoney a peer primary source.

## Acceptance Criteria For P8-S3 Plan/Review

- Plan contains a table mapping every source exception/failure mode to the five-category taxonomy.
- Plan contains an explicit fallback eligibility table.
- Plan explains why official-source schema drift, identity mismatch, and integrity errors must block fallback.
- Plan specifies structured provenance for both fallback-used and fallback-blocked paths.
- Plan assigns implementation ownership only to Fund Capability document source code and tests unless a stronger reason is documented.
- Plan includes targeted tests and full verification commands.

## Deferred Items

These remain behind P8-S3 unless user reprioritizes:

- `P8-S4 preflight quality gate optimization design`
- LLM semantic audit / evidence confirm for non-programmatic `must_answer`
- Further C2 marker granularity hardening only when tied to a concrete audit weakness

## Next Gate

```text
P8-S3 source fallback policy design plan/review
```
