# Release Maintenance Aggregate Deep Review - 2026-05-24

## Gate

- Current phase: `release maintenance`.
- Current gate: `release-maintenance aggregate deepreview`.
- Branch: `codex/checklist-host-engine-design`.
- Base/range: `origin/main..HEAD`.
- Worker role: review worker only; not controller.
- External actions: none.
- Commit / push / PR / merge: not performed.

## Review Scope

Aggregate correctness/stability/architecture review of all 25 branch commits relative to `origin/main`. Reviewed: AGENTS.md, docs/design.md, docs/implementation-control.md, all `.py` files, `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, all README files, and key review artifacts under `docs/reviews/`.

## Truth Sources Consulted

- `AGENTS.md` (Agent execution rules, single authoritative entry)
- `docs/design.md` v2.2 (design truth)
- `docs/implementation-control.md` (Startup Packet, current gate, control state)
- Current branch diff (`origin/main..HEAD`)

## Conclusion

**PASS_WITH_FINDINGS**

25 commits reviewed. No blocking findings. 2 low/cosmetic findings. All residual risks are pre-existing and owned by future cleanup / production hardening.

## Verification

| Check | Result |
|-------|--------|
| `uv run pytest -q` | 619 passed, 1.43s |
| `uv run ruff check .` | All checks passed |
| Coverage gate (CI) | `--cov=fund_agent --cov-fail-under=50` (gate at 50%) |
| `LICENSE` file | Present (MIT, 1071 bytes) |
| `LICENSE.md` file | Present (MIT, 1071 bytes) |
| `uv.lock` synced | Yes (setuptools backend, pandas declared, black/mypy/pyright/pytest-mock/pytest-timeout/requests-mock added to dev/test extras) |

## Findings

### F1 [LOW/COSMETIC] Section-count typo in implementation-control.md Startup Packet

**Location**: `docs/implementation-control.md` Resume checklist paragraph.

**Evidence**: "validation passed with `uv run pytest -q` 614 passed, coverage gate 91.94%" — this records prior gate validation numbers, not a current blocker. The Host/Agent boundary decision artifact (`docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md`) records "6 chapters (0-7)" when the template has 8 chapters (0-7). This was already flagged in MiMo/GLM code review and the fix commit (`release-maintenance-host-agent-boundary-decision-code-review-fix-20260524.md` records `HABC-C1 已修复`).

**Status**: Already fixed in prior review cycle. No action needed.

### F2 [LOW/COSMETIC] Missing type annotation on `_echo_checklist_result`

**Location**: `fund_agent/ui/cli.py:1043`.

**Evidence**: `def _echo_checklist_result(result) -> None:  # type: ignore[no-untyped-def]` — the `result` parameter lacks a `FundChecklistResult` type annotation. The `# type: ignore` comment suppresses the mypy warning.

**Impact**: Cosmetic only. The function is CLI-internal and correctly typed at runtime. Does not affect correctness or stability.

## Architecture Boundary Check (Dayu Four-Layer)

| Check | Status | Evidence |
|-------|--------|----------|
| UI -> Service -> Host -> Agent boundary defined | PASS | `AGENTS.md` lines 66-94, `docs/design.md` §2.1 |
| No placeholder `fund_agent/host` or `fund_agent/agent` | PASS | `ls fund_agent/host/ fund_agent/agent/` returns "No such file or directory" |
| Future Host uses `dayu.host` | PASS | `AGENTS.md` line 56, `design.md` §2.1 Host row |
| Future Agent execution uses `dayu.engine` | PASS | `AGENTS.md` line 56, `design.md` §2.1 Agent row |
| No explicit params in `extra_payload` | PASS | `FundAnalysisRequest` has all typed fields; no `extra_payload` dict |
| FundDocumentRepository annual-report boundary | PASS | `cache.py` atomic writes inside documents layer; Service/UI do not access PDF/cache directly |
| All "Capability" terminology replaced | PASS | `AGENTS.md`, `design.md`, all READMEs, all code docstrings updated to "Agent 层基金能力" |
| Dayu Host/Agent not declared as dependencies | PASS | `pyproject.toml` `dependencies` does not include `dayu.host` or `dayu.engine` |

## Engineering Baseline Check (pyproject.toml)

| Check | Status | Evidence |
|-------|--------|----------|
| Build backend | PASS | `setuptools>=68` (changed from `hatchling`) |
| PEP 621 metadata | PASS | `authors`, `keywords`, `classifiers`, `project.urls` present |
| `requires-python >=3.11` | PASS | `pyproject.toml` line 7 |
| `pandas>=2.1.4,<4.0.0` declared | PASS | `pyproject.toml` dependencies list |
| `test` / `dev` extras separated | PASS | `test` has pytest stack; `dev` adds ruff/black/mypy/pyright |
| pytest/ruff/black config | PASS | `[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.black]` sections |
| Package find excludes tests/docs | PASS | `[tool.setuptools.packages.find]` excludes `tests*`, `docs*`, `reports*`, `scripts*`, `workspace*`, `cache*` |
| License consistency | PASS | `license = "MIT"` in pyproject.toml; `LICENSE` file present at repo root |

## Code Change Summary

### Core Changes

| Area | Change | Commits |
|------|--------|---------|
| Service refactor | Extract `_run_analysis_core()` shared by `analyze` and `checklist`; add `FundChecklistResult`, `_AnalysisCoreResult`, `_ValidatedRequest` | 6fa072d, ccde2f7, 3303d4c |
| Checklist CLI | `fund-analysis checklist` fully wired to Service; outputs 7-question checklist, valuation, final judgment | ccde2f7 |
| Chapter 0 renderer | Risk/upgrade/downgrade slots now use structured data (veto/watch/stress items) instead of "数据不足" | e20367f |
| Cache hardening | Parsed report JSON uses atomic write (`NamedTemporaryFile` + `Path.replace`) with cleanup on failure | 720821a |
| Thermometer boundary | `ThermometerService` imports from `fund_agent/fund/data/__init__.py` public entry, not internal modules | a49ee9c |
| Fund code normalization | `normalize_fund_code` applied before service execution | 23b3a03 |
| Four-layer docs | All READMEs, AGENTS.md, design.md updated from "Capability/Runtime/Engine" to "Agent 层基金能力" with Dayu four-layer boundary | 11f01b5, ae3a82a, 785466e |
| Engineering baseline | pyproject.toml restructured to setuptools, PEP 621, split extras, added tools | 5443b09, 8ca620e |
| CI coverage gate | `--cov=fund_agent --cov-fail-under=50` added to CI | dceb5cc |
| Doc cleanup | Removed ~30 stale docs (old audits, plans, research notes); kept review artifacts | multiple |

### Deleted Files (Doc Cleanup)

Removed ~30 stale documents including `docs/20260430/` folder, old audit/plan/research docs, and superseded control files. All active review artifacts under `docs/reviews/` preserved.

## Residual Risks (Pre-existing, Non-Blocking)

These are carried forward from prior gate states and are not introduced by branch changes:

- RR-13 duplicate `016492` (excluded `docs/repo-audit-20260521.md`)
- Production `tracking_error` golden rows remain blocked for `001548` and P16-S1 enhanced-index candidates
- P19-S4 exact-index PE+PB sources unresolved for `399006`/`000688`/`000922`/`000932`/`000933`
- Release-maintenance repo-deepreview backlog: quality-gate watch/FQ3 semantics, developer override blocker severity, thermometer batch parallelism, Chinese amount unit parsing, style/equity bucket ambiguity, external I/O timeout/concurrency/table-parse hardening, fund-type ordering decision, Alpha attribution feature
- Host/Agent packages not yet implemented (correct per guardrails; future gate required)
- P15-S1A evidence acquisition accepted with `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`

## Summary

| Metric | Value |
|--------|-------|
| Commits reviewed | 25 |
| Files changed | 103 (+7536, -8400) |
| Tests passing | 619 |
| Blocking findings | 0 |
| Low/cosmetic findings | 2 |
| New residual risks | 0 |
| Conclusion | **PASS_WITH_FINDINGS** |
