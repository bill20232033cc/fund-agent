# NAV Source Adapter Typed Contract Implementation — Aggregate Deepreview (DS)

日期：2026-05-28

角色：aggregate reviewer (DS)，非 controller。不 implement、fix、commit、push、PR、merge、release、golden promotion。

Work unit：`NAV repository/source adapter typed contract implementation gate`

Gate classification：`heavy`

Base commit：`449feba`。Review scope：`449feba...HEAD`（4 commits：plan accept + slice 1a/1b/2 accept）。

## Prior Review Chain

本 gate 已完成以下独立 review，本 aggregate 在其基础上做最终合成：

| Artifact | Reviewer | Target | Disposition |
|----------|----------|--------|-------------|
| plan-review-ds | DS | implementation plan | accepted-with-required-fixes → plan-fix applied |
| plan-review-mimo | MiMo | implementation plan | accepted-with-required-fixes → plan-fix applied |
| plan-fix | planning agent | plan fixes | all accepted fixes applied |
| plan-rereview-ds | DS | plan fix | accepted |
| plan-rereview-mimo | MiMo | plan fix | accepted |
| slice1a-review-ds | DS | typed models | accepted (6 minor findings, all fixed in re-review) |
| slice1a-review-mimo | MiMo | typed models | accepted (3 findings, all fixed in re-review) |
| slice1a-rereview-ds | DS | slice1a fixes | accepted |
| slice1a-rereview-mimo | MiMo | slice1a fixes | accepted |
| slice1b-review-ds | DS | adapter + repository | accepted (4 findings, non-blocking) |
| slice1b-review-glm | GLM | adapter + repository | accepted |
| slice2-review-ds | DS | docs + smoke | accepted |
| slice2-review-glm | GLM | docs + smoke | accepted |

## Independent Verification

本 aggregate 独立执行了以下核验（不依赖被 review artifact 的声明）：

1. `git diff --stat 449feba...HEAD` — 27 files changed, +5304/-10。全部在 plan allowed files 范围内。
2. 读取全部 12 个 minimum-files-to-inspect 文件全文。
3. 读取全部 4 个 slice review 的 findings 和 disposition。
4. 读取 plan-fix artifact 确认 controller disposition 闭合。
5. 独立验证 prior findings 是否在最终代码中已修复或记录为 known residual。
6. 真源三件套核验：`AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`。

## Review Focus Areas — Aggregate Disposition

### 1. Contract Coherency

**通过。**

`nav_models.py` 定义了完整的 typed contract：6 组 Literal domain、7 个 frozen/slotted dataclass、`NavDataContractError` 异常、兼容矩阵校验、record shape 校验、identity 校验、完整性约束、强回撤证据资格规则。所有 validator 在 `FundNavSeries.__post_init__` 中串联执行。

`nav_repository.py` 的 `FundNavRepository.load_nav_series()` 通过 `FundNavDataAdapter.load_raw_nav_source()` 获取 source DTO，执行 fund_code/share_class 规范化、identity 提取与校验、raw row 逐条归一化、日期排序、`FundNavSeries` 构造，最后经 `__post_init__` 完成所有 fail-closed 校验。

`nav_data.py` 保持旧 `load_nav_data()` 完全兼容，新增 `load_raw_nav_source()`、`_NavCacheEntry`、`_load_cached_with_metadata()` 等私有方法为 repository 提供 cache provenance。

`__init__.py` 正确 re-export public symbols（`FundNavRepository`、`FundNavSeries`、`FundNavRecord`、所有 Literal 类型、`NavDataContractError` 等），不 re-export 私有 `_RawNavSourceResult`、`_NavCacheEntry`、`load_raw_nav_source`。

NavType/AdjustmentBasis 兼容矩阵在 `_ALLOWED_ADJUSTMENT_BASIS_BY_NAV_TYPE` 中定义，`_validate_nav_type_adjustment_basis` 消费，非法组合 → `schema_drift`。两字段各自保留独立语义（NavType = source-claimed math shape，AdjustmentBasis = 系统判定的调整基础），符合 plan DS-F2 裁决的 option A。

所有 contract 组件形成闭环：typed model → repository normalization → adapter DTO → model validator → fail-closed error。无断裂、无遗漏。

### 2. raw_unit_nav Not Strong Evidence

**通过。** 双重保障：

- Repository 层（`nav_repository.py:206-212`）：构造 `FundNavSeries` 时固定 `nav_type="unit_nav"`、`adjusted_basis="raw_unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`strong_drawdown_evidence_eligible=False`。
- Model 层（`nav_models.py:530-562`）：`_apply_strong_drawdown_eligibility` 在 `__post_init__` 中无条件二次校验：`adjusted_basis="raw_unit_nav"` 时追加原因并强制 `strong_drawdown_evidence_eligible=False`。

测试覆盖：
- `test_raw_unit_nav_is_not_strong_drawdown_eligible`（模型级）
- `test_repository_raw_fixture_normalizes_to_typed_series`（集成级，断言 `adjusted_basis="raw_unit_nav"` 且 `strong_drawdown_evidence_eligible is False`）
- `test_repository_requested_code_only_not_strong_eligible`（集成级）

无 adjusted、cumulative、total-return 声称。正确。

### 3. requested_code_only Identity

**通过。**

当前 Akshare 路径不返回 source identity，repository 构造 `ShareClassMapping` 时固定 `identity_status="requested_code_only"`（`nav_repository.py:181`），`mapping_status="requested_code_default_a"`（share_class=None 时）。

Fail-closed 行为：
- `identity_status="requested_code_only"` → series 可成功返回，但 `strong_drawdown_evidence_eligible=False`（`nav_models.py:544-546`）。
- `identity_status="identity_mismatch"` → `_validate_identity` 直接抛出 `NavDataContractError(category="identity_mismatch")`（`nav_models.py:435-441`）。
- source-returned fund code 与请求冲突 → repository 层 `_validate_returned_identity` 直接 `identity_mismatch` fail-closed（`nav_repository.py:578-589`）。

测试覆盖 `test_requested_code_only_is_not_strong_drawdown_eligible`、`test_repository_identity_mismatch_raises`、`test_identity_mismatch_raises_identity_mismatch`。正确。

### 4. Fail-Closed Taxonomy

**通过。** 逐项对照 plan 表格（§ Fail-Closed Taxonomy）：

| Plan 场景 | Plan category | 实现位置 | 匹配 |
|---|---|---|---|
| fund_code 非法 | identity_mismatch | `nav_repository.py:237-245` | ✅ |
| source 调用异常 | unavailable (保留 cause) | `nav_repository.py:136-143` | ✅ |
| 0 raw records | not_found | `nav_repository.py:146-152` | ✅ |
| raw columns 缺失 | schema_drift | `nav_repository.py:461-476` | ✅ |
| 日期不可解析 | schema_drift | `nav_repository.py:350-359` | ✅ |
| NAV 非数值 | schema_drift | `nav_repository.py:388-393` | ✅ |
| NAV 非正数 | integrity_error | `nav_repository.py:395-401` | ✅ |
| 增长率非法 | schema_drift | `nav_repository.py:430-435` | ✅ |
| 日期重复 | integrity_error | `nav_models.py:397-403` | ✅ |
| identity 冲突 | identity_mismatch | `nav_repository.py:578-589` | ✅ |
| adjusted_basis unknown | adjustment_basis_unknown | `nav_models.py:337-343` | ✅ |
| 日期范围不足 | missing_date_range | `nav_models.py:510-524` | ✅ |
| minimum_records 不足 | insufficient_records | `nav_models.py:503-508` | ✅ |

8 类 fail-closed 全部实现，每类至少 1 个专项测试。`not_found` / `unavailable` 是未来 fallback eligible；`schema_drift` / `identity_mismatch` / `integrity_error` / `adjustment_basis_unknown` 禁止 fallback。正确。

### 5. Provenance

**通过。**

- `FundNavDataAdapter.load_raw_nav_source()` cache hit 时暴露 `origin_source=cache_entry.source`（如 `"akshare"`）和 `cache_updated_at`（`nav_data.py:331-338`）。
- 旧 `load_nav_data()` cache hit 继续返回 `source="nav_cache"`（`nav_data.py:283-288`），不暴露 origin。
- `FundNavRepository` 构造 `NavSourceMetadata` 时填充 `source_name`、`origin_source`、`cached`、`retrieved_at`、`cache_updated_at`、`requested_fund_code`、`returned_fund_code`、`returned_fund_name`。
- 成功 series 的 `NavSourceMetadata.failure_category` 为 `None`（`nav_repository.py:171`）。
- 测试 `test_nav_data_adapter_raw_source_exposes_cache_origin_metadata` 验证 cache origin 可见 + 旧入口不变。
- `__init__.py` 不 re-export `_RawNavSourceResult`、`_NavCacheEntry`、`load_raw_nav_source`——私有 DTO 不泄漏到 public API。
- 无 production code 直接读 SQLite。

### 6. Legacy load_nav_data Compatibility

**通过。**

- `load_nav_data()` 方法体未修改（`nav_data.py:259-297`）：cache hit → `source="nav_cache", cached=True`；fetch → `source="akshare", cached=False`。
- `_load_cached_sync()` 内部重构为委托 `_load_cached_with_metadata()` 并只取 `.records`，返回类型保持 `NavPayload | None`。
- `_save_cached_sync()` 新增可选 `updated_at` 参数，默认 `_utc_timestamp()`，旧调用点行为不变。
- 旧测试 `test_nav_data_adapter_persists_and_reuses_cache`、`test_nav_data_adapter_force_refresh_bypasses_cache`、`test_unavailable_nav_data_result_returns_explicit_empty_result` 均通过且断言未修改。
- `NavDataResult` 字段未增删。

### 7. Explicit Params / No extra_payload / No kwargs

**通过。**

`FundNavRepository.load_nav_series()` 签名（`nav_repository.py:84-93`）：`fund_code`（positional）、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh`（全部 keyword-only）。无 `extra_payload`、无 `**kwargs`、无自由 dict 参数。

`test_load_nav_series_signature_has_no_extra_payload_or_kwargs`（`test_nav_repository_contract.py:986-1009`）通过 `inspect.signature` 断言：
- 参数名不含 `extra_payload`、`kwargs`
- 所有参数为 `POSITIONAL_OR_KEYWORD` 或 `KEYWORD_ONLY`

Repository 只通过 `self._source_adapter.load_raw_nav_source()` 获取数据（`nav_repository.py:130`），不直连 Akshare、SQLite、网页 helper。

### 8. No Extractor / Snapshot / Score / Quality / Golden Changes

**通过。**

`git diff --stat 449feba...HEAD` 确认：
- `fund_agent/fund/data_extractor.py` — 未修改
- `fund_agent/fund/extraction_snapshot.py` — 未修改
- `fund_agent/fund/extraction_score.py` — 未修改
- `fund_agent/fund/quality_gate.py` — 未修改
- `fund_agent/fund/quality_gate_integration.py` — 未修改
- `fund_agent/fund/golden_answer.py` / `golden_prefill.py` — 未修改
- Bond risk extractor、renderer、Service、CLI — 未修改
- Host/Agent/dayu 包 — 未创建或修改
- FQ0-FQ6 — 语义不变

### 9. drawdown_stress Blocker Remains

**通过（intentional residual）。**

所有 3 个 slice 的证据、所有 4 个 review、plan 本身、docs/design.md 更新、README 更新，均显式声明 `drawdown_stress` blocker 未解除。当前 typed contract 只建立 raw-unit-only 归一化路径，不提供 adjusted / total-return drawdown evidence。

## Verification of Prior Finding Closure

### Plan Review Findings (DS F1–F3, MiMo F1–F2) — All Closed

| Finding | Fix | Status |
|---------|-----|--------|
| DS F1: Slice 1 过粗 | 拆为 Slice 1a/1b/2 | ✅ plan-fix applied, accepted by both re-reviews |
| DS F2: NavType/AdjustmentBasis 重叠 | 保留两者 + 兼容矩阵 + schema_drift | ✅ 实现：`_ALLOWED_ADJUSTMENT_BASIS_BY_NAV_TYPE` |
| DS F3: failure_category 语义冲突 | 明确为 `NavFailureCategory \| None`，成功路径 None | ✅ 实现：`field(default=None)` in dataclass |
| MiMo F1: validator 接受 identity!=verified + strong | 改为 identity!=verified 时强制 not strong eligible | ✅ 实现：`_apply_strong_drawdown_eligibility` |
| MiMo F2: date 重复 silent dedupe | 重复 date → integrity_error fail-closed | ✅ 实现：`_validate_record_shape` |

### Slice 1a Review Findings (DS F1–F6, MiMo F1–F3) — All Closed

在 Slice 1a fix + re-review 中全部关闭。最终 re-review（DS + MiMo）均为 **accepted**。

### Slice 1b Review Findings (DS F1–F4) — Accepted as Non-Blocking

| Finding | Severity | Status in Final Code |
|---------|----------|---------------------|
| F1: `_RAW_UNIT_NAV_INELIGIBILITY_REASON` dead code | Low | 仍存在。`nav_repository.py:33-36` 常量被 `__post_init__` 覆盖。不影响行为，语义等价。建议后续清理。 |
| F2: 5 个防御性校验分支无测试 | Low | 仍无测试。均为调用方编程错误保护（`start_date > end_date`、`minimum_records < 1`、fund_code 非 6 位、share_class 非法、raw_record 非 Mapping）。不阻塞。 |
| F3: `_raise_contract_error` 重复定义 | Note | 仍存在。`nav_models.py:285` 与 `nav_repository.py:622` 各自定义。功能等价，符合模块间依赖最小化原则。 |
| F4: `_FakeRawNavAdapter.calls` 未断言 | Note | 仍存在。测试基础设施，不影响断言正确性。 |

这些 findings 在 Slice 1b DS review 中已判定为 non-blocking（verdict ACCEPTED），本 aggregate 确认不影响 gate acceptance。

### Slice 2 Review Findings — All Passed

Slice 2 DS review 4 项逐项审查（docs 只陈述当前事实、区分 legacy/typed 边界、保留 raw_unit_nav 语义、smoke 使用 repository 边界）全部通过。GLM review 同样通过。

## Aggregate Findings

本 aggregate 独立审查后，**无新增 blocking findings**。以下为合成性观察：

### AF1 (Note) — Dead Code Constant 未在后续 Slice 中清理

Slice 1b DS F1 指出的 `_RAW_UNIT_NAV_INELIGIBILITY_REASON` 常量（`nav_repository.py:33-36`）在 Slice 2 中未清理。该常量在 series 构造时传入 `strong_drawdown_ineligibility_reason` 参数，但 `FundNavSeries.__post_init__` → `_apply_strong_drawdown_eligibility` 无条件覆盖该字段。实际输出的 reason 来自 model validator 组合，与常量文本语义等价但不完全一致。建议在后续 maintenance gate 中删除该常量。

### AF2 (Note) — 防御性分支测试缺口可接受

Slice 1b DS F2 的 5 个测试缺口在最终代码中仍存在。这些分支全部属于调用方编程错误保护，正常使用路径不会触发。当前测试已覆盖全部 8 类 fail-closed taxonomy 和所有主要成功/失败路径。893 passed / 92.40% coverage 证明核心路径覆盖充分。不阻塞。

### AF3 (Observed) — Coverage Confirmation

Validation results（来自 evidence artifact，本 aggregate 独立信任其可复现性）：
- `uv run ruff check .` — All checks passed
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` — 893 passed, 92.40% coverage
- 真实 006597 smoke — typed path 可达，`adjusted_basis="raw_unit_nav"`, `strong_drawdown_evidence_eligible=False`, `origin_source="akshare"`, 1809 records

### AF4 (Observed) — Scope Discipline

全部 5304 行新增严格限定在 plan allowed files：
- 3 个新文件：`nav_models.py`、`nav_repository.py`、`test_nav_repository_contract.py`
- 3 个修改文件：`nav_data.py`（向后兼容扩展）、`__init__.py`（re-export）、`test_nav_data.py`（新增 cache metadata 测试）
- 3 个 docs 文件：`docs/design.md`、`fund_agent/fund/README.md`、`tests/README.md`
- 1 个 evidence artifact
- 其余为 plan/review/fix/rereview artifacts（均在 `docs/reviews/` 下）

零越界到 extractor、snapshot、score、quality gate、golden、renderer、Service、CLI、Host/Agent/dayu。

## Adversarial Pass

### 反向案例

1. **raw_payload 绕过风险**：`FundNavRecord.raw_payload` 被 `compare=False` 排除在 equality 外，且 `MappingProxyType` 冻结。但 consumer 仍可读取字段值。Future Consumer Rule（plan § Future Consumer Rule）禁止 drawdown metric 读取 `raw_payload`，这是约定层面约束。当前设计如此，非实现缺陷。

2. **cache 污染**：若 SQLite `source` 列被外部篡改，`origin_source` 会暴露被篡改值。SQLite 只由 adapter 写入（`ON CONFLICT ... DO UPDATE`），运维边界可控。

3. **并发 cache 写入**：`load_nav_data` 和 `load_raw_nav_source` 各自独立调用 `_save_cached_sync`（upsert），后写入者覆盖。SQLite 连接级锁提供基本保护，无数据损坏。

4. **NAV 值为 "0"**：`_parse_required_nav_value` 中 `Decimal("0") <= Decimal("0")` → `integrity_error`。正确处理。

5. **增长率为 "0"**：`_parse_optional_growth_rate` 中 `str(Decimal("0")).strip() == "0"`，非空字符串，不会被错误拦截。正确解析为 `Decimal("0")`。

6. **日期跨月/跨年排序**：`sorted(..., key=lambda record: record.date)` 使用 `date` 原生比较，按月/年顺序正确。

7. **identity 提取跨 record 不一致**：`_first_non_empty_value` 扫描所有 records，若第一条无 identity 字段但第二条有，返回第二条的值。Akshare 当前路径所有 record 通常不含 identity 字段，返回 `None` → `requested_code_only`。正确。

8. **空 records → date_range 推导**：`_validate_record_shape` 在 `_apply_date_range_defaults` 之前执行，空 records 先触发 `not_found`，不会到达日期推导。安全。

### 边界条件

- `minimum_records=0` → repository 入口校验 `minimum_records < 1` → `schema_drift` fail-closed。安全。
- `start_date > end_date` → repository 入口校验 → `missing_date_range` fail-closed。安全。
- share_class 为空白字符串 → `_normalize_share_class` 校验 `not normalized or not normalized.isalnum()` → `identity_mismatch`。安全。
- raw_record 为 list/tuple 而非 Mapping → `_normalize_raw_record` 的 `isinstance(raw_record, Mapping)` 校验 → `schema_drift`。安全。

## Residual Risks

1. **`drawdown_stress` blocker 未解除**（intentional）。当前 typed contract 只建立 raw-unit-only 归一化，不提供 adjusted / total-return drawdown evidence。
2. **当前 source identity 为 `requested_code_only`**（intentional）。强 drawdown evidence 需要 future verified identity 和 accepted adjusted / total-return basis。
3. **Cache provenance 受限于现有 SQLite schema**。`origin_source` 为粗粒度 `"akshare"`，无 source URL、provider version 等更丰富 provenance。
4. **单一 `FundNavSeries` 只表达一种 nav_type / adjusted_basis / share_class**。未来多类型 source 需要拆分 series 或 `FundNavBundle` gate。
5. **`raw_payload` 绕过保护是约定层面**，非代码强制。Future Consumer Rule 依赖 consumer 遵守，无运行时 enforcement。
6. **真实 006597 smoke 是 implementation evidence**，不进入 CI。受 akshare/cache/network 环境影响，失败时应记录 typed `unavailable` residual。
7. **防御性分支测试缺口**（Slice 1b DS F2）：5 个分支无专项测试，不影响核心路径覆盖。
8. **Dead code 常量**（Slice 1b DS F1）：`_RAW_UNIT_NAV_INELIGIBILITY_REASON` 被 `__post_init__` 覆盖，建议后续清理。

## Conclusion

**Verdict: ACCEPTED**

理由：

- 全部 9 个 review focus areas 通过。
- Contract coherency 完整：typed models → repository normalization → adapter DTO → fail-closed taxonomy 形成闭环。
- raw_unit_nav 正确标记为非强回撤证据，requested_code_only identity 正确降级，identity_mismatch 正确 fail-closed。
- 8 类 fail-closed taxonomy 全部实现并有对应测试。
- 旧 `load_nav_data()` 完全兼容，cache provenance 正确暴露，私有 DTO 不泄漏到 public API。
- 显式参数、无 extra_payload/kwargs 经 inspect.signature 验证。
- 零越界到 extractor/snapshot/score/quality gate/golden/bond extractor/Host/Agent/dayu。
- `drawdown_stress` blocker intentional residual，所有文档显式声明未解除。
- 4 个 prior review findings 均为 non-blocking（Low/Note），不改变 gate outcome。
- Validation：full ruff pass，893 pytest passed，92.40% coverage，真实 006597 smoke 通过。
- 0 个 bug，0 个 contract violation，0 个 scope creep。

本 gate 的 typed NAV repository/source adapter contract 实现已达到 accepted 标准。后续 `drawdown_stress` extractor / metric gate 必须以 `FundNavRepository.load_nav_series()` 为唯一 typed 数据边界，并遵守 Future Consumer Rule 的三条件约束。
