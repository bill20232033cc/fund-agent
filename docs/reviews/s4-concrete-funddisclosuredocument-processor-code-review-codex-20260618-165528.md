# Code Review

## Findings

### 001-未修复-[中]-fully-gapped 字段族仍携带非空 value，偏离 accepted plan 的空值合同
- **入口/函数**: `FundDisclosureDocumentProcessor.extract()` satisfied path / candidate-boundary admitted path，经 `_missing_field_family()` 构造六个字段族。
- **文件(行号)**: `fund_agent/fund/processors/fund_disclosure_processor.py:165`, `fund_agent/fund/processors/fund_disclosure_processor.py:278`
- **输入场景**: `active_fund + annual_report + fund_disclosure_document.v1` dispatch key，`intermediate` 身份一致，`admit_disclosure_intermediate()` 返回 `admitted=True`；包括非候选 satisfied 路径和 candidate boundary admitted-but-blocked 路径。
- **实际分支**: `extract()` 在 admission admitted 后执行 `field_families = tuple(_missing_field_family(...))`，`_missing_field_family()` 为每个 `FundFieldFamilyResult` 写入 `value={"schema_version": family_id}`。
- **预期行为**: accepted S4 plan 明确要求 fully-gapped result 中六个字段族均为 `status="missing"`、`extraction_mode="missing"`、空 anchors、一个 `field_family_missing` gap，并且 `value={}`；S4 不实现 `FundDisclosureDocument` schema，也不输出任何字段族提取 payload。
- **实际行为**: 当前 missing 字段族的 `value` 不是空对象，而是含 `schema_version` 的非空 dict。现有测试只断言 `status`、`extraction_mode`、anchors、gap 和 result-level gaps，没有断言 `family.value == {}`。
- **直接证据**: accepted plan 在 `docs/reviews/s4-concrete-funddisclosuredocument-processor-plan-ds-20260618.md:152-155` 写明 satisfied path 的字段族 `empty value={}`；实现于 `fund_agent/fund/processors/fund_disclosure_processor.py:281` 返回 `value={"schema_version": family_id}`；测试 `tests/fund/processors/test_fund_disclosure_processor.py:536-542` 未检查 value 为空。
- **影响**: S4 的 fully-gapped skeleton 会对外暴露非空字段族 payload。虽然当前未接入 `FundDataExtractor.extract()` facade，但后续 S5 若按非空 `value` 做 schema/payload presence 判断，可能把“schema gate 前无字段输出”的状态误读为已有字段族 schema payload，削弱 NOT_READY / fully-gapped 边界。
- **建议改法和验证点**: 将 `_missing_field_family()` 的 `value` 改为 `{}`，或由 controller 明确修订 accepted plan 允许 missing 字段族携带 metadata-only `schema_version`。同步补充 satisfied 与 candidate-boundary 两条测试，断言所有 missing family 的 `value == {}` 或断言修订后的唯一允许键集合。
- **修复风险（低/中/高）**: 低。S4 processor 尚未进入 production facade；改动只影响新 processor 的 missing payload shape 和对应测试。
- **严重程度（低/中/高/严重）**: 中

## Open Questions

- `ActiveFundAnnualProcessor` 对字段族 `value` 使用 `schema_version` 作为既有形状，但 accepted S4 plan 对 `FundDisclosureDocumentProcessor` 明确写了 `value={}`。controller 需要裁决 S4 是否必须严格遵守空 value，还是允许沿用 active processor 的 metadata-only shape。

## Residual Risk

- 本轮只 review 用户列出的 S4 implementation files 和 required context；未审查 scope 外 untracked residue。
- 已运行 no-live scoped tests：`uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/processors/test_registry.py tests/fund/processors/test_fund_disclosure_dispatch.py -q`，结果 `48 passed in 0.38s`。
- 未运行 live/network/PDF/FDR/Docling/pdfplumber/provider/LLM/analyze/checklist/golden/readiness/release 命令。

## Scope

- Mode: current changes
- Branch or PR: `post-merge/pr22-origin-main`
- Base: `main`
- Output file: `docs/reviews/s4-concrete-funddisclosuredocument-processor-code-review-codex-20260618-165528.md`
- Included scope:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `fund_agent/fund/processors/registry.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
  - `tests/fund/processors/test_registry.py`
  - `fund_agent/fund/README.md`
  - `docs/reviews/s4-concrete-funddisclosuredocument-processor-implementation-evidence-20260618.md`
- Required context read:
  - `AGENTS.md`
  - `docs/reviews/s4-concrete-funddisclosuredocument-processor-plan-ds-20260618.md`
  - `docs/reviews/s4-concrete-funddisclosuredocument-processor-plan-controller-judgment-20260618.md`
  - `fund_agent/fund/processors/contracts.py`
  - `fund_agent/fund/processors/fund_disclosure_dispatch.py`
  - `fund_agent/fund/processors/active_annual.py`
  - `tests/fund/processors/test_fund_disclosure_dispatch.py`
- Excluded scope: unrelated pre-existing untracked residue; live/network/PDF/FDR/Docling/pdfplumber/provider/LLM/analyze/checklist/golden/readiness/release paths and commands.
- Parallel review coverage: 无。
