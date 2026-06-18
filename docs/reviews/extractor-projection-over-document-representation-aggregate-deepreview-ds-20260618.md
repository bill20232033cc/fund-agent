# Extractor Projection Over Document Representation — Aggregate Deepreview (DS)

## Scope

- Mode: current changes
- Branch: post-merge/pr22-origin-main
- Review range: 293026d..HEAD (2 commits)
- Commits reviewed:
  - `9387224` feat: add fund disclosure admission helper
  - `2605ef2` docs: close extractor projection slice commit
- Output file: docs/reviews/extractor-projection-over-document-representation-aggregate-deepreview-ds-20260618.md
- Included scope:
  - `fund_agent/fund/processors/contracts.py` — `FundDisclosureDocumentIntermediate` protocol
  - `fund_agent/fund/processors/fund_disclosure_dispatch.py` — admission helper (new)
  - `tests/fund/processors/test_fund_disclosure_dispatch.py` — no-live contract tests (new)
  - `tests/fund/processors/test_registry.py` — `fund_disclosure_document.v1` unsupported test
  - `fund_agent/fund/README.md` — S3 current-implementation boundary sync
  - `docs/implementation-control.md` — gate advancement to aggregate deepreview
  - `docs/current-startup-packet.md` — gate pointer update
  - `docs/reviews/extractor-projection-over-document-representation-implementation-evidence-20260618.md`
  - `docs/reviews/extractor-projection-over-document-representation-implementation-controller-judgment-20260618.md`
  - `docs/reviews/extractor-projection-over-document-representation-code-review-20260618-143548.md`
  - `docs/reviews/extractor-projection-over-document-representation-code-review-20260618-143927.md`
  - `docs/reviews/extractor-projection-over-document-representation-code-review-controller-judgment-20260618.md`
  - `docs/reviews/extractor-projection-over-document-representation-accepted-slice-commit-controller-judgment-20260618.md`
- Excluded scope: `fund_agent/fund/data_extractor.py` (confirmed unchanged), `fund_agent/fund/documents/models.py` (confirmed unchanged), `fund_agent/fund/extractors/models.py` (confirmed unchanged), Service/UI/Host/Agent/renderer/quality-gate code, whole-repo ruff format baseline residual (out-of-scope per controller judgment)
- Parallel review coverage: 无

## Specific Check Results

| # | Check | Result | Direct Evidence |
|---|---|---|---|
| 1 | Pure processor-contract/admission-helper slice | PASS | `fund_disclosure_dispatch.py:1-7` module docstring declares scope; only imports from `contracts.py`; no fallback/processor/facade/registry/repository behavior |
| 2 | No `FundDataExtractor.extract` facade change | PASS | `git diff 293026d..HEAD -- fund_agent/fund/data_extractor.py` produces 0 lines |
| 3 | No repository behavior change | PASS | No source acquisition, live/network code modified in diff |
| 4 | No `EvidenceSourceKind` / `EvidenceAnchor.source_kind` expansion | PASS | `git diff 293026d..HEAD -- fund_agent/fund/extractors/models.py` produces 0 lines; test `test_no_candidate_only_leaks_to_public_evidence_source_kind` asserts `"candidate_only" not in get_args(EvidenceSourceKind)` |
| 5 | No production `FundDisclosureDocumentStub` or `documents/models.py` contamination | PASS | `git diff 293026d..HEAD -- fund_agent/fund/documents/models.py` produces 0 lines; stub is local to `test_fund_disclosure_dispatch.py:28-38` with docstring "不导出到生产模型" |
| 6 | Binding amendment branch order: failure_class → missing source_provenance → candidate_boundary → satisfied | PASS | `fund_disclosure_dispatch.py:102-130` — exact precedence chain matching controller judgment §Binding Amendment |
| 7 | Failure taxonomy maps only to existing processor gap codes | PASS | `FAILURE_CLASS_ADMISSION_MAP` uses `unsupported_intermediate`, `candidate_boundary_blocked`; `admit_disclosure_intermediate` additionally uses `source_provenance_unsafe`; all exist in `FundExtractionGapCode` Literal (`contracts.py:43-60`) |
| 8 | Tests cover fail-closed, candidate no-promotion, no-leak, default registry unsupported | PASS | 16 dispatch tests + 2 registry tests: 5 failure class parametrized, 2 precedence, 1 candidate boundary, 1 happy path, 1 no-leak, 1 map completeness, 1 import isolation, 1 unsupported registry, 1 legacy preservation; `32 passed in 0.71s` |
| 9 | README records current implementation facts only, no source truth/readiness/parser replacement claims | PASS | `fund_agent/fund/README.md:77` explicitly states S3 admission helper "也不证明 source truth、字段正确性、parser replacement、golden/readiness 或 release 状态" |
| 10 | Full-repo ruff format baseline residual preserved, no broad formatting | PASS | Focused `ruff format --check` for 4 implementation files → `4 files already formatted`; whole-repo format baseline residual not closed in this gate |
| 11 | No undeclared live/source/PDF/Docling/pdfplumber/provider/LLM/readiness/release expansion | PASS | Diff contains no live/network/PDF/Docling/pdfplumber/provider/LLM import or invocation; no readiness/release status change |
| 12 | Release/readiness remains NOT_READY | PASS | Controller judgment explicitly states `NOT_READY`; README confirms; implementation evidence confirms |

## Validation

All commands executed against committed state (9387224 + 2605ef2):

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/ -v --tb=short` | `32 passed in 0.71s` |
| `uv run pytest --tb=short -q` | `1807 passed in 6.52s` |
| `uv run ruff check fund_agent/ tests/` | `All checks passed!` |
| `uv run ruff format --check fund_agent/fund/processors/contracts.py fund_agent/fund/processors/fund_disclosure_dispatch.py tests/fund/processors/test_fund_disclosure_dispatch.py tests/fund/processors/test_registry.py` | `4 files already formatted` |
| `git diff --check 293026d..HEAD` | No whitespace errors |

## Findings

### 001-已处置-低-dispatch_key-参数被保留但未使用

- **入口/函数**: `admit_disclosure_intermediate`
- **文件(行号)**: `fund_agent/fund/processors/fund_disclosure_dispatch.py:101`
- **输入场景**: `dispatch_key` 与 `intermediate` 的 `intermediate_kind` / `fund_code` / `report_year` 不一致。
- **实际分支**: `_ = dispatch_key` — 参数被显式丢弃，不参与任何判定。
- **预期行为**: Plan §7.2-7.3 明确身份检查为 processor 职责；S3 保留参数边界但不使用。
- **直接证据**: `fund_disclosure_dispatch.py:101` 行 `_ = dispatch_key`；函数体后续所有分支只读 `intermediate` 属性。
- **影响**: S3 无 concrete consumer，无功能影响。S4 集成时需在 processor 层校验一致性。
- **处置**: Controller judgment `ACCEPT_CODE_REVIEW_WITH_NONBLOCKING_RESIDUALS` 已接受为 S3 design boundary；carry to S4 residual。本 gate 不要求修改。
- **严重程度（低）**: 符合 plan 设计意图，已由 controller 裁决接受。

### 002-已处置-低-FAILURE_CLASS_ADMISSION_MAP-KeyError-路径无显式测试

- **入口/函数**: `admit_disclosure_intermediate`
- **文件(行号)**: `fund_agent/fund/processors/fund_disclosure_dispatch.py:103-105`
- **输入场景**: `intermediate.failure_class` 返回非五类标准 Literal 值。
- **实际分支**: `FAILURE_CLASS_ADMISSION_MAP[intermediate.failure_class]` 触发 `KeyError`。
- **预期行为**: 函数 docstring 声明 `Raises: KeyError`。
- **直接证据**: `fund_disclosure_dispatch.py:103` 无 try/except；测试无非法 `failure_class` parametrize。
- **影响**: 类型正确的输入不会触发；运行时若出现非法值则以 `KeyError` fail-closed。
- **处置**: Controller judgment 已接受为 S3 fail-closed 行为；显式 negative test 或 wrapped exception 可 defer 到后续 gate。本 gate 不要求修改。
- **严重程度（低）**: 静态类型检查保证正常路径安全，异常路径 fail-closed。

## Open Questions

- 无。

## Residual Risk

- S3 无 concrete `FundDisclosureDocumentProcessor`；`admit_disclosure_intermediate` 返回的 `DisclosureAdmissionDecision` 当前不被任何生产调用链路消费。
- `dispatch_key` 的 `intermediate_kind` / `fund_code` / `report_year` 与 `intermediate` 对象属性的一致性校验 deferred 到 S4 concrete processor gate。
- 全仓 `ruff format --check fund_agent/ tests/` 仍有 152 个 out-of-scope 文件待格式化，为 controller judgment 已接受的 baseline residual。
- 候选路径 `candidate_only`、`field_correctness_status=not_proven`、`source_truth_status=not_proven`、`parser_replacement_authorized=False`、`readiness_status=not_ready` 均未被提升。Release/readiness 保持 `NOT_READY`。
- `EvidenceSourceKind` 未扩展；`EvidenceAnchor.source_kind` 保持 `annual_report` / `external_api` / `derived`。
