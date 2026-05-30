# Implementation Review: MVP Gate 2 chapter_writer + chapter_auditor

日期：2026-05-30
角色：AgentMiMo — independent implementation reviewer
Gate：`MVP Gate 2: chapter_writer + chapter_auditor`

## Reviewed Target

Uncommitted Gate 2 implementation on branch `codex/local-reconciliation`.

**Changed files (6):**
- `fund_agent/fund/chapter_writer.py` (new, 1135 lines)
- `fund_agent/fund/chapter_auditor.py` (new, 986 lines)
- `tests/fund/test_chapter_writer.py` (new, 572 lines, 21 tests)
- `tests/fund/test_chapter_auditor.py` (new, 513 lines, 13 tests)
- `fund_agent/fund/README.md` (modified, +20 lines)
- `tests/README.md` (modified, +3 lines)

**Untouched (verified):**
- `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- `fund_agent/fund/__init__.py`
- No golden fixtures, quality gate, CLI, Service, Host, dayu changes

## Source of Truth

- Accepted plan: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md` (commit `b46a80a`)
- Controller decision: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-decision-20260530.md`
- Implementation evidence: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-evidence-20260530.md`

## Validation Results

| Check | Result |
|-------|--------|
| `ruff check .` | All checks passed |
| Targeted pytest (34 tests) | 34 passed in 0.74s |
| Full pytest | 1006 passed in 4.75s |
| Coverage (full) | 91.65% (threshold 50%) |
| Coverage (chapter_writer.py) | 90% |
| Coverage (chapter_auditor.py) | 94% |
| `git diff --check` | Clean |

## Scope Verification

Plan §12 allowed files vs actual changes:

| Allowed | Actual | Status |
|---------|--------|--------|
| `fund_agent/fund/chapter_writer.py` | Created | OK |
| `tests/fund/test_chapter_writer.py` | Created | OK |
| `fund_agent/fund/chapter_auditor.py` | Created | OK |
| `tests/fund/test_chapter_auditor.py` | Created | OK |
| `fund_agent/fund/__init__.py` | Not modified | OK (not needed) |
| `fund_agent/fund/README.md` | Modified | OK |
| `tests/README.md` | Modified | OK |

Plan §15 controller-only files (design.md, startup-packet.md, implementation-control.md): **Not touched**.

## Findings

### 01-未修复-INFO-programmatic audit severity 全部硬编码为 blocking
- **位置**: `chapter_auditor.py:863` `_program_issue()` 函数
- **问题类型**: 最佳实践偏离
- **当前写法**: `_program_issue()` 将所有程序审计 issue 的 `severity` 硬编码为 `"blocking"`。这意味着 P2（占位符残留）、E1（锚点引用）等在 plan 中标注为"阻断"级别的规则，与 C1（禁用措辞）共用同一 severity。
- **反例/失败场景**: 无功能影响。plan §9 明确所有程序审计规则均为 blocking 级别，代码行为与 plan 一致。
- **为什么有问题**: 不是 bug，但 `_program_issue()` 不接受 severity 参数，未来如果需要区分 blocking/reviewable 程序审计规则时需要重构。
- **直接证据**: `chapter_auditor.py:863` 硬编码 `severity="blocking"`；plan §9 所有规则均标注为"阻断"。
- **影响**: 无。当前行为正确。
- **建议改法和验证点**: 无需修改。如果 Gate 3 需要非 blocking 级别的程序审计规则，可在那时增加 severity 参数。
- **修复风险（低/中/高）**: 无
- **严重程度（低/中/高/严重）**: INFO

### 02-未修复-INFO-writer 和 auditor 各自独立定义 _FORBIDDEN_PHRASES
- **位置**: `chapter_writer.py:68` 和 `chapter_auditor.py:58`
- **问题类型**: 最佳实践偏离
- **当前写法**: 两个模块各自独立定义了相同的 12 个禁用措辞列表。
- **反例/失败场景**: 如果未来新增禁用措辞，需要在两处同步更新，否则 writer 和 auditor 的禁用措辞集不一致。
- **为什么有问题**: 轻微维护风险。当前两处列表完全一致，不会导致功能问题。
- **直接证据**: `chapter_writer.py:68-81` 和 `chapter_auditor.py:58-71` 内容相同。
- **影响**: 低。维护风险，不影响当前正确性。
- **建议改法和验证点**: 可在 `chapter_writer.py` 中导出 `_FORBIDDEN_PHRASES` 供 auditor 导入，或在 shared constants 模块中定义。但当前实现与 plan 一致（plan 未要求共享）。
- **修复风险（低/中/高）**: 无
- **严重程度（低/中/高/严重）**: INFO

## Contract Compliance Check

### Writer Contract (Plan §7)

| Item | Plan | Implementation | Status |
|------|------|---------------|--------|
| Literal aliases | §7.1 | Lines 26-41, includes `prompt_only` | OK |
| ChapterLLMRequest | §7.2 | Lines 84-108, frozen+slots+kw_only | OK |
| ChapterLLMResponse | §7.2 | Lines 111-125, frozen+slots+kw_only | OK |
| ChapterLLMClient Protocol | §7.2 | Lines 128-145 | OK |
| ChapterWriterInput | §7.3 | Lines 148-170, frozen+slots+kw_only | OK |
| ChapterWriterPrompt | §7.3 | Lines 173-203, frozen+slots+kw_only | OK |
| ChapterDraft | §7.3 | Lines 206-232, frozen+slots+kw_only | OK |
| ChapterWriteIssue | §7.3 | Lines 235-255, frozen+slots+kw_only | OK |
| ChapterWriteResult | §7.3 | Lines 258-276, frozen+slots+kw_only | OK |
| ChapterWriter facade | §7.3 | Lines 279-305 | OK |
| build_chapter_writer_input() | §7.3 | Lines 308-346 | OK |
| build_chapter_prompt() | §7.3 | Lines 349-402 | OK |
| write_chapter() | §7.3 | Lines 405-448 | OK |
| Anchor marker regex | §7.5 | `<!-- anchor:([^<>\s]+) -->` | OK |
| Missing marker regex | §7.5 | `<!-- missing:([a-z_]+) -->` | OK |
| max_output_chars hard post-check | §7.5 | Line 716, `len(text) > max_output_chars` | OK |
| Invalid marker detection | §7.5 | `_invalid_marker_issues()` lines 747-779 | OK |
| Unknown anchor → bond_risk_evidence message | §7.5 | Lines 897-919 | OK |
| prompt_only → blocked, stop_reason="prompt_only" | §7.4.6 | Line 428 | OK |
| evidence_missing critical judgment | §7.4.5 | `_fact_supports_critical_judgment()` lines 568-585 | OK |
| Chinese docstrings | Plan | All functions and classes | OK |

### Auditor Contract (Plan §8)

| Item | Plan | Implementation | Status |
|------|------|---------------|--------|
| Literal aliases | §8.1 | Lines 21-39 | OK |
| ChapterAuditLLMRequest | §8.2 | Lines 112-138, frozen+slots+kw_only | OK |
| ChapterAuditLLMResponse | §8.2 | Lines 141-155, frozen+slots+kw_only | OK |
| ChapterAuditLLMClient Protocol | §8.2 | Lines 158-172 | OK |
| ChapterAuditInput | §8.3 | Lines 175-191, frozen+slots+kw_only | OK |
| ChapterAuditIssue | §8.3 | Lines 194-220, frozen+slots+kw_only | OK |
| ChapterProgrammaticAuditResult | §8.3 | Lines 223-235, frozen+slots+kw_only | OK |
| ChapterLLMAuditResult | §8.3 | Lines 238-254, frozen+slots+kw_only | OK |
| ChapterAuditResult | §8.3 | Lines 257-275, frozen+slots+kw_only | OK |
| ChapterAuditor facade | §8.3 | Lines 278-301 | OK |
| audit_chapter_programmatic() | §8.3 | Lines 304-331 | OK |
| audit_chapter_llm() | §8.3 | Lines 334-371 | OK |
| audit_chapter() | §8.3 | Lines 374-415 | OK |
| DEFAULT_AUDIT_FOCUS | §8.4 | Lines 44-50, 5 items | OK |
| SEVERITY\|LOCATION\|MESSAGE parser | §8.4 | `_parse_llm_audit_response()` lines 692-737 | OK |
| Parse failure → blocked C1 | §8.4 | `_llm_parse_failure()` lines 740-774 | OK |
| PASS\|chapter\|no issues | §8.4 | Line 709 | OK |
| repair_hint aggregation | §9 | `_aggregate_repair_hint()` lines 813-832 | OK |
| E2 deferral | §9 | Module docstring line 6 | OK |
| Chinese docstrings | Plan | All functions and classes | OK |

### Programmatic Audit Rules (Plan §9)

| Rule | Implementation | Status |
|------|---------------|--------|
| P1 (structure) | `_audit_structure()` lines 418-444 | OK |
| P2 (placeholders) | `_audit_placeholders()` lines 447-464 | OK |
| E1 (anchor refs) | `_audit_anchor_refs()` lines 467-506 | OK |
| E3 (evidence_missing fact used) | `_audit_anchor_refs()` lines 495-505 | OK |
| C1 (forbidden content) | `_audit_forbidden_content()` lines 601-618 | OK |
| C2 (contract markers) | `_audit_contract_markers()` lines 509-527 | OK |
| C2 (ITEM_RULE deleted) | `_audit_item_rule_deleted_sections()` lines 530-558 | OK |
| C2 (non_asserted_facets) | `_audit_non_asserted_facets()` lines 561-598 | OK |
| C2 (ch5 cross-period) | `_audit_missing_semantics()` lines 621-659 | OK |
| E2 (deferred) | Documented in module docstring | OK |

### Fail-Closed Verification

| Condition | Test | Status |
|-----------|------|--------|
| fund_type="unknown" | `test_writer_blocks_unknown_fund_type` | OK |
| Ch 0/7 without accepted conclusions | `test_writer_blocks_chapter_zero_and_seven_without_accepted_conclusions` | OK |
| llm_client=None, mode="llm" | (covered by prompt_only test which also tests None path) | OK |
| Empty LLM response | `test_writer_rejects_empty_llm_response` | OK |
| Over max_output_chars | `test_writer_rejects_response_over_max_output_chars_without_truncation` | OK |
| Forbidden phrases | `test_writer_rejects_forbidden_trading_advice` | OK |
| Invalid anchor marker format | `test_writer_rejects_invalid_anchor_marker_spacing_or_case` | OK |
| Unknown anchor | `test_writer_rejects_unknown_anchor_reference` | OK |
| Unknown missing reason | `test_writer_rejects_unknown_missing_reason_marker` | OK |
| Evidence line without anchor marker | Covered by `_evidence_line_issues` | OK |
| LLM audit parse failure | `test_llm_audit_parse_failure_is_blocked` | OK |
| LLM audit client None | `test_llm_audit_unavailable_is_blocked` | OK |
| Evidence_missing critical fact | `test_writer_blocks_evidence_missing_critical_fact_by_required_by` | OK |
| Evidence_missing numeric field | `test_writer_blocks_evidence_missing_numeric_source_field` | OK |
| Bond risk internal anchor | `test_writer_reports_bond_risk_internal_anchor_message` | OK |

### Import Isolation

| Module | AST Check Test | Result |
|--------|---------------|--------|
| chapter_writer.py | `test_writer_does_not_import_repository_source_service_dayu_or_openai` | Pass |
| chapter_auditor.py | `test_auditor_does_not_import_repository_source_service_dayu_or_openai` | Pass |

Forbidden fragments checked: documents, repository, cache, pdf, source, downloader, parser, service, dayu, openai, httpx.

## Review Checklist (Plan §16)

| # | Check Item | Result |
|---|-----------|--------|
| 1 | Only Fund-layer single-chapter writer/auditor primitives | OK |
| 2 | No Service orchestrator, repair loop, final assembler, CLI --use-llm, Host/Agent/dayu | OK |
| 3 | All business parameters typed, no extra_payload | OK |
| 4 | Writer/auditor only consume ChapterFactInput/ChapterFactProjection | OK |
| 5 | No repository/PDF/cache/source/downloader/parser/Service/dayu/OpenAI import | OK |
| 6 | fund_type unknown, missing facts, missing anchors, LLM unavailable all fail closed | OK |
| 7 | ITEM_RULE delete enforced | OK |
| 8 | non_asserted_facets not driving conclusions or ITEM_RULE | OK |
| 9 | Anchor/missing marker and LLM audit line parser enforced, no silent pass | OK |
| 10 | Chapter 5 cross-period missing only blocks un-negated assertions | OK |
| 11 | repair_hint aggregation priority implemented and tested | OK |
| 12 | E2 source verification not faked, explicitly deferred | OK |
| 13 | Programmatic vs LLM audit boundary clear | OK |
| 14 | prompt_only does not create fake accepted draft | OK |
| 15 | Tests cover happy path, blocked path, semantic fail, import boundary | OK |

## Verdict

**PASS**

Implementation faithfully follows the accepted plan. All 34 tests pass. All validation commands pass. No scope creep. No fake pass. All fail-closed semantics verified. Chinese docstrings present on all public interfaces. Import isolation verified via AST. Two INFO findings (non-blocking): programmatic audit severity hardcoded (correct per plan) and duplicate forbidden phrases list (maintenance concern only).

## Reviewer Self-Check

- [x] Verified all changed files against plan allowed files
- [x] Verified untouched files (AGENTS.md, design.md, startup-packet, implementation-control.md, __init__.py)
- [x] Checked contract compliance for writer and auditor dataclasses, protocols, and public APIs
- [x] Checked fail-closed semantics with test evidence
- [x] Checked import isolation via AST tests
- [x] Checked Chinese docstrings
- [x] Checked README diffs are within scope
- [x] Ran validation commands (ruff, pytest, coverage)
- [x] Findings are evidence-based, not style/nit
- [x] Verdict is PASS, PASS_WITH_NON_BLOCKING, or BLOCKED
