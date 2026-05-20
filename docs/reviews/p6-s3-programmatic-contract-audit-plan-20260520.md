# P6-S3 Programmatic Contract Audit Plan - 2026-05-20

## Verdict

P6-S3 plan accepted after controller review amendments. This slice should add the first deterministic programmatic audit for `CHAPTER_CONTRACT`, using the P6-S1 manifest and P6-S2 rendered chapter blocks. The audit must remain a Capability-layer programmatic check: no LLM call, no PDF evidence re-search, no Service/Engine/UI changes.

下一 gate：`P6-S3 implementation`。

## Inputs

- Design truth: `docs/design.md`
- P4/P5/P6 control context: `docs/implementation-control-p4.md`
- P6 backlog: `docs/reviews/post-p5-follow-up-planning-20260520.md`
- P6-S2 plan: `docs/reviews/p6-s2-renderer-contract-alignment-plan-20260520.md`
- P6-S2 accepted judgment: `docs/reviews/p6-s2-code-review-controller-judgment-20260520.md`
- Current code facts:
  - `fund_agent/fund/template/contracts.py`
  - `fund_agent/fund/template/renderer.py`
  - `fund_agent/fund/template/__init__.py`
  - `fund_agent/fund/audit/audit_programmatic.py`
  - `tests/fund/template/test_renderer.py`
  - `tests/fund/audit/test_audit_programmatic.py`

## Problem Statement

P6-S1 made `CHAPTER_CONTRACT` machine-readable. P6-S2 made renderer chapter headings and `RenderedChapterBlock` contract-aligned. The remaining gap is that `run_programmatic_audit(...)` still validates only coarse report structure, global evidence marker presence, R=A+B-C closure, checklist rules, and final judgment consistency. It does not inspect the manifest contract attached to each rendered chapter.

Current audit risks:

- `_REQUIRED_CHAPTER_TITLES` in `audit_programmatic.py` is still a separate partial title tuple and can drift from the manifest.
- The audit cannot say whether a rendered chapter contains required output items declared by `ChapterContract.required_output_items`.
- The audit cannot reject deterministic forbidden content declared by `ChapterContract.must_not_cover`, except for the renderer's separate global wording validator.
- P3 only checks that some evidence marker exists somewhere in the report; it does not ensure every template chapter has the minimum evidence line shape.
- P6-S3 cannot import current `renderer.py` from `audit_programmatic.py` directly, because `renderer.py` already imports `ProgrammaticAuditInput` from `fund_agent.fund.audit`, creating an import cycle.

P6-S3 should close these gaps in the programmatic audit layer while keeping the scope deterministic and narrow.

## Non-goals

P6-S3 must not:

- Implement LLM audit, Evidence Confirm, PDF re-search, or evidence-to-claim matching.
- Implement `ITEM_RULE`.
- Upgrade quality gate FQ5 or change score/quality gate behavior.
- Change Service, Engine, UI, CLI, extraction, fund type recognition, document repository, or annual report access.
- Access fund documents directly from filesystem. This slice should not read annual report PDFs at all; if future evidence validation needs documents, it must go through the unified document repository interface.
- Put explicit parameters into `extra_payload`; any new audit input must be an explicit typed field.
- Pretend to understand semantic requirements with keyword NLP. Required item and forbidden-content checks must be based on deterministic marker rules.
- Treat P6-S3 as a broad report rewrite. Renderer changes are allowed only where needed to make current report output explicitly expose required item labels for deterministic audit.

## Architecture And Dependency Direction

### Current dependency issue

Current direction:

```text
renderer.py -> fund_agent.fund.audit.ProgrammaticAuditInput
```

If P6-S3 makes `audit_programmatic.py` import `RenderedChapterBlock` or `split_rendered_chapter_blocks(...)` from `renderer.py`, the dependency becomes cyclic:

```text
renderer.py -> audit -> audit_programmatic.py -> renderer.py
```

### Required dependency direction

Move renderer-independent chapter block contracts into a new template helper module:

```text
contracts.py
  ↑
chapter_blocks.py
  ↑              ↑
renderer.py      audit_programmatic.py
```

Plan:

- Add `fund_agent/fund/template/chapter_blocks.py`.
- Move or re-home these public surfaces from `renderer.py` into `chapter_blocks.py`:
  - `RenderedChapterBlock`
  - `get_template_chapter_heading(chapter_id)`
  - `split_rendered_chapter_blocks(report_markdown)`
- `chapter_blocks.py` imports only `ChapterContract` / `get_chapter_contract` from `contracts.py`.
- `renderer.py` imports these public helpers from `chapter_blocks.py`.
- `audit_programmatic.py` imports these public helpers from `chapter_blocks.py`.
- `fund_agent/fund/template/__init__.py` continues to export the same public names, so existing callers do not need to change import paths.

This keeps the contract and parsing helper in Capability `template/`, avoids audit-renderer cycles, and keeps Service/UI out of the slice.

## Public Contract Changes

### `ProgrammaticAuditInput`

Add an explicit field after the existing fields:

```python
chapter_blocks: tuple[RenderedChapterBlock, ...] = ()
```

Rationale:

- P6-S2 already computes exact rendered chapter blocks in `render_template_report(...)`.
- Passing them explicitly avoids reparsing in the common renderer path.
- The field is explicit and typed; no `extra_payload`.
- The default empty tuple preserves direct test construction and external callers.

Audit behavior:

- If `chapter_blocks` is provided, audit uses it.
- If `chapter_blocks` is empty and `report_markdown` is present, audit tries `split_rendered_chapter_blocks(report_markdown)`.
- If splitting fails, audit records a P1 issue instead of raising.
- If `report_markdown` is missing, contract audit is skipped after required-input issues are recorded.

Renderer behavior:

- `render_template_report(...)` should keep computing `chapter_blocks` from final `report_markdown`.
- `ProgrammaticAuditInput(...)` constructed by renderer should receive `chapter_blocks=chapter_blocks`.
- Existing fields `report_markdown`, `rabc_attributions`, `checklist_result`, and `final_judgment` keep the same meaning.

### `ProgrammaticAuditResult.checked_rules`

Add `C2` to the checked rules after P3:

```python
("P1", "P2", "P3", "C2", "L1", "R1", "R2")
```

Tests that assert checked rules must be updated.

### Design truth sync

P6-S3 accepts `C2` only as a deterministic `CHAPTER_CONTRACT` subset:

- implemented now: exact required-item markers, exact forbidden markers, and chapter/contract metadata consistency
- still v2: semantic chapter overreach, hallucination, evidence-to-claim match, repair contracts, and LLM audit

Implementation must update `docs/design.md` 第 5.2 节 to reflect this split. The table should no longer imply that all C2 remains v2-only. The safe wording is: MVP implements deterministic C2 subset in programmatic audit; semantic C2 remains v2 and low-priority/patch-oriented once repair semantics exist.

## Audit Rule Code Choice

Use two existing rule families:

- `P3` remains the evidence-presence rule and should be extended from global evidence marker presence to per-chapter minimum evidence line presence.
- Add `C2` for deterministic `CHAPTER_CONTRACT` conformance:
  - required output item marker missing
  - deterministic forbidden phrase / forbidden heading present
  - rendered chapter contract mismatch

Why not `E1/E2/E3`:

- E-rules imply evidence precision, evidence-to-claim match, or full evidence absence.
- P6-S3 explicitly does not re-search PDFs or confirm evidence. Per-chapter evidence line shape is still a programmatic structure check, so it belongs under P3.

Why not overload `P1/P2`:

- P1/P2 are coarse Markdown structure and content length checks.
- Missing a required output item is a contract violation even if the chapter exists and is long enough.

Why `C2`:

- `docs/design.md` defines C2 as chapter boundary / forbidden-topic overreach.
- P6-S3 is the first deterministic subset of that concept: no semantic LLM judgment, only manifest-linked required/forbidden marker checks.
- `C1` is hallucination/content truthfulness and remains v2.

Severity:

- Current `ProgrammaticAuditResult.passed` is `False` whenever any issue exists, regardless of severity.
- P6-S3 should emit `severity="blocker"` for deterministic C2 failures because the current gate has no warning-only pass semantics.
- Do not add new severity semantics in this slice.

## Deterministic Interpretation Rules

The manifest remains the source of chapter ids, titles, `required_output_items`, and `must_not_cover`. P6-S3 must add a deterministic interpretation layer for the current renderer output. This layer must never claim semantic NLP coverage.

### Required Output Items

Add an audit-owned mapping from each manifest `required_output_items` entry to literal markers expected in the rendered chapter body.

Recommended shape in `fund_agent/fund/audit/contract_rules.py`:

```python
@dataclass(frozen=True, slots=True)
class ContractRequiredItemRule:
    chapter_id: int
    item_text: str
    markers_any: tuple[str, ...]
```

Rules:

- `chapter_id` must exist in `load_template_contract_manifest()`.
- `item_text` must exactly match one item in that chapter's `required_output_items`.
- `markers_any` must be non-empty.
- An item passes if any marker appears as a literal substring in `RenderedChapterBlock.body_markdown`.
- Matching is case-sensitive and Chinese punctuation-sensitive. Do not tokenize or infer synonyms.
- If a required item cannot be checked without semantic interpretation, the implementation must make the renderer expose an explicit deterministic label instead of weakening the audit.

Renderer implication:

- Current renderer output is an MVP prose fill and may not expose every required item label literally.
- P6-S3 implementation may add minimal explicit bullet labels / `数据不足` placeholders to renderer chapters so every `required_output_items` entry has a deterministic marker.
- This must be a narrow renderer adjustment, not a prose rewrite. It should not add new data sources or infer unavailable facts.
- Existing no-trading-advice and no-future-return constraints must still pass.

Example acceptable renderer adjustment:

```text
- 盈利投资者占比：数据不足，当前公开输入未提供该字段。
```

This is acceptable because it exposes a required output item and explicitly marks missing data without pretending to know the value.

#### Required Item Marker Matrix

The following matrix is binding for P6-S3 implementation. `markers_any` are literal substrings. `already-rendered` means the current renderer already emits the marker or equivalent stable phrase. `renderer-label-needed` means implementation may add only the listed label or an explicit `数据不足` placeholder for that item; it must not rewrite the chapter narrative more broadly.

| chapter | required item | markers_any | source |
|---:|---|---|---|
| 0 | 一句话这是什么基金 | `基金：` | already-rendered |
| 0 | 基金简介 | `基金：` | already-rendered |
| 0 | 当前动作（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换） | `最终判断：` | already-rendered |
| 0 | 当前业绩与运作状态 | `当前业绩与运作状态：` | renderer-label-needed |
| 0 | 支撑当前动作的最主要理由 | `支撑当前动作的最主要理由：` | renderer-label-needed |
| 0 | 当前最值得盯住的变量 | `当前最值得盯住的变量：` | renderer-label-needed |
| 0 | 当前最大的风险 | `当前最大的风险：` | renderer-label-needed |
| 0 | 下一步最小验证问题 | `下一步最小验证问题：` | already-rendered |
| 0 | 什么变化会升级、降级或终止当前动作 | `什么变化会升级、降级或终止当前动作：` | renderer-label-needed |
| 1 | 基金类型与分类标签 | `基金类型与分类标签：` | renderer-label-needed |
| 1 | 投资目标（一句话） | `投资目标（一句话）：` | renderer-label-needed |
| 1 | 投资策略概述 | `投资策略概述：` | renderer-label-needed |
| 1 | 业绩基准及合理性 | `业绩基准及合理性：` | renderer-label-needed |
| 1 | 看这类基金最先看什么 | `看这类基金最先看什么：` | renderer-label-needed |
| 1 | 会改变产品理解的特别情况（如有） | `会改变产品理解的特别情况：` | renderer-label-needed |
| 2 | 近 1/3/5 年净值增长率 | `近 1/3/5 年净值增长率：` | renderer-label-needed |
| 2 | 近 1/3/5 年业绩基准收益率 | `近 1/3/5 年业绩基准收益率：` | renderer-label-needed |
| 2 | 超额收益（A = R - B）及稳定性 | `超额收益（A = R - B）及稳定性：` | renderer-label-needed |
| 2 | 超额收益性质判断（结构性 vs 阶段性） | `超额收益性质：` | already-rendered |
| 2 | 成本拆解（管理费、托管费、交易成本） | `成本拆解：` | renderer-label-needed |
| 2 | 成本合理性判断（同类对比） | `成本合理性判断：` | renderer-label-needed |
| 2 | R=A+B-C 综合评估 | `R=A+B-C 综合评估：` | renderer-label-needed |
| 3 | 基金经理基本信息 | `基金经理基本信息：` | renderer-label-needed |
| 3 | 宣称的投资策略（§4） | `宣称的投资策略（§4）：` | renderer-label-needed |
| 3 | 实际投资行为（§8） | `实际投资行为（§8）：` | renderer-label-needed |
| 3 | 言行一致性判断 | `言行一致性判断：` | renderer-label-needed |
| 3 | 风格稳定性判断 | `风格稳定性判断：` | renderer-label-needed |
| 3 | 利益一致性判断 | `利益一致性判断：` | renderer-label-needed |
| 4 | 基金产品收益 vs 投资者实际收益 | `基金产品收益 vs 投资者实际收益：` | renderer-label-needed |
| 4 | 盈利投资者占比 | `盈利投资者占比：` | renderer-label-needed |
| 4 | 行为损益估算 | `行为损益估算：` | renderer-label-needed |
| 4 | 份额变动趋势 | `份额变动趋势：` | renderer-label-needed |
| 5 | 过去一年最关键的变化（1-3 个） | `过去一年最关键的变化：` | renderer-label-needed |
| 5 | 基金当前所处阶段 | `基金当前所处阶段：` | renderer-label-needed |
| 5 | 变化是否改变前文判断 | `变化是否改变前文判断：` | renderer-label-needed |
| 5 | 接下来最该跟踪的变量 | `接下来最该跟踪的变量：` | renderer-label-needed |
| 6 | 最关键的风险或否决项 | `最关键的风险或否决项：` | renderer-label-needed |
| 6 | 为什么足以改变结论 | `为什么足以改变结论：` | renderer-label-needed |
| 6 | 否决 vs 跟踪判断 | `否决 vs 跟踪判断：` | renderer-label-needed |
| 6 | 下一轮先验证什么 | `下一轮先验证什么：` | renderer-label-needed |
| 7 | 最终判断（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换） | `最终判断：` | already-rendered |
| 7 | 支撑判断的核心依据（1-2 条） | `支撑判断的核心依据：` | renderer-label-needed |
| 7 | 当前最容易看错的地方 | `当前最容易看错的地方：` | renderer-label-needed |
| 7 | 下一轮最小验证计划 | `下一轮最小验证计划：` | renderer-label-needed |
| 7 | 危级/降级阈值 | `危级/降级阈值：` | renderer-label-needed |

The source typo `危级/降级阈值` is intentionally preserved in P6-S3 because it is already tracked as RR-19. Do not silently rename it in the rule matrix, or the audit will drift from the manifest.

### Must-not-cover

Add an audit-owned mapping from deterministically enforceable `must_not_cover` entries to literal forbidden markers.

Recommended shape:

```python
@dataclass(frozen=True, slots=True)
class ContractForbiddenContentRule:
    chapter_id: int
    item_text: str
    forbidden_markers_any: tuple[str, ...]
```

Rules:

- `chapter_id` and `item_text` must validate against the manifest.
- A rule fails if any forbidden marker appears in that chapter's `body_markdown`.
- Do not infer whether a chapter is "too much summary", "too many reasons", "all possible risks", or "market competition analysis" unless there is an exact deterministic marker.
- For P6-S3, include only deterministic markers such as:
  - chapter 0: `证据与出处` inside chapter body
  - chapter 2: `未来收益预测`
  - chapter 3: `性格`, `人品`, `动机`
  - chapter 4: `具体投资者的交易行为`, `未来投资者行为预测`
  - chapter 5: `市场整体走势预测`
  - chapter 6: `风险发生概率`
  - chapter 7: `买入金额`, `卖出时机`, `仓位比例`

The rule mapping should be deliberately small. The purpose is deterministic safety, not natural-language compliance scoring.

### Minimum Evidence Rules

Extend P3 with per-chapter minimum evidence checks using `RenderedChapterBlock.body_markdown`.

Rules:

- Every chapter block must contain a line starting with `> 📎 证据：`.
- The global report must still contain `## 证据与出处`.
- Chapter 7 body must not include the appendix; this is already guaranteed by P6-S2 splitter tests, but P3 should fail if a block contains `## 证据与出处`.
- A data-insufficient evidence line is acceptable for P6-S3 if it uses the standard form:
  - `> 📎 证据：数据不足，当前章节未携带证据锚点`
- P6-S3 must not decide whether the evidence actually supports each claim; that is E1/E2/E3 v2.

### Contract Consistency

Contract audit should verify each block is internally consistent:

- `block.chapter_id == block.contract.chapter_id`
- `block.title == block.contract.title`
- `block.heading == get_template_chapter_heading(block.chapter_id)`
- The block sequence is exactly 0..7. If blocks came from splitter, this should already hold; audit should still fail closed if explicit `chapter_blocks` are malformed.

Failures should be C2 unless the issue is pure Markdown structure/splitting failure, which should remain P1.

## File-level Implementation Plan

### Step A. Behavior-preserving chapter block extraction

Step A must be implemented and verified before adding C2/P3 behavior changes. It should be a pure dependency-direction cleanup.

### 1. Add shared chapter block module

File: `fund_agent/fund/template/chapter_blocks.py`

Move from `renderer.py`:

- `RenderedChapterBlock`
- `get_template_chapter_heading`
- `split_rendered_chapter_blocks`
- private splitter helpers and regex constants

Keep all new/modified functions and classes with full Chinese docstrings. Keep the appendix-boundary inline comment.

### 2. Update renderer imports without behavior change

File: `fund_agent/fund/template/renderer.py`

- Remove local `RenderedChapterBlock` / splitter definitions after moving them.
- Import `get_template_chapter_heading`, `RenderedChapterBlock`, and `split_rendered_chapter_blocks` from `fund_agent.fund.template.chapter_blocks`.
- Keep `TemplateRenderResult.chapter_blocks` unchanged.

Verification before Step B:

```bash
.venv/bin/python -m pytest tests/fund/template/test_renderer.py -q
```

Implementation summary must separately report this step and confirm there was no intentional output behavior change.

### 3. Preserve template public exports

File: `fund_agent/fund/template/__init__.py`

- Continue exporting:
  - `RenderedChapterBlock`
  - `get_template_chapter_heading`
  - `split_rendered_chapter_blocks`
- Source them from `chapter_blocks.py`.

### Step B. Contract audit behavior changes

### 4. Add deterministic contract rule definitions

File: `fund_agent/fund/audit/contract_rules.py`

Add:

- `ContractRequiredItemRule`
- `ContractForbiddenContentRule`
- `load_programmatic_contract_rules()`
- `validate_programmatic_contract_rules(...)`

Validation must fail closed when:

- a rule references an unknown chapter id
- a required item text is not present in the manifest chapter's `required_output_items`
- a forbidden item text is not present in the manifest chapter's `must_not_cover`
- a marker tuple is empty
- a manifest required output item has no rule

This makes `required_output_items` coverage complete while keeping semantic interpretation explicit and auditable.

### 5. Update programmatic audit

File: `fund_agent/fund/audit/audit_programmatic.py`

Changes:

- Extend `AuditRuleCode` with `"C2"`.
- Add `chapter_blocks` field to `ProgrammaticAuditInput`.
- Replace or derive `_REQUIRED_CHAPTER_TITLES` from `load_template_contract_manifest()` so P1 no longer owns a second manual title source.
- Add `_resolve_chapter_blocks_for_audit(input_data)`:
  - prefer explicit `input_data.chapter_blocks`
  - otherwise split `input_data.report_markdown`
  - catch `ValueError` and return a P1 issue plus no blocks
- Extend `_audit_report_structure(...)` or add `_audit_minimum_chapter_evidence(...)` so P3 checks every chapter block has the standard evidence line.
- Add `_audit_contract_conformance(chapter_blocks)` returning C2 issues:
  - block-contract metadata consistency
  - required output item markers
  - forbidden markers
- Ensure `run_programmatic_audit(...)` includes these checks and reports checked rules as `("P1", "P2", "P3", "C2", "L1", "R1", "R2")`.

Do not import `renderer.py`.

### 6. Update renderer audit input and minimal markers

File: `fund_agent/fund/template/renderer.py`

- Pass `chapter_blocks=chapter_blocks` into `ProgrammaticAuditInput(...)`.
- Add only the `renderer-label-needed` markers listed in `Required Item Marker Matrix`.
- Missing data must be explicit as `数据不足` / `未披露` / `未定位`; do not infer unavailable values.
- Do not introduce buying/selling instructions, future return predictions, or new document reads.

### 7. Update audit public exports only if needed

File: `fund_agent/fund/audit/__init__.py`

- No export is required for private rule helpers.
- If implementation exposes rule dataclasses for tests, export only if there is a clear public need. Prefer testing through `run_programmatic_audit(...)` and keeping rules private.

### 8. Update tests

Files:

- `tests/fund/audit/test_audit_programmatic.py`
- `tests/fund/template/test_renderer.py`
- `tests/fund/template/test_contracts.py` only if export/helper coverage is needed
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`

Required test updates/additions:

1. Checked rules compatibility
   - Update existing assertions from `("P1", "P2", "P3", "L1", "R1", "R2")` to include `"C2"`.

2. Renderer output passes new audit
   - Existing renderer audit compatibility tests must still pass.
   - If renderer bullets are adjusted for deterministic item labels, keep existing evidence and forbidden-wording assertions.

3. Required output item failure
   - Start from a valid rendered report.
   - Remove a deterministic required item marker from one chapter.
   - Re-split blocks or pass explicit mutated blocks.
   - Assert `run_programmatic_audit(...)` returns a C2 issue with location including chapter id and item text.

4. Forbidden content failure
   - Inject a deterministic forbidden marker into a chapter body, for example chapter 7 `买入金额`.
   - Assert C2 issue with location including the chapter id.

5. Per-chapter evidence failure
   - Remove one chapter's `> 📎 证据：` line.
   - Assert P3 issue identifying that chapter.

6. Splitter fallback and explicit blocks
   - Audit with explicit `chapter_blocks` and confirm no reparsing-specific failure.
   - Audit with only `report_markdown` and confirm it can split and run contract audit.

7. Malformed report does not crash audit
   - Insert a non-template top-level heading into an otherwise valid report.
   - Assert audit records P1 instead of raising.

8. Rule mapping validation
   - Test that the programmatic contract rule set covers every `required_output_items` entry.
   - Test that a deliberately invalid rule fixture referencing an unknown required item fails validation.
   - Test that at least one `renderer-label-needed` marker appears in current renderer output, so the implementation cannot satisfy coverage only by weakening audit rules.

### 9. Update docs after tests pass

Files:

- `docs/design.md`
  - Update 第 5.2 节 so C2 is split into deterministic programmatic subset implemented in MVP and semantic C2 remaining v2.
  - Keep C1 hallucination and E1/E2/E3 as v2.

- `fund_agent/fund/README.md`
  - Add `C2` to the programmatic audit rule list.
  - State that P3 now checks per-chapter minimum evidence line presence.
  - State that C2 is deterministic `CHAPTER_CONTRACT` conformance based on explicit markers, not LLM semantic audit.
  - State that audit consumes `chapter_blocks` when available and can split `report_markdown` as fallback.

- `tests/README.md`
  - Update audit test coverage to include C2, required output item markers, forbidden content, per-chapter evidence, and malformed chapter block fallback.

Do not update control docs in implementation unless the controller explicitly asks after acceptance.

## Acceptance Commands

Implementation should run and report:

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

If renderer output is adjusted, also manually inspect `git diff -- fund_agent/fund/template/renderer.py` to confirm changes are limited to explicit item labels / missing-data placeholders and do not introduce buying/selling instructions or future return predictions.

Implementation summary must report Step A and Step B separately. If Step A fails, stop before C2/P3 behavior changes.

## Review Focus

Reviewers should check:

- No import cycle exists between audit and renderer.
- `audit_programmatic.py` does not import `renderer.py`.
- P1 chapter title source is manifest-derived or splitter-derived, not a second manual title tuple.
- `ProgrammaticAuditInput.chapter_blocks` is explicit and typed.
- Required item audit covers every manifest `required_output_items` entry through deterministic markers.
- Required item rule mapping exactly follows `Required Item Marker Matrix`, including `危级/降级阈值` until RR-19 is resolved.
- Must-not-cover audit only enforces deterministic markers and does not pretend to do NLP.
- `docs/design.md` is updated if C2 is added to `checked_rules`; no dual C2 status is left behind.
- P3 per-chapter evidence checks use chapter body text, not the global appendix.
- Existing Service/UI behavior is unchanged except for receiving richer audit results.
- No document filesystem/PDF/cache access is added.
- All new functions/classes have Chinese docstrings.

## Risks And Guardrails

| Risk | Guardrail |
|---|---|
| Audit-renderer import cycle | Move chapter block type and splitter to `template/chapter_blocks.py`; audit imports only that shared module. |
| Fake semantic NLP | Use explicit marker maps; no tokenization, embedding, LLM, or inferred synonyms. |
| Current renderer lacks required item labels | Add minimal explicit labels / `数据不足` bullets in renderer instead of weakening audit. |
| False positives from forbidden markers | Keep P6-S3 forbidden marker list small and directly tied to concrete `must_not_cover` text. |
| Evidence audit overclaims support | P3 only checks standardized evidence line presence; evidence correctness remains E1/E2/E3 v2. |
| Direct construction of `ProgrammaticAuditInput` breaks | Add `chapter_blocks` after existing fields with default `()`. |
| Existing tests asserting checked rules fail | Update all checked-rule assertions to include C2. |
| Contract rule mapping drifts from manifest | Validate rule keys against `load_template_contract_manifest()` in tests and at module load or audit setup. |

## Rollback Plan

If implementation causes unacceptable regressions:

1. Revert `run_programmatic_audit(...)` to exclude C2 from `checked_rules` and skip `_audit_contract_conformance(...)`.
2. Keep the `template/chapter_blocks.py` extraction if it is already stable and tests pass; it is a dependency-direction cleanup of P6-S2 surfaces.
3. Revert renderer label additions only if they materially changed report wording beyond deterministic labels/placeholders.
4. Restore previous P3 behavior by disabling per-chapter evidence checks while keeping global evidence marker checks.
5. Do not change Service/UI rollback paths; they should not be modified in this slice.

## Open Questions For Review

- Should C2 issues be `blocker` or `reviewable` once the result model supports warning-only pass semantics? Current plan uses blocker because any issue currently makes `passed=False`.
- Should the deterministic marker rule mapping live in `audit/contract_rules.py` or `template/contracts.py`? Current plan keeps it in audit because it is an audit interpretation of the manifest, not the manifest itself.
- Should P6-S3 update renderer output to include every required output item label in one slice, or should implementation split renderer label alignment into a prerequisite sub-slice? Current plan keeps it in P6-S3 because otherwise the first contract audit cannot pass current renderer output without weakening required item coverage.
