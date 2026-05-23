# PR Fix Re-Review — PR #16 (AgentGLM)

## Scope

- Mode: targeted PR fix re-review
- Gate: release-maintenance PR review fix re-review
- Pull Request: https://github.com/bill20232033cc/fund-agent/pull/16
- Head: `codex/checklist-host-engine-design`
- Base: `main`
- Finding under review: PR16-C1-accepted-low-current-source-old-runtime-engine-terms
- Fix artifact: docs/reviews/release-maintenance-pr-review-fix-20260524.md
- Original review: docs/reviews/release-maintenance-pr-review-glm-20260524.md
- Controller judgment: docs/reviews/release-maintenance-pr-review-controller-judgment-20260524.md
- Output file: docs/reviews/release-maintenance-pr-rereview-glm-20260524.md
- Included scope: workspace changes in `fund_agent/fund/_value_utils.py` and `fund_agent/fund/data/thermometer.py` relative to HEAD; full `rg` sweep of `fund_agent/` for remaining Engine/Runtime terminology
- Excluded scope: all other PR files not touched by the fix; no code execution

## Conclusion: PASS

## PR16-C1 Status: RESOLVED

The fix correctly removes obsolete Engine/Runtime architecture terminology from current-source docstrings in both files.

### Fix Detail

Two docstring-only changes in workspace (uncommitted):

1. `fund_agent/fund/_value_utils.py` line 4: `不依赖 Service、Engine、Runtime 或 UI 层` → `不依赖 Service、Host 或 UI 层`
2. `fund_agent/fund/data/thermometer.py` line 4: `它不依赖 UI、Service 或 Engine，` → `它不依赖 UI、Service 或 Host，`

Both replacements align with the current architecture truth `UI -> Service -> Host -> Agent` established in AGENTS.md. The fix is docstring-only; no runtime code, imports, data flow, or public behavior changed.

### Validation Evidence

| Check | Result | Detail |
|---|---|---|
| `rg -n "Engine\|Runtime" fund_agent/ --type py` | PASS | Sole remaining match: `fund_agent/fund/data/thermometer_source.py:127` uses `RuntimeError`, a Python exception base class, not architecture terminology |
| `uv run ruff check fund_agent/fund/_value_utils.py fund_agent/fund/data/thermometer.py` | PASS | All checks passed |
| `git diff --check` | PASS | No whitespace errors |
| No host/agent package | PASS | No `fund_agent/host/` or `fund_agent/agent/` files in PR diff |
| No dayu import | PASS | No `from dayu` / `import dayu` in Python source changes |
| No behavior/API/test/CI change | PASS | Diff is docstring-only; no executable code, imports, tests, CI, README, design, control, dependency, or lockfile touched |

## Scope Check

- Fix changed exactly two production docstrings in `fund_agent/fund/_value_utils.py` and `fund_agent/fund/data/thermometer.py`, plus the fix artifact itself.
- No behavior, API, test, README, design, control, CI, dependency, or lockfile change.
- No `fund_agent/host` or `fund_agent/agent` package creation.
- No `dayu.host`/`dayu.engine` dependency or import.
- Controller intentionally expanded the same-finding fix from `_value_utils.py` to `thermometer.py` because validation found another current-source `Engine` docstring there. This expansion is correct and within the accepted finding scope.

## New Blockers

无。

## Open Questions

无。

## Residual Risk

- Low. The change is docstring-only and does not alter imports, data flow, function signatures, or behavior.
- `RuntimeError` in `thermometer_source.py:127` remains as a Python exception base class, which is explicitly acceptable per controller judgment.
