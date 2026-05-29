# MVP Gate 1 ChapterFactProvider typed projection implementation evidence

日期：2026-05-30

角色：Gateflow implementation specialist。本文只记录 accepted plan `docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md` 的实现证据；未提交、未 push、未创建 PR。

## Scope

实现范围严格停在 MVP Gate 1 ChapterFactProvider typed projection：

- 新增 Fund 层 typed projection：`StructuredFundDataBundle -> ChapterFactProjection`
- 新增 public API：`project_chapter_facts(...)` 与 concrete `ChapterFactProvider.project(...)`
- 只消费现有 `StructuredFundDataBundle`、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE API
- 不修改 golden fixtures/answers/manifests、score/snapshot/quality gate/final judgment、CLI、Service、Host/Agent/dayu、pyproject 或 lockfile

## Changed Files

- `fund_agent/fund/chapter_facts.py`
  - 新增 `chapter_fact_projection.v1` dataclass contract
  - 新增章节字段映射、基金类型 unknown 语义、facet/lens/ITEM_RULE 投影、fact/anchor/missing reason 投影
  - 支持 `ExtractedField`、`NavDataResult` 三态和 `bond_risk_evidence` 组级 anchor 保留策略
- `tests/fund/test_chapter_facts.py`
  - 新增 13 个 deterministic tests
  - 覆盖 plan 和两份 plan review 的 non-blocking 建议
- `fund_agent/fund/README.md`
  - 最小同步 Fund 当前 public capability：`project_chapter_facts()` / `ChapterFactProvider.project()`
- `tests/README.md`
  - 最小同步新测试模块和运行命令
- `docs/design.md`
  - 最小同步 Route C Gate 1 中 `ChapterFactProvider` typed projection 已成为 Fund 层代码事实，同时保留 writer/auditor/orchestrator/Service/dayu 未实现边界
- `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md`
  - 本 evidence artifact

## Contract

- Schema version：`chapter_fact_projection.v1`
- Public entrypoints：
  - `project_chapter_facts(bundle, *, chapter_ids=DEFAULT_CHAPTER_FACT_IDS) -> ChapterFactProjection`
  - `ChapterFactProvider().project(bundle, *, chapter_ids=DEFAULT_CHAPTER_FACT_IDS) -> ChapterFactProjection`
- 同步函数：未引入 async API
- `fund_type`：
  - 有效值窄化为 `FundType` 后才传给 `resolve_preferred_lens()` / `evaluate_template_item_rules()`
  - 缺失或非法值投影为 `unknown`，并跳过 lens/item rule 有效路径
- facet：
  - 当前没有 exact structured evidence 时 `facets=()`
  - compatible catalog labels 只进入 `non_asserted_facets`
  - ITEM_RULE 调用固定使用 `facets=()`，不传 candidate facets
- anchors：
  - 章节内稳定 ID、去重、fact refs 校验
  - fact anchor refs 均必须存在于同章 `evidence_anchors`
  - `bond_risk_evidence.value.anchors` 保留在 value 内，不展开为普通 `ChapterEvidenceAnchor`
- source kind：
  - projection 层 source kind 扩展允许 `unknown`，用于 extractor source kind 闭集外兜底

## Validation Results

全部 required validation 已完成并通过：

```text
uv run pytest tests/fund/test_chapter_facts.py -q
13 passed in 0.75s
```

```text
uv run pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/test_data_extractor.py -q
35 passed in 0.75s
```

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
972 passed in 4.67s
Required test coverage of 50% reached. Total coverage: 91.64%
fund_agent/fund/chapter_facts.py: 97% coverage
```

## No-source / No-LLM / No-dayu Proof

Implementation import surface in `fund_agent/fund/chapter_facts.py` is limited to:

- Python stdlib: `hashlib`, `json`, `dataclasses`, `typing`
- Fund typed data already in memory: `StructuredFundDataBundle` and `NavDataResult` under `TYPE_CHECKING`
- extractor models: `EvidenceAnchor`, `ExtractedField`
- template truth APIs: `get_chapter_contract`, `resolve_preferred_lens`, `evaluate_template_item_rules`
- `FundType`

Static AST import isolation test verifies no imports containing:

```text
documents, repository, cache, pdf, source, downloader, parser, service, dayu, openai, llm
```

Runtime tests use in-memory fixtures only. No repository, PDF/cache/source helper, downloader, parser, LLM, Service, Host or dayu path is imported or called by the projection module.

## Reviewer Suggestions Addressed

- `_ChapterFieldSpec not_applicable_when` inconsistency resolved by not adding static `not_applicable_when`; not-applicable is derived from runtime field note and field name.
- Added valid chapter id happy paths for `(0,)`, `(7,)`, and full `0..7`.
- Added `ChapterFactProvider.project()` smoke equivalence test.
- Added `NavDataResult` available / empty missing / unavailable three-state test.
- Added `bond_risk_evidence` group anchors kept in value and not expanded test.
- Added type narrowing comment before calling strict `FundType` template APIs.
- Added projection-layer `unknown` source kind documentation and test.
- Added AST import isolation test.

## Residual Risks

- `ChapterFactEntry.value` remains intentionally broad as `object | None`, matching accepted plan and current heterogeneous bundle fields. Later writer/auditor gates should narrow per-consumer needs.
- Exact subtype facet assertion is deliberately empty until a future structured field stores exact subtype evidence. This avoids fail-open guessing but means Route C writer must treat `non_asserted_facets` as explanatory only.
- `bond_risk_evidence` group-level anchors are not expanded into `ChapterEvidenceAnchor`; future gates needing per-group chapter anchor navigation should implement a dedicated expansion contract.
