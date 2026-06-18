# Provider/LLM Chapter 3 Code-bug Root-cause Evidence Review — AgentMiMo

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Code-bug Root-cause Evidence Gate`

Role: AgentMiMo visible-panel evidence review only.

Verdict: **PASS**

## Review Questions

### Q1. No-live Boundary

Does the evidence artifact respect no-live boundary and avoid source/test/runtime/control/design changes except its own review artifact?

**PASS.** Section 1 explicitly declares the no-live boundary. Section 3 commands include only: `git status --branch --short`, `git status --short`, `git diff --name-only`, `git diff --check`, `rg` locator patterns, `sed` reads of plan/control/review artifacts, `uv run pytest` on four existing test files (`-q`), and `uv run ruff check` on six source + four test files. No source, test, fixture, assertion, runtime behavior, control doc or design doc was modified. No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR/cleanup/stage/commit/push/merge/archive commands were executed.

The memory `rg` command over `/Users/maomao/.codex/memories/MEMORY.md` was an unauthorized-by-handoff deviation. The artifact correctly classifies it as `DEVIATION_NOT_EVIDENCE` in Section 4 and asserts no H1-H5 classification relies on it. This residual is properly recorded for reviewer/controller disposition.

### Q2. EID Single-source Preservation

Does it correctly preserve current source truth as EID single-source only, with Eastmoney/fund-company/CNINFO/fallback not current source truth, not current execution path, and not authorized?

**PASS.** Section 1 and Section 10 both explicitly state: operational annual-report source truth remains EID single-source only (`selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`). Eastmoney, fund-company/CDN, CNINFO and annual-report fallback are correctly classified as not current execution paths, not current source truth and not authorized current sources. The artifact does not modify source acquisition policy and does not reintroduce fallback.

### Q3. Unauthorized Memory rg Classification

Does it correctly classify the unauthorized memory rg command as DEVIATION_NOT_EVIDENCE and process residual, without relying on it for H1-H5?

**PASS.** Section 4 "Process Boundary Deviation / Controller Boundary Finding" explicitly classifies the `rg` over MEMORY.md as `DEVIATION_NOT_EVIDENCE`: "actual command occurred, but it was unauthorized by the handoff allowed-command list and is not valid gate evidence. No source truth or root-cause conclusion is derived from this output." The artifact asserts: "No H1-H5 classification relies on memory output." This residual is recorded for reviewer/controller disposition without contaminating evidence classifications.

### Q4. H1-H5 Evidence-based Dispositions

Are H1-H5 dispositions evidence-based and consistent with the accepted plan?

**PASS.** All five dispositions match the plan's accept/reject signals:

| Hypothesis | Disposition | Plan signal | Consistent |
|---|---|---|---|
| H1 | `rejected` for covered typed path | "If fake writer is called successfully, H1 is rejected" — existing tests prove Chapter 3 reaches fake writer | Yes |
| H2 | `rejected` for currently inspected rows | "If all Chapter 3 typed requirements and availability rows are coherent... reject H2" — ch3.required_output.item_03 coherent | Yes |
| H3 | `MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY` | Plan allowed this classification for expected-but-generic mapping | Yes |
| H4 | `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` | Plan allowed this classification when cap exists in runtime plan but absent in first-failed diagnostic | Yes |
| H5 | `rejected` | "If artifact writer is faithful to serializer output, reject H5" — no extraction mismatch found | Yes |

Each disposition cites exact source/test evidence with file paths and line ranges. Residual routing (missing reproducer, missing assertion, missing fixture) correctly defers to future no-live gates.

### Q5. Targeted Validation Results

Are targeted validation results recorded and sufficient for this evidence gate?

**PASS.** Section 3 records: `uv run pytest` — `125 passed in 1.07s` across all four allowed test files; `uv run ruff check` — `All checks passed!` across all six source + four test files. Static code inspection covers all required files listed in Section 5, with specific `sed` ranges and `rg` patterns recorded. Existing test assertions for runtime plan propagation, typed path, diagnostics, code-bug classification, fake writer reachability and artifact safety are all verified. For a no-live evidence gate limited to existing tests and static/read-only inspection, the validation results are sufficient.

### Q6. NOT_READY Preservation

Does it preserve NOT_READY and avoid provider readiness, LLM content quality, release readiness, PR readiness, repeat-live, fallback or source-policy claims?

**PASS.** Section 10 explicitly states: "No current evidence supports a broad provider readiness, LLM content quality, source fallback, release readiness or PR readiness claim." The verdict concludes: "Release/readiness remains NOT_READY." EID single-source/no-fallback is preserved. No provider readiness, LLM content quality, release readiness, PR readiness, repeat-live, fallback or source-policy claims are made anywhere in the artifact.

## Residual Table

| Residual | Disposition |
|---|---|
| Memory `rg` command over MEMORY.md was an unauthorized-by-handoff deviation | Closed by DEVIATION_NOT_EVIDENCE classification in Section 4; no H1-H5 contamination; residual recorded for controller disposition |
| Missing exact Chapter 3 fake-writer reproducer for `004393 / 2025` live failure shape | Routed to future no-live `Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate` |
| Missing bridge projection assertion for pre-provider ValueError -> Service llm_exception/code_bug/safe metadata | Routed to future no-live diagnostic/test implementation planning gate |
| Missing pre-provider max_output_chars assertion | Routed to future no-live diagnostic/test implementation planning gate (H4 residual) |
| Missing artifact code-bug/pre-provider fixture | Routed to future no-live artifact diagnostic/test implementation planning gate (H5 residual) |

All residuals are correctly routed and do not authorize source/test/runtime edits, repeat live execution, source policy changes, fallback, readiness/release claims, PR, push, merge, mark-ready or cleanup.

## Summary

The evidence artifact satisfies all six review questions. H1-H5 dispositions are evidence-based, consistent with the accepted plan, and correctly classify `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` as the strongest current root-cause finding. The unauthorized memory rg deviation is properly classified and does not contaminate evidence. NOT_READY and EID single-source/no-fallback are preserved. Residuals are correctly routed to future no-live gates.

Recommended next step: controller judgment on this evidence artifact. If accepted, route the four missing-reproducer/assertion/fixture residuals to a future no-live `Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate` before any code fix or repeat live/provider execution.
