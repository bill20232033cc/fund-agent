# Code Review Re-review

## Scope

- Mode: targeted re-review
- Original review: `docs/reviews/code-review-20260622-161934.md`
- Branch: `evidence-confirm-productionization`
- Output file: `docs/reviews/code-review-rereview-20260622-162217.md`
- Included scope:
  - accepted finding 1 from original review
  - `fund_agent/fund/evidence_confirm_sources.py`
  - `scripts/evidence_confirm_ec_p2_live_sample.py`
  - `tests/fund/test_evidence_confirm_sources.py`
- Excluded scope:
  - new full-scope code review beyond accepted finding

## Findings

未发现实质性问题。

## Accepted Finding Closure

### CR-1 live sample 绕过 runner 的 repository failure classification 和 safe JSON 输出

- Verdict: fixed
- Direct evidence:
  - `EvidenceConfirmRepositoryRunRequest` now accepts `projection_factory`, allowing post-load smoke projection inside the runner boundary: `fund_agent/fund/evidence_confirm_sources.py:119-130`.
  - `run_repository_bounded_evidence_confirm()` now validates projection/projection_factory before loading, catches default repository initialization failures, calls repository `load_annual_report` inside the runner, classifies repository failures, and catches projection factory failures: `fund_agent/fund/evidence_confirm_sources.py:279-339`.
  - `run_authorized_sample()` no longer instantiates `FundDocumentRepository` or calls `load_annual_report` directly; it passes `projection_factory=build_live_section_smoke_projection` and optional repository injection into the runner: `scripts/evidence_confirm_ec_p2_live_sample.py:142-149`.
  - Regression tests cover runner post-load projection factory and live-sample safe payload on repository failure: `tests/fund/test_evidence_confirm_sources.py:354-387`, `tests/fund/test_evidence_confirm_sources.py:589-604`.

## Validation

```text
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
37 passed in 0.87s
```

```text
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
84 passed in 0.86s
```

```text
uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py
All checks passed!
```

```text
git diff --check -- fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py fund_agent/fund/README.md tests/README.md docs/reviews/evidence-confirm-productionization-ec-p2-implementation-evidence-20260622.md docs/reviews/code-review-20260622-161934.md
PASS
```

## Open Questions

- 无

## Residual Risk

- Live/PDF sample command has not been executed in this gate.
