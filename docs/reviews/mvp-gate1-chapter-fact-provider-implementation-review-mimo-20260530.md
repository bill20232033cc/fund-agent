# Implementation Review: MVP Gate 1 ChapterFactProvider typed projection

日期：2026-05-30
Reviewer：AgentMiMo
Plan artifact：`docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md`
Implementation evidence：`docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md`

## Verdict：PASS

实现严格符合 accepted plan，typed contract 完整、边界清晰、测试覆盖充分、文档同步准确。所有 validation 命令通过，单文件覆盖率 97%。

---

## Review checklist

| 检查项 | 结论 |
|--------|------|
| 严格停在 Fund 层 ChapterFactProvider typed projection | **PASS** — 新模块 `chapter_facts.py` 在 `fund_agent/fund/`，不触碰 Service/Host/dayu |
| 无 writer/auditor/orchestrator/CLI/dayu scope creep | **PASS** — 无任何 writer/auditor/orchestrator/CLI/dayu 代码或文档声称 |
| 无完整 FundToolService 过度设计 | **PASS** — `ChapterFactProvider` 是 frozen dataclass façade，仅 delegate 到 `project_chapter_facts()` |
| public API/dataclasses/schema_version 稳定且符合 plan | **PASS** — `chapter_fact_projection.v1`、`project_chapter_facts()`、`ChapterFactProvider.project()` 均与 plan §4/§5 一致 |
| fund_type unknown/invalid fail closed | **PASS** — `_read_classified_fund_type` 对 missing/invalid 返回 `"unknown"` 并记录 reason，跳过 lens/item rule 有效路径 |
| preferred_lens 来自现有 truth | **PASS** — 调用 `resolve_preferred_lens(chapter_id, fund_type)`，不复制 manifest |
| ITEM_RULE 来自现有 truth | **PASS** — 调用 `evaluate_template_item_rules(fund_type=fund_type, facets=())`，全局一次性调用后按 chapter_id 分发 |
| facet non_asserted 语义正确 | **PASS** — `facets=()`、`non_asserted_facets=lens.facets_any`、reason 含 `unsupported_facet_inference`；不从候选 catalog 猜 subtype |
| NavDataResult 三态映射正确 | **PASS** — `unavailable=True` → `status="unavailable"` + `field_unavailable`；`records=[]` 且 `unavailable=False` → `status="missing"` + `field_missing`；正常 → `status="available"` |
| bond_risk_evidence 组级 anchors 保留在 value 内 | **PASS** — `_project_bond_risk_evidence_fact` 不展开 `BondRiskEvidenceAnchorRef`，`evidence_anchor_ids=()` |
| EvidenceAnchor ID/ref 语义正确 | **PASS** — `anchor_id` 格式 `chapter-anchor:{fund_code}:{report_year}:ch{chapter_id}:{source_kind}:{section}:{hash8}`，碰撞用 `-2`/`-3` 后缀；fact refs 经 `_ensure_fact_anchor_refs_exist` 校验 |
| source field ids 稳定 | **PASS** — `_SOURCE_FIELD_IDS` 覆盖 plan §6 全部 16 个字段，id 格式 `structured.{field_name}` |
| 只消费 StructuredFundDataBundle 和 template truth APIs | **PASS** — import surface 仅：`hashlib`、`json`、`dataclasses`、`typing`、`EvidenceAnchor`、`ExtractedField`、`FundType`、`ChapterContract`、`LensKey`、`get_chapter_contract`、`resolve_preferred_lens`、`TemplateItemRuleDecision`、`evaluate_template_item_rules`；`NavDataResult`/`StructuredFundDataBundle` 仅在 `TYPE_CHECKING` 下 |
| 无 repository/PDF/cache/source/downloader/parser/LLM/dayu import | **PASS** — AST import isolation test 验证无 forbidden fragments |
| tests 覆盖 plan/review findings | **PASS** — 13 个 tests 覆盖全部 plan §13 required cases + plan review F1-F6 建议 |
| validation evidence 可信 | **PASS** — 复现验证：13 passed (chapter_facts)、35 passed (existing)、ruff clean、coverage 97% |
| docs/readme/design 同步准确 | **PASS** — 详见下方文档同步检查 |

---

## Documentation sync check

| 文件 | 检查结论 |
|------|----------|
| `fund_agent/fund/README.md` | **PASS** — 新增 `ChapterFactProvider` / `project_chapter_facts()` 到 public capability import 示例和代码示例，未声称 writer/auditor/orchestrator/dayu 已实现 |
| `tests/README.md` | **PASS** — 新增 `test_chapter_facts.py` 条目，准确描述覆盖范围和约束（不触发文档仓库/PDF/LLM/dayu） |
| `docs/design.md` | **PASS** — 最小同步：新增一行说明 ChapterFactProvider 已实现为 `chapter_fact_projection.v1`；Gate 1 组件表更新为 `ChapterFactProvider` 已是代码事实，`facet_recognizer` / `FundToolService` 仍为未来候选；保留 writer/auditor/orchestrator/Service/dayu 未实现边界 |

---

## Findings

### F1 [INFO] `_normalize_basis` 未覆盖的 edge case 分支

**位置**：`chapter_facts.py:547,572,574,577`

**描述**：`_normalize_basis` 中 `isinstance(value, str)` 空字符串分支、`isinstance(value, (tuple, list))` 内元素空字符串过滤、以及 fallback `str(value)` 路径未被测试覆盖。

**影响**：无。这些是防御性分支，当前 bundle fixture 已覆盖主路径。97% 覆盖率远超 80% 目标。

**建议**：无需补测。后续如有 regression 需要再加。

### F2 [INFO] `_project_field_fact` 对未知字段类型 ValueError 路径未覆盖

**位置**：`chapter_facts.py:923`

**描述**：当 `getattr(bundle, spec.field_name)` 既不是 `ExtractedField` 也不是 `nav_data` 时的 `raise ValueError` 路径未被测试覆盖。

**影响**：无。当前 `_CHAPTER_FIELD_SPECS` 中所有字段均为 `ExtractedField` 或 `NavDataResult`，该路径不可达。

**建议**：保持。作为 fail-safe 设施存在即可。

### F3 [INFO] `_dedupe_chapter_anchors` hash 碰撞后缀路径未覆盖

**位置**：`chapter_facts.py:1272`

**描述**：当两个不同 anchor 生成相同 base_id 时的 `-2`/`-3` 后缀处理路径未被测试覆盖。

**影响**：无。当前 test fixture 的锚点参数天然不碰撞，该路径极难触发。

**建议**：保持。实现逻辑正确，collision 后缀策略是 deterministic 的。

### F4 [INFO] `_ensure_fact_anchor_refs_exist` ValueError 路径未覆盖

**位置**：`chapter_facts.py:1431`

**描述**：当 fact 引用不存在的 anchor 时的 `raise ValueError` 路径未被测试覆盖。

**影响**：无。实现正确构造了 anchor refs，该路径是防御性 fail-safe。

**建议**：保持。正常数据流不会触发此路径。

### F5 [INFO] `test_bond_risk_evidence` 锚点 assertion 可更精确

**位置**：`tests/fund/test_chapter_facts.py:379`

**描述**：`assert all(not anchor.anchor_id.startswith("bond-risk:") for anchor in chapter.evidence_anchors)` 断言 chapter anchors 不以 `"bond-risk:"` 开头。由于 `_dedupe_chapter_anchors` 生成的 ID 前缀是 `"chapter-anchor:"`，该断言在任何实现下恒为 True，不直接验证 bond_risk_evidence 特殊路径。

**影响**：无。该 test 的核心断言在 line 375-377（`status=="available"`、`value==原始值`、`evidence_anchor_ids==()`），已充分验证 bond_risk_evidence 不展开策略。line 379 是补充性 assertion，不构成漏洞。

**建议**：保持。核心语义已被 line 375-377 覆盖。

---

## Coverage analysis

| 文件 | Stmts | Miss | Cover | 未覆盖行 |
|------|-------|------|-------|----------|
| `fund_agent/fund/chapter_facts.py` | 291 | 10 | 97% | 547, 572, 574, 577, 859, 923, 1110, 1272, 1402, 1431 |

所有未覆盖行均为防御性 edge case 或 error fail-safe 路径，不影响投影核心语义。

---

## Residual risks

与 implementation evidence 一致：

1. `ChapterFactEntry.value` 保持 `object | None`，匹配 plan 设计和当前异构 bundle 字段。后续 writer/auditor gate 应按消费方需求 narrowing。
2. facet 精确断言故意为空，直到未来 structured field 存储 exact subtype evidence。Route C writer 必须将 `non_asserted_facets` 视为解释性标签。
3. `bond_risk_evidence` 组级 anchors 未展开为 `ChapterEvidenceAnchor`；未来 gate 如需 per-group chapter anchor navigation，应实现专用 expansion contract。

---

## Conclusion

Implementation **PASS**。实现严格符合 accepted plan，无 scope creep，typed contract 完整且稳定，测试覆盖充分（13 tests / 97% coverage），文档同步准确。5 个 INFO findings 均为防御性分支未覆盖或 assertion 可更精确，不构成阻塞风险。
