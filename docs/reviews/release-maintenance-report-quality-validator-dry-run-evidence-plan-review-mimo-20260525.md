# Release Maintenance Report-Quality Validator Dry-Run Evidence Plan Review (MiMo)

> Date: 2026-05-25-142433
> Reviewed target: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`
> Gate: `report-quality validator dry-run evidence planning`
> Reviewer: AgentMiMo
> Truth sources: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md`, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md`

---

## 1. Reviewed Target and Scope

Plan artifact defines how to produce and review minimal dry-run evidence for the accepted `report_quality_validation.py` validator before integrating it into Service, CLI, renderer, FQ0-FQ6, durable baseline, or tracked reports. The plan is planning-only; no implementation is authorized until controller acceptance.

## 2. Assumptions Tested

| # | Assumption | Test result |
|---|-----------|-------------|
| A1 | Plan is strictly planning-only and future implementation only produces docs/reviews dry-run evidence | ✅ Confirmed. Section 1 scope, Section 8 allowed files, Section 10 stop conditions all enforce this. |
| A2 | Single-bundle JSONL scope is explicit and avoids multi-bundle aggregation | ✅ Confirmed in principle. Sections 2.4, 2.6, 4.1, 5.4, 7.1 all specify single-bundle constraint. See F1 for enforcement gap. |
| A3 | Input does not read PDF/cache/source helper/FundDocumentRepository, does not new fetch | ✅ Confirmed. Section 1 non-goal #3, Section 2 rejected inputs, Section 10 stop conditions. |
| A4 | Dry-run examples cover validator consumer contract | ✅ Confirmed. See detailed coverage matrix below. |
| A5 | Acceptance criteria do not overclaim product readiness | ✅ Confirmed. Section 5 explicitly distinguishes "consumable as contract" from "ready to wire into product flow". |
| A6 | Residuals are complete | ✅ Confirmed. See coverage matrix below. |
| A7 | Required validation boundary rg is reasonable | ✅ Confirmed. rg pattern targets forbidden source/import terms; plan acknowledges boundary-section mentions must be explicitly marked as non-goals. |

### Dry-Run Consumer Contract Coverage Matrix

| Contract dimension | Plan coverage | Evidence |
|---|---|---|
| Valid zero issue | ✅ Section 4 step 3 | `validate_report_quality_bundle(valid_bundle)` with zero-issue assertion |
| Fallback conflict | ✅ Section 4 step 5 | "fallback inconsistency to produce exactly one canonical `RQV_FALLBACK_CONFLICT`" |
| chapter_summary canonical / no duplicate N/A | ✅ Section 4 step 5 | "chapter_summary semantics without duplicate `RQV_NA_SEMANTICS`" |
| N/A semantics | ✅ Section 4 step 5 | "N/A semantics with missing na_reason / reviewer_note" |
| Link integrity | ✅ Section 4 step 5 | "link integrity, such as missing anchor or missing data gap refs" |
| scoring_ready precondition | ✅ Section 4 step 5 | Explicitly listed as blocking precondition failure |
| summary/error_code counts/run_id/schema_version/pointers | ✅ Section 4 steps 3-4 | Required fields listed for both valid-bundle and JSONL calls |

### Residual Coverage Matrix

| Residual | Plan coverage | Evidence |
|---|---|---|
| Multi-bundle | ✅ Section 7 #1 | Explicitly deferred; single-bundle only |
| unknown_upstream message | ✅ Section 7 #2 | Deferred per controller judgment |
| Non-scoring-ready chapter_summary/report_level | ✅ Section 7 #3-4 | Deferred; current stricter semantics preserved |
| nav_data | ✅ Section 7 #5 | Deferred |
| Derived calculations | ✅ Section 7 #6 | Deferred |
| Durable baseline | ✅ Section 7 #7 | Deferred |
| Host/Agent/dayu | ✅ Section 7 #8 | Deferred |
| Fallback recovery | ✅ Section 7 #9 | Deferred |
| FOF taxonomy | ✅ Section 7 #10 | Deferred |

---

## 3. Findings

### 001-未修复-低-single-bundle JSONL 约束缺少显式验证步骤

- **位置**: Section 4 "Dry-Run Verification Steps", step 2 `validate_report_quality_jsonl()` 调用
- **问题类型**: 契约缺失
- **当前写法**: Plan 要求 JSONL 文件"exactly one `record_type="bundle"` record"（Section 2.4, 2.6），但 Section 4 的验证步骤只要求记录 `summary.total_records` 和确认"the JSONL contains exactly one bundle record"，未要求实现 agent 在调用 validator 前或后用代码断言 bundle 计数为 1
- **反例/失败场景**: Implementation agent 构造 JSONL 时意外写入 2 个 bundle records，validator 会静默处理两个 bundle 并汇总结果（`validate_report_quality_jsonl` 遍历所有 bundle_records），dry-run 证据中人工确认"exactly one bundle"可能遗漏
- **为什么有问题**: Plan 的单 bundle 约束是核心设计决策（Section 7 #1 明确只验证 single-bundle），但缺少自动化验证手段；人工确认容易出错
- **直接证据**: `report_quality_validation.py:404-411` — `for line_number, bundle_record in bundle_records` 遍历所有 bundle，不检查数量；Plan Section 4 step 4 只要求"confirmation that the JSONL contains exactly one bundle record"
- **影响**: 低。Implementation agent 如果遵循 plan 会手动构造正确 JSONL，但缺少防御性检查
- **建议改法和验证点**: 在 Section 4 step 4 增加一条："`summary.total_records` minus score_issue count must equal 1 (proving exactly one bundle record)"，或要求实现 agent 在证据中记录 bundle record 行号并断言只有一个
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

---

## 4. Open Questions

无。Plan 在 scope、input selection、output artifact policy、verification steps、acceptance criteria、residuals、allowed files、stop conditions 和 implementation handoff 各方面均收敛。

---

## 5. Residual Risks and Suggested Tracking Destination

| Residual risk | Suggested tracking |
|---|---|
| Multi-bundle JSONL aggregation semantics | Next gate after dry-run evidence acceptance |
| unknown_upstream_failure_category exact message assertion | Future test-hardening pass per controller judgment |
| Non-scoring-ready chapter_summary blocking behavior | Future hardening gate if consumer needs relaxation |
| `nav_data` mapping into report facts | Future `nav_data` source-contract slice |
| Derived-calculation population beyond empty/synthetic | Future scoring-validation robustness gate |
| Durable baseline selection and curated fixture promotion | Future baseline-selection gate |
| Fallback upstream failure category recovery for `110020`, `017641`, `017970` | S1 entry gate residual |
| FOF taxonomy and QDII-FOF precedence | Fund-type taxonomy gate |

---

## 6. Reviewer Self-Check

- [x] Reviewed target, scope, source of truth, and assumptions tested are written
- [x] Findings are evidence-based, adversarial, actionable, and not style/nit/speculation
- [x] Open questions, residual risks, and tracking destinations are separate from findings
- [x] Conclusion is one of `pass`, `pass-with-risks`, `fail`
- [x] Output path uses system-clock timestamp and matches artifact path format

---

## 7. Conclusion

**PASS_WITH_FINDINGS**

The plan is well-structured, strictly planning-only, and correctly scopes the dry-run evidence gate. All requested review focus areas are addressed: single-bundle JSONL scope is explicit (one minor enforcement gap), input rejection is comprehensive, dry-run examples cover the full validator consumer contract, acceptance criteria do not overclaim, residuals are complete, and boundary validation is reasonable.

One minor finding: the single-bundle JSONL constraint lacks an automated verification step in the dry-run procedure. This does not block implementation acceptance — the constraint is clearly documented and an implementation agent following the plan will produce correct artifacts — but adding a bundle-count assertion to the evidence would make the single-bundle invariant self-proving.

No blocker or material findings. The plan is safe to advance to implementation upon controller acceptance.
