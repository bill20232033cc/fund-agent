# Controller Judgment: MVP Gate 1 ChapterFactProvider typed projection

日期：2026-05-30
角色：Phaseflow / Gateflow controller
Gate：`MVP Gate 1: ChapterFactProvider typed projection`
分类：`heavy`

## Decision

`ACCEPTED_LOCALLY`

Gate 1 is accepted as a Fund-layer typed projection slice. The accepted implementation adds `chapter_fact_projection.v1` and the public entrypoints `project_chapter_facts()` / `ChapterFactProvider.project()` to project an in-memory `StructuredFundDataBundle` into chapter-scoped facts, evidence anchors, missing semantics, preferred_lens and ITEM_RULE projections.

This acceptance does not promote any golden fixture, does not change deterministic production report behavior, and does not authorize writer/auditor/orchestrator/CLI/dayu work.

## Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md` |
| Plan review MiMo | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-mimo-20260530.md` |
| Plan review GLM | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-glm-20260530.md` |
| Accepted plan commit | `bea10d7 gateflow: accept plan for mvp gate1 chapter facts` |
| Implementation evidence | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md` |
| Implementation review MiMo | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-mimo-20260530.md` |
| Implementation review GLM | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-glm-20260530.md` |

## Scope Accepted

- Added Fund-layer typed projection in `fund_agent/fund/chapter_facts.py`.
- Added deterministic tests in `tests/fund/test_chapter_facts.py`.
- Updated `docs/design.md`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/current-startup-packet.md` and `docs/implementation-control.md`.
- Recorded implementation evidence and two independent implementation reviews.

## Boundary Decision

- `ChapterFactProvider` typed projection is now a current Fund-layer code fact.
- `facet_recognizer` remains a future capability; this gate did not implement deterministic facet inference beyond fail-closed projection semantics.
- Full `FundToolService` remains future work; this gate only introduced a concrete provider façade.
- Exact facets remain empty unless structured evidence exists. Compatible labels are carried only as `non_asserted_facets` and must not drive ITEM_RULE.
- Gate 1 did not implement LLM chapter writing, LLM audit, write-audit-repair loops, chapter orchestration, final assembly, chapter 0 generation, CLI `--use-llm`, Host/Agent/dayu integration, release readiness or promotion.

## Validation

Implementation evidence and independent reviews record the following passing commands:

```text
uv run pytest tests/fund/test_chapter_facts.py -q
13 passed
```

```text
uv run pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/test_data_extractor.py -q
35 passed
```

```text
uv run ruff check .
All checks passed
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
972 passed
Total coverage: 91.64%
fund_agent/fund/chapter_facts.py: 97%
```

Controller closeout additionally requires `git diff --check` before final commit.

## Review Disposition

- MiMo implementation review verdict: `PASS`.
- GLM implementation review verdict: `PASS`.
- All findings are INFO only and non-blocking.
- Residual risks are accepted for Gate 1 because they are intentionally deferred to later consumer gates:
  - `ChapterFactEntry.value` remains broad as `object | None`.
  - Exact facet assertion remains fail-closed until structured subtype evidence exists.
  - `bond_risk_evidence` group anchors remain inside `value.anchors` rather than being expanded to chapter anchors.

## Next Entry Point

`MVP Gate 2: chapter_writer + chapter_auditor plan gate`

Gate 2 must consume Gate 1 typed projection as input truth and must define writer/auditor contracts before any implementation. It must not jump directly to orchestrator, CLI `--use-llm`, final assembly, promotion or dayu integration.

## External State

- No push.
- No PR.
- No merge.
- No release.
- No golden promotion.
- No golden fixture or golden-answer change.
- Unrelated untracked workspace artifacts remain outside this gate.
