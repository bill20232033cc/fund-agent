# CSRC EID XBRL HTML Evidence Closeout / Control Sync Controller Judgment

Date: 2026-06-14

Phaseflow gate: `XBRL HTML evidence closeout / control sync gate`

Controller role: controller closeout and control sync only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_CLOSEOUT_READY_FOR_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_DESIGN_GATE_NOT_READY`

## 1. Scope

This gate reconciles the accepted `CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Gate` with current control truth.

This gate does not:

- implement source/parser/repository behavior;
- change tests or runtime behavior;
- change `FundDocumentRepository`;
- change `EvidenceAnchor` schema;
- change CHAPTER_CONTRACT;
- run production PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- claim raw XML download, field correctness, taxonomy compatibility, source truth, readiness or release readiness.

## 2. Evidence Reviewed

Accepted evidence and controller artifacts:

- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-post-gate-artifact-disposition-20260614.md`

Truth/control inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 3. Accepted Current Facts

| Fact | Disposition |
|---|---|
| Official EID `indexXbrlData.json` was reachable in bounded evidence and returned current JSON metadata | `ACCEPT` |
| 12 sampled rows across required EID XBRL lists resolved through `instance_html_view.do?instanceid=<idStr>` | `ACCEPT` |
| Final official `/xbrl/REPORT/HTML/...html` pages returned `200`, `text/html; charset=utf-8`, byte size and content hash | `ACCEPT` |
| Final render pages contain `<title>XBRL</title>` and `instance_navigation` | `ACCEPT` |
| Navigation labels, section headings, table cells and paragraph-like notes are locally extractable | `ACCEPT` |
| Candidate row/column locators can be formed for representative samples | `ACCEPT_WITH_RESIDUAL` |
| Candidate source classification remains `eid_xbrl_html_render_candidate` | `ACCEPT` |

## 4. Rejected / Blocked Claims

| Claim | Controller disposition |
|---|---|
| HTML render is raw XML / raw XBRL instance truth | `REJECT` |
| Concrete raw XML direct download is proven | `REJECT` |
| Field correctness is proven | `REJECT` |
| Taxonomy `schemaRef` / `contextRef` / `unitRef` compatibility is proven | `REJECT` |
| HTML render can replace production PDF parser now | `REJECT` |
| Service/UI/Host/renderer/quality gate may directly fetch EID HTML/XBRL endpoints | `REJECT` |
| Release/readiness should move beyond `NOT_READY` | `REJECT` |

## 5. Control Sync Decision

The previous current gate:

```text
CSRC EID XBRL HTML Structured Render Artifact Evaluation Planning Gate
```

is superseded by accepted plan and accepted evidence artifacts.

The current phase should remain:

```text
CSRC EID XBRL HTML render artifact evaluation route
```

The new next entry point should be:

```text
FundDisclosureDocument Candidate Source Design Gate
```

## 6. Phaseflow Recommendation

Mainline phaseflow from this checkpoint:

```text
A. XBRL HTML evidence closeout / control sync gate
B. FundDisclosureDocument Candidate Source Design Gate
C. Design review gate with DS + MiMo
D. Candidate source schema planning gate
E. Narrow no-live implementation gate, only after accepted design and plan
F. Same-report comparison evidence gate: EID HTML render vs current pdfplumber
G. Optional Docling benchmark gate, only if EID HTML + pdfplumber cannot cover target representation
H. Extractor projection planning gate
I. Readiness / release deferred
```

## 7. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Ordinary non-REIT annual/interim sample expansion | `OPEN` | Include as design/evidence residual; do not block design gate. |
| Locator normalization for repeated headings, hidden title tables, nested/merged table structure | `OPEN` | Candidate design must define schema and failure classes. |
| Raw XML endpoint route | `OPEN_BLOCKED` | Separate future endpoint evidence only if a public endpoint is discovered. |
| Field correctness validation | `OPEN` | Later validation gate, not design closeout. |
| Full CHAPTER_CONTRACT narrative coverage | `OPEN` | Compare against PDF/Docling routes later. |
| Production behavior | `NOT_AUTHORIZED` | Requires later accepted implementation gate. |
| Release/readiness | `NOT_READY` | Preserved. |

## 8. Final Verdict

`VERDICT: ACCEPT_CLOSEOUT_READY_FOR_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_DESIGN_GATE_NOT_READY`

Controller may sync `docs/current-startup-packet.md` and `docs/implementation-control.md` to set the next entry point to `FundDisclosureDocument Candidate Source Design Gate`.
