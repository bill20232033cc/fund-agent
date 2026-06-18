# Fund Processor/Extractor S2 DataExtractor Integration Plan Review — AgentMiMo

> Date: 2026-06-18
> Reviewer: AgentMiMo independent adversarial plan reviewer
> Plan artifact: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md`
> Review type: plan review gate; read-only; no code implementation

## Verdict

**PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY**

S2 plan is broadly code-generation-ready with two blocking ambiguities that require clarification before implementation gate, plus several nonblocking findings. The plan preserves FundDocumentRepository boundary, maintains fail-closed semantics for active fund processor path, explicitly residualizes non-active fund path, and provides sufficient test requirements. Blocking items are: (1) `core_risk.v1` fallback projection rules for fields beyond `risk_characteristic_text` are under-specified, and (2) processor `extract()` unexpected exception propagation contract is not explicit.

---

## Mandatory Review Questions

### Q1: FundDocumentRepository Boundary Preservation

**Verdict: PASS**

Evidence:
- Plan §Scope (line 19): "保持 `FundDocumentRepository` 仍是年报访问唯一入口"
- Plan §Non-goals (line 29): "不让 Service/UI/Host/renderer/quality gate/LLM prompt/模板直接消费 Docling、pdfplumber full JSON、EID HTML render、PDF cache 或 parser helper"
- Plan §Required Implementation Shape (line 57): "`FundDataExtractor` 仍通过 `FundDocumentRepository.load_annual_report()` 获得 `ParsedAnnualReport`"
- Plan §Exact Write Set (lines 163-190): Forbidden write set explicitly blocks `documents/repository.py`, `documents/sources/**`, `service/**`, `host/**`, `agent/**`, `render/**`, `quality/**`

The plan correctly maintains the repository boundary. No new direct parser/candidate consumption paths are introduced.

### Q2: Active Fund Integration Through FundProcessorRegistry — No Silent Fallback

**Verdict: PASS with nonblocking note**

Evidence:
- Plan §Active Fund Processor Path (line 86): "用 registry `resolve()` 获取 processor；unsupported 必须作为实现缺陷或 typed fail-closed exception 暴露，不能静默回到 direct path"
- Plan §Active Fund Processor Path (line 89): "若 result 为 `unsupported` 或 `blocked`，S2 必须 fail closed；不得返回 direct extractor bundle"
- Plan §Fail-closed Rules (line 155): "active fund registry unsupported、processor blocked、input type mismatch、unsafe source provenance：fail closed，不走 legacy direct path"

The plan correctly requires fail-closed behavior for active fund processor path. The `UnsupportedFundProcessorError` in registry (registry.py:17) and `_blocked_result` in active_annual.py already implement the fail-closed contract.

Nonblocking note: The plan does not explicitly specify what happens when `_classified_fund_type()` returns `None` for a report whose `basic_identity.value` is not `None` but `classified_fund_type` key is absent or has an unrecognized value. Current code (data_extractor.py:452-458) returns `None` in that case, which would correctly fall through to the direct path. This is correct behavior but should be noted as an implicit residual.

### Q3: Bootstrap Classification Strategy

**Verdict: PASS (accepted-risk candidate)**

Evidence:
- Plan §First-principles Decision (line 57): "`FundDataExtractor` 先用当前 `extract_profile()` 做基金类型 bootstrap；这是 S2 的临时分类桥，不是新字段来源策略"
- Plan §Residuals (line 163): "Active path temporarily duplicates in-memory profile extraction for classification and processor extraction"

The plan explicitly acknowledges the bootstrap extraction duplication as a short-term residual. The rationale (line 63) is sound: "重复只发生在已加载的 in-memory `ParsedAnnualReport` 上，不重复 source/PDF/cache/network/provider/LLM 访问；后续可由 S3 precomputed extraction context 或 profile-classifier processor gate 消除."

This is an accepted-risk candidate, not a blocking issue.

### Q4: Bundle Projection Detail Sufficiency

**Verdict: BLOCKING — `core_risk.v1` fallback projection rules incomplete**

Evidence:
- Plan §Bundle Projection Rules (lines 100-133): Provides projection rules for all six field families
- `product_essence.v1` (line 103): `basic_identity`, `product_profile`, `benchmark`, `risk_characteristic_text` — sufficient
- `return_attribution.v1` (line 108): `fee_schedule`, `nav_benchmark_performance`, `tracking_error` with `_tracking_error_for_fund_type()` — sufficient
- `manager_profile.v1` (line 112): `portfolio_managers`, `turnover_rate`, `manager_alignment`, `manager_strategy_text`, `holdings_snapshot` — sufficient
- `investor_experience.v1` (line 117): `investor_return`, `holder_structure`, `share_change` — sufficient
- `core_risk.v1` (line 122): **ONLY specifies `risk_characteristic_text` fallback** — BLOCKING
- `index_profile` (line 124): from bootstrap `profile_result.index_profile` — sufficient
- `bond_risk_evidence` (line 126): continue calling `extract_bond_risk_evidence()` — sufficient

**Blocking detail**: The `active_annual.py` processor maps `core_risk.v1` to 5 fields: `risk_characteristic_text`, `holder_structure`, `turnover_rate`, `holdings_snapshot`, `tracking_error` (active_annual.py:170-189). The plan's bundle projection rule for `core_risk.v1` (line 122) only says:

> `core_risk.v1`: 可作为 `risk_characteristic_text` fallback only if `product_essence.v1` lacks that field and core_risk has a public value; otherwise do not merge multiple family values implicitly.

This leaves the other 4 `core_risk.v1` fields (`holder_structure`, `turnover_rate`, `holdings_snapshot`, `tracking_error`) without explicit projection rules. The implementation worker must know:
1. Should these fields be used as fallbacks for their corresponding bundle fields when the primary family (e.g., `manager_profile.v1` for `turnover_rate`) lacks the value?
2. Or should they be ignored entirely since the primary families already provide these fields?

**Recommended fix**: Add explicit projection rules for all `core_risk.v1` fields, or explicitly state that only `risk_characteristic_text` from `core_risk.v1` has fallback semantics and the other fields are informational-only within the family.

### Q5: Boundary Preservation

**Verdict: PASS**

| Boundary | Status | Evidence |
|----------|--------|----------|
| Non-active fund behavior | Preserved | Plan §Non-active Fund Path (lines 137-151): explicit residual path for `index_fund`, `enhanced_index`, `bond_fund`, `qdii_fund`, `fof_fund`, unclassified |
| NAV degradation | Preserved | Plan §Fail-closed Rules (line 157): "NAV provider failure：保持当前 `nav_unavailable` 降级" |
| Repository failure propagation | Preserved | Plan §Fail-closed Rules (line 156): "repository failure：保持向上抛出，不被 NAV 或 processor 捕获吞掉" |
| Bond risk evidence | Preserved | Plan §Bundle Projection Rules (line 126): "对 active fund 继续调用 `extract_bond_risk_evidence()`，应返回 `not_applicable_non_bond_fund`" |
| Source provenance | Preserved | Plan §Active Fund Processor Path (line 87): "传入 `report` 与 `project_public_source_provenance(report.metadata.source)`" |
| NOT_READY | Preserved | Plan §Non-goals (line 28): explicit NOT_READY boundary |
| Candidate-only | Preserved | Plan §Fail-closed Rules (line 159): "candidate intermediate：S2 不构造、不接收、不消费" |
| No parser replacement | Preserved | Plan §Non-goals (line 27): "不替换生产 parser" |

### Q6: Exact Write Set Sufficiency

**Verdict: PASS**

Allowed:
- `fund_agent/fund/data_extractor.py` — primary implementation target
- `tests/fund/test_data_extractor.py` — primary test target
- `fund_agent/fund/README.md` (conditional) — only if behavior change needs documentation
- `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md` — implementation evidence

Forbidden: Explicitly listed (lines 175-190), covering all sensitive paths.

The write set is sufficient for the planned scope and not too broad.

### Q7: Required Tests Sufficiency

**Verdict: PASS with nonblocking gap**

Required tests (lines 196-211):
1. Active fund uses processor registry path and returns same public bundle fields — **sufficient**
2. Custom registry unsupported active fund fails closed — **sufficient**
3. NAV provider failure still degrades — **sufficient**
4. Repository failure still propagates, NAV not called — **sufficient**
5. Non-bond active fund doesn't scan bond evidence groups — **sufficient**
6. Bond fund path remains current direct branch with typed NAV drawdown — **sufficient**
7. Source provenance still projects — **sufficient**

Nonblocking gap: No explicit test for the case where `_classified_fund_type()` returns `None` (unclassified fund) to verify it correctly falls through to the direct legacy path. However, the existing code logic (data_extractor.py:305) already handles this correctly — when `classified_fund_type` is not `"active_fund"`, the code follows the direct path. This is implicit but correct.

### Q8: Blocking Ambiguity, Overreach, Missing Evidence, Under-specified Projection Rules

**Blocking findings:**

**F1 (blocking)**: `core_risk.v1` fallback projection rules for non-`risk_characteristic_text` fields are under-specified.
- Evidence: Plan line 122, active_annual.py lines 170-189
- Impact: Implementation worker cannot determine whether `holder_structure`, `turnover_rate`, `holdings_snapshot`, `tracking_error` from `core_risk.v1` should be used as fallbacks when primary families lack values
- Fix: Add explicit projection rules for all 5 `core_risk.v1` fields

**F2 (blocking)**: Processor `extract()` unexpected exception propagation contract is not explicit.
- Evidence: Plan §Fail-closed Rules (lines 155-159) covers `unsupported`, `blocked`, `input type mismatch`, `unsafe source provenance`, but does not specify behavior when `processor.extract()` raises an unexpected exception (e.g., `TypeError`, `KeyError`, `AttributeError`)
- Impact: Implementation worker must decide whether to catch all exceptions and fail-closed, or let them propagate
- Fix: Add explicit rule: "processor.extract() 意外异常必须向上抛出或转换为 fail-closed result；不得静默吞掉或 fallback 到 direct path"

**Nonblocking findings:**

**F3 (nonblocking)**: `current_stage.v1` family-to-bundle projection is implicit.
- Evidence: Plan lines 100-133 define projection rules for other families but not `current_stage.v1`; the active_annual processor maps `current_stage.v1` to `basic_identity`, `share_change`, `holdings_snapshot`, `portfolio_managers` (active_annual.py:156-169)
- Impact: These fields are already populated from primary families (`product_essence.v1`, `investor_experience.v1`, `manager_profile.v1`), so `current_stage.v1` values are redundant for bundle construction
- Fix: Add note that `current_stage.v1` fields are already covered by primary families and do not need separate bundle projection

**F4 (nonblocking)**: `_classified_fund_type()` returning `None` for active fund with missing/invalid classification is an implicit residual.
- Evidence: data_extractor.py:448-459; plan does not explicitly discuss this case
- Impact: Correct behavior (falls through to direct path) but should be noted
- Fix: Add to residuals section or test requirements

**F5 (nonblocking)**: `source_kind` field in `FundProcessorDispatchKey` derivation from `project_public_source_provenance()` result is not fully specified.
- Evidence: Plan line 86: `source_kind=<public source kind>`; `project_public_source_provenance()` returns `PublicSourceProvenance` object, not a string
- Impact: Implementation worker must determine which field of `PublicSourceProvenance` to use as `source_kind` (likely `resolved_source_name` or a derived string)
- Fix: Specify the exact field or derivation rule for `source_kind`

---

## Residual Risk

| Risk | Severity | Owner | Mitigation |
|------|----------|-------|------------|
| `core_risk.v1` non-`risk_characteristic_text` fields lack projection rules | blocking | Plan author | Clarify projection rules before implementation gate |
| Processor unexpected exception propagation not specified | blocking | Plan author | Add explicit fail-closed rule for unexpected exceptions |
| `current_stage.v1` bundle projection implicit | nonblocking | Implementation worker | Primary families already cover these fields |
| Unclassified fund type fallthrough implicit | nonblocking | Implementation worker | Current code logic handles correctly |
| `source_kind` derivation from `PublicSourceProvenance` | nonblocking | Implementation worker | Likely `resolved_source_name` or static string |
| Bootstrap profile extraction duplication | accepted-risk | S3 planning | In-memory only; no I/O duplication |
| `index_profile` still from bootstrap extraction | residual | S3 planning | Explicitly documented |
| Non-active fund processors not implemented | residual | Future gates | Explicitly documented |

---

## Review Scope Statement

This review did not implement code. This review did not modify source files, tests, control docs, or design docs. This review did not claim readiness for production, golden promotion, or release. Verdict is `PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY`.

---

## Artifact Path

`docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-review-mimo-20260618.md`
