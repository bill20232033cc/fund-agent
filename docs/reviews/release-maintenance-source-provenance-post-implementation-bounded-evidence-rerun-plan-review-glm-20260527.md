# Plan Review: Source Provenance Post-Implementation Bounded Evidence Rerun Plan

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27
> **Timestamp**: 20260527-065654
> **Plan artifact**: `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` (lines 603-624, source provenance section), `docs/implementation-control.md` (Startup Packet, Current Gate, Next Entry Point), accepted commit `f88a3aa`
> **Verdict**: **pass**

---

## Reviewed Target and Scope

Plan 要求为 `110020/2024` 和 `017641/2024` 两个 fund/year pair 执行 bounded public evidence rerun，验证 accepted source provenance implementation（`primary_failure_category` 持久化）后的公开 CLI 输出行为。Evidence worker 仅通过 `fund-analysis extraction-snapshot`、`extraction-score`、`quality-gate` 三个公开 CLI 命令分类每个 fund，禁止任何 promotion。

### Review Focus Areas

1. `--force-refresh` 是否是安全的公开路径，是否会改变 source strategy 或掩盖旧 cache 行为
2. 命令顺序和 output path 选择，特别是 score/quality 输出到同一 extraction-snapshot 目录
3. 分类排序：`repository_run_failed` vs `provenance_unknown_public_metadata_absent` vs `quality_blocked_after_provenance`
4. 无 promotion 纪律和禁止私有 source/cache/PDF 检查

## Assumptions Tested

| # | Assumption | Evidence | Result |
|---|---|---|---|
| A1 | `--force-refresh` 是纯 cache-bypass 机制，不改变 source strategy、fallback 逻辑或 provenance 投影 | CLI 定义 `cli.py:392-394`；`repository.py:323-324, 339-344` 跳过 parsed report cache 和 PDF path cache；`sources.py:598-660` orchestrator 的 fallback 逻辑完全独立于 `force_refresh`；`source_provenance.py:105-176` 无 `force_refresh` 参数 | **Confirmed** |
| A2 | 三个 CLI 命令写入同一 output-dir 不会产生文件名冲突 | `extraction_snapshot.py:438-440` 写 `snapshot.jsonl`, `errors.jsonl`, `summary.md`；`extraction_score.py:79-81, 1077-1079` 写 `score.json`, `score.md`, `golden_set.json`；`quality_gate.py:15-16, 196-197` 写 `quality_gate.json`, `quality_gate.md`；8 个文件名完全不相交 | **Confirmed** |
| A3 | `provenance_fail_closed` 在分类排序中正确优先于 `quality_blocked_after_provenance` | `source_provenance.py:156-166` fail-closed 是 snapshot-level 判定；plan stop conditions 明确禁止 quality output 覆盖 fail-closed | **Confirmed** |
| A4 | `provenance_unknown_public_metadata_absent` 和 `provenance_fail_closed` 互斥 | `source_provenance.py:139-176` 三分支 if/elif/return 逻辑，`effective_category` 只能命中一个分支或落入 unknown | **Confirmed** |
| A5 | `fallback_eligibility=fail_closed` 是真实的持久化字段 | `source_provenance.py:41` Literal 类型定义；`source_provenance.py:163` 直接赋值；`extraction_snapshot.py:1055` 写入 SnapshotRecord | **Confirmed** |
| A6 | Evidence worker 无需也不应进行私有 source/cache/PDF 检查 | Plan Forbidden Scope 明确列出所有禁止操作；AGENTS.md 硬约束要求通过统一文档仓库接口存取 | **Confirmed** |
| A7 | `--force-refresh` 后若 `primary_failure_category` 仍缺失，保守分类为 `provenance_unknown_public_metadata_absent` | Plan line 37-38 明确要求；`design.md` line 624 要求不得推断为 eligible | **Confirmed** |

## Detailed Review by Focus Area

### 1. `--force-refresh` 安全性

**结论：安全，无问题。**

代码证据链完整：
- `--force-refresh` 从 CLI (`cli.py:392`) 传入 `ExtractionSnapshotRequest` (`extraction_snapshot_service.py:36`)，透传到 `SnapshotExtractor.extract()` (`extraction_snapshot.py:452-458`)，再到 `FundDataExtractor.extract()` (`data_extractor.py:153-211`)，最终到达 `FundDocumentRepository.load_annual_report()` (`repository.py:290-385`) 和各 source 实现。
- 沿途无任何分支逻辑根据 `force_refresh` 改变 source strategy、fallback 规则、failure category 判定或 provenance 投影。
- `project_public_source_provenance()` (`source_provenance.py:105-176`) 完全不感知 `force_refresh`，仅从 `AnnualReportSourceMetadata` 推导。
- `AnnualReportSourceOrchestrator.fetch_annual_report_pdf()` (`sources.py:598-660`) 的 fallback 判定逻辑独立于 `force_refresh`。

Plan 的使用理由也成立：旧 cache 中的 metadata 可能有 `fallback_used=true` 但缺少 `primary_failure_category`（因为该字段是新实现的），`--force-refresh` 强制重新走完整 pipeline，使新的 `primary_failure_category` 持久化逻辑有机会生效。Plan 同时正确处理了即使刷新后 `primary_failure_category` 仍缺失的保守分类。

### 2. 命令顺序和 Output Path

**结论：无问题。**

三个命令按 `extraction-snapshot` → `extraction-score` → `quality-gate` 顺序执行。这是正确的 pipeline 依赖顺序：score 需要 snapshot 输出，quality-gate 需要 score 输出。

8 个输出文件名完全不相交：
- Snapshot: `snapshot.jsonl`, `errors.jsonl`, `summary.md`
- Score: `score.json`, `score.md`, `golden_set.json`
- Quality-gate: `quality_gate.json`, `quality_gate.md`

共享同一 `reports/extraction-snapshots/<run_id>/` 目录是项目的标准设计模式（score 默认 `output_dir` 就是 `snapshot_path.parent`，quality-gate 默认是 `score_path.parent`）。

Plan 为每个 fund 使用独立的 `run_id` 和 `output_dir`，两个 fund 之间完全隔离。

### 3. 分类排序

**结论：排序正确，与代码实现一致。**

分类表描述的条件在 provenance 层面互斥：
- `repository_run_failed`：snapshot 命令失败或无行
- `primary_succeeded_no_fallback`：`fallback_used=false`
- `provenance_unknown_public_metadata_absent`：`fallback_used=true`，无 category
- `provenance_fail_closed`：fail-closed category

质量层状态 `quality_blocked_after_provenance` 仅在 provenance 层无问题时适用（provenance 是 `primary_succeeded_no_fallback` 或 eligible complete fallback），这与其前置条件 "Provenance is `primary_succeeded_no_fallback` or eligible complete fallback" 一致。

代码中 `source_provenance.py:139-176` 的三分支逻辑确认 `eligible`、`fail_closed`、`unknown_public_metadata_absent` 互斥。Plan 的 stop conditions 明确 `provenance_fail_closed` 优先于 quality output。

唯一潜在歧义：`primary_succeeded_no_fallback` 的描述提到 "Quality may still pass/warn/block separately"，而 `quality_blocked_after_provenance` 的条件也覆盖了 provenance 为 `primary_succeeded_no_fallback` 的情况。但 plan 的 stop conditions 和 line 165 明确说明 score/quality 失败时应归为 `quality_blocked_after_provenance`，整体语义自洽。

### 4. 无 Promotion 纪律和禁止私有检查

**结论：充分且正确。**

- Plan Objective 明确 "No row may be promoted"，"Every disposition row in the evidence artifact must keep `promotion_disposition=not_promoted`"。
- Forbidden Scope 列出 10 类禁止操作，包括 baseline/golden/fixture/clean-denominator/corpus promotion、manual cache deletion、cache inspection、private `FundDocumentRepository` calls、source helper calls、PDF inspection、source/cache filesystem probing。
- Evidence Summary Artifact Contract 要求 "No durable baseline/golden/clean-denominator promotion statement"。
- Stop Conditions 明确 "Any command path would require private FundDocumentRepository, source helper, PDF/cache inspection, manual cache deletion, code changes, or docs/design/control edits: stop and return to controller。"

与 AGENTS.md 硬约束一致："生产年报 PDF 访问必须经过 FundDocumentRepository"、"年报来源编排属于 Agent 层 fund_agent/fund documents 内部实现，Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。"

## Findings

无 material finding。

所有 review focus area 经代码证据验证后均确认安全：
1. `--force-refresh` 是安全的纯 cache-bypass 公开路径
2. 命令顺序和 output path 无冲突
3. 分类排序与代码实现一致
4. 无 promotion 纪律和禁止私有检查充分

## Open Questions

无。

## Residual Risks

| Risk | Likelihood | Tracking |
|---|---|---|
| `--force-refresh` 后主源行为可能因外部状态变化而与历史 cache 不同（如 EID 恢复可用），导致 provenance 分类与预期不符 | Low | Plan 已覆盖：provenance 分类完全基于公开输出，不依赖预期行为 |
| 两个 fund 的 provenance 分类可能均为 `provenance_unknown_public_metadata_absent`（如果 fallback 仍成功但 `primary_failure_category` 因代码路径未触及而未持久化） | Low | Plan 已覆盖：保守分类为 unknown，不推断 eligible |
| Evidence worker 可能在 `primary_succeeded_no_fallback` + quality block 场景下对归为 `primary_succeeded_no_fallback` 还是 `quality_blocked_after_provenance` 产生歧义 | Low | Plan stop conditions 和 line 165 足够明确，但建议 evidence worker 优先匹配最具体条件 |

## Reviewer Self-Check

- [x] Reviewed target、scope、source of truth 和 assumptions tested 已写清
- [x] 无 findings 需要写，确认所有 review focus area 经证据验证后安全
- [x] Open questions、residual risks 与 findings 分开
- [x] Conclusion 为 `pass`
- [x] Artifact 使用系统时钟生成 timestamp

## Conclusion

**pass**

Plan 在所有 review focus area 上均有充分的代码证据支撑。`--force-refresh` 是安全的纯 cache-bypass 路径；命令顺序和 output path 无冲突；分类排序与代码实现一致；无 promotion 纪律和禁止私有检查覆盖完整。无 material finding，无 open question，residual risks 均已被 plan 本身的保守分类规则覆盖。
