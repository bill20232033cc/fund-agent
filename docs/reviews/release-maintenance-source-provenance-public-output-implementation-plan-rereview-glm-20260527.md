# Source Provenance Public Output Implementation Plan Re-Review (GLM)

> **Date**: 2026-05-27
> **Reviewer role**: AgentGLM independent plan re-review
> **Review target**: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-20260527.md` (revised)
> **Original review**: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-review-glm-20260527.md`
> **Scope**: targeted re-review — only check whether revised plan resolves F1–F4 plus score.json/FQ0 compatibility
> **Verdict**: **PASS**

---

## Finding Resolution Status

### F1 [HIGH] → RESOLVED

**Original finding**: `StructuredFundDataBundle` 新增 required field 实际影响 7 个测试文件+12 处 `replace()`，计划仅列出 3-4 个。

**Revised plan response**:

1. 新增 `default_public_source_provenance()` 函数声明（line 102）
2. 明确使用 `field(default_factory=default_public_source_provenance)` 而非 required field（line 118）
3. 生产代码 `FundDataExtractor.extract()` 必须显式从 `report.metadata.source` 计算并覆盖默认值（line 120）
4. "Update only provenance-focused fake bundle builders to pass explicit provenance. Other fixtures should rely on the safe default rather than broad constructor edits."（line 122）
5. 新增 stop condition：若 default-factory 无法干净实现、需要暴露 `None`、或改变现有 fixture 行为则停下（line 302）
6. Risk matrix 降级为 Low（line 288）
7. 测试计划新增断言："Constructing `StructuredFundDataBundle` without explicit provenance yields the safe `NOT_APPLICABLE` default object, never `None`"（line 216）

**Resolution assessment**: 完全采纳了推荐方案 A。`NOT_APPLICABLE` 默认值消除了 fixture churn，不引入 `None` 语义，生产路径始终显式覆盖。7 个不关心 provenance 的测试文件无需修改。

---

### F2 [MEDIUM] → RESOLVED

**Original finding**: Summary provenance 输出格式未具体化。

**Revised plan response**:

1. 精确定义为独立的 `## Source Provenance` section（line 149）
2. 精确列顺序：`fund_code`, `resolved_source_name`, `fallback_used`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`（line 150）
3. not-applicable 行的精确显示：`resolved_source_name=null`, `fallback_used=false`, `fallback_eligibility=not_applicable`, `source_provenance_status=not_applicable`（line 152）
4. 聚合策略：取 succeeded fund 的第一条 snapshot record（line 152）
5. Failed fund 处理：v1 中省略，附 out-of-scope 说明（lines 152-153）
6. 测试计划同步覆盖所有格式断言（lines 227-229）

**Resolution assessment**: 格式完全具体化，实施者无需在代码中做格式决策。

---

### F3 [MEDIUM] → RESOLVED

**Original finding**: SnapshotRecord 8 个新增字段的默认值策略和 legacy JSONL 兼容方式未明确。

**Revised plan response**:

1. SnapshotRecord 允许 `NOT_APPLICABLE`-compatible defaults 作为安全兜底，但生产路径必须通过 `build_snapshot_records()` / `_snapshot_record()` 完整填充（line 145）
2. Legacy JSONL 兼容性由 score reader 忽略 extra keys + 容忍缺失 provenance keys 实现，不通过 bundle 层 nullable 处理（line 147）
3. 测试计划明确断言生产路径完全填充，dataclass defaults 仅作为安全兜底（line 225）

**Resolution assessment**: 策略清晰——生产路径保证完整填充，dataclass defaults 只是防御性兜底，legacy 兼容在消费侧处理。

---

### F4 [LOW] → RESOLVED

**Original finding**: `SourceStrategy = Literal["primary_then_fallback"]` 单值需说明。

**Revised plan response**:

> `SourceStrategy` intentionally has a single Literal value in v1. It documents the current public strategy label without opening a policy surface for source ordering, fallback qualification, or repository behavior.（line 96）

**Resolution assessment**: 明确说明 intentionally single-valued，并解释了不开放策略面的原因。

---

### score.json key set / FQ0-FQ6 gate-sensitive no-change

**Revised plan response**:

1. 新增 "Score-compatible means deterministic no-change for `score.json` key set and all FQ0-FQ6 gate-sensitive output"（line 163）
2. 要求 "explicit assertions comparing the `score.json` top-level keys and gate-consumed fields before/after additive snapshot provenance"（line 163）
3. 测试计划逐项列出不受影响的 score.json sections：`field_scores`, `fund_scores`, `fund_quality`, `field_applicability_decisions`, `score_applicability_issues`, `failed_funds`, `golden_set`, `correctness`（line 237）
4. Risk matrix 新增 "score.json shape changes accidentally" 高风险项，附带断言缓解措施（line 290）
5. Stop condition 新增 score.json 变更触发停止（line 304）

**Resolution assessment**: score 兼容性从模糊的 "should not change" 升级为枚举式断言和 stop condition。

---

## New Issue Check

审查修订计划是否引入新问题：

- `default_public_source_provenance()` 作为 frozen dataclass 的 default_factory：技术上可行，因为 `PublicSourceProvenance` 是 `frozen=True, slots=True` dataclass，不可变实例可安全作为共享默认值。`default_factory=lambda: _NOT_APPLICABLE_PROVENANCE` 在每次构造时返回同一个不可变对象，语义正确。
- Summary `## Source Provenance` 作为新 section 而非 Fund Results 表的扩展列：这是更好的设计，不干扰现有 Fund Results 表结构，降低格式回归风险。
- Failed fund out-of-scope note：合理，v1 不处理无 snapshot record 的 failed fund provenance，避免引入 error-record 模式扩展。

无新问题。

---

## Verdict

**PASS** — 全部 4 项原始发现（F1 HIGH / F2 MEDIUM / F3 MEDIUM / F4 LOW）及 score.json/FQ0 兼容性要求均已解决。修订计划已采纳推荐的 `NOT_APPLICABLE` default-factory 方案，补全了 summary 精确格式、SnapshotRecord 默认值策略、score.json 逐项断言和 SourceStrategy 单值说明。未发现新问题。计划具备 code-generation-ready 的实施条件。
