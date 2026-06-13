# Provider/LLM Chapter 2 L1 Numerical Closure No-live Diagnostic Evidence

Date: 2026-06-14

Role: AgentCodex/procodex no-live diagnostic evidence worker

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Diagnostic Evidence Gate`

## Scope

This artifact records no-live diagnostic evidence for the current Chapter 2 L1 regression after checkpoint `1b9cd00`.

Allowed scope:

- compare prior-pass/current-fail Chapter 2 L1 attempt patterns using safe metadata only;
- verify whether the Chapter 2 L1 repair checklist still reaches the writer under no-live paths;
- verify whether the Chapter 3 required-output policy path currently changes Chapter 2 repair prompt assembly;
- run focused no-live tests only.

Out of scope:

- implementation, source/test/runtime behavior changes;
- live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands;
- writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body, or final report body reads;
- L1 weakening, repair budget default changes, source fallback changes, or readiness claims.

Release/readiness remains `NOT_READY`. EID single-source/no-fallback remains current policy.

## Evidence reviewed

Required control and review inputs:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-review-mimo-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-implementation-controller-judgment-20260614.md`
- `fund_agent/fund/chapter_writer.py`

Safe metadata inputs:

- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json`
- `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/summary.json`
- `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/chapters/chapter-02.json`

Focused no-live test/code inputs:

- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`

No forbidden body/payload/source/final report files were read.

## Commands run and results

| Command | Result |
|---|---|
| `git status --short` | Passed; workspace already dirty before artifact write, including modified `AGENTS.md`, `README.md`, `docs/design.md`, and multiple untracked residue paths. No cleanup or disposition was performed. |
| `git status --branch --short` | Passed; branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 103]`; same pre-existing dirty workspace observed. |
| `git diff --check` | Passed with no output. |
| `sed` / `rg` read-only inspections over allowed control, review, source and test files | Passed; used only allowed files. |
| `jq '.'` over the four allowed metadata JSON files | Passed; used safe metadata only. |
| `uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1_repair or l1_numerical_closure or repair_context" -q` | Passed: `6 passed, 40 deselected in 0.83s`. |
| `uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted" -q` | Passed: `4 passed, 76 deselected in 0.91s`. |
| `uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework or ch2_source_section" -q` | Passed: `6 passed, 43 deselected in 0.84s`. |

## Prior vs current metadata comparison

| Field | Prior run `4a531cbe94604e47` | Current run `605e381de24f4abb` | Diagnostic reading |
|---|---|---|---|
| Summary first failed | Chapter 3, `fact_gap`, `missing_required_facts` | Chapter 2, `prompt_contract`, `l1_numerical_closure`, `repair_budget_exhausted` | Current first blocker is Chapter 2 L1. |
| Chapter 2 terminal status | `accepted`, `stop_reason=none`, `failure_category=null`, non-terminal `failure_subcategory=l1_numerical_closure` | `failed`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure` | Prior Chapter 2 pass was repair-dependent; current repair did not clear L1. |
| Chapter 2 attempt count | 2 | 2 | Both runs used initial attempt plus one repair attempt. |
| Attempt 0 L1 count | 1 `programmatic:L1` issue | 2 `programmatic:L1` issues | Both runs share first-attempt L1 failure family; current run starts with more L1 findings. |
| Attempt 1 L1 count | 0 issues; audit passed | 2 `programmatic:L1` issues; audit failed | Difference is repair effectiveness, not initial L1 absence. |
| Repair decision | attempt 0 `action=regenerate`, then accepted | attempt 0 `action=regenerate`; attempt 1 `action=stop`, `repair_budget_exhausted` | Current default one-repair budget is exhausted. |
| Provider/runtime relation | first failed Chapter 3 has `provider_attempt_count=0`; Chapter 2 L1 diagnostics are auditor/programmatic | first failed Chapter 2 has `provider_attempt_count=0`; operation `auditor` | Current Chapter 2 failure is pre-provider and programmatic-audit classified. |
| Final assembly | `incomplete` | `incomplete` | Neither run proves completion/readiness. |

Limitation: safe metadata exposes status, issue ids, counts, writer response lengths, used fact/anchor ids, and artifact filenames. It does not expose attempt-level writer body shape, repair Markdown, raw prompt text, or model reasoning. Therefore this gate cannot prove from live bodies whether the model saw and ignored a specific checklist line; it can only prove the metadata pattern and no-live prompt assembly behavior.

## No-live diagnostic findings

### F1: Current Chapter 2 failure is repair-effectiveness failure, not clean-baseline regression

Prior Chapter 2 attempt 0 already failed L1 with `programmatic:L1:line:33:009a9dbf62` and was accepted only after attempt 1 cleared all programmatic issues. Current Chapter 2 attempt 0 and attempt 1 both fail L1 with two `programmatic:L1` issues each. The strongest metadata-supported description is: the same L1 family recurred, and the one allowed repair attempt no longer cleared it.

### F2: The Chapter 2 L1 repair checklist still reaches writer prompt assembly in current no-live code

Current `chapter_writer.py` assembles `fragments.repair_context` from both:

- `_repair_context_prompt(input_data.repair_context)`;
- `_ch2_l1_repair_guidance_prompt(chapter, input_data.repair_context)`.

The Chapter 2 L1 checklist renders only when `chapter.chapter_id == 2` and `repair_context.previous_issue_ids` contains an id starting with `programmatic:L1`. Focused writer tests prove:

- generic repair context is rendered without `extra_payload`;
- Chapter 2 L1 repair context renders `第2章 L1 数字闭环 repair checklist`;
- the checklist is absent for initial Chapter 2, non-Chapter-2, and non-L1 repair contexts;
- the typed `ChapterLLMRequest` carries `repair_context`.

Focused Service/orchestrator tests prove the second writer request receives the L1 repair context and its `user_prompt` contains the Chapter 2 checklist under a controlled fake-LLM path.

### F3: Current Chapter 3 required-output policy path does not route through the Chapter 2 L1 checklist condition

The Chapter 3 policy change is represented in current code by typed required-output planning/actions such as `render_evidence_gap`, `render_minimum_verification_question`, `delete`, and `block`. Those paths build required-output payload and preflight behavior. They do not participate in `_has_l1_numerical_closure_repair_issue()` or the `chapter.chapter_id != 2` gate inside `_ch2_l1_repair_guidance_prompt()`.

No git history comparison command was authorized, so this artifact does not claim byte-for-byte identity with checkpoint `842362d`. The no-live current-state evidence is narrower: after `1b9cd00`, the Chapter 2-specific checklist condition and orchestrator propagation still work, and the Chapter 3 typed required-output path is not on the Chapter 2 L1 checklist rendering branch.

### F4: L1 fail-closed behavior and repair-budget semantics are still preserved

Focused auditor tests prove:

- a concrete R=A+B-C / A=R-B / A-C percentage closure without nearby anchor triggers L1;
- the same closure with nearby anchor does not trigger L1;
- A-C percentage closure without nearby anchor triggers L1;
- missing/gap wording cannot wrap a concrete unanchored percentage closure to bypass L1;
- formula-framework explanation without concrete percentage is allowed;
- Chapter 2 source-section unanchored numeric closure still triggers L1, while nearby anchor allows it.

Focused orchestrator tests prove:

- L1 repair context is generated and sent to the repair writer request;
- when repair still leaves L1, the run stays fail-closed as `status=failed`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure`;
- no default repair-budget expansion was required or observed in the focused no-live path.

## Accepted/rejected hypotheses

| Hypothesis | Decision | Basis |
|---|---|---|
| H1: Current live failure is provider/network/runtime driven. | Rejected. | Safe metadata shows first failed Chapter 2 operation is auditor/programmatic and `provider_attempt_count=0`. |
| H2: Prior Chapter 2 was first-attempt clean and current run is a new L1 class. | Rejected. | Prior attempt 0 had one `programmatic:L1`; current attempts have two each. |
| H3: Chapter 2 L1 checklist is missing from current no-live writer assembly after `1b9cd00`. | Rejected. | Current code and focused writer/orchestrator tests prove the checklist renders and reaches the second writer request for Chapter 2 L1 repair. |
| H4: Chapter 3 required-output policy currently bypasses or owns the Chapter 2 L1 checklist path. | Rejected for current-state path. | Chapter 3 typed required-output actions are separate from the `chapter_id == 2` plus `programmatic:L1` checklist condition; focused tests still pass after `1b9cd00`. |
| H5: Current evidence proves the live model saw and ignored the checklist. | Rejected as overclaim. | Forbidden body/prompt/repair Markdown reads prevent attempt-level prompt/body proof. |
| H6: L1 should be weakened or warning-only. | Rejected. | Focused auditor and orchestrator tests preserve L1 fail-closed semantics. |
| H7: More live sampling is the next best diagnostic step. | Rejected for this gate. | Two live samples already show output sensitivity; no-live evidence identifies assembly intactness and repair ineffectiveness without stochastic provider sampling. |

## Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Attempt-level writer body shape and exact repair Markdown behavior | Unproven by design in this gate | Requires a future explicitly authorized body-read or controlled fixture/fake-LLM diagnostic, not live/provider sampling by default. |
| Whether the LLM ignored the checklist vs checklist wording remains too weak | Not directly proven | Narrow no-live fix planning should treat this as prompt-contract determinism problem, not as a proven missing-prompt bug. |
| Repair budget calibration | Deferred | Separate standard gate only; do not change default budget here. |
| Chapter 5 forbidden phrase blocker | Deferred downstream | Not first blocker for this diagnostic. |
| Provider/LLM full completion and content quality | Unproven | Future reviewed gates only; no readiness claim. |
| Workspace cleanliness and unrelated residue | Observed only via status | No disposition in this gate; not proof of readiness. |

## Next gate recommendation

Proceed to a narrow no-live fix planning gate.

Planning should assume:

- Chapter 2 L1 repair checklist currently reaches the writer under no-live paths;
- the current live failure is not explained by missing repair-context propagation;
- the next fix should target deterministic Chapter 2 L1 compliance under fake-LLM/fixture/no-live evidence, such as stronger prompt contract segmentation, safer required correction wording, deterministic post-writer validation guidance, or a bounded writer/auditor contract adjustment;
- L1 remains blocking and repair budget remains unchanged unless separately authorized.

Do not proceed directly to implementation without a reviewed narrow plan. Do not repeat live/provider evidence as the next step.

## Final verdict

READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY
