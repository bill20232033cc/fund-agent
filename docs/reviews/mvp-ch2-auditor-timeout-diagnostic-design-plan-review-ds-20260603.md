# MVP Ch2 auditor timeout diagnostic design plan review (DS)

## Reviewer Self-Check

- Role: independent plan reviewer only. Not controller. No edits to the plan. No implementation.
- Gate: `MVP Ch2 auditor timeout diagnostic design gate` (heavy).
- Plan under review: `docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md`.
- Scope: read-only verification of all review focus areas; write only this review artifact.

## Required Inputs

| Input | Status |
|---|---|
| `AGENTS.md` | Read and applied |
| `docs/design.md` | Read — Route C, current/future boundaries confirmed |
| `docs/implementation-control.md` | Read — current gate, accepted evidence, routing confirmed |
| `docs/current-startup-packet.md` | Read — short resume state matched to control doc |
| Plan under review | Read in full |
| Prior budget calibration controller judgment | Read — accepted evidence narrowing to Ch2 only |
| `summary.json` (baseline retained run) | Inspected — same-source chapter/runtime facts verified |
| `fund_agent/config/llm.py` | Read — `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` at line 34, range `(0,300]` at line 254 |
| `fund_agent/services/llm_provider.py` | Read — `_effective_timeout_seconds()` at line 637 selects `config.auditor_timeout_seconds` for `operation="auditor"` |
| `fund_agent/services/execution_contract.py` | Read — `ProviderRuntimeBudget.auditor_timeout_seconds` at line 143, `derive_host_timeout_seconds()` at line 406 |
| `fund_agent/services/fund_analysis_service.py` | Read — `build_fund_llm_execution_request()` copies config auditor timeout into runtime plan at line 953 |

## Findings

### Finding 1 — Same-Source Evidence: PASS

Verified against `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json`:

- **Ch2**: `status=failed`, `failure_category=llm_timeout`, `stop_reason=llm_timeout`. Runtime diagnostics confirm `operation=auditor` (line 290), `approx_prompt_tokens=758` (line 283), `timeout_seconds=60.0` (line 305), `timeout_max_attempts=2` (line 303), `timeout_budget_kind=auditor` (line 302), `timeout_root_cause_hint=small_prompt_provider_timeout` (line 304). Both attempts (index 1 and 2) timed out at ~60s each.
- **Ch3**: `status=failed`, `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`, `stop_reason=repair_budget_exhausted`. `prompt_contract_diagnostics` at line 202 confirms `issue_id_prefix_counts: {"programmatic:C2": 1}`. Runtime diagnostics confirm no provider call (all provider fields null) — this is a programmatic audit failure, not a provider runtime issue.
- **Ch4**: `status=accepted`. CONFIRMED.
- **Ch5**: `status=accepted`. CONFIRMED.
- **Ch6**: `status=accepted`. CONFIRMED.

The plan's same-source evidence claim (lines 38-52) is accurate. The current default-run blocker is Ch2 auditor timeout only. Ch4/Ch5/Ch6 are not current blockers. Ch3 is a separate `prompt_contract` / `programmatic:C2` issue.

### Finding 2 — Existing Code Supports Auditor-Only Timeout Override: PASS

Verified the full path from env var to provider request:

1. **Config definition** (`fund_agent/config/llm.py:34`): `_ENV_AUDITOR_TIMEOUT_SECONDS = "FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS"` exists.
2. **Config loading** (`fund_agent/config/llm.py:107-111`): `auditor_timeout_seconds = _load_optional_timeout_seconds(env, _ENV_AUDITOR_TIMEOUT_SECONDS, fallback=timeout_seconds)` — falls back to `FUND_AGENT_LLM_TIMEOUT_SECONDS` when unset. Range validation at line 254 enforces `(0, 300]`.
3. **Config field** (`fund_agent/config/llm.py:71`): `LLMProviderConfig.auditor_timeout_seconds: float` exists as a typed dataclass field.
4. **Service runtime plan** (`fund_agent/services/fund_analysis_service.py:953`): `auditor_timeout_seconds=config.auditor_timeout_seconds` — value flows from config into `ProviderRuntimeBudget`.
5. **Execution contract** (`fund_agent/services/execution_contract.py:143`): `ProviderRuntimeBudget.auditor_timeout_seconds: float` is a typed, validated field.
6. **Provider adapter selection** (`fund_agent/services/llm_provider.py:637-638`): `if operation == "auditor": return config.auditor_timeout_seconds` — correctly selects auditor-specific timeout.
7. **Timeout budget kind** (`fund_agent/services/llm_provider.py:662-663`): `if operation == "auditor": return "auditor"` — correctly records `timeout_budget_kind=auditor` in diagnostics.
8. **Host deadline derivation** (`fund_agent/services/execution_contract.py:429-434`): `phase_budget = writer + auditor + repair`, then `int(max(1.0, phase_budget * attempts * chapter_count))` — Host deadline automatically adjusts when auditor timeout is raised, without Host inspecting business fields.
9. **Config README** (`fund_agent/config/README.md:28`): Documents `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` with fallback and range.
10. **Test coverage**: `test_llm_config.py:105` tests explicit `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=80`; `test_llm_provider.py:370` tests `auditor_timeout_seconds=22` in provider adapter; `test_fund_analysis_service_llm.py:226` tests auditor timeout flow into runtime plan.

The plan's claim (lines 63-71) is accurate: no implementation is needed for the next evidence slice. Setting only `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120` at the shell will produce the intended diagnostic budget through existing code paths.

One observation (not a finding): The `httpx.Client` default timeout in `OpenAICompatibleChapterLLMClient.__init__` (`fund_agent/services/llm_provider.py:164`) uses `config.timeout_seconds` (the global default), but the per-request `timeout=effective_timeout` override at line 269 correctly supersedes it. Diagnostic behavior is correct.

### Finding 3 — Command Safety: PASS

The proposed diagnostic command:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 \
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Verified against the plan's constraints (lines 158-165) and code:

- **120s is bounded**: Within valid range `(0, 300]` per `fund_agent/config/llm.py:254`. PASS.
- **Default-preserving**: Only `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` is set. Writer timeout stays at default 60s (`fund_agent/config/llm.py:70`), repair falls back to writer (`fund_agent/config/llm.py:112-115`), global `timeout_seconds` stays at 60s (`fund_agent/config/llm.py:19`). PASS.
- **No PASS-only probe**: Plan explicitly forbids it (line 163). PASS.
- **No split-audit probe**: Plan explicitly forbids it (line 164). PASS.
- **No auditor relaxation**: Plan explicitly forbids it (line 312). PASS.
- **No score/golden/quality/readiness changes**: Plan explicitly forbids them (lines 313-315). PASS.
- **Attempt count unchanged**: `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` unset, stays at default 2. The comparison `60s x2` vs `120s x2` is apples-to-apples.

### Finding 4 — Service/Host/Agent/Fund Ownership Boundaries: PASS

| Concern | Disposition | Evidence |
|---|---|---|
| Config env var | Owned by config layer (`fund_agent/config/llm.py`); loaded by Service in `build_fund_llm_execution_request()` | `fund_agent/services/fund_analysis_service.py:939` |
| Provider runtime budget | Service-owned `ProviderRuntimeBudget` in `execution_contract.py` | `fund_agent/services/execution_contract.py:129` |
| Runtime plan | Service-owned `FundLLMRuntimePlan`; Host only receives `host_timeout_seconds` scalar | `fund_agent/services/execution_contract.py:284` |
| Provider adapter | Service-owned `OpenAICompatibleChapterLLMClient`; timeout selection by operation is internal | `fund_agent/services/llm_provider.py:133` |
| Host deadline | Derived by Service from provider budget; Host does not inspect fund/chapter/operation fields | `fund_agent/services/execution_contract.py:406-434` |
| Fund audit semantics | Not changed by this diagnostic; CHAPTER_CONTRACT, preferred_lens, ITEM_RULE untouched | Plan lines 309-310 |
| Agent | Not introduced; Agent engine/tool-loop/budget remains deferred future design | Plan lines 308-309 |

No boundary violations. The plan's non-goal checks (lines 306-316) are accurate.

### Finding 5 — Stop Conditions: PASS (with observation)

Slice A stop conditions (lines 109-113):

- `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` presence — already verified to exist. If a future branch check finds it absent, conditional Slice I provides a bounded implementation fallback.
- JSON validation failure — appropriate stop.
- Conflicting changes in relevant modules — appropriate stop; controller must decide.

Observation: The plan describes the stop condition as "If `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` is not present in code" (line 111), but the Slice A `rg` command is a preflight that verifies this before any live provider call. This is an adequate ordering — preflight first, live evidence only if preflight passes.

### Finding 6 — Interpretation Matrix: PASS

The matrix (lines 250-260) covers 7 outcomes:

1. Ch2 accepted, Ch3 still C2 — supports budget hypothesis; routes Ch3 separately.
2. Ch2 still times out at 120s — disproves simple budget sufficiency; controller decides next step.
3. Ch2 fails with audit issue — reveals content/audit blocker; routes to separate calibration.
4. Full report accepted — shows normal completion possible; does not authorize default change.
5. Writer/repair timeout — disproves Ch2-only auditor hypothesis.
6. Config/auth failure — routes to separate provider config gate.
7. Artifact missing — routes to artifact retention gate.

Each outcome has a concrete next route. The matrix does not prematurely authorize default changes, score-loop entry, or auditor relaxation.

Minor note on outcome 2: The plan writes "supports provider endpoint/runtime instability or auditor prompt/task latency beyond bounded budget." This covers both server-side timeout (where the provider has a hard timeout below 120s) and genuine endpoint instability. The distinction could matter for a subsequent gate but is not needed for this diagnostic design.

### Finding 7 — Artifact Handling: PASS

- Baseline artifact path `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a` is never overwritten, edited, or deleted (line 177).
- New artifact path handling covers both incomplete (retained artifact exists) and complete (no retained artifact) cases (lines 175-179).
- Artifact write warning is handled without changing fail-closed (line 179).
- Allowed evidence fields (lines 192-213) and forbidden evidence fields (lines 215-231) are comprehensive.

### Finding 8 — Secret Safety: PASS

- Slice E secret scan command (lines 239-243) covers Authorization headers, Bearer tokens, API key env var names, `sk-` prefixes, raw responses, drafts, and prompts.
- Stop-on-match behavior (lines 245-248) prevents secret-bearing content from entering review artifacts.
- The plan itself contains only labeled forbidden-output category names (e.g., "Authorization header", "raw provider response"), not secret values.

### Finding 9 — Documentation Drift: NON-BLOCKING OBSERVATION

The plan notes (lines 32-33) that root `README.md` only lists `FUND_AGENT_LLM_TIMEOUT_SECONDS` while `fund_agent/config/README.md` and code already document `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`, `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`, and `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`.

This is correctly classified as doc drift, not a runtime blocker. The plan explicitly defers it to a later doc-sync gate. This is appropriate — root README is a user manual and the operation-specific vars are an advanced diagnostic feature.

### Finding 10 — Conditional Implementation Slice: PASS (not needed)

The plan correctly determines (line 264) that conditional Slice I is not needed because the code already supports `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`. The slice is preserved as a fallback (lines 267-301) with correct:
- Allowed files/modules (lines 269-276)
- Implementation constraints matching current boundaries (lines 278-287)
- Validation commands (lines 291-294)
- Acceptance criteria (lines 296-302)

## Validation

```bash
git diff --check -- docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-review-ds-20260603.md
```

(To be run after writing this artifact.)

Secret scan over this review artifact: no API keys, Authorization headers, Bearer tokens, cookies, passwords, provider base URLs, model names, raw responses, prompts, drafts, or report bodies present.

## Disposition

**PASS — no blocking findings.**

All five review focus areas pass:

1. **Same-source evidence**: Verified against `summary.json`. Ch2 is the only current default-run auditor timeout blocker; Ch4/Ch5/Ch6 accepted; Ch3 is separate `programmatic:C2`.
2. **Existing code support**: Verified the full path from `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` env var through config → runtime plan → provider adapter → per-request timeout selection. No implementation is needed for the next evidence slice.
3. **Command safety**: 120s is within `(0,300]`, only auditor timeout is overridden, writer/repair/global defaults preserved, no PASS-only/split-audit/auditor-relaxation/score/golden/quality/readiness changes.
4. **Boundaries**: Service owns config parsing, runtime budget, runtime plan, and provider adapter. Host receives only derived `host_timeout_seconds` scalar. Fund audit semantics unchanged. Agent not introduced.
5. **Stop conditions, interpretation matrix, artifact handling, secret safety**: All adequate. Interpretation matrix covers 7 outcomes with concrete routes. Forbidden evidence list is comprehensive.

The plan is ready for controller judgment. The next step is an evidence-only, controller-authorized live diagnostic using the existing `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120` override.
