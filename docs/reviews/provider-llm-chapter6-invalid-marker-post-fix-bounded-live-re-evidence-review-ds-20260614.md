# Provider/LLM Chapter 6 Invalid-marker Post-fix Bounded Live Re-evidence — DS Review

Date: 2026-06-14

Role: AgentDS, evidence reviewer (not controller)

Review target: `docs/reviews/provider-llm-chapter6-invalid-marker-post-fix-bounded-live-re-evidence-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

## Findings

### F1 (non-blocking): summary.json first_failed attribution is factually wrong

Section 7 of the evidence artifact presents a table of `first_failed.*` values and labels it "From `summary.json`". Independent `jq` extraction from the actual `summary.json` shows all `runtime_diagnostics.first_failed.*` fields are `null`:

```text
$ jq '.runtime_diagnostics.first_failed' summary.json
{
  "chapter_id": null,
  "status": null,
  "stop_reason": null,
  "category": null,
  "subcategory": null,
  "runtime_operation": null,
  "provider_attempt_count": null,
  "provider_runtime_categories": null,
  "diagnostic_consistency_status": null
}
```

The values presented in the evidence (chapter_id=5, status=blocked, stop_reason=llm_contract_violation, category=audit_parse, subcategory=forbidden_phrase, runtime_operation=auditor) are independently verifiable from `chapter-05.json` and the stderr output quoted in section 4, but they are not stored in `summary.json` as claimed.

Severity: non-blocking. The per-chapter metadata independently confirms every factual claim, and the verdict does not depend on the summary.json attribution. The artifact should correct the source label (e.g., "From stderr and per-chapter metadata" rather than "From `summary.json`").

### F2 (non-blocking): manifest redaction_policy path is flat, not nested

Section 6 reports `redaction_policy.policy_id` as `llm_incomplete_artifact_redaction.v1`. The actual manifest.json stores this as a top-level string field `"redaction_policy": "llm_incomplete_artifact_redaction.v1"`, not as a nested object with a `.policy_id` key. The value is correct; the dotted-path notation implies a nested structure that does not exist.

Severity: non-blocking. The value is accurate.

## Cross-check Matrix

### Q1: One actual live command distinguished from AgentCodex attempt?

**PASS.** Section 3 clearly documents the AgentCodex nested sandbox failure (uv cache blocked) and states the attempt "produced no provider/analyze evidence and is not counted as a live execution fact." Section 4 records exactly one controller-run live command as the only accepted execution.

### Q2: Sample identity, command boundary, exit code, manifest path, safe metadata facts supported?

**PASS with F1, F2 caveats.**

| Fact | Evidence claim | Independent verification | Match? |
|---|---|---|---|
| fund_code | `004393` | manifest.json: `"004393"` | YES |
| report_year | `2025` | manifest.json: `2025` | YES |
| run_id | `host_run_8c795cd1469b44d3` | manifest.json: `"host_run_8c795cd1469b44d3"` | YES |
| created_at | `2026-06-14T00:26:57.622155Z` | manifest.json: same | YES |
| cli_command | `analyze --use-llm` | manifest.json: `"analyze --use-llm"` | YES |
| orchestration_status | `partial` | manifest.json: `"partial"` | YES |
| final_assembly_status | `incomplete` | manifest.json: `"incomplete"` | YES |
| Chapter 6 status | `accepted`, stop_reason `none`, issues `[]`, attempts `1` | chapter-06.json: all match | YES |
| Chapter 5 status | `blocked`, `llm_contract_violation`, `audit_parse`, `forbidden_phrase`, attempts `2` | chapter-05.json: all match | YES |
| Chapter 2 non-terminal | `accepted`, subcategory `l1_numerical_closure`, attempts `2` | chapter-02.json: all match | YES |
| summary.json first_failed.* | Various concrete values attributed to summary.json | summary.json: all `null` | NO (F1) |
| redaction_policy | `llm_incomplete_artifact_redaction.v1` | manifest.json: same value, flat field | Value YES, path NO (F2) |
| Manifest directory path | Correctly listed | `ls` confirms directory exists | YES |
| Exit code `1` | Attested in stderr | Consistent with incomplete run, Chapter 5 blocked; not independently verifiable from JSON metadata alone | CONSISTENT |
| Exact env vars in command | `FUND_AGENT_LLM_TIMEOUT_SECONDS=60` etc. | Not independently verifiable from metadata | ACCEPT on artifact's own attestation |
| Worker-channel `git diff --check` passed | Reported in section 3 | Controller `git diff --check` passed (no output) | YES |

### Q3: Chapter 6 accepted; Chapter 5 audit_parse/forbidden_phrase = new first failed blocker?

**PASS.**

- Chapter 6: `chapter-06.json` confirms `status: "accepted"`, `stop_reason: "none"`, `failure_category: null`, `failure_subcategory: null`, `attempt_count: 1`, `issue_count: 0`.
- Chapter 5: `chapter-05.json` confirms `status: "blocked"`, `stop_reason: "llm_contract_violation"`, `failure_category: "audit_parse"`, `failure_subcategory: "forbidden_phrase"`, `attempt_count: 2`, `issue_count: 1`.
- Chapters 1, 3, 4: all `accepted`, confirming Chapter 5 is the first failed chapter.

The accepted no-live Chapter 6 `writer:invalid_anchor_marker` retry fix is confirmed in this single live sample.

### Q4: Avoids overclaiming?

**PASS.** The artifact explicitly rejects: final assembly completion (FAIL), provider readiness (REJECT), release/readiness (REJECT), LLM route readiness (REJECT in section 10), provider behavior classification (REJECT), and broad live stability (single-sample caveat in section 11). The verdict string ends with `NOT_READY`. No overclaiming observed.

### Q5: Preserves source policy, no fallback reintroduction?

**PASS.** Section 1 declares source policy unchanged. Section 9 boundary check: fallback "NOT OBSERVED", source/fallback policy change "REJECT". Section 10 rejects source policy change and fallback authorization. No fallback language or design appears in the artifact.

### Q6: Next entry recommendation appropriate?

**PASS.** Recommended next entry is `Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition Gate`, scoped to root-cause classification and decision on diagnostic/planning/re-evidence/blocked next step. Boundaries preserve source policy, `NOT_READY`, and default-no-live-command. This follows the established pattern (Chapter 6 invalid-marker disposition gate → diagnostic evidence → fix plan → implementation → live re-evidence) and is an appropriate next step.

## Controller Judgment Cross-check

The evidence artifact references the controller judgment `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-implementation-controller-judgment-20260614.md` (verdict `ACCEPT_IMPLEMENTATION_NOT_READY`). The accepted implementation scope (Chapter 6-only writer-block retry for `writer:invalid_anchor_marker`, consuming existing repair budget) is consistent with the evidence observed: Chapter 6 passed in 1 attempt with no issues.

## Scope Boundary Verification

| Boundary | Status |
|---|---|
| Writer Markdown bodies not read | ACCEPT (no evidence of body reads) |
| Auditor feedback bodies not read | ACCEPT |
| Repair Markdown bodies not read | ACCEPT |
| Raw prompts not read | ACCEPT |
| Provider request/response payloads not read | ACCEPT |
| Credentials not read | ACCEPT |
| Raw source/PDF/cache bodies not read | ACCEPT |
| Accepted final report body not read | ACCEPT |
| Generated report Markdown body not read | ACCEPT |
| Only safe metadata JSON scalars extracted | ACCEPT (jq used for scalar extraction only) |
| No live/provider/LLM/network commands run | ACCEPT |
| No source/test/control/design/README modified | ACCEPT |
| No stage/commit/push/PR | ACCEPT |

## Residuals

- F1 (summary.json attribution) should be corrected in the evidence artifact or in a controller amendment.
- F2 (redaction_policy path notation) is cosmetic.
- Chapter 2 `l1_numerical_closure` non-terminal metadata (attempts=2) remains a diagnostic residual to monitor in future evidence.
- The fact that summary.json `runtime_diagnostics.first_failed` is all-null while chapter-level metadata carries the blocking facts is itself a diagnostic observation — the summary-level `first_failed` projection appears not to be populated in this run, though stderr emitted the values at runtime.

## Final Verdict

`PASS_WITH_FINDINGS`

The evidence artifact correctly records one live execution, distinguishes the AgentCodex sandbox attempt, accurately reports chapter-level metadata, avoids overclaiming, preserves source policy, and recommends an appropriate next entry. Two non-blocking factual findings (F1: summary.json attribution error; F2: redaction_policy path notation) do not undermine the verdict. Chapter 6 invalid-marker is resolved in this exact sample; Chapter 5 forbidden_phrase is the new first failed blocker. Release/readiness remains `NOT_READY`.
