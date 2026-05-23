# P16-S1 Enhanced-index Production Golden Candidate Evidence — Code Review (AgentGLM, 2026-05-22)

## Verdict

`PASS_WITH_FINDINGS`

Evidence acquisition artifact 正确遵守 plan、controller judgment 和 AGENTS.md 边界。5 个候选按固定顺序通过 `FundDocumentRepository` / `FundDataExtractor` 完成评估，fund type 全部确认为 `enhanced_index`，`index_profile` 正确限定为 benchmark-context 证据，`tracking_error` 全部正确阻断为 `blocked_no_direct_tracking_error`。未修改 source、tests、golden、README、design、control、CSV、RR-13 或任何外部状态。

4 个 findings 均为 info/low 级别，不影响证据正确性，不要求 artifact 修订。

## Review Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | Evidence acquisition artifact under review |
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | Accepted plan (truth for scope and contracts) |
| `docs/reviews/p16-s1-plan-review-controller-judgment-20260522.md` | Controller judgment with 10 implementation constraints |
| `AGENTS.md` | Agent execution rules, module boundaries, evidence requirements |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `docs/code_20260519.csv` rows 38-42 | Selected candidate identity |

Excluded inputs not read or cited: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Controller Constraint Compliance

| # | Constraint | Compliance | Evidence |
|---:|---|---|---|
| 1 | Create only the evidence artifact | ✅ | `git status --short` shows only pre-existing excluded files + the implementation artifact + sibling review artifacts; no tracked diffs |
| 2 | Evaluate exactly `004194`, `005313`, `017644`, `019918`, `019923` in order | ✅ | Artifact sections 1-5 match; CSV rows 38-42 verified |
| 3 | Use only `FundDocumentRepository.load_annual_report()` / `FundDataExtractor.extract()` | ✅ | Artifact Input Boundary section confirms; injected empty `nav_provider` to prevent NAV side effects (see F1) |
| 4 | Record CSV row, report year, report kind, document identity, source metadata, fallback status, `classified_fund_type` before field conclusions | ✅ | Every candidate record includes all required fields; `document_identity_status=matched` for all 5 |
| 5 | Source blockers use five-category taxonomy | ✅ | No blockers triggered; all 5 records correctly note `source blocker: absent` |
| 6 | Evaluate `index_profile` and `tracking_error` separately | ✅ | Each candidate has independent `index_profile classification` and `tracking_error classification` rows |
| 7 | Accept `tracking_error` only for direct observed disclosure | ✅ | Tracking Error Acceptance Check table confirms all 8 required fields absent for every candidate |
| 8 | Fail closed for target/limit, narrative, benchmark-only, ambiguous, etc. | ✅ | All 5 candidates blocked; rejected mentions categorized as target/limit text or strategy narrative |
| 9 | `001548` tracking_error remains blocked; `161725` fixture-only | ✅ | Artifact does not reference `001548` or `161725` as evidence sources |
| 10 | No golden/source/test/README/design/control/CSV/RR-13 edits | ✅ | `git diff --name-only HEAD` returns no output; `git diff --check HEAD` passes |

## Candidate-by-Candidate Verification

### 1. `004194` 招商中证1000指数增强A

- CSV row 38: `招商中证1000指数增强A,004194,国内股票类,` ✅ matches artifact
- `source=eid`, `fallback_used=False` ✅
- `classified_fund_type=enhanced_index`, `extraction_mode=direct`, anchored to `§2 page=5` ✅
- `benchmark_text=中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` ✅ composite benchmark correctly reported
- `benchmark_index_name=null` ✅ not rewritten from product name
- `tracking_error`: extractor `note=tracking_error_ambiguous`, rejected mentions are `§2` target/limit `不超过0.5%…不超过7.75%` and strategy narrative ✅ correctly blocked

### 2. `005313` 万家中证1000指数增强A

- CSV row 39: `万家中证1000指数增强A,005313,国内股票类,` ✅ matches artifact
- `source=eid`, `fallback_used=False` ✅
- `classified_fund_type=enhanced_index`, anchored to `§2 page=5` ✅
- `benchmark_text=中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` ✅ composite benchmark
- `tracking_error`: extractor `note=年报未直接披露跟踪误差`, rejected mentions are target/limit `不超过0.5%、年跟踪误差不超过7.75%` ✅ correctly blocked

### 3. `017644` 博道中证1000指数增强A

- CSV row 40: `博道中证1000指数增强A,017644,国内股票类,` ✅ matches artifact
- `source=eid`, `fallback_used=False` ✅
- `classified_fund_type=enhanced_index`, anchored to `§2 page=5` ✅
- `benchmark_text=中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` ✅ composite benchmark
- `tracking_error`: extractor `note=年报未直接披露跟踪误差`, rejected mentions are strategy narrative without observed value ✅ correctly blocked

### 4. `019918` 招商中证2000指数增强A

- CSV row 41: `招商中证2000指数增强A,019918,国内股票类,` ✅ matches artifact
- `source=eid`, `fallback_used=False` ✅
- `classified_fund_type=enhanced_index`, anchored to `§2 page=5` ✅
- `benchmark_text=中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` ✅ composite benchmark
- `tracking_error`: extractor `note=tracking_error_ambiguous`, rejected mentions are target/limit `不超过0.5%…不超过7.75%` and strategy narrative ✅ correctly blocked

### 5. `019923` 华泰柏瑞中证2000指数增强A

- CSV row 42: `华泰柏瑞中证2000指数增强A,019923,国内股票类,` ✅ matches artifact
- `source=eid`, `fallback_used=False` ✅
- `classified_fund_type=enhanced_index`, anchored to `§2 page=5` ✅
- `benchmark_text=中证2000指数收益率×95%＋人民币活期存款税后利率×5%` ✅ composite benchmark
- `tracking_error`: extractor `note=年报未直接披露跟踪误差`, rejected mentions include target/limit `不超过0.5%…不超过8%` and strategy narrative ✅ correctly blocked

## Cross-cutting Checks

### FundDocumentRepository / FundDataExtractor Boundary

All 5 candidates accessed through the official repository and extractor paths. No direct filesystem reads, no manual PDF/cache/source helper access, no Service/UI/Engine/renderer/quality gate source orchestration, no external web search or index data. The injected empty `nav_provider` stays within the extractor's dependency injection surface (see F1).

### CSV Line Grounding

CSV lines 38-42 verified against `docs/code_20260519.csv`. Each artifact record cites the exact row with fund code, name, and category text. No discrepancy.

### Source Metadata and Fallback Statuses

All 5 records include: `source=eid`, `report_name`, `report_year=2024`, `report_code=FB010010`, `report_desp=年度报告`, `source_url` (EID instance ID), `fallback_used=False`. Source blockers correctly absent.

### Fund Type Classification

All 5 candidates confirmed `enhanced_index` via `basic_identity.extraction_mode=direct` with anchors to annual-report `§2` fund_name rows. This satisfies the plan requirement that fund type must come from structured extraction / annual-report identity, not CSV name alone.

### index_profile Acceptance Scope

All 5 accepted strictly for `benchmark_context` only:
- `benchmark_text`: composite benchmark formula from `§2` ✅
- `benchmark_component_text`: parsed components with percentages ✅
- `benchmark_identity_status=composite` ✅
- `benchmark_index_name=null` ✅ not fabricated from product name
- `source_tier=benchmark_context` ✅
- Anchors: all `source_kind=annual_report`, `document_year=2024`, `section_id=§2`, with page/table/row locators ✅

Plan explicitly excluded methodology, constituents, weights, provider details, rebalance frequency, index code, external adapter output. Artifact correctly stays within benchmark-context scope.

### tracking_error Direct-disclosure Blocker Correctness

All 5 candidates blocked. Each Tracking Error Acceptance Check row confirms all 8 required fields are absent:
- `observed_value`: absent ✅
- `period_label`: absent ✅
- `annualization_support`: absent ✅
- `source_type`: absent ✅
- `calculation_method`: absent ✅
- parseable value: no ✅
- complete anchor: no ✅

Rejected mentions are correctly categorized as target/limit text (e.g., `不超过7.75%`, `不超过8%`) or strategy narrative (e.g., `控制跟踪误差的基础上`). These are not direct observed disclosures and are properly blocked.

### defer_extractor_false_negative

Artifact explicitly states: "not used. No repository-loaded annual report showed anchored, direct-looking observed tracking-error evidence that the extractor missed." This is consistent with the extraction results — all `tracking_error` values are `null` with either `tracking_error_ambiguous` or `年报未直接披露跟踪误差` notes.

### No Golden / Source / Test Changes

`git diff --name-only HEAD` returns no output. `git diff --check HEAD` passes. Only untracked files are the pre-existing excluded files and the new artifact. No production code, tests, golden files, README, design, control, CSV, or RR-13 were modified.

### Validation Adequacy

The `git diff --check HEAD` command validates tracked-file whitespace and conflict markers. The new artifact is untracked, so its content is not checked by this command. For a markdown evidence artifact, whitespace/diff validation of its content is not critical — the artifact is a review document, not executable code. The artifact structure is internally consistent, well-formatted, and does not contain conflict markers or corrupted encoding.

## Findings

### F1 — INFO: Empty `nav_provider` injection

**Severity**: INFO

**Evidence**: Artifact states: "为避免 `FundDataExtractor.extract()` 拉取净值外部数据，本次注入只读空 `nav_provider`。年报访问和字段抽取仍只经过 `FundDocumentRepository` 与 `FundDataExtractor`。"

**Impact**: The injection modifies the extractor's runtime environment by suppressing NAV data fetching. This is pragmatically correct for this gate because: (a) `index_profile` and `tracking_error` extraction does not depend on NAV data; (b) the official API surface (`FundDataExtractor.extract()`) was still used; (c) the alternative would be unnecessary external data fetching with no evidence benefit. The injection is transparent and documented.

**Required disposition**: None. The approach is acceptable for this evidence-only gate. Future golden implementation gate should note this and confirm whether the same injection is needed or whether the full extraction path should run.

### F2 — INFO: Extractor `tracking_error` note inconsistency across candidates

**Severity**: INFO

**Evidence**: Candidates `004194` and `019918` return `note=tracking_error_ambiguous`, while candidates `005313`, `017644`, and `019923` return `note=年报未直接披露跟踪误差`. Both notes correctly result in `extraction_mode=missing` and `value=null`.

**Impact**: The differing notes suggest the extractor may have different code paths or heuristics for classifying the absence of tracking-error data. This does not affect the evidence artifact's correctness — all 5 candidates are correctly blocked regardless of which note appears. However, it signals potential extractor inconsistency that could become relevant if future extractor refinement is attempted.

**Required disposition**: None for this gate. Note as a minor observation for any future extractor-improvement phase.

### F3 — LOW: `benchmark_index_name=null` requires explicit golden-gate decision

**Severity**: LOW

**Evidence**: All 5 candidates have `benchmark_index_name=null` because current extractor identifies these benchmarks as `benchmark_identity_status=composite`. The plan's `index_profile.index_name` subfield cannot be populated from current extractor semantics for composite benchmarks.

**Impact**: The artifact correctly records this as a residual: "later golden review must decide whether to golden the actual full `IndexProfileValue` shape." If a future golden gate accepts `index_profile` candidates, it must either: (a) accept the full composite `IndexProfileValue` with `benchmark_index_name=null`, or (b) defer until an extractor improvement can decompose composite benchmarks into a primary index name.

**Required disposition**: Future golden gate must explicitly resolve whether `benchmark_index_name=null` is acceptable for production golden rows. No action required in this evidence artifact.

### F4 — INFO: Untracked artifact content not validated by `git diff --check HEAD`

**Severity**: INFO

**Evidence**: The artifact notes that `git diff --check HEAD` "checks tracked diff state and does not list the untracked artifact content." This is correct and expected behavior.

**Impact**: None for this gate. The artifact is a review document, not executable code. Its internal consistency, formatting, and completeness were verified by this review. No whitespace, encoding, or structural issues found.

**Required disposition**: None.

## Residuals

| Residual | Status | Owner |
|---|---|---|
| `index_profile` benchmark-context golden eligibility | Accepted for future golden gate review; must resolve `benchmark_index_name=null` question | Future golden gate |
| `tracking_error` blocked for all 5 enhanced-index candidates | `blocked_no_direct_tracking_error`; no candidate promotable | Closed for P16-S1 |
| `001548` production `tracking_error` | Remains blocked by P15-S1A | Future retry gate |
| `161725` enhanced-index tracking-error | Fixture-only, not production evidence | Closed |
| Extractor `tracking_error` note inconsistency | Observation only; no evidence impact | Future extractor refinement |
| Empty `nav_provider` injection | Acceptable for evidence gate; future golden gate should confirm | Future golden gate |
| Index methodology / constituents / external adapters | Out of scope | Future phase |

## Next-gate Implications

1. If this review is accepted, a future golden gate may open for `index_profile` benchmark-context candidates only.
2. The golden gate must explicitly resolve whether `benchmark_index_name=null` composite benchmarks are acceptable production golden evidence.
3. No `tracking_error` golden gate should open from P16-S1 results — all 5 candidates lack direct observed disclosure.
4. `001548` and `161725` residuals remain unchanged from prior gates.
5. No source code, extractor, or test changes are justified by P16-S1 evidence results.
