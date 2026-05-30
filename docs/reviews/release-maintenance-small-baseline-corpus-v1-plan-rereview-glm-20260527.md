# Re-Review: Small Baseline Corpus v1 Evaluation Plan

> **Reviewer**: AgentGLM (independent plan re-reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md` (revised)
> **Previous review**: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-review-glm-20260527.md`
> **Scope**: Targeted re-review of GLM F1–F4 only, plus scope drift check

---

## Finding Disposition

### F1 (MATERIAL) — RESOLVED

Clean coverage 3/6 fund types 与 decision boundary 卡线问题。

修订后的 plan 做了三处针对性修改：

1. **Reconciliation 新增显式声明**（rev line 24）：
   > "The current clean denominator is only three clean candidates across three fund-type slots... This remains below the desired 5-10 representative target and below broad fund-type coverage..."

2. **Manifest freeze 新增覆盖记录要求**（rev line 57）：
   > "Record that this is only three clean candidates and three fund-type slots, below the 5-10 representative target."

3. **Next gate decision rules 调整 boundary**（rev line 149）：
   > "Clean coverage is **at or below** three clean candidates, covers **fewer than half the target fund-type slots**, or FOF/index/QDII blockers dominate."

原 review 要求的三项 recommendation 全部落地：3/6 residual 显式声明 ✓、decision boundary 从 `< 3` 改为 `at or below 3` 并增加 `fewer than half` 条件 ✓、index/QDII fallback-blocked 的 next-gate 硬前提已隐含在 stop conditions 和 decision rules 中 ✓。

---

### F2 (MATERIAL) — RESOLVED

Golden coverage 预期未说明问题。

修订后的 plan 做了四处针对性修改：

1. **Candidate Selection Strategy 新增第 6 条**（rev line 35-36）：
   > "Separate golden-covered observations from golden-missing observations. `004393` / 2024 may have current golden coverage; `004194` / 2024 and `006597` / 2024 are expected to produce `year_not_covered` / `FQ0/info`..."

2. **Decision summary 新增 golden 分离要求**（rev line 74）：
   > "Separate `golden_covered` from `golden_missing` / `year_not_covered` rows before classifying extraction gaps."

3. **Stop conditions 新增防误分类条目**（rev line 136）：
   > "`004194` / 2024 or `006597` / 2024 golden-missing `FQ0/info` is misclassified as extraction failure rather than missing golden coverage."

4. **Next gate decision rules 的 golden answer corpus 条件**（rev line 145）新增 "separated golden-covered vs golden-missing rows" 作为进入该 gate 的前提。

原 review 要求的三项 recommendation 全部落地：golden 仅覆盖 004393/2024 已注明 ✓、004194/006597 预期 `year_not_covered` 已注明 ✓、summary 需分组报告已写入 run procedure ✓。

---

### F3 (MINOR) — RESOLVED

7-row vs 8-row 行数不一致问题。

修订后的 plan 统一为 "8-row candidate matrix, covering seven unique fund codes"（rev line 28），并在 Reconciliation（rev line 18）和 Manifest freeze（rev line 55）中一致使用 "eight candidate rows / seven unique fund codes"。

数字不一致已消除 ✓。

---

### F4 (MINOR) — RESOLVED

dev-override judgment 语义未注明问题。

修订后的 plan 在四处补强了 dev-override 语义约束：

1. **Candidate Matrix 004393/2025 行**（rev line 42）：
   > "`--dev-override` smoke must not be interpreted as consuming final-judgment semantics; record only exit, quality gate summary, availability, and report-year scope."

2. **Product smoke / availability probes**（rev line 64）：
   > "For `004393` / 2025, `--dev-override` exists only to keep the probe observable; it must not be used to evaluate final-judgment semantics, report quality, or golden readiness."

3. **Verifier matrix 004393/2025 analyze smoke**（rev line 107）：
   > "Do not interpret dev override as final-judgment semantics."

4. **Verifier matrix 004393/2025 checklist smoke**（rev line 108）：
   > "Do not infer final-judgment semantics or durable readiness."

dev-override 的 judgment 语义隔离已在 plan 中多层次重复强调 ✓。

---

## Scope Drift Check

修订后的 plan 未引入任何超出原 scope 的新内容。检查项：

- [x] Non-Goals 未变更，仍完整覆盖 renderer / FQ0-FQ6 / Service-CLI / Host-Agent-dayu / FundDocumentRepository / extractor / extra_payload / durable baseline / unbounded chains / GitHub mutation。
- [x] 未新增任何要求修改代码、测试、产品行为或工程配置的条目。
- [x] 新增的 `git diff --check` verifier matrix row（rev line 125-126）是对 plan-only artifact closeout 的合理加强，不引入代码变更。
- [x] 新增的 stop condition（rev line 136，golden-missing 误分类防护）是观测层面约束，不扩大 gate scope。
- [x] Reconciliation、Candidate Selection Strategy、Run Procedure 和 Verifier Matrix 的修订均为对 review finding 的响应性补强，不偏离 gate 定位。

---

## Verdict

**PASS**

所有四个 finding（F1 MATERIAL、F2 MATERIAL、F3 MINOR、F4 MINOR）均已解决。修订后的 plan 在 clean coverage transparency、golden coverage 预期、行数一致性和 dev-override 语义隔离四个方面均达到可执行标准。Plan 保持在 gate scope 内，未引入 scope drift。
