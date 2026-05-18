# P2-S10 Code Review — AgentMiMo

## Gate

- Gate: `P2-S10 code review`
- Date: 2026-05-18
- Worker: AgentMiMo
- Scope: Capability template renderer evidence anchor labeling

## Review Inputs

- Design source: `docs/design.md` section 5.4 (evidence anchor format)
- Control source: `docs/implementation-control.md` P2-S10
- Implementation artifact: `docs/reviews/p2-s10-implementation-2026-05-18.md`
- Target files:
  - `fund_agent/fund/template/renderer.py`
  - `tests/fund/template/test_renderer.py`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Validation

```bash
.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q
```

Result: `23 passed in 0.50s`

```bash
.venv/bin/python -m pytest tests/fund/analysis -q
```

Result: `40 passed in 0.41s`

## Review Findings

### 1. Body evidence lines include traceable source with year and section

**PASS.** `_body_anchor_reference()` (renderer.py:447-467) correctly outputs `年报{year}§{section} {description}` for annual report anchors. Year uses `document_year` with explicit `"未知年份"` fallback when `None`. Section uses `_section_text()` which strips leading `§` to avoid double-prefix. Page metadata is appended as `（第N页）` before description.

Test coverage: `test_render_template_report_formats_evidence_anchors_with_year_section_and_optional_row` (test_renderer.py:533-549) asserts `年报2024§1` presence and absence of bare `年报§1`.

### 2. Appendix annual report anchors preserve year, section, table id, row locator, page metadata, and explicit fallback

**PASS.** `_anchor_reference()` (renderer.py:470-491) follows `年报{year}§{section}表{table_id}行{row_locator}{page_part}{note_part}` format. Missing `table_id` renders as `表未定位`, missing `row_locator` as `行未定位`, missing `document_year` as `未知年份`. All location fields are preserved in order; none is silently dropped.

Test coverage:
- `test_render_template_report_formats_appendix_anchor_with_table_and_row_exactly` (test_renderer.py:552-569) asserts `年报2024§8表T1行industry_distribution`.
- `test_render_template_report_formats_missing_row_fallback_without_dropping_year_or_section` (test_renderer.py:571-587) asserts `年报2024§1表未定位行未定位`.
- `test_render_template_report_retains_page_number_as_location_metadata` (test_renderer.py:589-609) asserts `（第18页）` appears in both body and appendix.

### 3. Non-annual sources are labeled explicitly and not rendered as annual report

**PASS.** `_source_kind_label()` (renderer.py:535-548) maps known kinds to explicit labels (`外部数据(external_api)`, `计算(derived)`) and uses `未知来源({kind})` fallback for unknown kinds. Both `_body_anchor_reference()` and `_non_annual_anchor_reference()` use this label instead of annual report format.

Test coverage: `test_render_template_report_renders_non_annual_source_kind_explicitly` (test_renderer.py:612-639) asserts `外部数据(external_api)§nav_return` appears and `年报2024§nav_return` does not appear.

### 4. Missing chapter evidence is explicit in both body and appendix

**PASS.**
- Body: `_evidence_line()` (renderer.py:429-444) returns `> 📎 证据：数据不足，当前章节未携带证据锚点` when `anchors` is empty.
- Appendix: `_missing_anchor_reference()` (renderer.py:514-532) outputs `年报{year}§未定位表未定位行未定位：数据不足，模板第N章《{title}》当前输入未携带证据锚点。`
- Chapter evidence groups in `_render_evidence_section()` (renderer.py:400-426) iterate all 8 groups; empty groups emit `[M{index}]` entries.

Test coverage: `test_render_template_report_emits_missing_evidence_line_and_appendix_entry_per_chapter` (test_renderer.py:642-662) asserts both body `数据不足` line and appendix `[M2]` entry with chapter title.

### 5. run_programmatic_audit compatibility preserved and tests meaningful

**PASS.**
- `TemplateRenderResult.audit_input` carries `report_markdown`, `rabc_attributions`, `checklist_result`, `final_judgment` (renderer.py:126-134).
- `build_programmatic_audit_input()` returns `render_result.audit_input` directly (renderer.py:138-151).
- Tests verify: full-data audit passes with exact rule set `(P1, P2, P3, L1, R1, R2)`, missing-data audit passes, structured inputs pass through unmodified, unsafe `final_judgment` is rejected at render time.

Test coverage: `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` (test_renderer.py:708-728), `test_render_template_report_missing_data_path_is_explicit_and_audit_compatible` (test_renderer.py:731-751), `test_render_template_report_keeps_l1_r1_r2_structured_inputs_unmodified` (test_renderer.py:790-812).

### 6. Boundary: renderer remains Capability layer

**PASS.** Renderer imports only from:
- `fund_agent.fund.analysis.*` (Capability analysis modules)
- `fund_agent.fund.audit` (Capability audit module)
- `fund_agent.fund.data_extractor` (Capability data extractor)
- `fund_agent.fund.extractors.models` (Capability models)

No imports from `documents/`, `pdf/`, `ui/`, `services/`, `engine/`, `config/`, `dayu.*`, `pathlib`, `os`, or any file/network I/O. The renderer is a pure function consuming structured data.

### 7. AGENTS requirements

**PASS.**
- **Chinese docstrings**: All functions have complete Chinese docstrings with Args/Returns/Raises. Module docstring in Chinese. (renderer.py:1-6 and all function docstrings)
- **Template chapter references**: Module docstring references `docs/design.md` 第 3.1 节. Each `_render_chapter_N()` docstring references the corresponding chapter number and title.
- **Evidence traceability**: `_FORBIDDEN_TERMS` constant (renderer.py:42) and `_validate_report_wording()` (renderer.py:960-975) enforce no buy/sell wording. All rendered evidence lines use `_evidence_line()` which traces to anchors.
- **No buy/sell wording**: `test_render_template_report_does_not_emit_buy_sell_wording` (test_renderer.py:770-787) and `test_render_template_report_rejects_unsafe_final_judgment_wording` (test_renderer.py:753-767) enforce this.

### 8. README consistency

**PASS.**
- `fund_agent/fund/README.md` line 219 has a single canonical entry for `template/` describing the renderer as consuming P1/P2 structured results and outputting 8 chapters + audit input. No duplicate or stale entries.
- `tests/README.md` line 23 correctly describes template renderer test coverage scope.

Test coverage: `test_fund_readme_has_single_current_template_layer_entry` (test_renderer.py:685-705).

## Conclusion

**PASS.** No blocking issues found. All review lenses satisfied. Implementation correctly standardizes body and appendix evidence anchor formatting per `docs/design.md` section 5.4. Non-annual sources are explicitly labeled. Missing evidence is explicit in both body and appendix. Boundary is preserved. All 63 validation tests pass (23 template+audit, 40 analysis).

## Residual Risks

1. Non-annual source labels currently cover `external_api` and `derived` only. Future `EvidenceSourceKind` expansions need an explicit label entry in `_SOURCE_KIND_LABELS` or will fall through to `未知来源({kind})`.
2. Missing evidence appendix entries are chapter-level, not item-level. Item-level evidence completeness remains a later concern.
3. `_validate_report_wording()` uses substring matching; future template text containing "买入前检查清单" would trigger a false positive. Current code does not have this issue.
