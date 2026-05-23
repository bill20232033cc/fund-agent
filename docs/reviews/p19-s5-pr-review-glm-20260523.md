# Code Review — PR #13 P19-S5 all-A market thermometer default

## Scope

- **Mode**: PR Review
- **PR**: [#13](https://github.com/bill20232033cc/fund-agent/pull/13) — P19-S5 all-A market thermometer default
- **Author**: bill20232033cc
- **Head**: `phase/p19-s5-all-a-pe-source-gate`
- **Base**: `main`
- **Output file**: `docs/reviews/pr-13-review-20260523-135222.md`（本文件按用户要求命名为 `p19-s5-pr-review-glm-20260523.md`）
- **Included scope**: 4 个核心实现文件 diff 完整走读 + 3 个 README diff + test 文件结构验证
  - `fund_agent/fund/data/thermometer_source.py` — 全 A 数据源、代码分类、合并、重试
  - `fund_agent/fund/data/thermometer_cache.py` — market/index 缓存分层
  - `fund_agent/services/thermometer_service.py` — 默认路由、代码规范化、Composite source 接入
  - `fund_agent/ui/cli.py` — CLI help/docstring 同步
  - `README.md`, `fund_agent/fund/README.md`, `tests/README.md` — 文档同步
- **Excluded scope**: review artifact 文件（docs/reviews/*）不做 code review；未读完整 test 文件内容，仅验证 CI 结果和 test 描述一致性
- **Parallel review coverage**: 无，单 reviewer 完整走读
- **CI**: GitHub Actions `test` job — **PASS** (22s, run 26324979415)

## Reviewed Evidence

| 证据类型 | 来源 |
|---------|------|
| PR diff | `gh pr diff 13` → `git diff origin/main...HEAD` 完整 4 文件 diff |
| 完整源文件 | `thermometer_source.py` (623 行), `thermometer_cache.py` (243 行), `thermometer_service.py` (354 行), `cli.py:258-312` |
| 设计真源 | `docs/design.md` §11 温度计设计 |
| 实施总控 | `docs/implementation-control.md` P19-S5 Startup Packet |
| 项目规则 | `AGENTS.md` 模块边界、fallback fail-closed |
| CI 结果 | `gh pr checks 13` → test pass |
| 文档同步 | `README.md`, `fund_agent/fund/README.md`, `tests/README.md` diff 完整审阅 |

## Verdict

**PASS** — 未发现 BLOCKING 问题。实现正确、一致地完成了 P19-S5 目标：全 A 市场 `wind_all_a` 作为默认温度计路径，akshare Legulegu all-A PE/PB source，Service 默认路由，market/index cache 分层，CLI/docs/tests 同步。代码遵循项目模块边界，fallback 行为 fail-closed，schema drift 有显式检测。

## Findings

未发现 BLOCKING findings。以下是 NON_BLOCKING 观察。

### N1-未修复-低-公开页 adapter 路径变为不可达死代码

- **入口/函数**: `ThermometerService.run` — `adapter = self._adapter_factory(request.cache_dir)` 路径
- **文件(行号)**: `fund_agent/services/thermometer_service.py:170-171`
- **输入场景**: 任何经 `_normalize_request` 处理后的请求
- **实际分支**: `_normalize_request` 在无参数时返回 `index_code=ALL_A_MARKET_CODE`（非 None），使得 `run()` 中第二个 `if normalized.index_code is not None` 始终为 True
- **预期行为**: 无影响；设计文档明确有知有行公开页为"过渡实现"
- **实际行为**: `run()` 第 170-171 行的 adapter 路径永远不可达；`__init__` 中 `_adapter_factory` 字段和 `_default_adapter_factory` 函数成为死代码；`_ThermometerAdapter` / `_ThermometerAdapterFactory` Protocol 定义也不再被生产路径使用
- **直接证据**: `_normalize_request`（行 304）`return _NormalizedThermometerRequest(index_code=ALL_A_MARKET_CODE, index_codes=None)` → `run()`（行 168）`if normalized.index_code is not None` 始终 True → 行 170-171 adapter 路径不可达
- **影响**: 仅代码整洁性；不影响正确性或稳定性
- **建议改法和验证点**: 后续可清理 `ThermometerService` 中的 adapter 相关字段和 `run()` 末尾死代码分支；不阻塞本次 merge
- **修复风险（低）**: 低；纯删除
- **严重程度（低）**

### N2-未修复-低-_normalize_date 错误消息对全 A 数据使用了"指数"措辞

- **入口/函数**: `_normalize_date` 被 `_strict_positive_records_by_date` 调用
- **文件(行号)**: `fund_agent/fund/data/thermometer_source.py:555-568`
- **输入场景**: 全 A PE/PB 表中存在非法日期值
- **实际分支**: 错误消息说"指数估值数据日期为空" / "指数估值数据日期不是 ISO 格式" / "指数估值数据日期非法"
- **预期行为**: 全 A 数据的错误消息应使用中性措辞如"估值数据"或"全 A 估值数据"
- **实际行为**: 错误消息使用了"指数估值数据"前缀，对全 A 数据语义不准确
- **直接证据**: 行 555 `raise ThermometerSourceError("指数估值数据日期为空")`，行 563 `raise ThermometerSourceError(f"指数估值数据日期不是 ISO 格式：{value}")`，行 568 `raise ThermometerSourceError(f"指数估值数据日期非法：{value}")`
- **影响**: 仅错误消息可读性；不影响功能正确性
- **建议改法和验证点**: 可将 `_normalize_date` 错误消息改为"估值数据日期"或接受 `date_column` 参数区分上下文；不阻塞
- **修复风险（低）**: 低
- **严重程度（低）**

## Non-blocking Notes

1. **全 A 验证严格度高于指数路径**: `_strict_positive_records_by_date`（全 A）检查了 NaN/Infinity、重复日期冲突、空表检测；`_records_by_date`（指数，P19-S1 遗留）未检查 NaN/Infinity 且无重复日期冲突检测。这是全 A 新代码比遗留指数代码更严格，属于正向改进，不需要回修指数路径。

2. **akshare API 选择正确**: `ak.stock_a_ttm_lyr()` 返回全 A TTM PE 中位数（`middlePETTM` 列），`ak.stock_a_all_pb()` 返回全 A PB 中位数（`middlePB` 列）。与设计文档 §11.2 等权中位数方法论一致。

3. **重试策略合理**: `ALL_A_FETCH_MAX_ATTEMPTS = 2`，无退避，对简单外部 API 调用足够。PE/PB 独立并发重试（`asyncio.gather`），任一失败则整体返回 `ThermometerSourceError`，Service 层再 fallback 到 stale cache 或 unavailable。

4. **_is_six_ascii_digits 比 str.isdigit 更严格**: 新代码使用 `all("0" <= char <= "9" for char in value)` 替代 `str.isdigit()`，排除了全角数字等 Unicode 数字字符。对指数代码纯 ASCII 场景更正确。

5. **文档同步完整**: README.md、fund/README.md、tests/README.md 均已更新，反映全 A 默认路由、market 缓存分层、CLI help 文案变化。README 示例命令使用真实参数名。

6. **不支持 6 位代码的 graceful degradation**: `_normalize_index_codes` 接受任何 6 位 ASCII 数字，不在 SUPPORTED_INDEX_SYMBOLS 中的代码会经 `_load_index_reading` 返回 `ThermometerUnavailable`，而非硬报错。用户得到有意义的"暂不支持温度计代码"消息。

## Residual Risks

1. **akshare API 稳定性**: `ak.stock_a_ttm_lyr()` 和 `ak.stock_a_all_pb()` 是外部 akshare 接口，列名（`middlePETTM`、`middlePB`、`date`）可能随 akshare 版本变化。当前 `_strict_positive_records_by_date` 对缺列会 fail-closed（抛出 `ThermometerSourceError`），风险已缓解但无法消除。建议后续关注 akshare changelog。

2. **全 A PE 历史覆盖长度**: 设计文档 §11.4 提到"两轮完整牛熊周期的动态窗口"，全 A 数据源是否提供足够长的历史取决于 akshare 返回。当前实现直接使用全量返回数据，不截断窗口。如需调整窗口应在后续 S 中处理。

3. **analyze 集成边界保持**: PR 正确未将全 A 温度计自动接入 `fund-analysis analyze` 的估值状态判断。design.md §11.7 明确 `analyze` 仍只对 exact supported-index (000300/000905) 的 index_fund/enhanced_index 自动调用温度计。全 A 自动映射需要 P19-S3 或后续专门 gate。

## Validation

| 验证项 | 结果 |
|-------|------|
| CI test job | PASS (22s) |
| 设计文档对齐 | §11.4 P0 万得全 A wind_all_a P19-S5 ✓ |
| 实施总控对齐 | P19-S5 ready-to-open-draft-PR 状态 ✓ |
| 模块边界 | Capability data 层处理数据源和 schema 验证，Service 层处理路由和 fallback，UI 层只传参数 ✓ |
| fallback fail-closed | 全 A source 失败 → ThermometerSourceError → Service fallback stale cache → unavailable；schema drift 缺列直接 raise ✓ |
| 无反向 import | Service 不 import akshare；UI 不 import Capability 内部 ✓ |
| 无 extra_payload | 所有参数显式声明 ✓ |
| 文档同步 | README、fund/README、tests/README 均已更新 ✓ |

## Stop Status

Review 完成。无 BLOCKING finding。Verdict: **PASS**。
