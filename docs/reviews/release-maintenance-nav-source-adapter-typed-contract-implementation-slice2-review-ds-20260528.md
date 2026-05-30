# NAV Source Adapter Typed Contract Implementation — Slice 2 Docs & Smoke Review (DS)

日期：2026-05-28

Work unit：`NAV repository/source adapter typed contract implementation gate`

Gate：Slice 2 — Docs, Design Sync, Real 006597 Smoke Evidence

角色：code review agent (DS)，非 controller。不 implement、fix、commit、push、PR、merge。

审查范围：docs diff + evidence artifact。不审查 Slice 1a/1b 实现代码（MiMo 已审）。

## 审查依据

- `AGENTS.md`（规则真源）
- `docs/design.md`（设计真源）
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md` Slice 2
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-evidence-20260528.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `git diff` for the three docs

## 逐项审查

### F1 — Docs 只陈述当前已实现事实，不把未来设计写成当前事实

**通过。**

`docs/design.md` 新增段落（diff +2行正文 +1行表格）：

- `FundNavRepository.load_nav_series()` 描述为「当前 Fund data 层 typed NAV repository contract」，使用「当前」限定，是已实现代码事实。
- 「后续路径型 drawdown metric 只能消费…typed 边界，不得直接读取 Akshare、SQLite cache…」是对未来 consumer 的约束声明（future consumer rule），不是声称该消费路径已存在。措辞「只能」「不得」是规则语气，不冒充当前事实。
- 「当前 Akshare / 天天基金 `单位净值走势` 路径只归一化为…」使用「当前」「只」限定，准确反映 Slice 1b 实现的 single-source raw-unit-only 现状。

`fund_agent/fund/README.md` 新增段落：

- `FundNavRepository.load_nav_series()` 描述为「是 data 层当前 typed NAV series contract」，旧 adapter 为「legacy/snapshot/analyze 兼容入口」。区分清晰。
- 「当前 Akshare `单位净值走势` 只会被 typed repository 标记为…」使用「当前」「只会」，不暗示未来有其他 source。

`tests/README.md` 新增内容：

- `test_nav_repository_contract.py` 说明使用「使用 fake adapter，不触发真实网络」——当前测试事实。
- Real smoke 段落明确「不放入常规 pytest」「只作为 implementation evidence」「即使成功也只证明 raw_unit_nav…不能证明 adjusted / total-return drawdown evidence」——准确限定 smoke 意义。

无任何一处把 adjusted、cumulative、total-return、verified identity 或 drawdown blocker 解除写成当前事实。

### F2 — Docs 区分 legacy NavDataResult 与 FundNavRepository.load_nav_series typed 边界

**通过。**

三份文档均明确区分：

| 文档 | Legacy 表述 | Typed 边界表述 |
|------|------------|---------------|
| `docs/design.md` | 「旧 `NavDataResult` 仅保留为 `analyze`、`checklist`、snapshot 和既有 P1 façade 兼容结果」 | 「后续路径型 drawdown metric 只能消费 `FundNavRepository.load_nav_series()` 的 typed 边界」 |
| `fund_agent/fund/README.md` | 「旧 `FundNavDataAdapter.load_nav_data()` 继续作为 legacy/snapshot/analyze 兼容入口，返回 `NavDataResult` 并保持 `source="nav_cache" / "akshare"` 与 `cached` 语义」 | 「`FundNavRepository.load_nav_series()` 是 data 层当前 typed NAV series contract」 |
| `tests/README.md` | `test_nav_data.py` 描述不变，仍为「净值数据适配器测试」 | `test_nav_repository_contract.py` 独立说明，覆盖 typed contract |

`fund_agent/fund/README.md` 内部分层描述同步更新：`data/` 从「外部数据适配器」扩展为「外部数据适配器与 typed repository」，并说明 `load_nav_data()` 保留 legacy 兼容、`load_nav_series()` 是 typed 边界。

### F3 — Docs 保留 raw_unit_nav / requested_code_only / not strong eligible 语义，不声称 adjusted / cumulative / total-return / verified identity / drawdown_stress unblock

**通过。**

关键语义在全部三份 docs + evidence 中一致保留：

- `docs/design.md`：「`nav_type="unit_nav"`、`adjusted_basis="raw_unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`identity_status="requested_code_only"`，并强制 `strong_drawdown_evidence_eligible=False`」「没有证明分红调整、累计净值或 total-return basis，也没有解除债券基金 `drawdown_stress` blocker」
- `fund_agent/fund/README.md`：「`strong_drawdown_evidence_eligible=False`；raw unit NAV 不能作为模板第 6 章强 drawdown evidence，也不解除当前 `drawdown_stress` blocker」
- `tests/README.md`：「该 smoke 即使成功也只证明 `raw_unit_nav`、`unit_nav`、`not_adjusted` 和 `strong_drawdown_evidence_eligible=False`，不能证明 adjusted / total-return drawdown evidence」

Evidence artifact 显式列出 non-claims（第 106–112 行），与 plan 第 56–65 行 Non-Goals 对齐。

### F4 — Smoke evidence 使用 FundNavRepository 边界，记录 provenance / identity / adjusted_basis；无直接 SQLite / Akshare / cache 绕过

**通过。**

Evidence doc 第 30–37 行声明访问边界：

- 未直接读 SQLite
- 未直接调用 Akshare
- 未绕过 adapter/repository

Smoke JSON（第 43–58 行）所有字段来自 `FundNavRepository.load_nav_series()` 返回的 `FundNavSeries` 投影：

```json
{
  "fund_code": "006597",
  "share_class": "A",
  "records": 1809,
  "adjusted_basis": "raw_unit_nav",
  "nav_type": "unit_nav",
  "dividend_adjustment_status": "not_adjusted",
  "identity_status": "requested_code_only",
  "strong_drawdown_evidence_eligible": false,
  "source": "nav_cache",
  "origin_source": "akshare",
  "cached": true,
  "cache_updated_at": "2026-05-28 04:04:23.530741+00:00"
}
```

Smoke assertions（第 60–68 行）逐项验证 plan 要求的 7 个 expected smoke assertions，全部 pass。

Provenance 记录完整：`source` / `origin_source` / `cached` / `cache_updated_at` 均存在；cache hit 场景下 `origin_source="akshare"` 可见，满足 plan 要求「即使 cache hit，origin source 仍可见」。

### F5 — 完整验证证据存在：ruff check 全通过；full pytest coverage gate 通过，893 tests，92.40% coverage

**通过。**

Evidence doc 第 72–95 行记录：

- `uv run ruff check .` → `All checks passed!`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` → `893 passed in 4.37s`，总覆盖率 `92.40%`

两命令均按 plan Slice 2 validation 要求执行，无删减。

### F6 — Scope：无 implementation-control 更新，无 extractor / snapshot / score / quality / golden / release / PR 变更

**通过。**

Evidence doc 明确：

- 第 11 行：「`docs/implementation-control.md` intentionally not edited; controller owns post-closure control update」
- 第 116–125 行 Non-Goal Preservation 逐项列出未触碰的模块：snapshot schema、score policy、quality gate / FQ0-FQ6、bond risk extractor、renderer、Service / CLI、Host / Agent / Dayu、golden / baseline fixtures、snapshot/score/quality gate rerun

`git diff` 确认只有三个 docs 文件变更，无代码或 control doc 改动。

### F7 — 是否有措辞可能削弱 FQ0-FQ6 或未来 drawdown contract

**未发现削弱性措辞。**

逐项检查：

- **FQ0-FQ6**：无任何 FQ 规则语义变更；docs 不涉及 FQ 规则描述修改。Evidence 明确声明 quality gate semantics 未改变。
- **drawdown contract**：三份 docs 一致强调 `raw_unit_nav` + `requested_code_only` → `strong_drawdown_evidence_eligible=False`，且 `drawdown_stress` blocker 未解除。这种反复声明是强化而非削弱。
- **Future consumer rule**：`docs/design.md` 中「不得直接读取 Akshare、SQLite cache、snapshot JSONL 或旧 raw payload」是对未来 drawdown metric 的硬约束，保护 typed contract 不被绕过。
- **调整基础声明**：无一处将 raw unit NAV 描述为可接受的 drawdown evidence；`adjusted_basis="raw_unit_nav"` 始终与 `strong_drawdown_evidence_eligible=False` 绑定。
- **Identity 声明**：`identity_status="requested_code_only"` 始终与 `not strong eligible` 绑定，不暗示 verified identity。

**无负面发现。**

## 观察（非阻断）

以下观察不影响 acceptance，仅供 controller 参考：

1. **Smoke JSON key naming**：evidence 中 smoke JSON 使用 flat keys（`"source"`, `"origin_source"`, `"cached"`, `"cache_updated_at"`），与 plan 中示例代码 `s.source.source_name` / `s.source.origin_source` 的嵌套路径不完全对应。这是 smoke 输出格式选择，不影响 typed contract 正确性。实际 `FundNavSeries.source` 是 `NavSourceMetadata` dataclass，嵌套字段在 typed API 中可正常访问。

2. **Share class mapping detail**：smoke JSON 显示 `"share_class": "A"`，但未展示完整的 `ShareClassMapping`（含 `mapping_status`、`mapping_evidence` 等字段）。plan 要求 `mapping_status="requested_code_default_a"` 或同等显式状态。建议在后续 controller acceptance 时抽查 `ShareClassMapping` 完整字段，确认 `mapping_status` 确为显式默认映射标记而非静默推断。

3. **One-line command SyntaxError**：evidence 记录了 plan 中的单行 `python -c` 命令因 `async def` 不能出现在分号后的语法限制而失败。这是命令格式问题，不影响 repository 正确性。evidence 透明记录并重跑，做法正确。

## 结论

**Accepted。**

Slince 2 docs 更新与 smoke evidence 满足 plan 全部 7 项要求：

- 三份 docs 只陈述当前已实现事实，不把未来设计写成当前事实
- Legacy `NavDataResult` 与 typed `FundNavRepository.load_nav_series()` 边界区分清晰
- `raw_unit_nav` / `requested_code_only` / `not strong eligible` 语义完整保留，未声称 adjusted / cumulative / total-return / verified identity / drawdown_stress unblock
- Smoke 通过 `FundNavRepository` 边界执行，provenance / identity / adjusted_basis 均记录，无直接 SQLite / Akshare / cache 绕过
- 完整验证通过：ruff check 全绿，893 tests passed，92.40% coverage
- Scope 合规：无 implementation-control、extractor、snapshot、score、quality、golden、release、PR 变更
- 未发现削弱 FQ0-FQ6 或未来 drawdown contract 的措辞

`drawdown_stress` blocker 仍未解除，与本 gate non-goal 一致。
