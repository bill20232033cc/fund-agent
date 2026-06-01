# MVP LLM writer/auditor contract hardening plan review — MiMo

Gate: `MVP LLM writer/auditor contract hardening gate`
Role: plan reviewer
Date: 2026-05-31
Reviewed artifact: `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`

## Conclusion

**PASS_WITH_NON_BLOCKING**

Plan is handoff-ready and code-generation-ready. Gate sequencing, scope boundaries, hard constraints and non-goals are correctly preserved. Two blocking findings and three non-blocking findings identified; all are resolvable without plan rewrite.

Finding count: 2 blocking, 3 non-blocking

---

## Findings

### F-001 [blocking] Auditor `_audit_contract_markers` must align with new writer output protocol

**Location**: Plan §7.1 (Writer output protocol), §9 Slice A (Exact changes), §9 Slice B (Exact changes), `chapter_auditor.py:534-553`

**Problem**: Plan §7.1 introduces `<!-- required_output:<exact required output item> -->` as the writer output protocol for required items. Slice A makes the writer parser block drafts missing these markers. However, the auditor's `_audit_contract_markers()` currently checks for **plain item text substring** in the draft:

```python
# chapter_auditor.py:548-552
for item in input_data.writer_input.chapter.contract.required_output_items
    if item and item not in markdown
```

If the writer protocol changes to marker-based output, this check becomes misaligned:
- If writer parser catches missing markers (normal flow), auditor never sees the draft — no issue.
- But as defense-in-depth: if writer parser misses a marker but the item name appears as free text elsewhere, auditor would incorrectly pass.
- Conversely, if a draft contains `<!-- required_output:<item> -->` markers correctly but not the bare item text, auditor would incorrectly fail.

The plan does not explicitly list `_audit_contract_markers` update in Slice B's allowed files or exact changes.

**Recommendation**: Add to Slice B exact changes: update `_audit_contract_markers()` to check for `<!-- required_output:<item> -->` marker presence instead of (or in addition to) bare item text. Alternatively, document in the plan that the auditor's programmatic contract marker check is intentionally left as-is because the writer parser now provides the primary enforcement, and the auditor check is a legacy fallback that will be removed in a later gate.

---

### F-002 [blocking] Test helper `_valid_chapter_markdown()` / `_valid_markdown()` update scope is incomplete

**Location**: Plan §9 Slice A (Tests), `tests/fund/test_chapter_writer.py:546-570`, `tests/fund/test_chapter_auditor.py:522-551`

**Problem**: Plan Slice A says:

> 更新 `_valid_chapter_markdown()`，让测试合法章节包含 required output markers。

The current `_valid_chapter_markdown()` produces required items as plain text lines:
```python
required_lines = "\n".join(f"- {item}: 已根据结构化事实说明。" for item in chapter.contract.required_output_items)
```

After the plan, valid markdown must include `<!-- required_output:<item> -->` markers. But:

1. The auditor test file has its own `_valid_markdown()` helper (lines 522-551) that uses the same plain-text pattern. If the auditor's `_audit_contract_markers` check changes (per F-001), this helper must also be updated, or `test_programmatic_audit_passes_minimal_valid_chapter()` will fail.

2. The plan does not mention updating the auditor test helper or the auditor programmatic tests that depend on it.

**Recommendation**: Explicitly add to Slice A or Slice B: "Update `tests/fund/test_chapter_auditor.py` `_valid_markdown()` helper to include `<!-- required_output:<item> -->` markers if the auditor's `_audit_contract_markers` check is updated." If F-001 is resolved by leaving the auditor check unchanged, then the auditor test helper does not need updating — but this should be explicitly stated.

---

### F-003 [non-blocking] Facet issue deduplication implementation gap in Slice B

**Location**: Plan §9 Slice B (Exact changes, `_audit_non_asserted_facets`)

**Problem**: Plan correctly identifies that `_audit_non_asserted_facets()` can produce duplicate issues (diagnostic shows `纯债基金` issue 3 times). Plan recommends:

> 不因同一个 facet 多次出现而重复输出完全相同 issue；可用 `(facet, index window)` 或 first occurrence 去重

However, the current code iterates through all occurrences of each facet in the markdown:

```python
# chapter_auditor.py:634-652
for facet in ...:
    start = 0
    while True:
        index = markdown.find(facet, start)
        if index < 0: break
        # ... check window, append issue ...
        start = index + len(facet)
```

The plan's "first occurrence" or "(facet, index window)" approach is underspecified. An implementation agent needs to choose between:
- **First occurrence only**: stop after first hit per facet (simplest, may miss legitimately different contexts)
- **Window-based dedup**: skip if a previous issue for the same facet exists within N characters (more robust, needs window size)
- **Exact message dedup**: filter duplicate `(facet, message)` pairs at the end (simplest post-hoc)

**Recommendation**: Specify the dedup strategy as "first occurrence per facet" for MVP simplicity. Add to Slice B exact changes: "In `_audit_non_asserted_facets()`, track seen facets in a set; skip subsequent occurrences of the same facet."

---

### F-004 [non-blocking] Validation matrix for Slice D does not explicitly list real provider smoke command

**Location**: Plan §10 (Validation matrix), §9 Slice D (Tests / validation)

**Problem**: Slice D's completion signal references real provider smoke (`006597 / 2024 --use-llm`), and §10 lists it under "Real provider smoke" with expected success/fail paths. However, the validation matrix's command list only includes:

```bash
uv run ruff check .
uv run pytest ... -q
uv run pytest --cov=fund_agent --cov-report=term-missing
uv run fund-analysis analyze 006597 --report-year 2024
env -u ... uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

The last command is the real provider smoke, but it's not labeled as such in the validation matrix command list — it appears under "Real provider smoke" in the prose section. An implementation agent might skip it if only following the command list.

**Recommendation**: Add a labeled entry in the validation matrix command list:

```bash
# Real provider smoke (requires valid FUND_AGENT_LLM_* env)
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

---

### F-005 [non-blocking] New `ChapterWriteStopReason` values need explicit Service mapping targets

**Location**: Plan §7.2 (Writer parser failure categories), §9 Slice A (Exact changes, `_WRITER_STOP_REASON_MAPPING`)

**Problem**: Plan §7.2 proposes new stop reasons:

```python
"missing_required_structure"
"missing_required_output_marker"
"unknown_anchor"
"response_too_long"
"response_truncated"
```

And states:

> Service `_WRITER_STOP_REASON_MAPPING` 必须同步接受新增 stop reasons；新增原因默认映射到 `blocked`，Service stop reason 可先使用 `llm_contract_violation`

This is clear. However, the plan does not specify the exact `ChapterRunStopReason` target for each new writer stop reason. The existing mapping test (`test_every_writer_stop_reason_maps_to_exact_run_reason`) asserts exact matches. The implementation agent needs to know:

- `missing_required_structure` → `("blocked", "llm_contract_violation")`
- `missing_required_output_marker` → `("blocked", "llm_contract_violation")`
- `unknown_anchor` → `("blocked", "llm_contract_violation")`
- `response_too_long` → `("blocked", "llm_contract_violation")`
- `response_truncated` → `("blocked", "llm_contract_violation")`

This is implied by "默认映射到 `blocked`" and "Service stop reason 可先使用 `llm_contract_violation`", but making it explicit would prevent implementation ambiguity.

**Recommendation**: Add a mapping table to §7.2 or Slice A exact changes listing each new `ChapterWriteStopReason` → `(ChapterRunStatus, ChapterRunStopReason)` pair.

---

## Gate sequencing check

| Criterion | Status |
|---|---|
| Current gate = contract hardening | PASS — plan scope matches |
| Next gate = real provider smoke acceptance | PASS — plan defers acceptance裁决 |
| Later gate = score improvement loop | PASS — plan explicitly excludes scoring |
| No golden/fixtures/score/quality gate changes | PASS |
| No Gate 5 dayu/Host/Agent | PASS |
| No PR state changes | PASS |
| No secrets/full provider response | PASS |
| No weak-evidence pass | PASS |
| No candidate facet asserted as fact | PASS — plan strengthens facet boundary |
| Deterministic analyze/checklist unchanged | PASS |

## Scope / sequencing check

- Plan correctly identifies that the first fix point is prompt contract, not audit relaxation.
- Parser fail-closed before auditor is the right design.
- Repair context is typed explicit, not extra_payload — PASS.
- Timeout classification separates provider runtime from writer/auditor contract — PASS.
- Bounded retry preserved via existing `max_repair_attempts` — PASS.
- Real smoke is validation-only in this gate, not acceptance裁决 — PASS.

## Code feasibility check

- `ChapterLLMRequest` is `frozen=True, slots=True` — adding `repair_context: ChapterRepairContext | None = None` with default is backward-compatible. PASS.
- `ChapterWriterInput` is `frozen=True, slots=True` — same pattern. PASS.
- `_WRITER_STOP_REASON_MAPPING` is `Final[dict]` — adding entries requires editing the literal, not runtime mutation. PASS.
- `LLMProviderRuntimeError` already exists as base class — adding `LLMProviderTimeoutError` subclass is clean. PASS.
- `_exception_result()` in orchestrator catches `Exception` — will naturally catch new typed exceptions; classification logic needs to be added. PASS.

## Self-check

Self-check: pass

---

Artifact path: `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-review-mimo-20260531.md`
Conclusion: PASS_WITH_NON_BLOCKING
Findings: 2 blocking (F-001, F-002), 3 non-blocking (F-003, F-004, F-005)
