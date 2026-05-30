# MVP Gate 4 Slice 4C CLI --use-llm controller judgment

日期：2026-05-30
角色：phaseflow / gateflow controller
Gate：`MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate`
分类：`heavy`

## Verdict

**ACCEPTED LOCALLY**

Slice 4C 已为 `fund-analysis analyze` 增加显式 `--use-llm` opt-in 入口。由于 Slice 4D production LLM provider construction 尚未接受，当前生产 CLI 在调用 Service LLM 用例前 fail-closed：stderr 输出 `LLM provider 未配置/未实现`，退出码为 `1`，stdout 为空，不输出确定性 Markdown，不注入 fake clients，也不调用 `analyze_with_llm()`。

默认 `fund-analysis analyze` 和 `fund-analysis checklist` 行为保持不变；`checklist` 不接受 `--use-llm`。

## Evidence

- Implementation evidence: `docs/reviews/mvp-gate4-cli-use-llm-implementation-evidence-20260530.md`
- MiMo review: `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-mimo-20260530.md`
- GLM review: `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-glm-20260530.md`
- Gate 4 accepted plan: `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- Gate 4 plan decision: `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- Slice 4B controller judgment: `docs/reviews/mvp-gate4-llm-service-controller-judgment-20260530.md`

## Review Judgment

MiMo verdict: PASS. No blocking, critical or medium findings.

GLM verdict: PASS. No blocking, critical or medium findings.

Controller disposition:

- `_build_llm_clients_or_fail() -> NoReturn` is accepted for Slice 4C because the only allowed production behavior before provider construction is fail-closed. Slice 4D must change this signature only after an accepted provider-specific plan.
- The test-only fake `analyze_with_llm()` method is accepted as a guard proving production CLI does not call Service LLM while provider construction is absent.

## Validation

Controller re-ran:

```text
uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
uv run pytest tests/ui/test_cli.py -q
46 passed
```

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q
51 passed
```

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1064 passed, total coverage 91.74%
```

```text
git diff --check
clean
```

## Boundary Confirmation

- No Service internals changed.
- No Fund primitives changed.
- No final judgment, quality gate, FQ0-FQ6, score, snapshot, golden fixture, golden answer, manifest or promotion state changed.
- No production LLM provider, API key, env/config, model choice, SDK dependency, retry/timeout policy or network smoke was introduced.
- No Host/Agent/dayu package, dependency or runtime integration was introduced.
- No `extra_payload` path was introduced.

## Next Entry Point

`MVP Gate 4 Slice 4D: production LLM provider construction plan gate`

Slice 4D is not pre-authorized for direct implementation. It must start with provider-specific plan/review covering provider choice, config/env, typed client construction, failure semantics, tests without live network, and CLI wiring from `_build_llm_clients_or_fail()` to explicit `ChapterOrchestratorLLMClients`.
