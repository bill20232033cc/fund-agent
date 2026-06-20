PLAN_REREVIEW_PASS

## Re-review Target

Plan artifact: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md`

Original review findings: `docs/reviews/plan-review-core-risk-source-truth-ds-20260620.md` (F1–F7)

Scope: confirm F1–F7 closure only, plus whether fixes introduced any new blocker inside the same planning scope.

## Required Checks

| Check | Status | Evidence |
|---|---|---|
| No `core_risk` path calls `_select_product_essence_values()` | CLOSED | Plan line 141: "Do not call `_select_product_essence_values()` from any `core_risk.v1` code path." Explicit prohibition. |
| Neutral shared risk-characteristic helper required | CLOSED | Plan lines 142–155: three neutral helpers `_collect_risk_characteristic_table_candidates`, `_collect_risk_characteristic_paragraph_candidates`, `_select_risk_characteristic_value` specified; `product_essence.v1` refactored to call same helpers. |
| Scope says only `risk_characteristic_text` implemented, four roles deferred | CLOSED | Plan lines 8–9 mandatory scope statement; lines 69–82 candidate role disposition with explicit defer rationale per role. |
| Accepted direct result exposes four `required=False` deferred_role gaps | CLOSED | Plan lines 77–82: deferred-role gaps specified with `gap_code="deferred_role"`, `required=False`, one per deferred role. |
| `data_extractor` core_risk fallback first activation tested | CLOSED | Plan line 179: "This slice is the first activation verification for the existing `data_extractor.py:742-754` core_risk.v1 -> risk_characteristic_text fallback path; before this work, the path is effectively dead code." Test matrix line 227 confirms. |
| `_select_core_risk_values()` call chain specified | CLOSED | Plan lines 148–151: call only neutral helpers, return `_RiskCharacteristicValueCandidate`, map ambiguity for single output path only. |
| Ambiguous `risk_characteristic_text` test exists | CLOSED | Test matrix line 209: "proof-positive ambiguous risk-characteristic text → missing, empty value/anchors, `ambiguous_table_or_locator`, `candidate_evidence == ()`". |
| `docs/fund-analysis-template-draft.md` forbidden | CLOSED | Plan line 267: explicitly listed in Forbidden files/modules. |
| Residual suggestions represented | CLOSED | Plan lines 272–281: seven residual risks covering fact-extractor boundary, deferred roles, binary status model, facade schema, readiness, shared-helper regression, and candidate-boundary behavior. |

## Finding-by-Finding Closure

### F1 [CRITICAL] – Slice 2 错误复用 product_essence selector

**Status: CLOSED**

Original issue: plan directed `core_risk.v1` to call `_select_product_essence_values()`, which collects all `_PRODUCT_ESSENCE_LABELS` (basic_identity, product_profile, benchmark, risk_characteristic_text) — wasteful, coupled, and semantically wrong.

Fix: plan now (a) explicitly prohibits `_select_product_essence_values()` from core_risk paths (line 141), (b) specifies three neutral helpers that collect only `risk_characteristic_text.risk_characteristic_text` (lines 142–145), (c) specifies `_select_core_risk_values()` call chain to use only these neutral helpers with family-neutral return type (lines 148–151), and (d) directs product_essence refactoring to call same helpers while retaining existing ownership (line 152).

Code fact verified: `fund_disclosure_processor.py:3666–3698` confirms `_select_product_essence_values()` iterates `_PRODUCT_ESSENCE_LABELS` — the original coupling was real and the neutral helper extraction is the correct fix.

### F2 [HIGH] – Gate 名称与实现范围严重不匹配

**Status: CLOSED**

Fix: gate label changed to include `risk_characteristic_text` (line 5). Mandatory scope statement added at lines 8–9 naming all four deferred roles and stating "Complete core_risk.v1 source truth requires later independent gates."

### F3 [HIGH] – Deferred roles 在 direct extraction 路径中无公开缺口语义

**Status: CLOSED**

Fix: plan lines 77–82 specify `FundExtractionGap` per deferred role with `gap_code="deferred_role"` and `required=False` on accepted direct results. Line 157 mandates `_core_risk_source_truth_gaps()` must add these four gaps. Test matrix line 207–208 requires exactly four `required=False` deferred_role entries in proof-positive accepted case.

Pattern verified against existing code: `_investor_experience_source_truth_gaps()` at `fund_disclosure_processor.py:6380–6435` and `_product_essence_source_truth_gaps()` at lines 4213–4268 confirm the gap emission pattern the plan follows.

### F4 [MEDIUM] – Facade fallback 死代码激活未显式承认

**Status: CLOSED**

Fix: plan line 179 explicitly states "This slice is the first activation verification for the existing `data_extractor.py:742-754` core_risk.v1 -> risk_characteristic_text fallback path; before this work, the path is effectively dead code because core_risk.v1 cannot emit an accepted direct value."

Code fact verified: `data_extractor.py:742–754` confirms the fallback condition checks `risk_characteristic_text.extraction_mode == "missing"` and `core_risk.value.get("risk_characteristic_text")` — today `core_risk.v1` is always candidate-only/missing, so this path is indeed dead code.

### F5 [MEDIUM] – `_select_core_risk_values()` 未充分指定

**Status: CLOSED**

Fix: plan lines 148–151 now specify the full call chain: neutral helpers only, family-neutral return type, ambiguity mapping limited to `risk_characteristic_text.risk_characteristic_text`. No ambiguity about whether it calls `_select_product_essence_values()` (prohibited) or duplicates code (neutral helpers are shared).

### F6 [LOW] – 缺少 risk_characteristic_text 歧义路径的 core_risk 专项测试

**Status: CLOSED**

Fix: test matrix line 209 explicitly lists "proof-positive ambiguous risk-characteristic text" case with expected `status="missing"`, `gap_code="ambiguous_table_or_locator"`, `candidate_evidence=()`. This covers the core_risk-specific behavior where a single required subvalue being ambiguous drives overall missing status.

### F7 [LOW] – Forbidden files 遗漏 `docs/fund-analysis-template-draft.md`

**Status: CLOSED**

Fix: plan line 267 lists `docs/fund-analysis-template-draft.md` in forbidden files/modules.

## New Blocker Check

No new blockers found within the planning scope. Specifically:

- Neutral helper approach is correctly specified with concrete function names and return types.
- Validation matrix (line 234) includes `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k "product_essence"` as required command, addressing the shared-helper regression risk from the original review's Residual Risk #1.
- Binary `accepted | missing` status model is explicitly documented as deliberate single-subvalue design (line 62) with clear migration note for future multi-subvalue gates.
- Deferred-role gap semantics are contract-compatible: `required=False` means consumers can distinguish "intentionally incomplete" from "fully covered" without breaking admission.

## Residual Risks (carried from original review, unchanged)

1. Shared helper refactoring may regress product_essence `risk_characteristic_text` shape. Mitigation: validation matrix requires focused product_essence test pass.
2. Binary status model is deliberate simplification; future multi-subvalue gate must redesign `_core_risk_status()`.
3. Candidate-boundary deferred role evidence behavior confirmed as expected but should have explicit test coverage.

## Verdict

**PLAN_REREVIEW_PASS**

All seven original findings (F1–F7) are closed with direct plan text evidence and verified code facts. No new blockers introduced within the planning scope. Plan is ready for implementation gate.

## Stop Condition Status

This artifact is the only file written in this re-review gate. No plan, code, test, docs, control, or other file was edited.
