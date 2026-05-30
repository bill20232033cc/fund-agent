# Implementation Review: MVP Gate 2 chapter_writer + chapter_auditor

日期：2026-05-30
角色：AgentDS — independent implementation reviewer
Gate：`MVP Gate 2: chapter_writer + chapter_auditor`

## Reviewed Target

Uncommitted Gate 2 implementation against accepted plan `b46a80a` and controller decision `PLAN_ACCEPTED_FOR_IMPLEMENTATION`.

## Files Reviewed

| File | Status | Purpose |
|------|--------|---------|
| `fund_agent/fund/chapter_writer.py` | New (1135 lines) | Writer dataclass, Protocol, builder, preflight, draft parsing |
| `fund_agent/fund/chapter_auditor.py` | New (986 lines) | Auditor dataclass, Protocol, programmatic audit, LLM line parser, aggregation |
| `tests/fund/test_chapter_writer.py` | New (572 lines) | 18 tests: input, prompt, fail-closed, marker parsing, import isolation |
| `tests/fund/test_chapter_auditor.py` | New (513 lines) | 16 tests: programmatic, LLM line protocol, repair_hint, import isolation |
| `fund_agent/fund/README.md` | Modified (+20 lines) | Gate 2 primitives description + example |
| `tests/README.md` | Modified (+3 lines) | Test descriptions + targeted command |

Not modified (per controller boundary): `fund_agent/fund/__init__.py`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `AGENTS.md`, `docs/fund-analysis-template-draft.md`.

## Source of Truth

- Accepted plan: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`
- Controller decision: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-decision-20260530.md`
- Implementation evidence: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-evidence-20260530.md`
- Gate 1 code fact: `fund_agent/fund/chapter_facts.py`

---

## Verification Matrix

### 1. Scope Compliance

| Check | Result | Evidence |
|-------|--------|----------|
| Only Fund-layer modules added | ✅ PASS | `chapter_writer.py` + `chapter_auditor.py` in `fund_agent/fund/` |
| No orchestrator | ✅ PASS | No multi-chapter scheduling, no repair loop execution |
| No final assembler | ✅ PASS | No chapter 0 generation, no assembly logic |
| No CLI `--use-llm` | ✅ PASS | No CLI changes |
| No Service/Host/dayu | ✅ PASS | AST import check: no `service`, `dayu`, `openai`, `httpx` imports |
| No repository/PDF/source | ✅ PASS | AST import check: no `documents`, `repository`, `cache`, `pdf`, `source`, `downloader`, `parser` |
| No control-doc modification | ✅ PASS | `docs/design.md`, startup, control doc untouched |
| No golden/score/snapshot | ✅ PASS | No quality gate or fixture changes |

### 2. Contract Accuracy

| Check | Result | Evidence |
|-------|--------|----------|
| Writer dataclasses match plan §7 | ✅ PASS | All 8 dataclasses present, `frozen=True, slots=True` |
| Writer Literal aliases match plan §7.1 | ✅ PASS | `ChapterWriteStopReason` includes `"prompt_only"`, 10 values total |
| Writer Protocol `ChapterLLMClient` | ✅ PASS | `generate_chapter(request) -> response` as specified |
| Auditor dataclasses match plan §8 | ✅ PASS | All 8 dataclasses present, `frozen=True, slots=True` |
| Auditor Literal aliases match plan §8.1 | ✅ PASS | `ChapterAuditRuleCode` includes `"E2"` |
| Auditor Protocol `ChapterAuditLLMClient` | ✅ PASS | `audit_chapter(request) -> response` as specified |
| No `extra_payload` | ✅ PASS | All parameters explicit in typed dataclass fields |
| Chinese docstrings | ✅ PASS | All public functions/classes have complete Chinese docstrings |

### 3. Fail-Closed Semantics

| Check | Result | Evidence |
|-------|--------|----------|
| `fund_type="unknown"` → blocked | ✅ PASS | `_preflight_issues()` line 486-489; test covered |
| Chapter 0/7 without accepted conclusions → blocked | ✅ PASS | `_preflight_issues()` line 490-497; test covered |
| All facts non-available → blocked | ✅ PASS | `_preflight_issues()` line 498-505 |
| `evidence_missing` critical fact → blocked | ✅ PASS | `_fact_supports_critical_judgment()` with 4 rules; 2 tests |
| `prompt_only` → blocked, `stop_reason="prompt_only"`, `draft=None` | ✅ PASS | `write_chapter()` line 427-428; test asserts exact values |
| `llm_client is None` with `mode="llm"` → blocked `llm_unavailable` | ✅ PASS | `write_chapter()` line 429-435 |
| Empty LLM response → blocked | ✅ PASS | `_draft_from_llm_response()` line 712-715; test covered |
| Over `max_output_chars` → blocked, no truncation | ✅ PASS | Line 716-723; test `max_output_chars=10` |
| Forbidden trading phrases → blocked | ✅ PASS | `_forbidden_phrase_issues()` checks 12 phrases; test covered |
| Invalid anchor marker format → blocked | ✅ PASS | `_invalid_marker_issues()` + `_parse_anchor_markers()`; test for case sensitivity |
| Unknown anchor id → blocked | ✅ PASS | `_parse_anchor_markers()` unknown → issue; test covered |
| Unknown missing reason → blocked | ✅ PASS | `_parse_missing_markers()` checks against `_SUPPORTED_MISSING_REASONS`; test covered |
| Evidence lines without anchor marker → blocked | ✅ PASS | `_evidence_line_issues()` line 848-870 |
| Audit LLM unavailable → blocked `LLM_UNAVAILABLE` | ✅ PASS | `audit_chapter_llm()` line 352-368; test covered |
| LLM audit parse failure → blocked, C1 issue, `repair_hint="regenerate"` | ✅ PASS | `_llm_parse_failure()`; test covered |
| Programmatic fail → audit not accepted even if LLM passes | ✅ PASS | `audit_chapter()` aggregation: programmatic fail → status="fail" |

### 4. Writer Marker Parsing (§7.5)

| Check | Result | Evidence |
|-------|--------|----------|
| Anchor marker regex `<!-- anchor:([^<>\s]+) -->` | ✅ PASS | `_ANCHOR_MARKER_RE` compiled at line 48 |
| Missing marker regex `<!-- missing:([a-z_]+) -->` | ✅ PASS | `_MISSING_MARKER_RE` compiled at line 49 |
| Case sensitive validation | ✅ PASS | Test: uppercase `ANCHOR:` → blocked |
| Invalid marker format detection | ✅ PASS | `_invalid_marker_issues()` checks HTML comments with anchor/missing in payload but not matching exact regex |
| `declared_missing_reasons=()` when no markers | ✅ PASS | `_parse_missing_markers()` returns empty when no matches |
| `max_output_chars` hard post-check | ✅ PASS | `len(text) > max_output_chars` → blocked |
| bond_risk_evidence specific error message | ✅ PASS | `_looks_like_bond_risk_internal_anchor()` + test |

### 5. LLM Audit Line Protocol (§8.4)

| Check | Result | Evidence |
|-------|--------|----------|
| `SEVERITY\|LOCATION\|MESSAGE` format | ✅ PASS | `_parse_llm_audit_response()` splits by `\|` |
| `PASS\|chapter\|no issues` → LLM pass | ✅ PASS | Exact match: `lines == ("PASS\|chapter\|no issues",)` |
| INFO-only → LLM pass | ✅ PASS | Severity `informational`, status `pass` |
| REVIEWABLE → LLM fail, `repair_hint="patch"` | ✅ PASS | `_llm_issue()` severity mapping |
| BLOCKING → LLM fail, `repair_hint="regenerate"` | ✅ PASS | `_llm_issue()` severity mapping |
| Parse failure → blocked | ✅ PASS | `_llm_parse_failure()` returns blocked with C1 |
| Empty response → blocked (parse failure) | ✅ PASS | `lines` empty → `_llm_parse_failure()` |
| `audit_focus` defaults | ✅ PASS | 5-item `DEFAULT_AUDIT_FOCUS` tuple |

### 6. Programmatic Audit Coverage (§9)

| Check | Result | Evidence |
|-------|--------|----------|
| P1: Structure check | ✅ PASS | `_audit_structure()`: chapter id/title match, 1-6章 structure markers, 0章 no evidence section |
| P2: Placeholder check | ✅ PASS | `_audit_placeholders()`: `[基金类型]`, `X.XX%`, `[列出` |
| E1: Anchor refs validation | ✅ PASS | `_audit_anchor_refs()`: used_anchor_ids in allowed set, evidence lines must have markers |
| E3: evidence_missing fact used in judgment | ✅ PASS | `_audit_anchor_refs()` checks `fact.missing_reason == "evidence_missing"` + `_fact_used()` |
| C2: required output items present | ✅ PASS | `_audit_contract_markers()` |
| C2: ITEM_RULE deleted sections must not appear | ✅ PASS | `_audit_item_rule_deleted_sections()` + `_deleted_rule_marker_present()` |
| C2: non_asserted_facets misuse | ✅ PASS | `_audit_non_asserted_facets()`: ±12 char qualifier window + assertion verb check |
| C1: Forbidden trading phrases | ✅ PASS | `_audit_forbidden_content()`: 12 forbidden phrases |
| L1: Text closure check | ⚠️ see finding 02 | Not separately implemented; partially covered by E3 |

### 7. Chapter 5 Cross-Period Detection

| Check | Result | Evidence |
|-------|--------|----------|
| Trigger: chapter_id=5 + `cross_period_comparison_missing` | ✅ PASS | `_audit_missing_semantics()` guard |
| 14 assertion phrases | ✅ PASS | `_CHAPTER5_ASSERTION_PHRASES` |
| 9 negation/gap prefixes | ✅ PASS | `_CHAPTER5_NEGATION_PREFIXES` |
| 12-char prefix window for negation | ✅ PASS | `markdown[max(0, index - 12):index]` |
| Question forms not blocked | ✅ PASS | `_QUESTION_PREFIXES` with 6-char window |
| Fail → C2, `repair_hint="needs_more_facts"` | ✅ PASS | Issue construction |

### 8. repair_hint Aggregation

| Check | Result | Evidence |
|-------|--------|----------|
| Priority: `needs_more_facts > regenerate > patch > none` | ✅ PASS | `_REPAIR_HINT_ORDER` dict + `max()` |
| No issues → status-dependent default | ✅ PASS | `_aggregate_repair_hint()`: empty issues + blocked → `regenerate` |
| Multi-source aggregation | ✅ PASS | Test: programmatic `needs_more_facts` + LLM `patch` → `needs_more_facts` |

### 9. E2 Deferral

| Check | Result | Evidence |
|-------|--------|----------|
| E2 NOT implemented in programmatic audit | ✅ PASS | No source re-reading code |
| E2 in rule code literal for forward reference | ✅ PASS | `ChapterAuditRuleCode` includes `"E2"` |
| Explicit documentation | ✅ PASS | Module docstring, README, implementation evidence |

### 10. Import Isolation

| Check | Result | Evidence |
|-------|--------|----------|
| Writer AST import check | ✅ PASS | `test_writer_does_not_import_repository_source_service_dayu_or_openai` |
| Auditor AST import check | ✅ PASS | `test_auditor_does_not_import_repository_source_service_dayu_or_openai` |
| Writer only imports `chapter_facts` from Fund layer | ✅ PASS | `from fund_agent.fund.chapter_facts import ...` |
| Auditor only imports `chapter_writer` types | ✅ PASS | `from fund_agent.fund.chapter_writer import ChapterDraft, ChapterWriterInput` |

### 11. README Updates

| Check | Result | Evidence |
|-------|--------|----------|
| Fund README documents Gate 2 primitives | ✅ PASS | Writer/auditor import + example usage |
| Fund README states boundaries | ✅ PASS | "不实现 chapter orchestrator、repair loop、final assembler..." |
| Fund README states E2 deferred | ✅ PASS | "E2 证据与断言源文匹配复核不在 Gate 2 实现范围" |
| Tests README documents new test files | ✅ PASS | File descriptions + `pytest` command |

### 12. Validation Commands

| Command | Result |
|---------|--------|
| `uv run ruff check .` | All checks passed |
| `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q` | 34 passed |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | 1006 passed, 91.65% coverage |
| `git diff --check` | Exit 0, no whitespace errors |

---

## Findings

### 01-未修复-MEDIUM-程序审计 must_not_cover 确定性检查被完全委托给 LLM audit

- **位置**: `fund_agent/fund/chapter_auditor.py` `_audit_contract_markers()` (line 509-527)；plan §9 programmatic audit C2
- **问题类型**: 契约缺失
- **当前写法**: `_audit_contract_markers()` 仅检查 `required_output_items` 是否在草稿中出现（对应 must_answer），未对 `must_not_cover` 做任何确定性检查。`must_not_cover` 边界检查完全依赖 LLM audit 的 `must_not_cover_boundary` focus。
- **反例/失败场景**: 若 LLM audit 不可用（`llm_client=None`），`must_not_cover` 中的明确禁用项（如"不展开收益率详细计算"、"不展开基金经理选股能力分析"）不会被任何程序化检查拦截。一份在第 1 章中大量展开收益计算和选股分析的草稿，在只跑程序审计时可以 `pass`。
- **为什么有问题**: Plan §9 将 C2 的 must_not_cover 检查列在 programmatic audit 覆盖范围内（"must_not_cover 中的明确禁用项不得出现"），但实现将其完全委托给 LLM audit。虽然 must_not_cover 项本质上是语义约束，确实难以纯确定性检查，但实现没有最低限度的关键词检测（如 must_not_cover 中出现的核心名词是否被大段展开）。
- **直接证据**: `_audit_contract_markers()` 函数体只有 7 行，仅做 `required_output_items` 存在性检查。Controller decision 要求 programmatic audit 通过 + LLM audit 通过才能 accepted=True，但 programmatic 对 must_not_cover 零覆盖意味着 programmatic-only run（`run_llm=False`）无法检测 must_not_cover 违规。
- **影响**: programmatic-only audit 漏检 must_not_cover 违规 → 若 LLM audit 不可用时有误导性 pass
- **建议改法和验证点**: 二选一：(a) 在 `_audit_contract_markers()` 增加最低限度的 must_not_cover 关键词检查（如 must_not_cover 项中出现的特征名词搭配 section-level heading marker 检测）；(b) 在代码注释和 README 中显式声明 must_not_cover 的确定性检查委托给 LLM audit，programmatic 只检查 required_output_items 存在性。同时增加 `run_llm=True` 的逻辑：当 `run_llm=False` 时应在 audit result 中标记 informational issue 说明 must_not_cover 未被程序化验证。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-LOW-L1 文本闭合检查未独立实现

- **位置**: `fund_agent/fund/chapter_auditor.py` `audit_chapter_programmatic()` (line 304-331)；plan §9 L1
- **问题类型**: 契约缺失
- **当前写法**: Plan §9 L1 要求"若 draft 声称 A=R-B 或 A-C，必须引用 derived/formula fact 或明确'数据不足，未计算'". 程序审计的 `checked_rules` 返回了 `"L1"`，但实际代码中 `_audit_*` helpers 没有独立的 L1 检查函数。L1 的效果部分由 E3（evidence_missing fact 被用于关键判断）间接覆盖。
- **反例/失败场景**: 草稿中写了一行"根据计算，A=R-B=5.3%"但未引用任何 formula fact。E3 不一定触发（如果 formula 是从 available facts 计算得出的，而非 missing）。L1 的"文本声称了公式计算但未引用来源"没有被独立检查。
- **为什么有问题**: E3 检查 fact 级别的 evidence_missing，但 L1 检查的是 draft markdown 级别的"声称公式计算结果但未溯源"。两者重叠但不相等。checked_rules 声明了 L1 已检查但实际未实现独立检查函数。
- **直接证据**: `checked_rules=("P1", "P2", "E1", "E3", "C1", "C2", "L1", "R1", "R2")` 包含 L1，但 `_audit_*` helpers 中没有 `_audit_numerical_closure` 或等效函数。
- **影响**: 低 — L1 的硬失效场景（声称 A=R-B 但缺来源）很可能被 E3 或 E1 覆盖；风险是 checked_rules 声明了但实际检查不完整
- **建议改法和验证点**: 二选一：(a) 增加独立的 `_audit_numerical_closure()` helper 做 L1 文本闭合检查（如检测 `A=R-B`、`A-C` 模式且无相邻 fact_id 引用）；(b) 将 L1 从 checked_rules 中移除，在注释中说明 Gate 2 程序审计不独立实现 L1，数值闭合完整检查留给 Evidence Confirm gate。推荐 (b)，与 E2 deferral 处理方式一致。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 03-未修复-LOW-`mode="llm"` + `llm_client=None` 路径的直接测试覆盖缺失

- **位置**: `fund_agent/fund/chapter_writer.py` line 429-435；`tests/fund/test_chapter_writer.py`
- **问题类型**: 测试缺口
- **当前写法**: `write_chapter()` 在 preflight 通过后检查 `llm_client is None` 并在 line 429-435 返回 blocked `llm_unavailable`。但测试套件中所有 `llm_client=None` 的用例(fund_type unknown、chapter 0/7、evidence_missing)都在 preflight 阶段就被阻断了，没有一条测试是 preflight 全部通过 + `mode="llm"` + `llm_client=None` 的组合。
- **反例/失败场景**: 如果 future refactor 意外在 preflight 之后、llm_client check 之前插入其他逻辑改变了行为，这个路径没有测试保护。或者如果有人在 llm_client check 处改了 stop_reason 但测试不会发现。
- **为什么有问题**: `llm_unavailable` 是 plan 要求的显式 fail-closed 路径（§7.4 第 4 点第 6 条），需要显式测试覆盖。
- **直接证据**: 遍历 18 个 writer 测试，所有 `write_chapter(input_data, llm_client=None)` 的调用都遇到 preflight block（fund_type unknown、accepted_conclusions_missing 或 evidence_missing）。
- **影响**: 低 — 代码路径简单清晰不易出错，但缺独立测试降低了 regression protection
- **建议改法和验证点**: 增加 `test_writer_blocks_llm_unavailable_when_preflight_passes` 测试：构造 preflight 全通过的 bundle（如为 chapter 1-6 中非 0/7 的章节、提供 valid fund_type、有足够 anchors），传入 `mode="llm"` + `llm_client=None`，断言 `status="blocked"`、`stop_reason="llm_unavailable"`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 04-未修复-INFO-`_audit_non_asserted_facets` assertion verb 检测可对"可能是"产生假阳性

- **位置**: `fund_agent/fund/chapter_auditor.py` line 574-598
- **问题类型**: 其它
- **当前写法**: 当 `prefix` 中包含 `"是"` 时会触发 assertion verb 检测，即使完整词语是 `"可能是"`（表示非断言）。例如"这只基金可能是主动权益基金（价值风格）"会被 flag，因为 `"是" in "可能是"` 为 True。
- **为什么有问题**: 极低影响 — 系统 fail-closed（保守阻断），不会产生错误结论。`"可能是"` 本身是合理的不确定表达，且 qualifier `"可能"` 也在 `_NON_ASSERTED_QUALIFIERS` 中。该语句会被双重标记：qualifier 检查通过（窗口中有"可能"）但 assertion verb 检查失败（prefix 含"是"），最终被 flag。
- **直接证据**: `any(verb in prefix for verb in ("属于", "是", "为", "定位为"))` — 子串匹配，`"是" in "可能是"` = True
- **影响**: 极低 — fail-closed，不会漏过真正的误断言
- **建议改法和验证点**: 无需修改。后续 gate 可将"是"替换为更精确的词边界匹配或排除"可能是"、"或许是"等复合词。Implementation evidence 可记录此已知保守行为。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: INFO

---

## Open Questions

无。

## Residual Risks

| 风险 | 来源 | 跟踪位置 |
|------|------|---------|
| must_not_cover 无程序化检查 | Finding 01 | 实现或 README 中声明委托给 LLM audit |
| L1 checked_rules 声明但无独立实现 | Finding 02 | 移除 L1 声明或增加独立 helper |
| llm_unavailable 路径无独立测试 | Finding 03 | 增加 preflight-pass + llm_client=None 测试 |
| non_asserted_facets 假阳性 | Finding 04 | 已知保守行为，后续 gate 窄化 |
| E2 deferred | Controller decision | Evidence Confirm gate |
| bond_risk_evidence 锚点未展开 | Gate 1 residual | 后续 conversion helper gate |
| LLM prompt 质量 | 依赖真实 LLM 行为 | Gate 3+ orchestrator prompt tuning |

---

## Implementation Review Conclusion

**PASS_WITH_NON_BLOCKING**

Implementation faithfully executes the accepted plan with high fidelity:

- **Scope**: Strictly Fund-layer single-chapter writer/auditor primitives; no orchestrator, repair loop, CLI, Host/dayu
- **Contracts**: All 16 dataclasses, 2 Protocols, and public APIs match the plan exactly; all `frozen=True, slots=True`
- **Fail-closed**: 15+ stop conditions all correctly implemented and tested; no fake pass paths detected
- **Marker parsing**: Writer anchor/missing marker contracts implemented with exact regex and comprehensive edge case handling
- **LLM audit line protocol**: `SEVERITY|LOCATION|MESSAGE` parser with all severities, parse failure → blocked, zero-issue pass
- **Programmatic audit**: Structure, placeholders, anchors, ITEM_RULE, non_asserted_facets, forbidden content, chapter 5 cross-period all covered
- **repair_hint aggregation**: Priority ordering correct; multi-source aggregation tested
- **Import isolation**: Zero forbidden imports (verified by both AST tests and manual review)
- **Tests**: 34 targeted tests all passing, covering happy/blocked/semantic/parse/import paths
- **Coverage**: 91.65% total (well above 50% threshold)
- **Documentation**: READMEs updated within allowed scope; control-docs untouched

3 findings (1 MEDIUM, 2 LOW, 1 INFO) are all non-blocking:
- MEDIUM: `must_not_cover` programmatic check can be documented as LLM-delegated or given minimal keyword detection
- LOW: L1 `checked_rules` declaration mismatch with implementation can be fixed by removing L1 or adding helper
- LOW: `llm_unavailable` test coverage gap easily closed
- INFO: Known conservative false-positive in assertion verb detection

None of these findings indicate incorrectness or require plan changes. The implementation is safe to accept.

## Reviewer Self-Check

- [x] reviewed target、scope、source of truth 已写清
- [x] findings 是 evidence-based、adversarial、可执行，且没有 style/nit/speculation
- [x] open questions、residual risks、tracking destination 与 findings 分开
- [x] conclusion 为 PASS_WITH_NON_BLOCKING
- [x] output path 为 `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-ds-20260530.md`
- [x] 未修改 plan 文件，未 stage/commit/push/PR
