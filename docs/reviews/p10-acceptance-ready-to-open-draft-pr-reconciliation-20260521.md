# P10 Acceptance / Ready-To-Open-Draft-PR Reconciliation

- **Date**: 2026-05-21
- **Gate**: `ready-to-open-draft-PR reconciliation`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Aggregate judgment**: `docs/reviews/p10-aggregate-deepreview-controller-judgment-20260521.md`

## Verdict

**ACCEPTED.** P10 is ready to open a draft PR after creating an accepted local commit.

P10-S1 closed the release-readiness scope accepted after P9: LICENSE, CI, artifact policy, static default paths, path migration guards, documentation sync, and durable review artifacts. Aggregate deepreview found no blocking issues.

## Inclusion Set

Include these files in the P10 accepted local commit:

- `.github/workflows/ci.yml`
- `.gitignore`
- `LICENSE`
- `README.md`
- `pyproject.toml`
- `docs/implementation-control.md`
- `docs/reviews/code-review-p8-s3-ds-20260521.md`
- `docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`
- `docs/reviews/p10-s1-plan-review-controller-judgment-20260521.md`
- `docs/reviews/p10-s1-plan-review-ds-20260521.md`
- `docs/reviews/p10-s1-plan-review-mimo-20260521.md`
- `docs/reviews/p10-s1-implementation-20260521.md`
- `docs/reviews/p10-s1-code-review-controller-judgment-20260521.md`
- `docs/reviews/p10-s1-code-review-mimo-20260521.md`
- `docs/reviews/p10-s1-code-review-glm-20260521.md`
- `docs/reviews/p10-aggregate-readiness-reconciliation-20260521.md`
- `docs/reviews/p10-aggregate-deepreview-controller-judgment-20260521.md`
- `docs/reviews/p10-aggregate-deepreview-mimo-20260521.md`
- `docs/reviews/p10-aggregate-deepreview-glm-20260521.md`
- `docs/reviews/p10-acceptance-ready-to-open-draft-pr-reconciliation-20260521.md`
- `fund_agent/README.md`
- `fund_agent/config/README.md`
- `fund_agent/config/paths.py`
- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/thermometer.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/golden_answer.py`
- `fund_agent/fund/golden_prefill.py`
- `fund_agent/fund/pdf/downloader.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/README.md`
- `tests/config/test_paths.py`
- `tests/test_repo_hygiene.py`
- `tests/ui/test_cli.py`

## Exclusion Set

Do not include these local or out-of-scope files in the P10 commit / draft PR:

- `docs/repo-audit-20260521.md`
  - Reason: useful follow-up input, but based on older repo state and already dispositioned in `p10-aggregate-readiness-reconciliation`; not required for release readiness.
- `docs/fund-agent_仓库级综合审核报告_2026-05-21.docx`
  - Reason: binary source audit input; ignored by `.gitignore`.
- `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`, `dist/`, `build/`, `*.egg-info/`
  - Reason: local generated artifacts.
- `cache/`, `reports/extraction-snapshots/`, `reports/quality-gate-runs/`, `report-*.md`
  - Reason: runtime outputs.
- `fund_agent/fund/tools/`
  - Reason: empty directory; track as post-P10 follow-up because Git will not include empty directories and no runtime behavior depends on it.

## Residual Risks

| Risk | Owner / Destination | Status |
|------|---------------------|--------|
| Empty `fund_agent/fund/tools/` directory conflicts with `docs/design.md` wording | Post-P10 follow-up | Not blocking; directory is empty and untracked by Git if no files are present. |
| `docs/repo-audit-20260521.md` contains useful but older audit suggestions | Post-P10 follow-up planning | Not included in PR; suggestions dispositioned in readiness artifact. |
| `docs/reviews/` directory size | Later control-doc hygiene slice | Deferred; durable artifacts retained for phaseflow recovery. |
| RR-13 duplicate `016492` selected-fund CSV | Human / App source confirmation | Unchanged. |

## Validation

Accepted validation evidence:

- `uv run pytest -q` -> `388 passed`
- `uv run ruff check .` -> passed
- `git diff --check` -> passed
- `uv lock --check` -> passed
- `.docx` ignored by `.gitignore`

## Next Gate

`ready-to-open-draft-PR`.

Controller may create the accepted local commit for the inclusion set. Opening the draft PR requires user authorization for the draft PR gate.
