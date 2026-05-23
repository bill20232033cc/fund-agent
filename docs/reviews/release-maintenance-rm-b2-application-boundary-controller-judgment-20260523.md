# Release Maintenance RM-B2 Application Boundary Controller Judgment - 2026-05-23

## Scope

Selected candidate: `RM-B2 UI/Application boundary closure`.

This slice closes the deterministic CLI boundary debt by adding a thin Application layer between UI and Service while
preserving current Service and Fund Capability behavior.

## Controller Decision

Accepted locally.

基于 `AGENTS.md` 的六层边界，最小正确修正是新增薄 Application facade，让 UI 不再直接导入或实例化 Service。
Application 只转发 typed request，不实现基金类型、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点、审计或年报来源规则。

## Worker Handling

Two delegated worker attempts did not produce an acceptable shared-workspace result:

- First worker reported Application files but the files were absent from the shared workspace; a conflicting local
  `AGENTS.md` diff was also observed. Rejection recorded in
  `docs/reviews/release-maintenance-rm-b2-worker-result-rejection-20260523.md`.
- Replacement worker updated existing files but again did not leave Application files in the shared workspace.

Controller then applied the smallest missing-file completion:

- Added `fund_agent/application/__init__.py`.
- Added `fund_agent/application/use_cases.py`.
- Added `tests/application/test_use_cases.py`.
- Updated UI imports/call sites to use Application facade classes.
- Added an AST boundary guard proving `fund_agent/ui/cli.py` no longer imports `fund_agent.services` or `fund_agent.fund`.

## Accepted Implementation

- `FundAnalysisUseCase` delegates `analyze()` and `checklist()` to `FundAnalysisService`.
- `ThermometerUseCase`, `ExtractionSnapshotUseCase`, `ExtractionScoreUseCase`, `GoldenPrefillUseCase`,
  `GoldenAnswerUseCase`, and `QualityGateUseCase` delegate to their corresponding Services.
- `fund-analysis checklist` remains implemented and deterministic, reusing the existing Service core and rendering a
  summary instead of the full 8-chapter report.
- README files now describe the Application layer and the implemented checklist command.
- `FundAnalysisService.checklist()` and its shared core extraction are included because Application delegates to Service
  and the CLI checklist command depends on that Service contract.

## Validation

Passed:

- `uv run pytest tests/services/test_fund_analysis_service.py tests/application/test_use_cases.py tests/ui/test_cli.py tests/config/test_paths.py -q` -> `73 passed`
- `ruff check fund_agent tests`
- `git diff --check fund_agent/services fund_agent/application fund_agent/ui tests/services/test_fund_analysis_service.py tests/application tests/ui tests/config/test_paths.py README.md fund_agent/README.md tests/README.md docs/reviews/release-maintenance-rm-b2-application-boundary-handoff-20260523.md docs/reviews/release-maintenance-rm-b2-worker-result-rejection-20260523.md docs/reviews/release-maintenance-rm-b2-application-boundary-controller-judgment-20260523.md`
- Static import check: `fund_agent/ui/cli.py` has no `fund_agent.services` or `fund_agent.fund` imports.

## Exclusions

- The local `AGENTS.md` diff conflicts with the active user-provided `AGENTS.md` instructions and is not accepted or
  staged by this slice.
- Existing unrelated deleted files, including `LICENSE`, remain unstaged and unresolved.
- No external Dayu runtime, Host, Engine, tool loop, or external Dayu API dependency is introduced.

## Residuals

- `docs/design.md` and `docs/implementation-control.md` still contain local workspace edits from another branch/actor.
  They are not finalized by this acceptance unless separately reviewed and staged.
- Full repo hygiene remains blocked by the current `LICENSE` deletion.
