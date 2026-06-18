# 004393 / 2025 Tracked Golden Content Write Implementation Evidence

Date: 2026-06-13

Gate: `004393 / 2025 Tracked Golden Content Write Implementation Gate`

Role: implementation worker

Status: `IMPLEMENTATION_READY_FOR_REVIEW`

## 1. Scope

Implemented only accepted plan S1-S3:

1. added one reviewed Markdown block for `004393 / 2025`;
2. regenerated strict JSON through `fund-analysis golden-build`;
3. recorded implementation evidence and preservation checks.

No fixtures, source, tests, runtime behavior, README, design/control docs,
release/readiness state, PR state or external state were changed.

## 2. Branch And Workspace

Command:

```bash
git branch --show-current
```

Result:

```text
feat/mvp-llm-incomplete-run-artifacts
```

Command:

```bash
git status --short
```

Result before writing this evidence artifact:

```text
 M reports/golden-answers/golden-answer-prefill-reviewed.md
 M reports/golden-answers/golden-answer.json
?? docs/audit/
?? docs/learning-roadmap.md
?? docs/next-development-phaseflow.md
?? docs/reviews/audit-disposition-phaseflow-reconciliation-controller-judgment-20260610.md
?? docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md
?? docs/reviews/mvp-post-eid-artifact-disposition-controller-judgment-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-inventory-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-review-ds-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-startup-judgment-20260609.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-controller-judgment-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-ds-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-mimo-20260606.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-evidence-20260608.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-mimo-review-20260608.md
?? docs/reviews/mvp-small-golden-set-matched-source-retained-excerpt-fixture-planning-prep-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260609.md
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/plan-review-20260609-071706.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/reviews/repo-review-20260609-130307.md
?? docs/reviews/repo-review-20260609-165959.md
?? docs/reviews/repo-review-20260611-231358.md
?? docs/reviews/workspace-ownership-reconciliation-20260531.md
?? docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md
?? docs/tmux-agent-memory-store.md
?? reports/live-evidence/
?? reports/manual-llm-smoke/
?? reviews/
?? scripts/claude_mimo_simple.py
?? "\345\237\272\351\207\221\345\271\264\346\212\245/"
?? "\345\256\232\346\200\247\345\210\206\346\236\220\346\250\241\346\235\277.md"
```

The untracked residue shown above existed outside this implementation scope and
was not touched.

## 3. Baseline Amendment

Command before editing:

```bash
uv run fund-analysis golden-build --input-path reports/golden-answers/golden-answer-prefill-reviewed.md --output-path /tmp/golden-answer-baseline-004393-2025.json
```

Result:

```text
golden_answer: /tmp/golden-answer-baseline-004393-2025.json
funds: 11
records: 150
skipped: 29
```

Baseline counts:

```text
baseline_funds=11
baseline_records=150
baseline_skipped=29
```

Post-write counts:

```text
post_write_funds=12
post_write_records=157
post_write_skipped=29
skipped_delta=0
```

## 4. Accepted Rows Written

The new Markdown block includes `golden-answer-metadata` with
`report_year: 2025` and this provenance text:

```text
Source-body verification provenance: docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-evidence-20260613.md; EID single-source/no-fallback; source=eid; selected_source=eid; source_mode=single_source_only; fallback_enabled=false; fallback_used=false; report_code=FB010010; upload_info_id=1447922; upload_info_detail_id=1494773; parsed_cache_hit=true; long text rows preserve normalized expected values from the accepted verification artifact.
```

Rows written:

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `basic_identity` | `fund_name` | `安信企业价值优选混合型证券投资基金` | `high` | `年报2025 §2 page-5 page-5-table-0 fund_name` |
| `basic_identity` | `fund_code` | `004393` | `high` | `年报2025 §2 page-5 page-5-table-0 fund_code` |
| `basic_identity` | `management_company` | `安信基金管理有限责任公司` | `high` | `年报2025 §2 page-5 page-5-table-0 management_company` |
| `basic_identity` | `custodian` | `中国银行股份有限公司` | `high` | `年报2025 §2 page-5 page-5-table-0 custodian` |
| `basic_identity` | `inception_date` | `2022年8月8日` | `high` | `年报2025 §2 page-5 page-5-table-0 inception_date` |
| `product_profile` | `investment_objective` | `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。` | `medium` | `年报2025 §2 page-5 page-5-table-1 investment_objective` |
| `benchmark` | `benchmark_name` | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20%` | `high` | `年报2025 §2 page-5 page-5-table-1 benchmark` |

Explicit exclusions preserved:

- `fee_schedule.management_fee`
- `fee_schedule.custody_fee`
- `turnover_rate`
- skipped fee rows
- skipped turnover rows
- deferred rows such as fund type, NAV/benchmark performance, manager alignment,
  holder structure, holdings, share change and strategy text

## 5. Build And Validation Results

Markdown parse check:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown; funds=parse_golden_answer_markdown(Path('reports/golden-answers/golden-answer-prefill-reviewed.md').read_text(encoding='utf-8')); target=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(target)==1; rows={(r.field_name,r.sub_field): r for r in target[0].records}; assert len(rows)==7; assert set(rows)=={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert target[0].skipped_fields==(); assert all(r.report_year==2025 for r in target[0].records); print('markdown_004393_2025_rows_ok')"
```

Result:

```text
markdown_004393_2025_rows_ok
```

Build command:

```bash
uv run fund-analysis golden-build --input-path reports/golden-answers/golden-answer-prefill-reviewed.md --output-path reports/golden-answers/golden-answer.json
```

Result:

```text
golden_answer: reports/golden-answers/golden-answer.json
funds: 12
records: 157
skipped: 29
```

JSON load check:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; funds=load_golden_answer_json(Path('reports/golden-answers/golden-answer.json')); target=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(funds)==12; assert sum(len(f.records) for f in funds)==157; assert len(target)==1; rows={(r.field_name,r.sub_field): r for r in target[0].records}; assert len(rows)==7; assert set(rows)=={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert target[0].skipped_fields==(); assert all(r.report_year==2025 for r in target[0].records); forbidden={('fee_schedule','management_fee'),('fee_schedule','custody_fee'),('turnover_rate','')}; assert not ({('fee_schedule','management_fee'),('fee_schedule','custody_fee')} & set(rows)); assert all(r.field_name!='turnover_rate' for r in target[0].records); print('json_004393_2025_rows_ok')"
```

Result:

```text
json_004393_2025_rows_ok
```

Non-target JSON preservation:

```bash
uv run python -c "import json, subprocess; from dataclasses import asdict; from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; old_path=Path('/tmp/old-golden-answer-004393-2025.json'); old_path.write_bytes(subprocess.check_output(['git','show','HEAD:reports/golden-answers/golden-answer.json'])); new_path=Path('reports/golden-answers/golden-answer.json'); old_records={(r.fund_code,r.report_year,r.field_name,r.sub_field): asdict(r) for f in load_golden_answer_json(old_path) for r in f.records}; new_records={(r.fund_code,r.report_year,r.field_name,r.sub_field): asdict(r) for f in load_golden_answer_json(new_path) for r in f.records}; allowed={('004393',2025,'basic_identity','fund_name'),('004393',2025,'basic_identity','fund_code'),('004393',2025,'basic_identity','management_company'),('004393',2025,'basic_identity','custodian'),('004393',2025,'basic_identity','inception_date'),('004393',2025,'product_profile','investment_objective'),('004393',2025,'benchmark','benchmark_name')}; assert set(new_records)-set(old_records)==allowed; assert set(old_records)-set(new_records)==set(); assert all(new_records[k]==old_records[k] for k in old_records); raw=json.loads(new_path.read_text(encoding='utf-8')); target=[f for f in raw['funds'] if f['fund_code']=='004393' and f.get('report_year')==2025]; assert len(target)==1; assert all(r.get('report_year')==2025 for r in target[0]['records']); print('non_target_preservation_ok')"
```

Result:

```text
non_target_preservation_ok
```

Non-target Markdown preservation:

```bash
python3 -c "import subprocess; from pathlib import Path; old=subprocess.check_output(['git','show','HEAD:reports/golden-answers/golden-answer-prefill-reviewed.md']).decode('utf-8'); new=Path('reports/golden-answers/golden-answer-prefill-reviewed.md').read_text(encoding='utf-8'); heading='\n## 004393 安信企业价值优选混合A（国内股票类）'; first=new.find(heading); second=new.find(heading, first+1); end=new.find('\n## 000216 华安黄金ETF联接A（黄金类）', second); assert first!=-1 and second!=-1 and end!=-1; reconstructed=new[:second]+new[end:]; assert reconstructed==old; print('markdown_non_target_preservation_ok')"
```

Result:

```text
markdown_non_target_preservation_ok
```

Raw JSON canonicalization check:

```bash
python3 -c "import json, subprocess; from pathlib import Path; old=json.loads(subprocess.check_output(['git','show','HEAD:reports/golden-answers/golden-answer.json']).decode('utf-8')); new=json.loads(Path('reports/golden-answers/golden-answer.json').read_text(encoding='utf-8')); old_fund_year=sum(1 for f in old['funds'] if 'report_year' in f); new_fund_year=sum(1 for f in new['funds'] if 'report_year' in f); old_record_year=sum(1 for f in old['funds'] for r in f['records'] if 'report_year' in r); new_record_year=sum(1 for f in new['funds'] for r in f['records'] if 'report_year' in r); print(f'raw_report_year_counts old_funds={old_fund_year} new_funds={new_fund_year} old_records={old_record_year} new_records={new_record_year}')"
```

Result:

```text
raw_report_year_counts old_funds=0 new_funds=12 old_records=0 new_records=157
```

This is the accepted generated-output effect from `golden-build`: legacy 2024
records are loader-normalized unchanged while raw JSON now carries explicit
fund-level and record-level `report_year`.

Post-write parsed counts:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown, load_golden_answer_json; md=parse_golden_answer_markdown(Path('reports/golden-answers/golden-answer-prefill-reviewed.md').read_text(encoding='utf-8')); js=load_golden_answer_json(Path('reports/golden-answers/golden-answer.json')); md_skipped=sum(len(f.skipped_fields) for f in md); js_skipped=sum(len(f.skipped_fields) for f in js); print(f'markdown funds={len(md)} records={sum(len(f.records) for f in md)} skipped={md_skipped}'); print(f'json funds={len(js)} records={sum(len(f.records) for f in js)} skipped={js_skipped}')"
```

Result:

```text
markdown funds=12 records=157 skipped=29
json funds=12 records=157 skipped=29
```

Targeted tests:

```bash
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
```

Result:

```text
..................................                                       [100%]
34 passed in 0.72s
```

Ruff:

```bash
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
```

Result:

```text
All checks passed!
```

Diff whitespace check:

```bash
git diff --check
```

Result: no output, exit 0.

Changed tracked files:

```bash
git diff --name-only
```

Result:

```text
reports/golden-answers/golden-answer-prefill-reviewed.md
reports/golden-answers/golden-answer.json
```

This evidence artifact is an allowed new untracked review file in the accepted
write set.

## 6. Changed Files

Allowed write set used:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-evidence-20260613.md`

`git diff --stat` for tracked content files:

```text
 .../golden-answer-prefill-reviewed.md              |  20 +
 reports/golden-answers/golden-answer.json          | 449 ++++++++++++++++++++-
 2 files changed, 467 insertions(+), 2 deletions(-)
```

## 7. Residuals And Stop Conditions

Residuals:

- The seven rows are written as tracked golden content but still require
  review/controller acceptance before being treated as fully accepted strict
  golden truth.
- Fixture promotion remains unresolved and was not attempted.
- This content write does not prove score, quality, readiness, release or PR
  readiness.
- Source-body verification provenance still records `parsed_cache_hit=true`,
  not fresh-fetch proof.
- Fee rows and `turnover_rate` remain excluded.

Stop conditions encountered:

- None.

Boundary confirmation:

- No fixture promotion command was run.
- No live/provider/LLM/analyze/checklist/readiness/release/PR command was run.
- No PDF/data directory was inspected.
- No source/test/runtime behavior file was modified.
- No stage, commit, push, PR, cleanup, delete, move or archive action occurred.
