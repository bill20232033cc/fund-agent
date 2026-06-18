# Docling Baseline Qualification Built-in Representation Handler Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Built-in Candidate Representation Route Handler Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan a narrow no-live implementation of built-in candidate route handlers for the accepted representation export harness.

The goal is to make the later `Full Representation Export Evidence Gate` reproducible: evidence workers should run reviewed handler code through a stable module/CLI entrypoint instead of inventing one-off Docling/pdfplumber export scripts.

This planning gate does not implement handlers, run Docling conversion, run pdfplumber export, read PDF bodies, run live/network/EID/FDR, modify production parser/repository/source behavior, or claim Docling baseline/readiness.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `fund_agent/fund/pdf/parser.py`

Accepted constraints:

- current production parser remains `pdfplumber -> ParsedAnnualReport -> extractor`;
- Docling remains candidate-only and not source truth;
- EID HTML render remains `eid_xbrl_html_render_candidate`, not raw XML/XBRL truth;
- production annual-report source remains EID single-source/no fallback;
- Service/UI/Host/renderer/quality gate must not directly call parser/cache/source helpers;
- release/readiness remains `NOT_READY`.

## 3. Non-goals

- No production parser replacement.
- No `FundDocumentRepository` behavior change.
- No source policy change.
- No use of Eastmoney, fund-company website, CNINFO or other non-EID fallback.
- No production cache promotion.
- No write to `cache/pdf`.
- No Service/UI/Host/renderer/quality-gate integration.
- No extractor / EvidenceAnchor / CHAPTER_CONTRACT consumer integration.
- No field correctness validation.
- No source truth, raw XML, taxonomy compatibility, baseline qualification or readiness claim.
- No large annual-report conversion in normal tests.
- No dependency installation or lockfile change.

## 4. Chosen Implementation Shape

Add one candidate-internal module:

```text
fund_agent/fund/documents/candidates/representation_handlers.py
```

Update the accepted harness only where needed:

```text
fund_agent/fund/documents/candidates/representation_export.py
```

Add tests:

```text
tests/fund/documents/test_candidate_representation_handlers.py
tests/fund/documents/test_candidate_representation_export.py
```

Update Fund README only if public developer documentation must mention the new handler boundary:

```text
fund_agent/fund/README.md
```

Do not modify:

```text
fund_agent/fund/documents/repository.py
fund_agent/fund/documents/sources.py
fund_agent/fund/documents/cache.py
fund_agent/fund/documents/adapters/annual_report_pdf.py
fund_agent/services/
fund_agent/host/
fund_agent/ui/
fund_agent/fund/extractors/
fund_agent/fund/quality_gate.py
docs/design.md
docs/implementation-control.md
docs/current-startup-packet.md
cache/pdf/
```

## 5. Handler API

Implement a small typed handler surface:

```python
@dataclass(frozen=True, slots=True)
class CandidateHandlerConfig:
    workspace_root: Path = Path(".")
    docling_artifacts_path: Path = Path("cache/docling-artifacts")
    docling_do_ocr: bool = False
    docling_do_table_structure: bool = True
    docling_socket_block: bool = True
    allow_overwrite: bool = False


def built_in_route_handlers(config: CandidateHandlerConfig) -> dict[CandidateRepresentationRoute, RouteHandler]:
    ...


def build_pdfplumber_candidate_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    config: CandidateHandlerConfig,
    text_extractor: Callable[[Path], str] = extract_text,
    table_extractor: Callable[[Path], list[dict[str, object]]] = extract_tables,
    section_locator: Callable[[str], dict[str, tuple[int, int]]] = locate_sections,
) -> dict[str, Any]:
    ...


def build_docling_candidate_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    config: CandidateHandlerConfig,
    converter_factory: Callable[[CandidateHandlerConfig], Any] | None = None,
) -> dict[str, Any]:
    ...


def build_eid_html_candidate_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    config: CandidateHandlerConfig,
) -> dict[str, Any]:
    ...
```

Implementation rules:

- `built_in_route_handlers()` returns handlers for all three route kinds.
- pdfplumber handler may use existing `fund_agent.fund.pdf.parser` helpers because this module is Fund documents candidate-internal. It must not call `FundDocumentRepository`.
- Docling handler must lazy-import Docling only inside the handler or converter factory.
- EID HTML handler must return blocked JSON unless `entry.mode` and manifest fields later carry an accepted HTML render artifact path or URL. This implementation slice should not add live HTML discovery.
- All handlers must return payloads through `build_representation_envelope()` or `build_blocked_representation()` so non-proof fields and blocked claims stay centralized.

## 6. CLI / Entrypoint Change

Extend `representation_export.py` with an explicit opt-in flag:

```text
uv run python -m fund_agent.fund.documents.candidates.representation_export \
  --manifest <manifest.json> \
  --run-built-in-handlers
```

Optional config flags:

```text
--docling-artifacts-path cache/docling-artifacts
--allow-overwrite  # default false; evidence gate must explicitly justify use
--docling-no-socket-block  # default remains socket blocked; allowed only for future explicitly authorized gates
```

Behavior:

- default command remains validation-only;
- `--write-blocked` remains blocked-output only;
- `--run-built-in-handlers` uses `built_in_route_handlers(config)`;
- `--run-built-in-handlers` and `--write-blocked` are mutually exclusive;
- `reference_existing_json` entries remain read-only validation references and are not rewritten;
- handler execution writes only manifest-declared output paths under `reports/representation-json`;
- handler execution must fail before writing if any write-producing target output already exists, unless `--allow-overwrite` is explicitly passed by a later evidence gate.

The implementation gate must not run this command on real annual reports. It only defines the entrypoint and tests it with fake/minimal handlers or tiny synthetic PDFs if needed.

## 7. Pdfplumber Handler Contract

Input:

- manifest entry route: `pdfplumber_pdf_candidate`;
- mode: `handled`;
- accepted PDF path under staged candidate path, not `cache/pdf`;
- accepted input SHA-256 must match.

Output:

- candidate envelope `source_kind=pdfplumber_pdf_candidate`;
- `summary_metrics` with required keys;
- `sections` from `locate_sections(raw_text)`;
- `headings` derived from section ids/titles;
- `paragraphs` as page-level or section-level text blocks, not business facts;
- `tables` from `extract_tables()`, with page number, table index, headers, row count, cell count and simple row/column locators;
- `text_blocks` minimally representing extracted text spans;
- `failure_taxonomy.route_failures=[]` on success.

Tests:

- fake `text_extractor`, `table_extractor`, `section_locator`;
- no real PDF body read;
- assert summary metrics and envelope non-proof fields;
- assert `cache/pdf` path remains rejected by the harness;
- assert no public `fund_agent.fund.documents` export.
- assert existing `reference_existing_json` entries validate without rewrite;
- assert existing `handled` or `blocked` output paths are rejected by default;
- assert a mixed manifest fails before any write if one write-producing target exists;
- assert `--allow-overwrite` applies only to write-producing entries and never rewrites `reference_existing_json`.

## 8. Docling Handler Contract

Input:

- manifest entry route: `docling_pdf_candidate`;
- mode: `handled`;
- accepted staged PDF path, not `cache/pdf`;
- local artifacts path default: `cache/docling-artifacts`;
- `docling_socket_block=True` by default;
- `docling_do_ocr=False` by default.

Containment requirements:

- lazy import Docling only inside handler or injected converter factory;
- if local artifacts path is missing, return blocked JSON with `docling_local_artifacts_missing`;
- if conversion attempts network under socket block, return blocked JSON with `docling_network_attempt_blocked`;
- if conversion fails because layout/model artifacts are unavailable, return blocked JSON with `docling_model_artifact_unavailable`;
- no production parser replacement or source truth claim on success.

Conversion output mapping:

- The implementation may support a minimal adapter from a Docling exported dict / `export_to_dict()`-like object to envelope fields.
- Tests must use a fake converter result object/dict, not real annual-report conversion.
- Full conversion for S4/S5/S6 is deferred to evidence gate after implementation acceptance.

## 9. EID HTML Handler Contract

This implementation slice should implement blocked behavior only:

- route: `eid_xbrl_html_render_candidate`;
- mode: `blocked`;
- output: blocked JSON with reason `eid_html_render_url_not_accepted_for_sample`;
- no live URL discovery;
- no raw XML/XBRL claim;
- no field correctness/taxonomy/source-truth/readiness claim.

If a later bounded discovery gate accepts S4/S5/S6 HTML render artifacts, a separate handler extension gate can add local HTML artifact parsing.

## 10. Manifest Plan For First Evidence Gate

After handler implementation acceptance, the evidence gate should use this first-wave manifest shape:

| Sample | Route | Mode | Output |
|---|---|---|---|
| S1 `004393 / 2025` | Docling/pdfplumber/EID HTML | `reference_existing_json` | existing three JSONs |
| S4 `006597 / 2024` | Docling/pdfplumber | `handled` | `reports/representation-json/006597_2024_*_full.json` |
| S4 `006597 / 2024` | EID HTML | `blocked` | `reports/representation-json/006597_2024_eid_html_render_blocked.json` |
| S5 `017641 / 2024` | Docling/pdfplumber | `handled` | `reports/representation-json/017641_2024_*_full.json` |
| S5 `017641 / 2024` | EID HTML | `blocked` | `reports/representation-json/017641_2024_eid_html_render_blocked.json` |
| S6 `110020 / 2024` | Docling/pdfplumber | `handled` | `reports/representation-json/110020_2024_*_full.json` |
| S6 `110020 / 2024` | EID HTML | `blocked` | `reports/representation-json/110020_2024_eid_html_render_blocked.json` |

S2/S3 remain deferred unless a separate provenance decision accepts them.

## 11. Output Overwrite Policy

Handler implementation must tighten the current harness default for write-producing entries:

- default behavior is no-clobber;
- write-producing entries are `handled` and `blocked`;
- `reference_existing_json` entries are read-only references and are excluded from write-target no-clobber checks;
- `reference_existing_json` entries must still be validated as existing JSON references and must not be rewritten;
- any existing output path for a write-producing entry must raise before writing;
- overwrite requires an explicit `--allow-overwrite` flag;
- `--allow-overwrite` applies only to write-producing entries;
- `--allow-overwrite` is not an implementation-test default and must be justified by a later evidence gate;
- if any entry would be blocked by no-clobber, the command must stop before partially writing later entries.

The evidence gate must record:

- whether each output path existed before execution;
- previous SHA-256 if it existed;
- new SHA-256 after execution;
- whether the entry was read-only reference or write-producing;
- exact manifest path;
- exact command line;
- whether `--allow-overwrite` was used and why.

No production cache path may be overwritten.

## 12. Validation Commands

Implementation gate must run:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
git diff --check
```

Implementation gate must not run:

```text
uv run python -m fund_agent.fund.documents.candidates.representation_export --run-built-in-handlers <real annual report manifest>
```

Full handler execution belongs to a later evidence gate.

## 13. Review Checklist

Reviewers must check:

- no production repository/source/cache behavior change;
- no public documents export of candidate internals;
- no Service/UI/Host/renderer/quality-gate direct access;
- no source truth / field correctness / taxonomy / readiness claim;
- Docling handler uses lazy import and blocked failure classes;
- pdfplumber handler is candidate-internal and fake-tested;
- EID HTML handler does not fabricate URLs;
- manifest and output overwrite policy are explicit;
- tests do not run real annual-report conversion.

## 14. Stop Conditions

Stop before implementation if:

- the plan requires real Docling conversion to validate implementation;
- the plan requires direct production `cache/pdf` input;
- the plan requires modifying `FundDocumentRepository`, sources or cache;
- the plan cannot keep Docling network/model-download containment explicit;
- the plan needs field correctness or EvidenceAnchor production schema decisions;
- the plan needs live/EID/FDR/network access.

## 15. Next Gate Recommendation

Immediate next gate:

`Built-in Candidate Representation Route Handler Plan Review Gate`

If accepted:

`Built-in Candidate Representation Route Handler No-live Implementation Gate`

Then:

`Full Representation Export Evidence Gate`

Deferred:

- S4/S5/S6 EID HTML render discovery;
- S2/S3 provenance resolution;
- field correctness validation;
- FundDisclosureDocument production schema / repository integration;
- readiness/release/PR gates.

## 16. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
