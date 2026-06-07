# MVP Agent Engine Design Slice B Tool Adapter Contract Plan Review - Codex

## 1. Verdict

`PASS_WITH_NON_BLOCKING_OBSERVATIONS`

Reviewed target:

- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md`

Assigned scope:

- Design-only adversarial plan review.
- No implementation, source edit, test edit, control-doc edit, live provider action, network probe, PR, push or commit.

Assumptions tested:

- Future ToolRegistry wraps current Fund primitives only.
- `EvidenceAvailability` remains run-level same-source precomputation, not a registry tool.
- Provider writer/auditor clients remain Service-constructed per-run typed fields.
- ToolTrace and Agent serialized diagnostics are allowlist-only.
- Runtime/provider failures remain separate from content repair.
- Programmatic audit remains before semantic audit and cannot be overridden by semantic pass.
- Slice B does not authorize runtime/default/budget/config, quality gate, golden/readiness, score-loop, multi-year, public chapter id, PR or push scope.

Conclusion:

- The plan is ready for controller judgment with non-blocking observations tracked below.

## 2. Findings Ordered By Severity

No blocking findings.

No material plan findings requiring controller stop were found. The target plan explicitly forbids implementation and external/runtime scope (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:73-89`), limits the registry to wrappers around existing Fund primitives (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:91-112`), preserves run-level `EvidenceAvailability` (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:152-181`), and defines allowlist-only trace serialization with explicit exclusions for prompt, draft, raw responses, secrets, model value and base URL value (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:346-407`).

Non-blocking observations:

### NBO-1-未修复-低-request id safe projection needs implementation-time shape constraint

- **位置**: ToolTrace allowed fields and runtime diagnostics rule (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:370-403`)
- **问题类型**: 最佳实践偏离 / residual risk
- **当前写法**: ToolTrace allowed fields include `request id`; forbidden fields exclude prompt, draft, raw provider/audit response, raw provider request/body, secrets, model value, base URL value and provider error message beyond the existing redacted policy.
- **反例/失败场景**: A future implementation could copy provider response header values into ToolTrace as unrestricted `request_id` strings. Current code already treats request id as safe, but the value is taken directly from response headers and then serialized.
- **为什么有问题**: `request_id` is useful for provider support and audit, but it can be provider/account-correlated. The current plan is safe enough for design review because it still requires implementation to define an allowlisted projection equivalent to current safe serializers, but the later implementation plan should pin the exact shape: header-name allowlist only, scalar string only, no full header map, no URL, no Authorization/cookie/header payload.
- **直接证据**: Current serializer outputs `request_id` directly from runtime diagnostic payload (`fund_agent/services/chapter_orchestrator.py:3258-3283`). Provider diagnostics read request ids from configured response headers (`fund_agent/services/llm_provider.py:796-813`).
- **影响**: Low residual risk of over-broad diagnostic copying in a later implementation if the implementation plan treats `request_id` as a generic header payload rather than a single allowlisted scalar.
- **建议改法和验证点**: In the implementation planning gate, define `request_id` as an optional scalar from the existing `_REQUEST_ID_HEADERS` allowlist only, and add a trace serialization assertion that no other response headers or provider URL/config values appear.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 3. Parent Slice A Follow-Up Assessment

Parent accepted follow-ups consumed by Slice B:

- Runtime diagnostics safe projection: covered. Slice B forbids storing `ChapterLLMRuntimeDiagnostic` wholesale and requires an allowlisted projection equivalent to current safe serializers (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:398-403`), satisfying Slice A judgment requirement for excluding unsafe prompt/draft/raw/model/base URL fields (`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md:79-83`).
- `diagnostic_consistency_status`: covered. Slice B pins the current literal set or a named explicit future equivalent (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:404-407`), matching Slice A follow-up (`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md:73-77`).
- Run-level `EvidenceAvailability` non-tool boundary: covered. Slice B repeats the accepted run-level once-after-projection boundary and forbids recomputation from artifacts/filesystem/external state (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:152-181`), matching Slice A accepted fact (`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md:45-47`).
- Hidden retry semantics: partially deferred by parent design. Slice B forbids converting provider runtime categories into hidden content repair attempts (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:430-432`). The full `hidden_retry` field decision remains appropriately owned by Slice C or implementation planning per Slice A judgment (`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md:61-65`).
- Chapter-attributed blocked reasons: not directly in Slice B scope, but not violated. The plan's ToolTrace fields include chapter id, stop reason/error category, provider runtime category and chapter failure category (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:352-380`). The exact flattened-vs-chapter-attributed `blocked_reasons` structure remains implementation-planning scope per Slice A judgment (`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md:67-71`).

Parent refresh-gate constraints preserved:

- Service retains provider construction and runtime ceilings; Host remains lifecycle-only; future Agent owns execution mechanics only after separate implementation gate (`docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md:39-48`).
- First ToolRegistry design must wrap existing Fund primitives and not rewrite Fund logic (`docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md:45-47`).

## 4. Scope And Forbidden-Action Audit

Scope audit:

- Tool boundary wraps existing Fund primitives only: pass. Current `project_chapter_facts()` projects an in-memory `StructuredFundDataBundle` and validates chapter ids without repository/provider access (`fund_agent/fund/chapter_facts.py:431-530`). `write_chapter()` consumes explicit `ChapterWriterInput` plus injected `ChapterLLMClient | None` (`fund_agent/fund/chapter_writer.py:741-807`). `audit_chapter_programmatic()` and `audit_chapter_llm()` are separate existing functions (`fund_agent/fund/chapter_auditor.py:420-508`).
- `EvidenceAvailability` non-tool precomputation: pass. Current `derive_evidence_availability()` derives only from `ChapterFactProjection` plus typed manifest and validates requirement ids/projection chapters (`fund_agent/fund/evidence_availability.py:261-293`). The module docstring states it does not read repository, PDF/cache/source helper, Service, Host, provider, retained report, filesystem, env or dayu runtime (`fund_agent/fund/evidence_availability.py:1-8`).
- Provider clients remain Service-constructed per-run fields: pass. The plan explicitly excludes provider writer/auditor clients from registry tools (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:103-112`) and the design truth says provider clients are Service-constructed per-run typed fields, not ToolRegistry tools or `extra_payload` (`docs/design.md:63`).
- ToolTrace and Agent diagnostics allowlist-only: pass with NBO-1. Current runtime diagnostic dataclass contains unsafe `model_name` and `message` fields (`fund_agent/services/chapter_orchestrator.py:201-269`), while current serializer explicitly omits `model_name`, `message`, prompt, draft and raw response (`fund_agent/services/chapter_orchestrator.py:727-735`, `fund_agent/services/chapter_orchestrator.py:3258-3301`). Slice B correctly forbids wholesale storage and unsafe fields.
- Error taxonomy separates provider runtime from content repair: pass. Current provider retries only timeout attempts and fails closed for network, rate limit, HTTP error and malformed response (`fund_agent/services/llm_provider.py:248-420`). Slice B keeps provider runtime categories out of hidden content repair (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:409-432`).
- Programmatic audit before semantic audit: pass. Current aggregate audit calls programmatic before LLM audit and only accepts when aggregate status is pass (`fund_agent/fund/chapter_auditor.py:511-550`). Slice B preserves programmatic-before-semantic and forbids semantic pass from overwriting programmatic blockers (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md:289-293`).

Forbidden-action audit:

- No source files edited.
- No tests edited.
- No control docs edited.
- Target plan artifact was not edited.
- No live `--use-llm`.
- No provider readiness, curl, DNS, socket, endpoint probe or network check.
- No PR, push, commit, staging or external comment.
- No `fund_agent/agent` package or implementation scaffold created.

Observed workspace state at review start:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Existing unrelated dirty/untracked state was observed and left untouched, including `pyproject.toml` modified and multiple untracked review/report/tool paths. The reviewed target plan was already untracked.

## 5. Validation Commands And Results

Commands run:

```text
git branch --show-current
```

Result: `feat/mvp-llm-incomplete-run-artifacts`.

```text
git status --short
```

Result: dirty worktree observed; no cleanup performed.

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md
```

Result: pass, exit code 0, no whitespace errors.

Final validation after writing this review artifact:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-codex-20260608.md
```

Result: pass, exit code 0, no whitespace errors.

## 6. Residual Risks Or Open Questions

Residual risks:

- `request_id` safe projection shape should be pinned in the later implementation planning gate, not left as an arbitrary provider header payload. Tracking destination: implementation planning gate or Slice D trace serialization validation.
- Full `hidden_retry` field semantics remain Slice C / implementation planning scope. Current Slice B does not authorize hidden Agent retry and does not violate the parent boundary.
- Equivalence testing remains Slice D / implementation planning scope. This review did not require source tests because the artifact is docs/reviews-only and design-only.

Open questions:

- None requiring controller stop.
