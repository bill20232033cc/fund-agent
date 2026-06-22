# Code Review EC-P4 Slice 6 — Docs Sync and Control Evidence

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `code review`
- Branch: `evidence-confirm-productionization`
- Implementation evidence: `docs/reviews/evidence-confirm-productionization-ec-p4-slice6-docs-sync-evidence-20260623.md`
- Review artifact: `docs/reviews/code-review-20260623-001200-ds-ec-p4-slice6.md`

## Verdict

**PASS**

## Review Scope

Target files reviewed:

- `README.md`
- `fund_agent/README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice6-docs-sync-evidence-20260623.md`

Source files cross-checked:

- `fund_agent/ui/cli.py` — CLI option definitions, `_echo_evidence_confirm_summary()`
- `fund_agent/fund/evidence_confirm_production.py` — `EvidenceConfirmProductionSummary` dataclass and factory functions
- `fund_agent/fund/quality_gate_integration.py` — ECQ issue projection
- `fund_agent/services/fund_analysis_service.py` — Service Evidence Confirm orchestration
- `fund_agent/fund/template/renderer.py` — renderer Evidence Confirm absence

## Verification Results

### 1. Docs match accepted Slice 1–5 implementation behavior

All Evidence Confirm claims in docs are verified against source code:

**README.md:**
- `--evidence-confirm-policy off|warn|block` with help text `开发覆盖：Evidence Confirm 策略 off/warn/block；opt-in，不代表 readiness` — matches `cli.py:750-752`
- `evidence_confirm_policy` defaults to `"off"` — matches `cli.py:753`
- `_echo_evidence_confirm_summary()` outputs `evidence_confirm_status`, `evidence_confirm_policy`, `evidence_confirm_checked_facts`, `evidence_confirm_failed_facts`, `evidence_confirm_auditability_score` to stderr — matches `cli.py:2664-2668`
- ECQ0-ECQ4 projection consumes only compact summary — matches `quality_gate_integration.py:173-194`

**fund_agent/README.md:**
- Default `analyze/checklist` don't call Evidence Confirm — matches `cli.py:753` (default `"off"`) and service layer `_effective_evidence_confirm_policy()` at `fund_analysis_service.py:1658-1682`
- `--dev-override --evidence-confirm-policy warn|block` is opt-in — matches `cli.py:747-753`
- Renderer doesn't render Evidence Confirm — confirmed: `rg` on `renderer.py` returns zero Evidence Confirm references
- Boundary statement: Service doesn't construct provider-backed semantic client — matches `evidence_confirm_production.py:87-88` docstring

**fund_agent/fund/README.md:**
- ECQ0-ECQ4 taxonomy table — matches `quality_gate_integration.py:_evidence_confirm_quality_gate_issues()` (lines 197-264):
  - ECQ0: `SEVERITY_INFO` for not-run ✅
  - ECQ1: `_ecq_policy_severity()` → block when policy=block, else warn ✅
  - ECQ2: `_ecq_policy_severity()` → block when policy=block, else warn ✅
  - ECQ3: `SEVERITY_WARN` ✅
  - ECQ4: `_ecq_policy_severity()` → block when policy=block, else warn ✅
- `EvidenceConfirmProductionSummary` fields and boundaries — matches dataclass at `evidence_confirm_production.py:34-74`; no excerpt/PDF/cache/path/provider fields present

**tests/README.md:**
- `test_evidence_confirm_production.py` entry added covering summary compression, status priority, not-run reason, runner/repository failure, no-live injected semantic result, and no excerpt/path/provider payload boundary — matches actual test file
- Combined test command added — matches test file paths

**docs/design.md:**
- Evidence Confirm developer opt-in section (lines 885-892) matches code behavior
- `off` is explicit no-run/off policy, `warn|block` call runner — verified in `fund_analysis_service.py:1306-1333`
- CLI/UI summary only, renderer doesn't render Evidence Confirm — verified
- Future/candidate boundaries explicitly listed as NOT implemented — confirmed

### 2. No overclaim

Strict checks confirmed no positive claims in the following categories:

| Overclaim category | Check result |
|---|---|
| Default-on Evidence Confirm | No positive claim found. Default consistently stated as `off` or not-run. |
| Release/readiness claim | No positive claim found. Consistently stated as `NOT_READY`. |
| Provider-backed semantic quality/client | No positive claim found. Consistently stated as "no-live injected result only". |
| Checklist Evidence Confirm CLI support | No positive claim found. Consistently stated as absent/deferred. |
| Evidence Confirm in report body | No positive claim found. Consistently stated as "不渲染"/"不写入". |

All positive statements are verified against source code. All negative/boundary statements about what is NOT implemented are accurate.

### 3. Policy `off` documented as no-run/off

- `docs/design.md:887`: "`off` 是显式 no-run/off policy，不调用 Evidence Confirm runner"
- `README.md:110`: "默认 `off`"
- `README.md:113`: "默认 `analyze` 和 `checklist` 都不会调用 Evidence Confirm"
- `fund_agent/README.md:9`: "默认 `analyze/checklist` 不调用 Evidence Confirm"
- Service code: `_effective_evidence_confirm_policy()` returns `"off"` for product mode and checklist — matches `fund_analysis_service.py:1587, 1614`

### 4. Renderer non-rendering and CLI/UI summary outside report body

- `fund_agent/README.md:34`: "Renderer 当前不渲染 Evidence Confirm"
- `README.md:115`: "报告 Markdown 正文不渲染 Evidence Confirm 段落"
- `docs/design.md:888`: "renderer 报告 Markdown 仍不渲染 Evidence Confirm"
- Source verification: `rg evidence_confirm fund_agent/fund/template/renderer.py` returns zero results
- Summary output via stderr only (`typer.echo(..., err=True)` at `cli.py:2664-2668`), not stdout report

### 5. ECQ0-ECQ4 taxonomy accuracy

ECQ taxonomy is consistent across all three locations:

| Source | ECQ0 | ECQ1 | ECQ2 | ECQ3 | ECQ4 |
|--------|------|------|------|------|------|
| `quality_gate_integration.py` | info, not-run | repo pathway fail | V2 hard-gate fail | V2 warn | semantic fail/warn |
| `fund_agent/fund/README.md` | info, not-run | repo pathway fail | V2 hard-gate fail | deterministic V2 warn | semantic fail/warn |
| `docs/design.md` | info, not-run | repo pathway fail | V2 hard-gate fail | deterministic V2 warn | semantic fail/warn |
| `README.md` | summary-level only (not per-code) | — | — | — | — |

All three detail sources are consistent. README.md summarizes at a higher level without contradicting. Taxonomy is limited to compact summary consumption; no document/PDF/cache reading in ECQ projection code (`quality_gate_integration.py:181-183`).

### 6. Docs do not direct Service/UI/renderer/quality gate to access PDF/cache/source/parser/provider internals

All boundary statements are correctly separated:

- **Service**: accesses Fund layer `EvidenceConfirmProductionSummary` only; no PDF/cache/source/parser/provider access — `fund_analysis_service.py:705-726`
- **UI/CLI**: outputs summary fields via stderr; no direct access — `cli.py:2641-2668`
- **Renderer**: zero Evidence Confirm references — confirmed
- **Quality gate**: ECQ projection consumes only `EvidenceConfirmProductionSummary`; no document/PDF/cache/provider access — `quality_gate_integration.py:181-183`

### 7. Evidence artifact records validation and residual risks

- Validation executed: overclaim `rg` checks (negative-only results), positive-overclaim `rg` (no hits), `git diff --check` (passed), untracked artifact whitespace check (clean)
- Residual risks table: 4 entries, each with classification and owner
- Completion status: `SLICE6_DOCS_SYNC_READY_FOR_CODE_REVIEW_NOT_READY` — marks readiness for code review, not release readiness

### 8. Git diff --check

`git diff --check` on target docs returns no whitespace errors.

## Findings

Count: **0**

No factual errors, overclaims, scope violations, or boundary inaccuracies found.

All docs claims are either:
- Verified against source code (positive claims), or
- Consistently stated as NOT implemented / deferred / candidate (negative claims about future features)

## Blocking Open Questions

None.

## Review Metadata

- Review type: code review (AgentDS worker)
- Reviewed by: AgentDS
- Reviewed at: 2026-06-23T00:12:00Z
- Target branch: `evidence-confirm-productionization`
- Base commit: `4ecc760 gateflow: accept ec-p4 service integration slice 5`
