# MVP typed template contract Slice 8 docs/control sync implementation evidence

## Worker Self-Check

- Role: AgentCodex documentation/control sync implementation worker only; not controller/reviewer.
- Gate: `MVP typed template contract Slice 8 Documentation And Control Sync After Accepted Implementation gate`.
- Classification: heavy.
- Branch/worktree: existing unrelated untracked files were left untouched.
- Scope: documentation/control truth sync only for accepted typed template contract Slice 1-7 implementation facts.

## Touched Files

- `fund_agent/fund/README.md`
- `fund_agent/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-typed-template-contract-slice8-docs-control-sync-implementation-evidence-20260603.md`

No code, tests, provider config, runtime defaults, fixtures, snapshots, quality gate, score, golden/readiness state, `docs/fund-analysis-template-draft.md`, Host runtime, Agent runtime or dayu dependency was modified.

## Summary

- Synced Fund package docs to describe current additive typed CHAPTER_CONTRACT sidecar, same-source `EvidenceAvailability`, `RequiredOutputItem.when_evidence_missing` writer behavior, Ch3 evidence-conditional programmatic `must_not_cover`, bounded semantic-only `audit_focus`, and explicit non-goals.
- Synced `fund_agent/README.md` to state that only explicit `analyze --use-llm` selects `typed_template_path="typed_template_contract"` and that Service passes typed required-output items, `EvidenceAvailability` and `audit_focus` to Fund primitives while Host remains business-opaque.
- Synced `tests/README.md` to document current Slice 7 Service typed path tests and existing Fund typed contract / availability coverage.
- Updated `docs/design.md` to separate current implemented additive typed facts from still-future/non-goal work.
- Updated control/startup docs only to record Slice 8 worker evidence path/status as pending review/controller acceptance; no next gate was advanced.

## Validation

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
```

Result: `16 passed in 0.74s`.

```bash
git diff --check -- fund_agent/fund/README.md fund_agent/README.md tests/README.md docs/design.md docs/current-startup-packet.md docs/implementation-control.md
```

Result: exited `0`.

## Non-Goals Preserved

- No Agent runner/tool-loop, ToolRegistry, ToolTrace, context budget or typed audit runtime migration.
- No multi-year annual evidence runtime.
- No provider live probe, endpoint disposition, budget/default/runtime change or provider SDK change.
- No score-loop, golden/readiness promotion, snapshot refresh or quality gate semantic change.
- No Ch2 public split, `0+9` / `0+10`, public chapter count change or template truth replacement.
- No deterministic `analyze/checklist` behavior change, deterministic fallback, partial stdout report or fail-closed relaxation.
- No direct Service/UI/Host/renderer/quality gate access to repository internals, PDF cache, source helper or filesystem document path.
- No business parameters in `extra_payload`, `**kwargs` or untyped payload bags.

## Residual Risks

- Slice 8 evidence still needs review/controller acceptance before the current gate can be closed.
- `ChapterOrchestrator` remains a Service-owned transition facade; future Agent implementation must decide how to migrate write-audit-repair execution while preserving Service use-case ownership and Host business opacity.
- Typed sidecar remains additive and has not replaced the public template truth; any future replacement needs a separate template truth gate.
