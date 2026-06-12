# CI Quality Warn-only Planning Gate Plan

Date: 2026-06-12

Role: controller-authored planning artifact

Gate: `CI quality warn-only planning gate`

Classification: `standard`

Accepted input:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md`
- Checkpoint `70b3f06`
- Control-sync checkpoint `84afd36`

## 1. Objective

Plan how CI/readiness should treat `quality_gate_status=warn` and nonzero `quality_gate_issues` after the accepted single-sample controlled live annual-period narrative evidence.

This planning gate answers:

1. What is the current truth-source policy for `quality_gate_policy=block` vs `warn`?
2. What should be required before any future readiness claim when live evidence exits `0` but quality gate status is `warn`?
3. What future implementation/evidence gate should run next without weakening FQ0-FQ6, changing source policy, or treating warn as release-ready?

## 2. Current Facts

| Fact | Source type | Source |
|---|---|
| Production `analyze` default uses `quality_gate_policy=block`. | truth-doc fact | `docs/design.md` states `quality_gate_policy=block` is default and `block` / `not_run` fail closed. |
| `quality_gate_policy=warn` permits output but remains a data-quality warning. | truth-doc fact | `docs/design.md` states warn allows continued output and is consumed by final judgment; it is not release/readiness proof. |
| Annual-period renderer exposes `quality_gate_status` in the formal report. | repo fact candidate for next evidence gate | `fund_agent/fund/template/annual_period_renderer.py` and tests appear to cover `quality_gate_status=warn` rendering; next evidence gate must verify. |
| CLI emits structured quality gate status / issue count. | repo fact candidate for next evidence gate | `fund_agent/ui/cli.py` appears to emit `quality_gate_status` and `quality_gate_issues`; CLI tests appear to cover warn/block/not-run stderr; next evidence gate must verify. |
| Golden readiness treats quality warn as not ready. | repo fact candidate for next evidence gate | `fund_agent/fund/golden_readiness_preflight.py` appears to contain explicit warn-derived readiness blocker text; next evidence gate must verify. |
| Accepted live evidence has `quality_gate_status=warn` and `quality_gate_issues=3`. | accepted controller fact | `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md`. |
| Accepted live evidence remains `NOT_READY`. | accepted controller fact | `docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md`. |

## 3. Non-goals

This planning gate does not authorize:

- source, tests, runtime, README, design or config changes
- FQ0-FQ6 severity changes
- quality gate semantics weakening
- treating `warn` as release-ready
- live/network/PDF/provider/LLM/analyze/checklist/golden/readiness/release/PR commands
- reading raw generated report/PDF/cache bodies
- cleanup/archive/delete/import/ignore actions
- PR/push/merge/mark-ready/release external state

## 4. Proposed Next Gate

Recommended next gate:

`CI quality warn-only evidence gate`

Type: docs/reviews-only evidence/disposition gate.

Purpose:

- prove current code and docs already preserve the required distinction:
  - production default `block`
  - `warn` may be used for controlled evidence/smoke runs
  - `warn` cannot prove release/readiness
  - `block` / `not_run` remain fail-closed where policy is `block`
- classify whether any implementation is actually required before further release-readiness work
- route remaining quality warning issues to a later root-cause/evidence gate rather than weakening gate policy

Expected outcome:

- likely `ACCEPT_NOT_READY_NO_CODE_CHANGE` if static evidence confirms current semantics
- next entry after evidence should be either:
  - `Quality warning issue root-cause planning gate` if the three warning issues need itemized owners before readiness
  - or `Additional EID live sample planning gate` only if user separately authorizes more live coverage

## 5. Evidence Matrix For Next Gate

The next evidence gate should collect static, no-live evidence only:

| Check | Evidence source | Acceptance |
|---|---|---|
| Default policy remains `block` | `docs/design.md`; `fund_agent/services/execution_contract.py`; `fund_agent/services/fund_analysis_service.py`; CLI option defaults | PASS if default request/contract path still defaults to `block` |
| Warn path remains explicit | CLI/service request construction and tests | PASS if `warn` is explicit and not silently used as production default |
| Block/not-run remains fail-closed under block policy | Service exception path and CLI tests | PASS if tests cover structured block/not-run failures and exit code behavior |
| Warn is not readiness pass | `golden_readiness_preflight.py`; design/control docs; current accepted evidence | PASS if warn is classified as blocker/residual for readiness |
| Annual-period report status is transparent | annual period renderer/tests and accepted live evidence | PASS if report exposes `quality_gate_status` instead of hiding it |
| Release/readiness remains `NOT_READY` | current control docs | PASS if next control state preserves `NOT_READY` |

Allowed commands for the next gate:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
rg -n "quality_gate_policy|quality_gate_status|quality_gate_issues|QualityGate|quality gate status=warn" fund_agent tests docs README.md
```

Optional no-live deterministic checks if the evidence owner decides static evidence is insufficient:

```bash
uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_annual_period_report.py -q
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py fund_agent/fund/golden_readiness_preflight.py fund_agent/fund/template/annual_period_renderer.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_annual_period_report.py
```

These optional checks are limited to no-live deterministic unit tests and lint. They do not authorize analyze/checklist/golden-readiness-preflight runtime commands, generation of readiness artifacts, live/provider/PDF access, or treating a passing test run as release/readiness proof.

## 6. Residual Owner Table

| Residual | Owner | Next handling |
|---|---|---|
| `quality_gate_status=warn`; `quality_gate_issues=3` | release/readiness owner + quality gate owner | `CI quality warn-only evidence gate`, then quality warning issue root-cause planning if still unresolved |
| Single accepted live sample only | evidence/release owner | additional EID live sample gate only by separate live authorization |
| Provider/LLM untested | provider/runtime owner | live provider / LLM acceptance gate only by separate live authorization |
| Current repo fact candidates not yet verified in this planning gate | controller/evidence owner | next evidence gate must classify `truth-doc fact` / `repo fact` / `accepted controller fact` |
| Artifact cleanup/import/ignore not handled | artifact owner/controller | separate artifact-action gate only by explicit authorization |

## 7. Future Implementation Boundary If Evidence Finds A Gap

If the evidence gate finds a gap, a separate implementation gate must be opened before changing code.

Allowed future implementation candidates:

- docs-only CI/readiness policy note under `docs/reviews/`
- test-only assertion that `warn` is not treated as readiness pass
- minimal CLI/service test strengthening for existing warn/block/not-run semantics
- control-doc wording sync if current control surface drifts

Disallowed without separate heavy gate:

- changing FQ0-FQ6 severities
- changing `quality_gate_policy=block` default
- allowing `warn` to pass release/readiness
- changing final judgment semantics
- changing golden/readiness promotion semantics
- adding live CI
- provider/LLM execution

## 8. Required Reviews

Before accepting this plan:

- AgentDS plan review
- AgentMiMo plan review

Review focus:

- whether the plan preserves `NOT_READY`
- whether it avoids weakening quality gate semantics
- whether next gate should be evidence-only before implementation
- whether allowed commands stay no-live and deterministic
- whether residual owners are explicit

## 9. Acceptance Criteria

This planning gate can be accepted only if:

1. This plan is reviewed by DS and MiMo.
2. Controller judgment maps all findings.
3. `git status --short`, `git status --branch --short`, `git diff --name-only` and `git diff --check` are recorded.
4. Local accepted checkpoint contains only plan/review/controller artifacts.
5. Release/readiness remains `NOT_READY`.

## 10. Next Entry

If accepted:

`CI quality warn-only evidence gate`

Deferred entries:

- quality warning issue root-cause planning gate
- additional EID live sample gate
- live provider / LLM acceptance gate
- fixture/golden/readiness promotion gate
- cleanup/archive/delete/import/ignore artifact-action gate
- PR / push / merge / mark-ready external-state gate
