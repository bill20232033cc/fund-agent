# P19-S5 Aggregate Deepreview — AgentDS — 2026-05-23

## Scope

- Mode: aggregate cross-slice deep review (Current Changes Mode, gate handoff)
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: `main` (2ab9b33 is HEAD, 8 commits ahead of main baseline)
- Output file: `docs/reviews/p19-s5-aggregate-deepreview-ds-20260523.md`
- Included scope: Commits f4ee668 through 2ab9b33 covering P19-S5 S5-1/S5-2/S5-3
- Excluded scope: Unrelated untracked docs (`docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`, and non-P19-S5 reviews)
- Truth artifacts: `AGENTS.md`, `docs/design.md` §11, `docs/implementation-control.md`, all S5-1/S5-2/S5-3 review artifacts as listed in gate handoff
- Review date: 2026-05-23

## Cross-Slice Architecture Walkthrough

### Entry to exit chain (no-arg default)

```
CLI thermometer (no args)
  → ThermometerService.run(ThermometerRequest())
    → _normalize_request() materializes index_code="wind_all_a"
    → _load_index_reading("wind_all_a")
      → classify_thermometer_code("wind_all_a") → "market" ✓
      → cache.load("wind_all_a") → market/ namespace ✓
      → AkshareThermometerSource.load_index_history("wind_all_a")
        → classify_thermometer_code("wind_all_a") → "market"
        → AkshareAllAMarketThermometerSource.load_index_history("wind_all_a")
          → _fetch_all_a_with_retry(pe_fetcher) → ak.stock_a_ttm_lyr()
          → _fetch_all_a_with_retry(pb_fetcher) → ak.stock_a_all_pb()
          → _merge_all_a_pe_pb_rows(date, middlePETTM, middlePB)
          → PePbHistory(index_code="wind_all_a", source="akshare_legulegu_all_a_pe_pb")
      → cache.save(history) → market/wind_all_a_history.json
      → calculate_thermometer_reading(history) → ThermometerReading
  → CLI renders plain/JSON output
```

No boundary violation. CLI → Service → Capability. No akshare imports above Capability.

### Entry to exit chain (explicit --index 000300)

```
CLI thermometer --index 000300
  → _normalize_index_codes(("000300",)) → ("000300",)
  → _load_index_reading("000300")
    → classify_thermometer_code("000300") → "index" ✓
    → cache.load("000300") → index/ namespace ✓
    → AkshareThermometerSource.load_index_history("000300")
      → classify → "index"
      → AkshareIndexThermometerSource.load_index_history("000300")
        → ak.stock_index_pe_lg("沪深300"), ak.stock_index_pb_lg("沪深300")
        → _merge_pe_pb_rows(滚动市盈率中位数, 市净率中位数)
```

P19-S1/S2 index path intact. No regression.

### P19-S3 analyze path: no all-A leakage

Confirmed via grep and code walkthrough:
- `tests/services/test_fund_analysis_service.py`: zero all_A/wind_all_a references
- `fund_agent/services/fund_analysis_service.py`: no wind_all_a import or usage
- `fund_agent/fund/analysis/`: no all-A valuation logic
- README.md line 179: "`analyze` 自动估值仍只使用沪深300/中证500 exact supported-index 单指数路径"

## Findings

### F1 — Cross-Slice Retry Budget Inconsistency (index vs all-A)

- **入口/函数**: `AkshareIndexThermometerSource._load_pe_frame` / `AkshareAllAMarketThermometerSource._load_pe_frame`
- **文件(行号)**: `thermometer_source.py:220-239` (index, no retry), `thermometer_source.py:307-335` (all-A, `ALL_A_FETCH_MAX_ATTEMPTS=2`)
- **输入场景**: Legulegu API 返回瞬态 SSL EOF 或连接重置
- **实际分支**: 指数路径单次调用失败立即传播异常；全 A 路径重试一次后传播
- **预期行为**: 两条路径对同类外部瞬态失败应有相同韧性
- **实际行为**: 指数路径对一次性网络抖动更脆弱，可能过早触发 stale cache 或 unavailable
- **直接证据**: `thermometer_source.py:200-206` — 指数路径 `asyncio.gather` 包裹在 try/except 中，内部 `_load_pe_frame` 和 `_load_pb_frame` 单次调用无重试；全 A 路径 `thermometer_source.py:320,335` — `_fetch_all_a_with_retry` 最多 2 次尝试
- **影响**: 指数查询在 Legulegu 间歇性故障期间有更高概率退化到 stale cache 或 unavailable，而全 A 查询在相同故障模式下可恢复
- **建议改法和验证点**: 为指数源 `_load_pe_frame` / `_load_pb_frame` 添加相同重试机制，或统一抽取重试 helper
- **修复风险（低）**: 仅增加重试循环，不影响契约语义
- **严重程度（低）**: 已有 stale cache 作为安全网；实际可用性影响取决于 Legulegu 故障频率

### F2 — Duplicate Date Handling: Index (silent last-wins) vs All-A (fail-closed)

- **入口/函数**: `_records_by_date` / `_strict_positive_records_by_date`
- **文件(行号)**: `thermometer_source.py:453-485` (index, silent overwrite), `thermometer_source.py:488-538` (all-A, fail-closed on conflict)
- **输入场景**: 外部数据源返回同一日期多条不同估值记录
- **实际分支**: 指数路径在 `_records_by_date:483` 直接覆盖 `values[date_text] = value`；全 A 路径在 `_strict_positive_records_by_date:533-534` 抛出 `ThermometerSourceError`
- **预期行为**: 两条路径对数据完整性问题应一致处理
- **实际行为**: 指数路径静默接受最后一条记录，可能掩盖上游数据质量问题
- **直接证据**: `thermometer_source.py:483` — `values[date_text] = value` 无条件覆盖；`thermometer_source.py:533-534` — `if existing_value != value: raise ThermometerSourceError(...)`
- **影响**: 低概率数据完整性问题在指数路径被静默掩盖；当前未观测到 akshare 指数接口产生重复日期，但缺乏防御
- **建议改法和验证点**: 考虑统一为 fail-closed 或至少对冲突记录 warning（需要 observability 基础设施）
- **修复风险（低）**: 将指数路径改为 fail-closed 仅在 akshare 返回冲突数据时才会触发，属于正确行为
- **严重程度（低）**: 预存行为（P19-S1/S2），非 P19-S5 引入；当前数据源未产生冲突

### F3 — Dead Code: Public Page Adapter Path Unreachable

- **入口/函数**: `ThermometerService.run` / `_normalize_request`
- **文件(行号)**: `thermometer_service.py:149-171` (run), `thermometer_service.py:281-304` (_normalize_request)
- **输入场景**: 任何 `ThermometerRequest` 调用
- **实际分支**: `_normalize_request:304` 始终将无参请求 materialize 为 `index_code=ALL_A_MARKET_CODE`，导致 `run:170-171` 的 adapter 分支永远无法通过正常请求流到达
- **预期行为**: 过渡期后应明确处理或移除 dead path
- **实际行为**: `ThermometerSnapshot` 返回类型和 adapter 调用路径保留在 `run()` 签名和分支中，但不可达
- **直接证据**: `thermometer_service.py:304` — 最后的 fallthrough return 始终设置 `index_code=ALL_A_MARKET_CODE`；`thermometer_service.py:168-169` — adapter 分支仅在 `normalized.index_code is None` 时可达，此条件永假
- **影响**: 维护者可能误以为公开页 adapter 路径仍然活跃；类型签名 `ThermometerSnapshot | ThermometerReading | ThermometerBatchResult` 包含不可达分支
- **建议改法和验证点**: 在独立 cleanup gate 中移除 dead path 或将公开页 adapter 作为显式 opt-in 参数重新暴露
- **修复风险（低）**: 纯删除，CLI 默认行为不变
- **严重程度（低）**: S5-3 controller 已记录为 intentional transitional state；不阻塞 ship

### F4 — All-A Source `asyncio.gather` Without Exception Wrapper

- **入口/函数**: `AkshareAllAMarketThermometerSource.load_index_history`
- **文件(行号)**: `thermometer_source.py:291-294`
- **输入场景**: `asyncio.gather` 自身的异常（如 `CancelledError`）或 `asyncio.to_thread` 的非 `Exception` 子类抛出
- **实际分支**: gather 未包裹在 try/except 中；index 源（`thermometer_source.py:200-206`）有 try/except 包裹
- **预期行为**: 与 index 源一致的异常包装
- **实际行为**: 极边缘情况下（如 event loop 取消），原始异常可能逃逸而非被包装为 `ThermometerSourceError`
- **直接证据**: `thermometer_source.py:291-294` — `pe_frame, pb_frame = await asyncio.gather(...)` 无 try/except；对比 `thermometer_source.py:200-206` — index 源显式包裹
- **影响**: `CancelledError` 在同步 `asyncio.run()` 调用中实际上不会发生；仅在异步上下文中理论存在
- **建议改法和验证点**: 添加 try/except 保持两条路径风格一致
- **修复风险（低）**: 仅添加异常包装
- **严重程度（低）**: 当前所有调用均通过 `asyncio.run()` 同步执行，触发概率极低

## Cross-Slice Correctness Verification

### Source Contract Fidelity

| Contract Element | Index Source | All-A Source | Status |
|---|---|---|---|
| PE column | `滚动市盈率中位数` | `middlePETTM` | Per design §11 |
| PB column | `市净率中位数` | `middlePB` | Per design §11 |
| Date column | `日期` | `date` | Per source feasibility |
| Source name | `akshare_legulegu_index_pe_pb` | `akshare_legulegu_all_a_pe_pb` | Distinct, traceable |
| Market code | N/A | `wind_all_a` | Not overloaded as index |
| Null/negative handling | Skip (PE>0 filter) | Drop (None/≤0 → optional) | All-A stricter |
| Duplicate date | Last-wins | Fail-closed | See F2 |
| Retry | None | 2 attempts | See F1 |

### Boundary Integrity

| Boundary | Check | Result |
|---|---|---|
| UI → Service only | CLI imports no akshare, no source types | PASS |
| Service → no akshare | `thermometer_service.py` grep: zero akshare/stock_a_/legulegu | PASS |
| Service → no source fields | Service doesn't import `middlePETTM`, `middlePB`, `date` column names | PASS |
| Capability owns classifier | `classify_thermometer_code` in `thermometer_source.py`, shared via import | PASS |
| Cache stores only | `thermometer_cache.py` no calculation, no akshare | PASS |
| Analyze not expanded | Zero all-A in analyze code/tests/docs | PASS |
| Cache namespace separation | `market/` vs `index/` enforced via `_path_for` classifier | PASS |

### Failure Semantics

| Scenario | Index Behavior | All-A Behavior | Status |
|---|---|---|---|
| Schema drift (wrong column) | `ThermometerSourceError` fail-closed | `ThermometerSourceError` fail-closed | PASS |
| Bool/invalid value | `ThermometerSourceError` | `ThermometerSourceError` | PASS |
| NaN/Infinity value | Not explicitly checked (Decimal(str(value)) may parse) | `ThermometerSourceError` via `is_finite()` | All-A stricter |
| Source transient failure | `ThermometerSourceError` | `ThermometerSourceError` after retry | PASS |
| Stale cache available on failure | Returns stale cached reading | Returns stale cached reading | PASS |
| No cache on failure | Returns `unavailable` reading | Returns `unavailable` reading | PASS |
| Calculation contract error | Propagates `ValueError` | Propagates `ValueError` | PASS |
| Empty common dates | `ThermometerSourceError` | `ThermometerSourceError` | PASS |

### Cache Bypass Prevention

| Scenario | Result |
|---|---|
| Unsupported well-formed code (999999) → cache.load | Returns None (classifier gate) |
| Unsupported code → cache.save | Raises ValueError |
| Unsupported code → Service | Returns unavailable reading BEFORE cache lookup |
| Forged unsupported cache file | Not loaded (classifier gate in load()) |
| `wind_all_a` → index/ path | Not possible (classifier routes to market/) |
| `000300` → market/ path | Not possible (classifier routes to index/) |

### P19-S3 Non-Regression

- `tests/services/test_fund_analysis_service.py`: 20 passed, zero all-A references
- `fund_agent/services/fund_analysis_service.py`: no wind_all_a import
- `fund_agent/fund/analysis/valuation_state.py`: no wind_all_a in index mapping
- README line 179: explicitly states analyze only uses 000300/000905
- Fund README: "只对 index_fund / enhanced_index 且业绩基准 exact identity 映射到沪深300 000300 或中证500 000905 的基金调用自建温度计"

### Test/Docs Coverage

| Layer | Test Count | Coverage Areas |
|---|---|---|
| Source | 37 passed | Classifier, index merge, all-A merge, schema drift, bool/NaN/Infinity reject, date strictness, duplicate conflict, retry, no-arg fetcher, composite dispatch |
| Cache | (in 33) passed | Fresh/stale/corrupt, market/index namespace, unsupported save/load reject |
| Service | (in 33) passed | Default all-A routing, explicit index/all-A routing, batch ordering/dedup, unsupported item-level unavailable, stale fallback (index + all-A), unavailable (index + all-A), cache save failure, calculation error propagation, malformed reject |
| CLI | 38 passed | Default all-A plain/JSON, help text, --index wind_all_a/000300/000905, batch mixed, malformed exit 2, unavailable output, disclaimer |
| Analyze regression | 20 passed | P19-S3 000300/000905 exact identity unchanged |
| Docs | README.md, fund/README.md, tests/README.md | All synchronized to all-A default, no future promises |

## Open Questions

无。

## Residual Risk

- **Retry budget asymmetry (F1)**: 指数路径无重试，全 A 路径 2 次重试。在实际 Legulegu 可用性数据出现前，无法判断是否需要提升指数路径韧性。当前 stale cache 作为安全网已覆盖。
- **Duplicate date asymmetry (F2)**: 指数路径静默覆盖可能在极边缘情况下掩盖数据质量问题。历史数据未显示 akshare 指数接口产生重复日期，风险较低。
- **Dead code (F3)**: 公开页 adapter 路径不可达但不影响正确性。S5-3 controller 明确标记为 intentional transitional state。
- **Gather exception wrapping (F4)**: 当前同步调用模式下发概率极低；若未来改为异步调用需关注。
- **Legulegu 外部依赖**: 全 A PE 源 (`stock_a_ttm_lyr`) 和 PB 源 (`stock_a_all_pb`) 均依赖 Legulegu 公开页面。源不可用时依赖缓存和 unavailable 降级，不产生错误数据。

## Controller Residual Judgment (for controller review)

| Residual | Source Gate | Severity | Recommendation |
|---|---|---|---|
| F1: retry inconsistency | S5-1 DS F1, accepted non-blocking | Low | Accept; monitor Legulegu availability before raising retry budget for index path |
| F2: duplicate date asymmetry | New in aggregate review | Low | Accept; pre-existing S5-1/S5-2 behavior, not a P19-S5 regression |
| F3: dead adapter code | S5-3 controller noted as transitional | Low | Accept; defer to separate cleanup gate |
| F4: gather exception gap | New in aggregate review | Low | Accept; theoretical only in current sync invocation pattern |

## Verdict

**PASS_WITH_FINDINGS**

P19-S5 all-A market thermometer source gate is ready for phase readiness review. The three slices (S5-1 Capability Source, S5-2 Service/Cache, S5-3 CLI/Docs) form a coherent whole:

- All-A PE/PB data is correctly sourced from akshare Legulegu with exact `date`/`middlePETTM`/`middlePB` contract
- Service routes no-argument requests to `wind_all_a` without leaking source field knowledge upward
- Cache uses separate `market/` and `index/` namespaces to prevent cross-contamination
- CLI and documentation reflect the all-A default without overstating analyze integration
- P19-S3 exact 000300/000905 behavior is preserved with passing regression tests
- 108 combo tests pass across all layers with comprehensive failure path coverage

Four low-severity findings are recorded (F1–F4). None are blocking for draft PR readiness. All have been previously noted by slice reviewers or controller judgments, or are pre-existing behavior outside P19-S5 scope.

Recommended next gate: P19-S5 ready-to-open-draft-PR reconciliation.
