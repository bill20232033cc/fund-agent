# Release Maintenance Gate 2 Implementation Plan: Core Analyze/Checklist Reliability Hardening

## Gate Self-Check

- Current gate / role: Gate 2 `implementation-plan handoff only`；我是 AgentCodex implementation-planning specialist，不是 controller。
- Source of truth: `AGENTS.md`、`docs/design.md` 当前设计章节、`docs/implementation-control.md` Startup Packet / Current gate / Next entry point、HEAD `20f58144b7ab696544f0d82110442ee963c99ddf`。
- Scope boundary: 只产出本计划；本轮不改 production code、不改 tests、不 commit、不 push、不做 GitHub mutation。
- Stop conditions: 若实现需要改变 FQ0-FQ6、renderer Chapter 3、`FundDocumentRepository` fallback 策略、Host/Agent/dayu 或 source helper，则停止回 controller。
- Evidence and validation: 本计划必须给 implementation agent 可直接执行的文件、契约、切片、测试矩阵和停止条件。

## Goal

在 release maintenance 的 `core analyze/checklist reliability hardening` gate 中，最小化修复三类可靠性/可观测性问题：

1. NAV 外部数据失败不得阻断 annual-report `analyze` / `checklist` 主路径。年报字段抽取必须继续，`nav_data` 以显式 unavailable/degraded 空结果进入 `StructuredFundDataBundle`。
2. 2026-05-01 以前的年报缺失 `turnover_rate` 保持为可解释的数据不足 / warning，不成为 hard blocker。优先用测试锁定现行语义；仅在现有 smoke 反例证明用户可见解释不足时补最小 note。
3. quality gate artifact 默认 `run_id` / path 必须区分 `analyze` 与 `checklist` 来源命令；不得改变 FQ0-FQ6 规则。

## Non-Goals

- 不改 renderer Chapter 3 或报告正文写作逻辑。
- 不改 Host/Agent/dayu，不创建占位包。
- 不改 `FundDocumentRepository`、PDF source helper、年报 source fallback 策略或失败分类。
- 不弱化 FQ0-FQ6 block/warn/info 语义。
- 不把 NAV 映射进 `ReportEvidenceBundle` 或 report-quality facts；`nav_data` mapping 仍属于后续 source-contract slice。
- 不引入 tracked run artifacts、scratch reports、quality-gate-run 输出或 durable fixtures。
- 不把显式参数塞入 `extra_payload` 或自由 dict。

## First-Principles Candidate Selection

### Candidate A: 在 `FundNavDataAdapter.load_nav_data()` 内吞掉所有异常

- 优点：最靠近外部 akshare / SQLite 失败源。
- 问题：会改变 adapter 的通用契约；`tests/fund/data/test_nav_data.py` 当前验证 cache/fetcher 行为，未来直接使用 adapter 的消费者可能需要异常来诊断数据源。它也无法区分调用场景是否是 annual-report 主路径。
- 结论：不选为主方案。只允许在 adapter 增加一个显式 factory/类型字段，不应默认吞异常。

### Candidate B: 在 `FundDataExtractor.extract()` 对 `nav_provider.load_nav_data()` 做 annual-report 主路径降级

- 优点：`FundDataExtractor` 是年报 repository + NAV + extractor 的 façade；它已经把 `nav_data` 聚合进 `StructuredFundDataBundle`，是最小同源修复点。失败仍发生在 NAV 依赖边界，不触碰年报 repository fail-closed policy。
- 直接证据：`fund_agent/fund/data_extractor.py:161-166` 先通过 repository 加载年报，再调用 `nav_provider.load_nav_data()`；`fund_agent/fund/data_extractor.py:167-192` 的 profile/performance/manager/holdings extractor 在 NAV 之后才执行，因此 NAV 异常会阻断所有年报抽取。
- 结论：选择 B。

### Candidate C: 在 Service 层 catch extractor 异常后重试不带 NAV

- 优点：可只影响 `analyze` / `checklist`。
- 问题：Service 无法知道异常来自 NAV 还是年报 repository / PDF identity；若 catch 太宽，会违反 PDF `identity_mismatch` / `integrity_error` / `schema_drift` fail-closed。若让 Service 直接理解 NAV provider，则越过 Agent/Fund 数据 façade。
- 结论：不选。

### Candidate D: 让 `checklist` 传 `quality_gate_run_id="checklist-..."`

- 优点：局部且显式。
- 问题：当前 `FundAnalysisRequest` 没有 source command 字段；默认 run_id 在 Service 内部 `_default_quality_gate_run_id()` 固定 `analyze-...`。只在 CLI 拼字符串会让 Service tests 和非 CLI callers 仍无法区分。
- 结论：选择“显式 command source 参数 + Service 内默认 run_id 使用该参数”的方案，不使用 `extra_payload`。

## Root Cause Evidence

### NAV failure blocks annual-report extraction

- `FundNavDataAdapter.load_nav_data()` 文档明确会抛 `sqlite3.Error`、fetcher 异常等：`fund_agent/fund/data/nav_data.py:184-198`。
- 默认 akshare fetcher 会传播 ImportError / AttributeError / akshare 查询异常：`fund_agent/fund/data/nav_data.py:38-52`、`fund_agent/fund/data/nav_data.py:55-72`。
- cache 初始化 / 读取 / 写入也可抛出：`fund_agent/fund/data/nav_data.py:140-154`、`fund_agent/fund/data/nav_data.py:242-263`、`fund_agent/fund/data/nav_data.py:265-300`。
- `FundDataExtractor.extract()` 当前在加载年报后立即调用 NAV：`fund_agent/fund/data_extractor.py:161-166`；随后才运行章节 extractor：`fund_agent/fund/data_extractor.py:167-170`。因此 NAV provider / cache / akshare 失败会阻断 annual-report 字段抽取。
- `StructuredFundDataBundle.nav_data` 是必填：`fund_agent/fund/data_extractor.py:70-110`。所以降级必须提供结构化 `NavDataResult`，不能置空。

### NAV unavailable representation has existing low-blast-radius consumers

- snapshot 的 `_build_nav_record()` 只读 `source`、`cached`、`records`，空 records 会变成 `extraction_mode="missing"`：`fund_agent/fund/extraction_snapshot.py:946-964`。
- renderer Chapter 5 只读 `len(nav_data.records)`：`fund_agent/fund/template/renderer.py:1295-1308`。本 gate 不改 renderer，因此空 records 是兼容的。
- `docs/implementation-control.md` 明确 `nav_data` mapping 仍属 future slice：`docs/implementation-control.md:298-299`。本 gate 不投射为 report facts。

### annual-report PDF fail-closed must be preserved

- `AGENTS.md` 要求生产年报 PDF 访问经过 `FundDocumentRepository`，且 `schema_drift`、`identity_mismatch`、`integrity_error` fail-closed。
- 当前执行链路把 repository 放在 NAV 前：`docs/design.md:71-79`；实现中 repository load 在 NAV 前：`fund_agent/fund/data_extractor.py:161-166`。
- 因此实现必须只 catch `nav_provider.load_nav_data()` 周围的异常，绝不包裹 `load_annual_report()`。

### pre-2026 turnover_rate already degrades as warn/missing, not block

- `turnover_rate` 是 P1 字段：`fund_agent/fund/extraction_score.py:41-58`、`docs/design.md:730-735`。
- FQ2/FQ2F 规则中 P1 fail 为 `warn`，P0 fail 才 `block`：`fund_agent/fund/quality_gate.py:563-601`、`fund_agent/fund/quality_gate.py:625-649`；设计文档同样记录：`docs/design.md:743-749`。
- 现有测试 `test_run_quality_gate_warns_failed_p1_without_blocking` 已验证 P1 fail 得到 warn：`tests/fund/test_quality_gate.py:56-91`。
- R=A+B-C 在 `turnover_rate` 缺失时返回 `status="missing"` 和 note，不抛异常：`fund_agent/fund/analysis/r_abc.py:154-173`、`fund_agent/fund/analysis/r_abc.py:310-317`。
- manager extractor 对未披露换手率返回 `extraction_mode="missing"` 和说明：`fund_agent/fund/extractors/manager_ownership.py:677-706`。
- 结论：无需改 FQ2/FQ2F 或 R=A+B-C 语义；只需增加 pre-2026 回归测试锁定 behavior。若 smoke 发现实际 `analyze/checklist` block，root cause 应优先怀疑 FQ4 missing-field-rate 或 P0 失败，而不是 turnover 本身。

### checklist quality gate run_id currently uses analyze prefix

- `FundAnalysisService.analyze()` 与 `checklist()` 都调用 `_run_analysis_core(request)`：`fund_agent/services/fund_analysis_service.py:434-502`。
- `_run_quality_gate_if_enabled()` 默认传 `_default_quality_gate_run_id(structured_data)`：`fund_agent/services/fund_analysis_service.py:846-875`。
- `_default_quality_gate_run_id()` 固定返回 `analyze-{fund_code}-{report_year}-{timestamp}`：`fund_agent/services/fund_analysis_service.py:928-942`。
- `FundAnalysisRequest` / `ResolvedAnalyzeContract` 当前没有 source command 字段：`fund_agent/services/fund_analysis_service.py:155-181`、`fund_agent/services/fund_analysis_service.py:184-220`。
- control doc residual 明确要求只做 naming/observability distinction，不改 FQ0-FQ6：`docs/implementation-control.md:298`。

## Minimal Contracts

### NAV unavailable/degraded contract

Do not break existing `NavDataResult` callers. Extend `NavDataResult` with optional fields that default to the current successful shape:

```python
@dataclass(frozen=True, slots=True)
class NavDataResult:
    fund_code: str
    records: NavPayload
    source: str
    cached: bool
    unavailable: bool = False
    unavailable_reason: str | None = None
```

Add a module-level helper:

```python
def unavailable_nav_data_result(
    fund_code: str,
    *,
    reason: str,
    source: str = "nav_unavailable",
) -> NavDataResult:
    ...
```

Required semantics:

- Successful cache/fetch behavior remains unchanged: `source` is `nav_cache` or `akshare`, `cached` reflects existing behavior, `unavailable=False`, `unavailable_reason=None`.
- NAV degraded result: `records=[]`, `source="nav_unavailable"`, `cached=False`, `unavailable=True`, `unavailable_reason` is non-empty and includes exception type + sanitized message.
- `FundDataExtractor.extract()` catches only exceptions raised by `self._nav_provider.load_nav_data(...)`; it must not catch repository/PDF exceptions or extractor exceptions.
- The NAV catch type is intentionally broad: use `except Exception as exc:` around the single `load_nav_data(...)` call because provider, cache, akshare import, and external request failures have heterogeneous exception types. The stop condition is about catch scope: never move the repository call or annual-report extractors inside this catch block.
- Snapshot note should include unavailable reason when present, preserving existing `source/cached/records` note. Existing empty records already produce `extraction_mode="missing"` in `_build_nav_record()`.

### analyze/checklist run_id distinction contract

Add an explicit request field instead of `extra_payload`:

```python
AnalyzeCommandSource = Literal["analyze", "checklist"]

@dataclass(frozen=True, slots=True)
class FundAnalysisRequest:
    ...
    command_source: AnalyzeCommandSource = "analyze"
```

Required semantics:

- `FundAnalysisService.analyze()` must run the core with `command_source="analyze"` even if a caller omitted the field.
- `FundAnalysisService.checklist()` must run the core with `command_source="checklist"` without requiring CLI to pass a developer override.
- Service methods are authoritative for `command_source`. CLI explicit construction is for readability and test observability only; if a direct caller passes `command_source="checklist"` to `analyze()`, Service normalizes the core run to `"analyze"`, and vice versa for `checklist()`.
- Explicit user/developer `quality_gate_run_id` remains authoritative and is not rewritten.
- Default run_id helper becomes `_default_quality_gate_run_id(structured_data, command_source)` and returns `{command_source}-{fund_code}-{report_year}-{timestamp}`.
- `_validate_request()` rejects invalid `command_source` values.
- CLI `analyze` and `checklist` can either rely on Service methods to set source or explicitly construct request with the matching `command_source`; the implementation should use explicit construction for readability and test observability.

## Implementation Slices

### Slice 1: NAV unavailable/degraded annual-report extraction

Allowed files:

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/data/test_nav_data.py`
- `tests/fund/test_extraction_snapshot.py`
- Add focused test file only if clearer: `tests/fund/test_data_extractor.py`

Exact changes:

1. Extend `NavDataResult` with optional `unavailable` and `unavailable_reason` fields, defaulting to successful values.
2. Add `unavailable_nav_data_result()` with full Chinese docstring.
3. In `FundDataExtractor.extract()`:
   - keep `report = await self._repository.load_annual_report(...)` unchanged and outside any NAV catch;
   - replace direct NAV call with a private module-level helper `_load_nav_data_or_unavailable(nav_provider, fund_code, force_refresh)` that catches `Exception` around NAV only;
   - implement that helper with `except Exception as exc:` around only `nav_provider.load_nav_data(...)`; `unavailable_reason` must include `f"{type(exc).__name__}: {exc}"`;
   - return unavailable result on NAV failure.
4. In `_build_nav_record()`, append `unavailable={nav_data.unavailable}` and `reason={nav_data.unavailable_reason}` to the existing `source=...; cached=...; records=...` note when unavailable; do not replace the existing note fields.
5. Do not change `FundNavDataAdapter.load_nav_data()` success/cache exception behavior.

Expected tests:

- New focused extractor test with fake repository returning a parsed annual report and fake nav provider raising `RuntimeError("network down")`; assert extraction succeeds, annual-report fields are populated, `bundle.nav_data.records == []`, `bundle.nav_data.unavailable is True`, reason contains `RuntimeError` and `network down`.
- Repository failure regression: fake repository raises an annual-report identity/integrity-style exception; assert exception still propagates and NAV provider is not called.
- Adapter success tests updated only for optional defaults: existing cache tests should continue to pass; optionally assert `unavailable is False`.
- Snapshot test for unavailable nav note includes `source=nav_unavailable`, `records=0`, and reason.

Stop conditions:

- If implementation needs to catch repository/PDF errors to make tests pass, stop and return to controller. This means the repository call has entered the wrong catch boundary; it does not mean the NAV-only catch should be narrowed below `Exception`.
- If a caller requires `nav_data=None`, stop; that would break `StructuredFundDataBundle` and renderer assumptions.

### Slice 2: Explicit command-source run_id for analyze vs checklist

Allowed files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`

Exact changes:

1. Define `AnalyzeCommandSource = Literal["analyze", "checklist"]`.
2. Add `command_source: AnalyzeCommandSource = "analyze"` to `FundAnalysisRequest` and document it in Chinese docstring.
3. In `analyze()`, normalize request to `command_source="analyze"` before `_run_analysis_core()` if needed. Preferred minimal implementation: use `dataclasses.replace(request, command_source="analyze")`.
4. In `checklist()`, normalize request to `command_source="checklist"` before `_run_analysis_core()`.
5. Add `command_source` to `_ValidatedRequest` or pass `request.command_source` through validation; reject any non `analyze/checklist`.
6. Change `_default_quality_gate_run_id(structured_data)` to `_default_quality_gate_run_id(structured_data, command_source)` and use it in `_run_quality_gate_if_enabled()`.
7. Preserve explicit `resolved_contract.quality_gate_run_id`: when provided, use it unchanged.
8. CLI should pass `command_source="analyze"` in analyze request and `command_source="checklist"` in checklist request so UI tests can inspect the explicit parameter. This is not the correctness boundary; Service method normalization remains authoritative.

Expected tests:

- Service analyze default quality-gate output dir basename starts with `analyze-004393-2024-`.
- Service checklist default quality-gate output dir basename starts with `checklist-004393-2024-`.
- Existing explicit `quality_gate_run_id="fixture-run"` tests still write/use exactly `fixture-run`.
- CLI analyze request carries `command_source == "analyze"`.
- CLI checklist request carries `command_source == "checklist"`.

Stop conditions:

- Do not add command source into `developer_overrides` or `extra_payload`.
- Do not change `run_quality_gate_for_bundle()` signature unless a test proves the Service-level explicit run_id cannot satisfy the requirement.

### Slice 3: pre-2026 turnover_rate regression lock

Allowed files:

- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/services/test_fund_analysis_service.py`
- Only if tests expose a real product blocker: `fund_agent/fund/extractors/manager_ownership.py` for note wording, or `fund_agent/fund/extraction_snapshot.py` for note propagation.

Expected primary decision:

- No production code change should be necessary. Current code already treats missing `turnover_rate` as P1 warn and R=A+B-C missing attribution.

Required tests:

- Quality gate unit: score payload where only `turnover_rate` P1 fails and fund-level `p1_status="fail"` yields `status == warn`, issues include `FQ2/warn` and `FQ2F/warn`, no block issues.
- Service integration: bundle with `report_year=2024` and `turnover_rate=ExtractedField(value=None, extraction_mode="missing", note="§8 未披露...")`, quality gate `warn` policy, selected CSV present. Construct the bundle so all other fields are present enough to keep `missing_field_rate < 20%`; assert no `QualityGateBlockedError`, `rabc_attribution.status == "missing"`, note contains `缺少 §8 换手率`, quality gate includes P1/FQ2/FQ2F warning semantics and does not include FQ4.
- Gate 1 correctness regression stays covered: same-year mismatch still FQ1/block, year-not-covered still FQ0/info.

Optional minimal production change only if required:

- If smoke shows user-facing text lacks pre-2026 explanation, update missing note in `manager_ownership._build_turnover_rate()` to mention `2026-05-01 前披露口径可能不足，作为数据不足处理` only when report date/year can be determined safely from `ParsedAnnualReport.key.year`.
- Do not add date-specific FQ rule. Do not demote P1 globally. Do not change FQ4 denominator.

Stop conditions:

- If pre-2026 missing turnover still blocks because total missing-field-rate triggers FQ4/block, do not weaken FQ4 in this gate. Return to controller with evidence and propose a separate field-applicability design gate.
- Concrete FQ4 decision procedure: run `uv run fund-analysis analyze 004393 --report-year 2024` under the default block policy. If it exits 2 with FQ4 block, inspect `quality_gate.json` and `score.json`: if `turnover_rate` is the only P1 failure and no P0 fields fail, return to controller because turnover may be driving an aggregate FQ4 false blocker; if multiple fields or any P0 fields fail, classify as designed aggregate data-quality block and do not change FQ4.

## Full Test Matrix

Focused unit/service tests:

- `uv run pytest tests/fund/data/test_nav_data.py tests/fund/test_extraction_snapshot.py -q`
- `uv run pytest tests/services/test_fund_analysis_service.py -q`
- `uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q`
- `uv run pytest tests/ui/test_cli.py -q`

Scenario assertions:

- Simulated NAV provider exception: annual-report extraction still succeeds; NAV result is unavailable/degraded with empty records and reason.
- NAV cache / akshare success regression: cached and fetched results still have `unavailable=False`.
- annual-report repository/PDF failure regression: repository exception propagates; NAV degradation does not mask `identity_mismatch` / `integrity_error` / `schema_drift` style failures.
- Turnover pre-2026 degradation: missing `turnover_rate` in 2024 is warning / insufficiency and not hard blocker by itself.
- Analyze/checklist artifact naming: default run IDs and output dirs start with `analyze-...` vs `checklist-...`; explicit `quality_gate_run_id` remains unchanged.
- Gate 1 correctness regression: `year_not_covered` remains `FQ0/info`; same-year mismatch remains `FQ1/block`; oracle identity remains `fund_code + report_year + field_name + sub_field`.

Project validation:

- `uv run ruff check .`
- `uv run pytest -q`
- `git diff --check`

004393 smoke commands, with scratch output outside tracked tree or ignored run dirs:

- `uv run fund-analysis analyze 004393 --report-year 2024`
- `uv run fund-analysis checklist 004393 --report-year 2024`
- `uv run fund-analysis analyze 004393 --report-year 2025`
- `uv run fund-analysis checklist 004393 --report-year 2025`

Smoke expectations:

- 2024 analyze/checklist commands exit 0 and preserve the accepted release-readiness baseline: `quality_gate_status: warn`, not a correctness block.
- 2025 analyze/checklist commands exit 0; missing same-year golden coverage remains `year_not_covered` / `FQ0/info`, not FQ1 mismatch from 2024 golden.
- Quality gate artifacts for analyze/checklist have distinguishable run_id/path prefixes: `analyze-...` vs `checklist-...`.
- No tracked report, scoring-run, quality-gate-run, cache, PDF, or smoke artifact is added.

## Documentation Decision

- If only internal dataclass optional fields, Service request field, and tests change, update `fund_agent/fund/README.md` only if it currently documents `NavDataResult` fields or NAV failure behavior; otherwise no README update is required.
- Because Slice 1 touches `fund_agent/fund/data/nav_data.py` and `fund_agent/fund/data_extractor.py`, implementation must explicitly check `fund_agent/fund/README.md` for NAV / `StructuredFundDataBundle` / `NavDataResult` wording and update it if the new degraded contract is part of the current Fund package behavior.
- Because `FundAnalysisRequest` public Service contract gains `command_source`, update `fund_agent/README.md` if its Service contract table or example request enumerates fields.
- Do not update root `README.md` unless CLI flags/user commands change. This plan does not require new CLI flags.
- Do not update `docs/design.md` during implementation unless controller explicitly asks for design truth sync after accepted implementation; if updated, state current code facts only.

## Risks

- Catching `Exception` around NAV is intentionally broad because the goal includes provider, cache, akshare, and external fetch failures. Risk is masking programming errors in NAV provider. Mitigation: unavailable reason must include exception type; catch scope must be exactly one call to `load_nav_data`.
- Empty NAV records may increase P2 `nav_data` missing signals in snapshot/score. This is acceptable because NAV is P2 and the gate goal is annual-report main path continuity; do not weaken scoring rules.
- `command_source` could be misused by direct Service callers. Mitigation: validate literal domain and Service methods normalize their own source.
- Pre-2026 turnover may still be one contributor to FQ4 missing-rate block in poor-quality bundles. This gate must not change FQ4; classify as separate field-applicability risk if observed.

## Implementation Completion Report Format

Implementation agent should report:

- Self-check: `pass` or `blocked - <reason>`.
- Changed files.
- Slice completion status for S1/S2/S3.
- Contract summary for NAV unavailable and command_source run_id.
- Validation commands run and exact pass/fail results.
- Residual risks classified as fixed / later slice / later phase / user decision.
- Confirmation: no renderer Chapter 3, Host/Agent/dayu, source fallback policy, FQ0-FQ6 weakening, tracked run artifacts, commit, push, or GitHub mutation.
