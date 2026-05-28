# NAV Source Adapter Typed Contract — Slice 2 Docs & Real Smoke Review (GLM)

日期：2026-05-28
Reviewer：GLM（code review agent）
Role：review only — 不 implementation、fix、commit、push、PR、merge、release 或 golden promotion
Gate：NAV repository/source adapter typed contract implementation gate — Slice 2
Gate classification：`heavy`

## Review Focus

1. Docs only state current implemented facts, not future design as current fact.
2. Docs distinguish legacy `NavDataResult` from `FundNavRepository.load_nav_series()` typed boundary.
3. Docs preserve `raw_unit_nav` / `requested_code_only` / `not strong eligible` semantics and do not claim adjusted, cumulative, total-return, verified identity, or `drawdown_stress` unblock.
4. Smoke evidence uses `FundNavRepository` boundary and records provenance/identity/adjusted_basis; no direct SQLite/Akshare/cache bypass.
5. Full validation evidence is present: ruff check all passed; full pytest coverage gate passed with 893 tests and 92.40% coverage.
6. Scope: no implementation-control update yet, no extractor/snapshot/score/quality/golden/release/PR changes.
7. If any wording could weaken FQ0–FQ6 or future drawdown contract, flag it.

## Artifacts Reviewed

- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md` — Slice 2 definition
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-evidence-20260528.md` — implementation evidence
- `docs/design.md` — git diff (2 paragraph additions + 1 table cell update)
- `fund_agent/fund/README.md` — git diff (1 paragraph addition + 2 list-item updates)
- `tests/README.md` — git diff (1 list-item split + 2 additions)
- `AGENTS.md` — 规则真源
- `docs/design.md` — 设计真源全文
- `fund_agent/fund/README.md` — Fund 包开发手册全文
- `tests/README.md` — 测试手册全文

## Findings

### F1: Docs state current implemented facts only — PASS

`docs/design.md` diff +641–644 uses "当前" consistently when describing the typed NAV repository contract. Forward-looking consumer rules ("后续路径型 drawdown metric 只能消费…") are phrased as constraints on future consumers, not claims of current capability. The explicit negative statement "该路径没有证明分红调整、累计净值或 total-return basis，也没有解除债券基金 `drawdown_stress` blocker" is a correct and important safeguard.

`fund_agent/fund/README.md` diff +90 uses "是 data 层当前 typed NAV series contract" and "当前 Akshare `单位净值走势` 只会被 typed repository 标记为…"; both anchored to "当前".

`tests/README.md` diff accurately describes test coverage scope and explicitly notes the smoke "不能证明 adjusted / total-return drawdown evidence".

No instance of future design written as current fact found.

### F2: Legacy vs typed boundary clearly distinguished — PASS

`docs/design.md` +641: "旧 `NavDataResult` 仅保留为 `analyze`、`checklist`、snapshot 和既有 P1 façade 兼容结果" clearly marks the legacy surface. The consumer rule "后续路径型 drawdown metric 只能消费 `FundNavRepository.load_nav_series()` 的 typed 边界" cleanly draws the line.

`fund_agent/fund/README.md` +90: "旧 `FundNavDataAdapter.load_nav_data()` 继续作为 legacy/snapshot/analyze 兼容入口" vs "`FundNavRepository.load_nav_series()` 是 data 层当前 typed NAV series contract" — unambiguous dual-entry documentation.

`fund_agent/fund/README.md` internal layering update: "`load_nav_data()` 保留 legacy 兼容，`load_nav_series()` 是后续路径型 NAV 指标的 typed 边界" — consistent.

No ambiguity found between legacy and typed paths.

### F3: Limitation semantics preserved, no overclaiming — PASS

All three doc changes and the evidence artifact consistently state:

- `nav_type="unit_nav"`, `adjusted_basis="raw_unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"` — confirmed in design.md +643, README +90, evidence smoke JSON, and tests/README.
- `strong_drawdown_evidence_eligible=False` — stated in all four locations with explicit reasoning.
- Explicit non-claims in evidence §Docs Decision: adjusted NAV, cumulative NAV, total-return, verified identity, `drawdown_stress` blocker解除 — all listed as intentionally not claimed.
- `fund_agent/fund/README.md` boundary section: "`data/nav_repository.py` 当前只把 Akshare `单位净值走势` 归一化为 raw unit NAV typed series，并显式标记为非 strong drawdown evidence；不提供 adjusted、dividend-adjusted 或 total-return 证据。" — correctly limiting.

No overclaiming detected.

### F4: Smoke uses FundNavRepository boundary, no bypass — PASS

Evidence §Real 006597 Smoke:

- Access boundary explicitly states: "Did not read SQLite directly. Did not call Akshare directly. Did not bypass adapter/repository."
- Smoke JSON fields confirm repository output: `source: "nav_cache"`, `origin_source: "akshare"`, `cached: true`, `cache_updated_at` present — provenance chain preserved.
- The SyntaxError note is transparent and properly resolved; the rerun used the same repository call.
- `share_class: "A"` consistent with plan working assumption for 006597.

No evidence of boundary bypass.

### F5: Full validation evidence present — PASS

Evidence §Validation:

- `ruff check .`: "All checks passed!"
- `pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: 893 passed, 92.40% coverage — exceeds CI gate.
- Both results include output summaries.

Validation is complete and verifiable.

### F6: Scope clean, no out-of-scope changes — PASS

Evidence §Non-Goal Preservation lists 10 items, all confirmed against the diff:

- `docs/implementation-control.md` not edited — confirmed in diff.
- Snapshot schema, score policy, quality gate, FQ0–FQ6, bond risk extractor, renderer, Service/CLI, Host/Agent/Dayu, golden/baseline fixtures — none appear in the diff.
- The diff touches only `docs/design.md`, `fund_agent/fund/README.md`, and `tests/README.md` — exactly the three files listed in Slice 2 "Allowed files" (excluding the evidence artifact itself).

No scope creep detected.

### F7: No weakening of FQ0–FQ6 or future drawdown contract — PASS

Checked all new wording for potential weakening:

- `docs/design.md` +642 consumer rule: "不得直接读取 Akshare、SQLite cache、snapshot JSONL 或旧 raw payload" — strengthens future drawdown contract by closing bypass paths.
- `fund_agent/fund/README.md` +90: "raw unit NAV 不能作为模板第 6 章强 drawdown evidence，也不解除当前 `drawdown_stress` blocker" — explicitly preserves blocker.
- `tests/README.md`: "该 smoke 即使成功也只证明…不能证明 adjusted / total-return drawdown evidence" — limits smoke interpretation.
- Evidence §Residuals: three items all correctly state unresolved status.
- No new wording introduces softening language like "may", "could", "partially", "tentatively" around evidence eligibility.

No weakening found.

## Observations (non-blocking)

- **O1**: `docs/design.md` +641 mentions `FundNavDataAdapter.load_raw_nav_source()` which is an internal adapter method not re-exported from `data/__init__.py`. This is consistent with design.md's existing style of documenting current implementation paths alongside public contracts, and does not create a misleading public API claim. No action required.
- **O2**: The smoke JSON shows `records: 1809` while earlier artifacts referenced `records=1802`. This is expected cache variation between runs and does not affect the review.

## Conclusion

**accepted**

All seven review focus areas pass. The Slice 2 documentation changes accurately state current implemented facts, clearly distinguish legacy from typed boundary, preserve all limitation semantics without overclaiming, the smoke evidence uses the proper repository boundary with full provenance, validation evidence is complete and verifiable, scope is clean, and no wording weakens existing or future contracts. No required fixes.
