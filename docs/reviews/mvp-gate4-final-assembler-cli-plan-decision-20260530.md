# MVP Gate 4 final assembler + CLI plan decision

日期：2026-05-30

角色：Gateflow / phaseflow controller。本文是 plan acceptance decision，不是 implementation evidence。

## Verdict

**PLAN ACCEPTED WITH CONTROLLER AMENDMENTS**

`docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md` 可作为 Gate 4 implementation source plan。MiMo 与 DS plan review 均为 PASS；MEDIUM findings 不阻断 plan acceptance，但以下 controller amendments 对 implementation worker 有约束力。

## Review inputs

- Plan: `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- MiMo review: `docs/reviews/mvp-gate4-final-assembler-cli-plan-review-mimo-20260530.md`
- DS review: `docs/reviews/mvp-gate4-final-assembler-cli-plan-review-ds-20260530.md`
- Current truth: `docs/current-startup-packet.md`
- Design truth: `docs/design.md` §5.4 / §5.4.1
- Gate 3 accepted judgment: `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md`

## Accepted implementation sequence

Gate 4 must be implemented in reviewed slices:

1. **Slice 4A: Service final assembler**
   - New Service-owned `final_chapter_assembler.v1`.
   - Deterministic chapter 7 assembly from existing `FinalJudgmentDecision`.
   - Deterministic chapter 0 assembly from accepted conclusions only.
   - No CLI changes in this slice.

2. **Slice 4B: Service LLM analyze use case**
   - Add explicit Service use case around existing `_run_analysis_core()`, Gate 3 orchestrator and Gate 4 assembler.
   - No CLI changes in this slice.

3. **Slice 4C: CLI `--use-llm` opt-in**
   - Default `analyze` and `checklist` behavior must remain unchanged.
   - If provider construction is not accepted, `--use-llm` must fail closed.

4. **Slice 4D: production LLM provider construction**
   - Not accepted by this plan for direct implementation.
   - Requires a separate provider-specific plan/review gate before implementation.

## Controller amendments

### A1. Quality gate exception path

`FundAnalysisService.analyze_with_llm()` must preserve existing `analyze()` quality gate blocking behavior:

- `QualityGateBlockedError` and `QualityGateNotRunBlockedError` from the deterministic core must propagate unchanged.
- CLI handling for those errors must keep the existing deterministic exit/status behavior.
- Final assembler incomplete/blocked policy applies only after deterministic core passes far enough to produce structured data and final judgment and Gate 3 orchestration returns partial/blocked.

### A2. Slice 4B / 4C do-not-edit boundaries

Slice 4B must not edit:

- `fund_agent/fund/analysis/final_judgment.py`
- `fund_agent/fund/analysis/checklist.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/audit/`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/ui/cli.py`

Slice 4C must not edit:

- `fund_agent/fund/`
- `fund_agent/services/fund_analysis_service.py` internals beyond calling the accepted public Service API from CLI-facing code.
- `derive_final_judgment()` or any final judgment semantic path.

If implementation requires violating these lists, stop and return to controller.

### A3. CLI provider unavailable path

Until Slice 4D is separately accepted, Slice 4C must use a single explicit fail-closed path:

- Introduce or reuse a clearly named CLI/helper boundary such as `_build_llm_clients_or_fail()`.
- In the absence of accepted provider construction, that helper must raise a typed/local runtime error with a clear message like `LLM provider 未配置/未实现`.
- CLI must catch that path and exit `1` without calling `analyze_with_llm()` and without outputting deterministic report markdown.
- No fake writer/auditor client may be passed from production CLI.

### A4. Chapter 0 preferred_lens handling

Chapter 0 assembler must not re-apply `preferred_lens`, ITEM_RULE or fund type rules. Lens/fund-type specialization is already encoded upstream in accepted chapter conclusions. Gate 4 can only consume those conclusions and deterministic final judgment output.

### A5. Chapter 0 truncation quality guard

Slice 4A tests must include at least one case where accepted conclusions are truncated or sparse. Expected behavior:

- no invented facts;
- no new numeric values or thresholds absent from accepted conclusions;
- explicit fallback or informational issue when a chapter 0 required item cannot be safely compressed.

If output quality is materially poor despite correctness, record a residual rather than widening Gate 4 inputs.

### A6. Chapter 7 core basis

Chapter 7 must not only rely on opaque internal rule messages when accepted conclusions provide concrete supporting context. Implementation should combine:

- `FinalJudgmentDecision.reasons` as authoritative rule basis;
- short snippets from existing chapter 1-6 accepted conclusions as supporting narrative;
- `developer_override` source and conflict reasons where present.

This does not authorize changing `FinalJudgmentDecision` or deriving a new judgment.

### A7. Chapter 0 current action typed source

The preferred implementation is to avoid brittle markdown parsing for current action. Slice 4A may add a Service-layer typed field to a new Gate 4-local chapter 7 summary object, or store typed action in `FinalChapterAssemblyResult`, while keeping `AcceptedChapterConclusion` from Gate 3 unchanged unless a review explicitly accepts changing that shared type.

If implementation chooses markdown parsing instead, parsing failure must create a blocking/incomplete issue, not silent fallback.

### A8. Generation order vs render order

Gate 4 generation order is:

```text
chapters 1-6 accepted drafts/conclusions -> chapter 7 -> chapter 0
```

Final report render order is:

```text
chapter 0 -> chapters 1-6 -> chapter 7
```

Tests must assert render order.

## Residuals

- Slice 4D provider construction remains a separate future gate unless the controller explicitly opens it.
- LLM polish or LLM audit of chapter 0/7 remains out of scope for Slice 4A.
- Evidence Confirm / E2 source verification remains out of scope.
- Host/Agent/dayu integration remains deferred to Route C Gate 5.

## Next entry point

`MVP Gate 4 Slice 4A: Service final_chapter_assembler implementation gate`

Allowed initial implementation files for Slice 4A:

- `fund_agent/services/final_chapter_assembler.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/README.md`
- implementation evidence artifact under `docs/reviews/`

No `fund_agent/fund/`, CLI, Host/Agent/dayu, golden, score, quality gate or final judgment semantic files are authorized for Slice 4A.
