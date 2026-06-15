# Docling Baseline Qualification Acquisition Status Plan Controller Judgment - 2026-06-15

Gate: `Docling Baseline Qualification Acquisition Status Planning Gate`
Role: controller
Readiness state: `NOT_READY`

## 1. Scope

This judgment closes the acquisition-status planning gate for Docling baseline qualification. It accepts or rejects the planning artifact only.

This judgment does not authorize Docling conversion, EID acquisition, live/network/PDF/FDR, pdfplumber export, manual reference review, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, production parser replacement, `FundDocumentRepository` behavior change, source policy change, Service/UI/Host/renderer/quality-gate direct parser access, raw XML claim, field correctness claim, taxonomy compatibility claim, source-truth claim, push or PR.

## 2. Artifacts Reviewed

- Plan: `docs/reviews/docling-baseline-qualification-acquisition-status-plan-20260615.md`
- DS review: `docs/reviews/docling-baseline-qualification-acquisition-status-plan-review-ds-20260615.md`
- MiMo review: `docs/reviews/docling-baseline-qualification-acquisition-status-plan-review-mimo-20260615.md`
- Parent accepted judgment: `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md`
- Current control docs: `docs/current-startup-packet.md`, `docs/implementation-control.md`

## 3. Accepted Plan Facts

| Fact | Controller disposition |
|---|---|
| S1 `004393 / 2025` is the only sample with accepted Docling, pdfplumber and EID HTML full representation JSONs. | ACCEPT |
| S2-S4 have visible EID-labeled local cache candidates and manual identity evidence, but still require no-live local provenance acceptance before baseline qualification use. | ACCEPT |
| S5-S6 have visible local PDFs that are not EID-labeled; they require bounded EID-only acquisition or profile-preserving replacement before active-sample use. | ACCEPT |
| Existing small-golden `expected_fields.json` and manual intake artifacts are reference candidates, not automatic field-truth for Docling baseline qualification. | ACCEPT |
| Route agreement cannot be used as field correctness or source truth. | ACCEPT |
| Gate 0A must be metadata-only and must not read PDF bodies or run repository/parser/conversion/network/provider commands. | ACCEPT |
| Future pdfplumber full representation export must be repository-owned or accepted as a repository-internal diagnostic runner; no Service/UI/Host/renderer/quality gate direct PDF/parser access. | ACCEPT |
| EID HTML render for S2-S6 remains unclassified; no URL fabrication or raw XML/XBRL proof claim is allowed. | ACCEPT |
| Release/readiness remains `NOT_READY`. | ACCEPT |

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Metadata query allowlist should be explicit. | DS | ACCEPT_AS_REQUIRED_NONBLOCKING_FIX | CLOSED in plan Gate 0A. |
| Gate 0C should explicitly require repository-owned export path and no ad hoc direct PDF body reads. | DS | ACCEPT_AS_REQUIRED_NONBLOCKING_FIX | CLOSED in plan Gate 0C. |
| Plan status and final verdict should use consistent tokens. | DS | ACCEPT_AS_REQUIRED_NONBLOCKING_FIX | CLOSED by status update to `READY_FOR_PLAN_REVIEW_NOT_READY`. |
| Plan preserves candidate-only, `NOT_READY`, no fallback, no source-truth and S5/S6 EID-only requirements. | MiMo | ACCEPT | No change required. |

No blocking finding remains.

## 5. Blocked Claims

The following claims remain blocked:

- Docling is baseline candidate;
- Docling is production baseline;
- Docling output is source truth;
- field correctness is proven;
- raw XML / raw XBRL direct download is proven;
- taxonomy compatibility is proven;
- EID HTML render is source truth;
- S2-S6 are accepted baseline qualification samples;
- S5/S6 local PDFs can be used without EID provenance;
- `FundDocumentRepository` behavior can change;
- production parser replacement;
- readiness/release/PR readiness.

## 6. Residuals

| Residual | Owner | Next handling | Blocks next gate? |
|---|---|---|---|
| `AGENTS.md` remains modified but rejected by separate rules-sync review. | Rules owner / controller | Separate rules-sync rewrite gate; do not stage current diff. | No, if unstaged and not used as source of truth beyond current effective rules. |
| Untracked historical/runtime/research residue remains. | Artifact owners | Deferred disposition gates; leave untracked. | No for metadata-only Gate 0A; yes for PR/readiness cleanliness. |
| S2-S6 provenance, pdfplumber export, reference coverage and EID HTML availability remain unproven. | Fund documents/source research owner | Gate 0A first, then 0B/0C/0D/0E as applicable. | No; this is exactly next gate scope. |

## 7. Next Gate

Primary next gate:

`Docling Baseline Qualification Local Artifact Provenance Status Evidence Gate`

Gate 0A must be metadata-only and write:

`docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-20260615.md`

Allowed command family:

- branch/status;
- `ls -lh` / `stat` for explicit sample paths;
- `python -m json.tool` for explicit metadata JSON;
- allowlisted `jq` metadata queries;
- `git diff --check`.

Forbidden:

- PDF body reads;
- PDF parsing;
- Docling conversion;
- pdfplumber export;
- `FundDocumentRepository` execution;
- EID/FDR/network/live commands;
- non-EID fallback;
- provider/LLM/analyze/checklist/golden/readiness/release/PR commands.

## 8. Validation

Required validation:

```text
git diff --check
```

Controller result: passed after plan, review artifacts and this judgment were written.

## 9. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_LOCAL_ARTIFACT_PROVENANCE_STATUS_EVIDENCE_GATE_NOT_READY`
