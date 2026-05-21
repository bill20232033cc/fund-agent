# Code Structure / Design Reconciliation - 2026-05-21

## Reviewed Inputs

- `docs/design.md`
- `docs/implementation-control.md`
- `README.md`
- `fund_agent/**`
- `pyproject.toml`

## Controller Judgment

Current code remains a deterministic UI / Service / Fund Capability application. Code structure does not justify treating Dayu Host/Engine, prompt scene registry, tool loop, or generic agent runtime as implemented design facts.

## Accepted As Design Facts

| Code fact | Judgment | Design action |
|---|---|---|
| `fund_agent/ui/cli.py` is the only user-facing runtime entry | accepted | Keep UI layer as CLI-only MVP |
| `fund_agent/services/*` owns use-case orchestration | accepted | Keep Service as orchestration layer, not domain-rule owner |
| `fund_agent/fund/*` owns documents, extraction, analysis, template, audit, data adapters and quality gate | accepted | Keep Fund as Capability layer |
| `FundDocumentRepository.load_annual_report(...)` is production document access boundary | accepted | Keep as only production annual-report read entry |
| `fund_agent/config` package exists but contains no runtime behavior | accepted as placeholder only | Document as no-op config namespace |
| `fund_agent/config/prompts/*` exists only as untracked empty local directories | not a design fact | Do not treat as prompt runtime |

## Rejected Or Removed

| Code fact | Judgment | Action |
|---|---|---|
| `fund_agent/fund/tools/__init__.py` empty package | rejected | Remove empty package; no current tool runtime exists |
| Empty prompt folders under `fund_agent/config/prompts` | rejected as current architecture | Leave untracked/local; do not document as implemented |
| Dayu dependency in `pyproject.toml` | rejected after user architecture decision | Remove dependency; keep Dayu only as methodology reference |

## Deferred Design Questions

| Topic | Reason |
|---|---|
| Whether to remove `dayu-agent` dependency | Resolved: remove it; future runtime capabilities must be internalized |
| Whether to introduce runtime prompt manifests | Requires Application/Runtime design slice; current MVP does not need it |
| Whether to add a generic tool layer | Requires Engine/Runtime design slice; current Fund tools should remain plain Capability functions |

## Applied Update Scope

- Added `fund_agent/README.md` as development overview for current package boundaries.
- Added `fund_agent/config/README.md` to state that config is a placeholder and not a runtime prompt system.
- Removed empty `fund_agent/fund/tools` package.
- Updated `docs/design.md` to explicitly classify config as placeholder and reject tool-loop / scene-runtime inference from directory shape.

## Residual Risk

`dayu-agent` should not remain a production dependency. Current production code does not import `dayu`; future Host/Engine/tool-loop capabilities should be implemented inside `fund_agent` behind project-owned contracts.
