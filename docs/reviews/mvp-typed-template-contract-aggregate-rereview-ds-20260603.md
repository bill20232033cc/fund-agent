# MVP typed template contract aggregate deepreview — re-review (DS)

## Re-Review Metadata

- Re-reviewer: AgentDS
- Source finding: `docs/reviews/code-review-20260603-225446.md`
- Fix evidence: `docs/reviews/mvp-typed-template-contract-aggregate-deepreview-fix-evidence-20260603.md`
- Gate: `MVP typed template contract aggregate deepreview`
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Scope: re-review only — no file edits, no commit/push/PR, no provider/runtime/live probe, no new gate

## Finding Under Re-Review

**Original finding (blocking):** Ch3 typed `must_not_cover` can be bypassed by putting a positive claim on the same line as an anchor marker (`<!-- anchor:<id> --> 言行一致性判断：言行一致。`).

Root cause: `_line_is_contract_or_anchor_metadata()` skipped any line whose stripped text started with `<!-- anchor:`, `<!-- required_output:`, or `> 📎 证据：`, without checking whether trailing body text followed the marker.

## Fix Analysis

### What Changed

`_line_is_contract_or_anchor_metadata()` in `fund_agent/fund/chapter_auditor.py:1162-1180`:

**Before (buggy):**
```python
stripped = line.strip()
return stripped.startswith(_REQUIRED_OUTPUT_MARKER_TEXT) or any(
    stripped.startswith(prefix) for prefix in _ANCHOR_CAPTION_PREFIXES
)
```

**After (fixed):**
```python
stripped = line.strip()
if stripped.startswith(_REQUIRED_OUTPUT_MARKER_TEXT):
    return stripped.endswith("-->")
if stripped.startswith("<!-- anchor:"):
    return stripped.endswith("-->")
return False
```

Key changes:
1. Each marker type now requires the stripped line to **end with** `-->` — a standalone HTML comment.
2. Evidence caption prefixes (`> 📎 证据：`, `>📎 证据：`) are no longer blanket-skipped; they now flow into normal sentence scanning.
3. `_ANCHOR_CAPTION_PREFIXES` constant is now unreferenced (dead code, hygiene note only).

### New Regression Test

`test_ch3_positive_claim_after_anchor_marker_blocks_when_actual_behavior_unreviewed` (test_chapter_auditor.py:288-316) constructs a Ch3 draft line `<!-- anchor:<valid_id> --> 言行一致性判断：言行一致。` with real `EvidenceAvailability` (actual behavior unreviewed) and asserts `programmatic:C2:ch3.must_not_cover.item_04` is emitted. This directly exercises the bypass scenario from the original finding.

## Verification Results

### 1. typed Ch3 must_not_cover 不再因 anchor marker 同行正向结论而跳过

**PASS.** The `stripped.endswith("-->")` guard means `<!-- anchor:xxx --> 言行一致。` does NOT match (ends with `一致。`, not `-->`). The line proceeds to `_split_sentences()` → `_first_ch3_style_claim_phrase()` → C2 issue emitted. Regression test confirms.

### 2. Standalone marker 行仍可作为 metadata

**PASS.** `<!-- anchor:xxx -->` on its own line starts with `<!-- anchor:` AND ends with `-->`, so `_line_is_contract_or_anchor_metadata()` returns `True`. Same for `<!-- required_output:xxx -->`. No existing marker tests regressed.

### 3. 证据 caption 不被宽泛用于 laundering

**PASS.** Evidence caption lines (`> 📎 证据：...`) are no longer matched by `_line_is_contract_or_anchor_metadata()` at all. If a caption line contains a Ch3 positive claim, it will be scanned and potentially blocked. This is fail-closed: metadata cannot be used to hide body conclusions. The fix evidence explicitly acknowledges this as intentional.

### 4. Slice 0 allowed contexts 不被放松

**PASS.** The fix touches only `_line_is_contract_or_anchor_metadata()`. All allowed-context functions are unchanged:
- `_ch3_style_claim_allowed()` — identical
- `_is_required_label_context()` — identical
- `_is_evidence_gap_statement_context()` — identical
- `_is_quote_context()` — identical
- All phrase/denial/marker/introducer constants — identical

The Slice 0 calibration taxonomy (`positive_assertion`, `quasi_positive_assertion`, `gap_statement`, `required_label`, `quote`, `anchor_caption`) encoded in these functions is preserved exactly.

### Test Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_chapter_auditor.py` | **40 passed** |
| `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py` | **314 passed** |
| `uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py` | **All checks passed!** |

No regressions. The new regression test passes alongside all existing tests.

## Blocking Findings

**无。**

原始 finding 已被正确、完整修复。修复是 minimal diff（仅 `_line_is_contract_or_anchor_metadata` 函数 + 一个新回归测试），不改变 Slice 0 允许上下文语义，fail-closed 方向正确。

## Minor Observations (non-blocking)

1. `_ANCHOR_CAPTION_PREFIXES` (chapter_auditor.py:221) 现在是未引用常量。不影响正确性，可在后续清理。

## Residual Risk

- `anchor_caption` 允许上下文未被实现为显式豁免——证据 caption 行中如有 Ch3 正向结论会被扫描并可能阻断。这是有意选择的 fail-closed 行为，修复证据已声明。
- 如果后续需要区分「caption 内对来源字段名的客观描述」与「caption 内夹带的正向结论」，需要新增更窄的 caption 豁免规则，但当前不需要。

## Conclusion

Aggregate deepreview finding 已修复。Re-review 未发现新的 blocking finding。原始 gate 的 blocking 条件已解除。
