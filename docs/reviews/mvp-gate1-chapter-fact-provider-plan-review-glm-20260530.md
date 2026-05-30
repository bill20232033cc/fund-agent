# MVP Gate 1 ChapterFactProvider typed projection plan review (GLM)

日期：2026-05-30
角色：Gateflow plan reviewer（独立 review，非 controller/implementation worker）
Plan artifact：`docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md`

---

## Verdict：PASS_WITH_NON_BLOCKING

Plan 严格停在 Gate 1 ChapterFactProvider typed projection 范围内，scope 控制良好，typed contract 定义详细且 implementation-ready。存在若干 non-blocking findings，不影响 plan 执行，但建议 implementation worker 注意。

---

## Findings

### Finding 1 — `ChapterFactFundType` 与 `FundType` 类型桥接需显式注释

**Severity：Medium（non-blocking）**

Plan §5.1 定义 `ChapterFactFundType = FundType | Literal["unknown"]`，§10/§11 正确指出 fund type unknown 时跳过 `resolve_preferred_lens()` 和 `evaluate_template_item_rules()`（两者签名均要求 `FundType` 而非 `ChapterFactFundType`）。

但 typed contract 中 `ChapterFacetResolution.fund_type`、`ChapterLensResolution.fund_type`、`ChapterFactInput.fund_type` 均为 `ChapterFactFundType`，而内部调用 `resolve_preferred_lens(chapter_id, fund_type)` 时需要 `FundType`。Implementation worker 需要在 helper 内部做显式的 valid/unknown 分支和 narrowing。

**建议**：在 `project_chapter_facts()` 实现中增加一行注释或 docstring 说明 valid fund type 路径如何将 `ChapterFactFundType` narrowing 为 `FundType` 再传入 contracts/item_rules API，确保类型检查器（mypy/pyright）能通过。

### Finding 2 — `ChapterEvidenceSourceKind` 扩展了 `EvidenceSourceKind` 闭集

**Severity：Low（non-blocking）**

现有 `EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]`（见 `extractors/models.py`），plan §5.1 新增 `ChapterEvidenceSourceKind` 加入了 `"unknown"`。

该扩展合理（projection 可能遇到 anchor 来源不明的情况），但 plan 未显式说明两者关系。

**建议**：在 `chapter_facts.py` 模块 docstring 或 `ChapterEvidenceSourceKind` 定义处说明这是 projection 层的扩展，与 extractor 层 `EvidenceSourceKind` 保持方向一致但允许 unknown 兜底。

### Finding 3 — `NavDataResult` 与 `ExtractedField` 形状不同，需特殊投影路径

**Severity：Low（non-blocking）**

Plan §8/§12 提到 `_project_nav_data_fact()` helper，但 plan 正文未详细说明 `NavDataResult`（非 `ExtractedField`，有 `unavailable: bool` 和 `records: list` 而非 `extraction_mode`）如何映射到 `ChapterFactStatus` 和 `ChapterFactMissingReason`。

现有代码中 `NavDataResult` 的 unavailable 路径与 `ExtractedField.extraction_mode == "missing"` 是不同的降级语义。Plan §9 提到 `nav_data.unavailable is True → field_unavailable`，这是正确的，但具体映射细节（如 `records` 为空但 `unavailable=False` 时如何处理）留给实现。

**建议**：Implementation worker 在 `_project_nav_data_fact()` 中对 `NavDataResult.unavailable=True`、`records=[]` 且 `unavailable=False`、正常有数据三种状态分别映射，并在测试中覆盖。

### Finding 4 — `bond_risk_evidence` 投影策略合理但需实现约束

**Severity：Low（non-blocking）**

Plan §8 承认 `bond_risk_evidence.value.anchors` 是 `BondRiskEvidenceAnchorRef`（组级引用，非普通 `EvidenceAnchor`），建议"先把 `bond_risk_evidence` 作为一个 fact value 投影，保留其内部 anchor ids 在 value 内"。

这与 `ChapterFactEntry.value: object | None` 的宽松类型一致，但需注意：
- 该 fact 的 `source_field_id` 为 `structured.bond_risk_evidence`
- `evidence_anchor_ids` 应为空元组（因为内部锚点不是 `ChapterEvidenceAnchor` 格式），或 plan 应明确说明投影策略

**建议**：Implementation worker 可将 `bond_risk_evidence` 投影为单个 `ChapterFactEntry`，`evidence_anchor_ids=()`，`missing_detail` 写明"组级锚点引用保留在 value 内部，未展开为 ChapterEvidenceAnchor"。若后续 gate 需要展开，再单独处理。

### Finding 5 — `ChapterFactEntry.value: object | None` 类型过宽

**Severity：Low（non-blocking）**

Plan §5.2 中 `value: object | None` 覆盖了 dict、str、int、float、BondRiskEvidenceValue、IndexProfileValue、TrackingErrorValue 等异构类型。对于 typed projection 而言，这比理想中的泛型窄一些，但考虑到 bundle 字段的异构性和 Gate 1 的 projection 定位（不对 value 做进一步类型细化），这是务实的。

**建议**：保持 `object | None`。后续 gate 如需对 value 做类型化消费，可在 writer/auditor 层做 narrowing。

### Finding 6 — 同步/异步选择未显式声明

**Severity：Low（non-blocking）**

Plan §4 的 `project_chapter_facts()` 和 `ChapterFactProvider.project()` 未声明 async。所有消费的 API（`get_chapter_contract`、`resolve_preferred_lens`、`evaluate_template_item_rules`）均为同步函数，因此 projection 应为同步。

**建议**：Implementation worker 确认使用同步 def，无需 async。

### Finding 7 — 导入隔离测试方法值得细化

**Severity：Low（non-blocking）**

Plan §13 的 `test_projection_does_not_call_repository_or_source_helpers` 使用"静态断言模块未暴露/导入"的方式。这种方法在防止意外依赖方面有效，但具体实现方式会影响可维护性。

**建议**：可用 `ast.parse` 检查模块源文件中的 import 语句，或用 `pytest.importlib.import_module` 后检查 `sys.modules` 依赖链，而非仅检查 `__all__`。

---

## Scope 合规检查

| 检查项 | 结论 |
|--------|------|
| 严格停在 Gate 1 ChapterFactProvider typed projection | **PASS** — 目标明确为 projection，不实现 writer/auditor/orchestrator |
| 无 writer/auditor/orchestrator/CLI/dayu scope creep | **PASS** — §3 Non-goals 显式列出 16 项排除项 |
| 无完整 FundToolService 过度设计 | **PASS** — §4 明确 `ChapterFactProvider` 只是 façade，§3 排除 FundToolService |
| 使用 StructuredFundDataBundle + CHAPTER_CONTRACT/preferred_lens/ITEM_RULE 真源 | **PASS** — §2/§4/§7/§11 均引用现有真源代码 |
| facet inference deterministic 且不让 LLM/文本猜 subtype | **PASS** — §10 禁止 LLM/raw PDF/NLP，当前无稳定 subtype 字段时 facets=() |
| typed contract 足够 implementation-ready | **PASS** — §5 定义完整 Literal aliases + 8 个 dataclass，字段语义清晰 |
| missing/unavailable/anchor/source-field 语义清晰 | **PASS** — §8/§9 详细定义 9 种 missing reason 和 5 种 status |
| tests/validation 足够 | **PASS** — §13 覆盖 happy/missing/invalid/no-source 共 9 个 case |
| 不违反 AGENTS/UI->Service->Host->Agent/FundDocumentRepository/extra_payload 边界 | **PASS** — 新模块在 fund_agent/fund/，不导入 repository/PDF/cache/source |

---

## 真源一致性验证

| Plan 声明 | 代码验证 | 一致性 |
|-----------|----------|--------|
| FundType 闭集 6 种 | `fund_type.py` line 15-22 `Literal[...]` | 一致 |
| `resolve_preferred_lens(chapter_id, fund_type)` 签名 | `contracts.py` line 798 | 一致 |
| `evaluate_template_item_rules(*, fund_type, facets)` 签名 | `item_rules.py` line 298-302 | 一致 |
| `TemplateItemRuleDecision` 字段 | `item_rules.py` line 102-125 | 一致 |
| `EvidenceAnchor` 字段 | `models.py` line 87-108 | 一致；plan 正确扩展了 source_kind |
| `StructuredFundDataBundle` 字段列表 | `data_extractor.py` line 139-188 | 一致；plan §6 的 `_SOURCE_FIELD_IDS` 覆盖所有字段 |
| `LensKey = FundType | Literal["default"]` | `contracts.py` line 16 | 一致 |
| 4 条 ITEM_RULE | `item_rules.py` line 131-184 | 一致 |
| 8 章模板 0-7 | `contracts.py` line 20 `_EXPECTED_CHAPTER_IDS` | 一致 |

---

## Slice 计划评估

- Slice 1（contract module + stubs）：合理，先建类型再填行为。
- Slice 2（projection 行为）：数据流清晰（validate → fund type → ITEM_RULE → per-chapter → facts → anchors → aggregate），stop condition 明确。
- Slice 3（export + doc sync）：范围克制，默认不改 Service/root README。

三个 slice 的 stop condition 均包含"如果需要修改 bundle schema 或触碰 Service/CLI/repository，停止并交回"，这是正确的 fail-safe 设计。

---

## 总结

Plan 是一份高质量的 implementation-ready plan，scope 严格控制，typed contract 定义详尽，真源引用一致，测试覆盖充分。7 个 findings 均为 non-blocking，建议 implementation worker 在实现时留意类型桥接注释和 NavDataResult/bond_risk_evidence 的特殊处理。

Gate 分类 `heavy` 合理：新增 Fund 层公共契约、typed projection、evidence/missing 语义、CHAPTER_CONTRACT/preferred_lens/ITEM_RULE 组合边界，影响后续所有 Route C gates。
