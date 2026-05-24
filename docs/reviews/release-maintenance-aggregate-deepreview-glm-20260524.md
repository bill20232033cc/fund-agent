# Release-Maintenance Aggregate Deepreview (GLM)

> **Review date**: 2026-05-24
> **Reviewer**: AgentGLM (GLM-5.1)
> **Branch**: `codex/checklist-host-engine-design`
> **Base/range**: `origin/main..HEAD`
> **Commits reviewed**: 24 commits (3303d4c → 2aa4a7c)
> **Files changed**: 103 (+7536 / −8400)
> **Conclusion**: **PASS_WITH_FINDINGS**
> **Finding count**: 7 (0 blocker, 0 high, 3 low, 4 informational)

---

## 1. Scope Summary

本次 aggregate deepreview 覆盖 `codex/checklist-host-engine-design` 分支相对 `origin/main` 的全部变更，包括：

- 代码变更（`.py`, `.toml`, `.yml`）
- 文档/控制文档变更（`docs/design.md`, `docs/implementation-control.md`）
- Review artifacts（`docs/reviews/` 新增 ~60 个 review artifact）
- 删除的历史文档清理（`docs/20260430/`, `docs/audit-alignment.md`, `docs/fund-analysis-research-notes.md` 等）
- `uv.lock` 依赖锁更新

### 代码变更清单

| 文件 | 变更性质 | 关键内容 |
|------|---------|---------|
| `pyproject.toml` | 重构 | hatchling → setuptools；PEP 621 元数据/classifiers/authors/urls；`pandas>=2.1.4,<4.0.0`；`test` 可选依赖分组；`black`/`mypy`/`pyright`；setuptools package discovery |
| `.github/workflows/ci.yml` | 增强 | 添加 `--cov-fail-under=50` 覆盖率门控 |
| `fund_agent/fund/data/__init__.py` | 扩展 | 温度计 source/cache/type 公共导出与默认工厂函数 |
| `fund_agent/fund/documents/cache.py` | 加固 | `NamedTemporaryFile` + `replace()` 原子写入 |
| `fund_agent/fund/template/renderer.py` | 功能 | 第 0 章风险/action-threshold 结构化 slot（+260 行） |
| `fund_agent/services/fund_analysis_service.py` | 重构 | `_run_analysis_core()` 共享核心；`checklist()` 方法；`FundChecklistResult`；`_ValidatedRequest` 基金代码规范化 |
| `fund_agent/services/thermometer_service.py` | 重构 | Protocol 化缓存/数据源抽象；移除直接实现导入 |
| `fund_agent/services/*.py`（6 个） | 术语 | "Capability" → "Agent 层基金能力" 全量替换 |
| `fund_agent/ui/cli.py` | 功能 | `checklist` 命令完整接入；`_echo_checklist_result` |
| `fund_agent/services/__init__.py` | 导出 | `FundChecklistResult`, `ThermometerBatchResult`, `ThermometerReading` |
| 测试文件（7 个） | 新增/扩展 | +898 行测试覆盖 |

---

## 2. Truth Source Conformance

### 2.1 Dayu 四层边界 `UI → Service → Host → Agent`

**结论：✅ 符合**

- 无 `fund_agent/host/` 或 `fund_agent/agent/` 占位目录存在（已验证）。
- 当前确定性主链路保持 UI → Service → `fund_agent/fund` Agent 层基金能力的过渡路径。
- 所有 Service 层 docstring 已从 "Capability 层" 更正为 "Agent 层基金能力"。
- `design.md` v2.2 明确标注 Host/Agent 为"目标包；当前尚未接入"。
- `implementation-control.md` Startup Packet 显式声明"未开独立 Host/Agent gate 前，不得创建占位包"。

### 2.2 Host 未来使用 `dayu.host`；Agent 执行/tool-loop 未来使用 `dayu.engine`

**结论：✅ 符合**

- 无 `dayu.host` 或 `dayu.engine` 导入。
- `pyproject.toml` 未声明 Dayu 运行时依赖。
- 设计文档明确记录未来要求。

### 2.3 无 placeholder `fund_agent/host` 或 `fund_agent/agent`

**结论：✅ 符合**

- `ls fund_agent/host/ fund_agent/agent/` 确认目录不存在。

### 2.4 无显式参数在 `extra_payload` 中

**结论：✅ 符合**

- 代码搜索仅发现 docstring 中的声明式提及（"不使用 `extra_payload`"），无实际使用模式。
- 所有 Service 请求参数均为显式 typed 字段。

### 2.5 FundDocumentRepository 年报边界

**结论：✅ 符合**

- `cache.py` 的原子写入变更属于 documents 层内部实现。
- Service 层仍通过 `FundDataExtractor` Protocol 访问年报，无直接文件系统绕过。

### 2.6 Package/Dependency 基线

**结论：✅ 符合**

- setuptools 替代 hatchling，PEP 621 元数据完整。
- `pandas>=2.1.4,<4.0.0` 显式声明上下界。
- `test` / `dev` 可选依赖正确分组，测试工具不污染生产依赖。
- setuptools package discovery 排除 `tests*`, `docs*`, `reports*`, `scripts*`, `workspace*`, `cache*`。
- `uv.lock` 已同步更新（361 行变更）。

### 2.7 docs/control 一致性

**结论：✅ 符合**

- `design.md` v2.2 包含 QG/FJ 契约表、ch0 风 险 slot、温度计集成完整文档。
- `implementation-control.md` Startup Packet 更新至 Host/Agent boundary decision accepted 状态。
- 术语迁移一致（ Capability → Agent 层）。

### 2.8 无 misleading future-work-as-done

**结论：✅ 符合**

- Host/Agent 始终标注为"目标"和"未来"。
- `design.md` §2.1 边界裁决明确当前"尚未接入 Host/Agent 调度"。

---

## 3. Validation Evidence

| 检查项 | 结果 |
|--------|------|
| `uv run pytest -q` | 619 passed, 0 failed |
| `uv run ruff check .` | All checks passed |
| `fund_agent/host/` 目录 | 不存在 ✅ |
| `fund_agent/agent/` 目录 | 不存在 ✅ |
| `extra_payload` 实际使用 | 无 ✅ |

---

## 4. Findings

### F1 — LOW：CI 覆盖率门控阈值偏低

**位置**: `.github/workflows/ci.yml`

CI 设置 `--cov-fail-under=50`，而 implementation-control.md 记录实际覆盖率为 91.94%。50% 阈值作为安全网可以接受，但可能无法有效捕获覆盖率回退。建议后续根据实际基线提升至更高阈值（如 80% 或 90%）。

**风险评估**: 当前不构成阻断，实际覆盖率远高于阈值。

### F2 — LOW：`fund_agent/fund/data/__init__.py` docstring 残留 "Capability" 术语

**位置**: `fund_agent/fund/data/__init__.py:2-5`

模块 docstring 使用 "Fund Capability data 层" 措辞。虽然此模块在 Agent 层 `fund_agent/fund` 内部，"Capability" 在此处可理解为"基金领域能力"而非旧架构术语，但与全项目 Service 层已完成 "Capability → Agent 层" 迁移的背景存在术语不一致。

**风险评估**: 内部模块 docstring，不影响外部契约或架构边界。

### F3 — LOW：`_echo_checklist_result` 缺少显式类型注解

**位置**: `fund_agent/ui/cli.py:1043`

```python
def _echo_checklist_result(result) -> None:  # type: ignore[no-untyped-def]
```

参数 `result` 使用了 `# type: ignore` 抑制警告，而非声明为 `FundChecklistResult` 类型。虽然 CLI 输出函数对运行时无影响，但显式类型注解可改善可读性和 IDE 支持。

**风险评估**: CLI 层输出辅助函数，不影响分析核心。

### F4 — INFO：`uv.lock` 变更范围合理

`uv.lock` 361 行变更与 pyproject.toml 依赖重构一致（setuptools 替换 hatchling、pandas 上下界、新增测试工具依赖）。无意外依赖引入。

### F5 — INFO：历史文档清理范围

以下文档被删除，属于合理的历史清理：
- `docs/20260430/` 全部（ARCH/PRD/RESEARCH/PONYFORGE_LESSONS）
- `docs/audit-alignment.md`, `docs/code-is-cheap-analysis.md`, `docs/dayu-agent-audit-analysis.md`
- `docs/design-update.md`, `docs/fund-analysis-research-notes.md`, `docs/implementation-control-p4.md`
- `docs/repo-audit-20260519.md`, `docs/repo-audit-20260520.md`

这些文档已被 design.md v2.2 和 implementation-control.md 吸收或替代。

### F6 — INFO：Review artifacts 量级

`docs/reviews/` 新增约 60 个 review artifact，覆盖 release-maintenance 各 slice 的 plan/review/code-review/controller-judgment 全链路。文档审计轨迹完整。

### F7 — INFO：`renderer.py` 第 0 章 slot 实现质量

`_render_chapter_0` 的新增 ~260 行代码实现了结构化风险 slot 和 action-threshold slot，优先级链（veto → watch → stress → default）与 `derive_final_judgment` 优先级表一致。新增 `_first_or_none` 辅助函数简洁实用。`_nullable_text` 和 `_sentence_body` 复用已有 renderer 工具函数。实现符合第一性原理。

---

## 5. Architecture Assessment

### 5.1 Service 重构

`FundAnalysisService` 重构为 `_run_analysis_core()` + `analyze()` + `checklist()` 三段结构，分析核心（抽取 → 基金类型 → QG → R=A+B-C → 一致性 → 投资者获得感 → 风险检查 → 压力测试 → 检查清单 → 估值状态 → 最终判断）由 `_run_analysis_core()` 统一执行，`analyze` 额外执行模板渲染和程序审计，`checklist` 直接返回 `FundChecklistResult`。

**判定**: 正确实现了 design.md §2.2 和 §9.0 的 checklist 独立用例要求，不重复基金规则，quality gate / final judgment 同源。

### 5.2 基金代码规范化

`_ValidatedRequest` 封装规范化后的 6 位基金代码，`_validate_request` 返回 `_ValidatedRequest`，所有后续调用使用规范化代码。修复了此前 commit `23b3a03` 记录的 fund code normalization 缺陷。

**判定**: 正确，规范化在 Service 入口处统一执行。

### 5.3 ThermometerService Protocol 化

`ThermometerService` 新增 `_ThermometerHistoryCache` 和 `_CachedPePbHistory` Protocol，将 `ThermometerHistoryCache` 具体类依赖替换为 Protocol 依赖。默认工厂函数 `create_default_thermometer_history_cache` / `create_default_thermometer_source` 从 `fund_agent/fund/data/__init__.py` 提供。

**判定**: 符合 Service 层依赖注入模式（Protocol + 默认工厂），与 `FundAnalysisService` 的 `_FundDataExtractor` Protocol 模式一致。

### 5.4 原子写入

`AnnualReportDocumentCache` 使用 `NamedTemporaryFile(delete=False)` + `Path.replace()` + 异常时 `unlink` 清理实现原子写入。

**判定**: 正确的 atomic write 模式，避免写入中途崩溃导致缓存损坏。`BaseException` 捕获范围适当（含 KeyboardInterrupt）。

### 5.5 pyproject.toml 工程基线

hatchling → setuptools 迁移与 Dayu 工程基线一致。PEP 621 完整元数据、setuptools package discovery 范围、`test`/`dev` 分组、`pandas` 上下界均符合 `AGENTS.md` 和 `design.md` §9.1 要求。

---

## 6. Residual Risks

| ID | 风险 | 等级 | 所有权 |
|----|------|------|--------|
| RR-A1 | CI 覆盖率阈值 50% 可能无法防止大幅回退 | LOW | 未来 hardening |
| RR-A2 | `fund_agent/fund/data/__init__.py` "Capability" 术语残留 | LOW | 未来术语统一 |
| RR-A3 | `_echo_checklist_result` 缺少显式类型注解 | LOW | 未来清理 |

---

## 7. Blocking Questions

无阻断性问题。

---

## 8. Conclusion

**PASS_WITH_FINDINGS** — 0 blocker, 0 high, 3 low, 4 informational findings。

分支变更完整且一致地实现了：
1. Dayu 四层边界对齐（术语迁移、Host/Agent 延迟裁决）
2. `fund-analysis checklist` 独立 Service 用例接入
3. pyproject.toml 工程基线对齐（setuptools/PEP 621/pandas 声明）
4. 第 0 章风险/action-threshold 结构化渲染
5. 缓存原子写入加固
6. 覆盖率 CI 门控
7. 基金代码规范化修复

所有代码变更与 `AGENTS.md`、`docs/design.md` v2.2、`docs/implementation-control.md` Startup Packet 保持一致。619 测试全部通过，ruff 检查无违规。

### Artifact

- **路径**: `docs/reviews/release-maintenance-aggregate-deepreview-glm-20260524.md`
- **结论**: PASS_WITH_FINDINGS
- **Finding count**: 7 (0 blocker, 3 low, 4 info)
- **Blocking questions**: 无
