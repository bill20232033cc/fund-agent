# P12 Aggregate Deepreview — AgentMiMo（2026-05-22）

## Verdict

`PASS`

P12 aggregate diff `ba77e02..HEAD` is complete, correct, and stays inside accepted boundaries. No blocking or non-blocking findings.

## Review Scope

| Item | Value |
|------|-------|
| Base | `ba77e02` |
| Range | `ba77e02..HEAD` |
| Commits | 8 |
| Files changed | 34 |
| Lines | +3964 / -37 |
| Source files | 4 (`item_rules.py`, `renderer.py`, `audit_programmatic.py`, `__init__.py`) |
| Test files | 2 (`test_renderer.py`, `test_audit_programmatic.py`) |
| README files | 2 (`fund_agent/fund/README.md`, `tests/README.md`) |
| Docs/control files | 1 (`docs/implementation-control.md`) |
| Review artifacts | 25 |

## Validation Results

| Check | Result |
|-------|--------|
| `git diff --check ba77e02..HEAD` | passed |
| `pytest tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py` | 83 passed |
| `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py` | 43 passed |
| `ruff check fund_agent/fund/template fund_agent/fund/audit tests/fund/template tests/fund/audit` | passed |
| `pytest` (full suite) | 403 passed |

## Checklist

### 1. ITEM_RULE deterministic renderer/audit compliance — no semantic overclaiming

**PASS.**

- `item_rules.py` maintains 4 conditional rules with typed `TemplateItemRuleDecision` and `TemplateItemRuleAuditContext`.
- `evaluate_template_item_rules()` is deterministic: fund type + explicit facets only, no text inference.
- `renderer.py` consumes decisions via `_resolve_item_rule_decisions()` at `renderer.py:208-229` and `_render_item_rule_segments_for_chapter()` at `renderer.py:440-464`.
- `_render_item_rule_segment()` dispatches to 4 fixed renderers (`renderer.py:467-492`), each producing heading + fixed bullets.
- `audit_programmatic.py` `_audit_item_rule_compliance()` at `audit_programmatic.py:477-524` consumes renderer-produced decisions and checks `RenderedChapterBlock.body_markdown`.
- No claim that renderer proves evidence sufficiency, tracking-error data, or index methodology.

### 2. Renderer and audit consume same ITEM_RULE decision source

**PASS.**

- `render_template_report()` at `renderer.py:126-128` produces `item_rule_decisions` and `item_rule_audit_context`.
- These are passed directly into `ProgrammaticAuditInput` at `renderer.py:157-158`.
- `run_programmatic_audit()` consumes them at `audit_programmatic.py:141-145` without re-deriving.
- Tests confirm `result.item_rule_decisions == result.audit_input.item_rule_decisions` (`test_renderer.py:1037`).

### 3. identity_missing / identity_present / unsupported fund-type — fail-closed/compatible

**PASS.**

- `identity_missing`: `_resolve_item_rule_decisions()` returns `(), "identity_missing"` (`renderer.py:224-225`).
- `identity_present` with missing/unsupported fund type: raises `ValueError` (`renderer.py:227-228`).
- Audit: `identity_missing` + empty decisions = skip ITEM_RULE issue (`audit_programmatic.py:498-499`); `identity_present` + empty decisions = C2 fail (`audit_programmatic.py:500-506`).
- Tests: `test_render_template_report_missing_data_path_is_explicit_and_audit_compatible` (`test_renderer.py:1132-1157`); `test_run_programmatic_audit_skips_missing_decision_issue_for_identity_missing_context` (`test_audit_programmatic.py:389-408`); `test_run_programmatic_audit_detects_identity_present_missing_item_rule_decisions` (`test_audit_programmatic.py:360-386`).

### 4. Conditional segment render/delete is chapter-scoped and marker-based

**PASS.**

- `_render_item_rule_segments_for_chapter()` at `renderer.py:440-464` filters by `decision.chapter_id` and `decision.status`.
- `_audit_item_rule_compliance()` at `audit_programmatic.py:511` indexes blocks by `chapter_id` and calls `rendered_segment_present()` which checks `block.body_markdown` (chapter body only, not global markdown).
- `rendered_segment_present()` at `item_rules.py:320-336` uses literal marker matching against `segment_markers_any`.
- Forbidden markers prevent ordinary prose from being used as segment markers (`item_rules.py:34-36`).
- Test `test_run_programmatic_audit_checks_item_rule_markers_inside_matching_chapter_only` (`test_audit_programmatic.py:526-564`) confirms chapter-scoped checking.

### 5. Multi-anchor provenance does not imply tracking-error/index methodology/constituents data

**PASS.**

- `_item_rule_evidence_bullet()` at `renderer.py:598-617` renders all deduped anchors as provenance references only.
- Segment renderers keep `数据不足` for tracking error (`renderer.py:591`), index methodology and constituents (`renderer.py:513-514`).
- Evidence boundary text format is `- 证据边界：...` (bullet, not `> 📎 证据`), preserving the one-per-chapter evidence line contract.
- P12-S2 controller judgment confirmed: "anchors are provenance display only and do not prove evidence sufficiency."

### 6. FQ5/quality gate semantics not expanded

**PASS.**

- P12 diff does not modify any quality gate file (`quality_gate.py`, `extraction_score.py`, `extraction_snapshot.py`).
- `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py`: 43 passed, no regression.
- FQ5 remains "mismatch block, resolved/not_applicable info" per `docs/design.md` §7.2.

### 7. No Service/UI/CLI/Engine/runtime/documents/source repository/Dayu boundary violation

**PASS.**

- `git diff --name-only ba77e02..HEAD` confirms only Capability layer source, tests, READMEs, control doc, and review artifacts.
- No changes to `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/config/`, `fund_agent/fund/documents/`, `fund_agent/fund/data/`.
- No Dayu runtime, Host, Engine, tool loop, or LLM writing introduced.

### 8. Tests cover render matrix, audit failure paths, evidence boundary paths, docs sync

**PASS.**

- **Render matrix**: `test_render_template_report_applies_item_rule_segments_by_fund_type` parametrized across 6 fund types with expected marker sets (`test_renderer.py:1001-1041`).
- **Audit failure paths**: identity_present missing decisions (`test_audit_programmatic.py:360-386`), render marker missing (`test_audit_programmatic.py:411-446`), deleted marker present (`test_audit_programmatic.py:449-480`), duplicate/unknown/mismatched decisions (`test_audit_programmatic.py:483-523`), chapter-scoped checking (`test_audit_programmatic.py:526-564`).
- **Evidence boundary paths**: multi-anchor dedup (`test_renderer.py:1110-1129`), empty anchor boundary (`test_renderer.py:1081-1107`), concrete anchor references (`test_renderer.py:1043-1078`).
- **Docs sync**: `test_fund_readme_has_single_current_template_layer_entry` (`test_renderer.py:905-925`).

### 9. Residuals have owner/destination; main-branch closeout is reasonable

**PASS.**

| Residual | Owner | In scope? |
|----------|-------|-----------|
| Real tracking-error extraction/calculation | Future extractor slice | No |
| Real index methodology / constituents extraction | Future extractor slice | No |
| Evidence sufficiency / claim matching (E1/E2/E3) | Future evidence-confirm slice | No |
| Long-anchor truncation/grouping | Future display policy slice | No |
| Future ITEM_RULE expansion | Future ITEM_RULE slice | No |
| Chapter-mismatch duplicate C2 noise | Future audit cleanup slice | No |
| RR-13 duplicate `016492` | User / App source | No |
| `docs/repo-audit-20260521.md` | Controller / user | No |

All residuals are documented in `docs/implementation-control.md` and the post-P12-S2 controller judgment. None block P12 closeout.

Main-branch closeout is appropriate because P12 commits are already on `main`; retroactive PR/revert would add risk without improving correctness (per GLM F3 finding in post-P12-S2 controller judgment).

## Diff Scope Verification

- `docs/repo-audit-20260521.md`: **not in diff** (confirmed).
- RR-13 source data (`docs/code_20260519.csv`): **not in diff** (confirmed).
- `tests/fund/template/test_item_rules.py`: **not in diff** (P12-S1 scope section over-listed it; actual test coverage is in `test_renderer.py` and `test_audit_programmatic.py`).
- `fund_agent/fund/template/__init__.py`: **in diff** (exports updated for new item_rule symbols).

## Summary

P12 delivers ITEM_RULE deterministic compliance across two slices:

1. **P12-S1** (`c757036`): Renderer produces ITEM_RULE decisions from `classified_fund_type`, renders/deletes fixed segments in target chapter bodies, and programmatic C2 audits renderer-produced decisions against `RenderedChapterBlock.body_markdown`. Identity-missing path is compatible; unsupported fund type is fail-closed.

2. **P12-S2** (`24a35b4`): ITEM_RULE evidence boundary renders all deduped relevant anchors in one bullet per segment, preserving the one-per-chapter `> 📎 证据` line contract. Empty anchors produce precise insufficient-data text.

Both slices stay inside Fund Capability boundaries, preserve deterministic MVP semantics, and do not expand FQ5/quality gate, Service/UI/CLI, Engine/runtime, or Dayu scope. Full test suite passes at 403.
