# Code Review — P19-S5 Draft PR Gate (AgentDS)

## Scope

- **Mode**: PR review
- **PR**: [#13](https://github.com/bill20232033cc/fund-agent/pull/13) — P19-S5 all-A market thermometer default
- **Head**: `phase/p19-s5-all-a-pe-source-gate`
- **Base**: `main`
- **Artifact**: `docs/reviews/p19-s5-pr-review-ds-20260523.md`
- **Timestamp**: 2026-05-23T13:54 CST
- **CI**: test PASS (22s), mergeStateStatus CLEAN
- **Included scope**: All 44 changed files in PR diff；重点审查 thermometer_source.py, thermometer_cache.py, thermometer_service.py, cli.py 及对应测试
- **Excluded scope**: `docs/reviews/` 下历史 artifact 不纳入本次审查范围
- **Parallel review coverage**: 无

## Reviewed Evidence

1. **PR diff** (`gh pr diff 13`): 44 files, +5761/-172 lines
2. **Key implementation files**:
   - `fund_agent/fund/data/thermometer_source.py` (+358 lines): 新增 `AkshareAllAMarketThermometerSource`、`AkshareThermometerSource` 复合源、`classify_thermometer_code` 共享分类器、`_strict_positive_records_by_date`、`_fetch_all_a_with_retry`、`_to_optional_positive_decimal`
   - `fund_agent/fund/data/thermometer_cache.py` (+20/-0 lines): 新增 market/index 命名空间分离、unsupported code guard
   - `fund_agent/services/thermometer_service.py` (+76/-0 lines): 默认路由到 `wind_all_a`、`AkshareThermometerSource` 替换 `AkshareIndexThermometerSource`、`_is_six_ascii_digits` 输入校验
   - `fund_agent/ui/cli.py` (+11/-0 lines): `--index` help 文本更新、`thermometer` 命令 docstring 更新
3. **Tests**: `test_thermometer_source.py` (488 lines, 37 tests), `test_thermometer_cache.py` (+136 lines), `test_thermometer_service.py` (+311 lines), `test_cli.py` (+284 lines)
4. **Calculator** (`thermometer_calculator.py`): 未在本次 PR 修改，作为计算契约参照
5. **CI**: GitHub Actions test SUCCESS，mergeStateStatus CLEAN
6. **Design docs**: `AGENTS.md`、`docs/design.md` §11、`docs/implementation-control.md` P19-S5 章节

## Verdict

**PASS** — 未发现 BLOCKING 问题。PR 实现与 P19-S5 目标、design.md §11 温度计设计、模块边界约束一致。代码结构清晰、测试覆盖充分、fail-closed 路径完整。

---

## Findings

### 1-NON_BLOCKING-[低]-公开页 adapter 默认路径变为死代码

- **入口/函数**: `ThermometerService.run()` → `_normalize_request()` 默认分支
- **文件(行号)**: `fund_agent/services/thermometer_service.py:165-171`
- **输入场景**: CLI 或调用方不传 `--index`，构造 `ThermometerRequest(index_code=None, index_codes=None)`
- **实际分支**: `_normalize_request()` 第 304 行始终将空请求规范化为 `index_code=ALL_A_MARKET_CODE`，因此 `run()` 第 165 行的 `if normalized.index_code is not None` 始终为 True，第 170-171 行的 `adapter.load_thermometer()` 分支不可达
- **预期行为**: 公开页 adapter 保留为过渡/对比能力，不作为默认路径（符合设计意图）
- **实际行为**: 代码路径不可达，`_default_adapter_factory` 和 `FundThermometerAdapter` 在默认路径中成为死代码
- **直接证据**: `_normalize_request()` 第 304 行 `return _NormalizedThermometerRequest(index_code=ALL_A_MARKET_CODE, index_codes=None)` 无任何条件返回 `index_code=None` 的分支
- **影响**: 公开页 adapter 和其工厂函数在当前默认流程中不可达，仅能通过测试注入或显式构造绕过 `_normalize_request` 调用。不影响正确性，但增加代码阅读困惑
- **建议改法和验证点**: 在后续 P19 清理 phase 中移除死代码路径，或将公开页 adapter 显式标记为 deprecated。当前 PR 内不需要修改
- **修复风险（低）**: 仅涉及死代码删除，不影响运行时行为
- **严重程度（低）**: 不影响正确性，属于 maintainability 范畴

### 2-NON_BLOCKING-[低]-指数与全 A 路径对重复日期的处理不对称

- **入口/函数**: `_records_by_date()` vs `_strict_positive_records_by_date()`
- **文件(行号)**: `fund_agent/fund/data/thermometer_source.py:453-485` vs `488-538`
- **输入场景**: akshare 返回包含同一日期的多条记录（例如数据修正重发）
- **实际分支**: 指数路径 `_records_by_date` 第 484 行 `values[date_text] = value` 直接覆盖，最后一条 wins；全 A 路径 `_strict_positive_records_by_date` 第 533-534 行对冲突值抛出 `ThermometerSourceError`
- **预期行为**: 两条路径对数据完整性违规应有对等的 fail-closed 策略
- **实际行为**: 指数路径静默接受重复日期（最后写入获胜），全 A 路径 fail-closed
- **直接证据**: 对比第 484 行（无重复检测）与第 533 行（`if existing_value != value: raise ThermometerSourceError(...)`）
- **影响**: 如果 akshare 指数 PE/PB 接口未来出现重复日期，指数路径会静默选择一个值而不报警。当前 akshare `stock_index_pe_lg` / `stock_index_pb_lg` 实际不产生重复日期，因此当前无实际危害
- **建议改法和验证点**: 后续统一两条路径的重复日期策略。当前 PR 新增的全 A 路径已经采用了更严格的策略，指数路径的对称收紧可在后续 cleanup 中完成
- **修复风险（低）**: 需要确认 akshare 指数接口不会产生重复日期后再收紧
- **严重程度（低）**: 当前无已知触发场景，属于防御性不对称

---

## Non-blocking Notes

1. **`_fetch_all_a_with_retry` 宽异常捕获** (`thermometer_source.py:445-450`): `except Exception` 包裹所有异常类型。注释说明外部数据源异常类型不稳定，且重试上限为 2 次，在 Legulegu 接口场景下合理。如果未来 akshare 异常类型稳定化，可收紧为具体异常类型。
2. **`ALL_A_FETCH_MAX_ATTEMPTS = 2`**: 仅 1 次重试。对瞬态网络抖动足够，但对 Legulegu 持续限流场景可能不足。当前作为初始值可接受，后续可根据生产观测调整。
3. **`stock_a_ttm_lyr()` 接口稳定性**: 该 akshare 接口在 source feasibility 阶段已验证可用，但其长期稳定性（字段名、返回结构）不如 `stock_a_all_pb()` 久经考验。已在 `_strict_positive_records_by_date` 中以 schema 校验 fail-closed 兜底。

## Residual Risks

1. **akshare `stock_a_ttm_lyr()` 接口 schema 漂移**: 通过 `_strict_positive_records_by_date` 的字段缺失检测 fail-closed，且 `ThermometerService._load_index_reading` 在 `ThermometerSourceError` 时会回退到 stale cache。风险已受控。
2. **全 A PE 历史覆盖长度**: 计算器要求 ≥30 个共同日期（`MIN_HISTORY_POINTS`），若 akshare 返回数据不足会以 `ThermometerCalculationError` 向上传播。CI 测试使用 fixture 验证了此路径。生产实际覆盖长度取决于 akshare 数据，建议后续监控首次全量回填的数据量。
3. **retry-budget harmonization**: control doc open residuals 已记录此项为非阻塞后续工作，不影响当前 PR merge。
4. **legacy public-page adapter cleanup**: control doc open residuals 已记录，不属于当前 PR scope。

## Validation

- GitHub CI test: **PASS** (22s, job [77500886021](https://github.com/bill20232033cc/fund-agent/actions/runs/26324979415/job/77500886021))
- mergeStateStatus: **CLEAN**
- ruff check: **PASS**（PR description 声明）
- git diff --check: **PASS**（PR description 声明）
- PR description 报告测试结果: thermometer_source 37 passed, service/cache 33 passed, CLI 38 passed, 组合 108 passed, analyze regression 20 passed

## Stop Status

本 review 不构成 draft PR gate 阻断。PR 13 可进入 draft-PR-pass 裁决。

---

**AgentDS 独立判断**。本 review 基于 PR #13 diff、源代码直接阅读、CI 结果和 design/control doc 对照完成，未依赖已有 aggregate review 结论。
