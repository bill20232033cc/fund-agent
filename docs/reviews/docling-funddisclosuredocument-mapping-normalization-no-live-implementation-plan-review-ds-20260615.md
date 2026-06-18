# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Plan Review — AgentDS

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Planning Gate`

Role: AgentDS, review worker only. 只 review，不修 plan，不实现代码。

Reviewed artifact: `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`

Readiness state: `NOT_READY`

Verdict: `PASS_WITH_NONBLOCKING_FINDINGS`

## 1. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md` — Current Truth Guardrails, Current Gate
- `docs/current-startup-packet.md` — Current Mainline, Resume Checklist
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md` (the plan under review)
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`

## 2. Review Method

Adversarial review: 每个 review focus 均从 implementation worker 视角检验 plan 是否足够具体、边界是否闭合、是否留有未解决的发明空间。

未运行任何 PDF/Docling/EID/network/provider/LLM/analyze/checklist/golden/readiness/release/PR 命令。未 stage/commit/push。

## 3. Controller Judgment Binding Amendment Compliance

Controller judgment `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md` 的 7 条 binding amendments 逐条核验：

| # | Amendment | Plan compliance | Evidence |
|---|---:|---|---|
| 1 | `docling_pdf_candidate` candidate-only | `PASS` | §3.1, §6.1 `CandidateSourceKind = Literal["docling_pdf_candidate"]`, §6.3 禁止加入 `EvidenceSourceKind` |
| 2 | Closed normalization-rule vocabulary | `PASS` | §7 定义 11 个闭合 rule name，§13 stop condition 禁止新增 |
| 3 | Split document normalization from extractor/value parsing | `PASS` | §8 明确定义 document normalization 的 may/must not 边界 |
| 4 | Whitespace-only numeric grouping with fail-closed | `PASS` | §9 定义 5 条 repair conditions + 6 条 fail-closed conditions，含 accepted/rejected 示例 |
| 5 | Candidate projection fixture-only | `PASS` | §6.3 `CandidateEvidenceAnchorNote` 是 TypedDict fixture-only，Slice 5 禁止实例化 production `EvidenceAnchor` |
| 6 | Preserve `FundDocumentRepository` boundary and no-consumption guards | `PASS` | §4 forbidden writes, §5.1 ownership rules, Slice 7 no-consumption guards |
| 7 | Preserve EID single-source/no-fallback and `NOT_READY` | `PASS` | §1.3 non-goals, §3.2 non-proofs, §13 stop conditions, §14 residual risks, §17 verdict |

7/7 binding amendments satisfied.

## 4. Findings

### DS-IMPL-F1 — `NormalizedText` value object 未在 §6 正式声明

- **Severity**: low
- **Plan reference**: §7 rule notes 和 Slice 2 合约引用 `NormalizedText(raw_text, normalized_text, rules_applied, failure_code)` 作为 normalization 函数返回值，但 §6 Candidate Dataclass Design 未包含该类型的正式声明。
- **Impact**: implementation worker 需要自行设计 `NormalizedText` 的字段名、类型和 failure_code 可选性，存在与 Slice 2 断言不一致的风险。
- **Recommendation**: 在 §6 补充 `NormalizedText` dataclass/TypedDict 声明，或在 Slice 2 合约中给出完整字段定义。

### DS-IMPL-F2 — 文本级与表级 normalization 函数签名未统一

- **Severity**: low
- **Plan reference**: §7 定义 11 个 rule name，其中 `cjk_space_repair` 等 4 个是文本级（返回 `NormalizedText`），`header_path_reconstruction` 等 7 个是文档/表级（操作 block/table 对象）。§2.2 将文本级规则放在 `normalization.py`，表级规则放在 `locators.py`，但 §7 将它们列在同一个 vocabulary 下，未区分返回类型。
- **Impact**: implementation worker 可能在 `normalization.py` 与 `locators.py` 之间引入不一致的函数签名约定。
- **Recommendation**: §7 增加一列标注每个 rule 的返回类型或所属模块。或在 §5.2 中将文本级 rules 明确归属于 `normalization.py`，表级 rules 归属于 `locators.py`。

### DS-IMPL-F3 — `CandidateTableGroup` / stitched table container 类型缺失

- **Severity**: low
- **Plan reference**: Slice 4 定义 `cross_page_table_stitching` 返回 stitched result，`CandidateTableBlock` 有 `continuation_group_id: str | None`，但 §6 没有定义容纳 stitched table group 的容器类型。
- **Impact**: implementation worker 需要自行设计 stitched group 的 container shape（是返回 `CandidateTableBlock` 合并体还是新的 `CandidateTableGroup` 类型）。
- **Recommendation**: 在 §6 补充 stitched table group 类型声明，或至少在 Slice 4 合约中明确返回类型。

### DS-IMPL-F4 — `fund_agent/fund/extractors` 未列入 Slice 7 import 检查清单

- **Severity**: low
- **Plan reference**: Slice 7 合约列举禁止导入 candidate 的模块：`fund_agent/services, fund_agent/ui, fund_agent/host, fund_agent/fund/template, fund_agent/fund/audit, fund_agent/fund/report_quality_validation.py`。但 §5.1 明确声明 `fund_agent/fund/extractors/models.py` 是 public `EvidenceAnchor` schema surface 且 must not import candidate internals。`fund_agent/fund/extractors` 未出现在 Slice 7 的检查清单中。
- **Impact**: no-consumption guard 可能漏检 extractor 模块对 candidate 的导入。
- **Recommendation**: Slice 7 合约的禁止导入模块清单补充 `fund_agent/fund/extractors`。

### DS-IMPL-F5 — Fixture excerpt `prov` 字段的 provenance 条目数未指定

- **Severity**: info
- **Plan reference**: §10.2 `text_excerpts[].prov` 显示为单元素数组 `[{"page_no": 50, "bbox": {...}}]`，但 Docling JSON 中 `prov` 可能包含多个 provenance 条目。未指定 excerpt 中应保留多少 provenance 条目。
- **Impact**: implementation worker 可能截断 provenance 导致测试断言在 page_no/bbox 验证时不一致。
- **Recommendation**: §10.2 明确 excerpt 中 `prov` 保留规则（如"保留首个和末个 provenance 条目"或"保留全部"）。

### DS-IMPL-F6 — 测试文件命名绑定 Docling 实现细节

- **Severity**: info
- **Plan reference**: §4 测试文件名均使用 `test_docling_*` 前缀，而 candidate 模块位于 `fund_agent/fund/documents/candidates/`。命名将测试绑定到 Docling 具体来源。
- **Impact**: 若后续新增非 Docling candidate source，测试命名需要重构或产生误导。
- **Recommendation**: 非阻塞。当前 scope 为 Docling-only，但可考虑 `test_candidate_*` 命名以避免未来重构。

## 5. Review Focus Summary

### 5.1 Code-generation-readiness

Plan 提供了 implementation worker 所需的全部具体信息：
- 精确的文件路径（§5.2）
- 完整 dataclass/enum/TypedDict 字段名和类型（§6）
- 闭合 normalization rule name vocabulary 及其语义（§7）
- 归一化与抽取边界（§8）
- numeric whitespace grouping 的确定性 repair/block 规则和具体示例（§9）
- fixture JSON schema 和 required excerpt cases（§10）
- 9 个 small slices，每个含 contracts、expected assertions、failure paths（§11）
- 精确的 validation commands（§12）
- stop conditions（§13）

Implementation worker 不需要发明任何 schema ownership、fixture shape、normalization vocabulary、failure mapping 或 test scope。

**结论**: `PASS`。DS-IMPL-F1/F2/F3 是 minor 类型声明 gap，不影响整体 code-generation-readiness。

### 5.2 Allowed write set 宽度

Plan 的 allowed write set（§4）限制在：
- `fund_agent/fund/documents/candidates/` 下 5 个新文件
- `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`
- `tests/fund/documents/` 下 6 个测试文件
- 可选的 README 更新

Forbidden writes 明确排除 production `FundDocumentRepository` behavior、`EvidenceAnchor` schema、Service/UI/Host/renderer/quality gate、source policy/fallback、full artifacts。

**结论**: `PASS`。Write set 严格限定在 candidate internals 和 no-live tests。

### 5.3 Candidate models/enums 是否为 candidate-only

- 所有 enum 以 `Candidate` 前缀命名
- `source_truth_status`、`field_correctness_status`、`taxonomy_compatibility_status` 固定为 `"not_proven"`
- `production_parser_replacement_status` 固定为 `"not_authorized"`
- `CandidateEvidenceAnchorNote` 是 fixture-only TypedDict
- §5.1 禁止从 `fund_agent/fund/documents/__init__.py` 导出 candidate internals
- §6.3 明确禁止将 `docling_pdf_candidate` 加入 `EvidenceSourceKind`

**结论**: `PASS`。无 public contract/schema overreach。

### 5.4 Normalization vocabulary 闭合性与可测试性

- §7 定义 11 个闭合 rule name，§13 stop condition 禁止新增
- 每个 rule 有明确的 layer、applies to、output semantics
- §9 详细定义 `numeric_whitespace_grouping_repair_or_block` 的 5 条 repair conditions + 6 条 fail-closed conditions
- §9 含 accepted repair 示例表和 no-repair 示例表
- §10.3 要求 fixture 覆盖 `numeric-punctuation` 和 `numeric-whitespace-grouping` cases
- Slice 2 预期断言覆盖 CJK/date/numeric repair 和 ambiguous block

**结论**: `PASS`。Vocabulary 闭合，whitespace-only numeric grouping 规则可测试。

### 5.5 Fixture/excerpt 最小化

- §10.1 明确 `full_json_committed: false`
- §10.2 每个 table 只保留 header rows + 2-4 representative body rows
- §10.3 excerpt cases 从 8 个 focused cases 中选取最小 cell
- §4 forbidden writes 禁止提交完整 JSON/Markdown/PDF/cache/model artifacts
- fixture 包含 hash metadata 关联 Route A 完整 JSON 但不嵌入

**结论**: `PASS`。Fixture 设计最小化。

### 5.6 Slices 大小和 no-live 约束

- 9 slices（0-8），每个聚焦单一关注点
- 每个 slice 的 contracts 明确测试只使用 JSON excerpts/fakes
- §12 validation commands 全部为 no-live pytest + ruff
- §12 forbidden validation 禁止 PDF/Docling/EID/network/provider/LLM/analyze/checklist

**结论**: `PASS`。Slices 足够小，tests/validation 均为 no-live only。

### 5.7 No-consumption guards 和 repository non-behavior tests

- Slice 7 覆盖 repository 行为不变断言 + AST/static import 检查
- 检查目标包括 Service/UI/Host/template/audit/report_quality_validation
- 检查 `__init__.py` 不导出 candidate internals
- 检查 `EvidenceSourceKind` 不包含 `docling_pdf_candidate`

**结论**: `PASS_WITH_FINDING`。DS-IMPL-F4 指出 `fund_agent/fund/extractors` 应列入 import 检查清单，但不影响 guard 的核心有效性。

### 5.8 NOT_READY 和 non-claim 保留

- §1.3 non-goals 排除 source truth/field correctness/raw XML/taxonomy/parser replacement/readiness
- §3.2 non-proofs 显式列出 8 条非证明
- §6.1 status Literal 固定为 `not_proven` / `not_authorized`
- §13 stop conditions 中多条阻止 source truth/field correctness/parser replacement/readiness claims
- §14 residual risks 承认单样本、model cache provenance、same-report comparison 等未解决
- §17 verdict 以 `NOT_READY` 结尾

**结论**: `PASS`。`NOT_READY` 全链路保留，无 source truth/field correctness/raw XML/taxonomy/parser replacement/readiness 声明。

## 6. Cross-cutting Observations

- Plan 与 controller judgment 的 binding amendments 完全对齐，每条 amendment 都在 plan 中有对应的章节落实。
- Plan 的 stop conditions（§13）覆盖了所有已知的 scope creep 风险，包括 EvidenceAnchor schema change、repository behavior change、source policy change、full artifact commit、Decimal parsing、same-report comparison requirement 等。
- Plan 的 residual risks（§14）诚实记录了单样本限制、model cache provenance、same-report comparison deferred、cross-page stitching 高风险等未解决项。
- Completion report format（§16）为 implementation worker 提供了结构化的边界验证 checklist。

## 7. Final Verdict

```text
VERDICT: PASS_WITH_NONBLOCKING_FINDINGS
```

6 findings，均为 low/info severity，0 blocker。Plan 满足 code-generation-ready 标准，implementation worker 不需要发明 schema ownership、fixture shape、normalization vocabulary、failure mapping 或 test scope。

Recommended next step: controller reviews this artifact and, if accepted, authorizes `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Gate`.
