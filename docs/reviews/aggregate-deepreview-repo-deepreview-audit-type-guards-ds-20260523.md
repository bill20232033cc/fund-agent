# Aggregate Deepreview — repo-deepreview-audit-type-guards

## Scope

- Mode: aggregate deepreview (current changes, second reviewer pass)
- Branch: `fix/repo-deepreview-audit-type-guards`
- Base: `main`
- Reviewed target: commit `2e2373d` 及当前分支相对 main 的完整 diff
- Output file: `docs/reviews/aggregate-deepreview-repo-deepreview-audit-type-guards-ds-20260523.md`
- Included scope: Slice A/B — C2 must_not_cover 覆盖完整性、Ch0 required marker 独立可审计、bool 数值输入防御
- Excluded scope: pre-existing untracked docs（非本 work unit 提交内容），完整仓库非 Fund 模块
- Parallel review coverage: 无
- Prior reviews: AgentMiMo initial code review (no blocker, 1 low-severity consistency finding) → fix → AgentMiMo re-review (finding fixed, no new findings) → controller accepted slice
- Pre-existing untracked docs under `docs/` not reviewed as they are not part of this work unit's committed changes

## Verification Baseline

- `uv run pytest -q`: **549 passed in 1.18s**
- `uv run ruff check .`: **All checks passed!**
- Controller acceptance: commit `2e2373d`

---

## Findings

### 1-未修复-低-`validate_programmatic_contract_rules` 重复加载 coverage manifest 引入冗余校验但无 correctness 风险

- **入口/函数**: `fund_agent/fund/audit/contract_rules.py:510` `validate_programmatic_contract_rules`
- **文件(行号)**: `fund_agent/fund/audit/contract_rules.py:510-531`
- **输入场景**: 任何调用 `validate_programmatic_contract_rules` 的路径（包括 `load_programmatic_contract_rules`、测试等）
- **实际分支**: 第 526 行 `coverage_manifest = load_contract_audit_coverage_manifest()` 触发完整 manifest 校验（包括以默认 `_FORBIDDEN_CONTENT_RULES` 为参照的 `_validate_must_not_cover_coverage_rules`），随后第 527 行再次以 `rules.forbidden_contents` 为参照调用同一函数
- **预期行为**: 两次校验均以不同的 `forbidden_content_rules` 为参照，构成纵深防御。正常路径下二者等价（`_FORBIDDEN_CONTENT_RULES` 是 Final），第二次校验为主校验
- **实际行为**: 功能正确，但调用者难以从代码结构直接判断第一次冗余校验是否非必需。当前无 bug，但若未来 `load_contract_audit_coverage_manifest` 的校验增强为有副作用（如日志输出），重复调用可能引入重复副作用
- **直接证据**: `contract_rules.py:526-531` — `load_contract_audit_coverage_manifest()` 内部调用 `validate_contract_audit_coverage_manifest` 以默认 forbidden rules 校验 must_not_cover；随后显式调用 `_validate_must_not_cover_coverage_rules(coverage_manifest, manifest, rules.forbidden_contents)` 以实际 forbidden rules 再校验
- **影响**: 无 correctness 影响。仅 maintainability 方面的轻微冗余
- **建议改法和验证点**: 可考虑让 `validate_contract_audit_coverage_manifest` 接受可选的 `forbidden_content_rules` 参数以消除冗余调用，或将 `load_contract_audit_coverage_manifest` 的 manifest 级校验与 programmatic-rules 级校验显式分层。当前状态可接受
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

---

## 重点审查结论

### CHAPTER_CONTRACT fail-closed 逻辑

- **`_validate_must_not_cover_coverage_rules`**（`contract_rules.py:637-681`）正确实现反向完整覆盖：
  - 从 manifest 提取全部 must_not_cover 条目（第 657 行）
  - 计算程序化 forbidden marker 覆盖集合（第 658-661 行）
  - 校验非程序化路由的有效性：去重（第 664-667 行）、匹配 manifest（第 668-669 行）、类型/rationale 校验（第 670 行）
  - 拒绝程序化与非程序化重叠覆盖（第 672-675 行）
  - 拒绝缺失覆盖（第 677-681 行）
- **双重调用路径**确保 fail-closed：
  1. `validate_contract_audit_coverage_manifest` → `_validate_must_not_cover_coverage_rules(coverage_manifest, template_manifest)` 使用默认 `_FORBIDDEN_CONTENT_RULES`
  2. `validate_programmatic_contract_rules` → `_validate_must_not_cover_coverage_rules(coverage_manifest, manifest, rules.forbidden_contents)` 使用实际程序规则
- **删除程序化 forbidden rule 会 fail-closed**：`test_programmatic_contract_rules_fail_closed_for_uncovered_must_not_cover`（`test_audit_programmatic.py:893-922`）已验证删除 `"不输出"证据与出处"小节。"` 规则后抛出 `ValueError`
- **结论：fail-closed 逻辑正确，无 gap**

### narrative_guidance 覆盖路由

- **33 template must_not_cover = 9 programmatic forbidden marker rules + 24 narrative_guidance routes**
- **0 overlap / 0 gap / 0 extra**：`test_contract_audit_coverage_manifest_covers_every_must_not_cover`（`test_audit_programmatic.py:932-964`）已验证
  - `assert programmatic_items | non_programmatic_items == manifest_items`（集合等价）
  - `assert programmatic_items.isdisjoint(non_programmatic_items)`（无重叠）
  - `assert len(coverage_manifest.must_not_cover_coverages) == 24`（精确数量）
- **Ch6 "不预测收益或市场走势"** 与 Ch2 programmatic "不做未来收益预测" 在不同章节，key 不同 `(6, ...)` vs `(2, ...)`，不构成重叠。rationale 显式声明"复合禁止项；未来收益由第 2 章程序规则覆盖，市场走势部分保留为非程序化覆盖"——准确反映设计意图
- **narrative_guidance 路由不执行语义审计**：这是已知设计权衡，非 defect。路由防止 manifest 覆盖缺口（fail-closed coverage accounting），但不证明 LLM 输出是否真正遵守禁止项语义
- **结论：覆盖路由无 gap/overlap/extra，静默降级风险已通过 fail-closed 校验消除**

### Ch0 renderer 输出一致性

- **Marker 独立性**：`test_chapter_0_required_items_use_distinct_markers`（`test_audit_programmatic.py:1048-1074`）验证：
  - `"这是什么基金："` 与 `"基金简介："` marker 集合互不重叠（`isdisjoint`）
  - 两个 marker 均出现在渲染后的 Ch0 输出中
- **`_REQUIRED_ITEM_RULES` 更新**（`contract_rules.py:138-139`）：
  - `"一句话这是什么基金"` → marker `("这是什么基金：",)`
  - `"基金简介"` → marker `("基金简介：",)`
  - 与 renderer 输出第 340-341 行一致
- **Renderer 输出映射**（`renderer.py:340-341`）：
  - `这是什么基金：` 覆盖基金名、代码、类型（对应 must_answer 第 0 章 Q1）
  - `基金简介：` 覆盖基金经理、管理规模、成立时间（对应 must_answer 第 0 章 Q2）
  - `_value_text` 缺失降级为 "未披露"，行为一致
- **e2e 测试更新**（`test_p3_cli_e2e_matrix.py:562-563`）：`"这是什么基金："` 和 `"基金简介："` 断言替代旧 `"基金："` / `"基金类型："` 断言，对齐新输出格式
- **结论：Ch0 renderer 输出与 required_output_items、测试、模板目标一致**

### bool guard 一致性

- **Slice B 全部 6 个数值入口均已添加显式 bool 拒绝**：
  1. `parse_ratio`（`_ratios.py:32-33`）：`isinstance(value, bool)` → `ValueError("不能为布尔值")`
  2. `checklist._parse_decimal`（`checklist.py:748-749`）：同上
  3. `investor_return._parse_decimal`（`investor_return.py:390-391`）：同上（fix cycle 补充）
  4. `risk_check._parse_decimal`（`risk_check.py:983-984`）：同上
  5. `quality_gate._required_number`（`quality_gate.py:1180`）：`isinstance(value, bool) or not isinstance(value, int | float)`
  6. `quality_gate._required_quality_number`（`quality_gate.py:992`）：同上
- **Reject-first 顺序正确**：所有 guard 均在 `isinstance(value, int | float)` 或 `str(value)` 之前执行，阻止 Python `bool` 作为 `int` 子类被静默转为 0/1
- **合法输入不受影响**：`int`、`float`、`Decimal`、numeric string 仍通过原有路径解析
- **`_optional_correctness_int`**（`quality_gate.py:1119`）：已预置 bool guard，本次未修改，与新增 guard 一致
- **测试覆盖**：6 个入口各自有独立测试（`test_ratios.py`、`test_checklist.py`、`test_investor_return.py`、`test_risk_check.py`、`test_quality_gate.py`），覆盖 `True` 和 `False` 场景
- **结论：bool guard 一致，不破坏合法输入**

### 测试与 artifacts

- **Focused module tests**: 114 passed（fix artifact 记录）
- **Full test suite**: **549 passed in 1.18s**（本次 aggregate review 验证）
- **Ruff**: All checks passed
- **Artifact chain**: implementation → code review → fix → re-review → accepted slice → aggregate deepreview（本次），完整闭环
- **测试覆盖关键面**：
  - must_not_cover 完整覆盖、fail-closed（缺失/重复/未知路由/删除程序规则）
  - Ch0 marker 独立性
  - bool guard 6 个入口
  - e2e 集成回归（`test_p3_cli_e2e_matrix.py` 已更新以匹配新输出格式）
- **结论：测试和 artifacts 充分支持 ready-to-open-draft-PR 前的本地 gate**

---

## Open Questions

无。

本次 aggregate review 在已有 AgentMiMo code review + fix + re-review + controller acceptance 的基础上进行独立复核，未发现新的 correctness/stability/maintainability 问题。

---

## Residual Risk

1. **narrative_guidance 路由声明式覆盖，不执行语义审计**。24 条 `narrative_guidance` 路由防止 manifest 覆盖缺口（fail-closed coverage accounting），但不能证明 LLM 输出是否真正遵守禁止项语义。这是已知设计权衡，已在 controller accepted slice evidence 中确认接受。

2. **`test_contract_audit_coverage_manifest_covers_every_must_not_cover` 硬编码 `== 24`**。template 新增/删除 `must_not_cover` 条目时此断言会失败，迫使同步更新。这是有意的 regression guard，但需要维护者知道此约束存在。

3. **Ch0 renderer 新增字段依赖上游提取器**。`fund_manager`、`fund_scale`、`inception_date` 若 `basic_identity` 提取器未覆盖，封面持续显示 "未披露"。这是数据源已知缺口，非本次引入。

4. **Ch0 "支撑当前动作的最主要理由" 与 "最终判断" 输出重复**。两行均展示 `checklist_result.overall_signal / overall_status`，语义重复。这是 pre-existing 行为，不在本次 diff 范围内。

5. **`validate_programmatic_contract_rules` 中 redundancy**（见 Finding 1）。两次 `_validate_must_not_cover_coverage_rules` 调用以不同 `forbidden_content_rules` 为参照，构成纵深防御但引入轻微冗余。当前无 correctness 影响。

---

## 结论

- **Findings**: 1（低严重度）
- **最高严重度**: 低
- **Blocker**: 无
- **Artifact 路径**: `docs/reviews/aggregate-deepreview-repo-deepreview-audit-type-guards-ds-20260523.md`

相对 main 的完整 diff 未引入 correctness/stability/maintainability regression。CHAPTER_CONTRACT fail-closed 逻辑正确，narrative_guidance 覆盖路由无 gap/overlap/extra，Ch0 renderer 输出与契约一致，bool guard 覆盖完整且不破坏合法输入。549 tests 全部通过。支持 ready-to-open-draft-PR。
