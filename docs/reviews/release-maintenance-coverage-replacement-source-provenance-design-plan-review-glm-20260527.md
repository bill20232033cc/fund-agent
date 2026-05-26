# Plan Review: Coverage Replacement / Source Provenance Design Plan

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-coverage-replacement-source-provenance-design-plan-20260527.md`
> **Verdict**: **PASS_WITH_FINDINGS**
> **Checkpoint**: `e41c829 docs: accept index qdii recovery evidence`
> **Truth sources checked**: `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, current code (`fund_agent/fund/documents/sources.py`, `fund_agent/fund/documents/models.py`, `fund_agent/fund/data_extractor.py`)

---

## Verdict: PASS_WITH_FINDINGS

Plan reasoning is correct and path selection is sound. Three findings ordered by severity below. No blocking findings.

---

## Finding 1: `primary_failure_category` 字段在现有元数据管线中无数据来源（medium severity）

**Section**: Minimal Public Output Contract — `primary_failure_category`

**Observation**: 计划提出 8 个公共输出字段，其中 `primary_failure_category` 是核心区分字段——它决定 `fallback_eligibility` 是 `eligible` 还是 `fail_closed`，进而决定 fallback-backed 行是否可进入 clean denominator。但代码验证表明：

- `AnnualReportSourceMetadata`（`fund_agent/fund/documents/models.py` L39-53）有 `fallback_used: bool`，但**没有** `failure_category` 或 `primary_failure_category` 字段。
- `AnnualReportSourceFailure`（`fund_agent/fund/documents/sources.py` L127-138）有 `category: AnnualReportSourceFailureCategory`，但该信息仅存在于源编排层异常路径，**未持久化到** `AnnualReportSourceMetadata` 或传播到 `StructuredFundDataBundle`。
- `StructuredFundDataBundle`（`fund_agent/fund/data_extractor.py` L75-114）不携带任何源元数据。

**Impact**: 在不修改源编排层或仓库元数据的前提下，`primary_failure_category` 对所有已有缓存条目和所有未来正常路径抽取都将返回 `null`，`fallback_eligibility` 将返回 `unknown_public_metadata_absent`。这意味着该合约在实施后对 `110020` / `017641` 的分类不会改变——它们仍将保持 `incomplete` / `unknown` 状态，与当前 `unrecoverable_safe_path` 终态等效。

**Assessment**: 这不构成阻塞性问题，因为计划已在 Residual Risks 第一条明确预见此风险：

> "if the current public extraction boundary has no repository metadata object, the implementation gate must stop and redesign the public contract rather than reaching into source helpers."

该止损条款是正确的。但建议在合约规则中增加一条显式约束：

> 对于 `primary_failure_category=null` 且 `fallback_used=true` 的行，`fallback_eligibility` 必须（MUST）分类为 `unknown_public_metadata_absent`，不得（MUST NOT）降级为 `eligible`。

当前合约规则已有 "Conservative by default" 条款，但该条款的措辞未明确覆盖 "元数据存在但 failure_category 缺失" 的场景。增加显式规则可消除歧义。

**Recommendation**: 在 "Contract rules" 中增加一条：

```
- Metadata-present but category-absent: when `fallback_used=true` but `primary_failure_category` is `null` due to the current metadata pipeline not persisting the original failure category, `fallback_eligibility` MUST classify as `unknown_public_metadata_absent`, not `eligible`. This must not be relaxed without a later accepted gate that threads `AnnualReportSourceFailure.category` through the metadata pipeline.
```

---

## Finding 2: 实施文件范围缺少具体的 provenance 投影代码归属判定（low severity）

**Section**: Future Implementation File Scope

**Observation**: 计划列出五个实施区域（Agent/Fund public model, Document repository metadata consumption, Service public output, Score compatibility, README sync），但未指定 provenance 投影逻辑的具体文件归属。对照 `AGENTS.md` 归属判定规则：

- "读取 prompt manifests / scene 定义" → `Service`
- "管理 tool loop / runner / trace" → `Agent`
- "理解基金类型、财报章节、投资规则" → `Agent` 层 `fund_agent/fund`

Provenance 投影需要从 `AnnualReportSourceMetadata`（Agent 层 documents）读取元数据、映射到公共字段、附加到 `ExtractionSnapshotService` 输出（Service 层）。这条跨层路径需要归属判定：

1. **读取仓库元数据** → Agent 层 `fund_agent/fund/documents/` 内部
2. **映射到公共 provenance 字段** → 应归属 Agent 层 `fund_agent/fund/`（基金领域模型投影）
3. **附加到 Service 公共输出** → 应归属 Service 层 `ExtractionSnapshotService`

**Assessment**: 当前计划的 "Agent/Fund public model" 和 "Service public output" 区域描述基本正确，但缺少投影函数的归属判定和依赖方向。实施 gate 需要在此明确：Agent 层提供 `SourceProvenanceProjection` 纯函数（输入 `AnnualReportSourceMetadata`，输出公共 provenance 字段），Service 层调用该投影并将结果附加到 snapshot 输出。

**Recommendation**: 在实施文件范围中增加一行：

```
| Provenance projection function | Agent 层 `fund_agent/fund/` 新增纯投影函数；输入 `AnnualReportSourceMetadata`，输出 additive public provenance 字段；不修改 `FundDocumentRepository`、源编排或 fallback 决策 |
```

---

## Finding 3: 合约字段 `source_provenance_status` 的 `not_applicable` 语义与 `fallback_eligibility` 的 `not_applicable` 语义重叠但触发条件不同（informational）

**Section**: Minimal Public Output Contract — `source_provenance_status` and `fallback_eligibility`

**Observation**: `source_provenance_status` 的 `not_applicable` 用于 "no-fallback primary success path"（即 `fallback_used=false` 且无 primary failure）。`fallback_eligibility` 的 `not_applicable` 用于同一场景。两者语义一致，但合约规则未明确说明当 `source_provenance_status=not_applicable` 时 `fallback_eligibility` 必须（MUST）同步为 `not_applicable`。

这不会导致实施错误（逻辑上必然同步），但测试范围应包含该一致性断言。

**Recommendation**: 在 Future Test Scope 中增加：

```
- `source_provenance_status=not_applicable` rows must have `fallback_eligibility=not_applicable` and `fallback_used=false`.
```

---

## Review Focus Checklist

| Focus area | Assessment |
|---|---|
| Prefer additive provenance over replacement selection given no approved candidates | **Correct.** No approved candidates exist; replacement is `not_run_no_approved_candidates`. Additive provenance is the shortest safe path. |
| Avoid unsafe inference from successful CLI extraction to fallback eligibility | **Correct.** Plan explicitly rejects "run succeeded = fallback was allowed" inference: "A successful later extraction is only indirect evidence that a document was obtained; it is not direct evidence that the fallback was allowed." This preserves AGENTS.md fail-closed semantics. |
| Preserve FundDocumentRepository source strategy and fail-closed categories | **Correct with Finding 1 caveat.** Plan explicitly preserves `schema_drift / identity_mismatch / integrity_error` as non-eligible and does not modify source strategy. Finding 1 notes `primary_failure_category` data is not currently available in metadata. |
| Keep renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, golden/baseline fixtures out of scope | **Correct.** All listed in Explicit non-scope. No violations found. |
| Minimal output contract breadth | **Appropriate.** 8 fields cover identity, fallback state, category, eligibility, and status. Finding 3 notes minor semantic overlap. Finding 1 notes `primary_failure_category` will be `null` initially. |
| Future implementation file/test scopes code-generation readiness | **Adequate with Finding 2 refinement.** File areas and test cases are described at a sufficient level for a planning gate, but exact file paths and cross-layer dependency direction need clarification at implementation gate. |

---

## Gate Boundary Compliance

| Constraint | Status |
|---|---|
| No code, tests, extraction evidence | ✅ Plan is planning-only |
| No `docs/design.md` update | ✅ Not modified |
| No `docs/implementation-control.md` update | ✅ Not modified |
| No commit, push, PR | ✅ Not attempted |
| No renderer / FQ0-FQ6 changes | ✅ Explicitly out of scope |
| No Host/Agent/dayu changes | ✅ Explicitly out of scope |
| No golden/baseline fixture promotion | ✅ Explicitly prohibited |
| No direct PDF/cache/source-helper access | ✅ Prohibited |
| No ad hoc web/search for replacements | ✅ Prohibited |
| Four-layer boundary preserved | ✅ Provenance projection follows Agent → Service dependency direction |
| Fail-closed source semantics preserved | ✅ Finding 1 confirms conservative-by-default stance |
| AGENTS.md fallback taxonomy respected | ✅ `schema_drift / identity_mismatch / integrity_error` remain non-eligible |

---

## Findings Summary

| # | Severity | Finding | Recommendation |
|---|---|---|---|
| F1 | medium | `primary_failure_category` 无现有数据来源；对 fallback-backed 行将全部返回 `unknown` | 增加显式合约规则：`fallback_used=true` + `primary_failure_category=null` → `fallback_eligibility=unknown_public_metadata_absent` |
| F2 | low | 实施文件范围缺少 provenance 投影函数的跨层归属判定 | 增加一行指定 Agent 层纯投影函数 + Service 层消费 |
| F3 | informational | `source_provenance_status` 与 `fallback_eligibility` 的 `not_applicable` 语义需测试同步 | 测试范围增加一致性断言 |

---

## Verdict

**PASS_WITH_FINDINGS**

路径选择正确，第一性原理推理无误，fail-closed 语义得到完整保留，scope 边界无越界。三个 findings 均可在实施 gate 中解决，不阻碍本计划被接受。
