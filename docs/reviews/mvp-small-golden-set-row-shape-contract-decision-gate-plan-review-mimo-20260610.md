# MVP Small Golden Set Row-shape Contract Decision Gate Plan Review — AgentMiMo

## Gate

- Review target: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`
- Reviewer: AgentMiMo
- Date: 2026-06-10
- Role: independent adversarial plan review only; no file modifications

## Source Evidence Read

- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`
- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md` (prior version)
- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260609.md` (prior DS review)
- `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` (oracle)
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py` (lines 1–50)
- `fund_agent/fund/extractors/manager_ownership.py` (lines 1–50)
- `fund_agent/fund/extractors/holdings_share_change.py` (lines 1–80)
- `fund_agent/fund/data_extractor.py` (lines 135–185)

## Findings

### F1 — 006597 risk anchor specifies §2.2 only, but oracle anchor is dual-source §2.2 + §4.4.1

- **位置**: Contract 2 "Source Anchor Requirements" and "Expected Oracle Mapping" for 006597
- **问题类型**: 契约缺失
- **当前写法**: Contract 2 states "section: `§2.2 基金产品说明`" and "retained oracle `fields.risk.anchor`" as anchor requirements. The expected oracle mapping table for 006597 lists "债券型基金；较低预期风险和预期收益；操作中强调信用风险和流动性风险控制".
- **反例/失败场景**: The retained excerpt JSON for 006597 has anchor `"PDF p5 §2.2 and p21 §4.4.1"`. The phrase "操作中强调信用风险和流动性风险控制" originates from §4.4.1 (管理人报告), not §2.2. If the extractor only anchors to §2.2, it will find "债券型基金，属于较低预期风险和预期收益" but miss "严控组合信用风险和流动性风险". The test would then fail because the expected text includes the §4.4.1 content.
- **为什么有问题**: The contract's anchor requirement is narrower than the oracle's actual anchor. An implementation agent following the contract literally would anchor only to §2.2 and produce an incomplete result for 006597.
- **直接证据**: Oracle JSON line for 006597 risk: `"anchor": "PDF p5 §2.2 and p21 §4.4.1"`, `"excerpt": "债券型基金，属于较低预期风险和预期收益；严控组合信用风险和流动性风险"`. Contract 2 anchor requirement: "section: `§2.2 基金产品说明`".
- **影响**: Implementation agent builds extractor that only reads §2.2 for 006597 risk; test fails because expected text includes §4.4.1 content; agent wastes time debugging or, worse, modifies the expected text to fit the extractor.
- **建议改法和验证点**: Contract 2 anchor requirements should state: "primary section `§2.2 基金产品说明`; when the oracle anchor includes additional sections (e.g., §4.4.1 for 006597), the extractor must also consume those sections." Alternatively, add a per-fund anchor note in the expected oracle mapping table noting the dual-source case.
- **修复风险（低/中/高）**: 低
- **严重程度（中）**: Implementation will break on 006597 risk test if contract is followed literally.

---

### F2 — Plan drops explicit two-reviewer requirement from the 0609 plan

- **位置**: Removed "Review Plan" section; replaced with "Verdict Target" section
- **问题类型**: 最佳实践偏离
- **当前写法**: The 0610 plan has a "Verdict Target" section (lines 13–18) that says "This plan is verdict-ready for controller review if reviewers can confirm..." but does not explicitly require two independent reviewers before the gate can be accepted. The 0609 plan had a dedicated "Review Plan" section (lines 192–198) that stated: "Send this plan to AgentDS for independent plan review. Send this plan to AgentMiMo for independent plan review." and "Only after accepted checkpoint may controller open the first implementation/test gate."
- **反例/失败场景**: Controller receives the 0610 plan, sees only one review (e.g., AgentDS passes), and proceeds to open the first implementation gate. The single reviewer may have missed a material issue that a second independent reviewer would have caught.
- **为什么有问题**: The 0609 plan explicitly stated this gate is `heavy` because "these choices affect public extractor contracts, snapshot comparability, downstream score/golden semantics, and fail-closed correctness rules". The two-reviewer requirement was a safety mechanism for this heavy gate. Removing it weakens the gate's review discipline.
- **直接证据**: 0609 plan lines 192–198: "1. Send this plan to AgentDS for independent plan review. 2. Send this plan to AgentMiMo for independent plan review... 7. Only after accepted checkpoint may controller open the first implementation/test gate." 0610 plan has no equivalent section.
- **影响**: Gate could be accepted with insufficient review, increasing risk of contract design errors propagating into implementation.
- **建议改法和验证点**: Add a "Review Requirements" section to the 0610 plan stating: "This heavy gate requires two independent plan reviews (AgentDS and AgentMiMo) and a controller judgment before the first implementation/test gate may open."
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: Process discipline issue; current user prompt already asks for both reviews, but the plan itself should be self-contained.

---

### F3 — Manager contract `role_status` derivation ambiguity for 004194 departed manager

- **位置**: Contract 1 "Optional Fields" for `role_status`
- **问题类型**: 契约缺失
- **当前写法**: `role_status` is described as "enum-like derived helper such as `current` / `departed`, only if derived from explicit role or end date; not required for first test gate".
- **反例/失败场景**: The oracle for 004194 has a manager with `role: "基金经理（已离任）"` and `end_date: "2024-12-31"`. The role text itself contains the "已离任" marker. If the first test does not assert `role_status`, an implementation agent might derive it incorrectly (e.g., always returning `current`) and the error would not be caught until a later gate.
- **为什么有问题**: The 004194 case is the only multi-manager case with a departed manager. If `role_status` is not asserted in the first test, the implementation has no guardrail for this derivation. The plan says "not required for first test gate" but doesn't specify when it should be asserted.
- **直接证据**: Oracle 004194 manager: `{"name": "王平", "role": "基金经理（已离任）", "start_date": "2017-03-03", "end_date": "2024-12-31"}`. Contract 1 optional fields: "not required for first test gate".
- **影响**: Implementation agent may produce incorrect `role_status` for departed managers; error undetected until later gate.
- **建议改法和验证点**: For the first test gate, at minimum assert that `role` text is preserved exactly as `"基金经理（已离任）"` for 王平. This ensures the departed-manager semantics are testable even without `role_status`. Alternatively, add `role_status` to the required fields for the first test if the contract defines it.
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: The `role` text preservation already captures departed-manager semantics; `role_status` is a convenience field.

---

### F4 — Risk contract `special_risk_clauses` and `fund_type_risk_label` have no first-test assertion guidance

- **位置**: Contract 2 "Optional Fields" for `special_risk_clauses` and `fund_type_risk_label`
- **问题类型**: 切片过粗
- **当前写法**: Both fields are described as optional with derivation rules, but the "Expected Oracle Mapping" table only lists the full `risk_characteristic_text` string. The "Acceptance Matrix" for Risk says "Tests assert raw retained disclosure text or exact accepted characteristic clauses, anchors, and source sections" but doesn't specify whether optional fields should be asserted.
- **反例/失败场景**: An implementation agent adds `special_risk_clauses: ["港股通"]` for 004393, but the first test doesn't assert this field. Later, a different agent changes the extraction logic and the clause extraction breaks silently. Or: an agent adds `fund_type_risk_label: "混合型基金"` derived from the risk text, but the test doesn't verify this derivation, so it could be wrong for other funds.
- **为什么有问题**: The plan's "Acceptance Matrix" says tests should assert "exact accepted characteristic clauses" but doesn't enumerate which clauses are accepted for each fund. This leaves the optional fields' test coverage to implementation agent discretion.
- **直接证据**: Contract 2 optional fields: `special_risk_clauses` example "港股通、信用风险、流动性风险、汇率风险"; `fund_type_risk_label` example "混合型基金". Acceptance Matrix: "Tests assert raw retained disclosure text or exact accepted characteristic clauses".
- **建议改法和验证点**: Add a per-fund expected optional field table to Contract 2, or explicitly state: "First test gate asserts only `risk_characteristic_text`, `source_anchor`, and `schema_version`. Optional fields are not asserted in the first test gate." This removes ambiguity.
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: Optional fields are correctly marked as optional; the main risk is implementation agent confusion about test scope.

---

### F5 — Bond holding contract `rank` field has no oracle value; test assertion guidance unclear

- **位置**: Contract 3 "Required Fields" for `rank`
- **问题类型**: 契约缺失
- **当前写法**: `rank` is listed as a required field: "integer or string if disclosed; first test may assert rank `1` only if table exposes it". But the oracle data for 006597 `top_bond_table_row` has keys `code`, `name`, `fair_value_cny`, `net_asset_ratio` — no `rank`.
- **反例/失败场景**: An implementation agent includes `rank: 1` in the bond holding row because the contract lists it as required. But the oracle doesn't have a `rank` value, so the test cannot assert it. The agent might skip the test assertion for `rank`, creating an untested field, or fabricate a rank value that doesn't match the actual table.
- **为什么有问题**: The contract says `rank` is required but the oracle doesn't provide it. This creates a conflict: the implementation must produce `rank` but the test cannot verify it from the oracle.
- **直接证据**: Contract 3 required fields: `rank: integer or string if disclosed; first test may assert rank 1 only if table exposes it`. Oracle `006597` `top_bond_table_row`: `{code, name, fair_value_cny, net_asset_ratio}` — no `rank` key.
- **建议改法和验证点**: Move `rank` to optional fields with explicit guidance: "`rank`: integer or string, only if the bond table explicitly discloses row order. First test does not assert `rank` because the retained oracle does not include it."
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: The plan already says "first test may assert rank 1 only if table exposes it", which implicitly handles this, but making it explicit in optional fields removes ambiguity.

---

### F6 — `StructuredFundDataBundle` wiring scope not bounded for four additive contracts

- **位置**: "Later Additive Extractor Fix Gate" allowed files for `fund_agent/fund/data_extractor.py`
- **问题类型**: 过度耦合
- **当前写法**: `fund_agent/fund/data_extractor.py` is allowed "only if the additive field must be surfaced through `StructuredFundDataBundle`". The bundle currently has 18 fields (lines 165–183 of data_extractor.py). If all four new contracts need bundle wiring, the bundle would grow to 22+ fields.
- **反例/失败场景**: An implementation agent adds all four new fields to `StructuredFundDataBundle` in a single gate, creating a large change that touches the bundle, the extract method, and all downstream consumers. This violates the plan's "each contract can change public extractor schema semantics and must remain reviewable" principle.
- **为什么有问题**: The plan's sequencing says "Do not combine all four implementation fixes in one slice; each contract can change public extractor schema semantics and must remain reviewable." But the bundle wiring constraint doesn't enforce this — an agent could add all four fields to the bundle in one pass.
- **直接证据**: Plan line 340: "Do not combine all four implementation fixes in one slice". Plan line 310: `fund_agent/fund/data_extractor.py` allowed "only if the additive field must be surfaced through `StructuredFundDataBundle`". `StructuredFundDataBundle` (data_extractor.py:140) currently has 18 fields.
- **建议改法和验证点**: Add a stop condition to the Later Additive Extractor Fix Gate: "Do not add more than one additive contract's fields to `StructuredFundDataBundle` per implementation slice. Each bundle wiring change must be reviewed independently."
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: The sequencing guidance already exists; this is a strengthening of an existing boundary.

---

### F7 — Plan removes "Residual Owners" and "Blocking Questions For Controller" from 0609 plan

- **位置**: Removed sections from 0609 plan
- **问题类型**: 最佳实践偏离
- **当前写法**: The 0610 plan has no "Residual Owners" table (0609 plan lines 202–209) and no "Blocking Questions For Controller" section (0609 plan line 213). The 0610 plan's "Explicit Non-goals" section (lines 372–386) is comprehensive but doesn't track residual ownership.
- **反例/失败场景**: After the first implementation slice, a residual (e.g., risk-characteristic text normalization) is unclear about who owns the next step. Without explicit residual owners, the controller may not know who to assign the follow-up gate to.
- **为什么有问题**: The 0609 plan's residual owners table explicitly mapped each residual to a gate owner and destination. This is valuable for gate handoff clarity. The 0610 plan's "Implementation Sequencing" section (lines 326–340) describes the order but not the ownership.
- **直接证据**: 0609 plan lines 202–209: residual owners table with explicit owner and destination for each residual. 0610 plan has no equivalent.
- **建议改法和验证点**: Add a "Residual Owners" table to the 0610 plan, or explicitly state that residual ownership is determined by the controller at gate open time.
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: The sequencing section provides implicit ownership; this is a clarity improvement.

---

## Open Questions

1. **Should the first test gate assert `end_date` for 004194's departed manager?** The plan says `end_date` is optional, but the oracle has it. If the first test doesn't assert `end_date`, the departed-manager semantics are only partially tested (via `role` text). Recommendation: assert `end_date` for 004194 in the first test gate since the oracle provides it.

2. **Should the risk contract explicitly enumerate which funds have dual-source anchors (§2.2 + §4.4.1)?** Currently only 006597 has this. Recommendation: yes, to prevent implementation agents from assuming all risk text comes from §2.2 only.

## Residual Risks

| Risk | Severity | Tracking Destination |
|---|---|---|
| 006597 risk dual-source anchor may cause extractor to miss §4.4.1 content | Medium | Implementation gate for `risk_characteristic_text.v1` |
| `StructuredFundDataBundle` growth from four additive contracts | Low | Implementation gates for each contract |
| Risk text normalization strategy (exact match vs. clause extraction) deferred to implementation | Low | Contract review gate (Slice A equivalent) |

## Self-Check

- [x] Reviewed target and scope clearly stated
- [x] Source of truth identified (retained excerpt JSON, current extractor surfaces, oracle anchors)
- [x] Findings are evidence-based, adversarial, and actionable
- [x] Open questions separated from findings
- [x] Residual risks separated from findings with tracking destinations
- [x] Conclusion is `pass`, `pass-with-risks`, or `fail`
- [x] Output path uses system-clock timestamp and matches artifact path format

## Verdict: PASS_WITH_FINDINGS

7 findings, 0 blockers.

F1 (006597 risk dual-source anchor) is the most material finding — it will cause the 006597 risk test to fail if the contract is followed literally. All other findings are process/clarity improvements that do not block plan acceptance.

**Acceptance recommendation**: Fix F1 before controller judgment. F2–F7 are optional enhancements that can be addressed in the controller judgment or the first implementation gate.
