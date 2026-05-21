# P10-S1 Plan Review — MiMo

- **Reviewed target**: `docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`
- **Scope**: P10-S1 repo hygiene / release readiness plan — LICENSE, CI, artifact policy, static path defaults, untracked file handling, docs/tests
- **Review date**: 2026-05-21
- **Reviewer**: AgentMiMo (plan review)
- **Inputs consulted**: `docs/design.md`, `docs/implementation-control.md`, `docs/reviews/post-p9-follow-up-planning-20260521.md`, current codebase facts

## Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|---------|
| A1 | No LICENSE file exists | ✅ confirmed — `ls LICENSE*` returns nothing |
| A2 | No `.github/workflows` directory exists | ✅ confirmed |
| A3 | `pyproject.toml` requires Python >=3.11 with ruff/pytest dev deps | ✅ confirmed |
| A4 | Default paths are scattered across UI/Service/Fund modules | ✅ confirmed — 10+ files define their own path constants |
| A5 | `.gitignore` already covers runtime outputs | ✅ confirmed — covers `cache/`, `reports/extraction-snapshots/`, `reports/quality-gate-runs/`, `report-*.md` |
| A6 | `fund_agent/config/` exists with `__init__.py` and `prompts/` subdirectory | ✅ confirmed — `config/prompts/{base,scenes,tasks}` subdirs exist (empty or skeleton) |
| A7 | `tests/config/` directory does not yet exist | ✅ confirmed |
| A8 | Plan's test validation paths are valid | ✅ confirmed — `tests/ui/test_cli.py`, `tests/services/test_fund_analysis_service.py`, `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_extraction_score.py`, `tests/fund/test_quality_gate_integration.py` all exist |

## Findings

### 001-未修复-中-import migration alias strategy underspecified

- **位置**: Section 4.4 "Import migration rules"
- **问题类型**: 不可直接实施
- **当前写法**: "Existing module-level constant names may remain as aliases to avoid noisy call-site churn."
- **反例/失败场景**: Implementation agent 必须决定：(1) 旧模块是否从 `config/paths` re-export，(2) 旧常量名与新名不一致时如何映射（如 `DEFAULT_SNAPSHOT_OUTPUT_ROOT` vs `DEFAULT_EXTRACTION_SNAPSHOT_ROOT`，`DEFAULT_CACHE_DIR` vs `DEFAULT_PDF_CACHE_ROOT`，`DOCUMENT_CACHE_ROOT` vs `DEFAULT_DOCUMENT_CACHE_ROOT`）。没有明确映射表，agent 可能创建重复定义、错误 alias 或遗漏迁移。
- **为什么有问题**: 当前代码中至少存在以下命名不一致：
  - `extraction_snapshot.py:23` 定义 `DEFAULT_SNAPSHOT_OUTPUT_ROOT`，plan 定义 `DEFAULT_EXTRACTION_SNAPSHOT_ROOT`
  - `pdf/downloader.py:20` 定义 `DEFAULT_CACHE_DIR`，plan 定义 `DEFAULT_PDF_CACHE_ROOT`
  - `documents/cache.py:19` 定义 `DOCUMENT_CACHE_ROOT`，plan 定义 `DEFAULT_DOCUMENT_CACHE_ROOT`
  - `quality_gate_integration.py:25` 定义 `DEFAULT_QUALITY_GATE_OUTPUT_ROOT`，plan 定义 `DEFAULT_QUALITY_GATE_OUTPUT_ROOT`（这个一致）
  - `fund_analysis_service.py:47` 定义 `DEFAULT_GOLDEN_ANSWER_PATH`，plan 定义 `DEFAULT_GOLDEN_ANSWER_JSON`
- **直接证据**: grep 结果显示 10+ 个现有常量定义分布在 `extraction_snapshot.py`、`extraction_score.py`、`fund_analysis_service.py`、`cli.py`、`documents/cache.py`、`pdf/downloader.py`、`data/nav_data.py`、`data/thermometer.py`、`quality_gate_integration.py`、`golden_prefill.py`、`golden_answer.py`
- **影响**: Implementation agent 可能创建不一致的 alias、遗漏某些 call-site 或引入命名冲突
- **建议改法和验证点**: 在 plan 中增加显式常量映射表，标注每个旧常量名 → 新常量名 → alias 策略（re-export from old module / rename at call-site / keep as local alias）
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 002-未修复-低-gitignore golden-answers comment premise不成立

- **位置**: Section 4.3 `.gitignore update requirements`
- **问题类型**: 最佳实践偏离
- **当前写法**: "Add a short comment that `reports/golden-answers/` is intentionally not ignored because curated golden answer fixtures are tracked."
- **反例/失败场景**: 当前 `.gitignore` 没有 `reports/` 通配 ignore 规则。已有规则是 `reports/extraction-snapshots/` 和 `reports/quality-gate-runs/`。对 `reports/golden-answers/` 添加"不被 ignore"的注释暗示它在被 ignore 的范围内需要豁免，但实际上它从未被 ignore。注释会误导后续维护者以为存在一个不存在的 ignore 规则。
- **为什么有问题**: 注释的前提（`reports/golden-answers/` 需要从 ignore 中豁免）与 `.gitignore` 实际状态不符
- **直接证据**: 当前 `.gitignore` 内容只包含 `reports/extraction-snapshots/` 和 `reports/quality-gate-runs/`，没有 `reports/` 通配
- **影响**: 低 — 注释不会改变行为，但会误导维护者
- **建议改法和验证点**: 改为在 `reports/extraction-snapshots/` 和 `reports/quality-gate-runs/` 条目旁添加注释说明这些是 generated output，而 `reports/golden-answers/` 是 curated fixture 目录，当前不在 ignore 范围
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 003-未修复-中-config/prompts existing content未处理

- **位置**: Section 4.4, Section 5 File Ownership
- **问题类型**: 范围漂移 / 遗漏
- **当前写法**: Plan 引入 `fund_agent/config/paths.py`，但未提及 `fund_agent/config/prompts/{base,scenes,tasks}` 子目录的现有内容
- **反例/失败场景**: `config/prompts/` 下存在 `base`、`scenes`、`tasks` 子目录（可能是空 skeleton 或未跟踪 prompt 文件）。Plan 的 Section 4.4 声明 `paths.py` "must not import from UI, Service, Fund Capability, Engine, or Runtime"，但未说明 `config/` 包的现有 prompt skeleton 内容是否应保留、清理或文档化。Implementation agent 可能忽略这些目录或意外修改它们。
- **为什么有问题**: `config/README.md` 当前声明"当前主链路没有运行时 prompt manifest"，但 `config/prompts/` 目录结构暗示曾有或计划有 prompt 配置。Plan 应明确这些目录的状态。
- **直接证据**: `ls fund_agent/config/prompts/` 返回 `base scenes tasks`
- **影响**: 低 — 不会破坏功能，但可能让 implementation agent 对 `config/` 包的职责边界产生困惑
- **建议改法和验证点**: 在 plan 的 Section 4.4 或 Non-Goals 中明确 `config/prompts/` 目录保持现状（保留或清理），不纳入 P10-S1 scope
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 004-未修复-低-cli hardcoded score path未覆盖

- **位置**: Section 4.4 Default Path Policy, Section 5 File Ownership
- **问题类型**: 遗漏
- **当前写法**: Plan 列出 `fund_agent/ui/cli.py` 作为消费模块，定义了 `DEFAULT_EXTRACTION_SNAPSHOT_ROOT` 和 `DEFAULT_QUALITY_GATE_OUTPUT_ROOT`
- **反例/失败场景**: `cli.py:46` 定义 `DEFAULT_QUALITY_GATE_SCORE = Path("reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json")`，这是一个硬编码的特定 run 路径，不在 plan 的静态路径常量范围内。Plan 的迁移可能遗漏此常量，或 implementation agent 可能尝试将其纳入 `config/paths.py`（不应纳入，因为它是特定 run 的固定路径，不是默认路径）。
- **为什么有问题**: 该路径是开发/测试阶段的特定产物路径，不是通用默认路径。Plan 应明确将其排除。
- **直接证据**: `cli.py:46` 硬编码 `reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json`
- **影响**: 低 — 不会破坏功能，但 implementation agent 可能困惑是否应迁移
- **建议改法和验证点**: 在 plan 中明确标注 CLI 中的特定 run 路径（如 `DEFAULT_QUALITY_GATE_SCORE`）不属于静态默认路径，不纳入 `config/paths.py`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 005-未修复-中-import migration测试覆盖缺口

- **位置**: Section 6 Slice P10-S1-B "Expected assertions"
- **问题类型**: 测试缺口
- **当前写法**: Plan 列出 12 个消费模块，但 validation 只运行 5 个测试文件
- **反例/失败场景**: 以下消费模块没有对应的现有测试来验证迁移后路径值不变：
  - `fund_agent/fund/golden_prefill.py` — 无 `tests/fund/test_golden_prefill.py`
  - `fund_agent/fund/golden_answer.py` — 无 `tests/fund/test_golden_answer.py`
  - `fund_agent/fund/documents/cache.py` — 测试存在但未在 validation 命令中
  - `fund_agent/fund/pdf/downloader.py` — 测试存在但未在 validation 命令中
  - `fund_agent/fund/documents/sources.py` — 无直接测试
  - `fund_agent/fund/data/nav_data.py` — 测试存在但未在 validation 命令中
  - `fund_agent/fund/data/thermometer.py` — 测试存在但未在 validation 命令中
- **为什么有问题**: 这些模块的路径常量迁移后，如果没有测试覆盖，implementation agent 可能引入静默的路径值变更
- **直接证据**: plan Section 4.4 列出 12 个消费模块，Section 6 Slice P10-S1-B validation 只运行 5 个测试文件
- **影响**: 中 — 部分模块的路径迁移缺乏回归保护
- **建议改法和验证点**: 在 Slice P10-S1-B validation 中增加 `uv run pytest tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py tests/fund/documents/ tests/fund/pdf/ tests/fund/data/ -q`，或在 `tests/config/test_paths.py` 中断言所有 12 个模块的导入路径常量值与 config/paths 一致
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 006-未修复-低-pyproject.toml license field未提及

- **位置**: Section 4.1 LICENSE
- **问题类型**: 最佳实践偏离
- **当前写法**: Plan 只添加 `LICENSE` 文件，声明"Do not change package metadata beyond documentation unless a reviewer explicitly requires it"
- **反例/失败场景**: `pyproject.toml` 的 `[project]` 表没有 `license` 字段。Python packaging best practice 建议在 `pyproject.toml` 中声明 `license = {text = "MIT"}` 或 `license = "MIT"`。Plan 明确排除此变更，但未说明原因。
- **为什么有问题**: PyPI 或 pip 工具链在分发时会读取 `pyproject.toml` 的 license 字段。缺少该字段可能导致 `pip show` 不显示 license 信息。
- **直接证据**: `pyproject.toml` 的 `[project]` 段无 `license` 字段
- **影响**: 低 — 不影响功能，不影响 CI，但影响 packaging metadata 完整性
- **建议改法和验证点**: 在 plan 中明确说明 P10-S1 不添加 `pyproject.toml` license 字段的原因（如"当前不发布到 PyPI"），或将其作为可选增强纳入
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

1. **Constants re-export location**: 当旧模块的常量变为 alias 后，alias 应从旧模块 re-export（如 `extraction_snapshot.py` 中 `DEFAULT_SELECTED_FUNDS_CSV` 从 `config.paths` import 后 re-export），还是旧模块保留独立定义？这影响已有 import 语句是否需要修改。
2. **`config/prompts/` 目录处置**: 是否在 P10-S1 中清理或文档化这些目录？还是保持现状？

## Residual Risks

| Risk | Suggested tracking |
|------|-------------------|
| Import migration 可能引入静默路径值变更，部分模块缺测试回归 | P10-S1 implementation code review |
| `pyproject.toml` license 字段缺失 | 后续 packaging slice |
| `config/prompts/` 目录状态不明 | 后续 config governance slice |

## Plan Review Conclusion

**pass-with-risks**

Plan 整体结构清晰、scope 合理、non-goals 明确，CI/artifact policy/untracked file handling 设计正确。主要风险在 import migration 细节：常量命名映射表缺失、部分模块测试覆盖不足。这些风险不阻塞 implementation，但应在 implementation agent 执行前或 code review 时收紧。建议 controller 在接受 plan 前补充 Finding 001 的常量映射表，其余 findings 可在 implementation 或 code review 阶段处理。

Output: `docs/reviews/p10-s1-plan-review-mimo-20260521.md`
