# MVP Future Live Provider Calibration Evidence Gate Plan — Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Future live provider calibration evidence gate`
- Gate stage: plan acceptance judgment
- Classification: `heavy`
- Controller role: controller only; not planning worker, not reviewer, not evidence executor
- Plan artifact: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`
- Preceding accepted gate: `Provider runtime residual disposition / calibration gate`
- Preceding accepted evidence checkpoint: `3f72786`

This judgment accepts the reviewed plan for the next evidence step. It does not itself execute provider readiness or live provider commands.

## 2. Sources Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-review-ds-20260604.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-rereview-ds-20260604.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-review-mimo-20260604.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-rereview-mimo-20260604.md`

## 3. Review Status

| Reviewer | Artifact | Verdict | Controller disposition |
|---|---|---|---|
| AgentDS | `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-review-ds-20260604.md` | PASS with findings | Material findings required plan fix before judgment |
| AgentDS | `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-rereview-ds-20260604.md` | PASS | DS findings confirmed fixed |
| AgentMiMo | `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-review-mimo-20260604.md` | PASS with one minor finding | Minor residual-owner table gap accepted as fix-before-judgment cleanup |
| AgentMiMo | `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-rereview-mimo-20260604.md` | PASS | MiMo finding confirmed fixed |

Controller finding disposition:

- DS Finding 1, non-timeout provider runtime taxonomy: fixed by adding `provider_runtime_error_non_timeout`.
- DS Finding 2, presence-only readiness implementation path: fixed by adding exact inline Python readiness command.
- DS Finding 3, fund/year rationale: fixed by documenting comparability rationale for `006597 / 2024`.
- DS Finding 4, redaction pattern adaptation: fixed by adding provider-key-format adaptation guidance.
- MiMo Finding 1, missing residual owner for non-timeout provider errors: fixed by adding the Section 11 owner row.

No blocking or material findings remain open.

## 4. Controller Judgment

The plan is accepted for the next evidence step.

Rationale: based on `docs/design.md` and `docs/implementation-control.md`, the current blocker is an endpoint/provider-runtime residual after `Real LLM smoke re-baseline gate` failed closed with all six body chapters timing out. The accepted plan is the narrowest evidence protocol that can collect current same-run evidence without changing provider defaults, relaxing fail-closed semantics, entering Chapter acceptance calibration, or promoting Agent/runtime future design into current fact.

The plan preserves the required heavy-gate order:

```text
plan -> independent review -> fix -> re-review -> controller judgment -> accepted checkpoint -> evidence execution
```

## 5. Explicit Authorization For The Evidence Step

After this plan judgment is included in a local accepted checkpoint, the evidence executor is authorized to run only the following sequence:

1. Record git/scope preflight exactly as the plan requires.
2. Run the plan's exact presence-only Python readiness command.
3. If readiness fails, stop as `environment_blocked`.
4. If readiness passes, run exactly one live command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

No other live provider command, endpoint probe, PASS-only timing probe, curl command, handwritten HTTP request, retry command, deterministic fallback command, chapter-only probe, model/endpoint/timeout/attempt/backoff/max-output override, or provider-default change is authorized.

## 6. Verifier Matrix

| Criterion | Direct evidence required | Validation command / artifact | Blocker or residual classification | Next entry |
|---|---|---|---|---|
| Plan accepted after two independent reviews | DS review/re-review PASS; MiMo review/re-review PASS; this judgment | Review artifacts listed in Section 3 | Missing second review blocks evidence | Accepted plan checkpoint |
| Presence-only readiness is secret-safe | Boolean-only config presence output; no env values or HTTP call | Plan Section 5.2 command output in future evidence artifact | `environment_blocked` if config invalid or shell lacks env | Stop or one live command |
| Exactly one live command under defaults | Command log proving one invocation and no overrides | Future evidence artifact command section | `safety_blocker` if count exceeds one or overrides appear | Stop after one command |
| Incomplete LLM run remains fail-closed | Exit code, stdout byte count, stderr safe summary, retained artifact path | Future evidence artifact plus retained manifest/summary | `safety_blocker` if partial stdout, exit 0 incomplete, or fallback | Stop and classify |
| Same-run direct evidence | New retained artifact from the one command | Future evidence artifact; retained `reports/llm-runs/.../manifest.json` if produced | Historical artifact substitution blocks acceptance | Controller residual classification |
| Secret-safe diagnostics | Redaction scan and allowlist-only diagnostic fields | Plan Section 7 scan in future evidence artifact | `safety_blocker` on value-like secret or raw prompt/response leak | Stop immediately |
| Boundary guardrails preserved | Git status/diff showing no source/test/config/runtime/control drift outside authorized artifact/output | Future evidence artifact preflight | Unauthorized diff blocks evidence acceptance | Controller judgment |
| Residual classification complete | One of Section 6 classifications with evidence | Future evidence artifact outcome section | Mixed historical/current inference blocks acceptance | Next gate decision |

## 7. Non-Goals And Prohibited Follow-On

This judgment does not authorize:

- Chapter acceptance calibration.
- Provider timeout/default/model/endpoint/attempt/backoff/budget changes.
- PASS-only timing probe execution.
- Agent runtime, tool loop, ToolRegistry, ToolTrace, multi-year evidence runtime or score-loop implementation.
- Golden/readiness/snapshot/fixture/promotion changes.
- Partial report stdout, deterministic fallback, or fail-closed relaxation.
- PR, push, mark-ready, merge, external issue/comment or release-state work.

## 8. Residual Risks

| Residual | Owner | Handling |
|---|---|---|
| Provider config/env missing in the evidence shell | provider config/operator shell owner | Stop as `environment_blocked`; no repo change implied |
| Endpoint availability residual remains active | provider endpoint operator / future calibration controller | Stop with same-run evidence; do not tune defaults in this gate |
| Non-timeout provider runtime error appears | provider runtime operator / future calibration controller | Stop with same-run evidence; do not retry or reclassify as endpoint availability |
| Provider runtime residual narrows to subset chapters/operations | future provider-runtime calibration owner | Controller decides next scoped gate |
| Content contract or audit-rule blocker appears | future chapter/content calibration owner | Only after provider runtime is no longer first blocker |
| Safety violation appears | controller | Stop immediately and open separate remediation gate |

## 9. Decision

**CONTROLLER JUDGMENT: ACCEPT PLAN**

Next entry after accepted local checkpoint: assign an evidence executor to run the accepted plan's preflight, presence-only readiness check, and at most one default-budget live command if readiness passes.
