# MVP Small Golden Set Row-field Extractor Gap Decision Gate Review — MiMo

## Gate

- Gate: `row-field extractor gap decision gate for retained manager / holdings / risk fields`
- Role: plan review (independent)
- Reviewer: AgentMiMo
- Date: 2026-06-09
- Review target: `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`

## Review Scope

- `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`
- Supporting evidence: extractor source code (`profile.py`, `holdings_share_change.py`, `manager_ownership.py`), oracle JSON (`mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`)

## Findings

### F1 — BLOCKING: `risk` → `style_positioning` passing test claim is incorrect

**Severity: blocking**
**Location:** `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`, Field Decisions table, `risk` row

The plan claims:

> `extract_profile(report).product_profile.value["style_positioning"]` consumes `风险收益特征` / `风格定位` / `产品定位` via `profile.py`

This is factually incorrect. `style_positioning` and the oracle's `risk.expected` extract fundamentally different information from different conceptual layers of the annual report:

1. **Semantic mismatch.** `style_positioning` captures investment style positioning (e.g., "价值成长均衡", "被动指数型产品，跟踪沪深300指数"). The oracle's `risk.expected` captures risk characteristics — multi-clause, semicolon-delimited summaries synthesizing fund-type classification, relative risk ranking, and special risk factors (e.g., `混合型基金；高于债券型和货币市场基金，低于股票型基金；含港股通特有风险`). These are different conceptual axes.

2. **Text shape differs.** `style_positioning` extracts only the text after a single `：` delimiter on one line (line 837 of `profile.py`). The oracle values are multi-sentence synthesized paragraphs. Even when `style_positioning` hits on the `风险收益特征` label, that label typically contains a short phrase, not the full risk characterization.

3. **Derivation fallback produces unrelated text.** When no explicit label is found, `_derive_style_positioning()` (line 861 of `profile.py`) extracts from `投资目标` using verb patterns like `力争实现...`, yielding goal-oriented text that has no structural relationship to risk characterization.

4. **Concrete failures:**
   - `004393`: oracle expects "含港股通特有风险" — `style_positioning` has no mechanism to capture special risk factors
   - `006597`: oracle expects "操作中强调信用风险和流动性风险控制" — this clause likely comes from management discussion, not §2 labeled fields
   - `017641`: oracle expects "含汇率风险等特别投资风险" — QDII regulatory disclosure, not a style label

**Impact:** The next gate's "allowed" list says "Remove `risk` from strict xfail only if adding passing `extract_profile(...).product_profile.value['style_positioning']` assertions for all five rows." If this proceeds, the test will fail on exact value matching because the extractor output does not match the oracle expected values.

**Required fix:** Move `risk` from "Convert to passing row-field assertion" to "Defer to row-shape contract decision." The next gate should not remove `risk` from xfail. A dedicated risk characteristic extractor or a broader `product_description` text extraction surface is needed before `risk` can become a passing assertion.

### F2 — ADVISORY: Equity-like holdings test extension requires header normalization decision

**Severity: advisory**
**Location:** `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`, Field Decisions table, `holdings` row

The plan correctly identifies that equity-like rows (004393, 004194, 017641) can enter a test-only extension gate using `holdings_snapshot.top_holdings`. However, the plan does not address a key implementation detail:

The current holdings extractor (`holdings_share_change.py`, `_extract_top_holdings` at line 541) passes raw PDF table headers through to the output dict via `_row_to_dict`. The output keys will be whatever the PDF table headers happen to be (e.g., "股票代码", "股票名称", "公允价值（元）", "占基金资产净值比例（%）"). The oracle uses canonical keys (`code`, `name`, `fair_value_cny`, `net_asset_ratio`).

This means the next gate's test will need to either:
- Assert on the raw PDF header keys (matching what the extractor actually produces), or
- Normalize the output keys before comparison

The plan should specify which approach the next gate should take, or at minimum acknowledge this as a design decision for the next gate.

### F3 — ADVISORY: `manager` deferral rationale is correct but could be more specific

**Severity: advisory**
**Location:** `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`, Field Decisions table, `manager` row

The deferral decision is correct. Verified that:
- Oracle `manager.expected` is a structured list of `{name, role, start_date, end_date}` objects sourced from §4.1.2 基金经理简介
- `profile.py`'s `fund_manager` is a flat string from §1/§2 — semantically different (may contain management company name, not portfolio manager list)
- `manager_ownership.py` covers strategy/turnover/manager-holding/holder-structure — none contain manager identity or tenure

The plan could strengthen the rationale by noting that the oracle anchors point to §4.1.2 (基金经理简介), while neither existing extractor reads that subsection. This makes the contract gap not just a shape mismatch but a source-section mismatch.

## Verification of Non-blocking Criteria

### 4. Out-of-bounds authorization check

**PASS.** The plan's "Forbidden" list (lines 55-57) correctly prohibits:
- Extractor modification
- PDF read, FundDocumentRepository live acquisition, network, fallback, live LLM, endpoint/provider probe
- Provider/default/runtime/budget/config changes
- Fixture projection, full golden/readiness promotion, release, merge or mark-ready

No authorization beyond docs-only decision is present.

### 5. Next gate code-generation-ready check

**CONDITIONAL PASS — blocked by F1.** The plan's "Allowed" list (lines 42-49) is well-structured with clear allowed fields, forbidden fields, and stop conditions. However, the `risk` route is incorrect (F1), so the next gate is not code-generation-ready as written. After fixing F1 (moving `risk` to row-shape contract decision), the next gate becomes code-generation-ready for the `holdings` equity-like subset only.

## Residual Risks

1. **`risk` requires a separate row-shape contract decision gate.** The plan's current routing of `risk` to "passing test extension" is wrong. After this review, `risk` should join `manager` in the deferred residuals table, requiring a row-shape contract decision before tests.

2. **Equity-like holdings header normalization is unresolved.** The next gate will need to decide whether to assert on raw PDF headers or normalize to canonical keys. This is a test design decision, not a blocking gate issue.

3. **Production PDF fidelity remains unproven.** Both the decision gate and the next test extension gate operate on oracle-derived minimal parsed reports, not real PDF output. This is by-design scope exclusion.

## Verdict

**One blocking finding (F1).**

The `risk` → `style_positioning` claim is factually incorrect. `style_positioning` extracts investment style positioning labels; the oracle's `risk.expected` contains synthesized risk characteristics from a different conceptual layer. The plan must move `risk` from "convert to passing assertion" to "defer to row-shape contract decision" before the next gate can be authorized.

All other decisions (`holdings` split, `manager` deferral, boundary constraints, stop conditions) are sound.

## Targeted Re-review

- Date: 2026-06-09
- Trigger: controller targeted re-review after F1 fix

**F1 fixed.** The target decision artifact (`docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`) has been updated to move `risk` from "Convert to passing row-field assertion" to "Defer to row-shape contract decision." The next gate is now scoped to the equity-like holdings subset only (`004393`, `004194`, `017641`), with `risk` joining `manager` in the deferred residuals table. The next gate's "allowed" and "forbidden" lists no longer reference `risk` test extension.

**Remaining advisories:**
- Holdings header normalization (F2): still requires the next gate to decide whether to assert on raw PDF headers or normalize to canonical keys. Not blocking.
- Manager deferral (F3): remains sound. No change needed.

**No other changes.** Boundary constraints, stop conditions, and `manager`/`holdings` bond/ETF deferral remain unchanged and correct.

**No new out-of-bounds authorization found.** The updated artifact still prohibits extractor modification, PDF/FDR/network/fallback/live/provider, config changes, fixture projection and golden/readiness promotion.

## Final Verdict (after targeted re-review)

**PASS / no blocking findings.**

F1 is fixed. The decision gate now correctly routes `risk` to row-shape contract decision, scopes the next gate to equity-like holdings subset only, and defers `manager` and bond/ETF holdings to separate contract decision gates. The next gate is code-generation-ready for the holdings equity-like subset.

## Self-check

- Current role is plan review (independent), not controller or implementation worker.
- Review scope is limited to the decision gate artifact and its supporting extractor code.
- No files were modified, staged, committed, pushed or used for PR.
- All five review criteria were checked against live extractor source code and oracle JSON.
- `style_positioning` extraction logic, holdings extractor keyword sets, and manager extractor surfaces were independently verified through Explore agents.
- Stop condition is satisfied: one blocking finding identified; review artifact written.
