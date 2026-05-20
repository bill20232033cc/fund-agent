# Code Review

## Scope

- Mode: current changes
- Branch: main
- Base: d33b901fd1bee9f85206df461cc6419a813bcbae (post-P5 baseline)
- HEAD: a993739
- Output file: `docs/reviews/p6-aggregate-deepreview-glm-20260520.md`
- Included scope: P6-S1 through P6-S5 — `fund_agent/fund/template/contracts.py` (new), `fund_agent/fund/template/chapter_blocks.py` (new), `fund_agent/fund/template/item_rules.py` (new), `fund_agent/fund/audit/contract_rules.py` (new), `fund_agent/fund/template/__init__.py`, `fund_agent/fund/template/renderer.py`, `fund_agent/fund/audit/audit_programmatic.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/implementation-control-p4.md`, all P6 test files
- Excluded scope: Service/UI/CLI source, `docs/fund-analysis-template-draft.md`, `docs/design.md` content-only edits for P6 status tracking, runtime reports, launchd, scripts, review artifacts
- Parallel review coverage: 无，单 reviewer 全量走读；subagent 辅助 contracts.py/chapter_blocks.py/quality_gate.py/renderer marker 覆盖率交叉校验

## Findings

未发现实质性问题。

## Verification Evidence

### Test Suite

```
246 passed in 0.98s
ruff check: All checks passed!
git diff --check: clean
```

### Import Cycle Verification

```text
contracts.py ← chapter_blocks.py ← audit_programmatic.py    ✅ 无 cycle
contracts.py ← chapter_blocks.py ← renderer.py              ✅ 无 cycle
contracts.py ← item_rules.py                                ✅ 无 cycle
contracts.py ← contract_rules.py ← audit_programmatic.py    ✅ 无 cycle
contracts.py ← extraction_score.py                          ✅ 无 cycle
__init__.py __getattr__ lazy loading                        ✅ renderer 不被 audit/item_rules 加载
Python sys.modules verification                             ✅ audit import 后 renderer 未加载
```

### CHAPTER_CONTRACT Manifest Completeness

| Chapter | Title | must_answer | must_not_cover | required_output_items | Lens Keys |
|---|---|---|---|---|---|
| 0 | 投资要点概览 | 9 | 8 | 9 | default + 6 FundType |
| 1 | 这只基金到底是什么产品 | 6 | 3 | 6 | 6 FundType (no default) |
| 2 | R=A+B-C 收益归因 | 6 | 3 | 7 | default + index_fund |
| 3 | 基金经理画像与言行一致性 | 6 | 3 | 6 | default + 6 FundType |
| 4 | 投资者获得感 | 4 | 2 | 4 | default + index/active/bond |
| 5 | 当前阶段与关键变化 | 5 | 2 | 4 | default + 6 FundType |
| 6 | 核心风险与否决项 | 4 | 3 | 4 | default + 6 FundType |
| 7 | 是否值得持有——最终判断 | 5 | 3 | 5 | default + 6 FundType |

- 8 章全部存在，chapter_id 严格 0-7 递增。 ✅
- `validate_template_contract_manifest` 对每个 FundType 检查每章要么有精确 lens 要么有 default fallback。 ✅
- 45 条 required_output_items 全部由 `contract_rules.py` 的 marker 规则覆盖。程序验证 `manifest_items == rule_items`。 ✅

### Renderer ↔ Required Marker Alignment

端到端验证：使用 `_render_input()` fixture 生成完整报告，`split_rendered_chapter_blocks` 切成 8 块，逐一检查 45 条 required marker 是否出现在对应 chapter body_markdown 中。

```
Blocks: 8, Missing: 0, Forbidden: 0
Audit: passed=True, issues=0, rules=('P1', 'P2', 'P3', 'C2', 'L1', 'R1', 'R2')
```

- 全部 45 条 required_output_items 的 marker 字面量在渲染输出中可找到。 ✅
- 全部 9 条 forbidden content marker（`证据与出处`、`未来收益预测`、`性格`、`人品`、`动机`、`具体投资者的交易行为`、`未来投资者行为预测`、`市场整体走势预测`、`风险发生概率`、`买入金额`、`卖出时机`、`仓位比例`）在当前渲染输出中未产生误报。 ✅

### ITEM_RULE Manifest Exactness

| Rule | chapter_id | mode | fund_types_any | Verified |
|---|---|---|---|---|
| chapter_1_index_constituents | 1 | conditional | index_fund, enhanced_index | ✅ |
| chapter_1_manager_philosophy | 1 | conditional | active_fund | ✅ |
| chapter_2_alpha_yearly_breakdown | 2 | conditional | active_fund, enhanced_index | ✅ |
| chapter_2_tracking_error_analysis | 2 | conditional | index_fund, enhanced_index | ✅ |

- `_BUILT_IN_RULE_IDS` 精确匹配四条规则，增删时 validation fail closed。 ✅
- `_FACET_FUND_TYPE_MAP` 7 条映射与规则 `facets_any`/`fund_types_any` 一致。 ✅
- `_FORBIDDEN_SEGMENT_MARKERS` 拒绝 5 条普通正文短语。 ✅
- 显式 facet 冲突（`bond_fund + 指数增强基金`）→ `ValueError`。 ✅
- 未知 facet → 静默忽略，不触发规则。 ✅

### FQ5 Contract Applicability

- 状态三值：`resolved` / `not_applicable` / `mismatch`。 ✅
- `mismatch` 触发 `FQ5/block`；`resolved` 和 `not_applicable` 仅进入 rule_results。 ✅
- 多值 `classified_fund_type` 冲突 → 最高优先级 mismatch。 ✅
- 旧 `"match"` 值通过 `_normalize_preferred_lens_status` 兼容为 `"resolved"`。 ✅
- `extraction_score.py` 只导入 contracts/item_rules（纯 Python 数据结构），不访问 PDF/cache/documents。 ✅
- `quality_gate.py` 只消费 `score.json`。 ✅

### Layer Boundary Compliance

| 检查项 | 结果 |
|---|---|
| Capability 层不依赖 Service/UI/CLI | ✅ |
| `contracts.py` 不导入 renderer | ✅ |
| `chapter_blocks.py` 不导入 renderer | ✅ |
| `item_rules.py` 不导入 renderer | ✅ |
| `contract_rules.py` 不导入 renderer | ✅ |
| `audit_programmatic.py` 不导入 renderer | ✅ |
| P6 代码无 PDF/cache/document 直接访问 | ✅ |
| P6 代码无 `extra_payload` 使用 | ✅ |
| `docs/fund-analysis-template-draft.md` 未修改 | ✅ |

### Overclaiming Prevention

- README 明确写明 FQ5 "不解析最终报告 Markdown，也不证明 renderer 已遵守 preferred_lens 或正确渲染/删除 ITEM_RULE 段落"。 ✅
- README 明确写明 "当前 CHAPTER_CONTRACT manifest 是可机器消费的契约清单，不改变 render_template_report() 的 Markdown 输出结构"。 ✅
- FQ5 不宣称 renderer compliance。 ✅

### Splitter Fail-Closed

| 场景 | 行为 |
|---|---|
| 空文本 | `ValueError` ✅ |
| 无 H1 标题 | `ValueError` ✅ |
| 非模板 H1 混入 | `ValueError` ✅ |
| chapter_id 越界 | `ValueError` ✅ |
| 标题与契约不匹配 | `ValueError` ✅ |
| 重复章节 | `ValueError` ✅ |
| 缺失章节 | `ValueError` ✅ |
| 乱序章节 | `ValueError` ✅ |
| 证据附录不进入 chapter 7 body | ✅ |

## Open Questions

- 无

## Residual Risk

1. **Chapter 0 信息重复**：`R=A+B-C 净超额` 和 `超额性质` 在新结构化 marker 和旧自由文本 bullet 中各出现一次（`renderer.py:182` 和 `renderer.py:186`）。非正确性问题，但公式变化时需同步更新两行。后续模板清理应考虑删除旧的自由文本 bullet。

2. **Chapter 2/4 显式 lens 覆盖不完整**：Chapter 2 只有 `default` + `index_fund`，Chapter 4 只有 `default` + `index/active/bond`。其他基金类型回退到 `default` 通用 lens。非 bug（validation 允许 default fallback），但 `active_fund` 和 `enhanced_index` 对收益归因章的分析视角确实与指数基金不同。后续 lens 扩展 slice 可补充。

3. **Chapter 1 无 default lens**：其他 7 章都有 `"default"` 作为安全 fallback，唯独 Chapter 1 全靠 6 个显式 FundType lens。如果 `FundType` Literal 扩展且忘记补 Chapter 1 的 lens，validation 会 fail closed（正确行为），但维护者可能困惑为何 Chapter 1 是唯一需要显式覆盖每类型的章节。

4. **`_SUPPORTED_FUND_TYPES` 重复定义**：`contracts.py:21-28` 和 `item_rules.py:22-29` 分别硬编码了与 `FundType` Literal 相同的 tuple。如果 `FundType` 扩展，两个文件需手动同步。Validation 会在运行时捕获不一致，但无静态/type-level 联动。

5. **Forbidden marker substring 匹配**：C2 审计使用字面子串匹配检查 `must_not_cover`。常见词如 `动机`（Chapter 3）或 `性格`（Chapter 3）理论上可能出现在合法基金策略文本中。当前渲染器不直接输出原始策略全文（通过 `_value_text` 提取特定字段），实际风险极低，但若后续 renderer 改为输出更完整的策略文本，需复核 forbidden marker 的误报风险。

6. **`facets_any` 仅信息性**：`TemplateLensRule.facets_any` 携带细分标签但不被 `resolve_preferred_lens()` 消费。`TemplateItemRule.facets_any` 则被 evaluator 实际使用。两处 `facets_any` 语义不同但名称相同，可能造成维护者混淆。

7. **`load_template_contract_manifest()` 每次调用重新 validation**：module-level 常量 `_MANIFEST` 不可变，但 `load_template_contract_manifest()` 每次都执行完整 validation（8 章 × 6 FundType × 所有 tuple）。性能影响可忽略，但属于设计味道。可考虑 import-time validate-once 或 `functools.lru_cache`。

8. **ITEM_RULE 未接入程序审计**：P6-S4 的 ITEM_RULE manifest 和 evaluator 不接入 `run_programmatic_audit`。后续 slice 需决定是否新增规则码或扩展 C2。

9. **`priority` 字段无闭集校验**：`TemplateLensRule.priority` 为 `str | None`，实际值为 `"core"/"high"/"medium"/"low"`，但 validation 只检查非空。拼写错误如 `"cor"` 会静默通过。
