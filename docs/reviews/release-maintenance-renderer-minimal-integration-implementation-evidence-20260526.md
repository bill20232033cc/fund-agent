# Renderer Minimal Integration Implementation Evidence

> Date: 2026-05-26
> Gate: renderer minimal integration implementation
> Status: Ready for code review

## Scope Implemented

Implemented the accepted active-fund Chapter 3 missing-reviewed-evidence renderer slice.

Changed files:

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`

No Service, CLI, FQ0-FQ6, Host/Agent/dayu, source helper, `FundDocumentRepository`, PDF/cache/downloader, fixture, durable baseline, or report-quality validator integration changes were made.

## Behavior

For active-fund Chapter 3, current renderer inputs do not expose explicit reviewed turnover/style-evidence status. Therefore the implementation treats the active-fund Chapter 3 path as missing-reviewed-evidence by default and:

- emits `证据不足`;
- states that the report cannot infer style stability, style consistency, or words-actions consistency;
- keeps C2 required markers `言行一致性判断：` and `风格稳定性判断：` under an explicit `不能据此判断...` negative prefix;
- suppresses positive `consistency_result` summary and dimension reason conclusions such as `green / aligned`, `风格一致。`, and `行业偏好一致。`;
- emits the next minimum validation question for annual-report §8 turnover and cross-period allocation / concentration review;
- preserves factual manager identity, disclosed strategy, holdings snapshot, manager alignment, chapter structure, evidence line, and evidence appendix.

The implementation does not add a positive reviewed-evidence branch. That remains deferred to a future input-contract design gate.

## Test Additions

Added focused renderer tests:

- active-fund Chapter 3 missing-reviewed-evidence path emits insufficiency and non-inference wording;
- green/aligned `ConsistencyCheckResult` does not leak unsupported accepted-conclusion wording;
- C2 required markers remain present;
- rendered Chapter 3 is wrapped as `ChapterDraftSurrogate` and validated with `audit_report_writing_bundle()` in test-only mode.
- non-active fund types keep the existing Chapter 3 consistency wording and do not receive the active-fund missing-evidence fallback.

## Validation Matrix

| Check | Command | Result |
|---|---|---|
| Focused renderer tests | `uv run pytest tests/fund/template/test_renderer.py -q` | `61 passed` |
| Sidecar + writing audit tests | `uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py -q` | `20 passed` |
| Full template tests | `uv run pytest tests/fund/template -q` | `101 passed` |
| Adjacent Fund report-quality tests | `uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py -q` | `152 passed` |
| Ruff | `uv run ruff check fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py` | Passed |
| Whitespace | `git diff --check` | Passed |
| Boundary scan | `rg -n "audit_report_writing_bundle\|ReportEvidenceBundle\|FundDocumentRepository\|dayu\\.host\|dayu\\.engine\|extra_payload" fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py` | Matches only test-only audit imports/calls; no production renderer forbidden integration |

## Explicit Non-goals Preserved

- No runtime call from renderer to `audit_report_writing_bundle()`.
- No `ReportEvidenceBundle` projection inside renderer.
- No new `TemplateRenderInput` fields.
- No Service/CLI default behavior or control-flow changes.
- No FQ0-FQ6 semantic changes.
- No Chapter 2 / Chapter 6 material enforcement.
- No Host/Agent/dayu or source-helper integration.

## Related Review Notes Deferred

The repository review `docs/reviews/repo-review-20260526-231040.md` identified useful follow-ups, but they are outside this renderer slice:

- NAV unavailable degradation should be a separate implementation gate.
- Trading-advice detector sharing between renderer and dev-only audit should be a separate safety/wording gate.
- report-quality wrapper collect-errors mode should be a future audit-output ergonomics gate.

## Code Review Follow-up

Two independent code reviews returned `PASS_WITH_FINDINGS` and no blocker.

Accepted fixes before closeout:

- Added non-active Chapter 3 text regression for `index_fund`, `enhanced_index`, and `bond_fund`.
- Adjusted active-fund degradation wording from the awkward `不能据此判断言行一致性判断：` shape to `不能据此判断：言行一致性判断：...`, preserving C2 markers and dev-only audit behavior.

Deferred residual:

- Real manager disclosure text may itself contain stability phrases and trigger future dev-only audit false positives. This should be handled in a later audit-output ergonomics / claim-attribution gate, not in this renderer slice.
