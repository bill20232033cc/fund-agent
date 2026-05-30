# Source Provenance Public Output Implementation Plan Review — MiMo

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-20260527.md`
> Checkpoint: `918f65d docs: accept source provenance design`
> Verdict: **PASS_WITH_FINDINGS**

---

## Review Scope

逐项检查 plan review 指令中的 6 个审查焦点。

---

## 1. Is the proposed slice truly minimal and additive?

**PASS**。Plan 提出的三步实现（新 projection module → bundle 穿线 → snapshot 字段追加）是 additive 的。不修改已有字段语义，不改变 `SNAPSHOT_FIELD_ORDER`，不引入新的 mandatory 下游依赖。`source_provenance_to_dict` 仅用于 snapshot 写入路径，不改变 scoring 或 quality gate 逻辑。

---

## 2. Does adding `source_provenance` to `StructuredFundDataBundle` risk broad constructor churn or public behavior change?

**PASS_WITH_FINDINGS**。

代码检查发现 **7 个测试文件**直接构造 `StructuredFundDataBundle`：

- `tests/services/test_fund_analysis_service.py:193`
- `tests/fund/test_golden_prefill.py:116`
- `tests/fund/analysis/test_r_abc.py:112`
- `tests/fund/test_extraction_snapshot.py:216, 594`
- `tests/fund/test_report_evidence.py:652`
- `tests/fund/template/test_renderer.py:296`

Plan step 2 的 stop condition 声明"如果 adding this required field causes broad fixture churn beyond focused fake builders, stop and evaluate an optional default-field approach"。但 plan 没有 proactive 地选择一个安全默认值策略，而是把决策推迟到实现时。

**Finding F1 (MEDIUM)**：建议 plan 在 step 2 明确采用 `source_provenance: PublicSourceProvenance | None = None` 作为 dataclass field default，而不是先尝试 required field、遇到 churn 再退回。理由：
- 当前 `AnnualReportSourceMetadata` 本身已经是 `Optional`（`report.metadata.source` 可为 `None`）
- Projection 对 `None` 输入已有确定性输出（not-applicable）
- 7 个测试文件修改量可接受，但用 `None` default 可以让每个测试文件只在需要验证 provenance 语义时才显式传入，避免每个 fake builder 都必须构造一个与测试主题无关的 projection
- 不影响生产路径（`extract()` 总是显式传入）

如果 controller 认为 required field 更符合数据完整性契约，则 plan 应在 step 2 明确列出所有 7 个需要修改的测试文件及其修改预期，而不是依赖 stop condition reactive 决策。

---

## 3. Does the plan preserve no source helper/downloader/cache/PDF access and no `FundDocumentRepository` strategy change?

**PASS**。Plan 明确禁止 `documents/sources.py` 导入，projection 只接受 `AnnualReportSourceMetadata | None` 和显式 `primary_failure_category` 参数。Stop condition 第一条即覆盖此约束。

---

## 4. Is `fallback_used=true` + missing `primary_failure_category` safely `unknown_public_metadata_absent`, never eligible?

**PASS**。Plan 的 conservative rules 和 projection 函数规则一致：`fallback_used=True` + `category=None` → `fallback_eligibility="unknown_public_metadata_absent"` + `source_provenance_status="incomplete"`。Test plan 包含 explicit "Fallback metadata gap" 和 "Do not infer" 用例。与 `docs/design.md` section 6.1 的约束完全对齐。

---

## 5. Are snapshot JSONL/summary and score compatibility tests sufficient?

**PASS_WITH_FINDINGS**。

Plan 的 test plan 覆盖了：
- Projection unit tests（6 类场景）
- Data extractor threading tests（2 类场景）
- Snapshot schema / JSONL / summary tests（5 类场景）
- Score compatibility tests（3 类场景）

**Finding F2 (LOW)**：Score compatibility test plan 第三条提到"Score JSON output shape for FQ0-FQ6 consumers remains unchanged unless explicitly accepted; if unchanged, assert no new gate-sensitive field is required"。建议改为确定性断言：明确声明 FQ0-FQ6 score JSON 不变，并在 test 中 assert `score.json` 的 key set 不变。当前措辞留有 "if unchanged" 的歧义空间。

---

## 6. Does the plan avoid renderer, FQ0-FQ6, default analyze/checklist behavior, Host/Agent/dayu, fund_type/extractor logic, golden/baseline promotion?

**PASS**。Forbidden scope 清单完整覆盖所有非目标。Step 5 的 report-evidence 明确标注为 "Default recommendation: do not touch"。Stop condition 第四条覆盖 fund_type/extractor/renderer/Host/Agent/dayu/golden/baseline。

---

## Additional Findings

**Finding F3 (LOW)**：Plan step 3 中 `write_snapshot_summary` 的 provenance aggregation 规则为"Aggregate from first record per fund"。当前设计下同一 fund 的所有 SnapshotRecord 携带 identical provenance（来自同一个 bundle），因此 first-record 策略正确。但 plan 没有在 test 中显式断言"所有 records 携带 identical provenance"。建议在 Snapshot test plan 中增加一条："All records for a fund carry identical provenance copied from the bundle"（plan 已有此条，但建议在 validation commands 的 focused tests 中显式加入这个 assert）。

**Finding F4 (INFO)**：Plan 的 exact files 列表和 validation commands 是 code-generation-ready 的。文件路径、函数签名、test 场景、CLI 命令均具体且可执行。

---

## Summary

| Finding | Severity | Description |
|---------|----------|-------------|
| F1 | MEDIUM | `StructuredFundDataBundle.source_provenance` 应 proactive 选择 `None` default 而非依赖 stop condition reactive 决策 |
| F2 | LOW | Score JSON shape 不变应改为确定性断言，消除 "if unchanged" 歧义 |
| F3 | LOW | Snapshot test 应显式断言同 fund 所有 records 的 provenance identical |
| F4 | INFO | 文件列表和 validation commands code-generation-ready |

**Verdict: PASS_WITH_FINDINGS**。Plan 整体架构正确、scope 收敛、与 accepted design 完全对齐。F1 建议在实现前由 controller 裁决是否采用 default value 策略；F2/F3 为测试完备性改进，不阻塞实现。
