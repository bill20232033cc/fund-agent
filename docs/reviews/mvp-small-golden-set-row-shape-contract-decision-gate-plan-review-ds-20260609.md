# MVP Small Golden Set Row-shape Contract Decision Gate Plan Review — AgentDS

## Gate

- Review target: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md`
- Reviewer: AgentDS
- Date: 2026-06-09
- Role: independent plan review only; no file modifications

## Source Evidence Read

- `AGENTS.md` Gate 轻重分类规则 + 硬约束
- `docs/current-startup-packet.md` §2 current mainline
- `docs/implementation-control.md` top status/current gate closeout (lines 1–75)
- `docs/design.md` via rg: Slice E, FundDocumentRepository, extractor/models/profile/manager_ownership/holdings_share_change/bond_risk_evidence references
- `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-controller-judgment-20260609.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-controller-judgment-20260609.md`
- `tests/fund/test_small_golden_set_extractor_correctness.py` (lines 1–50, xfail patterns)
- `fund_agent/fund/extractors/models.py` (relevant dataclass surfaces)
- `fund_agent/fund/extractors/profile.py` (relevant extractor surfaces)

## Findings

### F1 — Heavy classification is justified (INFO)

**Evidence**: AGENTS.md:56–57 heavy 定义为「架构边界、公共契约、schema/migration、质量门控语义」。Plan:52–61 列举四个残余每个都改变 extractor public output contract 或 schema 语义。

**Analysis**: 每个残余都要求新增 `ExtractedField` 输出契约（`portfolio_manager_tenure`、`risk_characteristics`、`bond_top_holdings`、`target_fund_holdings`），属于 public contract 变更。Plan 的「因为这些选择影响公共 extractor contract、snapshot comparability、下游 score/golden semantics 和 fail-closed correctness 规则」论证与 AGENTS.md 标准一致。

**Verdict**: INFO。分类正确，无争议。

---

### F2 — Plan correctly requires additive contracts before tests/fixes for all four residuals (INFO)

**Evidence**: Plan:63–70 每个 residual 决策列均为「Needs new additive output contract before tests」；Plan:85–90 unlock 规则中所有 residual 当前 `May pass now?` = No，`May add failing tests next?` = Yes only after contract accepted。

**Analysis**: 四残余均不存在可用的当前 extractor surface（confirmed by code evidence）：
- `manager`: `profile.py:35` `fund_manager` 是 scalar，「基金经理」单字段匹配，无 list/tenure 语义 (`profile.py:791`)；`manager_ownership.py` 的 `manager_alignment` 是 `strategy_text/turnover/holding/holder` (`models.py:649–652`)，不是 identity/tenure
- `risk`: `profile.py:837–839` 的 `style_positioning` 走 `_derive_style_positioning()`，输入来自投资目标/范围推断 (`profile.py:861–868`)，不是 `§2.2` 风险披露原文
- `006597`: `holdings_share_change.py` 只有 equity top-ten/stock detail 路由，无 bond top-holding；`bond_risk_evidence.py` 是 chapter 6 七组模板风险证据 (`models.py:165`)
- `110020`: `holdings_share_change.py` 无 target ETF/fund 路由；retained oracle 无 `code`

Plan 的「先 contract 后 failing test 后 fix」顺序正确。

**Verdict**: INFO。顺序决策与当前代码事实一致。

---

### F3 — Plan avoids reusing wrong current surfaces (NON-BLOCKING)

**Evidence**: Plan:63–70 每个 residual 的 Semantic mismatch 列与 Stop conditions 列均显式拒绝错误表面：
- manager: 「Do not overload `fund_manager` or `manager_alignment`」(line 67)
- risk: 「Do not map it to `style_positioning`; do not reuse `bond_risk_evidence`」(line 68)
- `006597`: 「Stop if implementation reuses equity `top_holdings` without distinct source/status, routes through `bond_risk_evidence`」(line 69)
- `110020`: 「Stop if implementation fabricates ETF code from fund name, maps target ETF into stock `top_holdings`」(line 70)

**Analysis**: 所有错误表面均被正确识别并列入 stop conditions。Plan 当前事实 (items 7–11, lines 35–39) 也显式标注了每个现有表面的局限性。

**Minor observation**: Plan:68 risk contract 说「normalized category/risk-return summary only if directly present」——这个约束在 stop condition 里没有对等强调。Stop condition 写道「stop if the route collapses risk to fund type」，但未显式说 stop if route collapses risk to `category + risk-return label` without raw disclosure text。这是边缘情况，不影响 plan 整体方向。

**Verdict**: NON-BLOCKING。核心错误表面全部被拒绝，仅 risk stop condition 可稍加强「fund type label only」覆盖。

---

### F4 — Non-goals are complete (INFO)

**Evidence**: Plan:43–49 列出 10 条 non-goals。

**Analysis**: 对照 implementation-control.md:9 current gate closeout 与 controller judgment 的禁止项，plan non-goals 覆盖：
- PDF 读取 ✓
- network/FDR/fallback/live/provider ✓
- extractor/config 修改 ✓
- fixture projection ✓
- exact/numeric correctness acceptance ✓
- golden/readiness promotion ✓
- 无关 untracked files ✓
- PR/release/merge 状态变更 ✓

未遗漏。

**Verdict**: INFO。Non-goals 完整。

---

### F5 — Plan avoids accepting exact/numeric correctness prematurely (INFO)

**Evidence**: Plan:48 non-goal 「Do not accept exact/numeric correctness for residual fields」；Plan:68 risk stop condition 「stop if exact/numeric correctness is claimed for free-text residuals」；Plan:95–99 acceptance matrix 每行均标注「No golden/readiness promotion」。

**Analysis**: Risk 字段是 free-text disclosure，不应以 exact string match 作为唯一接受标准；manager tenure 的 date 精确性取决于 PDF parser fidelity 而非 extractor contract；bond/ETF holdings 的 fair_value_cny 精确性同样受 parser 影响。Plan 正确地将 exact/numeric correctness 与 contract shape 分开。

**Verdict**: INFO。正确。

---

### F6 — Slices, unlock rules, stop conditions, residual owners, next entry are code-generation-ready (NON-BLOCKING)

**Evidence**: Plan:
- Slices A–F: lines 101–165
- Unlock rules: lines 72–90
- Stop conditions: per-residual table lines 66–70
- Residual owners: lines 202–209
- Next entry: lines 217–223

**Analysis**: Slice 拆解合理：A (contract review) → B (test-only guards) → C/D/E (implementation) → F (aggregate review)。每个 slice 有明确的 allowed files、expected outcome、stop condition。

**Minor observation**: Slice A 是「Contract Review And Model Surface Plan」——它本身是一个 planning gate，plan 未显式说明 Slice A 是否也应分类为 heavy（因为它决定 public contract names/schemas）。按 AGENTS.md:57「分类不确定时选择更重一级」，Slice A 大概率也是 heavy。这不影响当前 plan 的有效性，但 controller 在进入 Slice A 时应注意。

**Second observation**: Slice B (line 117) 说「add helpers only for minimal §4.1.2, §2.2, §4.4.1, §8.6, and §8.2 synthetic parsed report sections/tables built from oracle values」——这些 helper 如果构造不正确（例如用错误的 section id、错误的 table header），会导致 test 的 failing/passing 信号失真。Plan 的 stop condition「test needs non-oracle values, full PDF text, parser cache, network, FDR, fallback, or production normalization」(line 121) 正确排除了主要风险，但未显式说 synthetic report 的 section 结构必须经过 review。

**Verdict**: NON-BLOCKING。Slices 结构合理，两个小观察不影响 plan 接受。

---

### F7 — Plan self-consistency check (INFO)

**Cross-reference verification**:

| Plan claim | External evidence | Match? |
|---|---|---|
| Baseline `d61071a` | `git log` HEAD (from task context) = `d61071a` | Yes |
| Next entry matches control truth | `implementation-control.md:10` next entry = `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals` | Yes |
| Current gate classification `heavy` | `implementation-control.md:74` next gate classification = `heavy` for extractor public behavior | Yes |
| Retained excerpt JSON is only oracle | Controller judgment (equity-like holdings):16 "The only correctness oracle remains" | Yes |
| Four residuals not accepted passing | Controller judgment (equity-like holdings):25 "Blocked residuals preserved: manager, retained risk, 006597 bond top holding, 110020 target ETF holding" | Yes |
| `profile.py` has scalar `fund_manager` | `profile.py:791` `_extract_field(report, "fund_manager")` returns single matched field | Yes |
| `manager_ownership.py` no portfolio-manager list | `models.py:649–652` `ManagerOwnershipResult` fields: strategy_text, turnover, alignment, holder structure | Yes |
| `holdings_share_change.py` no bond/target-fund route | `models.py:664` `holdings_snapshot: ExtractedField[dict]` with `top_holdings` only | Yes |

无一矛盾。

**Verdict**: INFO。Plan 自洽且与外部证据一致。

---

### F8 — Adversarial pass: what could break this plan? (INFO)

**Scenario 1 — Contract creep**: Slice A 可能试图在一个 gate 里同时定义四个 additive contract。如果 reviewers 觉得范围过大，可能导致 contract review 不完整。Mitigation: plan 已将每个 residual 的 contract route 独立列出 (lines 67–70)，controller 可以在 Slice A 中按 residual 拆分 sub-slices。

**Scenario 2 — ParsedAnnualReport construction ambiguity**: Slice B 的 synthetic report construction 依赖测试作者正确理解 `ParsedAnnualReport` 的 section/table 模型。如果 helper 构造不正确（例如 section id 与实际 parser 输出不一致），test 可能错误地 passing 或 failing。Mitigation: 这是 Slice B 的 stop condition 范围，plan 正确地将此风险推迟到 Slice B review。

**Scenario 3 — `110020` code field dispute**: Plan 说 `code` 字段 optional only when directly disclosed (line 70)。如果未来有人从 fund name 推断 ETF code（例如从「易方达沪深300ETF」推断 code 510310），这违反了 plan 的 stop condition。Plan 的 stop condition「Stop if implementation fabricates ETF code from fund name」正确预防了这个问题。

**Scenario 4 — Risk free-text comparison fragility**: Plan:68 建议 risk 输出「raw disclosure text or exact accepted characteristic clauses」。如果 risk 字段在不同年报中的措辞有微小变化（如标点、空格），strict text match 会脆断。Plan 正确地将此标记为「text/disclosure assertions, not numeric correctness」(line 97)，但未显式讨论 text normalization 策略。这不影响 planning gate，但 Slice A contract 设计时应考虑。

**Verdict**: INFO。四个场景均有 plan 内建 mitigation 或可推迟到后续 slice 处理。

---

## Verdict: PASS

无 BLOCKING 发现。

F3 与 F6 的 NON-BLOCKING 观察不阻止 plan 接受：
- F3: risk stop condition 可稍加强「collapse to fund type label only」
- F6: Slice A 可能需要显式 heavy 分类；Slice B synthetic report construction 需要 review

**接受建议**: Accept as-is。三个 NON-BLOCKING 观察可作为 controller judgment 的可选增强项，不要求 plan 修改。
