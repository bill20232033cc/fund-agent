# Code Review

## Scope

- Mode: current changes
- Branch: post-merge/pr22-origin-main
- Base: accepted plan commit 293026d (HEAD)
- Output file: docs/reviews/extractor-projection-over-document-representation-code-review-20260618-143548.md
- Included scope: workspace changes in `fund_agent/fund/processors/contracts.py`, `fund_agent/fund/processors/fund_disclosure_dispatch.py`, `tests/fund/processors/test_fund_disclosure_dispatch.py`, `tests/fund/processors/test_registry.py`, `docs/implementation-control.md`, `docs/current-startup-packet.md`
- Excluded scope: other untracked files (not part of this implementation slice), whole-repo ruff format baseline (explicitly out-of-scope per controller judgment), `fund_agent/fund/data_extractor.py`, `fund_agent/fund/documents/models.py`, `fund_agent/fund/extractors/models.py` (not modified)
- Parallel review coverage: 无

## Findings

### 001-未修复-低-admission-helper-dispatch_key-位置参数被丢弃但未做类型一致性校验

- **入口/函数**: `admit_disclosure_intermediate`
- **文件(行号)**: `fund_agent/fund/processors/fund_disclosure_dispatch.py:84-131`
- **输入场景**: 调用方传入 `dispatch_key` 的 `intermediate_kind`、`fund_code`、`report_year` 与 `intermediate` 对象实际值不一致。
- **实际分支**: 函数在第101行执行 `_ = dispatch_key` 后不再读取任何 `dispatch_key` 字段。
- **预期行为**: 按 plan §7.3 设计，身份校验属于后续 concrete processor 的职责，S3 admission helper 不执行身份检查。
- **实际行为**: 当 `dispatch_key.intermediate_kind != intermediate.intermediate_kind` 时，admission helper 照常返回 satisfied/blocked，不会提示类型不匹配。
- **直接证据**: `fund_disclosure_dispatch.py:101` — `_ = dispatch_key` 丢弃参数；`fund_disclosure_dispatch.py:102-130` — 后续所有分支只读 `intermediate` 的属性，不交叉校验 `dispatch_key`。
- **影响**: 仅局部行为 — S3 没有 concrete processor，`dispatch_key` 当前不会被任何调用链路消费。但若后续实现直接复用此函数做 dispatch，可能静默接受类型不匹配的 intermediate。
- **建议改法和验证点**: 不修改代码（plan 已明确身份检查为 processor 职责）。后续 S4 concrete processor 实现 gate 应在 processor.supports() 或 extract() 中校验 `dispatch_key` 与 `intermediate` 的 `fund_code`/`report_year`/`intermediate_kind` 一致性。在 S4 测试中加入 cross-check 用例。
- **修复风险（低）**: 不修代码，无风险。
- **严重程度（低）**: 符合 plan 设计意图，S3 无 concrete consumer，静默失效可能性仅存在于后续误用场景。

### 002-未修复-低-FAILURE_CLASS_ADMISSION_MAP 的 KeyError 路径无测试覆盖

- **入口/函数**: `admit_disclosure_intermediate`
- **文件(行号)**: `fund_agent/fund/processors/fund_disclosure_dispatch.py:103-105`
- **输入场景**: `intermediate.failure_class` 返回非五类标准 Literal 值（例如运行时传入未校验的对象，其 `failure_class` 属性返回了不在 `AnnualReportSourceFailureCategory` 内的字符串）。
- **实际分支**: 第103行 `FAILURE_CLASS_ADMISSION_MAP[intermediate.failure_class]` 触发 `KeyError`。
- **预期行为**: fail-closed（抛出异常而非静默成功），函数 docstring 已声明 `Raises: KeyError`。
- **实际行为**: 抛出 `KeyError`，异常信息为标准 Python dict KeyError，不含业务上下文。
- **直接证据**: `fund_disclosure_dispatch.py:103` — `FAILURE_CLASS_ADMISSION_MAP[intermediate.failure_class]` 无 try/except 包裹；测试文件 `test_fund_disclosure_dispatch.py` 中无 parametrize 覆盖非法 `failure_class` 输入。
- **影响**: 仅局部行为 — 对类型正确（五类标准值或 None）的输入不会触发。运行时若因对象构造缺陷传入非法值，异常传播链缺少业务错误包装，排查时可能不直观。
- **建议改法和验证点**: 不要求修改（当前 `KeyError` 已是 fail-closed）。建议后续 gate 考虑添加一个 negative test：`admit_disclosure_intermediate` 对非法 `failure_class` 字符串抛出 `KeyError`，或在函数内显式包装为更具业务含义的异常。
- **修复风险（低）**: 不修代码，无风险。
- **严重程度（低）**: 类型安全由静态检查保证，运行时触发概率极低；已有 `KeyError` 是 fail-closed 行为。

## Open Questions

- 无。

## Residual Risk

- S3 无 concrete `FundDisclosureDocumentProcessor`；`admit_disclosure_intermediate` 返回的 `DisclosureAdmissionDecision` 当前不被 `FundDataExtractor.extract()` 消费。所有 admission 判定都是纯契约验证，未接入生产 facade。
- `_ = dispatch_key` 丢弃后的 dispatch key / intermediate 身份不一致风险在当前 slice 无消费方，但需在 S4 concrete processor gate 中显式校验。
- 全仓 `ruff format --check fund_agent/ tests/` 仍有 152 个 out-of-scope 文件待格式化，此为 controller judgment 已接受的 baseline residual，不属于本 gate 修复范围。
- 候选路径 `candidate_only`、`field_correctness_status=not_proven`、`source_truth_status=not_proven`、`parser_replacement_authorized=False`、`readiness_status=not_ready` 均未被本次实现提升。Release/readiness 保持 `NOT_READY`。
- `EvidenceSourceKind` 未扩展；`EvidenceAnchor.source_kind` 保持 `annual_report` / `external_api` / `derived`。
