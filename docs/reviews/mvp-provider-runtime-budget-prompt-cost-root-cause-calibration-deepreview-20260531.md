# Deep Review: MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Role: controller aggregate deep review over scoped gate evidence.
- Date: 2026-05-31
- Verdict: **PASS with blocked live-provider outcome**

## Scope

Reviewed:

- `AGENTS.md`
- Gate plan: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-20260531.md`
- Plan reviews: MiMo and DS
- Implementation evidence
- Code reviews: MiMo and DS
- Validation evidence
- Current real-provider report directory
- Current implementation paths:
  - `fund_agent/fund/chapter_writer.py`
  - `fund_agent/services/llm_provider.py`
  - `fund_agent/services/chapter_orchestrator.py`
  - `fund_agent/config/llm.py`
  - `fund_agent/ui/cli.py`

This deep review intentionally does not review the whole dirty worktree. The workspace contains many historical untracked artifacts outside this gate; including them would obscure the current gate contract.

## Blocking Findings

None for the implemented diagnostic / compact-payload / timeout-budget calibration slice.

## Adversarial Checks

### Prompt-Cost Diagnostic Safety

The diagnostic serializers are allowlisted and scalar/id based. Prompt-cost payloads record component char counts, fact ids, source field ids, status, missing reason, value char counts, serialized fact char counts, anchor ids and anchor source metadata. They do not serialize full fact values, anchor notes, prompt text, draft markdown, provider request JSON, provider response JSON, raw audit response, API key or Authorization header.

The current report directory exact-key scan reports `exact_key_hits=0`. Generic sensitive-word scan only finds safe field names such as `system_prompt_chars` and `user_prompt_chars`.

### Compact Payload Contract

The compact writer payload keeps required fact identity, status, missing semantics, `required_by`, evidence anchor ids and anchor source metadata. It does not relax evidence anchors, ITEM_RULE, candidate facet handling, missing semantics or audit rules. Compact mode is explicitly enabled for CLI `--use-llm`; deterministic `analyze` and `checklist` do not call the writer path.

### Timeout Budget And Retry

Provider retry remains timeout-only and bounded. Current live diagnostics record `timeout_seconds=60.0`, `provider_max_attempts=2`, `timeout_budget_kind=writer_initial`, and per-attempt elapsed milliseconds. Non-timeout provider errors are not converted into success and are not retried indefinitely.

### Final Assembly

The final report remains fail-closed. Current real provider evidence has empty stdout, `report_markdown_present=false`, `final_assembly_status=incomplete`, and no deterministic fallback. Partial body chapter matrices are diagnostic only and are not packaged as complete reports.

### Root Cause Evidence

The previous large prompt blocker for chapters 2 and 6 is no longer supported by current evidence:

- Chapter 2: `26086` approximate tokens before, `1590` after compact mode.
- Chapter 6: `29078` approximate tokens before, `2110` after compact mode.

The current run fails with writer timeouts for chapters 1-6, all below `3000` approximate tokens. This directly supports `provider_runtime_timeout_small_prompt`, not `large_writer_prompt_cost`.

## Residual Risks

- Small-prompt timeout may be caused by provider endpoint latency, model generation latency, model-side queuing, or an operation-specific timeout budget that is too low for this endpoint. The current evidence proves timeout location and prompt scale, but does not distinguish these provider-side causes.
- The next gate should use bounded budget experiments and same-source diagnostics. It should not relax writer/auditor safety rules or switch to deterministic fallback.
- The `_sanitize_text` helper differs between provider and orchestrator modules. Existing usage remains safe, but future diagnostic code should avoid reusing the narrower orchestrator helper for prompt-bearing messages.

## Conclusion

The implementation satisfies the gate's safety and observability requirements. The live provider acceptance remains blocked, but with a sharper and current root cause: compact prompts are small, yet writer calls time out across all body chapters under the default bounded provider budget.
