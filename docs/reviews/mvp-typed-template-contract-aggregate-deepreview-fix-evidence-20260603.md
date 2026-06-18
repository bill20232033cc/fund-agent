# MVP typed template contract aggregate deepreview fix evidence

## Worker Self-Check

- Role: controller-applied fix for accepted aggregate deepreview finding.
- Gate: `MVP typed template contract aggregate deepreview`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Source finding: `docs/reviews/code-review-20260603-225446.md`.
- Scope: fix Ch3 typed `must_not_cover` metadata-line bypass only.
- Non-goals preserved: no provider/default/runtime/live probe, no Agent runtime/tool-loop, no score-loop, no template truth replacement, no deterministic default behavior change, no quality/golden/readiness promotion.

## Finding Fixed

Aggregate deepreview found that Ch3 typed `must_not_cover` could be bypassed when a positive or quasi-positive consistency claim appeared on the same line as an allowed anchor marker, for example:

```markdown
<!-- anchor:<allowed_anchor_id> --> 言行一致性判断：言行一致。
```

The old audit path skipped any line whose stripped text started with `<!-- anchor:` or `> 📎 证据：`, so the Ch3 style-claim scanner never inspected trailing body text.

## Fix

- Tightened `_line_is_contract_or_anchor_metadata()` in `fund_agent/fund/chapter_auditor.py`.
- Only standalone `<!-- required_output:... -->` and standalone `<!-- anchor:... -->` comment marker lines are skipped.
- Evidence caption lines are no longer blanket-skipped; if they contain a Ch3 positive/quasi-positive claim, the normal deterministic typed C2 scanner evaluates them.
- Added `test_ch3_positive_claim_after_anchor_marker_blocks_when_actual_behavior_unreviewed()` proving an allowed anchor marker followed by `言行一致` on the same line still emits `programmatic:C2:ch3.must_not_cover.item_04`.

## Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py
```

Result: `40 passed in 0.73s`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
```

Result: `314 passed in 1.36s`.

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py docs/reviews/code-review-20260603-225446.md
```

Result: exited `0`.

## Residual Risk

Future work may add a narrower `anchor_caption` allowed context if there is a concrete need to preserve Ch3 style phrases inside evidence captions. This fix intentionally chooses fail-closed scanning for caption lines so metadata cannot launder body conclusions.
