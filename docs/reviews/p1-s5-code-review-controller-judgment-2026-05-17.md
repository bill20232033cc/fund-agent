# P1-S5 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S5 `§3` 表现提取与投资者收益 fallback
> Review artifacts：
> - `docs/reviews/p1-s5-code-review-mimo-2026-05-17.md`
> - `docs/reviews/p1-s5-code-review-glm-2026-05-17.md`
> Implementation artifact：
> - `docs/reviews/p1-s5-implementation-2026-05-17.md`

## 1. 裁决前提

- 两份独立 code review 均给出 `pass`
- 两份 review 均确认：
  - 当前实现严格留在 `§3` 边界内
  - `nav_benchmark_performance` 与 `investor_return` 已成为稳定输出
  - `investor_return` 已明确区分 `direct / estimated / missing`
  - 直接命中与估算口径命中均带 `EvidenceAnchor`
  - 当前实现未越界到 `documents/**`、`pdf/**`、`data_extractor.py`、`nav_data.py` 或其他 extractor
  - 当前 `estimated` 仅消费 `§3` 已显式标注的估算口径，没有偷跑 P2 分析公式
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py -q
```

结果：`8 passed`

## 2. Accepted Findings

### A1-已修复-中-`nav_benchmark_performance` 在部分命中时仍标记为 `direct`

- **来源**:
  - reviewer finding（并行独立 review）
- **裁决**: `accepted`
- **原因**:
  - 当前实现中，只要 `nav_growth_rate` 和 `benchmark_return_rate` 任意一项命中，就会把整个 `nav_benchmark_performance` 标记为 `extraction_mode="direct"`
  - 这会把“部分披露”伪装成“完整直接披露”，对下游状态判断构成直接语义误导
  - 该问题属于当前 slice 的 correctness 缺陷，不应 deferred

### A2-已修复-低-`estimated` 路径的 `fallback_status` 命名存在语义误导

- **来源**:
  - reviewer finding（并行独立 review）
- **裁决**: `accepted`
- **原因**:
  - 原状态名 `applied_in_section` 容易让下游误以为“后续 fallback 逻辑已经执行过”
  - 实际上当前 `estimated` 只表示“`§3` 中已显式披露估算口径”，没有执行任何跨章节 fallback
  - 该问题不影响行为，但会提高后续契约演进成本，当前改名成本低，应直接修

### A3-已修复-低-证据锚点完整性 contract 未被测试锁定

- **来源**:
  - reviewer finding（并行独立 review）
- **裁决**: `accepted`
- **原因**:
  - 原测试只断言 `row_locator`，没有锁定 `source_kind`、`section_id`、`document_year`、`note`
  - 这会让“证据必须可溯源”的 contract 存在静默回归风险
  - 当前补强测试成本低，应在本 slice 直接关闭

### A4-已修复-中-`fund` 与 `tests` 文档未随当前稳定 extractor 契约同步

- **来源**:
  - controller 自查
- **裁决**: `accepted`
- **原因**:
  - 当前 slice 已新增 `PerformanceExtractionResult`、`extract_performance()`、`tests/fund/extractors/test_performance.py` 与 `tests/fixtures/fund/extractors/performance/**`
  - 按 `AGENTS.md` 的文档同步规则，`fund_agent/fund/README.md` 与 `tests/README.md` 必须与当前实现对齐
  - 当前 worktree 中这两份 README 的 `P1-S5` 同步属于仓库规则层面的必要 fix，不是 capability 代码正确性缺陷

### A5-已修复-中-总控文档尚未把 `P1-S5` implementation 完成事实和 review gate 对齐

- **来源**:
  - controller 自查
- **裁决**: `accepted`
- **原因**:
  - `docs/implementation-control.md` 需要把 `P1-S5` 的 implementation 完成事实、当前 gate 和 artifact 入口显式记录下来
  - 当前 worktree 已包含这组总控同步改动，应作为 controller fix 一并收口

## 3. Deferred Findings

### D1-未修复-中-测试未覆盖 `§3` 整体缺失场景

- **来源**:
  - `AgentMiMo` Finding N-01
  - `AgentGLM` Finding N-1
- **裁决**: `deferred-with-owner`
- **Owner / Destination**: `P1-S8 / integration and fixture expansion`
- **原因**:
  - 当前 `P1-S5` completion signal 关注的是 `§3` 表现字段和投资者收益三态输出
  - `§3` 整体缺失是合理边界，但更适合在真实样本矩阵或集成测试里覆盖，而不是在当前最小 slice 内继续扩样本

### D2-未修复-低-docstring 风格存在形式化冗余

- **来源**:
  - `AgentMiMo` Finding N-04
- **裁决**: `deferred-with-owner`
- **Owner / Destination**: `later slice / docstring cleanup`
- **原因**:
  - 当前中文 docstring 覆盖已满足仓库硬约束
  - `Raises: 无显式抛出。` 属于风格问题，不影响行为或边界

### D3-未修复-低-手工 fixture 未覆盖真实年报格式变体

- **来源**:
  - `AgentMiMo` Finding N-05
- **裁决**: `deferred-with-owner`
- **Owner / Destination**: `P1-S8 / real sample matrix`
- **原因**:
  - 当前最小 fixture 的目的就是锁定三态和 anchor 行为
  - 真实年报格式异构应由后续样本矩阵统一回归，而不是在本 slice 无上限扩样本

### D4-未修复-低-`estimated_investor_return_rate` 的匹配顺序安全性依赖当前 pattern 细节

- **来源**:
  - `AgentMiMo` Finding N-06
- **裁决**: `deferred-with-owner`
- **Owner / Destination**: `later slice / extractor pattern hardening`
- **原因**:
  - 当前 reviewer 已确认现有顺序是安全的，不构成 bug
  - 后续若扩 pattern 变体，再一起做顺序和注释增强更合理

## 4. 当前 Gate 结论

- `P1-S5 code review` 结论：`pass-with-fix`
- 下一步：
  - 执行 code + controller fix，关闭 A1 / A2 / A3 / A4 / A5
  - 对 fix 做 controller re-review
  - 通过后进入 `accepted slice commit`
