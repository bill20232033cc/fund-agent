# Runtime/Engine Boundary Decision Plan Review (DS) — 2026-05-23

## Verdict: PASS-WITH-RISKS

No blockers. Material findings below are owned by Slice 1 docs-only alignment or are residual risks already acknowledged by the plan.

---

## 1. Evidence Verification

### 1.1 Defer decision — direct multi-source support

The plan recommends NOT creating `fund_agent/runtime` / `fund_agent/engine` placeholder packages. This is supported by four independent authoritative sources:

| Source | Specific Reference | What It Says |
|--------|-------------------|--------------|
| `docs/design.md` | §2.2 line 113 | "在没有明确 session/run/tool-loop 需求前，不应空造 Runtime 或 Engine 包" |
| `docs/design.md` | §2.1 line 69 | "当前尚未创建 `fund_agent/runtime` 或 `fund_agent/engine` 通用执行包" |
| `docs/implementation-control.md` | Open residuals (line 118) | "current remaining boundary debt: Runtime/Engine packages are not yet implemented" |
| `docs/implementation-control.md` | release-maintenance 候选表 (line 167) | "未选中具体 runner/tool-loop 需求前不得空造复杂框架" |
| `fund_agent/README.md` | 当前包边界 | Lists only `ui`, `application`, `services`, `fund`, `config` — no runtime/engine |
| Filesystem | `ls fund_agent/` | Confirmed ABSENT: no `runtime/` or `engine/` directories exist |

**Finding**: The defer recommendation is not speculative — it restates a design decision already recorded in design.md §2.2 and implementation-control.md. The plan adds value by formalizing trigger conditions and scoping the docs-only alignment.

### 1.2 Boundary debt ownership — addressed, not abandoned

The plan's future trigger conditions (§3) define five concrete gates before Runtime/Engine packages may be created:

1. Session/run lifecycle (concurrency, timeout, cancel, resume, memory, reply outbox, event delivery)
2. Scene registry / system_prompt rendering / prompt manifest / tool binding
3. Tool loop / runner / ToolRegistry / ToolTrace / context budget / tool execution state machine
4. LLM audit / Evidence Confirm / Agent analysis / async execution path
5. Each trigger requires a standalone plan-review artifact with typed contracts, dependency direction, failure semantics, event flow, test strategy, and README sync

These conditions are specific enough that an implementation worker could assess whether a given requirement meets the bar. The boundary debt remains tracked in implementation-control.md open residuals and the plan proposes making the defer explicit in three docs rather than leaving it implicit.

**Challenge conclusion**: The concern that deferring placeholder packages "leaves boundary debt without an owner" is not supported by the evidence. The debt has an owner (implementation-control.md open residuals), has defined trigger conditions, and is gated behind plan-review.

---

## 2. Material Findings

### M1: design.md §9 shows non-existent runtime/engine directories

**Evidence**: `docs/design.md` lines 698–699:
```
│   ├── runtime/                         # Runtime 层（目标包；当前未接入 Agent runtime）
│   ├── engine/                          # Engine 层（目标包；当前未接入通用工具执行框架）
```

Filesystem check confirms both directories are ABSENT. The annotations say "(目标包；当前未接入)" but the visual presentation — two entries in a directory tree that otherwise reflects actual on-disk layout — is misleading. A reader scanning the tree sees `runtime/` and `engine/` alongside real directories like `ui/`, `services/`, `fund/` and may conclude they exist.

**Severity**: Medium. Not a blocker for the plan itself, but Slice 1 docs-only alignment should explicitly address this. Options: remove the entries from the tree, or add a clear boundary line in the tree separating "current" from "future/target" directories.

**Recommendation**: Slice 1 should add a demarcation in the §9 tree (e.g., a comment line `# --- 以下为目标包，当前未创建 ---`) or remove the entries and document the target packages in prose only.

### M2: AGENTS.md conflict is a material residual risk

**Evidence**: The current on-disk `AGENTS.md` (line 56, 68–69, 88–89, 93–94) mandates:
- Four-layer boundary: `UI -> Service -> Host -> Agent`
- "Host 层实现必须使用 `dayu.host`"
- "Agent 执行内核必须使用 `dayu.engine`"

This directly contradicts the six-layer boundary (`UI / Application / Runtime / Service / Engine / Capability`) and the no-external-Dayu-runtime rule that the plan and all other authoritative documents follow.

The user has stated "本地 AGENTS.md 有未接受冲突改动，不要以它为准，不要修改它." The plan correctly excludes AGENTS.md from modification scope (§5 Non-Scope). The plan's risk table (§10) acknowledges this as risk #6.

**Severity**: High (acknowledged residual). The AGENTS.md is the declared "唯一权威入口" per CLAUDE.md. Any future worker who reads AGENTS.md without the user's oral override would conclude the boundary is 4-layer with mandatory dayu.host/dayu.engine. The plan's risk mitigation ("不读取为真源、不修改、不暂存；需要用户显式决策") is correct but depends entirely on human discipline — there is no automated guard preventing misreading.

**Recommendation**: No action in this plan scope. The user must explicitly resolve the AGENTS.md conflict before any Runtime/Engine implementation gate. The plan review checklist (§9) correctly flags this.

### M3: Slice 1 docs-only alignment — underspecified scope for design.md §9

**Evidence**: Slice 1 (§6) says to update `docs/design.md` to "保留六层目标边界，同时明确 Runtime/Engine 是 future concrete capability boundary，不以空包表示当前完成状态." It does not specify:
- Whether the §9 tree should remove `runtime/` / `engine/` entries
- Whether to add a visual boundary between current and target packages
- Whether the §2.1 table rows for Runtime/Engine should be marked more prominently as "未实现"

**Severity**: Low. The intent is clear. An implementation worker could infer the right changes from context. But the plan would be stronger with explicit §9 tree handling.

**Recommendation**: Accept as-is; the implementation worker should note M1 above and fix the §9 tree presentation during Slice 1.

### M4: Slice 2 validation commands use placeholders

**Evidence**: Slice 2 (§6) validation commands:
```bash
uv run pytest <boundary-test-file> -q
git diff --check <touched-files>
```
`<boundary-test-file>` and `<touched-files>` are not concrete. This is acceptable because Slice 2 is explicitly optional ("仅在 reviewer 明确要求后执行") and the actual test file would be determined at implementation time. Not a blocker.

**Severity**: Info. Acceptable for an optional slice.

---

## 3. Constraint Compliance Audit

### 3.1 Six-layer boundary

| Check | Status | Evidence |
|-------|--------|----------|
| Boundary is `UI / Application / Runtime / Service / Engine / Capability` | PASS | Plan §1 references six layers; plan review checklist §9 first item checks this; design.md v2.2 uses six layers |
| Current production path is `UI -> Application -> Service -> Capability` | PASS | Plan §3 explicitly states this; verified against design.md §2.1 and fund_agent/README.md |
| Runtime/Engine are recognized as target boundaries, not denied | PASS | Plan §3: "defer 不是否认六层边界，而是承认 Runtime / Engine 必须由真实运行时需求触发" |

### 3.2 Dayu reference / no runtime dependency

| Check | Status | Evidence |
|-------|--------|----------|
| Dayu is methodology/history/engineering reference only | PASS | Plan §1 references design.md Dayu 裁决; Non-Scope §5 explicitly excludes external dayu-agent |
| No external Dayu Host/Engine/tool loop in production path | PASS | Plan §3: current path has no Runtime/Engine; §5 Non-Scope explicitly forbids |
| Future Runtime/Engine must be project-internal | PASS | Plan §3 trigger condition #5: "证明不是外部 Dayu runtime 包装" |

### 3.3 Explicit-parameter / no-extra-payload

| Check | Status | Evidence |
|-------|--------|----------|
| Future scene/tool/audit params must be typed | PASS | Plan review checklist §9 item 4 checks this |
| No `extra_payload` for business parameters | PASS | Plan §6 Slice 2: "不把未来参数放进 `extra_payload` 或自由 dict" |

### 3.4 FundDocumentRepository boundary

| Check | Status | Evidence |
|-------|--------|----------|
| Production annual report access only through FundDocumentRepository | PASS | Plan §5 Non-Scope: "不改变年报访问路径；生产年报访问仍必须经过 FundDocumentRepository"; risk table row 5 covers this |
| Service/UI/future Runtime/Engine must not directly read PDF/cache/sources | PASS | Implicit in FundDocumentRepository boundary preservation |

### 3.5 Docs sync

| Check | Status | Evidence |
|-------|--------|----------|
| Slice 1 only updates current facts + defer decision | PASS | Plan §6 Slice 1 内容要求 specifies what to write |
| Does not mark future Runtime/Engine as implemented | PASS | Plan §6 Slice 1: "不以空包表示当前完成状态" |

### 3.6 Scope control

| Check | Status | Evidence |
|-------|--------|----------|
| No production code changes | PASS | Plan §5 Non-Scope |
| No test changes | PASS | Plan §5 Non-Scope |
| No AGENTS.md modification | PASS | Plan §5 Non-Scope |
| No commit/push/PR | PASS | Plan §5 Non-Scope |

---

## 4. Sequencing and Implementation Readiness

### 4.1 Can an implementation/docs worker execute Slice 1 from this plan alone?

**Assessment**: Yes, with one caveat (M1 above).

The plan specifies:
- Which files to touch: `docs/design.md`, `docs/implementation-control.md`, `fund_agent/README.md`
- What content to add: defer decision, trigger conditions, intentional absence of runtime/engine
- Validation commands: specific `rg` patterns and `git diff --check`

The worker would need to infer the exact placement of new text within each file, but the semantic intent is clear enough. The M1 finding (design.md §9 tree) is the only ambiguity — the worker should know to fix or annotate the non-existent directory entries.

### 4.2 Is Slice 0 self-contained?

Yes. The plan produces only itself (`docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-20260523.md`). No code or doc changes are made in Slice 0.

### 4.3 Is Slice 1 gated correctly?

Yes. Slice 1 only executes after plan review acceptance. This is appropriate.

---

## 5. Residual Risks (Plan §10) — Second Opinion

The plan's own risk table is comprehensive. Additional observations:

| Risk | Plan's Handling | Reviewer Assessment |
|------|----------------|---------------------|
| Runtime/Engine placeholder impulse returns | Plan-review checklist gate | Adequate. The checklist + trigger conditions create friction against premature creation |
| README 4-layer vs design 6-layer misread | Docs-only alignment clarification | Adequate, but see M2 — the root cause is AGENTS.md conflict, not README ambiguity |
| External Dayu runtime re-wrapped into main path | Dayu no-runtime-dependency checklist | Adequate as a checklist item; consider a programmatic import guard in Slice 2 |
| LLM audit/Evidence Confirm suddenly needed | Standalone design + plan-review gate | Adequate |
| Annual report access bypassed via Runtime/Engine excuse | FundDocumentRepository boundary preservation | Adequate; risk table explicitly covers this |
| AGENTS.md conflict diff accidentally included | Explicit exclusion + "需要用户显式决策" | Correct approach but see M2 — this is the highest residual risk |

---

## 6. Summary

| Dimension | Verdict |
|-----------|---------|
| Defer decision evidence | PASS — direct, multi-source support from design.md, implementation-control.md, README, and filesystem |
| Boundary debt ownership | PASS — trigger conditions are specific, debt is tracked in implementation-control.md, future creation is gated |
| Six-layer boundary compliance | PASS |
| Dayu no-runtime-dependency | PASS |
| explicit-parameter / no-extra-payload | PASS |
| FundDocumentRepository boundary | PASS |
| Docs sync | PASS-WITH-FINDING — M1 (design.md §9 tree) needs attention in Slice 1 |
| Scope control | PASS |
| Sequencing | PASS |
| Acceptance criteria | PASS — clear, specific, verifiable |
| Validation commands | PASS — Slice 0/1 commands are concrete; Slice 2 placeholders are acceptable for optional slice |
| Implementation worker readiness | PASS — Slice 1 is sufficiently specified; M1 is the only execution ambiguity |

**Overall: PASS-WITH-RISKS. No blockers.**

Material findings M1–M4 should be addressed during Slice 1 execution. M2 (AGENTS.md conflict) is an acknowledged residual that requires explicit user decision before any future Runtime/Engine implementation gate — not a defect of this plan.
