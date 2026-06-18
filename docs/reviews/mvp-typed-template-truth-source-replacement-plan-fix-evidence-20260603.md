# MVP typed template truth-source replacement plan-fix evidence

## Worker self-check

- Gate: `MVP typed template truth-source replacement gate`.
- Classification: `heavy`.
- Role: planning fix worker only.
- Actions taken: read accepted plan, AgentDS review, AgentMiMo review, `contracts.py`, `typed_contracts.py`, `evidence_availability.py`, `chapter_contract_constraints.py`, and `template/__init__.py`; updated only the allowed plan artifact and this evidence artifact.
- Actions intentionally not taken: no `/gateflow` or `$gateflow`; no implementation; no source/template/test/control doc edits; no review loop; no commit/push/PR; no provider/runtime/live probe.

## Files changed

- `docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-plan-fix-evidence-20260603.md`

## Findings fixed

- DS B1 fixed: added concrete canonical JSON schema/shape with exact top-level keys, chapter shape, per-clause shape, `must_not_cover.applies_when`, `preferred_lens`, Ch2 internal subcontract, `required_output_items.when_evidence_missing`, and a representative JSON snippet covering one normal chapter, Ch3 predicate, and one Ch2 subcontract.
- DS B2 fixed: chose Option A. The canonical JSON carries stable `id` plus exact `text` for every authored clause/item. `contracts.py` projects untyped text from that JSON, and `typed_contracts.py` projects ids/text from the same parsed JSON. `_CURRENT_TEXT_MAPPING` is no longer authored truth.
- DS B3 fixed: kept `EvidenceRequirementId` as a strict `Literal` guard and added manifest-load cross-validation plus test expectations for requirement specs/dependencies.
- MiMo F1 fixed: added `chapter_contract_constraints.py` scope/no-change analysis, included `tests/fund/template/test_chapter_contract_constraints.py`, and added regression expectations.
- MiMo F2/F3 and DS H2 fixed: made the controller-facing plan decision explicit: single canonical JSON is authoritative; per-chapter `CHAPTER_CONTRACT_REF` blocks remain short and non-authoritative; no duplicated clause summaries. Added authorability mitigation and validation command guidance.
- DS M1 and MiMo F4 fixed: clarified `source_manifest` as compatibility-only validation input, production expectation `None`, and added negative stale manifest test requirement.
- DS M2 fixed: specified path-keyed cache strategy, private cache clear helper, tempfile-path testing, and avoidance of `importlib.reload()`.
- DS M3 and MiMo F6 fixed: documented that current `template/__init__.py` does not re-export `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, or removed helpers; keep public exports stable.
- MiMo F5 fixed: added referenced test-file precheck and confirmed `tests/fund/template/test_chapter_contract_constraints.py` exists.
- DS H3 fixed through B1 schema: documented exact `preferred_lens` JSON object shape, lens key expectations, and priority closed set.

## Findings not fixed

- DS H1 is partially mitigated, not eliminated: the plan still allows Slice 1 template-doc work before parser code, but now requires manual JSON parse/equality evidence if Slice 1 is reviewed separately before Slice 2 parser exists. Full elimination would require resequencing implementation slices, which was not necessary for plan-fix-only scope.
- DS M4 remains a residual tooling risk: large JSON in a Markdown HTML comment can be corrupted by Markdown tooling. The plan now mitigates this with fail-closed parser tests and no-provider validation, but does not replace the canonical JSON approach.

## Validation commands

Safe commands to run for this plan-fix-only handoff:

```bash
git diff --check -- docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md docs/reviews/mvp-typed-template-truth-source-replacement-plan-fix-evidence-20260603.md
rg -n "Canonical JSON Schema|Text/id bridging|EvidenceRequirementId|chapter_contract_constraints|source_manifest|CHAPTER_CONTRACT_REF|cache|__init__" docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md
```

Additional read-only/context command already used:

```bash
rg --files tests | rg 'test_contracts.py|test_typed_contracts.py|test_chapter_contract_constraints.py|test_evidence_availability.py|test_chapter_writer.py|test_chapter_auditor.py|test_chapter_orchestrator.py|test_execution_contract.py|test_fund_analysis_service_llm.py|test_cli.py|test_renderer.py|test_audit_programmatic.py'
```

## Non-goals preserved

- No implementation, review, commit, push, PR, or controller action.
- No edits to `docs/fund-analysis-template-draft.md`, source files, tests, control docs, startup packet, README files, or template source.
- No Agent runtime, Host runtime, ToolRegistry, ToolTrace, provider runtime/config/default/budget, score/golden/readiness, Ch2 public split, multi-year annual evidence, renderer output, deterministic analyze/checklist, or FQ quality gate semantic change.
- No provider/runtime/live probe commands.

## Residual risks

- The canonical JSON block remains large and less ergonomic to edit by hand; the plan accepts this cost to remove code-authored parallel truth and requires validation tooling.
- `EvidenceRequirementId` coupling remains strict by design; template/evidence drift will fail closed and requires a separate evidence-availability contract gate to change.
- Slice sequencing still needs controller/implementation discipline if the template doc is edited before parser code exists; the plan now requires explicit evidence for that intermediate state.
