# CSRC EID XBRL HTML Structured Render Artifact Evaluation Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `CSRC EID XBRL HTML Structured Render Artifact Evaluation Planning Gate`

Verdict: `ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_EVIDENCE_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment reviews whether `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md` can serve as the handoff-ready evidence plan for the next evidence gate.

No source, test, runtime, `FundDocumentRepository`, parser, source policy, extractor, `EvidenceAnchor` schema, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, readiness, release, PR, push or merge behavior is changed by this judgment.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md`
- `docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md`

No production `FundDocumentRepository`, PDF, provider, LLM, analyze, checklist, golden, readiness, release, PR, push or merge command was run for this judgment.

## 3. Plan Disposition

The plan is accepted with binding amendments.

Accepted strengths:

- It correctly names the candidate source classification as `eid_xbrl_html_render_candidate`.
- It does not call the route raw XML or raw XBRL instance truth.
- It preserves `NOT_READY`.
- It keeps HTML render, JSON and parser intermediates below fund fact truth.
- It rejects production parser replacement, repository behavior changes, source policy changes, LLM route changes, field correctness claims and taxonomy compatibility claims.
- It defines artifact identity, section/table/narrative projection questions and candidate `EvidenceAnchor` mapping.
- It defines stop rules for auth/captcha/manual browser state, missing concrete instance ids, blank/binary/image-only HTML, off-domain redirects and prohibited production commands.

Required amendments before evidence execution:

1. Replace the plan's smaller sample minimum with the current controller/user-required matrix:
   - quarterly report: 3 rows from `seasonXBRLReportList`;
   - annual/interim report: 3 rows from `halfyearXBRLReportList`, including non-REIT if discoverable;
   - temporary announcement: 3 rows from `noticeXBRLReportList`;
   - fund contract effective announcement: 3 rows from `fAXBRLReportList`.
2. For each row, record the full required metadata:
   - source list;
   - `fundcode`;
   - `fundidStr`;
   - `idStr`;
   - `reportYear`;
   - `reportTypereportDesp`;
   - `reportSendDate`;
   - `instance_html_view` HTTP status;
   - redirect location;
   - final HTML status;
   - final HTML byte size;
   - `<title>XBRL</title>` presence;
   - `instance_navigation` presence;
   - major visible section labels;
   - render artifact classification;
   - raw XML status remains `not_proven`.
3. The evidence worker may use bounded HTTP GET/HEAD only to official `eid.csrc.gov.cn` URLs discovered from accepted inputs or `indexXbrlData.json`.
4. The evidence worker may locally parse downloaded HTML/JSON for metadata, headings, navigation labels, table samples, paragraph samples and content hashes.
5. The evidence artifact must explicitly include these guard labels:
   - `not_raw_xml_download_proof`;
   - `not_field_correctness_proof`;
   - `not_taxonomy_compatibility_proof`;
   - `not_source_truth`;
   - `not_readiness_proof`;
   - `no_repository_behavior_change`.

## 4. Rejected / Blocked Claims

| Claim | Decision | Reason |
|---|---|---|
| HTML render proves raw XML direct download. | REJECT | Prior raw XML endpoint probes remain `NOT_PROVEN`; HTML render is a separate render artifact. |
| HTML render is raw XBRL instance truth. | REJECT | Candidate classification is `eid_xbrl_html_render_candidate`, not `raw_xbrl`. |
| HTML table cells prove field correctness. | REJECT | Correctness requires later source/field validation; this gate only evaluates render artifact availability and locator candidates. |
| HTML render proves taxonomy schemaRef compatibility. | REJECT | No concrete raw instance `schemaRef` matrix is accepted. |
| HTML render changes production source/parser/repository behavior. | REJECT | This gate is evidence-only; production behavior remains unchanged. |
| HTML render is readiness/release proof. | REJECT | Release/readiness remains `NOT_READY`. |

## 5. Next Gate

Proceed to:

```text
CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Gate
```

Required evidence artifact:

```text
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md
```

Stop conditions:

- official EID HTML render requires auth/captcha/manual browser state;
- public JSON list cannot provide concrete instance id or HTML view path;
- HTML body is blank, binary-only or image-only for all samples;
- redirects leave official EID domains;
- evidence requires production repository/source/parser/LLM/analyze/checklist/readiness/release/PR commands.

If blocked, the evidence artifact must report `BLOCKED_NOT_READY` with exact failing URL, status and error class.

## 6. Final Verdict

VERDICT: `ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_EVIDENCE_GATE_NOT_READY`

The plan is handoff-ready only with the binding amendments above. The next evidence gate may proceed under these constraints. Release/readiness remains `NOT_READY`.
