# EID Single Source Operational Hardening Truth-Doc Revision Plan Review — MiMo

## Review Target

`docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`

## Review Date

2026-06-09

## Reviewer

AgentMiMo (plan review worker)

## Source Evidence Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/repo-review-20260609-165959.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-steering-judgment-20260609.md`
- 被审 plan

## Review Scope Checklist

| # | Scope Item | Status | Finding |
|---|---|---|---|
| 1 | Single source: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false` | PASS | Plan lines 65-68, 93-98 明确写出三项策略值 |
| 2 | No multi-source fallback / Eastmoney production fallback / 基金公司官网 adapter 当前生产路径 | PASS | Plan line 39-40 禁止 Eastmoney/fund-company-site production fallback；line 100-106 forbidden wording 列表完整 |
| 3 | FundDocumentRepository 单入口保留，UI/Service/Host/renderer/quality gate 不直接调用 source/downloader/cache/parser | PASS | Plan line 185 明确保持边界；Slice 1 step 2 (line 279) 保留 FDR boundary |
| 4 | 严格区分当前代码事实 vs accepted gate target，不把 EID single source 写成已实现 | PASS | Plan lines 76-87 定义四类标签并强制措辞纪律；line 100 禁止 "EID single source is implemented" |
| 5 | 不把 repo-review Eastmoney finding 转成当前 implementation scope drift | PASS | Plan lines 189-199 将 Eastmoney finding 标为 `deferred-with-owner`，不修复代码、不加测试 |
| 6 | Row-shape residual gate queued / paused by steering | PASS | Plan lines 202-209 明确 "queued / paused by steering"，不 rejected/deleted |
| 7 | no-live/no-FDR/no-fallback/no-source-code/no-tests/no-commit/no-PR 边界完整 | PASS | Plan lines 33-47 Non-Goals 完整覆盖；lines 233-248 Forbidden Files 列表完整 |
| 8 | no-live validation matrix 足够检查 EID policy、no fallback wording、FDR boundary、dayu runtime 和 extra_payload 禁令 | PASS | Plan lines 337-344 覆盖全部五项：EID policy rg、no fallback rg、row-shape rg、boundary rg (含 FDR/extra_payload/dayu)、formatting diff |

## Findings

### [F1] No-Live Validation Matrix — Boundary Check 可更显式

**Severity**: INFO
**Location**: Plan lines 342-343
**Description**: Boundary retained 检查项的 rg pattern `FundDocumentRepository|extra_payload|dayu-agent|dayu.host|dayu.engine` 能覆盖 FDR boundary、extra_payload 禁令和 dayu runtime 禁令，但这三项合并为一个检查行。若 revision worker 执行该 rg 时只命中 FDR 而遗漏 dayu/extra_payload，可能误判为 PASS。
**Recommendation**: 建议拆为两行独立检查：(a) FDR boundary；(b) dayu runtime + extra_payload prohibition。当前合并行在实际执行中仍可工作（rg 输出会显示所有命中行），不构成阻断。

### [F2] Revision Slice 4 — Consistency Check 未显式列出 dayu/extra_payload 验证步骤

**Severity**: INFO
**Location**: Plan lines 319-333 (Slice 4 Exact checks)
**Description**: Slice 4 的 Exact checks 第 3 步已包含 `rg -n "FundDocumentRepository|extra_payload|dayu-agent|dayu.host|dayu.engine"`，覆盖了 dayu/extra_payload 检查。但 Expected result 段落（lines 329-333）只提到了 "no dayu runtime or extra_payload authorization is introduced"，与 No-Live Validation Matrix 的 Expected 保持一致。无遗漏。

### [F3] EID Operational Topics — Identity / Metadata / Parsed Cache 细节充分

**Severity**: INFO
**Location**: Plan lines 173-186
**Description**: EID Operational Topics 表覆盖 discovery、identity、PDF integrity、metadata、repository cache、parsed cache、failure reporting、boundary 共 8 项，每项都有 Required doc stance。与 steering judgment 中的 source policy target 对齐，无遗漏。

### [F4] Direct Evidence Matrix 完整性

**Severity**: INFO
**Location**: Plan lines 354-361
**Description**: Direct Evidence Matrix 覆盖全部 6 个必读文件，每条 evidence 都标注了 direct fact used 和 plan consequence。与 review scope 要求的 "direct evidence mapping" 一致。

## Findings Summary

| ID | Severity | Classification | Description |
|---|---|---|---|
| F1 | INFO | NON-BLOCKING | Validation matrix boundary check 可拆分为更显式的独立行 |
| F2 | INFO | NON-BLOCKING | Slice 4 consistency check 与 validation matrix 一致，无遗漏 |
| F3 | INFO | NON-BLOCKING | EID operational topics 覆盖完整 |
| F4 | INFO | NON-BLOCKING | Direct evidence matrix 完整 |

**Blocking findings: 0**

## Verdict: PASS

Plan 通过 review scope 全部 8 项检查。无 blocking findings。

## Acceptance Recommendation

**Accept.**

Plan 完整覆盖了 steering judgment 要求的 EID single-source policy 目标，正确区分了当前代码事实与 accepted gate target，保留了 row-shape residual gate queued/paused 状态，Eastmoney finding 正确标为 deferred-with-owner，non-goals 和 forbidden files 边界完整，no-live validation matrix 可执行且覆盖所有要求的检查维度。所有 findings 均为 INFO 级别，不构成阻断。
