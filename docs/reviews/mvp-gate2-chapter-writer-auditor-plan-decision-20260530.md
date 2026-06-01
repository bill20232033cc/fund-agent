# Controller Plan Decision: MVP Gate 2 chapter_writer + chapter_auditor

日期：2026-05-30
角色：Phaseflow / Gateflow controller
Gate：`MVP Gate 2: chapter_writer + chapter_auditor plan gate`
分类：`heavy`

## Decision

`PLAN_ACCEPTED_FOR_IMPLEMENTATION`

The updated Gate 2 plan is accepted as code-generation-ready. It keeps the work strictly scoped to Fund-layer single-chapter writer/auditor primitives that consume Gate 1 `ChapterFactProjection` / `ChapterFactInput`. It does not authorize orchestrator, repair loop execution, final assembler, chapter 0 generation, CLI `--use-llm`, Host/Agent/dayu runtime, promotion, release, source access, score/snapshot/quality-gate changes, or golden fixture changes.

## Accepted Plan Artifacts

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md` |
| Plan review MiMo | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-mimo-20260530.md` |
| Plan review GLM | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-glm-20260530.md` |
| Plan review DS | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-ds-20260530.md` |
| Plan re-review MiMo | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-rereview-mimo-20260530.md` |
| Plan re-review DS | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-rereview-ds-20260530.md` |

## Review Finding Decision

All blocking-risk findings were accepted for plan fix before implementation. The plan now freezes:

- writer anchor marker parsing: `<!-- anchor:<anchor_id> -->`;
- writer missing marker parsing: `<!-- missing:<reason> -->`;
- `max_output_chars` as hard post-check without truncation;
- LLM audit line format: `SEVERITY|LOCATION|MESSAGE`;
- LLM audit parse-failure and zero-issue pass semantics;
- `prompt_only` stop reason;
- chapter 5 cross-period missing detection;
- `evidence_missing` critical-judgment algorithm;
- `declared_missing_reasons` extraction semantics;
- `repair_hint` aggregation priority;
- `non_asserted_facets` asserted-fact audit;
- explicit E2 deferral to a future Evidence Confirm gate;
- `bond_risk_evidence` internal-anchor blocked messaging;
- controller-only ownership of design/startup/control doc closeout updates.

MiMo re-review verdict: `PASS`.

DS re-review verdict: `PASS`.

GLM original review verdict: `PASS_WITH_NON_BLOCKING`; its findings are covered by the updated plan and MiMo/DS re-review.

## Accepted Residuals

| Residual | Disposition | Owner |
|---|---|---|
| `ChapterFactEntry.value: object | None` serialization quality | Accept for implementation; implementation evidence must record the conservative serialization strategy | Gate 2 implementation |
| Chapter 5 phrase matching may over-block `风格稳定性` style wording | Accept because fail-closed; implementation may narrow with tests if needed | Gate 2 implementation |
| `_fact_supports_critical_judgment` numeric-leaf rule may over-block | Accept because fail-closed; implementation evidence must record the chosen field/number strategy | Gate 2 implementation |
| LLM output format reliance | Accept only with deterministic fake-client tests; no fake pass allowed | Gate 2 implementation |
| `bond_risk_evidence` group anchor expansion | Deferred; Gate 2 must block internal-anchor use unless future conversion helper exists | Future evidence / Gate 3+ |
| E2 evidence-vs-assertion source verification | Deferred; requires source re-check outside Gate 2 no-source boundary | Future Evidence Confirm gate |

## Implementation Handoff Boundary

Implementation may touch:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `fund_agent/fund/__init__.py` only if package-level export is needed
- `fund_agent/fund/README.md`
- `tests/README.md`
- implementation evidence artifact under `docs/reviews/`

Implementation must not touch:

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- `AGENTS.md`
- golden fixtures / golden-answer / manifests
- score / snapshot / quality gate / FQ0-FQ6 / final judgment
- Service / UI / Host / Agent/dayu runtime
- CLI `--use-llm`
- repository / PDF / cache / source helper / downloader / parser access

Controller will update design/startup/control docs only after implementation review acceptance.

## Required Validation For Implementation

Because Gate 2 changes runtime code and tests, implementation must run:

```text
uv run ruff check .
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Implementation should also run targeted adjacent tests if package exports or template/audit integration are touched.

## Next Action

Proceed to Gate 2 implementation handoff after this accepted plan checkpoint is committed locally. The implementation worker must follow the accepted plan and this controller decision, and must stop if it needs to change scope, introduce Service orchestration, call real LLM provider SDKs directly, add dayu/Host/Agent runtime, read sources, or alter golden/score/quality semantics.
