# Bond Positive-Risk Evidence Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `release-maintenance bond positive-risk evidence gate`
> Plan artifact: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `release-maintenance consolidation / QDII post-021539 disposition accepted locally` |
| Startup Packet next entry point | `bond positive-risk evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `8083340 docs: accept qdii post 021539 disposition` |

This gate follows the Startup Packet next entry point. No cursor switch is required.

## Truth Preflight Judgment

The preflight found a truth-source mismatch: `docs/implementation-control.md` referenced `AGENTS.md` Gate classification rules, but `AGENTS.md` did not define `fast_path`, `standard`, or `heavy`.

Controller judgment:

- **Accepted** as truth-source mismatch.
- **Fixed** by adding a concise `Gate 轻重分类规则` section to `AGENTS.md`.
- The fix is docs-only and does not alter production code, renderer, FQ0-FQ6, extractor, Service/CLI, Host/Agent/dayu, source strategy, baseline/golden eligibility, or GitHub state.

Preflight artifact:

- `docs/reviews/release-maintenance-bond-positive-risk-truth-preflight-20260527.md`

## Accepted Plan Summary

The accepted plan is a plan/review-first evidence gate for `006597` / 2024 and only the residual `bond_risk_evidence_missing.baseline_blocking=true`.

The evidence run is authorized to:

- Run public CLI evidence commands listed in the plan after this judgment.
- Inspect generated public artifacts under `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/`.
- If public CLI output cannot determine whether annual-report evidence exists, run the bounded read-only `FundDocumentRepository.load_annual_report("006597", 2024)` inspection script from the patched plan.
- Classify the final state as one of:
  - `positive-risk evidence sufficient`
  - `evidence insufficient`
  - `evidence unavailable/disclosure gap`
  - `extractor/evidence anchor issue requiring future gate`

The evidence run is not authorized to change code/tests, renderer, FQ0-FQ6, extractor, Service/CLI, source strategy, Host/Agent/dayu, baseline/golden fixtures, or GitHub state.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentMiMo | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-review-mimo-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentMiMo targeted re-review | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-rereview-mimo-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS F1: plan used `summary.json` but CLI writes `summary.md` | **accepted and fixed** | The plan now references `summary.md`. |
| DS F2: Step B keywords omitted drawdown/stress terms | **accepted and fixed** | The keyword list now includes `回撤`, `最大回撤`, `波动率`, `压力测试`, and `波动`. |
| MiMo F1: `report.sections` iteration used dict keys | **accepted and fixed** | The script now uses `for section_id, section in report.sections.items()`. |
| MiMo F2: `ReportSection.text` does not exist | **accepted and fixed** | The script now extracts text from `report.raw_text[section.start_offset:section.end_offset]`. |
| MiMo F3: `ReportSection.tables` does not exist | **accepted and fixed** | The script now iterates `report.tables` at report level. |
| MiMo F4: `ParsedTable` has no `table_id` / `caption` | **accepted and fixed** | The script now uses `page_number`, `table_index`, `headers`, and `rows`. |

No blocking or material finding remains. MiMo targeted re-review passed and no further re-review is required.

## Authorized Evidence Run

Next role-scoped worker task:

- Write `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md`.
- Run only the accepted public CLI commands and bounded repository inspection if needed.
- Keep generated `reports/` outputs scratch/untracked unless already ignored.
- Do not modify production code/tests or control docs.
- Do not delete or stage the stray file named `--help`.
- Do not enter golden corpus or any other cursor.

## Validation To Date

- `git diff --check` passed after the plan patch.
- Ruff and pytest are not required at plan acceptance because the changes are docs-only and no source/test/runtime code changed.
