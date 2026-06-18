# Fund Processor/Extractor S2 DataExtractor Integration Plan Review (AgentDS)

> Date: 2026-06-18
> Role: AgentDS independent adversarial plan reviewer
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration Planning Gate
> Classification: standard plan review
> Review target: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md`
> Artifact status: review only, not implementation, not readiness

## Verdict

**PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY**

本计划可进入 implementation gate。8 项强制审查问题全部通过，没有阻塞性问题。存在 6 项非阻塞发现需要在 implementation gate 中注意，1 项 needs-more-evidence 建议在 implementation 前或中澄清。

本审查没有实现代码、没有修改源文件/测试/control docs、没有提交、没有推送、没有打开 PR、没有进入 implementation。本审查不声明 code-generation-readiness；那是下一个 gate 的裁决权限。

## Mandatory Review Questions

### Q1: FundDocumentRepository boundary and direct parser/candidate consumption guard

**PASS**

证据：
- Plan `Scope And Non-goals` 明确“保持 `FundDocumentRepository` 仍是年报访问唯一入口”（line 22）
- Non-goals 禁止 Service/UI/Host/renderer/quality gate/LLM prompt/模板直接消费 Docling/pdfplumber/EID HTML render/PDF cache/parser helper（lines 28-29）
- 实现形态中 `FundDataExtractor` 仍通过 `repository.load_annual_report()` 获取 `ParsedAnnualReport`（line 56）
- Constructor 不得访问 repository/source/Docling/I/O（line 73）
- Forbidden write set 排除 `fund_agent/fund/documents/candidates/**`、`fund_agent/service/**`、`fund_agent/host/**`、`fund_agent/render/**`、`fund_agent/quality/**`、`fund_agent/agent/**`（lines 176-188）
- Review checklist 要求验证 S2 不 import candidate internals 到 Service/UI/Host/renderer/quality gate/LLM/template 路径（line 218）

当前代码证据：`AGENTS.md:75-79` 要求生产年报 PDF 访问必须经过 `FundDocumentRepository`，结构化提取必须通过 Fund 层 Processor/Extractor 边界。Plan 完全遵守。

### Q2: active_fund integration avoids silent fallback to direct extractors on processor failure

**PASS**

证据：
- Line 86: registry `resolve()` 失败“必须作为实现缺陷或 typed fail-closed exception 暴露，不能静默回到 direct path”
- Line 89: 若 result 为 `unsupported` 或 `blocked`，“S2 必须 fail closed；不得返回 direct extractor bundle”
- Lines 155-156: fail-closed rules 明确“active fund registry unsupported、processor blocked、input type mismatch、unsafe source provenance：fail closed，不走 legacy direct path”

当前代码证据：`registry.py:123-127` 中 `resolve()` 在无匹配 processor 时抛出 `UnsupportedFundProcessorError`（LookupError 子类）。`active_annual.py:246-263` 中 `extract()` 在 `supports()` 失败或类型不匹配时返回 `blocked`/`unsupported` 结果，不吞错误。Plan 的 S2 规则正确继承了 S1 的 fail-closed 语义。

### Q3: Bootstrap classification strategy acceptability and residual explicitness

**PASS** (with nonblocking note — see Finding 3)

证据：
- Lines 57-58: “FundDataExtractor 先用当前 `extract_profile()` 做基金类型 bootstrap；这是 S2 的临时分类桥，不是新字段来源策略”
- Lines 63-64: “该方案承认一次 bootstrap profile extraction 与 processor 内部 profile extraction 的短期重复。重复只发生在已加载的 in-memory `ParsedAnnualReport` 上，不重复 source/PDF/cache/network/provider/LLM 访问”
- Lines 230-231: residual 明确记录“Active path temporarily duplicates in-memory profile extraction for classification and processor extraction”

策略在 S2 是可接受的：bootstrap 与 processor 都基于同一份 `ParsedAnnualReport` 内存对象，不产生重复 I/O。Residual 已显式记录并路由到 S3 precomputed extraction context 消除。唯一注意点是 bootstrap 分类结果与 processor 内部 `supports()` 判断之间的一致性未被显式验证（见 Finding 3）。

### Q4: Bundle projection from FundProcessorResult to StructuredFundDataBundle detail sufficiency

**PASS** (with nonblocking notes — see Findings 4, 5)

证据：
- Lines 94-132: 给出了六个字段族到 bundle 字段的完整映射表，包括 core_risk→risk_characteristic_text 的 fallback 规则、index_profile 的临时策略、bond_risk_evidence 的保留路径
- 每个投影字段必须保留 value、anchors、extraction_mode
- 缺失字段映射为 `extraction_mode="missing"` 且 note 包含 source family/gap
- 命名了三个私有 helper：`_active_processor_result_to_bundle`、`_field_from_family`、`_field_family_by_id`

投影规则覆盖了所有 `StructuredFundDataBundle` 字段，每个字段都有明确的来源归属（processor field family 或 bootstrap/legacy path）。实现细节层面有两个小缺口（见 Findings 4, 5），但不阻塞实现。

当前代码证据：`StructuredFundDataBundle` 的字段定义在 `data_extractor.py:181-237`。`FundFieldFamilyResult.value` 是 `dict[str, object]`，包含 `schema_version` 和具体字段名键（如 `basic_identity`）。投影 helper 需要从该 dict 中按字段名取值，plan 的 detail level 足以指导实现，不会产生 hidden behavior。

### Q5: Non-active fund behavior, NAV degradation, repository failure, bond risk evidence, source provenance, NOT_READY, candidate-only, no parser replacement preservation

**PASS**

证据（逐一核对）：

- **非 active fund 行为**：Lines 137-153 保留当前 direct extraction branch 用于 index/enhanced/bond/qdii/fof/unclassified，封装为 `_extract_bundle_direct_legacy_path()`，明确标注为 S2 residual path
- **NAV 降级**：Line 157 “NAV provider failure：保持当前 `nav_unavailable` 降级”
- **Repository 失败传播**：Line 156 “repository failure：保持向上抛出，不被 NAV 或 processor 捕获吞掉”
- **债券风险证据**：Lines 126-127 对 active fund 继续调用 `extract_bond_risk_evidence()`，应返回 `not_applicable_non_bond_fund`
- **债券 drawdown**：Line 158 “bond drawdown typed NAV failure：保持当前 weak/missing evidence 语义”
- **Source provenance**：Lines 87, 210 明确从 `ParsedAnnualReport.metadata.source` 投影，要求测试验证
- **NOT_READY**：贯穿全文，non-goals（lines 26-31）、residuals（lines 226-233）、stop condition（lines 235-243）
- **Candidate-only**：Lines 132-133 “不把 `candidate_boundary` 或 candidate status 写成 production proof”；line 159 “candidate intermediate：S2 不构造、不接收、不消费”
- **No parser replacement**：Non-goals line 27 “不修改生产 parser”；forbidden write set lines 176-190

当前代码证据：`data_extractor.py:291-295` repository 异常直接向上抛出；`data_extractor.py:425-431` NAV 失败降级为 `nav_unavailable`；`data_extractor.py:372-373` 非债券基金早退。Plan 完全保留了所有现有生产行为。

### Q6: Exact write set sufficiency and non-broadness

**PASS**

证据：
- Lines 163-168: allowed 文件列表精确到 4 个路径（其中 README 为条件更新）
- Lines 176-190: forbidden write set 覆盖所有不应触碰的生产路径、文档、配置
- Line 192: “If implementation discovers the exact write set is insufficient, stop and write a blocker note; do not expand scope silently”

写入集恰好覆盖了需要修改的最小文件集合：`data_extractor.py`（唯一需要改动的生产文件）、`test_data_extractor.py`（对应测试）、可选的 README 同步。Forbidden set 正确排除了 repository、sources、candidates、Service/Host/Agent/UI/quality gate、design/control docs 以及未经 disposition 的 residue。

### Q7: Required tests sufficiency for regression and boundary violation detection

**PASS** (with nonblocking note — see Finding 6)

证据：
- Lines 196-210: 7 项聚焦测试覆盖了核心 boundary：active fund processor path、fail-closed、NAV 降级、repository 传播、非债券扫描、债券路径、source provenance
- Lines 198-201: 要求运行现有 processor 测试和 data_extractor 测试全套，加 ruff 和 git diff 检查
- 测试矩阵覆盖了 fail-closed 场景（unsupported registry）、降级场景（NAV failure、bond drawdown error）、边界场景（non-bond active fund、bond fund typed NAV）、provenance 投影、行为保留（non-active direct path）

测试覆盖足以捕获核心回归和边界违规。有一个关于 active fund 字段归属验证策略的轻微注意点（Finding 6）。

### Q8: Blocking ambiguity, overreach, missing evidence, or under-specified projection rule

**NO BLOCKING ISSUES FOUND** (6 nonblocking findings + 1 needs-more-evidence, detailed below)

经过对 plan、AGENTS.md、design.md、implementation-control.md、S1 architecture plan 以及当前 `data_extractor.py`、`processors/`、`test_data_extractor.py` 代码的逐行比对，未发现阻塞性歧义、越界、缺失证据或投影规则不足。以下 findings 均为非阻塞性质。

## Findings

### Finding 1 (nonblocking): Dispatch key `source_kind` derivation underspecified

证据路径：
- Plan line 85: `source_kind=<public source kind>`
- `contracts.py:104`: `source_kind: str`，`__post_init__` 中无验证
- `active_annual.py:226-231`: `supports()` 不检查 `source_kind`
- `design.md` 中 evidence anchor `source_kind` 当前只允许 `annual_report`、`external_api`、`derived`

当前 S1 processor 的 `supports()` 不使用 `source_kind` 做路由决策，因此该歧义暂时不阻塞 dispatch。但在 S2 中需要构造 dispatch key 的 `source_kind` 参数，plan 只写了 `<public source kind>` 占位符而未指定具体映射规则。建议在 implementation 中将 `source_kind` 映射写为显式 helper（如从 `report.metadata.source` 的 `selected_source` / `source_mode` 派生出 `"annual_report"` 或 `"derived"`），避免不同调用路径产生分歧。

**处置**：implementation 前或中澄清映射规则即可，当前不阻塞。

### Finding 2 (nonblocking): `_tracking_error_for_fund_type()` facade-level filtering over processor output needs explicit interaction rule

证据路径：
- Plan line 110: tracking_error “仍必须经过 `_tracking_error_for_fund_type()`”
- `data_extractor.py:462-487`: `_tracking_error_for_fund_type()` 对非指数基金返回 `missing`
- `active_annual.py:111`: `performance.tracking_error` 映射到 `return_attribution.v1`

Processor 输出的 `return_attribution.v1` 包含 tracking_error 原始抽取值（对 active fund 可能非空）。Facade 的 `_tracking_error_for_fund_type()` 会对 active fund 返回 `missing`（“非指数基金不适用跟踪误差”）。这意味着 processor 输出被 facade 后处理覆盖，逻辑是正确的（processor 不应做 fund-type 策略判断），但 plan 只提了 tracking_error “仍必须经过” 而没说明为什么 facade 覆盖 processor 输出是预期行为。建议在 implementation artifact 中记录这一层叠关系。

**处置**：不阻塞，implementation 时写清楚即可。

### Finding 3 (nonblocking): Bootstrap classification vs processor internal extraction consistency not explicitly verified

证据路径：
- Plan lines 57-58: bootstrap 用 `extract_profile()` 做分类
- `data_extractor.py:434-459`: `_classified_fund_type()` 从 `basic_identity.value["classified_fund_type"]` 读类型
- `active_annual.py:226-231`: `supports()` 检查 `context.fund_type == "active_fund"`
- `active_annual.py:264-268`: processor 内部也调用 `extract_profile(report)` → 独立得出 `basic_identity`

Bootstrap 分类和 processor 内部分类都调用 `extract_profile()` 并读取同一份 `ParsedAnnualReport`，结果应一致。但如果极端情况下 extract_profile 内部有非确定性（如依赖 parse 顺序），可能出现 bootstrap 判为 active 但 processor 内部 supports() 仍通过的情况，或者相反。这极不可能，但 plan 没有记录该一致性假设。S3 precomputed extraction context 应彻底解决此问题。

**处置**：不阻塞。建议在 S2 implementation 中加一行注释说明两者使用同源 in-memory `ParsedAnnualReport`，一致性由 extract_profile 的确定性保证。

### Finding 4 (nonblocking): Field family value dict to individual ExtractedField projection detail left to implementation

证据路径：
- Plan lines 100-131: 投影规则指定了 family→field 映射
- `FundFieldFamilyResult.value` 是 `dict[str, object]`（`contracts.py:257`）
- `StructuredFundDataBundle` 各字段类型为 `ExtractedField[dict[str, object]]` 等（`data_extractor.py:211-227`）
- `active_annual.py:356-365`: family value 格式为 `{"schema_version": "product_essence.v1", "basic_identity": <raw_value>, "product_profile": <raw_value>, ...}`

投影时需从 `FundFieldFamilyResult.value` dict 中按 `output_field_name` 取出 raw value 并构造新 `ExtractedField`。Plan 在高层次描述了该过程（保留 value、使用 anchors、映射 extraction_mode），但未给出 `_field_from_family()` 的精确契约：是否需要从 family anchors 中筛选出与该字段相关的 anchors？如果 family 有 5 个字段和 10 个 anchors，单个字段的 `ExtractedField.anchors` 应该包含全部 10 个还是按需筛选？当前 S1 processor 的 anchors 是合并后去重的（`active_annual.py:357-359`），未按字段粒度分配。Plan 写“使用该 `FundFieldFamilyResult.anchors`”（line 129），暗示整个 family 的 anchors 映射到每个字段。这是合理选择但应在实现前确认。

**处置**：不阻塞。建议 implementation worker 明确 `_field_from_family` 的 anchor 分配策略。

### Finding 5 (nonblocking): `core_risk.v1` fallback to `risk_characteristic_text` rule edge case not fully specified

证据路径：
- Plan lines 122-123: “可作为 `risk_characteristic_text` fallback only if `product_essence.v1` lacks that field and core_risk has a public value”
- `active_annual.py:171-172`: `profile.risk_characteristic_text` 同时出现在 `product_essence.v1` 和 `core_risk.v1`
- `active_annual.py:368-369`: 两个 family value dict 各自独立包含 `risk_characteristic_text` 键

Plan 的 fallback 规则写的是“only if `product_essence.v1` lacks that field”，但实际上同一份 `risk_characteristic_text` 值会同时出现在两个 family 的 value dict 中（S1 的 mapping table 将同一 extractor 输出映射到两个 family）。Plan 说的“lacks that field”是指：
1. `product_essence.v1` → `risk_characteristic_text` 的 ExtractedField 本身为 missing？
2. 还是 `product_essence.v1` value dict 中 `risk_characteristic_text` 键缺失或值为 None？

建议 implementation 明确：优先使用 `product_essence.v1` 投影出的 risk_characteristic_text ExtractedField；仅当该字段 `extraction_mode == "missing"` 且 `core_risk.v1` 投影出的同名字段有 public value 时才 fallback。

**处置**：不阻塞。implementation 时写清判断条件即可。

### Finding 6 (nonblocking): Test for active fund field attribution to processor vs direct extractor verification strategy not explicit

证据路径：
- Plan lines 204-205: “active fund `FundDataExtractor.extract()` uses processor registry path and still returns the same public bundle fields”

该测试的核心目的是验证 active fund 已覆盖字段确实来自 processor，而不是 facade 静默退回到 direct extractor。但 plan 未指定如何区分 processor 输出与 direct extractor 输出——如果两者对同一份 fixture 报告产生相同的字段值（因为它们调用相同的窄 extractor），则仅凭“same public bundle fields”无法区分来源。

建议 implementation 中使用注入自定义 registry 的方式：注入一个返回已知特殊 marker 值的 processor，然后验证 bundle 中的字段携带该 marker 而非 direct extractor 的默认值。这样可以从根源上证明 processor path 被实际使用且 direct path 未被静默 fallback。

**处置**：不阻塞。属于测试设计细节，implementation worker 可以自行选择验证策略。

### Finding 7 (needs-more-evidence): Non-active fund type behavior preservation tests partially implicit

证据路径：
- Plan lines 209-210: “bond fund path remains current direct branch and keeps typed NAV drawdown behavior unchanged”
- Plan line 137-144: S2 保留当前 direct extraction branch 用于 index/enhanced/bond/qdii/fof/unclassified 五种类型

必测清单中只有债券基金有显式测试要求。Index、enhanced_index、qdii、fof、unclassified 五种类型的 current direct path 保留未在必测清单中单独列出。考虑到这些类型完全走 `_extract_bundle_direct_legacy_path()` 且代码路径不变，风险很低。但如果在重构中抽取 `_extract_bundle_direct_legacy_path()` 时无意间改变了调用顺序或参数传递，可能影响这五种类型。

**处置**：建议 implementation worker 至少对一种非 active、非 bond 的基金类型（如 index_fund）增加一个快速行为保留测试。不作为阻塞条件。

## Residual Risks

| Risk | Severity | Owner | Mitigation |
|---|---|---|---|
| Bootstrap 分类与 processor 内部 extract_profile 不一致（同一报告） | 极低 | S2 implementation worker | 两者消费同一份 in-memory `ParsedAnnualReport`，确定性 extractor 保证一致性；S3 precomputed context 彻底消除 |
| Non-active 类型测试覆盖不足 | 低 | S2 implementation worker / reviewer | 代码路径完全不变，仅抽取为命名 helper；建议至少加一个 index_fund 冒烟测试 |
| `source_kind` 映射在 dispatch key 中不统一 | 低 | S2 implementation worker | `supports()` 不使用 `source_kind`，不影响 dispatch；实现中定义显式映射 helper |
| Processor family anchor 到 field anchor 的分配策略不精确 | 低 | S2 implementation worker | 当前实现选择全量映射（family anchors → 每个字段 anchors），后续可按需细化 |
| S2 实现可能发现 exact write set 不足 | 中 | S2 implementation worker | Plan 已设 stop condition：不足时写 blocker note，不静默扩 scope |
| 临时重复 `extract_profile()` 的性能开销 | 极低 | S3 gate owner | 仅 memory 重复，无 I/O 重复；S3 消除 |

## Review Completeness Statement

本 review 执行了以下验证：

- 逐行比对 plan 与 `AGENTS.md` 的 Processor/Extractor 边界硬约束（lines 75-82）、fallback 分类规则（lines 236-247）、模块边界（lines 91-141）
- 逐行比对 plan 与 `docs/design.md` v2.20 的 FundDocumentRepository 边界、Processor/Extractor S1 当前状态、NOT_READY 边界
- 逐行比对 plan 与 `docs/implementation-control.md` 的 current gate 约束、当前 truth guardrails、forbidden actions
- 逐行比对 plan 的投影规则与 `fund_agent/fund/processors/active_annual.py` 的 `FIELD_FAMILY_MAPPINGS`、`_FAMILY_ORDER`、`_build_field_family_result()` 输出格式
- 逐行比对 plan 的 fail-closed 规则与 `fund_agent/fund/processors/registry.py` 的 `resolve()` / `UnsupportedFundProcessorError` 语义、`active_annual.py` 的 `_blocked_result()` 语义
- 逐行比对 plan 的保留行为与 `fund_agent/fund/data_extractor.py` 的 `extract()` 当前实现（repository 传播、NAV 降级、bond 路径、source provenance 投影、classified_fund_type、tracking_error_for_fund_type）
- 审阅了 `tests/fund/test_data_extractor.py` 的全部现有测试，确认 plan 的必测清单与现有测试不冲突

本 review 未执行、也不授权执行：live/source acquisition、PDF/FDR/Docling conversion、provider/LLM、analyze/checklist/golden/readiness/release、PR/push/merge 或任何超出 review artifact 写入范围的命令。

Review artifact path: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-review-ds-20260618.md`
