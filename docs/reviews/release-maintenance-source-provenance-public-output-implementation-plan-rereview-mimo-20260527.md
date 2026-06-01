# Source Provenance Public Output Implementation Plan Re-Review — MiMo

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Target: revised `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-20260527.md`
> Original review: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-review-mimo-20260527.md`
> Verdict: **PASS**

---

## Targeted Review Items

### 1. StructuredFundDataBundle safe NOT_APPLICABLE default factory

**RESOLVED**。

Plan step 2 明确采用 `field(default_factory=default_public_source_provenance)` 策略（line 118），新增 `default_public_source_provenance()` 函数（line 102）。生产路径 `FundDataExtractor.extract()` 必须显式传入 projection（line 119-120），default factory 仅服务于测试和非 provenance 构造场景（line 122）。Stop condition 新增第四条（line 302）覆盖 default factory 无法干净实现的情况。Risk matrix 中 fixture churn 风险从 MEDIUM 降为 LOW（line 288）。Data extractor test plan 新增 "Constructing without explicit provenance yields safe NOT_APPLICABLE default, never None"（line 216）。

比原 review F1 建议的 `None` default 更好——frozen dataclass + NOT_APPLICABLE default 比 nullable 更安全，不会隐藏 fallback-backed unknowns。

### 2. Summary exact Source Provenance section/table format and failed-fund note

**RESOLVED**。

Plan step 3 明确指定 `## Source Provenance` section（line 148），exact columns：`fund_code`, `resolved_source_name`, `fallback_used`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`（line 150）。Not-applicable 行的确定性输出值已列出（line 152）。Failed funds without snapshot records 在 v1 中 omitted，且 section 必须包含 out-of-scope note（line 152）。Snapshot test plan 新增两条 explicit assertions（lines 227-229）。

### 3. SnapshotRecord default/population and legacy JSONL compatibility

**RESOLVED**。

Plan step 3 明确 `SnapshotRecord` 可定义 NOT_APPLICABLE-compatible defaults（line 145），但生产路径必须通过 `build_snapshot_records()` / `_snapshot_record()` fully populated（line 145-146）。Legacy JSONL compatibility 由 downstream score readers ignoring extra keys 处理，不依赖 nullable bundle provenance（line 147）。Snapshot test plan 新增 "dataclass defaults, if present, are only NOT_APPLICABLE-compatible safety defaults" assertion（line 225）。

### 4. Deterministic score.json key set / FQ0-FQ6 gate-sensitive no-change tests

**RESOLVED**。

原 review F2 的 "if unchanged" 歧义已消除。Plan step 4 改为 "Score-compatible means deterministic no-change for `score.json` key set and all FQ0-FQ6 gate-sensitive output"（line 163），并要求 "Add explicit assertions comparing the `score.json` top-level keys and gate-consumed fields before/after"（line 163）。Score compatibility test plan 新增两条确定性断言（lines 236-237），覆盖 `field_scores`, `fund_scores`, `fund_quality`, `field_applicability_decisions`, `score_applicability_issues`, `failed_funds`, `golden_set`, `correctness` 语义。Risk matrix 新增 `score.json shape changes accidentally` 为 HIGH 风险（line 290）。

### 5. SourceStrategy single v1 value clarification

**RESOLVED**。

Plan step 1 新增段落（line 96）："SourceStrategy intentionally has a single Literal value in v1. It documents the current public strategy label without opening a policy surface for source ordering, fallback qualification, or repository behavior." 消除了多值 Literal 暗示未来扩展的歧义。

---

## Residual Observations

无阻塞项。原 review 的 F3（snapshot identical provenance assertion）在 revised plan line 224 保留。F4（INFO, code-generation-ready）不变。

---

## Summary

所有 5 个 targeted review items 均已 resolved。Revised plan 在 default factory 策略上优于原 review 建议（NOT_APPLICABLE default > None default），score.json 和 FQ0-FQ6 断言从模糊变为确定性，summary format 和 SourceStrategy 语义明确。

**Verdict: PASS**。
