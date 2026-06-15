# CSRC EID XBRL HTML Structured Render Artifact Evaluation Plan

Date: 2026-06-14

Gate: `CSRC EID XBRL HTML Structured Render Artifact Evaluation Planning Gate`

Classification: `standard`

Status: plan artifact only; not reviewed, not accepted, not readiness proof

## Objective

Evaluate official CSRC EID XBRL HTML render pages as candidate structured disclosure artifacts for fund-agent.

The question is not whether the render looks like Markdown or whether it can replace the PDF parser. The question is whether an official HTML render artifact can support low-noise projection into:

- candidate `FundDisclosureDocument` fields;
- section/table/provenance structures;
- `EvidenceAnchor` candidate fields;
- CHAPTER_CONTRACT facts through existing extractor / projection / fail-closed boundaries.

Candidate `source_kind`: `eid_xbrl_html_render_candidate`.

## Accepted Inputs

- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md`

## Non-goals

- Do not prove raw XML/XBRL instance direct download.
- Do not claim field correctness.
- Do not claim taxonomy cross-year compatibility.
- Do not implement parser code.
- Do not change `FundDocumentRepository`, source policy, parser cache, extractor, EvidenceAnchor schema, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior.
- Do not run production `FundDocumentRepository`, PDF, provider, LLM, analysis, checklist, golden, readiness, release, PR, push or merge commands.
- Do not treat HTML render, JSON, PDF parser output, Docling output or any intermediate artifact as fund fact truth.

## Evidence Gate Output

The next evidence gate should write exactly one evidence artifact:

`docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`

The evidence artifact must contain:

- official request URLs;
- HTTP status, content-type, content-length, redirect location and cache-related headers where available;
- concrete instance id / report type / report period metadata if present;
- HTML render URL and content hash;
- extracted navigation labels;
- extracted section/title samples;
- extracted table samples with row/column locator candidates;
- provenance locator candidates;
- candidate mapping to `FundDisclosureDocument`;
- candidate mapping to `EvidenceAnchor`;
- blocked proofs and residuals.

The evidence artifact must explicitly state:

- `not_raw_xml_download_proof`;
- `not_field_correctness_proof`;
- `not_taxonomy_compatibility_proof`;
- `not_source_truth`;
- `not_readiness_proof`;
- `no_repository_behavior_change`.

## Sample Matrix

Use bounded official EID requests only. Prefer samples discoverable from `indexXbrlData.json` and concrete `instance_html_view.do?instanceid=...` redirects.

Minimum matrix:

| Sample class | Minimum | Purpose |
|---|---:|---|
| Annual / interim report HTML render | 2 | Test long report section hierarchy, repeated tables and narrative/table mix |
| Quarterly report HTML render | 1 | Test shorter periodic report table structure |
| Net value announcement or temporary announcement HTML render | 1 if available | Test non-periodic or non-annual disclosure shape |
| Known reachable prior instance | 1 | Preserve continuity with existing `instanceid=22326918` evidence |

If a report class is unavailable from the public JSON list, record it as `not_available_in_sample`, not as a source failure for the whole gate.

## Evaluation Questions

### Artifact Identity

- Can the gate bind fund code, fund name, report type, report period and instance id from official JSON and/or rendered HTML?
- Can the gate preserve original list URL, `instance_html_view.do` URL, 302 target URL and HTML content hash?
- Can the gate distinguish a stale cached render from a current official redirect only through recorded metadata?

### Section Projection

- Does the HTML contain machine-extractable navigation or heading structure?
- Can each section be assigned stable labels and DOM/text locators?
- Are section labels sufficient to candidate-map into CHAPTER_CONTRACT areas, or only into generic disclosure sections?

### Table Projection

- Are table boundaries extractable without visual OCR?
- Can rows and columns be assigned stable locator candidates?
- Can repeated table names and multi-level headers be disambiguated by nearby section title, table caption, row text and DOM path?
- Can table cells preserve units, dates and footnotes as separate candidate fields?

### Narrative Projection

- Does the HTML expose narrative paragraphs needed by CHAPTER_CONTRACT, including manager discussion, investment strategy, risk disclosure and market review?
- If narrative paragraphs are absent or flattened, which CHAPTER_CONTRACT sections still require PDF narrative or other official disclosure material?

### EvidenceAnchor Mapping

For each sampled field, propose candidate mapping to existing `EvidenceAnchor` fields:

| EvidenceAnchor field | Candidate HTML render mapping |
|---|---|
| `source_kind` | `eid_xbrl_html_render_candidate` |
| `document_year` | report period / end date, if explicit |
| `section_id` | normalized section heading / navigation id |
| `page_number` | usually unavailable; record `null` unless render exposes page relation |
| `table_id` | table caption / sequence under section |
| `row_locator` | row index plus stable row text key / DOM path candidate |
| `note` | official render URL, instance id, content hash and extraction caveats |

## Stop Rules

- Stop if official EID HTML render requires authentication, captcha, non-public session state or manual browser state.
- Stop if the public JSON list cannot provide any concrete instance id or HTML view path.
- Stop if HTML body is blank, binary-only or image-only for all samples.
- Stop if redirects leave official EID domains.
- Stop if evidence requires production repository/source/parser/LLM commands.

Stop result should be `BLOCKED_NOT_READY` with exact failing URL/status/error class.

## Success Criteria

The evidence gate may recommend a future `FundDisclosureDocument Candidate Source Design Gate` only if it proves all of the following for at least one annual/interim sample and one non-annual sample:

- official HTML render is publicly reachable;
- artifact identity can be recorded;
- section labels can be extracted;
- at least one table can be extracted with row/column locator candidates;
- at least one narrative or note block can be extracted, or the absence is explicitly classified;
- candidate EvidenceAnchor mapping can be written without pretending page numbers or raw XML fact provenance exist.

If these are not met, the gate should recommend returning to annual-report document representation / parser benchmark planning rather than implementing an HTML render adapter.

## AgentController Prompt

Use this exact handoff prompt for the evidence worker:

```text
You are an evidence worker for fund-agent. Read AGENTS.md, docs/design.md, docs/implementation-control.md, docs/current-startup-packet.md, and docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md.

Execute only the CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Gate.

Write exactly one artifact:
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md

Allowed commands:
- bounded HTTP GET/HEAD only to official eid.csrc.gov.cn URLs discovered from accepted inputs or from indexXbrlData.json;
- local parsing of downloaded HTML/JSON content for metadata, headings, navigation labels, table samples, paragraph samples and content hashes;
- git diff --check for the single evidence artifact.

Forbidden:
- no production FundDocumentRepository/PDF/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- no code/test/runtime changes;
- no parser implementation;
- no Docling dependency or adapter;
- no raw XML direct-download claim unless a concrete official raw XML endpoint returns XML for a concrete instance;
- no field correctness or taxonomy compatibility claim;
- no readiness claim.

The evidence artifact must include explicit not-proof guards:
not_raw_xml_download_proof, not_field_correctness_proof, not_taxonomy_compatibility_proof, not_source_truth, not_readiness_proof, no_repository_behavior_change.

Stop after writing the evidence artifact and reporting its path plus git diff --check result.
```
