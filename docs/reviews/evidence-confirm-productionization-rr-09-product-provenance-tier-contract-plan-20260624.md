# RR-09 Product Provenance Tier Contract Plan

Final token:

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_PLAN_READY_FOR_REVIEW_NOT_READY`

## Gate

Gate: `RR-09 Product Provenance Tier Contract Planning Gate`.

Authorization: user accepted entering the next gate after `RR-09 Product Provenance Scope Decision`.

Classification: `heavy`, because the next implementation changes a public safety summary contract and ECQ disposition semantics for product provenance blockers.

This is a planning artifact only. It does not change production code, tests, runtime behavior, quality-gate output, checklist support, report-body rendering, provider/LLM defaults, PR state, tag, release or readiness. It does not run live/PDF, repository/source-helper/parser, product CLI or provider/LLM commands.

## Goal

Turn the accepted pragmatic provenance scope into a code-generation-ready implementation contract:

- product claims need repository-bounded provenance at `section` or better;
- `section` is the minimum current release floor, not row/value proof;
- `table` and `row` are stronger tiers when existing materialized references support them;
- `cell` is a reserved tier because current `EvidenceConfirmReference` has no independent cell field;
- strict deterministic V2 value-match failures become `strict_precision_residual` only when provenance exists;
- pathway failure and claim-level missing provenance remain blockers;
- safe CLI/UI/ECQ output must make the distinction visible without raw excerpts or paths.

Success signal for this planning gate: a reviewer can implement the approved slices without redesigning data ownership, tier names, issue routing, file scope or tests.

## Direct Code Evidence

- `fund_agent/fund/evidence_confirm_production.py` defines `EvidenceConfirmProductionSummary` v1. It currently contains policy/status/pathway/deterministic/semantic counts and issue ids, but no provenance tier or strict-precision residual field.
- `fund_agent/fund/evidence_confirm_sources.py` returns `EvidenceConfirmRepositoryRunResult` with `reference_build_result.references`; each `EvidenceConfirmReference` has `section_id`, `table_id` and `row_locator`, but no cell locator.
- `fund_agent/fund/evidence_confirm.py` V2 separates `source_support`, `missing_evidence` and `value_match` dimensions. This allows provenance presence to be determined separately from exact value matching.
- `fund_agent/fund/quality_gate_integration.py` maps compact summary to ECQ0-ECQ4 and does not read repository/PDF/source/parser/provider. ECQ2 currently treats any deterministic fail as `deterministic_fail_N`.
- `fund_agent/ui/cli.py` emits safe Evidence Confirm summary lines and currently prints status/policy/checked/failed/auditability only.
- `docs/design.md` states default product `analyze` uses Evidence Confirm `warn`, CLI/UI display safe summary, report body does not render Evidence Confirm, checklist remains off, provider-backed semantic default-on remains future scope, and release/readiness is `NOT_READY`.

## Non-goals

- No live/PDF, repository/source-helper/parser or product CLI execution.
- No provider/LLM execution or provider-backed semantic default-on.
- No report-body Evidence Confirm rendering and no evidence appendix change.
- No checklist Evidence Confirm support.
- No FDD default-on parsing or direct Docling/pdfplumber/EID HTML consumption outside Fund documents/Processor boundaries.
- No row/cell proof invention from section/table excerpts.
- No release, tag, PR external mutation or readiness claim.
- No broad rewrite of V2 matcher, reference materializer, extractor or quality gate framework.

## Contract

### Provenance tiers

Closed tier order:

```text
none < section < table < row < cell
```

Definitions for this implementation:

| Tier | Current producer condition | Meaning |
|---|---|---|
| `none` | no proven repository-bounded reference for a checked claim | claim provenance missing |
| `section` | proven reference has `section_id` but no `table_id` / `row_locator` | acceptable current release floor |
| `table` | proven reference has `table_id` but no `row_locator` | stronger than section, not row proof |
| `row` | proven reference has `row_locator` | row-level provenance exists |
| `cell` | reserved; no current producer because `EvidenceConfirmReference` has no cell field | must not be emitted in this slice |

### Summary fields

Upgrade `EvidenceConfirmProductionSummary` from v1 to v2 and add safe scalar fields only:

```python
EvidenceConfirmProvenanceTier = Literal["none", "section", "table", "row", "cell"]
EvidenceConfirmProvenanceStatus = Literal["pass", "fail", "not_run"]

provenance_status: EvidenceConfirmProvenanceStatus
minimum_provenance_tier: EvidenceConfirmProvenanceTier
provenance_missing_fact_count: int
strict_precision_residual_count: int
strict_precision_issue_ids: tuple[str, ...]
```

Rules:

- `schema_version` becomes `evidence_confirm_production_summary.v2`.
- `provenance_status="not_run"` and `minimum_provenance_tier="none"` when Evidence Confirm is not run or repository/pathway failed before V2 facts exist.
- `provenance_status="fail"` when any checked non-derived/non-not-applicable fact has `source_support` or `missing_evidence` fail.
- `provenance_status="pass"` only when every checked applicable fact has section-or-better proven provenance.
- `minimum_provenance_tier` is the minimum tier across applicable facts after each fact is assigned its strongest matched proven reference tier.
- `strict_precision_residual_count` counts applicable facts where provenance passes but `value_match` fails.
- `strict_precision_issue_ids` contains the stable issue ids from failing `value_match` dimensions for those residual facts.
- No raw excerpt, PDF/cache path, parser payload, provider payload, source URL or full value may enter the summary.

### Tier computation

Implementation should add private helpers in `fund_agent/fund/evidence_confirm_production.py`:

- `_reference_tier(reference: EvidenceConfirmReference) -> EvidenceConfirmProvenanceTier`
- `_strongest_tier(tiers: Iterable[EvidenceConfirmProvenanceTier]) -> EvidenceConfirmProvenanceTier`
- `_weakest_tier(tiers: Iterable[EvidenceConfirmProvenanceTier]) -> EvidenceConfirmProvenanceTier`
- `_dimension_by_name(fact_result: EvidenceConfirmFactResultV2, name: EvidenceConfirmDimension) -> EvidenceConfirmDimensionResult | None`
- `_provenance_contract_from_result(result: EvidenceConfirmRepositoryRunResult) -> ...`

The helper may use only:

- `result.reference_build_result.references`;
- `result.evidence_confirm_result.fact_results`;
- V2 dimension names/statuses/issue ids/matched anchor ids;
- reference metadata fields.

It must not read repository, PDF/cache/source-helper/parser/provider/LLM or report body.

Fact-level provenance pass condition:

- `source_support.status == "pass"`;
- `missing_evidence.status == "pass"`;
- at least one matched anchor maps to a proven reference whose tier is `section`, `table` or `row`.

Fact-level missing provenance condition:

- `source_support.status == "fail"` or `missing_evidence.status == "fail"`;
- or the matched-anchor tier lookup yields only `none`.

Fact-level strict precision residual condition:

- provenance pass condition is true;
- `value_match.status == "fail"`.

Derived and `not_applicable` facts keep the existing V2 boundary: they do not create missing-provenance blockers or strict precision residuals.

### ECQ mapping

Implementation should update only `_evidence_confirm_quality_gate_issues()` in `fund_agent/fund/quality_gate_integration.py`.

Rules:

- `ECQ0`: unchanged for not-run.
- `ECQ1`: repository/source/reference pathway failure remains a provenance blocker. Severity must be `block` regardless of Evidence Confirm policy because the approved product contract requires a controlled document pathway before user-visible provenance claims.
- `ECQ2`: deterministic fail splits by summary fields:
  - if `summary.provenance_status == "fail"`, emit `ECQ2/block` with reason `provenance_missing_<count>`;
  - else if `summary.strict_precision_residual_count > 0`, emit `ECQ2` with reason `strict_precision_residual_<count>` and severity from policy (`warn` under product `warn`, `block` under `block`);
  - else keep a fallback deterministic fail reason for defensive compatibility.
- `ECQ3`: deterministic warn remains `warn`.
- `ECQ4`: semantic companion mapping unchanged.

This is the only accepted quality-gate semantic change for the implementation slice: provenance/pathway absence is a blocker; strict precision residual follows policy.

### CLI safe summary

Update `_echo_evidence_confirm_summary()` in `fund_agent/ui/cli.py` to append safe lines when fields exist:

```text
evidence_confirm_provenance_status: pass|fail|not_run
evidence_confirm_min_provenance_tier: none|section|table|row|cell
evidence_confirm_provenance_missing_facts: N
evidence_confirm_strict_precision_residuals: N
```

Do not print issue ids in CLI. Do not print raw excerpts, paths, source URLs, parser payloads, provider payloads or report body.

### Service behavior

No Service orchestration change is required except updating the runner-exception summary constructor in `fund_agent/services/fund_analysis_service.py` to the v2 summary schema and default provenance fields:

- `provenance_status="not_run"`;
- `minimum_provenance_tier="none"`;
- counts `0`;
- `strict_precision_issue_ids=()`.

`checklist` remains Evidence Confirm `off`. `analyze-annual-period` inherits current-year summary through the existing `analyze()` path.

## Implementation Slices

### Slice S1: Summary V2 Provenance Contract

Allowed files:

- `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/services/fund_analysis_service.py`
- `tests/fund/test_evidence_confirm_production.py`

Exact changes:

- define provenance tier/status type aliases;
- upgrade `SUMMARY_SCHEMA_VERSION` and `EvidenceConfirmProductionSummary.schema_version` to v2;
- add v2 fields listed above;
- compute provenance status, minimum tier and strict precision residuals from V2 dimensions and reference metadata;
- update not-run and runner-exception constructors;
- update tests/factories to construct V2 dimension results and reference build results;
- add focused tests:
  - section-only reference produces `provenance_status=pass`, `minimum_provenance_tier=section`;
  - table and row references produce stronger tiers without emitting `cell`;
  - missing `source_support` / `missing_evidence` produces `provenance_status=fail` and increments `provenance_missing_fact_count`;
  - `value_match` fail with section-or-better provenance increments `strict_precision_residual_count` and keeps issue ids;
  - repository/pathway failure remains compact and sets provenance `not_run`;
  - summary payload still has no excerpt/path/parser/provider leakage.

Validation command:

```bash
uv run pytest tests/fund/test_evidence_confirm_production.py
```

### Slice S2: ECQ And CLI Safe Visibility

Allowed files:

- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/ui/test_cli.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

Exact changes:

- update ECQ1 severity to `block` for pathway failure;
- update ECQ2 reason/severity split for `provenance_missing` vs `strict_precision_residual`;
- append CLI safe summary lines for provenance status/tier/counts;
- update test helpers to build v2 summary objects;
- add focused tests:
  - pathway failure with policy `warn` emits ECQ1/block;
  - provenance missing emits ECQ2/block with `provenance_missing_N`;
  - strict precision residual with policy `warn` emits ECQ2/warn with `strict_precision_residual_N`;
  - strict precision residual with policy `block` emits ECQ2/block;
  - CLI prints provenance safe lines and does not print issue ids/raw fields;
  - checklist help still does not expose Evidence Confirm policy;
  - report body remains absent when quality gate blocks.
- update Fund README and design current-state wording to describe provenance tiers and strict precision residuals; keep checklist/report-body/provider/release boundaries unchanged.

Validation commands:

```bash
uv run pytest tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py
git diff --check -- fund_agent/fund/evidence_confirm_production.py fund_agent/services/fund_analysis_service.py fund_agent/fund/quality_gate_integration.py fund_agent/ui/cli.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py fund_agent/fund/README.md docs/design.md
```

## Expected User-visible Semantics After Implementation

Under default product `warn`:

- no repository/source/reference pathway -> block, no unsupported provenance claim;
- no claim provenance -> block, no unsupported provenance claim;
- section-or-better provenance + strict value-match fail -> report may continue, CLI/ECQ shows strict precision residual;
- row/table availability improves tier display but is not required for current release floor;
- report body still does not include Evidence Confirm content.

Under explicit developer `block`:

- strict precision residual blocks through ECQ2/block.

## Docs Decision

Because the implementation changes Fund summary and ECQ product semantics, update:

- `fund_agent/fund/README.md`: Evidence Confirm production summary and ECQ table.
- `docs/design.md`: current-state Evidence Confirm default-on / pragmatic provenance tier wording.

Do not update root README unless CLI command syntax changes. Do not update checklist or renderer docs because their behavior remains unchanged.

## Risks And Residuals

| Risk | Disposition |
|---|---|
| Current model cannot emit `cell` tier | Accepted residual; `cell` is reserved and must not be emitted until a future reference model gate adds proof-bearing cell metadata |
| Existing live R1-R4 strict V2 failures remain unmeasured after this contract | Assigned to optional A6 strict-precision evidence path; not required for this no-live contract implementation |
| B1 `017641 / 2024` manager strategy quality-gate block remains open | Separate RR-09 residual; not solved by provenance tier contract |
| Report-body sentence-level provenance remains unproven | Deferred by RR-S6; not part of current release floor |
| Provider-backed semantic default-on remains unproven | Deferred to future provider policy gate |

## Why This Is Not Over-designed

The plan adds only the minimum missing contract fields required to distinguish provenance absence from strict precision failure. It reuses current V2 dimensions, current materialized reference metadata, current ECQ family and current CLI safe-summary surface. It does not add a new auditor, new parser, new repository access path, report-body UX, provider default or live harness.

## Completion Report Format

Implementation closeout should report:

- changed files;
- completed slices;
- focused test commands and results;
- ECQ behavior matrix for pathway fail / provenance missing / strict precision residual;
- docs updates;
- residuals preserved;
- explicit statement that no live/PDF/product CLI/provider/checklist/report-body/tag/release/readiness action was performed.

Completion token:

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_PLAN_READY_FOR_REVIEW_NOT_READY`
