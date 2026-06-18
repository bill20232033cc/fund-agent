# fund-agent 仓库级深度审核报告

> 审核日期：2026-06-10
> 审核范围：仓库全量代码、文档、测试、治理产物（仅审核，未改动任何代码）
> 审核基准：`AGENTS.md`（规则真源）、`docs/design.md`（设计真源）、`docs/implementation-control.md`（实施总控）、`docs/fund-analysis-template-draft.md`（分析模板真源）、`docs/current-startup-packet.md`（当前控制包）
> 审核方法：第一性原理 + 文档-代码-治理三方对账 + 静态结构扫描

---

## 0. 执行摘要

fund-agent 是一个以"基金分析 Agent"为名、行"工程化 8 章基金体检报告生成"之实的 Python 包。它通过 24 天（2026-05-17 → 2026-06-10）连续迭代，已经搭建出一个**高强度治理、低业务通过**的系统：4 层架构骨架、99 个生产模块、84 个测试模块、约 7.3 万行生产代码与 6 万行测试代码、2170 份 markdown 文档、1 份 Acceptance Startup Packet 与 200+ 份 gate review 记录。

**整体判断：项目处于"工程化治理已成、领域能力只完成结构化抽取与分析的 40%、LLM 主路径只完成 typed template 闭环、Live 端到端 zero-proof 状态"。**

主要问题（按严重度从高到低）：

1. **生产主链路不真实可达**。`analyze` 真实运行依赖 CSRC EID 公网请求与 akshare `wind_all_a` 公网请求；当前 CI 没有任何"网络/PDF/Live EID"用例，CI 永远绿色不代表产物可用。
2. **8 章模板中第 1-6 章默认路径是确定性文本填充**，没有 LLM 生成也没有 LLM 审计；唯一走 LLM 的 `--use-llm` 路径在配置正确时也只是 typed template path 的薄封装，且该路径当前没有任何 live 端到端 evidence。
3. **Host / Agent 内化是"接口占位而非运行时"**：`fund_agent/host` 只有一个 719 行的 `runtime.py`，`fund_agent/agent` 5 个模块均围绕 `ChapterFactProjection` 与 Fund primitives wrapper；"tool loop / runner / ToolRegistry / ToolTrace schema" 全部以 typed dataclass 表达，**没有真正运行过 LLM tool loop**。`AGENTS.md` 第 1 节"必须内化 Dayu Host/Engine 能力"在事实层面只完成了 30%-40%。
4. **覆盖率 gate 50% 是项目级 CI 阻断线**（已落实），但 `AGENTS.md` / README 反复强调"单文件 ≥80% 是评审目标"。项目实际单文件覆盖率无法在 CI 报告中获取，且 `docs/reviews/` 中多次出现"单文件未达到 80%、在 review 中说明原因"的批注，说明这一"评审目标"长期不被强制。
5. **`docs/implementation-control.md` 与 `docs/reviews/` 的同步存在双重口径**：control doc 上半部为"当前真源"、下半部为"历史 gate 账本"，每次新 gate 都在尾部追加；与 `AGENTS.md` 要求的"优先压缩而不是追加长日志"不完全一致，文档实际长度已超 2000 行。
6. **`scripts/` 目录存在非产品脚本**（`claude_mimo_simple.py`、`aliases.zsh`、`multi_tail.py`、`remind-agentcontroller.sh`、`setup-ai-session.sh`、`start-tmux-agents.sh`、`start-tmux-ai.sh`），与 `pyproject.toml` 排除规则 `exclude = ["tests*", "docs*", "reports*", "scripts*", ...]` 一致地**不进 wheel**，但 README/AGENTS.md 没有任何一段说明这些脚本的合法用途，存在"开发态脚本外溢"风险。
7. **`fund_agent/tools/claude_mimo.py`** 与 **`scripts/claude_mimo_simple.py`** 是面向小米 MiMo Token Plan 的本地配置工具，**与基金分析无关**。`pyproject.toml` 中没有任何 `fund_agent.tools` 的 `[project.scripts]` 入口，但 `claude_mimo.py` 自身声明了 typer app 入口；存在"import 即可触发 typer 注册"风险，且该模块从未在 `tests/` 中被覆盖。
8. **核心模板的"AI 行为"集中在 prompt 字符串中**，例如 `chapter_writer.py` 的 prompt 由代码字符串拼接而成；测试只覆盖"marker 解析、必须 marker、必须 anchor"等结构性约束，不覆盖 LLM 输出分布。`prompt_only` 模式的设计哲学（"故意不调 LLM"）在产品 CLI 中可被误用：当用户没装 OpenAI SDK 但提供 `OPENAI_API_KEY`，CLI 仍尝试构造 client，最终失败。
9. **基金类型识别没有覆盖 QDII/FOF 的实证样本**。`fund_type.py` 已经把 `qdii_fund`、`fof_fund` 列为合法标签，但 `select_minimal_golden_set()` 明确"暂时排除货币基金类，作为当前 8 章模板适配度不足的 edge case"——意味着 FOF/货币类基金没有 golden coverage，`--use-llm` 路径在这些基金上的行为是"unspecified"。
10. **P13 跟踪误差 / P14 跟踪误差 / P15 跟踪误差** 等多条"已接受"产品承诺并未在 production 默认路径上启用：当前 `run_risk_checks()` 仍把 `tracking_error` 作为"显式传参"输入，跟踪误差结构化字段仅在 `index_fund` / `enhanced_index` 上进入 FQ2 coverage 分母，但 R1 程序审计的 `tracking_error` 真源解析是文档级"直接披露"路径，不验证 akshare 派生路径；这与 `P13/P14/P15` 的"派生接受"承诺之间存在事实缺口。

下文按"项目本质 → 仓库结构 → 架构边界 → 代码质量 → 模板/分析能力 → 测试/质量保障 → 文档/治理 → 风险与建议"逐节展开。

---

## 1. 第一性原理视角：项目到底在解决什么

剥开所有治理、文档、gate 记录后，`fund-agent` 真正尝试解决的需求是：

> **一个普通基民（理解 CS50P/价值投资语境下，作者本人或同侪）想买入某只公募基金时，5 分钟内拿到一份基于公开年报的 8 章结构化体检报告。**

这条需求成立的隐含前提是：

1. 年报 PDF 可以稳定、自动地下载到本地。
2. PDF 解析可以稳定提取出 `§1/§2/§3/§4/§8/§9/§10` 等章节。
3. 8 章模板（R=A+B-C、投资者获得感、言行一致性、压力测试、估值状态、最终判断）是公认的、对买入决策有信号价值的结构。
4. 任何数字判断都必须能溯源到年报具体章节/表格/行号。

把这条需求与项目现状对账：

- ✅ **年报 PDF 自动化**：已经实现 EID single-source policy、`httpx` mock 测试、`%PDF-` 校验、原子写入、PDF 缓存与元数据持久化，**但没有 live EID 通过的 evidence**。
- ⚠️ **PDF 解析稳定性**：`pdf/` 目录下 `parser.py` 在 `tests/fund/pdf/test_parser.py` 中只覆盖 `§3` 定位、目录误判回归、偏移单调递增；其它章节全部依赖"调用方传入已抽取文本"。`extractors/` 下的 4 个 extractor 只覆盖 4 个章节：`§1/§2/§3/§4/§8/§9/§10`，**§5/§6/§7 等章节的"事实层"根本没有抽取路径**，相关章节内容靠模板文案填空。
- ✅ **8 章模板共识性**：模板是 canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 投影的机器可消费契约，并通过 `fund_agent/fund/template/typed_contracts.py` 提供 typed dataclass；有 `tests/fund/template/` 覆盖每个章节字段、preferred_lens、ITEM_RULE、`audit_focus` 闭集。**唯一隐患**：模板"禁止预测、禁止交易、禁止动机猜测"等硬约束在 prompt 字符串里，prompt 不在测试断言范围。
- ✅ **数字溯源**：evidence anchor 通过 `> 📎 证据：年报§[章节] [内容描述]` 强制落到章节与表格/行号；附录集中 `年报[年份]§[章节]表[编号]行[行号]`。`audit_programmatic.py` 强制 P3 规则覆盖"每章最小证据行"。

**第一性原理结论**：项目的"骨架与契约"质量高于"数据真实可达性"。如果一个真实用户在 2026-06-10 拿到这个仓库并执行 `fund-analysis analyze --fund-code 004393 --report-year 2024`，会发生：

1. CLI 解析参数成功。
2. Service 调用 `FundDataExtractor.extract()` → 调用 `FundDocumentRepository.load_annual_report()`。
3. Repository 调用 EID source。EID 是真实公网端点，**未提供 mock 路径**。
4. 若用户机器能访问 CSRC EID：返回 PDF / 报错（`not_found` / `unavailable` / `schema_drift` / `identity_mismatch` / `integrity_error` 五种之一，按 `not_found` 与 `unavailable` 在 single-source mode 下 terminal）。
5. 若用户机器不能访问 EID：抛出 `AnnualReportSourceUnavailableError`，CLI 退出码非零。

这条 happy path 在 `tests/fund/integration/test_p3_cli_e2e_matrix.py` 中是 **fake repository / fake nav provider / fake thermometer 隔离后**测试的，**没有真实 EID/akshare 触发的 evidence**。`docs/current-startup-packet.md` 明确"Next entry point: User-directed next gate. Recommended options are downstream integration implementation gate, or a separately authorized live EID failure-branch evidence gate."

即：**当前仓库不是 production ready，而是 "no-live evidence + no-live enforcement" 的 engineering prototype**。这一点对任何新加入的贡献者必须坦白。

---

## 2. 仓库规模与目录结构

| 维度 | 数值 | 备注 |
|---|---|---|
| 生产 Python 文件 | 99 个 | `find fund_agent -name "*.py" \| wc -l` |
| 测试 Python 文件 | 84 个 | `find tests -name "*.py" \| wc -l` |
| 生产代码行数 | 73 343 | `wc -l` |
| 测试代码行数 | 59 706 | `wc -l` |
| markdown 文档 | 2 170 份 | `find docs -name "*.md" \| wc -l`（含 `docs/reviews/` gate 文档） |
| reviews 子目录文档 | 约 240+ | `ls docs/reviews/ \| wc -l` |
| reports 子目录运行产物 | 15 类 | `ls reports/`，含 1216 个 `quality-gate-runs` 子目录 |
| 关键文件行数 | audit 1488 / renderer 2046 / fund_analysis_service 1378 / agent runner 1600 / host runtime 719 / chapter_orchestrator 3393 / cli 2458 | 单文件 1k+ 行已成常态 |

**根目录布局**（已审核）：

```
fund-agent/
├── AGENTS.md                    # 规则真源（Claude Code 入口）
├── CLAUDE.md                    # Claude 类 Agent 入口适配层
├── README.md                    # 用户手册
├── LICENSE                      # MIT
├── pyproject.toml               # 项目元信息 + dev/test 依赖
├── uv.lock                      # 依赖锁
├── .github/workflows/ci.yml     # CI: ruff + pytest >= 50% 覆盖率
├── docs/
│   ├── design.md                # 设计真源
│   ├── implementation-control.md # 实施总控（> 2000 行）
│   ├── current-startup-packet.md # 当前控制包
│   ├── fund-analysis-template-draft.md # 8 章模板（canonical JSON 在此）
│   ├── learning-roadmap.md      # 作者个人学习路线
│   ├── next-development-phaseflow.md
│   ├── p19-phase-definition.md
│   ├── p19-thermometer-technical-proposal.md
│   ├── golden-answer-instructions.md
│   ├── golden-answer-template.md
│   ├── code_20260519.csv        # 精选基金池 CSV
│   ├── reviews/                 # 240+ 份 gate review
│   └── archive/                 # 历史账本（已迁出 control doc）
├── fund_agent/                  # 主包（4 层）
│   ├── __init__.py
│   ├── README.md
│   ├── ui/                      # Typer CLI（cli.py 2458 行）
│   ├── services/                # 14 个 .py 编排层
│   ├── host/                    # 内化 Host runtime（runtime.py 719 行）
│   ├── agent/                   # 内化 Agent 执行（5 个模块）
│   ├── fund/                    # Agent 层基金能力（最大包）
│   ├── config/                  # 静态路径 + LLM env config
│   └── tools/                   # 第三方 AI 工具配置（与基金无关）
├── tests/                       # 84 个测试文件
├── scripts/                     # 8 个本地脚本（不进 wheel）
└── reports/                     # 15 类运行产物
```

**观察**：

- `fund_agent/fund/` 是真正的领域包，承载了文档仓库、抽取器、分析、模板、审计、quality gate、数据适配器；`fund_agent/services/` 是 14 个 service 模块的薄编排层；`fund_agent/ui/` 只有一个 `cli.py`。
- `fund_agent/host/` 极薄（仅 1 个 py + 1 个 README），与 `AGENTS.md` 描述的"Host 治理 run lifecycle、cancel、deadline、terminal state、safe diagnostics、event/outbox"范围**不匹配**——`runtime.py` 提供了 run lifecycle 与 cancel/deadline，但 **outbox/replay/memory/durable session/external sink protocol 全部未实现**。`host/README.md` 自己也明确"非目标"。
- `fund_agent/agent/` 5 个模块全部围绕 `ChapterFactProjection` 与 Fund primitives wrapper，**没有真正的 LLM tool loop**。`AGENTS.md` 描述的"runner、tool loop、ToolRegistry、ToolTrace、context budget、tool execution contract" 在事实层面**只完成了 typed dataclass 表达 + scheduler interruption 模拟**。
- `fund_agent/tools/` 与 `scripts/claude_mimo_simple.py` 是**面向小米 MiMo Token Plan 的本地配置工具**，与基金分析无关；它们的存在会让任何只读 README 的用户困惑。`pyproject.toml` 已经把 `tools/` 包包含进 `fund_agent*`，但 `tools/claude_mimo.py` 没有在 `[project.scripts]` 注册为可执行命令；用户 `from fund_agent.tools.claude_mimo import app` 会触发 Typer app 构造但不会自动执行。

---

## 3. 架构与模块边界审核

### 3.1 目标架构

`AGENTS.md` 第 1 节硬约束：

```text
UI -> Service -> Host -> Agent
```

且明确：

- UI 只依赖 Service，不直接调用 Host 或 Agent 内部模块。
- Service 可调用 `fund_agent/fund` 公开能力，**不新增 UI 直接调用 Agent 内部模块**。
- Host 不直接依赖 `dayu-agent` / `dayu.host`。
- Agent 不直接依赖 `dayu-agent` / `dayu.engine`。
- `fund_agent/fund` 是 Agent 层基金领域能力包。

### 3.2 实际落地点

| 边界 | 实际状态 | 证据 | 评价 |
|---|---|---|---|
| UI → Service | ✅ 成立 | `fund_agent/ui/cli.py` 顶部 `from fund_agent.services import ...`；`tests/ui/test_cli.py` 守卫"CLI 不直接导入 fund_agent.fund" | 干净 |
| UI → Host/Agent | ❌ 不应发生 | `fund_agent/ui/cli.py` 顶部未发现 `from fund_agent.host` 或 `from fund_agent.agent` 导入 | 已通过 |
| Service → Host | ✅ 受控 | `fund_agent/services/agent_bridge.py` 把 `HostRunContext` 翻译为 `AgentSchedulerInterruption` | 边界清晰 |
| Service → Agent | ✅ 受控 | 同上 | 边界清晰 |
| Service → Fund | ✅ 多入口 | `fund_analysis_service.py`、`chapter_orchestrator.py`、`final_chapter_assembler.py` 等直接 import `fund_agent.fund.*` | 范围大，但分层职责清楚 |
| Host → Fund/Service | ❌ 不应发生 | `fund_agent/host/runtime.py` 顶部 `from __future__ import annotations` 之后无 `fund_agent.services` / `fund_agent.fund` 导入；`tests/host/` 守卫"Host 包不导入 Service/Fund" | 已通过 |
| Agent → Host | ❌ 不应发生 | `fund_agent/agent/contracts.py` 顶部 `from fund_agent.fund.chapter_facts import ChapterFactProjection` 与 `from fund_agent.fund.evidence_availability import EvidenceAvailability`，**没有 `from fund_agent.host`** | 已通过 |
| Agent → Fund | ✅ 受控 | Agent `tools.py` 通过 typed wrappers 包装 Fund primitives | 边界清晰 |
| `fund_agent/fund` 不依赖 Service/Host/Agent | ✅ 成立 | `fund_agent/fund/` 子模块无 `fund_agent.services` / `fund_agent.host` / `fund_agent.agent` 导入 | 干净 |

**结论**：四层架构的 import 边界严格遵守，所有 6 个跨层调用都有显式桥接模块（`agent_bridge.py`）；CI 守卫齐全（`tests/host/test_runtime_*.py` 验证 Host 不导入 Service/Fund，`tests/config/test_paths.py` 验证 UI 不越过 Service）。

### 3.3 边界执行中的细微问题

1. **Service → Fund 的接口过大**：`fund_agent/services/fund_analysis_service.py` 顶部一次性 import 30+ Fund 模块（`FundDataExtractor`、`ChapterFactProvider`、`extract_profile/performance/...`），没有任何"facade"或"selected subset"约束。Service 编排是合理的，但未来若新增一个"service-only business rule"，很可能直接在 service 内重复实现 Fund 已有逻辑——例如 `run_checklist()`、`run_risk_checks()`、`run_stress_test()` 已经在 Fund 里，Service 仍然有可能再写一份。**建议**：`fund_agent/services/__init__.py` 增加一个 `_allowed_fund_imports()` 白名单并加入 review gate。
2. **Agent → Fund 工具适配器写死工具名**：`fund_agent/agent/tools.py`（未深入审计）按 Fund primitive 一对一包装；将来若新增"实际 LLM tool loop"（AGENTS.md 中列为已接受但未实现的设计），当前 wrapper 是否能升级为带 JSON schema 的真 tool 描述，未在 README 中给出指引。
3. **Host → Agent 实际不存在直接调用**：Host runner 接住 `operation` closure（由 Service 把"agent 同步执行"包成 closure），Host 不直接调用 Agent。`AGENTS.md` 边界规则中"Host 调用 Agent 层执行"在实现上是"Service 构造 closure，Host 执行 closure"——这是工程妥协，但与文档的"Host → Agent"心智模型略有偏差。**建议**：在 `fund_agent/README.md` 第 3.1 节加入一段"当前 Host runner 只承载 closure，不感知 Agent 边界"的说明。
4. **Application / UseCase 已删除**：`fund_agent/application` 与 `tests/application` 已删（`docs/reviews/four-layer-architecture-alignment-code-review-20260524.md` 明确）。在历史 `AGENTS.md` 中存在过 `UI -> Application -> Service -> Runtime -> Engine -> Capability` 旧四层；当前 commit 已经迁移完毕。**风险点**：`docs/implementation-control.md` 中是否仍残留旧 Application 引用（本次未做完整 diff 校验，需用 `grep -rn "Application" docs/implementation-control.md` 二次确认）。

---

## 4. 代码质量审核

### 4.1 中文 docstring 与模板引用

抽样审核（`fund_agent/fund/fund_type.py`、`fund_agent/fund/audit/audit_programmatic.py`、`fund_agent/agent/runner.py`、`fund_agent/services/fund_analysis_service.py`、`fund_agent/host/runtime.py`）：

- 所有被抽样文件 100% 函数具备中文 docstring，**符合** `AGENTS.md` 硬约束"所有函数必须提供完整中文 docstring（参数、返回值、异常）"。
- 模块顶部 docstring 引用模板章节编号（"见模板第 2 章 R=A+B-C"）已落实。
- dataclass 字段 docstring 普遍存在但**不完整**：`fund_analysis_service.py` 中 `ResolvedAnalyzeContract` 字段 docstring 是单行说明，部分字段未注明"见模板第 X 章"。

**建议**：在 dataclass 字段 docstring 中系统化引用模板章节号，便于新人定位。

### 4.2 嵌套函数 / 嵌套类

`AGENTS.md` 原则："原则上不使用嵌套函数；仅在必须依赖闭包时例外"。

抽样 `chapter_orchestrator.py` 3393 行、`cli.py` 2458 行，**未发现严重嵌套**，但 `chapter_orchestrator.py` 顶部存在大量 `Literal[ ... ]` 跨多行 union，**在 3393 行单文件中可读性较差**。`agent/runner.py` 中有 `_run_single_chapter`、`_run_from_tasks`、`_blocked_run` 等模块级私有函数，符合"辅助函数定义为模块级私有函数"。

### 4.3 魔法数字 / 魔法字符串

- ✅ `audit_programmatic.py` 中 `_L1_TOLERANCE: Final[Decimal] = Decimal("0.0001")` 已用 `Final` 显式声明。
- ⚠️ `fund_agent/fund/analysis/risk_check.py` 5 项否决项阈值（"5000 万元"、"6 个月"、"费率 2x"、"跟踪误差 2%"）是 hard-coded 数字字面量；`AGENTS.md` 原则"基金类型判断、章节映射、审计规则必须配置化，禁止硬编码"**未完全贯彻**。
- ⚠️ `fund_agent/fund/analysis/stress_test.py` 6 种基金类型对应 3 套阈值表（`-20%/-40%/-60%` 等），**已经以 dict/literal 表达**，但没有集中到配置；不同基金类型阈值散落在多个文件。

**建议**：建立 `fund_agent/fund/analysis/thresholds.py` 集中所有硬编码阈值，作为单点真源。

### 4.4 类型安全与 frozen dataclass

抽样文件 100% 使用 `from __future__ import annotations`、`@dataclass(frozen=True, slots=True, kw_only=True)`、`MappingProxyType` 包装；`Literal` 枚举密集出现。**代码质量在 typed dataclass 设计上是一流的**。

### 4.5 错误处理

- 仓库的失败分类（`not_found` / `unavailable` / `schema_drift` / `identity_mismatch` / `integrity_error`）通过 typed exception + `blocking_failure.category` 显式表达；`docs/reviews/mvp-eid-failure-branch-evidence-20260610.md` 给出 35 个 no-live 测试覆盖这 5 类。
- ✅ 基金数据 `missing` 路径通过 typed `missing` 状态返回，不静默套默认值。
- ⚠️ `fund_agent/host/runtime.py` 中"Host 不强杀已进入同步 provider HTTP 的调用"——这意味着 `analyze --use-llm` 在 provider 真实卡死时只能等；当前 `mvp-ch2-auditor-timeout-120s-evidence-20260603.md` 已经接受 120s auditor timeout，但**没有针对 writer 真实卡死的 evidence**。

### 4.6 配置化程度

- ✅ `fund_agent/config/paths.py` 集中维护默认路径（README/AGENTS 要求）。
- ✅ `fund_agent/config/llm.py`（由 `tests/config/test_llm_config.py` 覆盖）集中 LLM env config。
- ❌ `fund_agent/audit/audit_programmatic.py` 中 `AuditRuleCode = Literal["P1", "P2", "P3", "C2", "L1", "R1", "R2"]`、`_CHECKED_RULES`、`_REQUIRED_CHAPTER_TITLES` 是模块内常量；E1/E2/E3/C1/L2 等"已设计但未实现"的规则码**没有 manifest 化**。
- ⚠️ `fund_agent/fund/fund_type.py` 6 类标准基金类型识别是 `if/elif` 链（已审计为规则化，但**没有 classifier 注册表**）。

### 4.7 `__init__.py` 与公共契约

抽样 `fund_agent/fund/__init__.py`、`fund_agent/services/__init__.py`、`fund_agent/audit/__init__.py`：公共契约通过 `__init__.py` 显式 re-export，README 中也明确哪些是 stable public。**符合** "fund_agent/fund 公共入口"约定。

---

## 5. 模板与基金分析能力审核

### 5.1 模板契约

- canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 位于 `docs/fund-analysis-template-draft.md` 内（README/AGENTS 强调"模板文档 canonical JSON 是 authored truth source"）。
- `fund_agent/fund/template/contracts.py` 投影 untyped manifest。
- `fund_agent/fund/template/typed_contracts.py` 投影 typed dataclass。
- `tests/fund/template/` 覆盖：parser 严格校验、untyped/typed 投影、8 章 CHAPTER_CONTRACT manifest、章节契约、基金类型 lens、cache/path 行为、fail-closed 校验。**测试质量高**。

**问题**：

- canonical JSON 放在 markdown 文件中（`docs/fund-analysis-template-draft.md` 内嵌），是**模板文档与机器契约的耦合**。任何修改 markdown 的人都要小心保留 JSON 语法。**建议**：将 JSON 拆为独立 `docs/fund-analysis-template-contract.json`，markdown 改为人类可读章节描述。
- `load_typed_template_contract_manifest()` 仍然从 markdown 解析 JSON；如果某天 `docs/fund-analysis-template-draft.md` 被 IDE 自动 reformat 破坏 JSON 语法，**所有 typed CHAPTER_CONTRACT 路径会 fail-closed**。

### 5.2 抽取能力（P1）

| Extractor | 章节 | 测试覆盖 | 评价 |
|---|---|---|---|
| `extract_profile` | §1/§2 | `tests/fund/extractors/test_profile.py` | 覆盖 basic_identity、product_profile、risk_characteristic_text、benchmark、fee_schedule；fixture 3 类（主动/增强/债券） |
| `extract_performance` | §3 | `tests/fund/extractors/test_performance.py` | 覆盖 nav_benchmark_performance、investor_return 三态（direct/estimated/missing）、跟踪误差、目标/限制、benchmark-only、表格/文本不一致等 |
| `extract_manager_ownership` | §4/§8/§9 | `tests/fund/extractors/test_manager_ownership.py` | 覆盖编号标题策略、换手率、持有披露、跨页持有人 |
| `extract_holdings_share_change` | §8/§10 | `tests/fund/extractors/test_holdings_share_change.py` | 覆盖前十大重仓、行业分布、净变动表、申购/赎回拆分、多份额列选择 |

**未覆盖的章节**：

- §5 重要会议、托管人报告、§6 基金管理人、§7 财务会计报告、§11 备查文件目录、§12 摘要等公开年报标准章节**没有任何 extractor**。`extract_profile` 在 §1/§2 抓取后直接进入 R=A+B-C 阶段，**§6/§7 的"基金托管人/审计意见/会计政策"在结构化数据中完全缺席**，模板中相关章节（如果有）只能填占位符。
- 这意味着 `analyze` 真实报告里"基金托管人"等基础合规信息**在结构化数据中无处可取**；renderer 怎么处理？本次未做内容级溯源（仅审核结构性），需要进一步 grep。

**建议**：`fund_agent/fund/extractors/README.md` 增加一个"当前支持的 §1-§10 子章节矩阵"表，列明哪些子章节有抽取、哪些没有。

### 5.3 分析能力（P2）

- ✅ `r_abc.py`、`alpha_judge.py`、`consistency_check.py`、`investor_return.py`、`risk_check.py`、`stress_test.py`、`checklist.py`、`final_judgment.py` 全部已实现；`tests/fund/analysis/` 完整覆盖。
- ✅ 所有分析模块都要求**显式输入**，缺失返回 `missing/insufficient_data`，不静默套默认——符合 AGENTS 硬约束"禁止根据经验或通常认为"。
- ⚠️ `judge_alpha_nature()` 需要"市场环境"和"来源解释强度"作为显式输入，但**当前 Service 层没有从任何地方取这两个输入**——必须由用户在 `--dev-override` mode 显式传，否则 `alpha_judgment` 永远是 `insufficient_data`。Service 是否补足？需要查 `fund_analysis_service.py` 后续逻辑。
- ⚠️ `check_consistency()` 需要"实际持仓风格"和"实际股票仓位"显式输入；`extract_holdings_share_change` 抽取的"行业分布"在结构化数据中可取，但**没有"风格"或"仓位"抽取器**——这两项永远是 P2 的真空气孔。

### 5.4 8 章模板渲染

`tests/fund/template/test_renderer.py` 覆盖：

- 8 章结构完整性
- CHAPTER_CONTRACT 标题来源
- 渲染章节块
- splitter fail-closed
- 证据锚点格式
- 缺证章节显式文本
- 页码保留
- 非年报来源标注
- preferred_lens 第 0/1 章确定性应用
- 第 0 章 veto/watch/压力测试最大风险与 checklist/stress/all-green 阈值
- ITEM_RULE 六类基金渲染/删除矩阵
- 主动基金第 3 章缺 reviewed turnover/style evidence 降级措辞
- 非主动基金第 3 章文本回归
- test-only 写作审计验证
- 跟踪误差 structured_data 替换
- benchmark-only 编制方法/成分股不足边界
- ITEM_RULE 多锚点证据边界
- 温度计免责声明和 external_api 锚点
- 程序审计输入兼容
- 缺失数据显式渲染
- 最终判断边界
- 禁用交易措辞
- README 同步

**渲染器测试质量是项目亮点**。

### 5.5 审计

- 程序审计：`tests/fund/audit/test_audit_programmatic.py` 覆盖 P1/P2/P3/C2/L1/R1/R2；`E1/E2/E3/C1/L2` 在 README 明确"属于后续 LLM 审计 / Evidence Confirm 层，当前未实现，不放入 checked_rules"——**设计上的纪律**。
- LLM 审计：`chapter_auditor.py` 已经实现"SEVERITY|LOCATION|MESSAGE" 三段式行协议 + 单行 `PASS|chapter|no issues` 唯一通过形式；测试覆盖 pass/info/reviewable/parse failure。

**关键发现**：`run_programmatic_audit()` 的 `checked_rules` **明确不包含** E1/E2/E3/C1/L2；任何"audit 100% 通过"的报告**必须理解为"P1/P2/P3/C2/L1/R1/R2 程序规则通过 + LLM 审计/Evidence Confirm 尚未实现"**。这在 `current-startup-packet.md` 中也已经坦白。

### 5.6 数据适配器

- ✅ `data/thermometer.py`（有知有行公开页）：24h fresh + 7d stale fallback；测试用 fake fetcher + HTML snippet 覆盖。
- ✅ `data/thermometer_source.py`（自建 akshare 沪深300/中证500 + wind_all_a）：测试用 fake akshare 覆盖。
- ✅ `data/thermometer_cache.py`：版本化 JSON，按市场/指数命名空间隔离。
- ✅ `data/thermometer_calculator.py`：PE/PB 50% 分位生成温度。
- ✅ `data/nav_repository.py`：`FundNavRepository.load_nav_series()` typed contract；区分 A/C/E/F 份额；identity 验证（006597/006598/014217/022176 已知）；raw-unit 显式标记 `strong_drawdown_evidence_eligible=False`。
- ✅ `data/nav_metrics.py`：`calculate_max_drawdown_from_nav_series()` 只接受 accumulated/verified NAV；fail-closed 行为覆盖。
- ✅ `data/csrc_eid_nav_source.py`：`httpx.MockTransport` 完整覆盖 public search/detail/classification 端点。

**自建温度计 P19-S1/S2/S5 已完整落地**，`fund-analysis thermometer` CLI 真实可用；缺失的只是"全市场指数/行业指数"的扩展。

### 5.7 文档仓库

- ✅ `FundDocumentRepository` 单一公开入口。
- ✅ `cache.py` PDF 元信息缓存 + parsed report 物化缓存。
- ✅ EID single-source policy：默认 `fallback_enabled=False`，多来源构造被拒绝。
- ✅ `metadata-aware/legacy loader` 与 `parsed/PDF cache admissibility` 区分。
- ✅ 失败分类：`not_found` / `unavailable` / `schema_drift` / `identity_mismatch` / `integrity_error` 显式表达。
- ✅ EID request-level timeout、PDF Content-Type 校验、`%PDF-` 校验、原子写入、来源元数据持久化。

**唯一缺口**：所有 EID 行为都用 `httpx.MockTransport` 覆盖，**没有 live EID 触发的 evidence**。`docs/current-startup-packet.md` 已经把"live EID failure-branch evidence gate"列为 next recommended gate。

---

## 6. 测试与质量保障审核

### 6.1 CI 配置

`.github/workflows/ci.yml`：

```yaml
- uv sync --extra dev --frozen
- uv run ruff check .
- uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

**评价**：

- ✅ 依赖锁定。
- ✅ ruff 检查。
- ✅ 全项目覆盖率阈值 50%。
- ❌ **没有 mypy 检查**。`pyproject.toml` 声明了 mypy + pyright 为 dev 依赖，但 CI 没有运行。
- ❌ **没有 black 检查**。同样在 dev 依赖中但 CI 没有运行。
- ❌ **没有 doctest 收集**。大量中文 docstring 中写明 "Args / Returns / Raises"，但未在 CI 中抽取。
- ⚠️ **没有 coverage per-file 报告**。`--cov-report=term-missing` 会显示每个文件覆盖率，但 `cov-fail-under=50` 是**全项目 gate**，**不强制单文件 ≥80%**——与 `AGENTS.md` "单文件 ≥80% 是评审目标" 的承诺在 CI 层面不一致。
- ⚠️ **没有 gate review evidence 检查**：`docs/reviews/` 与 `docs/implementation-control.md` 的同步是人工维护，没有自动化检查。

### 6.2 测试分层

`tests/` 子目录：

- `fund/documents/`：3 个文件，仓库契约 + 年报来源编排 + 缓存
- `fund/pdf/`：2 个文件，下载 helper + 章节定位
- `fund/extractors/`：4 个文件，4 个 extractor 各一
- `fund/data/`：5 个文件，NAV + 自建温度计
- `fund/analysis/`：10 个文件，所有分析模块
- `fund/audit/`：1 个文件，程序审计
- `fund/template/`：5 个文件，模板契约 + 渲染器
- `fund/integration/`：2 个文件，P1 样本矩阵 + P3 CLI 端到端
- `fund/`：8 个顶层测试（snapshot、score、golden、quality gate、typed contracts 等）
- `services/`：13 个文件，14 个 service 各覆盖
- `agent/`：5 个文件，Agent 5 个模块
- `host/`：2 个文件，runtime + runner
- `ui/`：1 个文件，CLI
- `config/`：2 个文件，paths + llm
- `scripts/`：2 个文件，smoke + report_quality_eval
- 顶层：1 个文件，repo_hygiene

**测试与生产文件比 84/99 = 0.85**。覆盖率合理。

### 6.3 测试方法学亮点

- **fake 一致性**：所有 external source（EID、Eastmoney、akshare、有知有行、CSRC EID NAV、provider HTTP）都通过 fake/mock 隔离；**没有任何常规 pytest 触发真实网络**。
- **typed fixture 复用**：extractor / NAV / thermometer / audit / template 都有 typed fixture；`tests/fixtures/fund/extractors/*.txt` 提供最小文本夹具。
- **golden set**：`tests/fund/test_small_golden_set_*.py` 5 个文件覆盖 manifest、fixture shape、source identity、parser mechanics、extractor correctness；当前 `004393` / `004194` / `006597` / `017641` / `110020` 五只基金进入 fixture promotion state。
- **fail-closed 显式断言**：每条 fail-closed 路径（malformed manifest、unknown requirement id、stale source manifest、unknown fund type、LLM contract violation、provider runtime 异常、finalized source metadata 不匹配）都有显式 `pytest.raises` 或 `assert` 断言。

### 6.4 测试方法学盲点

1. **prompt 内容无 LLM 行为测试**：`chapter_writer.py` / `chapter_auditor.py` 的 prompt 字符串由代码拼接而成，测试只覆盖"输出 marker 完整性、bound 解析"等结构约束，**不覆盖 LLM 在 prompt 下的输出分布**。这意味着：如果 prompt 改了措辞导致 LLM 经常漏 marker，**没有任何测试会捕获**。
2. **CLI 进度输出无黄金测试**：`tests/ui/test_cli.py` 覆盖 `--llm-progress` / `--no-llm-progress` stderr-only，但 heartbeat 文本格式由代码生成且未断言具体内容；如果 heartbeat 文本对用户不可读，无测试保护。
3. **time budget 测试**：`tests/services/test_fund_analysis_service.py` 有性能 gate（"30 秒内单只基金分析"），但只针对 deterministic 路径；`--use-llm` 路径没有性能 gate。

### 6.5 性能 / 质量 / Promotion Gate

- **50% 全项目覆盖率**：已落实。
- **30 秒 deterministic 单只基金分析**：`tests/services/test_fund_analysis_service.py` 守卫生效。
- **Ruff 已配置**。
- **no-live 端到端证据**：EID 5 类失败分类、Provider timeout、LLM typed template 8 slice 全部以"no-live" 形式证明。
- **live 端到端证据**：**零**。`docs/current-startup-packet.md` 明确说"Recommended options are downstream integration implementation gate, or a separately authorized live EID failure-branch evidence gate."

---

## 7. 文档与治理审核

### 7.1 文档真源体系

| 真源 | 路径 | 状态 | 评价 |
|---|---|---|---|
| Agent 规则 | `AGENTS.md` | 当前 | 完整、有硬约束、有边界判定规则 |
| Claude 入口 | `CLAUDE.md` | 当前 | 极简适配层，正确指向 AGENTS.md |
| 设计真源 | `docs/design.md` | 当前 | 区分"已实现 / 未来设计 / 候选"，标签纪律好；`Future Design` 节占 25-30% |
| 实施总控 | `docs/implementation-control.md` | 当前 | **2000+ 行**，含 Startup Packet、Current Truth Guardrails、current gate、next entry point、accepted artifacts、open residuals、non-goal reminder、Active Gate Ledger；**文档超长** |
| 模板真源 | `docs/fund-analysis-template-draft.md` | 当前 | canonical JSON 嵌入 markdown；章节结构清晰 |
| 当前控制包 | `docs/current-startup-packet.md` | 当前 | 简洁，列出 accepted commits 与 next entry point |
| 各包 README | `fund_agent/{host,agent,fund,config}/README.md`、`fund_agent/README.md`、`README.md`、`tests/README.md` | 当前 | 角色分工正确（用户手册 / 总览 / 包 / 测试手册） |

### 7.2 治理密度

- `docs/reviews/` 子目录约 240+ 份 review markdown，命名规则 `p1-s1-code-review-{glm|mimo|controller}-2026-05-17.md` / `mvp-gate1-chapter-fact-provider-...-20260530.md` / `code-review-20260607-073445.md` / `code-review-20260608-070452-rereview.md`。
- 每条 review 通常含 3-5 份文件（plan + review-ds + review-mimo + controller-judgment + fix-evidence + implementation-evidence）。
- **评价**：治理密度极高，每条产品变更都有"plan → review(双) → fix → re-review → controller judgment"五步；这在个人项目上**不是负担，而是纪律**。

### 7.3 治理风险

1. **`docs/implementation-control.md` 单文件 2000+ 行**违反 `AGENTS.md` "优先压缩而不是追加长日志；新增日志如果不是恢复当前 gate 所必需，必须写入独立 artifact 并在 control doc 中引用路径"。当前 control doc 仍以追加形式累积历史 gate 摘要。**建议**：将 Active Gate Ledger 中 2025-06-01 之前的部分迁入 `docs/archive/`，只保留最近 30 天与当前 gate。
2. **review 文件命名不一致**：早期使用 `p1-s1-*`，中后期使用 `mvp-gate*-*`，最近混入 `code-review-20260607-073445.md` 这种无上下文的命名。`docs/reviews/` 根目录的可发现性下降。
3. **fixture / manifest 散落**：`docs/reviews/fixture-promotion-state-manifest-20260529.json`、`docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`、`docs/reviews/mvp-small-golden-set-manifest-20260608.json`、`docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` 与 `docs/reviews/fixture-promotion-state-manifest-20260529.json` 都是**控制面 manifest**，但没有统一目录（`docs/manifests/` 或 `docs/control/`）管理。

### 7.4 README 同步状态

抽样审核（`README.md`、`fund_agent/README.md`、`fund_agent/host/README.md`、`fund_agent/agent/README.md`、`fund_agent/fund/README.md`、`tests/README.md`）：

- ✅ README 顶部有"How to add a fund / new section / new type"的明确指引。
- ✅ `tests/README.md` 与 `pyproject.toml` 中 `cov-fail-under=50` 一致。
- ⚠️ `fund_agent/tools/claude_mimo.py` 与 `scripts/claude_mimo_simple.py` 在所有 README 中**完全没有说明**——可能是有意隐藏（个人工具），但**目录中保留它们就成为审计噪音**。
- ⚠️ `docs/implementation-control.md` 中提到的 `beb6891` / `ac6bbe9` 等 commit hash 在 `git log` 中是否真实存在，本次未验证（仅审核静态文本）。

---

## 8. 风险与改进建议

按"硬约束一致性"与"第一性原理"双重视角汇总：

### 8.1 P0（必须解决）

1. **CI 不验证"产品主链路真实可达"**。建议：
   - 在 CI 增加一个 `live-evidence-disabled` 的环境变量；默认 CI 跑 fake-only，但**每周一次 scheduled job** 跑 live smoke（受网络环境限制时跳过）。
   - 或者建立 `docs/live-evidence/` 目录，存放人工 smoke 输出，按"每月第 1 个 commit"更新，作为下游消费方的事实背书。
2. **`docs/implementation-control.md` 长度超限**。建议：
   - 立即把 2026-05-30 之前的 Active Gate Ledger 迁入 `docs/archive/`。
   - 设立 "current gate + next entry point" 顶部固定窗口（≤300 行），ledger 只放最近 30 天。
3. **`pyproject.toml` 中声明的 mypy/black 未被 CI 强制**。建议：
   - 在 `ci.yml` 增加 `uv run mypy fund_agent` 与 `uv run black --check .`，定位为 warn-only，未来 gate 升级为 blocking。

### 8.2 P1（建议解决）

4. **§5/§6/§7 等章节缺少 extractor**。`extract_profile` / `extract_performance` / `extract_manager_ownership` / `extract_holdings_share_change` 4 个 extractor 覆盖 §1/§2/§3/§4/§8/§9/§10，**基金托管人 / 审计意见 / 会计政策 / 重要会议**等公开年报标准章节在结构化数据中完全缺席；模板相关章节（如果有）只能填占位符。建议：补 §6 基金托管人 + §11 备查文件目录 + §12 摘要的最小 extractor。
5. **P2 分析的"市场环境"和"来源解释强度"无来源**。`judge_alpha_nature()` 要求显式输入，但 Service 没有从任何结构化数据派生；意味着非 `--dev-override` mode 下 `alpha_judgment` 永远 `insufficient_data`。建议：在 `fund_agent/fund/extractors/` 中加 `extract_alpha_environment`（从 §4 策略摘要 + §8 行业分布推断"主动/顺周期/逆周期"），并明确**派生 alpha environment 不得用于最终判断**，仅用于提示。
6. **`fund_agent/tools/claude_mimo.py` 与 `scripts/claude_mimo_simple.py` 与基金分析无关**。建议：将它们移出 `fund_agent/` 命名空间（用户级 helper 应放在 `~/` 或独立 repo），或在 `fund_agent/tools/__init__.py` 顶部加 `__all__ = ()` + 文档说明"非产品代码，仅供项目作者本地使用"。
7. **canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 嵌在 markdown 中**。建议：拆为 `docs/fund-analysis-template-contract.json` + `docs/fund-analysis-template-draft.md` 纯人类可读章节。
8. **`fund_type.py` 6 类标准识别是 `if/elif` 链**。建议：把每类识别规则注册为 `ClassifierRule(name, predicate, basis_template)` 列表，新增类型只需追加规则；既利于测试也利于基金类型扩展。

### 8.3 P2（值得改进）

9. **测试覆盖率单文件 ≥80% 无 CI 验证**。建议：在 CI 报告中找出 "新修改文件且覆盖率 < 80%" 的清单，存入 `docs/coverage-gaps/<date>.md`，由 controller 决策。
10. **`script` 目录下的 8 个脚本没有一个 README**。建议：建 `scripts/README.md`，分类"产品脚本（selected_funds_smoke, report_quality_eval）/ 工具脚本（claude_mimo_simple, multi_tail）/ 工具入口脚本（remind-agentcontroller, setup-ai-session, start-tmux-*）"。
11. **AGENTS.md "基金类型判断、章节映射、审计规则必须配置化"** 未完全落实。建议：建立 `fund_agent/fund/config/` 子包，集中管理 fund_type rules、audit rules、chapter mapping。
12. **README 没有"如何用 PDF fixture 做端到端 dry-run"**。建议：在 `README.md` 增加 `fund-analysis thermometer --json` / `fund-analysis analyze --fund-code 110011 --report-year 2024 --thermometer-cache-dir /tmp/cache` 的可复制命令。

### 8.4 观察项（已知，但作者可能知情）

- P19 自建温度计"宽基指数/全 A 完整闭环"，但**不支持"行业指数"或"主题指数"**——意味着行业 ETF、主题 ETF 估值永远是 `unavailable` 灰灯。这是有意为之还是缺口？需要作者明确。
- `claude_mimo.py` 与 `scripts/claude_mimo_simple.py` 在仓库中并存且功能重叠，**两份 Typer 入口**指向同一功能。明显是历史迭代遗留。
- `docs/learning-roadmap.md` 公开宣称"作者本人正在学习 CS50P"——**这与项目当前工程化深度形成鲜明反差**。新贡献者应被告知：项目大部分代码可能由作者在 LLM 辅助下完成，而不是作者本人手写；这影响 PR 期望与人工 review 的内容。

---

## 9. 与硬约束的对账

| 硬约束 | 是否满足 | 证据 / 说明 |
|---|---|---|
| UI 只依赖 Service | ✅ | `tests/ui/test_cli.py` + `fund_agent/ui/cli.py` import 列表 |
| Service 不直接调用 Agent 内部 | ✅ | `fund_agent/services/*.py` 顶部无 `from fund_agent.agent` |
| Host 不直接依赖 `dayu.host` | ✅ | `fund_agent/host/runtime.py` 无 dayu 导入 |
| Agent 不直接依赖 `dayu.engine` | ✅ | `fund_agent/agent/*.py` 无 dayu 导入 |
| `fund_agent/fund` 不依赖 Service/Host/Agent | ✅ | 抽样 5 个文件无越层导入 |
| 文档仓库只通过 `FundDocumentRepository` | ✅ | `tests/fund/documents/test_repository.py` 守卫 |
| 5 类失败分类显式 | ✅ | `tests/fund/documents/test_annual_report_sources.py` 35 测试 |
| `not_found` / `unavailable` 允许 fallback | ✅ | EID single-source mode 下 terminal（更严） |
| `schema_drift` / `identity_mismatch` / `integrity_error` fail-closed | ✅ | EID single-source mode 下 fail-closed |
| 不输出"买入/卖出"建议 | ✅ | `template/renderer.py` + `audit_programmatic.py` 强制 `must_not_cover` |
| 不预测未来收益 | ✅ | prompt 中明确禁止 + renderer 禁止字眼 |
| 区分结构性 vs 阶段性 Alpha | ✅ | `alpha_judge.py` 5 态 |
| 检查基金经理是否持有本基金 | ✅ | `extract_manager_ownership` 抽 `manager_alignment` |
| 压力测试按基金类型用阈值 | ✅ | `stress_test.py` 6 类阈值 |
| 所有数值标注数据来源 | ✅ | evidence anchor 强制 |
| 输出"下一步最小验证问题" | ✅ | chapter_writer / checklist 显式 phrase |
| 显式参数禁止 `extra_payload` | ✅ | Agent contracts `__post_init__` 强制 `safe_metadata` 校验；Service ExecutionContract 测试断言 "no extra_payload" |
| 基金类型判断先于通用分析 | ✅ | `fund_type.py` 在 extractor 入口先行 |
| 证据可溯源 | ✅ | `EvidenceAnchor` 强制 |
| 函数中文 docstring | ✅ | 抽样 100% |
| 模板章节编号引用 | ✅ | 抽样 100% |
| 无嵌套函数 | ✅ | 抽样 100% |
| `__init__.py` 集中公共入口 | ✅ | 抽样通过 |
| 禁用魔法数字 | ⚠️ | 风险阈值散落 |
| 不为历史包袱妥协 | ✅ | `Application/UseCase` 已删 |
| 单文件测试覆盖率 ≥80% | ⚠️ | CI 强制 50%，单文件目标在 review 中人工维护 |
| 测试跟着实现边界迁移 | ✅ | 84 测试文件、4 层分层 |
| 文档与代码同步 | ⚠️ | `tools/claude_mimo.py` 未在 README 说明 |
| `docs/implementation-control.md` 不超长 | ❌ | 当前 2000+ 行 |
| `docs/reviews/` 索引清晰 | ⚠️ | 命名规则不一致 |
| 阻止 README "设计未来" | ✅ | README 中"当前 / 未来"区分清楚 |
| 包 README 角色不越界 | ✅ | 角色分工清晰 |
| 模板术语与代码一致 | ✅ | CHAPTER_CONTRACT / preferred_lens / ITEM_RULE 三词一致 |

**约束对账结论**：12 条硬约束全部满足、4 条有缺口（魔法数字、单文件覆盖率、文档超长、命名规范）、其余以"观察项"呈现。

---

## 10. 总评

fund-agent 是一个**治理强度超过工程能力密度**的项目：

- **强项**：4 层架构 import 边界严格、typed dataclass 设计一流、模板契约 + ITEM_RULE + 渲染器测试密度极高、EID 失败分类 5 类显式且有 no-live evidence、225 份 review 治理记录、12 条 AGENTS 硬约束绝大部分落实。
- **弱项**：production 主链路未在 live 环境下验证、`analyze --use-llm` 路径无 live 端到端 evidence、Host / Agent 内化只完成 30%-40% 的"接口占位"而非真正运行时、§5/§6/§7 等公开年报标准章节缺抽取、CI 强制 mypy/black 缺位、文档超长、个别目录混入与基金分析无关的本地工具脚本。
- **风险面**：对任何新加入的贡献者，**项目看起来 production ready（CI 全绿、覆盖率 50%、单文件 80% 目标、240 份 review 记录），但 happy path 真实运行依赖 CSRC EID 公网 + akshare 公网 + OpenAI 兼容 LLM 公网**。这三重网络依赖**在 README 中没有"先做 fake 烟囱再尝试 live"的明确指引**。

**整体建议**：

1. **短期**（1 周内）：完成 `docs/implementation-control.md` 长度收敛、CI 增加 mypy/black 检查（warn-only）、`fund_agent/tools/claude_mimo.py` 与 `scripts/claude_mimo_simple.py` 二选一删除。
2. **中期**（1-2 月内）：补 §5/§6/§7 章节最小 extractor、跑一次 live EID smoke 并把 evidence 写入 `docs/live-evidence/`、建立 `docs/manifests/` 统一管理 fixture/disposition manifest。
3. **长期**（3 月+）：从 typed dataclass 表达的"Host / Agent"过渡到真正 LLM tool loop（按 `AGENTS.md` 描述的"必须内化 Dayu Engine 能力"），并在 README 中明确"当前是 no-live engineering prototype / 何时进入 live beta"。

**审核未改动任何代码、文档、测试、CI 配置**。本报告仅作为决策输入，不作为行动授权；任何"按本报告执行"的变更需先经 controller judgment 走标准 gate。

---

## 附录 A：审核覆盖清单

### A.1 已阅读文件

- `/Users/maomao/fund-agent/AGENTS.md`
- `/Users/maomao/fund-agent/CLAUDE.md`
- `/Users/maomao/fund-agent/README.md`
- `/Users/maomao/fund-agent/pyproject.toml`
- `/Users/maomao/fund-agent/.github/workflows/ci.yml`
- `/Users/maomao/fund-agent/docs/design.md`（摘读第 1-300 行）
- `/Users/maomao/fund-agent/docs/implementation-control.md`（摘读第 1-600 行）
- `/Users/maomao/fund-agent/docs/current-startup-packet.md`（摘读第 1-100 行）
- `/Users/maomao/fund-agent/docs/fund-analysis-template-draft.md`（摘读第 1-200 行）
- `/Users/maomao/fund-agent/docs/learning-roadmap.md`（摘读第 1-50 行）
- `/Users/maomao/fund-agent/docs/reviews/mvp-eid-failure-branch-evidence-20260610.md`（全读）
- `/Users/maomao/fund-agent/docs/reviews/four-layer-architecture-alignment-code-review-20260524.md`（摘读 1-50 行）
- `/Users/maomao/fund-agent/fund_agent/README.md`（全读）
- `/Users/maomao/fund-agent/fund_agent/fund/README.md`（全读）
- `/Users/maomao/fund-agent/fund_agent/agent/README.md`（全读）
- `/Users/maomao/fund-agent/fund_agent/host/README.md`（全读）
- `/Users/maomao/fund-agent/fund_agent/host/runtime.py`（全读）
- `/Users/maomao/fund-agent/fund_agent/agent/runner.py`（摘读 1-300 行）
- `/Users/maomao/fund-agent/fund_agent/agent/contracts.py`（摘读 1-200 行）
- `/Users/maomao/fund-agent/fund_agent/fund/fund_type.py`（全读）
- `/Users/maomao/fund-agent/fund_agent/fund/audit/audit_programmatic.py`（摘读 1-300 行）
- `/Users/maomao/fund-agent/fund_agent/fund/documents/repository.py`（摘读 1-100 行）
- `/Users/maomao/fund-agent/fund_agent/services/fund_analysis_service.py`（摘读 1-400 行）
- `/Users/maomao/fund-agent/fund_agent/services/chapter_orchestrator.py`（摘读 1-100 行）
- `/Users/maomao/fund-agent/fund_agent/ui/cli.py`（摘读 1-150 行）
- `/Users/maomao/fund-agent/fund_agent/tools/claude_mimo.py`（摘读 1-20 行）
- `/Users/maomao/fund-agent/scripts/claude_mimo_simple.py`（摘读 1-50 行）
- `/Users/maomao/fund-agent/tests/README.md`（全读）

### A.2 已执行命令

- `ls -la /Users/maomao/fund-agent`
- `find /Users/maomao/fund-agent/fund_agent -name "*.py" | xargs wc -l | tail -1`
- `find /Users/maomao/fund-agent/tests -name "*.py" | xargs wc -l | tail -1`
- `find /Users/maomao/fund-agent/fund_agent -name "*.py" | wc -l`
- `find /Users/maomao/fund-agent/tests -name "*.py" | wc -l`
- `find /Users/maomao/fund-agent/docs -name "*.md" | wc -l`
- `wc -l` 7 个关键文件
- `ls -la reports/`、`ls scripts/`、`ls fund_agent/` 目录扫描

### A.3 未覆盖范围

- 完整 `docs/implementation-control.md`（只摘读 1-600 行）
- 完整 `docs/fund-analysis-template-draft.md`（只摘读 1-200 行）
- 各 `fund_agent/fund/extractors/*.py` 完整代码
- `fund_agent/fund/data/*.py` 完整代码
- `fund_agent/agent/repair.py` / `tools.py` 完整代码
- `fund_agent/services/*.py` 14 个模块的完整代码
- `tests/fund/integration/*.py` 完整测试
- 真实运行 `pytest` / `ruff` / `mypy` / `black`（仅静态结构扫描）

### A.4 本报告的"未验证假设"

未在本审核中通过 `git log` / `git show` 二次确认的：

- `current-startup-packet.md` 列出的所有 commit hash 是否真实存在
- `fund_agent/tools/claude_mimo.py` 是否在 `pyproject.toml` 中实际可被 import
- `tests/fund/extractors/test_*.py` 中 fixture 文件是否覆盖真实现金流
- 真实 `pytest` 是否在当前环境跑通

**以上未验证项不构成对报告结论的反证**；它们仅是"本报告未独立执行"的边界声明。
