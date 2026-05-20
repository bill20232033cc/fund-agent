# Code Review — P6-S3 Programmatic Contract Audit

## Scope

- Mode: current changes
- Branch: main (unstaged workspace changes)
- Base: main
- Output file: `docs/reviews/code-review-p6-s3-mimo-20260520.md`
- Included scope: P6-S3 deterministic programmatic CHAPTER_CONTRACT audit
  - `fund_agent/fund/audit/audit_programmatic.py` — C2/P3 audit rules, chapter block resolution
  - `fund_agent/fund/audit/contract_rules.py` — deterministic marker rule definitions (new)
  - `fund_agent/fund/template/chapter_blocks.py` — shared chapter block extraction (new, moved from renderer)
  - `fund_agent/fund/template/renderer.py` — renderer label additions, chapter_blocks passed to audit input
  - `fund_agent/fund/template/__init__.py` — lazy renderer imports, chapter_blocks exports
  - `docs/design.md` — C2/P3 design truth update
  - `fund_agent/fund/README.md` — audit rule documentation
  - `tests/README.md` — test coverage documentation
  - `tests/fund/audit/test_audit_programmatic.py` — C2/P3/fallback tests
  - `tests/fund/template/test_renderer.py` — checked_rules update
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py` — checked_rules update
- Excluded scope: Service/Engine/UI/CLI behavior, fund documents, PDF/cache access, LLM audit, ITEM_RULE, quality gate FQ5
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Detailed Review Evidence

### 1. Import cycle audit

Dependency graph:
```
contracts.py
  ↑
chapter_blocks.py    contract_rules.py
  ↑                      ↑
renderer.py          audit_programmatic.py
```

- `chapter_blocks.py` imports only from `contracts.py`. No cycle.
- `contract_rules.py` imports only from `contracts.py`. No cycle.
- `audit_programmatic.py` imports from `chapter_blocks.py`, `contract_rules.py`, and `contracts.py`. Does NOT import `renderer.py`. No cycle.
- `renderer.py` imports from `chapter_blocks.py` and `contracts.py`. Imports `ProgrammaticAuditInput` from `fund_agent.fund.audit` (same as before). No cycle.
- `__init__.py` uses `__getattr__` lazy loading for renderer exports to avoid importing `renderer.py` at module load time. This prevents the `__init__ -> renderer -> audit -> chapter_blocks -> contracts` chain from executing at import.
- `audit/__init__.py` is unchanged — no new exports added.
- **Pass.**

### 2. `ProgrammaticAuditInput.chapter_blocks` explicit field

- Field defined at `audit_programmatic.py:98`: `chapter_blocks: tuple[RenderedChapterBlock, ...] = ()`
- Default `()` preserves backward compatibility for direct test construction.
- Renderer passes `chapter_blocks=chapter_blocks` into `ProgrammaticAuditInput(...)` at `renderer.py:134`.
- No `extra_payload` used. All new audit inputs are explicit typed fields.
- **Pass.**

### 3. C2 rule / source alignment with manifest

`contract_rules.py` required items:

- 44 rules total across chapters 0-7.
- Every rule's `(chapter_id, item_text)` key matches exactly one entry in the manifest's `required_output_items`.
- `validate_programmatic_contract_rules()` cross-checks rule keys against `load_template_contract_manifest()`.
- Coverage is complete: `manifest_items - rule_items` is empty (enforced by validation).
- Marker tuples are non-empty (enforced by validation).
- `危级/降级阈值` preserved as-is per RR-19 tracking. Matches plan requirement.

`contract_rules.py` forbidden content:

- 9 rules total covering chapters 0, 2, 3, 4, 5, 6, 7.
- Each rule's `(chapter_id, item_text)` key matches exactly one entry in the manifest's `must_not_cover`.
- Deliberately small marker list. Only deterministic substring matches, no NLP.
- **Pass.**

### 4. Required item marker matrix compliance

Every `renderer-label-needed` marker from the plan matrix is present in the renderer output:

| Chapter | Marker | Renderer location |
|---:|---|---|
| 0 | `当前业绩与运作状态：` | `_render_chapter_0` line 182 |
| 0 | `支撑当前动作的最主要理由：` | `_render_chapter_0` line 183 |
| 0 | `当前最值得盯住的变量：` | `_render_chapter_0` line 184 |
| 0 | `当前最大的风险：` | `_render_chapter_0` line 185 |
| 0 | `什么变化会升级、降级或终止当前动作：` | `_render_chapter_0` line 188 |
| 1 | `基金类型与分类标签：` | `_render_chapter_1` line 219 |
| 1 | `投资目标（一句话）：` | `_render_chapter_1` line 220 |
| 1 | `投资策略概述：` | `_render_chapter_1` line 221 |
| 1 | `业绩基准及合理性：` | `_render_chapter_1` line 222 |
| 1 | `看这类基金最先看什么：` | `_render_chapter_1` line 223 |
| 1 | `会改变产品理解的特别情况：` | `_render_chapter_1` line 224 |
| 2 | `近 1/3/5 年净值增长率：` | `_render_chapter_2` line 266 |
| 2 | `近 1/3/5 年业绩基准收益率：` | `_render_chapter_2` line 267 |
| 2 | `超额收益（A = R - B）及稳定性：` | `_render_chapter_2` line 268 |
| 2 | `成本拆解：` | `_render_chapter_2` line 270 |
| 2 | `成本合理性判断：` | `_render_chapter_2` line 271 |
| 2 | `R=A+B-C 综合评估：` | `_render_chapter_2` line 272 |
| 3 | `基金经理基本信息：` | `_render_chapter_3` line 298 |
| 3 | `宣称的投资策略（§4）：` | `_render_chapter_3` line 299 |
| 3 | `实际投资行为（§8）：` | `_render_chapter_3` line 300 |
| 3 | `言行一致性判断：` | `_render_chapter_3` line 301 |
| 3 | `风格稳定性判断：` | `_render_chapter_3` line 302 |
| 3 | `利益一致性判断：` | `_render_chapter_3` line 303 |
| 4 | `基金产品收益 vs 投资者实际收益：` | `_render_chapter_4` line 335 |
| 4 | `盈利投资者占比：` | `_render_chapter_4` line 336 |
| 4 | `行为损益估算：` | `_render_chapter_4` line 337 |
| 4 | `份额变动趋势：` | `_render_chapter_4` line 338 |
| 5 | `过去一年最关键的变化：` | `_render_chapter_5` line 369 |
| 5 | `基金当前所处阶段：` | `_render_chapter_5` line 370 |
| 5 | `变化是否改变前文判断：` | `_render_chapter_5` line 371 |
| 5 | `接下来最该跟踪的变量：` | `_render_chapter_5` line 372 |
| 6 | `最关键的风险或否决项：` | `_render_chapter_6` line 396 |
| 6 | `为什么足以改变结论：` | `_render_chapter_6` line 397 |
| 6 | `否决 vs 跟踪判断：` | `_render_chapter_6` line 398 |
| 6 | `下一轮先验证什么：` | `_render_chapter_6` line 399 |
| 7 | `支撑判断的核心依据：` | `_render_chapter_7` line 434 |
| 7 | `当前最容易看错的地方：` | `_render_chapter_7` line 435 |
| 7 | `下一轮最小验证计划：` | `_render_chapter_7` line 436 |
| 7 | `危级/降级阈值：` | `_render_chapter_7` line 437 |

`already-rendered` markers (`基金：`, `最终判断：`, `下一步最小验证问题：`, `超额收益性质：`) were already present before P6-S3.

Forbidden terms verified absent from rendered report: `买入`, `卖出`, `仓位比例`, `收益预测`.

- **Pass.**

### 5. Must-not-cover exact-marker subset

Forbidden rules use deterministic substring matching only:
- `audit_programmatic.py:335-336`: `marker in block.body_markdown` — literal substring check.
- No tokenization, no synonym inference, no LLM, no NLP.
- Marker list is deliberately small per plan constraint.
- **Pass.**

### 6. P3 per-chapter evidence not overclaiming

- `_audit_minimum_chapter_evidence` (lines 262-296) checks:
  - Each chapter block has `> 📎 证据：` line via `_CHAPTER_EVIDENCE_LINE_PATTERN`.
  - No `## 证据与出处` in chapter body.
- Does NOT check whether evidence actually supports claims. That remains E1/E2/E3 v2.
- Global P3 still checks `## 证据与出处` presence via `_EVIDENCE_MARKER_PATTERN`.
- **Pass.**

### 7. Renderer labels limited to plan matrix

Renderer changes are minimal label additions:
- Each new line follows the pattern `- {marker from matrix}: {data or 数据不足 placeholder}`.
- No prose rewrite. Existing narrative lines preserved.
- Missing data explicit as `数据不足` / `未披露`.
- No buying/selling instructions or future return predictions added.
- **Pass.**

### 8. No Service/Engine/UI/CLI behavior expansion

Changed files do not include:
- `fund_agent/services/`
- `fund_agent/engine/`
- `fund_agent/ui/`
- `fund_agent/cli.py`

`tests/fund/integration/test_p3_cli_e2e_matrix.py` only updates `checked_rules` assertion. CLI behavior unchanged.

- **Pass.**

### 9. No direct document filesystem/PDF/cache access

- `audit_programmatic.py` imports: `checklist`, `r_abc`, `contract_rules`, `chapter_blocks`, `contracts`. No filesystem/PDF imports.
- `contract_rules.py` imports: `contracts` only.
- `chapter_blocks.py` imports: `contracts` only.
- **Pass.**

### 10. No `extra_payload`

- `ProgrammaticAuditInput` has explicit `chapter_blocks` field. No dict/Any payload.
- **Pass.**

### 11. `_REQUIRED_CHAPTER_TITLES` derived from manifest

- Old: hardcoded partial title tuple that could drift from manifest.
- New (`audit_programmatic.py:34-36`): `tuple(chapter.title for chapter in load_template_contract_manifest().chapters)`
- Single source of truth. No second manual title source.
- **Pass.**

### 12. `docs/design.md` C2 split

- C2 row updated: "阻断（确定性子集）/ 低优先级（语义子集）", "✅ 确定性子集；语义判断 v2"
- Added explanatory paragraph distinguishing deterministic C2 (implemented) from semantic C2 (v2).
- P3 description updated: "缺少'证据与出处'小节或章节内最小证据行"
- No dual C2 status left behind.
- **Pass.**

### 13. Step A / Step B separation

The diff shows:
- Step A: `chapter_blocks.py` created (moved from `renderer.py`), renderer imports updated, `__init__.py` updated. Behavior-preserving.
- Step B: `contract_rules.py` created, audit C2/P3 rules added, renderer labels added, `chapter_blocks` passed to audit input.
- All renderer tests pass after Step A (verified: 227/227).
- **Pass.**

### 14. Test coverage

| Plan requirement | Test | Pass? |
|---|---|---|
| Checked rules include C2 | `test_run_programmatic_audit_passes_complete_inputs` | Yes |
| Renderer output passes new audit | `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_c2_l1_r1_r2` | Yes |
| Required item failure | `test_run_programmatic_audit_detects_missing_required_output_item_marker` | Yes |
| Forbidden content failure | `test_run_programmatic_audit_detects_forbidden_contract_marker` | Yes |
| Per-chapter evidence failure | `test_run_programmatic_audit_detects_missing_chapter_evidence_line` | Yes |
| Explicit blocks audit | `test_run_programmatic_audit_passes_complete_inputs` (uses explicit blocks) | Yes |
| Fallback split audit | `test_run_programmatic_audit_splits_report_when_chapter_blocks_absent` | Yes |
| Malformed report → P1 | `test_run_programmatic_audit_reports_p1_when_splitter_fallback_fails` | Yes |
| Rule mapping validation | `test_programmatic_contract_rules_cover_manifest_and_fail_closed_for_invalid_rule` | Yes |

227/227 tests pass, ruff clean, no whitespace errors.

- **Pass.**

## Open Questions

- 无。

## Residual Risk

- `_rendered_audit_input` test helper in `test_audit_programmatic.py` imports private `_render_input` from `test_renderer.py`. Cross-test-module private imports are fragile but acceptable for test-only code.
- `_validate_required_item_rules` checks that every manifest `required_output_items` entry has a rule, but `_validate_forbidden_content_rules` does NOT check that every manifest `must_not_cover` entry has a rule. This is intentional (forbidden rules are deliberately small), but means manifest additions to `must_not_cover` won't trigger a validation failure. The risk is low because `must_not_cover` entries without markers are unenforceable deterministically anyway.
- `load_programmatic_contract_rules()` re-validates the full manifest on every call. For current usage (single audit per report) this is fine. If batch auditing becomes hot, consider caching the validated rules.

## Conclusion

PASS.

The P6-S3 implementation correctly adds deterministic C2 contract audit and P3 per-chapter evidence checks. Import cycles are avoided via the `chapter_blocks.py` shared module. All required item markers from the plan matrix are present in renderer output. Forbidden content checking is deterministic only. `docs/design.md` properly splits C2 into deterministic (MVP) and semantic (v2) subsets. No Service/Engine/UI/CLI behavior changes. 227/227 tests pass.
