# Bounded Same-report EID HTML Render Discovery Evidence Review — MiMo

Date: 2026-06-15

Gate: `Bounded Same-report EID HTML Render Discovery Gate`

Role: MiMo review worker

Verdict: `PASS_WITH_NONBLOCKING_FINDINGS`

## Scope

- Evidence artifact: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-20260615.md`
- JSON artifact: `reports/representation-json/004393_2025_eid_html_render_full.json`
- Controller input: `docs/reviews/same-report-full-annual-representation-json-evidence-controller-judgment-20260615.md`
- Control docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## Review Focus Assessment

### 1. Does the evidence prove same-report EID HTML render availability for 004393 / 2025, and only that?

**YES.** The evidence documents three official requests scoped exclusively to `004393 / 2025 / 年度报告`:

1. XBRL search metadata identifies `FB010010 = 年度报告`.
2. Same-report XBRL search with `fundCode=004393`, `reportYear=2025`, `reportTypeCode=FB010010` returns exactly one row with `uploadInfoId=22053366`.
3. Instance HTML view `HEAD/GET` on `instanceid=22053366` yields 302 redirect to final render URL, confirmed with 200 OK, `Content-Length: 822146`, and `SHA-256: 8e03dfee69eb8a17c653eb0ae5fcefd12d331820f0543bee83d7136c3cc3fb94`.

No other fund code, year, or report type was queried. No general discovery was attempted.

### 2. Does it avoid treating HTML render as raw XML/XBRL instance truth?

**YES.** Section 6 guardrails explicitly declare:

- `not_raw_xml_download_proof`: "this gate used generated HTML render only, not raw XML or raw XBRL instance."
- `not_field_correctness_proof`: "extracted cells are observed HTML render text only; no PDF/source-body value comparison was performed."
- `not_taxonomy_compatibility_proof`: "no schemaRef/contextRef/unitRef/taxonomy compatibility was proven."
- `not_source_truth`: "HTML render remains candidate evidence, not source truth."

The source_kind is `eid_xbrl_html_render_candidate` (candidate, not fact or truth).

### 3. Does it avoid field correctness, taxonomy compatibility, source truth, readiness, production parser replacement, or repository behavior claims?

**YES.** Section 6 guardrails cover all six:

- `not_field_correctness_proof` — present
- `not_taxonomy_compatibility_proof` — present
- `not_source_truth` — present
- `not_readiness_proof` — present
- `no_repository_behavior_change` — present
- `no_production_parser_replacement` — present

No implicit claims contradict these guardrails.

### 4. Does it preserve EID single-source and no non-EID fallback?

**YES.** Section 6 declares:

- `no_non_eid_fallback`: "no Eastmoney, CNINFO, fund-company website or other fallback was used."

All three requests target `eid.csrc.gov.cn` exclusively. The redirect chain stays within `eid.csrc.gov.cn`.

### 5. Does the JSON include enough request provenance, render URL/hash, navigation/section/table/locator candidates, and blocked claims?

**YES.** The JSON artifact contains:

| Category | Fields present | Status |
|---|---|---|
| Request provenance | `official_request_provenance` with `search_url`, `search_method`, `search_aoData` (full request body) | Adequate |
| Render identity | `html_render_identity` with `idStr`, `uploadInfoId`, `fundidStr`, `fundId`, `reportYear`, `reportSendDate`, `uploadDate`, `render_url`, `html_title`, `content_sha256`, `contains_xbrl_title` | Adequate |
| Navigation/section/table candidates | `navigation_labels` (211), `heading_candidates` (261), `paragraph_blocks` (750), `tables` (802), `target_table_candidates` (14) | Adequate |
| Summary metrics | `html_byte_size`, `navigation_label_count`, `heading_candidate_count`, `paragraph_block_count`, `table_count`, `table_cell_count`, `target_table_candidate_count`, `has_url_or_source_locator`, `has_content_hash`, `has_page_number`, `has_section_tree`, `has_table_cell_locator` | Adequate |
| Blocked claims | 9 entries: `not_raw_xml_download_proof`, `not_field_correctness_proof`, `not_taxonomy_compatibility_proof`, `not_source_truth`, `not_readiness_proof`, `no_repository_behavior_change`, `no_non_eid_fallback`, `no_production_parser_replacement`, `no_funddisclosuredocument_schema` | Adequate |

### 6. Does it honestly record that AgentCodex network approval UI blocked and controller collected the live facts?

**PARTIALLY.** The evidence file records in its role field:

> "Role: evidence worker fallback executed by controller after AgentCodex approval UI blocked on bounded curl requests."

This acknowledges controller fallback execution but does not explicitly state that the controller directly collected the live facts (the three official requests and the rendered HTML). The `same-report-full-annual-representation-json-evidence-controller-judgment-20260615.md` establishes the testing principle requiring full representation JSON, and this evidence follows that controller-established scope. The provenance is adequate but could be more explicit about the fact-collection delegation.

### 7. Any blocker requiring artifact rewrite before controller acceptance?

**NO.** The two findings below are non-blocking documentation residuals that do not invalidate the evidence artifact.

## Findings

### 1-未修复-低-证据文档 Section 4 summary_metrics 表中字段名与 JSON 实际字段名不一致

- **入口/函数**: 证据文档 Section 4 "Extracted Render Structure" summary metrics 表
- **文件(行号)**: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-20260615.md`, Section 4 table
- **输入场景**: 读者对比证据文档 summary metrics 表与 JSON `summary_metrics` 字段
- **实际分支**: 证据文档表中列出的字段名如 `html bytes`, `navigation labels`, `heading candidates`, `paragraph blocks`, `tables`, `table cells`, `target table candidates` 是语义描述，而非 JSON 中的实际键名（`html_byte_size`, `navigation_label_count`, `heading_candidate_count`, `paragraph_block_count`, `table_count`, `table_cell_count`, `target_table_candidate_count`）
- **预期行为**: 证据文档 summary metrics 表应使用与 JSON `summary_metrics` 一致的字段名，或明确标注为语义映射
- **实际行为**: 表中使用语义描述名，可能导致读者在 JSON 中搜索对应字段时产生混淆
- **直接证据**: JSON `summary_metrics` 键为 `html_byte_size`（非 `html bytes`）、`navigation_label_count`（非 `navigation labels`）等；证据文档表中使用后者
- **影响**: 仅影响文档可读性，不影响证据有效性或 JSON 内容正确性
- **建议改法和验证点**: 未来证据文档 summary metrics 表应使用 JSON 实际键名，或添加"JSON field name"列
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 2-未修复-低-AgentCodex 阻断和 controller 收集 live facts 的 provenance 描述可更明确

- **入口/函数**: 证据文档 Role 字段和 Section 1 Scope
- **文件(行号)**: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-20260615.md`, lines 7-8 and Section 1
- **输入场景**: 读者需要理解该证据的 provenance：为什么由 controller 执行而非 AgentCodex
- **实际分支**: Role 字段提到 "evidence worker fallback executed by controller after AgentCodex approval UI blocked on bounded curl requests"，但未明确说明 controller 直接收集了三个 official requests 的 live facts
- **预期行为**: 证据文档应明确记录 controller 在 AgentCodex 阻断后直接执行了 live fact collection（三个 official requests），而非仅作为 fallback worker
- **实际行为**: 当前描述暗示 controller 是 fallback 执行者，但未明确 controller 是 live facts 的直接收集者
- **直接证据**: 证据文档 Role 字段、Section 2 Official Requests 中的 observed responses 均由 controller 收集
- **影响**: 不影响证据有效性，但 provenance 透明度可进一步提升
- **建议改法和验证点**: Role 字段可改为 "Controller directly collected live facts after AgentCodex network approval UI blocked; this evidence documents controller-gathered observations"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

无。

## Residual Risk

- HTML table count (802) includes layout tables as well as data tables. Evidence Section 7 residual already accepts this; candidate schema must define table filtering.
- HTML has URL/hash/table locators but no PDF page numbers. Evidence Section 7 residual already accepts this.
- Field correctness, taxonomy compatibility, raw XML direct download, production ingestion schema, parser replacement and readiness remain blocked claims per evidence Section 6.

## Verdict

`PASS_WITH_NONBLOCKING_FINDINGS`

No blocker requires artifact rewrite before controller acceptance. The two non-blocking findings are documentation residuals that can be carried as accepted residuals in the controller judgment.

## Required Controller Disposition

| Finding | Recommended Disposition |
|---|---|
| F1: summary_metrics field name mismatch | ACCEPT_AS_NONBLOCKING_RESIDUAL — carry to future evidence documentation standard |
| F2: AgentCodex provenance description | ACCEPT_AS_NONBLOCKING_RESIDUAL — carry to future evidence documentation standard |
