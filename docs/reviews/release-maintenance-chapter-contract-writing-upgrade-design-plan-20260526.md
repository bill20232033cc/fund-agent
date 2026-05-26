# Chapter Contract Implementation + Report Writing Quality Upgrade Design Plan

> Date: 2026-05-26
> Role: AgentCodex specialist planning/synthesis
> Scope: design + code-generation-ready plan only
> Verdict: PLAN_READY

## 0. Boundary

This artifact is the only intended output of this turn. It does not implement source, tests, renderer, Service, CLI, product behavior, Host/Agent/dayu runtime, GitHub mutations, commits, or scratch outputs.

Truth read:

- `AGENTS.md`
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
- `docs/design.md` sections 1-3
- Accepted evidence artifacts listed below.

Accepted evidence used:

- `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-dev-tool-20260526.md`
- `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-controller-judgment-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-controller-judgment-20260526.md`
- `docs/reviews/release-maintenance-escalation-readiness-check-20260526.md`

## 1. Gate A: Report-Quality Escalation Synthesis

### 1.1 Evidence Summary

| Evidence stream | Accepted fact | Design implication |
|---|---|---|
| Quasi-real run | One manually assembled `004393` / 2024 active-fund bundle plus linked score issues validates with no validator issues; material localized issue is Chapter 3 `turnover_rate` fact coverage and next owner is `chapter_contract`. | Validator schema is not the blocker for the first active-fund report-quality issue; unsupported style-stability wording must be constrained before opening extraction. |
| Small baseline real evaluation | Clean denominator covers `004393` active, `004194` enhanced index, `006597` bond; per-sample bundle and JSONL validation pass; localized material issues remain. | The first report-writing slice should target active Chapter 3. Enhanced index and bond need fact coverage/extraction evidence before writing can safely conclude. |
| First quality fix | Combined JSONL originally failed with `RQV_REF_MISSING=4`; `validate_report_quality_jsonl()` now assigns standalone score-issue rows to the nearest preceding bundle and rejects orphan/cross-bundle references. | Dev/evaluation tooling can now aggregate multiple clean samples without false cross-bundle reference failures. |
| Dev-only tooling | `scripts/report_quality_eval.py` consumes explicit JSONL/bundle JSON paths and writes caller-selected summary output; not product CLI and not registered in product flow. | Future report-writing iteration should remain dev-only until a reviewed gate proves product-flow integration is required. |
| First Chapter 3 wording fix | Chapter 3 contract now contains active-fund style-stability / style-consistency precondition language, but runtime `ContractRequiredItemRule` was deliberately deferred because current renderer cannot satisfy the marker. | Next design must make CHAPTER_CONTRACT executable without breaking current v0 renderer, then decide if a tiny renderer change is necessary in a later output-changing slice. |

### 1.2 Top 5 Quality Issues

These issues are evidence-backed. `Validator issue` means the report-quality validator emitted an error; `explicit absence` means validator passed and the issue was localized by accepted score-issue / controller evidence instead.

| Rank | sample / fund code | fund_type | chapter | validator issue or explicit absence | failure category | direct artifact path | classification |
|---:|---|---|---|---|---|---|---|
| 1 | `004393` / 2024 | `active_fund` | `chapter_3` | Explicit absence: quasi-real bundle and JSONL validation returned `blocking_count=0`, `failed_closed=false`, `error_code_counts=[]`; accepted score issue `issue:004393:2024:chapter_3:fact_coverage:turnover_rate:material` remains material. | Missing/unreviewed turnover or style-change evidence can lead to unsupported style-stability / style-consistency / 言行一致 claims. | `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md` and `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` | `chapter contract` |
| 2 | `004393` / 2024 | `active_fund` | `chapter_3` | Explicit absence: no validator issue; controller accepted a runtime asymmetry because adding a required output marker would fail current renderer output. | Renderer/report-writing does not yet emit the accepted insufficiency + next-minimum-validation wording marker, so runtime required item remains deferred. | `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-controller-judgment-20260526.md` | `writing template` |
| 3 | `004194` / 2024 | `enhanced_index` | `chapter_2` | Explicit absence: per-sample bundle and JSONL validation passed; accepted score issue localizes `tracking_error` as material. | Benchmark context exists, but reviewed tracking-error / enhanced-deviation readiness is not proven. | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` | `data extraction` |
| 4 | `006597` / 2024 | `bond_fund` | `chapter_6` | Explicit absence: per-sample bundle and JSONL validation passed; accepted score issue localizes `risk.bond_lens` as material. | Bond risk lens lacks reviewed duration, credit, leverage, liquidity, and drawdown facts. | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` | `data extraction` |
| 5 | `004393` + `004194` + `006597` combined JSONL | multi-sample | multi-chapter score-issue rows | Validator issue before fix: combined JSONL failed with `RQV_REF_MISSING=4`; after fix validation reports `total_records=9`, `blocking_count=0`, `failed_closed=false`. | Standalone score-issue rows were validated against the first bundle only, causing false missing anchor/gap references for later bundles. | `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` and `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md` | `validator consumer / evidence-link integrity` |

Gate A conclusion: the next implementation must not start with broad renderer rewrite, extraction expansion, or LLM repair. The same-source evidence says the first actionable writing risk is active-fund Chapter 3 claim safety, while enhanced-index and bond rows are extraction / reviewed-fact readiness problems.

## 2. Gate B: CHAPTER_CONTRACT Executable Constraint Design

### 2.1 Design Objective

Implement CHAPTER_CONTRACT as executable constraints that help a constrained renderer or later LLM writer do the next correct action with low cognitive load:

1. identify the chapter and fund type;
2. determine what must be answered;
3. determine which evidence is required for the answer;
4. allow explicit `N/A` / `data_gap` only for named reasons;
5. block or downgrade unsupported claims instead of filling gaps with plausible prose.

This is not a report rewrite. It is a Fund-layer contract / audit capability. It must not change default `fund-analysis analyze`, `fund-analysis checklist`, current 8-chapter v0 renderer structure, FQ0-FQ6, Service/CLI, Host/Agent/dayu, source helpers, or repository behavior in the first implementation slice.

### 2.2 Proposed Runtime Model

Add a declarative executable constraint sidecar beside the existing template manifest. This sidecar is a wrapper over existing `ChapterContract` records, not a replacement for them.

Binding decision:

- `fund_agent/fund/template/contracts.py` remains the single machine source for `ChapterContract.chapter_id`, `title`, `narrative_mode`, `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`.
- Do not modify the frozen `ChapterContract` dataclass to add `required_evidence`, `allowed_na_reason`, or `failure_behavior`.
- Store `required_evidence`, `allowed_na_reason`, `failure_behavior`, and overlay severity in the new sidecar model. The sidecar must reference chapter ids and stable existing contract strings from `load_template_contract_manifest()`.
- Do not create a parallel contract truth. If the sidecar and existing manifest disagree on chapter ids/titles, the sidecar validation must fail closed in tests.
- The default audit module path is fixed: `fund_agent/fund/report_writing_audit.py`.

New concepts:

- `ChapterExecutableConstraint`: per chapter 0-7 constraint with `must_answer`, `must_not_cover`, `required_evidence`, `allowed_na_reason`, and `failure_behavior`.
- `EvidenceRequirement`: named fact / anchor / gap requirement, with fund-type overlays and accepted `data_gap` semantics.
- `ChapterContractAuditFinding`: deterministic finding emitted by a dev-only audit function; includes chapter, severity, field/claim, source anchor/gap ids, and failure category.
- `audit_chapter_contract(bundle, *, rendered_markdown=None, fund_type=None)`: pure Fund-layer function over `ReportEvidenceBundle`; optional Markdown input enables writing-template checks without calling renderer.

First slice must keep this capability dev-only / library-only. It may be consumed by maintainer scripts later, but it must not be wired into product CLI or quality gate defaults.

Boundary against existing audit/validator paths:

| Function | Input | Responsibility | Non-responsibility |
|---|---|---|---|
| `audit_chapter_contract()` | `ReportEvidenceBundle` plus optional explicit Markdown text | Report-writing semantic constraints: required evidence, allowed `N/A`, data-gap wording, active Chapter 3 claim safety, and final-judgment downgrade hints. | Does not validate JSONL schema, does not run product renderer, does not become FQ0-FQ6, and does not replace programmatic audit. |
| `run_programmatic_audit()` | `ProgrammaticAuditInput` / rendered report structure | Renderer-level contract markers, required sections/items, forbidden literal markers, selected/derived final judgment consistency in current programmatic audit. | Does not decide evidence sufficiency from `ReportEvidenceBundle`; does not own `required_evidence` or `allowed_na_reason`. |
| `validate_report_quality_bundle()` / `validate_report_quality_jsonl()` | `ReportEvidenceBundle` or serialized JSONL | Bundle/JSONL schema and content integrity: ids, backlinks, anchors, gaps, score issue references, source failure semantics. | Does not judge report prose quality, semantic claim safety, or whether a conclusion is adequately worded. |

### 2.3 Chapter Constraints 0-7

The exact strings in `fund_agent/fund/template/contracts.py` remain the human-facing `must_answer` source. The executable layer should use stable ids plus these semantic obligations.

| Chapter | must_answer | must_not_cover | required_evidence | allowed_na_reason | failure_behavior |
|---|---|---|---|---|---|
| 0 投资要点概览 | Product identity; current action among `worth_holding` / `needs_attention` / `suggest_replace`; status; one main reason; one main risk; one next minimum validation question; upgrade/downgrade/stop thresholds. | No buy/sell wording; no evidence appendix section; no unordered advantage list; no multi-risk laundry list. | `classified_fund_type`, fund profile, `FinalJudgmentDecision`, quality-gate status, at least one downstream evidence-backed reason or data gap, main risk source. | Downstream chapter evidence can be summarized as `data_gap` only if the gap id is explicit and action is not upgraded because of the gap. | Blocking if direct trading advice appears or final action is missing; material if reason/risk/next question lacks evidence or gap refs. |
| 1 产品本质 | Fund type, investment objective, strategy, benchmark, classification labels, and what to inspect first for this fund type. | No manager skill attribution, return attribution, market competition, or peer ranking. | fund profile, investment objective/strategy, benchmark identity, fund-type classification, preferred-lens focus label. | Benchmark or special-situation fields may be `N/A` only with `not_disclosed`, `not_applicable_to_fund_type`, or `data_gap` reason. | Blocking if fund type is unknown or contradicted; material if benchmark/strategy claims lack anchors. |
| 2 R=A+B-C | 1/3/5-year returns, benchmark returns, excess return, structural vs phase excess, cost breakdown, and whether excess covers cost. | No future return prediction; no manager stock-picking deep dive; no market timing narrative. | performance facts, benchmark returns, fee facts, transaction-cost proxy or explicit gap, R=A+B-C calculation facts, alpha nature judgment. | Short history may explain missing 3/5-year windows; benchmark unavailable must be an explicit data gap; cost component unavailable must not be silently omitted. | Blocking for future return prediction or trading advice; material if excess/cost/stability conclusion lacks required facts. |
| 3 基金经理画像与言行一致性 | Manager profile; stated strategy; actual behavior; consistency; style stability; manager holding / interest alignment. | No personality/motive judgment; no unsupported active-fund style stability, style consistency, or 言行一致 claim when turnover/style-change evidence is missing, unavailable, or unreviewed. | manager profile, annual report §4 stated strategy, annual report §8 holdings/industry/concentration/turnover or accepted style-change proxy, manager holding disclosure or explicit `not_disclosed`. | `not_disclosed_manager_holding`; `turnover_or_style_change_not_reviewed`; `source_unavailable`; all must preserve insufficiency wording and next minimum validation question. | Blocking for motive/personality claims; material for unsupported stability/consistency; material if manager holding is omitted without allowed N/A reason. |
| 4 投资者获得感 | Product return, investor actual return or proxy, behavior gap, share-flow trend. | No individual investor behavior diagnosis; no future investor behavior prediction. | product returns, investor-return disclosure if available, share change facts, NAV/share-flow proxy calculation or explicit gap. | Pre-2026 disclosure absence, report not disclosing investor return, or insufficient share-flow data; must render explicit insufficiency. | Material if behavior-gap conclusion lacks investor-return/proxy evidence; blocking if future behavior is predicted. |
| 5 当前阶段与关键变化 | Current stage; 1-3 key changes; whether changes alter Chapters 1-4; why now; next minimum validation question. | No market forecast; no exhaustive change list; no final hold/replace conclusion; no risk list unless translated to Chapter 6 risk. | cross-period manager/scale/strategy/fee/position/share-flow facts, prior-period comparison anchors, stage classification rationale. | No prior period or prior period not reviewed; must say no cross-period conclusion is available. | Material if change/stage claim lacks cross-period evidence; blocking if market forecast drives conclusion. |
| 6 核心风险与否决项 | Structural vs phase risks; 1-2 decisive risks; which core assumption the risk overturns; veto vs monitor; stress-test conclusion; next evidence gap. | No risk laundry list; no probability forecast; no final hold/replace conclusion; no return/market prediction. | risk-check facts, liquidation/scale facts, fee risk facts, stress-test result, fund-type risk facts from preferred lens. | A risk dimension may be `N/A` only if not applicable to fund type or not reviewed with explicit `data_gap`; stress-test missing inputs must not become a pass. | Blocking if risk chapter missing or direct trading advice appears; material if veto/stress conclusion lacks evidence; downgrade final confidence on unresolved material risk gap. |
| 7 最终判断 | Final judgment; why; key evidence chain; what would change the judgment; next minimum validation question. | No buy/sell instruction, no position sizing, no future return/market prediction, no contradiction of derived judgment without explicit developer override. | `FinalJudgmentDecision`, checklist lights, risk/stress findings, quality-gate status, material data gaps, Chapter 0/6 key reason/risk consistency. | No `N/A` for final judgment. Data gaps are allowed only as reasons for `needs_attention`, not for upgrading to `worth_holding`. | Blocking for buy/sell/position advice or missing final judgment; blocking for selected/derived contradiction without override; material if data gaps do not downgrade confidence. |

Deferred extraction-dependent handling:

- Chapter 2 enhanced-index tracking-error / enhanced-deviation requirements are configuration-side requirements in the first slice. Until a reviewed extraction/fact-coverage gate exists, they may emit only informational/config findings, not material end-to-end audit failures.
- Chapter 6 bond duration, credit, leverage, liquidity, and drawdown requirements are configuration-side requirements in the first slice. Until the corresponding extraction/fact-coverage gate exists, they may emit only informational/config findings, not material end-to-end audit failures.
- Active-fund Chapter 3 turnover/style-change claim safety is the only first-slice material semantic audit behavior, because that issue is already localized to `chapter_contract` by accepted evidence.

### 2.4 preferred_lens / fund_type Overlay

Executable constraints must first resolve `classified_fund_type`, then apply the base chapter constraint plus fund-type overlays.

| fund_type | Overlay |
|---|---|
| `index_fund` | Chapters 1/2/6 require benchmark/index identity, tracking error, fee, scale/liquidity, and index-specific veto thresholds; manager-dependence claims in Chapter 3 are low priority unless tied to tracking/fee/clearance risk. |
| `enhanced_index` | Chapters 2/3/5 require both excess-return source/stability and tracking-error / deviation evidence; benchmark context alone cannot satisfy enhanced-return quality. |
| `active_fund` | Chapters 2/3/4/5 require alpha stability, manager process, consistency, style stability, and investor behavior sensitivity; Chapter 3 cannot claim stability/consistency without reviewed turnover or style-change evidence. |
| `bond_fund` | Chapters 1/5/6 require duration, credit, leverage, liquidity, drawdown, and scale/stress facts before risk conclusions. |
| `qdii_fund` | Chapters 1/5/6 require overseas market exposure, currency risk, cross-border policy/fee context, and must not treat domestic benchmark valuation as sufficient. |
| `fof_fund` | Chapters 1/2/6 require sub-fund allocation, manager selection logic, double-fee / total-cost evidence, and fund-of-funds risk concentration facts. |

Overlay severity rule:

- `core` means a sidecar `EvidenceRequirement` whose absence can change the chapter conclusion for that fund type. It is not inferred from prose alone; it must be encoded explicitly on the sidecar requirement, normally mirroring `TemplateLensRule.priority="core"` when that requirement is directly tied to the preferred lens.
- If the fund-type overlay marks a requirement as `core`, missing evidence is material unless an allowed `data_gap` wording is present.
- If the missing evidence is used to support a positive final judgment or stability claim, escalate to blocking in dev-only audit output.

### 2.5 First Implementation Slice vs Future Design

First implementation slice:

- Add executable constraints and dev-only audit over `ReportEvidenceBundle` / optional explicit Markdown input.
- Implement the Chapter 3 active-fund turnover/style-change constraint fully.
- Add base skeleton constraints for Chapters 0-7 so every chapter has `required_evidence`, `allowed_na_reason`, and `failure_behavior`.
- Integrate Chapter 3 active-fund data-gap checks with existing `ReportDataGapOverride.required_report_wording`; the audit should verify that the accepted insufficiency wording and next-minimum-validation question are preserved when the gap is represented.
- Keep deferred extraction-dependent Chapter 2 and Chapter 6 requirements informational/config-only, as described in §2.3.
- Emit findings only; do not wire findings into product `quality_gate_policy`, renderer, Service, CLI, or FQ0-FQ6.
- Preserve current 8 chapter ids, titles, manifest loading, and renderer default output.

Future design:

- Promote selected constraints into runtime `ContractRequiredItemRule` only after renderer/report-writing output can satisfy them.
- Add per-chapter evidence checklist rendering.
- Add deterministic repair hints, then only later consider LLM audit / repair loop.
- Open separate extraction gates for enhanced-index tracking error, bond risk lens, QDII source recovery, and FOF taxonomy.

### 2.6 docs/design.md Update Decision

This planning artifact does not update `docs/design.md`.

Owner: the next implementation agent that adds the executable sidecar/audit code.

The next implementation gate should update `docs/design.md` after code and tests pass if it introduces executable constraint dataclasses/functions. The update scope is narrow: revise §3.2 to state that CHAPTER_CONTRACT now has a dev-only sidecar/wrapper audit layer over existing `ChapterContract`, with `required_evidence`, `allowed_na_reason`, and `failure_behavior`. It must not claim renderer, FQ0-FQ6, product CLI, `run_programmatic_audit()`, validator, LLM audit, or repair loop integration unless that code exists. Acceptance criterion: the design text describes only current code facts from the implementation diff and keeps future renderer/product-flow integration explicitly future-scoped or absent.

## 3. Gate C: Report Writing Quality Upgrade Plan

### 3.1 Selected Minimal Slice

Selected slice: executable Chapter 3 active-fund claim-safety audit plus chapter evidence checklist semantics.

This is the smallest implementable slice because it targets the accepted material issue without changing production output:

- Evidence checklist: Chapter 3 active requires reviewed turnover or style-change evidence for stability/consistency claims.
- Insufficient evidence: missing/unreviewed turnover/style-change must produce explicit insufficiency wording and a next minimum validation question.
- Final judgment derive contract: unresolved material Chapter 3 style-consistency gap cannot support upgrading to `worth_holding`.
- Forbidden unsupported style claim: active-fund stability/consistency/言行一致 cannot be inferred from absence of evidence.
- Dev-only chapter audit report: expose chapter-level findings for maintainers.

Renderer change decision:

- First slice: no renderer change.
- Renderer change is not yet the minimum necessary change because the first need is executable evidence that identifies exactly which wording is unsafe.
- A later output-changing slice may allow a minimal renderer change limited to active-fund Chapter 3 data-gap wording if the dev-only audit proves current rendered Markdown lacks the accepted insufficiency phrase. That later slice must not alter chapter count, final judgment enum, Service/CLI defaults, FQ0-FQ6 semantics, or Host/Agent/dayu.

### 3.2 Implementation Scope

Allowed files for the next implementation gate:

| File | Purpose |
|---|---|
| `fund_agent/fund/template/chapter_contract_constraints.py` | New declarative executable constraints and dataclasses. |
| `fund_agent/fund/report_writing_audit.py` | Default and only planned audit module path. Pure Fund-layer dev-only audit over `ReportEvidenceBundle` and optional explicit rendered Markdown. Keep public API small. |
| `tests/fund/template/test_chapter_contract_constraints.py` | Contract schema and Chapter 0-7 completeness tests. |
| `tests/fund/test_report_writing_audit.py` | Audit behavior tests for active Chapter 3, N/A/data_gap, unsupported claims, and final-judgment downgrade hints. |
| `tests/fund/test_report_evidence.py` | Only if current data-gap wording serialization needs a focused assertion extension. |
| `scripts/report_quality_eval.py` | Existing maintainer-only script. Optional and deferrable: add a flag to include chapter-audit summary for explicit input files only if capacity remains. Deferring this flag must not block the gate. Do not register product CLI. |
| `tests/scripts/test_report_quality_eval.py` | Optional and deferrable, only if the existing dev-only script flag is added. |
| `fund_agent/fund/README.md` | Minimal current-fact sync for Fund-layer contract/audit behavior. |
| `docs/design.md` | Narrow implementation-agent-owned sync after implementation passes, as described in §2.6. |
| `docs/reviews/<implementation-artifact>.md` | Implementation evidence artifact. |

Prohibited files for the first implementation slice:

- `fund_agent/fund/template/renderer.py`
- `fund_agent/services/`
- `fund_agent/ui/`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/documents/`
- `FundDocumentRepository` and any PDF/cache/source helper/downloader/adapter
- `fund_agent/host/`
- `fund_agent/agent/`
- `pyproject.toml` product entry points
- tracked report outputs, curated fixtures, durable baseline files, scratch JSON/JSONL promotion
- any GitHub mutation, `git add`, commit, push, ready-for-review, or merge action unless explicitly authorized in a later turn

### 3.3 Acceptance Tests / Commands

Focused tests:

```text
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Adjacent tests:

```text
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

If `scripts/report_quality_eval.py` is touched:

```text
uv run pytest tests/scripts/test_report_quality_eval.py
```

Lint:

```text
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Whitespace and boundary:

```text
git diff --check
git diff --name-only
git diff -- fund_agent/fund/template/renderer.py fund_agent/services fund_agent/ui fund_agent/fund/quality_gate.py fund_agent/fund/extraction_score.py fund_agent/fund/documents fund_agent/host fund_agent/agent pyproject.toml
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|FQ0|FQ6" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Expected boundary result:

- No diff in renderer, Service, UI, quality gate, extraction score, documents/source helpers, Host/Agent, or product entry points.
- No scratch output tracked.
- No product behavior change.

### 3.4 Required Test Coverage

The next implementation must cover:

- Chapter completeness: all chapter ids 0-7 have executable constraints.
- Evidence anchors: required evidence references are represented by source anchor ids or explicit data-gap refs.
- 禁用投资建议: buy/sell/position sizing is blocking in Chapters 0 and 7, and any chapter-level audit should propagate this as report-level blocking.
- `N/A`: accepted only with configured `allowed_na_reason`, never counted as passing evidence.
- `data_gap`: must link to a concrete gap id and preserve insufficiency wording for Chapter 3 active-fund turnover/style-change.
- Final judgment: unresolved material style-consistency gap cannot support `worth_holding`; contradiction with derived judgment remains blocking unless explicit developer override exists.
- `ReportDataGapOverride.required_report_wording`: active Chapter 3 gap audit must consume or reference this wording path and verify the insufficiency sentence plus next minimum validation question is preserved.
- Preferred lens: active overlay tests must enforce the Chapter 3 material claim-safety behavior. Enhanced-index and bond overlay tests are configuration tests only in this slice; they should assert the sidecar marks the right requirements and deferred informational/config severity, not reproduce end-to-end extraction failures.
- Single-file coverage target: newly added modules `fund_agent/fund/template/chapter_contract_constraints.py` and `fund_agent/fund/report_writing_audit.py` should each target ≥80% test coverage. If local tooling cannot report per-file coverage in the focused command, the implementation artifact must state the measured alternative and residual risk.

### 3.5 Stop Conditions

Stop and return to controller/review if any of these occur:

- The implementation needs to modify renderer, FQ0-FQ6, Service/CLI, source helpers, `FundDocumentRepository`, Host/Agent/dayu, or product entry points to make tests pass.
- A proposed constraint would make current default v0 renderer output fail product audit.
- The design requires new annual-report fetch/parse, extraction work, or scratch fixture promotion.
- `docs/design.md` would need to describe future behavior as current code fact.
- Active Chapter 3 cannot be audited using current `ReportEvidenceBundle` / score issue / data gap structures without adding a parallel extraction path.
- The implementation cannot preserve the current 8 chapter ids/titles and final judgment enum.

### 3.6 Residual Risks

| Risk | Handling |
|---|---|
| The first slice does not improve product Markdown directly. | Accepted intentionally. It creates executable evidence for the smallest later renderer change, if needed. |
| Template draft and machine constraints can drift. | Tests must compare chapter ids and key strings / stable ids; docs/design sync happens after code. |
| Current `ReportEvidenceBundle` may not contain all facts for Chapters 0-7. | First slice allows explicit data gaps and only fully enforces active Chapter 3; future extraction gates own missing facts. |
| Validator and audit may duplicate concepts. | Keep validator focused on schema/content integrity; keep chapter audit focused on report-writing contract semantics. |
| Enhanced-index and bond material issues remain unresolved. | Treat as data extraction / reviewed-fact residuals; do not hide them with writing templates. |
| Fallback-blocked index/QDII and FOF coverage remain unresolved. | Source recovery and fund-type taxonomy gates remain separate. |

## 4. Final Decision

PLAN_READY.

Evidence is sufficient to plan a narrow first implementation slice: Fund-layer executable CHAPTER_CONTRACT constraints plus dev-only report-writing audit, centered on active-fund Chapter 3 claim safety and generalized enough to cover Chapters 0-7 structurally. The plan deliberately avoids renderer/product-flow changes until a reviewed audit result proves the exact minimal output change needed.
