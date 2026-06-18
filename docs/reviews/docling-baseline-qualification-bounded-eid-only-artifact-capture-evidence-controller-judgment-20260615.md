# Docling Baseline Qualification Bounded EID-only Artifact Capture Evidence Controller Judgment - 2026-06-15

Gate: `Bounded EID-only Sample Acquisition Artifact Capture Evidence Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the staged EID-only artifact-capture evidence gate for S4/S5/S6.

This judgment accepts only the staged PDFs under `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/`. It does not accept, promote, overwrite, delete, move, rename or archive any production-shaped `cache/pdf` file. It does not run or change `FundDocumentRepository`, Docling, pdfplumber, analyzer/checklist, provider/LLM, golden/readiness/release/PR/push/merge behavior.

## 2. Artifacts Reviewed

- Evidence: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-20260615.md`
- DS-role review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-review-ds-20260615.md`
- MiMo-role review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-review-mimo-20260615.md`
- Plan controller judgment: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-controller-judgment-20260615.md`
- Metadata evidence controller judgment: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-controller-judgment-20260615.md`
- Current truth docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## 3. Accepted Evidence Facts

| Sample | Controller disposition | Staged path | SHA-256 |
|---|---|---|---|
| S4 `006597 / 2024` | ACCEPT as `eid_artifact_captured_staged` | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf` | `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982` |
| S5 `017641 / 2024` | ACCEPT as `eid_artifact_captured_staged` | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf` | `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c` |
| S6 `110020 / 2024` | ACCEPT as `eid_artifact_captured_staged` | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf` | `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790` |

Accepted request/integrity facts:

- each request used the accepted official EID `uploadInfoId`;
- each response returned HTTP `200`;
- each final host was `eid.csrc.gov.cn`;
- each response content type was `application/pdf`;
- each staged artifact begins with `%PDF-`;
- each staged artifact has a recorded byte size and SHA-256;
- no `.incomplete` file remained after capture;
- `cache/pdf/006597_2024_annual_report_eid.pdf` retained `mtime=May 29 05:51:59 2026`, so this gate did not overwrite it.

Whole-gate verdict accepted:

`ALL_REQUIRED_EID_ARTIFACTS_CAPTURED_STAGED_NOT_READY`

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| S4 staged byte size equals existing S4 `cache/pdf` byte size and could confuse later readers. | DS-role review | ACCEPT_AS_CLARIFICATION | Same byte size does not validate, promote or accept the old `cache/pdf/006597_2024_annual_report_eid.pdf`; only the staged path is accepted by this gate. |
| No evidence gate boundary violation found. | MiMo-role review | ACCEPT | Closed. |
| Staged artifact integrity evidence is sufficient for staged artifact capture. | DS-role / MiMo-role reviews | ACCEPT | Closed. |
| No field correctness/source truth/Docling baseline/readiness claim. | DS-role / MiMo-role reviews | ACCEPT | Closed. |

No unresolved blocking finding remains.

## 5. Rejected Or Deferred Claims

| Claim | Disposition | Reason |
|---|---|---|
| Existing S4 `cache/pdf/006597_2024_annual_report_eid.pdf` is accepted or repaired. | REJECT | This gate did not overwrite or promote that file; prior provenance conflict remains for the old production-shaped path. |
| Staged PDFs are production cache entries. | REJECT | They live under gate-owned staging path, not `cache/pdf`. |
| Staged PDFs prove field correctness or source truth. | REJECT | No table/narrative values were compared. |
| Staged PDFs prove Docling baseline qualification. | REJECT | No Docling conversion, representation export or quality comparison was run. |
| Staged PDFs prove pdfplumber export quality. | REJECT | No pdfplumber export was run. |
| Release/readiness improved to ready. | REJECT | Release/readiness remains `NOT_READY`. |
| Non-EID fallback is allowed. | REJECT | No fallback was used; EID single-source/no fallback remains binding. |
| S3 hash gap is closed. | DEFER | This gate handled S4/S5/S6 only. |

## 6. Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Staged PDFs are not production-shaped cache entries. | open | Controller / documents owner | Choose between cache promotion planning or direct staged-path export planning. |
| Existing S4 `cache/pdf` provenance conflict remains. | open | Controller / artifact owner | Do not use as accepted source unless a later promotion/replacement gate resolves it. |
| Representation export and route comparison not run for S4/S5/S6. | open | Controller / representation owner | `Full Representation Export Planning Gate`. |
| S3 hash gap remains. | accepted residual | Controller / export planning owner | Carry to later expansion if needed. |
| Control docs lag latest accepted gate chain. | open | Controller | Scoped control sync gate. |

## 7. Next Gate Recommendation

Recommended next gate:

`Full Representation Export Planning Gate`

Reason:

- S4/S5/S6 now have accepted staged EID-controlled PDFs;
- the next product question is whether Docling/pdfplumber/EID HTML representation comparison can consume staged paths directly;
- production-shaped cache promotion should be deferred unless an export tool requires `cache/pdf`.

Deferred gate:

`EID Staged PDF Cache Promotion Planning Gate`

Use this only if later export tooling cannot consume explicit staged paths.

## 8. Validation

```text
git diff --check
passed
```

## 9. Final Verdict

`VERDICT: ACCEPT_STAGED_EID_ARTIFACT_CAPTURE_READY_FOR_FULL_REPRESENTATION_EXPORT_PLANNING_NOT_READY`
