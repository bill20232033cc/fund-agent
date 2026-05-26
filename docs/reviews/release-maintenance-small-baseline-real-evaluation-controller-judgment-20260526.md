# Small Baseline Real Evaluation Controller Judgment

> Date: 2026-05-26
> Controller: AgentController
> Scope: Gate A small baseline real/quasi-real evaluation, Gate B first concrete quality fix, Gate C dev-only reporting tool, Gate D next escalation decision.

## Gate A Evidence

Accepted artifact:

- `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md`

Direct evidence:

- Clean evaluated fund-type slots: `active_fund` (`004393`), `enhanced_index` (`004194`), `bond_fund` (`006597`).
- Scratch paths under `/tmp/fund-agent-small-baseline-real-eval-20260526/`.
- Each clean sample produced a `ReportEvidenceBundle` JSON, per-sample JSONL, validator summary, and failure category localization.
- Per-sample bundle and JSONL validation passed for all three clean candidates.
- `index_fund`, `qdii_fund`, and `fof_fund` were not promoted: `110020` and `017641` remain fallback-blocked, while FOF remains data-gap/type-taxonomy evidence.

Gate A failure categories:

- `004393` active-fund turnover/style-consistency: `chapter contract`.
- `004194` enhanced-index tracking-error readiness: `data/source extraction`.
- `006597` bond risk lens facts: `data/source extraction`.
- Combined multi-bundle JSONL `RQV_REF_MISSING=4`: `validator schema / consumer limitation`.
- `110020` and `017641`: `data/source extraction` / upstream failure-category recovery.
- `007721` and `017970`: `corpus selection / fund-type taxonomy`, plus fallback category for `017970`.

Controller judgment:

- Gate A is accepted as an offline evidence run.
- It proves real evaluator consumption over three clean slots, not `scoring_ready`, durable baseline, or product-flow readiness.
- The highest-value concrete code fix is the validator consumer limitation because it is directly reproducible from Gate A and does not require renderer, Service/CLI, FQ0-FQ6, or source pipeline changes.

## Gate B Quality Fix

Accepted artifacts:

- `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-mimo-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-glm-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-mimo-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-glm-20260526.md`

Implemented scope:

- `validate_report_quality_jsonl()` now assigns standalone `record_type="score_issue"` rows to the nearest preceding bundle record.
- A `score_issue` before any bundle fails closed with `RQV_SCORE_ISSUE_ORPHANED`.
- Cross-bundle anchor/gap references still fail closed against the owning bundle indexes.
- `fund_agent/fund/README.md` documents the multi-bundle JSONL ownership rule.

Validation evidence:

- `.venv/bin/python -m pytest tests/fund/test_report_quality_validation.py -q` -> `28 passed`.
- `.venv/bin/python -m pytest tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py -q` -> `51 passed`.
- `.venv/bin/ruff check fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py` -> `All checks passed!`.
- `git diff --check` -> passed.
- `validate_report_quality_jsonl(Path('/tmp/fund-agent-small-baseline-real-eval-20260526/bundles.jsonl'))` -> `total_records=9`, `blocking_count=0`, `failed_closed=False`.

Review judgment:

- AgentMiMo initial review: `PASS_WITH_FINDINGS`; both low findings were fixed.
- AgentGLM initial review: `PASS_WITH_FINDINGS`; front-of-bundle behavior was resolved, duplicate-index issue is accepted residual.
- AgentMiMo targeted re-review: `PASS`.
- AgentGLM targeted re-review: `PASS_WITH_FINDINGS`; only low duplicate-index residual remains.

Accepted residual:

- Duplicate bundle index construction can duplicate `RQV_DUPLICATE_ID` messages for invalid bundles that also have external score issues. This is a low-severity reporting duplication on already-invalid inputs; fixing it requires a broader index caching refactor and is not necessary for the current Gate B goal.

## Gate C Dev-Only Tool

Accepted artifact:

- `docs/reviews/release-maintenance-small-baseline-real-evaluation-dev-tool-20260526.md`

Implemented scope:

- Added `scripts/report_quality_eval.py` as a maintainer-only/dev-only wrapper over explicit JSONL and bundle JSON inputs.
- Added `tests/scripts/test_report_quality_eval.py`.
- Updated `tests/README.md` with current script usage and test constraints.

Boundary:

- The tool is not registered in `pyproject.toml` and does not alter `fund-analysis analyze` or `fund-analysis checklist`.
- It does not read annual reports, call extractors, `FundDocumentRepository`, PDF/cache/source helpers, renderer, Service, Host/Agent/dayu, `nav_data`, or FQ0-FQ6.
- It writes caller-selected scratch summary JSON only.

Validation evidence:

- `.venv/bin/python -m pytest tests/scripts/test_report_quality_eval.py -q` -> `4 passed`.
- `.venv/bin/ruff check scripts/report_quality_eval.py tests/scripts/test_report_quality_eval.py` -> `All checks passed!`.
- `.venv/bin/python scripts/report_quality_eval.py --jsonl /tmp/fund-agent-small-baseline-real-eval-20260526/bundles.jsonl --output /tmp/fund-agent-small-baseline-real-eval-20260526/dev-tool-summary.json --run-id evidence:small-baseline-real-eval:20260526` -> passed.
- Scratch summary reports `total_records=9`, `blocking_count=0`, `failed_closed=false`.
- `git diff -- fund_agent/ui fund_agent/services fund_agent/fund/quality_gate.py fund_agent/fund/extraction_score.py pyproject.toml` -> no diff.

## Gate D Escalation Decision

Selected next path:

1. `chapter contract implementation` plus `report writing/template rewrite gate`.

Reason:

- Gate A localized an active-fund Chapter 3 chapter-contract failure around unsupported turnover/style-consistency claims.
- The previous contract slice hardened the contract wording, but the renderer/report-writing path still does not emit the accepted wording marker or runtime required item.
- Gate B removed the validator consumer blocker, so next evidence should focus on whether report writing can satisfy the accepted contract without weakening FQ0-FQ6 or changing product defaults broadly.

Paths not selected now:

- `more extraction fixes`: needed for enhanced-index and bond, but active-fund chapter-contract pressure is already directly localized and smaller.
- `evidence anchor model hardening`: current anchors are sufficient for offline evidence; no anchor model blocker remains.
- `dev-only evaluator expansion`: Gate C provides a minimal tool; broader expansion should wait until the next writing gate defines outputs to compare.
- `durable baseline fixture gate`: blocked by non-`scoring_ready` samples, fallback-blocked index/QDII, FOF data-gap, and not-yet-reviewed fact coverage.
- `report writing/template rewrite gate`: selected only as scoped design gate, not broad rewrite.
- `LLM audit / repair loop design gate`: premature; deterministic contract/rendering evidence is still insufficient.

Stop condition for next gate:

- If renderer/report-writing changes require weakening FQ0-FQ6, changing default Service/CLI behavior, or promoting scratch evidence into fixtures, stop and return to plan/review.

## Escalation Readiness Check

1. Small baseline real evaluation covers at least three `fund_type_slot`: yes. Evidence: Gate A artifact table covers `active_fund`, `enhanced_index`, `bond_fund`.
2. Every evaluated sample has bundle / JSONL / validator summary / failure categories: yes. Evidence: Gate A artifact scratch outputs and validator summary tables.
3. At least one concrete quality fix completed: yes. Evidence: Gate B validator multi-bundle JSONL ownership fix.
4. Fix directly corresponds to Gate A failure category: yes. Evidence: Gate A combined JSONL `RQV_REF_MISSING=4` -> Gate B validator schema/consumer fix.
5. Focused tests / adjacent tests / ruff / diff check exist: yes. Evidence: Gate B and Gate C validation sections above.
6. At least two independent review / re-review exist: yes for Gate B. Evidence: MiMo and GLM review/re-review artifacts listed above.
7. `docs/implementation-control.md` update: required before final accepted checkpoint. Evidence will be the final control doc diff and accepted local commit.
8. Current workspace clean: required after accepted commit. Pre-existing untracked `docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md` needs disposition before final readiness is claimed.
9. Uncommitted scratch/report output: scratch remains under `/tmp/fund-agent-small-baseline-real-eval-20260526/` only and is not intended for commit.
10. Next path recommendation: `chapter contract implementation + report writing quality upgrade design gate`, for the reasons in Gate D.

## Controller Decision

Final aggregate review artifacts:

- `docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-mimo-20260526.md` -> `PASS`.
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-glm-20260526.md` -> `PASS_WITH_FINDINGS`; only the accepted duplicate-index residual remains.

Gate A/B/C/D are accepted subject to final local accepted commit and post-commit clean-worktree readiness check. Do not enter the next gate until that readiness check passes.
