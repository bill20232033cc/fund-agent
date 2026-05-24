# Release Maintenance 004393 Quality Gate S1 Code Review - AgentMiMo - 2026-05-24

## Conclusion

`PASS_WITH_FINDINGS`

S1 的 004393 真实抽取路径已经能输出 `basic_identity.management_company / custodian / inception_date`，并从 parser 可见 `§5` 中的 `7.4.10.2.1 / 7.4.10.2.2` 文本抽到 `management_fee=1.20%`、`custody_fee=0.20%`。现有分类、benchmark newline normalization、非指数基金 `index_profile` 行为未被破坏。

但 table fallback 分支没有把候选表限制在 `7.4.10.2` 语义范围内，仍可能从任意包含“管理费/托管费”的表格行抽取第一个百分比。这与 accepted plan / S0 controller judgment 的 “按 `7.4.10.2` subsection/table semantics 搜索” 不完全一致。

## Scope Reviewed

- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/test_extraction_snapshot.py`
- Accepted plan: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- S0 judgment: `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
- S1 implementation artifact: `docs/reviews/release-maintenance-004393-quality-gate-s1-implementation-20260524.md`

## Findings

### Medium - table fallback is not scoped to `7.4.10.2` tables

Evidence:

- `fund_agent/fund/extractors/profile.py:274-306` scans every `report.tables` row in `_extract_fee_from_fallback_tables()`.
- `fund_agent/fund/extractors/profile.py:336-352` accepts a row whenever it contains the subsection number or any loose semantic label such as `管理费` / `托管费`.
- `fund_agent/fund/extractors/profile.py:355-371` then returns the first percentage in that accepted row.
- `fund_agent/fund/extractors/profile.py:396-413` assigns table fallback `section_id` by checking whether `§7`, `§5`, or `§2` exists anywhere in the report, not by locating the candidate table under `7.4.10.2`.

What can go wrong:

When `§2` direct fee labels are missing and the text fallback does not find the subsection text, table fallback can match unrelated tables before the real fee disclosure table. Any row containing `管理费` / `托管费` plus a percentage can become `fee_schedule`, even if that row is not the `7.4.10.2.1 基金管理费` or `7.4.10.2.2 基金托管费` disclosure. This is the same risk class S1 was meant to avoid: extracting a scalar percentage that is not the actual fee rate.

Impact:

The 004393 cached real path currently hits the text fallback first, so this does not break the observed 004393 output. It does leave the table fallback over-broad and can create false P0 `fee_schedule` coverage/correctness for reports where the parser exposes fee rates primarily as tables.

Concrete fix:

Constrain table fallback before extracting a rate:

- Build candidate table windows only from tables whose own row/header text contains `7.4.10.2.1 基金管理费` or `7.4.10.2.2 基金托管费`, or whose table ordinal/page is directly associated with a located `7.4.10.2.x` text offset.
- For management fee, require the same candidate window to contain `7.4.10.2.1` or the exact title `基金管理费`; for custody fee require `7.4.10.2.2` or `基金托管费`.
- Extract the percentage from the formula/rate row, not from arbitrary rows containing `管理费` / `托管费`.
- Derive `section_id` from the located subsection/table association; if parser only exposes containing `§5`, keep `section_id="§5"` but preserve `7.4.10.2.x` in `note` and page/table_id.
- Add regression tests where an earlier unrelated table contains `管理费 ... 3.00%` and the later `7.4.10.2.1` table contains `1.20%`; expected output must be `1.20%`. Add the symmetric custody case.

## Checks

Basic identity:

- PASS. New fields are populated from `§2` labels and anchors include `section_id`, `table_id`, `row_locator`, and note.
- 004393 real extraction produced `management_company=安信基金管理有限责任公司`, `custodian=中国银行股份有限公司`, `inception_date=2022年8月8日`, all anchored to `page-5-table-0`.

Classification / benchmark / index profile:

- PASS. 004393 real extraction remains `classified_fund_type=active_fund`; benchmark normalizes `中债综\n合` to `中债综合`; `index_profile` remains missing with note `非指数基金不适用指数画像`.

Fee fallback:

- PARTIAL. Text fallback correctly avoids `get_section_text("§7")` and finds parser-visible `7.4.10.2` under `§5`.
- FINDING. Table fallback is not sufficiently scoped to `7.4.10.2` table semantics.

Anchors and provenance:

- PASS with residual limitation. The implementation artifact does not overclaim `metadata.source` or fallback/source provenance beyond parser-visible same-source content.
- Text fallback anchors for 004393 have `section_id="§5"` and note `7.4.10.2.x ...`; page/table_id are absent because text fallback won before table fallback. This matches the accepted parser limitation, though future table fallback hardening should keep table page/table_id when table evidence is used.

Tests:

- PASS for required positive coverage: direct priority, partial direct+fallback, no fee, and snapshot comparable fields are covered.
- GAP tied to the finding: no test proves table fallback ignores unrelated `管理费` / `托管费` percentages outside `7.4.10.2`.

Guardrails:

- No Host/Agent package changes.
- No `extra_payload`.
- No direct production PDF/cache/source helper access in implementation.
- New helpers are module-level, not nested.
- New/changed functions and test helpers have Chinese docstrings.

## Verification Run

Commands run during review:

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
git diff --check
```

Results:

- `63 passed`
- `ruff`: all checks passed
- `git diff --check`: passed
