# Plan Review: Source Provenance Post-Implementation Bounded Evidence Rerun

> Reviewer: AgentMiMo
> Date: 2026-05-27 (065517)
> Reviewed target: `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-20260527.md`
> Scope: Bounded evidence rerun plan for fund 110020/2024 and 017641/2024 after accepted source provenance implementation
> Gate: `source provenance post-implementation bounded evidence rerun plan/review gate`

## Truth Sources Consulted

| Source | Key facts verified |
|--------|-------------------|
| `AGENTS.md` | 基金来源 fallback 策略五类失败；`FundDocumentRepository` 统一入口约束；禁止直接操作文件系统 |
| `docs/design.md` §6.1 | Source provenance 实现事实：公共投影字段、`primary_failure_category` 持久化条件、`unknown_public_metadata_absent` 分类规则、不授权 baseline/golden promotion |
| `docs/implementation-control.md` Startup Packet | Current gate: `source provenance primary-failure-category propagation implementation accepted locally`; Next entry: `source provenance post-implementation bounded evidence rerun plan/review gate` |
| Code: `fund_agent/fund/extraction_snapshot.py` | `force_refresh` 参数存在并传递到仓库层；公共 provenance 字段（8 个）已实现；`_source_provenance_summary_lines` 输出 |
| Code: `fund_agent/ui/cli.py` | `--force-refresh` 是 `extraction-snapshot` 的公开 CLI 选项 |
| `.gitignore` | `reports/extraction-snapshots/` 已被忽略，生成产物不会进入版本控制 |
| Commit `f88a3aa` | `feat: persist annual report fallback failure category` — 与 plan 声称的最新 accepted commit 一致 |

## Assumptions Tested

1. `--force-refresh` 是公开 CLI 选项且传递到仓库层 → **confirmed** (`cli.py:129-130`, `extraction_snapshot.py:102`)
2. 公共 provenance 字段（8 个）已在 snapshot JSONL 中实现 → **confirmed** (`extraction_snapshot.py:222-229`)
3. `reports/extraction-snapshots/` 被 `.gitignore` 忽略 → **confirmed** (`.gitignore:19`)
4. `primary_failure_category` 仅在 fallback 成功后持久化 → **confirmed** (`design.md` §6.1 当前已实现段落)
5. 旧缓存可能缺少 `primary_failure_category` → **confirmed** (`design.md`: "若 `fallback_used=true` 但旧缓存或测试元数据未持久化该字段，`fallback_eligibility` 必须为 `unknown_public_metadata_absent`")
6. Plan 不允许代码/设计/控制文档修改 → **confirmed** (Forbidden Scope 节完整覆盖)

## Findings

无 material finding。

Review focus area 逐项验证结果：

### 1. Commands are public CLI only, bounded to 110020/2024 and 017641/2024

- 三个命令 `fund-analysis extraction-snapshot`、`fund-analysis extraction-score`、`fund-analysis quality-gate` 均为 `fund_agent/ui/cli.py` 中注册的公开 Typer 命令。
- Bounded corpus 表只包含 `110020/2024` 和 `017641/2024`，plan 明确声明"No other fund may be added in this evidence gate"。
- 每个命令使用独立 run ID 和 output dir，不会交叉污染。**PASS**。

### 2. --force-refresh usage is appropriate; no manual cache/source/PDF inspection allowed

- `--force-refresh` 通过公开 CLI 传递，理由充分：旧缓存可能已有 `fallback_used=true` 但缺少 `primary_failure_category`，重用会产出 `unknown_public_metadata_absent` 而掩盖新实现的行为。
- Plan 明确禁止："evidence worker must not delete, rename, inspect, or manually patch any cache file"。
- 若 `--force-refresh` 后仍为 `fallback_used=true` + 缺失 `primary_failure_category`，plan 要求保守分类为 `provenance_unknown_public_metadata_absent`，不得推断。**PASS**。

### 3. Output paths/run ids are deterministic; generated outputs remain ignored

- Run ID 格式 `source-provenance-rerun-{fund_code}-{report_year}-{date}` 是确定性的。
- Output dir 与 run ID 一一对应，格式 `reports/extraction-snapshots/{run_id}`。
- `.gitignore` 第 19 行确认 `reports/extraction-snapshots/` 被忽略。
- Plan 明确声明产物"must not become durable baseline, golden, fixture, or clean-denominator assets"。**PASS**。

### 4. Terminal state taxonomy and no-promotion discipline are correct

七种 terminal state 与 design.md source provenance 字段语义一致：

| Terminal state | 与 design.md 一致性 |
|---|---|
| `repository_run_failed` | 覆盖命令失败和空 snapshot + errors 场景 |
| `primary_succeeded_no_fallback` | 与 `fallback_used=false` + `primary_failure_category=null` 一致 |
| `provenance_unknown_public_metadata_absent` | 与 design.md `unknown_public_metadata_absent` 分类规则一致 |
| `provenance_fail_closed` | 覆盖 `fail_closed` eligibility 和不一致场景 |
| `quality_blocked_after_provenance` | 正确处理 score/gate 失败但 provenance 完成的场景 |
| `provenance_eligible_for_next_review` | 限定 `not_found`/`unavailable` + `eligible` + quality pass/warn |
| `not_promoted` | 强制对所有 fund 和所有 row 生效 |

No-promotion discipline 贯穿 plan 全文：Objective、Classification Rules、Evidence Summary Artifact Contract、Review Matrix、Acceptance Criteria 均提及。**PASS**。

### 5. Plan does not permit forbidden scope changes

Forbidden Scope 节覆盖：
- Code changes ✅
- Source strategy changes ✅
- FQ0-FQ6 / quality gate semantic changes ✅
- Renderer changes ✅
- Default CLI behavior changes ✅
- Host / Agent / Dayu changes ✅
- Baseline, golden, fixture, clean-denominator, corpus promotion ✅
- Manual cache operations, private FundDocumentRepository calls, source helper calls, PDF inspection ✅
- Edits to docs/design.md or docs/implementation-control.md ✅
- Commit, push, PR, or branch operations ✅

Plan 还在 Worker 定位中声明"This worker is planning-only"。**PASS**。

### 6. Classification logic edge cases

- `extraction-score` 失败处理：plan 要求先按 snapshot provenance 分类，再标记 quality unavailable，不尝试 quality-gate。这避免了在 provenance 已知但 quality 不可用时丢失信息。**PASS**。
- Provenance tuple 一致性检查：plan 要求同一 fund 所有成功 row 必须同意 provenance tuple，不一致则 `provenance_fail_closed`。这正确处理了同一 fund 多行可能出现不同 provenance 的异常情况。**PASS**。
- `provenance_fail_closed` 优先于 quality output：plan 明确"Treat this as fail-closed even if downstream score/gate exists"，避免 quality pass 掩盖 provenance 失败。**PASS**。

## Open Questions

无。

## Residual Risks

| Risk | Severity | Tracking |
|------|----------|----------|
| `--force-refresh` 实际行为取决于仓库层实现；若仓库层 force_refresh 未完全清除 parsed report 缓存，可能仍返回旧 metadata | 低 | Evidence run 将验证；若出现 `unknown_public_metadata_absent` 即为信号 |
| `docs/code_20260519.csv` 是否包含 110020 和 017641 未在 plan 中显式验证 | 低 | Evidence run 的 extraction-snapshot 命令会在 CSV 不包含目标 fund 时失败，落入 `repository_run_failed` |

## Reviewer Self-Check

- [x] Reviewed target、scope、source of truth 和 assumptions tested 已写清
- [x] 无 finding（plan 在所有 review focus area 均通过验证）
- [x] Open questions、residual risks 与 findings 分开
- [x] Conclusion 只能是 `pass`、`pass-with-risks` 或 `fail`
- [x] Output path 使用本机系统时钟生成的 timestamp，格式匹配 `docs/reviews/plan-review-[0-9]{8}-[0-9]{6}.md`

## Conclusion

**PASS**

Plan 在所有 review focus area 均通过验证。命令为公开 CLI、bounded 到两个 fund/year pair、`--force-refresh` 使用合理、输出路径确定性且 gitignored、terminal state taxonomy 与 design.md source provenance 字段语义一致、no-promotion discipline 贯穿全文、forbidden scope 完整覆盖。无 material finding。Plan 可安全交给 evidence worker 执行。

Output path: `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-review-mimo-20260527.md`
