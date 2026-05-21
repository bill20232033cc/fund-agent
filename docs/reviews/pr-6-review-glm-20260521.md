# PR #6 PR-level Code Review — P10 Repo Hygiene / Release Readiness

> **Reviewer**: AgentGLM
> **Date**: 2026-05-21
> **PR**: https://github.com/bill20232033cc/fund-agent/pull/6
> **Base**: `main` (d5d54ae) → **Head**: `p10-release-readiness` (eb43dc3)
> **Commits**: 28 commits, 84 files changed
> **Scope**: P10 repo hygiene / release readiness；确认不改变 fund-analysis analyze、quality gate、renderer、audit 或 Fund Capability 行为

---

## Verdict: **PASS**

PR #6 可 squash merge。P10 基础设施变更（LICENSE、CI、`.gitignore`、`config/paths`、README/tests 同步）实现正确，守卫测试充分。P8/P9 功能变更已通过独立 aggregate deepreview，与 P10 基础设施层无交叉回归。Head eb43dc3 新增 CLI dev override 错误稳定化修复，纯 UI 层，不影响分析行为。残余风险均为已知 owner，无阻断 finding。

---

## 1. P10 基础设施变更审查

### 1.1 MIT LICENSE（`LICENSE`，新增）

| 检查项 | 结果 |
|--------|------|
| 标准 MIT 全文 | ✅ 21 行标准文本 |
| Copyright holder | ✅ `bill20232033cc`，与 P10-S1 plan 用户确认一致 |
| Year | ✅ `2026` |
| `pyproject.toml` 声明 | ✅ `project.license = "MIT"` |
| `test_repo_hygiene.py` 守卫 | ✅ 同时检查 LICENSE 文件和 pyproject 声明 |

**Finding**: 无。

### 1.2 GitHub Actions CI（`.github/workflows/ci.yml`，新增）

| 检查项 | 结果 |
|--------|------|
| Trigger | ✅ push to main + pull_request |
| Python 版本 | ✅ 3.11，与 `pyproject.toml requires-python` 一致 |
| uv 安装 | ✅ `astral-sh/setup-uv@v5`，`enable-cache: true` |
| 依赖安装 | ✅ `uv sync --extra dev --frozen`（frozen 保证 CI 可复现） |
| Lint | ✅ `uv run ruff check .` |
| Test | ✅ `uv run pytest -q` |
| 守卫测试 | ✅ `test_repo_hygiene.py` 验证 CI 命令和 Python 版本 |

**INFO-1（LOW）**: CI 未运行 `ruff format --check .`。当前项目 `ruff check .` 足够覆盖 lint，format 检查可作为后续强化项加入。不阻断。

**INFO-2（LOW）**: CI 无 test coverage gate（如 `--cov=fund_agent --cov-fail-under=50`）。当前覆盖率远超 50%（测试手册记录 90%+），不阻断。

### 1.3 `.gitignore` Artifact Policy（`.gitignore`，修改）

| 检查项 | 结果 |
|--------|------|
| Python 标准忽略 | ✅ `.pytest_cache/`、`.ruff_cache/`、`.coverage`、`htmlcov/`、`dist/`、`build/`、`*.egg-info/` |
| 生成物忽略 | ✅ `cache/`、`report-*.md`、`reports/extraction-snapshots/`、`reports/quality-gate-runs/` |
| Golden answers 保留 | ✅ 注释说明 `reports/golden-answers/` 有意 tracked；`reports/` 整体不在忽略列表 |
| `.docx` 本地忽略 | ✅ `docs/*.docx`，与 P10-S1 plan 一致 |
| 本地 helper 忽略 | ✅ `launchd/`、`scripts/aliases.zsh` 等保持原样 |
| 守卫测试 | ✅ `test_repo_hygiene.py` 验证 `reports/` 和 `reports/golden-answers/` 不在忽略列表 |

**Finding**: 无。

### 1.4 `fund_agent.config.paths` 默认路径迁移（`fund_agent/config/paths.py`，新增）

| 检查项 | 结果 |
|--------|------|
| 模块职责 | ✅ 纯静态路径常量，无 env/config/runtime 依赖 |
| 路径格式 | ✅ 全部相对路径（`Path("docs/...")`、`Path("cache/...")`、`Path("reports/...")`） |
| `Final` 注解 | ✅ 所有常量均标注 `Final[Path]` |
| 完整覆盖 | ✅ 12 个默认路径覆盖所有散落调用点 |
| 导入隔离 | ✅ 模块不反向导入 UI/Service（`test_paths_import_isolated` 验证） |

**迁移调用点验证**（全部指向 `config.paths` 同一值）：

| 调用点 | 原硬编码 | 迁移后 |
|--------|----------|--------|
| `nav_data.NAV_CACHE_ROOT` | `Path("cache/nav")` | `DEFAULT_NAV_CACHE_ROOT` ✅ |
| `thermometer.THERMOMETER_CACHE_ROOT` | `Path("cache/thermometer")` | `DEFAULT_THERMOMETER_CACHE_ROOT` ✅ |
| `documents.cache.DOCUMENT_CACHE_ROOT` | `Path("cache/documents")` | `DEFAULT_DOCUMENT_CACHE_ROOT` ✅ |
| `pdf.downloader.DEFAULT_CACHE_DIR` | `Path("cache/pdf")` | `DEFAULT_PDF_CACHE_ROOT` ✅ |
| `extraction_snapshot.DEFAULT_*` | `Path("docs/...")`/`Path("reports/...")` | 对应 config 常量 ✅ |
| `golden_prefill.DEFAULT_*` | `Path("docs/...")`/`Path("reports/...")` | 对应 config 常量 ✅ |
| `golden_answer.DEFAULT_*` | `Path("reports/...")` | 对应 config 常量 ✅ |
| `quality_gate_integration.DEFAULT_*` | `Path("reports/...")` | 对应 config 常量 ✅ |
| `cli.DEFAULT_*` | 多个 `Path(...)` | 对应 config 常量 ✅ |
| `fund_analysis_service.DEFAULT_*` | `Path("reports/...")` | 对应 config 常量 ✅ |

**守卫测试**（`tests/config/test_paths.py`，273 行）：

| 测试 | 覆盖 |
|------|------|
| `test_config_paths_are_relative_and_match_documented_defaults` | 12 个默认值与文档一致 + 全部相对路径 |
| `test_paths_module_import_is_isolated_from_ui_and_service` | 路径模块不引入运行时装配依赖 |
| `test_existing_path_aliases_point_to_config_defaults` | 16 个别名断言覆盖所有迁移调用点 |
| `test_historical_quality_gate_score_stays_cli_local` | P4 历史 fixture 路径未误提升为全局默认 |
| `test_config_init_does_not_reexport_path_constants` | `config/__init__` 不是路径重导出面 |
| `test_no_independent_repository_path_defaults_outside_config_paths` | AST 扫描防止新增散落路径 |
| `test_extraction_score_has_no_module_level_repository_path_default` | extraction_score 无散落路径 |

**Finding**: 无。

### 1.5 README / tests 同步

| 文件 | 变更性质 | 结果 |
|------|----------|------|
| `README.md` | 从旧 `zhixing` 项目说明重写为当前用户手册 | ✅ 与 CLI 成功路径对齐 |
| `CLAUDE.md` | 从 191 行独立指南精简为 15 行 AGENTS.md 入口适配层 | ✅ 与 AGENTS.md 规则真源声明一致 |
| `AGENTS.md` | 新增规则真源声明和模板路径修正 | ✅ `docs/fund-analysis-template-draft.md` 路径已更正 |
| `fund_agent/README.md` | 开发手册总览同步 | ✅ |
| `fund_agent/config/README.md` | 配置说明同步 | ✅ |
| `fund_agent/fund/README.md` | Fund 包说明同步 | ✅ |
| `tests/README.md` | 测试手册同步 | ✅ 新增路径守卫和 repo hygiene 测试说明 |

**Finding**: 无。

---

## 2. P8/P9 功能变更确认

PR 包含 P8（must_answer audit routing、preferred_lens application、source fallback）和 P9（产品契约加固、quality gate calibration）的功能变更。以下确认这些变更不与 P10 基础设施层产生交叉回归。

### 2.1 `final_judgment.py`（P9-S1，新增 282 行）

- 归属：Fund Capability 层 ✅
- 职责：最终判断派生策略，消费检查清单、否决项、压力测试和质量 gate 结果
- 边界：不读取 PDF/cache/UI/Service ✅
- 派生优先级：否决项 > 红灯 > 压力测试 > quality gate block > quality gate not_run > watch/黄/灰 > 值得持有 > fail-safe ✅
- Developer override：通过 `FinalJudgmentDecision.source` 区分，冲突记录 `conflict_reasons` 供 R2 审计 ✅

### 2.2 R2 审计增强（P9-S1）

- `ProgrammaticAuditInput` 新增 `derived_final_judgment` 和 `final_judgment_source` 字段 ✅
- `_audit_final_judgment` 从 early-return 改为累积收集所有 R2 issues ✅（审计覆盖改进，无回归风险）
- 新增 source 冲突审计：derived 路径下 selected != derived 报错；developer_override 路径下冲突仅记录 ✅

### 2.3 Renderer 契约变更（P9-S1）

- `TemplateRenderInput.final_judgment: TemplateFinalJudgment` → `final_judgment_decision: FinalJudgmentDecision` ✅
- 渲染器只消费 `selected_judgment`（用于报告显示）和 `source`（用于来源说明）✅
- `ProgrammaticAuditInput` 构造从 renderer 自动组装，传入 selected/derived/source ✅

### 2.4 Quality Gate / Golden Coverage（P9-S2）

- `CorrectnessSummary` 新增 `coverage_scope`/`coverage_reason`/`covered_fund_codes`/`missing_fund_codes`/`coverage_required` ✅
- 精选池成员缺 strict golden 覆盖以 `FQ0/info` 暴露，不等同 gate not_run ✅
- Unknown unavailable coverage metadata fail closed ✅

### 2.5 CHAPTER_CONTRACT 第 5/6 章边界强化（P8-S2 + P10-S1 plan alignment）

- 第 5 章 `must_not_cover` 新增"不给最终持有/替换结论"和"不展开风险清单" ✅
- 第 6 章 `must_not_cover` 新增"不复述当前阶段事实"和"不给最终持有/替换结论" ✅
- 与 `docs/design.md` 第 3.1 节第 5/6 章边界裁决一致 ✅

### 2.6 Template `__init__.py` 清理

- 移除 `TemplateFinalJudgment` 重导出 ✅（类型真源收口到 `final_judgment.py`）

---

## 3. 行为不变性确认

以下确认 P10 基础设施变更不改变 fund-analysis 核心行为：

| 行为 | 确认方式 | 结果 |
|------|----------|------|
| `fund-analysis analyze` CLI 入口 | CLI diff 只新增 `--dev-override` 参数组和路径常量迁移，product mode 最小输入不变 | ✅ 无回归 |
| Quality gate 规则 | `quality_gate.py` 变更仅限 P9-S2 coverage metadata 扩展，FQ0-FQ6 规则逻辑不变 | ✅ 无回归 |
| Renderer 8 章输出 | 渲染器变更仅限 `final_judgment` → `FinalJudgmentDecision` 适配，章节结构不变 | ✅ 无回归 |
| 程序审计规则 | P1/P2/P3/L1/R1 规则逻辑不变；R2 增强（累积收集 + source 审计）为正向扩展 | ✅ 无回归 |
| Fund Capability 分析 | P1 extractors、P2 analysis（R=A+B-C/alpha judge/consistency/investor return/risk/stress/checklist）无代码变更 | ✅ 无回归 |
| 路径默认值 | 所有迁移前后值完全相同（`Path("cache/...")` → `DEFAULT_*_ROOT`） | ✅ 值等价 |

---

## 3a. Targeted Re-review：eb43dc3 `fix: stabilize dev override CLI errors`

**变更范围**：`fund_agent/ui/cli.py` +21/-17（1 文件）

**变更内容**：`analyze` 命令中 `_build_developer_overrides(...)` 调用被 `try/except typer.BadParameter` 包裹；捕获后 `typer.echo(str(exc), err=True)` 输出到 stderr，`raise typer.Exit(code=2)` 退出。

| 检查项 | 结果 |
|--------|------|
| 影响范围 | ✅ 仅 CLI UI 层，不触及 Service/Capability/分析/审计/渲染 |
| 退出码语义 | ✅ code 2 与现有 quality gate block 退出码一致 |
| 错误输出稳定性 | ✅ `str(exc)` 来自 `typer.BadParameter`，文本由 Typer 参数验证决定，非未捕获异常堆栈 |
| `from exc` 链 | ✅ 保留原始异常 cause，便于调试 |
| 行为不变性 | ✅ product mode（无 `--dev-override`）不经过此路径；dev override 参数合法时无异常抛出 |
| CI 验证 | ✅ GitHub Actions run 26234941272 pass；本地 full suite 388 passed、ruff passed |

**Finding**: 无。纯防御性修复，稳定 CLI 测试输出。

---

## 4. Findings 汇总

| ID | Severity | 文件 | 说明 | 裁决 |
|----|----------|------|------|------|
| F-1 | INFO | `.github/workflows/ci.yml` | CI 未运行 `ruff format --check .`，仅 lint 无 format 校验 | 后续强化项，不阻断 |
| F-2 | INFO | `.github/workflows/ci.yml` | CI 无 test coverage gate | 当前覆盖率远超阈值，不阻断 |
| F-3 | INFO | `fund_agent/fund/analysis/final_judgment.py:151-156` | R2 developer_override 冲突审计只记录不阻断 override 本身；这是 P9-S1 设计决策 | 已通过 P9 aggregate deepreview，非 P10 finding |

---

## 5. 验证

| 检查 | 状态 |
|------|------|
| P10-S1 implementation 验证 | ✅ full suite 388 passed、ruff passed、diff check passed、`uv lock --check` passed |
| P10 aggregate deepreview | ✅ MiMo PASS + GLM PASS，无阻断 finding |
| P10 acceptance / ready-to-open-draft-PR reconciliation | ✅ inclusion/exclusion set 已明确 |
| eb43dc3 CLI fix 验证 | ✅ 本地 full suite 388 passed、ruff passed；GitHub Actions run 26234941272 pass |
| `git diff --check origin/main...HEAD` | 需在 merge 前确认 |

---

## 6. 残余风险

| 风险 | Owner | 说明 |
|------|-------|------|
| `docs/repo-audit-20260521.md` 排除 | P10 exclusion | 有意排除，非 PR 范围 |
| `fund_agent/fund/tools/` 空目录 | 后续 slice | 已在 P10 aggregate reconciliation 中裁决 |
| RR-13 `016492` CSV 重复 | Human-owned | P5-S6 已记录，不阻断 |
| Control doc 可读性 | 后续文档治理 slice | 不影响代码正确性 |

---

## 7. 结论

**Verdict: PASS**

P10 repo hygiene / release readiness 实现完整正确：MIT LICENSE 与 pyproject 声明一致；CI 工作流覆盖 lint + test；`.gitignore` 策略窄口径且不误忽略 fixtures；`config/paths` 集中管理全部默认路径，守卫测试通过 AST 扫描防止散落路径回退；README/tests 文档同步到位。Head eb43dc3 新增 CLI dev override `BadParameter` 稳定化捕获，纯 UI 层防御性修复。P8/P9 功能变更已通过独立 aggregate deepreview，与 P10 基础设施无交叉回归。PR 可 squash merge。
