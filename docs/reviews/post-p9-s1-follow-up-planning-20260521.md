# Post-P9-S1 Follow-Up Planning

- **Date**: 2026-05-21
- **Baseline commit**: `7cde828`
- **Previous accepted slice**: P9-S1 analyze product contract hardening
- **Current gate**: `P9-S1 accepted`

## Baseline

P9-S1 closed the product contract gap:

- `fund-analysis analyze` now defaults to product mode and only exposes user-safe inputs.
- developer-only fields require `--dev-override`.
- final judgment is derived by Fund Capability and audited through selected/derived/source.
- product mode keeps quality gate `block` fail-closed.

Current verification baseline:

- `.venv/bin/python -m pytest -q` -> `365 passed`
- ruff passed during P9-S1 review
- `git diff --check` passed during P9-S1 review

## Remaining Options

### Option A — Quality Gate / Golden Coverage ROI

P9-S1 made product `analyze` depend more strictly on quality gate readiness. Current evidence shows `reports/golden-answers/golden-answer.json` is centered on `004393`, while `docs/code_20260519.csv` contains the broader selected fund pool. Product mode will now correctly fail closed for low-quality or not-run gate paths, but the user-facing happy path is too narrow unless quality gate coverage and defaults are deliberately calibrated.

This option directly affects whether normal users can run product `analyze` beyond the current golden-covered sample without relying on developer override.

### Option B — Repo Hygiene

LICENSE, CI, `.gitignore`, and default path hygiene remain useful. This improves maintainability and GitHub readiness but does not change the current report generation contract or user-facing analysis path.

### Option C — Control Doc Hygiene

`docs/implementation-control.md` is long and harder to scan. It remains recoverable as phaseflow truth, so readability cleanup should not take priority over product-path correctness unless the control doc itself starts blocking execution.

## Controller Decision

**Next slice: P9-S2 quality gate / golden coverage product-path calibration.**

Reasoning:

1. P9-S1 intentionally made product mode fail closed on quality gate `block/not_run`.
2. The current golden answer fixture appears to cover `004393`, while the selected fund pool is broader.
3. If left unresolved, product mode may be technically correct but practically narrow: many funds can be blocked by quality gate readiness rather than meaningful analysis failure.
4. Repo hygiene and control-doc hygiene remain valuable, but they are lower leverage than ensuring the default product path has a clear calibrated quality story.

## P9-S2 Planning Scope

P9-S2 should be a planning/review slice first, not immediate implementation.

The plan must decide:

- whether default product `analyze` should require strict golden correctness coverage for every selected fund, or treat missing correctness as an explicit non-blocking FQ0/info under defined conditions.
- how to distinguish "quality gate could not run" from "correctness golden coverage is intentionally absent".
- what minimum golden coverage is required for selected fund categories before calling the product path broadly usable.
- whether `docs/code_20260519.csv` should remain the default product quality gate source, or whether product analyze needs a narrower default curated source until coverage expands.
- how to expose quality gate not-run/block messages so users can understand whether the issue is fund quality, missing fixture coverage, or selected-pool membership.
- which tests should lock product-mode behavior for `004393` and at least one selected fund without golden coverage.

## Explicit Non-Goals

- Do not weaken P9-S1 product/dev separation.
- Do not expose `warn/off` to normal product mode.
- Do not bypass quality gate in product mode.
- Do not expand golden answers by guessing values; golden expected values must remain human-reviewable and evidence-backed.
- Do not treat repo hygiene tasks as part of this slice.

## Next Gate

Current gate becomes `post-P9-S1 follow-up planning accepted`.

Next entry point:

`P9-S2 quality gate / golden coverage calibration plan/review`
