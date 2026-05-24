# Release Maintenance 004393 Quality Gate Plan Handoff - 2026-05-24 08:06:33

## Controller Context

- Current phase: `release maintenance`
- Current gate: `release-maintenance candidate selection / plan-review`
- Selected candidate for planning: `004393/2024 quality gate block root-cause investigation`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Rule entry: `AGENTS.md`

This is a planning handoff only. Do not implement source, tests, config, runtime behavior, golden answers, or README changes in this gate.

## Current Truth Guardrails

- Current truth is limited to `AGENTS.md`, current sections of `docs/design.md`, and `docs/implementation-control.md` Startup Packet / current gate.
- `docs/reviews/` and implementation-control archive old six-layer, Application, Runtime, or Engine wording are historical evidence only, not current architecture.
- Current target architecture is Dayu four-layer `UI -> Service -> Host -> Agent`; current deterministic mainline is UI -> Service -> `fund_agent/fund`.
- Do not create placeholder `fund_agent/host` or `fund_agent/agent` packages.
- If a future plan needs Host, it must use `dayu.host`; if it needs Agent execution kernel/tool-loop/runner/ToolRegistry/ToolTrace, it must use `dayu.engine`.
- Annual report access must remain through `FundDocumentRepository` / `FundDataExtractor`; no direct production PDF/cache/source helper access outside the document repository boundary.
- Explicit business parameters must be typed request/contract/config fields, not `extra_payload` or free dicts.

## Candidate Input

The user identified a quality gate block around `004393/2024`. The planning task is not to bypass the quality gate; it is to plan root-cause fixes for real extraction, applicability, and correctness-normalization issues.

Required candidate facts to incorporate:

1. `basic_identity`: the 2024 annual report §2 has `management_company`, `custodian`, and `inception_date`, but current `basic_identity` does not expose these comparable fields.
2. `fee_schedule`: annual report §7.4.10.2 discloses management fee `1.20%` and custodian fee `0.20%`; current extractor only searches §2 for fee rates, causing P0 missing.
3. `holdings_snapshot`: annual report §8 has industry distribution and "all stock investment details"; current rules only search "top ten" and "heavy holdings", missing the available evidence.
4. `share_change`: annual report §10 table is split by parser into a header table and a data table; current extraction cannot inherit A/C share-class headers from the previous table, causing multi-column ambiguity.
5. `benchmark mismatch`: extractor output containing `中债综合` is a reasonable visual newline normalization issue; the plan must decide whether the fix belongs in golden answer update, correctness normalization, or both.
6. `turnover_rate`: do not plan this as a `004393/2024` direct extraction bug. 2024 annual reports are not governed by the periodic-report/XBRL stock turnover disclosure rules effective 2026-05-01. For report years before 2026 where disclosure is not mandatory and the report does not directly disclose stock turnover, missing `turnover_rate` should be modeled as disclosure applicability, not ordinary P1 extraction failure or missing-field-rate penalty.

## Required Planning Output

Produce a code-generation-ready implementation plan artifact under `docs/reviews/` with a stable descriptive filename. The plan must include:

- Goal and success signal.
- Non-goals, especially no quality gate bypass, no direct turnover derivation pretending to be disclosed turnover, no Host/Agent package creation, no direct PDF/cache access outside repository boundary.
- Direct evidence to verify before implementation, including which annual report sections/tables must be inspected and how to inspect them through existing repository/extractor interfaces.
- Affected files/modules and ownership boundaries.
- Contract/schema decisions for each candidate field:
  - whether `basic_identity` comparable fields require schema/golden/test updates;
  - whether `fee_schedule` fallback to §7.4.10.2 is extraction-only or also scoring/golden;
  - whether `holdings_snapshot` should use "all stock investment details" as top-10 source and how industry continuation is handled;
  - how `share_change` continuation headers should be represented without hardcoding a single parser artifact;
  - whether benchmark normalization belongs in correctness normalization, golden answer, or extractor output normalization;
  - how turnover disclosure applicability statuses should be named and where they belong.
- Proposed implementation slices small enough for Gateflow:
  - P0 extraction/comparable fields slice;
  - P1 extraction/correctness slice;
  - quality gate disclosure-applicability slice if selected;
  - golden/correctness fixture update slice if needed.
- Tests and validation commands with expected assertions, including failure paths.
- Residual risks and stop conditions.
- Completion report format for implementation agents.

## Candidate Prioritization Guidance

Prefer a plan that handles the direct blockers first:

- P0: `basic_identity` comparable fields and `fee_schedule` §7.4.10.2 fallback.
- P1: `holdings_snapshot`, `share_change`, and benchmark correctness normalization/golden decision.
- Separate quality-gate applicability: `turnover_rate` pre-2026 disclosure applicability and denominator handling.

If the plan finds that the turnover applicability work is larger than the extraction fixes, it should split that into a follow-up Gateflow candidate rather than coupling all behavior into one broad slice.

## Review Expectations

The plan will be adversarially reviewed for:

- Four-layer boundary compliance.
- Document repository boundary compliance.
- No direct implementation disguised as planning.
- No hardcoded one-fund fix when a rule should be adaptive.
- No derived turnover proxy masquerading as direct `turnover_rate`.
- Clear tests proving both improved extraction and non-regression of quality gate semantics.
