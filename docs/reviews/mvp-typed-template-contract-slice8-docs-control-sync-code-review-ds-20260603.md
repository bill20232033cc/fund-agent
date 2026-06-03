# MVP typed template contract Slice 8 docs/control sync — Code Review (DS)

- **Gate**: `MVP typed template contract Slice 8 Documentation And Control Sync After Accepted Implementation gate`
- **Classification**: `heavy`
- **Reviewer**: AgentDS (code review only; not controller)
- **Date**: 2026-06-03
- **Evidence reviewed**: `docs/reviews/mvp-typed-template-contract-slice8-docs-control-sync-implementation-evidence-20260603.md`
- **Base documents**: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`

## Review Scope

Per controller instruction: review workspace diff only for the Slice 8 docs/control sync. No file modification, no commit, no push, no new gate, no provider/runtime/live probe.

## Verification Commands Executed

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -v
# Result: 16 passed in 0.66s

git diff --check -- fund_agent/fund/README.md fund_agent/README.md tests/README.md docs/design.md docs/current-startup-packet.md docs/implementation-control.md
# Result: exit 0 (no whitespace issues)
```

## Touched Files (Scope Check)

| File | In allowed scope? | Changes |
|------|-------------------|---------|
| `fund_agent/fund/README.md` | Yes | Add typed sidecar non-goal, closed-set `audit_focus` wording, updated primitive descriptors |
| `fund_agent/README.md` | Yes | Add `typed_template_path` to Service boundary list, new paragraph on explicit typed path |
| `tests/README.md` | Yes | Update test descriptions for Slice 7 typed path, add quick verification command |
| `docs/design.md` | Yes | Replace future-design section with 4 new current-implementation / non-goal sections under §3.2 |
| `docs/current-startup-packet.md` | Yes | Update gate status/next entry, one new fact line re Slice 1-6, phase goal paragraph refresh |
| `docs/implementation-control.md` | Yes | Update gate status/next entry, template contract fact line, add worker evidence ref |
| `docs/reviews/mvp-typed-template-contract-slice8-docs-control-sync-implementation-evidence-20260603.md` | Yes | New evidence file (worker output) |

No out-of-scope files modified. No code, tests, provider config, runtime defaults, fixtures, snapshots, quality gate, score, golden/readiness state, `docs/fund-analysis-template-draft.md`, Host runtime, Agent runtime, or dayu dependency touched.

## Finding 1 — Slice 1-7 Factual Accuracy (PASS)

Each document correctly describes the accepted Slice 1-7 additive typed facts without overclaim:

| Slice | Fact | docs/design.md | impl-control.md | startup-packet.md | fund/README.md | fund_agent/README.md |
|-------|------|:-:|:-:|:-:|:-:|:-:|
| 1 | `typed_chapter_contract.v1` sidecar | ✅ | ✅ | ✅ | ✅ | — |
| 2 | same-source `EvidenceAvailability` | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 | `RequiredOutputItem.when_evidence_missing` | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4 | Ch3 evidence-conditional `must_not_cover` | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 | bounded `audit_focus` | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6 | Ch0/Ch7 readiness metadata | ✅ | ✅ | ✅ | — | — |
| 7 | Service `typed_template_path` wiring | ✅ | ✅ | ✅ | — | ✅ |

All documents consistently use the "additive sidecar" / "typed path" framing and do not claim these replace template truth, renderer, quality gate, or deterministic defaults.

## Finding 2 — Prohibited Claims Absence (PASS)

Verified that none of the following are claimed as current implementation in any touched file:

- **Agent runner/tool-loop**: Always qualified as "future design" / "尚未实现" / "非目标" / "separate future gate". No Agent runtime, ToolRegistry, ToolTrace, context budget, or typed audit runtime migration described as current.
- **Multi-year annual evidence runtime**: Consistently "design-only future architecture" / "尚未实现".
- **Provider budget/default/runtime change**: Explicitly preserved as unchanged. Budget calibration described as "evidence-only" / "accepted plan", not implementation.
- **Score-loop**: Listed as "separate future gates" / "非目标" / "design-only". No score, golden, readiness, snapshot, or promotion state change claimed.
- **Ch2 public split / `0+9` / `0+10`**: Explicitly prohibited from being written as current fact. Ch2 subcontracts are correctly described as internal to `chapter_id=2`.
- **Template truth replacement**: Every document that adds typed sidecar facts also explicitly states template truth is NOT replaced.
- **Deterministic default behavior change**: `analyze/checklist` consistently described as unchanged default.

## Finding 3 — Control Doc Gate Non-Advancement (PASS)

Both `docs/current-startup-packet.md` and `docs/implementation-control.md` maintain correct gate posture:

- **Current gate status**: "Slice 8 documentation/control sync implementation evidence has been produced by worker; pending review/controller acceptance"
- **Next entry point**: "Review Slice 8 documentation/control sync evidence and decide acceptance; do not advance to any later gate until controller judgment"

No next gate is named, no subsequent phase is entered, no PR/merge/release authorization is implied. The control docs correctly reflect that this gate is mid-review, not closed.

## Finding 4 — Design Document Status Transition Accuracy (PASS)

`docs/design.md` §3.2 transitions the old single "已接受的未来设计：typed template contract redesign" block into four well-separated sections:

1. **当前已实现：typed template contract additive sidecar** — correctly scoped to Fund-layer `typed_chapter_contract.v1`, Ch2 internal subcontracts only, Ch0 `consumes_chapter_conclusions=(7,)`, `RequiredOutputItem.when_evidence_missing`, `audit_focus` closed-set.
2. **当前已实现：same-source EvidenceAvailability 与 typed audit/writer 消费** — correctly scoped to same-source derivation, writer fail-closed block, programmatic auditor Ch3 coverage, LLM auditor bounded focus.
3. **当前已实现：Service explicit typed path wiring** — correctly scoped to `typed_template_path` field, `--use-llm` only, `ChapterOrchestrator` transition façade, Host business opacity.
4. **仍未实现 / 非目标** — comprehensive non-goal list covering Agent runtime, multi-year, provider defaults, score-loop, Ch2 public split, template truth replacement, etc.

The document header status line also correctly states "已作为当前实现接受，但尚未替换模板真源、deterministic renderer/checklist/analyze 或 Agent runtime."

This four-section structure is the right pattern: it distinguishes what IS implemented from what IS NOT, with precise boundaries.

## Finding 5 — Terminology Consistency (PASS)

Key terms are used consistently across all touched documents:

- "additive" / "sidecar" — the typed contracts are additive, not replacement
- "same-source" — `EvidenceAvailability` derives from the same `ChapterFactProjection`
- "typed path" / "explicit typed path" — the `--use-llm` route through typed contracts
- "closed-set" / "bounded" — `audit_focus` is bounded, not open-ended
- "transition façade" — `ChapterOrchestrator` is Service-owned and temporary
- "business-opaque" — Host does not inspect fund/chapter/provider semantics
- "fail-closed" — all error paths block, no silent fallback

No新旧术语并存 (old/new terminology coexistence) observed. No Dayu runtime dependency claimed.

## Finding 6 — README Update Rule Compliance (PASS)

Per `AGENTS.md` README update rules:

| README | Trigger | Updated? | Content check |
|--------|---------|----------|---------------|
| `fund_agent/fund/README.md` | Fund package modified (Slice 1-6) | Yes | Adds typed sidecar facts + non-goals; no infrastructure leakage |
| `fund_agent/README.md` | Layering/boundary change (Slice 7) | Yes | Adds `typed_template_path` to Service boundary; no internal detail leakage |
| `tests/README.md` | Test changes (Slice 7 tests) | Yes | Updates test descriptions, adds quick verify command; no overclaim |

No stale code examples, no旧术语残留, no职责越界 (boundary violation). Each README stays within its fixed positioning per `AGENTS.md`.

## Finding 7 — Evidence File Self-Consistency (PASS)

The worker evidence file (`mvp-typed-template-contract-slice8-docs-control-sync-implementation-evidence-20260603.md`) correctly identifies:
- Worker role (not controller/reviewer)
- Scope limited to docs/control sync
- Touched files match actual diff
- Non-goals preserved list matches what the diff actually preserves
- Residual risks noted (pending review, `ChapterOrchestrator` transition status, typed sidecar not replacing template truth)

The evidence validation commands match what was independently re-run in this review, with consistent results.

## Finding 8 — Minor Observation: `audit_focus` Terminology Refinement (INFO)

In `fund_agent/fund/README.md`, the description of `audit_focus` changed from:
- "bounded semantic audit 的数据提示" (data hint)
to:
- "bounded semantic audit 的闭集语义提示" (closed-set semantic hint)

This is a precision improvement that aligns with the "closed-set" language used in `docs/design.md` and `typed_contracts.py`. Not a finding — noted as confirmation of terminology alignment.

## Blocking Findings

**None.**

All documents accurately describe Slice 1-7 current additive typed facts without overclaiming Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, Ch2 public split, template truth replacement, or deterministic default behavior changes. Control docs correctly do not advance to the next gate. Tests pass (16/16). Git diff whitespace is clean.

## Recommendation

Proceed to controller judgment. The worker's documentation/control sync implementation is faithful to the accepted Slice 1-7 implementation facts and respects all gate scope constraints.

---

*Review artifact path: `docs/reviews/mvp-typed-template-contract-slice8-docs-control-sync-code-review-ds-20260603.md`*
