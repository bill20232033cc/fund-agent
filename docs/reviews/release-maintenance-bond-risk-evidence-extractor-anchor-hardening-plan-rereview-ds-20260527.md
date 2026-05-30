# Bond Risk Evidence Extractor / Anchor Hardening — Plan Re-Review

> Date: 2026-05-27
> Reviewer: AgentDS
> Gate: plan re-review for `bond risk evidence extractor / anchor hardening design gate`
> Source review: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-ds-20260527.md`
> Fix artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-fix-20260527.md`
> Updated plan: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
> Scope: re-review DS 01, DS 02, DS 03 only

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: re-review worker only, not controller, not planning fix worker.
- Scope confirmed: DS 01, DS 02, DS 03 only. No new findings search.
- Source evidence read: fix artifact, updated plan (full), original DS review.

### Before Completion

- Self-check: pass
- All three findings re-reviewed against updated plan text with line-number evidence.
- No scope drift or new material choices detected.

---

## Finding Status

### DS 01: `bond_risk_evidence` Field Priority — 已修复

Original finding: plan 未在 `FIELD_PRIORITY_BY_NAME` 中注册 `bond_risk_evidence`，未定义 coverage/traceability 语义。

Fix evidence (updated plan):

| Claim | Plan evidence |
|-------|--------------|
| 注册为 P1 | Line 391: "Register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1`"; Line 561: "Add `bond_risk_evidence` to `FIELD_PRIORITY_BY_NAME` as `P1`" |
| Coverage 语义 | Line 392: "`value_present=True` means `contract_status != \"missing\"`"; Line 580: "`value_present` is derived from `contract_status != \"missing\"`" |
| Traceability 语义 | Line 393: "`anchor_present=True` requires at least one stable group-level anchor resolving to annual-report evidence"; Line 581: identical |
| P1 denominator | Line 579: "New field does enter P1 coverage/traceability denominators" |
| 完整路径断言 | Line 394: "100% P1 coverage and 100% P1 traceability"; Line 731: manual assertion for complete `006597` |

Fix is complete: P1 注册、coverage/traceability 语义、P1 denominator 纳入、100% 断言、slice-level 和 plan-level 双重记录。无遗漏。

### DS 02: Non-Bond Extraction Boundary — 已修复

Original finding: extractor 签名缺少 fund type gating，非债券基金可能不必要地遍历 section/table。

Fix evidence (updated plan):

| Claim | Plan evidence |
|-------|--------------|
| 显式参数 | Line 477: `extract_bond_risk_evidence(report: ParsedAnnualReport, classified_fund_type: str \| None)` |
| early return | Line 426: "For non-`bond_fund`, it returns a missing/not-applicable field immediately and must not scan seven bond evidence groups" |
| 不扫描七组 | Lines 491-496: Non-bond boundary section; "return a missing/not-applicable `ExtractedField` without scanning report sections/tables" |
| fail-closed | Line 496: "Unknown or absent `classified_fund_type` must not be treated as bond evidence; it should fail closed to missing/not-applicable" |
| 无 extra_payload | Line 495: "do not add hidden state to `extra_payload`" |
| 测试覆盖 | Line 513: "Non-bond `classified_fund_type` returns missing/not-applicable and does not invoke the seven group extractors"; Line 544: bundle integration test |
| Stop condition | Line 518: stop if fund type unavailable at boundary; Line 549: stop if classified fund type unavailable |

Fix is complete: 显式参数传入、非债券 early return、不扫描七组、未知类型 fail-closed、无 extra_payload、测试和 stop condition 全覆盖。无遗漏。

### DS 03: Required vs Missing Evidence Groups Invariant — 已修复

Original finding: `required_evidence_groups` 是契约级不变量（始终全七组）、`missing_evidence_groups` 是实例级动态值（仅未满足组），这个不变性应显式声明。

Fix evidence (updated plan):

| Claim | Plan evidence |
|-------|--------------|
| 不变性声明 (plan level) | Line 413: "`required_evidence_groups` is a contract-level invariant and must always equal all seven `BOND_RISK_EVIDENCE_GROUPS` ids" |
| 动态性声明 (plan level) | Line 414: "`missing_evidence_groups` is instance-level dynamic state and must contain only currently unsatisfied group ids" |
| 禁止缩减 | Line 415: "Do not shrink `required_evidence_groups` to match `missing_evidence_groups`" |
| Slice 5 invariants | Line 621: "`required_evidence_groups` is always the full ordered set of seven"; Line 622: "`missing_evidence_groups` is dynamic" |
| Slice 5 测试 | Line 632: "Partial issue keeps `required_evidence_groups` at all seven group ids while `missing_evidence_groups` lists only unsatisfied ids" |
| Behavior 描述 | Line 702: step 7 — emits issue 时保持 required 全七组、missing 仅未满足子集 |
| Manual assertion | Line 734: "Any partial issue must keep `required_evidence_groups` equal to all seven ids while `missing_evidence_groups` lists only unsatisfied ids" |

Fix is complete: plan 级别声明、Slice 5 invariants、测试用例、行为描述、manual assertion 均包含该不变性。无遗漏。

---

## Scope Drift Check

对比原 plan 与更新后 plan，所有变更均直接针对三条 finding：

- 新增内容限于：P1 注册与语义 (DS 01)、non-bond boundary 段落 (DS 02)、required/missing 不变性声明 (DS 03)
- 未发现新的 material choices、goal expansion、或 scope creep
- 未修改架构边界、七组决策、implementation slices ordering、out-of-scope 声明
- 未引入新的 blocking questions

---

## Conclusion

三条 finding 全部 **已修复**。Plan 保持 code-generation-ready 状态。无新增 blocking findings。

| Finding | Status |
|---------|--------|
| DS 01: field priority registration | 已修复 |
| DS 02: non-bond extraction boundary | 已修复 |
| DS 03: required vs missing invariant | 已修复 |
