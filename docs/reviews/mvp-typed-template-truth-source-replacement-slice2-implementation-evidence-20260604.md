# MVP typed template truth-source replacement Slice 2 implementation evidence

## Worker self-check

- Role: implementation worker.
- Gate / slice: `MVP typed template truth-source replacement gate` / Slice 2: parse template doc into current untyped manifest.
- Source of truth read: `AGENTS.md`, accepted plan Slice 2 and plan-review addendum, plan controller judgment, Slice 1 controller judgment, current `docs/fund-analysis-template-draft.md`, current `contracts.py`, and current `test_contracts.py`.
- Scope boundary preserved: only `fund_agent/fund/template/contracts.py`, `tests/fund/template/test_contracts.py`, and this evidence artifact changed.
- Explicit non-goals preserved: no `typed_contracts.py`, README, design/control/startup, renderer, Service, Host/Agent, provider/runtime, golden/readiness, PR/push, or live probe changes.

## Changed files

- `fund_agent/fund/template/contracts.py`
- `tests/fund/template/test_contracts.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md`

## Implementation summary

- Replaced Python-authored `_CHAPTERS` manifest content with strict parsing of exactly one `TEMPLATE_CONTRACT_MANIFEST_JSON` block from `docs/fund-analysis-template-draft.md`.
- Used stdlib `json` parsing and projected `id` + `text` JSON entries into the existing untyped `TemplateContractManifest`, `ChapterContract`, and `TemplateLensRule` public API.
- Preserved `load_template_contract_manifest()`, `validate_template_contract_manifest()`, `get_chapter_contract()`, and `resolve_preferred_lens()` behavior.
- Added fail-closed validation for missing/duplicated/empty/malformed JSON blocks, unknown keys, public chapter id drift, chapter id drift, required field emptiness, stable id shape, item text shape, lens key/fund_type mismatch, priority closed set, missing-evidence behavior closed set, predicate context/status structure, and Ch2-only internal subcontracts.
- Added path-keyed `lru_cache` with private cache clear helper for tests.
- Added no-provider local validation path via `uv run python -m fund_agent.fund.template.contracts --validate-template-doc`; the test suite also calls the module entrypoint directly.

## Validation outputs

### 1. Pytest

Command:

```bash
uv run pytest tests/fund/template/test_contracts.py -q
```

Output:

```text
...............................                                          [100%]
31 passed in 0.45s
```

Exit code: `0`

### 2. Ruff

Command:

```bash
uv run ruff check fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py
```

Output:

```text
All checks passed!
```

Exit code: `0`

### 3. Git Diff Check

Command:

```bash
git diff --check -- fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
```

Output:

```text
```

Exit code: `0`

### 4. Git Status

Command:

```bash
git status --short -- fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
```

Output:

```text
 M fund_agent/fund/template/contracts.py
 M tests/fund/template/test_contracts.py
?? docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
```

Exit code: `0`

## Non-goals preserved

- Did not modify `fund_agent/fund/template/typed_contracts.py`.
- Did not modify `docs/fund-analysis-template-draft.md`.
- Did not modify README, design/control/startup docs, renderer, Service, Host/Agent, provider/runtime, golden/readiness, PR or push state.
- Did not run a live provider probe.

## Residual risks

- Slice 2 only replaces the current untyped manifest source. Typed manifest projection still remains a later slice responsibility, so `typed_contracts.py` still owns typed sidecar truth until Slice 3.
- The evidence artifact is untracked at completion by request; `git diff --check` does not inspect untracked file contents unless staged, but the required exact command was still run and recorded.
