# Implementation Plan Review: CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit

> Date: 2026-05-26
> Reviewer: AgentGLM
> Review target: `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md`
> Truth sources: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted design plan (`docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md`), controller judgment (`docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-controller-judgment-20260526.md`)

## Evidence Checked

| Evidence | Source | Verified |
|---|---|---|
| `ChapterContract` frozen/slots, 7 fields (chapter_id, title, narrative_mode, must_answer, must_not_cover, required_output_items, preferred_lens) | `fund_agent/fund/template/contracts.py` | Yes |
| `load_template_contract_manifest()` no-param returns `TemplateContractManifest` | `fund_agent/fund/template/contracts.py` | Yes |
| `ReportEvidenceBundle` frozen/slots, 18 fields including facts, data_gaps, score_issue_links | `fund_agent/fund/report_evidence.py` | Yes |
| `ReportDataGap.required_report_wording: str` required field, frozen/slots | `fund_agent/fund/report_evidence.py` | Yes |
| `ReportDataGapOverride.required_report_wording: str` required field, frozen/slots | `fund_agent/fund/report_evidence.py` | Yes |
| `FundType = Literal["index_fund", "active_fund", "bond_fund", "enhanced_index", "qdii_fund", "fof_fund"]` | `fund_agent/fund/fund_type.py` | Yes |
| `validate_report_quality_bundle()` / `validate_report_quality_jsonl()` public API | `fund_agent/fund/report_quality_validation.py` | Yes |
| Controller judgment fixes audit module path to `fund_agent/fund/report_writing_audit.py` | Controller judgment §Review Findings | Yes |
| Controller judgment stores new fields in sidecar, does not mutate `ChapterContract` | Controller judgment §Gate B | Yes |
| Controller judgment limits Chapter 2/6 to informational/config until extraction gates supply reviewed evidence | Controller judgment §Gate B | Yes |
| Accepted design plan §2.3 Chapter 3 active must not claim stability without reviewed turnover/style-change evidence | Design plan §2.3 | Yes |
| `AGENTS.md` §硬约束: CHAPTER_CONTRACT sidecar must be wrapper over existing `ChapterContract`, not replacement | `AGENTS.md` lines 95-107 | Yes |
| `AGENTS.md` §模块边界: CHAPTER_CONTRACT 解析 goes in `fund_agent/fund` Agent layer | `AGENTS.md` lines 125-133 | Yes |
| `AGENTS.md` §测试策略: 单文件 >=80% coverage target | `AGENTS.md` lines 170-172 | Yes |

## Findings

### F1 (Minor) — `FailureBehavior` vs `RequirementSeverity` 命名不一致

**Severity**: Minor

Plan §2.2 的 `ChapterExecutableConstraint` 表格中 `failure_behavior` 字段类型标注为 `FailureBehavior`，但建议的 Literal 类型定义使用名称 `RequirementSeverity`。两个名称语义相同（值域均为 `"blocking", "material", "informational", "config_only"`），但 plan 未明确声明 `FailureBehavior` 就是 `RequirementSeverity` 的别名，或是否为独立类型。

**Why it matters**: 编码 worker 需要决定统一使用哪个名称，或显式定义别名关系。若不一致选择，可能在 dataclass 和函数签名间产生命名碎片。

**Suggested resolution**: 编码 worker 应将 `FailureBehavior` 定义为 `RequirementSeverity` 的别名（`FailureBehavior = RequirementSeverity`），或在 dataclass 字段中直接使用 `RequirementSeverity`。不应出现两个独立 Literal 声明同一值域。

### F2 (Minor) — JSONL 输入记录结构未约定

**Severity**: Minor

Plan §3.2 定义 JSONL 输入为 `Iterable[Mapping[str, object]]` 或显式 parsed records，但未约定记录期望的 key 结构。dev-only audit 的 JSONL 消费路径可能接收 bundle records 和 score_issue records，编码 worker 需要从调用方推断结构。

**Why it matters**: dev-only 场景下这是可接受的灵活度，但如果两个 coder 各自假定不同结构，可能产出不一致的 record 解析逻辑。

**Suggested resolution**: 编码 worker 应在 `audit_report_writing_records` docstring 中注明期望至少包含 `fund_code`、`report_year`、`classified_fund_type` 和 chapter-level fact/gap 摘要结构，或显式声明"records 的结构由调用方保证，本函数不做 schema 校验"。

### F3 (Informational) — `ChapterDraftSurrogate.fund_type_slot` 类型简化

Plan §3.2 的 `ChapterDraftSurrogate.fund_type_slot` 使用 `FundType | Literal["default", "unknown"]`，而 `ReportEvidenceBundle.classified_fund_type` 使用更具体的 `ClassifiedFundType`。这是 surrogate 的有意简化（surrogate 不是 production 路径），但编码 worker 需要注意从 bundle 构建 surrogate 时的类型映射。

**Assessment**: 可接受。surrogate 明确定义为 dev-only 测试辅助，不进入 production 消费路径。

### F4 (Informational) — 中文 docstring 约束隐式依赖 AGENTS.md

Plan §2.2 提到 dataclass 应有 Chinese docstrings，但未在 §3.4 公共 API 或 §5 测试策略中显式重申 AGENTS.md 的"所有函数必须提供完整中文 docstring"要求。编码 worker 已被要求先读取 AGENTS.md（plan §0），因此该约束是隐式生效的。

**Assessment**: 可接受。AGENTS.md 是必读文件，plan §0 已声明作为依据。

### F5 (Informational) — boundary rg 缺少 `quality_gate_policy` 模式

Plan §6 的 boundary rg 命令 grep 模式为 `dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|FQ0|FQ6|renderer|FundAnalysisService`。Stop condition §7 提到"Tests require wiring findings into FQ0-FQ6 or `quality_gate_policy`"，但 rg 模式未包含 `quality_gate_policy`。

**Assessment**: 极低风险。`quality_gate` 已在 grep 模式中，足以捕获对 quality gate policy 模块的引用。`quality_gate_policy` 作为 `QualityGatePolicy` Literal 值出现在 Service 层，但本 gate 不允许修改 Service 层，且 boundary diff 命令已覆盖 `fund_agent/services`。

## Verification Summary

| 审查维度 | 结果 |
|---|---|
| 实现文件/测试/README 范围是否明确 | Yes — §1.1–§1.4 完整列出 add/read/out-of-scope 文件 |
| sidecar 是否 wrapper 而非平行真源 | Yes — §2.1 明确绑定决策，引用 contracts.py 为唯一真源 |
| sidecar 数据结构是否 code-generation-ready | Yes — §2.2 提供完整字段表、类型指导和 suggested dataclasses |
| dev-only audit 输入输出是否明确 | Yes — §3.2–§3.3 定义三种输入、输出 dataclasses 和公共 API |
| 首片是否只覆盖 active_fund chapter_3 | Yes — §4 明确限制 material 行为仅 active_fund chapter_3 |
| 是否严守不改 renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/FundDocumentRepository | Yes — §1.4、§3.1、§6、§7 均显式禁止 |
| 测试和验收命令是否足够 | Yes — §5 提供 10 个具体测试用例，§6 提供完整验收命令集 |
| stop conditions 是否完整 | Yes — §7 列出 7 条 stop condition 覆盖所有边界 |
| 与 controller judgment 一致性 | Yes — 审计模块路径、sidecar 设计、Chapter 2/6 deferred、coverage 目标均对齐 |
| 与 AGENTS.md 模块边界一致性 | Yes — sidecar 和 audit 均在 Agent 层 `fund_agent/fund` 内 |
| 与 design.md 架构边界一致性 | Yes — 不触及 UI/Service/Host 四层边界 |
| accepted evidence 链是否可追溯 | Yes — §0 列出 5 个真源，§4.1 引用 accepted evidence 的 wording fragments |

## Verdict

**PASS_WITH_FINDINGS**

Plan 是 code-generation-ready 的。无 blocking 或 material finding。5 个 finding 均为 minor 或 informational 级别，不影响编码 worker 从本 plan 直接开始实现。两个 minor finding（F1 命名一致性、F2 JSONL 结构约定）建议编码 worker 在实现时以 docstring 或 type alias 显式解决。
