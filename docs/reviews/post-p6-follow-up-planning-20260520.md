# Post-P6 Follow-up Planning - 2026-05-20

## Verdict

Post-P6 next phase should be **P7 annual report source migration**.

First recommended next gate:

```text
P7-S1 EID source research spike plan/review
```

Rationale in one sentence: after P6 made template contracts deterministic, the highest leverage remaining reliability bottleneck is the trustworthiness, provenance, and resilience of annual report acquisition through the unified document repository.

## Inputs

- `docs/design.md`
- `docs/implementation-control-p4.md`
- `docs/reviews/p6-draft-pr-gate-reconciliation-20260520.md`
- `docs/reviews/p6-acceptance-ready-to-open-draft-pr-reconciliation-20260520.md`
- `docs/reviews/annual-report-source-strategy-reconciliation-20260520.md`
- `docs/reviews/post-p5-follow-up-planning-20260520.md`

## Current State

P6 is closed and already integrated on `main`. It delivered deterministic template contract hardening:

- machine-readable `CHAPTER_CONTRACT`
- renderer chapter identity aligned to contract truth
- deterministic C2 programmatic contract audit
- deterministic `ITEM_RULE` manifest/evaluator
- FQ5 upgraded to `template_contract_applicability`

The remaining accepted residual risks are non-blocking for P6:

- P6-S6 / RR-13 `016492` duplicate App source reconciliation remains user/App-source owned.
- RR-16 correctness denominator expansion remains future contract-aware correctness work.
- RR-7 item-level Evidence Confirm remains v2 scope.
- LLM audit E1/E2/E3/C1/C2 remains v2 scope.
- Annual report source strategy remains P7 data-source migration.
- Template content refinements, including Chapter 2/4 lens expansion and Chapter 0 copy cleanup, remain future template content work.

## First Principles

The project’s north star is not merely to render a structurally valid report; it is to produce a fund analysis that is evidence-backed and useful enough to prevent poor investor behavior.

P4/P5 made extraction quality measurable and gateable. P6 made template rules deterministic. The next foundational question is:

```text
Are we obtaining the right official source documents, with enough provenance, through the right boundary?
```

If annual report acquisition is not anchored on the most authoritative public source and does not carry source metadata, then later work has weaker footing:

- correctness expansion compares against data whose origin is less explicit
- Evidence Confirm lacks strong document provenance
- LLM audit may review fluent text over uncertain source material
- template/lens refinements improve wording but not underlying evidence trust

The existing architecture already has the right boundary: callers use `FundDocumentRepository.load_annual_report(...)`; source migration can happen behind that interface without moving source-specific logic into Service/UI.

## Candidate Backlog

| Candidate | Priority | Owner | Scope | Acceptance Signal | Decision |
|---|---:|---|---|---|---|
| P7 annual report source migration | P0 | Capability / document repository | Move annual report acquisition toward EID / CSRC electronic disclosure as primary source, with Eastmoney/akshare fallback and source metadata | Repository can locate/download annual reports via EID research path or documented adapter contract; fallback is explicit; source/year metadata is preserved | Recommended next phase |
| RR-16 contract-aware correctness denominator expansion | P1 | Capability / snapshot + score | Expand correctness denominator beyond current explicit comparable subfields using contract-aware fields and golden answer coverage | `score.json.correctness` compares more audited subfields without guessing unavailable values | Defer until source/provenance layer is stronger |
| P6-S6 / `016492` human source reconciliation | Human / P1 | User / App source | Verify duplicate `016492` in selected-fund CSV against App source | User confirms whether CSV should keep, delete, or correct duplicate | Human-owned; can run in parallel, not next code phase |
| v2 Evidence Confirm / LLM audit | P2 | Capability / future audit | Add item-level evidence confirmation and LLM audit for E1/E2/E3/C1/semantic C2 | Claims are checked against evidence spans through document repository, with repair contract support | Premature before source metadata and document retrieval hardening |
| ITEM_RULE renderer/audit integration | P2 | Capability / template + audit | Use ITEM_RULE evaluator to assert inactive conditional sections are absent and eventually render triggered sections | Conditional segment behavior is tested against rendered chapter blocks | Useful but lower leverage than source trust; current renderer does not yet render those conditional full sections |
| Template content/lens refinement | P3 | Capability / template content | Refine Chapter 2/4 lens coverage, Chapter 0 copy duplication, and wording | Cleaner reports and fewer deferred template content risks | Important polish, but does not improve data provenance or audit foundation |

## Recommended Phase: P7 Annual Report Source Migration

### Why Highest Leverage

1. It directly supports the design principle “证据可审计”.
2. It improves the root input for extraction, snapshot, score, quality gate, audit, and future Evidence Confirm.
3. It is already identified and accepted in `annual-report-source-strategy-reconciliation`.
4. It fits existing boundaries: implementation should stay behind `FundDocumentRepository`, not leak source details into Service/UI.
5. It de-risks later correctness and LLM audit work by giving them stronger document provenance.

### Recommended P7 Slices

| Slice | Scope | Acceptance Signal |
|---|---|---|
| P7-S1 EID source research spike | Research `eid.csrc.gov.cn/fund` lookup flow, fund code/name query, annual report filtering, PDF/download identifiers, rate limits, timeout and failure modes | Artifact documents API/browser flow samples, stable query keys, response shape, failure modes, and whether automated access is practical |
| P7-S2 Document repository source abstraction | Introduce internal `AnnualReportSource` adapter boundary inside document repository; define source priority, timeout, fallback, source metadata, and year validation | Existing repository callers unchanged; tests prove fallback order and no Service/UI source coupling |
| P7-S3 EID primary implementation | Implement EID-primary annual report lookup/download with Eastmoney/akshare fallback | For fixture/fake adapters, EID hit wins; EID miss/failure falls back; wrong-year documents fail closed |
| P7-S4 Source metadata hardening | Persist annual report source metadata through cache/parsed report metadata | Snapshot/report debugging can identify source, announcement id/pdf id/year, and fallback path |

## First Gate Requirements

`P7-S1 EID source research spike plan/review` should produce a code-generation-ready plan before any implementation.

The plan must answer:

1. What is the exact EID public access path for fund annual reports?
2. Can lookup be done by fund code, fund name, manager, or a platform-specific id?
3. How does the system distinguish annual reports from quarterly/semiannual reports?
4. How is report year validated before download/cache reuse?
5. What stable source metadata should be captured?
6. What are bounded timeout, retry, rate-limit, and schema-drift behaviors?
7. What remains fallback-only on Eastmoney/akshare?
8. How tests avoid real network while still covering source priority and fallback?

## Non-goals

The next phase should not:

- bypass `FundDocumentRepository`
- let Service/UI know about EID, Eastmoney, akshare, 天天基金, or PDF URLs
- directly read PDF/cache from upper layers
- put explicit source parameters in `extra_payload`
- introduce LLM audit or Evidence Confirm
- expand template prose/lens content
- auto-resolve `016492` without user/App source confirmation
- change CHAPTER_CONTRACT / ITEM_RULE semantics
- change quality gate FQ5 beyond consuming current score facts

## Residual Risks And Owners

| Risk | Owner / Destination | Status |
|---|---|---|
| P6-S6 / RR-13 duplicate `016492` | User / App source reconciliation | Open, human-owned; can proceed in parallel |
| RR-16 correctness denominator limited | Future contract-aware correctness slice after P7 source/provenance hardening | Open |
| RR-7 item-level Evidence Confirm | v2 Evidence Confirm after repository/source metadata is reliable | Deferred |
| LLM audit E1/E2/E3/C1/semantic C2 | v2 LLM audit | Deferred |
| ITEM_RULE renderer/audit integration | Future template/audit slice | Deferred |
| Template content and lens refinements | Future template content slice | Deferred |
| Annual report source migration | P7 | Recommended next |

## Gate Decision

Move from:

```text
P6 closed / integrated on main
```

to:

```text
P7-S1 EID source research spike plan/review
```

No code should be changed until the P7-S1 plan is reviewed and accepted.
