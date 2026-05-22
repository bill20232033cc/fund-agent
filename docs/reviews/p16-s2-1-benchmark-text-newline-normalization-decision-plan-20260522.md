# P16-S2.1 Benchmark Text Newline Normalization Decision Plan（2026-05-22）

## Verdict

`RECOMMEND_NARROW_BENCHMARK_TEXT_NEWLINE_NORMALIZATION`

本 gate 只产出 decision plan。未修改 source code、tests、golden files、README、`docs/design.md`、`docs/implementation-control.md`、selected CSV、RR-13 data、commits、branches、PRs 或外部状态。

第一性原理结论：未来 implementation 应在 Fund Capability 的 profile extractor `benchmark_text` 路径做窄口径 embedded newline normalization，然后重新执行 P16-S2 golden implementation。不要保留 PDF 表格单元格的原始嵌入换行作为 production golden expected value。

选择 normalization 的原因：

- `benchmark_text` 是给 correctness、snapshot、报告和人工审核共同消费的结构化标量；PDF 表格单元格中的换行是版面换行，不是基金业绩比较基准的语义组成。
- P16-S2 blocker 已证明 `017644` 与 `019918` 的差异只来自当前 production extractor 输出中的嵌入换行，其他 `index_profile` 标量语义仍保持 `composite / benchmark_only / benchmark_context`。
- 现有 strict golden Markdown 是单行表格；`parse_golden_answer_markdown()` 按 `splitlines()` 解析，不能安全表达真实多行 cell。`golden_prefill._escape_markdown_cell()` 也会把换行替换成空格，不能保留 raw newline。
- correctness 比对虽有保守 whitespace normalize，但 golden rows 和 blocker 检查仍需要可读、稳定、同源的 expected string；把 PDF 行折叠 artifact 写入 golden 会制造可读性和 anchor drift。
- normalization 只删除或替换直接来自同一表格 cell 的换行，不引入外部证据、不合成 `benchmark_index_name`，符合 fail-closed evidence rules。

## Truth Inputs Used

本计划只使用以下输入：

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md`
- `docs/reviews/p16-s2-code-review-controller-judgment-20260522.md`
- `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md`
- `docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md`
- current code facts under `fund_agent/fund/extractors/profile.py`
- relevant tests under `tests/fund/`

明确未读取、未引用、不得作为事实来源：

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`
- excluded audit inputs

## Current Facts

| Fact | Current state |
|---|---|
| Active gate | `P16-S2.1 benchmark_text newline normalization decision plan-review` |
| P16-S2 status | blocked before golden edit |
| Blocked funds | `017644`, `019918` |
| Unaffected P16-S2 funds | `004194`, `005313`, `019923` |
| Current extractor path | `profile._build_benchmark()` stores `matched_field.value` as `benchmark_text`; `_build_index_profile()` reuses it through `_benchmark_text()` |
| Table extraction behavior | `_first_non_empty_after()` returns `cell.strip()` and preserves embedded newlines inside a table cell |
| Golden Markdown behavior | table rows are line-based; active `expected_value` must be non-empty single-cell text |
| Golden prefill behavior | `_escape_markdown_cell()` replaces `\n` with a space |
| Correctness behavior | `_normalize_comparable_value()` collapses whitespace before comparison, but P16-S2 stop condition used exact current extractor text vs accepted expected text |
| Evidence boundary | annual report access must stay through `FundDocumentRepository` / `FundDataExtractor`; no direct PDF/cache/source helper access |

P16-S2 blocker facts to preserve:

| fund_code | Accepted no-newline value | Current raw extractor value |
|---|---|---|
| `017644` | `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` | `中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%` |
| `019918` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）\n*5%` |

## Decision

### Recommended Path

Implement benchmark-only newline normalization in `fund_agent/fund/extractors/profile.py`.

The normalization belongs at the `benchmark_text` construction boundary, not in general table parsing, not in snapshot/golden correctness, and not in renderer or quality gate. The future implementation should normalize the matched benchmark value before building both:

- `benchmark.value["benchmark_text"]`
- the benchmark evidence anchor note derived from the same matched benchmark row

This keeps `benchmark` and `index_profile.benchmark_text`同源 and prevents future P16-S2 rows from depending on renderer-, score-, or Markdown-specific cleanup.

### Exact Normalization Rule

Add a private helper in `profile.py`, for example `_normalize_benchmark_text(value: str) -> str`, used only by the benchmark field path.

Required behavior:

- normalize `\r\n`, `\r`, and `\n` inside `benchmark_text`;
- remove newline runs when they are PDF visual wraps inside CJK text or adjacent to benchmark arithmetic punctuation, percent signs, parentheses, or full-width equivalents;
- replace newline runs with one ASCII space only when removing them would merge two ASCII word tokens;
- preserve ordinary non-newline spaces that already exist in the source value;
- trim leading/trailing whitespace;
- do not normalize all fields globally;
- do not normalize methodology, constituents, manager narrative, tracking error, or arbitrary raw section text.

The helper should not alter punctuation variants such as `×` vs `*`, `+` vs `＋`, or `（税后）` vs `(税后)`.

### Rejected Path: Preserve Raw Newlines

Preserving raw embedded newlines is rejected for this gate.

Reasons:

- strict Markdown active rows cannot safely carry a true newline inside `expected_value`; a newline splits the table row and breaks human review locality;
- writing raw multiline expected values directly into JSON would bypass the existing `golden-build` path and create a second golden source of truth;
- replacing newline with a visible Markdown-space artifact would make expected values less faithful than the accepted no-newline benchmark text;
- anchors would point to the same table cell while expected text would include a PDF layout artifact, increasing readability drift without adding evidence.

If a future schema phase wants true multiline golden values, it must first design explicit Markdown/JSON escaping and reviewer display semantics. That is out of P16-S2.1 and P16-S2 implementation scope.

## Future Implementation Ownership

### P16-S2.1 Normalization Implementation

| File | Ownership |
|---|---|
| `fund_agent/fund/extractors/profile.py` | Add benchmark-only newline normalization helper and apply it only to the benchmark matched field before `ExtractedField` creation. Preserve anchors, table IDs, section IDs, and composite benchmark semantics. |
| `tests/fund/extractors/test_profile.py` | Add focused deterministic table-fixture tests for `017644` and `019918` newline shapes, plus unaffected `004194`, `005313`, `019923` no-op shapes. |
| `fund_agent/fund/README.md` | Update only if the extractor behavior description becomes inaccurate; do not add future-looking design text. |
| `tests/README.md` | Update only if test organization or running instructions change. |

No other source files are owned by P16-S2.1 unless implementation discovers the benchmark path is different from current code facts and stops for re-plan.

### Resumed P16-S2 Golden Implementation After Normalization

| File | Ownership |
|---|---|
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Add only the accepted scalar `index_profile` rows after normalized extractor output equals the canonical no-newline values. |
| `reports/golden-answers/golden-answer.json` | Rebuild only through existing `golden-build` path. |
| `tests/fund/test_golden_answer.py` | Cover strict Markdown/JSON acceptance of the rows and rejection of empty active expected values if needed. |
| `tests/fund/test_golden_prefill.py` | Keep scalar dataclass prefill behavior stable; do not synthesize composite `benchmark_index_name`. |
| `tests/fund/test_extraction_snapshot.py` | Verify comparable scalar serialization includes normalized `benchmark_text` and omits null/tuple fields. |
| `tests/fund/test_extraction_score.py` | Verify correctness matching for the planned scalar rows and no active denominator for absent `benchmark_index_name`. |
| `tests/fund/test_quality_gate.py` or `tests/fund/test_quality_gate_integration.py` | Verify quality behavior remains based on scalar comparable rows and does not require null/tuple golden rows. |

## Required Tests

P16-S2.1 normalization tests must include:

- `017644`-shape table cell: `中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%` normalizes to `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%`.
- `019918`-shape table cell: `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）\n*5%` normalizes to `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%`.
- Unaffected `004194` value remains exactly `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%`.
- Unaffected `005313` value remains exactly `中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%`.
- Unaffected `019923` value remains exactly `中证2000指数收益率×95%＋人民币活期存款税后利率×5%`.
- `benchmark_identity_status` remains `composite` for composite benchmark values.
- `benchmark_index_name` remains `None`; no synthesis from product name, CSV name, index family, or benchmark text.
- `benchmark_component_text` behavior is unchanged except for consuming the normalized benchmark text.
- anchor `section_id`, `page_number`, `table_id`, and `row_locator` remain from the original benchmark row.

Production repository verification after tests may use `FundDocumentRepository` / `FundDataExtractor` only. It must not read PDF/cache files directly.

## Validation Plan

P16-S2.1 implementation should run:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
```

If normalization source changes are accepted, resumed P16-S2 golden implementation should additionally run:

```bash
.venv/bin/python -m fund_agent.ui.cli golden-build \
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py -q
.venv/bin/python -m pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
.venv/bin/python -m pytest -q
git diff --check HEAD
```

Optional production evidence check, only through repository/extractor boundaries:

```bash
.venv/bin/python - <<'PY'
import asyncio
from fund_agent.fund.data_extractor import FundDataExtractor

EXPECTED = {
    "004194": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
    "005313": "中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%",
    "017644": "中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%",
    "019918": "中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%",
    "019923": "中证2000指数收益率×95%＋人民币活期存款税后利率×5%",
}

async def main():
    extractor = FundDataExtractor()
    for code, expected in EXPECTED.items():
        bundle = await extractor.extract(code, 2024, force_refresh=False)
        value = bundle.index_profile.value
        assert value is not None
        assert value.benchmark_text == expected
        assert value.benchmark_identity_status == "composite"
        assert value.benchmark_index_name is None
        print(code, "OK")

asyncio.run(main())
PY
```

## Realignment Of P16-S1 / P16-S2 Expected Values

After normalization is implemented and reviewed:

1. Treat the canonical expected `benchmark_text` values for all five candidates as the no-newline strings already listed in the accepted P16-S2 plan.
2. Do not rewrite historical P16-S1 or P16-S2 blocker artifacts; they remain audit history.
3. The P16-S2.1 implementation artifact must record that current production extractor output now matches the canonical no-newline values for `004194`, `005313`, `017644`, `019918`, and `019923`.
4. Resume P16-S2 golden implementation using the same 25 scalar rows from the accepted P16-S2 plan, with no embedded newline expected values.
5. Rebuild strict JSON from reviewed Markdown through `golden-build`.
6. Verify rebuilt JSON preserves pre-existing golden records unchanged, especially existing `001548 index_profile` rows.

## Prohibitions

Future implementation must not:

- add any `tracking_error` rows for the five P16-S1/P16-S2 candidates;
- treat target/limit text, manager narrative, benchmark-only text, or ambiguous text as observed `tracking_error`;
- synthesize `benchmark_index_name` from product names, CSV names, benchmark family, or external sources;
- add `benchmark_component_text` production golden rows while tuple/list semantics remain outside the current comparable path;
- introduce external index adapters, calculated tracking error, methodology extraction, or constituents extraction;
- access PDF/cache/concrete annual-report source helpers directly from Service/UI/Engine/renderer/quality gate;
- bypass `FundDocumentRepository` / `FundDataExtractor` for production annual-report verification;
- edit selected CSV, RR-13 data, `docs/design.md`, `docs/implementation-control.md`, excluded inputs, commits, branches, PRs, issues, comments, or external state;
- use Dayu Host/Engine/tool loop, LLM audit, E1-E3, or Evidence Confirm execution.

## Stop Conditions

Stop before source edits if:

- current code facts differ from this plan's ownership model;
- the newline discrepancy cannot be reproduced from table-cell benchmark values;
- the future implementation would require changing parser internals, repository fallback, source adapters, snapshot schema, or golden schema.

Stop before golden edits if:

- normalized extractor output still differs from canonical no-newline expected values;
- any candidate no longer resolves to the accepted 2024 annual-report identity, `enhanced_index`, or benchmark anchor;
- normalization changes `benchmark_identity_status=composite`, `benchmark_index_name=None`, `methodology_availability=benchmark_only`, `constituents_availability=benchmark_only`, or `source_tier=benchmark_context`;
- `golden-build` cannot rebuild strict JSON without unrelated record churn;
- correctness reports `no_comparable_fields` or mismatches for the planned scalar rows;
- reviewers require active golden rows for `benchmark_index_name=null` or `benchmark_component_text` tuple semantics.

When stopped, produce a blocker artifact and do not partially update production golden files.

## Review Rejection Criteria

Reject any future implementation that:

- normalizes all profile fields or all parsed table cells instead of the benchmark path only;
- removes meaningful non-newline spacing broadly or rewrites punctuation;
- changes source/adapters, PDF cache behavior, repository fallback behavior, Service/UI/Engine/renderer boundaries, or quality-gate severity to make tests pass;
- uses direct PDF/cache/source helper access in production verification;
- adds `tracking_error`, methodology, constituents, external adapter, or calculated index-series behavior;
- infers a single `benchmark_index_name` for composite benchmarks;
- edits design/control documents, selected CSV, RR-13, excluded inputs, branches, PRs, issues, or external state;
- omits focused tests for `017644`, `019918`, and unaffected `004194`, `005313`, `019923`;
- leaves reviewed golden Markdown and strict JSON out of sync after resumed P16-S2;
- fails `git diff --check HEAD`.

## Validation Success Signals

P16-S2.1 succeeds when:

- `017644` and `019918` benchmark texts no longer contain embedded newlines;
- `004194`, `005313`, and `019923` benchmark texts are byte-for-byte unchanged;
- all five candidates remain composite benchmark-context `index_profile` values with no synthesized index name;
- focused profile tests pass;
- snapshot/correctness targeted tests pass or remain unchanged where no source behavior is touched;
- ruff and `git diff --check HEAD` pass;
- implementation artifact records no golden/source CSV/RR-13/design/control/external changes beyond the accepted source/test scope.

Resumed P16-S2 succeeds when:

- strict JSON contains exactly the planned scalar `index_profile` rows for the five candidates;
- no candidate has `tracking_error`, `benchmark_index_name`, `benchmark_index_code`, `benchmark_component_text`, methodology summary, or constituents detail rows;
- pre-existing golden records remain unchanged after rebuild;
- correctness matches the planned scalar rows;
- full tests pass and `git diff --check HEAD` passes.

## Residuals

| Residual | Owner | Handling |
|---|---|---|
| Full tuple/null golden semantics | Future golden/comparable schema phase | Do not force `benchmark_component_text` or `benchmark_index_name=null` into P16-S2. |
| Enhanced-index `tracking_error` production golden | Future evidence gate only after direct observed disclosure | P16-S1/P16-S2 candidates remain blocked for `tracking_error`. |
| Index methodology extraction | Future source-contract phase | Current `methodology_availability=benchmark_only` is only a boundary marker. |
| Constituents extraction | Future source-contract phase | Current `constituents_availability=benchmark_only` is only a boundary marker. |
| Broader PDF table text normalization policy | Future parser/extractor design if needed | P16-S2.1 authorizes only benchmark path normalization. |
| Historical P16-S1/P16-S2 artifact text | Controller history | Do not rewrite; supersede by P16-S2.1 decision and implementation artifact. |

## Future Handoff Prompt

```text
P16-S2.1 implementation: implement narrow newline normalization for profile extractor benchmark_text only, then verify the five P16-S2 enhanced-index candidates.

Use truth inputs: AGENTS.md, docs/design.md, docs/implementation-control.md, docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md, docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md, docs/reviews/p16-s2-code-review-controller-judgment-20260522.md, docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md, docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md, and current code facts under fund_agent/fund/extractors/profile.py and relevant tests.

Do not read or cite docs/design0522.md, docs/implementation-control0522.md, docs/repo-audit-20260521.md, or excluded audit inputs.

Edit only fund_agent/fund/extractors/profile.py and focused tests under tests/fund/extractors/test_profile.py unless a stop condition is triggered. Normalize embedded newlines only in the benchmark_text path before benchmark/index_profile values and anchor notes are built. Preserve ordinary non-newline spaces, punctuation variants, table anchors, benchmark_identity_status=composite, benchmark_index_name=None, benchmark_only availability, and source_tier=benchmark_context.

Add deterministic tests for newline shapes matching 017644 and 019918, plus no-op tests for 004194, 005313, and 019923. Do not add tracking_error rows, synthesize benchmark_index_name, add external adapters, extract methodology/constituents, access direct PDF/cache/source helpers, edit golden files, selected CSV, RR-13, docs/design.md, docs/implementation-control.md, commits, branches, PRs, or external state in this implementation gate.

Run targeted tests, ruff, and git diff --check HEAD. Produce an implementation artifact under docs/reviews with exact source/test changes, production repository/extractor verification if run, residuals, and whether P16-S2 golden implementation may resume.
```

## Plan Gate Validation

Required command:

```bash
git diff --check HEAD
```

Result: pending at initial file creation; planning agent must update this section after running the command.

Final result: exit code `0`, no output.

Additional artifact hygiene checks:

```bash
rg -n "^(<<<<<<<|=======|>>>>>>>)" docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md
rg -n "[ \t]+$" docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md
```

Result: both commands exited `1` with no output, meaning no conflict markers and no trailing whitespace were found.
