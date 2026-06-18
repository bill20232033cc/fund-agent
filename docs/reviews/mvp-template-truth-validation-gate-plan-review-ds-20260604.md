# MVP Template Truth Validation Gate — AgentDS Plan Review

**Review target**: `docs/reviews/mvp-template-truth-validation-gate-plan-20260604.md`
**Reviewer**: AgentDS
**Date**: 2026-06-04
**Review lens**: verifier matrix 覆盖、hard stop 充分性、未来设计误写为当前事实、forbidden scope 夹带、hard boundaries 保持、public chapter ids / Ch2 subcontracts 边界

---

## Findings

### Finding DS-1 — NON-BLOCKING RESIDUAL: A6 validation command includes `test_execution_contract.py` without explicit coverage mapping

- **Severity**: Non-blocking residual
- **Plan reference**: Section 5, Verifier Matrix row A6; Section 6, validation command 6
- **Finding**: A6 的 acceptance criterion 覆盖 "Service report generation typed path 直接消费 same-source contract inputs"，proposed validation command 包含 `tests/services/test_execution_contract.py`。但 verifier matrix 的 "Direct evidence required" 列没有明确说明 `test_execution_contract.py` 验证的是 ExecutionContract 的哪个具体方面（request/runtime policy consistency、typed path wiring 还是 quality fail-closed policy）。该文件存在且属于 services 测试套件，但 plan 未解释将它加入 A6 命令的必要性。
- **Why non-blocking**: 该命令属于 proposed validation command，validation/evidence agent 执行时自然会记录该文件的实际覆盖内容。不阻断 plan acceptance。
- **Recommendation**: Controller 可要求 validation evidence agent 在输出 evidence artifact 时明确 `test_execution_contract.py` 在 A6 下的具体覆盖点。

### Finding DS-2 — NON-BLOCKING RESIDUAL: Section 7 evidence artifact requirements 缺少对 A8 forbidden scope 的显式 pass/fail recording 模板

- **Severity**: Non-blocking residual
- **Plan reference**: Section 7 "Evidence Artifact Requirements For Validation Step"
- **Finding**: Section 7 要求 evidence artifact 记录每条 validation command 的 exit code、stdout/stderr 摘要、A1-A8 pass/fail 判定、以及 "明确声明未运行 live provider、promotion、golden/readiness..."。但没有给出 A8 forbidden scope 的具体 pass/fail checklist（例如逐条确认 no live provider / no promotion / no golden readiness / no snapshot refresh / no release readiness / no push / no PR / no external state change）。其他 A1-A7 都可以通过命令 exit code 直接判定，A8 是负面证明，需要更结构化的 recording 模板才能避免漏检。
- **Why non-blocking**: 属于 evidence artifact 模板规范问题，可在 validation step 执行时由 evidence agent 自行结构化。Section 6 已明确列出禁止运行的命令类别，与 Section 7 的声明要求结合使用已足够。
- **Recommendation**: Controller 可要求 validation evidence agent 在 evidence artifact 中为 A8 输出一个 explicit checklist（逐条标注 "confirmed not run" 或等效声明）。

### Finding DS-3 — NON-BLOCKING OBSERVATION: `lru_cache` residual 的 risk window 描述可以更精确

- **Severity**: Observation (not a finding)
- **Plan reference**: Section 5, Verifier Matrix row A1 residual column; Section 10 residual classification
- **Observation**: Plan 正确地将 `lru_cache` 长进程 mutation masking 归类为 future cleanup residual。但 plan 没有说明当前一次性 validation 能覆盖这个风险到什么程度（例如：验证命令本身是短进程，验证完成即退出，不存在长进程缓存污染窗口）。这个信息对 controller judgment 有帮助但不属于 plan 必须包含的内容。
- **No action required**.

---

## Cross-check Summary

以下检查项逐一对照 plan artifact、`docs/design.md`、`docs/implementation-control.md`、`AGENTS.md` 进行验证：

### 1. Phaseflow/Gateflow 顺序合规

- **PASS**: Plan 明确遵循 plan → review → controller judgment → accepted checkpoint 顺序。Section 8 要求两份独立 review，Section 9 定义了 accepted checkpoint 必需条件。符合 `AGENTS.md` gate 分类规则中的 `heavy` 要求。

### 2. Verifier Matrix 覆盖

- **PASS**: Matrix 包含 8 个 acceptance criteria (A1-A8)，每个都有：direct evidence required、proposed validation command/artifact、blocker vs residual 分类、accepted 后 next entry point。覆盖了 canonical JSON truth source → untyped/typed projection → sidecar consumer → EvidenceAvailability → writer/auditor → Service typed path → CLI/fail-closed → forbidden scope 的完整链。

### 3. 旧日志/间接证据问题

- **PASS**: Section 6 明确声明 "本 planning handoff 不运行它们，不把它们写成已通过证据"。Section 7 要求 evidence artifact 必须记录当前 git branch、`git status --short`、每条命令的完整输出，并 "不得用间接日志或旧 review 结论替代"。Section 9 要求 "不得使用旧日志、旧 aggregate review 或间接 evidence 代替本 gate 当前 plan review 与 controller judgment"。

### 4. 未来设计误写为当前事实

- **PASS**: Section 2 "当前未改变事实" 明确列出 Agent runtime implementation、multi-year annual evidence runtime、score-loop "未实现且不在本 gate"。Section 3 non-goals 再次确认不做 Agent runtime、tool-loop、ToolRegistry、ToolTrace、score-loop、chapter_generation_score。Section 10 将这些明确归类为 future gate owner。与 `docs/design.md` 和 `docs/implementation-control.md` 中 "design-only future architecture" 状态一致。

### 5. Forbidden Scope 夹带

- **PASS**: Section 3 non-goals 完整覆盖：no live provider、no real LLM smoke、no provider runtime/live probe、no promotion/golden/readiness/snapshot/release、no PR/push/commit（除非 controller 授权）。Section 6 禁止命令列表与 Section 3 一致。所有 proposed validation commands 都是 `uv run pytest` 本地测试，不涉及外部状态。

### 6. Hard Boundaries 保持

- **PASS — Dayu dependency**: Section 3 明确 "不直接依赖 dayu-agent / dayu.host / dayu.engine"。与 AGENTS.md 和 design.md 的 Dayu 裁决一致。
- **PASS — Auditor/quality gate/fail-closed**: Section 3 明确不放松 auditor、programmatic blockers、quality gate、fail-closed、no deterministic fallback、stdout empty on incomplete 语义。Hard stop 条件覆盖这些语义漂移场景。
- **PASS — Incomplete LLM fallback**: Section 3 明确 "不让 incomplete LLM result 回退 deterministic"。Hard stop 条件包含 "任一 LLM incomplete / partial path 输出 stdout report、回退 deterministic、或绕过 fail-closed"。
- **PASS — 半成品 stdout**: Section 3 明确 "不向 stdout 输出半成品报告"。Hard stop 条件覆盖。
- **PASS — FundDocumentRepository**: Section 3 明确 "生产年报访问仍只能经 FundDocumentRepository"。Hard stop 条件包含 "发现 Service/UI/Host/renderer/quality gate 直接读取 PDF/cache/source helper"。
- **PASS — extra_payload**: Section 3 明确 "不把显式参数放进 extra_payload"。

### 7. Public Chapter Ids / Ch2 Subcontracts 边界

- **PASS**: Section 2 明确 "public chapter ids 必须保持 0-7；Ch2 performance / attribution / cost 只能是第 2 章内部 typed subcontracts，不得成为公开章节"。Hard stop 条件包含 "public chapter ids 偏离 0-7，或 Ch2 internal subcontracts 变成公开章节"。代码验证确认 `contracts.py` 中 `_EXPECTED_PUBLIC_CHAPTER_IDS` 强制 `[0,1,2,3,4,5,6,7]`，`typed_contracts.py` 中 Ch2 `internal_subcontracts` 仅允许第 2 章。

### 8. Gate 分类合理性

- **PASS**: Plan 分类为 `heavy`，理由充分：涉及 public template contract、auditor fail-closed 语义、report generation typed path、Agent migration 输入边界。符合 `AGENTS.md` 中 "架构边界、公共契约、schema/migration、质量门控语义" 应使用 `heavy` 的规则。

### 9. Proposed Validation Commands 可行性

- **PASS**: 所有 7 条 proposed commands 对应的源文件和测试文件均已确认存在：
  - `contracts.py` 有 `--validate-template-doc` CLI 入口
  - 所有 10 个测试文件路径有效
  - 命令均为本地 pytest，不需要 live provider/key/external state

### 10. Residual Owner 分类合理性

- **PASS**: Section 10 正确区分可进入后续 gate 的 residual（lru_cache、TemplateLensRule naming、TypedTemplatePathMode literal、Ch3 single-year availability、Ch7 polish、provider runtime timeout、Agent runner/tool-loop、score-loop）和必须阻断当前 gate 的 blocker（truth source uniqueness、same-source projection、chapter id 0-7、Ch2 boundary、EvidenceAvailability/consumer regression、auditor/quality gate/fail-closed 语义漂移、deterministic behavior change、dayu dependency、PDF/cache bypass、extra_payload）。该分类与 `docs/design.md` 和 `docs/implementation-control.md` 的当前状态一致。

---

## Verdict

**PASS**

Plan artifact 满足 `heavy` gate plan review 的全部要求：
- Verifier matrix 覆盖完整（A1-A8），每行有 direct evidence、command、blocker/residual 分类和 next entry point
- Hard stop 条件充分覆盖 truth source integrity、same-source projection、chapter id boundary、consumer regression、forbidden scope 和 semantic drift
- 未将未来 Agent runtime / multi-year runtime / provider runtime / score-loop 误写为当前事实
- 未夹带 forbidden scope（live provider、real LLM smoke、promotion、golden/readiness、PR/push/release）
- 全部 hard boundaries 保持（dayu 依赖、auditor/quality gate/fail-closed、incomplete LLM 回退、半成品 stdout、FundDocumentRepository、PDF/cache bypass、extra_payload）
- Public chapter ids 0-7 和 Ch2 internal subcontracts 边界明确
- 无旧日志或间接证据替代当前验证的问题

Non-blocking residual findings: DS-1（A6 command 中 test_execution_contract.py 覆盖映射）、DS-2（A8 forbidden scope recording 模板）。均不阻断 plan acceptance。

Blocking findings: 0。

---

## Artifact Compliance

- 是否只写了允许 artifact：**是**。仅写入 `docs/reviews/mvp-template-truth-validation-gate-plan-review-ds-20260604.md`。
- 是否修改了 plan artifact 或其他文件：**否**。
- 是否运行了 live provider / promotion / golden readiness / snapshot refresh / release readiness / push / PR：**否**。
