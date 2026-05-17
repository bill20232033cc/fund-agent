# P1-S4 Re-Review (AgentGLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> Phase / Slice：P1 / P1-S4 基础画像与基金类型识别
> 分支：`chore/reconcile-baseline`
> 审查范围：controller fix 涉及的 3 个文件
> Fix artifact：`docs/reviews/p1-s4-fix-2026-05-17.md`
> Controller judgment：`docs/reviews/p1-s4-code-review-controller-judgment-2026-05-17.md`

---

## 结论

**PASS — A1、A2 已被正确关闭，fix 未引入新的边界问题。**

`fund_agent/fund/README.md` 与 `tests/README.md` 已与当前实现对齐。`docs/implementation-control.md` 的 gate 推进、slice 编号更新和 P1-S4 状态登记均正确。

下文列出 4 条 non-blocking findings，属于总控文档中残留的旧编号/旧状态未完全清理，不影响 A1/A2 的关闭判定，建议在后续 gate 中顺手修掉。

---

## A1 关闭验证：fund_agent/fund/README.md 与 tests/README.md 同步

### fund_agent/fund/README.md

逐项核实：

| 核实项 | 状态 | 证据 |
|--------|------|------|
| 导入路径是否与代码一致 | ✅ | 行 10-11：`from fund_agent.fund.documents import FundDocumentRepository` / `from fund_agent.fund.extractors import extract_profile`，与 `extractors/__init__.py` 的 `__all__` 导出一致 |
| `ProfileExtractionResult` 四类输出是否完整 | ✅ | 行 27-30：`basic_identity`、`product_profile`、`benchmark`、`fee_schedule`，与 `models.py:54-67` 的定义一致 |
| `classified_fund_type` / `classification_basis` 是否声明为稳定输出 | ✅ | 行 27 / 行 50-51 |
| `EvidenceAnchor` 描述是否与 `models.py` 一致 | ✅ | 行 32：列出 `document_year`、`section_id`、`row_locator` 和命中原文，与 `models.py:14-33` 的字段定义一致 |
| 内部分层是否准确反映当前目录结构 | ✅ | 行 61-69：`documents/`、`extractors/`、`fund_type.py`、`pdf/` 及后续扩展位置 |
| 当前边界是否准确 | ✅ | 行 71-77：只支持 `annual_report`、只覆盖 `§1/§2`、`data_extractor.py` 未接入，均与代码事实一致 |
| 是否遵守 AGENTS.md "当前怎么用"约束 | ✅ | 全文描述当前实现状态，未设计未来 |

### tests/README.md

逐项核实：

| 核实项 | 状态 | 证据 |
|--------|------|------|
| 6 个测试文件是否都已列出 | ✅ | 行 7-12：`test_repository`、`test_cache`、`test_downloader`、`test_parser`、`test_profile`、fixture 目录 |
| 运行命令是否可直接执行 | ✅ | 行 19-21 / 行 26-28 |
| 维护约定是否与 AGENTS.md 测试策略一致 | ✅ | 行 32-36：围绕公共契约断言、先补 fixture 再补测试、不把 P2 分析混入 P1 数据层测试 |

**A1 关闭判定：已正确关闭。**

---

## A2 关闭验证：docs/implementation-control.md 同步

### gate 推进

- 行 34：当前 gate 已从 `P1-S4 implementation + review` 推进到 `P1-S5 implementation + review` ✅
- 行 55-57：下一 entry point 已明确为 P1-S5 ✅

### P1 任务切片表

- 行 185-192：已从旧口径 `P1-S4~P1-S12` 统一到已接受 plan 的 `P1-S1~P1-S8` ✅

### P1-S4 状态登记

- 行 264-288：`P1-S4 当前状态（2026-05-17）` 已补充，包含完成内容、residual risks、验证命令 ✅

### P1-S4 artifact 列表

- 行 90-100：已登记 baseline reconciliation、implementation、code review、controller judgment、fix、re-review、accepted slice commit（PENDING） ✅

**A2 关闭判定：已正确关闭。**

---

## Non-Blocking Findings

### R-1 [MEDIUM] implementation-control.md 行 407 仍残留旧 slice 编号

**文件与行号：** `docs/implementation-control.md:407`

**事实：**

```
- P1 内部的 Slice 可部分并行（P1-S1~S3 与 P1-S8~S12 可并行）
```

已接受 plan 的 P1 slice 是 `P1-S1~P1-S8`，不存在 `P1-S9~P1-S12`。按 plan §8.1，并行规则应为 `P1-S4~P1-S7` 可并行（在 P1-S3 被接受后）。

**影响：** 不影响 A2 关闭判定（A2 重点是 gate 推进和 P1-S4 状态），但与已更新到 P1-S8 的切片表并存了旧口径。

**建议：** 在 P1-S5 或下一个涉及总控文档修改的 gate 中顺手修正。

---

### R-2 [MEDIUM] BQ-4 / BQ-5 状态未随已完成的 slice 更新

**文件与行号：** `docs/implementation-control.md:419` 和 `:421`

**事实：**

- 行 419：`BQ-4 | ... | P1-S12 验证后关闭` — 引用旧编号 `P1-S12`，应为 `P1-S8`（净值适配器已归入 façade 集成 slice）。
- 行 421：`BQ-5 | ... | ⬜ open | 作为 P1-S2 的首要修复项` — P1-S2 已完成且 §3 root cause 已关闭（行 229-244 明确记载），但 BQ-5 状态仍为 `⬜ open`，应为 `✅ closed`。

**影响：** 不影响 A2 关闭判定，但会让后续读者误以为 §3 问题尚未关闭。

**建议：** 与 R-1 一并在下一 gate 修正。

---

### R-3 [LOW] P1-S4 artifact 列表缺少 MiMo code review

**文件与行号：** `docs/implementation-control.md:93-95`

**事实：**

当前 P1-S4 code review 子列表为：

```
- `docs/reviews/p1-s4-code-review-glm-2026-05-17.md`
- `docs/reviews/p1-s4-code-review-controller-judgment-2026-05-17.md`
```

缺少 `docs/reviews/p1-s4-code-review-mimo-2026-05-17.md`。该文件已存在于磁盘（9857 字节），controller judgment 也引用了它（行 7）。对比 P1-S1 的 artifact 列表（行 65-66），MiMo 和 GLM 的 review 都被分别列出。

**影响：** 不影响 A2 关闭判定。artifact 列表不完整但不影响 gate 推进。

**建议：** 下一 gate 中补齐。

---

### R-4 [LOW] P1-S4 re-review 列表中 MiMo re-review 未标注 PENDING

**文件与行号：** `docs/implementation-control.md:97-99`

**事实：**

```
- re-review:
  - `docs/reviews/p1-s4-rereview-glm-2026-05-17.md`
  - `docs/reviews/p1-s4-rereview-controller-2026-05-17.md`
```

当前 re-review 只列了 GLM 和 controller，未列出 MiMo re-review（`p1-s4-rereview-mimo-2026-05-17.md`）。对比 P1-S1 的 re-review 列表（行 70-71），MiMo 和 GLM 的 re-review 都被列出。如果本轮 re-review 流程不包含 MiMo，则当前列表正确；否则应补齐或标注为 PENDING。

**影响：** 不影响 A2 关闭判定。需 controller 确认本轮 re-review 是否只需 GLM。

---

## 总结

| Fix Item | 关闭状态 | 新边界问题 |
|----------|----------|-----------|
| A1: README 同步 | ✅ 已关闭 | 无 |
| A2: 总控文档同步 | ✅ 已关闭 | 无（有 4 条旧内容残留，non-blocking） |

A1、A2 均已正确关闭。4 条 non-blocking findings 全部属于 `docs/implementation-control.md` 中 P1-S4 之前就已存在的旧编号/旧状态，fix 没有引入新的边界问题。建议在 P1-S5 或下一个涉及总控修改的 gate 中一并清理。
