# Scoped Accepted Checkpoint Plan

Date: 2026-06-15

Gate: `Scoped Accepted Checkpoint Planning Gate`

Role: controller

Readiness state: `NOT_READY`

## 1. Scope

This planning artifact defines exact local checkpoint slices for the current dirty workspace.

This gate does not stage, commit, push, create PR, delete, move, archive or ignore files.

Input disposition:

- `docs/reviews/workspace-scope-reconciliation-artifact-disposition-20260615.md`

Current control truth:

- Current active gate: `Docling Baseline Qualification Acquisition Status Planning Gate`
- Current gate type: planning-only
- Current source policy: EID single-source; no fallback re-entry
- Release/readiness: `NOT_READY`

## 2. Planning Decision

Direct PR remains blocked.

Local checkpointing is feasible only if split into narrow accepted slices. The safe checkpoint order is:

1. `evidence-chain-route-artifacts`
2. `control-route-sync`
3. `docling-candidate-internals`
4. `design-doc-sync`
5. `docs-user-surface-sync`
6. `rules-truth-sync` only after separate rules review

Rationale:

- Control docs reference route artifacts; route artifacts should be checkpointed before or with control sync.
- Source-like Docling candidate internals already have an accepted implementation judgment and should not be mixed with control-only sync.
- `docs/design.md` changes are design truth and need their own review/sync checkpoint.
- `AGENTS.md` is rules truth and has a large rewrite; it must not be bundled into the Docling/control checkpoint.

## 3. Checkpoint Slice 1: Evidence-chain Route Artifacts

Suggested commit message:

```text
gateflow: accept xbrl docling route evidence artifacts
```

Stage list:

```text
docs/reviews/bounded-same-report-eid-html-render-discovery-controller-judgment-20260615.md
docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-20260615.md
docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-review-ds-20260615.md
docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-review-mimo-20260615.md
docs/reviews/csrc-eid-xbrl-html-evidence-closeout-control-sync-controller-judgment-20260614.md
docs/reviews/csrc-eid-xbrl-html-post-gate-artifact-disposition-20260614.md
docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md
docs/reviews/docling-baseline-qualification-plan-20260615.md
docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md
docs/reviews/docling-baseline-qualification-plan-rereview-ds-20260615.md
docs/reviews/docling-baseline-qualification-plan-rereview-mimo-20260615.md
docs/reviews/docling-baseline-qualification-plan-review-ds-20260615.md
docs/reviews/docling-baseline-qualification-plan-review-mimo-20260615.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-review-ds-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-review-mimo-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-controller-judgment-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-rereview-ds-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-rereview-mimo-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-review-ds-20260614.md
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-review-mimo-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-design-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-design-controller-judgment-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-design-review-ds-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-design-review-mimo-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-schema-plan-rereview-mimo-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-schema-plan-review-ds-20260614.md
docs/reviews/funddisclosuredocument-candidate-source-schema-plan-review-mimo-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-control-sync-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-plan-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-plan-controller-judgment-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-plan-rereview-ds-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-plan-rereview-mimo-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-plan-review-ds-20260614.md
docs/reviews/same-report-document-representation-quality-comparison-plan-review-mimo-20260614.md
docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-20260615.md
docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-controller-judgment-20260615.md
docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-review-ds-20260615.md
docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-review-mimo-20260615.md
docs/reviews/same-report-full-annual-representation-json-evidence-20260615.md
docs/reviews/same-report-full-annual-representation-json-evidence-controller-judgment-20260615.md
docs/reviews/same-report-full-annual-representation-json-evidence-review-ds-20260615.md
docs/reviews/same-report-full-annual-representation-json-evidence-review-mimo-20260615.md
docs/reviews/workspace-artifact-disposition-before-same-report-comparison-20260614.md
docs/reviews/workspace-scope-reconciliation-artifact-disposition-20260615.md
docs/reviews/scoped-accepted-checkpoint-plan-20260615.md
```

Validation before commit:

```text
git diff --check
git status --short
```

Stop conditions:

- any listed artifact missing;
- artifact body claims readiness/source truth/raw XML/field correctness beyond accepted judgments;
- user decides not to checkpoint historical route artifacts.

## 4. Checkpoint Slice 2: Control-route Sync

Suggested commit message:

```text
gateflow: sync control docs for docling baseline qualification
```

Stage list:

```text
docs/current-startup-packet.md
docs/implementation-control.md
```

Validation before commit:

```text
git diff --check
rg -n "Docling Baseline Qualification Acquisition Status Planning Gate|NOT_READY|Eastmoney|CNINFO|fallback" docs/current-startup-packet.md docs/implementation-control.md
git status --short
```

Acceptance checks:

- current gate is `Docling Baseline Qualification Acquisition Status Planning Gate`;
- release/readiness remains `NOT_READY`;
- EID single-source/no-fallback remains preserved;
- no live/provider/LLM/readiness/release/PR authorization is added.

Stop conditions:

- control docs reference route artifacts not included in Slice 1 or already tracked;
- control docs claim Docling baseline, production parser replacement, source truth, field correctness or raw XML availability.

## 5. Checkpoint Slice 3: Docling Candidate Internals

Suggested commit message:

```text
gateflow: accept docling candidate document internals
```

Stage list:

```text
fund_agent/fund/documents/candidates/__init__.py
fund_agent/fund/documents/candidates/failures.py
fund_agent/fund/documents/candidates/locators.py
fund_agent/fund/documents/candidates/models.py
fund_agent/fund/documents/candidates/normalization.py
tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json
tests/fund/documents/test_docling_candidate_models.py
tests/fund/documents/test_docling_failure_mapping.py
tests/fund/documents/test_docling_locators.py
tests/fund/documents/test_docling_no_consumption_guards.py
tests/fund/documents/test_docling_normalization.py
tests/fund/documents/test_repository.py
docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-ds-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-mimo-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-controller-judgment-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-review-ds-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-review-mimo-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-review-ds-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-review-mimo-20260615.md
docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-controller-judgment-20260615.md
```

Validation before commit:

```text
uv run pytest tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_normalization.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_failure_mapping.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run pytest tests/fund/documents/test_repository.py -q
uv run ruff check fund_agent/fund/documents tests/fund/documents
git diff --check
```

Acceptance checks:

- candidate internals are not exported as production public API;
- `FundDocumentRepository.load_annual_report()` behavior remains unchanged;
- `EvidenceAnchor` schema and `EvidenceSourceKind` remain unchanged;
- no Service/UI/Host/renderer/quality gate direct Docling/parser consumption.

Stop conditions:

- tests fail;
- candidate internals alter production repository behavior;
- implementation artifacts are missing or conflict with current code.

## 6. Checkpoint Slice 4: Design-doc Sync

Suggested commit message:

```text
gateflow: sync design truth for document representation route
```

Stage list:

```text
docs/design.md
```

Required precondition:

- create or identify a design-truth-sync controller judgment that accepts the exact `docs/design.md` diff.

Validation before commit:

```text
git diff --check
rg -n "当前 PDF parser 边界与 Docling 候选|CSRC EID XBRL HTML render artifact|候选/研究输入|NOT_READY|FundDocumentRepository" docs/design.md
```

Stop conditions:

- `docs/design.md` writes future Docling/XBRL candidate as current production code fact;
- design claims raw XML direct download, field correctness, taxonomy compatibility, parser replacement or readiness;
- no controller judgment exists for this design truth sync.

## 7. Checkpoint Slice 5: README User-surface Sync

Suggested commit message:

```text
docs: clarify annual-period llm route boundary
```

Stage list:

```text
README.md
```

Required precondition:

- Slice 4 design-doc sync is accepted, or README diff is tied to an accepted implementation/control checkpoint.

Validation before commit:

```text
git diff --check
rg -n "analyze-annual-period|--use-llm|annual-period LLM route design" README.md
```

Stop conditions:

- README describes future annual-period LLM route as current product capability;
- README contradicts current control truth.

## 8. Deferred Slice: AGENTS Rules-truth Sync

Do not stage in the current checkpoint flow:

```text
AGENTS.md
```

Reason:

- current diff is a large rules-truth rewrite/recompression;
- it changes execution commands, structure, guardrails and module-boundary wording;
- it needs separate rules-truth review before any checkpoint.

Recommended separate gate:

```text
AGENTS Rules-truth Sync Review Gate
```

Minimum review focus:

- no loss of hard constraints from current user-provided AGENTS text;
- no accidental weakening of EID single-source/no-fallback;
- no weakening of `FundDocumentRepository` boundary;
- no readiness/release/PR authorization;
- no conflict with `docs/design.md` and `docs/implementation-control.md`.

## 9. Explicitly Excluded From All Checkpoints

Do not stage without a later dedicated gate:

```text
.mimocode/
docs/audit/
docs/code-wiki-and-audit-report-20260613.md
docs/dayu-agent-architect-gap-analysis-20260613.md
docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md
docs/dayu-fund-agent-mvp-gap-discussion-summary-20260613.md
docs/learning-roadmap.md
docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md
docs/next-development-phaseflow.md
docs/tmux-agent-memory-store.md
reports/
reviews/
scripts/claude_mimo_simple.py
scripts/review-artifact.sh
基金年报/
定性分析模板.md
```

Also do not stage broad historical `docs/reviews/*` files outside the explicit slice lists above.

## 10. PR Decision

Do not open PR after this planning gate.

Draft PR becomes reasonable only after:

1. Slices 1-3 are committed cleanly, or explicitly rejected/deferred with clean residual state.
2. `docs/design.md`, `README.md` and `AGENTS.md` are either checkpointed through their own gates or reverted/deferred by explicit user instruction.
3. `git status --short` has no unrelated source-like/test-like artifacts.
4. Release/readiness remains clearly marked `NOT_READY`.

Possible future PR title:

```text
Draft PR: Docling candidate document representation route checkpoint
```

Non-goals for the PR:

- no release-ready claim;
- no production parser replacement;
- no raw XML/field correctness/taxonomy claim;
- no source policy or fallback expansion;
- no live/provider/LLM readiness claim.

## 11. Final Verdict

`VERDICT: READY_FOR_SCOPED_LOCAL_CHECKPOINTS_NOT_READY_NO_PR`
