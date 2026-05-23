# Release Maintenance RM-B2 Application Boundary Handoff - 2026-05-23

## Controller Context

- Branch: `codex/checklist-host-engine-design`
- Current gate: `release maintenance boundary-debt selection`
- Selected candidate: `RM-B2 UI/Application boundary closure`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`

## Current Workspace Facts

The current workspace already contains uncommitted source/test/doc changes from another actor:

- `fund_agent/services/fund_analysis_service.py` adds a shared analysis core and a `FundAnalysisService.checklist()` use case.
- `fund_agent/ui/cli.py` changes `fund-analysis checklist` from a placeholder into a real command.
- `tests/services/test_fund_analysis_service.py` and `tests/ui/test_cli.py` add checklist coverage.
- `docs/design.md` and `docs/implementation-control.md` contain additional Dayu/manual mapping and checklist status edits.

Focused verification before this handoff:

- `uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q` -> `62 passed`
- `ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py` -> passed
- `git diff --check fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py docs/design.md docs/implementation-control.md` -> passed

## Problem

The current implementation proves the checklist use case is viable, but it does not close the boundary debt:

- `fund_agent/ui/cli.py` still imports and instantiates Service classes directly.
- The new checklist command expands that UI -> Service pattern instead of routing through Application.
- The docs currently contain wording that future Agent paths "must use `dayu.host` / `dayu.engine`". This conflicts with `AGENTS.md`: Dayu is only method/reference material, and future runtime/engine capabilities must be internalized inside this project boundary unless a later explicit design gate changes the dependency policy.

## Worker Task

Implement the RM-B2 thin Application use-case facade, preserving current deterministic behavior.

Owned implementation scope:

- Add a minimal `fund_agent/application/` package.
- Move UI-facing orchestration entry points into Application facade(s), without adding business logic.
- Update `fund_agent/ui/cli.py` so it imports Application-level API only, not `fund_agent.services`.
- Keep `FundAnalysisService.checklist()` and the shared Service core if they remain the cleanest Service-level implementation.
- Update tests to cover:
  - `fund-analysis checklist` still calls the use case and prints summary output.
  - UI no longer imports `fund_agent.services`.
  - Application delegates to Service without changing request fields, including explicit `valuation_state`, `force_refresh`, and thermometer cache options.
- Update README/docs required by `AGENTS.md` for a new package/layer and changed CLI checklist behavior.

Required docs corrections:

- `docs/design.md` must not say future work "must use `dayu.host` / `dayu.engine`".
- Correct wording: Dayu Host/Engine manuals can inform future Runtime/Engine design, but any such capability must be internalized in this project and pass an explicit gate before becoming a runtime dependency.
- Preserve the explicit-parameter/no-`extra_payload` rule.
- `docs/implementation-control.md` is controller-owned; do not finalize gate status there beyond avoiding contradictions if the current diff already touched it.

Out of scope:

- No external Dayu runtime dependency.
- No Host/Engine/tool loop implementation.
- No Fund Capability behavior changes.
- No annual-report source, repository, PDF cache, or document access changes.
- No unrelated deletion restoration or cleanup.

## Validation Required

Run and report:

- `uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`
- Any new Application-layer tests.
- Any changed README/docs related tests if applicable.
- `ruff check fund_agent tests`
- `git diff --check`

## Controller Acceptance Criteria

The controller can accept this slice only if:

- UI imports from Application, not Service or Capability.
- Application is a thin use-case facade and does not absorb Fund domain rules.
- Checklist behavior remains deterministic and explicit-parameter based.
- Dayu wording is brought back under `AGENTS.md` constraints.
- Existing unrelated deletions remain unstaged and untouched.
