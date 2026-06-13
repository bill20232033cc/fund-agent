# 004393 / 2025 Tracked Golden Content Write Plan After Source-body Verification

Date: 2026-06-13

Gate: `004393 / 2025 Tracked Golden Content Write Planning Gate`

Role: planning worker

Status: `PLAN_READY_FOR_REVIEW`

## 1. Goal

Plan a later implementation gate that writes exactly the seven source-body-verified
`004393 / 2025` golden answer rows into tracked golden content.

This plan does not implement the write. It does not edit tracked golden content,
fixtures, source, tests, README, design, control docs, release state, PR state or
external state.

## 2. Planning Self-check

- Current gate / role: `004393 / 2025 Tracked Golden Content Write Planning Gate`; planning worker only.
- Source of truth: `AGENTS.md`, current startup/control docs, accepted Markdown/golden tooling judgment, same-year candidate rows, controlled live EID source-body verification evidence and controller judgment, current tracked reviewed Markdown/JSON, loader/build/preflight code and targeted tests.
- Scope boundary: this artifact is the only file written in this gate. Future write scope is limited below.
- Stop conditions: any fixture promotion, readiness/release claim, live/provider/analyze/checklist/readiness/release/PR command, schema/contract surprise or row set expansion stops the future implementation.
- Evidence and validation: completion signal for this gate is this handoff-ready plan artifact only.

## 3. Accepted Inputs

| Input | Accepted fact used by this plan |
|---|---|
| `docs/current-startup-packet.md` | Current active gate is planning-only; seven source-body-verified candidates may be used; two fee rows must remain excluded; release/readiness remains `NOT_READY`. |
| `docs/implementation-control.md` | Current mainline is this tracked golden content write planning gate after checkpoint `ba0a96a`; no tracked write is accepted yet. |
| `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-implementation-controller-judgment-20260613.md` | Accepted tooling is Markdown-first, year-aware. JSON-only edits are rejected as default tracked write authority. |
| `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md` | Candidate artifact has parser-valid `golden-answer-metadata` with `report_year: 2025` and nine candidate rows. |
| `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-controller-judgment-20260613.md` | Seven rows were accepted as reviewed candidates; `fee_schedule.management_fee` and `fee_schedule.custody_fee` were rejected for this route. |
| `docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-evidence-20260613.md` | The seven rows passed source-body verification through `FundDocumentRepository().load_annual_report("004393", 2025)` with EID single-source/no-fallback metadata. |
| `docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-controller-judgment-20260613.md` | The seven rows are accepted as source-body-verified candidates; two fee rows remain excluded; no `turnover_rate` row was added or verified. |
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Current reviewed Markdown is the tracked human-reviewed source authority and currently contains only legacy 2024 `004393` content. |
| `reports/golden-answers/golden-answer.json` | Current strict JSON has `fund_count=11`, `record_count=150`; current raw JSON is legacy and omits `report_year`, which loader semantics treat as 2024. |
| `fund_agent/fund/golden_answer.py` | Parser/build identity is `fund_code + report_year + field_name + sub_field`; missing Markdown metadata defaults to legacy 2024; build output writes fund-level and record-level `report_year`. |
| `fund_agent/fund/golden_readiness_preflight.py` | Readiness coverage is year-aware and only checks strict JSON coverage; content write alone does not perform fixture promotion or readiness release. |

## 4. Future Implementation Allowed Write Set

The later implementation gate may edit only:

1. `reports/golden-answers/golden-answer-prefill-reviewed.md`
2. `reports/golden-answers/golden-answer.json`
3. `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-evidence-20260613.md`

No source, tests, README, `docs/design.md`, `docs/implementation-control.md`,
`docs/current-startup-packet.md`, fixture promotion manifest, runtime report,
PDF/cache/data directory, release artifact, PR artifact or external state may be
edited by that implementation worker.

Controller status sync, if needed, must be a separate controller-owned gate after
implementation review acceptance.

## 5. Exact Row List Allowed For Write

The future implementation may write exactly these seven active rows under a new
`004393 / 2025` reviewed Markdown fund block and generated JSON fund block:

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `basic_identity` | `fund_name` | `安信企业价值优选混合型证券投资基金` | `high` | `年报2025 §2 page-5 page-5-table-0 fund_name` |
| `basic_identity` | `fund_code` | `004393` | `high` | `年报2025 §2 page-5 page-5-table-0 fund_code` |
| `basic_identity` | `management_company` | `安信基金管理有限责任公司` | `high` | `年报2025 §2 page-5 page-5-table-0 management_company` |
| `basic_identity` | `custodian` | `中国银行股份有限公司` | `high` | `年报2025 §2 page-5 page-5-table-0 custodian` |
| `basic_identity` | `inception_date` | `2022年8月8日` | `high` | `年报2025 §2 page-5 page-5-table-0 inception_date` |
| `product_profile` | `investment_objective` | `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。` | `medium` | `年报2025 §2 page-5 page-5-table-1 investment_objective` |
| `benchmark` | `benchmark_name` | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20%` | `high` | `年报2025 §2 page-5 page-5-table-1 benchmark` |

Explicit exclusions:

- Do not write `fee_schedule.management_fee = 1.20%`.
- Do not write `fee_schedule.custody_fee = 0.20%`.
- Do not write any `turnover_rate` row.
- Do not add skipped rows for `fee_schedule` or `turnover_rate` in the new 2025 block; the new block should contain seven active rows and no skipped rows.
- Do not add deferred candidate rows such as `classified_fund_type`, NAV/benchmark performance, share change, manager alignment, holder structure, holdings, or strategy text.

## 6. Implementation Decisions

### 6.1 Write Target

The write must target both tracked golden content files, but with different
authority:

- Authoritative reviewed content edit: `reports/golden-answers/golden-answer-prefill-reviewed.md`.
- Generated machine-readable artifact: `reports/golden-answers/golden-answer.json`, produced from the reviewed Markdown by `fund-analysis golden-build`.

Rationale:

- Accepted tooling rejects JSON-only writes as default write authority.
- Current loader and preflight semantics consume strict JSON, so generated JSON must also be updated and tracked.
- The reviewed Markdown must carry `golden-answer-metadata` with `report_year: 2025`; source text alone must not be used to infer year.

### 6.2 Markdown Placement And Shape

Add a second `004393` fund block immediately after the existing 2024
`## 004393 安信企业价值优选混合A（国内股票类）` block and before the next fund heading.

The new block must use this shape:

````markdown
## 004393 安信企业价值优选混合A（国内股票类）

```golden-answer-metadata
report_year: 2025
```

Source-body verification provenance: `docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-evidence-20260613.md`; EID single-source/no-fallback; `source=eid`; `selected_source=eid`; `source_mode=single_source_only`; `fallback_enabled=false`; `fallback_used=false`; `report_code=FB010010`; `upload_info_id=1447922`; `upload_info_detail_id=1494773`; `parsed_cache_hit=true`; long text rows preserve normalized expected values from the accepted verification artifact.

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 安信企业价值优选混合型证券投资基金 | high | 年报2025 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 004393 | high | 年报2025 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 安信基金管理有限责任公司 | high | 年报2025 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 中国银行股份有限公司 | high | 年报2025 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2022年8月8日 | high | 年报2025 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。 | medium | 年报2025 §2 page-5 page-5-table-1 investment_objective |
| benchmark | benchmark_name | 沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20% | high | 年报2025 §2 page-5 page-5-table-1 benchmark |
````

If Markdown rendering cannot represent the nested code fence in an editing
context, use the same literal text from this section; do not alter the row values.

### 6.3 JSON Generation And Expected Canonicalization

Run the accepted public build path after the Markdown edit:

```bash
uv run fund-analysis golden-build \
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
```

Expected stdout after the write:

```text
golden_answer: reports/golden-answers/golden-answer.json
funds: 12
records: 157
skipped: 29
```

Important expected diff behavior:

- The new `004393 / 2025` fund block adds seven records.
- Because current accepted build tooling writes explicit `report_year`, the generated JSON may also canonicalize existing legacy 2024 funds/records by adding `report_year: 2024`.
- That canonicalization is acceptable only if loader-normalized non-target record identities, expected values, confidence and source are unchanged.
- Manual JSON editing is prohibited except via the generated output from `golden-build`.

## 7. Implementation Slices

### Slice S1 - Reviewed Markdown Content Write

Objective: add the new reviewed Markdown block with exactly seven active
`004393 / 2025` rows and provenance note.

Allowed files:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`

Prerequisites:

- Confirm the existing file still has one legacy `004393` heading and no existing `004393 / 2025` metadata block.
- Stop if a `004393` block with `report_year: 2025` already exists.

Exact changes:

- Insert the block from §6.2 immediately after the existing 2024 `004393` table section.
- Preserve existing 2024 rows byte-for-byte except the unavoidable insertion location.
- Do not edit any other fund block.
- Do not add fee rows, turnover rows, skipped fee rows or skipped turnover rows to the new 2025 block.

Validation:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown; funds=parse_golden_answer_markdown(Path('reports/golden-answers/golden-answer-prefill-reviewed.md').read_text(encoding='utf-8')); target=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(target)==1; rows={(r.field_name,r.sub_field): r for r in target[0].records}; assert len(rows)==7; assert set(rows)=={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert target[0].skipped_fields==(); assert all(r.report_year==2025 for r in target[0].records); print('markdown_004393_2025_rows_ok')"
```

Stop conditions:

- Parser rejects the Markdown.
- More or fewer than seven active `004393 / 2025` rows are parsed.
- Any excluded fee or turnover row is parsed as active or skipped.
- Existing 2024 rows change beyond insertion context.

### Slice S2 - Generate Strict JSON From Reviewed Markdown

Objective: regenerate `reports/golden-answers/golden-answer.json` from the
reviewed Markdown using the accepted build path.

Allowed files:

- `reports/golden-answers/golden-answer.json`

Prerequisites:

- S1 validation passed.

Exact changes:

- Run the `uv run fund-analysis golden-build ...` command in §6.3.
- Do not manually patch JSON.
- Do not run `golden-prefill`, `extraction-snapshot`, `extraction-score`, `quality-gate`, `golden-readiness-preflight`, `analyze`, `checklist`, live EID/network/PDF/FDR/provider/LLM/readiness/release/PR commands.

Validation:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; funds=load_golden_answer_json(Path('reports/golden-answers/golden-answer.json')); target=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(funds)==12; assert sum(len(f.records) for f in funds)==157; assert len(target)==1; rows={(r.field_name,r.sub_field): r for r in target[0].records}; assert len(rows)==7; assert set(rows)=={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert target[0].skipped_fields==(); assert all(r.report_year==2025 for r in target[0].records); print('json_004393_2025_rows_ok')"
```

Stop conditions:

- Build command fails.
- JSON loader rejects the generated file.
- JSON fund count is not 12 or record count is not 157.
- New 2025 row set differs from §5.
- Any excluded fee or turnover row appears under `(004393, 2025)`.

### Slice S3 - Non-target Preservation And Gate Evidence

Objective: prove the write only adds the approved seven rows and accepted build
canonicalization, then record implementation evidence.

Allowed files:

- `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-evidence-20260613.md`

Exact checks:

- Compare `HEAD:reports/golden-answers/golden-answer.json` and working-tree JSON through `load_golden_answer_json()`.
- For every loader-normalized key except the seven new `(004393, 2025, field, sub_field)` keys, assert `expected_value`, `confidence` and `source` are unchanged.
- Assert no old key disappeared.
- Assert the only new keys are the seven keys in §5.
- Assert raw generated JSON has fund-level and record-level `report_year` for the new 2025 block.
- Record whether build canonicalized legacy 2024 `report_year` fields as an expected generated-output effect, not a semantic content change.

Suggested validation script:

```bash
uv run python -c "import json, subprocess; from dataclasses import asdict; from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; old_path=Path('/tmp/old-golden-answer.json'); old_path.write_bytes(subprocess.check_output(['git','show','HEAD:reports/golden-answers/golden-answer.json'])); new_path=Path('reports/golden-answers/golden-answer.json'); old_records={(r.fund_code,r.report_year,r.field_name,r.sub_field): asdict(r) for f in load_golden_answer_json(old_path) for r in f.records}; new_records={(r.fund_code,r.report_year,r.field_name,r.sub_field): asdict(r) for f in load_golden_answer_json(new_path) for r in f.records}; allowed={('004393',2025,'basic_identity','fund_name'),('004393',2025,'basic_identity','fund_code'),('004393',2025,'basic_identity','management_company'),('004393',2025,'basic_identity','custodian'),('004393',2025,'basic_identity','inception_date'),('004393',2025,'product_profile','investment_objective'),('004393',2025,'benchmark','benchmark_name')}; assert set(new_records)-set(old_records)==allowed; assert set(old_records)-set(new_records)==set(); assert all(new_records[k]==old_records[k] for k in old_records); raw=json.loads(new_path.read_text(encoding='utf-8')); target=[f for f in raw['funds'] if f['fund_code']=='004393' and f.get('report_year')==2025]; assert len(target)==1; assert all(r.get('report_year')==2025 for r in target[0]['records']); print('non_target_preservation_ok')"
```

Implementation evidence artifact must include:

- current branch and `git status --short`;
- changed files;
- exact row list written;
- build command output;
- validation command outputs;
- confirmation that fee rows and `turnover_rate` are absent for `004393 / 2025`;
- residuals and next gate recommendation;
- explicit statement that no fixture promotion, readiness/release, PR/push/merge or external state action occurred.

Stop conditions:

- Non-target preservation check fails.
- Any unplanned file changes appear.
- Evidence artifact cannot classify residuals.

## 8. Validation Matrix

Run these commands in the future implementation gate after S1/S2:

```bash
uv run fund-analysis golden-build \
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
```

Expected: exit 0; stdout shows `funds: 12`, `records: 157`, `skipped: 29`.

```bash
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
```

Expected: pass. Existing tests cover Markdown metadata, build output, duplicate identity, same fund across years, loader legacy defaults and year-aware preflight coverage behavior.

```bash
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
```

Expected: pass. This checks touched-contract-adjacent Python files even though no Python edits are expected.

```bash
git diff --check
```

Expected: no output.

Additional mandatory assertions:

- Markdown parser sees exactly one `(004393, 2025)` fund block.
- Strict JSON loader sees exactly one `(004393, 2025)` fund block.
- New `(004393, 2025)` active row set is exactly the seven rows in §5.
- No `(004393, 2025, fee_schedule, management_fee)`.
- No `(004393, 2025, fee_schedule, custody_fee)`.
- No `(004393, 2025, turnover_rate, *)`.
- Existing loader-normalized non-target records have unchanged values, confidence and source.

Do not run:

- live EID/network/PDF/FDR/provider/LLM commands;
- `fund-analysis analyze`;
- `fund-analysis checklist`;
- `fund-analysis extraction-snapshot`;
- `fund-analysis extraction-score`;
- `fund-analysis quality-gate`;
- `fund-analysis golden-readiness-preflight`;
- release/readiness/PR/push/merge commands.

## 9. Non-goals

- No fixture promotion or fixture promotion state edit.
- No readiness or release claim.
- No MVP/release-ready claim.
- No PR, push, merge, mark-ready, approval or external issue/comment action.
- No live source access, source fallback expansion, Eastmoney/fund-company/CNINFO access, provider call, LLM call, PDF/cache/data directory inspection or direct filesystem corpus access.
- No schema, public contract, FQ0-FQ6, quality gate, extraction score, preflight, Service/UI/Host/Agent runtime or Dayu boundary change.
- No fee row clarification.
- No `turnover_rate` applicability change.
- No addition of other deferred 2025 rows.
- No README/design/control-doc update inside the implementation worker scope.

## 10. Rollback And Residual Handling

Rollback before review acceptance:

- If S1 fails before JSON generation, revert only the new Markdown block.
- If S2/S3 fails, revert only `reports/golden-answers/golden-answer-prefill-reviewed.md` and `reports/golden-answers/golden-answer.json` to the pre-slice state, then record the failure in the implementation evidence artifact.
- Do not clean unrelated untracked files.
- Do not use broad destructive commands.
- Do not stage or commit after a failed validation.

Residuals after a successful write:

| Residual | Owner | Destination |
|---|---|---|
| Fixture promotion remains unresolved and year-blind. | Fixture promotion owner | Separate fixture promotion design/evidence gate. |
| Content write does not prove score/quality/readiness pass. | Release owner / quality owner | Separate non-live score/quality/readiness evidence gates if authorized. |
| Source-body verification used parsed cache, not fresh-fetch proof. | Evidence owner | Preserve as provenance context; fresh-fetch proof requires separate gate if needed. |
| Long text rows depend on PDF whitespace normalization. | Golden content/evidence owner | Already preserved in provenance note; future locator stability gate only if needed. |
| Fee rows remain excluded. | Golden contract/source owner | Separate fee-row contract/source-owner clarification gate if needed. |
| `turnover_rate` remains non-applicable for this 2025 route. | Quality/scoring owner | Separate applicability gate only if policy changes. |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup only. |

## 11. Stop Conditions

The future implementation worker must stop and return control to the controller
without committing, pushing or opening PR if any of these occur:

- A `004393 / 2025` block already exists in tracked reviewed Markdown or JSON.
- Any row outside the seven in §5 is needed to satisfy parser/build validation.
- Fee rows or `turnover_rate` appear necessary, requested, or accidentally parsed.
- `golden-build` changes schema version, identity semantics, output shape, or count behavior beyond expected 2024 report-year canonicalization plus seven new rows.
- Non-target loader-normalized records differ in expected value, confidence or source.
- Tests fail for reasons not directly explained by this content addition.
- Any implementation requires source/test/runtime/README/design/control-doc edits.
- Any fixture promotion, readiness/release, live/provider/analyze/checklist/readiness/release/PR/push/merge action becomes necessary.
- Any local PDF/data/cache directory inspection appears necessary.
- Dirty worktree ownership becomes unclear.

## 12. Docs Decision

No README, `docs/design.md`, `docs/implementation-control.md`,
`docs/current-startup-packet.md`, package README or tests README update is part of
the implementation worker scope.

Reason: the future implementation is a tracked golden content data update using
already accepted Markdown/golden tooling and loader semantics. It does not change
user commands, public interfaces, schema contracts, module boundaries, template
chapter structure, source policy, quality gate semantics or test procedure.

Controller may later update control/startup docs only after implementation review
acceptance, under a separate controller status-sync boundary.

## 13. Next Gate Recommendation

Recommended next gate after plan review/re-review acceptance:

```text
004393 / 2025 Tracked Golden Content Write Implementation Gate
```

Implementation handoff should assign S1-S3 exactly as written here and must not
ask the worker to redesign row identity, write target, build path, fixture
promotion, readiness/release path or validation scope.

After successful implementation review and accepted local checkpoint, recommended
later gates remain:

1. Fixture promotion year-aware design/evidence gate.
2. Strict golden 2025 score/quality evidence gate, only if separately authorized.
3. Release/readiness rollup gate, only after content and promotion residuals have accepted dispositions.
