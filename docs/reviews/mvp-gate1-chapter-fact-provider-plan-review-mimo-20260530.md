# Plan Review: MVP Gate 1 ChapterFactProvider typed projection

日期：2026-05-30
Reviewer：AgentMiMo
Plan artifact：`docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md`

## Verdict：PASS_WITH_NON_BLOCKING

Plan 整体质量高，gate 定位清晰、边界严格、typed contract 设计 implementation-ready，non-blocking findings 均可在实现阶段修正。

---

## Gate 定位检查

- [x] 严格停在 Gate 1 ChapterFactProvider typed projection
- [x] 没有 writer/auditor/orchestrator/CLI/dayu scope creep
- [x] 没有完整 FundToolService 过度设计
- [x] 使用 StructuredFundDataBundle + CHAPTER_CONTRACT/preferred_lens/ITEM_RULE 真源
- [x] facet inference deterministic 且不让 LLM/文本猜 subtype
- [x] typed contract 足够 implementation-ready
- [x] missing/unavailable/anchor/source-field semantics 清晰
- [x] tests/validation 足够
- [x] 不违反 AGENTS UI->Service->Host->Agent/FundDocumentRepository/extra_payload 边界

---

## Findings

### F1 [LOW] §7 `_ChapterFieldSpec` 缺少 `not_applicable_when` 字段

**位置**：§7 Chapter field mapping

**描述**：§7 开头列出 `_ChapterFieldSpec` 至少包含 `not_applicable_when`，但 §1 Slice 1 的 dataclass 定义中没有此字段：

```python
# §7 声明至少包含
- chapter_id / field_name / source_field_id / required_by / not_applicable_when / item_rule_ids

# §1 Slice 1 实际定义
@dataclass
class _ChapterFieldSpec:
    chapter_id: int
    field_name: str
    source_field_id: str
    required_by: tuple[str, ...]
    item_rule_ids: tuple[str, ...] = ()
```

**建议**：二选一：
1. 在 `_ChapterFieldSpec` 中添加 `not_applicable_when: tuple[str, ...] = ()`，并让实现通过此字段驱动 `field_not_applicable` 语义；
2. 从 §7 声明中删除 `not_applicable_when`，明确 `not_applicable` 语义完全由运行时 fund type + field note 驱动（如 §9 所述）。

推荐方案 2，因为 §9 已经明确定义了 `field_not_applicable` 的运行时判定逻辑（按 fund type + note），预置静态条件反而可能与运行时 note 冲突。

### F2 [LOW] §7 特殊缺口 `bond_risk_evidence` 的 anchor 处理未在 field mapping 中体现

**位置**：§7 / §8

**描述**：§8 明确指出 `bond_risk_evidence.value.anchors` 是组级 `BondRiskEvidenceAnchorRef`，不同于普通 `EvidenceAnchor`，本 gate 不强行拆成普通 `ChapterEvidenceAnchor`。但 §7 field mapping 表中 `bond_risk_evidence` 出现在第 0/6/7 章的 source fields 里，没有标注其特殊 anchor 语义。

**建议**：在 §7 mapping 表下方补充说明：`bond_risk_evidence` 作为 fact value 投影时，其内部 anchor ref 保留在 value 内，不生成 `ChapterEvidenceAnchor`；或在 `_CHAPTER_FIELD_SPECS` 中对 `bond_risk_evidence` 添加特殊标记，让 `_project_field_fact` 走不同路径。这样实现者不会在 Slice 2 中混淆两种 anchor。

### F3 [LOW] §13 test plan 缺少 `test_chapter_id_validation_fails_closed` 的具体断言

**位置**：§13 Test plan / §1 Slice 1 Tests

**描述**：§1 Slice 1 Tests 列出了 `test_chapter_id_validation_fails_closed`，§13 也列出了此 case 并说明 `()`、重复、负数、`8` 均 `ValueError`。但没有说明是否需要测试边界值如 `(0,)` 合法单章、`(7,)` 合法尾章、`(0, 1, 2, 3, 4, 5, 6, 7)` 全量合法。

**建议**：补充 happy path 边界 case：`test_chapter_id_validation_accepts_valid_range`，覆盖 `(0,)`、`(7,)`、全量 8 章，确保 validation 不仅 fail closed 也 pass correct。

### F4 [INFO] §4 public API 中 `ChapterFactProvider` 的定位可更明确

**位置**：§4 推荐总体方案

**描述**：§4 说 "`ChapterFactProvider` 只是 typed provider façade，不是 `FundToolService`"，但没有说明它是 concrete class 还是 Protocol。从 Slice 2 看它是 concrete class 带 `project()` 方法。

**建议**：在 §4 中明确标注 `ChapterFactProvider` 是 concrete frozen class（非 Protocol），避免实现者在 class vs Protocol 上产生歧义。

### F5 [INFO] §11 ITEM_RULE 全局调用时机可更精确

**位置**：§11 Preferred lens / ITEM_RULE 规则

**描述**：§11 说 "projection 级别先调用一次 `evaluate_template_item_rules(fund_type=fund_type, facets=())`"，但 §10 facet inference 规则 3 也说了同样的话。两处重复但措辞略有不同（§10 说"默认调用"，§11 说"先调用一次"）。

**建议**：在 §11 中引用 §10 规则 3 而非重复，或统一措辞为"全局一次性调用，结果按 chapter_id 分发"，消除歧义。

### F6 [INFO] §13 缺少 `ChapterFactProvider.project()` 的显式测试

**位置**：§13 Test plan

**描述**：test plan 中所有 case 都以 `project_chapter_facts()` 函数为入口，没有显式测试 `ChapterFactProvider.project()` 方法。虽然它只是 façade delegate，但作为 public API 之一，至少需要一个 smoke test。

**建议**：添加 `test_chapter_fact_provider_delegates_to_project_chapter_facts`，验证 `ChapterFactProvider().project(bundle)` 与 `project_chapter_facts(bundle)` 结果一致。

---

## 实现风险评估

| 风险 | 等级 | 说明 |
|------|------|------|
| Scope creep 到 writer/auditor/orchestrator | 低 | Non-goals §3 和 stop conditions §16 足够严格 |
| 破坏现有 deterministic analyze/checklist 行为 | 低 | 新增模块不改现有代码，§3 明确声明 |
| `StructuredFundDataBundle` schema 变更 | 低 | §1 Slice 1 stop condition 明确禁止 |
| facet inference fail open | 低 | §10 规则明确 unknown 必须 empty + 记录原因 |
| anchor dedupe 碰撞 | 低 | §8 已定义 hash8 + `-2`/`-3` 后缀策略 |
| `nav_data` 特殊处理遗漏 | 中 | `nav_data` 是 `NavDataResult` 非 `ExtractedField`，需要独立 projection path；plan 在 §6 已列出但 §7 mapping 表未标注差异 |

---

## 与真源的一致性检查

| 真源 | 一致性 |
|------|--------|
| `AGENTS.md` 模块边界 | 一致：projection 在 `fund_agent/fund/`，不触碰 Service/Host/dayu |
| `AGENTS.md` FundDocumentRepository 约束 | 一致：§3/§4 明确禁止 repository/PDF/cache import |
| `AGENTS.md` extra_payload 禁令 | 一致：所有参数显式声明在 typed dataclass |
| `docs/design.md` §5.4 Route C Gate 1 | 一致：plan 严格对应 facet_recognizer + ChapterFactProvider scope |
| `docs/fund-analysis-template-draft.md` 8 章结构 | 一致：chapter_ids 0-7，contract/lens/item_rule 来自现有 manifest |
| `fund_agent/fund/fund_type.py` FundType 闭集 | 一致：plan 使用相同 6 种类型 + `"unknown"` |
| `fund_agent/fund/template/contracts.py` API | 一致：plan 消费 `get_chapter_contract()` / `resolve_preferred_lens()` |
| `fund_agent/fund/template/item_rules.py` API | 一致：plan 消费 `evaluate_template_item_rules()` |
| `fund_agent/fund/data_extractor.py` StructuredFundDataBundle | 一致：plan §6 source field ids 准确对应 bundle 字段 |

---

## 结论

Plan 通过 review gate。6 个 findings 均为 LOW/INFO 级别，不阻塞 implementation。建议在 Slice 1/2 实现阶段按上述建议修正 F1-F3，F4-F6 可作为 implementation evidence 的备注项。
