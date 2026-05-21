# Post-P9 Follow-Up Planning

- **Date**: 2026-05-21
- **Baseline commit**: `01f2d0d`
- **Previous accepted phase**: P9 analyze product contract hardening
- **Current gate**: `P9 aggregate deepreview accepted`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`

## Baseline

P9 is accepted and closed. It delivered:

- product-mode `fund-analysis analyze` with minimal user-facing inputs;
- developer-only parameters gated behind `--dev-override`;
- Capability-owned final judgment derivation;
- Service-owned quality gate state handling for `pass / warn / block / not_run`;
- strict golden coverage calibration where missing selected-pool coverage is `FQ0/info`, not `gate_not_run`;
- aggregate review acceptance by AgentDS plus supplemental MiMo review with reviewer limitation recorded.

The design goal remains: help ordinary fund investors get an auditable pre-buy fund checkup without LLM hallucination, buy/sell advice, or external Dayu runtime dependency.

## Remaining Options

### Option A - Start another product feature phase

Candidates include automatic thermometer-to-valuation mapping, critical-data report suppression, broader strict golden coverage, LLM writing, and richer report UX.

Decision: defer. These items either require new product design input, new evidence rules, or v2 scope. Starting them immediately would blur the now-closed P9 product-contract boundary.

### Option B - Control document hygiene

The control document is long and difficult to scan. A cleanup could add an index, archive older phase logs, or split historical details.

Decision: defer. The current document is the phaseflow recovery ledger. Any structural rewrite must preserve artifact paths, gate decisions, commits, validation results, and residual risk owner fields. This should be planned after release-readiness basics are stable.

### Option C - Repo hygiene / release readiness

Current repository hygiene facts:

- no `LICENSE*` file is present;
- no `.github/workflows` CI exists;
- `.gitignore` covers runtime outputs and local tmux/launchd helpers, but the inclusion/exclusion policy is still mostly artifact-driven;
- default paths for selected-fund CSV, golden answer, report/cache/output roots are scattered across UI and Capability modules;
- two unrelated untracked files remain outside current commits: the source `.docx` audit report and `docs/reviews/code-review-p8-s3-ds-20260521.md`.

Decision: accept as the next phase. This is the smallest high-leverage follow-up after P9: it reduces review friction, makes validation reproducible, and avoids mixing local artifacts with product code. It does not require changing fund-domain behavior.

## Controller Decision

**Next phase: P10 repo hygiene / release readiness.**

First gate:

`P10-S1 repo hygiene and release readiness plan/review`

P10-S1 should produce a code-generation-ready plan, not implementation.

## Accepted Scope For P10-S1 Planning

The plan must cover:

- LICENSE decision and exact file addition strategy.
- GitHub Actions CI strategy for Python 3.11 with `ruff check .` and `.venv/bin/python -m pytest -q` or equivalent `uv` commands.
- `.gitignore` / artifact policy for generated outputs, local automation, curated fixtures, review artifacts, and source audit documents.
- Default path policy for `docs/code_20260519.csv`, `reports/golden-answers/golden-answer.json`, `reports/quality-gate-runs`, `reports/extraction-snapshots`, and `cache/*`.
- Whether path defaults should remain constants or move behind a small config layer, without introducing Dayu/Host/Engine runtime.
- Handling of current untracked files: source `.docx` audit input and `docs/reviews/code-review-p8-s3-ds-20260521.md`.
- Documentation and test update requirements.

## Non-Goals

- Do not change fund analysis behavior, quality gate semantics, extraction rules, renderer wording, or product CLI contract.
- Do not introduce external Dayu runtime, prompt scene registry, Host/Engine/tool loop, or LLM writing.
- Do not rewrite `docs/implementation-control.md` structure in this slice.
- Do not automatically modify `docs/code_20260519.csv` duplicate `016492`; RR-13 remains human-owned.
- Do not delete or commit unrelated untracked files without explicit scope decision.

## Agent Routing

- Planning specialist: AgentCodex first; AgentMiMo may substitute if AgentCodex has environment/network trouble.
- Plan review: two reviewers from AgentMiMo, AgentDS, AgentGLM, respecting conflict rules.
- Implementation/fix, if the plan is accepted later: AgentCodex preferred.

## Next Entry Point

`P10-S1 repo hygiene and release readiness plan/review`
