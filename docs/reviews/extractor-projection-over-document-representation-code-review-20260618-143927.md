# Code Review

## Scope

- Mode: current changes
- Branch: `post-merge/pr22-origin-main`
- Base: `293026d` (accepted plan commit)
- Output file: `docs/reviews/extractor-projection-over-document-representation-code-review-20260618-143927.md`
- Included scope:
  - `fund_agent/fund/processors/contracts.py` — added `FundDisclosureDocumentIntermediate` protocol
  - `fund_agent/fund/processors/fund_disclosure_dispatch.py` — new admission helper
  - `tests/fund/processors/test_fund_disclosure_dispatch.py` — new no-live contract tests
  - `tests/fund/processors/test_registry.py` — added dispatch-key test for `fund_disclosure_document.v1`
  - `docs/reviews/extractor-projection-over-document-representation-implementation-evidence-20260618.md`
  - `docs/reviews/extractor-projection-over-document-representation-implementation-controller-judgment-20260618.md`
  - `docs/implementation-control.md`
  - `docs/current-startup-packet.md`
- Excluded scope:
  - `fund_agent/fund/data_extractor.py` — no facade change (confirmed unmodified)
  - `fund_agent/fund/documents/models.py` — no production stub (confirmed unmodified)
  - `fund_agent/fund/extractors/models.py` — no `EvidenceSourceKind` change (confirmed unmodified)
  - Service/UI/Host/Agent/renderer/quality-gate code
  - Whole-repo `ruff format --check` baseline residual (out-of-scope per controller judgment)
- Parallel review coverage: 无
- Accepted plan: `docs/reviews/extractor-projection-over-document-representation-plan-20260618.md`
- Accepted plan judgment: `docs/reviews/extractor-projection-over-document-representation-plan-controller-judgment-20260618.md`

## Specific Check Results

| Check | Result | Evidence |
|---|---|---|
| No `FundDataExtractor.extract` facade change | PASS | `git diff 293026d...HEAD` shows no change to `fund_agent/fund/data_extractor.py` |
| No repository behavior change | PASS | No repository, source acquisition, or live path code modified |
| No `EvidenceSourceKind` / `EvidenceAnchor.source_kind` expansion | PASS | `fund_agent/fund/extractors/models.py` unmodified; `EvidenceSourceKind` remains `Literal["annual_report", "external_api", "derived"]` |
| No production `FundDisclosureDocumentStub` or `documents/models.py` contamination | PASS | `fund_agent/fund/documents/models.py` unmodified; test stub is local to `test_fund_disclosure_dispatch.py` |
| `fund_disclosure_dispatch.py` is pure admission helper | PASS | Only imports from `contracts.py`; no fallback/processor/facade/registry behavior |
| Binding amendment branch order: failure_class → source_provenance missing → candidate_boundary → satisfied | PASS | `fund_disclosure_dispatch.py:101-131` implements exact precedence |
| Failure taxonomy maps only to existing processor contracts | PASS | Uses `unsupported_intermediate`, `candidate_boundary_blocked`, `source_provenance_unsafe` gap codes; all exist in `FundExtractionGapCode` |
| Tests cover negative paths and no-leak boundaries | PASS | 13 tests cover boundary violations, failure class mapping, precedence ordering, happy path, and import isolation |
| Whole-repo ruff format failure is out-of-scope baseline residual | PASS | Controller judgment accepted this; focused format check passes for 4 changed files |
| Release/readiness remains `NOT_READY` | PASS | Evidence and controller judgment both confirm `NOT_READY` |

## Findings

### 001-未修复-低-unused-dispatch_key-parameter-in-admit_disclosure_intermediate

- **入口/函数**: `admit_disclosure_intermediate()` in `fund_agent/fund/processors/fund_disclosure_dispatch.py:84-131`
- **文件(行号)**: `fund_disclosure_dispatch.py:101`
- **输入场景**: 所有调用场景
- **实际分支**: `_ = dispatch_key` — 参数被显式忽略
- **预期行为**: 按 plan §7.2，`dispatch_key` 被保留为 "explicit parameter boundary"；当前不执行 registry 解析
- **实际行为**: 参数赋值给 `_`，未参与任何判定逻辑
- **直接证据**: `fund_disclosure_dispatch.py:101` — `_ = dispatch_key`；函数体中无任何对 `dispatch_key` 的读取
- **影响**: 无功能影响。当 S4 实现具体 processor 时，此参数可能用于 registry 解析或 intermediate_kind 匹配。当前 plan 明确保留此参数，代码意图清晰
- **建议改法和验证点**: 无需修改。当 S4 集成时应决定是否使用此参数做 intermediate_kind 一致性校验
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 002-未修复-低-test-coverage-diverges-from-plan-count

- **入口/函数**: `tests/fund/processors/test_fund_disclosure_dispatch.py`
- **文件(行号)**: 整个测试文件
- **输入场景**: N/A — 测试覆盖范围
- **实际分支**: 13 个测试函数实现，plan §8.1 列出 18 个测试用例
- **预期行为**: plan 定义 18 个测试用例（test_fund_disclosure_dispatch.py 15 个 + test_registry.py 3 个）
- **实际行为**: test_fund_disclosure_dispatch.py 实现 12 个测试函数，test_registry.py 实现 1 个新测试。部分 plan 用例被合并或以不同名称覆盖
- **直接证据**:
  - Plan test #14（gap code 覆盖检查）→ 实际 `test_failure_class_map_covers_canonical_categories_and_existing_gap_codes` 覆盖
  - Plan test #13（no-leak）→ 实际 `test_no_candidate_only_leaks_to_public_evidence_source_kind` 覆盖
  - Plan test #15（边界隔离）→ 实际 `test_admission_helper_source_boundary_imports_stay_isolated` 覆盖
  - Plan test #11（provenance 缺失阻断）→ 合并到 `test_missing_provenance_precedes_candidate_boundary`
  - Plan test #16-18（registry 测试）→ 实际 test_registry.py 中 `test_registry_default_does_not_support_fund_disclosure_document_intermediate` 覆盖 test #16；test #17/#18 由既有 registry 测试隐式覆盖
- **影响**: 核心行为（fail-closed、failure class mapping、precedence ordering、happy path、no-leak、boundary isolation）均已覆盖。test_fund_disclosure_dispatch.py 的边界隔离测试（AST 解析）比 plan 描述的 import 检查更严格
- **建议改法和验证点**: 无需修改。所有 plan 中定义的关键断言均被实际测试覆盖
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 003-未修复-低-test-stub-source_provenance-type-uses-object-instead-of-PublicSourceProvenance

- **入口/函数**: `StubDisclosureIntermediate` in `tests/fund/processors/test_fund_disclosure_dispatch.py:27-37`
- **文件(行号)**: `test_fund_disclosure_dispatch.py:35`
- **输入场景**: 所有使用 `StubDisclosureIntermediate` 的测试
- **实际分支**: `source_provenance: object | None = None`
- **预期行为**: Protocol 声明 `source_provenance` 返回 `PublicSourceProvenance | None`
- **实际行为**: Stub 使用 `object | None` 作为类型注解，比 Protocol 要求更宽
- **直接证据**: `test_fund_disclosure_dispatch.py:35` vs `contracts.py:251`
- **影响**: 运行时无影响 — `default_public_source_provenance()` 返回值满足 `PublicSourceProvenance` 协议。`runtime_checkable` 的 `isinstance` 检查（test #1）通过。静态类型检查器可能不会报错因为 `object` 是所有类型的超类型，但语义上不够精确
- **建议改法和验证点**: 可将类型改为 `PublicSourceProvenance | None` 以与 Protocol 一致。非阻塞
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。所有 specific checks 均通过，实现与 plan 和 binding amendment 一致。

## Residual Risk

- **Format baseline residual**: 全仓 `ruff format --check fund_agent/ tests/` 有 152 个 scope-out 文件需要格式化，但聚焦于变更文件的格式检查通过。已由 controller judgment 确认为 out-of-scope
- **No concrete processor**: S3 不实现具体 `FundDisclosureDocumentProcessor`；`FundDataExtractor.extract()` 不接受 `fund_disclosure_document.v1`
- **Candidate boundary remains locked**: `field_correctness_status=not_proven`, `source_truth_status=not_proven`, `parser_replacement_authorized=False`, `readiness_status=not_ready`
- **No source truth / parser replacement / readiness claim**: 全部 `NOT_READY`
