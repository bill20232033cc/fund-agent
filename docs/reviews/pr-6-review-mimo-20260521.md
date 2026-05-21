# PR #6 Code Review — P10 Repo Hygiene / Release Readiness

- **Date**: 2026-05-21
- **Reviewer**: AgentMiMo (PR-level review + targeted re-review)
- **PR**: https://github.com/bill20232033cc/fund-agent/pull/6
- **Base**: main
- **Head**: `eb43dc3` (p10-release-readiness, includes `fix: stabilize dev override CLI errors`)
- **Scope**: P10 repo hygiene / release readiness: MIT LICENSE, GitHub Actions CI, .gitignore artifact policy, config.paths default path migration, README/tests/review artifacts
- **Constraint**: Must not change fund-analysis analyze behavior, quality gate semantics, renderer output, audit rules, or Fund Capability analysis behavior
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`

## Verdict

**PASS** — no blocking findings.

P10 release-readiness changes are correctly implemented: LICENSE, CI, .gitignore, config.paths, path migration guards, and documentation sync all pass review. The diff does not change fund-analysis analyze product behavior, quality gate semantics, renderer output, audit rules, or Fund Capability analysis rules. CI test failure from initial review has been fixed in `eb43dc3` and CI now passes.

## CI Status

**SUCCESS** — CI run `26234941272` passes (`ubuntu-latest`, Python 3.11): `388 passed`, ruff clean.

Initial CI run `26234664649` had 2 test failures due to Typer `BadParameter` rendering difference on ubuntu-latest. Fixed in commit `eb43dc3` by wrapping `_build_developer_overrides` in try/except that echoes the error message and raises `typer.Exit(code=2)`.

## Findings (ordered by severity)

### FINDING-1: CI test failure — CLOSED

- **Severity**: CLOSED (fixed by `eb43dc3`)
- **File**: `fund_agent/ui/cli.py:172-186`
- **Evidence**: Initial CI run `26234664649` showed `2 failed, 386 passed`. Fix wraps `_build_developer_overrides` in try/except: catches `typer.BadParameter`, echoes message via `typer.echo(str(exc), err=True)`, raises `typer.Exit(code=2)`. CI run `26234941272` passes: `388 passed`.
- **Assessment**: Fix is correct and minimal. The explicit `typer.echo` + `typer.Exit` ensures the custom error message is always in output regardless of Typer version behavior on different platforms.
- **Action**: Closed. No further action needed.

### FINDING-2: PR scope broader than P10 repo hygiene — LOW

- **Severity**: LOW (informational, not blocking)
- **Evidence**: PR includes P9 functional changes that were already accepted in local phaseflow:
  - `FundAnalysisDeveloperOverrides` nested dataclass (P9-S1)
  - `FinalJudgmentDecision` / `derive_final_judgment` (P9-S1)
  - Quality gate `FQ0/info` calibration with `coverage_scope` (P9-S2)
  - `AnalyzeMode` product/developer_override separation (P9-S1)
  - CLI `--dev-override` flag (P9-S1)
- **Assessment**: These changes were reviewed and accepted in P9-S1/P9-S2 local slices. They are correct and well-tested. The PR title "P10 repo hygiene and release readiness" understates the scope. This is acceptable because the branch was created after P9 acceptance, but should be noted in the merge commit message.
- **Action**: Include P9 functional changes in merge commit description.

### FINDING-3: config.paths module is pure static — PASS

- **Severity**: PASS
- **File**: `fund_agent/config/paths.py` (27 lines)
- **Evidence**: 12 `Final[Path]` constants, imports only `pathlib.Path` and `typing.Final`. No `os.environ`, no workspace config, no prompt manifest, no Dayu/Host/Engine runtime. `config/__init__.py` remains empty (no re-exports).
- **Assessment**: Correctly designed as a static default path module. Test guards cover all 16 consumer aliases, import isolation, and AST scan for scattered defaults.

### FINDING-4: Path migration preserves all aliases — PASS

- **Severity**: PASS
- **Files**: `ui/cli.py`, `services/fund_analysis_service.py`, `fund/extraction_snapshot.py`, `fund/golden_answer.py`, `fund/golden_prefill.py`, `fund/quality_gate_integration.py`, `fund/documents/cache.py`, `fund/pdf/downloader.py`, `fund/data/nav_data.py`, `fund/data/thermometer.py`
- **Evidence**: All 16 old module-level constants are preserved as aliases pointing to `config.paths` equivalents. `test_existing_path_aliases_point_to_config_defaults` verifies all 16.
- **Assessment**: No path value changed during migration. `DEFAULT_QUALITY_GATE_SCORE` correctly stays CLI-local (historical P4 fixture path).

### FINDING-5: golden-build default input corrected — PASS

- **Severity**: PASS (intended fix)
- **File**: `fund_agent/ui/cli.py:460`, `fund_agent/fund/golden_answer.py:17-19`
- **Evidence**: Default input changed from `golden-answer-prefill.md` to `golden-answer-prefill-reviewed.md`. This corrects a P4-era naming mismatch. `golden-build` contract says it consumes human-reviewed Markdown. Test `test_golden_build_cli_defaults_to_reviewed_markdown` covers this.
- **Assessment**: Does not affect `analyze` product behavior. `golden-build` is an independent subcommand.

### FINDING-6: dayu-agent dependency removed — PASS

- **Severity**: PASS
- **File**: `pyproject.toml`
- **Evidence**: `dayu-agent @ https://github.com/...` removed from dependencies. `license = "MIT"` added. `uv.lock` updated accordingly.
- **Assessment**: Correct per P10 plan and 2026-05-21 architecture decision. AGENTS.md and design.md already state Dayu is methodology reference only.

### FINDING-7: LICENSE and CI — PASS

- **Severity**: PASS
- **Files**: `LICENSE`, `.github/workflows/ci.yml`, `pyproject.toml`
- **Evidence**: MIT License with holder `bill20232033cc`. CI runs Python 3.11 with `uv sync --extra dev --frozen`, `uv run ruff check .`, `uv run pytest -q`. Triggers on push to main and pull_request.
- **Assessment**: Correct and matches plan slice P10-S1-A. `enable-cache: true` for uv is appropriate.

### FINDING-8: .gitignore narrow policy — PASS

- **Severity**: PASS
- **File**: `.gitignore`
- **Evidence**: Added `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`, `dist/`, `build/`, `*.egg-info/`, `docs/*.docx`. Explicit comment: `# reports/golden-answers/ contains curated fixtures and is intentionally tracked.`
- **Assessment**: Narrow, does not hide curated fixtures. `test_gitignore_keeps_generated_outputs_local_without_hiding_fixtures` verifies.

### FINDING-9: README updates describe current behavior — PASS

- **Severity**: PASS
- **Files**: `README.md`, `fund_agent/README.md`, `fund_agent/config/README.md`, `fund_agent/fund/README.md`, `tests/README.md`
- **Evidence**: README simplified to product mode (no dev override params in quick-start). CI commands added. Artifact policy section added. All docs describe "current how-to" not "future plan".
- **Assessment**: Consistent with AGENTS.md documentation constraints. `golden-build` default corrected in README examples.

### FINDING-10: P9 product contract changes — PASS (previously reviewed)

- **Severity**: PASS
- **Files**: `fund_agent/services/fund_analysis_service.py`, `fund_agent/fund/analysis/final_judgment.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/template/renderer.py`, `fund_agent/fund/audit/audit_programmatic.py`, `fund_agent/fund/audit/contract_rules.py`
- **Evidence**: P9-S1 (product contract, developer override, final judgment) and P9-S2 (quality gate calibration) were independently reviewed and accepted in local phaseflow. All changes stay within UI → Service → Fund Capability boundary. Full suite 388 passed locally.
- **Assessment**: These are correct P9 functional changes bundled into the P10 branch. They do not change existing analysis behavior — they add the product/developer_override mode separation and final judgment derivation.

### FINDING-11: docs/ changes — PASS

- **Severity**: PASS
- **Files**: `docs/design.md`, `docs/implementation-control.md`, `docs/fund-analysis-template-draft.md`, `docs/reviews/code-review-p8-s3-ds-20260521.md`, 30+ review artifacts
- **Evidence**: design.md updated to reflect P9 product contract decisions and Dayu methodology-only stance. implementation-control.md updated with P9/P10 gate history. Template chapter 5/6 boundaries clarified. Review artifacts are durable phaseflow evidence.
- **Assessment**: All doc updates describe current state, not future plans. Control-doc updates are controller bookkeeping as required by phaseflow.

## Verification Summary

| Check | Result | Notes |
|-------|--------|-------|
| fund_analysis analyze behavior unchanged | ✅ PASS | Product mode defaults match pre-P9 behavior; dev override is opt-in |
| Quality gate semantics unchanged | ✅ PASS | FQ0/info calibration is additive, not behavioral change |
| Renderer output unchanged | ✅ PASS | `fund_agent/fund/template/renderer.py` changes only add `FinalJudgmentDecision` contract |
| Audit rules unchanged | ✅ PASS | `fund_agent/fund/audit/` changes add R2 conflict audit, do not change existing rules |
| Fund Capability analysis rules unchanged | ✅ PASS | No changes to `fund/analysis/`, `fund/fund_type.py` |
| config.paths is static | ✅ PASS | No env/runtime/config loading |
| Path aliases preserved | ✅ PASS | 16 aliases verified by test |
| LICENSE correct | ✅ PASS | MIT, holder `bill20232033cc` |
| CI workflow correct | ✅ PASS | Python 3.11, uv, ruff, pytest |
| .gitignore narrow | ✅ PASS | Curated fixtures not hidden |
| CI tests pass | ✅ PASS | Fixed in `eb43dc3`; CI run `26234941272` = `388 passed` |

## Residual Risks

| Risk | Severity | Owner |
|------|----------|-------|
| PR scope broader than title suggests (P9 functional changes included) | LOW | Document in merge commit message |
| Empty `fund_agent/fund/tools/` directory contradicts design.md | LOW | Post-P10 follow-up |
| `docs/reviews/` volume (300+ artifacts) | LOW | Later control-doc hygiene slice |
| RR-13 duplicate `016492` in selected-fund CSV | LOW | Human/App source confirmation |

## Recommendation

All findings closed. CI passes. PR is ready for merge. Include P9 functional changes in merge commit description since the scope extends beyond the P10 repo hygiene title.
