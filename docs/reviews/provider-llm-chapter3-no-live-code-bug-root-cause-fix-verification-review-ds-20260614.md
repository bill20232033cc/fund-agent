# Provider/LLM Chapter 3 No-live Code-bug Root-cause/Fix Verification — Review DS — 2026-06-14

Role: DS-role review.

Target artifact: `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-evidence-procodex-20260614.md`

## Review Scope Compliance

| Scope item | Compliance | Notes |
|---|---|---|
| AGENTS.md, startup packet, implementation-control.md read | Yes | Used as truth/control baseline |
| Target evidence artifact read | Yes | Full body read |
| Prior retry controller judgment read | Yes | `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-controller-judgment-20260614.md` |
| Source/test snippets referenced by artifact only | Yes | runner.py:1399-1481, chapter_writer.py:910-992; read only to verify root-cause chain |
| No chapter bodies, raw prompts, provider payloads read | Yes | None accessed |
| No source/PDF/cache bodies read | Yes | None accessed |
| No live/provider/network/analyze/checklist/readiness/release/PR commands run | Yes | None executed |
| No source/tests/control/design modified | Yes | No modifications |
| No stage/commit/push/PR | Yes | None performed |

## 1. BLOCKED_NEEDS_CONTROLLER_DECISION Verdict Assessment

**Finding: Supported.**

The evidence correctly identifies the root cause of the remaining Chapter 3 pre-provider `ValueError` / `code_bug` failure. The root-cause chain is:

```
chapter_writer.py:_availability_for_required_output()  (line 987-992)
  → raises ValueError 当 typed required output item 有 when_evidence_missing 但 EvidenceAvailability 缺少对应 requirement
  → 传播至 build_chapter_writer_input()
  → runner.py 捕获为 exception
  → _terminal_from_exception() → "blocked_internal_code_bug"  (line 1414)
  → _failure_category_from_exception() → "code_bug"  (line 1481)
  → _stop_reason_from_exception() → "llm_exception"  (line 1439)
  → _exception_task() → status="failed", provider attempt count=0
```

Code inspection at `runner.py:1399-1481` confirms:
- `_terminal_from_exception()` maps any non-provider-runtime exception (including plain `ValueError`) to `"blocked_internal_code_bug"` (line 1414).
- `_failure_category_from_exception()` maps any non-provider-runtime exception to `"code_bug"` (line 1481).
- `_is_provider_runtime_exception()` only matches the five LLM provider exception types (lines 1455-1460); a plain `ValueError` does not match.

Code inspection at `chapter_writer.py:970-992` confirms:
- `_availability_for_required_output()` calls `evidence_availability.require()` at line 988.
- If that raises `ValueError` AND `item.when_evidence_missing is not None`, a new `ValueError` is re-raised at line 992.
- The call chain is `_typed_required_output_plan()` (line 915-928) → `_required_output_plan_item()` (line 931-967) → `_availability_for_required_output()` (line 970-992).

The BLOCKED verdict is legitimate: the semantic fix belongs in `fund_agent/fund/chapter_writer.py` (or companion typed sidecar files), and the worker correctly and conservatively assessed this as outside the scope inherited from the prior gate's "no scope expansion" constraint (`aabe308`). The worker's approach of identifying the root cause, demonstrating it with a red reproducer, and requesting controller authorization for write-set expansion aligns with this project's gateflow discipline.

## 2. Root-cause Classification Coherence

**Finding: Coherent.**

The artifact classifies as H3 (hybrid: typed mapping gap surfacing as pre-provider ValueError). The classification is internally consistent:

- **Provider attempt count 0**: The `ValueError` is raised during `build_chapter_writer_input()` → `_typed_required_output_plan()` → `_availability_for_required_output()`, all of which execute before any `write_chapter_tool` invocation. The temporary red reproducer independently confirms `writer.requests == []` passed before the failed assertion.

- **Typed required-output / availability gap as pre-provider ValueError**: When `EvidenceAvailability` is missing a requirement for a `RequiredOutputItem` that declares `when_evidence_missing`, the current code path can only raise `ValueError`. There is no writer-preflight `ChapterWriteIssue` / `status="blocked"` path for this specific case.

- **H2 (diagnostic-only) rejection is correct**: The bounded retry already has safe runtime metadata (`max_output_chars=12000`, `terminal_runtime_diagnostic_present=true`, `diagnostic_consistency_status=consistent`). The remaining `ValueError` is not a diagnostic projection gap — it is a real semantic gap in how `ChapterWriterInput` construction handles missing typed availability.

- **H5 rejection is correct**: The red reproducer uses a fake writer/auditor client with no provider/network call, which excludes fixture/provider-origin explanations.

No contradiction found in the classification.

## 3. Write-set Expansion Justification

**Finding: Justified, with one observation.**

The worker proposes expanding the write set to `fund_agent/fund/chapter_writer.py` (and possibly `fund_agent/fund/evidence_availability.py` or typed contract sidecar files). The worker also explicitly rejects three in-scope workarounds:

| Rejected workaround | Reason | Assessment |
|---|---|---|
| Patch `runner.py` to reclassify as success | Would weaken fail-closed evidence | Correct — runner's current safe diagnostic is already accepted and valuable |
| Patch `agent_bridge.py` to fabricate availability | Service should not invent Fund-domain evidence semantics | Correct — violates AGENTS.md module boundary (Service owns orchestration, Fund owns domain rules) |
| Patch `chapter_orchestrator.py` to silently downgrade gaps | Would mask typed contract gaps | Correct — orchestrator should not override Fund-layer contract semantics |

The proposed fix location (`chapter_writer.py`) is technically correct:
- The `ValueError` originates at `chapter_writer.py:922` and `chapter_writer.py:992`.
- The fix should convert missing typed required-output availability (for items with `when_evidence_missing`) into a deterministic `ChapterWriteIssue` / `ChapterWriteResult(status="blocked")` with zero provider attempts.
- This is a Fund-layer concern under AGENTS.md module boundaries: "任何理解基金类型、财报章节、投资规则、有知有行方法论、CHAPTER_CONTRACT 解析 / preferred_lens 应用、审计规则执行 / 证据锚点验证的代码，默认放在 Agent 层的 fund_agent/fund."

**Observation (non-blocking)**: The worker's interpretation of "allowed write set" derives from the prior gate's constraint (`aabe308`: "mandatory amendments require red-test-first proof, exact empty-traces `_exception_task()` guard and no scope expansion"), which was specific to the provider-before safe-diagnostic fix in `runner.py`. The current gate's objective explicitly includes root-cause fixing, and `chapter_writer.py` is the natural root-cause file. A reasonable alternative interpretation would have treated `chapter_writer.py` as within scope for this gate. However, the worker's conservative choice to seek explicit controller authorization before crossing from Agent-layer to Fund-layer edits is consistent with this project's gateflow methodology and does not invalidate the evidence or the BLOCKED verdict.

## 4. No-live Boundary and Scope Discipline

**Finding: Fully preserved.**

- No live/provider/network/analyze/checklist/readiness/release/PR command was run.
- The red reproducer uses monkeypatched `derive_evidence_availability` and fake writer/auditor clients — zero provider/network calls.
- No source/PDF/cache/FDR/FundDocumentRepository body was read.
- The artifact correctly rejects all readiness/provider/content-quality claims (7 REJECT dispositions, all proper).
- `NOT_READY` is explicitly preserved.
- EID single-source/no-fallback remains unchanged.
- No source policy, provider default, repair budget, annual-period LLM route, or Docling scope changes are proposed or implied.

## 5. Residual Accuracy

| Residual | Assessment |
|---|---|
| Chapter 3 typed availability gap can still surface as pre-provider ValueError/code_bug | Confirmed by code inspection and red reproducer |
| Provider readiness remains unproven | Correct — no provider attempt occurred |
| LLM content quality remains unaccepted | Correct — no chapter body was read |
| Release/readiness remains NOT_READY | Correctly preserved |

## Final Verdict

**VERDICT: PASS_BLOCKED**

The BLOCKED_NEEDS_CONTROLLER_DECISION verdict is supported by technically correct root-cause analysis, verified by code inspection against `runner.py:1399-1481` and `chapter_writer.py:910-992`, and independently demonstrated by a no-live red reproducer. The no-live boundary is fully preserved. The proposed fix location (`chapter_writer.py`) is the correct layer under AGENTS.md module boundaries. The only minor observation is that the worker's write-set constraint interpretation was perhaps more conservative than necessary, but this does not detract from the evidence quality.
