# MVP typed template truth-source replacement Slice 3 code review — AgentMiMo

## Review metadata
- Reviewer: AgentMiMo
- Date: 2026-06-04
- Scope: Slice 3 only
- Files reviewed:
  - `fund_agent/fund/template/typed_contracts.py`
  - `tests/fund/template/test_typed_contracts.py`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-plan-controller-judgment-20260603.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-controller-judgment-20260604.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-controller-judgment-20260604.md`

## Validation reproduced

- `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py -q` → **45 passed in 0.79s**, exit 0
- `uv run ruff check fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py` → **All checks passed!**, exit 0
- `git diff --check` scoped to changed files → exit 0, no whitespace errors
- `git diff HEAD` full review of all changed lines → complete diff verified

## Question-by-Question Assessment

### Q1: 唯一 authored truth source
- 结论: **PASS**
- 证据:
  - `_CURRENT_TEXT_MAPPING` (old L115-L438): 完全删除 (diff hunks at L115-L438)。旧 module 含约 300 行硬编码文本→id 映射，已全部移除。
  - `_TextIdMapping` dataclass (old L98-L104): 完全删除 (diff L98-L104)。
  - `_ChapterTextMapping` dataclass (old L107-L113): 完全删除 (diff L107-L113)。
  - `_AUDIT_FOCUS_BY_CHAPTER` (old L440-L449): 完全删除 (diff L440-L449)。audit_focus 现由 `_read_string_array(raw_chapter["audit_focus"])` 从模板 JSON 投影 (new L382-L389)。
  - `_CH3_STYLE_EVIDENCE_UNREVIEWED` (old L451-L458): 完全删除 (diff L451-L458)。Ch3 evidence predicate 现由 `_project_evidence_predicate` 从 `raw_predicate["applies_when"]` 投影 (new L583-L618)。
  - `_required_output_missing_behavior()` (old L733-L757): 完全删除 (diff L733-L757)。缺证行为现从 `raw_chapter["required_output_items"][*]["when_evidence_missing"]` 读取 (new L488-L490)。
  - `_required_output_missing_reason()` (old L760-L790): 完全删除 (diff L760-L790)。缺证原因现从 `raw_chapter["required_output_items"][*]["missing_evidence_reason"]` 读取 (new L497-L502)。
  - `_build_internal_subcontracts()` (old L867-L935): 完全删除 (diff L867-L935)。Ch2 内部子契约现由 `_project_internal_subcontracts` 从 JSON 投影 (new L545-L580)。
  - `_project_chapter()` 硬编码 `consumes_chapter_conclusions=(7,) if chapter_id == 0 else ()` (old L558-L559): 已删除。现由 `_read_int_array(raw_chapter["consumes_chapter_conclusions"])` 从 JSON 投影 (new L391-L394)。
  - `_project_chapter()` 硬编码 `independent_action_source=False` (old L560): 已删除。现由 `_read_required_bool(raw_chapter, "independent_action_source")` 从 JSON 投影 (new L396-L399)。
  - `_assert_exact_text_mapping()` (old L1005-L1034): 完全删除。不再需要 text→mapping 精确匹配函数。
  - `_must_not_cover_predicate()` (old L938-L953) / `_must_not_cover_allowed_contexts()` (old L959-L980): 完全删除。predicate 和 allowed_contexts 现从 JSON 中的 `applies_when` 和 `allowed_contexts` 字段直接投影 (new L448-L466)。
  - 测试 `test_typed_contracts_has_no_code_authored_text_mapping_truth` (test L53-L72) 通过源码文件内容检查确认五大旧符号不存在于源文件中。
  - 新引入的 code-authored 值仅有 schema 常量 (`TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION`、`TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID`、`EXPECTED_PUBLIC_CHAPTER_IDS`) 和 Literal type 闭集定义 (`SUPPORTED_AUDIT_FOCUS` 等) —— 这些是 validation gate 常量而非模板内容真源。

### Q2: source_manifest 只做 validation
- 结论: **PASS**
- 证据:
  - `load_typed_template_contract_manifest()` (L220-L257): `source_manifest` 参数唯一使用点在第 238-239 行: `if source_manifest is not None and source_manifest != current_manifest: raise ValueError(...)` —— 纯粹 compatibility validation。
  - stale source_manifest fail-closed: 第 238-239 行，`source_manifest != current_manifest` 比较失败直接 raise ValueError。
  - `source_manifest=None` 时: 第 238 行 `if source_manifest is not None` 为 False，跳过校验，直接进入 `_load_raw_template_contract_manifest()` (L241)。
  - typed 字段全部来自 raw JSON: `schema_version` (L246), `template_id` (L247), `source_template_id` (L248-L251), `source_path` (L253), `chapters` (L254) 全部从 `raw_manifest` 的字段读取，不使用 `source_manifest`。
  - 测试 `test_stale_source_manifest_raises_value_error` (test L140-L161) 验证 stale manifest 触发 ValueError。
  - 测试 `test_changing_template_json_changes_projected_typed_manifest` (test L164-L183) 验证 JSON 修改反映到 typed 投影，不受 source_manifest 影响。

### Q3: Malformed template 是否全面 fail-closed
- 结论: **PASS** (含 2 个 MEDIUM findings)
- 逐项检查:

| 场景 | 状态 | 证据 |
|------|------|------|
| chapters 不是 array | PASS | `_read_mapping_array` L959：`if not isinstance(value, list): raise ValueError`。`load_typed_template_contract_manifest` L242-L244 有顶层 check。 |
| 单章不是 object | PASS | `_read_mapping_array` L965：`if not isinstance(item, dict): raise ValueError`。 |
| chapter_id 不是 integer | PASS | `_read_required_int` L1078：`if not isinstance(value, int) or isinstance(value, bool): raise ValueError`。 |
| must_answer 不是 array 或为空 | PASS | `_project_must_answer_entries` L422 调用 `_read_mapping_array(..., allow_empty=False)`。L961 拒绝空数组。 |
| must_not_cover 不是 array 或为空 | PASS | `_project_must_not_cover_entries` L446 调用 `_read_mapping_array(..., allow_empty=False)`。 |
| required_output_items 不是 array 或为空 | PASS | `_project_required_output_entries` L486 调用 `_read_mapping_array(..., allow_empty=False)`。 |
| 条目 id/text 不是非空字符串 | PASS | `_read_required_string` L1034：`if not isinstance(value, str) or not value.strip(): raise ValueError`。 |
| when_evidence_missing 是非法值 | PASS | `_validate_required_output_items` L774-L781：`if item.when_evidence_missing not in SUPPORTED_MISSING_EVIDENCE_BEHAVIORS`。 |
| audit_focus 包含非法 literal | PASS | `_validate_audit_focus` L860-L862：`if focus not in SUPPORTED_AUDIT_FOCUS`。 |
| allowed_contexts 包含非法 literal | PASS | `_validate_must_not_cover_clause` L709-L711：`if context not in SUPPORTED_ALLOWED_CONTEXTS`。 |
| applies_when 有 predicate 但没有 allowed_contexts | PASS | `_validate_must_not_cover_clause` L703-L706：新增 check `if not clause.allowed_contexts: raise ValueError`。 |
| allowed_contexts 有值但没有 applies_when | PASS | `_validate_must_not_cover_clause` L707-L708：新增 check `elif clause.allowed_contexts: raise ValueError`。 |
| evidence predicate requirement_id 不在 _KNOWN_REQUIREMENT_IDS | PASS | `_validate_evidence_predicate` L732-L739：对每个 requirement_id 检查 `if requirement_id not in known_requirement_ids`。 |
| preferred_lens 的 fund_type 不是合法 LensKey | **MEDIUM finding** | `_project_typed_lens_rules` L530-L532 用 `cast(LensKey, _read_required_string(...))` 读取 fund_type，但 `cast` 没有运行时校验。`_validate_preferred_lens` L803 只检查 `key != rule.fund_type`，不校验 fund_type 是否属于 `FundType` 枚举或 `"default"`。非法 fund_type 可通过校验。详见 Finding M1。 |
| Ch2 internal subcontract requirement_id 检查 | **MEDIUM finding** | `_validate_internal_subcontracts` L905-L924 对每个 subcontract 的 requirement_ids 做了两次独立 check：先检查是否全在 `known_chapter_requirement_ids`（L905-L914），再检查是否全在 `known_evidence_requirement_ids`（L915-L924）。这意味着 requirement_id 必须同时在两个集合中（AND 语义），而非"在章节 clause/item id 或 evidence guard 中"（OR 语义）。当前 Ch2 数据恰好满足 AND（所有 ch2.must_answer.item_* / ch2.required_output.item_* 都在 `EvidenceRequirementId` Literal 中），但该 AND 逻辑过度约束，可能拒绝对未来 subcontract 的合法扩展。详见 Finding M2。 |
| template_id 与 typed constant 不匹配 | PASS | `validate_typed_template_contract_manifest` L277-L278：`if manifest.template_id != TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID: raise ValueError`。旧逻辑只检查 `not manifest.template_id.strip()`，新逻辑更严格地校验与 typed constant 精确匹配。 |
| schema_version 与 typed constant 不匹配 | PASS | `validate_typed_template_contract_manifest` L275-L276：`if manifest.schema_version != TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION: raise ValueError`。 |

### Q4: Public chapter ids 0-7 & deterministic
- 结论: **PASS**
- 证据:
  - `EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))` (L24)：闭集 {0,1,2,3,4,5,6,7}。
  - `validate_typed_template_contract_manifest` L284-L288：`if chapter_ids != EXPECTED_PUBLIC_CHAPTER_IDS` 精确比对（含顺序）；`if len(set(chapter_ids)) != len(chapter_ids)` 检查重复。
  - Ch0 依赖 Ch7：`_validate_dependencies` L839：`if chapter.chapter_id == 0 and dependencies != (7,): raise ValueError` —— 精确要求 `(7,)`，不允许空或额外依赖。测试 `test_ch0_consumes_ch7_and_has_no_independent_action_source` (test L261-L294) 验证。
  - Ch2 唯一有 internal_subcontracts：`_validate_internal_subcontracts` L879-L881：`if chapter.chapter_id != 2: if chapter.internal_subcontracts: raise ValueError`。L884-L885: `if subcontract_ids != ("performance", "attribution", "cost"): raise ValueError`。测试 `test_typed_manifest_preserves_public_chapter_ids_0_to_7` L50 验证非 Ch2 章节无子契约。
  - 无随机性：所有投影使用 tuple、frozenset、zip 等确定性操作。无 random/shuffle/set iteration order 依赖。

### Q5: 非目标不侵入
- 结论: **PASS**
- 证据:
  - 无 provider/runtime/Agent/score/golden/readiness 导入或引用。所有 import 限于 stdlib (`pathlib`, `typing`) 和 `fund_agent/fund` 内部模块 (`contracts`、`fund_type`、`evidence_availability` lazy import)。
  - `__init__.py` 未修改：`git diff HEAD -- fund_agent/fund/template/__init__.py` 无输出。
  - renderer、Service、Host 未修改。
  - `contracts.py` 未修改：Slice 3 仅从 `contracts.py` 导入现有类型和私有 helper 函数；不修改 contracts.py 源码。
  - `typed_contracts.py` 调用 `contracts_module._DEFAULT_TEMPLATE_PATH`、`contracts_module._load_template_contract_manifest_from_path()`、`contracts_module._parse_template_contract_manifest_json()` —— 这些是同一 `fund/template` 包内的私有函数调用，不违反模块边界。

### Q6: 安全与边界
- 结论: **PASS** (含 2 个 LOW findings)
- 逐项检查:

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 路径遍历 | **LOW finding** | `_load_raw_template_contract_manifest(path)` L333 接受可选 path 参数并直接 `Path(path)`。该参数为私有函数参数，公开 API (`load_typed_template_contract_manifest`、`get_typed_chapter_contract`) 不暴露 path 参数。path 未做 resolve/validation，但不可通过公开 API 注入用户输入。详见 Finding L1。 |
| JSON injection / 类型混淆 | PASS | JSON 解析使用 stdlib `json.loads`（via `contracts_module._parse_template_contract_manifest_json`）。所有投影值都通过 strict reader helper 做类型检查和 strip 校验。无 eval/exec/template injection。 |
| lazy import 循环导入 | **LOW finding** | `_known_evidence_requirement_ids()` L937 使用 lazy import `from fund_agent.fund.evidence_availability import _KNOWN_REQUIREMENT_IDS`。`evidence_availability.py` 存在 module-level import `from fund_agent.fund.template.typed_contracts import ...`。形成 `typed_contracts ↔ evidence_availability` 双向依赖。lazy import 避免了模块级 ImportError，但 import 顺序敏感。详见 Finding L2。 |
| 模块边界 | PASS | 所有 import 限于 Agent 层 `fund_agent/fund` 包内。无 Service/Host/UI 导入。符合 AGENTS.md 第 89-139 行模块边界约束。`typed_contracts.py` 位于 `fund_agent/fund/template/`，属于 "CHAPTER_CONTRACT 解析" 能力明确规定的位置（AGENTS.md L138）。 |

### Q7: 测试覆盖
- 结论: **PASS** (含 1 个 LOW finding)
- 新增 6 个测试逐一评估:

| 测试 | 覆盖场景 | 状态 |
|------|----------|------|
| `test_typed_contracts_has_no_code_authored_text_mapping_truth` | 代码 authored truth 符号不存在 | PASS：通过 `Path.read_text()` 读取源文件并 assert 五大旧符号不在文件中。验证了 `_CURRENT_TEXT_MAPPING`、`_TextIdMapping`、`_ChapterTextMapping`、`_AUDIT_FOCUS_BY_CHAPTER`、`_CH3_STYLE_EVIDENCE_UNREVIEWED` 均不存在。 |
| `test_current_typed_projection_matches_template_json_exact_fields` | JSON→typed 精确投影 | PASS：对全部 8 章的 schema_version、template_id、source_template_id、source_path、must_answer id/text、required_output id/text、when_evidence_missing/missing_evidence_reason、audit_focus、consumes_chapter_conclusions、independent_action_source、internal_subcontracts 全部字段做逐字段 equality assert。还单独验证 Ch3 predicate 的 4 个字段。 |
| `test_stale_source_manifest_raises_value_error` | stale source_manifest | PASS：构造 stale manifest（修改 Ch0 title），传入 `load_typed_template_contract_manifest()`，assert ValueError 带正确错误信息。 |
| `test_changing_template_json_changes_projected_typed_manifest` | JSON 修改影响 typed 投影 | PASS：通过 monkeypatch `_load_raw_template_contract_manifest` 返回修改后的 JSON，验证 typed manifest 反映 JSON 变化。排除了 source_manifest 或代码 mapping 作为真源。 |
| `test_unknown_template_requirement_id_fails_closed` | 未知 evidence requirement id | PASS：在 Ch3 predicate 的 requirement_ids 注入 `ch3.requirement.unknown_reviewed`，assert ValueError。 |
| `test_malformed_typed_values_fail_closed` | 非法 typed 值 | PASS：将 Ch3 required_output_items[1] 的 when_evidence_missing 改为 `silent_skip`（不在闭集中），assert ValueError。 |

- Helper `_mutable_raw_manifest()` (test L454-L470)：PASS。调用 `typed_contracts._load_raw_template_contract_manifest()` 获取 raw JSON，`deepcopy()` 做深拷贝，断言返回值为 dict。功能正确。
- Helper `_replace_typed_chapter()` (test L473-L494)：PASS。使用 `dataclasses.replace` 构造新的 typed manifest 并替换指定章节。
- **遗漏关键负面测试**: LOW finding。以下 validation path 缺少专门负面测试：template_id 与 typed constant 不匹配、schema_version 不匹配、chapters 顶层不是 array、preferred_lens fund_type 不是合法 LensKey（与 M1 相关）、applies_when 有 predicate 但没有 allowed_contexts、allowed_contexts 有值但没有 applies_when、audit_focus 为空。详见 Finding L3。

## Findings

### Finding M1: preferred_lens fund_type 缺少 LensKey 闭集校验
- Severity: MEDIUM
- Location: `typed_contracts.py` L530-L532, `_validate_preferred_lens` L801-L813
- Description: `_project_typed_lens_rules` 使用 `cast(LensKey, _read_required_string(...))` 读取 fund_type。`cast` 是类型提示级别操作，不做运行时校验。`_validate_preferred_lens` L803 只校验 `key != rule.fund_type`（dictionary key 与 fund_type 字段一致性），不校验 fund_type 是否属于 `FundType` 枚举值或 `"default"`。这意味着模板 JSON 中 `fund_type: "invalid_type"` 可通过所有校验。
- Impact: 非法 fund_type 值会流入 typed manifest，下游消费者（如 `resolve_preferred_lens`）可能产生 KeyError 或静默使用错误 lens。
- Recommendation: 在 `_validate_preferred_lens` 中增加对 `rule.fund_type` 的闭集校验，例如 `if rule.fund_type not in get_args(LensKey): raise ValueError(...)`。

### Finding M2: Ch2 internal subcontract requirement_ids 过度约束（AND vs OR）
- Severity: MEDIUM
- Location: `typed_contracts.py` L887-L924
- Description: `_validate_internal_subcontracts` 对 subcontract 的 requirement_ids 做了两次独立 checker：先检查全在 `known_chapter_requirement_ids`（L905-L914），再检查全在 `known_evidence_requirement_ids`（L915-L924）。这意味着每个 requirement_id 必须同时存在于两个集合中（AND 语义），而非 OR 语义。当前 Ch2 所有 requirement_ids (`ch2.must_answer.item_01-06`, `ch2.required_output.item_01-07`) 恰好同时在两个集合中（因为 `EvidenceRequirementId` Literal 包含了所有 Ch2 子句 id），所以测试通过。但如果在 subcontract 中使用了仅在 `known_chapter_requirement_ids` 中存在但不在 `EvidenceRequirementId` 中的合法子句 id，该 validation 会 false-positive reject。
- Impact: 限制 Ch2 internal subcontract 只能引用同时是 EvidenceRequirementId 的子句 id。未来 Ch2 扩展时可能 reject 合法 subcontract。
- Recommendation: 将两次 check 合并为一个 OR check：`if requirement_id not in known_chapter_requirement_ids and requirement_id not in known_evidence_requirement_ids`，或明确文档化 AND 语义的设计意图。

### Finding L1: _load_raw_template_contract_manifest path 参数无路径遍历防护
- Severity: LOW
- Location: `typed_contracts.py` L320-L340
- Description: `_load_raw_template_contract_manifest(path)` 接受可选 path 参数并直接 `Path(path)`，未做 resolve/验证/沙箱化。该参数为私有函数参数，不在任何公开 API（`load_typed_template_contract_manifest`、`get_typed_chapter_contract`）的调用路径中暴露。当前唯一调用来源是测试中不带参数的 `_load_raw_template_contract_manifest()`（走默认路径）。
- Impact: 如果有代码（即使是同一 package 内的测试或内部工具）传入不受信任的路径，可能读取任意文件。
- Recommendation: 对 path 做 `resolve()` 并验证其在 repo root 下，或直接移除 path 参数（当前无内部使用场景需要非默认路径）。

### Finding L2: typed_contracts ↔ evidence_availability 双向 import
- Severity: LOW
- Location: `typed_contracts.py` L937 (lazy import), `evidence_availability.py` L20-L23 (module-level import)
- Description: `typed_contracts.py._known_evidence_requirement_ids()` 使用 lazy import `from fund_agent.fund.evidence_availability import _KNOWN_REQUIREMENT_IDS`。`evidence_availability.py` 有 module-level import `from fund_agent.fund.template.typed_contracts import TypedTemplateContractManifest, load_typed_template_contract_manifest`。形成双向依赖。lazy import 防止了模块级 ImportError，但 import 顺序仍然敏感。如果未来 `evidence_availability.py` 在 module-level 就调用 `load_typed_template_contract_manifest()`，会在 typed_contracts 完成 import 前触发循环。
- Impact: 潜在的 import order dependent bug；重构时容易被触发。
- Recommendation: 考虑提取 `_KNOWN_REQUIREMENT_IDS` 到一个独立的常量模块（如 `fund_agent/fund/evidence_requirement_ids.py`），打破循环依赖。

### Finding L3: 多个 validation path 缺少专门负面测试
- Severity: LOW
- Location: `tests/fund/template/test_typed_contracts.py`
- Description: 以下 fail-closed 校验路径缺少独立负面测试：
  - template_id 与 `TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID` 不匹配（`validate_typed_template_contract_manifest` L277-L278）
  - schema_version 与 `TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION` 不匹配（L275-L276）
  - chapters 顶层不是 array（L242-L244）
  - preferred_lens fund_type 非法（与 M1 关联）
  - applies_when 有 predicate 但没有 allowed_contexts（L703-L706）
  - allowed_contexts 有值但没有 applies_when（L707-L708）
  - audit_focus 为空数组（L858-L859）
- Impact: 上述 fail-closed 路径仅有代码层面的 ValueError raise，没有被测试覆盖的 evidence。模板 JSON 格式变化时缺少 regression 保护。
- Recommendation: 在后续 Slice 或专项测试 pass 中补充覆盖。

### Finding L4: _load_raw_template_contract_manifest 存在双重文件读取和 TOCTOU 风险
- Severity: LOW
- Location: `typed_contracts.py` L334-L336
- Description: `_load_raw_template_contract_manifest` 内部先调用 `contracts_module._load_template_contract_manifest_from_path(template_path)`（L335）做 untyped 校验，然后重新 `template_path.read_text()`（L337）再 `_parse_template_contract_manifest_json`（L340）。这意味着同一文件被读取两次，且两次读取之间存在 TOCTOU 窗口——如果模板文档在两次读取之间被外部修改，typed 投影可能基于不同于 untyped 校验通过版本的文件内容。
- Impact: 极低概率的时序问题；仅在模板文档被外部进程同时修改时可能触发。实用影响可忽略。
- Recommendation: 接受为已知 residual risk；或改为让 `_load_template_contract_manifest_from_path` 返回 raw manifest 而非整形后的 untyped manifest，避免二次读取。

## Summary
- BLOCKING: 0
- HIGH: 0
- MEDIUM: 2 (M1, M2)
- LOW: 4 (L1, L2, L3, L4)

## Verdict: PASS-WITH-RISKS

All code-authored typed truth sources (`_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, `_CH3_STYLE_EVIDENCE_UNREVIEWED`, `_required_output_missing_behavior`, `_required_output_missing_reason`, `_build_internal_subcontracts`, 硬编码 `consumes_chapter_conclusions=(7,)` / `independent_action_source=False`) have been completely removed. All typed fields now project from the template JSON's canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block.

The `source_manifest` parameter is correctly reduced to compatibility validation only. The 6 new tests all pass and cover their claimed scenarios. 45 total tests (typed + untyped) pass with zero failures.

Two MEDIUM findings require attention but are not blocking for Slice 3 acceptance:
- M1: preferred_lens fund_type value is not validated against the LensKey closed set (cast-only, no runtime guard).
- M2: Ch2 internal subcontract requirement_id checks use AND logic instead of OR logic, over-restricting future subcontract expansion.

These findings should be addressed before or during Slice 4 (typed consumer regression) per the accepted plan.
