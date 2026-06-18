# Strict Golden 2025 Coverage / Promotion Planning Gate Plan

Date: 2026-06-12

Gate: `Strict golden 2025 coverage / promotion planning gate`

Verdict: `PLAN_DRAFT_FOR_REVIEW`

## 1. Goal

Plan the next strict golden / coverage route after the accepted turnover-rate applicability fix.

The planning question is:

> After `turnover_rate` is no longer a valid 2025 blocker, what evidence is needed to classify the remaining 2025 strict-golden coverage residual, and what later implementation or promotion gates are allowed?

This gate does not implement coverage, edit golden answers, promote fixtures, run readiness, or claim release readiness.

## 2. Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-quality-warning-issue-identity-evidence-controller-judgment-20260612.md`
- `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-implementation-controller-judgment-20260612.md`
- `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-implementation-evidence-20260612.md`
- Current code facts in:
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`
  - `fund_agent/fund/golden_readiness_preflight.py`
  - `fund_agent/fund/README.md`
  - targeted tests under `tests/fund/` and `tests/services/`

## 3. Current Facts

### Accepted Gate Facts

- Quality warning issue identity evidence accepted three identities:
  - `FQ2/warn turnover_rate`
  - derivative `FQ2F/warn 004393`
  - `FQ0/info year_not_covered`
- Turnover-rate regulatory applicability evidence reclassified the 2025 `turnover_rate` warning as an applicability/scoring issue, not a default extractor failure.
- The narrow fix implementation is accepted:
  - pre-2026 and explicit non-annual `turnover_rate` rows are excluded through `_scorable_records(...)`;
  - 2026+ missing `turnover_rate` still fails P1;
  - no replacement `ScoreApplicabilityIssue` is emitted for expected non-applicability.

### Repo Facts

- `extraction_score.py` already derives `correctness.coverage_scope="year_not_covered"` when strict golden contains the fund but not the current `(fund_code, report_year)`.
- `quality_gate.py` maps `year_not_covered` to `FQ0/info`, not to `FQ2/FQ2F`.
- `golden_readiness_preflight.py` currently loads strict golden coverage at fund-code level only.
- `fund_agent/fund/README.md` states `strict_golden_year_not_covered` and `strict_golden_partial_coverage` are reserved future codes and do not currently trigger in preflight.

### Planning Implication

The remaining 2025 strict golden work should not be framed as "fix extractor" or "promote fixture now".

It should first prove the current post-fix identity:

```text
2025 turnover_rate warning removed
remaining strict-golden residual = year-specific coverage / promotion policy
release/readiness = NOT_READY
```

## 4. Non-goals

This planning gate and its immediate evidence successor must not:

- modify source, tests, runtime behavior, golden answers, fixtures, promotion manifests, README, or design docs;
- run live EID, network, PDF, FDR, provider, LLM, `analyze`, `checklist`, release, PR, merge, mark-ready, cleanup, delete, move, archive, import, ignore, or push commands;
- use arbitrary `reports/` or untracked residue as proof unless a gate captures path, size, hash, command, and lineage;
- add Eastmoney, fund-company website, CNINFO, fallback, or any source expansion;
- promote 2025 strict golden coverage or fixture eligibility;
- claim release/readiness pass.

## 5. Recommended Next Gate

Recommended next entry:

`Strict golden 2025 coverage evidence gate`

Classification: `standard`, no-live, no source/test/runtime changes.

Purpose:

1. Verify the accepted turnover-rate fix removes `turnover_rate` from the 2025 quality warning path in a no-live, reproducible way.
2. Verify the remaining 2025 strict golden residual is `FQ0/info year_not_covered` / year-specific strict golden coverage, not a field extraction failure.
3. Verify current `golden_readiness_preflight` v1 is fund-level and does not yet represent year-specific coverage.
4. Decide whether the following implementation gate is needed:
   - `Strict golden year-aware preflight implementation gate`; or
   - no-code disposition if evidence is sufficient and promotion remains deferred.

## 6. Evidence Gate Plan

### Allowed Write Set

- `docs/reviews/mvp-strict-golden-2025-coverage-evidence-20260612.md`
- two independent review artifacts under `docs/reviews/`
- controller judgment under `docs/reviews/`
- `docs/current-startup-packet.md` and `docs/implementation-control.md` only after controller acceptance

### Allowed Commands

Only local deterministic, no-live commands:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_readiness_preflight.py -q
uv run ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_readiness_preflight.py
```

If additional evidence is needed, use a temporary no-live script or existing unit helpers that construct synthetic score / quality / preflight inputs in `/tmp`. The script must not read PDF/cache/repository/provider/network and must record its input JSON in the evidence artifact.

### Evidence Questions

| Question | Required direct evidence | Acceptance signal |
|---|---|---|
| Is 2025 `turnover_rate` removed from quality warning identity after the accepted fix? | Targeted tests or synthetic score/quality input showing no `FQ2/FQ2F` from `turnover_rate` for 2025 | PASS only if no turnover-derived `FQ2` or P1 `FQ2F` remains |
| Does 2025 still produce strict golden coverage residual? | Synthetic or existing same-source score correctness summary with golden covering `004393 / 2024` but snapshot/report year `2025` | `coverage_scope="year_not_covered"` and `FQ0/info` |
| Is this residual year-specific rather than fund-level? | Code/test evidence from `extraction_score.py` and `golden_readiness_preflight.py` | Score/quality are year-aware; preflight v1 is fund-level only |
| Is promotion allowed now? | Evidence matrix with readiness blockers/warnings | Promotion remains deferred unless year-aware preflight and fixture promotion state are accepted later |

### Explicit Rejections

- Reject any finding that treats 2025 non-disclosed `turnover_rate` as a blocker after the accepted fix.
- Reject any readiness claim based only on `quality_gate_status=pass/warn`.
- Reject any promotion claim based on fund-level strict golden coverage when year-specific coverage is unresolved.
- Reject arbitrary pre-existing `reports/` residue without current-gate lineage.

## 7. Possible Follow-up Implementation Gate

Open only if the evidence gate confirms a current product gap in promotion/preflight semantics.

Name:

`Strict golden year-aware preflight implementation gate`

Allowed source write set:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `fund_agent/fund/README.md` only if public Fund README coverage semantics change
- `docs/reviews/` implementation/review/controller artifacts
- control docs after acceptance

Non-goals:

- no extractor/source/FDR/PDF/network/provider/LLM/analyze/checklist changes;
- no golden answer JSON edits;
- no fixture promotion state edits;
- no promotion/readiness/release claim;
- no fallback/source expansion.

Expected implementation decisions:

1. Load strict golden coverage as `(fund_code, report_year)` identities, not only fund codes.
2. Preserve the existing `strict_golden_not_configured` and `strict_golden_fund_not_covered` semantics.
3. Add `strict_golden_year_not_covered` only when:
   - fund code exists in strict golden; and
   - requested `report_year` is not covered by that fund's strict golden records.
4. Keep `strict_golden_partial_coverage` deferred unless the evidence gate proves it is necessary for the current 2025 route.
5. Preserve old v1 / legacy JSON behavior where missing `report_year` is loaded as the accepted legacy year by the golden-answer loader; do not invent report years in preflight.
6. Ensure preflight output remains readiness metadata only and does not alter quality gate severity.

Required tests:

- strict golden absent -> `strict_golden_not_configured`;
- fund not covered -> `strict_golden_fund_not_covered`;
- fund covered for 2024 but artifact report year is 2025 -> `strict_golden_year_not_covered`;
- fund covered for 2025 -> no strict golden coverage blocker;
- reserved `strict_golden_partial_coverage` remains not emitted unless explicitly implemented;
- fixture promotion absence still blocks independently;
- existing 006597 bond resolved item behavior unchanged.

## 8. Promotion Policy After Evidence

Do not open a fixture/golden promotion gate until all are true:

- turnover-rate applicability fix is accepted;
- 2025 strict golden year coverage is represented in preflight or explicitly accepted as deferred;
- fixture promotion state manifest exists and is accepted;
- quality gate output has no `block`;
- any remaining `warn` is classified with owner and does not claim readiness;
- no live/provider/source expansion evidence is required for the specific no-live promotion claim.

## 9. Validation For This Planning Gate

This planning gate should validate only docs hygiene:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

## 10. Completion Report Format

The evidence gate worker must report:

- exact commands run and outputs;
- exact input artifact paths, sizes, and hashes for any generated temp JSON used as proof;
- accepted / rejected / deferred finding table;
- whether implementation is needed;
- exact next entry recommendation, one primary entry only.
