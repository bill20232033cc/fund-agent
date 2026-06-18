# 004393 / 004194 / 006597 Strict Correctness Follow-up Plan — Review (MiMo)

日期：2026-05-29

角色：AgentMiMo，independent plan reviewer。不是 controller，不做实现。

## Verdict

**PASS**

Plan 在所有关键约束上与 AGENTS.md、docs/design.md、docs/implementation-control.md、上一 strict golden correctness fixture promotion controller judgment / decision、fixture promotion state manifest、golden readiness preflight 输出、以及 004393 / 004194 / 006597 score / quality artifacts 对齐。无需修改即可进入 implementation worker。

## Review Scope

审核对象：`docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md`

核对来源：
- `AGENTS.md`（规则真源）
- `docs/design.md` v2.2（设计真源）
- `docs/implementation-control.md` v2.1（实施总控）
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json`、`quality_gate.json`、`golden_set.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`、`quality_gate.json`、`golden_set.json`
- `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`、`score.md`、`golden_set.json`
- `reports/golden-answers/golden-answer.json`（验证 006597 覆盖）
- `uv run fund-analysis extraction-score --help`（验证 public CLI）

## Findings

### F1 — 006597 rerun 命令完整性与 public CLI

**结论：通过。**

- `uv run fund-analysis extraction-score --help` 确认 `--snapshot-path`、`--errors-path`、`--golden-answer-path`、`--output-dir` 均为 public 参数。
- Plan 指定的 rerun 命令使用正确路径：
  - `--snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl` — 文件存在。
  - `--errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl` — 文件存在。
  - `--golden-answer-path reports/golden-answers/golden-answer.json` — 文件存在，已验证包含 `006597` 的 20 条记录。
  - `--output-dir reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529` — 新输出目录，不覆盖现有产物。
- 当前 006597 score 的 `golden_answer_path=""`、`total_records=0`、`comparable_records=0`、`correctness=unavailable` 是因为未提供 golden answer path（machine setup failure），而非 fund evidence failure。Rerun 后应产出实际 correctness 数据。

### F2 — mismatch / unavailable 按用户停止条件处理

**结论：通过。**

Plan Result Handling Rules（§006597）正确覆盖三种场景：
1. `correctness` remains `unavailable / not_configured` → classify as machine setup failure，不是 fund evidence failure。正确。
2. `mismatched_records > 0` → open manual evidence confirmation for mismatched records only；do not edit golden answer in this gate。正确。
3. `unavailable_records > 0` → manually inspect only 006597 same-year records；不跨基金检查。正确。

Stop Conditions 明确：Stop if any step requires editing golden-answer.json or golden fixtures；Stop if any step would set `promotion_allowed=true`。正确。

### F3 — 004393 partial coverage 未被升级为 minimum v1 promotion-prep

**结论：通过。**

- 当前 004393 score：`coverage_scope=partially_covered`，`comparable_records=9`，`total_records=150`，P0 9/11，P1 0/10，`mismatched_records=0`。
- Plan decision：`not_minimum_v1_promotion_prep_by_default`。
- Required residual owner：future partial-coverage / extractor coverage decision gate。
- Plan 明确 "Escalate only if a controller explicitly accepts P0 9/11 and P1 0/10 residual risk with named missing fields and owner"。
- 与 controller judgment 的 `conditional_candidate_pending_partial_coverage_decision` 一致。
- 未将 partial coverage 误升级为 full readiness。

### F4 — 004194 index_profile-only 未被误判为 full fixture ready

**结论：通过。**

- 当前 004194 score：`coverage_scope=covered`，但 `comparable_records=5`（仅 `index_profile.*` 字段），P0 strict correctness coverage=0。
- Plan decision：`index_profile_only_candidate_not_full_fixture_ready`。
- Plan 明确 "Do not treat five matched `index_profile.*` records as full fixture readiness"。
- Required residual owner：P0 strict correctness coverage gate。
- Stop condition："Stop if implementation wording suggests `004194` is full `promotion-prep-ready`"。
- 与 controller judgment 的 `conditional_candidate_pending_p0_coverage_decision` 一致。

### F5 — 不需要更新 manifest / preflight

**结论：通过。**

- Plan 明确 "No fixture manifest update"、"No golden readiness residual disposition manifest update"、"No preflight rerun in this gate"。
- 理由正确：所有三行仍 `promotion_allowed=false`；manifest 是 accepted control-plane evidence；更新 manifest 属于 fixture promotion state gate。
- Preflight rerun without separate consumption/path update 不会证明新 promotion readiness。
- Decision artifact 明确标记 `not_promotion_manifest=true` 和 `runtime_consumed=false`。

### F6 — promotion_allowed=false，不改 golden fixtures，不改 FQ0-FQ6

**结论：通过。**

- Plan 所有 result handling rules 保持 `promotion_allowed=false` 和 `fixture_state=absent`。
- Scope 部分明确 "No score / quality / snapshot / FQ0-FQ6 semantic changes"。
- Stop conditions 覆盖所有 mutation 场景。
- Validation matrix 包含 `git diff -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` 验证无 mutation。
- 006597 bond blocker closure 保持为 resolved context only，不替代 strict correctness evidence。

## Observations（不阻塞 PASS）

### O1 — Validation Matrix 命令在 Implementation Steps 中未完全显式引用

Validation Matrix 列出 7 项检查，Implementation Steps 第 7 步说 "Run validation commands from the matrix below"。Implementation Steps 1-6 中只显式引用了 `git diff --check` 和 `python -m json.tool`。建议 implementation worker 在 step 7 中逐项执行 matrix 全部命令，而非仅执行步骤中提及的子集。不阻塞，因为 matrix 本身是权威验证清单。

### O2 — Quality-gate rerun 输出路径与现有 fixture 路径不同

Plan 推荐的 quality-gate rerun 输出到 `reports/quality-gate-runs/strict-correctness-follow-up-006597-2024-20260529/`，而非现有 fixture 路径 `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/`。这是正确行为——新输出是 follow-up decision 的 read-only evidence，不是 fixture 更新。Plan 明确 "The quality-gate rerun is not a policy change"。建议 implementation worker 在 decision artifact 中记录两个路径的关系。

### O3 — 006597 golden_set.json 当前为空

当前 `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/golden_set.json` 无 `source_score_golden_set_path`（fixture manifest 中为 `null`），因为未提供 golden answer path。Rerun 后新 score 将产出 populated golden_set.json。Decision artifact 应引用新路径。

## Alignment Checklist

| 检查项 | 结果 |
|---|---|
| AGENTS.md Gate 轻重分类：heavy 分类正确 | ✓ 影响 strict golden correctness / fixture promotion 前置判断 |
| AGENTS.md 硬约束：不修改代码、不改 public contract | ✓ Scope 明确 out of scope |
| docs/design.md：不改 FQ0-FQ6 语义 | ✓ Scope 和 Stop Conditions 覆盖 |
| docs/implementation-control.md Next Entry Point 对齐 | ✓ Plan 与 control doc 的 "004393 / 004194 / 006597 strict correctness follow-up gate" 一致 |
| Controller judgment decisions 对齐 | ✓ 004393=conditional_pending_partial, 004194=conditional_pending_p0, 006597=needs_future_gate |
| Fixture manifest 所有行 promotion_allowed=false | ✓ Plan 保持不变 |
| Residual disposition manifest 未被修改 | ✓ Plan 不更新 manifest |
| Preflight 输出未被修改 | ✓ Plan 不 rerun preflight |
| Golden answer / golden fixtures 未被修改 | ✓ Stop condition 覆盖 |
| 006597 bond blocker closure 未被误用 | ✓ "Bond resolved does not imply promotion-ready" |
| QDII / FOF / 110020 未被拉入 | ✓ Scope 明确 out of scope |
| No PR / push / merge / release | ✓ Scope 明确 out of scope |
