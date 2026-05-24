# Runtime/Engine Docs Alignment Review (DS) — 2026-05-23

## Scope

Slice 1 docs-only alignment after accepted Runtime/Engine boundary decision plan. Review target: `docs/design.md`, `docs/implementation-control.md`, `fund_agent/README.md`, plus four plan/review artifacts.

## Verdict: PASS

No material findings. All five review focus areas are satisfied with direct evidence. No blockers. No production code, tests, root README, or AGENTS.md were touched. No `fund_agent/runtime` or `fund_agent/engine` were created.

---

## 1. design.md §9 — Tree No Longer Fakes On-Disk Runtime/Engine

**Before**: §9 directory tree showed `│   ├── runtime/` and `│   ├── engine/` as if they existed alongside real directories.

**After**: Both entries removed from the tree. A prose paragraph added after the tree:

> Runtime / Engine 是目标边界，不是当前磁盘目录事实。当前生产路径故意保持为 UI → Application → Service → Fund Capability；在没有真实 session/run/cancel/resume/outbox、scene registry、tool loop、runner、ToolRegistry、ToolTrace 或 context budget 需求前，不创建 Runtime 或 Engine 占位包。

**Evidence**: `git diff HEAD -- docs/design.md` lines 695–811 show deletion of the two `runtime/` / `engine/` tree entries and addition of the prose paragraph. `ls fund_agent/` confirms only `application/ config/ fund/ services/ ui/` exist.

**Finding**: This directly addresses DS plan-review finding M1 and GLM M1 — the §9 tree now reflects filesystem facts. The intent (target boundaries, not placeholder packages) is preserved in prose. ✅

## 2. README — Current Path vs Target Boundary Clearly Separated

**Before**: "确定性四层架构" — ambiguous wording that could be read as endorsing four-layer as the architecture.

**After**:
- "当前生产路径是确定性 CLI 管线" — avoids implying 4-layer = architecture
- Explicit: "目标架构边界仍是 UI / Application / Runtime / Service / Engine / Capability 六层"
- Explicit: "当前没有 Runtime 或 Engine 通用包是有意 defer，不是遗漏"
- Concrete trigger conditions listed (session/run/cancel/resume/outbox, scene registry, tool loop, etc.)
- Stable boundaries section updated: config description changed from "Host/Engine" → "Runtime/Engine"
- New bullet: "Runtime / Engine 是目标边界；当前不创建 runtime / engine 占位目录，后续必须由具体需求 gate 驱动"
- Dayu paragraph tightened: "Dayu 只作为工程纪律和设计参考"

**Evidence**: `git diff HEAD -- fund_agent/README.md` confirms all above changes. The README now makes `absence ≠ omission` explicit. ✅

## 3. implementation-control — Accurate Artifact/Gate/Entry-Point Records

| Check | Status | Evidence |
|---|---|---|
| Current gate updated | ✅ | `release maintenance Runtime/Engine boundary decision accepted; Slice 1 docs alignment pending review` |
| Next entry point correct | ✅ | `Runtime/Engine docs alignment review/acceptance or push authorization` |
| Latest artifacts row added | ✅ | Row 45: four Runtime/Engine boundary decision artifacts listed |
| Product baseline updated | ✅ | Row 117: includes "Runtime/Engine boundary decision accepted, Slice 1 docs alignment completed locally and pending review/acceptance" |
| Resume checklist updated | ✅ | Row 122: references controller judgment artifact and four gate constraints |
| New acceptance row | ✅ | Row 420: full scope/non-scope recorded; explicitly forbids production code, tests, AGENTS.md, commit/push/PR, Runtime/Engine package creation |
| Defer NOT written as done | ✅ | Row 420 status is "accepted; Slice 1 docs alignment pending review" — not "completed" or "implemented" |
| design boundary correction row sanitized | ✅ | Row 419: "AGENTS.md" references removed, now says "six-layer boundary" |

**Finding**: All state transitions are accurately recorded. No defer is reported as implemented. ✅

## 4. Production Code / Test / AGENTS.md / Root README — Untouched

| Check | Status | Evidence |
|---|---|---|
| No `.py` files modified | ✅ | `git diff HEAD --name-only | grep '\.py$'` returns empty |
| No root README touched | ✅ | Only `fund_agent/README.md` in diff |
| No AGENTS.md in scope | ✅ | AGENTS.md diff is pre-existing four-layer conflict; explicitly excluded per plan §5 Non-Scope |
| No `runtime/` or `engine/` created | ✅ | `ls fund_agent/runtime fund_agent/engine` → both "No such file or directory" |
| No new untracked files in `fund_agent/` | ✅ | `git status --short fund_agent/` shows only ` M fund_agent/README.md` |

## 5. Dayu Four-Layer / dayu.host / dayu.engine Residuals — Absent

Validation scan (`rg` for `dayu\.host|dayu\.engine|UI -> Service -> Host -> Agent|外部 Dayu runtime|external Dayu runtime`) returned hits across all three docs, but ALL are in prohibition/checklist context:

| Context | Example |
|---|---|
| Anti-external-dayu statement | "当前确定性主链路不依赖外部 Dayu runtime、Host、Engine、tool loop 或外部 Dayu API" |
| Checklist gate | "是否在当前确定性主链路中误拼接外部 Dayu runtime" |
| Engineering baseline | "keeps external Dayu runtime out" |
| Pyproject absorption | "浏览器/Web/微信/外部 Dayu runtime 不作为默认或可选生产目标" |
| Future plan constraint | "不重新引入外部 Dayu runtime 或三层口径" |

**Zero hits** for `dayu.host` or `dayu.engine` as literal dotted import paths. No residual four-layer target wording (`UI -> Service -> Host -> Agent`) in any of the three docs. ✅

## 6. Diff Hygiene

- `git diff --check docs/design.md docs/implementation-control.md fund_agent/README.md` → exit 0, no whitespace errors ✅
- `git diff HEAD --stat` → 27 files, +57/-8101 lines. Vast majority of deletions are dead doc cleanup (20260430/, old audit docs, old research notes, old plan docs) — none are in review scope ✅

## 7. Minor Observations (Non-Blocking)

**O1. `rg` scan regex is overly broad.** The plan's Slice 1 validation regex catches `外部 Dayu runtime` / `external Dayu runtime` which legitimately appear in prohibition statements. A more precise scan using only `dayu\.host` and `dayu\.engine` literal dotted paths would have zero hits across all three docs. This is a validation-command precision issue, not a doc-content issue.

**O2. AGENTS.md conflict remains unresolved.** Local `AGENTS.md` still carries uncommitted four-layer + `dayu.host`/`dayu.engine` mandate diff. This is explicitly excluded from Slice 1 scope per plan §5 and controller judgment. It is a known residual that must be resolved by user decision before any push or future Runtime/Engine implementation gate. Not a defect of this alignment.

**O3. Deleted docs are stale but mass-deletion is coarse.** 22 doc files deleted (~8K lines). These are all pre-P19 audit/plan/research artifacts from 20260430 and earlier dates — genuinely stale. However the deletions are not directly part of Slice 1 scope (they're inherited dirty workspace from `main`) and should ideally be in a separate hygiene commit. Not a review blocker.

## Summary

| Review Focus | Result |
|---|---|
| design.md §9 tree reflects disk facts | ✅ PASS |
| README separates current path from target boundary | ✅ PASS |
| implementation-control accurately records state | ✅ PASS |
| No production code/tests/AGENTS.md/root README touched | ✅ PASS |
| No runtime/engine created | ✅ PASS |
| No Dayu four-layer/dayu.host/dayu.engine residuals | ✅ PASS |

**Overall: PASS.** Slice 1 docs-only alignment is consistent with the accepted plan, faithfully implements the controller's instructions, and introduces no regressions, misleading claims, or scope violations. Ready for review/acceptance or push authorization.
