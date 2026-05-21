# P10-S1 Code Review (AgentGLM)

- **Date**: 2026-05-21
- **Reviewer**: AgentGLM
- **Gate**: P10-S1 implementation → code review
- **Plan**: `docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`
- **Implementation**: `docs/reviews/p10-s1-implementation-20260521.md`
- **Diff scope**: 18 modified files, 11 untracked files (incl. new `fund_agent/config/paths.py`, `.github/workflows/ci.yml`, `LICENSE`, test files, review artifacts)

## Verdict: PASS

P10-S1 implementation 完整执行了 plan 的四个 slice（P10-S1-A 至 P10-S1-D），未引入任何阻断级 finding。所有变更限定在仓库发布卫生范围内，未改变 `fund-analysis analyze` 产品行为、quality gate 语义、renderer/audit/fund capability 行为。388 测试全部通过，ruff lint 通过。

---

## Findings

### INFO-1: `golden-build` 默认输入路径变更是有意的产品行为调整

- **Severity**: INFO（非阻断）
- **File/Line**: `fund_agent/ui/cli.py:456`，`fund_agent/fund/golden_answer.py:18-19`
- **Evidence**: `golden-build` 的 `--input-path` 默认值从 `golden-answer-prefill.md` 变为 `golden-answer-prefill-reviewed.md`。这是 plan slice P10-S1-D 的明确目标。
- **Assessment**: Plan 的 non-goal 是"不改变 `fund-analysis analyze` 产品行为"，而 `golden-build` 是独立子命令。该变更使默认路径与预期工作流一致（先 prefill → 人工 review → golden-build 读取 reviewed 版本），语义正确。测试覆盖存在：`tests/ui/test_cli.py:test_golden_build_cli_defaults_to_reviewed_markdown`。

### INFO-2: 散落路径 AST 扫描守卫依赖 `Path(...)` 构造模式

- **Severity**: INFO（非阻断）
- **File/Line**: `tests/config/test_paths.py:254-273`（`_is_repository_path_call`）
- **Evidence**: 守卫测试通过 AST 匹配 `Path("docs/...")` / `Path("reports/...")` / `Path("cache/...")` 模式来检测散落默认路径。如果未来代码使用 `pathlib.PurePosixPath`、字符串拼接或其他构造方式，该守卫不会捕获。
- **Assessment**: 当前代码库统一使用 `Path("...")` 构造，守卫有效。风险可接受，但应在 tests/README 维护约定中注明该假设。当前 `tests/README.md` 的维护约定已包含"不要在 UI、Service 或 Fund Capability 模块里新增散落的 `Path(...)` 默认值"，覆盖了核心意图。

### INFO-3: `config/__init__.py` 保持空文件

- **Severity**: INFO（非阻断）
- **File/Line**: `fund_agent/config/__init__.py`
- **Evidence**: 该文件为空（0 有效行），不重导出任何路径常量。
- **Assessment**: Plan 明确要求 `config/__init__.py` 不做路径重导出。`test_config_init_does_not_reexport_path_constants` 验证了这一约束。正确。

---

## Review Focus Checklist

### 1. 未改变 `fund-analysis analyze` 产品行为

| 检查项 | 结果 |
|--------|------|
| `analyze` 命令参数默认值 | 无变化。CLI `analyze` 入口参数未修改 |
| Service 层 analyze 编排 | 无变化。`fund_analysis_service.py` 仅将 `DEFAULT_GOLDEN_ANSWER_PATH` 从内联 `Path("reports/golden-answers/golden-answer.json")` 改为引用 `DEFAULT_GOLDEN_ANSWER_JSON`，值相同 |
| Fund Capability 分析逻辑 | 无变化。extraction_snapshot / golden_prefill / golden_answer / quality_gate 仅将内联路径常量改为从 `config.paths` 引用，值相同 |
| Renderer / audit / fund capability 行为 | 无变化。未触及 renderer、审计规则、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE |

### 2. `config.paths` 只是静态路径常量

| 检查项 | 结果 |
|--------|------|
| 模块内容 | `fund_agent/config/paths.py` 仅包含 `Final[Path]` 常量赋值，共 12 个路径 |
| 无环境变量读取 | 确认。无 `os.environ`、`os.getenv` |
| 无 workspace 配置 | 确认。无配置文件读取 |
| 无 prompt manifest | 确认。无 manifest 加载 |
| 无 Dayu/Host/Engine runtime | 确认。无任何运行时依赖 |
| docstring 声明 | 明确声明"不读取环境变量、workspace 配置、prompt manifest 或运行时配置" |
| 测试守卫 | `test_config_paths_are_relative_and_match_documented_defaults` 验证全部值；`test_paths_module_import_is_isolated_from_ui_and_service` 验证导入隔离 |

### 3. 旧默认路径 alias 完整保留

| 模块 | 旧常量 | 是否保留 | 测试覆盖 |
|------|--------|----------|----------|
| `ui/cli.py` | `DEFAULT_SELECTED_FUNDS_CSV` | ✅ 指向 `paths.DEFAULT_SELECTED_FUNDS_CSV` | ✅ |
| `ui/cli.py` | `DEFAULT_GOLDEN_TEMPLATE` | ✅ 指向 `paths.DEFAULT_GOLDEN_TEMPLATE_PATH` | ✅ |
| `ui/cli.py` | `DEFAULT_GOLDEN_PREFILL_OUTPUT` | ✅ 指向 `paths.DEFAULT_GOLDEN_PREFILL_OUTPUT` | ✅ |
| `ui/cli.py` | `DEFAULT_GOLDEN_ANSWER_OUTPUT` | ✅ 指向 `paths.DEFAULT_GOLDEN_ANSWER_JSON` | ✅ |
| `services/fund_analysis_service.py` | `DEFAULT_GOLDEN_ANSWER_PATH` | ✅ 指向 `paths.DEFAULT_GOLDEN_ANSWER_JSON` | ✅ |
| `fund/extraction_snapshot.py` | `DEFAULT_SELECTED_FUNDS_CSV` | ✅ 指向 `paths.DEFAULT_SELECTED_FUNDS_CSV` | ✅ |
| `fund/extraction_snapshot.py` | `DEFAULT_SNAPSHOT_OUTPUT_ROOT` | ✅ 指向 `paths.DEFAULT_EXTRACTION_SNAPSHOT_ROOT` | ✅ |
| `fund/golden_prefill.py` | `DEFAULT_GOLDEN_TEMPLATE_PATH` | ✅ 指向 `paths.DEFAULT_GOLDEN_TEMPLATE_PATH` | ✅ |
| `fund/golden_prefill.py` | `DEFAULT_GOLDEN_PREFILL_OUTPUT` | ✅ 指向 `paths.DEFAULT_GOLDEN_PREFILL_OUTPUT` | ✅ |
| `fund/golden_answer.py` | `DEFAULT_GOLDEN_REVIEWED_MARKDOWN` | ✅ 指向 `paths.DEFAULT_GOLDEN_REVIEWED_MARKDOWN` | ✅ |
| `fund/golden_answer.py` | `DEFAULT_GOLDEN_ANSWER_JSON` | ✅ 指向 `paths.DEFAULT_GOLDEN_ANSWER_JSON` | ✅ |
| `fund/quality_gate_integration.py` | `DEFAULT_QUALITY_GATE_OUTPUT_ROOT` | ✅ 指向 `paths.DEFAULT_QUALITY_GATE_OUTPUT_ROOT` | ✅ |
| `fund/documents/cache.py` | `DOCUMENT_CACHE_ROOT` | ✅ 指向 `paths.DEFAULT_DOCUMENT_CACHE_ROOT` | ✅ |
| `fund/pdf/downloader.py` | `DEFAULT_CACHE_DIR` | ✅ 指向 `paths.DEFAULT_PDF_CACHE_ROOT` | ✅ |
| `fund/data/nav_data.py` | `NAV_CACHE_ROOT` | ✅ 指向 `paths.DEFAULT_NAV_CACHE_ROOT` | ✅ |
| `fund/data/thermometer.py` | `THERMOMETER_CACHE_ROOT` | ✅ 指向 `paths.DEFAULT_THERMOMETER_CACHE_ROOT` | ✅ |

全部 16 个旧常量 alias 保留完整，由 `test_existing_path_aliases_point_to_config_defaults` 统一覆盖。

### 4. CLI historical `DEFAULT_QUALITY_GATE_SCORE` 保持 CLI-local

- **File**: `fund_agent/ui/cli.py:48-49`
- `DEFAULT_QUALITY_GATE_SCORE` 仍为 CLI 模块内联定义，未进入 `config.paths`。
- `test_historical_quality_gate_score_stays_cli_local` 验证 `paths` 模块无此属性。
- 注释明确标注"独立 quality-gate helper 的历史 P4 score fixture 路径，不是仓库级默认输出根"。
- ✅ 正确。

### 5. `.gitignore` 窄口径

| 检查项 | 结果 |
|--------|------|
| `reports/golden-answers/` 未被忽略 | ✅ 显式注释说明"intentionally tracked" |
| `reports/` 未被整体忽略 | ✅ `test_gitignore_keeps_generated_outputs_local_without_hiding_fixtures` 验证 |
| 新增条目合理 | `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`, `dist/`, `build/`, `*.egg-info/`, `docs/*.docx` 均为标准本地产物 |
| 保留既有条目 | `cache/`, `report-*.md`, `reports/extraction-snapshots/`, `reports/quality-gate-runs/` 保持不变 |
- ✅ 窄口径，未误忽略 curated fixture。

### 6. CI 符合 plan

- **File**: `.github/workflows/ci.yml`
- Python 3.11 ✅
- `uv sync --extra dev --frozen` ✅
- `uv run ruff check .` ✅
- `uv run pytest -q` ✅
- Triggers: `push` to `main` + `pull_request` ✅
- `actions/checkout@v4` + `setup-python@v5` + `setup-uv@v5` ✅
- `enable-cache: true` for uv ✅
- `test_ci_workflow_runs_release_readiness_checks` 验证 ✅
- 与 plan slice P10-S1-A 完全一致。

### 7. Docs 未设计未来

| 文档 | 更新内容 | 是否越界 |
|------|----------|----------|
| `README.md` | 新增 CI 命令、仓库产物策略段落 | ✅ 描述当前状态 |
| `fund_agent/README.md` | config 包描述更新、paths.py 边界说明 | ✅ 描述当前职责 |
| `fund_agent/config/README.md` | 重写为当前路径策略说明，明确列出"不提供"清单 | ✅ 描述当前状态，未设计未来 |
| `tests/README.md` | 新增 CI 命令、路径迁移守卫测试条目、维护约定 | ✅ 同步当前测试结构 |

所有文档更新均描述"当前怎么用/怎么工作"，无"未来会怎样"口径。

### 8. `golden-build` 默认 reviewed markdown 变更

- **变更**: `--input-path` 默认值从 `golden-answer-prefill.md` → `golden-answer-prefill-reviewed.md`
- **合理性**: golden-build 命令的语义是"将人工审核后的 Markdown 转为 strict JSON"，默认读取 reviewed 版本符合命令意图。原始 prefill 输出仍作为 `golden-prefill` 的默认输出路径保留。
- **测试覆盖**: `test_golden_build_cli_defaults_to_reviewed_markdown` 验证默认路径为 `golden-answer-prefill-reviewed.md`。
- ✅ 合理且有测试覆盖。

### 9. Durable artifact `code-review-p8-s3-ds-20260521.md` inclusion

- 文件存在于 `docs/reviews/`，为未跟踪状态，将随 P10-S1 commit 纳入。
- Plan slice P10-S1-C 明确要求保留此文件作为 durable review artifact。
- ✅ 合理。

---

## Open Questions

无。

---

## Verification Notes

| 验证项 | 命令 | 结果 |
|--------|------|------|
| 全量测试 | `uv run pytest -q` | 388 passed |
| P10-S1 定向测试 | `uv run pytest tests/test_repo_hygiene.py tests/config/test_paths.py tests/ui/test_cli.py -q` | 29 passed |
| Lint | `uv run ruff check .` | All checks passed |
| Lock 文件 | `uv lock --check` | 无变化（implementation report 已验证） |
| git check-ignore | `git check-ignore "docs/fund-agent_仓库级综合审核报告_2026-05-21.docx"` | 正确被忽略（implementation report 已验证） |
| git diff --check | 无 trailing whitespace | 通过（implementation report 已验证） |

---

## Residual Risk

| 风险 | 级别 | 说明 |
|------|------|------|
| AST 扫描不覆盖非 `Path(...)` 构造 | 极低 | 当前代码库统一使用 `Path("...")`；如有需要可后续增强 `_is_repository_path_call` |
| `extraction_score.py` 无路径默认值需迁移 | 无 | 已由 `test_extraction_score_has_no_module_level_repository_path_default` 守卫 |
| CI 仅为单 Python 版本 | 极低 | Plan 明确为 Python 3.11 单版本；多版本支持非 P10 范围 |
