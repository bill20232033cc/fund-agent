# Atomic Source Fact Store / Composite Analysis View Split S6 Implementation Evidence

## Gate

- Gate: Atomic Source Fact Store / Composite Analysis View Split S6 Regression / Docs / Control Sync Gate
- Role: S6 implementation worker
- Branch: `evidence-confirm-productionization`
- Verdict: `S6_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

## Scope

S6 is a no-live regression/docs truth sync gate. It does not add product behavior.

Allowed scope used:

- `docs/design.md`
- `fund_agent/fund/README.md`
- this implementation artifact
- control/startup sync, if needed after artifact creation

Explicit non-goals preserved:

- No production code or test code changes.
- No Evidence Confirm V2 / ECQ / quality-gate semantic changes.
- No report body, checklist, provider/LLM, product CLI, renderer, Service, UI, Host, or Agent runtime changes.
- No `FundDisclosureDocument` default-on behavior change.
- No live/PDF/repository/source-helper/parser/provider/LLM/product CLI command.
- No PR, remote state, tag, release, merge, stage, commit, push, or readiness transition.

## Preflight

- `git branch --show-current` -> `evidence-confirm-productionization`
- `git status --short` showed existing unrelated dirty/untracked docs/reviews/docs/scripts residue and no conflict markers.
- S5/control checkpoint confirmed by local log: `29fbb79 gateflow: accept atomic source fact split s5`; `a2e4255 control: advance atomic source fact split to s6`.

## Changes

### `docs/design.md`

- Reclassified Atomic Source Fact Store / Composite Analysis View Split from future/stale wording to current implemented fact.
- States current structured extraction truth surface is Fund Processor/Extractor atomic source facts:
  - `FundProcessorResult.source_facts` is the Processor atomic fact store.
  - `StructuredFundDataBundle.source_facts` mirrors that store.
  - S1-S5 cover source fact store contract, default parsed annual child atomic emission, explicit FDD source-truth child atomic emission, ChapterFactProvider bridge, and Evidence Confirm bridge-aware material resolution.
- States composite fields are writing/analysis compatibility or derived analysis views, not source-truth extraction objects.
- Adds explicit non-goal boundary for Evidence Confirm V2/ECQ/quality gate, report body, checklist, provider/LLM, product CLI, FDD default-on, live/PDF, tag, release, and readiness.

### `fund_agent/fund/README.md`

- Updated Fund package current implementation section and internal module guide for `source_facts.py`.
- Replaced S1/S2B stale wording with S1-S5 current fact wording.
- States composite field-family values remain compatibility/derived views while atomic facts are the truth surface.
- Preserves no-fabrication rule: derived views must come from dependency atomic facts and must not infer child provenance from composite dict shape.

## Validation

### Required no-live validation

Command:

```bash
uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_atomic.py tests/fund/processors/test_fund_disclosure_processor_atomic.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q
```

Result: failed before collection because the required local paths do not exist:

- `tests/fund/processors/test_active_annual_atomic.py`
- `tests/fund/processors/test_fund_disclosure_processor_atomic.py`

Observed pytest error:

```text
ERROR: file or directory not found: tests/fund/processors/test_active_annual_atomic.py
no tests ran in 0.00s
```

Supplemental equivalent no-live atomic/source fact validation:

```bash
uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q
```

Result: `243 passed in 0.54s`.

Command:

```bash
uv run pytest tests/fund/test_data_extractor.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q
```

Result: `180 passed in 1.20s`.

### Targeted stale wording checks

Command:

```bash
rg -n '已接受的未来设计：Atomic|当前实现尚未落地 atomic|Processor-level `AtomicSourceFact` emission 仍属于 S2B|processor-level `AtomicSourceFact` emission 仍归 S2B|后续结构化提取应把 extraction truth' docs/design.md fund_agent/fund/README.md
```

Result: no matches.

## Residual Risks

| Residual | Classification | Owner / Next gate |
|---|---|---|
| Required first pytest command references two non-existent local test files, so that exact command cannot pass in this checkout. | requiring explicit controller/code-review decision | S6 code review/controller should decide whether the command list is stale or whether missing test files must be restored/renamed. Supplemental existing atomic/source fact processor coverage passed. |
| S6 only syncs documentation truth and runs no-live regression; it does not prove live/PDF, product CLI, provider-backed semantic default, report-body/checklist Evidence Confirm, tag, release, or readiness. | assigned to later work unit | Existing release/readiness and live/PDF gates remain owners. |
| Existing unrelated dirty/untracked docs/reviews/docs/scripts residue remains untouched. | tracked by existing controller residue ownership | Controller/artifact disposition gates remain owners. |
| Real-report correctness, full field correctness, golden/readiness, and release proof are not established by S1-S6 no-live docs sync. | assigned to later work unit | Future evidence/readiness gates. |

## Completion Status

S6 implementation artifacts and docs truth sync are ready for code review, with the exact required first pytest command blocked by stale/missing test paths and supplemental existing no-live atomic/source fact coverage passing.

Final token: `S6_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`
