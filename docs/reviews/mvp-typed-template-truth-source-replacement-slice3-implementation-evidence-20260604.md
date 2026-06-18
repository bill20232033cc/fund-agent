# MVP typed template truth-source replacement Slice 3 implementation evidence

## Worker self-check

- Current gate / role: `MVP typed template truth-source replacement gate` / implementation worker, Slice 3 only.
- Source of truth: `AGENTS.md`, accepted plan Slice 3 and plan-review fix addendum, plan controller judgment, Slice 1/2 controller judgments, current `contracts.py`, current `typed_contracts.py`, current typed tests, and `EvidenceRequirementId` guard in `evidence_availability.py`.
- Scope boundary: changed only `fund_agent/fund/template/typed_contracts.py`, `tests/fund/template/test_typed_contracts.py`, and this evidence artifact. `fund_agent/fund/template/__init__.py` did not require export changes.
- Stop conditions: no live probe, provider/runtime/renderer/Service/Host/Agent/golden/readiness/PR/push work performed.
- Evidence and validation: ran all user-requested commands and recorded exact outputs below.

## Changed files

- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md`

## Implementation summary

- Replaced typed manifest projection with raw canonical JSON projection from the same template document parser used by `contracts.py`.
- Removed code-authored typed truth helpers for `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, Ch3 predicate truth, missing-evidence behavior/reason, internal subcontract construction, predicate/context construction, and exact text mapping.
- Kept typed dataclasses, public API, closed-set Literal constants, public chapter id guard, Ch2 internal subcontract validation, Ch0/Ch7 dependency validation, audit_focus validation, Ch3 evidence predicate validation, and required output missing behavior/reason validation.
- Kept `source_manifest` as compatibility validation only: stale/different manifests raise `ValueError`; typed fields still come from raw template JSON.
- Added local import of `fund_agent.fund.evidence_availability._KNOWN_REQUIREMENT_IDS` inside a guard helper and validate evidence predicate requirement ids plus Ch2 internal subcontract requirement ids against that strict set.
- Added tests proving old code-authored truth symbols are absent, stale `source_manifest` fails closed, unknown template requirement id fails closed, raw JSON changes alter typed projection, malformed typed values fail closed, and current typed projection matches template JSON exact ids/text/missing behavior/audit_focus/dependencies/subcontracts/predicate.

## Validation outputs

### 1. typed contracts tests

Command:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py -q
```

Output:

```text
..............                                                           [100%]
14 passed in 0.90s
```

Exit code: `0`

### 2. untyped + typed template tests

Command:

```bash
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
```

Output:

```text
.............................................                            [100%]
45 passed in 1.05s
```

Exit code: `0`

### 3. ruff

Command:

```bash
uv run ruff check fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py
```

Output:

```text
All checks passed!
```

Exit code: `0`

### 4. scoped diff whitespace check

Command:

```bash
git diff --check -- fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py fund_agent/fund/template/__init__.py docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md
```

Output:

```text
```

Exit code: `0`

### 5. scoped status

Command:

```bash
git status --short -- fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py fund_agent/fund/template/__init__.py docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md
```

Output:

```text
 M fund_agent/fund/template/typed_contracts.py
 M tests/fund/template/test_typed_contracts.py
?? docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md
```

Exit code: `0`

## Non-goals preserved

- Did not modify `docs/fund-analysis-template-draft.md`, `contracts.py`, README, design/control/startup docs, renderer, Service, Host/Agent, provider/runtime, golden/readiness, PR/push state, or release state.
- Did not run live probes or commands requiring real provider credentials.
- Did not stage, commit, push, review, or create PR artifacts.

## Residual risks

- Slice 3 validates typed projection and strict requirement-id coupling only for current template tests. Broader typed consumer regression remains deferred to Slice 4 per accepted plan.
- The typed loader intentionally reuses `contracts.py` private parser helpers as allowed by this slice; if those private helper names change, this projection layer must be updated in the same template parser boundary.
