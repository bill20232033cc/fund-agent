# Fund Processor/Extractor S2 DataExtractor Integration Planning Gate

> Date: 2026-06-18
> Role: planning worker only
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration Planning Gate
> Classification: standard implementation planning
> Artifact status: handoff-ready, code-generation-ready, not implementation

## Verdict

S2_PLAN_READY_FOR_REVIEW_NOT_READY

本计划可进入 review gate。不得据此直接实现、替换生产 parser、消费 Docling/FundDisclosureDocument 候选 JSON、声明 source truth/full field correctness/golden/readiness/release，或执行 live/source acquisition/PDF/FDR/Docling conversion/provider/LLM/analyze/checklist/golden/readiness/release 命令。

## Scope And Non-goals

Scope:

- 规划把 S1 `FundProcessorRegistry` / `ActiveFundAnnualProcessor` 接入 `FundDataExtractor.extract()` 默认 façade 的最小实现 slice。
- 规划 active fund annual report 的 processor-mediated bundle projection，使已覆盖字段从 `FundProcessorResult.field_families` 投影到现有 `StructuredFundDataBundle`。
- 保持 `FundDocumentRepository` 仍是年报访问唯一入口；保持 NAV provider / typed NAV repository 的当前降级语义。
- 明确非 active fund、bond-specific evidence、`index_profile` 和候选中间态的 residual owner。
- 给出 exact write set、验证矩阵、review 检查点和停止条件。

Non-goals:

- 不实现代码，不修改生产 parser，不改变 EID single-source policy、fallback 分类、source acquisition、provider/runtime/config、repair budget、annual-period route、quality gate 或 readiness/release 状态。
- 不让 Service/UI/Host/renderer/quality gate/LLM prompt/模板直接消费 Docling、pdfplumber full JSON、EID HTML render、PDF cache 或 parser helper。
- 不引入 `FundDisclosureDocument`、Docling candidate、pdfplumber candidate、EID HTML render candidate 的生产消费路径。
- 不把 S1/S2 processor 输出解释为 source truth、full-document correctness、parser replacement、golden promotion 或 release proof。
- 不重构 `StructuredFundDataBundle` public contract；S2 是接入与投影 slice，不是新报告 schema gate。

## Current Evidence

- `AGENTS.md` 要求生产年报 PDF 访问必须经过 `FundDocumentRepository`，结构化基金字段提取必须通过 Fund 层 Processor/Extractor 边界。
- `docs/reviews/fund-processor-extractor-architecture-plan-20260617.md` 已接受首个实现方向：`fund_agent/fund/processors/` 提供 registry、contract、active annual processor，首 slice 包装现有窄 extractor，不做 parser replacement。
- S1 已落地：
  - `fund_agent/fund/processors/contracts.py` 定义 `FundProcessorDispatchKey`、`FundProcessorInput`、`FundFieldFamilyResult`、`FundProcessorResult` 和 fail-closed gap 语义。
  - `fund_agent/fund/processors/registry.py` 定义 `FundProcessorRegistry.create_default()`，可解析默认 active annual processor。
  - `fund_agent/fund/processors/active_annual.py` 支持 `active_fund + annual_report + parsed_annual_report.v1`，输出第 1-6 章六个字段族。
- 当前 `fund_agent/fund/data_extractor.py` 仍直接调用 `extract_profile()`、`extract_performance()`、`extract_manager_ownership()`、`extract_holdings_share_change()`，再组装 `StructuredFundDataBundle`；它尚未使用 registry。
- 当前 `FundDataExtractor.extract()` 还负责：
  - repository failure 不吞掉。
  - NAV provider failure 降级为 `nav_unavailable`。
  - 非债券基金不扫描 bond risk evidence groups。
  - 债券基金使用 typed NAV repository 计算 drawdown stress。
  - 从 `ParsedAnnualReport.metadata.source` 投影 public source provenance。
- 当前 processor 只能覆盖 active fund annual parsed report；不能覆盖 bond-specific risk evidence、non-active fund processors 或 candidate intermediates。

## First-principles Decision

S2 的目标不是新增 parser route，也不是扩大字段覆盖率。真实目标是把现有“隐式窄 extractor 编排”迁移到一个可测试的 Fund-owned Processor/Extractor 边界，让上层继续拿到现有 `StructuredFundDataBundle`，但 active fund 已覆盖字段不再由 façade 直接组装自散落的窄 extractor。

因此 S2 采用窄接入：

- `FundDataExtractor` 仍通过 `FundDocumentRepository.load_annual_report()` 获得 `ParsedAnnualReport`。
- `FundDataExtractor` 先用当前 `extract_profile()` 做基金类型 bootstrap；这是 S2 的临时分类桥，不是新字段来源策略。
- 当分类结果为 `active_fund` 时，构造 `FundProcessorDispatchKey` 并通过 registry 解析 processor。
- active fund 已覆盖字段必须从 `FundProcessorResult.field_families` 投影到 bundle；不得静默 fallback 到原直接窄 extractor 组装同一字段。
- 非 active fund 在 S2 保留当前 direct extractor path，并记录为 explicit residual；不能为了满足边界口号让 bond/index/QDII/FOF 路径回归或失败。
- Candidate intermediates 仍不可进入 production façade。

该方案承认一次 bootstrap profile extraction 与 processor 内部 profile extraction 的短期重复。重复只发生在已加载的 in-memory `ParsedAnnualReport` 上，不重复 source/PDF/cache/network/provider/LLM 访问；后续可由 S3 precomputed extraction context 或 profile-classifier processor gate 消除。

## Required Implementation Shape

### Constructor Injection

修改 `FundDataExtractor.__init__()`：

- 新增可选参数 `processor_registry: FundProcessorRegistry | None = None`。
- 默认值为 `FundProcessorRegistry.create_default()`。
- 仅保存 registry；不得在构造函数中解析 processor、访问 repository、访问 source、访问 Docling 或执行 I/O。

### Active Fund Processor Path

在 `FundDataExtractor.extract()` 中：

1. 保持先加载 annual report，再加载 NAV data 的现有顺序。
2. 调用 `extract_profile(report)` 只用于：
   - 读取 `basic_identity`。
   - 调用 `_classified_fund_type()`。
   - 保留 `index_profile` 这类 S1 processor 未覆盖字段的 temporary projection。
3. 当 `classified_fund_type == "active_fund"`：
   - 构造 `FundProcessorDispatchKey(fund_type="active_fund", report_type="annual_report", intermediate_kind="parsed_annual_report.v1", source_kind=<public source kind>, document_year=report.key.year, fund_code=report.key.fund_code)`。
   - 用 registry `resolve()` 获取 processor；unsupported 必须作为实现缺陷或 typed fail-closed exception 暴露，不能静默回到 direct path。
   - 构造 `FundProcessorInput`，传入 `report` 与 `project_public_source_provenance(report.metadata.source)`。
   - 调用 processor `extract()`。
   - 若 result 为 `unsupported` 或 `blocked`，S2 必须 fail closed；不得返回 direct extractor bundle。
   - 从 `FundProcessorResult.field_families` 投影 bundle 字段。

### Bundle Projection Rules

新增私有 helper，建议名称：

- `_active_processor_result_to_bundle(...) -> StructuredFundDataBundle`
- `_field_from_family(...) -> ExtractedField[...]`
- `_field_family_by_id(...) -> dict[FundFieldFamilyId, FundFieldFamilyResult]`

投影规则：

- `product_essence.v1`:
  - `basic_identity`
  - `product_profile`
  - `benchmark`
  - `risk_characteristic_text`
- `return_attribution.v1`:
  - `fee_schedule`
  - `nav_benchmark_performance`
  - `tracking_error`，仍必须经过 `_tracking_error_for_fund_type()`。
- `manager_profile.v1`:
  - `portfolio_managers`
  - `turnover_rate`
  - `manager_alignment`
  - `manager_strategy_text`
  - `holdings_snapshot`
- `investor_experience.v1`:
  - `investor_return`
  - `holder_structure`
  - `share_change`
- `core_risk.v1`:
  - 可作为 `risk_characteristic_text` fallback only if `product_essence.v1` lacks that field and core_risk has a public value; otherwise do not merge multiple family values implicitly.
- `index_profile`:
  - S1 processor 未覆盖；S2 可继续使用 bootstrap `profile_result.index_profile`，但必须在 implementation artifact residual 中记录。
- `bond_risk_evidence`:
  - 对 active fund 继续调用 `extract_bond_risk_evidence()`，应返回 `not_applicable_non_bond_fund`；不得扫描 bond-specific groups。

每个从 family value 投影出的 `ExtractedField` 必须：

- 保留 value。
- 使用该 `FundFieldFamilyResult.anchors`。
- 将 accepted/partial family 映射到可用字段；缺失字段映射为 `extraction_mode="missing"` 且 note 包含 source family/gap。
- 不把 `candidate_boundary` 或 candidate status 写成 production proof。

### Non-active Fund Path

S2 保留当前 direct extraction branch 用于：

- `index_fund`
- `enhanced_index`
- `bond_fund`
- `qdii_fund`
- `fof_fund`
- unclassified fund type

该 branch 必须被封装为私有 helper，例如 `_extract_bundle_direct_legacy_path(...)`，并在 docstring 中明确：

- 这是 S2 residual path。
- 仅为避免 S2 对未实现 processor 的基金类型造成行为回归。
- 不授权 Service/UI/Host/renderer/quality gate 直接消费 parser/candidate internals。
- 后续每个基金类型 processor 需要独立 planning/implementation gate。

### Fail-closed Rules

- active fund registry unsupported、processor blocked、input type mismatch、unsafe source provenance：fail closed，不走 legacy direct path。
- repository failure：保持向上抛出，不被 NAV 或 processor 捕获吞掉。
- NAV provider failure：保持当前 `nav_unavailable` 降级。
- bond drawdown typed NAV failure：保持当前 weak/missing evidence 语义。
- candidate intermediate：S2 不构造、不接收、不消费；如测试注入 candidate key，应保持 unsupported/blocked 或 constructor/type guard。

## Exact Write Set For Implementation Gate

Allowed implementation files:

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md` only if implementation changes documented Fund package current behavior.
- `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md`

Allowed optional test-only helper edits:

- None by default. If existing fixtures are insufficient, implementation worker may extend only `tests/fund/test_data_extractor.py`.

Forbidden write set:

- `fund_agent/fund/documents/candidates/**`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/sources/**`
- `fund_agent/service/**`
- `fund_agent/host/**`
- `fund_agent/agent/**`
- `fund_agent/render/**`
- `fund_agent/quality/**`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `.gitignore`
- `reports/**`
- `docs/archive/**`
- untracked residue paths classified by `docs/reviews/post-merge-untracked-residue-disposition-20260618.md`

If implementation discovers the exact write set is insufficient, stop and write a blocker note; do not expand scope silently.

## Required Tests

Run and record:

- `uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py`
- `uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py`
- `git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md`

Add or update focused tests:

- active fund `FundDataExtractor.extract()` uses processor registry path and still returns the same public bundle fields.
- custom registry unsupported active fund fails closed instead of falling back to direct extractor path.
- NAV provider failure still degrades without blocking annual-report extraction.
- repository failure still propagates and NAV provider is not called.
- non-bond active fund still does not scan bond evidence groups.
- bond fund path remains current direct branch and keeps typed NAV drawdown behavior unchanged.
- source provenance still projects from `ParsedAnnualReport.metadata.source`.

Do not run live/source/PDF/FDR/Docling/provider/LLM/analyze/checklist/golden/readiness/release commands.

## Review Checklist

Reviewers must verify:

- S2 does not import candidate internals into Service/UI/Host/renderer/quality gate/LLM/template paths.
- active fund covered fields are actually sourced from `FundProcessorResult`, not silently reassembled from direct extractor calls.
- active fund processor failure does not fallback to legacy direct path.
- non-active branch is explicitly residual and behavior-preserving.
- No repository/source/cache/PDF/Docling/network/provider/LLM calls were added inside processor code.
- No extra_payload or implicit parameter bag was introduced.
- `NOT_READY`, candidate-only and no parser replacement boundaries remain intact.

## Residuals After S2

- Non-active fund processors are not implemented.
- `index_profile` is still projected from bootstrap profile extraction because S1 processor field families do not cover it.
- Active path temporarily duplicates in-memory profile extraction for classification and processor extraction.
- No `FundDisclosureDocument` / Docling candidate / pdfplumber candidate / EID HTML render candidate production processor is authorized.
- No source truth, full field correctness, golden promotion, release readiness or parser replacement is proven.

## Stop Condition

Implementation worker stops after:

1. Code/tests/conditional Fund README update within exact write set.
2. Focused tests and static checks recorded.
3. Implementation evidence artifact written.
4. `git status --short` captured.

Do not push, open PR, merge, run live commands, delete/ignore/archive residue, or advance readiness/release without the next explicit gate authorization.
