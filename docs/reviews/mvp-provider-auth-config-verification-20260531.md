# MVP provider auth/config verification

Gate: `MVP provider auth/config verification gate`
Role: Gateflow controller diagnostic
Date: 2026-05-31
Branch: `codex/local-reconciliation`
Classification: `provider_auth_passed_then_llm_contract_blocked`

## Scope

This gate verified the newly configured real provider in a secret-safe shell, then reran the PR #21 real `--use-llm` smoke. It did not change runtime code, schema, quality gate, golden fixtures, score, snapshot, Host/Agent/dayu integration, PR state, merge state or release state.

## Config Verification

Secret-safe config loader check:

- provider: `openai_compatible`
- model: `mimo-v2.5-pro`
- base URL: `https://token-plan-cn.xiaomimimo.com/v1`
- API key env var: `FUND_AGENT_LLM_API_KEY`
- API key value: not recorded; only length was checked locally
- timeout: `60.0`
- max output chars: `12000`

Minimal provider request:

- request shape: one short chat-completions call through the production `OpenAICompatibleChapterLLMClient`
- result: success
- returned model: `mimo-v2.5-pro`
- finish reason: `stop`
- text preview: `OK`

This resolves the prior `provider_config` / HTTP `401` blocker for the current MiMo-compatible provider configuration.

## Real Smoke Evidence

Command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Raw paths:

- stdout: `reports/mvp-local-acceptance/20260531-auth-verification/real-provider-use-llm-006597-2024.stdout.md`
- stderr: `reports/mvp-local-acceptance/20260531-auth-verification/real-provider-use-llm-006597-2024.stderr.txt`
- exit code: `reports/mvp-local-acceptance/20260531-auth-verification/real-provider-use-llm-006597-2024.exitcode`
- chapter 1 API diagnostic: `reports/mvp-local-acceptance/20260531-auth-verification/chapter1-api-diagnostic.json`

Result:

- exit code: `1`
- stdout: empty
- stderr: `LLM 分析未完成：orchestration_status=blocked, final_assembly_status=incomplete, ...`
- API key leak scan over the gate report directory: `key_leak_hits=[]`

The full CLI smoke no longer fails with HTTP `401`, but it still does not produce an accepted 8-chapter report.

## Same-Source Diagnostic

The narrowed Service/API diagnostic ran only chapter 1 to identify the first material blocker without rerunning all chapters.

Chapter 1 summary:

- API status: `completed`
- orchestrator status: `blocked`
- chapter status: `failed`
- chapter stop reason: `llm_exception`
- attempt count: `1`
- writer status: `drafted`
- writer stop reason: `none`
- writer draft model: `mimo-v2.5-pro`
- writer draft finish reason: `stop`
- writer draft length: `2256`
- writer used 8 allowed anchor ids
- writer declared missing reason: `unsupported_facet_inference`

Programmatic audit blockers in the accepted diagnostic summary:

- missing required structure markers: `结论要点`, `详细情况`, `证据与出处`
- missing required output item marker: `会改变产品理解的特别情况（如有）`
- candidate facet written as asserted fact: `纯债基金`
- candidate facet written as asserted fact: `二级债基/混合债基`

LLM audit blocker:

- `llm:parse_failure`
- rule code: `C1`
- message: `LLM audit response parse failure，禁止 silent pass。`

Repair decision:

- action: `regenerate`
- reason: MVP has no typed patch API, so patch/regenerate maps to bounded whole-chapter rewrite
- following regenerate provider call timed out: `LLMProviderRuntimeError: LLM provider request timed out`

## Classification

Classification: `provider_auth_passed_then_llm_contract_blocked`

Rationale:

- `provider_config` is resolved for the current MiMo provider because config loading and a minimal provider request succeeded.
- A true draft was produced for chapter 1, so the path reached writer output and audit.
- The first content blocker is the chapter 1 draft failing programmatic structure/facet contract and LLM audit parse protocol.
- Provider runtime latency remains a secondary risk because the repair regenerate call timed out.
- The CLI final-assembly error remains a downstream symptom: the assembly cannot proceed without accepted chapter drafts/conclusions.

## Minimal Next Entry

`MVP LLM writer/auditor contract hardening gate`

Minimum scope:

- inspect Gate 2 writer prompt requirements for mandatory section markers and required output item markers;
- inspect auditor prompt/parse protocol for MiMo output behavior and `PASS|chapter|no issues` / `SEVERITY|LOCATION|MESSAGE` compliance;
- preserve fail-closed semantics, anchor marker strictness and `non_asserted_facets` blocking;
- decide whether to strengthen prompts only, add deterministic wrapper/repair hints, or add provider-specific timeout configuration;
- add tests with fake clients; do not depend on live provider pytest.

## Boundaries Preserved

- No runtime code changed in this gate.
- No deterministic fallback introduced.
- No chapter acceptance, quality gate, final judgment, score, snapshot, golden fixture or promotion state changed.
- No Host/Agent/dayu runtime introduced.
- No PR status, merge, release or promotion action performed.
- No API key value, Authorization header, full environment or full provider response recorded.

## Self-Check

- Current gate/role: provider auth/config verification, controller diagnostic.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, and previous diagnostic artifacts.
- Scope boundary: secret-safe provider verification and same-source smoke evidence only.
- Stop conditions: real report still blocked; next gate requires implementation planning before code changes.
- Evidence: raw reports under `reports/mvp-local-acceptance/20260531-auth-verification/`.
- Next action: update control docs to point at LLM writer/auditor contract hardening.
