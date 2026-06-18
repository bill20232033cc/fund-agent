# MVP dayu.host runtime governance adapter implementation preflight

Date: 2026-06-01
Gate: `MVP dayu.host runtime governance adapter implementation gate`
Gate type: heavy implementation preflight
Role: Gateflow controller
Status: blocked before runtime edits

## Preflight Result

Implementation is blocked at Slice H0 before any runtime/code/test edits.

The accepted plan requires the implementation to verify `dayu.host` API and dependency declaration before writing runtime. Local import succeeds, but dependency ownership is not declared in project truth:

- `uv run python -c "import importlib.util; print(importlib.util.find_spec('dayu.host'))"` succeeds.
- `pyproject.toml` does not declare `dayu` or `dayu-agent`.
- `uv.lock` does not contain `dayu` or `dayu-agent`.
- `uv pip show dayu` fails with `Package(s) not found for: dayu`.
- `uv pip show dayu-agent` reports an installed package `dayu-agent==0.1.4`, which appears to provide the importable `dayu` package in the current venv.

This means the current environment can import `dayu.host`, but a fresh project environment created from `pyproject.toml` / `uv.lock` would not reliably provide it.

## Commands

```text
git branch --show-current
codex/local-reconciliation

git status --short --untracked-files=all
only pre-existing historical untracked residuals

uv run python -c "import dayu, importlib.util; print(dayu.__file__); print(importlib.util.find_spec('dayu.host'))"
dayu.host importable from .venv/site-packages

rg -n "name = \"dayu\"|dayu" uv.lock pyproject.toml
no matches

uv pip show dayu
Package(s) not found for: dayu

uv pip show dayu-agent
Name: dayu-agent
Version: 0.1.4
```

## Controller Judgment

Stop before implementation.

Adding runtime code that imports `dayu.host` without a declared dependency would make the implementation depend on an undeclared local environment artifact. That violates the accepted plan's Slice H0 stop condition:

> Confirm current dependency declaration/lock already provides `dayu.host`; if not, stop for a dependency-declaration decision before editing runtime.

## Required User / Gate Decision

Choose the dependency-source path before implementation:

1. Add declared dependency on `dayu-agent==0.1.4` or the intended package name/version if different.
2. Vendor or local-path dependency if `dayu.host` is not meant to come from a published package.
3. Defer implementation and run a dedicated `dayu.host dependency declaration gate`.

No runtime implementation should start until this is resolved.

## Scope Preserved

- No runtime/code/tests modified.
- No dependency files modified.
- No `fund_agent/host` created.
- No `dayu.engine` touched.
- No score, quality gate, golden, fixture, release-readiness or PR state changed.
- No push, PR, merge, mark-ready or release action occurred.
- Historical untracked residuals remain out of scope.
