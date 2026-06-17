# Docling Reference Bundle Producer Determinism Contract Plan Review (DS) - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism Contract Planning Gate` — plan review
Reviewer role: AgentDS (plan review worker only)
Reviewed artifact: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
Review artifact: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-ds-20260617.md`

## Verdict

`PASS_WITH_FINDINGS_NOT_READY`

Blocking findings: 0
Non-blocking findings: 4

---

## Review Summary

The plan correctly addresses the accepted comparability diagnostic root problem: wrapper/reference-bundle construction drift before helper semantics, not closure-count chasing. It preserves all binding candidate-only / NOT_READY / no-source-truth constraints. The deterministic sorting and fingerprinting specification is strong enough for future like-with-like comparison. Four non-blocking findings identified below; none block handoff.

---

## Findings

### DS-F1-未修复-中-Slice4条件歧义使实施者无法独立推进

- **Plan位置**: §Proposed Implementation Slices → Slice 4 - Evidence Wrapper Contract Update (第217-231行)
- **问题类型**: 不可直接实施
- **计划当前写法**:
  > the no-live evidence wrapper used to generate residual-closure matrices, if it exists as a committed script; otherwise keep this slice as an evidence-artifact generation instruction and do not add a new production CLI.

- **为什么有问题**: 计划没有先检查该 wrapper 脚本是否存在。如果不存在，Slice 4 退化为一条给未来 evidence worker 的指令——这不是一个可实施的 implementation slice，而是一个 deferred instruction。实施 worker 无法自行决定 Slice 4 是写代码还是写文档。
- **直接证据**: 计划本身未包含对 `fund_agent/fund/documents/candidates/` 或 `tests/` 下是否存在已提交 residual-closure matrix 生成脚本的检查结论。
- **影响**: 实施 worker 进入 Slice 4 时会遇到歧义：不知道该写代码、更新已有脚本、还是只写 evidence 指令。不会导致错误实现，但会浪费 worker 时间或需要回到 controller 澄清。
- **建议改法和验证点**: 在计划中增加一节 "Slice 4 Precondition Check"，由 controller 或 plan worker 先确认 wrapper 脚本是否存在并给出确切路径。如果不存在，将 Slice 4 降级为 "Future Evidence Instruction (not implementation)" 并从 implementation slices 中移除。
- **修复风险**: 低 — 仅需一次文件系统检查，不涉及代码变更。
- **严重程度**: 中

---

### DS-F2-未修复-低-测试文件路径缺失

- **Plan位置**: §Test Strategy (第236-261行)
- **问题类型**: 测试缺口
- **计划当前写法**: 列出了四类必测项（determinism / boundary / diagnostic sufficiency / regression guard），但未指定测试文件路径。
- **为什么有问题**: 实施 worker 需要自行决定测试放在哪个文件。`source_truth_residual_closure.py` 是 `fund_agent/fund/documents/candidates/` 下的生产代码，按照项目惯例测试应对应放在 `tests/fund/documents/` 下。计划不指定路径虽然不会导致错误，但增加了 worker 的决策负担，且在 plan review 阶段可以低成本补全。
- **直接证据**: 计划中 Slice 1-3 都指名为同一个 target file，但 §Test Strategy 没有对应的测试文件路径。对比已接受的 EvidenceAnchor mapping 实现 `tests/fund/documents/test_docling_evidence_anchor_mapping.py` 有明确路径。
- **影响**: 低 — worker 大概率会放在合理位置，但 reviewer 无法在 plan 阶段验证测试位置是否符合项目惯例。
- **建议改法和验证点**: 在 Test Strategy 节增加一行 `Target test file: tests/fund/documents/test_docling_reference_bundle_producer_determinism.py` 或类似路径。
- **修复风险**: 低 — 纯计划文本补充。
- **严重程度**: 低

---

### DS-F3-未修复-低中-fingerprint输入范围未精确定义

- **Plan位置**: §Bundle-level contract → `bundle_content_fingerprint` (第85行) 和 §Required Algorithmic Constraints (第146行)
- **问题类型**: 契约缺失
- **计划当前写法**:
  > `bundle_content_fingerprint` must be computed from normalized diagnostic payload only, not from Python object identity or dict insertion order.

- **为什么有问题**: "normalized diagnostic payload" 包含 bundle-level contract 下列出的 ~16 个字段（第71-86行）。但其中某些字段（如 `diagnostic_payload_available`）是元诊断标记而非内容载荷。计划没有精确划定哪些字段进入 fingerprint 计算、哪些字段是伴随元数据。实施 worker 需要在 `cell_count`/`text_span_count`/`enrichment_status` 等字段中自行决定 fingerprint 输入子集，这可能导致两个 worker 做出不同选择，削弱跨 run 可比性目标。
- **直接证据**: 计划在 bundle-level contract 列举了 16 个字段，但只说 fingerprint 来自 "normalized diagnostic payload"，未定义 "normalized diagnostic payload" 与 "diagnostic metadata" 的精确边界。
- **影响**: 不同实现可能选取不同的 fingerprint 输入子集，导致相同 bundle 产生不同 fingerprint，反而破坏可比性目标。不会导致功能错误但可能使未来 evidence 比较失败。
- **建议改法和验证点**: 在 bundle-level contract 中增加一个明确的 "fingerprint input fields" 子列表，例如 `cell_count + text_span_count + table_count + section_count + table_family_counts + section_inference_counts + row_hierarchy_role_counts + text_semantic_context_counts` 构成 fingerprint 输入，而 `producer_contract_version`、`diagnostic_payload_available`、`enrichment_status` 等是伴随元数据不参与 hash。
- **修复风险**: 低 — 设计决策，不涉及代码。
- **严重程度**: 低中

---

### DS-F4-未修复-低-契约版本号使用示例性语言而非绑定声明

- **Plan位置**: §Slice 1 → Implementation (第166行)
- **问题类型**: 切片过粗
- **计划当前写法**:
  > Add a module-level producer contract version constant, for example `docling_reference_bundle_producer_contract.v1`.

- **为什么有问题**: "for example" 暗示 worker 可以选择其他版本号格式。如果未来 evidence artifact 中的 `producer_contract_version` 格式不一致（如 `v1` vs `1.0` vs `20260617`），跨 run 比较时会出现不必要的格式差异。这不是严重问题，但与计划追求确定性的目标相悖。
- **直接证据**: 计划在同一句中使用了 "for example"，而其他约束（如排序键、字段名）都使用 must/shall 等绑定语言。
- **影响**: 低 — 即使版本号格式不同，核心确定性不受影响，但增加未来 evidence 解析的摩擦。
- **建议改法和验证点**: 将 "for example" 改为 "must be"，或直接声明精确版本字符串如 `PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"`。
- **修复风险**: 低 — 措辞修正。
- **严重程度**: 低

---

## Criteria Checklist

| 审查标准 | 结果 |
|---|---|
| 计划是否针对 accepted comparability diagnostic root problem（wrapper/reference-bundle 构造漂移，非 closure-count 追逐） | ✅ 通过 — Core Decision 明确禁止使 helper 更宽松以增加 closure count，目标是使 producer 输入和诊断输出稳定 |
| 计划是否 handoff-ready 和 code-generation-ready | ⚠️ 基本通过，DS-F1（Slice 4 条件歧义）需要在 handoff 前收敛 |
| affected files/modules、exact allowed changes、non-goals、tests、validation commands、stop conditions、evidence shape 是否足够具体 | ⚠️ 基本通过，DS-F2（测试路径）、DS-F3（fingerprint 输入范围）、DS-F4（版本号格式）有轻微不具体 |
| 是否保留 candidate-only、source_truth_status=not_proven、NOT_READY、no source truth、no baseline promotion、no parser replacement、no full field correctness、no golden/readiness/release/PR claim | ✅ 通过 — 全计划多处反复声明，Non-goals 和 Stop Conditions 完整覆盖 |
| 是否避免 direct PDF/cache/source-helper access、unplanned repository reload、live/network/provider/LLM/analyze/checklist/golden/readiness/release commands | ✅ 通过 — Non-goals 明确列出，Slice 1 要求 "file-read free, repository-free, source-helper-free" |
| 是否保持 diagnostics bounded 和 non-authoritative，保持 residual closure semantics 不变（除 diagnostic payload） | ✅ 通过 — raw_text_excerpt 声明为 bounded/non-authoritative，stop condition 禁止改变 closure semantics |
| 是否足够强地指定 deterministic sorting/fingerprinting 以支持未来 like-with-like 比较 | ⚠️ 基本通过 — 排序键具体明确，fingerprint 范围有 DS-F3 轻微歧义 |
| 是否避免过度宽泛的 implementation scope 或 future-slice leakage | ✅ 通过 — 范围限于单一文件 `source_truth_residual_closure.py`，四个 slice 均为增量添加诊断能力 |

---

## Controller Judgment Inputs Check

对照 controller judgment `docs/reviews/docling-reference-bundle-comparability-diagnostic-controller-judgment-20260617.md` 的 binding 约束：

| Controller Binding | Plan 是否遵守 |
|---|---|
| define a stable, reproducible reference-bundle producer contract | ✅ bundle-level + cell-level + text-span contracts 已定义 |
| decide whether to persist enough raw cell/text-span payload | ✅ cell-level 和 text-span diagnostic contract 包含 raw_text_excerpt 和 normalized_text_hash |
| preserve `source_truth_status=not_proven` and candidate-only boundaries | ✅ 全计划反复声明 |
| avoid direct PDF/cache/source-helper access | ✅ Non-goals 和 stop conditions 覆盖 |
| avoid live acquisition unless separately authorized | ✅ 未授权 |
| If exact producer-line root cause is required, create separately scoped gate | ✅ Stop condition 明确：exact producer-line root cause 被请求时应 stop and return to controller |

---

## Worker Self-check

- 分配 role：plan review worker only（DS），非 controller，非 implementation worker
- 分配 gate：`Docling Reference Bundle Producer Determinism Contract Planning Gate` — plan review
- 仅允许输出文件：`docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-ds-20260617.md` — ✅ 正在写入此文件
- 无代码编辑：✅ 未编辑任何代码文件
- 无 commit/push/PR：✅ 未执行
- NOT_READY 保留：✅ verdict 为 `PASS_WITH_FINDINGS_NOT_READY`，artifact 中未声明任何 readiness
- Scope 边界：仅审查计划 artifact，不进入 implementation、controller judgment 或 gateflow — ✅

**Self-check: pass**
