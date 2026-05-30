# MVP Gate 4 Slice 4D Provider Construction Aggregate Controller Judgment

日期：2026-05-30
角色：phaseflow / gateflow controller
Gate：`MVP Gate 4 Slice 4D aggregate review gate`
结论：accepted local checkpoint

## Scope

本 aggregate judgment 覆盖 provider construction work unit：

- Plan accepted commit：`b688d30`
- 4D1 provider factory commit：`26203d3`
- 4D2 CLI provider wiring commit：`ab0590a`
- 4D3 docs/control sync commit：`4d0c19f`

审查范围为 typed LLM env config、Service-owned `openai_compatible` provider factory、CLI `analyze --use-llm` wiring、相关 tests 和 docs/control truth sync。

## Aggregate Reviews

- MiMo：`docs/reviews/mvp-gate4-provider-construction-aggregate-review-mimo-20260530.md`
- GLM：`docs/reviews/mvp-gate4-provider-construction-aggregate-review-glm-20260530.md`

MiMo verdict：`PASS`

GLM verdict：`PASS`

无 blocking findings。

## Controller Validation

已由 controller 重新执行：

```text
git diff --check
```

结果：passed。

```text
uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py -q
```

结果：`125 passed in 1.19s`。

Prior controller / worker validations already recorded full regression:

- 4D1：`1101 passed`, coverage `91.75%`
- 4D2：`1106 passed`, coverage `91.76%`
- 4D3：`1106 passed`, coverage `91.76%`

No runtime files changed after 4D3 commit. Aggregate review added review artifacts only; targeted regression and whitespace check were sufficient at this checkpoint.

## Accepted Facts

1. `fund-analysis analyze --use-llm` is now an explicit opt-in provider-backed Route C path.
2. Default `fund-analysis analyze` and `fund-analysis checklist` remain deterministic and do not read LLM env or construct provider clients.
3. Provider config is typed env config in `fund_agent/config/llm.py`.
4. Provider factory is Service-owned in `fund_agent/services/llm_provider.py`.
5. MVP provider protocol is `openai_compatible` HTTP chat-completions over existing `httpx`; no vendor SDK, no default vendor/model/base URL.
6. CLI builds provider clients only in the `--use-llm` branch and calls `FundAnalysisService.analyze_with_llm(...)`.
7. Missing/invalid config and construction failure fail before Service call with exit code `1` and empty stdout.
8. Provider runtime failure, writer/auditor blocked status, partial orchestration and incomplete final assembly fail closed without deterministic fallback.
9. Quality gate block/not-run still exits `2`.
10. Tests use fake env mappings, `httpx.MockTransport`, monkeypatch and test doubles; no live provider/key/network tests.
11. Docs/control truth now describe 4D1/4D2 as accepted current facts and keep Host/Agent/dayu, retry/backoff, provider fallback, live smoke, multi-model split, chapter 0/7 LLM polish and Evidence Confirm as future residuals.

## Residuals

- Provider runtime error CLI message prefix can be polished in a future CLI diagnostics gate.
- `build_chapter_llm_clients()` broad construction wrapper can be revisited in a future provider polish gate.
- `OpenAICompatibleChapterLLMClient` / provider public export surface can be tightened in a future API consistency gate.
- Retry/backoff, provider fallback, live provider smoke, multi-model writer/auditor split, chapter 0/7 LLM polish, Evidence Confirm, Host/Agent/dayu Gate 5 and full `FundToolService` remain future gates.
- Unrelated untracked workspace files remain outside accepted evidence.

## Decision

MVP Gate 4 Slice 4D provider construction is accepted locally.

This does not authorize push, PR, merge, release, golden promotion or marking MVP complete. It only accepts the local provider-backed `--use-llm` path and docs/control sync.

## Next Entry Point

`MVP Gate 4 closeout / ready-to-open-draft-PR readiness reconciliation gate`

Recommended next controller action:

1. Reconcile Gate 4A/4B/4C/4D accepted commits and artifacts.
2. Update `docs/current-startup-packet.md` and `docs/implementation-control.md` from `aggregate review gate` to Gate 4 closeout / readiness reconciliation.
3. Decide whether to proceed to ready-to-open-draft-PR locally or continue with Gate 5/future residuals.
