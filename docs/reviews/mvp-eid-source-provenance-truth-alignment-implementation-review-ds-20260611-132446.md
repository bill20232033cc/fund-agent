# Code Review

## Scope

- Mode: current changes (implementation review handoff within Gateflow)
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: not applicable (implementation review of a specific gate write set)
- Output file: `docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-review-ds-20260611-132446.md`
- Included scope: `fund_agent/fund/source_provenance.py`, `fund_agent/fund/extraction_snapshot.py`, `fund_agent/fund/documents/sources.py`, `fund_agent/fund/README.md`, `tests/fund/test_source_provenance.py`, `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_extraction_score.py`, `tests/fund/test_data_extractor.py`
- Excluded scope: `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, root `README.md`, `pyproject.toml`, `.gitignore`, `fund_agent/fund/documents/repository.py`, `fund_agent/fund/documents/cache.py`, `fund_agent/fund/documents/models.py`, live evidence / reports / golden / readiness artifacts
- Parallel review coverage: none (single reviewer)

## Findings

未发现实质性问题。

### Evidence Summary

**1. `primary_then_fallback` removed from all active code/tests**

Static check `rg -n "primary_then_fallback" fund_agent tests --glob '*.py'` returns exactly two matches, both in the required current EID negative assertion test at `tests/fund/test_source_provenance.py:337,360`. No other occurrence exists.

**2. No Eastmoney/fund-company/CDN/CNINFO fallback reintroduced**

`source_provenance.py` and `extraction_snapshot.py` contain zero references to Eastmoney, fund-company, CDN, or CNINFO. The `sources.py` change is a single docstring correction (line 584-585) replacing "使用 EID 主源与 Eastmoney fallback" with "仅使用 EID single-source，Eastmoney 不在当前 production fallback 中". The `EastmoneyAnnualReportSource` class remains frozen as a deferred future candidate per plan.

**3. Source Provenance v2 fields are correct**

- `source_provenance.py:14`: `PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION = "repository_source_provenance.v2"` ✅
- `source_provenance.py:15`: `CURRENT_SOURCE_STRATEGY = "single_source_only"` ✅
- `source_provenance.py:31`: `SourceStrategy = Literal["single_source_only", "legacy_or_unknown"]` — no `primary_then_fallback` ✅
- `source_provenance.py:79-81`: `selected_source: SelectedSourceName | None`, `source_mode: SourceMode`, `fallback_enabled: bool | None` — additive fields present ✅
- `source_provenance.py:143`: `source_strategy = source_mode` — compatibility alias, not independent strategy control ✅

**4. Legacy/unknown provenance does not masquerade as current policy**

Verified through three paths:
- **No metadata** → `default_public_source_provenance()`: `selected_source=None`, `source_mode=legacy_or_unknown`, `fallback_enabled=None` ✅
- **Legacy metadata without current fields** → test `test_primary_metadata_without_fallback_remains_not_applicable`: `selected_source=None`, `source_mode=legacy_or_unknown`, `fallback_enabled=None` ✅
- **Legacy fallback without failure category** → test `test_fallback_without_public_failure_category_is_incomplete_unknown`: `selected_source=None`, `source_mode=legacy_or_unknown`, `fallback_enabled=None`, `fallback_eligibility=unknown_public_metadata_absent` ✅

**5. `_selected_source_name` does not infer from `resolved_source_name`**

`source_provenance.py:242-257`: `_selected_source_name()` validates against `{"eid", "eastmoney"}` independently. It does not fall back to or read `resolved_source_name`. Test `test_eastmoney_source_name_alone_does_not_imply_fallback` confirms no inference. ✅

**6. Snapshot propagation and summary aligned**

- `extraction_snapshot.py:235-245`: `SnapshotRecord` includes `selected_source`, `source_mode`, `fallback_enabled` ✅
- `extraction_snapshot.py:1165-1175`: `_snapshot_record()` copies provenance fields directly, no transformation ✅
- `extraction_snapshot.py:1209`: Summary table header includes `selected_source`, `source_mode`, `fallback_enabled` before fallback fields ✅
- Test `test_build_snapshot_records_copies_identical_bundle_source_provenance_to_all_rows` confirms consistency across all field records ✅

**7. Fund README aligned and does not authorize fallback**

- `fund_agent/fund/README.md:73`: Documents EID single-source as `selected_source=eid`、`mode=single_source_only`、`fallback_enabled=false` ✅
- `fund_agent/fund/README.md:196`: States `source_strategy` 只作为兼容 alias，不是来源获取策略或 fallback 授权 ✅
- Does not authorize Eastmoney, fund-company, CDN, or CNINFO fallback ✅

**8. No changes outside accepted write set**

`git diff --name-only` returns exactly the 8 accepted files. `fund_agent/fund/documents/models.py` is absent from the diff. ✅

**9. Release/readiness compatibility preserved**

`fallback_used`, `primary_failure_category`, `fallback_eligibility`, and `source_provenance_status` remain unchanged in meaning. `golden_readiness_preflight.py` was not modified. ✅

**10. Existing fallback metadata tests are explicitly legacy/unknown**

Tests `test_fallback_with_metadata_owned_eligible_category_is_complete` and `test_fallback_with_fail_closed_category_is_incomplete` assert `selected_source=None`, `source_mode=legacy_or_unknown`, `fallback_enabled=None` — making clear they are legacy metadata tests, not current production fallback proof. ✅

**11. Score semantics unchanged by additive provenance fields**

Tests `test_source_provenance_keys_do_not_change_score_outputs` and `test_run_extraction_score_output_ignores_additive_source_provenance` prove score JSON keys, gate-sensitive outputs, and FQ decisions unchanged. ✅

**12. No live EID/network/PDF/FDR commands executed**

Review was conducted statically. No live execution commands were run. ✅

## Open Questions

无。

## Residual Risk

- `docs/design.md` still contains historical public snapshot v1 wording. This is outside the current gate scope and deferred to a later design-truth-sync gate as recorded in the controller judgment.
- `AnnualReportSourceName` still includes `"eastmoney"`. This is outside scope per plan — deferred source-candidate/fallback design scope.
- `golden_readiness_preflight.py` fallback field semantics verified unchanged through static review of field names and test coverage; a live readiness run was not executed (and is not required for this gate).
