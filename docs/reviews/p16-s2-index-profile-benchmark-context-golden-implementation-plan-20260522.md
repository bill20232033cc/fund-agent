# P16-S2 Index Profile Benchmark-context Golden Implementation Plan（2026-05-22）

## Verdict

`RECOMMEND_FUTURE_GOLDEN_IMPLEMENTATION_INDEX_PROFILE_ONLY`

本 gate 只产出 implementation plan。未修改 source code、tests、golden files、README、`docs/design.md`、`docs/implementation-control.md`、selected CSV、RR-13 data、commits、branches、PRs 或外部状态。本 gate 不添加 golden rows。

第一性原理结论：

- 未来 golden implementation 应为 `004194`、`005313`、`017644`、`019918`、`019923` 添加生产 `index_profile` benchmark-context golden rows。
- golden 的对象必须是当前 extractor 实际抽出的 `IndexProfileValue` benchmark-context 形状，而不是人为补齐的单一指数名。
- 五只基金的复合基准都必须保留 `benchmark_identity_status=composite` 与 `benchmark_index_name=null` 的语义；不得把产品名、CSV 名、指数族或 benchmark text 推断成 `benchmark_index_name`。
- 当前 strict golden / comparable 路径只能安全比对标量子字段，不能直接表达 tuple/list，也不能把 JSON `null` 当成 active golden expected value。因此未来 implementation 应 golden 当前可比标量：`benchmark_text`、`benchmark_identity_status`、`methodology_availability`、`constituents_availability`、`source_tier`；并用测试证明 `benchmark_index_name` 在 composite 情况下不进入 comparable/golden 分母且不会被补值。
- 如果 reviewer 或 controller 要求 production golden 完整覆盖 `benchmark_component_text` tuple 或显式 `benchmark_index_name=null` 的逐字段 JSON 断言，则未来 implementation 必须 stop，先设计 golden/comparable null 与 tuple 表达语义，不能在现有 correctness 路径中硬塞。

`tracking_error` 结论：

- 禁止从 P16-S1 结果添加任何 `tracking_error` golden rows。
- 五只基金的 `tracking_error` 均为 `blocked_no_direct_tracking_error`；target/limit text、manager narrative、benchmark-only text、非观察值语言、缺 anchor 或 ambiguous note 都不得进入 production golden。

## Current Truth Inputs

本计划只使用以下输入：

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md`
- `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md`
- `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md`
- `docs/reviews/p16-s1-plan-review-controller-judgment-20260522.md`
- current code facts under `fund_agent/fund/`, `docs/golden-answer-template.md`, `reports/golden-answers/`, and `tests/`

明确排除且未读取、未引用、不得作为事实来源：

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`
- excluded audit inputs

## Baseline Facts

| Fact | Current state |
|---|---|
| Current gate | `P16-S2 index_profile benchmark-context golden implementation plan-review` |
| P16-S1 accepted result | `PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY` |
| Accepted candidates | `004194`、`005313`、`017644`、`019918`、`019923` |
| Actual fund type | all five `classified_fund_type=enhanced_index` |
| Annual-report source | all five EID 2024 annual reports, `fallback_used=False` |
| Accepted evidence | annual-report `§2` benchmark/profile context only |
| Composite shape | all five `benchmark_identity_status=composite`, `benchmark_index_name=null` |
| Source tier | all five `source_tier=benchmark_context` |
| Methodology / constituents | all five `methodology_availability=benchmark_only`, `constituents_availability=benchmark_only` |
| Tracking error | all five `blocked_no_direct_tracking_error` |

## First-principles Decision

### Why Golden Rows Are Useful

P14 made `index_profile` a conditional P1 quality field for `index_fund` and `enhanced_index`. Without selected-fund enhanced-index production golden rows, correctness coverage still leans on `001548` index-fund rows and deterministic fixtures. That under-protects an important product type: enhanced-index funds have the same benchmark-context dependency, and P16-S1 already proved five selected-fund annual reports expose accepted benchmark-context evidence through the production repository/extractor path.

Adding production rows for these five funds improves the quality denominator in the direction the design wants:

- `index_profile` stays in Fund Capability and remains evidence-backed by annual-report `§2`.
- correctness can catch regressions where benchmark text, identity status, source tier, or benchmark-only availability changes.
- enhanced-index coverage becomes production selected-fund coverage, not only fixture coverage.

### Why `benchmark_index_name=null` Is Acceptable

For these five candidates, `benchmark_index_name=null` is not missing evidence in the ordinary sense. It is the current extractor's fail-closed representation for composite benchmarks such as:

```text
指数收益率 * 95% + 存款利率 * 5%
```

The annual report directly supports the full benchmark text and the composite identity. It does not directly support a single canonical `benchmark_index_name` under current extractor semantics. Therefore the safest golden target is the actual current shape:

- full benchmark text is direct evidence;
- identity status is `composite`;
- single index name is intentionally absent;
- methodology and constituents are only `benchmark_only`;
- source tier is `benchmark_context`.

Deferring solely because `benchmark_index_name` is null would weaken the quality denominator and incentivize a worse implementation: inferring a single index name from product names or index-family text. That would violate fail-closed evidence rules.

### Current Comparable / Golden Path Constraint

Current `COMPARABLE_SUB_FIELDS_BY_FIELD["index_profile"]` supports these scalar subfields:

```text
benchmark_text
benchmark_identity_status
benchmark_index_name
benchmark_index_code
methodology_availability
constituents_availability
source_tier
```

Current comparable extraction deliberately drops `None`, tuple/list, dict and set values. Strict golden Markdown also requires non-empty `expected_value`. Therefore:

- `benchmark_component_text` cannot be production-goldened through current correctness without changing comparable semantics.
- `benchmark_index_name=null` cannot be represented as an active strict golden row through current Markdown/JSON schema.
- A future implementation may still preserve null semantics by not adding `benchmark_index_name` rows for these five funds and adding regression tests that composite benchmark rows do not synthesize `benchmark_index_name`.

This is a safe compromise: production golden rows cover the accepted scalar evidence, while tests protect the fail-closed null behavior.

## Scope And Non-goals

### In Scope For Future Implementation

- Add production `index_profile` rows for `004194`、`005313`、`017644`、`019918`、`019923`.
- Add only current extractor benchmark-context scalar fields that are directly supported by P16-S1 evidence.
- Rebuild strict JSON through the existing `golden-build` path.
- Add focused tests for composite benchmark golden correctness and no synthesized `benchmark_index_name`.
- Sync docs only where implementation changes trigger existing README rules.

### Out Of Scope For This Plan Gate

- No source code edits.
- No test edits.
- No golden Markdown/JSON/template edits.
- No README edits.
- No `docs/design.md` or `docs/implementation-control.md` edits.
- No selected CSV or RR-13 edits.
- No commits, branches, PRs, issues, comments, or external state.
- No golden rows in this gate.

### Out Of Scope For Future Golden Implementation

- No `tracking_error` rows from P16-S1 results.
- No calculated tracking error.
- No external index adapters.
- No index methodology extraction.
- No constituents extraction.
- No source/test/golden edits beyond the exact files owned by the future golden implementation.
- No Service/UI/Engine/renderer/quality-gate direct access to PDF cache, concrete annual-report sources, source adapters, download helpers, or external web data.
- No Dayu runtime, Host, Engine, tool loop, LLM audit, E1-E3, or Evidence Confirm execution.

## Proposed Production Rows

Future implementation should append these rows to `reports/golden-answers/golden-answer-prefill-reviewed.md` and rebuild `reports/golden-answers/golden-answer.json`.

### `004194` 招商中证1000指数增强A

| field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `index_profile` | `benchmark_text` | `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `benchmark_identity_status` | `composite` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `methodology_availability` | `benchmark_only` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `constituents_availability` | `benchmark_only` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `source_tier` | `benchmark_context` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |

### `005313` 万家中证1000指数增强A

| field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `index_profile` | `benchmark_text` | `中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `benchmark_identity_status` | `composite` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `methodology_availability` | `benchmark_only` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `constituents_availability` | `benchmark_only` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `source_tier` | `benchmark_context` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |

### `017644` 博道中证1000指数增强A

| field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `index_profile` | `benchmark_text` | `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `benchmark_identity_status` | `composite` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `methodology_availability` | `benchmark_only` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `constituents_availability` | `benchmark_only` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `source_tier` | `benchmark_context` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |

### `019918` 招商中证2000指数增强A

| field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `index_profile` | `benchmark_text` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `benchmark_identity_status` | `composite` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `methodology_availability` | `benchmark_only` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `constituents_availability` | `benchmark_only` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `source_tier` | `benchmark_context` | `high` | `年报2024 §2 page-5 page-5-table-1 benchmark` |

### `019923` 华泰柏瑞中证2000指数增强A

| field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `index_profile` | `benchmark_text` | `中证2000指数收益率×95%＋人民币活期存款税后利率×5%` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `benchmark_identity_status` | `composite` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `methodology_availability` | `benchmark_only` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `constituents_availability` | `benchmark_only` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `index_profile` | `source_tier` | `benchmark_context` | `high` | `年报2024 §2 page-6 page-6-table-0 benchmark` |

Do not add rows for these subfields in this future implementation:

| sub_field | Decision | Reason |
|---|---|---|
| `benchmark_index_name` | do not add row | current value is `null`; strict Markdown requires non-empty expected value; adding a name would be inference |
| `benchmark_index_code` | do not add row | current value is `null`; no accepted direct evidence |
| `benchmark_component_text` | do not add row | tuple/list is not in current comparable whitelist and `_comparable_scalar()` excludes nested values |
| `methodology_summary` | do not add row | methodology extraction is out of scope |
| `methodology_source_title` | do not add row | methodology extraction is out of scope |
| `constituents_summary` | do not add row | constituents extraction is out of scope |
| `constituents_as_of_date` | do not add row | constituents extraction is out of scope |
| `missing_reasons` | do not add row | tuple/list and not user-facing correctness denominator |
| any `tracking_error.*` | prohibited | P16-S1 blocked direct observed disclosure for all five |

## File Ownership For Future Implementation

### Production / Golden Files

| File | Ownership |
|---|---|
| `docs/golden-answer-template.md` | Add empty `index_profile` row scaffolding for the five candidates only if future implementation decides template persistence is required. Do not add `tracking_error` rows. |
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Append reviewed `index_profile` rows listed above. |
| `reports/golden-answers/golden-answer.json` | Rebuild only through existing golden-build path after Markdown edit. |

### Source Files

Default future implementation should not need source changes. Source changes are allowed only if the existing path cannot safely represent the planned rows:

| File | Allowed reason |
|---|---|
| `fund_agent/fund/golden_prefill.py` | Only if template rows need prefill behavior not already supported by dataclass value mapping. |
| `fund_agent/fund/extraction_snapshot.py` | Only if current comparable whitelist behavior has regressed; do not add tuple/null support in this gate without a new reviewed plan. |
| `fund_agent/fund/extraction_score.py` | Only if correctness coverage behavior for current scalar rows has regressed; do not change coverage semantics otherwise. |

### Tests

| File | Required future coverage |
|---|---|
| `tests/fund/test_golden_answer.py` | strict Markdown/JSON accepts the added production rows and rejects empty active `expected_value`. |
| `tests/fund/test_golden_prefill.py` | dataclass prefill still resolves scalar `index_profile` fields; composite fixture should not synthesize `benchmark_index_name`. |
| `tests/fund/test_extraction_snapshot.py` | composite `IndexProfileValue` serializes comparable scalar fields and omits null / tuple fields. |
| `tests/fund/test_extraction_score.py` | correctness for the five future rows is comparable and matched; `benchmark_index_name` absent for composite rows is not treated as matchable expected data. |
| `tests/fund/test_quality_gate.py` or `tests/fund/test_quality_gate_integration.py` | coverage stays non-blocking for absent non-comparable null/tuple rows and catches mismatches on scalar rows. |

### Docs

README sync triggers only after future implementation, not this plan gate:

| Trigger | File |
|---|---|
| `fund_agent/fund/` source behavior changes | `fund_agent/fund/README.md` |
| `tests/` changes | `tests/README.md` |
| golden CLI/user workflow changes | root `README.md` |
| no source/test workflow changes; only golden data rows | no README update required unless existing docs become inaccurate |

Do not update `docs/design.md` or `docs/implementation-control.md` inside the future implementation unless controller explicitly scopes control-doc bookkeeping. This plan does not authorize design/control edits.

## Future Implementation Sequence

1. Reconfirm no source blockers from P16-S1 evidence artifact and controller judgment.
2. Inspect existing `reports/golden-answers/golden-answer-prefill-reviewed.md` structure and append five new fund sections or extend existing sections if already present.
3. Add exactly the planned `index_profile` rows. Preserve source strings from P16-S1 anchors.
4. Do not add `benchmark_index_name`, `benchmark_index_code`, `benchmark_component_text`, or any `tracking_error` row.
5. Rebuild strict JSON using the existing CLI/service path, for example:

```bash
.venv/bin/python -m fund_agent.ui.cli golden-build \
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
```

If the module CLI invocation differs in current environment, use the existing project-supported `golden-build` command without changing semantics.

6. Add focused tests for composite `IndexProfileValue` semantics and correctness matching.
7. Run targeted validation commands.
8. Run `git diff --check HEAD`.
9. Create implementation artifact under `docs/reviews/` summarizing exact rows, JSON rebuild command, tests, and residuals.

## Targeted Validation Commands

Future implementation should run at minimum:

```bash
.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
.venv/bin/python -m pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
.venv/bin/python -m ruff check fund_agent tests
.venv/bin/python -m pytest -q
git diff --check HEAD
```

Optional targeted data validation:

```bash
.venv/bin/python -m fund_agent.ui.cli golden-build \
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
```

Expected future success signals:

- strict JSON contains the five candidate fund codes.
- each candidate has exactly five new `index_profile` rows listed in this plan, unless implementation artifact explains an evidence-backed stop before editing.
- no candidate has `tracking_error` golden rows.
- no candidate has `benchmark_index_name` golden rows.
- correctness comparable rows for the planned scalar subfields match.
- quality gate does not treat absent `benchmark_index_name=null` as a required active golden expected value.
- full tests and ruff pass.
- `git diff --check HEAD` passes.

## Stop Conditions

Future implementation must stop before golden edits if any of these occur:

- current extractor output differs from P16-S1 accepted values for any candidate;
- candidate annual-report identity, fund type, source metadata, or anchor provenance cannot be reconciled to P16-S1 artifact;
- current golden/comparable path cannot represent scalar `index_profile` rows without source changes beyond this plan;
- reviewer/controller requires active golden assertions for `benchmark_component_text` tuple or `benchmark_index_name=null`;
- `golden-build` rejects planned rows or changes unrelated existing records unexpectedly;
- correctness reports `no_comparable_fields` for the planned scalar rows;
- adding rows would require direct PDF/cache/source-adapter access outside `FundDocumentRepository` / `FundDataExtractor`;
- implementation pressure appears to add `tracking_error`, calculated tracking error, external index data, methodology, constituents, or inferred benchmark identity.

When stopped, produce a blocker artifact and do not partially update production golden files.

## Review Rejection Criteria

Reject any future implementation that:

- adds `tracking_error` rows for any P16-S1 candidate;
- treats target/limit text such as annualized tracking-error control thresholds as observed tracking error;
- infers `benchmark_index_name` from product names, CSV names, benchmark family, or external sources;
- changes `benchmark_identity_status=composite` to `identified` for the five composite benchmarks without a separately reviewed extractor-semantics gate;
- adds `benchmark_component_text` rows while the current comparable path still excludes tuple/list values;
- changes source/adapters, PDF cache, repository fallback behavior, Service/UI/Engine/renderer boundaries, or quality-gate severity to make golden rows pass;
- modifies `docs/code_20260519.csv`, RR-13 data, `docs/design.md`, `docs/implementation-control.md`, excluded inputs, commits, branches, PRs, issues, or external state without explicit authorization;
- leaves strict JSON unrebuilt after reviewed Markdown changes;
- omits targeted tests for composite benchmark null/no-synthesis behavior;
- fails `git diff --check HEAD`.

## Residuals

| Residual | Owner | Handling |
|---|---|---|
| Full dataclass tuple/null production golden semantics | future golden/comparable schema phase if selected | Current path cannot active-golden `benchmark_component_text` or `benchmark_index_name=null`; do not force into P16-S2 implementation. |
| `tracking_error` production golden for enhanced-index funds | future evidence gate only after direct observed disclosure | P16-S1 blocked all five candidates; no rows from target/limit/narrative text. |
| Index methodology extraction | future source-contract phase | Current `methodology_availability=benchmark_only` is a boundary marker, not methodology extraction. |
| Constituents extraction | future source-contract phase | Current `constituents_availability=benchmark_only` is a boundary marker, not constituents extraction. |
| Extractor semantics for composite benchmarks | future extractor-semantics phase if product requires a single index name | Do not change in golden implementation. |
| Evidence Confirm / E1-E3 | future audit architecture phase | Out of deterministic golden gate scope. |
| RR-13 duplicate `016492` | user / App source | untouched. |

## Handoff Prompt For Future Implementation

```text
P16-S2 implementation: add production golden correctness rows only for accepted P16-S1 index_profile benchmark-context evidence for 004194, 005313, 017644, 019918, and 019923.

Use current truth inputs: AGENTS.md, docs/design.md, docs/implementation-control.md, docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md, docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md, docs/reviews/p16-s1-code-review-controller-judgment-20260522.md.

Do not read or cite docs/design0522.md, docs/implementation-control0522.md, docs/repo-audit-20260521.md, or excluded audit inputs.

Edit only the owned files required by the P16-S2 plan. Add the planned scalar index_profile rows to reviewed golden Markdown, rebuild strict JSON through golden-build, and add focused tests proving composite benchmark rows keep benchmark_identity_status=composite, do not synthesize benchmark_index_name, and do not add tracking_error rows. Preserve FundDocumentRepository/FundDataExtractor evidence provenance; do not use external adapters, calculated tracking_error, methodology extraction, constituents extraction, source CSV edits, RR-13 edits, commits, branches, PRs, or external state.

Stop without golden edits if the current golden/comparable path cannot safely represent the planned scalar rows, if active null/tuple golden semantics are required, or if any row would require inferred benchmark identity or tracking_error evidence.

Run targeted tests, ruff, full pytest, and git diff --check HEAD. Produce an implementation artifact under docs/reviews with exact changed rows, JSON rebuild result, validation output, residuals, and stop-condition status.
```

## Plan Gate Validation

This plan gate created only:

```text
docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md
```

Required command:

```bash
git diff --check HEAD
```

Result to be recorded after file creation by the planning agent: command completed with no whitespace-error output, exit code `0`.
