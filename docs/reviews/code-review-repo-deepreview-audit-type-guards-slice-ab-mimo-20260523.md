# Code Review

## Scope

- Mode: current changes
- Branch: fix/repo-deepreview-audit-type-guards
- Base: main (working tree diff)
- Output file: docs/reviews/code-review-repo-deepreview-audit-type-guards-slice-ab-mimo-20260523.md
- Included scope: Slice A/B — C2 must_not_cover 覆盖完整性、Ch0 required marker 独立可审计、bool 数值输入防御
- Excluded scope: 非 Slice A/B 的模板章节变更、完整仓库 test suite
- Parallel review coverage: 无

## Findings

未发现实质性问题。

以下为低严重度观察项，不构成 merge blocker：

### 1-未修复-低-investor_return._parse_decimal 缺少显式 bool 拒绝

- **入口/函数**: `fund_agent/fund/analysis/investor_return.py:374` `_parse_decimal`
- **文件(行号)**: `fund_agent/fund/analysis/investor_return.py:374-396`
- **输入场景**: 份额数据中出现 `True` / `False`
- **实际分支**: `str(True)` → `"True"` → `Decimal("True")` → 抛出 `InvalidOperation`
- **预期行为**: bool 输入应被显式拒绝，与本 slice 其他 `_parse_decimal` 保持一致
- **实际行为**: 功能上安全（bool 转字符串后 Decimal 解析失败），但拒绝路径不一致
- **直接证据**: `investor_return.py:390` `text = str(value).replace(",", "").strip()` 对 bool 产生 `"True"`/`"False"` 字符串，随后 `Decimal(text)` 在 `:394` 失败
- **影响**: 无 correctness 风险；维护一致性低，后续统一 bool 防御时可能遗漏此入口
- **建议改法和验证点**: 在 `:388` 之前添加 `if isinstance(value, bool): raise ValueError(...)`，与 `_ratios.py:32` 对齐
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

无。

## Residual Risk

1. **非程序化 must_not_cover 路由仅声明覆盖责任，不执行语义审计**。`narrative_guidance` 路由防止 manifest 覆盖缺口，但不能证明 LLM 输出是否真正遵守禁止项。这是设计权衡，非 defect。
2. **investor_return._parse_decimal 未加入 bool guard**（见 Finding 1）。功能安全但不一致。不在本 slice 改动范围内，建议 follow-up 统一。
3. **完整仓库 test suite 未在本 work unit 运行**。implementation artifact 记录了 focused modules 全部通过（107 + 97 + 1），但未覆盖跨模块回归。
4. **test_contract_audit_coverage_manifest_covers_every_must_not_cover 硬编码 `== 24`**。template 新增/删除 must_not_cover 条目时此断言会失败，这是有意的 regression guard，但需同步更新。
5. **renderer Ch0 新增 `fund_manager` / `fund_scale` / `inception_date` 字段**。`_value_text` 对缺失值返回 "未披露"，行为正确。但如果上游 `basic_identity` 提取器未覆盖这三个字段，封面会持续显示 "未披露"。这是数据源已知缺口，非本次引入。

## 验证摘要

- must_not_cover 覆盖完整性：33 template items = 9 forbidden rules + 24 coverage rules，0 overlap / 0 gap / 0 extra ✓
- Ch0 marker 独立性：`"这是什么基金："` 与 `"基金简介："` 互不重叠 ✓
- bool guard 覆盖：5/5 本 slice 入口均已添加 ✓
- renderer 新字段：`_value_text` 缺失降级为 "未披露" ✓
- tests：focused modules 107 passed / 97 passed / 1 passed ✓
