# Evidence Confirm Productionization RR-09 B1 / R1-R4 Live Re-evidence Authorization Precheck

Verdict token:

`RR_09_B1_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`

## Scope

Gate: `RR-09 B1 Runtime Re-evidence Authorization / R1-R4 Live/PDF Re-evidence Gate`.

This artifact records the post-A3 authorization precheck only. It does not run repository-bounded live/PDF diagnostics, does not run `fund-analysis analyze`, does not read annual-report/PDF bodies, does not call provider/LLM, and does not change V2, ECQ, quality-gate semantics, checklist support, report-body rendering, PR state, tag, release or readiness.

## Current Accepted Inputs

Accepted A3 chain:

- A3 plan/controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a3-plan-controller-judgment-20260624.md`
- A3 no-live implementation evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a3-implementation-evidence-20260624.md`
- A3 code review judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a3-code-review-controller-judgment-20260624.md`
- Accepted implementation commit: `2fbbd92`

Accepted A3 behavior:

- Available `bond_risk_evidence` group refs are projected into ordinary annual-report chapter anchors.
- Semantic table row locators narrow only when exactly one available non-derived non-synthetic fact is attached to the anchor and all deterministic V2 material tokens uniquely match one parsed table row.
- Unsafe cases still downgrade to table/section proof references with E1 precision warning.

Accepted A2-S2 diagnostic facts before A3:

- R1/R2/R4 strict V2 failures classified as `coarse_reference_insufficient`.
- R3 strict V2 failures classified as `coarse_reference_insufficient` plus `bond_risk_group_anchor_projection_gap`.
- EID `single_source_only`, fallback disabled/unused and metadata admission were proven for all four R1-R4 samples.
- Reference materialization was already nonzero before A3.

Accepted B1 no-live chain:

- B1 implementation evidence: `docs/reviews/evidence-confirm-productionization-rr-09-b1-manager-strategy-qdii-implementation-evidence-20260624.md`
- B1 aggregate judgment: `docs/reviews/evidence-confirm-productionization-rr-09-b1-aggregate-deepreview-controller-judgment-20260624.md`
- Accepted slice commit: `4f4c00b`

## Authorization Boundary

Two executable gates are prepared but still require exact user authorization.

### Option A: R1-R4 Live/PDF Re-evidence After A3

Required exact authorization should name:

`授权 RR-09 R1-R4 live/PDF re-evidence after A3 no-live fixes`

Intended samples:

| Residual | Sample |
|---|---|
| R1 | `004393 / 2025` |
| R2 | `004194 / 2024` |
| R3 | `006597 / 2024` |
| R4 | `110020 / 2024` |

Allowed command shape after authorization:

```bash
uv run python - <<'PY'
...
bundle = await FundDataExtractor().extract(fund_code, report_year, force_refresh=True)
projection = project_chapter_facts(bundle)
runner_result = await run_repository_bounded_evidence_confirm(
    EvidenceConfirmRepositoryRunRequest(
        fund_code=fund_code,
        report_year=report_year,
        projection=projection,
        force_refresh=False,
    )
)
diagnostic = summarize_value_match_diagnostics(
    projection=projection,
    references=runner_result.reference_build_result.references,
    result=runner_result.evidence_confirm_result,
)
...
PY
```

Allowed evidence fields:

- command exit code;
- sample id;
- selected source and source mode;
- fallback enabled / fallback used;
- metadata admitted flag;
- document identity match for fund code and report year;
- reference build status, reference count and issue reason counts;
- strict V2 overall status, score and checked/fail/warn/not-applicable counts;
- failing dimensions and source-field buckets;
- value diagnostic classification counts;
- whether R3 `structured.bond_risk_evidence` missing-evidence closed;
- whether former coarse-reference failures now pass, remain fail, or become a narrower residual;
- statement that output is safe aggregate metadata only.

Forbidden evidence fields:

- raw annual-report excerpt text;
- raw scalar token values;
- full structured fact values;
- PDF/cache paths;
- URLs;
- source-helper internals;
- provider payloads;
- report body text;
- API keys, secrets or tracebacks.

Stop conditions:

- Stop and classify fail-closed if source provenance is not EID `single_source_only`.
- Stop and classify fail-closed if fallback is enabled or used.
- Stop and classify fail-closed on identity mismatch, schema drift, integrity error, unsupported source or ambiguous repository failure.
- Stop if the command path bypasses `FundDocumentRepository` / `FundDataExtractor` / `run_repository_bounded_evidence_confirm()`.
- Stop if strict V2 remains fail after A3; write residual classification, do not claim release/readiness.
- Stop if output would require raw excerpts, raw token values, PDF/cache paths or source-helper internals to interpret.

Expected artifact after authorization:

- `docs/reviews/evidence-confirm-productionization-rr-09-a3-live-pdf-reevidence-20260624.md`

### Option B: B1 Runtime Product CLI Re-evidence

Required exact authorization should name:

`授权 RR-09 B1 runtime product CLI re-evidence for 017641 / 2024`

Intended sample:

| Residual | Sample | Purpose |
|---|---|---|
| R5a | `017641 / 2024` | Verify product CLI behavior after accepted B1 `manager_strategy_text` QDII no-live fix and Branch F blocked-path EC summary propagation. |

Allowed command shape after authorization:

```bash
uv run fund-analysis analyze 017641 --report-year 2024 --valuation-state unavailable --force-refresh
```

Allowed evidence fields:

- command exit code;
- stdout presence/absence and safe high-level shape;
- stderr quality-gate status;
- quality-gate issue family/code/status counts;
- whether `manager_strategy_text` still blocks;
- whether Evidence Confirm safe summary is emitted even if quality gate blocks;
- `evidence_confirm_status`, `evidence_confirm_policy`, checked/failed facts and auditability score if present;
- confirmation that report body remains suppressed when quality gate blocks.

Forbidden:

- provider/LLM execution;
- direct PDF/cache/source-helper calls outside repository-bounded product path;
- checklist Evidence Confirm support;
- report-body Evidence Confirm rendering;
- V2/ECQ/quality-gate semantic change;
- tag, release or readiness claim.

Stop conditions:

- Stop if product CLI command is unavailable or requires an unreviewed flag shape.
- Stop if quality gate blocked output suppresses the already-computed safe Evidence Confirm summary unexpectedly.
- Stop if report Markdown is emitted despite a quality-gate block.
- Stop if the command writes unexpected tracked artifacts or mutates PR/remote/release state.
- Stop if any live/source failure category is not safely classified.

Expected artifact after authorization:

- `docs/reviews/evidence-confirm-productionization-rr-09-b1-runtime-product-cli-reevidence-20260624.md`

## Decision

The current state is ready for exact authorization, but no live/PDF/product command is executed by this precheck.

This artifact does not prove:

- R1-R4 strict V2 pass after A3;
- `017641 / 2024` product CLI residual closure;
- checklist Evidence Confirm support;
- report-body Evidence Confirm rendering;
- provider-backed semantic production default;
- tag, release or release/readiness.

## Minimal Required User Decision

To continue with runtime evidence, the next user authorization must choose one or both exact executable gates:

```text
授权 RR-09 R1-R4 live/PDF re-evidence after A3 no-live fixes
```

```text
授权 RR-09 B1 runtime product CLI re-evidence for 017641 / 2024
```

## Validation

- Read `docs/current-startup-packet.md` and `docs/implementation-control.md`; both route current entry to exact authorization for `RR-09 R1-R4 live/PDF re-evidence after A3 no-live fixes` and/or `RR-09 B1 runtime product CLI re-evidence for 017641 / 2024`.
- Read A1/A2/A3 evidence artifacts and reused their accepted runner/diagnostic command shape.
- Read `scripts/evidence_confirm_ec_p2_live_sample.py`, `fund_agent/fund/evidence_confirm_sources.py`, README CLI docs and existing review artifacts for repository-bounded runner and product CLI boundaries.
- No live/PDF/provider/LLM/product CLI/repository/parser/source-helper command was executed.

Release/readiness remains `NOT_READY`.
