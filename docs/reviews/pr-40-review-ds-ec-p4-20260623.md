# PR-40 DS PR Review — Evidence Confirm Productionization through EC-P4

**Role**: AgentDS independent PR review reviewer
**PR**: https://github.com/bill20232033cc/fund-agent/pull/40
**Head**: `12f36c3628626611f3385c7cbc943856292ea046`
**Base**: `evidence-confirm-anchor-audit-score`
**Branch**: `evidence-confirm-productionization`
**Date**: 2026-06-23

## Verdict: PASS

---

## Review Matrix

| Dimension | Method | Result |
|-----------|--------|--------|
| Code correctness | Full diff review of all production files | PASS |
| Test coverage | Full suite execution | PASS |
| Boundary compliance | AGENTS.md four-layer boundary verification | PASS |
| PR body accuracy | Cross-check body claims against diff evidence | PASS |
| NOT_READY enforcement | Verify non-goals are not claimed | PASS |
| Evidence chain | Verify accepted controller judgments present | PASS |

## Commands Executed

```bash
# Full test suite
.venv/bin/python -m pytest tests/ -q
# → 2259 passed in 7.46s

# Ruff on all EC-P4 files
.venv/bin/python -m ruff check fund_agent/fund/evidence_confirm_production.py \
  fund_agent/fund/evidence_confirm_runner.py fund_agent/fund/quality_gate.py \
  fund_agent/fund/quality_gate_integration.py fund_agent/services/fund_analysis_service.py \
  fund_agent/ui/cli.py tests/fund/test_evidence_confirm_production.py \
  tests/fund/test_quality_gate_integration.py tests/fund/test_evidence_confirm_semantic.py \
  tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
# → All checks passed!

# PR changed files
gh pr diff 40 --name-only
# → 110 files (82 review artifacts + 28 source/test/doc changes)
```

## Findings

### F1 — PASS: Boundary import compliance (re-verified)

After aggregate deepreview F1 fix, Service now imports from `fund_agent.fund.evidence_confirm_runner` facade (`fund_analysis_service.py:65–69`), not from `evidence_confirm_sources`. Boundary test passes (`tests/services/test_fund_analysis_service_llm.py::test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries` → 1 passed). No Service or UI production code directly imports from `evidence_confirm_sources`.

**Production import audit results:**

| Layer | Module | Direct `evidence_confirm_sources` import? | Direct `documents.repository` / source/PDF/cache import? |
|-------|--------|------------------------------------------|--------------------------------------------------------|
| Service | `fund_analysis_service.py` | No — uses `evidence_confirm_runner` facade | No |
| UI | `cli.py` | No | No |
| Fund | `evidence_confirm_production.py` | Yes — Fund-internal sibling (typed result only) | No |
| Fund | `evidence_confirm_runner.py` | Yes — Fund-internal facade re-export | No |
| Fund | `evidence_confirm_semantic.py` | No | No |
| Fund | `evidence_confirm_sources.py` | N/A (self) | Yes — `FundDocumentRepository` in function body (EC-P2 accepted scope) |
| Script | `evidence_confirm_ec_p2_live_sample.py` | Yes — hard-limited 004393/2025 only | Via `evidence_confirm_sources` |

**Disposition**: accepted candidate. No new boundary violation. F1 fix is correctly applied.

### F2 — PASS: Live sample script scope is properly bounded

`scripts/evidence_confirm_ec_p2_live_sample.py:34–35` enforces `AUTHORIZED_FUND_CODE="004393"` and `AUTHORIZED_REPORT_YEAR=2025`. Non-authorized inputs produce exit 2 with safe payload. Script explicitly sets `field_correctness_proven=False` (line 210) and output excludes PDF paths, source URLs, or full excerpt. This matches EC-P2 accepted scope.

**Disposition**: accepted candidate.

### F3 — PASS: Semantic companion remains no-live injected contract

`fund_agent/fund/evidence_confirm_semantic.py` imports zero provider/LLM/openai/httpx modules. The `EvidenceEntailmentClient` is a Protocol injected by the caller; Fund layer never constructs a provider client. Production integration (`evidence_confirm_production.py:77–81`) accepts `semantic_result: EvidenceSemanticResult | None` as an already-computed no-live input. This matches EC-P3 accepted scope — no provider-backed semantic quality is implemented or claimed.

**Disposition**: accepted candidate.

---

## PR Body Cross-Check

| Claim in PR body | Code evidence | Match |
|-----------------|---------------|-------|
| EC-P4 developer opt-in `--dev-override --evidence-confirm-policy` | `cli.py:747–753` | ✓ |
| Product default and checklist remain `off` | `fund_analysis_service.py:1587` (product default `"off"`), `:1679–1680` (checklist fixed `"off"`) | ✓ |
| CLI stderr summary | `cli.py:2641–2668` | ✓ |
| Renderer non-rendering guard | `renderer.py` has zero Evidence Confirm references; test `test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report` | ✓ |
| ECQ0-ECQ4 projection from compact summary only | `quality_gate_integration.py:173–264` | ✓ |
| No-live injected semantic companion | `evidence_confirm_production.py:239–258` (`_semantic_status` only reads pre-computed result) | ✓ |
| Fund-layer `evidence_confirm_runner` facade | `evidence_confirm_runner.py:10–20` | ✓ |
| No default-on Evidence Confirm | product mode `evidence_confirm_policy="off"` (`fund_analysis_service.py:1587`) | ✓ |
| No checklist Evidence Confirm CLI | `cli.py` checklist command has no `--evidence-confirm-policy` parameter | ✓ |
| No provider-backed semantic quality | Zero provider/LLM imports in semantic modules | ✓ |
| No release/readiness promotion | PR body: "PR remains draft; this update does not mark ready, merge, or request reviewers" | ✓ |

## Residual Risks

1. **EC-P2 live sample is single-fund/single-year**: Only `004393/2025` is authorized. The bounded live evidence is an existence proof, not general coverage.
2. **Semantic companion requires caller to construct client**: The `EvidenceEntailmentClient` Protocol has no production implementation. ECQ4 path will remain `not_run` in any production setting until a separate reviewed gate authorizes provider-backed semantic quality.
3. **ECQ0/info dual-path None handling** (original F2, unchanged): `_evidence_confirm_quality_gate_issues(summary=None)` produces ECQ0/info, but `run_quality_gate_for_bundle(evidence_confirm_summary=None)` skips the call entirely. Intentional backward-compatible design; no behavioral impact on current production paths.
4. **F1 facade introduces an intermediate module**: If `evidence_confirm_sources` adds new public symbols in future gates, the facade must be updated. This is a maintenance convention, not a correctness risk.

## Evidence Chain

Accepted controller judgments for all EC phases present in `docs/reviews/`:
- EC-P1A: final closeout, draft-PR-pass controller judgment
- EC-P2: final closeout, draft-PR-pass controller judgment
- EC-P3: final closeout, draft-PR-pass controller judgment
- EC-P4: plan controller judgment, Slice 1-6 code review controller judgments, aggregate deepreview controller judgment, fix artifact, ready-to-open-draft-pr controller judgment
- Prior PR-40 reviews (EC-P3, EC-P1A update, EC-P2 update) in `docs/reviews/pr-40-review-*.md`

PR_REVIEW_COMPLETE_NOT_READY
