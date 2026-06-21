# Extractor Output Repository Plan

## Gate

- Work unit: `Extractor 输出仓库化`
- Branch: `extractor-output-repository`
- Classification: `standard`
- Plan artifact: `docs/reviews/extractor-output-repository-plan-20260621-041604.md`
- Goal confirmation status: accepted by continuation context after feasibility discussion

## Goal

将 `FundDataExtractor.extract(...)` 产生的 `StructuredFundDataBundle` 显式落盘为结构化 JSON，并按 `fund_code + report_type + year` 组织，为多年分析和后续 LLM route 提供稳定输入层。

## First-principles Judgment

当前系统已经有三类相关能力，但都不能直接当成目标实现：

- `FundDataExtractor.extract(...)` 只返回内存 bundle；它的职责是抽取，不应隐式写盘。
- `fund_agent/fund/extraction_snapshot.py` 写 `snapshot.jsonl`，但它是一行一个字段的评分/quality gate 输入，不是完整 extractor 输出仓库。
- `fund_agent/fund/quality_gate_integration.py` 能从已抽取 bundle 写 snapshot/score/gate，但它是 quality gate adapter，不是通用稳定输入层。

因此当前 work unit 应新增 Fund 层 output repository：显式保存和读取完整 `StructuredFundDataBundle` 的 JSON 投影；Service/CLI 只做薄编排。

## Success Signal

- 新增 `ExtractorOutputRepository`，默认根目录为 `reports/extractor-outputs`。
- 保存路径固定为：

```text
reports/extractor-outputs/<fund_code>/annual_report/<year>/structured_fund_data.json
```

- JSON 顶层包含稳定 schema 和 identity：

```json
{
  "schema_version": "fund-agent.extractor_output.v1",
  "fund_code": "004393",
  "report_type": "annual_report",
  "report_year": 2024,
  "created_at": "ISO-8601 UTC",
  "bundle": {}
}
```

- `bundle` 保留所有 `StructuredFundDataBundle` 当前字段，包括每个 `ExtractedField` 的 `value`、`anchors`、`extraction_mode`、`note`，以及 `nav_data`、`source_provenance`。
- `load(...)` 同时校验路径参数和 JSON identity；不一致时 fail-closed。
- CLI 提供显式薄入口，能运行 extractor 并输出仓库 JSON 路径。
- 文档同步当前真实用法和非目标。
- focused tests 通过，且既有 extractor/snapshot/quality gate 测试不回退。

## Non-goals

- 不让 `FundDataExtractor.extract(...)` 默认写盘。
- 不复用 `extraction_snapshot` 作为 bundle repository。
- 不把 repository 输出声明为 source truth、golden answer、readiness 或 release proof。
- 不让 UI/Host/LLM 直接消费 PDF、cache、Docling、FundDisclosureDocument candidate 或 parser 原始产物。
- 不在本 gate 改造 `analyze-annual-period` 去读取 repository；该消费路径属于后续独立 gate。
- 不支持半年度、季度、招募说明书等其它 `report_type`；v1 只支持 `annual_report`。
- 不新增数据库、索引服务、并发锁、清理策略、retention policy 或远端存储。

## Design Alignment

- 遵守 `AGENTS.md` 的 UI -> Service -> Host -> Agent 边界：Fund 层实现结构化输出仓库；Service 做请求编排；UI 只解析 CLI 参数并打印路径。
- 生产年报访问仍只通过 `FundDocumentRepository`，由 `FundDataExtractor` 内部维持现有访问路径。
- 显式参数全部放在 typed request / function signature，不使用 `extra_payload`。
- 不改变 `FundProcessorRegistry`、processor admission、FDD candidate boundary 或 `EvidenceSourceKind`。

## Affected Files

Production:

- `fund_agent/config/paths.py`
- `fund_agent/fund/extractor_output_repository.py` 新增
- `fund_agent/fund/README.md`
- `fund_agent/services/extractor_output_service.py` 新增
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `README.md`

Tests:

- `tests/fund/test_extractor_output_repository.py` 新增
- `tests/services/test_extractor_output_service.py` 新增
- `tests/ui/test_cli.py`
- `tests/README.md`

Artifacts:

- `docs/reviews/extractor-output-repository-plan-20260621-041604.md`
- 后续 implementation/review artifacts in `docs/reviews/`

## Public Contract

### Schema

Constant:

```python
EXTRACTOR_OUTPUT_SCHEMA_VERSION = "fund-agent.extractor_output.v1"
SUPPORTED_EXTRACTOR_OUTPUT_REPORT_TYPES = ("annual_report",)
EXTRACTOR_OUTPUT_FILENAME = "structured_fund_data.json"
```

Top-level JSON:

```python
{
    "schema_version": EXTRACTOR_OUTPUT_SCHEMA_VERSION,
    "fund_code": str,
    "report_type": "annual_report",
    "report_year": int,
    "created_at": str,
    "bundle": dict[str, object],
}
```

`bundle` keys must mirror `StructuredFundDataBundle` current public fields:

- scalar identity: `fund_code`, `report_year`
- extracted fields: `basic_identity`, `product_profile`, `benchmark`, `index_profile`, `fee_schedule`, `turnover_rate`, `nav_benchmark_performance`, `investor_return`, `tracking_error`, `share_change`, `manager_alignment`, `manager_strategy_text`, `holdings_snapshot`, `holder_structure`, `bond_risk_evidence`, `portfolio_managers`, `risk_characteristic_text`
- side data: `nav_data`, `source_provenance`

Each extracted field JSON:

```python
{
    "value": object | None,
    "anchors": list[dict[str, object]],
    "extraction_mode": str,
    "note": str | None,
}
```

### Repository API

Module: `fund_agent/fund/extractor_output_repository.py`

```python
@dataclass(frozen=True, slots=True)
class ExtractorOutputIdentity:
    fund_code: str
    report_type: str
    report_year: int

@dataclass(frozen=True, slots=True)
class ExtractorOutputRecord:
    schema_version: str
    identity: ExtractorOutputIdentity
    created_at: str
    bundle_payload: dict[str, object]
    path: Path

class ExtractorOutputRepository:
    def __init__(self, root_dir: Path = DEFAULT_EXTRACTOR_OUTPUT_ROOT) -> None: ...
    def path_for(self, *, fund_code: str, report_type: str, report_year: int) -> Path: ...
    def save(self, *, bundle: StructuredFundDataBundle, report_type: str = "annual_report") -> ExtractorOutputRecord: ...
    def load(self, *, fund_code: str, report_type: str, report_year: int) -> ExtractorOutputRecord: ...
```

Identity validation:

- `fund_code` must be 6 digits.
- `report_year` must be positive.
- `report_type` must be exactly `annual_report` in v1.
- `save(...)` requires `bundle.fund_code == fund_code` implied by bundle and `bundle.report_year == report_year` implied by bundle.
- `load(...)` requires JSON `fund_code/report_type/report_year` equal request identity.
- `load(...)` rejects unknown schema version, missing `bundle`, or malformed top-level identity.

### Service API

Module: `fund_agent/services/extractor_output_service.py`

```python
@dataclass(frozen=True, slots=True)
class ExtractorOutputSaveRequest:
    fund_code: str
    report_year: int
    report_type: str
    output_root: Path | None
    force_refresh: bool = False

class ExtractorOutputExtractor(Protocol):
    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle: ...

class ExtractorOutputRepositoryProtocol(Protocol):
    def save(self, *, bundle: StructuredFundDataBundle, report_type: str = "annual_report") -> ExtractorOutputRecord: ...

class ExtractorOutputService:
    def __init__(
        self,
        extractor: ExtractorOutputExtractor | None = None,
        repository_factory: Callable[[Path | None], ExtractorOutputRepositoryProtocol] | None = None,
    ) -> None: ...
    async def save(self, request: ExtractorOutputSaveRequest) -> ExtractorOutputRecord: ...
```

Service behavior:

- Validate fund code, report year, report type.
- Production default constructs `FundDataExtractor()` and `ExtractorOutputRepository(root)`.
- Tests can inject a fake extractor and fake repository factory without touching `FundDocumentRepository`.
- Call `extractor.extract(fund_code, report_year, force_refresh=force_refresh)`.
- Save bundle with `report_type`.
- Return repository record.

### CLI

Add command:

```text
fund-analysis extractor-output-save FUND_CODE --report-year 2024 [--report-type annual_report] [--output-root reports/extractor-outputs] [--force-refresh]
```

Stdout:

```text
extractor_output_json: reports/extractor-outputs/004393/annual_report/2024/structured_fund_data.json
schema_version: fund-agent.extractor_output.v1
fund_code: 004393
report_type: annual_report
report_year: 2024
```

Invalid input or extractor/repository error exits nonzero and writes concise error to stderr.

## Implementation Slices

### Slice 1: Fund-layer Repository and Serialization

Allowed files:

- `fund_agent/config/paths.py`
- `fund_agent/fund/extractor_output_repository.py`
- `tests/fund/test_extractor_output_repository.py`

Changes:

- Add `DEFAULT_EXTRACTOR_OUTPUT_ROOT = Path("reports/extractor-outputs")`.
- Implement identity dataclasses, constants and repository.
- Implement JSON serialization using a strict recursive `_jsonable(...)`, not ad hoc string building.
- `_jsonable(...)` accepts only `None`, `str`, `int`, `float`, `bool`, dataclass instances, mappings with string keys, and sequences.
- Dataclass instances are converted through field iteration or `dataclasses.asdict`; tuples are emitted as JSON arrays.
- Unknown objects fail closed with `TypeError`; do not use `default=str` or generic text fallback.
- `Path` conversion is not allowed in bundle payload unless a future schema explicitly introduces a path field.
- Write JSON with `ensure_ascii=False`, `indent=2`, trailing newline.
- Load validates schema and identity and returns `ExtractorOutputRecord`.

Tests:

- `test_repository_saves_bundle_under_fund_report_type_year_path`
- `test_repository_roundtrip_preserves_extracted_field_missing_semantics`
- `test_repository_roundtrip_preserves_anchors_nav_data_and_source_provenance`
- `test_repository_rejects_path_json_identity_mismatch`
- `test_repository_rejects_unsupported_report_type`
- `test_repository_rejects_malformed_fund_code_and_year`
- `test_repository_rejects_unknown_non_jsonable_bundle_value`

Validation:

```bash
uv run pytest tests/fund/test_extractor_output_repository.py -q
```

### Slice 2: Service and CLI Thin Entry

Allowed files:

- `fund_agent/services/extractor_output_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_extractor_output_service.py`
- `tests/ui/test_cli.py`

Changes:

- Add typed Service request and service class.
- Add constructor injection for fake extractor and fake repository factory while keeping production defaults.
- Export request/service in `fund_agent/services/__init__.py`.
- Add CLI command that delegates to service.
- Keep UI thin: no direct import from `fund_agent.fund.extractor_output_repository` in CLI except through service result types already exposed by service package.

Tests:

- Service validates explicit request fields.
- Service calls extractor once and repository save once using injected fakes.
- Service fake tests prove no real `FundDocumentRepository` path is touched.
- CLI passes `fund_code`, `report_year`, `report_type`, `output_root`, `force_refresh` to service.
- CLI prints output path and identity lines.

Validation:

```bash
uv run pytest tests/services/test_extractor_output_service.py tests/ui/test_cli.py -q
```

### Slice 3: Docs Sync and Focused Regression

Allowed files:

- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/*implementation-evidence*.md`

Changes:

- Root README: add user command and default output layout.
- Fund README: document repository contract, schema, non-goals and relation to snapshot/quality gate.
- Tests README: add new focused tests and boundary notes.
- Implementation evidence records validation.

Validation:

```bash
uv run pytest tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py tests/fund/test_extraction_snapshot.py tests/fund/test_quality_gate_integration.py -q
git diff --check
```

## Error Handling and Invariants

- Unsupported `report_type` is a `ValueError`; do not silently create arbitrary subdirectories.
- Identity mismatch is a `ValueError`; do not return stale or mismatched JSON.
- Unsupported bundle payload value type is a `TypeError`; do not silently stringify schema drift.
- Repository creates parent directories on save only; load does not create directories.
- Save is deterministic for path and schema shape, but `created_at` changes per write.
- Existing file at same identity may be overwritten by explicit save; this v1 does not implement history or conflict detection.
- Missing fields remain explicit missing `ExtractedField` payloads, not omitted keys.

## Testing Strategy

Focused tests prove:

- path organization by `fund_code/report_type/year`;
- JSON schema top-level shape;
- roundtrip preserves missing semantics and anchors;
- fail-closed identity validation;
- Service/CLI are thin and explicit;
- existing snapshot/quality gate behavior remains separate.

No live PDF/network tests are required for this gate. Fake bundles and fake services are sufficient because this work unit is storage/serialization/entrypoint behavior, not extractor correctness.

## Docs Decision

Docs must be updated because this adds a user-visible CLI and Fund-layer storage contract:

- `README.md`: command and output layout.
- `fund_agent/fund/README.md`: Agent/Fund boundary and repository contract.
- `tests/README.md`: test coverage entry.

No `docs/design.md` update in this gate unless implementation changes architecture beyond this plan. This plan preserves the current architecture and adds an implementation-level storage capability.

## Risks and Residual Owners

- Future consumers may want to hydrate `StructuredFundDataBundle` objects from JSON. This gate only returns validated `ExtractorOutputRecord` with payload; typed hydration is assigned to the later consumer gate.
- Concurrency and conflict detection are not implemented. Later production scheduling can add atomic write/lock semantics if concurrent writers become a real use case.
- Other report types are unsupported by design in v1; half-year/quarter support requires a later schema extension gate.
- Annual-period analysis does not yet read these artifacts; assigned to later annual-period consume gate.
- LLM route does not yet consume these artifacts; assigned to later LLM route design/implementation gate.

## Overengineering Check

This plan adds one repository module, one Service wrapper and one CLI command because the user-visible goal requires a stable persisted input layer and explicit invocation. It does not add database, indexing, typed hydration, migrations, lock managers, background jobs, retention policy or multi-report generalization. The abstraction matches an existing local pattern: Fund-layer capability plus Service request plus UI thin command.

## Completion Report Format

Final report must include:

- changed files;
- artifact paths;
- validation commands and results;
- schema/path summary;
- residual risks and next gate;
- whether goal remains active or complete.
