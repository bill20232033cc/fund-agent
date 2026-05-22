# P16-S2 Index Profile Benchmark-context Golden Implementation（2026-05-22）

## Verdict

`BLOCKED_BEFORE_GOLDEN_EDIT_EXTRACTOR_TEXT_DIFF`

本 implementation gate 已按 stop condition 停止，未修改 production golden Markdown、strict JSON、source code、tests、README、selected CSV、RR-13、commits、branches、PRs、issues 或外部状态。

阻断原因：golden 编辑前通过 `FundDocumentRepository` 读取 2024 年报并用当前 production `extract_profile()` 复核五只基金 `index_profile` 输出时，`017644` 与 `019918` 的当前 `benchmark_text` 原始值含有嵌入换行，和已接受 P16-S1 计划要求保留的精确 benchmark text 不一致。计划明确要求当前 extractor 输出不同于 P16-S1 值时，必须 stop before golden edits。

## Scope Executed

| Item | Result |
|---|---|
| 读取 implementation plan | completed |
| 读取 controller judgment | completed |
| 检查工作区状态 | completed |
| 使用生产仓库入口复核 extractor 输出 | completed |
| 编辑 golden Markdown | not executed |
| rebuild `golden-answer.json` | not executed |
| 添加/更新 tests | not executed |
| 更新 README | not executed |

未读取或引用排除输入：`docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md` 或 excluded audit inputs。

## Stop-condition Evidence

复核命令：

```bash
.venv/bin/python - <<'PY'
import asyncio
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.extractors import extract_profile

EXPECTED = {
    "004194": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
    "005313": "中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%",
    "017644": "中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%",
    "019918": "中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%",
    "019923": "中证2000指数收益率×95%＋人民币活期存款税后利率×5%",
}

async def main():
    repo = FundDocumentRepository()
    for code, expected_text in EXPECTED.items():
        report = await repo.load_annual_report(code, 2024, force_refresh=False)
        profile = extract_profile(report).index_profile
        value = profile.value
        if value is None:
            print(code, "VALUE_NONE")
            continue
        anchor = profile.anchors[0] if profile.anchors else None
        print("|".join([
            code,
            str(value.benchmark_text),
            str(value.benchmark_identity_status),
            str(value.benchmark_index_name),
            str(value.benchmark_index_code),
            str(value.methodology_availability),
            str(value.constituents_availability),
            str(value.source_tier),
            str(value.benchmark_component_text),
            f"年报{anchor.document_year} {anchor.section_id} page-{anchor.page_number} {anchor.table_id} {anchor.row_locator}" if anchor else "NO_ANCHOR",
            "TEXT_OK" if value.benchmark_text == expected_text else "TEXT_DIFF",
        ]))

asyncio.run(main())
PY
```

结果摘要：

| fund_code | current extractor `benchmark_text` | expected P16-S1 text | status |
|---|---|---|---|
| `004194` | `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` | same | `TEXT_OK` |
| `005313` | `中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` | same | `TEXT_OK` |
| `017644` | `中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%` | `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` | `TEXT_DIFF` |
| `019918` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）\n*5%` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` | `TEXT_DIFF` |
| `019923` | `中证2000指数收益率×95%＋人民币活期存款税后利率×5%` | same | `TEXT_OK` |

All five current extractor outputs still preserve:

- `benchmark_identity_status=composite`
- `benchmark_index_name=None`
- `benchmark_index_code=None`
- `methodology_availability=benchmark_only`
- `constituents_availability=benchmark_only`
- `source_tier=benchmark_context`

But the two text diffs are enough to block this gate because the plan requires exact P16-S1 benchmark text punctuation/anchors and also requires stopping when extractor output differs.

## Golden Edit Status

No planned rows were added.

Explicitly not added:

- no `benchmark_index_name` rows
- no `benchmark_index_code` rows
- no `benchmark_component_text` rows
- no methodology or constituents detail rows
- no `missing_reasons` rows
- no `tracking_error` rows

`reports/golden-answers/golden-answer-prefill-reviewed.md` and `reports/golden-answers/golden-answer.json` were not rebuilt or edited in this gate.

## Validation

Commands run before this artifact:

```bash
sed -n '1,240p' docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md
sed -n '1,240p' docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md
git status --short
rg -n "golden-answer|golden build|golden-build|prefill|index_profile|004194|005313|017644|019918|019923" tests reports/golden-answers fund_agent -g '!docs/design0522.md' -g '!docs/implementation-control0522.md' -g '!docs/repo-audit-20260521.md'
sed -n '240,520p' docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md
sed -n '450,500p' fund_agent/ui/cli.py
sed -n '1,240p' fund_agent/fund/golden_answer.py
sed -n '1,280p' tests/fund/test_golden_answer.py
sed -n '1040,1150p' tests/fund/test_extraction_score.py
sed -n '1,220p' fund_agent/fund/data_extractor.py
rg -n "FundDocumentRepository|FundDataExtractor\(|extract\(" tests fund_agent docs/reviews -g '!docs/reviews/*0522.md'
sed -n '1,260p' tests/fund/test_extraction_snapshot.py
sed -n '1,280p' tests/fund/test_golden_prefill.py
sed -n '1,180p' fund_agent/fund/extractors/models.py
sed -n '1,140p' fund_agent/fund/extraction_snapshot.py
sed -n '500,620p' fund_agent/fund/extraction_snapshot.py
sed -n '1,220p' tests/fund/test_quality_gate_integration.py
sed -n '1,320p' tests/fund/test_quality_gate.py
.venv/bin/python - <<'PY'
# extractor stop-condition check shown above
PY
```

Result:

- plan/controller review completed;
- golden-build command shape confirmed in `fund_agent/ui/cli.py`;
- current comparable path confirmed to support the planned scalar subfields only;
- stop-condition extractor check exited `0` and reported `TEXT_DIFF` for `017644` and `019918`;
- golden-build, targeted tests, ruff, and full pytest were intentionally not run after stop because no golden/source/test implementation proceeded.

Artifact creation后补充验证：

```bash
rg -n "^(<<<<<<<|=======|>>>>>>>)" docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md
```

Result: exit code `1`，无输出；未发现 conflict marker。

```bash
rg -n "[ \t]+$" docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md
```

Result: exit code `1`，无输出；未发现行尾空白。

```bash
git diff --check HEAD
```

Result: exit code `0`，无输出。

```bash
git status --short
```

Result:

```text
?? docs/design0522.md
?? docs/implementation-control0522.md
?? docs/repo-audit-20260521.md
?? docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md
```

```bash
git diff -- reports/golden-answers/golden-answer-prefill-reviewed.md reports/golden-answers/golden-answer.json tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py
```

Result: exit code `0`，无输出；确认 golden 和 targeted tests 未被修改。

## Changed Files

Only this implementation artifact was created:

```text
docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md
```

Pre-existing untracked excluded files remain untouched:

```text
docs/design0522.md
docs/implementation-control0522.md
docs/repo-audit-20260521.md
```

## Residuals

| Residual | Owner | Handling |
|---|---|---|
| Decide whether current extractor should preserve embedded line breaks or normalize benchmark table text before goldening | next reviewed extractor/golden plan | This gate cannot silently normalize P16-S1 rows or edit extractor behavior. |
| Production golden rows for five enhanced-index funds | future implementation after text discrepancy is resolved | Add only the 25 scalar rows once current extractor output and accepted values agree. |
| Tuple/null golden semantics for `benchmark_component_text` and `benchmark_index_name=None` | future golden/comparable schema phase | Still out of scope for P16-S2. |
| `tracking_error` production golden | future evidence gate only after direct observed disclosure | No rows from P16-S1 candidates. |
