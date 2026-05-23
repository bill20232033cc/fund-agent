# Design / Control / Code Reconciliation

## Scope

- Trigger: post-P7 follow-up planning after repo-level `deepreview --all`.
- Current HEAD before this reconciliation: `26adce7 Document post-P7 follow-up plan`.
- Compared documents:
  - `docs/design.md`
  - `docs/implementation-control.md`
  - `docs/implementation-control-p4.md`
  - current `fund_agent/` and `tests/` code facts
- Reconciliation date: 2026-05-21 Asia/Shanghai.

## Current Code Facts

- Main user entry is `fund-analysis` from `fund_agent.ui.cli:app`.
- `fund-analysis analyze` calls `FundAnalysisService`, then `fund_agent/fund` Capability modules.
- Current production analyze path does not go through `dayu.host`, `dayu.engine`, scene preparation or an `ExecutionContract`.
- Fund documents are accessed through `FundDocumentRepository` / documents adapters.
- Annual report source order is EID/证监会资本市场统一信息披露平台 primary, Eastmoney/akshare fallback.
- PDF cache hits validate `%PDF-`; PDF writes use temp file + atomic replace.
- Parsed report JSON cache corruption is treated as cache miss.
- Template contract machinery is implemented in `fund_agent/fund/template/contracts.py`, `item_rules.py`, `chapter_blocks.py` and renderer/audit/quality gate integrations.
- Full test suite status after repo-level follow-up fixes: `299 passed`.

## Reconciled Findings

| Area | Previous document state | Code fact | Action |
|---|---|---|---|
| `docs/design.md` status | Still described itself as a frozen design draft waiting for implementation | P0-P7 are implemented/accepted; code is ahead of the original plan | Updated header and statement to say the document records accepted design intent plus current code facts, and code/latest reconciliation wins on conflict. |
| Architecture chain | Claimed `UI → Service → Host → Agent/Engine` and listed dayu Host/Engine as direct reuse | Current CLI directly calls Service and Capability; dayu runtime is not in the main chain | Rewrote §2.1/§2.2/§2.3 to current UI/Service/Capability chain and marked dayu Host/Engine as v2 candidates. |
| Preferred lens table | Lacked QDII/FOF rows | Code supports `qdii_fund` and `fof_fund` standard fund types | Added QDII/FOF rows. |
| Thermometer | Pseudocode with unconfirmed URL and auto fallback description | Current implementation has `FundThermometerAdapter`, `ThermometerService`, `fund-analysis thermometer`; no auto `valuation_state` mapping | Rewrote thermometer section to current behavior. |
| Project structure | Listed nonexistent modules (`dependency_setup.py`, `checklist_service.py`, `contract_preparation.py`, `audit_coordinator.py`, prompt scene directories, etc.) and omitted current modules | Current code has documents source abstraction, extraction score/snapshot, golden answer/prefill, quality gate, template contracts/item rules/chapter blocks, thermometer service | Replaced §7 with current structure. |
| Dayu reuse table | Claimed direct reuse of `dayu.engine`, `dayu.host`, `dayu.contracts`, `dayu.prompting` | Current production code does not use these runtime paths | Rewrote §7.1 as module status table. |
| `docs/implementation-control.md` phase status | P6 still planned; current gate stuck at P6-S2 | P6 and P7 are done; post-P7 planning and repo-level fix done | Updated phase table and §1.3 current gate. |
| `docs/implementation-control-p4.md` top status | Header/gate still pointed at P7 closed → repo-level deepreview | Repo-level deepreview is complete; post-P7 follow-up planning is active | Updated top status/current gate and added current post-P7 summary. |

## Remaining Non-Blocking Gaps

- `docs/implementation-control.md` and `docs/implementation-control-p4.md` still contain long historical logs with stale intermediate lines. This reconciliation only updates top-level current state and does not rewrite historical execution records.
- `docs/design.md` §6.3 fund type pseudo-rule remains more aspirational than current code for compound cases such as `QDII` + enhanced index. This is a known domain follow-up from repo-level deepreview, not a documentation-only fix.
- `AGENTS.md` is mostly current but still references `fund-agent-prompt-template.md` and `/workspace/fund-analysis-template-draft.md` paths from the prompt context. User marked AGENTS cleanup as non-urgent.
- Runtime/Agent/Host integration remains a future architecture candidate; current repo is a deterministic CLI/Service/Capability pipeline.

## Verification

Run after this reconciliation:

```bash
pytest
git diff --check
```

Actual:

- `pytest`: `299 passed in 0.80s`.
- `git diff --check`: passed.
- Stale-project-structure grep found no remaining obsolete module names in `docs/design.md`; obsolete names only appear in this artifact as historical evidence.
