# Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition — MiMo Independent Review

Date: 2026-06-14

Role: MiMo independent reviewer, not controller.

Review target: `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-20260614.md`

Gate: `Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition Gate`

Verdict: **PASS**

## 1. Scope

This review challenges the disposition artifact's assumptions, root-cause classification, sequencing, evidence handling and next-gate recommendation. Review method: adversarial pass against safe metadata, no-live code evidence, accepted upstream facts and repo instructions.

Evidence read for this review:

- Review target artifact in full.
- `AGENTS.md` — repo rule truth.
- `docs/current-startup-packet.md` — current gate, accepted checkpoint lineage, control truth.
- `docs/implementation-control.md` — current guardrails, active gate objective.
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` — accepted upstream live judgment.
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-20260614.md` — upstream live evidence artifact.
- `reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/summary.json` — safe scalar metadata.
- `reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/chapters/chapter-03.json` — safe Chapter 3 metadata.
- `fund_agent/fund/chapter_writer.py` lines 660-736, 916-1045, 1101-1124, 1560-1625, 1759-1880 — writer prompt contract, typed required-output plan, preflight block, parser marker items, marker/degrade issue generation.
- `fund_agent/agent/runner.py` lines 1172-1193 — Agent runner typed required-output item supply.

## 2. Findings

### 01-未修复-[低]-summary.json / chapter-03.json attempt_count 不一致

- **入口/函数**: safe runtime metadata 读取
- **文件(行号)**: `summary.json` `first_failed.attempt_count`; `chapter-03.json` `attempt_count`
- **输入场景**: 读取 Chapter 3 safe metadata 做 disposition 分类
- **实际分支**: `summary.json.first_failed.attempt_count=1` 而 `chapter-03.json.attempt_count=null`
- **预期行为**: 两处 metadata 对同一 chapter 的 attempt count 应一致
- **实际行为**: summary 层记录 attempt_count=1，chapter 文件层记录 null
- **直接证据**: summary.json `"first_failed":{"attempt_count":1,...}`; chapter-03.json `"attempt_count":null`
- **影响**: 仅局部 diagnostic 不一致；不影响 disposition 结论，因为 prompt diagnostics 中 `attempt_index=0` 与 summary `attempt_count=1` 一致（0-indexed = 第 1 次）
- **建议改法和验证点**: 后续 no-live diagnostic gate 应记录此不一致并在验证矩阵中覆盖；不阻塞本次 disposition
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: 低

### 02-未修复-[低]-chapter-03.json runtime_diagnostics 为 null

- **入口/函数**: Chapter 3 safe metadata 读取
- **文件(行号)**: `chapter-03.json` `runtime_diagnostics`
- **输入场景**: 读取 Chapter 3 runtime diagnostics 做 provider/runtime 分类
- **实际分支**: `runtime_diagnostics=null`
- **预期行为**: 若 provider 已被调用，应有 runtime diagnostics
- **实际行为**: null，但 artifact 正确解读为 writer parse 阶段失败、provider 未被调用
- **直接证据**: chapter-03.json `"runtime_diagnostics":null`; prompt diagnostics `"phase":"writer_parse"`, `"finish_reason":"stop"`
- **影响**: 无直接影响；artifact 正确将此作为 evidence limitation 处理，不从中推断 provider 质量
- **建议改法和验证点**: 无；null 值与 writer-parse 阶段失败一致
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: 低

## 3. Assumption and Sequencing Challenge

### 3.1 Root-cause classification

Artifact 分类为 `LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT`。

**挑战结果**: 分类合理且有直接证据支撑。

- repo fact: writer prompt 在 `chapter_writer.py:682-708` 定义了 exact required-output marker 行为，包括 `<!-- required_output:<typed item id> -->` 格式。
- repo fact: parser 在 `chapter_writer.py:1759-1784`（`_required_output_marker_issues`）和 `chapter_writer.py:1787-1834`（`_required_output_degrade_issues`）检查 marker presence 并在缺失时 emit `missing_required_output_marker` / `writer:required_output_gap_missing`。
- repo fact: `chapter_writer.py:1806` 确认 `writer:required_output_gap_missing` issue 仅在 `plan.action == "render_evidence_gap"` 时生成，意味着 item 01 和 05 的 typed contract 行为均为 `render_evidence_gap`。
- accepted live fact: Chapter 3 prompt diagnostics 显示 `phase=writer_parse`, `required_output_missing_count=2`, `issue_reason_counts.missing_required_output_marker=2`, issue prefix `writer:required_output_gap_missing=2`。
- accepted live fact: issue ids 为 `ch3.required_output.item_01` 和 `ch3.required_output.item_05`。

分类不是 source/EID issue、provider availability issue、runtime truncation issue、final assembly bug 或 missing template truth-source issue。这一排除有直接证据支撑：`runtime_diagnostics=null` + `phase=writer_parse` + `finish_reason=stop` 表明失败发生在 writer parse 阶段、provider 调用之前。

### 3.2 Sequencing

Artifact 决定先做 no-live diagnostic evidence gate，再做 fix planning。

**挑战结果**: 顺序正确。

- 当前证据足以排除 source/provider/final-assembly overread。
- 当前证据不足以决定修复机制：prompt wording、repair-context propagation、writer retry trigger、item 05 policy、diagnostic mapping 或 accepted residual 都是候选。
- diagnostic gate 的四个最小问题（prompt 含 exact markers?、fake response 可复现?、repair path 有足够 context?、item 05 配置正确?）精确覆盖了 fix-planning 前需要回答的问题。

### 3.3 Stale truth-doc use

**挑战结果**: 未发现 stale truth-doc use。

- artifact 引用的 `docs/design.md` 行号（154-180, 512-522, 529-536）描述 CHAPTER_CONTRACT、typed template、EvidenceAvailability、Route C、Host/Agent 和 writer/auditor boundary。这些与 `AGENTS.md` 和 `docs/implementation-control.md` 当前控制面一致。
- artifact 引用的 `docs/current-startup-packet.md` 行号（22-24, 49-55, 66-73）描述当前 gate、accepted checkpoint lineage 和 no implementation boundary。与当前 startup packet 内容一致。

### 3.4 Overread from runtime null fields

**挑战结果**: 未发现 overread。

- artifact 明确声明 "Do not infer provider quality or provider availability from this blocker. Safe runtime metadata shows provider attempt count 0 and no provider runtime categories"。
- artifact 明确声明 "Do not claim Chapter 3 content quality, correctness, factual sufficiency or source-body validity from safe metadata"。
- `runtime_diagnostics=null` 被正确解读为 writer-parse 阶段失败的 evidence limitation，而非 provider 质量证据。

### 3.5 Premature fix-planning

**挑战结果**: 未发现 premature fix-planning。

- artifact 明确 "proceed to a no-live diagnostic evidence gate before any fix planning"。
- Residual 表将 "Raw prompt/body not read in this gate" 和 "Provider behavior for this blocker remains unclassified" 标记为 evidence limitation / accepted residual。
- 未提出具体修复方案或代码修改建议。

### 3.6 Unsupported line references

**挑战结果**: 所有 line references 经验证均正确。

| Reference | Verified |
|---|---|
| `chapter_writer.py:664-736` | `_chapter_prompt_fragments` at line 660; range covers writer prompt marker contract |
| `chapter_writer.py:916-1045` | `_required_output_evidence_plan` at 916, `_required_output_plan_item` at 942, `_required_output_action` at 1005 |
| `chapter_writer.py:1101-1124` | `_required_output_preflight_issues` at 1101 |
| `chapter_writer.py:1560-1625` | `_prompt_required_output_payload` at 1560, `_prompt_required_output_plan_item` at 1582, `_prompt_required_output_marker_items` at 1605 |
| `chapter_writer.py:1759-1878` | `_required_output_marker_issues` at 1759, `_required_output_degrade_issues` at 1787, `_required_output_segment_contains` at 1837, `_required_output_marker` at 1866 |
| `runner.py:1172-1193` | `_typed_required_output_items` at 1172 |

## 4. Adversarial Failure Pass

### 4.1 Could this be a parser sensitivity issue rather than writer noncompliance?

`_required_output_segment_contains`（line 1837）使用 `text.find(marker)` 做 exact string match。若 writer 输出的 marker 有微小格式差异（多余空格、不同换行符），parser 会判定为 missing。当前 disposition 不区分"writer 未输出 marker"和"writer 输出了近似 marker 但 parser 未匹配"。

**评估**: 这属于 no-live diagnostic gate 的验证范围（diagnostic question D2: "Does a no-live fake writer response that omits only those gap marker segments reproduce the exact issue?"）。不阻塞当前 disposition，但 diagnostic gate 应覆盖此场景。

### 4.2 Could item 01 and item 05 have different root causes?

Both items emit the same `writer:required_output_gap_missing` issue code，表明两者都是 `render_evidence_gap` action 且 writer 未输出 approved gap phrasing。但 item 05 的 `when_evidence_missing` 配置和 evidence availability 状态未经独立验证。

**评估**: artifact 正确将 item 05 policy status 列为 residual，diagnostic question D4 覆盖此场景。不阻塞当前 disposition。

### 4.3 Could the repair path have corrected this?

`attempt_count=1` 和 `attempt_index=0` 表明只有一次 writer attempt，无 repair attempt。当前 repair budget 为 `max_repair_attempts=1`（per `docs/implementation-control.md:35`）。若 repair context 传播了 missing-marker issue ids，第二次 attempt 可能修复此问题。

**评估**: artifact 将此列为 diagnostic question D3（"Does the current repair path receive missing-marker issue ids and required-output item ids clearly enough to make a second attempt possible within existing repair budget?"）。不阻塞当前 disposition。

### 4.4 Could this finding be caused by a template truth-source gap?

`docs/design.md` 定义 `TEMPLATE_CONTRACT_MANIFEST_JSON` 为 authored template contract truth source。若 Chapter 3 item 01/05 的 `when_evidence_missing` 在 canonical template 中未正确声明，可能触发 preflight block 而非 `render_evidence_gap`。

**评估**: 但 live metadata 显示 issue 是 `writer:required_output_gap_missing`（来自 `_required_output_degrade_issues`），不是 `writer:required_output_block`（来自 `_required_output_preflight_issues`）。这表明 item 01/05 的 `when_evidence_missing` 已正确配置为 `render_evidence_gap`，否则 preflight 会先阻断。artifact 的 root-cause 分类与此一致。

## 5. Residual Risk

| Risk | Classification | Notes |
|---|---|---|
| Raw prompt/body not read | Evidence limitation | Appropriate for disposition gate; diagnostic gate authorized next |
| Provider behavior unclassified | Accepted residual | `runtime_diagnostics=null` consistent with writer-parse failure |
| Item 05 policy not independently verified | Diagnostic residual | Covered by diagnostic question D4 |
| Parser sensitivity not tested | Diagnostic residual | Covered by diagnostic question D2 |
| Repair-context propagation not tested | Diagnostic residual | Covered by diagnostic question D3 |
| summary/chapter attempt-count mismatch | Non-blocking diagnostic | DS previously noted; does not affect disposition |
| Full Route C completion unproven | Readiness blocker | Preserved `NOT_READY` |

## 6. Reviewer Self-Check

- [x] Review mode, scope and source evidence written in Section 1.
- [x] Each finding bound to specific code location or explicit behavior; root cause uses direct evidence.
- [x] Findings are material, executable, no style/nit/speculation.
- [x] Adversarial pass documented in Section 4.
- [x] Open questions: none beyond those already captured in diagnostic gate recommendations.
- [x] Residual risk documented in Section 5.
- [x] Output path is `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-review-mimo-20260614.md`.

## 7. Final Verdict

**PASS**

The disposition artifact correctly classifies the Chapter 3 blocker as `LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT`, properly sequences diagnostic evidence before fix planning, maintains all `NOT_READY` and EID single-source/no-fallback postures, and does not overread from runtime null fields or stale truth-docs. All line references are verified. The two low-severity metadata inconsistencies (attempt_count mismatch, null runtime_diagnostics) are correctly handled as non-blocking residuals. The recommended next gate (`Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate`) with its four minimum diagnostic questions is appropriate and sufficient to unblock fix planning.
