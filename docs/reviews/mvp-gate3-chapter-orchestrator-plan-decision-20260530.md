# Controller Plan Decision: MVP Gate 3 chapter_orchestrator

日期：2026-05-30
角色：Phaseflow / Gateflow controller
Gate：`MVP Gate 3: chapter_orchestrator plan gate`
分类：`heavy`

## Decision

`PLAN_ACCEPTED_FOR_IMPLEMENTATION`

The updated Gate 3 plan is accepted as code-generation-ready. It scopes implementation to a Service-layer `chapter_orchestrator` and write-audit-repair policy that consumes accepted Gate 1 chapter facts and Gate 2 writer/auditor primitives. It does not authorize final assembler, chapter 0 assembly, chapter 7 final judgment assembly, CLI `--use-llm`, Host/Agent/dayu integration, source probing, release, promotion or golden/score/quality semantics changes.

## Accepted Plan Artifacts

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md` |
| Plan review MiMo | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-mimo-20260530.md` |
| Plan review DS | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-ds-20260530.md` |
| Plan re-review MiMo | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-rereview-mimo-20260530.md` |
| Plan re-review DS | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-rereview-ds-20260530.md` |

## Review Finding Decision

DS original review verdict was `BLOCKED`. Controller accepted all BLOCKING/HIGH/MEDIUM findings for plan fix before implementation. The fixed plan now includes:

- complete one-to-one `ChapterWriteStopReason` to `ChapterRunStopReason` mapping, including `llm_empty_response` and `llm_contract_violation`;
- consistent `ChapterOrchestrator` façade contract with injectable `fact_provider`;
- auditor LLM unavailable early stop before writer calls and before repair-loop retry;
- `_decide_repair()` signature and decision table, including `max_repair_attempts=0`;
- accepted conclusion extraction with `###` / `##` heading support, fallback to first non-empty lines and 500-character cap;
- exact `fund_agent/services/__init__.py` exports;
- patch-to-regenerate and partial-result behavior recorded as explicit residuals for future gates.

MiMo re-review verdict: `PASS`.

DS re-review verdict: `PASS`.

## Accepted Residuals

| Residual | Disposition | Owner |
|---|---|---|
| `patch` maps to best-effort `regenerate` with same writer input | Accepted for MVP; budget-bounded and must be tested | Future repair contract gate if needed |
| `partial` orchestration result is not a complete report | Gate 3 must not treat partial as complete; Gate 4 must decide reject/degrade/incomplete assembly behavior | Gate 4 plan |
| E2 evidence-vs-assertion source verification | Deferred; Gate 3 has no source access | Future Evidence Confirm gate |
| Chapter 5 cross-period evidence | No source probing in Gate 3 | Future cross-period data gate |
| No production LLM provider construction | Explicit client injection only | Gate 4/provider configuration gate |

## Implementation Boundary

Implementation may touch:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_chapter_orchestrator.py`
- `fund_agent/README.md`
- `tests/README.md`
- implementation evidence artifact under `docs/reviews/`

Implementation must not touch:

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- `AGENTS.md`
- deterministic `analyze/checklist` behavior
- CLI `--use-llm`
- Service code outside the explicit orchestrator/export surface unless the plan requires it and review accepts it
- Host/Agent/dayu packages or dependencies
- repository/PDF/cache/source helper/downloader/parser access
- golden fixtures / golden-answer / manifests
- score / snapshot / quality gate / FQ0-FQ6 / final judgment

Controller will update design/startup/control docs only after implementation review acceptance.

## Required Validation For Implementation

Because Gate 3 changes runtime Service code and tests, implementation must run:

```text
uv run ruff check .
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py -q
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

```text
git diff --check
```

## Next Action

Proceed to Gate 3 implementation handoff after this accepted plan checkpoint is committed locally. Implementation must stop if it needs to generate chapters 0/7, add final assembly, add CLI `--use-llm`, instantiate real LLM providers, read sources, introduce Host/Agent/dayu, or alter golden/score/quality semantics.
