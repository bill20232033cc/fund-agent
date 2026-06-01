# MVP Gate 1 ChapterFactProvider typed projection implementation review (GLM)

日期：2026-05-30
角色：Gateflow implementation reviewer（独立 review，非 controller/implementation worker）
Plan artifact：`docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md`
Plan reviews：`mvp-gate1-chapter-fact-provider-plan-review-mimo-20260530.md`、`mvp-gate1-chapter-fact-provider-plan-review-glm-20260530.md`
Implementation evidence：`docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md`

---

## Verdict：PASS

实现严格停在 MVP Gate 1 ChapterFactProvider typed projection 范围内，public contract、语义映射、测试覆盖和文档同步均符合 accepted plan。3 个 findings 均为 INFO 级别，不阻塞。

---

## Scope 合规检查

| 检查项 | 结论 | 证据 |
|--------|------|------|
| 严格停在 Fund 层 typed projection | **PASS** | `chapter_facts.py` 只定义 typed projection dataclasses 和 `project_chapter_facts()` / `ChapterFactProvider.project()` |
| 无 writer/auditor/orchestrator/CLI/dayu scope creep | **PASS** | AST import isolation test 断言无 documents/repository/cache/pdf/source/downloader/parser/service/dayu/openai/llm 导入；README/doc 同步均保留"未实现"边界 |
| 无完整 FundToolService 过度设计 | **PASS** | `ChapterFactProvider` 是 concrete façade（非 Protocol），只有 `project()` 委托 `project_chapter_facts()` |
| public API 与 plan 一致 | **PASS** | `project_chapter_facts(bundle, *, chapter_ids)` 和 `ChapterFactProvider.project(bundle, *, chapter_ids)` 签名与 plan §4 完全匹配 |
| Literal aliases 与 plan §5.1 一致 | **PASS** | `ChapterFactSchemaVersion`、`ChapterFactFundType`、`ChapterFactStatus`（5 值）、`ChapterFactMissingReason`（9 值）、`ChapterFacetStatus`（3 值）、`ChapterFacetSource`（4 值）、`ChapterEvidenceSourceKind`（4 值）均逐条匹配 |
| 8 个 dataclass 与 plan §5.2 一致 | **PASS** | `ChapterEvidenceAnchor`（8 字段）、`ChapterFactEntry`（12 字段）、`ChapterFacetResolution`（7 字段）、`ChapterLensResolution`（8 字段）、`ChapterItemRuleProjection`（2 字段）、`ChapterFactInput`（12 字段）、`ChapterFactProjection`（7 字段）、`_ChapterFieldSpec`（5 字段）均逐字段匹配 |
| `_SOURCE_FIELD_IDS` 16 条与 plan §6 一致 | **PASS** | basic_identity 至 nav_data 共 16 条，id 格式均为 `structured.{field_name}` |
| `_CHAPTER_FIELD_SPECS` 8 章映射与 plan §7 一致 | **PASS** | 逐章对照：ch0=5 字段、ch1=5 字段、ch2=5 字段、ch3=6 字段、ch4=5 字段、ch5=6 字段、ch6=8 字段、ch7=6 字段，字段名与 plan 表格完全匹配 |
| schema_version 稳定 | **PASS** | `CHAPTER_FACT_SCHEMA_VERSION = "chapter_fact_projection.v1"` 与 plan §4/§5.1 一致 |
| 只消费 StructuredFundDataBundle + template truth APIs | **PASS** | 导入限于 `EvidenceAnchor`、`ExtractedField`、`FundType`、`get_chapter_contract`、`resolve_preferred_lens`、`evaluate_template_item_rules`；`NavDataResult`、`StructuredFundDataBundle` 仅在 `TYPE_CHECKING` 下导入 |
| 无 repository/PDF/cache/source/downloader/parser/LLM/dayu import | **PASS** | `test_projection_does_not_call_repository_or_source_helpers` 使用 `ast.parse` 校验模块级全部 import 语句 |

---

## 语义正确性检查

### fund_type unknown/invalid

- `_read_classified_fund_type()`（line 530-555）：`identity_value` 非 dict 或 `classified_fund_type` 缺失/空 → `"unknown"` + `"classified_fund_type_missing"`；不在 `FundType` 闭集 → `"unknown"` + `"classified_fund_type_invalid"`。与 plan §9 一致。
- `fund_type == "unknown"` 时：`_resolve_chapter_lens()` 返回 `lens_key="unknown"`、`_evaluate_item_rule_decisions()` 返回 `()`、`_resolve_chapter_facets()` 返回 `facets=()` + `non_asserted_facets=()`。与 plan §10 规则 1 一致。
- 测试 `test_missing_or_invalid_fund_type_yields_unknown_without_lens_or_item_rules` 覆盖 missing + invalid 两条路径，断言 `lens_key=="unknown"` + `decisions==()` + `facets==()`。**PASS**。

### preferred_lens resolution

- `_resolve_chapter_lens()`（line 745-789）：fund_type valid 时调用 `resolve_preferred_lens(chapter_id, fund_type)`，保存 `lens_key`、`used_default`、`statements`、`facets_any`、`priority`。与 plan §11 一致。
- line 777-778 添加了显式类型窄化注释，响应 GLM plan review Finding 1。
- 测试 `test_preferred_lens_resolution_preserves_default_and_exact_lens` 验证 active_fund ch2=`default`+`used_default=True`、ch3=`active_fund`+`priority="core"`。**PASS**。

### ITEM_RULE

- `_evaluate_item_rule_decisions()`（line 792-809）：全局一次调用 `evaluate_template_item_rules(fund_type=fund_type, facets=())`。与 plan §10 规则 3 和 §11 一致。
- `_item_rule_decisions_for_chapter()`（line 812-831）：按 `chapter_id` 过滤，不重评估。与 plan §11 "每章只保留 `decision.chapter_id == chapter_id`" 一致。
- 不传 `non_asserted_facets` 给 ITEM_RULE。与 plan §10 规则 3 "不把 non_asserted_facets 传给 ITEM_RULE" 一致。
- 测试 `test_item_rule_decisions_are_chapter_scoped_and_fund_type_deterministic` 验证 active/index/bond/QDII/FOF 的 rule_id→status 映射，bond/QDII/FOF 全 `delete`。**PASS**。

### facet resolution

- `_resolve_chapter_facets()`（line 694-742）：fund_type valid 且 `facets_any` 非空时 `facets=()`、`non_asserted_facets=lens_resolution.facets_any`、`status="empty"`、reason 含 `"unsupported_facet_inference"`。与 plan §10 规则 2 一致。
- 测试 `test_facet_resolution_does_not_semantically_guess_subtype` 验证 active_fund ch1 的 `facets==()`、`non_asserted_facets` 包含候选标签、`unsupported_facet_inference` 出现在 reason 和 missing_reasons。**PASS**。

### NavDataResult 三态

- `_project_nav_data_fact()`（line 1023-1080）：`unavailable=True` → `status="unavailable"` + `missing_reason="field_unavailable"`；`records=[]` 且非 unavailable → `status="missing"` + `missing_reason="field_missing"`；有数据 → `status="available"`。与 plan §9 和 GLM plan review Finding 3 一致。
- 测试 `test_nav_data_three_states` 覆盖三种路径。**PASS**。

### bond_risk_evidence 组级 anchors

- `_anchors_for_field()`（line 852-853）：`bond_risk_evidence` 直接返回 `()`，不展开。
- `_project_bond_risk_evidence_fact()`（line 979-1020）：`evidence_anchor_ids=()`，`missing_detail` 写明"组级锚点引用保留在 value.anchors 内"。与 plan §8 和 GLM plan review Finding 4 一致。
- 测试 `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded` 验证 `bond_fact.evidence_anchor_ids==()` 且 `bond_fact.value==value`。**PASS**。

### EvidenceAnchor ID/ref 语义

- `_anchor_id_for()`（line 1315-1343）：格式 `chapter-anchor:{fund_code}:{report_year}:ch{chapter_id}:{source_kind}:{section}:{hash8}`，hash 使用 SHA-256 前 8 位。与 plan §8 一致。
- `_dedupe_chapter_anchors()`（line 1244-1279）：按 key 去重 + hash 碰撞 `-2`/`-3` 后缀。与 plan §8 一致。
- `_ensure_fact_anchor_refs_exist()`（line 1406-1431）：校验 fact `evidence_anchor_ids` 均存在于本章 `evidence_anchors`。与 plan §8 一致。
- 测试 `test_missing_field_semantics_and_anchor_traceability` 验证 anchor ref 完整性。**PASS**。

### 合成缺口事实

- `_synthetic_missing_facts()`（line 1160-1199）：ch0/ch7 → `accepted_chapter_conclusions_missing`，ch5 → `cross_period_comparison_missing`。与 plan §7 特殊缺口一致。
- 测试 `test_projects_eight_chapter_inputs_from_structured_bundle` 间接触盖 8 章生成。**PASS**。

### source kind unknown 兜底

- `_chapter_anchor_from_raw()`（line 1299-1302）：`source_kind` 不在 `{"annual_report", "external_api", "derived"}` 时投射为 `"unknown"`。与 plan §5.1 和 GLM plan review Finding 2 一致。
- 模块 docstring（line 6-7）显式说明了 `ChapterEvidenceSourceKind` 的扩展意图。
- 测试 `test_source_kind_unknown_note` 验证 `"vendor_feed"` → `"unknown"`。**PASS**。

---

## Plan Review Findings 处置验证

| Plan review finding | 实现处置 | 验证 |
|---------------------|----------|------|
| MiMo F1: `_ChapterFieldSpec` 缺 `not_applicable_when` | 采用推荐方案 2：未添加字段，not_applicable 由运行时 `_missing_status_for_field` 驱动 | **PASS** — 实现与 Slice 1 dataclass 定义一致 |
| MiMo F2: `bond_risk_evidence` anchor 特殊语义 | `_anchors_for_field` 和 `_project_bond_risk_evidence_fact` 走专用路径，`evidence_anchor_ids=()` | **PASS** |
| MiMo F3: 缺 happy path 边界测试 | 新增 `test_chapter_id_validation_accepts_valid_range` 覆盖 `(0,)`、`(7,)`、全量 8 章 | **PASS** |
| MiMo F6: 缺 `ChapterFactProvider.project()` smoke test | 新增 `test_chapter_fact_provider_delegates_to_project_chapter_facts` | **PASS** |
| GLM F1: `ChapterFactFundType` → `FundType` narrowing 需注释 | line 777-778 添加显式 narrowing 注释 | **PASS** |
| GLM F2: `ChapterEvidenceSourceKind` 扩展说明 | 模块 docstring line 6-7 显式说明扩展意图 | **PASS** |
| GLM F3: NavDataResult 三态映射 | `_project_nav_data_fact` 实现三态 + 测试 `test_nav_data_three_states` | **PASS** |
| GLM F4: bond_risk_evidence 投影策略 | `_project_bond_risk_evidence_fact` + 测试 `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded` | **PASS** |
| GLM F7: 导入隔离测试方法 | `test_projection_does_not_call_repository_or_source_helpers` 使用 `ast.parse` 检查全部 import | **PASS** |

---

## Findings

### F1 [INFO] `_anchor_normalized_payload` 包含 `source_kind`，超出 plan §8 hash 输入声明

**位置**：`chapter_facts.py` line 1377-1385

**描述**：Plan §8 明确列出 anchor hash 输入的 6 个字段：`document_year`、`section_id`、`page_number`、`table_id`、`row_locator`、`note`。实现在 `_anchor_normalized_payload()` 中额外包含 `source_kind`（7 个字段）。

**影响**：功能正确——不同 source_kind 的锚点获得不同 ID，dedupe key（`_anchor_key`）也使用相同 payload 保持一致。`source_kind` 已在 anchor_id 前缀中出现，hash 中冗余包含不影响唯一性。

**建议**：无需修改。后续如需严格对齐 plan 声明，可在 `_anchor_normalized_payload` 中排除 `source_kind`，但当前行为更保守。

### F2 [INFO] 10 行未覆盖代码含防御性错误路径

**位置**：`chapter_facts.py` lines 547, 572, 574, 577, 859, 923, 1110, 1272, 1402, 1431

**描述**：97% coverage 超过 plan §13 的 ≥80% 目标。未覆盖路径均为防御性分支：
- line 547：`identity_value` 非 dict（理论上 extractor 总返回 dict）
- lines 572/574/577：`_normalize_basis` 的 None/str/其他类型分支
- line 859：非 `ExtractedField` 非 `nav_data` 字段的 fallback `return ()`
- line 923：不支持的章节事实字段类型 `raise ValueError`
- line 1110：note 含 `"unavailable"` 或 `"不可用"` 语义
- line 1272：anchor hash 碰撞 `-2`/`-3` 后缀路径
- line 1402：`_stable_id_part` 正常替换路径
- line 1431：`_ensure_fact_anchor_refs_exist` 发现引用不存在

**影响**：不影响功能正确性；均为不应触发的防御性路径。

**建议**：如追求更高 coverage，可补充 1-2 个测试覆盖 `unavailable` note 语义和 hash 碰撞路径，但不阻塞。

### F3 [INFO] `_missing_status_for_field` note-based 语义判断依赖 extractor 约定

**位置**：`chapter_facts.py` line 1083-1111

**描述**：`_missing_status_for_field()` 通过 field note 中的关键词（`"not_applicable"` / `"non_bond"` / `"non_index"` / `"unavailable"` 等）判断 `not_applicable` / `unavailable` 语义。Plan §9 明确说明 `field_not_applicable` "按 fund type + note 驱动"，implementation 正确遵守。但未来 extractor note 约定变化可能影响此处判断。

**影响**：当前 extractor note 约定稳定（`"not_applicable_non_bond_fund"`、`"not_applicable_non_index_fund"` 等），测试 fixture 也验证了关键词匹配。

**建议**：后续 gate 如引入更结构化的 not_applicable 标记（例如在 `ExtractedField` 上增加显式 status 字段），此处可相应升级。当前实现与 plan 完全一致，无需修改。

---

## 测试覆盖评估

| 测试 case（plan §13） | 实现 | 状态 |
|----------------------|------|------|
| `test_projects_eight_chapter_inputs_from_structured_bundle` | line 37-69 | **PASS** |
| `test_missing_or_invalid_fund_type_yields_unknown_without_lens_or_item_rules` | line 136-169 | **PASS** |
| `test_preferred_lens_resolution_preserves_default_and_exact_lens` | line 172-192 | **PASS** |
| `test_item_rule_decisions_are_chapter_scoped_and_fund_type_deterministic` | line 195-226 | **PASS** |
| `test_facet_resolution_does_not_semantically_guess_subtype` | line 229-252 | **PASS** |
| `test_missing_field_semantics_and_anchor_traceability` | line 255-299 | **PASS** |
| `test_nav_data_three_states` | line 302-343 | **PASS** |
| `test_projection_does_not_call_repository_or_source_helpers` | line 423-458 | **PASS** |
| `test_chapter_id_validation_fails_closed` | line 90-107 | **PASS** |
| `test_chapter_fact_provider_delegates_to_project_chapter_facts`（MiMo F6） | line 72-87 | **PASS** |
| `test_chapter_id_validation_accepts_valid_range`（MiMo F3） | line 110-133 | **PASS** |
| `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded`（GLM F4） | line 346-379 | **PASS** |
| `test_source_kind_unknown_note`（GLM F2） | line 382-420 | **PASS** |

测试文件 `tests/fund/test_chapter_facts.py` 共 13 个 case，覆盖 plan §13 全部 9 个 required case 和两份 plan review 的 4 个建议补充 case。

---

## 文档同步评估

| 文件 | 评估 |
|------|------|
| `fund_agent/fund/README.md` | **PASS** — 准确描述 `project_chapter_facts()` / `ChapterFactProvider.project()` 为 typed projection，明确列出"不读取文档仓库、PDF、cache、source helper、下载器或 parser，不调用 LLM、Service、Host 或 dayu；它不是 writer、auditor、orchestrator 或 FundToolService" |
| `tests/README.md` | **PASS** — 准确描述 test scope 和运行命令，明确"使用内存 fixture，不触发文档仓库、PDF、cache、来源 helper、LLM、Service、Host 或 dayu" |
| `docs/design.md` | **PASS** — line 493 准确标记 Route C Gate 1 `ChapterFactProvider` 已为 Fund 层代码事实；line 507 正确保留"只代表 typed projection façade，不是 writer、auditor、orchestrator 或 FundToolService"边界；line 501 保留未来 `facet_recognizer` / `FundToolService` 候选命名但不声称已实现 |

---

## 验证结果复现

| 命令 | 结果 |
|------|------|
| `uv run pytest tests/fund/test_chapter_facts.py -q` | 13 passed in 0.78s |
| `uv run pytest tests/fund/test_chapter_facts.py --cov=fund_agent.fund.chapter_facts --cov-report=term-missing -q` | 97% coverage（291 stmts, 10 miss） |
| `uv run ruff check fund_agent/fund/chapter_facts.py tests/fund/test_chapter_facts.py` | All checks passed |
| `uv run pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/test_data_extractor.py -q` | 35 passed in 0.39s |

所有验证结果与 implementation evidence 声明一致。

---

## 总结

实现严格遵循 accepted plan，scope 控制优秀。Public contract（7 个 Literal aliases + 8 个 frozen/slotted dataclass + 2 个 public entrypoints）与 plan §4/§5 逐字段一致。语义映射（fund_type unknown、preferred_lens、ITEM_RULE、facet 不猜 subtype、NavDataResult 三态、bond_risk_evidence 组级 anchors、evidence anchor ID/ref）均正确实现。Plan review 的所有 non-blocking findings 已在实现中妥善处置。测试 13 passed、97% coverage、lint 全绿。文档同步准确，不把 writer/auditor/orchestrator/Service/dayu 写成已实现。

3 个 INFO findings 均为实现细节观察，不影响正确性和 plan 合规性。

**Verdict：PASS**
