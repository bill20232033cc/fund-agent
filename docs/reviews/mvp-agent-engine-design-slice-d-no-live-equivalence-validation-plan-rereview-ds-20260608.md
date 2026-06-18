# MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan Re-Review (DS)

## 1. Verdict

**PASS**

All four prior findings (3 DS NBO, 2 Codex blocking, 1 overlapping) are resolved in the current plan. Zero blocking findings remain.

## 2. Scope

Targeted re-review only. Scope limited to:

- DS NBO-1: missing `ChapterRunStopReason` values in 5.2 terminal mapping
- DS NBO-2: `request_id` explicit response-header allowlist constraint
- DS NBO-3: `ChapterFailureCategory` mapping completeness
- Codex BF-1: `llm_exception` + `code_bug` misclassification as provider/runtime
- Codex BF-2: duplicate chapter rows / source accepted ids uniqueness fail-closed

No plan edits, source edits, test edits, control doc edits, live commands, provider probes, or commits.

## 3. Finding-by-Finding Re-Verification

### 3.1 DS NBO-1: Missing Stop Reasons → RESOLVED

Prior DS review claimed `fund_type_unknown`, `writer_blocked`, `llm_unavailable`, `llm_empty_response` were not explicitly mapped in Section 5.2.

Current plan evidence:

| Value | Plan Location | Mapping |
|---|---|---|
| `llm_unavailable` | 5.2 line 103 | provider/runtime blocked state (grouped with `llm_timeout` etc.) |
| `llm_empty_response` | 5.2 line 103 | provider/runtime blocked state (same group) |
| `fund_type_unknown` | 5.2 line 114 | fund identity/fact-gap precondition state |
| `writer_blocked` | 5.2 line 115 | writer precondition blocked state with no provider call |

Full enumeration check: all 23 `ChapterRunStopReason` literal values (confirmed from `fund_agent/services/chapter_orchestrator.py:53-77`) have explicit mappings in Section 5.2. No value is silently dropped.

### 3.2 DS NBO-2: request_id Allowlist → RESOLVED

Prior DS review recommended expanding wording to explicitly reference response-header allowlist.

Current plan 5.5 line 195 reads:

> `allowlisted request id scalar from an explicit response-header allowlist only`

The constraint is explicit and matches the Slice B Codex NBO-1 requirement.

### 3.3 DS NBO-3: ChapterFailureCategory Mapping → RESOLVED

Prior DS review noted that Section 5.2's preamble declares the mapping key is the `(stop_reason, failure_category)` pair, but the mapping entries that follow are primarily stop-reason-based, with `ChapterFailureCategory` values not having their own explicit rows.

Current plan addresses this at two levels:

1. **Immediate**: Line 96-98 declares the mapping key IS the pair, and line 106-107 provides an explicit pair-based entry (`llm_exception` + `code_bug` → fail-closed internal code bug state).
2. **Deferred**: Lines 121-123 require the implementation planning gate to "explicitly enumerate every current `ChapterRunStopReason` and every current `ChapterFailureCategory`, including `provider_runtime`, `llm_timeout`, `prompt_contract`, `audit_parse`, `audit_rule_too_strict`, `fact_gap` and `code_bug`."

All 7 `ChapterFailureCategory` values (confirmed from `fund_agent/services/chapter_orchestrator.py:105-113`) are covered: `provider_runtime` and `llm_timeout` map via the provider/runtime blocked group; `prompt_contract` maps via the content contract blocked group; `audit_parse` and `audit_rule_too_strict` map via the audit blocked/content group; `fact_gap` maps via the needs-more-facts group; `code_bug` has its own explicit entry. The full pair-based table is correctly deferred to implementation planning with an explicit enumeration requirement.

### 3.4 Codex BF-1: llm_exception + code_bug → FIXED

Prior Codex review (blocking) stated the plan grouped `llm_exception` with `llm_timeout`, `llm_rate_limited`, etc. under provider/runtime blocked state, which would misclassify code bugs.

Current plan 5.2 lines 102-107:

> \- `llm_timeout`, `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, `llm_unavailable`, `llm_empty_response` with provider-classified failure categories -> provider/runtime blocked state;
> \- `llm_exception` with `failure_category=code_bug` -> fail-closed internal code bug state, not provider/runtime;

`llm_exception` is explicitly **excluded** from the provider/runtime group and given its own entry with `failure_category=code_bug` mapped to fail-closed internal code bug state. This directly matches the test expectation at `tests/services/test_chapter_orchestrator.py:1584-1599` and the control truth at `docs/implementation-control.md:55`.

### 3.5 Codex BF-2: Duplicate Chapter Rows Fail-Closed → FIXED

Prior Codex review (blocking) stated Section 5.4 omitted duplicate chapter row uniqueness from minimum assertions.

Current plan 5.4 lines 157-158:

> \- required body chapter rows and source accepted chapter ids are unique;
> \- duplicate chapter rows remain fail-closed with no report markdown;

Both assertions are now explicitly present in the minimum assertion list. This directly matches the current test at `tests/services/test_final_chapter_assembler.py:321-344`.

## 4. Positive Findings (Reconfirmed)

The following review focus areas from the prior DS review all remain PASS after re-verification:

1. **Equivalence criteria concreteness**: Five sub-sections with explicit current→future pairs and minimum assertions.
2. **No-live constraints enforceability**: Closed set of allowed commands, enumerated allowed test doubles, enumerated forbidden categories, double enforcement via Section 7.
3. **Final assembly readiness not weakened**: All minimum assertions preserve fail-closed semantics.
4. **Repair/provider budget separation**: Eight explicit preservation rules.
5. **ToolTrace safety assertions**: 13 forbidden items, 20 allowed items — comprehensive.
6. **No implementation scope authorized**: Section 1, 4, 6, 10 all prevent scope creep.

## 5. Validation Commands

```text
$ git branch --show-current
feat/mvp-llm-incomplete-run-artifacts

$ git status --short -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md
?? docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md

$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md
(exit 0, no whitespace errors)

$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-rereview-ds-20260608.md
(exit 0, no whitespace errors)
```

## 6. Artifact Readiness

The plan artifact is ready for controller judgment. All prior NBOs and blocking findings are resolved. No new blocking findings identified.
