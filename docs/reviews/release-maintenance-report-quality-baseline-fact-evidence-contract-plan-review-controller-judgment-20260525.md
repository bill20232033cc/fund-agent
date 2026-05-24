# Release Maintenance Report-Quality Baseline / Fact-Evidence Contract Plan Review Controller Judgment

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract candidate selection / plan-review`
> Controller status: accepted locally; next gate is `report-quality-baseline S0 corpus-selection evidence`

## Step Self-Check

- Current role: controller. This artifact records plan review裁决 and gate bookkeeping only.
- Source of truth: `AGENTS.md`, `docs/design.md` current §5.4 to §5.4.3, `docs/implementation-control.md` Startup Packet / current gate / next entry point, and accepted artifacts from the chapter-audit report pipeline and methodology coverage matrix gates.
- Reviewed plan: `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md`.
- Independent reviews: `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-mimo-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-ds-20260525.md`.
- Scope boundary: no source code, tests, renderer, quality gate, Host/Agent package, Dayu runtime, report output, golden answer, push, PR, or external state change.

## Verdict

**ACCEPTED FOR NEXT GATE.**

The plan is executable as a design plan for report-quality baseline / Fact-Evidence contract candidate selection. Both independent reviews returned `PASS_WITH_FINDINGS` with no blocking finding. The plan preserves the current v0 deterministic 8-chapter renderer, treats report-quality scoring as observational, keeps annual-report access behind `FundDocumentRepository`, and explicitly gates any future Host work on `dayu.host` and Agent execution work on `dayu.engine`.

Because `AgentGLM` was not available in the tmux pane discovery for this session, the second independent review was routed to `AgentDS`, which is review/re-review eligible under `init-agents`.

## Accepted Plan Scope

The accepted next implementation sequence is:

1. `report-quality-baseline S0 corpus-selection evidence`
   - Produce a reviewed candidate table with fund type slot, fund code, report year, repository verification status, review state, source failure category, and ignored run path.
   - Do not change renderer, quality gate, source code behavior, Host/Agent packages, or Dayu dependencies.
2. `report-quality-baseline S1 score-schema fixture draft`
   - Design the scoring record/schema from observed S0 evidence and one reviewed dry-run scoring artifact under ignored `reports/scoring-runs/`.
   - Do not promote long-lived fixtures without a separate curated-fixture gate.
3. `fact-evidence-contract S2 bundle candidate`
   - Define any typed contract in code only after S0/S1 pass their own plan/review gates.
   - Any code gate must include tests and README updates according to touched package boundaries.

## Controller Decisions On Open Questions

| Question | Decision | Reason |
|---|---|---|
| FOF in S0 | S0 should attempt FOF, but must not block if no repository-verified FOF annual report is available. Missing FOF must be recorded as a `data_gap`; FOF becomes required by the second pass / S1 expansion. | A forced unverified FOF substitute would violate the FundDocumentRepository identity boundary and weaken baseline evidence quality. |
| Weighted total | First implementation remains issue-based. `N/A` dimensions are excluded from any denominator; a chapter with all dimensions `N/A` is `skipped`, not `passing`. No weighted total is accepted until issue localization proves stable. | The design goal is root-cause selection between data/extraction and template/writing work, not a premature aggregate score. |
| `fact_prefill_reviewed` artifact | S0 uses a Markdown evidence table under `docs/reviews/` as the human-review artifact. JSON fixture promotion is deferred to a separate curated-fixture gate after S0/S1 evidence exists. | Human-readable review evidence is sufficient for corpus selection; durable machine fixtures need stronger acceptance criteria. |

## Finding Disposition

| Finding | Source | Disposition | Owner / Gate |
|---|---|---|---|
| Manual review state machine lacks transition triggers | MiMo F-1 | Accepted. S0 must define transition trigger, actor, and minimum evidence for each state before any code implementation. | S0 corpus-selection evidence |
| FOF ambiguity | MiMo F-2 | Resolved by controller decision above: attempt in S0, record gap if unavailable, require by second pass. | S0 / S1 |
| `N/A` scoring semantics | MiMo F-3 | Accepted. First implementation excludes `N/A` from denominators and treats all-`N/A` chapters as skipped. | S1 score schema |
| Tie-breaker citation | MiMo F-4 | Accepted as documentation polish for the next plan/update; non-blocking. | Next plan update |
| `source_strength` distinction | MiMo F-5 | Accepted as S2 wording constraint: distinguish third-party comparison from derived internal calculation. | S2 bundle candidate |
| Top-level bundle shape design-vs-implementation boundary | MiMo F-6 | Accepted. S2 must state the shape is a design-level contract before concrete dataclass work. | S2 bundle candidate |
| `source_boundary` value domain undefined | DS Finding 1 | Accepted. S1/S2 must define a literal/enum value set before implementation; suggested starting values are `repository_derived`, `derived_calculation`, `external_official`, and `manual_review`. | S1/S2 |
| Anchor naming consistency | DS Finding 2 | Accepted. S1/S2 should normalize the anchor id prefix and distinguish one-to-one score issues from one-to-many fact support. | S1/S2 |
| Bundle-level vs fact-level `review_status` | DS Finding 3 | Accepted. S2 must define bundle status as derived from contained facts, anchors, calculations, and gaps, or explicitly justify independent status. | S2 |
| Relationship to `StructuredFundDataBundle` | DS Finding 4 | Accepted. S2 must decide whether `ReportEvidenceBundle` wraps, evolves from, or coexists with current `StructuredFundDataBundle`; default preference is consuming current structured bundle outputs rather than creating a parallel extraction path. | S2 |
| `fq_gate_status` citation | DS Finding 5 | Accepted as documentation polish. Future quality context wording should cite the existing quality gate final judgment contract / design semantics for `pass`, `warn`, `block`, `not_run`. | S1/S2 |

## Boundary Confirmation

- The plan does not modify current renderer behavior or the v0 8-chapter report structure.
- The plan does not modify current FQ0-FQ6 quality gate behavior.
- The plan does not implement LLM audit, Evidence Confirm, chapter repair, patch/regenerate, or a chapter writer.
- The plan does not create `fund_agent/host` or `fund_agent/agent`.
- Future Host work remains an explicit separate gate and must use `dayu.host`.
- Future Agent execution/tool-loop work remains an explicit separate gate and must use `dayu.engine`.
- Business parameters must remain explicit typed fields and must not be placed in `extra_payload` or `extra_payloads`.
- Annual-report access for corpus verification and future evidence bundles must stay behind `FundDocumentRepository` or public Fund APIs that themselves use it.

## Residual Risks

- The first baseline corpus is intentionally small and must not be treated as product-wide quality proof.
- Manual review can become the bottleneck; S0 must make transition evidence and reviewer responsibility explicit.
- Scoring may show source/extraction defects before writing quality can be improved; the accepted plan intentionally prioritizes fact correctness over prose polishing.
- Future LLM audit / repair may require Host/Agent runtime, but remains blocked until a separate gate with `dayu.host` / `dayu.engine` design.

## Validation

```text
rg -n "report-quality baseline|Fact / Evidence|ReportEvidenceBundle|FundDocumentRepository|extra_payload|dayu.host|dayu.engine|CHAPTER_CONTRACT|0-10|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-mimo-20260525.md docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-ds-20260525.md docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-review-controller-judgment-20260525.md
git diff --check
```

Result: passed.

## Next Entry Point

`report-quality-baseline S0 corpus-selection evidence`
