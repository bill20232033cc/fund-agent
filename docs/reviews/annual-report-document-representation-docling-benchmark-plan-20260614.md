# Annual-report Document Representation / Docling Benchmark Plan

Date: 2026-06-14

Role: Planning worker only

Gate: `Annual-report Document Representation / Docling Benchmark Planning Gate`

Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

Release/readiness posture: `NOT_READY`

## 1. Goal And Motivation

Define a bounded, code-generation-ready plan for evaluating whether `fund-agent` needs a normalized Fund documents-layer annual-report document representation.

The motivation is not that Docling is currently required for OCR or should replace the production parser. The accepted control diagnosis is narrower: repeated Route C chapter-specific stabilization moves the first blocker but does not prove comprehensive annual-report understanding. The project currently has a field/extractor-driven and prompt-contract-driven path, while the Fund documents layer lacks a durable representation that preserves section hierarchy, reading order, table blocks, page spans, provenance, bbox, failure taxonomy and stable `EvidenceAnchor` mapping across reports.

The later implementation gate should therefore benchmark:

- current `pdfplumber` plus `locate_sections` plus current extractor pipeline;
- Docling as a parallel benchmark candidate inside the Fund documents boundary;
- a candidate normalized annual-report representation that can feed existing extractor / chapter fact projection / `EvidenceAnchor` machinery without making Docling Markdown, raw text, HTML or JSON a fact truth source.

## 2. Accepted Current Facts

Accepted from `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` and `docs/reviews/provider-llm-route-stabilization-closeout-controller-judgment-20260614.md`:

| Fact | Planning consequence |
|---|---|
| `AGENTS.md` is the highest-priority execution rule source. | This plan cannot authorize source/test/runtime changes, parser replacement, fallback/source expansion, readiness, release or PR work. |
| `docs/design.md` is the design truth source; `docs/implementation-control.md` is the control truth source. | This artifact is a planning proposal only and does not update design/control truth. |
| The target architecture remains `UI -> Service -> Host -> Agent`. | Any future parser or representation implementation must stay under Agent/Fund documents; UI, Service, Host, renderer and quality gate must not directly call parser internals. |
| Production annual-report access must go through `FundDocumentRepository.load_annual_report()`. | Later benchmark execution must use the repository boundary or explicitly authorized non-production fixtures; it must not directly read production PDF paths from UI/Service/Host/renderer/quality gate. |
| Annual-report parser internals, including `pdfplumber` or Docling, belong inside `fund_agent/fund` documents. | Docling can only be introduced as a Fund documents internal benchmark candidate unless a later accepted design gate changes that. |
| Document intermediates are not fact truth. | Docling Markdown, raw text, HTML, JSON, OCR text or table raw output can only be extractor inputs or benchmark artifacts; fund facts still require project-owned extractor / chapter fact projection / `EvidenceAnchor`. |
| Current operational annual-report source policy is EID single-source, no fallback. | Benchmarking must preserve `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false` and no Eastmoney/fund-company/CNINFO fallback. |
| `not_found` and `unavailable` are terminal EID source failures under current policy; `schema_drift`, `identity_mismatch` and `integrity_error` fail closed. | Benchmark taxonomy must not reclassify source failures into parser wins/losses or fallback eligibility. |
| Current default production path is deterministic `fund-analysis analyze/checklist`; `analyze-annual-period` is deterministic and does not accept `--use-llm`. | This plan must not design an annual-period LLM route or default-on LLM analysis. |
| Route C `--use-llm` is explicit opt-in, provider-backed and fail-closed. | Benchmark output must not be accepted as LLM route readiness or content-quality proof. |
| Current body-chapter repair budget remains one regenerate attempt and is not product-calibrated. | Benchmark planning must not change repair budget or use repair churn as a substitute for document representation evidence. |
| Release/readiness remains `NOT_READY`. | Later evidence may support a representation decision, but cannot itself claim release/readiness without a separate readiness gate. |

Research input from `docs/reviews/annual-report-docling-parser-discussion-summary-20260613.md` is useful but not accepted design truth. It may inform future benchmark hypotheses, especially around text-based PDFs, section gaps, table structure and provenance, but future evidence must re-establish any measured claims under an accepted evidence gate.

## 3. Non-goals And Hard Boundaries

This gate and this plan do not authorize:

- source, test, runtime, README, design doc, control doc or startup packet changes;
- live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands in this planning gate;
- PDF body inspection or report body inspection in this planning gate;
- Docling installation, dependency changes or production dependency declaration;
- production parser replacement;
- Docling Markdown/HTML/JSON/raw output as fund fact truth;
- direct Service/UI/Host/renderer/quality-gate calls to `pdfplumber`, Docling, parser cache, PDF cache, source helpers or download helpers;
- fallback/source expansion, including Eastmoney, fund-company/CDN, CNINFO or multi-source policy;
- annual-period LLM route design, `analyze-annual-period --use-llm`, default-on LLM writing or multi-period LLM chapter generation;
- chapter repair-budget calibration;
- golden/readiness promotion, release readiness, cleanup, staging, commit, push or PR state changes.

## 4. Benchmark Sample Policy

Later benchmark execution must use an explicit sample manifest, reviewed before parser execution. The manifest should be data-minimal and identity-first:

| Sample tier | Purpose | Inclusion policy | Exclusion policy |
|---|---|---|---|
| Tier A: accepted exact identity sample | Anchor the benchmark to already accepted annual-report source policy. | Include `004393 / 2021-2025` only if the later evidence gate explicitly authorizes FDR/PDF access or uses existing accepted non-body metadata. | Do not reuse prior live output as parser-quality proof without rerunning or citing accepted evidence scope. |
| Tier B: fund-type coverage sample | Cover `index_fund`, `enhanced_index`, `active_fund`, `bond_fund`, `qdii_fund`, `fof_fund` when available. | Select by exact `(fund_code, report_year, report_type=annual)` identity and source metadata through `FundDocumentRepository`. | Do not treat local `基金年报/` files or metadata-only disposition as source identity proof. |
| Tier C: table-stress sample | Exercise fees, performance, holdings, holder structure, share changes, manager ownership and bond-risk tables. | Require documented expected stress reason before execution, such as cross-page table, multi-level header, merged cell or ambiguous same-name field. | Do not add samples solely because a parser output looks good or bad after inspection. |
| Tier D: synthetic/parser fixtures | Validate parser adapter mechanics without production PDF reads. | Use small hand-authored text/table fixtures or generated in-repo parser fixtures if a later implementation gate approves them. | Do not infer real annual-report coverage, source identity or readiness from synthetic fixtures. |

Minimum later benchmark set recommendation:

- one accepted exact identity chain sample: `004393 / 2021-2025` if authorized;
- one same-year fund-type panel with at least five annual reports covering active, index/enhanced, QDII, feeder/ETF-linked and bond styles, re-established through FDR/source identity in the later gate;
- two negative or degraded fixtures for parser failures, such as missing section heading and malformed/merged table header, without PDF body access.

The later gate must predeclare:

- sample ids, fund code, report year, report type and expected fund type;
- source identity proof required for each real report;
- which samples are real FDR-loaded annual reports and which are non-production fixtures;
- whether body/PDF access is authorized for that evidence gate;
- expected benchmark output paths and disposition.

## 5. Benchmark Artifact Policy

Benchmark artifacts must remain evidence artifacts, not production truth:

| Artifact class | Later path policy | Retention policy | Truth status |
|---|---|---|---|
| Parser raw output | Runtime/cache path under a later approved benchmark directory, not committed unless explicitly reduced/redacted. | Large Docling JSON, HTML, Markdown, page images or raw parser dumps should be untracked runtime artifacts by default. | Parser intermediate only; not fund fact truth. |
| Normalized representation snapshots | Small, redacted JSON fixtures may be committed under a later approved test fixture path if needed. | Commit only minimal records needed for deterministic unit tests. | Candidate contract fixtures only. |
| Benchmark summary | `docs/reviews/*evidence*.md` in a later evidence gate. | Commit as reviewed evidence artifact if accepted. | Evidence-chain artifact only; does not update design truth by itself. |
| Metrics table | CSV/JSON under a later approved evidence artifact path, preferably small and deterministic. | Commit if it contains no report body and is necessary for review. | Benchmark metric evidence only. |
| Error taxonomy log | Structured JSON or Markdown table in the evidence artifact. | Commit reduced failure records, not raw PDFs or full extracted bodies. | Failure-classification evidence only. |

Raw body text and full extracted report bodies should not be committed. If future reviewers need body snippets, the plan must require bounded excerpts with page/section/table references and copyright-safe minimization.

## 6. Comparison Matrix

Later implementation/evidence must compare current pipeline and Docling candidate across the following dimensions.

| Dimension | Current pipeline observation to capture | Docling candidate observation to capture | Acceptance signal | Fail-closed signal |
|---|---|---|---|---|
| Section hierarchy | `locate_sections` section ids, headings, start/end offsets, missed sections. | heading levels, reading-order groups, page spans and section nesting. | Candidate improves or equals coverage for core annual-report sections without breaking existing anchors. | Candidate invents hierarchy, merges unrelated sections or loses required current sections. |
| Page spans | current section/page inference available to `EvidenceAnchor`. | block-level and section-level page spans. | Stable section-to-page mapping supports chapter evidence routing. | Page spans missing, unstable or incompatible with existing anchors. |
| Paragraphs | raw text paragraph boundaries, if any, and extractor consumption points. | normalized paragraph blocks with reading order and provenance. | Paragraph blocks reduce same-field ambiguity and preserve context. | Paragraph segmentation drops disclaimers, table notes or manager discussion context. |
| Table blocks | current `page.extract_tables()` rows/headers and downstream table adapters. | table cells, rows, columns, captions, header structure and provenance. | Candidate preserves row/column meaning for fees, performance, holdings, holder structure, share changes and bond-risk tables. | Candidate flattens tables into lossy text or changes numeric association. |
| Cross-page tables | current split-table behavior and downstream stitching gaps. | cross-page continuation signals or recoverable table grouping. | Candidate enables deterministic continuation grouping or at least exposes enough provenance for project-owned stitching. | Candidate silently duplicates, drops or misorders rows across pages. |
| Merged headers/cells | current header rows, blank cells and manual disambiguation burden. | explicit spans or recoverable cell grouping. | Candidate improves multi-level header mapping for performance/fee/holding tables. | Candidate expands merged cells incorrectly or hides ambiguity. |
| bbox/provenance | existing page/table/row anchor fields and any coordinate absence. | bbox, page, block id, cell id and source element provenance. | Candidate provenance maps to stable `EvidenceAnchor` fields without leaking parser-specific ids into public contracts. | Provenance is absent, non-deterministic or too parser-specific for stable anchors. |
| `EvidenceAnchor` mapping | current anchors from extractor fields to section/table/row/page. | adapter-projected anchors from normalized blocks. | Anchor projection is deterministic and row-level/table-level where available. | Any field fact loses traceability or maps to broad raw document spans only. |
| Failure taxonomy | current missing/ambiguous/unavailable/fail-closed parser/extractor outcomes. | parser failure, partial parse, low confidence, unsupported element, timeout and schema drift categories. | New taxonomy composes with current EID source failures and extractor fail-closed semantics. | Parser failures are reported as source not-found/unavailable, fallback eligibility or silent success. |
| Latency | current parse time and cache reuse behavior. | Docling conversion time and normalized projection time. | Candidate overhead is measurable, cacheable and acceptable for offline benchmark or future precompute. | Conversion time is unbounded, non-reproducible or blocks current deterministic commands. |
| Cache | current EID single-source cache metadata and parser output cache. | candidate Docling artifact cache and representation cache. | Cache key includes parser name/version, fund code, year, report type, source identity and content fingerprint when available. | Cache can cross-apply wrong fund/year/source or hides parser version drift. |
| Reproducibility | current parser output stability across repeated runs. | Docling output stability across repeated runs and versions. | Repeat runs produce identical normalized snapshots or explainable versioned diffs. | Non-deterministic ordering, ids, text normalization or table layout changes break fixtures. |

## 7. Candidate `FundDisclosureDocument` Schema Concept

This section is candidate-only. It is not current design truth and must not be implemented without a later accepted design/implementation gate.

Candidate module ownership:

- package: `fund_agent/fund/documents/`;
- stable public boundary: repository returns or exposes it only through Fund documents-owned APIs;
- consumers: existing Fund extractors, chapter fact projection and evidence anchor mapping;
- non-consumers: UI, Service, Host, renderer and quality gate must not directly parse or inspect parser-specific documents.

Candidate schema sketch:

```python
@dataclass(frozen=True)
class FundDisclosureDocument:
    """候选年报文档表示；仅供后续 gate 评审，不是当前代码事实。"""

    document_id: DisclosureDocumentId
    source_identity: DisclosureSourceIdentity
    parser_identity: ParserIdentity
    sections: tuple[DisclosureSection, ...]
    blocks: tuple[DisclosureBlock, ...]
    tables: tuple[DisclosureTable, ...]
    anchors: tuple[DisclosureAnchorCandidate, ...]
    failures: tuple[DisclosureParseIssue, ...]
    metadata: DisclosureDocumentMetadata
```

Candidate field concepts:

| Concept | Required contents | Boundary |
|---|---|---|
| `DisclosureDocumentId` | `fund_code`, `report_year`, `report_type`, source id, optional content fingerprint. | Must be exact identity; no fund-code-only cache state. |
| `DisclosureSourceIdentity` | selected source, source mode, fallback flags, acquisition metadata already accepted by FDR policy. | Must preserve EID single-source/no-fallback. |
| `ParserIdentity` | parser engine, parser version, adapter version, projection version, options hash. | Required for cache reproducibility and fixture drift diagnosis. |
| `DisclosureSection` | stable section id when known, title, level, page span, block span, confidence, parent id. | Must distinguish canonical annual-report section id from parser-inferred heading. |
| `DisclosureBlock` | block id, type (`paragraph`, `heading`, `table`, `list`, `note`, `image_ref`, `unknown`), text summary, page span, bbox list, reading order. | Full body text may be excluded from committed fixtures. |
| `DisclosureTable` | table id, caption, page span, rows, cells, header candidates, continuation links, bbox/provenance. | Must support row-level `EvidenceAnchor` candidates. |
| `DisclosureCell` | row/column index, row/column span, normalized text, numeric parse candidate, bbox/provenance, header role. | Parser-specific raw fields stay internal. |
| `DisclosureAnchorCandidate` | block/table/cell/section provenance that can project to existing `EvidenceAnchor`. | Does not replace project-owned `EvidenceAnchor`. |
| `DisclosureParseIssue` | issue code, severity, parser stage, affected page/block/table, cause, fail-closed mapping. | Must not collapse into source fallback policy. |
| `DisclosureDocumentMetadata` | page count, parse duration, cache key, created parser artifact references, redaction/body-retention flags. | Artifact references are internal and must not leak into Service/UI contracts. |

Candidate parser adapters:

- `PdfplumberDisclosureParser`: wraps current `pdfplumber` plus `locate_sections` output into the candidate representation without changing production extraction semantics.
- `DoclingDisclosureParser`: converts Docling output into the same candidate representation for benchmark only.
- `DisclosureDocumentComparator`: compares two candidate representations and emits metrics, not product facts.

Any later implementation must keep existing `ParsedAnnualReport` and extractor behavior stable until a separate migration gate explicitly accepts replacement or dual-read behavior.

## 8. Later Implementation Slices

These slices are for a future gate only. They are not authorized now.

### Slice 0: Preflight And Sample Manifest

Goal: create a reviewed sample manifest and artifact routing policy.

Allowed future changes:

- add a benchmark manifest file under a later approved path;
- add small schema docs or typed constants if the later plan authorizes them.

Required decisions:

- exact sample list and source identity requirements;
- real-report vs fixture split;
- whether FDR/PDF body access is authorized;
- benchmark artifact output directory and retention policy.

Stop if any sample lacks exact `(fund_code, report_year, report_type)` identity or body-access authorization is unclear.

### Slice 1: Candidate Schema Types Only

Goal: introduce candidate internal dataclasses/protocols without wiring production behavior.

Potential future files:

- `fund_agent/fund/documents/disclosure_document.py`;
- `tests/fund/documents/test_disclosure_document_schema.py`;
- conditional `fund_agent/fund/README.md` update if public package documentation changes.

Expected assertions:

- exact identity fields are required;
- parser identity/version/options are required;
- parser-specific raw ids do not appear in public `EvidenceAnchor`;
- source policy flags preserve EID single-source/no-fallback semantics.

### Slice 2: Pdfplumber Projection Adapter

Goal: project the current parser output into candidate `FundDisclosureDocument` for benchmark comparison, without changing current extractors.

Potential future files:

- `fund_agent/fund/documents/pdfplumber_disclosure_parser.py`;
- tests with synthetic parsed annual report fixtures.

Expected assertions:

- current sections/tables/metadata can be represented loss-minimally;
- missing bbox is explicit, not silently invented;
- current failure categories map to candidate parse issues without changing source failure semantics.

### Slice 3: Docling Benchmark Adapter Behind Optional Boundary

Goal: add a Docling adapter only if a later gate explicitly authorizes dependency strategy.

Potential future strategies:

- optional import with clear `DoclingUnavailable` benchmark-only failure;
- no production dependency unless separately accepted;
- benchmark CLI/helper stays under Fund documents test/tooling boundary, not Service/UI/Host.

Expected assertions:

- absence of Docling fails as skipped/unavailable benchmark, not production failure;
- Docling output is projected into candidate schema;
- no direct Docling imports outside approved Fund documents adapter.

### Slice 4: Comparator And Metrics

Goal: compare pdfplumber projection and Docling projection on predeclared dimensions.

Potential future files:

- `fund_agent/fund/documents/disclosure_benchmark.py`;
- tests for deterministic metric calculation.

Expected metrics:

- section coverage and hierarchy depth;
- table count and table role coverage;
- row/cell/header preservation;
- cross-page continuation candidates;
- anchor projection coverage;
- parse issue counts by taxonomy;
- latency and cache-key stability.

### Slice 5: Evidence Gate Runner

Goal: run the accepted benchmark matrix and write a reviewed evidence artifact.

Allowed only in a later evidence gate:

- FDR/PDF/parser commands explicitly authorized by that gate;
- Docling execution only if dependency and environment are approved;
- reduced evidence artifact under `docs/reviews/`.

Stop if parser output requires committing raw report bodies, if source identity is ambiguous, or if any fallback/source expansion is attempted.

### Slice 6: Decision Gate

Goal: decide whether to keep Docling as research input, continue parallel benchmark, or design a Fund documents-layer representation implementation.

Possible outcomes:

- `KEEP_PDFPLUMBER_ONLY`: Docling does not improve required dimensions enough.
- `CONTINUE_PARALLEL_BENCHMARK`: promising but evidence incomplete.
- `DESIGN_FUND_DISCLOSURE_DOCUMENT`: normalized representation justified, parser choice still internal.
- `DESIGN_DOCLING_INTERNAL_CANDIDATE`: Docling justified as one internal parser candidate, not production replacement by default.

## 9. Validation Matrix For Later Evidence Gate

| Validation id | Scope | Command class | Expected pass condition | Must not prove |
|---|---|---|---|---|
| V0 | Static import boundary | no-live static test | No Docling/parser imports outside approved `fund_agent/fund/documents` adapter path. | Does not prove parser quality. |
| V1 | Schema identity | unit tests | Candidate document requires exact fund/year/report/source/parser identity. | Does not prove source acquisition. |
| V2 | Pdfplumber projection | unit tests with fixtures | Current parsed output projects to candidate schema with explicit gaps. | Does not change production extractor behavior. |
| V3 | Docling unavailable path | unit tests | Missing optional Docling reports benchmark-unavailable without production failure. | Does not accept Docling dependency. |
| V4 | Section hierarchy benchmark | evidence metric | Predeclared sections compared with missed/extra/ambiguous categories. | Does not claim all sections are semantically correct. |
| V5 | Table block benchmark | evidence metric | Predeclared table families compared on row/header/cell preservation. | Does not claim extracted fund facts are correct. |
| V6 | Cross-page and merged-cell benchmark | evidence metric | Continuation/header-span candidates reported deterministically. | Does not enable production stitching automatically. |
| V7 | `EvidenceAnchor` projection | unit + evidence metric | Candidate blocks/tables can map to existing anchor shape at section/page/table/row/cell granularity where available. | Does not replace current anchor contract. |
| V8 | Failure taxonomy | unit tests | Parser failures map to parse issues and compose with EID source failure taxonomy. | Does not authorize fallback. |
| V9 | Latency/cache | benchmark evidence | Parse duration, artifact size and cache key are recorded with parser version/options. | Does not set production SLA. |
| V10 | Reproducibility | repeated benchmark or snapshot test | Normalized snapshots are stable or diffs are version-explained. | Does not freeze Docling version policy. |
| V11 | Non-regression | targeted existing tests | Current deterministic analyze/checklist/extractor tests remain unchanged unless a later migration gate authorizes change. | Does not prove LLM readiness. |
| V12 | Artifact hygiene | evidence review | Raw bodies/PDFs/full parser dumps are untracked or explicitly dispositioned; summary evidence is reviewable. | Does not prove release readiness. |

Later evidence must report exact commands, environment, parser versions, sample manifest hash/path, output artifact paths and any skipped validations.

## 10. Risks And Residuals

| Risk / residual | Impact | Mitigation / owner |
|---|---|---|
| Docling output looks richer but does not improve project-owned extractor correctness. | Parser churn without product value. | Require extractor-adjacent metrics and `EvidenceAnchor` mapping, not only prettier Markdown/HTML. Owner: Fund documents / extractor owner. |
| Parser-specific ids leak into public contracts. | Future cache and anchor instability. | Candidate schema must project to stable project-owned ids and keep raw parser ids internal. Owner: Fund documents owner. |
| Benchmark sample is biased toward known easy documents. | False confidence. | Predeclare sample manifest with fund-type and table-stress coverage before execution. Owner: evidence gate owner. |
| Local `基金年报/` corpus is treated as truth. | Violates FDR/source policy. | Use only as research/disposition input unless exact FDR/source identity is established in a later gate. Owner: controller/evidence owner. |
| Docling dependency or model assets change reproducibility. | Non-deterministic benchmark and CI friction. | Record parser version/options/cache key; optional boundary first; no production dependency without separate gate. Owner: implementation owner. |
| Large raw parser artifacts enter git. | Repository noise and copyright/body-retention risk. | Commit reduced metrics/snapshots only; keep raw dumps untracked or separately dispositioned. Owner: artifact owner. |
| Source failures and parser failures are conflated. | Breaks EID single-source/no-fallback semantics. | Separate source taxonomy from parser taxonomy in schema and evidence. Owner: Fund documents owner. |
| Benchmark is mistaken for readiness. | Incorrect release posture. | Preserve `NOT_READY`; require separate readiness/release gate. Owner: controller/release owner. |
| Annual-period LLM route pressure re-enters through representation design. | Scope expansion. | Keep multi-period LLM route deferred until representation evidence is accepted. Owner: Service/Fund/Agent product owner. |
| Current `ParsedAnnualReport` migration is under-specified. | Implementation may accidentally change production extraction. | Future slices must be additive first; replacement requires separate migration gate. Owner: implementation/review owners. |

## 11. Exact Next Gate Recommendation

Proceed next to:

```text
Annual-report Document Representation / Docling Benchmark Plan Review Gate
```

Review scope:

- verify this plan preserves `FundDocumentRepository` boundary, EID single-source/no-fallback and `NOT_READY`;
- verify Docling is only a parallel benchmark candidate, not a production parser replacement;
- verify the comparison matrix covers section hierarchy, page spans, paragraphs, table blocks, cross-page tables, merged headers/cells, bbox/provenance, `EvidenceAnchor` mapping, failure taxonomy, latency/cache/reproducibility;
- verify sample/artifact policy prevents body/PDF/source/readiness overclaiming;
- verify candidate `FundDisclosureDocument` remains explicitly candidate-only;
- verify later implementation slices are additive, bounded and reviewable.

If the plan review accepts this artifact, the next implementation-facing gate should be:

```text
Annual-report Document Representation / Docling Benchmark Sample Manifest And Candidate Schema No-live Implementation Gate
```

That gate should start with Slice 0 and Slice 1 only. It should still preserve no-live posture unless separately authorized, should not install Docling by default, and should not run parser/PDF/FDR commands until a later evidence gate explicitly authorizes them.

Deferred gates:

- Docling execution / parallel parser evidence gate;
- `FundDisclosureDocument` migration or production adoption gate;
- Provider/LLM chapter stabilization gates;
- repair budget calibration;
- annual-period or multi-period disclosure LLM route design;
- fallback/source expansion;
- golden/readiness/release/PR gates.
