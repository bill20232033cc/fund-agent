# P4 PR Scope Hygiene Reconciliation - 2026-05-20

## Verdict

**PASS for scope classification.** P4 can move from `P4 PR scope hygiene / inclusion-set reconciliation` to `ready-to-open-draft-PR` once the draft PR is prepared with the inclusion set below. No files were deleted, staged, committed, pushed, or moved by this reconciliation.

## Include in P4 Draft PR

### Tracked modified files

These 30 tracked files are in scope for the P4 draft PR.

| File group | Files |
|---|---|
| User docs / control docs | `README.md`, `docs/golden-answer-template.md`, `docs/implementation-control-p4.md`, `docs/implementation-control.md`, `fund_agent/fund/README.md`, `tests/README.md` |
| Capability code | `fund_agent/fund/analysis/consistency_check.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/extraction_snapshot.py`, `fund_agent/fund/extractors/manager_ownership.py`, `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/golden_answer.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/fund/template/renderer.py` |
| Service / UI thin entry points | `fund_agent/services/extraction_score_service.py`, `fund_agent/services/fund_analysis_service.py`, `fund_agent/ui/cli.py` |
| Tests | `tests/fund/analysis/test_consistency_check.py`, `tests/fund/documents/test_cache.py`, `tests/fund/extractors/test_manager_ownership.py`, `tests/fund/extractors/test_profile.py`, `tests/fund/template/test_renderer.py`, `tests/fund/test_extraction_score.py`, `tests/fund/test_golden_answer.py`, `tests/fund/test_golden_prefill.py`, `tests/fund/test_quality_gate.py`, `tests/services/test_extraction_score_service.py`, `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py` |
| Lockfile | `uv.lock` |

`uv.lock` is included as a separate dependency-lock item because the current `pyproject.toml` already declares `pytest-cov>=7.1` in the dev extra, and the lockfile now records `pytest-cov`, `coverage`, and `tomli`. This is not part of the P4 feature logic, but leaving the lock out would make dependency metadata inconsistent.

### P4 review artifacts

Include these untracked P4 artifacts because they are referenced by control docs or are direct P4 gate evidence:

```text
docs/reviews/correctness-golden-answer-completion-20260519.md
docs/reviews/correctness-slice-code-review-controller-judgment-20260519.md
docs/reviews/correctness-slice-code-review-glm-20260519.md
docs/reviews/correctness-slice-code-review-mimo-20260519.md
docs/reviews/correctness-slice-implementation-20260519.md
docs/reviews/p4-aggregate-deepreview-codex-20260519.md
docs/reviews/p4-aggregate-deepreview-controller-judgment-20260519.md
docs/reviews/p4-aggregate-deepreview-ds-20260519.md
docs/reviews/p4-aggregate-deepreview-mimo-20260519-2108.md
docs/reviews/p4-aggregate-rereview-controller-judgment-20260519.md
docs/reviews/p4-aggregate-rereview-glm-20260519.md
docs/reviews/p4-aggregate-rereview-mimo-20260519.md
docs/reviews/p4-design-control-code-reconciliation-20260519.md
docs/reviews/p4-final-aggregate-deepreview-controller-judgment-20260520.md
docs/reviews/p4-final-aggregate-deepreview-glm-20260520.md
docs/reviews/p4-final-aggregate-deepreview-mimo-20260520.md
docs/reviews/p4-pr-scope-hygiene-reconciliation-20260520.md
docs/reviews/p4-readiness-reconciliation-20260520.md
docs/reviews/p4-s4-control-doc-reconciliation-20260519.md
docs/reviews/style-positioning-field-reconciliation-20260519.md
```

### Golden answer artifacts

Include these three files under `reports/golden-answers/` unless the user explicitly wants golden answers kept out of git:

```text
reports/golden-answers/golden-answer-prefill.md
reports/golden-answers/golden-answer-prefill-reviewed.md
reports/golden-answers/golden-answer.json
```

Rationale:

- P4 correctness comparison needs a strict golden answer JSON for reproducible smoke and future review.
- `golden-answer-prefill-reviewed.md` is the human-reviewed source used to build the strict JSON.
- `golden-answer-prefill.md` is useful provenance for the reviewed Markdown.
- These files are not generic runtime logs; they are curated correctness fixtures for P4.

## Exclude from P4 Draft PR

Do not include these untracked files/directories in the P4 draft PR:

| Path | Reason |
|---|---|
| `reports/.DS_Store` | local filesystem artifact |
| `reports/extraction-snapshots/**` | runtime smoke outputs; reproducible and not fixture-quality |
| `report-004393.md` | ad hoc generated report output |
| `launchd/**` | local automation / operational helper, not P4 feature scope |
| `scripts/aliases.zsh` | local shell helper, not P4 feature scope |
| `scripts/multi_tail.py` | local terminal helper, not P4 feature scope |
| `scripts/remind-agentcontroller.sh` | local automation helper, not P4 feature scope |
| `scripts/setup-ai-session.sh` | local tmux setup helper, not P4 feature scope |
| `scripts/start-tmux-agents.sh` | local tmux setup helper, not P4 feature scope |
| `scripts/start-tmux-ai.sh` | local tmux setup helper, not P4 feature scope |
| `docs/reviews/code-review-20260517-0727.md` | older generic review artifact, not P4 scope |
| `docs/reviews/p2-full-retrospective-controller-judgment-20260519-0014.md` | P2 retrospective artifact, not P4 scope |
| `docs/reviews/p2-full-retrospective-deepreview-glm-20260518-2358.md` | P2 retrospective artifact, not P4 scope |
| `docs/reviews/p2-full-retrospective-deepreview-mimo-20260519-0004.md` | P2 retrospective artifact, not P4 scope |
| `docs/reviews/pr-1-review-mimo-2026-05-18.md` | older PR 1 review artifact, not P4 scope |

## Validation

Commands used for this reconciliation:

```bash
git status --short
git diff --name-only
git ls-files --others --exclude-standard
git diff --stat
rg -n "pytest-cov|coverage|golden-answer|reports/golden|golden-answers|p4-s3|code_20260519" pyproject.toml uv.lock tests fund_agent docs README.md
git diff -- pyproject.toml uv.lock
find reports -maxdepth 3 -type f | sort
```

Existing post-cleanup validation from final aggregate judgment remains current:

- `ruff check .`: passed
- `ruff format --check` on the three previously failing files: passed
- `git diff --check`: passed
- targeted P4 + cache tests: `73 passed`
- full test suite: `171 passed`

## Gate Decision

RR-17 / P4-R11 is closed for classification purposes.

Next gate: `ready-to-open-draft-PR`.

Draft PR preparation must use the include/exclude rules above. If the PR tool cannot select files precisely, prepare the PR from an explicit staging list rather than staging all changes.
