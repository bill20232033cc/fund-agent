# MVP Ch2 auditor timeout 120s evidence controller judgment

## Controller Self-Check

- Role: phaseflow/gateflow controller.
- Parent gate: `MVP Ch2 auditor timeout diagnostic design gate`.
- Current slice: `MVP Ch2 auditor timeout 120s evidence slice`.
- Classification: heavy.
- Scope: judge direct evidence only; no source/test/config/runtime/default/provider/auditor/template/score/golden/readiness change.

## Judgment

**Accepted as evidence, rejected as a basis for default provider budget change.**

The accepted diagnostic command was executed exactly as scoped:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 \
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Result:

- exit code: `1`
- stdout: empty
- fail-closed behavior: preserved
- deterministic fallback: not observed
- retained artifact: `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7`
- artifact JSON validation: pass
- secret scan: no matches

## Finding Disposition

Accepted findings:

- The run used the intended auditor-only override and derived a safe progress host timeout of `2880s`.
- The live run remained incomplete and failed closed after approximately `1102644ms`.
- The new first failed chapter is Ch1, not Ch2: `repair_budget_exhausted` / `audit_rule_too_strict`.
- Ch2 remains top-level `llm_timeout`, but the retained chapter artifact does not provide a matching timeout scalar row; it shows an auditor row with `finish_reason=stop`, `response_chars=22`, and no timeout fields, plus a programmatic L1 repair decision before the chapter-level timeout issue.
- Ch5 has a clear writer timeout under unchanged writer budget: writer `60s x2`, `timeout_budget_kind=writer_initial`, approx prompt tokens `2518`.
- Ch6 blocks on `unknown_anchor`.

Rejected conclusions:

- Do not conclude that raising auditor timeout to `120s` fixes Ch2.
- Do not conclude that the provider default timeout should be changed.
- Do not conclude that writer timeout should now be changed directly from this slice.
- Do not relax auditor rules, repair budget, anchor validation, required output semantics, quality gate, golden/readiness or score-loop semantics.
- Do not start Ch3 calibration implementation from this evidence.

## Controller Decision

The direct evidence shows that the current failure surface is broader than a single Ch2 auditor budget problem. The diagnostic produced cross-chapter acceptance volatility and an internal diagnostic attribution gap for Ch2. The next best-practice move is a design/review gate that reconciles evidence semantics before any runtime, prompt, audit or diagnostic implementation.

Next entry point:

`MVP LLM acceptance volatility and diagnostic evidence reconciliation design gate`

Gate scope:

- design/review only first;
- no code until plan/review/controller judgment accepts an implementation slice;
- reconcile Ch2 timeout attribution, Ch1/Ch4 audit-rule volatility, Ch5 writer timeout, Ch6 unknown-anchor, and the safe evidence contract for future probes;
- decide whether future probes should be provider endpoint disposition, PASS-only timing, split-audit, bounded semantic audit-focus design, or typed diagnostic serialization repair.

## Acceptance Evidence

| Purpose | Evidence |
|---|---|
| Accepted Ch2 diagnostic plan checkpoint | `023af63` |
| 120s evidence artifact | `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-20260603.md` |
| Baseline retained artifact | `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a` |
| 120s retained artifact | `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7` |

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, markdown report body, raw PDF text or raw parsed annual-report text.
