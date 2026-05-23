# Post-P12-S1 Follow-up Planning（2026-05-22）

- **Role**: AgentCodex planning specialist
- **Gate**: `post-P12-S1 follow-up planning`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **P12-S1 accepted commits**: `c757036`, `617ca58`
- **Output only**: 本 artifact 只规划下一条最小 product-safety slice；不改 source/test/README/control doc，不 commit、不 push、不建 PR。

## 1. Goal / Motivation

选择下一条最小、最直接、风险收益最高的 product-safety slice：**P12-S2 ITEM_RULE multi-anchor evidence boundary**。

P12-S1 已关闭 ITEM_RULE renderer/audit compliance：renderer 从 `classified_fund_type` + `facets=()` 产生 `item_rule_decisions`，程序审计 C2 消费 renderer 的同一 tuple/context 验证段落应渲染或应删除。剩余最靠近用户报告正确性的缺口，是 ITEM_RULE 段落内的局部证据边界目前只展示首个 anchor。对于跟踪误差段落这类同时携带 benchmark anchor 和 R=A+B-C anchor 的确定性占位，多来源 provenance 会被压缩掉，降低读者和后续 evidence audit 对“哪些事实支撑了这个段落上下文”的可追溯性。

第一性原理判断：现在不应该先做真实 tracking-error/index constituents extractor。真实抽取需要新增数据契约、来源边界、计算口径和更宽测试矩阵；而多 anchor 展示只修复已存在报告输出的信息损失，改动面窄、收益直接、不会改变分析结论或外部契约。

## 2. Direct Evidence

- `docs/implementation-control.md` Startup Packet 记录当前 gate 为 `P12-S1 ITEM_RULE renderer/audit compliance accepted`，Next entry point 为 `post-P12-S1 follow-up planning`，open residuals 包括 RR-13 duplicate `016492`、排除的 `docs/repo-audit-20260521.md`、P12-S1 evidence/extractor follow-ups。
- `docs/implementation-control.md` P12 notes 明确：P12-S1 evidence presentation follow-ups 中，multi-anchor ITEM_RULE evidence display 和真实 tracking-error/index methodology/constituents extraction 均保持在 P12-S1 scope 外。
- `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md` 接受 P12-S1，同时裁决 “ITEM_RULE evidence bullet renders only the first anchor” 为 deferred，owner 是 future evidence-display/evidence-confirm slice。
- `docs/reviews/p12-s1-code-review-glm-20260522.md` F1 指出 `_item_rule_evidence_bullet` 只引用 `anchors[0]`；不阻塞 P12-S1，但后续多来源段落可能丢失部分 provenance。
- `fund_agent/fund/template/renderer.py` 当前 `_render_tracking_error_segment()` 先把 benchmark anchors 和 RABC anchors 合并去重，再调用 `_item_rule_evidence_bullet(anchors)`；`_item_rule_evidence_bullet()` 在 anchors 非空时只返回 `_body_anchor_reference(anchors[0])`。
- `tests/fund/template/test_renderer.py` 当前 `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` 只断言固定 bullet 和数据不足边界，未覆盖多 anchor 展示。
- `docs/design.md` 和 `AGENTS.md` 均要求证据可审计、所有数值判断可追溯；本 slice 不新增判断，只让已有 anchor 更完整地显式呈现。
- `docs/repo-audit-20260521.md` 的可采纳建议主要偏 repo hygiene / 文档布局 / 旧实现状态核对，且该文件仍是未跟踪候选输入，不是当前 accepted artifact。

## 3. Candidate Comparison

| Candidate | Product-safety value | Scope / risk | Decision |
|---|---:|---:|---|
| P12-S2 ITEM_RULE multi-anchor evidence boundary | 高：减少已渲染报告的 provenance 信息损失，直接强化证据可追溯 | 低：Fund Capability renderer + renderer tests + Fund/tests README | **Selected** |
| RR-13 duplicate `016492` | 中：精选池源数据身份冲突可能影响后续池内分析 | 高：需要用户/App 源真相，不能由代码推断 | Not selected；继续 human-owned |
| Publish or include `docs/repo-audit-20260521.md` | 低到中：审计输入里有部分可用建议 | 中：artifact 是旧 baseline 审核，当前控制文档明确 excluded | Not selected；保持未跟踪候选输入 |
| Real tracking-error extractor/calculator | 高：填充目前 `数据不足` 的实质字段 | 高：需定义数据源、时间序列口径、指数净值来源、错误分类、schema、缓存和审计 | Not selected；后续独立 extractor/calculation phase |
| Real index methodology / constituents extractor | 高：填充指数基金产品本质证据 | 高：需新增招募说明书或指数公告来源、表格解析、来源 fallback 和 identity 校验 | Not selected；后续独立 documents/extractor phase |
| Audit noise cleanup for chapter-mismatched ITEM_RULE decision | 低：当前已 fail-closed，不隐藏缺陷 | 低：可维护性优化，但产品安全收益弱 | Not selected |
| Future ITEM_RULE dispatch extensibility | 中：降低后续新增规则漏测试风险 | 中：没有当前新增规则需求，容易过早抽象 | Not selected |
| Repo-audit suggestions: design structure tree / reviews archive / version bump / `fund/tools` check | 低到中：主要改善可读性或历史状态 | 中：不直接改善当前用户报告安全，且部分已被 P10/P11 裁决 | Not selected |

## 4. Selected Work Unit

**Name**: `P12-S2 ITEM_RULE multi-anchor evidence boundary`

**Objective**: 让 ITEM_RULE 段落内的 `- 证据边界：...` bullet 展示去重后的全部相关 anchor，而不是只展示第一个 anchor；保持章节级 `> 📎 证据` 一章一条契约不变。

**Expected outcome**:

- 跟踪误差 ITEM_RULE 段落在同时有 benchmark 和 RABC anchors 时，证据边界 bullet 同时展示多个来源引用。
- 单 anchor 段落输出保持简洁、兼容当前中文格式。
- 无 anchor 段落仍输出当前 `数据不足，当前段落未携带独立证据锚点。`
- 不改变 `item_rule_decisions`、`item_rule_audit_context`、C2 presence/delete compliance、FQ5 语义、Service/UI/CLI 行为。

## 5. Non-goals

- 不实现真实 tracking error、index methodology、index constituents、日频净值/指数序列抽取或计算。
- 不改变任何 ITEM_RULE 触发条件、manifest、fund type/facet 评估逻辑或段落 marker。
- 不把 benchmark anchor 伪装成指数成分股、指数编制方法或 tracking error 的证明。
- 不新增 Evidence Confirm、LLM audit、RepairContract、Host、Engine、tool loop 或 Dayu runtime。
- 不改 `FundDocumentRepository`、PDF/cache/source helper、fallback taxonomy。
- 不改 Service/UI/CLI、quality gate、score JSON、public CLI 参数或退出码。
- 不处理 RR-13 duplicate `016492`。
- 不发布、修改或 stage `docs/repo-audit-20260521.md`。
- 不清理 review 目录、不调整 control doc、不做 repo hygiene。

## 6. Affected Files / Modules

Allowed implementation files:

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- implementation artifact under `docs/reviews/` for the implementation gate

No other source/test/doc files are allowed without stopping for controller approval.

Ownership boundary: all behavior remains inside Fund Capability template renderer and its tests/docs. Programmatic audit already validates segment presence/delete by marker and should not need source changes because marker presence is unchanged.

## 7. Contract / Schema / Public-interface Changes

- No dataclass field additions.
- No schema or serialized output contract changes.
- No `TemplateRenderInput`, `TemplateRenderResult`, `ProgrammaticAuditInput`, `QualityGateResult`, CLI, Service, UI, or public package export changes.
- Markdown content changes only inside existing ITEM_RULE local evidence bullet:
  - From single anchor: `- 证据边界：年报2024§...。`
  - To all anchors: `- 证据边界：年报2024§...；年报2024§...。`
- Existing no-anchor fallback text remains exact unless implementation discovers punctuation-only formatting conflict.

## 8. Implementation Decisions

1. Update `_item_rule_evidence_bullet(anchors)` in `fund_agent/fund/template/renderer.py` only.
2. Preserve existing `_dedupe_anchors(...)` call sites; the helper should also be robust if passed a non-deduped tuple by de-duplicating locally or by documenting it consumes pre-deduped anchors. Preferred implementation: call `_dedupe_anchors(anchors)` inside `_item_rule_evidence_bullet` to make the helper self-contained.
3. Format all anchors using existing `_body_anchor_reference(anchor)` to preserve body evidence reference format.
4. Join multiple anchor references with `；` inside the same bullet to avoid introducing extra `> 📎 证据` lines and avoid changing P3 chapter evidence semantics.
5. Keep output deterministic and stable by preserving input order after de-duplication.
6. Do not add truncation or “等 N 条” behavior in this slice. Current deterministic renderer fixtures use a small anchor set; truncation policy would require a separate UX/contract decision.
7. Do not alter `_render_tracking_error_segment()` text: it must remain data-insufficient and must not imply anchors prove tracking error.

## 9. Small Implementation Slices

### Slice 1: Multi-anchor ITEM_RULE evidence bullet

**Objective**: Change the helper to render every relevant anchor in a single deterministic bullet.

**Allowed files**:

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`

**Prerequisites**: P12-S1 accepted behavior exists; `_item_rule_evidence_bullet()` is the only current formatter for ITEM_RULE local evidence boundary.

**Exact changes**:

- In `_item_rule_evidence_bullet(anchors)`:
  - if anchors empty, keep current no-anchor text exactly;
  - otherwise compute `anchor_references = tuple(_body_anchor_reference(anchor) for anchor in _dedupe_anchors(anchors))`;
  - return `f"- 证据边界：{'；'.join(anchor_references)}。"` or equivalent deterministic implementation;
  - keep Chinese docstring updated to state all deduped anchors are rendered.
- In `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` or a new focused test:
  - render `enhanced_index`;
  - locate chapter 2 `#### 跟踪误差分析` segment;
  - extract the single line that starts with `- 证据边界：`;
  - assert this same line includes at least one benchmark anchor reference and at least one R=A+B-C attribution anchor reference from the fixture, using the exact `_body_anchor_reference(...)` text or exact equivalent literal expected text;
  - assert the same line contains `；` between references when two or more distinct anchors exist; checking `；` alone is insufficient;
  - assert tracking error still says `数据不足，当前输入未抽取跟踪误差。`
- Add an explicit empty-anchor path test:
  - keep `identity_present` by starting from a normal typed render input, not `missing=True`;
  - construct the missing segment input with inline `replace(...)`, preferably clearing the relevant field anchors or attribution anchors for one triggered ITEM_RULE segment;
  - do not expand `_render_input` / `_bundle` fixture factories for this edge case;
  - assert the triggered segment still renders and its evidence boundary line is exactly `- 证据边界：数据不足，当前段落未携带独立证据锚点。`
- Add an explicit duplicate-anchor path test:
  - construct a tuple containing the same `EvidenceAnchor` more than once and verify the rendered evidence boundary contains that anchor reference once;
  - either test `_item_rule_evidence_bullet(...)` directly or trigger it through a segment with inline `replace(...)`;
  - direct access to `_item_rule_evidence_bullet` is allowed only inside `tests/fund/template/test_renderer.py` as a renderer unit test for this private formatting helper, and must not turn the helper into a public export.
- Add or preserve a single-anchor assertion:
  - active fund manager philosophy or index constituents segment may still have one source anchor;
  - expected output should have no duplicated same anchor and no extra chapter-level `> 📎 证据` line inside the ITEM_RULE segment.

**Data flow / invariants**:

- `TemplateRenderInput` -> `_render_tracking_error_segment()` -> `_item_rule_evidence_bullet()` -> Markdown only.
- `item_rule_decisions` and programmatic audit marker checks are unchanged.
- Existing `_collect_rabc_anchors()` and `_dedupe_anchors()` remain the source of anchor ordering.

**Error handling**:

- Empty tuple remains non-error and renders explicit data-insufficient evidence boundary.
- No new exceptions should be introduced.

**Non-goals**:

- No new anchor model.
- No evidence appendix changes.
- No audit rule changes.

**Completion signal**:

- Targeted renderer tests pass and diff shows only renderer helper/test changes for Slice 1.

**Stop condition**:

- Stop if implementation needs to change `EvidenceAnchor`, audit input schema, source extraction, or Service code.

### Slice 2: Documentation sync

**Objective**: Update package/test docs to describe current multi-anchor local evidence boundary without overstating semantic proof.

**Allowed files**:

- `fund_agent/fund/README.md`
- `tests/README.md`

**Exact changes**:

- In `fund_agent/fund/README.md` ITEM_RULE/renderer section:
  - add one sentence that ITEM_RULE local evidence boundary renders all deduped relevant anchors in one bullet;
  - state this preserves existing chapter-level `> 📎 证据` line and does not prove tracking error/index methodology/constituents.
- In `tests/README.md` renderer test description:
  - mention ITEM_RULE fixed segments include multi-anchor evidence boundary coverage.
- Do not add future promises or mention planned extractors as implemented.

**Completion signal**:

- README wording matches implemented behavior and keeps FQ5/audit boundaries unchanged.

**Stop condition**:

- Stop if docs update would require changing `docs/design.md` or `docs/implementation-control.md`; this slice is too small to justify design/control edits.

## 10. Tests / Validation Commands / Expected Assertions / Failure Paths

Run:

```bash
pytest tests/fund/template/test_renderer.py
pytest tests/fund/template/test_item_rules.py tests/fund/audit/test_audit_programmatic.py
ruff check fund_agent/fund/template tests/fund/template
git diff --check HEAD
```

Expected assertions:

- `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` or new equivalent test verifies a multi-anchor ITEM_RULE evidence bullet includes all deduped references.
- The multi-anchor test must verify concrete anchor reference text, not only punctuation: at least one benchmark `_body_anchor_reference(...)` output and at least one R=A+B-C `_body_anchor_reference(...)` output must appear on the same `- 证据边界：` line.
- A separate empty-anchor path test must keep identity present, trigger an ITEM_RULE segment whose relevant anchors are empty via inline `replace(...)`, and assert the exact no-anchor text.
- A separate duplicate-anchor path test must prove the same anchor reference is rendered once after de-duplication; direct private-helper testing is acceptable only in renderer unit tests.
- Existing six fund-type ITEM_RULE render/delete matrix still passes.
- Existing audit ITEM_RULE C2 tests still pass without any audit source change.
- No test should assert tracking error is available; it must remain `数据不足`.

Failure paths that must be tested or manually checked:

- Empty anchors still render explicit no-anchor data-insufficient evidence boundary.
- Duplicate anchors do not render twice.
- Multiple anchors do not create extra `> 📎 证据` lines inside ITEM_RULE segments.
- Programmatic audit still passes for a valid rendered report because segment markers remain unchanged.

Full suite `pytest` is recommended before accepted slice commit, but the implementation handoff minimum is the targeted commands above. If full suite is skipped or fails for unrelated pre-existing reasons, implementation report must state the reason and exact failure.

## 10.1 Plan Review Response / Finding Disposition

| Finding | Source | Disposition | Plan update |
|---|---|---|---|
| Duplicate anchor 测试路径未明确要求为独立 test case | MiMo F1 | accepted | §9 Slice 1 和 §10 现在明确要求 duplicate-anchor path test；允许在 `tests/fund/template/test_renderer.py` 直接测试 `_item_rule_evidence_bullet(...)`，但不得导出私有 helper。 |
| 多锚点断言应验证具体 anchor 文本，不仅仅是分隔符 | GLM F1 | accepted | §9 Slice 1 和 §10 现在要求同一 `- 证据边界：` 行同时包含 benchmark anchor 和 R=A+B-C anchor 的具体 `_body_anchor_reference(...)` 文本；`；` 只能作为附加断言。 |
| Empty anchor 路径需要显式测试策略 | GLM F2 | accepted | §9 Slice 1 和 §10 现在要求 identity_present 场景下用 inline `replace(...)` 清空相关 anchors，断言 exact no-anchor 文本；不得扩展 fixture factory。 |
| Duplicate anchor 消除需要显式测试方案 | GLM F3 | accepted | 与 MiMo F1 合并处理；§9 Slice 1 和 §10 指定直接 helper 测试或 segment 间接触发均可，但私有 helper 访问仅限 renderer unit test。 |

## 11. Docs Decision

Update `fund_agent/fund/README.md` and `tests/README.md` because `fund_agent/fund/template/renderer.py` and renderer tests change. Do not update:

- `docs/design.md`: no architecture, public contract, template chapter structure, audit layer, or source boundary change.
- `docs/implementation-control.md`: controller owns phase ledger update after implementation/review acceptance, not this implementation slice.
- Root `README.md`: no CLI/user workflow change.
- `docs/repo-audit-20260521.md`: remains an excluded, untracked audit input.

## 12. Review Gates

Plan review should verify:

- Selected slice is truly smaller and safer than real extractor/calculation work.
- Allowed files keep changes inside Fund Capability renderer/docs/tests.
- Tests prove multi-anchor behavior and preserve no-anchor/data-insufficient paths.
- Non-goals prevent semantic overclaiming and source-boundary drift.

Code review should verify:

- `_item_rule_evidence_bullet()` renders all deduped anchors in deterministic order.
- No extra chapter-level evidence quote is introduced inside ITEM_RULE segments.
- Tracking error / index methodology / constituents remain data-insufficient unless real data exists.
- No Service/UI/CLI/audit/quality gate/source repository changes were made.
- README wording does not claim FQ5 or C2 proves semantic evidence sufficiency.

Aggregate review is not required for this planning-only artifact. For the eventual implementation work unit, follow normal gateflow review/fix/re-review and accepted local commit rules.

## 13. Stop Conditions

Stop and return control to controller if any of the following occurs:

- Implementing all anchors requires changing `EvidenceAnchor` schema or public renderer/audit dataclasses.
- Multiple anchors expose excessive output length that would require truncation, grouping, appendix, or UX policy.
- Tests reveal current fixtures do not contain at least two distinct anchors for a multi-anchor segment; controller should decide whether to extend fixture data or pick another slice.
- Implementation needs to touch Service/UI/CLI, `FundDocumentRepository`, document sources, quality gate, `docs/design.md`, `docs/implementation-control.md`, RR-13 source files, or `docs/repo-audit-20260521.md`.
- Any reviewer argues multi-anchor display should be deferred until Evidence Confirm; controller must adjudicate because this plan intentionally treats it as deterministic renderer provenance display, not evidence verification.

## 14. Risks / Open Questions

| Risk / question | Blocking? | Working assumption / owner |
|---|---:|---|
| Multi-anchor line may get long in future real data | No | Current deterministic fixtures are small; no truncation until real large anchor sets exist. Future evidence-display UX slice owns truncation/grouping. |
| Multi-anchor display does not prove evidence supports the claim | No | Correct: this slice only displays provenance. E1/E2/E3 evidence matching remains future audit. |
| Tracking error remains data-insufficient after this slice | No | Intentional non-goal; real extractor/calculation remains future product slice. |
| RR-13 duplicate `016492` remains unresolved | No | User/App source owned; not safe for code to auto-decide. |
| `docs/repo-audit-20260521.md` remains untracked | No | Control doc says keep excluded unless future scope explicitly accepts publication. |

No blocking open questions for controller.

## 15. Completion Report Format

Implementation agent should report:

```markdown
## P12-S2 Implementation Report

- Gate: `P12-S2 ITEM_RULE multi-anchor evidence boundary implementation`
- Approved plan: `docs/reviews/post-p12-s1-follow-up-planning-20260522.md`
- Slice(s): Slice 1 / Slice 2
- Changed files:
  - ...
- Implemented:
  - ...
- Validation:
  - `pytest tests/fund/template/test_renderer.py`: ...
  - `pytest tests/fund/template/test_item_rules.py tests/fund/audit/test_audit_programmatic.py`: ...
  - `ruff check fund_agent/fund/template tests/fund/template`: ...
  - `git diff --check HEAD`: ...
- Docs decision:
  - ...
- Residual risks:
  - ...
- Stop status: completed / stopped with reason
- Artifact path: `docs/reviews/p12-s2-implementation-20260522.md`
```

## 16. Recommended Next Gate

Proceed to:

```text
P12-S2 ITEM_RULE multi-anchor evidence boundary plan review
```

After plan review/re-review acceptance, implementation should receive only the P12-S2 slice above. No blocking open questions.
