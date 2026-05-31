# Plan Review: MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration

## Verdict

**PASS**

## Blocking Findings

None.

## Non-blocking Findings

1. **Classification threshold gap.** The plan uses `approx_prompt_tokens >= 8000` for `large_writer_prompt_cost` and `<= 3000` for `small_prompt_provider_timeout`. Service diagnostic shows chapter 1 writer at ~2202 tokens, chapters 3/5 auditor at ~1047/983 tokens — all clearly small. Chapters 2/6 writer at ~26086/29078 — clearly large. The 3000-8000 gap is untested in current evidence; no chapter falls in that range. The plan correctly labels these as `provider_runtime_timeout_uncalibrated` and stops for controller decision. Acceptable for this gate.

2. **Compact mode scope.** The plan makes compact mode explicit `--use-llm` only (Slice 2 Task 2) and notes deterministic path remains unchanged. This is correct. The wording "unless tests and review accept making it the universal writer prompt mode" (line 232) is a future escape hatch, not a current gate commitment — acceptable.

3. **Timeout budget interaction with chapter 4 accepted.** Chapter 4 was accepted under the current 60s default timeout. If operation-specific timeouts are raised to 120s, chapter 4 latency characteristics may change. The plan does not explicitly call this out as a regression risk. Non-blocking: the rerun matrix in Slice 3 covers this implicitly.

4. **Anchor `note` field safety.** The plan says "no full anchor note if it can contain source text" (line 162) for the anchor cost diagnostic. This is a conditional guard. Implementation must verify anchor notes don't leak source text; the plan acknowledges this but leaves it to implementation judgment. Acceptable given the allowlisted serializer requirement.

## Required Fixes

None. All 8 review criteria pass:

| # | Criterion | Result |
|---:|---|---|
| 1 | Diagnostics before compaction/budget | PASS — Slice 1 diagnostics, Slice 2 compaction, Slice 3 budget |
| 2 | Same-source ch2/6 vs ch1/3/5 classification | PASS — service diagnostic data used as direct evidence |
| 3 | No full prompt/draft/provider response/secret | PASS — explicit in Safety Invariants and schema |
| 4 | No evidence/ITEM_RULE/candidate facet/audit relaxation | PASS — explicit in Safety Invariants |
| 5 | No Gate 5/dayu/Host/Agent entry | PASS — explicit Non-Goal |
| 6 | No golden/fixtures/extraction score/quality gate | PASS — explicit Non-Goal |
| 7 | Deterministic default and fail-closed preserved | PASS — state machine section explicit |
| 8 | docs/design.md update not overreaching | PASS — Docs Decision defers design.md to post-acceptance |

## Review Scope

Files read: plan artifact, `AGENTS.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-evidence-20260531.md`, `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-controller-judgment-20260531.md`, `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.json`, `fund_agent/config/llm.py`, `fund_agent/services/llm_provider.py`, `fund_agent/fund/chapter_writer.py` (prompt construction and fact/anchor serialization).

Cross-referenced: plan's direct evidence table against service diagnostic JSON; existing timeout config defaults against plan's proposed env vars; writer prompt construction (`_prompt_fact_payload`, `_prompt_anchor_payload`) against plan's compaction contract.
