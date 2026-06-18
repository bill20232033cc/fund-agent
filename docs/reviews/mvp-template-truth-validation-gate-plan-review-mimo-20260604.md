# AgentMiMo Plan Review: Template Truth Validation Gate

> **Review target**: `docs/reviews/mvp-template-truth-validation-gate-plan-20260604.md`
> **Reviewer**: AgentMiMo
> **Date**: 2026-06-04
> **Gate**: MVP typed-template-to-agent report generation stabilization phase / Gate 1 Template truth validation gate

---

## Findings

### Finding 1 — Hard Stop 条件未覆盖"测试本身被修改以掩盖失败"的场景

**Severity**: non-blocking residual
**Location**: Section 4 Hard Stop Conditions, 第2条

当前 hard stop 第2条写的是：

> 任一 proposed validation command 失败，且失败不能用当前 gate 外部环境问题解释。

这覆盖了"测试因代码回归而失败"的场景，但没有覆盖"测试本身被修改以静默通过 fail-closed 语义验证"的场景。例如，如果有人修改了 `test_chapter_auditor.py` 中的 fail-closed 断言，使其不再严格验证 unknown requirement 的阻断行为，当前 hard stop 条件不会触发。

**为什么是 residual 而非 blocker**：测试完整性由 code review 和 gateflow 独立保障，本 gate 的职责是验证"当前代码 + 当前测试"的一致性。但建议在 Evidence Artifact Requirements (Section 7) 中增加一条：evidence artifact 必须记录 `git diff --name-only` 以确认测试文件未被修改。

---

### Finding 2 — Accepted Checkpoint Requirements 与 Non-goals 存在表面张力

**Severity**: non-blocking residual
**Location**: Section 9 Accepted Checkpoint Requirements vs Section 3 Explicit Non-goals

Section 9 第5条要求：

> Controller judgment artifact，逐条裁决 review findings，并用 `docs/design.md` / `docs/implementation-control.md` 当前事实说明为什么 accepted。

但 Section 3 non-goals 第1条明确：

> 不修改 source、tests、config、runtime behavior、README、design/control docs 或模板文档。

这里存在一个问题：gate acceptance 后是否需要回写 `docs/implementation-control.md` 的当前 gate 状态？如果需要，non-goals 的措辞过于宽泛；如果不需要（即 controller judgment artifact 独立存在、不回写 control doc），则 Section 9 第5条应明确排除 control doc 回写。

**为什么是 residual 而非 blocker**：这是一个流程澄清问题，不阻断 gate 执行。Controller 可以在 judgment artifact 中独立记录裁决，后续由 closeout gate 决定是否回写 control doc。

---

### Finding 3 — `lru_cache` masking 风险的 residual owner 描述可更精确

**Severity**: non-blocking residual
**Location**: Section 10 Residual Owner Classification, 第1条

当前描述：

> `contracts.py` loader `lru_cache` 对长进程模板文档 mutation 的 masking 风险：future developer tooling/cache invalidation cleanup owner。

这个 residual 的触发条件是"长进程内模板文档被修改"。在当前 CLI 一次性验证场景下不会触发，但如果未来接入 Agent runner/tool-loop（长生命周期进程），这个风险会变得实际。建议补充：该 residual 应在 Agent engine implementation gate 中一并评估。

**为什么是 residual 而非 blocker**：当前 gate 是一次性验证，不涉及长进程运行。

---

### Finding 4 — A1 验证命令只验证结构，不验证模板业务内容

**Severity**: non-blocking residual
**Location**: Section 5 Verifier Matrix, A1 row; Section 6 Proposed Validation Commands, Command 1

`uv run python -m fund_agent.fund.template.contracts --validate-template-doc` 验证的是 canonical JSON 的结构合法性（8章、id 0-7、字段完整性），但不验证模板业务内容（如 must_answer 问题是否合理、audit_focus 闭集是否完整、ITEM_RULE 是否覆盖所有基金类型）。

**为什么是 residual 而非 blocker**：业务内容验证属于模板质量 gate，不在 template truth source validation 的范围内。本 gate 的职责是验证"同一 JSON 是否仍作为唯一 truth source 被正确投影"，不是验证"truth source 内容是否最优"。

---

### Finding 5 — A8 Evidence Artifact 要求未提及测试文件完整性校验

**Severity**: non-blocking residual
**Location**: Section 5 Verifier Matrix, A8 row

A8 要求 evidence artifact 记录：

> 当前命令列表，并明确声明未运行 live provider / promotion / external state。

但没有要求记录 `git status --short` 中测试文件的变更状态。虽然 Section 7 要求记录 `git status --short` 并说明"除验证 artifact 外没有 source/test/config/runtime behavior 改动"，但 A8 本身没有重申这一点。

**为什么是 residual 而非 blocker**：Section 7 的全局要求已覆盖，A8 只是未在本行重复。建议在 A8 的 evidence required 列中增加"测试文件未被修改"的显式声明。

---

## 逐 Review Lens 审查

### Lens 1: 命令矩阵是否足以验证 canonical TEMPLATE_CONTRACT_MANIFEST_JSON、untyped/typed same-source projection、chapter ids 0-7、Ch2 internal subcontract 边界

**PASS**。

- Command 1 (`contracts --validate-template-doc`) 直接验证 canonical JSON 结构。
- Command 2 (`test_contracts.py + test_typed_contracts.py`) 覆盖 untyped/typed projection、public ids 0-7、stale source_manifest fail-closed、Ch2 internal subcontract 边界。
- Command 8 (focused aggregate) 提供单条回归命令。
- 代码验证确认：`contracts.py` 的 `_EXPECTED_CHAPTER_IDS = tuple(range(8))` 和 `typed_contracts.py` 的 `EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))` 均严格校验 id 范围；Ch2 subcontracts 要求 `public_chapter_id is None` 且必须是 `("performance", "attribution", "cost")`。

### Lens 2: 是否覆盖 same-source consumers

**PASS**。

| Consumer | 验证命令 | A-criterion |
|----------|---------|-------------|
| `EvidenceAvailability` | Command 4 | A4 |
| `chapter_writer` | Command 5 | A5 |
| `chapter_auditor` | Command 5 | A5 |
| `ChapterOrchestrator` | Command 6 | A6 |
| `chapter_contract_constraints` | Command 3 | A3 |

代码验证确认：所有 7 个 same-source consumer 的行为均与 plan 声明一致。

### Lens 3: 是否覆盖 no deterministic fallback、incomplete stdout empty、quality gate/fail-closed 语义

**PASS**。

- A7 显式覆盖 deterministic defaults、quality gate、no fallback、empty stdout。
- Command 7 (`test_cli.py`) 覆盖 CLI incomplete stdout 为空、exit 1、quality gate block/not-run 语义。
- 代码验证确认：`test_fund_analysis_service_llm.py` 和 `test_cli.py` 中有 focused assertions 验证 missing/partial/incomplete 不回退 deterministic、stdout 为空、exit code 正确。

### Lens 4: 是否误用旧日志、旧 aggregate review 或间接证据标记 accepted

**PASS**。

- Section 2 明确引用当前代码事实（文件路径、函数名、行为），不是旧日志。
- Section 2 引用 `docs/implementation-control.md` 和 `docs/design.md` 的当前状态，不是旧 review 结论。
- Section 9 第6条明确禁止使用旧日志或旧 aggregate review。
- 代码验证确认所有 8 条声明均为当前代码事实。

### Lens 5: 是否夹带 forbidden scope

**PASS**。

| Forbidden scope | 检查结果 |
|----------------|---------|
| real LLM smoke | 不在 proposed commands 中 |
| provider budget/default/runtime/live probe | 不在 proposed commands 中 |
| Agent runtime implementation | Non-goal Section 3 第3条显式排除 |
| multi-year runtime | Non-goal Section 3 第3条显式排除 |
| score-loop | Non-goal Section 3 第3条显式排除 |
| golden/readiness | Non-goal Section 3 第3条显式排除 |
| PR/push/release | Non-goal Section 3 第6条显式排除 |

### Lens 6: 是否存在过度验证或遗漏

**PASS（无过度验证）；minor residual（见 Findings 1-5）**。

- 无 promotion/snapshot/live provider 运行。
- A1-A8 与 validation commands 的映射清晰，无冗余命令。
- 每个 acceptance criterion 都有明确的 blocker vs residual 分类。
- Focused aggregate command (Command 8) 是可选的，仅用于 controller 需要单条回归命令时，不增加验证负担。

---

## Verdict

**PASS**

5 个 non-blocking residual findings，0 个 blocking findings。Plan 的 verifier matrix 足以验证 same-source consumer regression、no fallback/stdout/quality gate 语义，且未夹带 forbidden scope。所有 8 条代码声明经独立 Explore agent 验证均为当前代码事实。Gate 分类 `heavy` 合理。
