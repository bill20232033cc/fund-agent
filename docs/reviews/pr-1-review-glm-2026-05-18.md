# PR #1 Review (AgentGLM)

> **PR**: https://github.com/bill20232033cc/fund-agent/pull/1
> **Title**: P2 template renderer and evidence anchors
> **Branch**: `chore/reconcile-baseline` → `main`
> **Reviewer**: AgentGLM (independent PR reviewer)
> **Date**: 2026-05-18
> **Base ref**: `a6b1516` (P2-S1–S8 accepted baseline)
> **Head**: `7ab7132` (HEAD, 7 commits)
> **Diff scope**: 20 files, +3167 / −15
> **Design source**: `docs/design.md` §3.1 (8-chapter template), §4.1 (R=A+B-C), §5.2 (MVP audit)
> **Control source**: `docs/implementation-control.md`

---

## Conclusion

**PASS** — No blocking or reviewable issues. The renderer, evidence anchors, audit contract, READMEs, and control doc are correct, boundary-clean, and test-verified. One info-level finding on trailing whitespace in review artifacts; no production code impact.

---

## Findings

### F1. Trailing whitespace in review artifacts — Info

**Severity**: info
**Files**: `docs/reviews/p2-aggregate-fix-2026-05-18.md:3-5`, `docs/reviews/p2-aggregate-review-controller-judgment-2026-05-18.md:3-7`
**Detail**: `git diff --check` reports trailing whitespace on several lines in review markdown artifacts. These are documentation files, not production code. No behavioral impact. Can be cleaned up in a follow-up commit or ignored.

### F2. Cross-slice correctness: Renderer → Audit contract — OK

`render_template_report()` constructs `ProgrammaticAuditInput` at `renderer.py:128-134`, passing exactly the four fields defined in `audit_programmatic.py:79-94`:

| Field | Renderer source | Audit consumer |
|-------|----------------|---------------|
| `report_markdown` | rendered 8-chapter Markdown | P1/P2/P3 structure audit |
| `rabc_attributions` | `input_data.rabc_attributions` | L1 closure audit |
| `checklist_result` | `input_data.checklist_result` | R1 rule audit |
| `final_judgment` | `input_data.final_judgment` | R2 consistency audit |

Test `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` (`test_renderer.py:708-728`) verifies end-to-end: render → build audit input → `run_programmatic_audit` → all 6 rules pass. No cross-slice regression.

### F3. Evidence anchors → P3 audit rule compatibility — OK

P3 audit regex `(证据与出处|📎\s*证据|年报\d{4}§)` at `audit_programmatic.py:24` matches three patterns all emitted by the renderer:
- `## 证据与出处` appendix heading (`renderer.py:419`)
- `> 📎 证据：` body lines (`renderer.py:443-444`)
- `年报{year}§` in both body and appendix references

P3 reliably passes with rendered output.

### F4. Missing data does not mask R=A+B-C or checklist inputs — OK

- Missing values render as `未披露` or `数据不足` (`renderer.py:43-44`), never as empty string or fabricated values.
- Empty `rabc_attributions` triggers explicit `数据不足，缺少可审计的 R=A+B-C 输入` at `renderer.py:248`.
- `current_stage` defaults to `数据不足` at `renderer.py:330`.
- `TemplateRenderInput` is a frozen dataclass; missing structured data is passed as `None` inside `ExtractedField.value` and handled at render time.

### F5. Boundary: Template stays Capability layer — OK

Imports in `renderer.py` are limited to:
- `fund_agent.fund.analysis.*` (P2 analysis result types)
- `fund_agent.fund.audit` (`ProgrammaticAuditInput`)
- `fund_agent.fund.data_extractor` (`StructuredFundDataBundle`)
- `fund_agent.fund.extractors.models` (`EvidenceAnchor`, `ExtractedField`)

No imports from: repository, PDF, filesystem, UI, Service, Engine, Runtime, cache, or document store. Clean Capability-layer boundary.

### F6. Final judgment and wording — OK

- `_validate_final_judgment()` (`renderer.py:943-957`): rejects values outside `{worth_holding, needs_attention, suggest_replace}` with `ValueError`.
- `_validate_report_wording()` (`renderer.py:960-975`): rejects reports containing `买入`, `卖出`, `仓位比例`, or `收益预测`.
- Chapter 7 explicitly states "不预测未来收益，不给出交易或配置指令" (`renderer.py:390`).
- No hidden buy/sell/return-prediction language in any chapter renderer.

### F7. `_validate_report_wording` substring matching — Info (known residual risk)

**Severity**: info
**File**: `renderer.py:973`
**Detail**: `_FORBIDDEN_TERMS` check uses `term in report_markdown` (substring match). Future template phrases like "买入前检查清单" would produce a false positive `ValueError`. Already documented as residual risk in `implementation-control.md`. No action for this PR.

### F8. P2 exit condition checkbox — OK (fixed)

**File**: `implementation-control.md:576`
**Detail**: Previously unchecked. Now correctly shows `- [x]`. The F8 fix from the aggregate review is applied and verified.

### F9. READMEs correctly synced — OK

**`fund_agent/fund/README.md`**:
- Adds `TemplateRenderInput` / `render_template_report` to the import example (`README.md:28`)
- Adds template renderer documentation block covering input contract, output chapters, audit bridge, evidence anchors, and missing data handling (`README.md:164-177`)
- Adds `template/` layer description (`README.md:219`), replacing stale placeholder `template/：后续模板能力的扩展位置`
- Adds current boundary note for `renderer.py` (`README.md:242`)

**`tests/README.md`**:
- Adds `test_renderer.py` entry with coverage description (`README.md:23`)
- Adds `pytest` command (`README.md:48`)
- Adds test convention note requiring structural coverage beyond string-existence smoke tests (`README.md:75`)

Both READMEs are current and consistent with the implementation.

### F10. `__init__.py` re-exports — OK

**File**: `fund_agent/fund/template/__init__.py`
**Detail**: Exports `TemplateFinalJudgment`, `TemplateRenderInput`, `TemplateRenderResult`, `build_programmatic_audit_input`, `render_template_report`. All five symbols are defined in `renderer.py` and listed in `__all__`. No missing or stale exports.

### F11. Review artifacts and control doc coherence — OK

**Files**: `docs/implementation-control.md`, `docs/reviews/p2-s9-*`, `docs/reviews/p2-s10-*`, `docs/reviews/p2-aggregate-*`
**Detail**:
- `implementation-control.md` correctly records: current gate `ready-to-open-draft-PR`, P2-S9 accepted commit `bf64b0f`, P2-S10 accepted commit `2d041ae`, aggregate review passed.
- All review artifacts referenced in the control doc exist on disk.
- P2 phase status updated to `✅ done`.
- Residual risks correctly attributed to P3-S4, v2, and later template refinement.
- State update log entries for 2026-05-18 are coherent with gate transitions.

---

## Validation Summary

| Lens | Result |
|------|--------|
| Tests: 63/63 pass | template(13) + audit(10) + analysis(40) |
| Renderer → audit contract | Pass — fields match, test confirms |
| Evidence → P3 rule | Pass — all regex patterns present |
| Boundary: no layer violation | Pass — Capability-layer only |
| Evidence: traceable, no masking | Pass — missing data explicit |
| Final judgment: no buy/sell/predict | Pass — validated by code and test |
| `__init__.py` re-exports | Pass — complete and consistent |
| READMEs | Pass — synced with implementation |
| Control doc coherence | Pass — gate, artifacts, risks correct |
| Whitespace (`git diff --check`) | Info — trailing spaces in review artifacts only |

---

## Residual Risks Carried Forward

| ID | Risk | Carried to |
|----|------|-----------|
| RR-1 | `_validate_report_wording` substring false positive | P3/v2 |
| RR-2 | End-to-end CLI report through programmatic audit | P3-S4 |
| RR-3 | Evidence confirmation is chapter-level, not item-level | v2 |
| RR-4 | Trailing whitespace in review artifacts | Follow-up cleanup |

---

## Verdict

**PASS.** PR #1 is ready to merge. Production code (renderer, `__init__.py`, tests) is correct, boundary-clean, and well-tested. Documentation and control artifacts are coherent. The only actionable item is cosmetic trailing whitespace in review artifacts, which has no impact on correctness.
