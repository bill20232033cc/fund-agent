# Docling FundDisclosureDocument Mapping And Normalization Plan Review - MiMo

Date: 2026-06-15

Reviewer: AgentMiMo

Gate: `Docling FundDisclosureDocument Mapping And Normalization Plan Review Gate`

Reviewed target: `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-20260615.md`

## 1. Scope

Review focus areas specified by controller:

1. 是否把 `docling_pdf_candidate` 错写成当前 production `EvidenceAnchor.source_kind` 或 source truth。
2. 是否保持 `FundDocumentRepository` / Fund documents 边界，禁止 Service/UI/Host/renderer/quality gate 直接调用 Docling/PDF/parser/cache。
3. 是否明确用 Docling JSON `table_cells` 而不是 Markdown 作为结构化输入。
4. normalization 是否覆盖中文空格、数字 token、多层表头、重复 header、跨页表、merged cell、TOC/页眉页脚剔除、row/column path。
5. Validation matrix 是否 no-live fixture/excerpt-only，且不跑 PDF/Docling conversion、network/provider/LLM/analyze/checklist/readiness/release/PR。
6. 是否保留 EID single-source/no-fallback policy，不引入 Eastmoney/CNINFO/基金公司官网 fallback。
7. 是否过度声明 field correctness、raw XML、taxonomy、readiness、parser replacement。

## 2. Evidence Read

- `AGENTS.md`
- `docs/implementation-control.md`, `Current Truth Guardrails` and `Current Gate`
- `docs/current-startup-packet.md`, `Current Mainline` and `Resume Checklist`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-20260615.md` (reviewed target)
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`

## 3. Review Focus Analysis

### 3.1 `docling_pdf_candidate` as production `EvidenceAnchor.source_kind` or source truth

**PASS**

The plan correctly maintains the candidate/production boundary:

- Section 4 "Candidate Source Classification" explicitly states: `docling_pdf_candidate` "is not a current `EvidenceAnchor.source_kind` production fact" and "It must not be added to current production renderer/audit/source-label behavior in this gate."
- Section 6 "Candidate EvidenceAnchor Projection Strategy" states: "Keep `docling_pdf_candidate` inside the candidate representation layer for now" and "Do not add `docling_pdf_candidate` to current production `EvidenceAnchor.source_kind` in this gate."
- Section 3 "Current Accepted Facts And Non-Proofs" explicitly lists non-proofs: "The local user-owned PDF benchmark is not source truth" and "Docling output is not field correctness proof."
- Section 5.1 identity fields enforce `source_truth_status: fixed "not_proven"`, `field_correctness_status: fixed "not_proven"`, `taxonomy_compatibility_status: fixed "not_proven"`, `production_parser_replacement_status: fixed "not_authorized"`.
- Section 10 "Stop Conditions" includes: "`docling_pdf_candidate` is treated as current production `EvidenceAnchor.source_kind`" as a stop condition.

The plan does not conflate `docling_pdf_candidate` with existing production source kinds (`annual_report`, `external_api`, `derived`).

### 3.2 `FundDocumentRepository` / Fund documents boundary

**PASS**

The plan correctly enforces module boundaries:

- Section 4 "Ownership" states: "Candidate acquisition, parsing, normalization, cache metadata and failure classification must remain inside `fund_agent/fund/documents` and behind `FundDocumentRepository` boundaries if later implemented."
- Section 4 "Ownership" continues: "Service/UI/Host/renderer/quality gate must continue to consume only accepted typed domain outputs, not PDF files, Docling artifacts, parser cache or parser helpers."
- Section 8 "Slice 4: Repository Boundary Non-Behavior Planning" plans verification that "Service/UI/Host/renderer/quality gate do not import/call Docling, PDF cache, parser helper or candidate artifacts."
- Section 9 "Validation Matrix" includes "No direct parser access" row checking static/fake import boundary.
- Section 10 "Stop Conditions" includes: "The plan lets Service/UI/Host/renderer/quality gate call Docling, PDF, parser cache or candidate artifacts directly" as a stop condition.

This aligns with `AGENTS.md` hard constraint: "基金文档存取必须通过 `FundDocumentRepository`。Service、UI、Host、renderer、quality gate 不得直接调用 PDF cache、下载 helper 或具体 parser。"

### 3.3 Docling JSON `table_cells` vs Markdown as structured input

**PASS**

The plan explicitly prefers JSON `table_cells`:

- Section 5.5 "Table Blocks" mapping rules state: "Use `tables[].data.table_cells`, not Markdown tables, as the primary structured input."
- Section 3 "Current Accepted Facts" documents `table_cells` schema: `bbox`, `row_span`, `col_span`, `start_row_offset_idx`, `end_row_offset_idx`, `start_col_offset_idx`, `end_col_offset_idx`, `text`, `column_header`, `row_header`, `row_section`, `fillable`.
- Section 5.6 "Table Cell Locators" builds on `table_cells` fields.
- Section 9 "Validation Matrix" "Cell locator fixture" row validates `table_cells` excerpts with bbox/header flags/offsets.

This aligns with Route A evidence finding: "JSON carries page provenance, bbox and row/column offsets for tables" and "JSON `table_cells` should be consumed instead of Markdown tables."

### 3.4 Normalization coverage

**PASS**

The plan covers all required normalization scenarios:

| Scenario | Plan section | Coverage |
|---|---|---|
| 中文空格 | 7.1 Chinese Space Repair | Remove ASCII spaces between adjacent CJK characters; preserve Latin/token spaces; normalize date spaces |
| 数字 token | 7.2 Numeric Token Repair | Repair spaces inside numeric tokens; normalize comma-grouped decimals; block ambiguous repairs |
| 多层表头 | 7.3 Multi-Level Header Reconstruction | Identify header cells by `column_header=true`; expand merged headers; build `column_header_path` |
| 重复 header | 7.4 Repeated Header Deduplication | Detect repeated header rows; remove from `body_rows`; preserve in `excluded_rows` |
| 跨页表 | 7.5 Cross-Page Table Stitching | Stitch consecutive tables when conditions pass; preserve original refs |
| merged cell | 7.6 Merged Cell Handling | Use `row_span`/`col_span` to expand logical grid; forward-fill labels within span |
| TOC/页眉页脚剔除 | 7.7 Directory/Page Header/Footer Exclusion | Classify TOC tables as `document_index`; exclude cover/headers/footers; keep with `excluded_reason` |
| row/column path | 7.8 Row Label Path And Column Header Path Generation | Build from row-section/header cells; normalize; deduplicate; include units/periods |

### 3.5 Validation matrix: no-live fixture/excerpt-only

**PASS**

The plan correctly constrains validation to fixture/excerpt only:

- Section 9 "Validation Matrix For Later No-Live Implementation" title and introduction: "The later implementation-planning worker should require fixture/excerpt validation only."
- Section 9 "Forbidden in later no-live implementation planning" explicitly lists: PDF/Docling conversion, PDF parser execution, EID/FDR/network, provider/LLM, analyze/checklist, golden, readiness/release/PR, source fallback expansion.
- All 17 validation rows use "Fixture input" and "Expected proof" columns, not live inputs.
- Section 8 implementation slices all specify "Plan only" and "No PDF, no Docling conversion, no live source" for Slice 0.
- Section 10 "Stop Conditions" includes: "PDF/Docling conversion, PDF parser, EID/FDR/network, provider/LLM, analyze/checklist/golden/readiness/release/PR commands are required" as a stop condition.

### 3.6 EID single-source/no-fallback policy preservation

**PASS**

The plan preserves EID policy without fallback expansion:

- Section 4 "Relation to current source policy" states: "Current production annual-report source policy remains EID single-source, no fallback."
- Section 4 continues: "`docling_pdf_candidate` does not authorize Eastmoney, CNINFO, fund-company website, CDN or other fallback."
- Section 10 "Stop Conditions" includes: "EID single-source/no-fallback policy is changed or bypassed" and "Eastmoney, CNINFO, fund-company website/CDN or other fallback is introduced" as stop conditions.

This aligns with `AGENTS.md`: "当前 EID single-source policy：`not_found` / `unavailable` 是 terminal failure，不触发 fallback。"

### 3.7 Overclaiming field correctness, raw XML, taxonomy, readiness, parser replacement

**PASS**

The plan does not overclaim:

- Section 3 "Non-proofs" explicitly lists: "Docling output is not field correctness proof", "Docling output is not raw XML/XBRL proof", "Docling output is not taxonomy compatibility proof", "Docling output is not current production parser replacement", "Docling output is not readiness, release or PR proof."
- Section 5.1 identity fields enforce `not_proven` / `not_authorized` status.
- Section 6 projection strategy stores `source_truth_status: "not_proven"` and `field_correctness_status: "not_proven"` in candidate note.
- Section 10 "Stop Conditions" includes: "Candidate output is described as source truth, field correctness proof, raw XML/XBRL proof, taxonomy proof, parser replacement, readiness or release proof" as a stop condition.

## 4. Findings

### 001-未修复-低-numeric token repair 空白分隔符歧义规格不足

- **位置**: Section 7.2 Numeric Token Repair, "Plan" 和 "Tests later"
- **问题类型**: 契约缺失
- **当前写法**: "Repair spaces inside numeric tokens only when both sides match numeric punctuation grammar." 测试示例仅覆盖标点分隔（`33,984,439 .75` 和 `154,973,70 4.60`）。
- **反例/失败场景**: `100 000`（无标点的空格分隔千位）和 `1 234 567` 是中国基金年报常见格式。Plan 未定义此类空白分隔是否修复、如何修复、歧义时如何 block。
- **为什么有问题**: 实施 agent 可能对空白分隔数字做出不一致的修复决策，或在歧义场景下不 block projection。
- **直接证据**: Section 7.2 "Repair spaces inside numeric tokens only when both sides match numeric punctuation grammar" 未覆盖无标点空白分隔。
- **影响**: 实施 agent 需要自行定义空白分隔规则，可能导致 locator 不稳定或 field 投影错误。
- **建议改法和验证点**: 在 Section 7.2 补充空白分隔数字的修复规则或明确 block 语义；测试覆盖 `100 000`、`1 234 567` 等无标点场景。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 5. Open Questions

None. All review focus areas are addressed by the plan with direct evidence.

## 6. Residual Risks

The plan correctly identifies residual risks in Section 11:

- Single sample `004393 / 2025`; cross-fund, cross-year and report-type coverage unproven.
- Local HuggingFace cache provenance is not production model provenance acceptance.
- Docling JSON schema may drift across versions.
- PDF page provenance is useful for anchors, but not equivalent to source-truth validation.
- Cell text quality needs extractor validation before becoming field facts.
- Multi-level headers, cross-page stitching and merged cells are highest-risk normalization areas.
- TOC and repeated headers can create false positives if not excluded before locator generation.
- Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred.

These residual risks are appropriate for a planning gate and should be tracked to later implementation/evidence gates.

## 7. Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are written clearly.
- [x] Findings are evidence-based, adversarial, actionable, and not style/nit/speculation.
- [x] Open questions, residual risks and tracking destination are separated from findings.
- [x] Conclusion is one of `pass`, `pass-with-risks` or `fail`.
- [x] Output path uses system-clock timestamp and matches artifact path format.

## 8. Final Verdict

```text
VERDICT: PASS_WITH_NONBLOCKING_FINDINGS
```

The plan correctly addresses all 7 review focus areas:

1. `docling_pdf_candidate` is correctly classified as candidate-only, not production `EvidenceAnchor.source_kind` or source truth.
2. `FundDocumentRepository` / Fund documents boundary is preserved; Service/UI/Host/renderer/quality gate direct access is forbidden.
3. Docling JSON `table_cells` is explicitly specified as structured input, not Markdown.
4. Normalization covers all 8 required scenarios: Chinese space, numeric token, multi-level header, repeated header, cross-page table, merged cell, TOC/header/footer exclusion, row/column path.
5. Validation matrix is fixture/excerpt-only; no PDF/Docling conversion, network, provider/LLM, analyze/checklist/readiness/release/PR.
6. EID single-source/no-fallback policy is preserved; no Eastmoney/CNINFO/基金公司官网 fallback.
7. No overclaiming of field correctness, raw XML, taxonomy, readiness or parser replacement.

The single non-blocking finding (001) concerns ambiguity in numeric token repair for whitespace-only separators. It does not block the planning gate but should be addressed before implementation planning proceeds.

Output artifact: `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-mimo-20260615.md`
