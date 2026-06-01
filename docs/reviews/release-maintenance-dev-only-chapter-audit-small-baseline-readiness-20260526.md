# Dev-only Chapter Audit x Small Baseline Readiness

> Date: 2026-05-26
> Role: Controller
> Gate: dev-only chapter audit x small baseline corpus evaluation
> Verdict: READY_FOR_DEV_ONLY_AUDIT_RUN

## Startup State

- Current phase: `release maintenance`
- Current accepted gate: Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation
- Current local HEAD at readiness check: `9f17b6c`
- Worktree status: clean
- Product-flow status: no renderer, FQ0-FQ6, Service/CLI, Host/Agent, Dayu, repository/source-helper integration is authorized for this gate.

## Accepted Implementation Check

| Requirement | Evidence | Status |
|---|---|---|
| CHAPTER_CONTRACT sidecar accepted | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md` | Accepted |
| Dev-only report-writing audit accepted | `fund_agent/fund/report_writing_audit.py`; implementation controller judgment | Accepted |
| Focused tests accepted | Controller judgment records `19 passed` for sidecar/audit focused tests | Accepted |
| Adjacent tests accepted | Controller judgment records `147 passed` for template/evidence/validator adjacent tests | Accepted |
| README / design / control doc synced | `fund_agent/fund/README.md`, `tests/README.md`, `docs/design.md`, `docs/implementation-control.md` updated in accepted commits | Accepted |
| Default product behavior unchanged | Controller judgment boundary: no renderer, FQ0-FQ6, Service/CLI, Host/Agent, Dayu, repository/source-helper integration | Accepted |

## Available Small Baseline Candidates

The candidate status below is inherited from accepted evidence only. This gate must not promote any candidate to durable baseline or `scoring_ready`.

| fund_code | report_year | fund_type_slot | current status | usable in this gate | Notes |
|---|---:|---|---|---|---|
| `004393` | 2024 | `active_fund` | `repository_verified`; not `scoring_ready`; not baseline | Yes | Clean candidate. Must cover Chapter 3 active-fund turnover/style-consistency audit. |
| `004194` | 2024 | `enhanced_index` | `repository_verified`; not `scoring_ready`; not baseline | Yes | Clean candidate. Current sidecar has Chapter 2 deferred `config_only`; no material audit expected unless explicit surrogate tests config-only behavior. |
| `006597` | 2024 | `bond_fund` | `repository_verified`; not `scoring_ready`; not baseline | Yes | Clean candidate. Current sidecar has Chapter 6 deferred `config_only`; no material audit expected unless explicit surrogate tests config-only behavior. |
| `110020` | 2024 | `index_fund` | repository evidence but fallback-blocked by `unknown_upstream_failure_category`; not `scoring_ready` | Excluded from clean denominator | May be listed as source/data residual only. |
| `017641` | 2024 | `qdii_fund` | repository evidence but fallback-blocked by `unknown_upstream_failure_category`; not `scoring_ready` | Excluded from clean denominator | May be listed as source/data residual only. |
| `007721` | 2024 | `fof_fund` attempt | `data_gap` / type gap; current accepted evidence classifies QDII-FOF as `qdii_fund` | No | FOF remains unfulfilled. |
| `017970` | 2024 | `fof_fund` attempt | `data_gap` / type gap plus fallback-blocked source status | No | FOF remains unfulfilled. |

## Gate B Run Shape

Allowed:

- Use explicit, manually assembled `ReportEvidenceBundle`, records, and `ChapterDraftSurrogate` inputs.
- Use scratch output under `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/` or ignored `reports/` run paths.
- Track only a concise summary artifact and controller decision.
- Cover at least three fund_type slots using `004393`, `004194`, and `006597`.
- Materially evaluate active-fund Chapter 3, because it is the only current material sidecar/audit contract.
- Report Chapter 2 / Chapter 6 as deferred `config_only` coverage, not as material audit proof.

Forbidden:

- Do not call `fund-analysis analyze` or `fund-analysis checklist`.
- Do not modify or invoke renderer integration, FQ0-FQ6 policy, Service/CLI defaults, Host/Agent/dayu, repository/PDF/cache/source helpers, downloaders, or production extractors.
- Do not promote any sample to durable fixture, `scoring_ready`, or `accepted_baseline`.
- Do not commit large scratch JSON/JSONL outputs.
- Do not push, create PR, merge, or perform GitHub mutation.

## Gate A Decision

Gate A passes for a dev-only audit run. The run must be interpreted narrowly:

- active-fund Chapter 3 can test the executable material contract;
- enhanced-index Chapter 2 and bond Chapter 6 can test candidate routing / deferred sidecar visibility only;
- index, QDII, and FOF remain residuals and cannot be used as clean evidence for renderer escalation.

## Residual Risks Entering Gate B

- Current dev-only audit material enforcement is only active-fund Chapter 3.
- Small baseline clean denominator lacks clean `index_fund`, `qdii_fund`, and pure `fof_fund` samples.
- Prior small baseline evidence found combined multi-bundle JSONL validator ownership limitations; per-sample JSONL is safer for this run.
- Records-mode audit is intentionally narrow and fail-closed.
- Duplicate occurrence-level `issue_id` remains deferred.

## Verifier Matrix

| Gate | Required evidence |
|---|---|
| Gate B run | scratch path, per-sample summary, active Chapter 3 issue taxonomy, no large tracked outputs |
| Gate C taxonomy | 7-category issue taxonomy with sample evidence and renderer-blocking decision |
| Gate D escalation | explicit next gate decision with proof or refusal for renderer minimal integration |
| Closeout | control doc update, closeout artifact, validation commands, clean local commit, no GitHub mutation |
