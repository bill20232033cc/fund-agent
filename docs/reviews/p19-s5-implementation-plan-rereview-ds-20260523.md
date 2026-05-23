# P19-S5 All-A Market Thermometer — Implementation Plan Re-Review (AgentDS)

## Verdict

**`pass`**

Patch 关闭了全部 5 个原 findings，未引入新 blocker。Plan 现可安全交给 implementation agent。

---

## Scope

- **Original review**: `docs/reviews/p19-s5-implementation-plan-review-ds-20260523.md` (5 findings, pass-with-risks)
- **Patched target**: `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- **Re-review type**: targeted — 只判断原 findings 关闭状态 + patch 是否引入新 blocker

---

## Original Finding Closure Status

### F1 (中) — unavailable name 映射位置未指定 → **CLOSED**

- **Patch 变更**:
  - §7.8 新增: "When source support or source failure returns `ThermometerUnavailable`, resolve the human-readable name through the shared Capability helper. For `wind_all_a`, the unavailable reading must use `index_name="万得全 A / 全 A 市场"`, not `index_name="wind_all_a"`."
  - §7.3 新增: "Expose one shared code classifier… plus helper name lookups."
  - S5-2 测试新增: "Source failure without cache returns unavailable reading with `index_name="万得全 A / 全 A 市场"`."
- **证据**: name 映射现在有明确的 shared helper 归属 + 具体测试

### F2 (中) — duplicate-date 检测影响现有指数路径 → **CLOSED**

- **Patch 变更**:
  - §7.3 明确分离 `AkshareAllAMarketThermometerSource` 与 `AkshareIndexThermometerSource`
  - S5-1 新增: "Harden all-A parsing to enforce strict `date`, positive Decimal, duplicate conflict detection, and common-date intersection. Do not change existing index `_records_by_date()` duplicate overwrite behavior in this slice unless adding explicit index regression tests proving no P19-S1/S2 behavior regression."
- **证据**: duplicate-date 检测被显式限定在 all-A 专用解析函数内，index 路径的 last-write-wins 行为保留

### F3 (低) — fetcher 签名与 unified source class 的张力 → **CLOSED**

- **Patch 变更**:
  - §7.3: "Controller decision: add a separate `AkshareAllAMarketThermometerSource` in this module, and keep `AkshareIndexThermometerSource` for six-digit indexes. Do not merge no-arg all-A fetchers into the symbol-based index source class."
  - S5-1: "Add `AkshareAllAMarketThermometerSource` with no-arg fetchers. … Add a thin composite source, for example `AkshareThermometerSource`, that implements `ThermometerDataSource.load_index_history(code)` by dispatching to the index source or all-A market source using the shared classifier."
- **证据**: 三个 class 的架构（index source / all-A source / composite dispatch）彻底消除了签名混用风险

### F4 (低) — CLI 公共页快照访问路径消失 → **CLOSED**

- **Patch 变更**:
  - §7.5 新增: "The legacy public-page adapter path becomes internal/transitional only in this gate. Do not remove `FundThermometerAdapter`; keep its dedicated data-layer tests. Do not add a public CLI flag unless a later controller decision reopens comparison UX."
  - S5-2 测试新增: "Public-page adapter tests remain in `tests/fund/data/test_thermometer.py`; Service no-arg default test is updated from public-page delegation to all-A source routing."
- **证据**: 决策显式化 — 保留代码和测试，标记为 internal-only，留待后续 Controller 裁决。不是 ambiguity，是 explicit deferral

### F5 (低) — NaN/Inf 检测遗漏 → **RESIDUAL (非 plan 缺陷)**

- **Patch 变更**: §8 Positive Decimal 保留 "Reject None, bool, non-numeric, NaN, Infinity and <= 0"
- **现状**: 由于 all-A 解析现在在独立的 `AkshareAllAMarketThermometerSource` 中从头实现（§7.3、S5-1），implementation agent 必须按 §8 实现 NaN/Inf 检测。Source feasibility 确认实际数据 0 NaN，风险仍为低
- **证据**: 不再是与共享 `_to_decimal` 的耦合问题，而是新代码的正确实现问题

---

## New Blocker Scan

对 patch 新增内容逐项检查：

| 新增决策 | 风险 | 判断 |
|---------|------|------|
| All-A date column = `"date"` (English)，与 index `"日期"` 分离 | 若实现 agent 混淆两者 | 不构成 blocker：§9 fixture 测试要求中文 `日期` all-A fixture fail-closed，强制验证 |
| Composite `AkshareThermometerSource` 作为统一 Service 注入点 | 过度抽象 | 不构成 blocker：复合 class 只做 classifier-based dispatch，逻辑极薄 |
| Shared `classify_thermometer_code` classifier 跨 source/cache/service 共享 | 循环依赖 | 不构成 blocker：classifier 在 Capability data 层，source 和 cache 都在同层或下层；Service 向下依赖 Capability 符合现有边界 |
| `_normalize_request()` materialize default `wind_all_a` | 与现有 public-page 路径互斥 | 不构成 blocker：这是 plan 的 intentional design choice，不是 bug |
| `_normalize_index_codes()` 接受 exact `wind_all_a` 或六位 ASCII digit | 非 ASCII digit 绕过 | 不构成 blocker：plan 明确要求拒绝 non-ASCII digit variants |
| P19-S3 analyze non-regression test 要求 | 测试不存在则需新增 | 不构成 blocker：plan 在 S5-2 和第 S5-3 validation 中都包含 `test_fund_analysis_service.py`，若不存在会因 pytest file-not-found 失败，自然 stop |
| `FundThermometerAdapter` 保留为 internal-only | 死代码 | 不构成 blocker：保留测试覆盖，代码不删除，Controller 后续裁决 |

---

## Residual Risks (post-patch)

- NaN/Inf 检测仍需 implementation agent 在 all-A 专用解析中显式实现（低风险，§8 指令已明确）
- Composite source dispatch 的 class 命名和模块内结构由 implementation agent 决定，plan 只给了 example
- `classify_thermometer_code` 精确签名（参数、返回值 Literal）由 implementation agent 按 §7.3 example 实现

---

## Final Re-Review Conclusion

**`pass`**

全部 5 个原 findings 已关闭（4 个直接关闭，F5 降为 residual 实现细节）。Patch 未引入新 blocker。Plan 可安全进入 implementation。

---

*Re-review by AgentDS, 2026-05-23 09:48 CST. No source, test, control, or design files were modified.*
