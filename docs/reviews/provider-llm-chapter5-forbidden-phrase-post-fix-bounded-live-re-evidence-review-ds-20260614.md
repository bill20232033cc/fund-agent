# Provider/LLM Chapter 5 Forbidden-phrase Post-fix Bounded Live Re-evidence — AgentDS Review

Date: 2026-06-14

Role: AgentDS independent live evidence reviewer

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Post-fix Bounded Live Re-evidence Gate`

Review target: `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-20260614.md`

Verdict: `PASS`

Release/readiness: `NOT_READY`

## 1. Scope

This review evaluates the bounded live evidence artifact against five questions. Only allowed verification was used: jq safe scalar metadata from summary/chapter-03/chapter-05/manifest, `git diff --check`, `git status --short`. No raw prompt, provider payload, chapter body, report body, source/PDF/cache bodies, or live/provider/LLM/network commands were executed or read.

## 2. Review Questions

### Q1: Does the artifact accurately report the single live command result and runtime path?

**Verdict: PASS**

Every safe scalar reported in the artifact was cross-checked against jq output:

| Artifact claim | jq source | Match? |
|---|---|---|
| exit `1`, `elapsed_ms=272595` | Command output text | ✓ |
| `summary schema = llm_incomplete_run_summary.v1` | `summary.json.schema_version` | ✓ |
| `run id = host_run_68d54160dc204eb9` | `summary.json.run_id`, `manifest.json.run_id` | ✓ |
| `fund/year = 004393 / 2025` | `summary.json.fund_code`, `report_year` | ✓ |
| `orchestration=partial`, `final_assembly=incomplete` | `summary.json.orchestration_status`, `final_assembly_status` | ✓ |
| `redaction_applied=false`, `redaction_count=0` | `summary.json.redaction_applied`, `redaction_count` | ✓ |
| first failed: chapter `3`, `blocked`, `missing_required_output_marker`, `prompt_contract`, `missing_required_marker`, `attempt_count=1` | `summary.json.first_failed` | ✓ |
| Chapter 5: `accepted`, `stop_reason=none`, `issues=[]`, prompt diagnostics `[]` | `chapters/chapter-05.json` | ✓ |
| Chapter 3 issues: `writer:required_output_gap_missing` for item_01 and item_05 | `chapters/chapter-03.json.issues[]` | ✓ |
| Chapter 3 prompt diagnostic: `phase=writer_parse`, `attempt_index=0`, `primary_subcategory=missing_required_marker`, `required_output_missing_count=2`, `max_output_chars=12000`, `response_chars=1906` | `chapters/chapter-03.json.chapter_prompt_contract_diagnostics[0]` | ✓ |
| Chapter 3 prompt diagnostic: `issue_reason_counts.missing_required_output_marker=2` | `chapters/chapter-03.json.chapter_prompt_contract_diagnostics[0].issue_reason_counts` | ✓ |
| manifest: `source_policy=null`, `emitted_source_policy=null`, `command=null`, `artifacts=null` | `manifest.json.source_policy`, `emitted_source_policy`, `command`, `artifacts` | ✓ |
| manifest redaction policy: `llm_incomplete_artifact_redaction.v1` | `manifest.json.redaction_policy.policy_id` | ✓ |

One minor metadata internal inconsistency observed in the runtime artifacts themselves (not the evidence artifact): `chapter-03.json` reports `attempt_count=null` while `summary.json.first_failed.attempt_count=1`. This is a runtime metadata field-level discrepancy, not an evidence reporting error. The evidence artifact correctly attributes `attempt_count=1` to the `first_failed` summary block.

The artifact's chapter matrix line from command output text matches `summary.json.chapter_matrix[]` for all six chapters including Chapter 2 `accepted` with `l1_numerical_closure` residual subcategory and Chapter 4 `attempt_count=2`.

### Q2: Do safe metadata support Chapter 5 accepted and first failed Chapter 3 missing_required_marker?

**Verdict: PASS**

Chapter 5 accepted is independently confirmed by three metadata sources:
- `summary.json.chapter_matrix[4]`: `status=accepted`, `stop_reason=none`, `accepted_draft_present=true`, `accepted_conclusion_present=true`
- `chapters/chapter-05.json`: `status=accepted`, `stop_reason=none`, `issues=[]`, `chapter_prompt_contract_diagnostics=[]`
- No Chapter 5 entry in `summary.json.first_failed`

Chapter 3 missing_required_marker is independently confirmed by four metadata sources:
- `summary.json.first_failed`: `chapter_id=3`, `status=blocked`, `stop_reason=missing_required_output_marker`, `failure_category=prompt_contract`, `failure_subcategory=missing_required_marker`
- `summary.json.chapter_matrix[2]`: `status=blocked`, `stop_reason=missing_required_output_marker`, `failure_category=prompt_contract`, `failure_subcategory=missing_required_marker`, `accepted_draft_present=false`, `accepted_conclusion_present=false`
- `chapters/chapter-03.json`: `status=blocked`, `stop_reason=missing_required_output_marker`
- `chapters/chapter-03.json.chapter_prompt_contract_diagnostics[0]`: `primary_subcategory=missing_required_marker`, `required_output_missing_count=2`

The `ch3.required_output.item_01` gap is a known residual: it was previously dispositioned as an intentional fail-closed residual at checkpoint `62c7a2e`, then routed to `render_evidence_gap` at `1b9cd00`. The current evidence artifact correctly reports item_01 plus item_05 both appearing as `writer:required_output_gap_missing`. The artifact does not attempt to classify whether this is a regression or a different failure mode — it correctly leaves that to the recommended disposition gate.

### Q3: Does the artifact avoid overreading provider behavior, source policy, readiness, raw content or EID proof from null manifest fields?

**Verdict: PASS**

The artifact's section 4 explicitly rejects five categories of overread:
- LLM path readiness
- Full report completion
- Source policy proof from null manifest fields
- Raw provider response quality classification
- Raw prompt content, final report content, or chapter body quality

The artifact correctly reports null manifest fields as null without inference. `first_failed_provider_attempts=0/unknown` and `first_failed_provider_runtime_category=unknown` are reported from the command output text and corroborated by `chapter-03.json.runtime_diagnostics=null` — the artifact does not extrapolate provider behavior from absent data.

The artifact's disposition limits accepted facts to what the safe metadata directly supports and nothing more.

### Q4: Are residuals and next gate recommendation appropriate?

**Verdict: PASS**

Residuals:
- Chapter 3 missing required marker as active blocker with disposition gate routing — appropriate, follows the established pattern from prior blocker dispositions (Chapter 5 disposition at `746ff7e`)
- Provider behavior unclassified — appropriate, prevents over-inference from absent provider diagnostics
- Manifest null fields as evidence limitation — appropriate, correctly warns against using this artifact for source-policy proof
- Full Route C completion unproven — appropriate, the run exited 1 and final assembly is incomplete
- Release/readiness unproven — appropriate, preserves `NOT_READY`

Next gate recommendation: `Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition Gate` — appropriate sequencing. This mirrors the Chapter 5 pattern: disposition first, then diagnostic evidence, then plan, then implementation. The recommendation correctly specifies disposition rather than direct implementation or fix planning, which would be premature without understanding why Chapter 3's required-output marker gap resurfaced after item_01 was routed to `render_evidence_gap` and the prior live evidence at `2f8dce9` accepted Chapter 3.

### Q5: Any blocker before controller acceptance?

**Verdict: No blocker**

No discrepancies were found between the evidence artifact's claims and the safe runtime metadata. The artifact is internally consistent, properly bounded, and does not overread. The artifact correctly preserves `NOT_READY` and does not claim readiness or release state.

One observation (not a blocker): the runtime metadata shows Chapter 3 `attempt_count=null` in the chapter file while `summary.json.first_failed.attempt_count=1`. This is a minor runtime metadata internal inconsistency that does not affect the evidence artifact's accuracy. The controller may optionally note this as a non-blocking diagnostic residual.

## 3. Final Verdict

```text
PASS
```

Release/readiness: `NOT_READY`
