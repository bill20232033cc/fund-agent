# MVP PASS-only provider timing probe design plan review — Agent B

## Findings

### Blocking Findings

None. **PASS** for design-only gate, subject to controller must-answer items below.

### NB-1 — attempts=1 is not a default-budget probe, but it is not a config-semantics change

- **Location**: plan §5 Attempt Policy, §8 Future Evidence Command Contract.
- **Type**: terminology / measurement semantics.
- **Current plan**: uses loaded config, then clones it in memory with `timeout_max_attempts=1` and `timeout_backoff_seconds=0`.
- **Disposition**: non-blocking. This does not change provider config/default semantics if it remains probe-local and in-memory only. But it must not be described as a default-budget probe. It is a **single-attempt current-timeout PASS-only probe**.
- **Impact**: if controller later treats it as same-budget production evidence, the comparison will be overstated.
- **Recommendation**: controller should explicitly choose the measurement lens: `attempts=1` for endpoint health latency, or unchanged attempts for production-similar comparison.

### NB-2 — `audit_chapter()` necessarily receives and returns body text; no-body evidence must be enforced by construction

- **Location**: plan §4, §6, §8; `fund_agent/services/llm_provider.py`; `fund_agent/fund/chapter_auditor.py`.
- **Type**: evidence safety / implementation readiness.
- **Current plan**: discard response body and record only `response_char_count`.
- **Code fact**: `audit_chapter()` returns `ChapterAuditLLMResponse(raw_text=...)`; the harness must touch `raw_text` at least to count chars.
- **Disposition**: non-blocking because the plan forbids raw response/body storage. The future harness should use an allowlist serializer by construction: compute `len(raw_text)`, discard the response object, and never serialize response objects, exception reprs, diagnostics objects, request body, prompt body, or request id.
- **Recommendation**: controller should require no response body capture by construction, not only post-hoc secret scan.

### NB-3 — `ChapterAuditLLMRequest` construction is almost code-generation-ready, but exact synthetic fields should be pinned

- **Location**: plan §3, §4, §8.
- **Type**: code-generation readiness.
- **Current plan**: says “minimal synthetic `ChapterAuditLLMRequest` fields” and gives PASS literals.
- **Code fact**: the dataclass also requires `chapter_id`, `fund_code`, `report_year`, `allowed_fact_ids`, `allowed_anchor_ids`, and `audit_focus`; provider audit prompt appends allowed ids and focus to the user prompt.
- **Disposition**: non-blocking. Empty tuples are likely sufficient for allowed ids and focus, but the future command contract should spell this out so implementation does not redesign the probe or accidentally introduce report-like identifiers.

## Challenge Disposition

1. Cloned config attempts semantics: not a hidden default change if in-memory only; do not call it default-budget.
2. PASS-only prompt and artifacts: safe from report artifact generation if it bypasses Service analyze/orchestrator/report assembly and stores no raw response. `audit_chapter()` still returns `raw_text`; harness must discard it.
3. attempts=2 vs attempts=1: attempts=1 is better for endpoint health measurement; unchanged config is better for production-similar comparison. This is a controller choice, not a blocker.
4. request field completeness: non-blocking gap; pin exact synthetic request values in controller judgment or future evidence plan.
5. no-response-body capture: should be by allowlist construction plus scan, not scan alone.
6. hidden path to endpoint/config/default change: plan correctly blocks direct change from one PASS-only result. Any endpoint/config/default action still needs a separate heavy disposition gate.

## Controller Must-Answer Items

- Is the accepted probe name `single-attempt current-timeout PASS-only probe`, or should the future evidence use unchanged retry attempts for production-similar comparison?
- What exact synthetic `ChapterAuditLLMRequest` fields are authorized?
- Must the harness use an allowlist output schema and avoid serializing diagnostics/request ids wholesale?
- Does a PASS-only timeout only authorize a future disposition gate, not any endpoint/config/default/runtime change?

## Residual Risks

- One PASS-only observation remains time-window-specific and cannot prove durable endpoint behavior.
- `audit_chapter()` is still auditor-shaped, not a raw minimal chat probe; that is intentional for same-source auditor attribution but should not be generalized to writer or full report behavior.

## Final Conclusion

**PASS** — no blocking findings. The plan is acceptable as a design-only gate if controller pins the attempt-policy terminology and no-body capture contract before any live evidence gate.
