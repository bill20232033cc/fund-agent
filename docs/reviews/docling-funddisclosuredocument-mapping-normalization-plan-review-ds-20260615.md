# Docling FundDisclosureDocument Mapping And Normalization Plan Review — AgentDS

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization Plan Review Gate`

Role: AgentDS, review worker only. 不修 plan，不实现代码。

Readiness state: `NOT_READY`

## 1. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md`，`Current Truth Guardrails` 和 `Current Gate`
- `docs/current-startup-packet.md`，`Current Mainline` 和 `Resume Checklist`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-20260615.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`

未运行任何 PDF/Docling conversion、parser、EID/FDR/network、provider/LLM、analyze/checklist/readiness/release/PR 命令。

## 2. Review Matrix

| # | Review focus | Verdict | Evidence in plan |
|---|---|---|---|
| 1 | 是否把 `docling_pdf_candidate` 错写成当前 production `EvidenceAnchor.source_kind` 或 source truth | PASS | §4: "not a current `EvidenceAnchor.source_kind` production fact", "not a current production annual-report source policy"; §3 non-proofs 完整列出 source truth / field correctness / taxonomy / parser replacement 均为 `not_proven`；§6: "Do not add `docling_pdf_candidate` to current production `EvidenceAnchor.source_kind` in this gate"；§10 stop condition 第一项即为阻止此错误 |
| 2 | 是否保持 `FundDocumentRepository` / Fund documents 边界，禁止 Service/UI/Host/renderer/quality gate 直接调用 Docling/PDF/parser/cache | PASS | §4: candidate acquisition/parsing/normalization/cache 必须留在 `fund_agent/fund/documents` 并在 `FundDocumentRepository` 边界内；Service/UI/Host/renderer/quality gate 只能消费 typed domain outputs；§8 Slice 4 专门规划 Repository Boundary Non-Behavior Planning；§9 validation matrix 包含 "No direct parser access" 行；§10 stop condition 明确禁止此越界 |
| 3 | 是否明确用 Docling JSON `table_cells` 而不是 Markdown 作为结构化输入 | PASS | §5.5: "Use `tables[].data.table_cells`, not Markdown tables, as the primary structured input"；§5.6 以 `table_cells` 字段（`bbox`, `row_span`, `col_span`, `start/end_row_offset_idx`, `start/end_col_offset_idx`, `column_header`, `row_header`, `row_section`）为基础构建 cell locator；与 Route A evidence §7 disposition 一致 |
| 4 | normalization 是否覆盖中文空格、数字 token、多层表头、重复 header、跨页表、merged cell、TOC/页眉页脚剔除、row/column path | PASS | §7.1 中文空格修复（含 CJK-CJK 删除、日期标准化、mixed token 保留）；§7.2 数字 token 修复（`33,984,439 .75` → `33,984,439.75`、`154,973,70 4.60` → `154,973,704.60`）；§7.3 多层表头重建（`column_header_path` 从顶层到叶子）；§7.4 重复 header 去重；§7.5 跨页表拼接（含六项条件 check）；§7.6 merged cell 展开（row_span/col_span + forward-fill）；§7.7 TOC/页眉页脚剔除；§7.8 row label path 和 column header path 生成。八类全覆盖 |
| 5 | Validation matrix 是否 no-live fixture/excerpt-only，且不跑 PDF/Docling conversion、network/provider/LLM/analyze/checklist/readiness/release/PR | PASS | §9: "fixture/excerpt validation only"；Forbidden 列表逐项禁止 PDF/Docling conversion、PDF parser、EID/FDR/network、provider/LLM、analyze/checklist、golden、readiness/release/PR、source fallback expansion；16 行 validation 全部用 "excerpted" / "excerpts" / "static/fake" 输入 |
| 6 | 是否保留 EID single-source/no-fallback policy，不引入 Eastmoney/CNINFO/基金公司官网 fallback | PASS | §4: "Current production annual-report source policy remains EID single-source, no fallback"；"does not authorize Eastmoney, CNINFO, fund-company website, CDN or other fallback"；§10 stop condition 明确阻止 source policy 变更或 fallback 引入 |
| 7 | 是否过度声明 field correctness、raw XML、taxonomy、readiness、parser replacement | PASS | §3 non-proofs 完整列出；§5.1 identity 字段固定 `source_truth_status=not_proven`、`field_correctness_status=not_proven`、`taxonomy_compatibility_status=not_proven`、`production_parser_replacement_status=not_authorized`；§10 stop condition 覆盖所有过度声明；readiness 全局保持 `NOT_READY` |

## 3. Findings

### F1 — NONBLOCKING — normalization 边界可更明确 (severity: low)

§7 的 normalization 规则覆盖全面，但 document normalization 与 extractor normalization 的边界只在 §7.2 处有一处说明（"Do not coerce to `Decimal` in document normalization; numeric parsing belongs to later extractor validation"）。§7.1 的中文空格修复和 §7.2 的数字 repair 均属 document 级归一化，但两者的输入/输出契约未显式区分哪些规则是 document-level（always apply）哪些是 extractor-level（只在 field extraction 时 apply）。当前 plan 已声明 "keep both raw and normalized values"，边界风险低；后续 implementation planning 建议显式分层。

**Plan 依据**: §7 引言 "Normalization must be deterministic, fixture-based and auditable. It must keep both raw and normalized values." 和 §7.2 的单处边界说明。

**Disposition**: 非阻塞。当前 plan 在 planning gate 层面表达已足够；implementation planning 需显式分层契约。

### F2 — NONBLOCKING — normalization rule name vocabulary 未闭合 (severity: low)

§6 的 `note` JSON shape 中 `"normalization": ["numeric_token_repair_if_needed", "chinese_space_repair_if_needed"]` 使用字符串数组表示应用的归一化规则，但 plan 未给出 normalization rule name 的完整受控词汇表。§7 各处规则命名方式不一致（有的用描述性短语，有的用章节标题），可能导致后续 implementation planning 需要自行发明规则名。

**Plan 依据**: §6 recommended `note` shape L370-371: `"normalization": ["numeric_token_repair_if_needed", "chinese_space_repair_if_needed"]`；§7.1-7.8 各规则无统一 name key。

**Disposition**: 非阻塞。planning gate 层面不需要完整枚举；后续 implementation planning 应定义受控 vocabulary。

### F3 — NONBLOCKING — same-report comparison 已在 residual risks 中声明为 deferred 但未在 plan body 显式 cross-reference controller judgment 的 sequencing constraint (severity: low)

Controller judgment `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md` §5 binding residuals 要求 "Same-report comparison has not run. Do not plan consumer integration or field projection before that evidence gate." Plan §11 residual risks 正确声明 "Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred"，但 §6 EvidenceAnchor projection strategy 和 §8 Slice 3 未显式引用该 sequencing constraint 作为 projection fixture 的前置条件。当前 §8 Slice 3 已声明 "keep candidate source kind non-production"，风险低。

**Plan 依据**: §11 residual risks: "Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred"；Controller judgment §5 residual: same-report comparison 是 consumer integration 前置条件。

**Disposition**: 非阻塞。plan 已正确将 candidate projection 限定为 non-production fixture；implementation planning 建议显式引用 controller judgment 的 sequencing constraint。

## 4. Cross-Reference Verification

### 4.1 Controller judgment contract compliance

Controller judgment `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md` 的 accepted facts 和 binding residuals 与当前 plan 的对齐检查：

| Controller accepted fact / residual | Plan compliance |
|---|---|
| `docling_pdf_candidate` is not current `EvidenceAnchor.source_kind` | §4 + §6 + §10 明确遵守 |
| Option B (intermediate candidate, no schema mutation) | §6: "Keep `docling_pdf_candidate` inside the candidate representation layer for now" |
| Candidate failure classes map to canonical outcomes | §5.1: 完整 `not_found` / `unavailable` / `schema_drift` / `identity_mismatch` / `integrity_error` mapping |
| Same-report comparison not run → no consumer integration | §11 声明 deferred；§8 Slice 3 限定 non-production fixture |
| Docling remains later and optional, not parser replacement | §3 non-proofs + §5.1 status fields + §10 stop conditions |

无违反。

### 4.2 Route A evidence contract compliance

Route A evidence `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` 的 key dispositions 与 plan 的对齐检查：

| Route A disposition | Plan treatment |
|---|---|
| "DoclingDocument JSON, not Markdown text" 是正确消费层 | §5.5: 明确用 `table_cells` |
| "JSON carries page provenance, bbox and row/column offsets" | §5.5 / §5.6 完整保留 |
| "Markdown inserts spaces inside Chinese words and numeric tokens" | §7.1 / §7.2 直接处理 |
| "Multi-level headers are sometimes duplicated or split" | §7.3 / §7.4 直接处理 |
| "Cross-page tables are split" | §7.5 直接处理 |
| "Local PDF is user-owned benchmark, not EID source truth" | §3 non-proofs + §5.1 status fields |

无违反。

### 4.3 AGENTS.md hard constraints compliance

| Constraint | Plan compliance |
|---|---|
| 基金文档存取必须通过 `FundDocumentRepository` | §4 + §8 Slice 4 |
| Service/UI/Host/renderer/quality gate 不得直接调用 parser/cache | §4 + §10 stop condition |
| EID single-source/no-fallback policy | §4 + §10 stop condition |
| 不预测、不猜测、不输出买卖建议 | 不适用（planning only, no content generation） |
| LLM 路径显式 opt-in | 不适用（无 LLM route） |

无违反。

## 5. Verdict

```text
VERDICT: PASS
```

All seven review focus areas pass. Three nonblocking findings (F1–F3) are low severity and do not block plan acceptance or next-gate entry. The plan correctly:

- Classifies `docling_pdf_candidate` as candidate-only, never production source truth or `EvidenceAnchor.source_kind`.
- Preserves `FundDocumentRepository` boundary and prohibits direct Docling/PDF/parser/cache access by Service/UI/Host/renderer/quality gate.
- Requires `tables[].data.table_cells` JSON as structured input, not Markdown.
- Covers all eight normalization areas: Chinese space, numeric token, multi-level headers, repeated headers, cross-page stitching, merged cells, TOC/header/footer exclusion, row/column paths.
- Restricts validation matrix to fixture/excerpt-only with no PDF/Docling/network/provider/LLM/analyze/checklist/readiness/release/PR.
- Preserves EID single-source/no-fallback policy, excludes Eastmoney/CNINFO/基金公司官网.
- Avoids over-claiming field correctness, raw XML, taxonomy, readiness or parser replacement.

The plan is ready for controller review.

## 6. Output Artifact

Path: `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-ds-20260615.md`

不 stage，不 commit，不 push，不 PR。
