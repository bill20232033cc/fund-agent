# P10-S1 Plan Review — Adversarial DeepReview

- **Date**: 2026-05-21
- **Reviewer**: AgentDS (adversarial plan review)
- **Plan under review**: `docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`
- **Inputs**: `docs/design.md`, `docs/implementation-control.md`, `docs/reviews/post-p9-follow-up-planning-20260521.md`
- **Code facts verified**: `.gitignore`, `fund_agent/config/`, `fund_agent/ui/cli.py`, `fund_agent/services/fund_analysis_service.py`, `fund_agent/fund/extraction_snapshot.py`, `fund_agent/fund/golden_prefill.py`, `fund_agent/fund/golden_answer.py`, `fund_agent/fund/quality_gate_integration.py`, `fund_agent/fund/documents/cache.py`, `fund_agent/fund/documents/sources.py`, `fund_agent/fund/pdf/downloader.py`, `fund_agent/fund/data/nav_data.py`, `fund_agent/fund/data/thermometer.py`, `tests/ui/test_cli.py`, `tests/services/test_fund_analysis_service.py`

## Scope & Assumptions Tested

### Plan Claims

1. Add MIT LICENSE with holder `bill20232033cc`.
2. Add single GitHub Actions CI (`python 3.11`, `ruff check .`, `pytest -q`).
3. Update `.gitignore` with hygiene entries and artifact policy.
4. Introduce `fund_agent/config/paths.py` as static path-defaults module; migrate 12 consumer modules.
5. Handle two untracked files: stage the P8-S3 review artifact, ignore the `.docx`.
6. Update README/docs without changing product behavior.

### Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|--------|
| A1 | `bill20232033cc` is the legal copyright holder | Not verified; GitHub username ≠ legal entity |
| A2 | `uv.lock` is tracked and current | Confirmed tracked; currency not verified |
| A3 | All 12 listed consumer modules actually use path defaults | Partially false: `extraction_score.py` has no path defaults |
| A4 | `fund_agent.config.paths` can import only `pathlib.Path` and `typing.Final` without cycles | Credible; current dependency direction is one-way (UI/Services → Fund → nothing) |
| A5 | Path constant names in plan match existing code | Partially false: several name mismatches (see Finding 2) |
| A6 | Existing tests will pass after import migration without behavior change | Likely true; tests use literal strings, not imported constants |
| A7 | No `.github/workflows` directory exists | Confirmed |
| A8 | `fund_agent/config/` is a clean namespace for the new module | Questionable: empty `prompts/` subdirectories exist |

---

## Findings

### P10S1-001-未修复-中-LICENSE 版权持有人为 GitHub 用户名而非法律实体

- **位置**: Plan §4.1 LICENSE; stop condition
- **问题类型**: open question 未收敛 / 契约缺失
- **当前写法**: 版权行使用 `Copyright (c) 2026 bill20232033cc`，stop condition 仅在 maintainer 主动声明不同持有人时才停止。
- **反例/失败场景**: `bill20232033cc` 是 GitHub 用户名，不是自然人或法人名称。MIT License 的版权行通常应标识实际法律实体。如果 copyright holder 应为个人真实姓名或组织名称，当前默认值在未确认的情况下直接写入 LICENSE 文件，会产生误导性版权声明，且需要后续 fixup commit 修正。
- **为什么有问题**: MIT 许可证的版权归属一旦写入仓库历史就具有法律暗示效力。用 GitHub 用户名代替法律实体名称，即使技术上可接受，也不符合开源项目惯例。plan 的 stop condition 是被动等待 maintainer 纠正，而非主动要求确认。
- **直接证据**:
  - Plan §4.1: `Copyright (c) 2026 bill20232033cc`
  - Plan §4.1 stop condition: "If the maintainer states the legal copyright holder is not `bill20232033cc`"
  - GitHub 仓库 remote: `https://github.com/bill20232033cc/fund-agent.git`
- **影响**: 实施 Agent 在未确认法律实体的情况下提交 LICENSE，后续可能需要修正提交。
- **建议改法和验证点**:
  - 在 Slice P10-S1-A 进入实施前，要求 maintainer 显式确认 copyright holder 的 legal name（自然人姓名或组织名称）。
  - 若 maintainer 确认 `bill20232033cc` 即为预期版权持有人，在 plan 中记录该确认。
  - 验证点：LICENSE 中的版权行与 maintainer 确认一致。
- **修复风险（低）**: 只需在实施前增加一次确认。
- **严重程度（中）**: 不影响代码行为，但涉及法律声明准确性。

---

### P10S1-002-未修复-中-路径常量清单不完整且命名与现有代码不一致

- **位置**: Plan §4.4 Default Path Policy; allowed API 常量列表
- **问题类型**: 切片过粗 / 不可直接实施
- **当前写法**: Plan 在 `config/paths.py` 中定义 12 个 `DEFAULT_*` 常量，并声明 "Existing module-level constant names may remain as aliases to avoid noisy call-site churn"。
- **反例/失败场景**: 实施 Agent 读取 plan 后直接逐文件替换 import，但会遇到以下冲突：
  1. `DEFAULT_SELECTED_FUNDS_CSV` 当前在 **两个** 文件中独立定义（`cli.py:41` 和 `extraction_snapshot.py:22`），且 `fund_analysis_service.py:37` 从 `extraction_snapshot` 导入。Plan 未指定以哪个现有定义为 canonical、哪个变为 alias。
  2. `DEFAULT_GOLDEN_TEMPLATE`（`cli.py:42`）与 plan 的 `DEFAULT_GOLDEN_TEMPLATE_PATH` 名称不同。
  3. `DEFAULT_CACHE_DIR = Path("cache/pdf")`（`downloader.py:20`）与 plan 的 `DEFAULT_PDF_CACHE_ROOT` 名称不同。
  4. `DEFAULT_GOLDEN_ANSWER_OUTPUT`（`cli.py:44`）与 plan 的 `DEFAULT_GOLDEN_ANSWER_JSON` 名称不同但值相同。
  5. `DEFAULT_QUALITY_GATE_SCORE`（`cli.py:45-46`）在 plan 常量列表中完全缺失。
  6. `DEFAULT_SNAPSHOT_OUTPUT_ROOT`（`extraction_snapshot.py:23`）在 plan 常量列表中缺失。
- **为什么有问题**: "may remain as aliases" 给了实施 Agent 过大裁量权。不同模块可能以不同方式做 alias（`from config.paths import X as Y`、模块级 `Y = X`、或直接删旧常量改用新名），导致不一致的导入风格和未来维护困难。
- **直接证据**:
  - `cli.py:41-46`: 定义 5 个 `DEFAULT_*` 常量，其中 `DEFAULT_QUALITY_GATE_SCORE` 未出现在 plan 中
  - `extraction_snapshot.py:22-23`: 定义 2 个 `DEFAULT_*` 常量，`DEFAULT_SNAPSHOT_OUTPUT_ROOT` 未出现在 plan 中
  - `downloader.py:20`: `DEFAULT_CACHE_DIR = Path("cache/pdf")`，plan 中对应 `DEFAULT_PDF_CACHE_ROOT`
- **影响**: 实施 Agent 做不一致的迁移，部分模块用旧名、部分用新名，或遗漏 `DEFAULT_QUALITY_GATE_SCORE` 和 `DEFAULT_SNAPSHOT_OUTPUT_ROOT` 的迁移。
- **建议改法和验证点**:
  - 补充精确的 alias 迁移表，每一行列出：`{现有文件:行号, 现有常量名, 现有值} → {plan 常量名, 是否保留 alias, alias 写法}`。
  - 将 `DEFAULT_QUALITY_GATE_SCORE` 和 `DEFAULT_SNAPSHOT_OUTPUT_ROOT` 纳入 `config/paths.py` 常量列表。
  - 验证点：`grep -rn 'DEFAULT.*Final\[Path\]\|DEFAULT.*= Path(' fund_agent/` 在迁移后只在 `config/paths.py` 中有唯一真源定义（alias 除外）。
- **修复风险（低）**: 只需补充迁移映射表，不改架构。
- **严重程度（中）**: 不修复会导致实施结果不一致，需要返工。

---

### P10S1-003-未修复-低-消费者清单中包含无路径常量的文件

- **位置**: Plan §4.4 消费者文件列表
- **问题类型**: 不可直接实施
- **当前写法**: Plan 将 `fund_agent/fund/extraction_score.py` 列为消费者。
- **反例/失败场景**: `extraction_score.py` 当前不定义任何 `DEFAULT_*` 路径常量，也不直接使用相对路径字符串。实施 Agent 按 plan 修改该文件时，会发现没有需要迁移的 import。
- **为什么有问题**: 不准确的消费者清单会浪费实施 Agent 时间，且掩盖了真正需要关注的遗漏文件（如 `fund_agent/fund/quality_gate.py` 虽无路径常量但可能间接消费，plan 正确未列出）。
- **直接证据**:
  - `grep -n 'DEFAULT.*Path\|Path("' fund_agent/fund/extraction_score.py` → 无输出
  - Plan §4.4 列表第 6 项: `fund_agent/fund/extraction_score.py`
- **影响**: 实施 Agent 做无意义的文件检查或编辑；低影响。
- **建议改法和验证点**: 从消费者列表中移除 `extraction_score.py`，或标注为"验证无需修改"。
- **修复风险（低）**: 删除一行列表项。
- **严重程度（低）**: 不影响正确性，仅影响实施效率。

---

### P10S1-004-未修复-低-空 prompts 目录与 config 范围声明矛盾

- **位置**: Plan §4.4（整体）与 `fund_agent/config/` 当前状态
- **问题类型**: 架构边界 / open question 未收敛
- **当前写法**: Plan 声明 `fund_agent.config.paths` 为静态路径常量模块，不含 prompt manifest、scene registry 或 Dayu config。但未提及 `config/prompts/base/`、`scenes/`、`tasks/` 三个空目录的处理。
- **反例/失败场景**: 新开发者看到 `config/prompts/` 下有 `base/`、`scenes/`、`tasks/` 子目录，会合理推断 config 包承担 prompt 管理职责，与 plan 和 `config/README.md` 的"当前只是配置命名空间占位"声明矛盾。这削弱了 plan 试图建立的 config 包职责边界。
- **为什么有问题**: `config/paths.py` 是一个静态常量模块，与 `prompts/` 目录暗示的运行时配置职责完全不同。两者共存于同一包下且 plan 不对 prompts 目录做任何处置，会让 config 包的边界持续模糊。
- **直接证据**:
  - `ls fund_agent/config/prompts/base/` → 空目录
  - `ls fund_agent/config/prompts/scenes/` → 空目录
  - `ls fund_agent/config/prompts/tasks/` → 空目录
  - `fund_agent/config/README.md`: "当前主链路没有运行时 prompt manifest、scene registry"
  - Plan §4.4: 未提及 prompts 目录
- **影响**: config 包职责边界模糊，未来可能被误用为 prompt/config 混合模块。
- **建议改法和验证点**:
  - 选项 A（推荐）: 删除空 `prompts/` 目录树，在 plan 或 `config/README.md` 中说明 prompt 相关能力属于后续设计裁决，不在当前 config 包范围内。
  - 选项 B: 在 plan 中显式声明 `prompts/` 目录保留但不在 P10 范围内处理，并更新 `config/README.md` 说明其状态。
- **修复风险（低）**: 删除空目录无代码影响。
- **严重程度（低）**: 不影响当前功能，但积累技术债。

---

### P10S1-005-未修复-中-缺少迁移完整性验证测试

- **位置**: Plan §5 Tests, Slice P10-S1-B validation
- **问题类型**: 测试缺口
- **当前写法**: Plan 添加 `tests/config/test_paths.py`（测试 config 模块自身）和 `tests/test_repo_hygiene.py`（测试 LICENSE/CI/gitignore），并复用现有测试验证行为不变。
- **反例/失败场景**: 迁移完成 6 个月后，开发者在 `fund_agent/fund/new_module.py` 中写了 `MY_PATH = Path("cache/foo")`，绕过了 `config.paths`。没有测试能发现这一回归，路径常量重新开始分散。或者，迁移时某个模块的 import 被遗漏（例如 `extraction_snapshot.py` 的 `DEFAULT_SNAPSHOT_OUTPUT_ROOT` 不在 plan 常量列表中），实施 Agent 保持原样不迁移，没有测试报错。
- **为什么有问题**: Plan 依赖实施 Agent 的人工完整性检查，但无自动化回归保护。路径常量的集中化是一次性迁移收益，没有测试守卫会随时间退化。
- **直接证据**:
  - Plan §5 Tests 允许的测试文件: `tests/config/test_paths.py`、`tests/test_repo_hygiene.py`
  - 无任何测试断言"所有 UI/Service/Fund 模块中的路径默认值来源于 `fund_agent.config.paths`"
  - 现有测试使用 literal string（如 `Path("docs/code_20260519.csv")`），即使迁移遗漏也不会失败
- **影响**: 路径常量逐渐重新分散，P10-S1-B 的投资回报随时间衰减。
- **建议改法和验证点**:
  - 在 `tests/config/test_paths.py` 中增加测试：扫描 `fund_agent/ui/`、`fund_agent/services/`、`fund_agent/fund/` 下所有 `.py` 文件，断言不包含 `= Path("cache` 或 `= Path("docs/` 或 `= Path("reports/` 模式的模块级常量定义（排除 `config/paths.py` 自身和注释）。
  - 或将此测试作为 P10-S1-D 的 hygiene 验证项。
- **修复风险（低）**: 增加一个 lint 级测试，不影响功能。
- **严重程度（中）**: 不影响当前正确性，但缺少回归保护意味着迁移收益不可持续。

---

### P10S1-006-未修复-低-config/__init__.py 用途未定义

- **位置**: Plan §5 Config Path Defaults 允许文件列表
- **问题类型**: 不可直接实施
- **当前写法**: Plan 将 `fund_agent/config/__init__.py` 列为允许修改的文件，但未说明应写入什么内容。当前该文件为 0 字节。
- **反例/失败场景**: 实施 Agent 自行决定在 `__init__.py` 中添加 `from fund_agent.config.paths import *` 或包级 docstring 或 `__all__`，这些选择会影响后续所有 `from fund_agent.config import ...` 的调用方行为。
- **为什么有问题**: `__init__.py` 的内容决定了 config 包的公开 API 面。Plan 不给方向，实施 Agent 可能做出与项目惯例不一致的选择，或创建不必要的重导出。
- **直接证据**:
  - `fund_agent/config/__init__.py`: 0 bytes
  - Plan §5: `fund_agent/config/__init__.py` 列为 allowed file
- **影响**: 实施 Agent 的随意选择可能创建后续清理负担。
- **建议改法和验证点**:
  - 明确 `__init__.py` 保持空文件，或只包含包级 docstring。
  - 若需要重导出，显式列出允许重导出的符号。
- **修复风险（低）**: 加一句话即可。
- **严重程度（低）**: 不影响功能，但缺少规格。

---

## Architecture Boundary Review

Plan 的架构边界设计总体良好：

- **Import direction**: `config/paths.py` → 只依赖 stdlib；UI/Service/Capability → 可导入 config。无反向依赖。与当前代码事实一致（Capability 不导入 UI/Service）。
- **No runtime config creep**: Plan 显式拒绝 env var、workspace config、Dayu/Host/Engine。边界清晰。
- **No product behavior change**: Path 值不变，只改定义位置。CLI、Service、renderer、quality gate 语义不变。

轻微关注点（已在 findings 中覆盖）：
- `config/prompts/` 空目录与 plan 对 config 包的定义不一致（P10S1-004）。
- `config/__init__.py` 未定义公开 API 面（P10S1-006）。

## Overengineering Review

Plan 的克制程度良好：
- 拒绝 matrix CI builds、coverage thresholds、packaging workflows（§4.2, Slice A non-goals）。
- 拒绝 env var override、workspace discovery、dataclass settings loader、Dayu/Host/Engine config（§4.4 non-goals）。
- 拒绝 `.docx` 转换、删除或检查（Slice C non-goals）。
- `config/paths.py` 仅包含 12 个 `Final[Path]` 常量，无类、无 loader、无 factory。

无过度设计发现。

## Overcoupling Review

轻微关注：
- Plan 将 `config/README.md` 更新纳入 Slice P10-S1-D（文档）。当前 `config/README.md` 描述 config 为"命名空间占位"，plan 要将其更新为"静态默认路径"。这一更新是合理的，但应在 Slice B（路径配置）完成后立即做，而非延迟到 Slice D。如果 Slice B 完成但 Slice D 被阻塞，config README 与实际代码状态不一致。
- 12 个消费者模块全部依赖单一 `config/paths.py`。如果未来某个消费者需要不同的路径值，修改 `paths.py` 会影响所有消费者。但 plan 已明确"Explicit CLI / Service parameters remain authoritative over defaults"，所以这是低风险的正常依赖。

---

## Open Questions

1. **Copyright holder 确认**: `bill20232033cc` 是否为 maintainer 期望的 LICENSE 版权持有人？若是，是否接受 GitHub 用户名而非法律实体名称？
2. **空 prompts 目录处置**: 删除还是保留并文档化？若保留，是否应在 `config/README.md` 中说明其状态？
3. **`DEFAULT_QUALITY_GATE_SCORE` 归属**: 该常量在 `cli.py:45` 中定义，值为 `Path("reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json")`。这是一个指向特定历史运行产物的硬编码路径，不应作为通用默认值。是否应将其从 path defaults 集中移除，或改为仅用于 CLI 默认的局部常量？

---

## Residual Risks

| Risk | Severity | Suggested Tracking |
|------|----------|-------------------|
| Path constant migration 可能遗漏 `DEFAULT_QUALITY_GATE_SCORE` 和 `DEFAULT_SNAPSHOT_OUTPUT_ROOT` | Low | P10-S1-B implementation review checklist |
| `uv.lock` 过期导致 CI `--frozen` 失败 | Low | P10-S1-A implementation preflight: run `uv lock --check` |
| `config/paths.py` 未来被滥用为 runtime config | Low | P10-S1-D `config/README.md` 显式声明边界 |
| `fund_agent/README.md` 更新后与 `AGENTS.md` 的 README 职责定义不一致 | Low | P10-S1-D review checklist |
| CI `ubuntu-latest` 与 macOS 本地开发环境 Python 3.11 行为差异 | Low | 接受；release readiness 基线 |

---

## Final Plan Review Conclusion

**PASS-WITH-RISKS**

Plan 整体合理，scope 清晰，slice sequencing 正确（A→B→C→D），过度设计风险低。6 个 findings 均不构成 blocker：

- P10S1-001（LICENSE 持有人）需要在实施前增加一次确认。
- P10S1-002（路径常量命名不一致）需要补充精确 alias 迁移表。
- P10S1-003/004/006 为低严重度，修复成本极低。
- P10S1-005（迁移完整性测试）是可持续性改进，可在 Slice D 或后续处理。

建议在 plan 修订后、P10-S1-A 实施前，优先关闭 P10S1-001 和 P10S1-002。
