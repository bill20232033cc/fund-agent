# MVP Gate 3 chapter_orchestrator controller judgment

日期：2026-05-30

角色：Gateflow / phaseflow controller。结论只覆盖本地 workspace；未 push、未 PR、未 merge、未 release、未 golden promotion。

## Verdict

**ACCEPTED LOCALLY**

`MVP Gate 3: chapter_orchestrator` 已完成本地 accepted。Service 层新增 `chapter_orchestrator.v1` write-audit-repair façade，能够通过显式 contract 消费 Gate 1 `ChapterFactProjection` / `StructuredFundDataBundle` 和 Gate 2 writer/auditor primitives，仅生成模板第 1-6 章 accepted conclusions，供未来 Gate 4 final assembly 使用。

## Accepted scope

- 新增 `fund_agent/services/chapter_orchestrator.py`。
- 更新 `fund_agent/services/__init__.py` 导出 Gate 3 public API。
- 新增 `tests/services/test_chapter_orchestrator.py`。
- 同步 `fund_agent/README.md` 和 `tests/README.md` 当前实现事实。
- 更新 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`，将 Gate 3 标记为 accepted locally，并把下一入口切到 Gate 4。

## Boundary decision

- Gate 3 只生成模板第 1-6 章，不生成第 0/7 章。
- Gate 3 不构造生产 LLM provider，不读取 env/config provider，不提供默认 fake pass。
- Gate 3 不读取文档仓库、PDF、cache、source helper、downloader 或 parser。
- Gate 3 不接入 Host/Agent/dayu，不创建 `fund_agent/host` 或 `fund_agent/agent`。
- Gate 3 不修改 deterministic `fund-analysis analyze/checklist` 默认生产路径。
- Gate 3 不修改 golden fixture / golden answer / manifests / score / snapshot / quality gate / FQ0-FQ6 / final judgment。
- 显式参数保持 typed dataclass / keyword-only contract；未使用 `extra_payload`。

## Review summary

- Plan accepted at `docs/reviews/mvp-gate3-chapter-orchestrator-plan-decision-20260530.md` after MiMo + DS plan reviews and re-reviews.
- Implementation evidence: `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-evidence-20260530.md`.
- Implementation reviews:
  - MiMo: `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-mimo-20260530.md` — PASS.
  - DS: `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-ds-20260530.md` — PASS with MEDIUM maintainability findings.
- Review fix evidence: `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-evidence-20260530.md`.
- Fix re-reviews:
  - MiMo: `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-mimo-20260530.md` — PASS.
  - DS: `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-ds-20260530.md` — PASS.

The review fix added typed `ChapterRepairDecision.stop_reason`, removed the prior Chinese reason-text dependency for `repair_budget_exhausted`, and centralized stop reason derivation in `_decide_repair()`.

## Validation

Controller reran:

```text
git diff --check
```

Result: clean.

```text
uv run ruff check .
```

Result: `All checks passed!`

```text
uv run pytest tests/services/test_chapter_orchestrator.py -q
```

Result: `30 passed`.

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
```

Result: `51 passed`.

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Result: `1040 passed`; total coverage `91.73%`.

## Residuals

- `patch` repair remains mapped to budget-bounded full regenerate because Gate 2 has no typed patch API.
- `partial` orchestration result is not a complete report. Gate 4 must decide reject/degrade/incomplete assembly behavior.
- Final chapter assembler, chapter 0 assembly, chapter 7 final judgment assembly and CLI `--use-llm` are not implemented.
- Production LLM provider construction remains deferred.
- Evidence Confirm / E2 source verification and chapter 5 cross-period source hardening remain deferred.
- Host/Agent/dayu integration remains deferred to Route C Gate 5.

## Next entry point

`MVP Gate 4: final_chapter_assembler + chapter 0 + CLI --use-llm plan gate`

Gate 4 must start with planning/review. It must not treat `ChapterOrchestrationResult(status="partial")` as a complete report without an explicit accepted policy, and must keep deterministic `analyze/checklist` available unless a later gate explicitly changes that behavior.
