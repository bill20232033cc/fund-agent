# Code Review

## Scope

- Mode: current changes（evidence artifact review）
- Review target: `docs/reviews/release-maintenance-index-qdii-source-recovery-evidence-20260527.md`
- Reviewer: AgentGLM
- Date: 2026-05-27
- Output file: `docs/reviews/release-maintenance-index-qdii-source-recovery-evidence-review-glm-20260527.md`
- Base: `codex/local-reconciliation` HEAD
- Included scope: evidence artifact 的 terminal state 分类、public output 直接证据链、quality gate 与 source safety 边界、replacement 探测记录、next recommended gate
- Excluded scope: 未重跑 CLI 命令或验证生成产物内容；未检查 `reports/extraction-snapshots/` 下的实际文件
- Parallel review coverage: 无

## Findings

### F1-未修复-低-Subgate B terminal state `not_run_no_approved_candidates` 未在 Per-Candidate Terminal State 表中正式声明

- **入口/函数**: Per-Candidate Terminal State 表（证据文档第 40-47 行）
- **文件(行号)**: evidence artifact 第 40-47 行
- **输入场景**: 两个 candidate 均为 Subgate A `unrecoverable_safe_path`，且无 controller-approved replacement candidate
- **实际分支**: 表中仅声明 `unrecoverable_safe_path`，未声明 Subgate B terminal state
- **预期行为**: plan §3.2 要求 "Close replacement probing as `not_run_no_approved_candidates`"；controller judgment 列出的 accepted terminal states 包含 `not_run_no_approved_candidates`；plan §6 verification matrix 要求 closeout state per candidate one of `recovered_eligible`, `recovered_fail_closed`, `unrecoverable_safe_path`, `repository_run_failed`, `excluded`, `replacement_verified`, or `not_run_no_approved_candidates`
- **实际行为**: Startup Replay 第 19 行提及 "Replacement candidates: none approved in this handoff"；Residual Risks 第 93 行提及 "Because no replacement candidates were approved in this handoff"；但 Per-Candidate Terminal State 表和 "No row is classified as" 列表（第 47 行）均未出现 `not_run_no_approved_candidates`
- **直接证据**: plan §3.2 明确定义该 terminal state；controller judgment "Accepted Evidence Gate Boundaries" 列出该 state；evidence artifact 第 47 行明确排除该 state（"No row is classified as ... `not_run_no_approved_candidates`"），说明 worker 知道该 state 存在但选择不在表中声明
- **影响**: controller 或后续 gate 只读 Per-Candidate Terminal State 表时，无法从表中看到 Subgate B 的正式关闭状态；需要跨多个 section 拼接才能确认 replacement 探测的关闭结论。不改变最终结论（两行保持 excluded），但 terminal state machine 表达不完整
- **建议改法和验证点**: 在 Per-Candidate Terminal State 表中为每个 candidate 增加 Subgate B 行（或在 Reason 列追加 `not_run_no_approved_candidates`），或在 "No row is classified as" 之后增加一段显式声明 "Both candidates close Subgate B as `not_run_no_approved_candidates` because no controller-approved replacement candidate exists"
- **修复风险（低）**: 纯文档变更，不影响已执行的 CLI 命令、生成产物或 source boundary
- **严重程度（低）**: 结论正确但 terminal state 覆盖不完整

## Open Questions

- 无

## Residual Risk

- review 未重跑 CLI 命令或直接读取 `reports/extraction-snapshots/` 下生成的 snapshot/score/quality_gate 产物；terminal state 判断基于证据文档中的直接证据引用，这些引用声称来自 `jq 'keys'`、`rg` 和 `sed -n` 的实际输出
- 证据文档声称 `errors.jsonl` 为空（0 lines），但未提供 `wc -l` 或 `cat` 的完整输出；若 `errors.jsonl` 包含未被报告的 upstream failure category 线索，terminal state 可能需要重新评估——不过即使如此，`unrecoverable_safe_path` 仍然是最保守的分类

## Review Self-Check

- review mode、base、included/excluded scope 和 source evidence 已写清 ✓
- 唯一 finding 绑定到 evidence artifact 的具体行和 terminal state machine 的定义 gap ✓
- finding 是 material、可执行的（补充 Subgate B terminal state 声明），不是 style/nit ✓
- adversarial pass 已执行：重点检查了 quality gate success/block 是否被误用为 source safety evidence——证据文档正确区分了 downstream field evidence 和 upstream category evidence ✓
- open questions 和 residual risk 已记录 ✓
- output path 位于 `docs/reviews/` ✓
