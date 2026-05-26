# Release Maintenance Report-Quality Validator Integration Decision Plan

> Date: 2026-05-25
> Gate: `report-quality validator integration decision planning`
> Role: planning specialist
> Status: planning-only; not approved for implementation
> Rules truth: `AGENTS.md`
> Design truth: `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §9.1 / §10
> Control truth: `docs/implementation-control.md` Startup Packet and Next Entry Point
> Prior evidence: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`
> Prior judgment: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-controller-judgment-20260525.md`

## 1. Scope / Non-Goals

This gate is planning-only. The allowed output is this plan artifact under `docs/reviews/`.

This plan must not authorize source, test, README, tracked report, fixture, curated baseline, renderer, Service, CLI, `quality_gate.py`, `extraction_score.py`, repository/PDF/cache/source helper, `FundDocumentRepository`, Host/Agent, Dayu, or product-flow changes.

Non-goals:

1. Do not change current v0 renderer or current 8-chapter report output.
2. Do not change FQ0-FQ6 behavior or wire report-quality validator results into FQ0-FQ6.
3. Do not promote scoring-run output, JSONL, reviewed bundles, local scratch files, or synthetic data into durable fixtures or baseline.
4. Do not create `fund_agent/host`, `fund_agent/agent`, `dayu.host`, `dayu.engine`, runner, ToolRegistry, ToolTrace, session/run lifecycle, memory, outbox, or replay behavior.
5. Do not introduce a Service/CLI user command unless a later reviewed gate proves crossing that boundary is necessary.
6. Do not change `nav_data` projection, derived-calculation population, fallback recovery, FOF taxonomy, repository identity proof, or source fallback behavior.
7. Do not pass explicit arguments through `extra_payload`, `**kwargs`, or implicit extension dictionaries.

## 2. First-Principles Decision

The immediate problem is not that users lack a command to invoke the validator. The immediate problem is that report quality is still not proven observable on real or quasi-real `ReportEvidenceBundle` content.

`docs/design.md` §5.4 requires report quality to become scoreable and replayable before data-source, extractor, template, writer, Service, renderer, or gate changes. §5.4.1 requires failures to localize to field, chapter, evidence, or writing rule. §5.4.2 requires Fact/Evidence to be the only factual input. The accepted dry-run evidence proves public validator API consumption over synthetic input, but it explicitly does not prove product-flow readiness, extraction correctness, annual-report identity, durable baseline readiness, or multi-bundle aggregation.

Therefore the next shortest and most robust path is to keep the validator outside product flow and run it against one real or quasi-real scoring candidate bundle as evidence. This advances上线可用性 because it tells the project whether the current report-quality input contract can produce actionable failure categories from production-shaped content, without prematurely converting an experimental diagnostic into a product gate.

## 3. Candidate Paths

| Path | Description | Benefit | Risk / cost | Decision |
|---|---|---|---|---|
| A | `docs/reviews` scoring-run evidence loop: continue evidence-only, use one real or quasi-real bundle, do not create durable fixture | Shortest path to product-useful evidence; preserves design rule that scoring precedes product integration; failure categories can drive next source/template/scoring choice | Still manual; does not create reusable command; needs careful identity and scratch-output boundaries | **Recommended next** |
| B | Fund internal report-quality tooling / script-like module, still not Service/CLI | Creates repeatable internal consumer without crossing product boundary | Adds source surface before proving real bundle usefulness; may become a hidden CLI by convention | Defer until A shows repeated evidence collection is valuable |
| C | Service/CLI opt-in integration | Gives developers a command or scenario entry point | Crosses Service/CLI boundary before proving input quality; can be mistaken for product readiness | Defer pending A evidence and a separate boundary design/review |
| D | `quality_gate.py` / FQ0-FQ6 integration | Centralizes gating | Violates current non-goal; report-quality scoring is future observation tool and must not replace current FQ gate | Defer by default |
| E | Curated fixture / baseline promotion | Durable regression asset | Current evidence is synthetic; real corpus identity, fallback category, FOF taxonomy, and review-state proof remain incomplete | Defer by default |
| F | Host/Agent/dayu path | Aligns future orchestration | Current deterministic main path has no session/run/cancel/resume/tool-loop need; design requires independent architecture gate | Must defer |

## 4. Recommended Path

Recommend Path A: a `docs/reviews` scoring-run evidence loop over one real or quasi-real `ReportEvidenceBundle`, with scratch JSONL/result output outside durable baseline.

The next implementation gate should be:

`report-quality validator real-bundle evidence run`

It should answer one narrow question:

Can the accepted `validate_report_quality_bundle()` / `validate_report_quality_jsonl()` APIs consume a production-shaped or reviewed quasi-real `ReportEvidenceBundle` and produce replayable issue localization that tells us which next上线 blocker category dominates: data/source extraction, evidence traceability, chapter contract, score schema, or upstream identity?

Allowed tracked file:

1. `docs/reviews/release-maintenance-report-quality-validator-real-bundle-evidence-20260525.md`

Allowed untracked scratch output:

1. `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`
2. `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json`
3. Optional ignored local run directory only if already ignored, for example `reports/scoring-runs/report-quality-validator-real-bundle-20260525/`; do not rely on it as evidence unless the tracked Markdown summarizes it.

Allowed input for the next gate:

1. Use a manually assembled quasi-real bundle derived from accepted S0/S1/S2 review evidence and the current validator serialization shape.
2. Label the input provenance as `quasi_real_review_evidence`.
3. Do not claim `repository_verified`, `scoring_ready`, or `accepted_baseline`.

The implementation/evidence agent must not choose another input source without returning to controller. In particular, it must not project from a freshly generated `StructuredFundDataBundle`, run production extractors, fetch or parse annual reports, or call `FundDocumentRepository`, PDF/cache/source helpers, downloaders, or source adapters.

Minimum bundle content:

1. current `schema_version`;
2. `corpus_id`;
3. a non-final review status that does not overclaim baseline readiness;
4. at least one source document with explicit non-production provenance;
5. at least one fact or data gap tied to the accepted S0/S1/S2 evidence chain;
6. at least one score issue that can prove validator issue localization;
7. evidence anchors sufficient for backlink / pointer checks.

Disallowed inputs:

1. Fresh annual-report fetch or parse.
2. Direct PDF/cache/source helper access.
3. New tracked JSON fixture, golden answer, baseline, or report artifact.
4. Any input marked `accepted_baseline`.
5. Any bundle claiming FOF coverage without resolving the current FOF taxonomy/data-gap residual.
6. Any input sourced from live production extraction during this gate.

## 5. Concrete Consumer

The concrete consumer in the next gate is the implementation specialist's evidence command, not product code.

Consumer shape:

1. A one-off `.venv/bin/python` command or `/tmp` script imports:
   - `fund_agent.fund.report_quality_validation.validate_report_quality_bundle`
   - `fund_agent.fund.report_quality_validation.validate_report_quality_jsonl`
   - existing `ReportEvidenceBundle` / schema constants only if needed for serialization.
2. It receives explicit inputs:
   - `bundle_source_label`
   - `bundle_input_path` or in-memory bundle construction source
   - `run_id="evidence:report-quality-validator-real-bundle:20260525"`
   - `jsonl_output_path=/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`
   - `result_output_path=/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json`
3. It calls:
   - `validate_report_quality_bundle(bundle, source_path=bundle_source_label, run_id=run_id)`
   - `validate_report_quality_jsonl(jsonl_output_path, run_id=run_id)`
4. It writes only scratch JSONL/result to `/tmp`.
5. It writes the durable evidence summary only to the tracked Markdown artifact.

Required output in the evidence artifact:

1. Exact input provenance and why it is real or quasi-real.
2. State that the input is `quasi_real_review_evidence`; do not overclaim `repository_verified`, `fact_prefill_reviewed`, `scoring_ready`, or `accepted_baseline`.
3. `bundle_record_count`, `score_issue_record_count`, `schema_version`, `run_id`, `source_path`, `summary.total_records`, `summary.scoring_ready_record_count`, `blocking_count`, `material_count`, `minor_count`, `failed_closed`, and `error_code_counts`.
4. Top issue table grouped by `error_code`, `severity`, `record_pointer`, `record_id`, `field_name`, `expected`, `actual`, and next owner category.
5. Explicit statement that scratch JSONL/result are not durable fixture/baseline.

## 6. Boundary Plan

Path A remains inside planning/evidence workflow and Fund public validator APIs. It does not require Service or CLI because the current need is diagnostic evidence, not user invocation.

If later entering Service/CLI, a separate design/review gate must first answer:

1. Which user or developer workflow needs the command.
2. Whether the command consumes existing bundle JSONL, generates a bundle from an already extracted `StructuredFundDataBundle`, or triggers extraction.
3. How Service avoids direct PDF/cache/source helper calls and respects `FundDocumentRepository`.
4. Whether validator failures are warnings, structured diagnostics, or hard blockers.
5. How output paths are chosen without polluting durable baseline.
6. How FQ0-FQ6 remains unchanged.
7. Whether README/user docs must change because a new command is visible.

If the evidence loop remains manual after one run, that is acceptable. A manual loop is currently lower risk than a product command because it preserves the current non-goals and still produces the missing decision evidence.

## 7. Success Evidence

The next gate succeeds if it proves all of the following:

1. The validator can consume a real or quasi-real production-shaped bundle, not just synthetic negative cases.
2. The result is replayable: same input, same run id, stable summary fields, stable pointers, stable issue categories.
3. The output identifies the dominant next implementation category, such as `source_reliability`, `fact_projection`, `evidence_traceability`, `chapter_contract`, `score_schema`, or `identity_gap`.
4. The evidence is useful for上线 readiness because it tells the project what must be fixed before report-quality scoring can be trusted in a product path.
5. The artifact does not claim Service/CLI/FQ gate integration, renderer readiness, durable baseline readiness, extraction correctness, or annual-report identity beyond the input provenance actually shown.

This is product-useful but not product-integrated evidence.

## 8. Stop Conditions

Stop the next implementation and return to controller if any of the following becomes necessary:

1. Modifying source, tests, README, tracked reports, fixtures, product flow, Service, CLI, renderer, FQ0-FQ6, Host/Agent, Dayu, or package metadata.
2. Fetching or parsing a new annual report.
3. Calling repository/PDF/cache/source helper code beyond already accepted local evidence.
4. Promoting JSONL/result into a durable fixture or baseline.
5. Claiming `scoring_ready` without satisfying current validator preconditions.
6. Reclassifying FOF/QDII-FOF taxonomy or resolving fallback upstream category recovery.
7. Requiring multi-bundle aggregation semantics to interpret the result.
8. Needing `nav_data` or derived-calculation projection changes.

## 9. Residuals / Owners

| Residual | Owner / future gate | Handling |
|---|---|---|
| Multi-bundle JSONL | future validator hardening or tooling gate | Defer; next gate remains one bundle unless the input already contains one bundle plus linked issues |
| `unknown_upstream_failure_category` exact message | future validator robustness gate | Defer message-specific assertion; current evidence may record issue category only |
| Non-scoring-ready `chapter_summary/report_level` | future score-schema policy gate | Defer policy change; next evidence records current validator behavior |
| `nav_data` mapping | future source-contract slice | Keep excluded until safe mapping is accepted |
| Derived calculations | future calculation projection slice | Record empty/missing calculation issues only; do not populate new calculations |
| Durable baseline | future curated fixture/baseline gate | Do not promote scratch evidence |
| Fallback recovery | future source reliability evidence gate | Keep unresolved categories visible; do not repair in this gate |
| FOF taxonomy | future fund-type taxonomy gate | Keep current FOF data gap; do not classify QDII-FOF as pure FOF |
| Host/Agent/dayu | future architecture gate | Must defer; current deterministic path remains UI -> Service -> Fund |
| Real corpus identity proof | future corpus selection / repository evidence gate | Next gate may use only already accepted identity evidence; otherwise label as quasi-real |

## 10. Review Strategy

Plan review:

1. AgentMiMo review should challenge whether Path A actually advances上线 readiness, whether boundary controls are sufficient, and whether any hidden product integration is implied.
2. AgentGLM review should challenge input provenance, consumer specificity, success evidence, and whether the plan is concrete enough for implementation without redesign.

If either reviewer reports blocker or material ambiguity, patch this artifact and request targeted re-review before implementation.

Future implementation review:

1. Review only the evidence artifact and summarized scratch command output.
2. Confirm tracked file scope is limited to the evidence Markdown.
3. Confirm no source/test/README/product-flow/durable fixture/FQ gate/Host/Agent/dayu changes occurred.
4. Confirm input provenance is not overclaimed.
5. Confirm issue summary and pointers match current `report_quality_validation.py` behavior.
6. Confirm the evidence identifies a next owner category instead of merely dumping validator output.

## 11. Required Validation For Next Implementation

Required validation commands:

1. `git status --short`
   - Expected: only the future evidence Markdown is new/modified for that gate, aside from pre-existing unrelated untracked files.
2. `git diff --check`
   - Expected: clean.
3. `git ls-files | rg -n "report-quality-validator-real-bundle|input\\.jsonl|result\\.json"`
   - Expected: no tracked scratch JSONL/result files.
4. `test -f /tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`
   - Expected: scratch JSONL exists under `/tmp` if the run completed.
5. `test ! -e /Users/maomao/fund-agent/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`
   - Expected: no repo-local scratch JSONL at that path.
6. Boundary `rg` over the future evidence artifact:
   - Pattern: `FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|annual_report_pdf|extra_payload|dayu\\.host|dayu\\.engine|nav_data|quality_gate|extraction_score|fund-analysis|reports/scoring-runs|Service|CLI|renderer|fixture|baseline`
   - Expected: matches only in non-goal, boundary, validation, or residual sections; no integration claim.

Optional validation:

1. If the one-off command imports more than `report_quality_validation` / `report_evidence`, record why and confirm it does not fetch/parse documents.
2. If local ignored `reports/scoring-runs/` scratch output is used, prove it is ignored and not part of durable evidence.

No `ruff` or pytest run is required for the recommended next gate because it should not change Python source or tests. If implementation needs source/test changes, it has left Path A and must return to controller for a new gate decision.

## 12. Final Recommendation

Proceed with Path A: `docs/reviews` scoring-run evidence loop over one real or quasi-real bundle, with no product-flow integration and no durable baseline promotion.

Defer Path B until one or two evidence runs show repeated manual collection cost. Defer Path C until a boundary-reviewed Service/CLI design proves a concrete user or developer workflow needs it. Defer Path D/E/F by default because they either change current gates, promote unstable evidence, or require an independent architecture gate.
