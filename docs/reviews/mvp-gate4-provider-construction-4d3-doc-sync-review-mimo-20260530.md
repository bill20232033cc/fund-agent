# MVP Gate 4 Slice 4D3 Doc/Control Sync Review

日期：2026-05-30
角色：review agent（独立审查，不修改文件）
Gate：`MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression gate`
结论：**BLOCKING** — 1 blocking finding 需要修复后才能通过

---

## Verdict

**fail** — 存在 1 个 blocking finding：`docs/implementation-control.md` 的 Current Decision Summary 中 "only production report/checklist mainline" 与同一文件中已接受的 `--use-llm` provider-backed 生产路径直接冲突。

---

## Blocking Findings

### B1. `docs/implementation-control.md` 第 122 行 "only" 与已接受 provider-backed 路径冲突

**文件**：`docs/implementation-control.md` 第 122 行
**现状**：
```
- Current deterministic `fund-analysis analyze/checklist` remains the only production report/checklist mainline.
```

**冲突证据**：

1. 同文件第 21 行（Control Truth Guardrails）已改为"默认"口径：
   ```
   - 当前默认实现仍以确定性 `fund-analysis analyze/checklist` 为生产主链路
   ```
   Guardrails 正确使用了"默认"（default）限定词。

2. 同文件第 128 行（同一 Current Decision Summary 小节）已接受 `--use-llm` 为生产路径：
   ```
   - Gate 4 Slice 4C/4D `fund-analysis analyze --use-llm` is implemented and accepted locally as explicit provider-backed CLI opt-in: complete typed env config constructs Service-owned `openai_compatible` writer/auditor clients and calls `analyze_with_llm()`; missing config, construction failure and incomplete LLM result fail closed without deterministic fallback.
   ```

3. `docs/current-startup-packet.md` 第 33 行已改为 "Default report generation is deterministic"。

4. `docs/design.md` 第 23 行已改为 "当前默认 `fund-analysis analyze` 与 `fund-analysis checklist`"。

**冲突性质**："only" 表示排他性——确定性路径是唯一的生产报告/检查清单主线。但 4D1/4D2 已被 accepted 为 provider-backed 生产路径（配置完整时可输出 LLM 报告）。Guardrails 和 startup-packet 正确改为 "默认"，而 Decision Summary 遗漏了同一更新。

**最小修复建议**：将第 122 行改为：
```
- Current deterministic `fund-analysis analyze/checklist` remains the default production report/checklist mainline.
```
仅改动 "only" → "default"，与 Guardrails 第 21 行、startup-packet 第 33 行、design.md 第 23 行保持一致。

---

## Non-Blocking / Residual Findings

### N1. startup-packet Route C Gate 4 表格措辞微调可选

`docs/current-startup-packet.md` 第 68 行：
```
| Gate 4 | Slice 4A `final_chapter_assembler`, Slice 4B Service `analyze_with_llm`, Slice 4C CLI `--use-llm` and Slice 4D provider construction accepted locally; next is aggregate review |
```
"next is aggregate review" 与下方 Gate 4 Slice 4D 描述末尾 "next is aggregate review" 略有重复，不影响正确性。

### N2. design.md §5.4 未在 Gate 4 行更新 "Slice 4D" 为 "Slices 4C/4D"

`docs/design.md` Gate 4 行描述已更新为 "Slices 4A/4B/4C/4D accepted locally"，但 §5.4.1 当前已实现状态的 bullets 中，4C 和 4D 合并为单条。这不是错误，只是 4C/4D 合并表述与 Gate 序列表的 4A/4B/4C/4D 分列略有风格差异。非阻塞。

### N3. implementation-control.md Gate 4 Route C 表未同步更新 "Slice 4D"

`docs/implementation-control.md` 第 141 行 Route C Future Route 表格中：
```
| MVP Gate 4 | Slices 4A `final_chapter_assembler`, 4B Service `analyze_with_llm`, 4C CLI `--use-llm` and 4D provider construction accepted locally |
```
此处已正确更新。一致。

### N4. README 用户手册未过度泄漏实现

`README.md` 的 `--use-llm` 环境变量表和 fail-closed 说明面向用户，足够指导配置使用。没有泄漏 Service 内部类名、Fund writer/auditor Protocol 细节或 `llm_provider.py` 内部结构。符合 AGENTS.md README 定位（用户手册）。

---

## Validation Reviewed

### Lens 1: 4D1/4D2 accepted provider-backed CLI path 是否准确写为 current fact

| 文件 | 状态 |
|------|------|
| `docs/design.md` §2.1 架构边界 Config 行 | ✅ 新增 `llm.py` |
| `docs/design.md` §2.1 当前实现裁决 | ✅ 新增 Route C `analyze --use-llm` 显式 opt-in 描述 |
| `docs/design.md` §5.4.1 Route C 已实现状态 | ✅ 4C/4D 合并为 provider-backed 入口 |
| `docs/design.md` Route C gate 序列 Gate 4 行 | ✅ 更新为 4A/4B/4C/4D |
| `docs/design.md` 目录结构 | ✅ 新增 `llm.py` 和 `llm_provider.py` |
| `docs/current-startup-packet.md` §2 | ✅ 更新 gate/next entry/commits |
| `docs/current-startup-packet.md` §3 | ✅ 4D1/4D2 代码事实完整 |
| `docs/current-startup-packet.md` §4 | ✅ 4D accepted |
| `docs/implementation-control.md` Guardrails | ✅ 正确 |
| `docs/implementation-control.md` Decision Summary | ⚠️ 第 122 行 "only" 冲突（blocking） |
| `docs/implementation-control.md` Route C/Gate/Residuals | ✅ 正确 |
| `README.md` | ✅ 环境变量表 + fail-closed 说明 |
| `fund_agent/README.md` | ✅ Service provider construction + Fund boundary |
| `fund_agent/config/README.md` | ✅ LLM env config 说明 |
| `tests/README.md` | ✅ MockTransport/fake env/monkeypatch 说明 |

Default analyze/checklist 仍为 deterministic 的表述在所有文件中均正确保留。

### Lens 2: 是否没有把 deferred 内容写成已实现

| Deferred 项目 | 状态 |
|---------------|------|
| Host/Agent/dayu | ✅ 均标注为 future/deferred |
| retry/backoff | ✅ residual |
| provider fallback | ✅ residual |
| live provider smoke | ✅ residual |
| 多模型 writer/auditor split | ✅ residual |
| chapter 0/7 LLM polish | ✅ residual |
| Evidence Confirm | ✅ residual |
| full FundToolService | ✅ residual |

### Lens 3: Env contract 是否与 4D1 code 一致

| 参数 | 控制文档 | README | config/README | 一致性 |
|------|---------|--------|---------------|--------|
| provider required | ✅ | ✅ | ✅ | 一致 |
| model required | ✅ | ✅ | ✅ | 一致 |
| base_url required | ✅ | ✅ | ✅ | 一致 |
| api_key env var default `FUND_AGENT_LLM_API_KEY` | ✅ | ✅ | ✅ | 一致 |
| timeout `(0, 300]` default `60` | ✅ | ✅ | ✅ | 一致 |
| max_output_chars `(0, 50000]` default `12000` | ✅ | ✅ | ✅ | 一致 |
| max_output_chars 是字符上限不是 token budget | ✅ | — | ✅ | 一致 |

### Lens 4: Failure semantics 是否与 4D2 code 一致

| 失败场景 | 控制文档 | README |
|----------|---------|--------|
| missing config → exit 1, stdout empty | ✅ | ✅ |
| construction fail → exit 1, stdout empty | ✅ | ✅ |
| runtime error → exit 1, no fallback | ✅ | ✅ |
| blocked/partial → exit 1, no fallback | ✅ | ✅ |
| incomplete final assembly → exit 1, no fallback | ✅ | ✅ |
| quality gate block/not-run → exit 2 | ✅ | ✅ |
| no deterministic fallback | ✅ | ✅ |

### Lens 5: Control docs next entry point 是否明确到 Gate 4 aggregate review

| 文件 | Next entry point | Commits 记录 |
|------|-----------------|-------------|
| `docs/current-startup-packet.md` | `MVP Gate 4 Slice 4D aggregate review gate` ✅ | `26203d3` + `ab0590a` ✅ |
| `docs/implementation-control.md` | `MVP Gate 4 Slice 4D aggregate review gate` ✅ | `26203d3` + `ab0590a` ✅ |

不再指向 4D1/4D2。一致。

### Lens 6: Release/golden residual 是否保留但不拉回 MVP 主线

- `docs/current-startup-packet.md` §6 保留 golden/QDII/FOF/promotion residual ✅
- `docs/implementation-control.md` Open Residuals 保留 golden/promotion residual ✅
- 无 golden/fixture/score/quality gate 语义变更 ✅

### Lens 7: README 用户手册是否不过度泄漏内部实现

- `README.md`：环境变量表面向用户，fail-closed 说明清晰。未泄漏 Service 类名、Protocol 细节或 `llm_provider.py` 内部结构 ✅
- `--use-llm` 参数说明足够用户配置和排错 ✅

### Lens 8: Config/tests docs 是否说明 pytest fake env/MockTransport/monkeypatch

- `fund_agent/config/README.md`：明确 "pytest 使用 fake env mapping、`httpx.MockTransport` 和 monkeypatch，不需要真实 key，也不访问 live provider" ✅
- `tests/README.md`：CLI 测试条目更新为 "LLM/provider 分支使用 fake env、monkeypatch 或测试替身，不访问 live provider" ✅
- 新增维护约定条目："LLM config/provider/CLI 测试必须使用 fake env mapping、`httpx.MockTransport`、monkeypatch 或测试替身" ✅

### Lens 9: `implementation-control.md` 第 122 行冲突判断

**结论：BLOCKING / fix-required。**

详见上方 B1。该句与同文件 Guardrails（第 21 行）、同文件 Decision Summary 第 128 行、startup-packet（第 33 行）和 design.md（第 23 行）直接冲突。修复成本为一个单词（"only" → "default"）。

---

## Scope Check

| 检查项 | 状态 |
|--------|------|
| 只修改允许的 7 个文档文件 + 本 review artifact | ✅ |
| 未修改 Python runtime code | ✅ |
| 未修改 tests | ✅ |
| 未引入 Host/Agent/dayu | ✅ |
| 未修改 golden/score/snapshot/quality gate | ✅ |
| 未修改 final judgment 语义 | ✅ |
| 未修改 `AGENTS.md` | ✅ |
| 未做 live provider smoke | ✅ |
| 未做 provider fallback / retry/backoff | ✅ |
| 未 commit / push / PR / merge / release | ✅ |

---

## Summary

4D3 docs/control sync 整体质量良好：7 个文档文件的更新准确反映了 4D1/4D2 已接受的 provider-backed CLI 路径，deferred 项目均正确标注为 future/residual，env contract 和 failure semantics 与代码一致，next entry point 明确指向 Gate 4 aggregate review。

唯一阻塞项是 `docs/implementation-control.md` 第 122 行 "only" 措辞与已接受的 `--use-llm` 生产路径冲突。修复后即可通过。
