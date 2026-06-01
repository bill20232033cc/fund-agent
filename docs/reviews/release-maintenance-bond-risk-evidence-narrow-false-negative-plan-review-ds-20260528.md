# Bond Risk Evidence Narrow False-Negative Plan — Plan Review (DS)

> Date: 2026-05-28
> Role: plan review worker DS
> Review target: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
> Required context: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, Slice 6 validation/root-cause/investigation artifacts, aggregate deepreview (MiMo + controller judgment)
> Verdict: **PASS_WITH_FINDINGS** — plan is handoff-ready for controller after 4 mandatory fixes; 3 advisory items

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: plan review worker DS only; no gateflow start, no implementation, no commit, no push, no PR.
- Truth sources read: `AGENTS.md` (v2.1+), `docs/design.md` (v2.2), `docs/implementation-control.md` (v2.1), Slice 6 controller judgment / real validation / root-cause DS / investigation GLM / aggregate deepreview MiMo + controller judgment.
- Current code inspected: `fund_agent/fund/extractors/bond_risk_evidence.py` (1355 lines), `fund_agent/fund/extractors/models.py` (bond risk types), `tests/fund/extractors/test_bond_risk_evidence.py` (711 lines).
- Repository boundary verified: `load_annual_report` is `async def`; `ExtractionMode` Literal = `"direct", "derived", "estimated", "missing"` (no `partial`).

### Before File Edit

- Allowed write path: this review artifact only.
- No source code, tests, generated reports, or external state changed.

### Before Completion

- Self-check: pass
- All review criteria addressed with evidence and specific fix recommendations.
- Four mandatory findings, three advisory findings.

---

## Review Criteria Check

| Criterion | Verdict |
|---|---|
| Handoff/code-generation readiness | PASS after M1-M4 fixes |
| Scope tightness | PASS — two files only, correct |
| No FQ0-FQ6 weakening | PASS — quality gate unchanged |
| No direct PDF/cache | PASS — extractor consumes ParsedAnnualReport |
| No fund-own-rating confusion | PASS — portfolio_credit_exposure semantic split explicit |
| credit_risk semantic split | PASS — holding_rating_distribution vs fund_own_rating clear |
| Rating table detection false-positive risk | PASS after M4 fix |
| A/C/E/F all-class aggregation, fail-closed, not A-only | PASS after M3 fix |
| Drawdown qualitative remains weak, no NAV-derived | PASS — hard boundary explicit |
| Validation command correctness (async smoke) | FAIL — M1 |
| No schema/score/snapshot changes unless justified | PASS after M2 clarification |
| Tests sufficient | PASS after A2 advisory |

---

## Mandatory Findings

### M1: Validation Smoke Command Will Fail — Missing `asyncio.run()`

**Severity**: CRITICAL (would block implementation acceptance validation)

**Evidence**: `FundDocumentRepository.load_annual_report` is `async def` (repository.py:32, 290). The plan's validation command on line 365–366 is:

```python
uv run python -c '... report = FundDocumentRepository().load_annual_report("006597", 2024, force_refresh=True); print(report.key.fund_code, ...)'
```

This calls an async function synchronously. The result would be a coroutine object, not a `ParsedAnnualReport`. `report.key.fund_code` would raise `AttributeError`.

The GLM investigation artifact (slice6-investigation-glm line 290-294) correctly wraps the call in `asyncio.get_event_loop().run_until_complete()`. The Slice 6 controller validation may have used a different command than the one written in this plan, or used a sync wrapper method.

**Fix**: Replace line 365–366 with one of:

Option A (single-line asyncio):
```bash
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); report = asyncio.run(repo.load_annual_report("006597", 2024, force_refresh=True)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
```

Option B (explicit event loop, matches GLM approach):
```bash
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); report = loop.run_until_complete(repo.load_annual_report("006597", 2024, force_refresh=True)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
```

Option A is simpler and works in Python 3.11+ with no running event loop. Recommend Option A.

### M2: `extraction_mode` Mismatch Between Plan And Available Type

**Severity**: MODERATE (not blocking, but needs explicit resolution)

**Evidence**: The plan's line 194 F1 finding references `extraction_mode` should use `partial`. However, `ExtractionMode` Literal (`models.py:10`) only defines `"direct", "derived", "estimated", "missing"` — there is no `"partial"` value. The current code (`bond_risk_evidence.py:1314-1331`) maps `partial` → `estimated`, which the aggregate deepreview F4 correctly classified as a reasonable fallback and non-blocking.

The plan says "no expected changes to `fund_agent/fund/extractors/models.py`" (line 93), but also implies the `extraction_mode` field should show `partial`. These two statements conflict unless the plan explicitly accepts `estimated` as the correct mapping for partial contract status.

**Fix**: Add one sentence to the plan's scope section:
> `extraction_mode` for `bond_risk_evidence` with `contract_status=partial` remains `estimated` because `ExtractionMode` has no `partial` value; the structured `bond_risk_contract_status` field is authoritative for consumers.

This eliminates the contradiction without expanding scope to models.py.

### M3: `_find_share_change_table` First-Match Problem — Net-Asset Statement Table

**Severity**: MODERATE (implementation bug if not addressed)

**Evidence**: The GLM investigation (line 193-198) proved that `_find_share_change_table` returns the **first** table matching keywords. In the real `006597` / 2024 parse, Table #23 (page 28, 净资产变动表) appears before Table #78 (page 65, §10 基金份额变动表). Both contain `期初`/`期末`/`申购`/`赎回`. The current code iterates tables sequentially and returns the first match.

The plan's Slice 2 says "improve `_find_share_change_table()` to prefer real §10 share-change tables and reject net-asset statement tables" (line 249), and "reject or deprioritize financial-statement tables with `实收基金`, `未分配利润`, `净资产合计`" (line 169). This is directionally correct.

However, the plan does not specify **whether to scan all tables first** to pick the best match, or to continue scanning after finding a match that is later rejected. The current implementation (`bond_risk_evidence.py:947-951`) returns on first keyword match. If the implementation only adds a rejection check for financial-statement keywords to the existing first-match loop, and the first match (Table #23) is rejected, it would then correctly find Table #78. But the plan's wording "deprioritize" is ambiguous — it could mean "skip financial tables and take the first non-financial match" or "score all tables and pick the best."

**Fix**: Clarify Slice 2 to say:
> Change `_find_share_change_table()` to scan all tables and select the best match: prefer tables containing `基金份额` and `份额总额` over tables containing `实收基金` and `净资产合计`. If multiple candidates remain, prefer those with multi-class columns that align with §2 mapping. Return `None` if no table survives rejection.

The test `test_redemption_share_pressure_rejects_net_asset_statement_table` (line 319-321) already covers this scenario.

### M4: Rating Table Detection False-Positive Risk — Insufficient Shape Constraint

**Severity**: MODERATE (could cause false acceptance in edge cases)

**Evidence**: The plan's detection rules (line 132-136):
- Table header contains `信用` + `评级`
- Rows contain rating category tokens (A-1, AAA, AA+, etc.)

This is a reasonable heuristic for `006597` / 2024, but the plan does not define a shape constraint. A table could match the header keywords AND have rows containing "AAA" but be a peer comparison table, a rating methodology description table, or a table where "AAA" refers to the fund itself rather than holdings.

The GLM investigation confirms Tables #59-#62 have the expected shape: header contains `短期信用评级` / `长期信用评级`, data rows contain `A-1`/`AAA`/`AAA以下`/`未评级`/`合计` with numeric values. This is the correct pattern.

**Fix**: Add to Slice 1 credit risk detection rules:
> Require at least one data row with a non-empty numeric value in the current-period column. If all rows are dash-only or the table has fewer than 2 data rows, do not accept. Prefer tables where the first column contains rating category labels and the second/third columns contain numeric amounts (not percentages or text descriptions).

Additionally, add to stop conditions:
> If the helper matches a table where "AAA" or other rating tokens appear in a fund-own-rating context (e.g., "本基金评级为AAA"), stop and revise.

The test `test_holding_rating_distribution_table_is_credit_risk_portfolio_exposure_not_fund_rating` (line 290-297) covers the semantic check, but the numeric-value shape constraint should also be tested or at minimum mentioned as an implementation requirement.

---

## Advisory Findings

### A1: Decimal Tolerance Not Specified

**Severity**: LOW (implementation can choose a reasonable default, but ambiguity risks inconsistent behavior)

The plan (line 181) says: `beginning + subscription - redemption + split == ending, with a small Decimal tolerance for formatting noise`. "Small" is not defined. Recommended: specify `Decimal("0.01")` (one cent tolerance) or `Decimal("1.0")` (one unit tolerance) explicitly, so the test `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch` (line 327-329) has a defined boundary between "formatting noise" and "arithmetic mismatch."

### A2: Missing Test for §2 Parsed Table Mapping

**Severity**: LOW (covered implicitly by all-class aggregation test, but explicit test would improve coverage)

The plan specifies §2 mapping should use parsed tables first (line 157: "Parse §2 subordinate fund mapping from parsed tables first"), which aligns with the GLM investigation finding that Table #0 contains clean A/C/E/F → fund code mapping. However, the test list (line 306-333) does not include a test that isolates `_share_class_evidence` from table-based §2 mapping. The test `test_redemption_share_pressure_aggregates_all_a_c_e_f_classes` (line 308-313) covers this end-to-end, but a unit-level test for the §2 table parsing helper would make failures easier to diagnose.

**Recommendation**: Add a targeted test `test_share_class_evidence_from_section_two_table` that builds a synthetic Table #0 with `下属分级基金的基金简称` and `下属分级基金的交易代码` rows, and asserts correct A/C/E/F → fund code mapping.

### A3: Plan References `_trim_note` Without Definition

**Severity**: INFO (exists in current code, no action needed)

The plan (line 144) references `_trim_note` for metric_value formatting. This helper exists in the current codebase (`bond_risk_evidence.py:1295-1311`) and truncates to 120 characters. No issue — just noting for cross-reference.

---

## Invariant Verification

### FQ0-FQ6

Plan correctly prohibits FQ0-FQ6 weakening (line 50). Explicitly excludes `quality_gate.py` from scope (line 95). No changes to FQ rules, thresholds, or severity. **PASS.**

### FundDocumentRepository Boundary

Extractor consumes only `ParsedAnnualReport` (line 51). Validation command uses `FundDocumentRepository` (line 365). No direct PDF/cache/source helper access. **PASS** (after M1 fix).

### Fund-Own-Rating Confusion

Plan's Contract Decisions section (line 105-119) draws a clear line: rating distribution = `portfolio_credit_exposure` / `holding_rating_distribution`; explicitly forbids `fund_rating`, `基金评级`, `本基金评级`. Test `test_holding_rating_distribution_table_is_credit_risk_portfolio_exposure_not_fund_rating` validates this. **PASS.**

### credit_risk vs fund_own_rating Semantic Split

Plan (line 42-46) correctly distinguishes: annual-report rating distribution tables = held bond/security rating distribution (usable); fund own rating = separate contract requiring rating object, agency, rating date, source anchor (not implemented, explicitly forbidden). **PASS.**

### A/C/E/F All-Class Aggregation And Fail-Closed

Plan requires all four classes A/C/E/F (line 46-48), explicit beginning/subscription/redemption/split/ending rows, class net change, arithmetic reconciliation, fail-closed on missing class/missing row/unparseable number/column mismatch/arithmetic mismatch (line 48). Test `test_redemption_share_pressure_not_a_only` ensures A-only not accepted. **PASS** (after M3 fix for table selection).

### Drawdown Boundary

Plan explicitly states no NAV-derived drawdown (line 49, 218-219), qualitative `控制回撤` remains `weak`, `drawdown_stress` stays in `weak_group_ids`. Test `test_drawdown_control_text_alone_remains_weak_after_false_negative_fix` validates. **PASS.**

### Schema/Score/Snapshot Changes

Plan lists allowed-only-if-mandatory for models/snapshot/score/quality_gate (line 91-96). No changes expected per plan intent. `extraction_mode` = `partial` vs `estimated` is the only tension (see M2). **PASS** after M2 resolution.

### Test Sufficiency

Test list covers: positive credit risk, negative credit risk, anchor-missing credit risk, all-class redemption, not-a-only redemption, reject-net-asset redemption, class-mismatch redemption, arithmetic-mismatch redemption, anchor-missing redemption, drawdown regression. 10 tests minimum. Clear pass/fail assertions. **PASS** (advisory A2 for additional coverage).

### No Score-Policy Bypass

Plan (line 50, 440) explicitly prohibits score-policy bypass, missing evidence pass, quality gate semantic change. Expected outcome keeps `bond_risk_evidence_missing.baseline_blocking=true` with only `drawdown_stress` remaining. **PASS.**

---

## 设计边界检查 (Design Boundary Checklist from design.md §12)

| Requirement | Verdict |
|---|---|
| 违反 §1.3 非目标 | 否 — 不做组合管理、不输出买卖建议、不引入 Host/Agent |
| 保持 `UI → Service → Host → Agent` 四层边界 | 是 — 只修改 Agent 层 extractor |
| 生产年报访问只通过 `FundDocumentRepository` | 是 — extractor 只消费 `ParsedAnnualReport` |
| 未误拼接 Host/tool loop/LLM 写作 | 是 — 纯确定性 extractor 增强 |
| 遵守 `pyproject.toml` 工程基线 | 是 — Python 3.11+, 无新依赖 |
| 测试覆盖率策略说明 | 是 — 单文件 ≥80% 评审目标隐含在 AGENTS.md 要求中 |
| License/repo hygiene | N/A — 不涉及 |
| success signal 可验证 | 是 — 明确 CLI 验证命令和预期输出 |

---

## Review Summary

The plan is well-structured, evidence-based, and correctly scoped. It faithfully incorporates:

- The user correction that annual-report rating distribution = holding rating distribution, not fund own rating
- The user correction that `006597` redemption must aggregate A/C/E/F, not A-only
- The Slice 6 controller judgment that `drawdown_stress` stays weak
- The GLM investigation's real table evidence (Tables #0, #59-#62, #78)

Four mandatory findings must be addressed before handoff to implementation:

1. **M1 (CRITICAL)**: Validation command is missing `asyncio.run()` wrapper — would fail immediately
2. **M2 (MODERATE)**: Resolve `extraction_mode` = `partial` vs `estimated` contradiction
3. **M3 (MODERATE)**: Clarify `_find_share_change_table` scan-all vs first-match behavior
4. **M4 (MODERATE)**: Add numeric shape constraint to rating table detection to reduce false-positive risk

M1 is a one-line fix. M2-M4 are specification clarifications.

After these fixes, the plan is code-generation ready. The implementation is well-bounded (one extractor file + one test file), has specific stop conditions per slice, and includes a complete validation command matrix.

## Review Signature

- Reviewer: DS (plan review worker)
- Review type: adversarial plan review
- Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-ds-20260528.md`
- Verdict: **PASS_WITH_FINDINGS** — 4 mandatory findings, 3 advisory findings; plan ready for controller after M1-M4 resolution
