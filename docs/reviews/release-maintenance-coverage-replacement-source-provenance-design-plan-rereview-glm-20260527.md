# Targeted Re-Review: Coverage Replacement / Source Provenance Design Plan

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-coverage-replacement-source-provenance-design-plan-20260527.md` (revised)
> **Original review**: `docs/reviews/release-maintenance-coverage-replacement-source-provenance-design-plan-review-glm-20260527.md`
> **Verdict**: **PASS**
> **Scope**: Targeted re-review of four revision items only. No new findings.

---

## Verdict: PASS

All three original findings and the追加的 multi-source chain 规则已被修订版充分解决。无需进一步修改。

---

## Finding-by-Finding Disposition

### F1 (medium): `fallback_used=true` + `primary_failure_category` null/unavailable => `unknown_public_metadata_absent`

**Status**: ✅ Resolved.

Contract rules 新增第 4 条（line 82）:

> If `fallback_used=true` and `primary_failure_category` is `null` or unavailable because current metadata does not persist the failure category, `fallback_eligibility` MUST be `unknown_public_metadata_absent`, not `eligible`. This cannot be relaxed except by a later accepted gate that threads `AnnualReportSourceFailure.category` through metadata and public output.

该规则精确覆盖了原始 F1 的诉求：
- 明确了触发条件（`fallback_used=true` + `primary_failure_category` 为 `null` 或 unavailable）
- 锁定了输出值（`unknown_public_metadata_absent`，不是 `eligible`）
- 限制了放宽条件（只能通过后续 accepted gate 把 `AnnualReportSourceFailure.category` 穿透到元数据管线才能解除）

Future Test Scope 第 7 条（line 115）进一步在测试层强化了同一约束：

> Fallback-backed rows with `fallback_used=true` and missing / unavailable `primary_failure_category` classify as `fallback_eligibility="unknown_public_metadata_absent"`, not eligible.

合约规则和测试范围双重锁定，F1 充分解决。

---

### F2 (low): provenance projection ownership

**Status**: ✅ Resolved.

Future Implementation File Scope 新增独立行（line 94）:

> | Agent/Fund provenance projection | Own a pure projection function in `fund_agent/fund` that maps `AnnualReportSourceMetadata` / public repository metadata to additive public provenance fields. This function must be deterministic, side-effect-free, and must not reach into source helpers. |

Service public output 行（line 96）同步修改为消费侧:

> | Service public output | Consume the Agent/Fund projection result and include additive provenance fields in `ExtractionSnapshotService` output and any summary artifact generated from that output. Service must not invert dependencies into source internals or access source helpers. |

归属判定完整：
1. Agent 层 `fund_agent/fund` 拥有纯投影函数（输入 `AnnualReportSourceMetadata`，输出 additive provenance 字段）
2. Service 层 `ExtractionSnapshotService` 消费投影结果，不反向依赖源内部
3. 投影函数约束明确：deterministic、side-effect-free、不接触 source helpers

符合 `AGENTS.md` 归属判定规则。F2 充分解决。

---

### F3 (informational): `not_applicable` consistency test

**Status**: ✅ Resolved.

Future Test Scope 新增第 4 条（line 113）:

> Consistency assertion: rows with `source_provenance_status="not_applicable"` must have `fallback_eligibility="not_applicable"` and `fallback_used=false`.

该断言精确覆盖了 `source_provenance_status` 与 `fallback_eligibility` 在 `not_applicable` 状态下的同步语义。F3 充分解决。

---

### 追加项: multi-source chain selection rule

**Status**: ✅ Resolved.

Contract rules 新增第 6 条（line 84）:

> Multi-source chains must have their `primary_failure_category` selection rule specified in the future implementation gate. If the public output cannot determine the applicable primary failure category for the chain, conservative `unknown_public_metadata_absent` applies.

该规则正确地：
- 将多源链路的具体选择规则推迟到实施 gate（不在此计划 gate 过早决定）
- 设置了保守止损（无法确定时归为 `unknown_public_metadata_absent`）
- 与 F1 的保守语义保持一致

追加项充分解决。

---

## No New Findings

修订版未引入新的 scope 越界、语义矛盾或合约规则冲突。四层边界、fail-closed 语义、AGENTS.md 回退分类法和所有显式非目标保持不变。

---

## Verdict

**PASS**

三个原始 findings 和追加的 multi-source chain 规则全部被修订版精确解决。计划可被接受。
