# Dev-only Chapter Audit x Small Baseline Taxonomy Decision

> Date: 2026-05-26
> Role: Controller
> Gate: issue taxonomy and contract tuning decision
> Verdict: CONTRACT_TUNING_REQUIRED_BEFORE_RENDERER_INTEGRATION

## Evidence Inputs

- Gate A readiness: `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-readiness-20260526.md`
- Gate B run: `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-run-20260526.md`
- Scratch run path: `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/`
- Accepted sidecar judgment: `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md`

## Taxonomy Summary

| Category | Evidence sample | Immediate fix? | More evidence needed? | Blocks renderer minimal integration? | Controller decision |
|---|---|---|---|---|---|
| data/source extraction | `004194` Chapter 2 and `006597` Chapter 6 only have deferred `config_only` sidecar requirements; `110020` / `017641` fallback category unresolved. | No in this gate | Yes before broader chapter coverage or durable baseline | No for active-only design; yes for broader renderer claims | Defer to data extraction / more chapter coverage gates. |
| evidence traceability | `004393` reviewed-turnover positive control passes only with resolvable anchor. | No | No for active Chapter 3 slice | No | Current anchor contract is adequate for this slice. |
| chapter contract too strict | `004393-active-ch3-compatible-datagap-wording-false-positive-probe.json` shows accepted insufficient-evidence question wording triggers `unsupported_stability_claim`. | Yes | No; scratch reproduces the defect directly | Yes for renderer implementation | Accept as blocker; tune contract matcher before renderer integration. |
| chapter contract too loose | Missing evidence + stability claim produces `required_evidence_missing` and `unsupported_stability_claim`; missing data-gap wording produces `insufficient_evidence_wording_missing`. | No | Yes with more fund types / chapters | No | No looseness observed in current slice. |
| report writing/template gap | Active Chapter 3 renderer/writer will need deterministic insufficiency wording if evidence is missing. | Not as code in this gate | No for design; yes for implementation | Yes for implementation | Renderer gate must remain design-only until tuning passes. |
| validator schema issue | This run uses `audit_report_writing_bundle`; prior combined JSONL validator limitation remains separate. | No | Yes if combined multi-bundle JSONL is reused | No | Not blocker for dev-only audit API. |
| fund-type taxonomy issue | FOF attempts `007721` / `017970` remain QDII-FOF/type-gap residuals. | No | Yes before durable baseline | No for active-only design | Defer to taxonomy/corpus gate. |

## Accepted Contract Tuning Finding

The current phrase matcher is too strict for a valid next-minimum-validation question.

Direct evidence:

- Scratch file: `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-compatible-datagap-wording-false-positive-probe.json`
- Draft text: `当前证据不足，不能据此判断风格稳定、风格一致或言行一致；下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，风格稳定性和言行一致性判断是否仍成立？`
- Actual issue: `unsupported_stability_claim=1`
- Expected behavior: no unsupported positive claim, because the phrase appears inside a question after explicit insufficient-evidence wording.

Decision:

- Accepted as `chapter contract too strict`.
- Must be fixed in `fund_agent/fund/report_writing_audit.py` before any renderer minimal integration implementation.
- The fix must not weaken detection for actual positive claims such as `基金经理风格稳定，言行一致。`

## Required Fix Scope

Allowed files:

- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/test_report_writing_audit.py`
- Gate B / Gate C review artifacts if evidence needs appending

Required tests:

- The exact false-positive wording above must pass with compatible `data_gap`.
- Existing positive claim with only `data_gap` must still emit `unsupported_stability_claim`.
- Existing missing evidence and missing wording tests must remain green.

Non-goals:

- Do not change renderer, Service/CLI, FQ0-FQ6, Host/Agent/dayu, source/PDF/cache helpers, or product defaults.
- Do not broaden Chapter 2 / Chapter 6 material enforcement.
- Do not promote any baseline fixture.

## Escalation Decision

The next immediate gate is `contract tuning implementation`.

Renderer minimal integration design is not yet accepted as the next implementation step. It may be opened after tuning and re-running the active Chapter 3 dev-only audit controls, if the false-positive blocker is closed and no new material false positives appear.
