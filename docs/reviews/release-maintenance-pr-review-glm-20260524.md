# Code Review — PR #16

## Scope

- Mode: PR
- PR: https://github.com/bill20232033cc/fund-agent/pull/16
- Title: Codex/checklist host engine design
- Author: bill20232033cc
- Branch: codex/checklist-host-engine-design (HEAD: 23a3c320fd0fa9a317f0803fe567125ca9dc9125)
- Base: main (3769def95badb5d89ba32db4ff4fa00443dbcd44)
- Output file: docs/reviews/release-maintenance-pr-review-glm-20260524.md
- Included scope: 完整 PR diff（~130 个文件）；重点 review 生产代码（fund_agent/）、测试（tests/）、CI（.github/workflows/）、配置（pyproject.toml）、架构文档（AGENTS.md、docs/design.md、docs/implementation-control.md）
- Excluded scope: docs/reviews/ 审查产物文件（~80 个 .md 文件，仅抽样验证）、docs/20260430/ 历史研究文件、uv.lock
- Parallel review coverage:
  - Subagent A: 架构边界护栏验证（5 项护栏 + 旧六层措辞清理检查）
  - Subagent B: 全量生产代码变更逐文件审查（fund_agent/ 下 42 个文件）
  - Subagent C: 测试/CI/pyproject.toml 变更审查
  - 未覆盖区域: docs/reviews/ 下的审查产物文件仅抽样检查关键词，未逐文件走读

## PR Facts

| Field | Value |
|---|---|
| State | OPEN |
| CI | test pass (20s) |
| Commits (range) | main...23a3c32 |
| Files changed | ~130 |

## PR Intent

本 PR 是 release maintenance 阶段的架构对齐与功能增强合并，核心变更：

1. **术语统一**：从旧六层（Application/Runtime/Engine/Capability）全面迁移到 Dayu 四层（UI/Service/Host/Agent），涉及 ~25 个生产文件的 docstring 更新
2. **第 0 章渲染增强**：renderer.py 新增 ~250 行结构化风险文本生成，替换 `_INSUFFICIENT_TEXT` 占位符
3. **Service 层重构**：抽取 `_run_analysis_core` 共享分析核心，新增 `checklist()` 独立检查清单用例
4. **数据层边界优化**：`data/__init__.py` 新增公共工厂入口，thermometer_service 引入 Protocol 解耦
5. **cache.py 原子写入**：parsed report JSON 使用 `NamedTemporaryFile` + `replace`
6. **CLI checklist 命令**：从 stub 升级为完整实现
7. **工程基线对齐**：pyproject.toml 构建后端从 hatchling 迁移到 setuptools，CI 新增 coverage gate

## Guardrail Validation

### G1: 无 fund_agent/host 或 fund_agent/agent 占位包

**PASS** — `gh pr diff 16 --name-only | grep -E '(fund_agent/host/|fund_agent/agent/)'` 零命中。所有 `fund_agent/host` / `fund_agent/agent` 引用仅出现在文档/审查产物中，无文件创建。

### G2: 无 dayu.host/dayu.engine import 或依赖

**PASS** — `gh pr diff 16 | grep '^+' | grep -E '(from dayu|import dayu)' | grep -v '\.md'` 零命中。Python 源码中无新增 dayu import。文档中 `dayu.host` / `dayu.engine` 仅作为声明性规则出现（"必须使用"、"当前不声明"）。

### G3: 当前确定性路径保持 UI -> Service -> fund_agent/fund

**PASS** — CLI 直接调用 `FundAnalysisService`，Service 直接调用 `fund_agent.fund.*` 模块，无 Host/Agent 中间层插入。新增的 `checklist()` 方法遵循相同路径。

### G4: 无显式业务参数隐藏在 extra_payload

**PASS** — `gh pr diff 16 | grep '^+' | grep 'extra_payload'` 所有命中均为禁止性声明或审查产物验证记录。生产代码中所有新增参数均为 typed dataclass 字段（`FundAnalysisRequest`、`FundChecklistResult`、`FundAnalysisDeveloperOverrides`）。

### G5: review_report.md 不在 PR diff 中

**PASS** — `gh pr diff 16 --name-only | grep 'review_report'` 零命中。

## Findings

未发现严重、高或中等问题。以下为低严重度观察性发现：

### F1-未修复-低-renderer 第0章硬编码状态值集合

- **入口/函数**: `_chapter_0_largest_risk_text`、`_first_stress_attention_scenario`、`_chapter_0_upgrade_threshold_text`
- **文件(行号)**: fund_agent/fund/template/renderer.py（新增函数）
- **输入场景**: 正常渲染路径
- **实际分支**: 全部分支正常工作
- **预期行为**: 状态值判断应与类型定义同步
- **实际行为**: `{"near_limit", "beyond_tolerance"}` 和 `{"needs_attention", "suggest_replace"}` 硬编码在渲染函数中，与 `StressCapacityStatus` / `FinalJudgment` Literal 类型分别维护
- **直接证据**: 新增代码中 `status in {"near_limit", "beyond_tolerance"}` 和 `judgment in {"needs_attention", "suggest_replace"}` 使用字符串字面量集合
- **影响**: 若后续新增状态值需同步更新此处，但当前 `StressCapacityStatus` 和 `FinalJudgment` 已是 `Literal` 类型约束，运行时不会出现非法值
- **建议改法和验证点**: 后续考虑将状态集合提取为模块级常量或使用排除法（`!= "worth_holding"`）；当前无需修改
- **修复风险（低）**: 无回归风险
- **严重程度（低）**

### F2-未修复-低-CLI report_year 默认值硬编码 2024

- **入口/函数**: `fund-analysis checklist` 和 `fund-analysis analyze` 命令
- **文件(行号)**: fund_agent/ui/cli.py
- **输入场景**: 用户未显式传入年份
- **实际分支**: 使用默认值 2024
- **预期行为**: 默认年份应反映合理分析年度
- **实际行为**: `report_year` 默认值硬编码为 2024，随时间推移会过时。`analyze` 和 `checklist` 两处一致
- **直接证据**: `report_year: int = typer.Option(2024, ...)`
- **影响**: 2025 年后用户可能意外分析旧年份数据
- **建议改法和验证点**: 后续考虑动态默认值（当前年 -1）或移除默认值要求用户显式指定；当前两命令一致，无回归
- **修复风险（低）**: 低
- **严重程度（低）**

### F3-未修复-低-CLI 导入边界测试冗余

- **入口/函数**: `test_cli_module_imports_service_but_not_agent_internals` 和 `test_ui_cli_imports_service_but_not_agent_internals`
- **文件(行号)**: tests/ui/test_cli.py、tests/config/test_paths.py
- **输入场景**: CI 执行
- **实际分支**: 两个测试都通过
- **预期行为**: 测试覆盖不冗余
- **实际行为**: test_paths.py 使用 AST 解析（精确），test_cli.py 使用字符串匹配（可能误判注释文本），功能重叠
- **直接证据**: 两个测试文件中存在目标相同的边界检查
- **影响**: 不影响正确性，仅增加维护成本
- **建议改法和验证点**: 后续统一为 AST 版本或合并到单一测试文件；当前不影响通过/失败判断
- **修复风险（低）**: 无
- **严重程度（低）**

## Open Questions

- 无

## Residual Risk

- **docs/reviews/ 审查产物文件**（~80 个 .md）仅抽样验证了关键词（dayu.host、extra_payload、fund_agent/host），未逐文件走读内容正确性。这些文件是历史审查记录而非生产代码，风险可控。
- **CI coverage gate 阈值**（50%）远低于实际覆盖率（92%），作为最低安全网合理，但不会阻止覆盖率回归到 50-92% 之间的情况。
- **checklist 命令默认 quality gate policy**：CLI 中 `checklist` 使用 `policy="off"`，与 `analyze` 的 `policy="block"` 不同。这是当前实现选择（独立检查清单不阻断于质量门控），但产品意图需确认。

## Review Conclusion

**PASS_WITH_FINDINGS**

五项架构边界护栏全部通过验证（G1-G5 PASS）。PR 正确完成了从旧六层到 Dayu 四层的术语迁移，未在生产代码中引入 Host/Agent 中间层、dayu 依赖或 extra_payload 参数走私。三个低严重度发现（F1-F3）均为后续优化建议，不影响当前功能正确性和架构合规性。

CI 检查通过（test pass, 20s）。测试新增 9 个用例，全部覆盖真实行为和关键边界条件。

**PR Gate 建议**: 可以合并。建议后续跟踪 F1（状态值集合常量化）、F2（年份默认值动态化）和 F3（测试冗余清理）作为低优先级技术债。
