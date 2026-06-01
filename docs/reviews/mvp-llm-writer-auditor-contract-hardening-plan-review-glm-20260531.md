# MVP LLM writer/auditor contract hardening plan review (GLM)

日期：2026-05-31
角色：Gateflow plan review specialist (GLM)
Review target：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`

## Conclusion: PASS_WITH_NON_BLOCKING

Plan is handoff-ready and code-generation-ready. No blocking issues found. 4 non-blocking findings documented below.

## Finding count

| Severity | Count |
|----------|-------|
| BLOCKING | 0 |
| NON_BLOCKING | 4 |

## Findings

### N-1: `content_filter` in `TRUNCATED_FINISH_REASONS` has semantic mismatch

**Category**: naming / semantics
**Location**: Plan Section 9 Slice A, `TRUNCATED_FINISH_REASONS` constant

Plan lumps `content_filter` with `length` and `max_tokens` under `TRUNCATED_FINISH_REASONS` and maps them all to `response_truncated`. `content_filter` is content policy enforcement, not truncation — the model chose not to continue for safety reasons, not because it ran out of tokens.

The fail-closed behavior (reject partial/filtered output) is correct. However, the category name `response_truncated` is semantically misleading for this case. An operator seeing `response_truncated` with `content_filter` origin would diagnose the wrong root cause (increase max_tokens vs. adjust prompt content).

**Recommendation**: Either rename the set and stop reason to something more general (e.g., `INCOMPLETE_FINISH_REASONS` / `response_incomplete`), or split `content_filter` into a separate category such as `response_content_filtered`. This is purely a naming precision issue and does not affect correctness.

### N-2: `required_corrections` field in `ChapterRepairContext` is underspecified

**Category**: contract specification gap
**Location**: Plan Section 7.4 `ChapterRepairContext` definition

`ChapterRepairContext` has `required_corrections: tuple[str, ...]` but the plan does not specify how this field is synthesized from the audit result. Audit issues carry `rule_code`, `location`, `message`, and `repair_hint` (typically `"patch"` or `"regenerate"`). The plan says `_repair_context_from_audit()` uses "issue ids, rule/location/message 脱敏摘要", but does not commit to whether `required_corrections` is:
- a verbatim copy of audit issue messages,
- a synthesis of rule_code + location into action items (e.g., "补齐 ### 结论要点", "把候选 facet 改为未断言"),
- or a hard-coded mapping from known rule codes to fixed correction templates.

Each option has different implementation complexity and maintenance cost. Option 2 or 3 aligns best with the plan's own required corrections list (Section 7.4: 补齐结构段落、补齐 marker、改候选 facet、遵守 audit 反馈), but the plan should commit.

**Recommendation**: Specify that `required_corrections` are synthesized from audit issues using a fixed mapping of known rule codes to correction templates. This keeps the repair prompt deterministic and avoids free-form string manipulation. If the implementation agent encounters an unknown rule code, it should include the raw issue message as fallback and continue — no stop required.

### N-3: Service stop reason mapping for new writer categories should be more specific

**Category**: traceability
**Location**: Plan Section 7.2, Section 9 Slice A

Plan says new writer stop reasons (`missing_required_structure`, `missing_required_output_marker`, `unknown_anchor`, `response_too_long`, `response_truncated`) should all be fail-closed, and "Service stop reason 可先使用 `llm_contract_violation`". However, mapping five distinct writer failure categories to a single `llm_contract_violation` Service stop reason loses diagnostic fidelity that the plan itself is trying to create.

The whole motivation of this gate is making failure reasons classifiable. If the orchestrator collapses them back to `llm_contract_violation`, the operator cannot distinguish "missing heading" from "response too long" from "truncated by provider" without looking at individual issue messages — which requires digging into per-chapter attempt records.

**Recommendation**: Map each new writer stop reason to a distinct Service stop reason that preserves the category. For example: `missing_required_structure` → `("blocked", "missing_required_structure")`, `response_truncated` → `("blocked", "response_incomplete")`. The `ChapterRunStopReason` type should be extended accordingly. This maintains the diagnostic chain from writer parser through orchestrator to CLI output.

### N-4: `non_asserted_facets` de-duplication strategy should commit to one approach

**Category**: specification ambiguity
**Location**: Plan Section 9 Slice B, `_audit_non_asserted_facets()` changes

Plan says "可用 `(facet, index window)` 或 first occurrence 去重" but does not commit to which strategy. The two approaches have different behaviors:
- First-occurrence dedup: one issue per unique facet text, regardless of how many times it appears. Simple but may miss a later occurrence that is actually asserted while an earlier one was properly qualified.
- Window-based dedup: one issue per unique (facet, window) pair. More precise but more complex and requires tuning the window size.

For MVP, first-occurrence dedup is the safer choice: it reduces noise without risking false negatives from window boundary issues. The current code already creates one issue per occurrence, so switching to one-per-facet is a strict reduction in issue count and won't introduce new assertion escapes.

**Recommendation**: Commit to first-occurrence dedup (one issue per unique facet text, using the first match location). Add a code comment explaining that later occurrences of the same facet are intentionally not re-reported to reduce repair prompt noise.

## Verified plan properties

### Scope compliance

| Check | Result |
|-------|--------|
| Solves writer prompt output protocol | Yes — Section 7.1 specifies fixed headings, required output markers, anchor/missing formats, non_asserted_facets language |
| Solves writer parser failure categories | Yes — Section 7.2 adds 5 new categories with clear mapping |
| Solves auditor LLM line protocol | Yes — Section 7.3 specifies exact PASS format, severity enum, location/message constraints |
| Solves repair/regenerate previous failure context | Yes — Section 7.4 introduces `ChapterRepairContext` with typed fields |
| Solves bounded retry | Yes — `max_repair_attempts` preserved, no infinite retry |
| Solves timeout classification | Yes — Section 7.5 adds `LLMProviderTimeoutError` + Service-level categories |
| Solves audit rule calibration | Yes — Section 11 explicitly lists allowed vs prohibited calibrations |
| Solves smoke acceptance boundary | Yes — Sections 3, 4, 9D, 10 clearly separate current gate from next gate |

### Hard constraint compliance

| Constraint | Compliant |
|------------|-----------|
| No golden/fixtures/score/quality gate changes | Yes — explicitly listed in Section 4 non-goals |
| No Gate 5 dayu/Host/Agent | Yes — Section 4 non-goals, Section 6 prohibited files |
| No PR state changes | Yes — Section 4 non-goals, Section 6 prohibited files |
| No secrets/full provider response | Yes — Section 4 non-goals, evidence hygiene in Section 1, Section 10 secret scan |
| No weak-evidence pass | Yes — Section 4 non-goals |
| No candidate facet asserted | Yes — Section 7.1 prohibits assertion forms, Section 11 prohibits calibration |
| Deterministic analyze/checklist unchanged | Yes — Section 4 non-goals, validation matrix Section 10 |
| Deterministic `analyze`/`checklist` unchanged | Yes — validation matrix confirms |

### Gate sequencing compliance

| Check | Result |
|-------|--------|
| Current gate scope correct | Yes — contract hardening only |
| Next gate `MVP real provider smoke acceptance gate` not pulled in | Yes — Section 3, 4, 9D, 10 all state acceptance is next gate's job |
| Later gate `MVP chapter generation score improvement loop` not pulled in | Yes — Section 4 non-goals explicitly excludes score schema, task generation, dashboard |

### Code feasibility verification

| Item | Feasible | Evidence |
|------|----------|----------|
| `ChapterWriteStopReason` extension | Yes | Current `Literal` type can be extended backward-compatibly |
| `finish_reason` available in parser | Yes | `ChapterLLMResponse.finish_reason: str | None` already exists (line 125) |
| `_WRITER_STOP_REASON_MAPPING` updatable | Yes | `Final dict` can be replaced at module level |
| `ChapterWriterInput` extension with `repair_context` | Yes | `dataclass(frozen=True, slots=True)` with default `None` is backward-compatible |
| `ChapterLLMRequest` extension | Yes | Same pattern as writer input |
| Auditor prompt strengthening | Yes | `_llm_request()` builds prompts from strings, easily extended |
| `_parse_llm_audit_response()` already fail-closed | Yes | Parse failure → `blocked`, confirmed in code and plan |
| Timeout typed exception | Yes | Pattern matches existing `LLMProviderRateLimitError` / `LLMProviderMalformedResponseError` |
| `_exception_result()` updatable | Yes | Simple isinstance cascade can be added |
| `required_output_marker` regex in HTML comments | Yes | Existing `_COMMENT_RE` captures content; specific prefix match needs new regex with Chinese character support |

### Slice structure assessment

- Slice A (writer) and Slice B (auditor) are independent — can be implemented in parallel or either order.
- Slice C (repair/timeout) depends on Slice A's `ChapterRepairContext` dataclass and new stop reasons — this dependency is implicit but logical.
- Slice D (smoke/docs) depends on A, B, C — correctly placed last.
- Each slice has allowed files, exact changes, tests, validation commands, completion signal, and stop conditions — handoff quality is good.

## Self-check

| Check | Result |
|-------|--------|
| Only read allowed truth/evidence | Yes — AGENTS.md, startup packet, implementation-control, controller judgment, chapter1 diagnostic summary, Gate 2 code |
| No code modification | Yes |
| No plan modification | Yes |
| No commit/push/PR/merge | Yes |
| No controller actions | Yes |
| Findings use gateflow format | Yes |
| Artifact path correct | Yes |
