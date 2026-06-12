# Plan Review DS: Data Artifact Disposition Planning Gate

Date: 2026-06-12

Reviewed target: `docs/reviews/mvp-data-artifact-disposition-plan-20260612.md`

Role: AgentDS, independent plan reviewer.

## 1. Boundary Compliance Verification

### Authorized reads

All declared reads match the allowed set. The plan reads the eight authorized control documents plus performs the eight metadata-only checks — no extra reads.

The audit artifact disposition evidence controller judgment `mvp-audit-artifact-disposition-evidence-controller-judgment-20260612-135642.md` is the correct upstream routing authority: its Section 7 explicitly recommends "Data Artifact Disposition Planning Gate for 基金年报/ PDFs" as the next mainline entry.

### Forbidden reads / actions

| Category | Not performed |
|---|---|
| PDF body reads or text extraction | Confirmed — only `wc -c` (byte count) and `du -sh` (directory size) |
| Source/test/runtime file inspection | Confirmed |
| Live/provider/EID/network/PDF/FDR/LLM commands | Confirmed |
| Cleanup/archive/delete/move/ignore/import/promote/stage/commit | Confirmed |

### Metadata check appropriateness

| Check | Classification | Appropriate? |
|---|---|---|
| `git status --short` | Metadata | Yes |
| `git status --branch --short` | Metadata | Yes |
| `git diff --check` | Metadata | Yes |
| `git ls-files -- 基金年报` | Metadata | Yes — confirms untracked |
| `git check-ignore -v 基金年报` | Metadata | Yes — confirms not ignored |
| `find 基金年报 -maxdepth 2 -type f -print` | Metadata | Yes — file inventory |
| `find 基金年报 -maxdepth 1 -type f -exec wc -c {} +` | Metadata | Yes — byte counts, not content |
| `du -sh 基金年报` | Metadata | Yes — aggregate directory size |

All checks are metadata-only. None reads PDF content. `wc -c` reads byte count, not file content. `du -sh` reads filesystem-level directory size.

## 2. Metadata-only Sufficiency and Scope

The plan's core architectural decision: a metadata-only evidence gate is sufficient to dispose the `基金年报/` PDFs as user-owned data artifacts left untracked.

This is correct because:

- **The question is ownership/disposition routing, not content correctness.** Classifying five untracked files as "user-owned data artifacts" requires knowing their existence, paths, sizes, and tracked/ignored status — all available from metadata without reading PDF bodies.
- **PDF content verification is a separate question.** Whether these PDFs are valid fund annual reports, have correct source identity, or could serve as fixtures is a content question that belongs in a future fixture/source-identity gate. The plan explicitly defers this.
- **The plan correctly limits scope.** Section 4: "PDF body read may only be considered in a future, explicitly authorized fixture/source-identity/data-ingestion gate that proves why metadata is insufficient." This establishes the correct evidentiary bar: metadata is sufficient for classification, content reading requires separate justification.

The plan's observed metadata is complete for classification purposes: five files, all at `基金年报/` top level, total 8097390 bytes (7.7M), untracked, not ignored. The filenames are visible from `find` output — they reveal fund names and report years, which is filesystem-level metadata, not PDF content.

## 3. PDF Body-read Prohibition and User/Data Artifact Ownership

The plan has layered, redundant guardrails against PDF body reads:

| Location | Guardrail |
|---|---|
| Section 1 | "This plan does not authorize PDF body reads, PDF text extraction..." |
| Section 2 | "Prohibited inputs/actions not used: PDF body reads, PDF text extraction..." |
| Section 4 | "PDF body read is not needed for that disposition and must remain prohibited by default." |
| Section 7 | "Explicitly disallowed validation: PDF body read or text extraction" |
| Section 8 | Review focus: "Verify no PDF body read or text extraction occurred." |

User ownership is correctly preserved:

- Default classification: "user-owned/data artifact candidate" (Section 4)
- Default disposition: "leave-untracked" (Section 4)
- Cleanup constraint: "deletion requires explicit user authorization" (Section 4)
- Residual table: Owner is "User / data-artifact owner + controller" (Section 9)

## 4. Prevention of PDFs Becoming Fixtures / Source Truth / Release Evidence / Readiness Proof / Product Scope

The plan has a comprehensive policy statement (Section 4):

> "These PDFs must not become fixtures, source truth, release evidence, readiness proof, golden inputs, source identity proof, or product scope merely because they are present in the workspace."

This is enforced through:

- Section 5 step 4: Evidence artifact must "explicitly reject fixture/source-truth/release-evidence/readiness-proof treatment"
- Section 7: No validation that would establish content-level proof (hash, integrity, source identity)
- Section 8: Review focus explicitly requires verification of this rejection
- Section 9: "PDF body content, source identity, integrity and suitability as fixtures remain unknown" — explicitly leaves the content question open

The plan correctly prevents the mere presence of PDF files from silently becoming accepted evidence.

## 5. FundDocumentRepository and EID Single-source Boundary Preservation

The plan correctly enforces the two key repository access constraints from AGENTS.md:

| Constraint | Plan enforcement |
|---|---|
| `FundDocumentRepository` is sole annual-report entry point | Section 3 truth-doc fact + Section 4: "These PDFs must not be used to bypass FundDocumentRepository" |
| EID single-source/no-fallback is current policy | Section 3 truth-doc fact + Section 4: PDFs must not bypass "current EID single-source/no-fallback source policy" |

The plan correctly references AGENTS.md lines 76-80 (FundDocumentRepository exclusivity) and design.md lines 657-661 (EID single-source policy). Local PDF files in the workspace cannot be used as an alternative data path — production access must go through the repository.

## 6. Write Set, Validation Matrix, Lifecycle, and Next Evidence Gate

### Write set (Section 6)

| Artifact | Gate |
|---|---|
| `mvp-data-artifact-disposition-plan-20260612.md` | This planning gate |
| `mvp-data-artifact-disposition-evidence-20260612.md` | Next evidence gate |
| Review artifacts (MiMo + DS) and controller judgment | After evidence worker |

Scoped to exactly one file per gate. No source, test, runtime, design, control, README, `.gitignore`, or `基金年报/` modification authorized.

### Validation matrix (Section 7)

Eight checks, all metadata-only. Each has explicit purpose, expected evidence, and per-gate authorization columns. The disallowed validation list is comprehensive: PDF body reads, PDF integrity/hash, live commands, analyze/checklist/golden/readiness/release, source/test/runtime suites, and cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge.

### Lifecycle (Section 8)

Standard 11-step pattern: plan → MiMo + DS review → controller judgment → checkpoint → evidence worker → MiMo + DS review → controller judgment → checkpoint → controller sync. Review focus areas are clearly specified and aligned with the plan's key guardrails.

### Next evidence gate (Section 9)

Metadata-only, no PDF body read, write exactly one file, preserve NOT_READY. Correctly gates any body read behind a future separate authorization.

## 7. NOT_READY

Explicitly preserved in three locations:
- Section 1: "Preserve NOT_READY."
- Section 9 stop condition: "Do not claim readiness."
- Final line: "**NOT_READY preserved.**"

Also required in the evidence artifact (Section 5 step 4) and review verification (Section 8).

## 8. Consistency with AGENTS/Design/Control Truth

| Claim | Truth-doc source | Consistent? |
|---|---|---|
| Current annual-report source policy is EID single-source/no-fallback | `docs/design.md` lines 657-661, `AGENTS.md` lines 76-80 | ✓ |
| Production access must go through `FundDocumentRepository` | `AGENTS.md` lines 76-78 | ✓ |
| `基金年报/` previously classified as user-owned unknown | Untracked residue disposition index row for `基金年报/` | ✓ |
| Next mainline from audit evidence controller judgment | Controller judgment Section 7: "Data Artifact Disposition Planning Gate for 基金年报/ PDFs" | ✓ |
| Evidence-chain indexes do not override truth docs | Startup packet Section 1, index preambles | ✓ |
| Release/readiness remains NOT_READY | Startup packet, control doc, prior controller judgments | ✓ |

## 9. Discrepancy Between Metadata Checks

The plan uses two `find` commands with different `-maxdepth` values:

| Check | Maxdepth | Captures |
|---|---|---|
| `find 基金年报 -maxdepth 2 -type f -print` | 2 | Files up to 1 level of subdirectory |
| `find 基金年报 -maxdepth 1 -type f -exec wc -c {} +` | 1 | Only top-level files |

If a PDF were placed in a subdirectory (e.g., `基金年报/subdir/file.pdf`), the inventory check (`maxdepth 2`) would find it but the size total check (`maxdepth 1`) would miss it, causing the size table to be inaccurate. Currently all five PDFs are at the top level so there is no actual gap. The evidence gate's required re-run of both checks would detect any structural change.

## 10. Findings

### Blocking

None.

### Non-blocking

| # | Finding | Severity | Rationale |
|---|---|---|---|
| N1 | The `wc -c` byte-count check uses `-maxdepth 1` while the inventory `find` uses `-maxdepth 2`. If a PDF were added in a subdirectory of `基金年报/`, the inventory would detect it but the size total would miss it, creating a metadata inconsistency. | Low | All five current PDFs are at the top level. The evidence gate's re-run of both checks would expose any change. The plan could align both to `-maxdepth 2` or add a note about the depth assumption. |
| N2 | The plan does not explicitly address what happens if `基金年报/` contents change (files added, removed, or renamed) between the planning gate and the evidence gate. | Low | The validation matrix requires re-running all metadata checks in the evidence gate, which would detect any changes. Implicitly handled but could be stated explicitly for robustness. |
| N3 | The plan's Section 4 policy says a metadata-only evidence gate is "sufficient" for disposition. This is technically correct for the classification question (ownership/disposition), but the evidence worker should be careful not to claim "sufficient" for any question beyond that. | Informational | The plan already limits this: Section 9 acknowledges "PDF body content, source identity, integrity and suitability as fixtures remain unknown." The scope boundary is clear. |

## 11. Verification Against Review Focus Questions

| Focus question | Assessment |
|---|---|
| Is metadata-only planning sufficient and correctly scoped? | **Yes.** Ownership/disposition classification doesn't require PDF content. Content verification is correctly deferred to future fixture/source-identity gate. |
| Does it preserve PDF body-read prohibition and user/data artifact ownership? | **Yes.** Five layered guardrails against body reads. User ownership preserved via classification, disposition, and deletion-authorization constraints. |
| Does it prevent PDFs from becoming fixtures/source truth/release evidence/readiness proof/product scope? | **Yes.** Explicit policy statement prohibits all seven categories. Evidence artifact must explicitly reject each. |
| Does it preserve FundDocumentRepository/EID single-source boundaries? | **Yes.** Both constraints are stated as truth-doc facts and enforced in the disposition policy. |
| Are write set, validation matrix, lifecycle and next evidence gate sufficient? | **Yes.** Single-file write set, 8-check metadata-only validation matrix, standard 11-step lifecycle, metadata-only evidence gate. |
| Is NOT_READY preserved? | **Yes.** Three locations in the plan, plus required in evidence artifact and review verification. |

## 12. Verdict

**PASS — no blocking findings.**

The plan correctly scopes a metadata-only planning gate for the `基金年报/` PDF residue. It:

- Classifies PDFs as user-owned data artifacts using only metadata (filenames, sizes, tracked/ignored status)
- Implements layered guardrails against PDF body reads, with body-read prohibition at five locations
- Prevents PDFs from silently becoming fixtures, source truth, release evidence, readiness proof, or product scope
- Preserves `FundDocumentRepository` as the sole annual-report entry point and EID single-source/no-fallback as the current source policy
- Provides a complete write set (one plan file), metadata-only validation matrix (8 checks), standard lifecycle (11 steps), and correctly scoped next evidence gate (metadata-only, no body read)
- Preserves NOT_READY at three locations

Three non-blocking findings (N1–N3) — all low or informational, none affecting plan soundness.
