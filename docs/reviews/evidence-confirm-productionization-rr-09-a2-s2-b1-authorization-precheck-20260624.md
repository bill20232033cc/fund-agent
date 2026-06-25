# Evidence Confirm Productionization RR-09 A2-S2 / B1 Authorization Precheck

Verdict token:

`RR_09_A2_S2_B1_AUTHORIZATION_PRECHECK_BLOCKED_EXACT_AUTH_NOT_READY`

## Scope

Gate: `RR-09 A2-S2 Live/PDF Diagnostic Authorization / RR-09 B1 Runtime Re-evidence Authorization`.

This artifact records the authorization precheck only. It does not run repository-bounded live/PDF diagnostics, does not run `fund-analysis analyze`, does not read annual-report/PDF bodies, does not call provider/LLM, and does not change quality-gate semantics, checklist support, report-body rendering, PR state, tag, release or readiness.

## Current Accepted Inputs

Accepted A2-S1 chain:

- A2 plan/controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a2-plan-controller-judgment-20260624.md`
- A2-S1 implementation evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a2-s1-implementation-evidence-20260624.md`
- A2-S1 code review judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a2-s1-code-review-controller-judgment-20260624.md`
- A2-S1 aggregate judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a2-s1-aggregate-deepreview-controller-judgment-20260624.md`
- Accepted slice commit: `bdcf484`

Accepted B1 no-live chain:

- B1 implementation evidence: `docs/reviews/evidence-confirm-productionization-rr-09-b1-manager-strategy-qdii-implementation-evidence-20260624.md`
- B1 aggregate judgment: `docs/reviews/evidence-confirm-productionization-rr-09-b1-aggregate-deepreview-controller-judgment-20260624.md`
- Accepted slice commit: `4f4c00b`

Accepted A1 live/PDF facts route A2:

- A1 live/PDF evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a1-live-pdf-reevidence-20260624.md`
- A1 live/PDF controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a1-live-pdf-reevidence-controller-judgment-20260624.md`
- A1-C closed the previous zero-reference materializer defect.
- R1-R4 strict V2 still fails on value-match residuals; R3 also carries `structured.bond_risk_evidence` `missing_evidence`.

## Authorization Boundary

Two executable options are now technically prepared but not authorized.

### Option A: A2-S2 R1-R4 Live/PDF Diagnostic Evidence

Required exact authorization should name:

`授权 RR-09 A2-S2 repository-bounded live/PDF value-match diagnostics for R1-R4`

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

Allowed output:

- safe aggregate markdown / JSON only;
- schema version;
- sample id;
- source provenance enums/booleans;
- source field ids;
- failing/warning dimensions;
- fact/chapter ids;
- anchor/reference/proof-reference counts;
- token category counts;
- unmatched structural value paths;
- reference granularity counts;
- locator downgrade flags;
- diagnostic classifications.

Forbidden output:

- raw annual-report excerpt text;
- raw scalar token values;
- full structured fact values;
- PDF/cache paths;
- URLs;
- source-helper internals;
- provider payloads;
- report body text;
- API keys, secrets, tracebacks.

Expected artifact paths after authorization:

- `docs/reviews/evidence-confirm-productionization-rr-09-a2-value-match-diagnostic-evidence-20260624.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-a2-controller-judgment-20260624.md`

### Option B: B1 Runtime Product CLI Re-evidence

Required exact authorization should name:

`授权 RR-09 B1 runtime product CLI re-evidence for 017641 / 2024`

Intended sample:

| Residual | Sample | Purpose |
|---|---|---|
| R5a | `017641 / 2024` | Verify product CLI behavior after accepted B1 `manager_strategy_text` QDII no-live fix. |

Allowed command shape after authorization:

```bash
uv run fund-analysis analyze 017641 --report-year 2024 --valuation-state unavailable --force-refresh
```

Allowed evidence:

- command exit code;
- safe stdout/stderr summary;
- quality-gate status;
- Evidence Confirm safe summary if produced;
- whether `manager_strategy_text` still blocks;
- whether product CLI reaches expected warn/block behavior.

Forbidden:

- provider/LLM execution;
- raw PDF/cache/source-helper access outside `FundDocumentRepository`;
- report-body rendering change;
- quality-gate semantic change;
- checklist support;
- tag, release or readiness claim.

## Decision

Stop before execution.

Blocking reason:

- The current user message continues the broad objective but does not explicitly authorize either exact live/PDF action: A2-S2 repository-bounded live/PDF diagnostics or B1 runtime product CLI re-evidence.

## Minimal Required User Decision

To continue with live evidence, the next user authorization must choose one of:

```text
授权 RR-09 A2-S2 repository-bounded live/PDF value-match diagnostics for R1-R4
```

or:

```text
授权 RR-09 B1 runtime product CLI re-evidence for 017641 / 2024
```

The two can also be authorized together, but the authorization must explicitly name both.

## Validation

- `git status --short --branch` shows branch `evidence-confirm-productionization`, ahead of origin, with only previously classified unrelated untracked residue.
- `git log --oneline -8` shows current accepted chain through `5282469 Accept RR-09 A2-S1 aggregate deepreview`.
- `docs/current-startup-packet.md` and `docs/implementation-control.md` both route current entry to `RR-09 A2-S2 Live/PDF Diagnostic Authorization / RR-09 B1 Runtime Re-evidence Authorization`.
- No live/PDF/provider/LLM/product CLI command was executed in this precheck.

Release/readiness remains `NOT_READY`.
