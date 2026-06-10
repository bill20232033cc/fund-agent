# EID Source Metadata Design Wording Docs-Sync Plan - 2026-06-11

Status: DRAFT_FOR_REVIEW

## Role And Boundary

Role: planning worker.

This artifact is a code-generation-ready docs-sync plan for the next gate:

```text
EID source metadata design wording docs-sync planning gate
```

This plan does not implement the docs-sync patch.

## Source Of Truth Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` around EID source metadata wording
- `fund_agent/fund/documents/models.py` `AnnualReportSourceMetadata`
- `fund_agent/fund/documents/sources.py` `_build_eid_metadata`
- `scripts/controlled_live_eid_failure_branch_observation.py` `_safe_report_payload`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-stage-b-live-retry-evidence-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-stage-b-live-retry-controller-judgment-20260611.md`

## Problem Statement

`docs/design.md` currently contains stale wording in the annual-report cache/source metadata section:

```text
来源元数据：当前 AnnualReportSourceMetadata 支持 ... source failure category、identity status 和 integrity status
```

This wording is stale because current `AnnualReportSourceMetadata` does not define `identity_status` or `integrity_status` fields. The current dataclass fields are the source identity/provenance fields and policy fields, including:

- `source`
- `source_url`
- EID identifiers and report metadata: `fund_code`, `fund_id`, `report_year`, `report_code`, `report_desp`, `report_name`, `upload_info_id`, `upload_info_detail_id`, `table_name`, `report_send_date`, `operation_upload_type`, `corrections_num`
- `fallback_used`
- `primary_failure_category`
- `selected_source`
- `source_mode`
- `fallback_enabled`
- `discovery_contract_version`

`identity_mismatch` and `integrity_error` are `AnnualReportSourceFailureCategory` values / validation outcomes. They are not `AnnualReportSourceMetadata` status fields.

NAV `identity_status` is a separate typed NAV repository domain. It belongs to `FundNavRepository.load_nav_series()` and NAV source eligibility, not annual-report PDF source metadata. The docs-sync must not mix NAV identity wording into annual-report EID metadata.

## Current Repo Fact

- `AnnualReportSourceMetadata` in `fund_agent/fund/documents/models.py` has no `identity_status` or `integrity_status`.
- `_build_eid_metadata()` in `fund_agent/fund/documents/sources.py` constructs EID metadata with `source="eid"`, `source_url`, EID candidate identifiers, `selected_source=EID_SELECTED_SOURCE`, `source_mode=EID_SINGLE_SOURCE_MODE`, `fallback_enabled=False`, and `discovery_contract_version=EID_DISCOVERY_CONTRACT_VERSION`.
- `_safe_report_payload()` only exposes safe scalar metadata summary fields: `source`, `selected_source`, `source_mode`, `fallback_enabled`, `fallback_used`, `primary_failure_category`, `discovery_contract_version`, cache hit flags, and basic parsed-report counts.
- Current annual-report source policy remains EID single-source: `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.
- Eastmoney remains source code / deferred future source candidate only. CNINFO and fund-company routes are not current production fallback paths.

## Truth-Doc Fact

- `docs/current-startup-packet.md` and `docs/implementation-control.md` set the next entry point as this no-live/docs-only docs-sync planning gate.
- The current accepted Stage B live retry checkpoint is `f0a1459`.
- Stage B accepted evidence classification is `accepted_live_window_no_failure_observed`.
- Stage B observed one successful live window for `006597 / 2024` with `status=success`, `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`, and `primary_failure_category=null`.
- Stage B is not all failure-branch live proof. No live `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, or `integrity_error` branch was observed.
- Checkpoint `ac6bbe9` remains the accepted no-live code-behavior proof for modeled EID failure categories.

## Accepted Residual

- `docs/design.md` stale identity/integrity metadata wording remains a deferred docs-sync residual.
- The residual is documentation wording drift only. It does not prove a missing runtime field, a required schema migration, or a source behavior defect.

## Non-Goals

- Do not modify source code.
- Do not modify tests.
- Do not modify runtime behavior.
- Do not modify `docs/implementation-control.md`.
- Do not modify `docs/current-startup-packet.md`.
- Do not run live EID, network, PDF, FDR, `FundDocumentRepository`, helper command, fallback, non-EID source, provider, LLM, extractor, `analyze`, `checklist`, golden, readiness, score-loop, release, PR, push, or merge commands.
- Do not reclassify Stage B as all failure-branch live proof.
- Do not reintroduce Eastmoney, CNINFO, fund-company, or other non-EID fallback as current production behavior.
- Do not move NAV `identity_status` wording into annual-report source metadata.

## Later Implementation Scope

Allowed file for the later docs-only implementation gate:

```text
docs/design.md
```

Optional later gate artifacts, if required by controller/review flow:

```text
docs/reviews/*implementation-evidence-20260611.md
docs/reviews/*review-*.md
docs/reviews/*controller-judgment-20260611.md
```

Disallowed for later implementation:

- source files
- test files
- runtime behavior
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `AGENTS.md`

## Exact Patch Plan

Patch only the `docs/design.md` bullet under:

```text
缓存策略 -> 来源元数据
```

Replace the stale wording that says `AnnualReportSourceMetadata` supports `identity status` and `integrity status`.

Use wording equivalent to:

```text
- 来源元数据：当前 `AnnualReportSourceMetadata` 是年报来源 provenance 容器，支持 `selected_source=eid`、`source_mode=single_source_only`、`fallback_enabled=false`、`fallback_used=false`、EID URL/identifier、`primary_failure_category` 和 `discovery_contract_version` 等当前字段；`identity_mismatch` / `integrity_error` 是来源失败分类与校验结果，不是 `AnnualReportSourceMetadata` 的 status 字段。不得通过隐藏 fallback metadata 伪装 EID source。
```

Implementation details:

- Keep the surrounding cache strategy section unchanged.
- Keep EID single-source wording unchanged.
- Keep fail-closed semantics unchanged:
  - `schema_drift` fail-closed
  - `identity_mismatch` fail-closed
  - `integrity_error` fail-closed
  - `not_found` / `unavailable` remain terminal EID source failures under `single_source_only`
- Keep Eastmoney / CNINFO / fund-company as deferred source candidate or historical evidence route only; do not write them as current production fallback.
- Keep Stage B live evidence wording as `accepted_live_window_no_failure_observed`; do not imply all failure branches were observed live.
- Keep `ac6bbe9` as no-live failure-category proof if the patch mentions failure-branch proof at all.

## Validation Plan

Allowed validation commands only:

```bash
rg -n "identity status|integrity status|identity_status|integrity_status|AnnualReportSourceMetadata|来源元数据|accepted_live_window_no_failure_observed|ac6bbe9|Eastmoney|CNINFO|基金公司|fund-company" docs/design.md
sed -n '650,682p' docs/design.md
git diff --check -- docs/design.md
```

Expected validation:

- `docs/design.md` no longer claims annual-report `AnnualReportSourceMetadata` has identity/integrity status fields.
- `docs/design.md` still preserves annual-report EID single-source policy.
- `docs/design.md` still preserves fail-closed failure category semantics.
- `docs/design.md` does not imply Eastmoney / CNINFO / fund-company fallback is current production behavior.
- `git diff --check -- docs/design.md` exits `0`.

Do not run tests. Do not run live commands.

## Review Gate

Required next sequence:

```text
plan review DS/MiMo -> controller judgment -> docs-only implementation gate
```

Plan review should check:

- stale wording is correctly identified as documentation drift
- current dataclass field set is not expanded by the plan
- NAV `identity_status` remains separate from annual-report source metadata
- EID single-source and no-fallback policy remains intact
- Stage B live evidence classification remains bounded
- allowed files and validation commands are constrained

## Stop Conditions

Stop before implementation if review or controller finds any of the following:

- the patch would require adding/removing fields from `AnnualReportSourceMetadata`
- the patch would change source/fallback/runtime behavior
- the patch would require tests or live validation
- the patch would alter control docs or current startup packet
- wording would imply non-EID fallback is current production behavior
- wording would imply Stage B proved all live failure branches

## Completion Report Format For Later Implementation Worker

The later implementation worker should report only:

```text
Artifact/path changed:
- docs/design.md

Validation:
- rg ...: PASS/FAIL
- sed ...: PASS/FAIL
- git diff --check -- docs/design.md: PASS/FAIL

Residuals:
- <none or exact residual>
```
