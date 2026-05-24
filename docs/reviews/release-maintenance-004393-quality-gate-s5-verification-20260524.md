# Release Maintenance 004393 Quality Gate S5 Verification

## Scope

- Gate: `release-maintenance 004393 S5 end-to-end quality gate verification`.
- Branch: `codex/checklist-host-engine-design`.
- Truth sources: `AGENTS.md`, current `docs/design.md`, and `docs/implementation-control.md` Startup Packet / current gate.
- Non-goals: no golden answer edits, no runtime/config changes, no Host/Agent package creation, no `turnover_rate` applicability policy implementation.

## Controller Decision

S5 is accepted locally after validation fixes.

The 004393 end-to-end smoke now completes with `quality_gate_status: warn`, not `block` or renderer failure. The remaining warning is the already-deferred `turnover_rate` disclosure applicability issue for a pre-2026 annual report. It is not treated as a direct extraction bug for 004393/2024 in this gate.

## Fixes Accepted During S5

1. Service quality-gate fixture alignment.
   - File: `tests/services/test_fund_analysis_service.py`.
   - Reason: S2 made holdings coverage fail-closed based on `top_holdings_status` / `top_holdings_source`; an existing service fixture had top holdings data without the new source/status contract.
   - Artifact: `docs/reviews/release-maintenance-004393-quality-gate-s5-validation-fix-20260524.md`.

2. P3 CLI evidence locator expectation alignment.
   - File: `tests/fund/integration/test_p3_cli_e2e_matrix.py`.
   - Reason: S2 changed holdings evidence row locator from broad `top_holdings` to source-semantic `top_ten`; the fake report still anchors the same §8 table.

3. `basic_identity.inception_date` correctness normalization.
   - Files: `fund_agent/fund/extraction_score.py`, `tests/fund/test_extraction_score.py`.
   - Reason: strict golden expected `2022 年 8 月 8 日` while snapshot produced `2022年8月8日`; this is a visual spacing difference in a complete Chinese date, not a correctness mismatch.
   - Guardrail: normalization is scoped to `basic_identity.inception_date` and full `YYYY 年 M 月 D 日` shape; non-date strings still mismatch.
   - Artifact: `docs/reviews/release-maintenance-004393-quality-gate-s5-correctness-date-normalize-worker-20260524.md`.

4. Report wording false positive.
   - Files: `fund_agent/fund/template/renderer.py`, `tests/fund/template/test_renderer.py`.
   - Reason: renderer rejected any occurrence of `买入` / `卖出`, conflating direct trading advice with annual-report disclosure such as `买入并持有`.
   - Guardrail: renderer still rejects explicit trading advice phrases such as `买入金额`, `卖出时机`, `仓位比例`, `收益预测`, `建议买入`, `建议卖出`, `推荐加仓`, and `应该减仓`.
   - Artifact: `docs/reviews/release-maintenance-004393-quality-gate-s5-report-wording-worker-20260524.md`.

5. Report wording targeted re-review fix.
   - Files: `fund_agent/fund/template/renderer.py`, `tests/fund/template/test_renderer.py`.
   - Reason: S5 targeted review found the first wording fix still treated broad modal phrases such as `可以` / `不宜` near `买入` / `卖出` as direct advice, which could still block annual-report disclosure context.
   - Guardrail: broad modal triggers were removed; explicit advice triggers and fixed phrases remain blocked.
   - Artifact: `docs/reviews/release-maintenance-004393-quality-gate-s5-renderer-wording-fix-20260524.md`.

## 004393 Smoke Result

Command:

```text
uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block
```

Result:

- Exit code: `0`.
- `quality_gate_status: warn`.
- Latest run: `reports/quality-gate-runs/analyze-004393-2024-20260524T020730622039Z`.
- Remaining issues:
  - `FQ2 warn` for `turnover_rate`.
  - `FQ2F warn` for fund `004393` P1 failed field `turnover_rate`.
  - `FQ0 info` for strict golden fields outside current snapshot comparable contract.
- Resolved during S5:
  - No `FQ1` block for `basic_identity.inception_date`.
  - No renderer failure for annual-report disclosure wording `买入并持有`.

## Validation

- `uv run pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_holdings_share_change.py -q`
  - Result: `49 passed`.
- `uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q`
  - Result after S5 fixture/date fixes: passed in targeted reruns.
- `uv run pytest tests/services/test_fund_analysis_service.py tests/fund/test_quality_gate_integration.py -q`
  - Result: `31 passed`.
- `uv run pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/services/test_fund_analysis_service.py tests/fund/test_quality_gate_integration.py -q`
  - Result: `33 passed`.
- `uv run pytest tests/fund/template/test_renderer.py -q`
  - Result after wording re-review fix: `56 passed`.
- `uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/fund/integration/test_p3_cli_e2e_matrix.py tests/services/test_fund_analysis_service.py -q`
  - Result: `91 passed`.
- `uv run pytest -q`
  - Result: `649 passed`.
- `uv run ruff check .`
  - Result: passed.
- `uv lock --check`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## Residuals

- `turnover_rate` remains a future quality gate disclosure applicability candidate:
  - For 004393/2024, no direct disclosed stock turnover rate was observed in S0 same-source evidence.
  - Pre-2026 annual reports should not be forced into ordinary P1 extraction failure without a disclosure applicability policy.
  - Future policy should distinguish `regulatory_not_required` / `not_required_pre_2026`, `not_applicable_by_fund_type`, and `required_but_missing`.
- Fee correctness remains a future schema candidate if `fee_schedule` subfields become part of snapshot comparable contract.
- `ParsedTable` physical section metadata and broader continuation handling remain parser hardening residuals from S1/S2.

## Next Entry Point

Proceed to `release-maintenance 004393 aggregate deepreview` for the full 004393 work unit before any draft PR readiness decision.
