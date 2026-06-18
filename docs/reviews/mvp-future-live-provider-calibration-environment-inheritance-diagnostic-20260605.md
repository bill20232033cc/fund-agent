# MVP Future Live Provider Calibration — Environment Inheritance Diagnostic

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Future live provider calibration evidence gate`
- Role: controller diagnostic after accepted `environment_blocked` evidence
- Related evidence checkpoint: `79fd068`

This diagnostic is not a live provider probe and does not authorize rerunning the evidence gate. It records only presence booleans for environment inheritance troubleshooting.

## 2. Controller Shell Presence

Command printed only presence booleans and no values.

```text
FUND_AGENT_LLM_PROVIDER: absent
FUND_AGENT_LLM_MODEL: absent
FUND_AGENT_LLM_BASE_URL: absent
FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
effective_api_key_value: absent
```

## 3. Tmux Global Environment Presence

Command parsed `tmux show-environment -g` locally and printed only key presence booleans, not values.

```text
tmux_global_FUND_AGENT_LLM_PROVIDER: absent
tmux_global_FUND_AGENT_LLM_MODEL: absent
tmux_global_FUND_AGENT_LLM_BASE_URL: absent
tmux_global_FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
tmux_global_FUND_AGENT_LLM_API_KEY: absent
```

## 4. Controller Interpretation

The latest evidence executor shell failed presence-only readiness because required provider config was absent. This follow-up diagnostic shows the controller shell and tmux global environment also lack the required `FUND_AGENT_LLM_*` presence.

Next entry remains unchanged: fix environment inheritance outside the repository or provide an execution shell that inherits the required LLM provider/model/base-url/API key configuration, then rerun the accepted gate from presence-only readiness after controller authorization.

No source, tests, config, runtime defaults, provider endpoint/model/timeout, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, PR, push or external state was changed by this diagnostic.
