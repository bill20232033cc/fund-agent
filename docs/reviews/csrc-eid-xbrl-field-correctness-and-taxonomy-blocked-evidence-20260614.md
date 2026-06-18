# CSRC EID XBRL Field Correctness And Taxonomy Compatibility Blocked Evidence

Date: 2026-06-14
Gate: `XBRL Field Correctness Proof` and `CSRC Fund XBRL Taxonomy Cross-Year Compatibility Proof`
Worker role: evidence worker only; not controller
Readiness state: `NOT_READY`

## 1. Scope

This artifact records why the field-correctness and taxonomy-compatibility gates cannot validly proceed as raw-XML fact proofs after `CSRC EID XBRL Raw Instance Download Proof`.

It does not parse production report facts, does not compare field values, does not inspect DTS package contents, does not change `FundDocumentRepository`, does not replace the current PDF parser, and does not change release/readiness state.

## 2. Blocking Precondition

The field-correctness plan requires concrete raw XML facts:

- QName
- value
- `contextRef`
- `unitRef`
- `decimals`
- tuple/dimension/row identity
- `link:schemaRef`

The taxonomy-compatibility plan requires concrete instance taxonomy references:

- `schemaRef`
- namespace URI
- report type code
- report year
- DTS package relation

The raw-instance download evidence did not discover a public raw XML instance URL for 12 sampled concrete announcements across quarterly, annual, temporary-announcement, and fund-contract-effective rows. It proved generated XBRL HTML views, but not raw XML instances.

## 3. Result

| Planned proof | Status | Reason |
|---|---|---|
| XBRL field correctness from raw XML facts | `BLOCKED_BY_RAW_XML_NOT_PROVEN` | No concrete raw XML fact source was discovered. |
| XBRL fact to `EvidenceAnchor` mapping | `BLOCKED_BY_RAW_XML_NOT_PROVEN` | No QName/context/unit tuple can be read from concrete reports. |
| Taxonomy cross-year compatibility from concrete `schemaRef` | `BLOCKED_BY_RAW_XML_NOT_PROVEN` | Generated HTML path does not expose concrete instance `schemaRef`. |
| Raw XML direct download | `NOT_PROVEN` | 12 samples expose HTML views; path-derived raw XML probes returned 404. |

## 4. Non-Equivalent Evidence

These facts are useful but insufficient:

| Available evidence | Why it is insufficient |
|---|---|
| Official `example1.xml` is XBRL-shaped | It is a sample XML, not a concrete production report instance. |
| Official DTS and element-list zip URLs return 200 | They prove official resources are reachable, not which taxonomy a concrete report used. |
| Concrete report HTML views are reachable | HTML views may be generated from XBRL, but they are not raw XML facts with `schemaRef`, `contextRef`, and `unitRef`. |
| HTML paths contain year and report type code | Path metadata is not a taxonomy reference. |

## 5. Recommended Re-route

The next valid route is not field correctness from raw XML. It is one of:

1. `CSRC EID XBRL Raw XML Endpoint Discovery Deep Probe Gate`
   - Goal: find an official public endpoint for raw XML instance download.
   - Stop condition: no endpoint discovered after documented JavaScript and public-link inspection.

2. `CSRC EID XBRL HTML Structured Render Artifact Evaluation Gate`
   - Goal: evaluate the generated HTML report as a structured render artifact.
   - Required caveat: source kind must not be called `raw_xbrl`; it should be a separate candidate such as `eid_xbrl_html_render`.
   - Required proof: HTML table cells must be mapped to stable section/table/row locators before any field claim.

## 6. Stop Rule

This artifact does not authorize:

- production source strategy changes
- `FundDocumentRepository` behavior changes
- raw XML availability claims
- field correctness claims
- taxonomy compatibility claims
- extractor migration
- direct Service/UI/Host/renderer/quality-gate access to XBRL endpoints
- parser replacement
- provider/LLM route changes
- readiness, release, PR, cleanup, or merge state changes
