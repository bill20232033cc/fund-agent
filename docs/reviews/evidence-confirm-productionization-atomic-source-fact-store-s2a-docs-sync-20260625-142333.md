# Atomic Source Fact Store / Composite Analysis View Split S2A Docs Sync

- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Gate: `S2A docs-sync/fix gate after code review pass`
- Verdict: `S2A_DOCS_SYNC_READY_FOR_REREVIEW_NOT_READY`
- Stop condition: ready for rereview / accepted slice commit decision, not committed, release/readiness `NOT_READY`

## Scope

S2A changed the `fund_agent/fund` extractor public result surface by adding child-level extractor result fields. This docs-sync updates only the Fund README current-state wording required by the README trigger.

No production code, tests, control docs, design docs, source helpers, parser/repository paths, live/PDF path, product CLI, provider/LLM, PR state, tag, release, or readiness state was changed.

## Changed Files

- `fund_agent/fund/README.md`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s2a-docs-sync-20260625-142333.md`

## Exact Wording Decision

The existing current-state paragraph that mentions `fund_agent/fund/source_facts.py` / S1 was updated to add this S2A boundary:

```text
S2A 当前只把默认 parsed annual extractor public result surface 拆出 child-level trailing/defaulted `ExtractedField[object]` 字段，覆盖 `fee_schedule`、`nav_benchmark_performance`、`manager_strategy_text` 和 `manager_alignment` 的子披露值；既有复合 dict value 仍作为兼容输出保留。Processor-level `AtomicSourceFact` emission 仍属于 S2B，当前不声明默认 parsed annual / FDD processor 已发射子字段 atomic facts。
```

The internal layering bullet for `source_facts.py` was also minimally aligned so it no longer reads as S1-only:

```text
`source_facts.py`：atomic source fact store 和 composite analysis view 契约；当前 S1 提供默认空 store、不可变索引、strict merge、derived-only 依赖视图和 compatibility surface；S2A 只在默认 parsed annual extractor result dataclass 上增加 trailing/defaulted child-level `ExtractedField[object]` 字段，覆盖 `fee_schedule`、`nav_benchmark_performance`、`manager_strategy_text` 和 `manager_alignment`，复合 value 仍是兼容输出，processor-level `AtomicSourceFact` emission 仍归 S2B。
```

This wording intentionally avoids release/readiness, live/PDF, Evidence Confirm bridge, default atomic emission, or processor-level atomic source fact claims.

## Validation

- `rg -n 'S2A 当前只把默认 parsed annual extractor public result surface|S2A 只在默认 parsed annual extractor result dataclass|Processor-level \`AtomicSourceFact\` emission 仍属于 S2B|processor-level \`AtomicSourceFact\` emission 仍归 S2B' fund_agent/fund/README.md` -> found the added wording at `fund_agent/fund/README.md:139` and `fund_agent/fund/README.md:676`.
- `git diff --check` -> passed with no output.

Not run:

- Tests.
- Live/PDF, product CLI, provider/LLM, network, repository/parser/source-helper commands.

## Residual Risks / Owner

- S2B processor-level `AtomicSourceFact` emission remains pending. Owner: S2B implementation worker.
- ChapterFactProvider bridge, Evidence Confirm bridge, renderer, quality gate, product CLI, live/PDF evidence, release and readiness remain outside S2A docs-sync. Owner: later approved S3/S4/S5/RR gates.
- S2A code review residual table-backed child anchor assertion gaps remain as recorded in `docs/reviews/code-review-atomic-source-fact-store-s2a-20260625-142104.md`. Owner: controller/S2B owner disposition.

## Completion Status

`S2A_DOCS_SYNC_READY_FOR_REREVIEW_NOT_READY`

No commit was created. No push, PR mutation, merge, tag, release, live/PDF, product CLI, provider/LLM, or readiness action was executed.
