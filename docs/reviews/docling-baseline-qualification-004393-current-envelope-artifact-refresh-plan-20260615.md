# 004393 Current-envelope Candidate Artifact Refresh Planning Gate - 2026-06-15

Gate: `004393 Current-envelope Candidate Artifact Refresh Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan how to make the user-designated fund sample `004393` / 安信企业价值优选混合A available under the current candidate representation envelope:

```text
candidate_annual_report_representation.v1
```

The plan exists because the accepted locator-stability evidence found that current 004393 artifacts are legacy or route-specific JSON and therefore cannot be used as current-envelope locator proof.

## 2. Motivation

Future Docling baseline / correctness work should use `004393_2025` as the primary user-designated fund sample. However:

- `reports/representation-json/004393_2025_docling_full.json` has no current candidate envelope schema version.
- `reports/representation-json/004393_2025_pdfplumber_full.json` has no current candidate envelope schema version.
- `reports/representation-json/004393_2025_eid_html_render_full.json` uses `eid_xbrl_html_render_candidate.full_representation.v1`, not the route-neutral candidate envelope.

Using those files directly would blur legacy diagnostic artifacts with accepted current candidate representation.

## 3. Non-goals

This plan does not authorize:

- live/network/EID/provider/LLM commands
- production `FundDocumentRepository` changes
- source policy changes
- parser replacement
- public `EvidenceAnchor` schema changes
- Service/Host/UI/renderer/quality gate consumption
- field correctness claims
- source truth claims
- taxonomy compatibility claims
- release/readiness/PR claims
- deletion, archive, or cleanup of legacy artifacts

## 4. Direct Evidence Inputs

Accepted gate artifacts:

- `docs/reviews/docling-baseline-qualification-candidate-representation-locator-stability-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-baseline-candidate-decision-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-controller-judgment-20260615.md`

Current local artifacts:

- `reports/representation-json/004393_2025_docling_full.json`
- `reports/representation-json/004393_2025_pdfplumber_full.json`
- `reports/representation-json/004393_2025_eid_html_render_full.json`
- `reports/representation-json/full-representation-export-manifest-20260615.json`

Current implementation helpers:

- `fund_agent/fund/documents/candidates/representation_export.py`
- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `fund_agent/fund/documents/candidates/representation_models.py`
- `fund_agent/fund/documents/candidates/representation_projection.py`

## 5. Preferred Implementation Strategy

Use a two-path decision sequence.

### Path A: no-conversion current-envelope wrapper

Use existing 004393 legacy JSON as read-only input and write new current-envelope outputs under new no-clobber paths:

- `reports/representation-json/004393_2025_docling_current_envelope.json`
- `reports/representation-json/004393_2025_pdfplumber_current_envelope.json`
- `reports/representation-json/004393_2025_eid_html_render_blocked_current_envelope.json`

Allowed behavior:

- read legacy JSON files as candidate inputs;
- map only fields that have explicit structural meaning;
- preserve route-specific source kind;
- preserve non-proof statuses and blocked claims;
- preserve field gaps as projection issues or route failures;
- compute summary metrics from mapped structure;
- validate new outputs with `project_candidate_representation`.
- emit EID HTML only as blocked current-envelope artifact with route failure and zero sections/tables/cells unless a separate EID HTML Candidate Envelope Mapping Gate has accepted table-bearing mapping rules.

Prohibited behavior:

- overwrite existing legacy JSON paths;
- treat legacy JSON as source truth;
- invent page, bbox, row/column, header flag, or table structure not present in input;
- wrap the 004393 route-specific EID HTML full JSON into a table-bearing current envelope;
- compare values to PDF;
- run Docling/pdfplumber conversion;
- run live/network/EID commands.

Stop condition:

- If legacy JSON lacks enough structure to map Docling/pdfplumber into current envelope without inventing locators, stop with `NEEDS_NO_LIVE_LOCAL_CONVERSION_GATE_NOT_READY`.

### Path B: no-live local conversion refresh

Only if Path A is insufficient, run the accepted built-in handler route against already accepted local input artifacts in a separate implementation/evidence gate.

Allowed behavior for that later gate:

- use `representation_export.py --run-built-in-handlers`;
- keep `--docling-artifacts-path` local;
- keep socket block enabled by default;
- write only new no-clobber output paths;
- include CPU/runtime measurement as evidence;
- validate with `project_candidate_representation`.

Additional required authorization:

- This later gate must explicitly allow no-live local PDF/Docling/pdfplumber processing because it is CPU-heavy and reads local report artifacts.

## 6. Manifest Design

Create a new implementation-only manifest path:

```text
reports/representation-json/004393-current-envelope-refresh-manifest-20260615.json
```

Manifest entries should use new output paths and must not clobber existing files.

For Path A, the manifest can be wrapper-specific and docs/test scoped. If implementation reuses `representation_export.py`, the route handler should be injected in tests or a candidate-internal helper, not public API.

For Path B, the manifest should follow current `CandidateRepresentationExportManifest` rules and target:

- Docling PDF candidate
- pdfplumber PDF candidate
- EID HTML render candidate only if a current-envelope mapping has been explicitly accepted; otherwise blocked.
- For this 004393 refresh line, EID HTML remains blocked unless an independent EID HTML Candidate Envelope Mapping Gate has already accepted table-bearing mapping semantics.

## 7. Acceptance Criteria

The implementation/evidence gate passes only if:

- 004393 Docling output has schema version `candidate_annual_report_representation.v1`;
- 004393 pdfplumber output has schema version `candidate_annual_report_representation.v1`;
- 004393 EID HTML output is blocked with zero sections/tables/cells unless a separate accepted EID HTML mapping gate exists;
- outputs validate through `project_candidate_representation`;
- all status fields remain non-proof;
- blocked claims are complete;
- no existing legacy JSON path is overwritten;
- no production repository/source/parser behavior changes;
- no Service/Host/UI/renderer/quality gate consumption is introduced;
- evidence clearly classifies whether Path A succeeded or Path B is required.

## 8. Tests / Validation Commands

Planning gate validation:

```text
git diff --check
```

Future implementation/evidence gate validation:

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_models.py fund_agent/fund/documents/candidates/representation_projection.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py
```

```text
git diff --check
```

If Path A adds wrapper code, targeted tests must prove:

- no overwrite of legacy JSON;
- missing locator fields remain missing;
- current-envelope output validates;
- non-proof statuses survive;
- 004393 Docling/pdfplumber outputs are projectable.

## 9. Review Focus

Reviewers should check:

- whether the plan accidentally treats legacy 004393 JSON as source truth;
- whether Path A might invent locators;
- whether Path B CPU/local conversion is properly separated and not silently authorized by this planning gate;
- whether EID HTML render is kept out of raw XBRL/source truth claims;
- whether output paths are no-clobber and current-envelope-specific;
- whether field correctness/readiness/parser replacement claims are avoided.

## 10. Stop Conditions

Stop before implementation if:

- existing 004393 legacy JSON cannot be mapped without inventing structural facts;
- producing table-bearing EID HTML current-envelope output would be required before the separate EID HTML Candidate Envelope Mapping Gate is accepted;
- implementation would need live/network/EID/provider/LLM access;
- implementation would need to overwrite current committed artifact paths;
- implementation would need to read production `cache/pdf` through a path outside accepted candidate harness rules;
- implementation would change `FundDocumentRepository`, parser, Service, Host, UI, renderer, quality gate, or public `EvidenceAnchor`;
- the controller cannot classify whether Path A or Path B is being used.

## 11. Recommended Next Gate

`004393 Current-envelope Candidate Artifact Refresh Plan Review Gate`

If accepted, next:

`004393 Current-envelope Candidate Artifact Refresh No-live Implementation/Evidence Gate`

Default implementation preference:

1. Try Path A no-conversion wrapper evidence first.
2. If Path A is insufficient, stop and request/record explicit authorization for Path B no-live local conversion.
