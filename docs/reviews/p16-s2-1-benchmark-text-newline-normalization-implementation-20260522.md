# P16-S2.1 Benchmark Text Newline Normalization Implementation（2026-05-22）

## Verdict

`IMPLEMENTED_READY_TO_RESUME_P16_S2_GOLDEN`

本 gate 已按 accepted plan 和 controller judgment 完成窄口径 `benchmark_text` 换行规范化实现。未触发 stop condition。

## Changed Files

| File | Change |
|---|---|
| `fund_agent/fund/extractors/profile.py` | 在 profile extractor 的 benchmark 构造边界新增业绩比较基准专用换行规范化；基于 frozen `_MatchedField` 创建新对象，不原地 mutation；在 `benchmark.value["benchmark_text"]` 与 benchmark anchor note 构造前同步应用。 |
| `tests/fund/extractors/test_profile.py` | 增加 5 个目标形态的聚焦测试，覆盖 `017644` / `019918` 换行清理、`004194` / `005313` / `019923` 不变、anchor note 规范化、composite 语义和 benchmark-only/source-tier 语义保持。 |
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-implementation-20260522.md` | 本实现记录。 |

未更新 `fund_agent/fund/README.md` 或 `tests/README.md`，因为本次没有改变公开 Fund 包契约、测试组织或运行方式。

## Implementation Notes

- normalization 只在 `_build_benchmark()` 路径调用，不改 `_first_non_empty_after()`、表格通用解析、snapshot、score、renderer、quality gate 或 annual-report source/repository 行为。
- `_normalize_benchmark_matched_field()` 会返回新的 `_MatchedField`，使 `benchmark_text` 和 `EvidenceAnchor.note` 消费同一份规范化值；原 frozen `_MatchedField` 不被修改。
- 换行规则只处理 `\r\n`、`\r`、`\n` 及其紧邻的横向空白：
  - 两侧都是 ASCII 字母/数字时替换成一个 ASCII 空格；
  - 其他情况删除换行片段；
  - 保留非换行 ordinary spacing 和 `×` / `*` / `+` / `＋` / `（税后）` / `(税后)` 等标点变体。
- 未合成 `benchmark_index_name`，未新增 tracking error、外部 adapter、methodology/constituents 抽取、PDF/cache/source helper 直连或 golden rows。

## Required Case Results

| fund_code | Result |
|---|---|
| `004194` | `benchmark_text` 保持 `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` |
| `005313` | `benchmark_text` 保持 `中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` |
| `017644` | `中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%` 规范化为 `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` |
| `019918` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）\n*5%` 规范化为 `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` |
| `019923` | `benchmark_text` 保持 `中证2000指数收益率×95%＋人民币活期存款税后利率×5%` |

所有 5 个形态均保持：

- `benchmark_identity_status=composite`
- `benchmark_index_name=None`
- `methodology_availability=benchmark_only`
- `constituents_availability=benchmark_only`
- `source_tier=benchmark_context`
- benchmark anchor 的 `section_id`、`page_number`、`table_id`、`row_locator` 来自原 benchmark row

## Validation

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q
```

Result: `22 passed in 0.39s`

```bash
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
```

Result: `32 passed in 0.46s`

```bash
.venv/bin/python -m ruff check fund_agent tests
```

Result: `All checks passed!`

```bash
git diff --check HEAD
```

Result: passed with no output.

## Production Boundary Verification

Executed through `FundDataExtractor` only, with `force_refresh=False`; no direct PDF/cache/source helper access.

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
        assert value.benchmark_text == expected, (code, value.benchmark_text)
        assert value.benchmark_identity_status == "composite", code
        assert value.benchmark_index_name is None, code
        print(code, "OK")

asyncio.run(main())
PY
```

Result:

```text
004194 OK
005313 OK
017644 OK
019918 OK
019923 OK
```

## Stop Condition Status

No stop condition triggered.

- No scope expansion beyond allowed files plus implementation artifact.
- No golden files changed.
- No selected CSV, RR-13 data, commits, branches, PRs, issues, comments, external state, `docs/design.md`, or `docs/implementation-control.md` changes.
- Excluded inputs `docs/design0522.md`, `docs/implementation-control0522.md`, and `docs/repo-audit-20260521.md` were not read or cited.

## Resume Decision

P16-S2 golden implementation may resume. Canonical expected `benchmark_text` values for `004194`、`005313`、`017644`、`019918`、`019923` are now matched by current production extractor output without embedded newlines.
