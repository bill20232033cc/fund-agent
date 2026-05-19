# P4-S1 Code Review — AgentMiMo

> 日期：2026-05-19
> Gate：`P4-S1 code review`
> Reviewer：AgentMiMo
> Scope：Selected Fund Extraction Snapshot + Quality Gate MVP
> 结论：**PASS**（0 blocking, 4 non-blocking findings）

---

## Finding 1 — `_validate_request` docstring 缺少 `limit` 参数说明

**Severity**: INFO
**File**: `fund_agent/services/extraction_snapshot_service.py:75-97`

**证据**：

docstring Args 仅列 `fund_code`、`report_year`、`run_id` 和抽样参数，但实现还校验了 `limit`（第 96 行）：

```python
def _validate_request(request: ExtractionSnapshotRequest) -> None:
    """校验快照请求的 Service 层显式输入。

    Args:
        request: 快照请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当基金代码、年报年份、run_id 或抽样参数非法时抛出。
    """
    # ...
    if request.limit is not None and request.limit < 0:  # 第 96 行
        raise ValueError("limit 不能为负数")
```

**Recommendation**：将 Raises 文档补充 `limit` 说明，例如 `当基金代码、年报年份、run_id、抽样参数或 limit 非法时抛出`。

**Verdict**: PASS（info only）

---

## Finding 2 — `_normalize_extraction_mode` 对未知模式静默降级未文档化

**Severity**: INFO
**File**: `fund_agent/fund/extraction_snapshot.py:964-981`

**证据**：

函数对不在 `{direct, estimated, missing, partial, derived}` 集合中的未知模式静默返回 `missing`。当前上游 extractor 只输出这四种模式，但如果后续引入新模式（如 `inferred`），该行为可能导致 snapshot 误报 coverage 下降而无任何日志或 note。

```python
def _normalize_extraction_mode(extraction_mode: str) -> str:
    if extraction_mode == "derived":
        return _EXTRACTION_MODE_DIRECT
    if extraction_mode in {"direct", "estimated", "missing", "partial"}:
        return extraction_mode
    return _EXTRACTION_MODE_MISSING  # 静默降级
```

**Recommendation**：在 docstring 中明确记录"未知模式降级为 missing"的行为约定，或在降级时追加 logging.warning。当前 P4-S1 范围内不构成 blocking，但 P4-S2 评分阶段需注意此行为可能污染 coverage 统计。

**Verdict**: PASS（info only）

---

## Finding 3 — extraction_mode normalization 仅覆盖 direct/missing 两态测试

**Severity**: LOW
**File**: `tests/fund/test_extraction_snapshot.py:262-354`

**证据**：

测试 helper `_field()` 默认 `extraction_mode="direct"`，仅对 `turnover_rate`、`investor_return`、`manager_alignment` 传入 `"missing"`。`_normalize_extraction_mode` 覆盖的 `estimated`、`partial` 和 unknown→missing 降级路径均无测试。

`_build_bundle` 构造了 14 个字段，extraction_mode 分布：
- `"direct"`: 10 个字段
- `"missing"`: 4 个字段（turnover_rate, investor_return, manager_alignment, nav_data 默认）
- `"estimated"`: 0
- `"partial"`: 0

**Recommendation**：后续补充至少一条 `estimated` 和 `partial` 模式的 snapshot 记录断言，确认 normalization 不改变合法模式。当前 P4-S1 优先验证 CSV 校验和 schema，可接受。

**Verdict**: PASS（low）

---

## Finding 4 — `_validate_request` 校验路径未被 Service 测试完整覆盖

**Severity**: LOW
**File**: `tests/services/test_extraction_snapshot_service.py:87-112`

**证据**：

Service 测试仅覆盖 `fund_code="ABC"`（非法代码）的拒绝路径。以下校验分支无测试：
- `report_year <= 0`
- `run_id` 为空白字符串
- `sample_per_category < 0`（Service 层）
- `limit < 0`（Service 层）

Capability 层 `select_snapshot_funds()` 对 `sample_per_category < 0` 和 `limit < 0` 有独立测试覆盖（通过 `test_run_snapshot_summary_highlights_duplicates_and_continues_failures` 间接验证正值路径），但 Service 层的 early-reject 路径未覆盖。

**Recommendation**：补充 Service 层对 `report_year`、`run_id`、`sample_per_category` 和 `limit` 的拒绝测试。当前由 Capability 层兜底，不阻塞 P4-S1。

**Verdict**: PASS（low）

---

## 通过项确认

### 架构边界

- Snapshot 核心在 Capability 层 `fund_agent/fund/extraction_snapshot.py`。
- Service 层 `fund_agent/services/extraction_snapshot_service.py` 只做请求校验和参数转发。
- UI 层 `fund_agent/ui/cli.py` 只导入 Service 层（第 16-24 行），不直接依赖 Capability。
- `services/__init__.py` 正确导出 `ExtractionSnapshotRequest` 和 `ExtractionSnapshotService`。

### 年报访问隔离

- `run_extraction_snapshot()` 通过 `active_extractor.extract()` 获取数据（第 387-391 行）。
- 默认使用 `FundDataExtractor()`（第 377 行），不直接读取 PDF、cache 或底层解析文件。
- 测试通过 `SnapshotExtractor` Protocol 注入 `_FakeExtractor`，不触发真实网络/PDF。

### 显式参数

- `ExtractionSnapshotRequest` 字段：`fund_code`、`report_year`、`source_csv`、`run_id`、`output_dir`、`force_refresh`、`sample_per_category`、`limit`。
- `run_extraction_snapshot()` 参数列表与 Request 一一对应，无 `extra_payload`。
- Service → Capability 参数转发测试验证了 8 个参数完全一致（`test_extraction_snapshot_service_delegates_explicit_params` 第 75-84 行）。

### Snapshot Schema

- `SnapshotRecord` 包含 P4-S1 控制文档 §4.5 全部 18 个字段。
- `SNAPSHOT_FIELD_ORDER` 与控制文档 field_group/field_name 映射完全一致（14 个条目）。
- `classification_basis` 类型为 `tuple[str, ...]`，JSON 序列化为数组。
- Schema 测试验证了字段集合和记录数量（`test_build_snapshot_records_contains_required_schema_and_all_fields` 第 137-163 行）。

### 错误继续与 errors.jsonl

- 单基金异常被捕获并写入 `errors.jsonl`（第 392-407 行），run 继续执行。
- 测试验证了失败基金代码、成功基金代码和错误消息（`test_run_snapshot_summary_highlights_duplicates_and_continues_failures` 第 214-222 行）。

### 016492 重复 summary 标红

- `validate_selected_fund_pool()` 检测重复代码（第 279-280 行）。
- `write_snapshot_summary()` 用 `<mark>` 标签输出重复代码（第 574-576 行）。
- 重复代码不阻断运行（`has_blocking_errors` 仅检查 missing_rows 和 bad_code_rows）。
- 测试验证了 `<mark>004393</mark>` 出现在 summary 中（第 221 行）。

### 004393 known failure 捕获

- `_record_note()` 在 `fund_code=="004393"` 且 `classified_fund_type=="index_fund"` 且 `field_name=="classified_fund_type"` 时追加 known failure note（第 1046-1047 行）。
- 不静默覆盖分类结果：snapshot 记录真实的 `classified_fund_type=index_fund`。
- 测试验证了 note 包含 `known_failure:P4-S1` 且 summary 中也有该标记（`test_004393_known_failure_classification_is_captured` 第 256-259 行）。

### 非目标合规

- 未修复 004393 分类器。
- 未扩展 extractor 逻辑。
- 未建立 golden answer。
- 未接入 LLM 审计。
- 未接入 CI quality gate。

### 文档同步

- `README.md` 已新增 extraction-snapshot 命令说明和常用命令示例。
- `fund_agent/fund/README.md` 已新增 `run_extraction_snapshot()` 能力说明。
- `tests/README.md` 已新增 P4-S1 snapshot 测试说明和 CLI 运行示例。
- `docs/implementation-control.md` 已同步 P4 状态。
- `docs/implementation-control-p4.md` 已同步 gate 状态。

### 测试覆盖

- `tests/fund/test_extraction_snapshot.py`：4 个测试覆盖 CSV 校验、schema、重复标红、失败继续、004393 known failure。
- `tests/services/test_extraction_snapshot_service.py`：2 个测试覆盖参数转发和非法代码拒绝。
- `tests/ui/test_cli.py`：1 个测试覆盖 CLI → Service 边界参数转发。
- 全部测试使用 fake extractor，不触发真实网络/PDF。
- Implementation artifact 报告 `17 passed`。

---

## 结论

**PASS**。P4-S1 实现符合控制文档 §4.2 范围、§4.3 约束和 §4.7 验收条件。4 个 INFO/LOW findings 均为文档完善和测试补充，不阻塞 P4-S1 进入 review judgment。
