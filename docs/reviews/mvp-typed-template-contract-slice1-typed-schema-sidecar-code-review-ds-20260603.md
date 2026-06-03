# MVP typed template contract Slice 1 typed schema sidecar code review (AgentDS)

## Reviewer Self-Check

- Role: AgentDS independent code reviewer only.
- Gate: `MVP typed template contract Slice 1 typed schema sidecar implementation gate`.
- Classification: `heavy`.
- Scope: uncommitted diff only for Slice 1 implementation files.
- Actions intentionally not taken: no implementation, no file edits, no commit, no push, no PR.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-controller-judgment-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-controller-judgment-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-implementation-evidence-20260603.md`, `fund_agent/fund/template/contracts.py`, and all six touched files.

## Verdict

**pass-with-risks**

One non-blocking finding (Finding 1: TemplateLensRule naming collision). All eight implementation requirements from the accepted Slice 0 controller judgment are correctly satisfied. Validation (18 passed, ruff clean, git diff --check clean) is consistent with the implementation evidence. No existing runtime, provider, audit, renderer, score, or quality gate behavior is changed.

---

## Material Findings

### Finding 1 (non-blocking): TemplateLensRule 同名类在两个模块中重复定义

**文件/行号:**
- `fund_agent/fund/template/contracts.py:29` — 定义 `contracts.TemplateLensRule`
- `fund_agent/fund/template/typed_contracts.py:133` — 定义 `typed_contracts.TemplateLensRule`
- `fund_agent/fund/template/__init__.py:6` — 只重导出 `contracts.TemplateLensRule`
- `fund_agent/fund/template/typed_contracts.py:1224` — `typed_contracts.__all__` 包含 `TemplateLensRule`

**问题:** `typed_contracts.py` 定义了自己的 `TemplateLensRule` 类，与 `contracts.py` 中已有的 `TemplateLensRule` 同名但属于不同类型（不同模块来源）。两个类虽然字段、类型、默认值完全一致（`fund_type: LensKey`, `statements: tuple[str, ...]`, `facets_any: tuple[str, ...] = ()`, `priority: str | None = None`），但在 Python 类型系统中是不同的 class object。

`TypedChapterContract.preferred_lens` 的类型注解 `Mapping[str, TemplateLensRule]` 解析为 `typed_contracts.TemplateLensRule`，而 `from fund_agent.fund.template import TemplateLensRule` 得到的是 `contracts.TemplateLensRule`。如果调用方用包级 `TemplateLensRule` 对 typed chapter 的 preferred_lens 值做 `isinstance` 检查，会静默返回 `False`。类型检查器（mypy/pyright）也会把两者视为不兼容类型。

**严重程度:** non-blocking。两个类都是 `@dataclass(frozen=True, slots=True)`，字段完全一致，运行时属性访问、相等比较、哈希均正确。`__init__.py` 没有同时重导出两个版本，包级 API 无歧义。当前 typed sidecar 尚未接入 Service/CLI 生产路径，不会触发实际 bug。

**建议:** 在 Slice 2 或 Slice 7（Service facade wiring）之前，将 typed_contracts 中的 `TemplateLensRule` 改为直接复用 `contracts.TemplateLensRule`，或重命名为 `TypedTemplateLensRule`。如果选择复用，需注意 `LensKey` type alias 在两个模块中各自定义但解析相同——也应统一来源。

---

### Finding 2 (non-blocking): get_typed_chapter_contract 每次调用触发全量 manifest 校验

**文件/行号:** `fund_agent/fund/template/typed_contracts.py:648-665`

`get_typed_chapter_contract()` 内部调用 `load_typed_template_contract_manifest()`，后者每次都会执行 `validate_typed_template_contract_manifest()`。如果未来 Service/CLI 路径在单次请求中多次按 chapter_id 取 typed contract，会造成重复校验。

**严重程度:** non-blocking。当前 typed sidecar 仅作为 schema 定义和测试消费，未接入热路径。未来接入时加缓存即可，不影响本 slice 验收。

---

## Focus Area 判定

### 1. additive typed contract schema sidecar 与 loader/projection 正确性

**判定: PASS**

- `typed_contracts.py:22-23` 定义 schema version `typed_chapter_contract.v1` 和 template id `fund-analysis-template-typed-v1`，与当前 contracts id `fund-analysis-template-v1` 区分。
- `load_typed_template_contract_manifest()` (`typed_contracts.py:582-606`) 接收可选 `source_manifest`，缺省时调用 `load_template_contract_manifest()` 从 contracts.py 加载。
- `_project_chapter()` (`typed_contracts.py:668-698`) 逐章投影：先从 `_CURRENT_TEXT_MAPPING` 取 reviewed exact mapping，缺失章节 fail-closed；再分别投影 must_answer / must_not_cover / required_output_items / preferred_lens / audit_focus / dependencies / internal_subcontracts。
- `_assert_exact_text_mapping()` (`typed_contracts.py:900-923`) 做精确元组比较 `source_values != mapped_text`，不一致时抛出 `ValueError("未命中 typed reviewed exact mapping")`。无 fuzzy/substring/embedding/LLM 匹配。

### 2. public chapter ids 0-7 保留；Ch2 内部子契约不公开；Ch0 消费 Ch7 且不独立派生动作

**判定: PASS**

- `EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))` (`typed_contracts.py:24`)。
- `validate_typed_template_contract_manifest()` (`typed_contracts.py:632-633`) 校验 `chapter_ids != EXPECTED_PUBLIC_CHAPTER_IDS` 时抛出，同时校验无重复 (`typed_contracts.py:635-636`)。
- `_build_internal_subcontracts()` (`typed_contracts.py:814-861`) 只在 `chapter_id == 2` 时构造 performance/attribution/cost 三个子契约，其它章节返回空元组。
- `ChapterInternalSubcontract.public_chapter_id` 默认 `None` (`typed_contracts.py:158`)。
- `_validate_internal_subcontracts()` (`typed_contracts.py:1157-1205`) 校验：非 Ch2 有子契约→拒绝；Ch2 子契约顺序不是 `("performance", "attribution", "cost")` →拒绝；任意子契约 `public_chapter_id is not None` →拒绝 (`typed_contracts.py:1184-1185`)。
- `_project_chapter()` 对 Ch0 硬编码 `consumes_chapter_conclusions=(7,)` 和 `independent_action_source=False` (`typed_contracts.py:695-696`)。
- `_validate_dependencies()` (`typed_contracts.py:1131-1134`) 校验 Ch0 必须消费 Ch7 且不得独立派生动作。

### 3. mapping 是显式 reviewed exact mapping，文本漂移 fail-closed

**判定: PASS**

- `_CURRENT_TEXT_MAPPING` (`typed_contracts.py:235-558`) 覆盖全部 8 章，每章包含 must_answer / must_not_cover / required_output_items 的 `_TextIdMapping(text, stable_id)`。
- 已抽样核验 Ch0 must_answer item_01、Ch3 must_not_cover item_04、Ch2 must_answer item_05 与 `contracts.py` `_CHAPTERS` 原文完全一致。
- `_assert_exact_text_mapping()` 使用 `source_values != mapped_text` 精确元组比较，不是 `in`、`startswith`、`SequenceMatcher`、embedding 或 LLM 调用。
- 任何 contracts.py 文本修改（包括空格、标点、措辞）若未同步更新 `_CURRENT_TEXT_MAPPING` 都会 fail-closed。

### 4. fail-closed 校验覆盖

**判定: PASS**

| 校验项 | 位置 | 状态 |
|---|---|---|
| schema_version 不匹配 | `typed_contracts.py:623-624` | fail-closed |
| template_id/source_template_id/source_path 空白 | `typed_contracts.py:625-630` | fail-closed |
| 公开章节 id 非精确 0..7 | `typed_contracts.py:633-634` | fail-closed |
| 章节 id 重复 | `typed_contracts.py:635-636` | fail-closed |
| clause_id 跨章重复 | `typed_contracts.py:644-645` | fail-closed |
| clause_id 章内重复 | `typed_contracts.py:982-983` | fail-closed |
| clause_id 空或前缀不稳定 | `typed_contracts.py:985-988` | fail-closed |
| clause text 空 | `typed_contracts.py:989-990` | fail-closed |
| required_output item_id 重复 | `typed_contracts.py:1061-1062` | fail-closed |
| required_output item_id 空或前缀不稳定 | `typed_contracts.py:1064-1067` | fail-closed |
| required_output text 空 | `typed_contracts.py:1068-1069` | fail-closed |
| when_evidence_missing 不在闭集 | `typed_contracts.py:1072-1077` | fail-closed |
| audit_focus 空或不在闭集 | `typed_contracts.py:1150-1154` | fail-closed |
| allowed_contexts 不在闭集 | `typed_contracts.py:1012-1013` | fail-closed |
| evidence predicate statuses 不在闭集 | `typed_contracts.py:1038-1040` | fail-closed |
| 依赖 id 未知 | `typed_contracts.py:1128-1130` | fail-closed |
| Ch0 未消费 Ch7 或 independent_action_source=True | `typed_contracts.py:1131-1134` | fail-closed |
| Ch2 子契约 requirement_id 未知 | `typed_contracts.py:1196-1205` | fail-closed |
| preferred_lens statements 空或含空值 | `typed_contracts.py:1098-1101` | fail-closed |
| lens key 与 fund_type 不一致 | `typed_contracts.py:1096-1097` | fail-closed |

全部校验均为 fail-closed（抛出 `ValueError`），无 warn-and-continue 或 silent-default 路径。

### 5. 现有 manifest / renderer / auditor / deterministic analyze/checklist / --use-llm fail-closed 行为不变

**判定: PASS**

- `typed_contracts.py` 只从 `contracts.py` 导入并读取数据（`ChapterContract`, `TemplateContractManifest`, `load_template_contract_manifest`），不修改 contracts 模块状态。
- `_project_lens_rules()` (`typed_contracts.py:790-811`) 只从已有 `ChapterContract.preferred_lens` 做字段对字段投影，不改变源数据。
- `__init__.py` 新增 typed imports 放在已有 imports 之后 (`__init__.py:38-53`)，不替换或遮蔽已有名称。
- `__init__.__all__` 新增 7 个 typed 名称（`ChapterInternalSubcontract`, `EvidencePredicate`, `MustAnswerClause`, `MustNotCoverClause`, `RequiredOutputItem`, `TypedChapterContract`, `TypedTemplateContractManifest` 等），保留所有已有导出。
- 测试 `test_typed_contract_loader_does_not_mutate_current_manifest` (`test_typed_contracts.py:176-216`) 验证 typed loader 前后当前 manifest 对象同一性 (`is`) 和内容等价性 (`==`) 均不变。
- 验证命令 `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py` 18 passed 确认现有 contracts 测试和 typed 测试均通过。

### 6. 无 provider/runtime/default/budget/endpoint 等越界

**判定: PASS**

- 新增文件中无 `httpx`、`openai`、`anthropic`、`requests`、`aiohttp` 导入。
- 无 `timeout`、`retry`、`budget`、`endpoint`、`base_url`、`api_key`、`model` 字符串。
- 无 `FUND_AGENT_LLM_` 环境变量引用。
- 无 `FundDocumentRepository`、`FundDataExtractor`、PDF/cache/source helper 导入。
- 无 `Service`、`Host`、`Agent`、`dayu` 导入。
- 无 `score`、`golden`、`readiness`、`promotion`、`snapshot` 引用。
- 无 `extra_payload`、`**kwargs`、untyped dict payload bag。

### 7. 包导出命名：typed sidecar 是否造成公开命名回归

**判定: PASS-WITH-FINDING**（见 Finding 1）

- `__init__.py` 只重导出 `contracts.TemplateLensRule`（行 6），不重导出 `typed_contracts.TemplateLensRule`。
- 包级 `from fund_agent.fund.template import TemplateLensRule` 行为不变——始终得到 `contracts.TemplateLensRule`。
- 无已有公开 API 被移除或重命名。
- Finding 1 描述的同名类风险属于未来维护风险，当前不触发运行时 bug。

### 8. 测试和 README 充分且不过度声称

**判定: PASS**

测试覆盖（8 个测试用例，均在 `tests/fund/template/test_typed_contracts.py`）:

| 测试 | 覆盖点 | 状态 |
|---|---|---|
| `test_typed_manifest_preserves_public_chapter_ids_0_to_7` | 公开 id 0-7、Ch2 子契约、非 Ch2 无子契约 | PASS |
| `test_typed_manifest_rejects_ch2_public_subchapter_ids` | Ch2 子契约携带 public_chapter_id 被拒绝、非法 Ch2 public split 被拒绝 | PASS |
| `test_ch0_consumes_ch7_and_has_no_independent_action_source` | Ch0 依赖 Ch7、无 independent action、缺 Ch7 依赖 fail-closed、有独立动作 fail-closed | PASS |
| `test_required_output_item_ids_are_unique` | 重复 required output item_id fail-closed | PASS |
| `test_audit_focus_literals_are_closed_and_do_not_imply_programmatic_disable` | audit_focus 闭集、`AUDIT_FOCUS_IS_SEMANTIC_ONLY=True`、不支持的值 fail-closed | PASS |
| `test_typed_contract_loader_does_not_mutate_current_manifest` | 当前 manifest 不被 typed loader 改变（对象同一性和内容等价性） | PASS |
| `test_unknown_dependency_ids_fail_closed` | 未知依赖 id fail-closed | PASS |
| `test_non_ch2_internal_subcontracts_fail_closed` | 非 Ch2 章节携带内部子契约 fail-closed | PASS |

README 更新:

- `fund_agent/fund/README.md:114-121`：新增 typed sidecar 描述段落，声明 additive、public chapter ids 0-7、Ch2 子契约内部性、Ch0 依赖 Ch7、exact mapping fail-closed、audit_focus 语义性。全部为当前已实现事实，无未来 overclaim。
- `tests/README.md:49`：新增一行 `test_typed_contracts.py` 目录条目。描述准确限于 additive loader、Ch2 子契约、Ch0 依赖、required output id 唯一、audit_focus 闭集和当前 manifest 非突变。

## Adversarial Failure Pass

以下 adversarial 场景已通过或已有防护：

| 场景 | 结果 |
|---|---|
| contracts.py 文本被意外修改（加空格、改标点） | `_assert_exact_text_mapping` fail-closed |
| contracts.py 新增第 8 章（9 章 manifest） | `chapter_ids != EXPECTED_PUBLIC_CHAPTER_IDS` fail-closed |
| contracts.py 重排章节顺序 | `chapter_ids != (0,1,2,3,4,5,6,7)` fail-closed |
| Ch2 子契约被设置 public_chapter_id=20 | `_validate_internal_subcontracts` fail-closed |
| 新增非 Ch2 章节的内部子契约 | `_validate_internal_subcontracts` fail-closed |
| Ch0 consumes_chapter_conclusions 被设为空或不含 7 | `_validate_dependencies` fail-closed |
| Ch0 independent_action_source 被设为 True | `_validate_dependencies` fail-closed |
| typed clause_id 在 must_answer 和 must_not_cover 之间重复 | 跨章 clause_id 去重检查 fail-closed |
| audit_focus 被设为 `"disable_programmatic"` | 闭集检查 fail-closed |
| evidence predicate status 被设为 `"unknown_status"` | 闭集检查 fail-closed |
| allowed_context 被设为 `"llm_judgment"` | 闭集检查 fail-closed |
| 依赖 id 指向不存在的章节（如 99） | 未知依赖检查 fail-closed |
| required_output item_id 前缀不稳定（非 `ch{n}.required_output.`） | 前缀检查 fail-closed |
| clause_id 前缀不稳定（非 `ch{n}.must_answer.` / `ch{n}.must_not_cover.`） | 前缀检查 fail-closed |
| `_CURRENT_TEXT_MAPPING` 缺少某个章节 | `_project_chapter` 中 `text_mapping is None` fail-closed |

## 项目指令检查

对照 `AGENTS.md` 硬约束：

| 约束 | 状态 |
|---|---|
| 用中文回答 | N/A（本 artifact 面向 controller，是结构化 review） |
| 第一性原理思考 | PASS — 从 Slice 0 preconditions 和 contracts.py 原始文本出发逐条核验 |
| 找 root cause 逻辑/数据同源 | PASS — 所有判定引用精确文件/行号 |
| CHAPTER_CONTRACT 设计目标（最低认知负担做对下一步） | PASS — typed schema 稳定 clause/item id 降低后续推理器认知负担 |
| 基金文档存取只通过统一文档仓库接口 | PASS — 本 slice 不读取任何文档 |
| 禁止直接操作文件系统 | PASS — 本 slice 不涉及文件系统 |
| 禁止把显式参数放 extra_payload | PASS — 所有 typed 字段均为显式 dataclass 属性 |
| 基金类型判断优先于通用分析 | N/A — 本 slice 不涉及基金分析 |
| 证据必须可溯源 | PASS — 每个 finding 引用精确文件/行号 |

## Overcoupling 检查

| 检查项 | 结果 |
|---|---|
| typed_contracts 是否直接依赖 Service/Host/Agent 层 | 否 — 只依赖 `fund_agent.fund.fund_type` 和 `fund_agent.fund.template.contracts` |
| typed_contracts 是否绕过 contracts 直接读取 docs/ 或模板真源 | 否 — 只通过 `load_template_contract_manifest()` 读取 |
| typed_contracts 是否引入新的外部依赖 | 否 — 只使用 stdlib `dataclasses`、`typing` |
| __init__.py 新增导出是否与已有导出冲突 | Finding 1 描述的同名风险；包级 API 无冲突 |

## 结论

本 slice 正确实现了 Slice 0 controller judgment 授权的全部 Slice 1 范围：

- additive typed schema sidecar（`typed_contracts.py`）严格从当前 `contracts.py` manifest 投影，不替换模板真源；
- 公开章节 id 精确保持 0-7；
- Ch2 内部子契约 performance/attribution/cost 只作为 chapter_id=2 内部数据结构，不泄露为公开章节；
- Ch0 声明 `consumes_chapter_conclusions=(7,)` 且 `independent_action_source=False`；
- `audit_focus` 是 closed-set semantic-only 数据，`AUDIT_FOCUS_IS_SEMANTIC_ONLY=True`；
- 所有 fail-closed 校验覆盖 duplicate ids、unknown deps、required output 唯一性、stable prefix、closed literals；
- 现有 contracts.py manifest、renderer、auditor、deterministic analyze/checklist、--use-llm fail-closed 行为均不变；
- 无 provider/runtime/default/budget/endpoint、Agent runtime/tool-loop、score/golden/readiness、文档仓库/PDF/cache/source-helper 访问；
- 测试 8 个用例覆盖关键路径和边缘场景，README 更新仅描述已实现事实。

Finding 1（TemplateLensRule 同名类）是唯一的非阻塞发现：`typed_contracts.py` 和 `contracts.py` 各定义了结构相同但类型不同的 `TemplateLensRule` 类。当前不触发运行时 bug，建议在 Slice 2 或 Slice 7 之前解决（复用 contracts 版本或重命名 typed 版本）。

**Verdict: pass-with-risks**

Risk owner: Slice 2/Slice 7 implementation. Risk: 如果 typed_contracts.TemplateLensRule 和 contracts.TemplateLensRule 长期并存，后续类型检查器和 isinstance 使用可能产生静默错误。

---

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
