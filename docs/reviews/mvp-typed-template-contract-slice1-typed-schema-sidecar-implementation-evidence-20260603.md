# MVP typed template contract Slice 1 typed schema sidecar implementation evidence

## Worker Self-Check

- Role: AgentCodex implementation worker only; not controller.
- Gate: `MVP typed template contract Slice 1 typed schema sidecar implementation gate`.
- Classification: `heavy`.
- Scope implemented: additive Fund-layer typed contract schema sidecar only.
- Actions intentionally not taken: no commit, no push, no PR, no live provider probe, no provider/runtime/default/budget/endpoint change, no Agent runtime/tool-loop, no score/golden/readiness/promotion change, no deterministic fallback or stdout partial-report behavior change.
- Truth-source edits intentionally not taken: no edit to `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, or `docs/fund-analysis-template-draft.md`.

## Touched Files

- `fund_agent/fund/template/typed_contracts.py`
- `fund_agent/fund/template/__init__.py`
- `tests/fund/template/test_typed_contracts.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-implementation-evidence-20260603.md`

## Behavior Summary

- Added typed schema/version literal `typed_chapter_contract.v1`.
- Added typed schema objects: `TypedChapterContract`, `TypedTemplateContractManifest`, `MustAnswerClause`, `MustNotCoverClause`, `EvidencePredicate`, `RequiredOutputItem`, `MissingEvidenceBehavior`, `TemplateLensRule`, `ChapterInternalSubcontract`, and `AuditFocusLiteral`.
- Added `load_typed_template_contract_manifest()` projection from current `contracts.py` manifest. It preserves public chapter ids exactly as `0-7` and uses reviewed exact string mapping for current `must_answer`, `must_not_cover`, and `required_output_items`; text drift fails closed.
- Added Ch2 internal subcontracts only under `chapter_id=2`: `performance`, `attribution`, and `cost`. They carry no public chapter id.
- Added Ch0 typed dependency `consumes_chapter_conclusions=(7,)` and `independent_action_source=False`.
- Added `audit_focus` as semantic-only data with closed literals. `AUDIT_FOCUS_IS_SEMANTIC_ONLY=True`; no code path uses it to disable programmatic blockers.
- Added fail-closed validation for schema version, exact public ids, duplicate ids, unknown dependencies, Ch0 consuming Ch7, Ch2 internal subcontract public ids, non-Ch2 internal subcontracts, required output item id uniqueness, stable clause/id prefixes, evidence predicate closed statuses, allowed contexts, preferred lens shape, and closed `audit_focus`.
- Added package-level additive exports for typed sidecar APIs without replacing existing `load_template_contract_manifest()` or existing `TemplateLensRule`.
- Updated Fund and tests README with current implemented sidecar facts only.

## Validation

Command:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py
```

Output:

```text
collected 18 items
tests/fund/template/test_typed_contracts.py ........                     [ 44%]
tests/fund/template/test_contracts.py ..........                         [100%]
18 passed in 0.49s
```

Command:

```bash
uv run ruff check fund_agent/fund/template tests/fund/template
```

Output:

```text
All checks passed!
```

Command:

```bash
git diff --check -- fund_agent/fund/template/typed_contracts.py fund_agent/fund/template/__init__.py tests/fund/template/test_typed_contracts.py fund_agent/fund/README.md tests/README.md
```

Output: no output; exit code `0`.

## Non-Goals Preserved

- Current `contracts.py` manifest remains the source being projected; it was not rewritten.
- Current deterministic renderer/auditor behavior remains unchanged.
- Current deterministic `fund-analysis analyze/checklist` defaults remain unchanged.
- Current `--use-llm` fail-closed behavior remains unchanged.
- No provider, endpoint, timeout, runtime budget, model, env config, or live probe behavior changed.
- No Agent runtime, ToolRegistry, ToolTrace, tool-loop, Host boundary, multi-year evidence runtime, score-loop, golden/readiness, quality gate, final judgment, or promotion state changed.
- No direct document/PDF/cache/source-helper access was added.
- No business parameters were introduced through `extra_payload`, `**kwargs`, or untyped payload bags.

## Residual Risks

- The exact mapping table is intentionally verbose because Slice 1 requires reviewed explicit mapping and forbids fuzzy matching. Future template text changes must update the mapping under review or the typed loader will fail closed.
- `EvidencePredicate`, `MissingEvidenceBehavior`, and `audit_focus` are schema/data only in this slice. They do not enforce evidence availability, missing/degrade behavior, or bounded semantic audit routing until later accepted slices.
- Ch3 style evidence predicate is represented as data for the accepted future path; current C2 phrase extraction and programmatic auditor behavior are not changed in this slice.
