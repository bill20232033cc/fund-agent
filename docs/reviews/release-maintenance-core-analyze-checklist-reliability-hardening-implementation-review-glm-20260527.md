# Code Review

## Scope

- Mode: current changes（Gate 2 implementation review）
- Branch: `codex/local-reconciliation`
- Base: `20f5814`
- Output file: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-implementation-review-glm-20260527.md`
- Included scope: 12 个已修改/新增文件，覆盖 Slice 1（NAV 降级）、Slice 2（command_source run_id）、Slice 3（turnover 回归锁定），以及 `quality_gate.py`、`r_abc.py`、renderer/template、host/agent 的 diff-verified 未修改确认
- Excluded scope: `tests/fund/integration/`、`tests/fund/template/`、`tests/fund/analysis/` 未随本轮改动，不在 review scope 内
- Parallel review coverage: 无 subagent；全部证据由主 reviewer 直接从代码路径和 git diff 提取
- Accepted plan: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md`
- Evidence: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-implementation-evidence-20260527.md`

## Adversarial Review Focus

逐条回答 review 请求中的六个 adversarial focus：

### Q1: NAV provider/cache/akshare 失败是否仍阻断 analyze/checklist annual-report 主路径？

**结论：否。**

- `data_extractor.py:165-169`：`report = await self._repository.load_annual_report(...)` 在 NAV 调用之前执行，且不在任何 try/except 内。
- `data_extractor.py:170-174`：NAV 调用被 `_load_nav_data_or_unavailable()` 包裹，该 helper 在 `except Exception` 时返回 `unavailable_nav_data_result()`。
- `data_extractor.py:175-178`：profile/performance/manager/holdings extractor 在 NAV 之后执行，NAV 失败不阻断。
- `test_data_extractor.py:131-158`：fake repository 返回年报 + fake nav provider 抛 `RuntimeError`，断言抽取成功、年报字段填充、`nav_data.unavailable is True`。

### Q2: repository/PDF identity/integrity/schema 失败是否被 NAV 降级误吞？

**结论：否。**

- `data_extractor.py:165-169`：repository 调用在 NAV try/except 之外。repository 异常直接向上传播。
- `test_data_extractor.py:162-183`：fake repository 抛 `RuntimeError("identity_mismatch fixture")`，断言异常传播且 NAV provider 未被调用（`nav_provider.calls == []`）。
- 任何 repository 异常类型（包括 `schema_drift`、`identity_mismatch`、`integrity_error` 风格的异常）都会传播，因为 catch 边界只包裹 `nav_provider.load_nav_data(...)` 单次调用。

### Q3: NavDataResult 新字段或 command_source 是否引入向后兼容问题？

**结论：否。**

- `NavDataResult` 新增 `unavailable: bool = False` 和 `unavailable_reason: str | None = None`，均有默认值。已验证所有 12 处 `NavDataResult()` 构造点（`nav_data.py:149, 251, 260` 及 9 个测试文件）均未传入新字段，默认值正确生效。
- `FundAnalysisRequest` 新增 `command_source: AnalyzeCommandSource = "analyze"`，默认 `"analyze"` 与旧行为一致（旧 `_default_quality_gate_run_id` 固定 `"analyze-"` 前缀）。
- 生产代码中仅 `cli.py:210` 和 `cli.py:290` 构造 `FundAnalysisRequest`，两处均已显式传入 `command_source`。
- `AnalyzeCommandSource` 为模块级 `Literal` 类型，不从 `__init__.py` 导出，使用范围限于 service 模块和测试，不影响外部契约。

### Q4: checklist run_id 前缀变化是否改变了 FQ0-FQ6 policy/result 语义？

**结论：否。**

- `git diff HEAD -- fund_agent/fund/quality_gate.py`：无输出，FQ0-FQ6 规则代码未修改。
- 唯一变化是 `_default_quality_gate_run_id()` 返回值从 `"analyze-..."` 变为 `"{command_source}-..."`。这仅影响 run_id 命名和输出目录名称，不影响 quality gate 的 block/warn/info 判定逻辑。
- 显式 `quality_gate_run_id` 保持权威，不被覆盖。`_run_quality_gate_if_enabled` 中 `resolved_contract.quality_gate_run_id or _default_quality_gate_run_id(...)` 的短路逻辑确认显式值优先。

### Q5: turnover 回归测试是否证明 standalone missing turnover 是 warn，且 aggregate FQ4 不受影响？

**结论：是。**

- `test_quality_gate.py:93-152`（`test_run_quality_gate_warns_turnover_only_p1_failure_without_fq4`）：构造仅 `turnover_rate` P1 fail 的 score，断言 `status == warn`、包含 FQ2/warn 和 FQ2F/warn、无 block issue、无 FQ4 issue。
- `test_fund_analysis_service.py:1280+`（`test_fund_analysis_service_pre_2026_missing_turnover_is_warn_not_standalone_block`）：Service 层集成测试，构造 2024 缺失 `turnover_rate` 的 bundle，断言 `rabc_attribution.status == "missing"`、note 包含 "缺少 §8 换手率"、quality gate warn 且无 FQ4。
- 测试正确隔离了 turnover-only 场景（其他字段全部 present），证明单字段缺失不会触发 FQ4 aggregate block。多字段同时缺失仍可能触发 FQ4，这是设计的 aggregate data-quality 机制，不在本 gate 修改范围。
- FQ4 规则代码完全未修改（`git diff HEAD -- fund_agent/fund/quality_gate.py` 无输出）。

### Q6: Docs/tests 是否与 AGENTS.md 对齐；有无 renderer/Host/Agent/dayu/source-helper/durable fixture/GitHub mutation？

**结论：对齐，无禁止改动。**

- `git diff HEAD -- fund_agent/fund/template/`：无输出，renderer/Chapter 3 未修改。
- `git diff HEAD -- fund_agent/host/ fund_agent/agent/`：无输出，Host/Agent/dayu 未修改。
- `FundDocumentRepository`、PDF adapter、source helper 文件均不在 changed files 列表中。
- `fund_agent/fund/README.md` 更新了 NAV 降级行为描述，符合 AGENTS.md 触发规则（`fund_agent/fund/` 修改 → 更新 `fund_agent/fund/README.md`）。
- `tests/README.md` 更新了新增 `tests/fund/test_data_extractor.py` 条目，符合 AGENTS.md 触发规则（`tests/` 修改 → 更新 `tests/README.md`）。
- 未更新根 `README.md`（无 CLI flags/user workflow 变化）、`fund_agent/README.md`（未枚举 `FundAnalysisRequest` 字段集）、`docs/design.md`（未超出当前设计边界），符合 plan documentation decision。
- 无 commit、push、PR、merge、approval 或 GitHub mutation。

## Findings

未发现实质性问题。

实现忠实地遵循了 accepted plan 的三个 slice：

1. **Slice 1 NAV 降级**：catch 边界精确限定在 `nav_provider.load_nav_data(...)` 单次调用，repository/PDF 失败在 catch 边界之外，fail-closed policy 完整保留。`NavDataResult` 新增可选字段有正确默认值，所有现有构造点兼容。

2. **Slice 2 command_source run_id**：`AnalyzeCommandSource` 作为显式 `Literal` 类型定义在请求 dataclass 上，Service 方法通过 `dataclasses.replace()` 做权威覆盖，CLI 显式构造仅为可观测性。显式 `quality_gate_run_id` 保持权威不被覆盖。FQ0-FQ6 规则代码零修改。

3. **Slice 3 turnover 回归**：无生产代码修改，通过单元测试和 Service 集成测试锁定 missing `turnover_rate` 的 warn 语义。测试正确隔离了 turnover-only 场景，FQ4 aggregate block 语义未被弱化。

## Open Questions

- 无。

## Residual Risk

- **NAV broad catch 的编程错误风险**：`except Exception` 会吞掉 NAV provider 编程错误（如 `TypeError`、`AttributeError`），将其转为 unavailable data。这是 plan 明确接受的 tradeoff，`unavailable_reason` 包含异常类型和消息可辅助诊断。风险可接受。
- **空 NAV records 对 P2 信号的影响**：NAV 不可用时 `records=[]` 会增加 snapshot/score 中 `nav_data` 的 missing 信号。`nav_data` 是 P2 字段，plan 明确接受此影响，因为 gate 目标是年报主路径连续性。
- **NAV 异常类型的测试覆盖**：`test_data_extractor.py` 仅使用 `RuntimeError` 模拟 NAV 失败。`sqlite3.Error`、`ImportError`、`AttributeError` 等实际生产异常类型未在 extractor 测试中逐一覆盖。但 catch 使用 `except Exception` 涵盖所有这些类型，且 adapter 层（`test_nav_data.py`）已有 cache/fetcher 行为测试。风险低。
- **turnover 在多字段缺失场景仍可能贡献 FQ4**：plan 和 evidence 均已记录此 residual。若未来出现 aggregate FQ4 false blocker，应作为独立的 field-applicability 设计 gate 处理，不在本 gate scope 内。

## Reviewer Self-Check

- review mode（current changes）、base（`20f5814`）、included/excluded scope、source evidence 已写清。
- 每个 adversarial focus 均绑定到具体 code location 和 explicit behavior，root cause 使用直接证据（git diff、代码行号、测试断言）。
- findings 为空（"未发现实质性问题"），无 style/nit/speculation。
- adversarial pass 覆盖了全部六个 review focus，open questions 和 residual risk 已记录。
- output path 为 `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-implementation-review-glm-20260527.md`。

## Verdict

**PASS**
