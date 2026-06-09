# EID Single Source Operational Hardening Truth-Doc Revision Plan — Targeted Re-Review (MiMo)

## Re-Review Target

`docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`

## Re-Review Date

2026-06-09

## Reviewer

AgentMiMo (targeted re-review)

## Source Evidence Read

- Revised plan: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
- DS review: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-ds-20260609.md`
- MiMo first review: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-mimo-20260609.md`
- Controller judgment: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-controller-judgment-20260609.md`

## Controller-Accepted Required Fixes Check

### Fix 1: control doc EID-not-exclusive / multi-official-url conflict explicit in conflict inventory or slice exact changes

**Verdict: FIXED**

- Conflict inventory table lines 55-56 新增 "Control doc source-truth policy" 行，明确列出当前 control doc 声明 "EID 是 preferred locator 但 not exclusive source truth" 以及 `official_document_url` 可能来自 fund-company/CDN/CNINFO 的冲突。
- Slice 2 exact changes lines 305-307 新增步骤 4（替换 EID-not-exclusive 声明）和步骤 5（替换 multi-official-url 声明），明确要求 rewrite 为 `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`。
- Slice 3 exact changes lines 324-325 新增步骤 4 和 5，要求 startup packet 若镜像旧 control doc 策略则同步替换。

### Fix 2: control doc not_found / unavailable fallback-eligible conflict explicit in conflict inventory or slice exact changes

**Verdict: FIXED**

- Conflict inventory table line 56 新增 "Control doc fallback eligibility" 行，明确列出当前 control doc 声明 `not_found`/`unavailable` remain fallback-eligible 与 `fallback_enabled=false` 的冲突。
- Slice 2 exact changes line 307 新增步骤 6，明确要求替换为 `not_found`/`unavailable` 是 terminal EID source failures，不 authorize fallback。
- Slice 3 exact changes line 325 新增步骤 5，要求 startup packet 同步替换 fallback eligibility 声明。

### Fix 3: Slice 2 和 Slice 3 都有对应 revision targets

**Verdict: FIXED**

- Slice 2 (lines 300-311) 包含 8 个 exact change steps，覆盖 active gate、accepted artifacts、row-shape、EID-not-exclusive、multi-official-url、fallback-eligible、Eastmoney deferred、no-live boundaries。
- Slice 3 (lines 318-328) 包含 6 个 exact change steps，覆盖 gate/status/entry、row-field/row-shape、source-policy paragraph、EID-not-exclusive mirror、fallback-eligible mirror、unauthorized actions。
- 两个 slice 都有明确的 control doc 冲突对应的 revision targets。

### Fix 4: no-live validation matrix 能分别验证每个目标文档中的 selected_source=eid、mode=single_source_only、fallback_enabled=false，不再是 loose OR false-pass

**Verdict: FIXED**

- No-live validation matrix (lines 358-373) 已重写为 per-doc per-value 独立检查：
  - `docs/design.md`: 3 行分别检查 `selected_source=eid`、`mode=single_source_only`、`fallback_enabled=false`
  - `docs/implementation-control.md`: 3 行分别检查，且 expected 描述明确指出 replaces old EID-not-exclusive wording、non-EID routes must be deferred、not_found/unavailable are terminal
  - `docs/current-startup-packet.md`: 3 行分别检查
- 共 9 行精确检查，每个 target doc 的每个 policy value 都有独立 falsifiable 验证。
- Slice 4 consistency checks (lines 338-345) 同步拆分为 3 个独立 rg 命令检查 `selected_source=eid`、`mode=single_source_only`、`fallback_enabled=false`。

### Fix 5: 没有引入新授权（源码、测试、README、live/network/PDF/FDR/fallback、commit/push/PR）

**Verdict: PASS**

- Non-Goals (lines 33-46) 完整保留全部 12 项禁止事项，无新增授权。
- Forbidden Files (lines 244-258) 完整保留，无新增。
- Stop conditions (lines 417-426) 完整保留，无新增。
- Slice 2 stop condition (line 311) 和 Slice 3 stop condition (line 328) 均保留原有边界。

### Fix 6: Eastmoney deferred risk、row-shape queued/paused、current code fact vs accepted target 仍保持

**Verdict: PASS**

- Eastmoney finding disposition (lines 199-209): `deferred-with-owner`，owner 为 future source-candidate gate，不修复代码/不加测试。
- Row-shape residual gate disposition (lines 214-218): "queued / paused by steering"，"not rejected, deleted, or converted"。
- Current code fact vs accepted target separation rules (lines 74-88): 四类标签完整保留，措辞纪律不变。

## Findings

**0 findings.** All controller-accepted required fixes are addressed in the revised plan. No new issues introduced.

## Verdict: PASS

## Acceptance Recommendation

**Accept.**

Revised plan 完整修复了 controller judgment 要求的全部 4 项 required fixes：

1. control doc EID-not-exclusive / multi-official-url 冲突已列入 conflict inventory 和 Slice 2/3 exact changes。
2. control doc not_found / unavailable fallback-eligible 冲突已列入 conflict inventory 和 Slice 2/3 exact changes。
3. Slice 2 和 Slice 3 都有对应的 control doc 冲突 revision targets。
4. No-live validation matrix 已重写为 per-doc per-value 独立 falsifiable 检查（9 行精确 rg）。

原有边界（non-goals、forbidden files、stop conditions）和原有正确性（Eastmoney deferred、row-shape queued/paused、code fact vs target separation）均保持不变。Plan 可进入 truth-doc revision 阶段。
