# DS Review: Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Post-fix Bounded Live Re-evidence

Date: 2026-06-14

Role: AgentDS reviewer (not controller)

Review target: `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-20260614.md`

## 1. Verdict

**PASS**

The evidence accurately states all safe metadata facts, correctly concludes Chapter 2 is accepted and no longer first failed, correctly identifies Chapter 6 `invalid_marker` as the new first failed blocker, preserves `NOT_READY`, avoids source-policy/fallback drift, and recommends an appropriate narrow next gate. No findings.

## 2. Cross-check Evidence

### 2.1 Command and exit code

- Command string is stated exactly, consistent with the artifact directory name (`004393-2025-…`) and `cli_command` in `manifest.json`.
- Exit code `1` is consistent with `orchestration_status=partial`, `final_assembly_status=incomplete`, and Chapter 6 `blocked`.

### 2.2 Artifact path

- `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/` exists and contains the four inspected metadata files (`manifest.json`, `summary.json`, `chapters/chapter-02.json`, `chapters/chapter-06.json`).

### 2.3 Safe metadata facts (evidence §4 vs source files)

| Evidence claim | Source | Match |
|---|---|---|
| `fund_code=004393` | `manifest.json:15`, `summary.json:150` | ✓ |
| `report_year=2025` | `manifest.json:24`, `summary.json:273` | ✓ |
| `run_id=host_run_8bbf668bcf7644ec` | `manifest.json:31`, `summary.json:274` | ✓ |
| `orchestration_status=partial` | `manifest.json:18`, `summary.json:151` | ✓ |
| `final_assembly_status=incomplete` | `manifest.json:19`, `summary.json:141` | ✓ |
| first failed `chapter_id=6` | `summary.json:144` (first_failed) | ✓ |
| first failed `status=blocked` | `summary.json:147` | ✓ |
| first failed `stop_reason=llm_contract_violation` | `summary.json:148` | ✓ |
| first failed `failure_category=prompt_contract` | `summary.json:145` | ✓ |
| first failed `failure_subcategory=invalid_marker` | `summary.json:146` | ✓ |
| first failed `runtime_operation=writer` | `summary.json:442` (runtime_diagnostics.first_failed) | ✓ |
| first failed `provider_attempt_count=0` | `summary.json:438` | ✓ |
| host `status=failed` | stderr diagnostic text | ✓ |
| `timeout_classification=none` | stderr diagnostic text | ✓ |
| `cancel_reason=none` | stderr diagnostic text | ✓ |
| `elapsed_ms=241702` | stderr diagnostic text | ✓ |

Evidence correctly reports `0/unknown` from stderr for provider attempts alongside `0` from `summary.json` — these are two consistent views of the same fact (stderr uses a `value/inference` format; summary reports the exact integer).

### 2.4 Chapter matrix (evidence §5 vs `summary.json` chapter_matrix)

All six chapters cross-checked:

- **Ch1**: status `accepted`, stop_reason `none`, failure_category `null`, failure_subcategory `null`, attempt_count `1`, accepted_conclusion `true`, accepted_draft `true` — matches.
- **Ch2**: status `accepted`, stop_reason `none`, failure_category `null`, failure_subcategory `l1_numerical_closure`, attempt_count `2`, accepted_conclusion `true`, accepted_draft `true` — matches. The `failure_subcategory` with `failure_category=null` is correctly described in evidence as non-terminal residual metadata from the prior attempt-level L1 phase.
- **Ch3**: all null/none, attempt_count `1`, accepted — matches.
- **Ch4**: all null/none, attempt_count `1`, accepted — matches.
- **Ch5**: all null/none, attempt_count `1`, accepted — matches.
- **Ch6**: status `blocked`, stop_reason `llm_contract_violation`, failure_category `prompt_contract`, failure_subcategory `invalid_marker`, attempt_count `1`, accepted_conclusion `false`, accepted_draft `false` — matches.

### 2.5 Final assembly issues (evidence §6 vs `summary.json` final_assembly_issues)

All five issues verified present in `summary.json` with matching `issue_id`, `reason`, and `severity=blocking`. Evidence correctly traces the cascade: Chapter 6 blocked → missing draft/conclusion → Chapter 7 readiness blocked → final assembly incomplete.

### 2.6 Stderr chapter_matrix transcription

Stderr `chapter_matrix=1:accepted/none/unknown/unknown;2:accepted/none/unknown/l1_numerical_closure;3:accepted/none/unknown/unknown;4:accepted/none/unknown/unknown;5:accepted/none/unknown/unknown;6:blocked/llm_contract_violation/prompt_contract/invalid_marker` — matches evidence table.

### 2.7 Chapter 2 terminal state (evidence claim: "Chapter 2 accepted, no longer first failed")

`chapter-02.json` confirms:
- `status: "accepted"` (line 216)
- `stop_reason: "none"` (line 217)
- `accepted: true` (line 2)
- Attempt 1 audit: `audit_status: "pass"`, `audit_accepted: true`
- `failure_category: null` (line 208)

`summary.json` `first_failed.chapter_id: 6`, not 2.

Conclusion is correct: Chapter 2 is accepted and is not the first failed chapter in this exact sample.

### 2.8 Chapter 6 blocker (evidence claim: "Chapter 6 invalid_marker is new first failed blocker")

`chapter-06.json` confirms:
- `status: "blocked"` (line 170)
- `stop_reason: "llm_contract_violation"` (line 171)
- `failure_category: "prompt_contract"` (line 157)
- `failure_subcategory: "invalid_marker"` (line 158)
- 4 `writer:invalid_anchor_marker` issues at positions 63, 711, 1095, 1521
- `writer_status: "blocked"`, no `writer_draft_file`

`summary.json` `first_failed` confirms chapter 6 as the first failed.

Conclusion is correct.

## 3. Gate Boundary Compliance

| Check | Result |
|---|---|
| Avoids readiness/MVP/LLM-ready claims | ✓ — `NOT_READY` stated 5 times; verdict includes `NOT_READY` |
| Preserves EID single-source/no-fallback | ✓ — §1 and §7 explicitly affirm |
| No source-policy drift | ✓ — no fallback, Eastmoney, or source expansion mentioned |
| No source/test/runtime changes recommended | ✓ — evidence-only gate |
| Artifact boundary: only safe metadata read | ✓ — writer/auditor/repair markdown, prompt bodies, provider payloads, PDF/source/cache bodies, final report body all declared not read |
| Does not read reviewer/auditor/repair bodies | ✓ — explicitly listed in §3 |

## 4. Recommended Next Gate

`Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate`

Assessment: appropriate and narrow. It directly targets the newly observed first-failed blocker without expanding scope. It follows the established disposition-gate pattern (compare Chapter 3 item 01 fact-gap disposition, Chapter 2 L1 live-regression disposition). It does not presume root cause, prescribe a fix, or claim readiness.

## 5. Residuals

- Chapter 2 `failure_subcategory: l1_numerical_closure` persists as non-terminal metadata (correctly noted in evidence §8). This is a monitoring signal, not a current blocker, and does not affect the evidence conclusions.
- Chapter 2 required 2 attempts (one repair) to reach accepted. The evidence notes this in the attempt count and residual metadata. The determinism of the repair path across different live samples remains unproven — correctly deferred, not claimed.
- Chapter 6 `invalid_marker` has 4 instances in a single writer attempt with `response_chars=3120` and `max_output_chars=12000`. Whether the invalid markers are a prompt-contract gap or an LLM output-format reliability issue is correctly left to the next disposition gate.

## 6. Recommendation for Controller

Accept this evidence as `PASS`. Route to `Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate` for root-cause classification (prompt-contract gap vs LLM output-format reliability), with the same `NOT_READY`, EID single-source/no-fallback, and bounded-scope constraints.
