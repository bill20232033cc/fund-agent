# CSRC EID Accumulated NAV Adapter Normalization — Plan Review (GLM)

日期：2026-05-29
角色：plan review worker（GLM），非 controller，非 implementation worker。
Work unit：`CSRC EID accumulated NAV adapter normalization implementation gate`

## Verdict

**accepted-with-required-fixes**

Plan 整体质量高，真源复述准确，scope 控制严格，slice 划分合理，test/validation 矩阵完整。存在 2 个 required fix 和 4 个 non-blocking finding。无 blocking finding。Required fix 均为 code-generation-readiness 缺口，不涉及 scope 或 design 方向变更。

---

## Review Focus 确认

| Review focus | 评估 |
|---|---|
| code-generation-ready / 无需自行选架构 | **部分通过**；2 处需补充（见 R1、R2） |
| CSRC EID endpoint/params/rnd handling 稳健 | **通过**（§4.1 明确排除 rnd/t 依赖） |
| 默认 FundNavRepository 切到 CSRC EID 合理性 | **通过**（见 R2 补充要求） |
| A/C/E/F share-class identity 可复核/无混算 | **通过**（§4.3 双重验证 + fail-closed） |
| 022176/F direct search gap fail-closed | **通过**（§4.3 明确 identity_mismatch fail closed） |
| accumulated_nav 未伪装为其他 basis | **通过**（§4.4 明确禁止 dividend_adjusted/total_return） |
| provenance 字段扩展明确无 free dict | **通过**（§4.5 显式 source_query_params tuple） |
| failure taxonomy 保持 8 类 fail-closed | **通过**（§4.6 无新增） |
| stock-sdk evidence-only / date-shift 锁 | **通过**（§4.7 + Slice 4 锁定测试） |
| forbidden scope 未触碰 | **通过**（§3 + §5 明确禁止列表） |
| tests/validation/smoke 足以验收 | **通过**（§7 + §8 矩阵完整） |

---

## Findings（按 severity 排序）

### R1 — [Medium/Required Fix] Source adapter Protocol / type contract 未定义

**章节**：§5 Affected Files、§6 Slice 2、§6 Slice 3

**问题**：Plan 引入 `CsrcEidNavSource` 作为新类，返回 `_RawNavSourceResult`（`nav_data.py` 的私有类型），并要求默认 `FundNavRepository()` 使用 CSRC EID。但 plan 未定义：

1. `CsrcEidNavSource` 与现有 `FundNavDataAdapter` 的共享 Protocol 或 base class
2. Repository 构造函数当前签名为 `source_adapter: FundNavDataAdapter | None`，切到 CSRC EID 后类型注解如何变更
3. `_RawNavSourceResult` 是 `nav_data.py` 的私有 frozen dataclass，CSRC EID source 返回该类型意味着要么跨模块引用私有类型，要么在 `csrc_eid_nav_source.py` 中定义独立但结构兼容的 DTO

**为什么阻塞 code-generation**：Implementation worker 需要自行决定用 Protocol、Union type 还是 base class，这是架构选择而非实现选择。

**Required fix**：

- Plan 必须显式声明 adapter Protocol 接口（例如 `_NavSourceAdapter` Protocol，含 `load_raw_nav_source` 方法签名和返回类型），或在 `_RawNavSourceResult` 扩展后指定 CSRC EID source 返回该扩展类型。
- 必须指定 repository 构造函数的类型注解如何更新（`_NavSourceAdapter | None` 或其他）。
- 若使用 Protocol，plan 应指明 Protocol 定义在哪个文件（推荐 `nav_models.py` 或独立 Protocol 模块）。

---

### R2 — [Medium/Required Fix] Repository source selection mechanism 未明确

**章节**：§6 Slice 3

**问题**：Plan 要求"Make default FundNavRepository() use CsrcEidNavSource for load_nav_series()"，同时要求"Preserve tests with injected _FakeRawNavAdapter for raw-unit path"。但 plan 未明确：

1. 默认构造的 repository 内部如何选择 source（直接构造 `CsrcEidNavSource`？工厂函数？）
2. 当 CSRC EID 返回 `unavailable` 时，是否尝试 Akshare raw unit fallback，还是直接抛出？Plan 只说"本 gate 默认不 fallback 到 stock-sdk"，未提及 Akshare。
3. 已有 injected adapter 的测试如何绕过 CSRC EID 默认路径——是靠检测 DTO 类型，还是靠构造函数传入 mock？

当前代码中 `FundNavRepository.__init__` 接受 `FundNavDataAdapter | None`，默认构造 `FundNavDataAdapter()`。切到 CSRC EID 后，这个默认行为需要变更，但测试注入机制也需要保留。

**为什么阻塞 code-generation**：Implementation worker 需要自行设计 source selection 逻辑，这影响 repository 的公共构造函数签名和内部 flow，是架构选择。

**Required fix**：

- 明确默认 repository 构造行为：`FundNavRepository()` 无参构造时内部创建 `CsrcEidNavSource`（或组合 adapter）。
- 明确 `unavailable` 时的行为：是否 fallback 到 Akshare raw unit，还是直接 fail。推荐：直接 fail（与 plan 的 fail-closed 精神一致），但需显式声明。
- 明确测试注入路径：构造函数 `source_adapter` 参数接受 Protocol 类型（见 R1），测试注入 `_FakeRawNavAdapter` 走 raw unit normalization 分支。

---

### N1 — [Low/Non-blocking] `source_nav_type` / `source_adjustment_basis` 为 deferred design choice

**章节**：§6 Slice 1

**问题**：Plan 在 `_RawNavSourceResult` 扩展中提到可选 `source_nav_type: str | None` / `source_adjustment_basis: str | None`，并附注 "only if repository needs to branch without isinstance; otherwise avoid"。这把一个设计决策留给 implementation worker。

**评估**：这是一个较小的设计选择。Repository 可以通过检查 DTO 是否包含 CSRC EID specific 字段（如 `source_id`）来区分 accumulated vs raw unit 路径，不需要 `source_nav_type`。不阻塞，但建议 plan 明确选择一种方式。

**建议**：明确推荐不在 `_RawNavSourceResult` 上加 `source_nav_type` / `source_adjustment_basis`，而是让 repository 根据 `NavSourceMetadata.source_name` 或 DTO 结构选择 normalization 路径。

---

### N2 — [Low/Non-blocking] HTTP client 和 HTML parser 选择未指定

**章节**：§6 Slice 2

**问题**：Plan 说 "Use stdlib urllib.request or existing project HTTP pattern if present; no new dependency unless controller approves"。项目已有 `httpx` 依赖（用于文档仓库），CSRC EID 返回 HTML 需要解析，但 plan 未指定 HTML 解析方式。

**评估**：项目 `pyproject.toml` 已有 `httpx` 依赖，且 `documents/sources.py` 使用 `httpx`。HTML 解析可用 stdlib `html.parser`。这是一个实现细节，不阻塞。

**建议**：明确推荐使用 `httpx`（已有依赖）和 stdlib `html.parser`，避免新依赖。

---

### N3 — [Low/Non-blocking] A/C blank accumulated NAV 日期集合未完全枚举

**章节**：§6 Slice 2、§6 Slice 3

**问题**：Prior evidence review residuals 已记录 "A/C blank accumulated NAV date set not fully listed"。Plan §4.6 说 "若 blank 累计净值 rows 落在 requested window 内" 但未枚举 A/C blank rows 的精确日期集。

**评估**：CSRC EID evidence 记录了 A 2018-12-07 和 2018-12-14 有 blank accumulated NAV。Plan 的 fail-closed 语义（`missing_date_range`）足够处理，但 fixture tests 可以更精确。

**建议**：在 Slice 2 fixture tests 中包含 A/C blank accumulated rows 的具体日期 fixture（至少 2018-12-07 和 2018-12-14），确保 fail-closed 逻辑被精确验证。

---

### N4 — [Low/Non-blocking] `单位净值` blank 处理语义与 `raw_payload` 记录策略需明确

**章节**：§4.2、§6 Slice 3

**问题**：Plan §6 Slice 3 说 "validate optional 单位净值 as Decimal positive and store in raw_payload; blank unit NAV -> schema_drift because source row no longer matches accepted schema"。但 CSRC EID A/C 最早两行（2018-12-07、2018-12-14）的 `累计净值` 为 blank，`单位净值` 有值。如果 `单位净值` blank 触发 `schema_drift`，但 `累计净值` blank 只触发 `missing_date_range`（按 §4.6），那么这两行的处理会有分支复杂性。

**评估**：不阻塞。当 `累计净值` blank 时整行已被 drop 或归类为 `missing_date_range`，不会到达 `单位净值` blank 检查。但如果 `累计净值` 有值而 `单位净值` blank，是否触发 `schema_drift`？Plan 应明确这种 edge case 不存在于 CSRC EID evidence 中，或者明确处理方式。

**建议**：在 Slice 3 tests 中添加一个 fixture：`累计净值` 有值但 `单位净值` blank 的 row，明确验证处理方式。

---

## 真源一致性检查

| 真源 | Plan 复述 | 一致性 |
|---|---|---|
| `AGENTS.md` 四层边界 | §1.1 正确复述 | ✅ |
| `AGENTS.md` 禁止 extra_payload | §1.1、§4.5、§9 均遵守 | ✅ |
| `AGENTS.md` fallback 分类 | §1.1、§4.6 遵守 8 类 | ✅ |
| `docs/design.md` typed NAV contract | §1.2 正确引用 FundNavSeries/Record/Metadata | ✅ |
| `docs/design.md` raw unit current fact | §1.2 明确当前 raw-unit-only | ✅ |
| `docs/implementation-control.md` next entry point | §1.3 正确引用 | ✅ |
| `docs/implementation-control.md` allowed scope | §1.3 完整复述 | ✅ |
| Typed NAV controller judgment | §1.4 正确复述 8 类 taxonomy + 兼容矩阵 | ✅ |
| CSRC EID / stock-sdk judgment + evidence | §1.5 完整复述 endpoint/classification/identity | ✅ |
| 006597 latest snapshot/score | §1.6 正确记录 bond_risk_evidence_missing | ✅ |

**无真源不一致。**

---

## Scope Boundary 检查

| 检查项 | 结果 |
|---|---|
| 是否触碰 bond extractor | ❌ 未触碰（§3 + §5 明确禁止） |
| 是否触碰 score / quality gate | ❌ 未触碰 |
| 是否触碰 golden / snapshot | ❌ 未触碰 |
| 是否触碰 Host/Agent/dayu | ❌ 未触碰 |
| 是否触碰 PR/push/release | ❌ 未触碰 |
| 是否实现 drawdown metric | ❌ 未实现（§2 + §3 明确排除） |
| 是否解除 drawdown_stress blocker | ❌ 未解除（§1.3、§11 明确声明） |
| 是否引入 stock-sdk runtime | ❌ 未引入（§4.7 + Slice 4 锁定） |
| 是否引入 extra_payload / free dict | ❌ 未引入（§4.5 显式字段） |
| Gate classification 为 heavy | ✅ 正确（改变 runtime source normalization） |

---

## Test Matrix 完整性评估

| Test requirement (§7) | Coverage | 评估 |
|---|---|---|
| CSRC EID A fixture normalizes to accumulated | Slice 2 + 3 | ✅ |
| A/C/E/F mapping from detail page | Slice 2 | ✅ |
| F direct-search missing but detail succeeds | Slice 2 | ✅ |
| Identity mismatch code/share_class conflict | Slice 2 + 3 | ✅ |
| Malformed search/detail/list -> schema_drift | Slice 2 | ✅ |
| HTTP unavailable | Slice 2 | ✅ |
| Pagination integrity | Slice 2 | ✅ |
| Missing accumulated: outside dropped / inside -> missing_date_range / all blank -> adjustment_basis_unknown | Slice 3 | ✅ |
| Malformed date/value | Slice 3 | ✅ |
| stock-sdk rejected (date shift integrity_error) | Slice 4 | ✅ |
| Raw unit ineligible (strong_drawdown_evidence_eligible=False) | Slice 3 | ✅ |
| No extra_payload / **kwargs | Slice 1 | ✅ |
| Docs reflect current code facts only | Slice 5 | ✅ |

**缺口**：无显著缺口。N3 和 N4 建议补充 edge case fixture。

---

## Stop Conditions 评估

Plan 的 stop conditions 合理：

- Slice 1：如果 source_query_params 需要大量下游改写 → ask controller ✅
- Slice 2：如果 CSRC EID 需要非公开 auth / JS 执行 / random token as state → stop ✅
- Slice 3：如果 repository 无法支持双路径 → ask controller, 不加 source_options dict ✅
- Slice 4：不安装 npm 包 ✅
- Slice 5：full tests/ruff fail → stop; real smoke schema_drift/identity_mismatch 等 → controller 分类 ✅

---

## Residual Risks

| Risk | Severity | Mitigation |
|---|---|---|
| CSRC EID public endpoint schema 在实现时已变化 | Medium | Slice 2 stop condition 已覆盖；fixture tests 不依赖网络 |
| CSRC EID 需要非公开的 rate-limiting 或 blocking | Medium | `unavailable` fail-closed；controller 接受 environment residual |
| A/C blank accumulated NAV rows 的精确日期窗口处理复杂度 | Low | Fail-closed 语义足够；N3 建议精确 fixture |
| `source_query_params` 字段加入 `NavSourceMetadata` 后需要 freeze check | Low | frozen dataclass + default `()` 保证向后兼容 |
| `_RawNavSourceResult` 扩展后可能影响 Akshare raw path 构造 | Low | Slice 1 要求保持 legacy 构造不变 |

---

## Completion Signal 评估

Plan §11 列出 6 个 completion signals：

1. ✅ All planned slices implemented
2. ✅ Required validations pass or unavailable residual classified
3. ✅ Evidence artifact exists under docs/reviews/
4. ✅ git diff shows only allowed files
5. ✅ Artifact states drawdown_stress blocker unresolved
6. ✅ No report/snapshot/score/quality/golden modified

---

## Recommended Controller Actions

1. 要求 planning worker 修复 R1 和 R2 后重新提交 plan fix（或由 controller 批准 minor amendment）。
2. 修复后派 implementation worker 按 Slice 1-5 实现。
3. 实现后派至少两份独立 review，重点审查 source identity、share-class separation、provenance、failure taxonomy、no drawdown metric / no blocker 解除。
