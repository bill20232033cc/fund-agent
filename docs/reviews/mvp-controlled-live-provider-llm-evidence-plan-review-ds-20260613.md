# DS Review: Controlled Live Provider/LLM Evidence Plan

Date: 2026-06-13

Reviewed artifact:

- `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md`

Review scope:

- Review only.
- No file modifications.
- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR/push/merge/cleanup commands.

## Initial Verdict

`FINDINGS`

## Findings

| Severity | File / section | Issue | Minimum revision |
|---|---|---|---|
| Medium | Redaction Requirements | Bare substring redaction checks could misclassify safe metadata such as `redaction_policy.forbidden_categories`, `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens` and `max_output_chars` as sensitive leaks. | Use value-bearing secret/raw-body checks or JSON allowlist checks; explicitly allow safe scalar/policy metadata. |
| Medium | Command Boundary / Environment Boundary | The exact live command fixed timeout/retry/backoff but did not fix `FUND_AGENT_LLM_MAX_OUTPUT_CHARS`; ambient env could raise local output cap. | Add `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000` to exact/allowed commands or require metadata equality. |

## Targeted Re-review

`PASS`

Closure basis:

- Redaction now distinguishes value-bearing secret/raw-body retention from safe scalar/policy metadata.
- Safe metadata such as `redaction_policy.forbidden_categories`, `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens` and `max_output_chars` is explicitly allowed when it contains no underlying value/body.
- Exact and allowed live commands force `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`.
- Environment boundary marks `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` as forced.
- Stop conditions require retained safe metadata `max_output_chars` to equal `12000`.

No new blocker found. The plan remains planning/authorization only; live execution still requires later explicit authorization.
