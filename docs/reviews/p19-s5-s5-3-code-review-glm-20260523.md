# Code Review

## Scope

- Mode: current changes (role-scoped S5-3 code review handoff)
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: S5-2 accepted state (uncommitted S5-3 workspace changes)
- Output file: `docs/reviews/p19-s5-s5-3-code-review-glm-20260523.md`
- Included scope: `fund_agent/ui/cli.py`, `tests/ui/test_cli.py`, `README.md`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/reviews/p19-s5-s5-3-cli-docs-implementation-20260523.md`
- Excluded scope: Service internals (`thermometer_service.py`), source/cache (`thermometer_source.py`, `thermometer_cache.py`), analyze, renderer, audit, design doc, control doc, PR/commit state
- Parallel review coverage: 无；单 reviewer 完整走读全部 diff

## Findings

未发现实质性问题。

### 逐项走读证据

**1. CLI help 文案 — `fund_agent/ui/cli.py:260-271`**

- `--index` help 从 `"自建温度计指数代码；支持 000300、000905 或逗号分隔批量"` 更新为 `"自建温度计代码；支持 wind_all_a、000300、000905 或逗号分隔批量"`。
- `--force-refresh` help 从 `"强制刷新温度计公开页面数据"` 更新为 `"强制刷新自有温度计历史数据"`。
- 测试 `test_thermometer_cli_help_documents_all_a_and_self_owned_history`（test_cli.py:997-1018）断言 `wind_all_a`、`000300`、`000905` 和 `"自有温度计历史数据"` 出现在 help 输出中。
- 判定：help 文案与 P19-S5 契约一致。

**2. CLI no-arg 默认路由 — `fund_agent/ui/cli.py:290-301`**

- `_parse_index_option(None)` → `(None, None)`，`ThermometerRequest(index_code=None, index_codes=None)` 正确转发到 Service。
- CLI 层不硬编码 `wind_all_a`；默认路由由 Service 层拥有。
- 测试 `test_thermometer_cli_no_arg_json_delegates_default_to_service`（test_cli.py:1107-1138）验证 `last_request.index_code is None`、`last_request.index_codes is None`，且 JSON 输出为全 A 读数。
- 测试 `test_thermometer_cli_prints_plain_summary`（test_cli.py:1066-1104）验证 plain 输出包含 `index_code: wind_all_a`、`index_name: 万得全 A / 全 A 市场`、`source: akshare_legulegu_all_a_pe_pb`、`temperature: 35.25`、`pe_percentile: 30.00`、`pb_percentile: 40.50`、`valuation_state_candidate: fair` 和 disclaimer。
- 判定：CLI 无参默认路由语义正确，默认路由权归 Service。

**3. CLI `--index wind_all_a --json` — `fund_agent/ui/cli.py:945-962`**

- `_parse_index_option("wind_all_a")` → `"," not in "wind_all_a"` → `("wind_all_a", None)`。
- 测试 `test_thermometer_cli_prints_all_a_reading_json`（test_cli.py:1171-1198）验证 `payload["index_code"] == "wind_all_a"`、`payload["source"] == "akshare_legulegu_all_a_pe_pb"`、`last_request.index_code == "wind_all_a"`、`last_request.index_codes is None`。
- 判定：单指数全 A 路径正确。

**4. CLI `--index wind_all_a,000300 --json` 顺序保持 — `fund_agent/ui/cli.py:945-962`**

- `_parse_index_option("wind_all_a,000300")` → `(None, ("wind_all_a", "000300"))`，tuple 保留原始顺序。
- 测试 `test_thermometer_cli_prints_all_a_mixed_batch_reading_json`（test_cli.py:1296-1325）验证 `requested_index_codes == ["wind_all_a", "000300"]`、`readings[0]["index_code"] == "wind_all_a"`、`readings[1]["index_code"] == "000300"`、`last_request.index_codes == ("wind_all_a", "000300")`。
- 判定：批量混合顺序保持正确。

**5. Malformed `--index wind_all_a,abc` 退出 2 — `test_cli.py:1432-1463`**

- 参数化测试包含 `"wind_all_a,abc"` 用例。
- `_parse_index_option` 返回 `(None, ("wind_all_a", "abc"))` → Service 校验 `abc` → `ValueError` → CLI 捕获 `ValueError` → exit 2。
- 测试断言 `result.exit_code == 2` 且 `"温度计请求参数错误" in result.output`。
- 判定：全 A + malformed 组合正确退出 2。

**6. Plain 输出全 A 字段完整性 — `fund_agent/ui/cli.py:915-942,878-912`**

- `_thermometer_reading_payload` 输出 `index_code`、`index_name`、`source`、`temperature`、`pe_percentile`、`pb_percentile`、`valuation_state_candidate`、`disclaimer` 等字段。
- `_echo_thermometer_snapshot` 对无 `"readings"` 键的 dict（单读数）遍历所有 key-value 输出。
- 测试断言覆盖：code、name、source、temperature、PE/PB percentiles、valuation candidate、disclaimer 均在 plain 输出中。
- 判定：plain 输出字段完整。

**7. 现有行为回归检查**

- `test_thermometer_cli_prints_index_reading_json`（000300 单指数 JSON）：保留，断言未变。
- `test_thermometer_cli_prints_index_reading_plain`（000300 单指数 plain）：保留。
- `test_thermometer_cli_prints_batch_reading_json`（000300+000905 批量 JSON）：保留，断言 `requested_index_codes == ["000300", "000905"]` 未变。
- `test_thermometer_cli_prints_batch_reading_plain`（000300+000905 批量 plain）：保留。
- `test_thermometer_cli_partial_unavailable_batch_json_exits_zero`：保留，用例不变。
- `test_thermometer_cli_unsupported_batch_item_returns_unavailable_json`：测试名更新（去掉了 "ignores fresh cache"），移除了对 999999 伪造缓存的创建，断言更新为 "暂不支持温度计代码"。核心行为（unsupported 返回 unavailable）仍然被验证。cache-poisoning 防御角度已由 Service 层测试覆盖。
- `test_thermometer_cli_malformed_index_input_exits_two`：参数化用例从 5 个扩展到 6 个（增加 `"wind_all_a,abc"`）。
- `test_thermometer_cli_exits_nonzero_on_service_error`：保留。
- 判定：现有 000300、000300+000905、unavailable、unsupported、malformed、service error 行为未回归。

**8. README 文档一致性**

- `README.md:66-67`：示例从 `"查询温度计公开页快照"` 更新为 `"查询默认全 A 市场温度计"`，从 `"查询自建宽基指数温度计"` 更新为 `"查询自建全 A / 宽基指数温度计"`。
- `README.md:119-121`：当前能力列表更新，公开页 adapter 标注为 "保留为过渡/对比能力"，全 A 为默认 CLI 路径。
- `README.md:137`：非目标列表移除 "全 A 市场温度计"，因已实现。
- `README.md:161-179`：温度计查询章节完整描述默认全 A、`--index wind_all_a`、批量查询、`--force-refresh` 刷新自有历史数据、analyze 自动估值仍限 exact supported-index。
- 未声称 analyze 使用全 A 自动估值（line 179 显式说明 "analyze 自动估值仍只使用沪深300/中证500 exact supported-index 单指数路径"）。
- `fund_agent/fund/README.md:310-315`：自建温度计描述更新至 P19-S5，提及全 A 覆盖、market/index 缓存命名空间、数据源说明。
- `tests/README.md:26-27,45-46`：测试描述更新，覆盖全 A source/cache/service/CLI。
- 判定：文档与实现一致，不夸大 analyze 估值范围。

**9. 导入清理 — `test_cli.py:14-16`**

- 移除了 `MacroTemperature`、`MarketTemperature`、`ThermometerSnapshot` 的导入。
- 这些类型仅被旧的 `_available_thermometer_snapshot()` 和 `_unavailable_thermometer_snapshot()` 使用，这两个 fixture 已被替换为基于 `ThermometerReading` 的版本。
- 判定：导入清理干净，无残留依赖。

**10. `_FakeThermometerService` 默认返回值 — `test_cli.py:396`**

- 从 `_available_thermometer_snapshot()` 更新为 `_available_all_a_thermometer_reading()`。
- 所有未显式设置 `snapshot` 的 fake Service 测试（如 `test_thermometer_cli_exits_nonzero_on_service_error`）将获得全 A 读数作为默认返回。
- 判定：与 CLI 默认全 A 路由一致。

## Open Questions

- 无。

## Residual Risk

- `test_thermometer_cli_unsupported_batch_item_returns_unavailable_json` 移除了对 999999 伪造缓存的创建和 "ignores fresh cache" 断言，cache-poisoning 防御不再在 CLI 测试中验证。该场景已由 Service 层测试覆盖，不属于 CLI 层回归，但记录为 residual risk。
- 公开页 `ThermometerSnapshot` 的 CLI 测试已完全替换为全 A `ThermometerReading` 测试。`_thermometer_snapshot_payload` 的 legacy 分支仍存在但无 CLI 测试覆盖。legacy 分支仅在 Service 返回 `ThermometerSnapshot` 时触发，当前 CLI 默认路径不会触发。该分支属于 Capability data adapter 过渡期代码，非 S5-3 scope。
