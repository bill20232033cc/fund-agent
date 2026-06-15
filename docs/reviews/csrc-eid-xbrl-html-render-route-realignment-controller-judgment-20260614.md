# CSRC EID XBRL HTML Render Route Realignment Controller Judgment

Date: 2026-06-14

Role: controller route decision

Verdict: `ACCEPT_ROUTE_REALIGNMENT_TO_XBRL_HTML_RENDER_EVALUATION_NOT_READY`

## Decision

Current mainline is realigned from `Annual-report Document Representation Sample Manifest And Candidate Schema No-live Implementation Gate` to `CSRC EID XBRL HTML Structured Render Artifact Evaluation Planning Gate`.

The immediate next work is a planning/evidence gate for official CSRC EID XBRL HTML render pages as candidate structured disclosure artifacts. The candidate source kind is `eid_xbrl_html_render_candidate`.

This decision supersedes the Docling/parser benchmark route as the current mainline, but does not delete it. Annual-report document representation / Docling benchmark work is deferred until the EID XBRL HTML render candidate has been evaluated against evidence projection needs.

Release/readiness remains `NOT_READY`.

## Inputs Reviewed

- `docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md`
- Prior route checkpoint: `docs/reviews/annual-report-document-representation-docling-benchmark-plan-controller-judgment-20260614.md`

## Accepted Evidence

- Official CSRC EID fund XBRL resource pages expose reachable standard packages, element list packages, technical guidance and sample XML resources.
- `indexXbrlData.json` exposes XBRL report list keys for fund disclosure categories.
- A concrete `instance_html_view.do?instanceid=...` request redirects to an official HTML render artifact under `/xbrl/REPORT/HTML/...`.
- The HTML render artifact is publicly reachable and contains structured report navigation/rendered disclosure content.

## Not Accepted

- No public raw XML/XBRL instance download endpoint is proven.
- No concrete announcement raw XML payload is accepted as directly downloadable.
- No field correctness is proven.
- No cross-year taxonomy compatibility is proven.
- No `schemaRef`, `contextRef`, `unitRef` or raw fact-level provenance is accepted for concrete announcements.
- No replacement of the current PDF parser, `FundDocumentRepository`, extractor, `EvidenceAnchor`, CHAPTER_CONTRACT, quality gate, renderer, Service, Host or UI behavior is authorized.

## Binding Route Constraints

1. Treat `eid_xbrl_html_render_candidate` as a candidate structured render artifact, not as raw XBRL instance truth.
2. Keep all source acquisition and render parsing inside `fund_agent/fund/documents` / `FundDocumentRepository` boundaries in future implementation gates.
3. Service, UI, Host, renderer and quality gate must not directly call EID XBRL endpoints, HTML render pages, parser cache or concrete parser helpers.
4. HTML, JSON, PDF parser output, Docling output and any raw intermediate representation remain extractor inputs or benchmark artifacts only. They are not fund fact truth until projected through extractor / section facts / `EvidenceAnchor` / fail-closed classification.
5. The first next gate must evaluate whether HTML render artifacts can support section/table/provenance projection into candidate `FundDisclosureDocument` / `EvidenceAnchor` semantics.
6. The evaluation standard is evidence projection support, not Markdown similarity or visual rendering similarity.
7. Preserve EID single-source annual-report production policy, no fallback expansion, no provider/default/runtime/budget changes, no LLM route enablement and no readiness/release/PR state change.

## Truth Sync Authorized

Authorized minimal write set:

- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/design.md`

`docs/design.md` may only record the XBRL HTML render route as `候选/研究输入`; it must not present raw XML availability, field correctness, taxonomy compatibility or production implementation as current facts.

## Next Gate

`CSRC EID XBRL HTML Structured Render Artifact Evaluation Planning Gate`

Required scope:

- define sample selection across annual, semi-annual, quarterly and net-value/temporary disclosures where available;
- define HTML render artifact identity and source metadata fields;
- define section/table/provenance extraction questions;
- define candidate mapping to `FundDisclosureDocument` and `EvidenceAnchor`;
- define explicit blocked proofs for raw XML download, field correctness and taxonomy compatibility;
- produce no code/runtime change unless a later implementation gate is accepted.
