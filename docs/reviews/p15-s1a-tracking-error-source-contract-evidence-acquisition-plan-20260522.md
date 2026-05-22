# P15-S1A Tracking Error Source Contract / Evidence Acquisition Plan（2026-05-22）

## Verdict

`PROCEED_TO_EVIDENCE_ACQUISITION_IMPLEMENTATION`

建议下一步进入 evidence-acquisition implementation，但该 implementation 的唯一目标是生成 reviewed evidence artifact，用来证明 `001548` 2024 年报是否存在可复核的 direct observed `tracking_error` 披露；不得先改 production golden rows。

理由：

- P15-S1 已接受 blocker：当前 reviewed artifacts 没有 `001548` 的 direct observed `tracking_error` 值，不能从现有 golden/review 资料补 rows。
- 设计真源要求生产年报访问经过 `FundDocumentRepository`，当前代码已有 `ParsedAnnualReport`、`extract_performance()`、`EvidenceAnchor` 和 `TrackingErrorValue(source_type="direct_disclosure")` 这些边界内能力。
- 最短可验证路径不是继续等待，也不是计算 tracking error，而是在 Fund Capability 文档仓库边界内读取 `001548` 2024 年报，枚举所有跟踪误差相关披露，输出可人工复核的 evidence artifact。若 artifact 仍无 direct observed disclosure，golden gate 继续 blocked。

## Source Contract

### Acceptable Direct Disclosure Evidence

可接受证据必须同时满足：

| Field | Requirement |
|---|---|
| `fund_code` | 必须是 `001548`，不得由名称或基金代码外推替代 |
| `report_year` | 必须是 `2024` 年报 |
| `document_kind` | 必须是 `annual_report` |
| `access_path` | 必须通过 `FundDocumentRepository.load_annual_report()` 或 `FundDataExtractor.extract()`，不得直接读 PDF cache、下载 helper、source adapter 或本地 parsed cache |
| `value_text` | 年报原文披露的实际跟踪误差数值，例如 `1.23%` |
| `normalized_value` | 从 `value_text` 解析出的 ratio，仅作为同源值规范化结果，不得由 NAV/index series 计算 |
| `period_label` | 年报披露或上下文可直接确定的期间，如 `报告期`、`本报告期`、`过去一年` |
| `annualized` | 年报表头或正文直接支持的年化状态；无法确定时不得臆断为 `True` |
| `source_type` | 必须是 `direct_disclosure` |
| `calculation_method` | 必须是 `disclosed` |
| `anchor` | 必须能定位到年报章节；表格证据还必须有 page/table/row 或等价表头与行标签；正文证据必须有原文行 |
| `provenance` | 必须记录 repository source metadata、fallback_used、cache provenance、extractor/classifier decision 和 rejected candidates |

### Rejected Evidence Classes

以下内容不能证明 observed `tracking_error` value：

| Evidence class | Decision |
|---|---|
| benchmark-only text | 只能支持 `index_profile`，不能作为 `tracking_error` value proof |
| investment objective target / limit | 例如“年化跟踪误差控制在 2% 以内”，这是目标或限制，不是实际观测值 |
| manager narrative | 关于控制、降低、最小化跟踪误差的叙述不是数值披露 |
| standard deviation columns | 净值增长率标准差、基准收益率标准差不得误认为跟踪误差 |
| calculated value | 从基金/指数序列计算出的值属于后续 calculated tracking-error phase |
| ambiguous or conflicting hits | 同一上下文混有实际值和目标控制语义，或表格/正文数值冲突时 fail closed |
| unparseable percent | 无法稳定解析为百分比 ratio 时不得入 golden |

### Failure Classification

Source-access failure 由 Fund Capability documents 层保持既有分类：

| Category | Meaning | P15-S1A action |
|---|---|---|
| `not_found` | 来源正常响应但没有 `001548` 2024 年报 | record as source blocker; no golden |
| `unavailable` | 网络、超时、服务端或本地依赖临时不可用 | record as deferred source blocker; no golden |
| `schema_drift` | 来源响应结构、字段或附件形态偏离契约 | fail closed; no fallback masking; no golden |
| `identity_mismatch` | 返回候选与基金代码、年份或报告类型矛盾 | fail closed; no golden |
| `integrity_error` | PDF Content-Type、文件头或写入内容完整性失败 | fail closed; no golden |

Evidence-level failure 在 reviewed artifact 中单独记录：

| Category | Meaning | P15-S1A action |
|---|---|---|
| `no_tracking_error_mentions` | 年报中无跟踪误差相关关键词 | blocked; no golden |
| `target_only` | 只有目标/限制/控制阈值 | blocked; no golden |
| `benchmark_only` | 只有基准或指数身份上下文 | blocked; no golden |
| `narrative_only` | 只有管理人叙述，无实际数值 | blocked; no golden |
| `standard_deviation_only` | 只有标准差列或标准差说明 | blocked; no golden |
| `ambiguous` | 实际披露与目标/限制语义混杂，或多候选无法唯一选择 | blocked; no golden |
| `unparseable` | 值无法稳定解析为百分比 ratio | blocked; no golden |
| `anchor_incomplete` | 有候选值但缺少可复核章节/表格/行锚点 | blocked until anchor is fixed |

### Stop Conditions

未来 implementation 必须在以下情况停止，不得编辑 production golden：

- `extract_performance(report).tracking_error` 不是 `extraction_mode="direct"`，或 `value.source_type!="direct_disclosure"`。
- 只发现 benchmark、目标/限制、经理 narrative、标准差、歧义或不可解析文本。
- 候选证据无法给出年报章节和可复核锚点。
- 需要计算 tracking error、引入外部 index adapter、抽取 methodology/constituents、重设 QDII subtype、运行 E1-E3/Evidence Confirm、LLM writing、Dayu runtime、Host、Engine 或 tool loop。
- 来源失败属于 fail-closed 类别，或 repository provenance 显示基金代码/年份/报告类型不一致。

## Evidence Acquisition Design

### Boundary

未来 implementation 只能在 Fund Capability 边界内获取年报：

```text
Evidence acquisition helper
  -> FundDataExtractor.extract("001548", 2024)
     -> FundDocumentRepository.load_annual_report("001548", 2024)
        -> documents layer source orchestration and cache internals
  -> extract_performance(ParsedAnnualReport)
  -> reviewed evidence artifact
```

Service、UI、Engine、renderer、quality gate、golden tooling 不得直接读取 PDF/cache/source adapter。若 implementation 增加一个临时或内部 helper，也必须依赖 `FundDocumentRepository` 或 `FundDataExtractor` 的公开边界。

### Implementation Steps

1. 建立 Capability-owned evidence acquisition helper，默认输入显式为 `fund_code="001548"`、`report_year=2024`、`force_refresh=False`；允许 reviewer 通过显式参数选择 `force_refresh=True` 重新走 repository，但不允许直接指定 PDF/cache 路径。
2. 调用 `FundDocumentRepository.load_annual_report()` 获取 `ParsedAnnualReport`，记录 `DocumentKey`、`AnnualReportMetadata.source`、`fallback_used`、cache provenance 和 source URL/报告名称等可用 provenance。
3. 验证 parsed report identity：`report.key.fund_code == "001548"`、`report.key.year == 2024`、`document_kind == "annual_report"`；不一致时记录 `identity_mismatch` 并停止。
4. 调用 `extract_performance(report)`，把 `tracking_error` 的 extraction mode、value、anchors、note 作为 primary structured decision。
5. 在同一个 `ParsedAnnualReport` 内做 full keyword inventory：扫描 `raw_text` 与 `tables` 中所有包含 `跟踪误差`、`跟踪偏离度` 或英文 tracking-error 语义的行、表头和单元格，并映射到章节、page/table/row 或正文行。
6. 对每个 candidate 按 source contract 分类：`accepted_direct_disclosure`、`target_only`、`benchmark_only`、`narrative_only`、`standard_deviation_only`、`ambiguous`、`unparseable`、`anchor_incomplete`。
7. 若 primary structured decision 与 inventory 分类冲突，必须 fail closed：例如 inventory 找到 direct-looking value 但 extractor 返回 missing 时，artifact 只能记录 `needs_extractor_or_anchor_fix`，不得直接改 golden。
8. 输出 reviewed evidence artifact，包含 accepted evidence（若有）、所有 rejected candidates、source provenance、commands、stop-condition result 和 golden decision。
9. 只有当 reviewed evidence artifact 明确 `ACCEPTED_DIRECT_DISCLOSURE` 且包含完整 anchors 后，才允许开启后续 separate golden implementation gate。P15-S1A implementation 本身不改 production golden。

### Reviewed Evidence Artifact Shape

未来 artifact 建议路径：

```text
docs/reviews/p15-s1a-tracking-error-evidence-acquisition-implementation-20260522.md
```

最小内容：

- verdict：`ACCEPTED_DIRECT_DISCLOSURE` 或 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`
- request：`fund_code`、`report_year`、`document_kind`、`force_refresh`
- repository provenance：source metadata、fallback_used、cache provenance、report identity
- structured extraction decision：`extraction_mode`、`note`、`value_text`、`period_label`、`annualized`、`source_type`、`calculation_method`
- accepted evidence table：只在 direct observed value 存在时填写
- rejected candidates table：列出关键词命中位置、原文短摘、分类和拒绝理由
- anchor appendix：使用 `年报2024§<section>表<page-table>行<tracking_error>` 或正文行 note 的等价可复核格式
- golden decision：`do_not_edit_golden` 或 `eligible_for_future_golden_gate`

### Golden Sequencing

顺序必须固定：

1. P15-S1A evidence acquisition implementation 生成 reviewed evidence artifact。
2. Plan/review 或 controller judgment 接受该 artifact。
3. 若 verdict 是 `ACCEPTED_DIRECT_DISCLOSURE`，再开启独立 golden implementation gate。
4. 独立 golden gate 才能修改 reviewed Markdown、strict JSON、必要测试和文档。
5. 若 verdict 是 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`，production `tracking_error` golden rows 继续 blocked/deferred。

## File Ownership For Future Implementation

### Allowed If P15-S1A Enters Implementation

| Area | Files | Scope |
|---|---|---|
| evidence helper | `fund_agent/fund/tracking_error_evidence.py` or equivalent Fund Capability module | acquire/classify/report evidence through repository boundary |
| extractor fix, only if artifact proves a false negative | `fund_agent/fund/extractors/performance.py` | tighten direct-disclosure extraction, anchors, ambiguity handling |
| extractor/evidence tests | `tests/fund/extractors/test_performance.py`, optional `tests/fund/test_tracking_error_evidence.py` | direct value, target-only, benchmark-only, narrative-only, ambiguous, anchor completeness |
| document repository tests, only if boundary/provenance regression is found | `tests/fund/documents/test_repository.py`, `tests/fund/documents/test_annual_report_sources.py` | provenance and fail-closed behavior only |
| implementation artifact | `docs/reviews/p15-s1a-tracking-error-evidence-acquisition-implementation-20260522.md` | reviewed evidence result |
| package README, only if a stable public Capability API is introduced | `fund_agent/fund/README.md` | current behavior only; no future-design prose |
| tests README, only if a new test class/command is added | `tests/README.md` | test maintenance note only |

### Prohibited In P15-S1A Implementation

| Area | Files / behavior |
|---|---|
| production golden | `reports/golden-answers/golden-answer-prefill-reviewed.md`, `reports/golden-answers/golden-answer.json`, `reports/golden-answers/golden-answer-prefill.md` |
| golden template/tooling | `docs/golden-answer-template.md`, golden build/prefill tooling unless a later separate golden gate authorizes it |
| selected-fund source data | RR-13 data and source CSV files |
| architecture/control truth | `docs/design.md`, `docs/implementation-control.md` |
| runtime layers | Service/UI/Engine/renderer/quality gate direct document access or behavior changes |
| out-of-scope systems | external index adapter, methodology/constituents extraction, QDII subtype redesign, E1-E3/Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, tool loop |
| excluded audit artifact | do not read, cite, stage, edit, or use it |

## Acceptance Tests / Validation Commands

Minimum validation for future evidence implementation:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
.venv/bin/python -m pytest tests/fund/test_tracking_error_evidence.py -q
.venv/bin/python -m pytest tests/fund/documents/test_repository.py tests/fund/documents/test_annual_report_sources.py -q
.venv/bin/python -m pytest tests/fund/integration/test_p1_sample_matrix.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
```

If the implementation adds no stable public API and only produces a reviewed artifact through a one-off helper/test, success signal is:

- bounded command reads `001548` 2024 only through `FundDocumentRepository` or `FundDataExtractor`;
- reviewed evidence artifact exists and records repository provenance;
- all tracking-error mentions in the parsed report are classified;
- direct observed evidence, if accepted, has `value_text`、`period_label`、`annualized`、`source_type=direct_disclosure` and a complete annual-report anchor;
- if no accepted evidence exists, artifact explicitly says `do_not_edit_golden`;
- tests prove target/limit, benchmark-only, narrative-only, standard deviation, ambiguous and unparseable cases cannot become accepted direct disclosure.

If the artifact accepts direct disclosure, separate future golden-gate validation must include:

```bash
.venv/bin/python -m pytest tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate_integration.py -q
.venv/bin/python -m ruff check fund_agent tests
.venv/bin/python -m pytest
git diff --check HEAD
```

Golden-gate success signal would be strict JSON rows for `001548.tracking_error` matching the accepted reviewed evidence artifact. That success signal is intentionally not part of P15-S1A evidence implementation.

## Residuals

| Residual | Owner | Status |
|---|---|---|
| `001548` production `tracking_error` golden rows | future golden implementation gate | blocked until reviewed direct evidence artifact is accepted |
| `001548` direct disclosure evidence acquisition | P15-S1A implementation | ready for implementation plan/review acceptance |
| extractor false negative on actual direct disclosure | P15-S1A implementation, only if evidence inventory proves it | possible; must fix extractor before golden |
| enhanced-index production golden expansion | future selected-fund/golden expansion | deferred |
| calculated tracking error | future calculation/data-source phase | out of scope |
| external index adapter | future source/data phase | out of scope |
| index methodology / constituents extraction | future source-contract phase | out of scope |
| QDII subtype applicability | future subtype-design phase | out of scope |
| E1-E3 / Evidence Confirm | future audit architecture phase | out of scope |

## Explicit Non-goals

- No code, test, golden, README, design-doc or control-doc changes in this plan gate.
- No production golden rows in P15-S1A evidence implementation.
- No calculated tracking error.
- No external index data adapter.
- No index methodology or constituents extraction.
- No QDII subtype redesign.
- No E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop.
- No RR-13 or source CSV work.
- No Service/UI/Engine/renderer/quality gate direct document access.
- No commit, push, PR, external comment, or branch cleanup.

## Plan Review Checklist

- [x] Verdict chooses evidence-acquisition implementation, not golden implementation.
- [x] Direct disclosure source contract requires observed value, period, annualization, source type and anchors.
- [x] Target/limit, benchmark-only, manager narrative, standard deviation, ambiguous and calculated values are rejected.
- [x] Source access stays behind `FundDocumentRepository` / Fund Capability document boundary.
- [x] Evidence acquisition records provenance and failure classification.
- [x] Golden sequencing requires accepted reviewed evidence artifact before any golden rows.
- [x] Future file ownership separates evidence implementation from prohibited golden/source/control changes.
- [x] Validation commands and success signals are explicit.
- [x] Residuals and non-goals preserve P15-S1 controller guardrails.
