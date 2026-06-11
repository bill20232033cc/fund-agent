# EID Source Provenance Truth Alignment Gate Plan

日期：2026-06-11 13:01:59

状态：planning artifact；不进入 implementation。

Gate: `EID source provenance truth alignment gate`

Classification: `standard`

Planning worker: `019eb50c-71f4-7280-82b3-35d5c6b8b19d`

## Objective

把公共 source provenance 输出从旧 `primary_then_fallback` 口径对齐到当前 EID single-source truth：

- `selected_source="eid"`
- `source_mode="single_source_only"`
- `fallback_enabled=false`
- `fallback_used=false`

当前 gate 只修公共 provenance schema / snapshot 输出 / 测试断言 / EID source wording，不改变年报来源获取策略。

## Non-goals

- 不重新引入 Eastmoney、基金公司官网/CDN、CNINFO。
- 不实现 fallback invocation、source expansion、多 source orchestrator。
- 不运行 live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR。
- 不修改 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`。
- 不改变 `FundDocumentRepository`、cache policy、PDF downloader、EID HTTP 行为。
- 不改变 renderer、FQ0-FQ6、score 语义、golden/readiness promotion。
- 不把 legacy fallback metadata 当作当前 production fallback evidence。

## Repo Facts

### Truth-doc facts

- `docs/current-startup-packet.md` 当前 active gate 是 `EID source provenance truth alignment gate`，next entry 是 planning。
- `docs/implementation-control.md` 定义 implementation objective：对齐 public EID provenance，不重引入 fallback/source expansion/live commands。
- `docs/design.md` 明确当前 EID single-source code fact：`selected_source=eid`、`mode=single_source_only`、`fallback_enabled=false`。
- `docs/design.md` 同时记录当前公共 snapshot 仍包含 `source_strategy`、`resolved_source_name`、`fallback_used` 等字段。这是当前代码事实，不是未来正确口径。
- `docs/reviews/repo-review-20260611-114133.md` finding 1 指出 public provenance 仍输出 `primary_then_fallback`，进入 `FundDataExtractor` 和 `extraction_snapshot`，并被测试固化。

### Code facts

- `fund_agent/fund/source_provenance.py` defines `PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION = "repository_source_provenance.v1"`.
- `fund_agent/fund/source_provenance.py` defines `DEFAULT_SOURCE_STRATEGY = "primary_then_fallback"`.
- `fund_agent/fund/source_provenance.py` `SourceStrategy` only allows `"primary_then_fallback"`.
- `PublicSourceProvenance` currently does not contain `selected_source`, `source_mode`, or `fallback_enabled`.
- Default provenance and non-fallback metadata success paths emit `source_strategy="primary_then_fallback"`.
- `FundDataExtractor.extract()` projects `ParsedAnnualReport.metadata.source` via `project_public_source_provenance()`.
- `SnapshotRecord` stores public provenance fields and copies `bundle.source_provenance`.
- Snapshot summary currently displays `resolved_source_name`, `fallback_used`, `fallback_eligibility`, `source_provenance_status`, and `source_provenance_reason`.
- `AnnualReportSourceOrchestrator` class docstring already states single-source only, but its `__init__` parameter docstring still says default sources are EID primary plus Eastmoney fallback.
- `_build_eid_metadata()` already writes `selected_source=EID_SELECTED_SOURCE`, `source_mode=EID_SINGLE_SOURCE_MODE`, and `fallback_enabled=False`.
- Repository cache reuse already requires current EID single-source metadata.

### Tests currently using old value

- `tests/fund/test_source_provenance.py` asserts default `source_strategy == "primary_then_fallback"` and dict serialization includes that key/value.
- `tests/fund/test_extraction_snapshot.py` `_SOURCE_PROVENANCE_FIELDS` does not include current policy fields and asserts snapshot `source_strategy == "primary_then_fallback"`.
- `tests/fund/test_extraction_snapshot.py` constructs `PublicSourceProvenance(source_strategy="primary_then_fallback")`.
- `tests/fund/test_extraction_score.py` `_PUBLIC_SOURCE_PROVENANCE_PAYLOAD` fixes old `source_strategy`.
- `tests/fund/test_data_extractor.py` verifies resolved/fallback/status fields but does not assert current policy fields.

## Proposed Schema / Field Change

Minimum compatibility strategy:

- Retain legacy field name `source_strategy` for one compatibility cycle, but stop emitting `"primary_then_fallback"` for the current EID success path.
- Redefine `source_strategy` as a legacy-compatible alias:
  - current EID success path: `"single_source_only"`
  - metadata absent or legacy/unknown path: `"legacy_or_unknown"`
- Add current policy fields:
  - `selected_source: Literal["eid", "eastmoney"] | None`
  - `source_mode: Literal["single_source_only", "legacy_or_unknown"]`
  - `fallback_enabled: bool | None`
- Upgrade schema version to `repository_source_provenance.v2`.

Default provenance with no metadata:

- `selected_source=None`
- `source_mode="legacy_or_unknown"`
- `fallback_enabled=None`
- `source_strategy="legacy_or_unknown"`
- `fallback_used=False`
- `fallback_eligibility="not_applicable"`

Current EID metadata success path:

- `selected_source="eid"`
- `source_mode="single_source_only"`
- `fallback_enabled=False`
- `source_strategy="single_source_only"`
- `resolved_source_name="eid"`
- `fallback_used=False`
- `primary_failure_category=None`
- `fallback_eligibility="not_applicable"`

Legacy fallback metadata path:

- Preserve `fallback_used`, `primary_failure_category`, and `fallback_eligibility` projection for old fixtures/snapshots.
- Set current policy fields from metadata if present; otherwise use `legacy_or_unknown` / `None`.
- Do not present legacy fallback metadata as current production fallback proof.
- Do not add or call fallback acquisition.

Naming:

- Use `selected_source` / `source_mode` / `fallback_enabled`, matching `AnnualReportSourceMetadata`.
- Keep `source_strategy` only as a compatibility alias, not as a strategy control surface.
- Do not add `mode`; use `source_mode` to avoid collision with CLI/analyze mode.

## Implementation Slices

### Slice 1 - PublicSourceProvenance schema

- Update schema version to `repository_source_provenance.v2`.
- Replace `DEFAULT_SOURCE_STRATEGY` with:
  - `CURRENT_SOURCE_STRATEGY = "single_source_only"`
  - `LEGACY_OR_UNKNOWN_SOURCE_STRATEGY = "legacy_or_unknown"`
- Extend `SourceStrategy = Literal["single_source_only", "legacy_or_unknown"]`.
- Add `SelectedSourceName`, `SourceMode`, and `FallbackEnabled` compatible fields to `PublicSourceProvenance`.
- Update docstrings so `source_strategy` is clearly a compatibility alias.

### Slice 2 - Projection logic

- Add `_selected_source_name(source_metadata)` using `source_metadata.selected_source` first.
- Add `_source_mode(source_metadata)`:
  - if metadata `source_mode` is present: return it
  - else return `"legacy_or_unknown"`
- Add `_fallback_enabled(source_metadata)`:
  - if metadata `fallback_enabled` is present: return it
  - else return `None`
- Default path returns unknown legacy-safe current fields.
- Non-fallback EID path projects metadata fields directly.
- Fallback metadata paths preserve fallback classification, but set current policy fields from metadata or legacy unknown.
- Do not infer `selected_source` from `resolved_source_name` when metadata lacks `selected_source`.

### Slice 3 - Snapshot propagation

- Add to `SnapshotRecord`:
  - `selected_source`
  - `source_mode`
  - `fallback_enabled`
- Update snapshot record construction to copy the new fields.
- Update source provenance summary table to include current policy fields before fallback fields:
  - `fund_code`
  - `selected_source`
  - `source_mode`
  - `fallback_enabled`
  - `resolved_source_name`
  - `fallback_used`
  - `fallback_eligibility`
  - `source_provenance_status`
  - `source_provenance_reason`
- Keep failed-funds omission behavior unchanged.

### Slice 4 - EID source wording

- In `AnnualReportSourceOrchestrator.__init__` docstring, replace old wording:
  - from: “未提供时使用 EID 主源与 Eastmoney fallback”
  - to: “未提供时仅使用 EID single-source；Eastmoney 不在当前 production fallback 中”
- Do not change orchestrator implementation.

### Slice 5 - Tests

- Update existing tests to expect v2 schema and current fields.
- Add EID single-source specific projection test.
- Add legacy fallback metadata test to prove it remains legacy/unknown and does not masquerade as current EID policy.
- Add current EID negative assertion proving `"primary_then_fallback"` does not appear in current EID provenance payload values.
- Update snapshot and score fixtures to include new additive fields.
- Keep score semantic assertions unchanged.

### Slice 6 - Fund README sync

- Update only source provenance / snapshot wording in `fund_agent/fund/README.md`.
- Document v2 additive fields: `selected_source`, `source_mode`, and `fallback_enabled`.
- State that `source_strategy` is a compatibility alias, not source acquisition strategy or fallback authorization.
- Keep root `README.md` forbidden.

## Allowed Write Set

- `fund_agent/fund/source_provenance.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_data_extractor.py`

## Forbidden Write Set

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `README.md`
- `pyproject.toml`
- `.gitignore`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/models.py`
- live evidence / reports / golden / readiness artifacts

## Test Plan

Update `tests/fund/test_source_provenance.py`:

- `test_default_public_source_provenance_is_not_applicable` expects schema v2, `source_strategy == "legacy_or_unknown"`, `selected_source is None`, `source_mode == "legacy_or_unknown"`, and `fallback_enabled is None`.
- Add `test_eid_single_source_metadata_projects_current_policy_fields` with `AnnualReportSourceMetadata(source="eid", fallback_used=False, selected_source="eid", source_mode="single_source_only", fallback_enabled=False)`.
- Add `test_source_provenance_no_primary_then_fallback_value_in_current_eid_path`, asserting `"primary_then_fallback"` does not appear in the current EID provenance payload values.
- Update primary metadata non-fallback test to use full current EID metadata or explicitly assert legacy/unknown when current fields are absent.
- Update fallback tests to preserve classification assertions and assert missing current fields become legacy/unknown.
- Update stable dict serialization to include `selected_source`, `source_mode`, and `fallback_enabled`.

Update `tests/fund/test_data_extractor.py`:

- In EID source metadata projection tests, assert `selected_source == "eid"`, `source_mode == "single_source_only"`, `fallback_enabled is False`, and `source_strategy == "single_source_only"`.
- Keep fallback metadata tests, but assert legacy/unknown current policy fields.

Update `tests/fund/test_extraction_snapshot.py`:

- Extend `_SOURCE_PROVENANCE_FIELDS`.
- Update default provenance payload assertions to schema v2 and unknown/default current fields.
- Update `PublicSourceProvenance` fixtures with new dataclass fields.
- Update summary header and row assertions to include current policy fields.
- Assert all snapshot rows copy identical `selected_source`, `source_mode`, and `fallback_enabled`.

Update `tests/fund/test_extraction_score.py`:

- Update `_PUBLIC_SOURCE_PROVENANCE_PAYLOAD` to v2 fields.
- Keep tests proving source provenance keys do not change scoring semantics.

## Validation Matrix

| Check | Command | Required result |
|---|---|---|
| Static old value removal from active code/tests | `rg -n "primary_then_fallback" fund_agent tests --glob '*.py'` | No match except the required current EID negative assertion test |
| Public provenance tests | `uv run pytest tests/fund/test_source_provenance.py -q` | Pass |
| Data extractor provenance tests | `uv run pytest tests/fund/test_data_extractor.py -q` | Pass |
| Snapshot tests | `uv run pytest tests/fund/test_extraction_snapshot.py -q` | Pass |
| Score additive compatibility tests | `uv run pytest tests/fund/test_extraction_score.py -q` | Pass |
| Focused fund tests | `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | Pass |
| Lint | `uv run ruff check fund_agent/fund/source_provenance.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/documents/sources.py tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py` | Pass |
| Diff hygiene | `git diff --check` | Pass |
| No live/source expansion commands | Review command history / evidence artifact | No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR |
| No unauthorized files | `git diff --name-only` | Only allowed write set |
| Fund README sync | `rg -n "selected_source|source_mode|fallback_enabled|source_strategy" fund_agent/fund/README.md` | Shows v2 current fields and compatibility alias wording |

No full `uv run pytest -q` requirement by default unless focused tests expose shared breakage.

## Risks / Residuals

| Risk / residual | Disposition |
|---|---|
| Public schema v2 is a contract change | Keep legacy `source_strategy` field as compatibility alias; add current fields rather than replacing all old fields |
| `golden_readiness_preflight.py` reads fallback fields from snapshot rows | Keep fallback fields present and unchanged in meaning; do not change readiness behavior |
| Legacy fallback tests can look like current production fallback proof | Rename/comment tests as legacy metadata projection tests and assert legacy/unknown current policy fields |
| `docs/design.md` still describes current public snapshot v1 fields | Do not edit in this gate; record controller residual after implementation acceptance if design truth-sync is needed |
| `AnnualReportSourceName` still includes `"eastmoney"` | Do not remove; this belongs to source-candidate/fallback design scope |
| `source_strategy` name remains awkward | Retain only as compatibility alias; authoritative fields are `selected_source`, `source_mode`, `fallback_enabled` |
| Fund package README can drift from public provenance schema | Update only `fund_agent/fund/README.md` provenance wording in this gate; keep root README unchanged |

## Reviewer Handoff Checklist

AgentMiMo:

- Verify no slice changes source acquisition or orchestrator behavior.
- Verify current EID path emits `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.
- Verify `primary_then_fallback` is gone from active current-path public output.
- Verify snapshot schema is additive and score semantics remain unchanged.
- Verify fallback metadata tests are explicitly legacy/unknown, not current production fallback proof.
- Verify `fund_agent/fund/README.md` is synchronized for v2 fields and does not imply fallback authorization.
- Verify validation matrix excludes live/provider/PDF/readiness/release commands.

AgentDS:

- Verify schema naming is compatible with `AnnualReportSourceMetadata` and design truth.
- Verify implementation does not infer current policy from indirect fields like `resolved_source_name`.
- Verify `source_strategy` retention cannot be read as current fallback authorization.
- Verify `AnnualReportSourceOrchestrator` docstring correction is wording-only.
- Verify allowed write set is not exceeded.
- Verify `source_strategy` docstring/README wording says compatibility alias, not source acquisition strategy or fallback authorization.
- Verify any design/control mismatch discovered during implementation is deferred to controller/design-truth-sync, not patched in this gate.
