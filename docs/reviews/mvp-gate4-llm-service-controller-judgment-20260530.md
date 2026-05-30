# MVP Gate 4 Slice 4B Service analyze_with_llm controller judgment

日期：2026-05-30
角色：phaseflow / gateflow controller
Gate：`MVP Gate 4 Slice 4B: Service analyze_with_llm implementation gate`
分类：`heavy`

## Verdict

**ACCEPTED LOCALLY**

Slice 4B 已在 Service 层新增显式 `FundAnalysisService.analyze_with_llm(...)` 用例和 `FundLLMAnalysisResult` typed result。实现复用现有 `_run_analysis_core()`，通过显式注入的 `ChapterOrchestratorLLMClients` 调用 Gate 3 `orchestrate_chapters()`，并始终调用 Slice 4A `assemble_final_chapters()` 形成第 0/7 章总装结果。

本裁决不授权 CLI `--use-llm`、生产 LLM provider、Host/Agent/dayu、final judgment 语义、quality/FQ、golden/score/snapshot/manifest 或 fixture promotion 变更。

## Evidence

- Implementation evidence: `docs/reviews/mvp-gate4-llm-service-implementation-evidence-20260530.md`
- MiMo review: `docs/reviews/mvp-gate4-llm-service-implementation-review-mimo-20260530.md`
- GLM review: `docs/reviews/mvp-gate4-llm-service-implementation-review-glm-20260530.md`
- Accepted plan: `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- Plan decision: `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- Slice 4A controller judgment: `docs/reviews/mvp-gate4-final-assembler-slice4a-controller-judgment-20260530.md`

## Review Judgment

MiMo verdict: PASS. No blocking or medium findings.

GLM verdict: PASS. No blocking, critical or medium findings.

Controller disposition:

- MiMo O1 (`FundLLMAnalysisResult` module-level `__all__` absent): rejected as non-blocking consistency observation because the module has no existing `__all__` convention and `fund_agent/services/__init__.py` exports the public type.
- MiMo O2 (`command_source` override not explicitly tested): deferred as low-risk; `replace(request, command_source="analyze")` is the accepted plan behavior for this analyze-only use case.
- GLM L1 (result omits intermediate deterministic analysis products): accepted as non-blocking residual; the plan allowed the smaller result as long as `structured_data`, `final_judgment_decision`, quality gate status and final assembly are preserved.
- GLM L2 (Gate 3/4 are synchronous functions): accepted as future residual for provider/Host/dayu gates; current Gate 3/4 functions are intentionally synchronous and provider-agnostic.

## Validation

Controller re-ran:

```text
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/services/test_fund_analysis_service_llm.py
All checks passed!
```

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py -q
7 passed
```

```text
uv run pytest tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q
44 passed
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1061 passed, total coverage 91.73%
```

```text
git diff --check
clean
```

## Boundary Confirmation

- No CLI files changed.
- No production LLM provider construction was added.
- No Host/Agent/dayu package, dependency or runtime integration was added.
- No Fund primitive, final judgment, quality gate, FQ0-FQ6, score, snapshot, golden fixture, golden answer, manifest or promotion state was changed.
- `llm_clients` is keyword-only and explicit; no `extra_payload` path was introduced.
- Partial/blocked Gate 3 output remains fail-closed through `FinalChapterAssemblyResult` and `FundLLMAnalysisResult.report_markdown`.

## Next Entry Point

`MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate`

Slice 4C may wire the CLI flag to the accepted Service API, but until Slice 4D provider construction is separately accepted, production CLI must fail closed with a clear "LLM provider 未配置/未实现" path and must not call `analyze_with_llm()` with fake clients or silently fall back to deterministic markdown.
