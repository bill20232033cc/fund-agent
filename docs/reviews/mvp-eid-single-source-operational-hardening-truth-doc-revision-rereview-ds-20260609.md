# EID Single Source Operational Hardening Truth-Doc Revision — Targeted Re-Review (AgentDS)

## Gate

| Item | Value |
|---|---|
| Gate | `EID Single Source Operational Hardening Gate` |
| Classification | `heavy` |
| Role | AgentDS — targeted re-reviewer, not controller |
| Review target | Truth-doc revision actual diff and evidence |
| Date | 2026-06-09 |

## Artifacts Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-steering-judgment-20260609.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-acceptance-controller-judgment-20260609.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-evidence-20260609.md`
- `docs/reviews/repo-review-20260609-165959.md`

## Review Method

No-live text validation only: `rg` checks against the three truth docs, `git diff --check`. No live EID/network/PDF/FDR/fallback/provider/curl/DNS/socket/smoke run.

## Checklist Results

### 1. Exact policy values in all three truth docs

PASS. `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false` present in all three docs:

| Doc | Lines |
|---|---|
| `docs/design.md` | 5, 650, 657, 676, 711, 1096 |
| `docs/implementation-control.md` | 9, 63, 71, 595 |
| `docs/current-startup-packet.md` | 20, 332 |

All grep results verified independently against actual file content — evidence artifact line numbers are correct.

### 2. Current code fact vs accepted gate target separation

PASS. All three docs consistently label EID single-source as accepted gate target / future implementation direction, not implemented code fact:

- `docs/design.md:5`: "尚未作为代码实现事实"
- `docs/design.md:655`: "当前代码事实：仓库源码中仍可能保留历史 EID primary 与 Eastmoney fallback 机制"
- `docs/implementation-control.md:9`: "not an implemented code fact"
- `docs/current-startup-packet.md:21`: "not implemented code fact"

No instance found where EID single-source is written as already implemented.

### 3. Eastmoney / fund-company website/CDN / CNINFO as deferred candidates only

PASS. All three docs consistently label non-EID routes as deferred source candidate or historical evidence route only:

- `docs/design.md:657`: "只能作为 deferred source candidate / historical evidence route"
- `docs/implementation-control.md:63`: "仅保留为 deferred source candidate / historical evidence route"
- `docs/current-startup-packet.md:21`: "deferred source candidates or historical evidence-intake routes only"

No current production fallback wording found. `rg` for `Eastmoney fallback|fallback 到 Eastmoney|production fallback` returned only deferred/future risk phrasing — no current-production claim.

### 4. Row-shape contract decision gate queued / paused by steering

PASS. Present across control and startup docs:

- `docs/implementation-control.md`: lines 9, 10, 72, 73, 597
- `docs/current-startup-packet.md`: lines 21, 22, 334

Row-shape gate is consistently labeled `queued / paused by steering`, not rejected or deleted. Manager, retained risk, `006597` bond top holding and `110020` target ETF holding all preserved as residuals.

### 5. not_found / unavailable terminal under single_source_only; schema_drift / identity_mismatch / integrity_error fail-closed

PASS. Under `mode=single_source_only`:

- `docs/design.md:659-667`: explicit table showing `not_found` and `unavailable` are terminal EID source failures that do not authorize fallback; `schema_drift`, `identity_mismatch`, `integrity_error` are fail-closed.
- `docs/implementation-control.md:63`: same semantics.
- `docs/current-startup-packet.md:21`: "Under mode=single_source_only, not_found and unavailable are terminal EID source failures and do not authorize fallback; schema_drift, identity_mismatch and integrity_error fail closed."

No fallback eligibility gate remains for `not_found` / `unavailable` in any of the three truth docs.

### 6. FundDocumentRepository as sole production annual-report access boundary

PASS.

- `docs/design.md:643`: "对基金文档的存取统一通过 FundDocumentRepository，禁止直接操作文件系统"
- `docs/design.md:711`: annual-report PDF source acquisition "后续实现仍必须经 FundDocumentRepository 边界"
- `docs/implementation-control.md:62`: "生产年报访问必须通过 FundDocumentRepository；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper"
- `docs/current-startup-packet.md:318`: same boundary preserved

No authorization found for UI/Service/Host/renderer/quality gate direct source/downloader/cache/parser access.

### 7. Dayu reference only; no runtime dependency; extra_payload prohibited

PASS. All hits for `dayu-agent`, `dayu.host`, `dayu.engine`, `extra_payload` across all three truth docs are prohibition or boundary/reference-only statements. No authorization of Dayu as production runtime dependency. `extra_payload` prohibition consistently repeated.

### 8. Source code / tests / README / live actions unauthorized

PASS. Implementation-control.md and startup packet explicitly prohibit source code, test, README changes. Evidence artifact confirms: no source code modified, no tests modified, no README modified, no live EID/network/PDF/FDR/fallback/provider/curl/DNS/socket/smoke run, no commit/push/PR/merge/release.

### 9. Repo-review Eastmoney finding is deferred future risk only

PASS.

- `docs/current-startup-packet.md:333`: "Eastmoney integrity-classification finding from repo-review... is deferred future source-candidate/fallback risk only"
- `docs/implementation-control.md:596`: "Deferred-with-owner... retained as future source-candidate/fallback risk evidence only"
- `docs/design.md:678`: same disposition

No authorization to fix Eastmoney code, add tests, or validate live fallback.

### 10. Evidence artifact consistency with actual diff

PASS. All grep line numbers in the evidence artifact match the actual file state. `git diff --check` passes. No discrepancy found between evidence claims and actual truth doc content.

Specifically verified:
- Evidence claims line 5, 650, 657, 676, 711, 1096 for `selected_source=eid` in design.md → all present
- Evidence claims line 9, 63, 71, 595 for `selected_source=eid` in implementation-control.md → all present
- Evidence claims line 20, 332 for `selected_source=eid` in startup packet → both present
- Same verification for `mode=single_source_only` and `fallback_enabled=false` → all correct
- Evidence claims row-shape hits include startup lines 21, 22, 334 and control lines 9, 10, 72, 73, 597 → all correct

## Additional Observations (Non-Blocking)

- `docs/implementation-control.md` version and date (v2.5 / 2026-06-07) were not bumped during revision. The startup packet now serves as the primary gate-status surface and the control doc `Current Truth Guardrails` section is fully updated with EID single-source policy, so this is cosmetic only — the gate content is unambiguous.
- The `docs/design.md` §6.6 (error/degradation) was listed as modified in evidence but was not independently spot-checked in this review; the §6.1 fallback table, §6.3 external data table, and decision comparison table are sufficient to confirm policy alignment.

## Verdict

**PASS** — zero blocking findings.

All 10 checklist items pass. The three truth docs are internally consistent on EID single-source operational hardening policy. Current code fact and accepted gate target are clearly separated. Eastmoney / fund-company website/CDN / CNINFO are deferred candidates only. Row-shape gate remains queued / paused by steering. `not_found` / `unavailable` are terminal EID source failures under `single_source_only`; `schema_drift` / `identity_mismatch` / `integrity_error` remain fail-closed. `FundDocumentRepository` boundary, Dayu reference-only discipline, and `extra_payload` prohibition are all preserved. Evidence artifact grep results match reality.
