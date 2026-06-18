# MVP Future Live Provider Calibration — Env Source Presence Diagnostic

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Future live provider calibration evidence gate`
- Role: controller diagnostic
- Related blocked evidence checkpoint: `79fd068`
- Related prior diagnostic checkpoint: `29e896f`

This diagnostic prints only variable-name presence and file-level presence. It does not print provider values, model values, base URL values, API key values, Authorization headers, full env dumps, raw prompts or provider responses.

## 2. Repository Dotenv Presence

Checked common repository/workspace dotenv paths:

- `.env`
- `.env.local`
- `.envrc`
- `workspace/.env`
- `workspace/.env.local`
- `workspace/config/.env`
- `workspace/config/.env.local`

Result: no checked path produced a `FUND_AGENT_LLM_*` variable-name presence report. No values were printed.

## 3. User Shell Config Presence

Checked existing user shell config files for variable-name presence only:

```text
/Users/maomao/.zshrc: llm_names=absent
/Users/maomao/.zprofile: llm_names=absent
/Users/maomao/.profile: llm_names=absent
```

## 4. Current Process Presence

```text
current_process_presence
FUND_AGENT_LLM_PROVIDER:absent
FUND_AGENT_LLM_MODEL:absent
FUND_AGENT_LLM_BASE_URL:absent
FUND_AGENT_LLM_API_KEY_ENV_VAR:absent
FUND_AGENT_LLM_API_KEY:absent
```

## 5. Tmux Global Presence

```text
tmux_global_presence
FUND_AGENT_LLM_PROVIDER:absent
FUND_AGENT_LLM_MODEL:absent
FUND_AGENT_LLM_BASE_URL:absent
FUND_AGENT_LLM_API_KEY_ENV_VAR:absent
FUND_AGENT_LLM_API_KEY:absent
```

## 6. Controller Interpretation

The accepted evidence checkpoint `79fd068` remains correctly classified as `environment_blocked`. The current controller shell, tmux global environment, common repository dotenv files and existing user shell startup files do not expose the required `FUND_AGENT_LLM_*` presence.

Next entry remains unchanged: fix environment inheritance outside the repository or provide an execution shell that inherits the required LLM provider/model/base-url/API key configuration, then rerun the accepted gate from presence-only readiness after controller authorization.

This diagnostic does not authorize live provider execution, endpoint probes, provider/default/runtime/budget changes, Chapter acceptance calibration, Agent runtime, multi-year evidence runtime, score-loop, golden/readiness, PR/push/release or fail-closed relaxation.
