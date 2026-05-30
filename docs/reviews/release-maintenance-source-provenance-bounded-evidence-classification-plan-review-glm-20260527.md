# Plan Review: Source Provenance Bounded Evidence Classification Plan

> Date: 2026-05-27
> Reviewer: AgentGLM
> Role: Independent plan review — command bounds, terminal states, denominator rules, forbidden scope
> Reviewed target: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-20260527.md`
> Checkpoint: `a0de731 feat: expose source provenance in snapshots`
> Truth sources: `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts in `docs/reviews/`

---

## Reviewed Scope And Assumptions Tested

1. Commands are bounded to public CLI for exactly `110020`/2024 and `017641`/2024.
2. Classification uses only public provenance fields and quality outputs, not downstream success as fallback proof.
3. Terminal states cover unknown metadata, fail-closed, repository failure, quality block after provenance, eligible for later review, `not_promoted`.
4. No code changes, no PDF/cache/source helper access, no source strategy change, no renderer/FQ/default CLI/Host/Agent/dayu/golden/baseline promotion.
5. Output hygiene and tracked summary artifact are adequate.
6. Plan does not require revision before evidence.

---

## Code Facts Verified

### Provenance field emission chain

- `fund_agent/fund/source_provenance.py` defines `PublicSourceProvenance` with Literal domains: `FallbackEligibility ∈ {"eligible", "fail_closed", "not_applicable", "unknown_public_metadata_absent"}`, `SourceProvenanceStatus ∈ {"complete", "incomplete", "not_applicable"}`, `PrimaryFailureCategory ∈ {"not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error"}`.
- `fund_agent/fund/data_extractor.py` line 210 calls `project_public_source_provenance(report.metadata.source)` **without** passing `primary_failure_category`.
- `fund_agent/fund/documents/models.py` `AnnualReportSourceMetadata` does **not** include a `primary_failure_category` field.
- No production code outside `source_provenance.py` passes `primary_failure_category` to `project_public_source_provenance`.
- Therefore, when `fallback_used=True` in the repository metadata, the provenance output is always `fallback_eligibility="unknown_public_metadata_absent"` with `source_provenance_status="incomplete"`.
- The implementation evidence artifact (`release-maintenance-source-provenance-public-output-implementation-evidence-20260527.md` line 70) explicitly records this as an expected residual.

### CLI command signatures

- `extraction-snapshot` accepts `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir` — plan commands match.
- `extraction-score` accepts `--snapshot-path`, `--source-csv` (default), `--output-dir`, `--golden-answer-path` (optional), `--errors-path` (optional) — plan commands omit `--golden-answer-path` (valid; FQ0 coverage/traceability scoring proceeds without correctness comparison).
- `quality-gate` accepts `--score-path`, `--output-dir` — plan commands match.

### Output hygiene

- `.gitignore` covers `reports/extraction-snapshots/`, `reports/scoring-runs/`, `reports/quality-gate-runs/` — plan's generated output dirs are all ignored.
- Tracked summary artifact is a single file in `docs/reviews/`.

### Prior evidence context

- The index/QDII source recovery evidence (`release-maintenance-index-qdii-source-recovery-evidence-20260527.md`) ran the same CLI commands for `110020`/2024 and `017641`/2024 **before** the source provenance implementation. Both extracted successfully but did not expose upstream failure categories. Both were classified as `unrecoverable_safe_path`.

---

## Findings

### F1-未修复-中-分类规则 3/4/5 在当前实现下为不可触达的死路径

- **位置**: Classification Rules 第 3、4、5 条；Public Provenance Fields 节；Gate Objective 节
- **问题类型**: 不可直接实施 / 状态机漏洞
- **当前写法**: 分类规则 3（`provenance_fail_closed`）要求 `primary_failure_category ∈ {"schema_drift", "identity_mismatch", "integrity_error"}`；规则 4（`quality_blocked_after_provenance`）要求公共 provenance 显式证明 fallback eligibility；规则 5（`provenance_eligible_for_next_review`）要求 `primary_failure_category ∈ {"not_found", "unavailable"}` 且 `fallback_eligibility="eligible"`。
- **反例/失败场景**: `data_extractor.py` 第 210 行调用 `project_public_source_provenance(report.metadata.source)` 时不传 `primary_failure_category` 参数。`AnnualReportSourceMetadata` 不包含此字段。因此生产路径中 `fallback_used=True` 的行始终产生 `fallback_eligibility="unknown_public_metadata_absent"` 和 `source_provenance_status="incomplete"`。无论实际的 `primary_failure_category` 是什么，公共输出都无法反映。规则 3、4、5 的入口条件永远不满足。
- **为什么有问题**: Gate Objective 问"公共 provenance 是否证明了一个 eligible 的上游主源失败和非阻断质量输出？"——在当前实现下答案确定性地为"不能"，因为 `primary_failure_category` 始终为 `null`。运行 6 条 CLI 命令不会改变分类结果：两只基金都将落入规则 2（`provenance_unknown_public_metadata_absent`）。证据运行仍然有价值（形式化确认 provenance 字段被正确发出、建立审计轨迹），但 Gate Objective 的问法暗示存在发现空间，实际上不存在。
- **直接证据**:
  - `source_provenance.py` 第 105-170 行：`project_public_source_provenance` 的 `primary_failure_category` 参数默认为 `None`，且当 `None` 时唯一输出 `unknown_public_metadata_absent`。
  - `data_extractor.py` 第 210 行：调用时不传 `primary_failure_category`。
  - `documents/models.py` `AnnualReportSourceMetadata`：字段列表不含 `primary_failure_category`。
  - `grep -rn "primary_failure_category" fund_agent/ | grep -v "source_provenance.py\|test_"` 返回空。
  - 实现证据 artifact 第 70 行明确记录此 residual。
- **影响**: 不影响安全性。规则 2 和 `not_promoted` 正确处理了实际结果。但证据 worker 可能误以为规则 3-5 有触达可能；证据审查时可能对"为什么规则 3-5 未触发"产生不必要的疑问。
- **建议改法和验证点**:
  1. 在 Classification Rules 节加一条显式说明："当前实现不传播 `primary_failure_category`，因此规则 3-5 在本 gate 为预置防御路径，不预期触发。两只基金的预期终态均为 `provenance_unknown_public_metadata_absent`（规则 2）。"
  2. Gate Objective 改为不含暗示发现空间的措辞，例如："本 gate 运行有界公共 CLI 并形式化记录两只基金的公共 provenance 终态分类，确认当前实现正确发出 provenance 字段，并确认当前公共输出无法证明 eligible fallback。"
  3. 验证点：无需代码改动；仅需 plan 文档修订。
- **修复风险**: 低。仅涉及 plan 文档措辞，不涉及代码或命令变更。
- **严重程度**: 中。plan 的核心声称（"分类"）有一个可预测的结果但未明确承认，可能导致后续 reviewer 和 controller 的认知偏差。

### F2-未修复-低-缺少 `fallback_used=false`（主源成功）的显式分类状态

- **位置**: Classification Rules 节
- **问题类型**: 状态机漏洞
- **当前写法**: 分类规则 1-6 均假设或隐含 `fallback_used=True`。无规则处理 `fallback_used=false`、`fallback_eligibility="not_applicable"`、`source_provenance_status="not_applicable"` 的情况。
- **反例/失败场景**: 如果自上次 evidence 运行以来仓库主源对 `110020` 或 `017641` 修复可用，则 `fallback_used=false`，provenance 输出为 `not_applicable`。此时规则 1-5 均不匹配，只有规则 6（`not_promoted`）兜底。证据 artifact 中的中间终态字段无值可填。
- **为什么有问题**: 虽然最终 disposition 不变（`not_promoted`），但证据 artifact 要求为每只基金填写 `terminal state`。如果主源成功，worker 将无法从规则 1-5 中选择一个合法的中间状态。
- **直接证据**:
  - Plan 第 168 行要求："For each fund: output paths, provenance fields, quality gate status, issue count, terminal state, and `promotion_disposition=not_promoted`."
  - `source_provenance.py` 第 127-136 行：当 `fallback_used=False` 时输出 `fallback_eligibility="not_applicable"`, `source_provenance_status="not_applicable"`。
  - Plan Classification Rules 无规则匹配此组合。
- **影响**: 低。基于 prior evidence，两只基金极有可能仍使用 fallback。但如果主源恢复，worker 会遇到未定义状态。
- **建议改法和验证点**: 在规则 1 之前或之后添加 `primary_succeeded_no_fallback` 状态：`fallback_used=false` 且 snapshot 成功。此状态同样以 `not_promoted` 为最终 disposition。验证点：规则枚举覆盖 `fallback_used` 的所有可能值。
- **修复风险**: 低。
- **严重程度**: 低。基于 prior evidence，此场景不太可能发生，但防御性覆盖成本极低。

---

## Open Questions

无。所有 reviewer focus area 均有直接证据支撑。

---

## Residual Risks

1. **`primary_failure_category` 传播缺失是已知 residual**（实现证据 artifact 已记录）。本 gate 的证据运行不会改变此 residual，但会形式化记录其后果。后续 gate 需决定是否在 `FundDocumentRepository` 公共元数据中持久化 `primary_failure_category`，或授权显式传入路径。
2. **规则 3-5 作为防御性框架保留**。一旦 `primary_failure_category` 传播实现，这些规则可立即激活，无需重写 plan 结构。建议将此 residual 的 resolution 追踪到下一个 source-strategy 或 repository-metadata gate。

---

## Verification Against Review Focus Areas

| Focus area | Result | Evidence |
|---|---|---|
| Commands bounded to public CLI for exactly 110020/2024 and 017641/2024 | PASS | 6 条命令均为 `fund-analysis` 子命令，`--fund-code` 和 `--report-year` 严格限定；CLI 签名与代码一致 |
| Classification uses only public provenance fields, not downstream success | PASS | Strict negative rule 显式禁止；分类规则要求 `fallback_eligibility` 字段而非 extraction/score 结果 |
| Terminal states cover required list | PASS with finding F2 | 6 个状态覆盖 5 个要求场景；`fallback_used=false` 缺显式覆盖（F2） |
| No code changes / forbidden scope | PASS | Forbidden Scope 节完整覆盖所有 review focus 禁止项；与 AGENTS.md 模块边界一致 |
| Output hygiene and tracked summary artifact | PASS | Generated outputs under gitignored `reports/`；tracked artifact 为 `docs/reviews/` 单文件 |
| Plan needs revision before evidence | FINDING F1 | 建议加显式确定性说明，非 blocker |

---

## Plan Review Conclusion

**PASS_WITH_FINDINGS**

Plan 的安全边界、命令范围、禁止事项、denominator 规则和输出卫生均与真源一致。两只基金的 `not_promoted` 最终 disposition 不受 findings 影响。两条 findings 均为 plan 文档层面改进，不涉及代码变更或命令变更。

- F1（中）：建议在 plan 中显式承认规则 3-5 为不可触达的防御路径，明确 Gate Objective 的确定性答案。不改不影响安全性，但影响后续 reviewer/controller 认知效率。
- F2（低）：建议添加 `primary_succeeded_no_fallback` 中间状态以覆盖 `fallback_used=false` 场景。
