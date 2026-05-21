# P12-S1 ITEM_RULE Renderer / Audit Compliance Plan（2026-05-22）

- **Role**: AgentCodex planning specialist
- **Gate**: `P12-S1 ITEM_RULE renderer/audit compliance plan/review`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Previous planning artifact**: `docs/reviews/post-p11-second-follow-up-planning-20260522.md`
- **Accepted baseline before gate**: `79fb3e3`

## 1. Objective

把当前已经存在的 ITEM_RULE manifest / evaluator 连接到确定性渲染和程序审计闭环，让第 1/2 章的条件型段落在标准基金类型下稳定满足：

1. 条件触发时，renderer 输出对应段落。
2. 条件未触发时，renderer 删除整段，而不是输出“不适用”段落或保留残留标题。
3. programmatic audit 使用同一份 ITEM_RULE 决策验证“应出现则出现、应删除则不存在”。
4. 全链路不从报告正文、基金名称或自然语言描述反推 facet，不引入 LLM、Evidence Confirm、RepairContract、Host/Engine/tool loop，也不改变产品 CLI 行为。

第一性原理判断：ITEM_RULE 已经是 Capability 层的模板契约事实；最短安全路径不是新建语义审计，而是让 renderer 和 C2 程序审计共同消费同一个确定性决策对象，避免“渲染按一套逻辑、审计按另一套逻辑”。

## 2. Non-goals

- 不实现 LLM audit、Evidence Confirm、RepairContract、语义越界判断或证据复核。
- 不新增 Host、Engine、Runtime、tool loop、prompt scene registry 或 Dayu 运行时依赖。
- 不改 `fund-analysis analyze` CLI 参数、退出码、用户可见 product contract 或 final judgment policy。
- 不改 `FundDocumentRepository`、年报来源 fallback taxonomy、PDF/cache/helper 访问边界。
- 不改 `docs/implementation-control.md`、`docs/repo-audit-20260521.md`，不处理 RR-13 duplicate `016492`。
- 不让 FQ5 宣称最终报告语义正确；FQ5 仍是 snapshot/score 侧的模板契约适用性事实。
- 不从 prose 推断主动价值/成长等细分 facet；当前渲染只用 `classified_fund_type`，显式 `facets=()`。

## 3. Ownership Boundaries

Fund Capability owns the full slice:

| Area | Files likely to change | Ownership / boundary |
|---|---|---|
| ITEM_RULE decision contract | `fund_agent/fund/template/item_rules.py` | Capability/template。可新增 helper 或 audit-friendly result 类型；不得读取基金文档或调用 renderer 私有逻辑。 |
| Renderer integration | `fund_agent/fund/template/renderer.py` | Capability/template。renderer 从 `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]` 构造 ITEM_RULE 决策，并按决策输出/删除第 1/2 章段落。 |
| Programmatic audit integration | `fund_agent/fund/audit/audit_programmatic.py` | Capability/audit。C2 消费 renderer 传入的 ITEM_RULE 决策，检查 segment marker presence/delete compliance。 |
| Public exports | `fund_agent/fund/template/__init__.py` and possibly `fund_agent/fund/audit/__init__.py` | 只导出真正需要被测试或 Capability 内调用的稳定类型/helper；避免把 renderer 私有 helper 变成公共 API。 |
| Tests | `tests/fund/template/test_renderer.py`, `tests/fund/audit/test_audit_programmatic.py`, maybe `tests/fund/template/test_item_rules.py` | 聚焦确定性行为，不访问网络/PDF/真实年报。 |
| README sync | `fund_agent/fund/README.md`, `tests/README.md` | 只更新当前行为变化：ITEM_RULE 已接入 renderer 和 programmatic audit；FQ5 仍不证明 renderer compliance。 |

Do not modify Service/UI/CLI unless implementation discovers an impossible blocker. Current evidence indicates no blocker: `render_template_report()` already resolves `preferred_lens` from `StructuredFundDataBundle` and returns `ProgrammaticAuditInput`.

## 4. Proposed Contracts

### 4.1 Renderer obtains ITEM_RULE decisions

Add a renderer-side resolution path mirroring `preferred_lens`:

```text
TemplateRenderInput.structured_data.basic_identity.value
  -> classified_fund_type
  -> evaluate_template_item_rules(fund_type=classified_fund_type, facets=())
  -> item_rule_decisions
```

Contract rules:

- If `basic_identity.value is None`, renderer may return no ITEM_RULE decision plan, matching the current missing-data path that also returns no lens plan.
- If `basic_identity.value` exists but `classified_fund_type` is missing/blank/unsupported, renderer must fail closed with `ValueError`, matching the existing preferred_lens behavior.
- `facets=()` is mandatory for this slice. There is no facet inference from report Markdown, fund name, fund category, investment strategy, benchmark or classification basis prose.
- `TemplateRenderResult` should expose `item_rule_decisions: tuple[TemplateItemRuleDecision, ...] = ()` so tests and future callers can inspect deterministic decisions without parsing Markdown.
- `TemplateRenderResult` should also expose `item_rule_audit_context: TemplateItemRuleAuditContext`, where `TemplateItemRuleAuditContext = Literal["identity_missing", "identity_present"]`.
- Renderer sets `item_rule_audit_context="identity_missing"` only when `basic_identity.value is None`; it sets `item_rule_audit_context="identity_present"` after successfully evaluating decisions for any present identity.
- `ProgrammaticAuditInput` should carry both `item_rule_decisions` and `item_rule_audit_context`, produced by renderer, so audit verifies the actual render path’s intended decisions rather than recomputing from potentially different inputs.

### 4.2 Renderer segment behavior

Renderer should add four concrete segment renderers or a small rule-dispatch helper for the current built-in ITEM_RULE ids:

| Rule | Triggered fund types | Renderer behavior |
|---|---|---|
| `chapter_1_index_constituents` | `index_fund`, `enhanced_index` | Add fixed heading `#### 指数编制规则与成分股` and fixed bullets only. Benchmark anchor only proves benchmark/index reference, not constituents or methodology; therefore methodology and constituents must render as `数据不足` until an extractor exists. |
| `chapter_1_manager_philosophy` | `active_fund` | Add fixed heading `#### 基金经理投资哲学` and fixed bullets only. Use `manager_strategy_text` only as disclosed strategy source; if absent, write `未披露`/`数据不足` with evidence preservation. |
| `chapter_2_alpha_yearly_breakdown` | `active_fund`, `enhanced_index` | Add fixed heading `#### 超额收益分年度拆解` and fixed bullets only. Reuse available `rabc_attributions`; if only one period exists, state current input only supports that period and keep existing R=A+B-C evidence anchors. |
| `chapter_2_tracking_error_analysis` | `index_fund`, `enhanced_index` | Add fixed heading `#### 跟踪误差分析` and fixed bullets only. Current P1/P2 does not provide tracking error, so this is a deterministic data-insufficient placeholder until a tracking-error extractor exists; do not calculate or infer tracking error. |

Conditional rules with `status="delete"` must contribute no heading, no placeholder, and no residual unique marker. Deleting a segment must not delete the rest of the chapter or the chapter-level evidence line.

Segment Markdown must be deterministic: each segment is a heading followed by a fixed ordered set of `- key：value。` bullets, with no free prose paragraphs. Initial fixed formats:

```markdown
#### 指数编制规则与成分股
- 业绩基准引用：{benchmark_text_or_数据不足}。
- 编制方法：数据不足，当前输入未抽取指数编制方法。
- 成分股：数据不足，当前输入未抽取指数成分股。
> 📎 证据：...

#### 基金经理投资哲学
- 披露策略：{manager_strategy_summary_or_未披露}。
- 可验证动作：数据不足，当前输入仅保留披露原文，不推断投资哲学。
> 📎 证据：...

#### 超额收益分年度拆解
- 可用周期：{period_summary_or_数据不足}。
- 分年度结论：数据不足，当前输入未形成多年度完整序列时不得推断稳定性。
> 📎 证据：...

#### 跟踪误差分析
- 跟踪误差：数据不足，当前输入未抽取跟踪误差。
- 后续最小验证：补充跟踪误差披露或净值/指数日频序列后再计算。
> 📎 证据：...
```

Evidence strategy:

- `chapter_1_index_constituents` uses benchmark anchors only for the benchmark-reference bullet; methodology/constituents bullets remain `数据不足` and must not cite benchmark evidence as proof of constituents.
- `chapter_1_manager_philosophy` uses `manager_strategy_text` anchors when available; absence renders `未披露` and may use the existing chapter missing-evidence behavior.
- `chapter_2_alpha_yearly_breakdown` uses `RabcAttribution.anchors`; no multi-year stability claim is allowed unless multiple attribution periods exist.
- `chapter_2_tracking_error_analysis` is a deterministic data-insufficient placeholder for `index_fund` and `enhanced_index`; it may cite benchmark/RABC anchors only to identify the relevant index context, not to prove tracking error.

### 4.3 Programmatic audit verifies presence/delete compliance

Extend C2 audit with an ITEM_RULE sub-check:

```text
ProgrammaticAuditInput.item_rule_decisions
ProgrammaticAuditInput.item_rule_audit_context
ProgrammaticAuditInput.chapter_blocks
load_template_item_rule_manifest()
rendered_segment_present(block.body_markdown, rule)
```

Expected behavior:

- For each decision with `status="render"`, exactly require that at least one configured `segment_markers_any` exists in the matching chapter block.
- For each decision with `status="delete"`, require that no configured `segment_markers_any` exists in the matching chapter block.
- Use route A missing-decision semantics:
  - `item_rule_audit_context="identity_missing"` and empty decisions: skip ITEM_RULE missing-decision C2 issue because the renderer took the missing-data path.
  - `item_rule_audit_context="identity_present"` and empty decisions while `chapter_blocks` exist: emit C2 issue such as `基金身份存在但缺少 ITEM_RULE 决策，无法验证条件型段落合规。`
  - `item_rule_audit_context="identity_present"` and non-empty decisions: run presence/delete compliance checks.
- If a decision references a rule id not present in manifest, duplicated decision ids, wrong chapter id, or unsupported status, audit should emit C2 fail-closed issue.
- Audit must match `decision.chapter_id` to the corresponding `RenderedChapterBlock` and inspect only that block’s `body_markdown` through `rendered_segment_present(block.body_markdown, rule)` or equivalent manifest marker logic. It must not scan global `report_markdown` for ITEM_RULE markers.
- Ordinary prose such as “跟踪指数” must not count as segment presence.

This remains C2 deterministic contract audit. It does not validate whether the rendered paragraph’s prose is semantically complete or whether evidence supports every assertion.

### 4.4 Quality Gate / FQ5 metadata

No product quality gate behavior change is required for this slice.

- `extraction_score.py` already records ITEM_RULE decisions in FQ5 applicability facts.
- `quality_gate.py` should not parse final report Markdown and should not claim renderer/audit compliance.
- `fund_agent/fund/README.md` should keep the distinction explicit: FQ5 proves CHAPTER_CONTRACT / ITEM_RULE applicability can be derived from snapshot facts; programmatic audit C2 verifies rendered report compliance when `render_template_report()` supplies decisions.
- Do not add new `score.json` fields unless implementation discovers a serialization gap in existing tests. Current facts indicate no metadata extension is needed.

## 5. Implementation Slices

### Slice 1: Renderer decision plumbing

Files:

- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/template/__init__.py` if a new public dataclass/helper is introduced
- `tests/fund/template/test_renderer.py`

Steps:

1. Add a private `_resolve_item_rule_decisions(structured_data)` helper with Chinese docstring.
2. Reuse existing classified fund type fail-closed semantics:
   - no identity -> `()`
   - identity present but missing/blank `classified_fund_type` -> `ValueError`
   - unsupported type -> `ValueError` from evaluator
3. Add `TemplateItemRuleAuditContext = Literal["identity_missing", "identity_present"]` in the narrowest appropriate module, likely `fund_agent/fund/template/item_rules.py` if shared by renderer and audit.
4. Add `item_rule_decisions: tuple[TemplateItemRuleDecision, ...] = ()` and `item_rule_audit_context: TemplateItemRuleAuditContext` to `TemplateRenderResult`.
5. Pass both fields into `ProgrammaticAuditInput`.
6. Renderer must set:
   - no identity -> `item_rule_decisions=()`, `item_rule_audit_context="identity_missing"`
   - identity present and valid type -> evaluated decisions, `item_rule_audit_context="identity_present"`
   - identity present but invalid/missing type -> raise `ValueError`
7. Add renderer tests for:
   - active fund renders manager philosophy and alpha breakdown, deletes index constituents and tracking error.
   - index fund renders index constituents and tracking error, deletes manager philosophy and alpha breakdown.
   - enhanced index renders index constituents, alpha breakdown and tracking error, deletes manager philosophy.
   - at least one non-triggering fund type such as `bond_fund` deletes all four current built-in conditional segments.
   - preferably table-driven checks for all six standard fund types: `index_fund`, `active_fund`, `bond_fund`, `enhanced_index`, `qdii_fund`, `fof_fund`.
   - missing identity path returns empty ITEM_RULE decisions and remains audit-compatible for missing-data report.
   - present identity without `classified_fund_type` still fails closed.

### Slice 2: Conditional segment rendering

Files:

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`

Steps:

1. Add small segment rendering helpers keyed by `rule_id`, e.g. `_render_item_rule_segment(decision, input_data)`.
2. Append chapter 1 ITEM_RULE segments after the existing product/strategy bullets and before the chapter evidence line.
3. Append chapter 2 ITEM_RULE segments after existing R=A+B-C / alpha judgment bullets and before chapter evidence line.
4. Keep segment Markdown deterministic: heading plus fixed `- key：value。` bullets only, no free prose paragraphs and no variable bullet labels.
5. Keep segment headings equal to manifest markers’ stable heading form:
   - `#### 指数编制规则与成分股`
   - `#### 基金经理投资哲学`
   - `#### 超额收益分年度拆解`
   - `#### 跟踪误差分析`
6. Preserve evidence:
   - use existing `_evidence_line(...)` where a segment uses a source field or attribution;
   - do not remove existing chapter-level evidence line;
   - use `未披露`/`数据不足` when structured data is absent.
   - benchmark anchors cannot be used as evidence for index constituents or methodology.
   - tracking error remains `数据不足` until a dedicated extractor or calculation input exists.

### Slice 3: Programmatic audit C2 ITEM_RULE compliance

Files:

- `fund_agent/fund/audit/audit_programmatic.py`
- possibly `fund_agent/fund/audit/__init__.py` only if exports are needed
- `tests/fund/audit/test_audit_programmatic.py`

Steps:

1. Add `item_rule_decisions: tuple[TemplateItemRuleDecision, ...] = ()` and `item_rule_audit_context: TemplateItemRuleAuditContext = "identity_missing"` to `ProgrammaticAuditInput`.
2. Extend `run_programmatic_audit()` to call `_audit_item_rule_compliance(chapter_blocks, input_data.item_rule_decisions)`.
3. Implement fail-closed validation:
   - no chapter blocks -> leave existing P1/block behavior responsible;
   - `item_rule_audit_context="identity_missing"` and decisions empty -> skip ITEM_RULE missing-decision issue;
   - `item_rule_audit_context="identity_present"` and chapter blocks exist but decisions empty -> C2 issue;
   - duplicated decision ids -> C2 issue;
   - unknown rule id -> C2 issue;
   - chapter id mismatch -> C2 issue;
   - render decision absent marker -> C2 issue;
   - delete decision present marker -> C2 issue.
4. Test audit catches:
   - rendered report manually stripped of a triggered segment heading.
   - rendered report manually injected with a deleted segment heading.
   - audit input with `item_rule_audit_context="identity_present"` and missing decisions while report/chapter blocks exist.
   - audit input with `item_rule_audit_context="identity_missing"` and missing decisions skips the ITEM_RULE missing-decision issue while still allowing existing P/L/R issues.
   - ordinary prose marker false positive remains false by using `rendered_segment_present()` behavior.
   - enhanced index render/delete matrix passes through audit.
   - at least one non-triggering fund type, preferably `bond_fund`, verifies all built-in markers are absent and audit passes.

Compatibility note: Some existing unit tests construct `ProgrammaticAuditInput` directly to test isolated P/L/R failures. Route A avoids mass fixture churn by letting direct missing-data fixtures use the default `item_rule_audit_context="identity_missing"`. Existing helpers/tests likely needing updates are:

- `tests/fund/audit/test_audit_programmatic.py::_valid_audit_input()` or equivalent full-pass helper should use `render_template_report(_render_input()).audit_input` so decisions/context come from renderer.
- Audit tests that manually rebuild `ProgrammaticAuditInput(...)` from rendered Markdown/chapter blocks and expect a full pass should copy `item_rule_decisions` and `item_rule_audit_context` from `render_result.audit_input`.
- Tests that intentionally isolate P1/P2/P3/L1/R1/R2 failures with partial inputs may keep the default identity-missing context unless they also claim identity-present C2 compliance.
- New C2 tests should explicitly set `item_rule_audit_context="identity_present"` when simulating missing decisions.

The renderer audit-pass test must pass with decisions supplied by `render_template_report()`.

### Slice 4: README and test documentation

Files:

- `fund_agent/fund/README.md`
- `tests/README.md`

Updates:

- Replace the current statement “ITEM_RULE 不接入程序审计、质量门禁、Service/UI/CLI” with current behavior:
  - connected to renderer and programmatic C2 audit;
  - still not connected to Service/UI/CLI as a product-facing option;
  - still not read by quality gate as final Markdown compliance.
- Update renderer/audit sections to mention `TemplateRenderResult.item_rule_decisions` and `ProgrammaticAuditInput.item_rule_decisions`.
- Update tests README entries for renderer/audit ITEM_RULE coverage.

## 6. Edge Cases

| Edge case | Required behavior |
|---|---|
| `active_fund` | Render only active segments: `基金经理投资哲学`, `超额收益分年度拆解`; delete index constituents and tracking error segments. |
| `index_fund` | Render only index segments: `指数编制规则与成分股`, `跟踪误差分析`; delete manager philosophy and alpha yearly breakdown. |
| `enhanced_index` | Render index constituents, alpha yearly breakdown and tracking error; delete manager philosophy. Tracking error is still a deterministic `数据不足` placeholder until tracking-error data exists. |
| `bond_fund`, `qdii_fund`, `fof_fund` | Current four built-in conditional ITEM_RULEs should all delete unless future manifest rules add those types. Audit must verify deleted markers are absent. |
| Non-triggered conditional segment | Delete the entire segment including heading; no “不适用” placeholder and no unique marker residue. |
| Missing `classified_fund_type` with present identity | Fail closed in renderer before producing a report, matching existing preferred_lens behavior. |
| Missing identity entirely | Preserve current missing-data path; renderer sets `item_rule_audit_context="identity_missing"`, no ITEM_RULE decisions, no conditional segments, no facet inference. Programmatic audit skips only the ITEM_RULE missing-decision C2 issue and should remain able to report broader missing-data issues without crashing. |
| Identity present but decisions missing | Programmatic audit receives `item_rule_audit_context="identity_present"` with empty decisions and must fail C2. |
| No facet inference from prose | Renderer passes `facets=()` only. Do not inspect fund name, category, benchmark, strategy, classification basis or report Markdown to infer fine-grained facets. |
| Evidence preservation | New segments must reuse existing extracted-field or R=A+B-C anchors where available and use explicit `未披露`/`数据不足` rather than fabricating source facts. |
| Ordinary prose false positive | Presence checks must require manifest `segment_markers_any`, not general text like “跟踪指数” or “投资哲学”. |
| Tracking error data absent | For `index_fund` and `enhanced_index`, render `#### 跟踪误差分析` as a fixed data-insufficient segment; do not delete it when the rule triggers and do not infer values. |

## 7. Validation Commands

Planning gate validation:

```bash
git diff --check
```

Implementation gate targeted validation:

```bash
pytest tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py
pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
ruff check fund_agent/fund/template fund_agent/fund/audit tests/fund/template tests/fund/audit
git diff --check
```

Implementation gate recommended full validation:

```bash
pytest
```

No network, PDF download or real annual-report filesystem access should be needed for this slice.

## 8. Acceptance Criteria

The implementation is acceptable only if all are true:

1. Renderer exposes and passes through ITEM_RULE decisions derived from `classified_fund_type` with `facets=()`.
2. Renderer exposes `item_rule_audit_context` and sets identity-missing vs identity-present according to the concrete `basic_identity.value` path.
3. Active/index/enhanced index reports contain exactly the conditional segment markers expected by the manifest decisions.
4. Bond/QDII/FOF, or at least a table-driven all-six-fund-type test matrix, verifies non-triggering fund types delete all current built-in conditional segments.
5. Non-triggered conditional segments are absent as whole segments.
6. Segment Markdown uses fixed headings and fixed bullet keys; no free prose paragraphs or inferred values are introduced.
7. Programmatic audit C2 fails when a triggered segment is missing or a deleted segment is present.
8. Programmatic audit C2 fails for identity-present empty decisions and skips only the missing-decision issue for identity-missing context.
9. Programmatic audit uses the same decision tuple and audit context that renderer produced; no second, divergent prose-based inference path exists.
10. Audit checks the matching `RenderedChapterBlock.body_markdown`, not global report Markdown.
11. Missing/unsupported `classified_fund_type` remains fail-closed when identity exists.
12. New segments preserve evidence anchors or explicitly state `未披露`/`数据不足`; benchmark anchors do not prove constituents/methodology, and tracking error remains `数据不足` until data exists.
13. FQ5 / quality gate semantics remain unchanged except README clarification.
14. README updates describe current code behavior and do not promise future LLM/evidence repair features.
15. Targeted tests, ruff and `git diff --check` pass.

## 9. Stop Conditions

Stop implementation and return to planning/controller review if any of the following is discovered:

- The renderer cannot derive ITEM_RULE decisions without changing Service/UI/CLI public behavior.
- Audit compliance would require reading fund documents, PDF cache, external data or source-specific helpers outside `FundDocumentRepository`.
- Existing report structure cannot accept deterministic segments without breaking CHAPTER_CONTRACT P1/P2/P3/C2 tests in a way that needs template redesign.
- A reviewer proposes using LLM, Evidence Confirm, RepairContract or prose-based facet inference for this MVP slice.
- Implementing FQ5 metadata changes becomes necessary; that requires explicit plan review because current decision is “no FQ5 behavior change”.
- Any need arises to edit `docs/implementation-control.md` or `docs/repo-audit-20260521.md`; both are outside this planning handoff.
- `docs/implementation-control.md` remains outside implementation scope for this specialist slice; it may only be updated later by the controller as phaseflow bookkeeping after plan/code acceptance, not by the implementation agent.
