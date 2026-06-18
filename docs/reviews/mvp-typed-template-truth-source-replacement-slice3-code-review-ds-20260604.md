# MVP typed template truth-source replacement Slice 3 code review -- AgentDS

## Review metadata
- Reviewer: AgentDS
- Date: 2026-06-04
- Scope: Slice 3 only (typed_contracts.py 从模板 JSON 投影 typed dataclasses，移除 code-authored typed truth)

## Scope files reviewed
- `fund_agent/fund/template/typed_contracts.py` (working tree, git diff HEAD)
- `tests/fund/template/test_typed_contracts.py` (working tree, git diff HEAD)
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-plan-controller-judgment-20260603.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-controller-judgment-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-controller-judgment-20260604.md`

## Validation

- `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py -q`: 45 passed, exit 0
- `uv run ruff check`: All checks passed
- Manual adversarial edge case verification (orphaned reason, missing-key KeyError, source_manifest=None): all confirmed

---

## Findings

### Finding 1: 缺少必需 JSON key 时抛出 KeyError 而非 ValueError (severity: LOW)

- 位置: `fund_agent/fund/template/typed_contracts.py` 多处 `_project_*` 函数 (e.g. 367 行 `raw_chapter["must_answer"]`)
- 证据: 当模板 JSON 中 chapter 对象缺少 `must_answer`、`must_not_cover` 等必需的顶层 key 时，`_project_typed_chapter` 使用 `raw_chapter["key"]` 直接字典访问，抛出 `KeyError: 'must_answer'` 而非 `ValueError`。经实际运行验证确认。
- 影响: `KeyError` 仍然是 fail-closed（不会返回无效 manifest），但与 `load_typed_template_contract_manifest()` 公开文档声明的 `ValueError` 异常类型不一致，对调用方的异常处理造成困惑。实践中 Slice 2 的 `_load_template_contract_manifest_from_path()` 会对同一 JSON 做结构校验，大部分 missing key 已被 Slice 2 拦截，此路径实际触发概率低。
- 建议: 在 `_project_typed_chapter` 开头对必需 key 做 `if key not in raw_chapter` 检查，统一抛出 `ValueError`。或在调用方 `load_typed_template_contract_manifest` 中 wrap `KeyError` 为 `ValueError`。

### Finding 2: 孤立 `missing_evidence_reason`（behavior 为 None 但 reason 非空）通过校验 (severity: LOW)

- 位置: `fund_agent/fund/template/typed_contracts.py` 782-785 行 (`_validate_required_output_items`)
- 证据: `_validate_required_output_items` 对 `required_output_items` 的校验只有两个 guard:
  1. `when_evidence_missing is not None and missing_evidence_reason is None` → ValueError
  2. `missing_evidence_reason is not None and not missing_evidence_reason.strip()` → ValueError

  当 `when_evidence_missing=None` 且 `missing_evidence_reason="some orphan reason"` 时，两个 guard 均不触发，校验通过。经实际运行验证确认。
- 影响: 模板作者可能在不设置 behavior 的情况下填入 reason，导致数据不一致。运行时该 reason 不会被消费（因为没有关联的 behavior），属于无实际危害的静默数据垃圾。但如果后续代码假定 reason 只在 behavior 非 None 时有意义，可能产生意外行为。
- 建议: 增加第三个 guard：`if item.when_evidence_missing is None and item.missing_evidence_reason is not None: raise ValueError(...)` 确保 behavior 与 reason 双向一致性。

### Finding 3: `_load_raw_template_contract_manifest` 存在冗余文件读取 (severity: LOW)

- 位置: `fund_agent/fund/template/typed_contracts.py` 333-340 行
- 证据: 函数先调用 `contracts_module._load_template_contract_manifest_from_path(template_path)` 做 Slice 2 校验（该函数内部已读取并解析文件），然后 `_load_raw_template_contract_manifest` 再次调用 `template_path.read_text(encoding="utf-8")` 重复读取同一文件。
- 影响: 对同一文件做两次 I/O 读取，轻微效率损失。不是正确性问题，两次读取之间文件内容变化的 TOCTOU 在实际开发场景中无安全影响。
- 建议: 可以考虑直接复用 `contracts_module._load_template_contract_manifest_from_path` 返回的已解析 JSON，或让其暴露 `(text, manifest)` 元组。但需要确保不侵入 Slice 2 的私有 API 边界。当前实现虽不完美但可接受。

---

## 逐项 review 问题回答

### 1. 唯一 authored template truth source

**通过。** `typed_contracts.py` 已完全移除所有 code-authored stable id/text mapping：
- `_CURRENT_TEXT_MAPPING`、`_TextIdMapping`、`_ChapterTextMapping`、`_AUDIT_FOCUS_BY_CHAPTER`、`_CH3_STYLE_EVIDENCE_UNREVIEWED` 及其配套构造/查找函数（`_required_output_missing_behavior`、`_required_output_missing_reason`、`_build_internal_subcontracts`、`_must_not_cover_predicate`、`_must_not_cover_allowed_contexts`、`_project_lens_rules`、`_assert_exact_text_mapping`、`_project_chapter`、`_project_must_not_cover`、`_project_required_output_items`）全部移除。

所有 typed 字段均从 `_load_raw_template_contract_manifest()` 返回的模板 JSON 通过 `_project_*` 系列函数投影而来，无 hardcoded id/text/behavior/audit_focus/subcontract/predicate 残留在 typed 路径中。

类型级别的常量（`SUPPORTED_AUDIT_FOCUS`、`SUPPORTED_MISSING_EVIDENCE_BEHAVIORS` 等）是从 `Literal` 类型推导的闭集定义，属于类型约束而非数据真源，符合预期。

### 2. source_manifest 只做 validation

**通过。** `load_typed_template_contract_manifest(source_manifest)` 中 `source_manifest` 参数仅在 238-239 行用于 compatibility validation：

```python
if source_manifest is not None and source_manifest != current_manifest:
    raise ValueError("source_manifest 与当前模板文档投影不一致")
```

stale/different 输入 fail-closed。传入 `source_manifest=None` 时跳过此检查，所有 typed 字段完全来自模板 JSON。经实际运行验证，`source_manifest=None` 与不传参数产生相同 typed 结果。

### 3. Malformed template fail-closed

**通过，有一个 LOW 级别的异常类型不一致。**

- 非 array chapters（243 行）、非 object 条目（`_read_mapping_array` 965 行）、非 string id/text（`_read_required_string` 1033 行）均 fail-closed 为 `ValueError`。
- 非法 `missing_evidence_missing` behavior、非法 `audit_focus`、非法 predicate status 均被闭集 guard 拒绝为 `ValueError`。
- 未知 `EvidenceRequirementId` 被 `_known_evidence_requirement_ids()` guard 拒绝（733-738 行）。经实际运行验证，未知 requirement id 正确触发 `ValueError`。
- Ch2 internal subcontract 的 `requirement_ids` 通过章节内 clause/item id（887-914 行）和 evidence requirement id（915-924 行）双重 guard。每个 requirement_id 必须同时在两个集合中存在，否则 fail-closed。
- 唯一例外：当模板 JSON 缺少某章节对象下的顶层 key（如 `must_answer`）时抛出 `KeyError` 而非 `ValueError`（见 Finding 1）。

### 4. Public chapter ids 0-7 & deterministic behavior

**通过。**
- `EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))` 保持不变（24 行）。
- `validate_typed_template_contract_manifest` 在 285-286 行校验 `chapter_ids == EXPECTED_PUBLIC_CHAPTER_IDS` 及无重复。
- 模块无 `random`、`time`、LLM、provider、runtime 依赖，行为完全 deterministic。

### 5. 非目标保留

**通过。** 未引入 provider/runtime/Agent/score/golden/readiness 相关代码。变更仅限 `typed_contracts.py` 和 `test_typed_contracts.py`。renderer、Service、Host 层代码未修改。无 live probe 或需要真实 provider credentials 的操作。

### 6. 测试质量

**通过。** Slice 3 新增 6 个测试覆盖：
1. `test_typed_contracts_has_no_code_authored_text_mapping_truth` -- 5 个旧 authored truth symbol 不存在
2. `test_current_typed_projection_matches_template_json_exact_fields` -- typed projection 精确匹配模板 JSON（id/text/behavior/audit_focus/dependencies/subcontracts/predicate）
3. `test_stale_source_manifest_raises_value_error` -- stale source_manifest fail-closed
4. `test_changing_template_json_changes_projected_typed_manifest` -- 模板 JSON 变更驱动 typed projection
5. `test_unknown_template_requirement_id_fails_closed` -- 未知 requirement id fail-closed
6. `test_malformed_typed_values_fail_closed` -- malformed typed 值 fail-closed

所有测试只依赖本地数据（模板文件、fixture），不依赖外部服务。与已有测试共计 14 个 typed tests + 31 个 untyped tests = 45 passed。

### 7. 代码质量

**通过，无安全隐患。**
- 无命令注入：模块无 `subprocess`/`os.system` 调用。
- 无路径遍历风险：`_load_raw_template_contract_manifest` 的 `path` 参数为 `_` 前缀私有参数，公开 API `load_typed_template_contract_manifest` 不暴露 path 参数；默认值固定为 `contracts_module._DEFAULT_TEMPLATE_PATH` 常量。
- JSON reader helpers 无类型混淆漏洞：`_read_required_int` 正确使用 `isinstance(value, bool)` 拒绝 boolean（Python 中 `bool` 是 `int` 子类）；`_read_string_array` 正确检查 `isinstance(item, str)`。
- 无 `eval()`/`exec()` 调用。
- 模块边界清晰：typed_contracts 通过 `contracts_module._load_template_contract_manifest_from_path` 和 `contracts_module._parse_template_contract_manifest_json` 两个私有接口依赖 Slice 2 parser，属于模板解析层的合理内部耦合。如果 Slice 2 私有 helper 重命名，此投影层需同步更新，这在 Slice 3 implementation evidence 的 residual risks 中已有记录。

---

## Summary
- BLOCKING: 0
- HIGH: 0
- MEDIUM: 0
- LOW: 3 (KeyError vs ValueError 不一致、孤立 missing_evidence_reason 未被校验、冗余文件读取)

## Verdict: PASS

Slice 3 实现正确执行了已接受 plan。所有 code-authored typed truth（stable id/text mapping、audit focus、missing behavior/reason、Ch2 internal subcontract construction、Ch3 evidence predicate truth）已移除，typed 字段从模板 JSON 唯一真源投影。source_manifest 仅做 compatibility validation。Malformed 输入 fail-closed。public chapter ids 保持 0-7，deterministic 行为不变。非目标未引入。测试全面且仅依赖本地数据。3 个 LOW findings 均不影响正确性，建议在后续 slice 中视情况修复。
