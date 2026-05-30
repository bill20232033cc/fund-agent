# Plan Re-Review: MVP Gate 2 chapter_writer + chapter_auditor

日期：2026-05-30
角色：AgentMiMo — independent re-reviewer
Gate：`MVP Gate 2: chapter_writer + chapter_auditor plan gate`

## Reviewed Target

Updated plan: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`

## Prior Reviews

| Reviewer | Artifact | Verdict |
|----------|----------|---------|
| MiMo | `mvp-gate2-chapter-writer-auditor-plan-review-mimo-20260530.md` | PASS_WITH_NON_BLOCKING |
| DS | `mvp-gate2-chapter-writer-auditor-plan-review-ds-20260530.md` | PASS_WITH_NON_BLOCKING |
| GLM | `mvp-gate2-chapter-writer-auditor-plan-review-glm-20260530.md` | PASS_WITH_NON_BLOCKING |

## Re-Review Scope

Verify that all findings from MiMo (5), DS (7), and GLM (4) reviews are resolved or properly deferred in the updated plan. Specifically verify: writer anchor/missing parsing, LLM audit line format, prompt_only stop reason, chapter 5 detection, evidence_missing critical algorithm, repair_hint aggregation, non_asserted_facets audit, E2 deferral, bond_risk_evidence messaging, and controller-only control-doc updates.

## Finding Disposition Verification

### MiMo-01 (MEDIUM) — Writer anchor ref parsing 未冻结

**Verdict: RESOLVED**

§7.5 now defines a complete parsing contract:
- Anchor marker: `<!-- anchor:<anchor_id> -->`, regex `<!-- anchor:([^<>\s]+) -->`
- Case sensitive; `<!--anchor:...-->`, `<!-- anchor: ... -->`, `<!-- ANCHOR:... -->` all invalid
- Unknown anchor id or invalid marker → blocked, `stop_reason="llm_contract_violation"`
- `used_anchor_ids` deterministic dedupe by first-occurrence order
- `max_output_chars` hard post-check: `len(response.text)`, over → blocked, no truncation
- bond_risk_evidence special error message included (§7.5 last bullet)

### MiMo-02 (MEDIUM) — LLM audit 输出解析未冻结

**Verdict: RESOLVED**

§8.4 now defines a fixed protocol:
- `audit_focus` defaults: `evidence_support`, `must_not_cover_boundary`, `missing_semantics`, `readability`, `non_asserted_facet_boundary`
- Line format: `SEVERITY|LOCATION|MESSAGE`, SEVERITY ∈ {BLOCKING, REVIEWABLE, INFO, PASS}
- Parse failure → blocked, single issue `rule_code="C1"`, `severity="blocking"`, `repair_hint="regenerate"`, no silent pass
- `PASS|chapter|no issues` = LLM pass; empty raw_text still blocked
- Informational-only → pass; REVIEWABLE → fail/patch; BLOCKING → fail/regenerate

### MiMo-03 (LOW) — prompt_only stop_reason 歧义

**Verdict: RESOLVED**

§7.1 adds `"prompt_only"` to `ChapterWriteStopReason` closed set (now 10 values). §7.4 point 6 fixes `stop_reason="prompt_only"` instead of "由实现选一".

### MiMo-04 (LOW) — Slice 4 docs 范围

**Verdict: RESOLVED**

§6 adds explicit statement: control-doc updates belong to controller closeout, not implementation slices. §12 Slice 4 stop condition: "如果需要更新 `docs/design.md`...停止交回 controller". §15 separates implementation-worker docs (README only) from controller-only docs (design/startup/control).

### MiMo-05 (INFO) — value serialization

**Verdict: ACCEPTED RESIDUAL**

§17 retains as residual. No plan change needed; implementation evidence must record strategy.

### DS-01 (HIGH) — evidence_missing critical judgment 算法缺失

**Verdict: RESOLVED**

§7.4 point 5 defines `_fact_supports_critical_judgment(fact) -> bool`:
- `required_by` contains `CHAPTER_CONTRACT.` → critical
- `required_by` contains `ITEM_RULE.` → critical
- `source_field_id` ∈ numeric/evidence-strong set (11 fields including nav_benchmark_performance, fee_schedule, turnover_rate, etc.) → critical
- `value` is `int`/`float`/`Decimal`, or dict/list/tuple containing numeric leaf → critical
- Only decides evidence_missing fail-closed; does not open repository/source

### DS-02 (MEDIUM) — declared_missing_reasons 提取机制缺失

**Verdict: RESOLVED**

§7.5 defines missing marker:
- Format: `<!-- missing:<reason> -->`, regex `<!-- missing:([a-z_]+) -->`
- `reason` must be in `ChapterFactMissingReason` closed set AND in `ChapterFactInput.missing_reasons`
- Invalid reason or reason not in chapter missing_reasons → blocked, `stop_reason="llm_contract_violation"`
- `declared_missing_reasons` deterministic dedupe by first-occurrence order
- No marker → `declared_missing_reasons=()`; Gate 2 does not infer from free text

### DS-03 (MEDIUM) — repair_hint 聚合规则缺失

**Verdict: RESOLVED**

§9 汇总规则 now specifies:
- Priority: `needs_more_facts` > `regenerate` > `patch` > `none`
- No issues → `none`
- `status="blocked"` without more specific hint → default `regenerate`
- Missing facts / missing semantics → default `needs_more_facts`

### DS-04 (MEDIUM) — non_asserted_facets 误用未审计

**Verdict: RESOLVED**

§9 adds C2 non_asserted_facets deterministic check:
- If candidate facet string appears in text AND no negation qualifier within 12 Chinese characters (词表: 未断言, 未确认, 候选, 可能, 不可据此判断, 不能据此判断, 仅为 lens 候选) → fail
- `facets=()` AND text contains 属于/是/为/定位为 + candidate facet → blocking
- Writer prompt requires "（未断言）" or equivalent qualifier

### DS-05 (LOW) — E2 缺席需显式 deferred

**Verdict: RESOLVED**

§9 explicitly states: "E2（证据与断言不匹配）需要重新对照年报原文...超出 Gate 2 边界；本 gate 只做 E1/E3 与 LLM semantic support，E2 source verification 显式 deferred 到后续 Evidence Confirm gate"。§17 residual risks also references E2.

### DS-06 (LOW) — bond_risk_evidence 锚点错误消息

**Verdict: RESOLVED**

§7.5 adds: "若 unknown anchor id 疑似来自 `bond_risk_evidence.value.anchors` 内部 ref，issue message 必须写明：`bond_risk_evidence 组级锚点未展开为 ChapterEvidenceAnchor，需后续 conversion helper 后才能引用`"。§10 also adds the same requirement for auditor side.

### DS-07 (INFO) — MiMo findings confirmation

**Verdict: INFORMATIONAL**

All MiMo findings independently confirmed as valid. Disposition verified above.

### GLM-F1 (MEDIUM) — prompt_only stop_reason

**Verdict: RESOLVED** (same as MiMo-03)

§7.1 adds `"prompt_only"` literal. §7.4 point 6 fixes `stop_reason="prompt_only"`.

### GLM-F2 (MEDIUM) — Chapter 5 cross-period 检测欠规格

**Verdict: RESOLVED**

§9 adds detailed chapter 5 cross-period detection:
- Assertion phrase 初始集合: 风格稳定, 风格保持稳定, 风格一致, 风格延续, 言行一致, 投资框架稳定, 没有明显变化, 变化不大, 持续改善, 明显漂移, 发生转型, 阶段切换, 相比上一期, 过去一年变化 (14 phrases)
- Negation/gap prefix 初始集合: 不判断, 不能判断, 无法判断, 不足以判断, 不能据此判断, 证据不足, 数据不足, 缺少跨期, 未披露上期 (9 prefixes)
- Detection: assertion phrase hit + no negation/gap prefix within 12 Chinese chars → fail, rule C2, repair_hint=needs_more_facts
- Question-form expressions (是否风格稳定, 能否判断风格稳定, 下一步验证风格是否稳定) explicitly allowed

### GLM-F3 (LOW) — Slice 4 allowed files 矛盾

**Verdict: RESOLVED** (same as MiMo-04)

Control docs moved to controller-only scope.

### GLM-F4 (LOW) — LLM audit 零 issue 通过条件

**Verdict: RESOLVED**

§9 汇总规则: "LLM 零 blocking/reviewable issue 且 programmatic pass 时，`ChapterAuditResult.status="pass"`，`accepted=True`"。§8.4: "`PASS|chapter|no issues` 或零 issue 等价于 LLM pass"。

---

## New Observations (Non-Finding)

The updated plan demonstrates strong systematic fix quality. The §4.1 "Review Finding Disposition" table provides complete traceability from each prior finding to its plan change. No new findings emerge from the re-review.

One minor note for implementation agent awareness (not a finding): chapter 5 assertion phrases include "明显漂移" but not standalone "风格漂移" or "漂移"。Implementation agent may choose to include these as additional phrases in `_audit_missing_semantics()`, but the current set is sufficient for the stated stop condition ("判断跨期风格/阶段变化为确定事实").

---

## Verdict

**PASS**

All 16 findings from three prior reviews (MiMo: 5, DS: 7, GLM: 4) are resolved, accepted as residual, or confirmed informational. The updated plan is code-generation-ready. No new findings.

## Reviewer Self-Check

- [x] Every finding from MiMo/DS/GLM reviews verified against updated plan
- [x] Each disposition confirmed with specific plan section references
- [x] No new BLOCKING or HIGH findings introduced
- [x] Verdict is PASS (no new blocking issues)
- [x] Output path uses system-clock timestamp
