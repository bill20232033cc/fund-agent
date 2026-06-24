# EC-P2 Live Warning Disposition / Fix Plan

## Verdict

`PLAN_READY_FOR_TARGETED_REREVIEW_NOT_READY`

## Scope

- Work unit: `Evidence Confirm Productionization Program`
- Slice: `EC-P2 live warning disposition / fix`
- Gate: `plan fix after plan review`
- Gate classification: `heavy`
- Artifact: `docs/reviews/evidence-confirm-productionization-ec-p2-live-warning-disposition-fix-plan-20260622.md`
- Branch: `evidence-confirm-productionization`
- Current local checkpoint: `46c7014`
- Initial plan review: `docs/reviews/plan-review-20260622-162937.md`

This fixed plan does not implement source code, run live/PDF/provider/LLM commands, alter Service/UI/Host/renderer/quality-gate behavior, change source fallback behavior, mark PR-40 ready, merge, or claim release/readiness.

## Goal Confirmation

### Goal

Resolve the accepted EC-P2 live sample result:

```json
{
  "status": "fail",
  "evidence_confirm_overall_status": "warn",
  "source_metadata_admitted": true,
  "reference_count": 1,
  "field_correctness_proven": false
}
```

The goal is to correctly classify this result as live source/PDF pathway evidence without pretending that section-only Evidence Confirm is strict V2 pass.

### Motivation

The current section-smoke projection proves repository load, same-source metadata admission and annual-report section reference materialization. It fails strict EC-P2 pass because V2 `anchor_precision` intentionally warns when an annual-report reference has `section_id` but no page/table/row locator.

Trying to force V2 pass through a table-row smoke projection is unsafe under the current data model: `ParsedTable` has page/table/row data but no table-to-section mapping, while the annual-report proof predicate still expects section context. A V2 pass would require synthetic section context, which is stronger than the current `ParsedAnnualReport` table model can prove.

### Success Signal

After reviewed no-live implementation, the same already executed live output can be represented by the runner/script as:

- `pathway_status="pass"`
- `status="fail"` or equivalent strict V2 aggregate remains visible
- `evidence_confirm_overall_status="warn"`
- `accepted_pathway_warning_reasons` includes only the expected E1 anchor precision warning caused by section-only smoke evidence
- `source_metadata_admitted=true`
- `reference_count=1`
- `field_correctness_proven=false`

After the fix is accepted, a single rerun of the same authorized command may be executed only in the next live re-evidence gate:

```text
uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh
```

Expected safe JSON properties after rerun:

- `projection_kind="ec_p2_live_section_smoke"`
- `pathway_status="pass"`
- `status="fail"` if strict V2 still warns
- `evidence_confirm_overall_status="warn"`
- `source_metadata_admitted=true`
- `reference_count=1`
- `field_correctness_proven=false`

This would accept EC-P2 live source/PDF pathway evidence only. It would not accept semantic entailment, full V2 strict pass, field correctness, golden/readiness or release.

### Non-goals

- No global relaxation of `anchor_precision`.
- No table-row smoke workaround requiring synthetic table-to-section context.
- No semantic entailment Evidence Confirm.
- No Service/UI/renderer/quality-gate integration.
- No public `EvidenceAnchor` / `EvidenceSourceKind` expansion.
- No repository/source/fallback behavior change.
- No product fact, field-family source truth, golden, readiness or release claim.
- No provider/LLM command.
- No additional live sample, no multi-sample matrix.
- No PR push/update/mark-ready in this slice.

### Direct Code Evidence

| Evidence | Meaning |
|---|---|
| `fund_agent/fund/evidence_confirm.py::_precision_issue()` | Annual-report references warn when they have `section_id` but no `page_number`, `table_id` or `row_locator`. |
| `tests/fund/test_evidence_confirm.py::test_imprecise_anchor_warns_but_keeps_value_match` | E1-only imprecision intentionally yields V2 `warn`, score 70, not pass. |
| `scripts/evidence_confirm_ec_p2_live_sample.py::build_live_section_smoke_projection()` | Current smoke projection builds an annual-report anchor with `section_id` only and no table/row/page locator. |
| `fund_agent/fund/documents/models.py::ParsedTable` | Current parsed table model has `page_number`, `table_index`, `headers`, `rows`; no `section_id`. |
| `fund_agent/fund/evidence_confirm_sources.py::_anchor_preflight_issue()` | Current annual-report materializer requires anchor `section_id` to exist in `parsed_report.sections`, including table path preflight. |
| `fund_agent/fund/evidence_confirm_sources.py::_build_reference_for_anchor()` | Table path emits `section_id=anchor.section_id`; it does not prove table-to-section ownership. |
| `docs/reviews/plan-review-20260622-162937.md` | Initial table-row smoke plan failed because it could create V2 pass from unproven section context. |
| `docs/reviews/evidence-confirm-productionization-ec-p2-live-sample-controller-judgment-20260622.md` | Current live run accepted only as partial pathway evidence and requires warning disposition/fix planning before any EC-P2 pass claim. |

## Disposition

The V2 `warn` is expected for the current section-only smoke projection and must remain visible as strict Evidence Confirm status.

The correct EC-P2 fix is not to make V2 pass. The correct fix is to add an explicit repository/source/PDF pathway status that can pass when:

1. repository load succeeds through the runner boundary;
2. source metadata admission is positive;
3. the annual-report reference materializer produces at least one proven reference;
4. V2 result has no blocking failure;
5. any V2 non-pass status is limited to the expected E1 `anchor_precision` warning from section-only smoke.

This keeps strict V2 semantics intact and prevents source/PDF pathway evidence from being misrepresented as semantic or locator-complete Evidence Confirm.

## Implementation Decision

Add a separate pathway status to the EC-P2 repository runner result and safe live JSON.

### Runner Contract Additions

In `fund_agent/fund/evidence_confirm_sources.py`:

- Add `EvidenceConfirmRepositoryPathwayStatus = Literal["pass", "fail"]`.
- Add fields to `EvidenceConfirmRepositoryRunResult`:
  - `pathway_status: EvidenceConfirmRepositoryPathwayStatus`
  - `pathway_warning_reasons: tuple[str, ...]`
- Compute `pathway_status` independently from strict `status`.

Pathway status rules:

- `fail` if repository init/load fails.
- `fail` if source provenance is missing or not admitted.
- `fail` if `reference_build_result` is missing, status is not `pass`, or `references` is empty.
- `fail` if V2 result is missing when `run_v2_confirm=True`.
- `fail` if V2 has any blocking issue or `overall_status=="fail"`.
- `pass` if V2 `overall_status=="pass"`.
- `pass` if V2 `overall_status=="warn"` and all non-pass dimensions/issues are the expected E1 `anchor_precision` reviewable warning.
- Otherwise `fail`.

Strict `status` remains unchanged: pass only when reference build passes and V2 is absent or `overall_status=="pass"`.

### Safe JSON Additions

In `scripts/evidence_confirm_ec_p2_live_sample.py`, include safe scalar fields:

- `pathway_status`
- `pathway_warning_reasons`
- keep existing `status`
- keep existing `evidence_confirm_overall_status`
- keep `field_correctness_proven=false`

Do not output excerpts, PDF paths, source URLs, section text, table text, prompt, provider data or semantic conclusion.

### Expected Warning Reason

Use a stable reason string such as:

- `v2_anchor_precision_warn_section_only_smoke`

It may be emitted only when all V2 warnings are E1 `anchor_precision` reviewable warnings and there are no blocking issues.

## Affected Files

Allowed implementation files:

- `fund_agent/fund/evidence_confirm_sources.py`
- `scripts/evidence_confirm_ec_p2_live_sample.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- implementation/review/evidence artifacts under `docs/reviews/`
- control doc sync only after accepted implementation/review:
  - `docs/implementation-control.md`
  - `docs/current-startup-packet.md`

Forbidden files/modules:

- `fund_agent/fund/evidence_confirm.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/services/`
- `fund_agent/ui/`
- renderers
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- public `EvidenceSourceKind` / `EvidenceAnchor` schemas

## Slice Plan

### Slice EC-P2W-1: no-live pathway status fix

Objective: expose EC-P2 live source/PDF pathway success separately from strict V2 status.

Allowed changes:

- In `fund_agent/fund/evidence_confirm_sources.py`:
  - add pathway status type and result fields;
  - add helper to evaluate pathway status from source provenance, reference build and V2 result;
  - preserve existing strict `status` behavior;
  - preserve existing repository failure classification and no helper/source/PDF direct calls.
- In `scripts/evidence_confirm_ec_p2_live_sample.py`:
  - serialize `pathway_status` and `pathway_warning_reasons`;
  - keep section-smoke projection;
  - keep authorization hard limit `004393/2025`;
  - keep safe scalar JSON only.
- In tests:
  - add fake repository section-smoke case proving:
    - strict `status=="fail"`;
    - V2 `overall_status=="warn"`;
    - `pathway_status=="pass"`;
    - warning reasons are exactly expected;
  - add V2 value mismatch case proving `pathway_status=="fail"`;
  - add negative provenance/materializer failure cases proving `pathway_status=="fail"`;
  - add safe JSON test proving `pathway_status` is serialized and no traceback.
- Update README/test README current-state wording.

Validation:

```text
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
```

```text
uv run ruff check fund_agent/fund/evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py tests/fund/test_evidence_confirm_sources.py
```

```text
git diff --check -- fund_agent/fund/evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py tests/fund/test_evidence_confirm_sources.py fund_agent/fund/README.md tests/README.md
```

Stop condition:

- Stop after no-live implementation evidence and code review/re-review. Do not run live command until controller accepts the slice and explicitly opens the live re-evidence gate.

### Slice EC-P2W-2: authorized live re-evidence

Prerequisite:

- Slice EC-P2W-1 implementation/code review/re-review accepted and committed.

Allowed command:

```text
uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh
```

Expected artifact:

- `docs/reviews/evidence-confirm-productionization-ec-p2-live-warning-disposition-re-evidence-20260622.md`

Stop condition:

- If output has `pathway_status="pass"` and the only strict V2 non-pass status is expected `anchor_precision` warn, write controller judgment accepting EC-P2 live source/PDF pathway evidence only.
- If output has `pathway_status="fail"` or unexpected warning/failure reasons, write the exact safe JSON and route to a new disposition gate. Do not adjust code in the live gate.

## Test Matrix

No-live tests must prove:

- section-smoke V2 warning is classified as pathway pass only when it is E1 `anchor_precision` with no blocking issues;
- V2 fail or unexpected warning remains pathway fail;
- source metadata negative remains pathway fail;
- reference build fail/no references remains pathway fail;
- safe JSON includes pathway status and warning reasons;
- import isolation still does not instantiate repository on import.

## Docs Decision

Update `fund_agent/fund/README.md` and `tests/README.md` only for current code facts:

- EC-P2 distinguishes strict V2 status from repository/source/PDF pathway status;
- section-smoke `anchor_precision` warning can be accepted only as pathway warning, not strict Evidence Confirm pass;
- output still does not prove field correctness or semantic entailment.

## Risks / Residuals

- Pathway pass is weaker than strict V2 pass. Owner: later semantic entailment / locator-complete Evidence Confirm gates.
- Full table-to-section provenance would require a separate parser/repository data-model gate if later EC-Px wants V2 pass over table-row live smoke without synthetic section context.
- Service/UI/renderer/quality-gate production integration remains unimplemented. Owner: later production integration work unit.
- Release/readiness remains `NOT_READY`. Owner: later release-readiness gate.

## Completion Report Format

After implementation/review, report:

- changed files;
- tests/validation;
- review finding status;
- whether EC-P2W-1 is accepted;
- whether live re-evidence is authorized next;
- explicit `NOT_READY` scope.
