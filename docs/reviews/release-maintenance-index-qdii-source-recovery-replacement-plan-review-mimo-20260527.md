# Plan Review: index/QDII source recovery and replacement plan

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Gate: `index/QDII source recovery and replacement decision gate`
> Review target: `docs/reviews/release-maintenance-index-qdii-source-recovery-replacement-plan-20260527.md`

## Truth Sources Consulted

| Source | Sections checked |
|---|---|
| `AGENTS.md` | FundDocumentRepository boundary, fallback fail-closed contract, indirect evidence prohibition |
| `docs/design.md` | §6.1 文档仓库层, §6.2 结构化抽取层, §7.4 质量门控规则 |
| `docs/implementation-control.md` | Startup Packet, Current Gate, Next Entry Point, Open Residuals, baseline coverage recovery decision controller judgment |
| baseline coverage recovery decision controller judgment | Accepted next gate boundaries, `extraction-snapshot` is real repository access |

## Verdict

**PASS**

Plan is repository-safe, fail-closed, and bounded. No material findings. No re-review required.

## Checklist Results

| # | Check | Result |
|---|---|---|
| 1 | Repository-safe: no bypass of FundDocumentRepository, no direct PDF/cache/source-helper | PASS. Section 2 Forbidden list and Section 7 Hard Prohibitions both explicitly forbid direct PDF/cache/source-helper/downloader access. Section 4 allowed commands use only `extraction-snapshot` / `extraction-score` / `quality-gate` which route through `FundDataExtractor` → `FundDocumentRepository`. |
| 2 | Public CLI evidence recovery, no indirect evidence | PASS. Section 3.1 step 4 explicitly prohibits inferring root cause from indirect symptoms. Four-state classification (`recovered_eligible`, `recovered_fail_closed`, `unrecoverable_safe_path`, `repository_run_failed`) limits recovery to evidence-based outcomes. |
| 3 | Replacement candidate rules prevent ad hoc search / incorrect elevation | PASS. Section 3.2 requires controller-supplied or accepted-artifact-derived candidates only, `repository_verified`, exact `fund_type_slot`, no unknown fallback boundary, and explicitly closes as `not_run_no_approved_candidates` with stop instead of ad hoc web/search. |
| 4 | Stop conditions cover fail-closed, identity/type mismatch, fallback unknown, large outputs, golden pressure | PASS. Section 5 covers all five fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`), identity/type mismatch (5.4), fallback unknown (5.3), large outputs (5.10), and golden/baseline pressure (5.11). |
| 5 | Commands/outputs bounded; `extraction-snapshot` treated as real repository access | PASS. Section 4 explicitly states `extraction-snapshot` / `extraction-score` / `quality-gate` are "real repository/product-path evidence commands, not lightweight read-only probes." Allowed command set is closed. Output policy separates tracked artifacts (summary/path only) from scratch/ignored paths. |

## Material Findings

None.

## Informational Findings

### F1: `extraction-snapshot` as sole evidence path assumption

**Severity**: Informational
**Location**: Section 3.1

The plan assumes `extraction-snapshot` will expose the original upstream failure category for `110020` and `017641`. If the original failure is specific to the `analyze` / `checklist` code path and does not manifest in `extraction-snapshot`, the row would be classified `unrecoverable_safe_path` and remain excluded. The plan handles this conservatively (the row stays outside clean denominator), but does not explicitly acknowledge that `extraction-snapshot` coverage of the failure category is an assumption, not a guarantee.

**Disposition**: Acceptable as-is. The `unrecoverable_safe_path` state is the correct conservative classification. The assumption is low-risk because `extraction-snapshot` exercises the same `FundDataExtractor` → `FundDocumentRepository` → sources pipeline. No change required.

### F2: Cache artifact output policy gap

**Severity**: Informational
**Location**: Section 4 Output rules

The output rules list "downloaded/cache artifacts" as scratch/ignored, but the `cache/annual-reports/` directory is not explicitly listed as an ignored path. If the evidence gate triggers `FundDocumentRepository.load_annual_report()` for a fund whose PDF is not cached, the downloaded PDF will land in `cache/annual-reports/{fund_code}/{year}.pdf`. This is a minor gap in the output policy specificity.

**Disposition**: Acceptable as-is. The plan's intent is clear (large outputs stay untracked), and the evidence gate closeout artifact should explicitly state the cache path is scratch. No change required.

### F3: Downstream path when both rows are unrecoverable

**Severity**: Informational
**Location**: Section 3.1, Section 6

If both `110020` and `017641` are classified `unrecoverable_safe_path` after the evidence gate, the plan correctly keeps them excluded. However, it does not explicitly state what the next gate should do in this scenario—whether to attempt another evidence approach, accept the coverage gap, or proceed to durable baseline with reduced coverage. The closeout requirement (Section 6) states "the correct next state is stop/exclude, not repeated probing," but does not define the next gate's options.

**Disposition**: Acceptable as-is. The controller judgment for the next gate will determine the path forward. The plan correctly stops rather than looping. No change required.

## Re-Review Required

No. All findings are informational and do not affect plan safety or correctness.

## Summary

The plan correctly replays Startup Packet, preserves fail-closed source semantics, treats `extraction-snapshot` as real repository access, requires controller-approved replacement candidates, covers all stop conditions, and bounds commands/outputs. The plan aligns with AGENTS.md hard constraints, design.md §6 source boundaries, implementation-control.md Next Entry Point, and the baseline recovery decision controller judgment's accepted next gate boundaries.
