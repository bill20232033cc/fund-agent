# P17-S1 Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPT_P17-S1_PLAN_AND_PROCEED_TO_IMPLEMENTATION`

Controller accepts `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md` as code-generation-ready. The next gate is:

```text
P17-S1 tracking_error extractor ambiguity boundary implementation
```

MiMo and GLM both returned `PASS_WITH_FINDINGS` with no blocking findings. The design-boundary checklist passes: the plan stays inside Fund Capability extractor hardening, keeps annual-report access through `FundDocumentRepository` / `FundDataExtractor`, rejects production `tracking_error` golden rows without direct observed disclosure evidence, and does not introduce calculated tracking error, external index adapters, Dayu runtime, LLM writing, Evidence Confirm, or Service/UI/Runtime/Engine/source orchestration changes.

## Inputs

| Artifact | Result |
|---|---|
| `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md` | Plan target |
| `docs/reviews/p17-s1-plan-review-mimo-20260522.md` | `PASS_WITH_FINDINGS` |
| `docs/reviews/p17-s1-plan-review-glm-20260522.md` | `PASS_WITH_FINDINGS` |
| `docs/design.md` v2.1 | Design truth and §11 design-boundary checklist |
| `docs/implementation-control.md` | Control truth |

Excluded local drafts remain out of scope: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Finding Decisions

| Finding | Decision | Implementation constraint |
|---|---|---|
| MiMo F1: old `"tracking_error_ambiguous"` usage may remain | Accepted | Implementation must replace all current `"tracking_error_ambiguous"` usages in production code and focused tests with specific successor notes; no stale literal should remain unless implementation artifact explicitly justifies a residual and reviewers accept it. |
| MiMo F2: `tracking_error_manager_narrative` classifier underspecified | Accepted | Implementation should define deterministic manager-narrative signals or, if no stable signal exists without false positives, keep it as a documented residual instead of adding brittle heuristics. |
| MiMo F3 / GLM F3: `tracking_error_benchmark_only` may be unreachable under current keyword gating | Accepted | Implementation should only add this note for reachable, direct tracking-error keyword contexts; do not add a new broad benchmark-only scan that changes extraction semantics. If unreachable, record it as residual. |
| MiMo F4: incomplete-anchor fixture may require impossible objects | Accepted as residual option | Implement only if naturally representable through current `ParsedAnnualReport` / `ParsedTable`; otherwise record `future parser malformed-table fixture` residual. |
| MiMo F5 / GLM F1: blocker accumulation / duplicate scan strategy | Accepted as implementation guidance | Prefer one classification path or explicit precedence-based blocker selection; do not let first-seen ordering override the accepted blocker precedence. |
| MiMo F6/F7: existing target and standard-deviation tests lack note assertions | Accepted | Update existing tests or add equivalent focused tests so target/limit and standard-deviation-only paths assert their precise notes. |
| GLM F2: target-only `continue` path may remain silent | Accepted | Implementation must record target/limit/control blocker notes even when current code would `continue`, while still allowing later valid direct disclosure to win. |
| GLM F4/F5: `_has_actual_tracking_error_signal` and success-path helper signatures | Deferred / non-blocking | Do not broaden keyword strategy in P17-S1; preserve public extractor success contract and existing success tests. |

## Accepted Implementation Scope

Implementation may edit only:

- `fund_agent/fund/extractors/performance.py`
- `tests/fund/extractors/test_performance.py`
- optional focused fixture snippets under `tests/fixtures/fund/extractors/performance/` if materially clearer
- implementation and code-review artifacts under `docs/reviews/`

Implementation must not edit:

- production golden files or golden templates;
- selected CSV / RR-13 data;
- `docs/design.md`, `docs/implementation-control.md`, README files, Service/UI/Runtime/Engine/source orchestration, document source adapters, PDF/cache helpers, branch/PR/issue/external state;
- excluded local drafts.

## Required Implementation Validation

Minimum validation:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
.venv/bin/python -m pytest tests/fund/extractors -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
```

If shared extractor models, snapshot serialization, score/quality behavior, or comparability paths are touched, also run:

```bash
.venv/bin/python -m pytest tests/fund -q
.venv/bin/python -m pytest -q
```

## Controller Decision

Proceed to implementation. No plan revision is required before implementation; all reviewer findings are narrow enough to be implementation constraints and later code-review checks.
