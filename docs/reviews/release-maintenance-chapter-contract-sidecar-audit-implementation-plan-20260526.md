# Fund-layer CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit Implementation Plan

> Date: 2026-05-26
> Role: AgentCodex specialist implementation-plan refinement
> Gate: Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation gate
> Verdict: PLAN_READY

## 0. Scope and Truth Sources

本 artifact 只把已接受设计计划收敛成可交给下一位 worker 直接编码的 implementation plan。本轮不修改 source、tests、README、`docs/design.md` 或 `docs/implementation-control.md`。

已读取并作为本计划依据的真源：

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-controller-judgment-20260526.md`

当前 gate 的核心约束：

- 只实现 Fund 层能力。
- 只增加 CHAPTER_CONTRACT executable sidecar 和 dev-only report-writing audit。
- 首个实现 slice 只对 `active_fund` / `chapter_3` turnover / style-consistency / insufficient-evidence claim safety 做 material 行为。
- Chapter 2 enhanced-index tracking-error 和 Chapter 6 bond risk-lens requirements 只做 informational/config，不能制造 end-to-end false positive。
- 不接入 renderer、FQ0-FQ6、Service、CLI 默认链路、Host/Agent、dayu runtime、文档仓库、PDF/cache/source helper/downloader/production extractor。

## 1. Implementation File Plan

### 1.1 Source Files to Add

| File | Required action | Purpose |
|---|---|---|
| `fund_agent/fund/template/chapter_contract_constraints.py` | Add | CHAPTER_CONTRACT executable sidecar/wrapper. 定义 sidecar dataclasses、0-7 章 constraint manifest、fund-type overlay、manifest validation helpers。 |
| `fund_agent/fund/report_writing_audit.py` | Add | Dev-only pure Fund-layer audit. 消费 `ReportEvidenceBundle`、JSONL record payload 或 chapter draft surrogate，输出 issue list、summary、failure categories 和 evidence requirement gaps。 |

### 1.2 Test Files to Add

| File | Required action | Purpose |
|---|---|---|
| `tests/fund/template/test_chapter_contract_constraints.py` | Add | 验证 sidecar 完整性、与 existing `ChapterContract` 的 wrapper 关系、0-7 章 completeness、active Chapter 3 overlay、Chapter 2/6 deferred config severity。 |
| `tests/fund/test_report_writing_audit.py` | Add | 验证 dev-only audit 的 claim safety、data_gap wording、must_not_cover、required_evidence gap 和 valid minimal case。 |

### 1.3 Existing Files That May Be Read but Should Not Be Modified in First Pass

| File | Reason |
|---|---|
| `fund_agent/fund/template/contracts.py` | Existing `ChapterContract` truth source. Sidecar must wrap this manifest, not mutate the dataclass. |
| `fund_agent/fund/report_evidence.py` | Existing `ReportEvidenceBundle` / `ReportDataGap` / `ReportDataGapOverride.required_report_wording` contract source. Audit should consume these types. |
| `fund_agent/fund/report_quality_validation.py` | Boundary reference only. Do not merge validator responsibility into writing audit. |
| `scripts/report_quality_eval.py` | Optional future integration point only. Do not touch in this first implementation unless controller explicitly expands scope. |

### 1.4 Files Explicitly Out of Scope

Do not modify:

- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/audit/audit_programmatic.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/documents/`
- `fund_agent/fund/pdf/`
- `fund_agent/services/`
- `fund_agent/ui/`
- `fund_agent/host/`
- `fund_agent/agent/`
- `pyproject.toml`
- `README.md`
- `fund_agent/README.md`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/implementation-control.md`

README/docs 同步范围 for later implementation gate:

- 本 gate 的 coding worker 应先完成代码和测试。
- 若实现成功且 controller 允许文档同步，最小同步只可能是 `fund_agent/fund/README.md` 和 `docs/design.md` 的 current-code-fact 更新。
- 本 implementation-plan gate 禁止提前修改 README/design/control doc。

## 2. CHAPTER_CONTRACT Sidecar Data Structure

### 2.1 Binding Decision

`fund_agent/fund/template/contracts.py` 中的 frozen `ChapterContract` 保持不变，仍是以下字段的唯一机器真源：

- `chapter_id`
- `title`
- `narrative_mode`
- `must_answer`
- `must_not_cover`
- `required_output_items`
- `preferred_lens`

新 sidecar 是 wrapper over existing `ChapterContract`，不是 replacement，也不是平行真源。它只能：

- 引用 existing manifest 的 `chapter_id`。
- 复用 existing `must_answer` / `must_not_cover` 作为基础语义。
- 增补可执行写作审计所需字段。
- 在 validation 中 fail closed：如果 sidecar 的 chapter ids 不等于 existing manifest 的 0-7，或引用了不存在章节，测试必须失败。

不得：

- 修改 frozen `ChapterContract` dataclass。
- 在 sidecar 中重新维护 chapter title / narrative_mode 作为独立真源。
- 让 renderer 或 product audit 默认消费 sidecar。

### 2.2 Required Sidecar Fields

`chapter_contract_constraints.py` should define frozen slotted dataclasses with Chinese docstrings:

| Field | Type guidance | Meaning |
|---|---|---|
| `chapter_id` | `int` | Existing chapter id 0-7. Must match `load_template_contract_manifest()`. |
| `fund_type_slot` | `FundType | Literal["default"]` | Constraint applies to a fund type slot or default chapter constraint. |
| `must_answer` | `tuple[str, ...]` | Wrapper copy/reference of existing `ChapterContract.must_answer` for audit output context. Use existing manifest values when building constraints. |
| `must_not_cover` | `tuple[str, ...]` | Wrapper copy/reference of existing `ChapterContract.must_not_cover` plus sidecar-specific forbidden claim patterns only where needed. |
| `required_evidence` | `tuple[EvidenceRequirement, ...]` | Evidence requirements for report-writing claims. Each requirement must identify accepted evidence categories and allowed gap semantics. |
| `allowed_na_reason` | `tuple[str, ...]` | Explicit N/A/data-gap reasons allowed for this chapter/fund-type slot. N/A never counts as passing evidence. |
| `failure_behavior` | `FailureBehavior` | How to report missing evidence or forbidden prose: `blocking`, `material`, `informational`, or `config_only`. |

Suggested supporting literals:

```python
RequirementSeverity = Literal["blocking", "material", "informational", "config_only"]
RequirementStatus = Literal["satisfied", "missing", "satisfied_by_data_gap", "not_applicable"]
FailureCategory = Literal[
    "unsupported_stability_claim",
    "required_evidence_missing",
    "forbidden_content",
    "allowed_na_reason_missing",
    "insufficient_evidence_wording_missing",
    "final_judgment_unsupported",
    "deferred_extraction_requirement",
]
```

Suggested dataclasses:

- `EvidenceRequirement`
  - `requirement_id: str`
  - `chapter_id: int`
  - `fund_type_slot: FundType | Literal["default"]`
  - `fact_categories: tuple[str, ...]`
  - `accepted_fact_ids: tuple[str, ...]`
  - `accepted_gap_reason_codes: tuple[str, ...]`
  - `required_wording_fragments: tuple[str, ...]`
  - `severity: RequirementSeverity`
  - `deferred: bool = False`
- `ChapterExecutableConstraint`
  - fields listed in 2.2 required sidecar fields
- `ChapterContractConstraintManifest`
  - `schema_version: str`
  - `source_manifest_template_id: str`
  - `constraints: tuple[ChapterExecutableConstraint, ...]`

### 2.3 Required Constraints in First Slice

All chapters 0-7 must have at least one default `ChapterExecutableConstraint`, but only active Chapter 3 is fully enforced.

Required active Chapter 3 material requirement:

- `chapter_id=3`
- `fund_type_slot="active_fund"`
- requirement id suggested: `chapter_3.active_fund.turnover_style_consistency_evidence`
- required evidence:
  - reviewed turnover fact, or
  - reviewed style-change proxy fact, or
  - explicit `ReportDataGap` with reason compatible with turnover/style-change not reviewed.
- allowed `data_gap` / N/A reasons:
  - `turnover_or_style_change_not_reviewed`
  - `not_reviewed_in_current_slice`
  - `source_unavailable`
  - `not_disclosed_manager_holding` only for manager holding, not for style-stability evidence
- required insufficiency wording fragments must include:
  - insufficient evidence wording that prevents stability inference.
  - next minimum validation question wording.
  - it should consume or compare against `ReportDataGap.required_report_wording`, which is populated from `ReportDataGapOverride.required_report_wording`.

Deferred informational/config requirements:

- Chapter 2 enhanced-index tracking-error / enhanced-deviation evidence:
  - encode in sidecar as `severity="informational"` or `severity="config_only"`.
  - `deferred=True`.
  - tests only assert configuration exists and is not material/blocking.
- Chapter 6 bond duration / credit / leverage / liquidity / drawdown evidence:
  - encode in sidecar as `severity="informational"` or `severity="config_only"`.
  - `deferred=True`.
  - tests only assert configuration exists and is not material/blocking.

## 3. Dev-only Report-writing Audit Contract

### 3.1 Module Boundary

`fund_agent/fund/report_writing_audit.py` is a pure Fund-layer library module.

It must not:

- call `FundDocumentRepository`
- call PDF/cache/source helpers/downloader/source adapters
- call production extractors
- call renderer
- call Service/CLI
- call FQ0-FQ6 quality gate
- create Host/Agent packages
- import or use `dayu.host` / `dayu.engine`

It may:

- import typed models from `fund_agent/fund/report_evidence.py`
- import sidecar constraints from `fund_agent/fund/template/chapter_contract_constraints.py`
- consume explicit in-memory objects or explicit serialized records supplied by caller
- emit findings only

### 3.2 Inputs

The audit should support three explicit input forms:

| Input | Shape | Purpose |
|---|---|---|
| `ReportEvidenceBundle` | Existing dataclass object | Primary dev-only audit input. Use facts, anchors, gaps, score issue links, classified fund type, preferred lens and judgment support metadata already projected into bundle. |
| JSONL | `Iterable[Mapping[str, object]]` or explicit parsed records from caller | Optional helper for dev/eval consumers. It should parse only caller-supplied records. Do not open files unless a later script integration explicitly passes a path. |
| chapter draft surrogate | small typed dataclass or explicit `Mapping` with `chapter_id`, `fund_type_slot`, `markdown`, optional `claim_tags` | Lets tests audit unsafe prose without invoking renderer. This is not product renderer output and not a new rendering path. |

Suggested dataclass:

- `ChapterDraftSurrogate`
  - `chapter_id: int`
  - `fund_type_slot: FundType | Literal["default", "unknown"]`
  - `markdown: str`
  - `claim_tags: tuple[str, ...] = ()`
  - `gap_refs: tuple[str, ...] = ()`
  - `anchor_refs: tuple[str, ...] = ()`

### 3.3 Outputs

The audit output must be deterministic and issue-based.

Suggested dataclasses:

- `ReportWritingAuditIssue`
  - `issue_id: str`
  - `chapter_id: int | None`
  - `fund_type_slot: str`
  - `severity: Literal["blocking", "material", "minor", "informational"]`
  - `failure_category: FailureCategory`
  - `requirement_id: str | None`
  - `message: str`
  - `evidence_requirement_gaps: tuple[str, ...]`
  - `anchor_refs: tuple[str, ...]`
  - `data_gap_refs: tuple[str, ...]`
- `ReportWritingAuditSummary`
  - `issue_count: int`
  - `blocking_count: int`
  - `material_count: int`
  - `minor_count: int`
  - `informational_count: int`
  - `failure_category_counts: tuple[tuple[str, int], ...]`
  - `evidence_requirement_gap_count: int`
- `ReportWritingAuditResult`
  - `schema_version: str`
  - `issues: tuple[ReportWritingAuditIssue, ...]`
  - `summary: ReportWritingAuditSummary`
  - `failed_closed: bool`

Required output behavior:

- Missing required evidence should create issue(s) and list evidence requirement gaps.
- Forbidden content should create issue(s) with `failure_category="forbidden_content"`.
- Unsupported active Chapter 3 stability / consistency / 言行一致 claim without reviewed turnover/style evidence should create material issue.
- Direct buy/sell or position sizing language, if checked by this dev-only audit, should be blocking and report-level.
- Deferred Chapter 2/6 requirements should be informational/config only.

### 3.4 Public API

Keep the public surface small:

```python
def audit_report_writing_bundle(
    bundle: ReportEvidenceBundle,
    *,
    chapter_drafts: tuple[ChapterDraftSurrogate, ...] = (),
) -> ReportWritingAuditResult:
    ...

def audit_report_writing_records(
    records: Iterable[Mapping[str, object]],
    *,
    chapter_drafts: tuple[ChapterDraftSurrogate, ...] = (),
) -> ReportWritingAuditResult:
    ...
```

Do not name the API `run_programmatic_audit`; that name belongs to the existing renderer/programmatic audit path.

## 4. First Implementation Slice

Implement only this material behavior:

### 4.1 active_fund Chapter 3: Insufficient Evidence / Turnover Stability Claim Contract

The audit must detect:

1. `active_fund` + `chapter_3` draft contains stability / style consistency / 言行一致 positive claim.
2. Bundle lacks reviewed turnover evidence and lacks reviewed style-change proxy evidence.
3. Bundle either lacks a data gap, has a data gap without allowed reason, or has a data gap but the draft does not preserve required insufficiency wording.

Expected result:

- Unsupported positive claim -> `material` issue with `failure_category="unsupported_stability_claim"`.
- Missing required evidence with no explicit gap -> `material` issue with `failure_category="required_evidence_missing"`.
- Explicit compatible data gap plus correct insufficiency wording -> no material issue for missing turnover evidence.
- Explicit compatible data gap but missing insufficiency wording in draft -> `material` issue with `failure_category="insufficient_evidence_wording_missing"`.

### 4.2 Chapter 2/6 Deferred Requirements

Implement sidecar config only:

- Chapter 2 enhanced-index tracking-error requirement exists.
- Chapter 6 bond risk-lens requirement exists.
- Both are `deferred=True` and severity informational/config only.
- The audit must not fail a bundle solely because those extraction-dependent facts are missing in this first slice.

## 5. Test Strategy

### 5.1 Required Focused Tests

`tests/fund/template/test_chapter_contract_constraints.py`:

1. `test_sidecar_covers_all_chapter_ids_0_to_7`
   - load existing `load_template_contract_manifest()`
   - load new sidecar manifest
   - assert chapter ids exactly match 0-7
2. `test_sidecar_wraps_existing_chapter_contract_without_parallel_truth`
   - assert sidecar `must_answer` / `must_not_cover` for default constraints are sourced from existing manifest or equal to it.
   - assert no sidecar chapter id exists outside existing manifest.
3. `test_active_chapter_3_turnover_requirement_is_material`
   - assert active Chapter 3 requirement exists, has accepted gap reasons, required wording fragments, and material severity.
4. `test_chapter_2_and_6_deferred_requirements_are_config_only`
   - assert enhanced-index Chapter 2 and bond Chapter 6 requirements are present and deferred informational/config, not blocking/material.

`tests/fund/test_report_writing_audit.py`:

1. `test_active_chapter_3_turnover_missing_blocks_stability_claim`
   - active bundle/draft asserts "风格稳定" or "言行一致".
   - no turnover/style evidence and no data gap.
   - expect material unsupported-stability issue.
2. `test_active_chapter_3_explicit_data_gap_allows_insufficient_evidence_wording`
   - active bundle includes compatible `ReportDataGap.required_report_wording`.
   - draft states insufficient evidence and next minimum validation question.
   - expect no material issue for turnover stability requirement.
3. `test_must_not_cover_hit_emits_issue`
   - draft contains direct motive/personality claim or buy/sell/position sizing phrase covered by `must_not_cover`.
   - expect forbidden-content issue; trading advice should be blocking if included.
4. `test_required_evidence_missing_emits_gap`
   - active Chapter 3 no evidence/no gap/no stability claim.
   - expect required evidence gap issue, because the chapter still cannot satisfy required evidence.
5. `test_valid_minimal_active_chapter_3_case`
   - active bundle has reviewed turnover/style evidence anchor or compatible data gap with correct wording.
   - draft avoids unsupported positive stability claim.
   - expect no blocking/material issues.

### 5.2 Fixture Construction Guidance

Prefer small in-test dataclass builders using existing `ReportEvidenceBundle` types. Do not read annual reports, JSON fixtures, report output files, PDF cache or scratch run artifacts.

When constructing facts/gaps:

- Use deterministic ids.
- Use `chapter_refs=("chapter_3",)` for Chapter 3 facts/gaps.
- Use evidence anchors or `data_gap_refs` explicitly.
- For compatible data gap, use `required_report_wording` that includes the existing accepted wording fragments:
  - "不能据此判断风格稳定、风格一致或言行一致"
  - "下一步最小验证问题："

### 5.3 Coverage Target

New source modules should target >=80% per-file coverage:

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`

If local coverage tooling cannot report per-file coverage in the focused command, the implementation evidence artifact must record the measured alternative and residual risk.

## 6. Acceptance Commands

Focused tests:

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Adjacent tests:

```bash
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Ruff:

```bash
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Whitespace:

```bash
git diff --check
```

Boundary diff:

```bash
git diff --name-only
git diff -- fund_agent/fund/template/renderer.py fund_agent/services fund_agent/ui fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py fund_agent/fund/extraction_score.py fund_agent/fund/documents fund_agent/fund/pdf fund_agent/host fund_agent/agent pyproject.toml README.md fund_agent/README.md fund_agent/fund/README.md docs/design.md docs/implementation-control.md
```

Boundary rg:

```bash
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|FQ0|FQ6|renderer|FundAnalysisService" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Expected boundary result:

- No diff in renderer, Service, UI, quality gate, documents/source helpers, PDF downloader/cache, Host/Agent, product entry points, README/design/control docs.
- No references to Dayu runtime, document repository, PDF/cache/source helpers/downloaders, production extractors, renderer, Service/CLI default flow, FQ0-FQ6.
- No tracked scratch outputs.

## 7. Stop Conditions

The implementation worker must stop and return to controller if any condition occurs:

- Tests require modifying renderer output.
- Tests require wiring findings into FQ0-FQ6 or `quality_gate_policy`.
- Tests require changing Service/CLI default behavior.
- The implementation needs `FundDocumentRepository`, annual-report fetch/parse, PDF/cache/source helpers, source adapters, downloaders or production extractors.
- The implementation needs new `fund_agent/host` or `fund_agent/agent` package, or any `dayu.host` / `dayu.engine` import.
- Active Chapter 3 cannot be audited from current `ReportEvidenceBundle` / data gap / score issue structures without inventing a parallel extraction path.
- Sidecar cannot preserve existing 8 chapter ids and existing `ChapterContract` as the base truth.
- The plan would require modifying README/design/control docs before code/tests pass.

## 8. Residual Risks

| Risk | Handling |
|---|---|
| First slice does not change product Markdown. | Accepted. The point is executable dev-only evidence before renderer changes. |
| Sidecar and template contract may drift. | Require sidecar-vs-existing-manifest tests and fail-closed validation. |
| ReportEvidenceBundle may not carry all possible evidence names. | First material enforcement is only active Chapter 3; other chapters use skeleton/config until later gates. |
| Required evidence and report-quality validator concepts can overlap. | Keep validator on schema/content integrity; keep writing audit on semantic claim safety and evidence sufficiency. |
| Chapter 2 enhanced-index and Chapter 6 bond issues remain unresolved. | They are extraction/reviewed-fact residuals, not first-slice writing fixes. |
| Product renderer may later need wording changes. | Open a later output-changing renderer/report-writing gate only after dev-only audit evidence proves the exact missing wording. |

## 9. Handoff for Next Worker

Start with:

1. Add `fund_agent/fund/template/chapter_contract_constraints.py`.
2. Add `tests/fund/template/test_chapter_contract_constraints.py`.
3. Add `fund_agent/fund/report_writing_audit.py`.
4. Add `tests/fund/test_report_writing_audit.py`.
5. Run focused tests, adjacent tests, ruff, `git diff --check`, boundary diff and boundary rg.
6. Only after tests pass, produce an implementation evidence artifact. Do not update README/design/control docs unless the controller explicitly authorizes the implementation worker to perform current-code-fact doc sync.

Do not:

- `git add`
- commit
- push
- open or mutate GitHub PRs
- promote scratch outputs or fixtures

Final implementation report should state either:

- `IMPLEMENTATION_READY` with commands run and boundary check result, or
- `NEEDS_MORE_EVIDENCE` with the exact stop condition and missing same-source evidence.

## 10. Decision

PLAN_READY.

This plan is code-generation-ready for the next implementation worker: add a Fund-layer sidecar over existing `ChapterContract`, add a dev-only report-writing audit over explicit evidence inputs, fully enforce only active-fund Chapter 3 turnover/style-consistency claim safety, keep Chapter 2/6 extraction-dependent requirements informational/config-only, and preserve all product-flow and architecture boundaries.
