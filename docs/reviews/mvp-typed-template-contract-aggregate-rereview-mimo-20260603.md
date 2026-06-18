# Re-review: MVP typed template contract aggregate deepreview finding

## Gate

`MVP typed template contract aggregate deepreview`

## Scope

Re-review only: verify that the single blocking finding from `docs/reviews/code-review-20260603-225446.md` is fixed. No file edits, no commit/push/PR, no provider/runtime/live probe, no new gate.

## Source artifacts

- Finding: `docs/reviews/code-review-20260603-225446.md`
- Fix evidence: `docs/reviews/mvp-typed-template-contract-aggregate-deepreview-fix-evidence-20260603.md`
- Diff: `fund_agent/fund/chapter_auditor.py`, `tests/fund/test_chapter_auditor.py`

## Finding under review

**Blocking: Ch3 typed must_not_cover can be bypassed by putting a positive claim on the same line as an anchor marker.**

Triggering input: `<!-- anchor:<allowed_anchor_id> --> 言行一致性判断：言行一致。`

Old behavior: `_line_is_contract_or_anchor_metadata()` treated any line whose stripped text started with `<!-- anchor:` as metadata, skipping the entire line before sentence scanning. The Ch3 style-claim scanner never inspected trailing body text after the marker.

## Verification

### 1. typed Ch3 must_not_cover no longer bypassed by anchor marker on same line

`chapter_auditor.py:1175-1180` — `_line_is_contract_or_anchor_metadata()` now requires `stripped.endswith("-->")` for both `<!-- required_output:... -->` and `<!-- anchor:... -->` markers. A line like `<!-- anchor:foo --> 言行一致性判断：言行一致。` has stripped text ending with `言行一致。`, not `-->`, so it is NOT classified as metadata and flows through normal sentence scanning.

Regression test `test_ch3_positive_claim_after_anchor_marker_blocks_when_actual_behavior_unreviewed` (test_chapter_auditor.py:288-316) constructs exactly this input using a real anchor id from the writer input and asserts `programmatic:C2:ch3.must_not_cover.item_04` is emitted.

**Verdict: fixed.**

### 2. Standalone marker lines still treated as metadata

A standalone `<!-- anchor:foo -->` line has stripped text ending with `-->`, so `_line_is_contract_or_anchor_metadata` returns `True` and the line is correctly skipped. No regression to normal marker-only lines.

**Verdict: no regression.**

### 3. Evidence caption lines not broadly exempt from scanning

The old code had `> 📎 证据：` in `_ANCHOR_CAPTION_PREFIXES` and blanket-skipped such lines. The fix removed evidence caption blanket-skipping from `_line_is_contract_or_anchor_metadata()`. Evidence caption lines now flow through normal sentence scanning; if they contain a Ch3 positive/quasi-positive claim, the deterministic typed C2 scanner evaluates them. This is intentional fail-closed behavior per the fix evidence residual risk note.

**Verdict: fixed; fail-closed by design.**

### 4. Slice 0 allowed contexts not relaxed

`_ch3_style_claim_allowed()` (line 894-913) is unchanged — it still checks exactly three narrow contexts:
- `_is_required_label_context()`: requires a required label prefix + gap/non-assertive suffix
- `_is_evidence_gap_statement_context()`: requires evidence gap marker + denial, no reversal
- `_is_quote_context()`: requires quoted phrase with introducer, no author conclusion

No new allowed contexts were introduced. No existing context was widened.

**Verdict: no relaxation.**

## Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py
```

Result: `40 passed in 0.72s`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
```

Result: `314 passed in 1.22s`.

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py
```

Result: `All checks passed!`.

## Blocking Findings

无。原 blocking finding 已被正确修复，回归测试覆盖了触发场景，现有 allowed contexts 未被放松。

## Conclusion

原 aggregate deepreview 的唯一 blocking finding 已修复并通过 re-review。fix 收紧了 metadata 行判定逻辑，从 prefix-match 改为 exact standalone marker match（`stripped.endswith("-->")`），同时保持 standalone marker 行的 metadata 免疫和 Slice 0 窄允许上下文不变。证据 caption 行按 fail-closed 设计不再被宽泛跳过。314 项测试全部通过，ruff 无告警。
