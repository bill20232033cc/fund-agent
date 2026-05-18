# P2 Aggregate Deep Review (GLM)

> **Reviewer**: AgentGLM (independent aggregate reviewer)
> **Date**: 2026-05-18
> **Base ref**: a6b1516 (P2-S1–S8 accepted baseline)
> **Head**: HEAD (contains P2-S9 template renderer + P2-S10 evidence anchor labeling + artifacts/docs)
> **Diff scope**: 16 files changed, 2769 insertions, 9 deletions
> **Design source**: `docs/design.md` §3.1 (8-chapter template), §4.1 (R=A+B-C), §5.2 (MVP audit)
> **Control source**: `docs/implementation-control.md`

---

## Conclusion

**PASS** — No blocking issues found. P2-S9 template renderer and P2-S10 evidence anchor labeling are correct, boundary-clean, and compatible with P2-S8 programmatic audit. P2 is ready to exit subject to one minor doc-sync fix and known residual risks carried to P3.

---

## Findings

### F1. Cross-slice correctness: Renderer → Audit contract — OK

`render_template_report()` (renderer.py:97–135) constructs `ProgrammaticAuditInput` at line 128–134, passing exactly the four fields defined in `audit_programmatic.py:79–94`:

| Field | Renderer source | Audit consumer |
|-------|----------------|---------------|
| `report_markdown` | rendered 8-chapter Markdown | P1/P2/P3 structure audit |
| `rabc_attributions` | `input_data.rabc_attributions` | L1 closure audit |
| `checklist_result` | `input_data.checklist_result` | R1 rule audit |
| `final_judgment` | `input_data.final_judgment` | R2 consistency audit |

Test `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` (test_renderer.py:708–728) verifies end-to-end: render → build audit input → `run_programmatic_audit` → all 6 rules pass.

**No cross-slice regression.**

### F2. Evidence anchors → P3 audit rule compatibility — OK

P3 audit checks for evidence markers via regex `(证据与出处|📎\s*证据|年报\d{4}§)` (audit_programmatic.py:24). The renderer emits:
- `## 证据与出处` appendix heading (renderer.py:419)
- `> 📎 证据：` body lines (renderer.py:443–444)
- `年报{year}§` in both body and appendix references

All three patterns are present in rendered output. P3 will reliably pass.

### F3. Missing data does not mask R=A+B-C or checklist inputs — OK

- Missing values render as `未披露` or `数据不足` (renderer.py:43–44), never as empty string or fabricated values.
- `_render_chapter_2` (renderer.py:247–248): when `rabc_attributions` is empty, it explicitly renders `数据不足，缺少可审计的 R=A+B-C 输入`.
- `_render_chapter_5` (renderer.py:330): `current_stage` defaults to `数据不足`.
- `TemplateRenderInput` is a frozen dataclass with all fields typed — no optional fields for required inputs; missing structured data is passed through as `None` inside `ExtractedField.value` and handled at render time.

### F4. Boundary: Template stays Capability layer — OK

Imports in `renderer.py`:
- `fund_agent.fund.analysis.*` (AlphaJudgment, ChecklistResult, ConsistencyCheckResult, InvestorExperienceResult, RabcAttribution, RiskCheckResult, StressTestResult)
- `fund_agent.fund.audit` (ProgrammaticAuditInput)
- `fund_agent.fund.data_extractor` (StructuredFundDataBundle)
- `fund_agent.fund.extractors.models` (EvidenceAnchor, ExtractedField)

No imports from: repository, PDF, filesystem, UI, Service, Engine, Runtime, cache, or document store. Clean Capability-layer boundary.

### F5. Final judgment and wording — OK

- `_validate_final_judgment()` (renderer.py:943–957): rejects any value outside `{worth_holding, needs_attention, suggest_replace}` with `ValueError`.
- `_validate_report_wording()` (renderer.py:960–975): rejects reports containing `买入`, `卖出`, `仓位比例`, or `收益预测`.
- Chapter 7 explicitly states "不预测未来收益，不给出交易或配置指令" (renderer.py:390).
- No hidden buy/sell/return-prediction language found in any chapter renderer.

### F6. Test coverage — Adequate for P2 aggregate readiness

| Suite | Count | Status |
|-------|-------|--------|
| tests/fund/template/test_renderer.py | 13 | All pass |
| tests/fund/audit/test_audit_programmatic.py | 10 | All pass |
| tests/fund/analysis/* | 40 | All pass |
| **Total** | **63** | **All pass** |

Template tests specifically cover:
- 8-chapter structural completeness
- Evidence anchor body format (year + section + description)
- Evidence anchor appendix format (year + section + table + row)
- Missing row/table fallback without dropping year or section
- Page number metadata preservation
- Non-annual source kind explicit labeling
- Missing evidence per chapter (body + appendix)
- `dict_values(...)` leak regression
- Punctuation duplication regression
- README consistency (no stale entries)
- Full render → audit → pass end-to-end
- Missing data path with audit compatibility
- Unsafe final judgment rejection
- Forbidden wording absence
- L1/R1/R2 structured input pass-through

### F7. `_validate_report_wording` substring matching — Info (known residual risk)

**Severity**: info
**File**: `fund_agent/fund/template/renderer.py:973`
**Detail**: `_FORBIDDEN_TERMS` check uses `term in report_markdown` (substring match). If a future template legitimately contains phrases like "买入前检查清单", this would produce a false positive `ValueError`. Already documented as residual risk RR-template-wording in implementation-control.md. No action needed for P2.

### F8. P2 exit condition checkbox not synced — Info

**Severity**: info
**File**: `docs/implementation-control.md:568`
**Detail**: The P2 exit condition `- [ ] fund/template/renderer.py 能将数据填充到定性模板 v2` remains unchecked, even though the renderer is fully implemented and tested. Should be updated to `- [x]` when P2 exits. Non-blocking.

---

## Validation Summary

| Lens | Result |
|------|--------|
| Cross-slice: renderer ↔ audit | Pass — contract fields match, test confirms end-to-end |
| Cross-slice: evidence → P3 rule | Pass — all three regex patterns present in output |
| Boundary: no layer violation | Pass — only Capability-layer imports |
| Evidence: traceable, no masking | Pass — missing data explicitly rendered |
| Final judgment: no buy/sell/predict | Pass — validated by code and test |
| Tests: meaningful coverage | Pass — 13 template + 10 audit + 40 analysis = 63 pass |
| Docs/control coherence | Pass — gate, artifacts, risks correctly recorded |

---

## Residual Risks Carried Forward

| ID | Risk | Carried to | Notes |
|----|------|-----------|-------|
| RR-1 | `_validate_report_wording` substring false positive | P3/v2 | Already documented; low impact |
| RR-2 | End-to-end CLI report through programmatic audit | P3-S4 | P3 scope |
| RR-3 | Evidence confirmation is chapter-level, not item-level | v2 | Design gap, not regression |
| RR-4 | P2 exit condition checkbox unchecked | P2 exit | Doc sync only |

---

## Verdict

**PASS.** P2-S1 through P2-S10 are internally consistent, boundary-clean, and test-verified. No blocking or reviewable issues found. P2 is ready to exit to P3 upon updating the exit condition checkbox and recording the aggregate review gate.
