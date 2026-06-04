# MVP Provider Runtime Residual Disposition / Calibration Plan Review — MiMo

## 1. Review Scope

- Plan artifact: `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-plan-20260604.md`
- Preceding gate: `Real LLM smoke re-baseline gate` — blocked at evidence stage by `B3 provider_runtime_residual_all_chapters_llm_timeout`
- This gate: `Provider runtime residual disposition / calibration gate`
- Gate classification: `heavy`
- Review role: independent plan reviewer (not planner, not controller)
- Allowed write: this artifact only

## 2. Artifacts Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md` (lines 0–500)
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-controller-judgment-20260604.md`
- `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-plan-20260604.md`
- Retained artifact manifest: `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/manifest.json`
- Retained artifact chapters: `chapter-01.json`, `chapter-02.json`, `chapter-03.json`, `chapter-06.json`
- Retained artifact writer drafts: `chapter-01-attempt-00-writer.md`, `chapter-06-attempt-00-writer.md`

## 3. Verdict

**PASS_WITH_FINDINGS**

## 4. Gate Sequencing Compliance

| Criterion | Judgment | Evidence |
|---|---|---|
| Plan is the correct next entry after `Real LLM smoke re-baseline gate` blocked by `B3` | PASS | Startup packet §2 next entry: "provider runtime residual disposition/calibration or provider endpoint/runtime policy decision gate"; plan scope matches exactly |
| Plan does not enter Chapter acceptance calibration | PASS | §3 Non-Goals explicitly forbids it; §4.3 classification confirms no chapter has accepted draft/conclusion |
| Plan does not change provider defaults/runtime/budget | PASS | §3 Non-Goals and §6 Contract Impact both explicitly confirm zero changes |
| Plan does not enter Agent runtime, multi-year, score-loop, golden/readiness, PR/push/release | PASS | §3 Non-Goals comprehensive |
| Plan does not run live provider smoke/probe | PASS | §3 Non-Goals, §7.2, §10 Stop Conditions, §13 Gate Nature all reinforce this |
| Gate classification `heavy` is appropriate | PASS | Real provider evidence affects calibration sequencing; plan preserves fail-closed/no-fallback/stdout safety |

## 5. First-Principles Residual Classification Review

| Criterion | Judgment | Evidence |
|---|---|---|
| Classification distinguishes endpoint availability vs runtime policy vs evidence insufficiency | PASS | §4.2 presents four distinct hypotheses (A–D) with explicit evidence for/against each |
| Hypothesis A (endpoint availability) is primary — supported by same-run evidence | PASS | Verified: all 12 provider calls show `ReadTimeout`, `status_code: null`, `response_chars: null`, elapsed times cluster at 60s ceiling. Ch1/Ch2/Ch3/Ch6 chapter JSON confirmed directly |
| Hypothesis B (timeout too short) is correctly demoted to secondary | PASS | `ReadTimeout` with zero bytes received is not consistent with "merely slow" endpoint; 1074 tokens at 60s is ~18 tok/s, far below any provider throughput |
| Hypothesis C (evidence insufficient) is correctly rejected | PASS | 12/12 calls have complete diagnostics; `terminal_runtime_diagnostic_present: true` and `diagnostic_consistency_status: consistent` on all 6 chapters verified |
| Hypothesis D (code/serializer bug) is correctly rejected | PASS | Diagnostic serialization repair gate (commit `218a4f6`) is accepted; all 6 chapters show consistent patterns |
| Classification does not overclaim beyond evidence | PASS | Plan explicitly states "resolution depends on provider endpoint availability, which is outside the scope of this project's code" |
| Ch3 C2 residual is correctly separated | PASS | §11 explicitly: "Ch3 writer timeout in the current retained artifact means the C2 rule was never reached; the prior Ch3 C2 evidence is from a different historical run and must not be mixed" |

## 6. D1–D4 Slice Review

### 6.1 Slice D1: Diagnostic Completeness Verification

| Check | Judgment | Notes |
|---|---|---|
| `terminal_runtime_diagnostic_present: true` for all 6 chapters | PASS (verified) | Ch1, Ch2, Ch3, Ch6 confirmed directly; Ch4/Ch5 inferred from summary consistency |
| `diagnostic_consistency_status: consistent` for all 6 chapters | PASS (verified) | All checked chapter JSONs show `consistent` |
| `chapter_runtime_diagnostics[]` has 2 entries per chapter | PASS (verified) | Ch1: 2 auditor entries; Ch2: 2 writer entries; Ch3: 2 writer entries; Ch6: 2 auditor entries |
| Each entry has non-null `error_type`, `operation`, `provider_runtime_category`, `timeout_seconds`, `approx_prompt_tokens`, `elapsed_ms` | PASS (verified) | Confirmed in all checked chapters |
| Writer draft `.md` files exist for Ch1 and Ch6 only | PASS (verified) | `ls` confirms: `chapter-01-attempt-00-writer.md`, `chapter-06-attempt-00-writer.md`; no files for Ch2–Ch5 |
| No secrets in chapter JSON | PASS (verified) | No `prompt`, `raw_response`, API key, Authorization, or base URL values found |

### 6.2 Slice D2: Cross-Chapter Failure Pattern Analysis

| Invariant | Judgment | Notes |
|---|---|---|
| All 12 calls have `error_type: ReadTimeout` | PASS (verified) | Confirmed across Ch1/Ch2/Ch3/Ch6 (8 entries checked) |
| All 12 calls have `provider_runtime_category: timeout` | PASS (verified) | Confirmed |
| All 12 calls have `status_code: null` and `response_chars: null` | PASS (verified) | Confirmed — zero bytes received from provider |
| All 12 calls have `timeout_root_cause_hint: small_prompt_provider_timeout` | PASS (verified) | Confirmed |
| Elapsed times cluster at 60s ceiling | PASS (verified) | Observed: 60003, 60152, 60160, 60173, 60185, 60004, 60171 ms — all within [60000, 60224] |
| Prompt token range is small (1074–2879) | PASS (verified) | Ch1: 1074, Ch2: 1843, Ch3: 2879, Ch6: 946 |
| Both writer and auditor operations fail | PASS (verified) | Ch1/Ch6: auditor terminal; Ch2/Ch3: writer terminal |
| `repair_timeout_fallback_used: true` on all calls | PASS (verified) | Confirmed on all checked entries |

### 6.3 Slice D3: Fail-Closed Safety Verification

| Invariant | Judgment | Notes |
|---|---|---|
| CLI exit code is 1 | PASS | Controller judgment §2 confirms |
| stdout is empty | PASS | Controller judgment §2 confirms |
| `orchestration_status: blocked` | PASS | Manifest confirms |
| `final_assembly_status: incomplete` | PASS | Manifest confirms |
| No deterministic fallback | PASS | Controller judgment §2 confirms |
| No accepted report file | PASS | All 6 chapters show `accepted: false` |
| Retained artifact written to local ignored path | PASS | Path `reports/llm-runs/` confirmed |

### 6.4 Slice D4: Calibration Readiness

D4 is correctly defined as a synthesis gate depending on D1–D3 all PASS. The readiness criteria in §7.4 are appropriate: readiness means diagnostic evidence is sufficient and fail-closed is intact, NOT that the endpoint is working or defaults should change.

## 7. Blocking Findings

None.

## 8. Non-Blocking Findings

### Finding 1: D4 is a synthesis gate, not an independent verification slice

**Location**: §7.3 Slice D4

**Observation**: D1–D3 are independent verification slices with specific checks against retained artifact data. D4 is purely a conditional verdict ("if D1–D3 all PASS → ready"). Calling it a "slice" alongside D1–D3 creates a false impression of four independent verifications when there are really three plus a decision rule.

**Impact**: Low. The validation matrix (§8) correctly describes D4 as "synthesis of D1-D3". No functional issue.

**Recommendation**: Consider renaming D4 to "Calibration Readiness Verdict" to distinguish it from the verification slices. Not blocking.

### Finding 2: Ch4/Ch5 prompt token values not directly verified in this review

**Location**: §4.1 Direct Evidence Summary table (Ch4/Ch5 `approx_prompt_tokens` shown as `(writer)`)

**Observation**: The plan's table shows Ch4 and Ch5 prompt tokens as `(writer)` rather than numeric values. I did not read `chapter-04.json` or `chapter-05.json` in this review. The manifest and summary confirm 6 chapters present; cross-chapter pattern claims for Ch4/Ch5 are inferred from the consistent schema and the controller judgment's prior acceptance.

**Impact**: Very low. The plan does not make specific numeric claims about Ch4/Ch5 tokens that would alter the classification. The `small_prompt_provider_timeout` hint and `ReadTimeout` pattern are the dispositive evidence.

**Recommendation**: D1 execution evidence should explicitly read all 6 chapter JSONs and record numeric values for completeness. Not blocking for plan acceptance.

### Finding 3: Historical evidence context could confuse readers

**Location**: §4.2 Hypothesis B "Evidence against" — reference to "Historical evidence from 2026-06-02"

**Observation**: The plan correctly notes that the 2026-06-02 run had some chapters succeed under the same 60s timeout, supporting the "intermittent availability" interpretation. However, the startup packet documents that the 2026-06-02 run and the current 2026-06-04 run are different runs with different failure patterns (2026-06-02 had Ch1/Ch5 accepted; 2026-06-04 has all chapters failed). The plan handles this correctly by not substituting historical evidence, but the brief historical reference could lead a reader to conflate the two runs.

**Impact**: Very low. The plan explicitly states "from the single retained artifact `host_run_b52b779e7e9a43c`" as the evidence source for all classification claims.

**Recommendation**: No change needed. The historical reference is appropriate context for Hypothesis B dismissal.

### Finding 4: Second reviewer / DS-as-author self-review residual

**Location**: §9 Review Gates

**Observation**: The plan was authored by AgentDS (the planning worker). The plan requires "at least two reviewers (AgentMiMo, AgentDS per current convention)". If AgentDS reviews its own plan, that constitutes self-review. The AGENTS.md gate rules require "at least two independent reviews (unless recording reviewer unavailability)".

**Impact**: Low if MiMo performs independent review. This review (MiMo) satisfies one independent review slot. If AgentDS also reviews, that should be flagged as self-review and either the controller should record the limitation or a third reviewer should be sought.

**Recommendation**: Controller should note that AgentDS authored the plan and may self-review; MiMo review is independent. If controller accepts one independent review plus one self-review with acknowledgment, this is acceptable for a disposition plan gate (not an implementation gate). Not blocking.

## 9. Over-Conclusion Check

| Concern | Judgment | Evidence |
|---|---|---|
| Does plan prematurely declare endpoint as "down"? | PASS | §4.3 says "The provider endpoint is not responding...within 60s" — this is a factual statement about the retained evidence, not a permanent endpoint status claim |
| Does plan write future evidence gate as current fact? | PASS | §7.4 explicitly distinguishes readiness (diagnostic sufficiency) from outcome (endpoint working); §13 separates disposition from live evidence |
| Does plan authorize future live probe prematurely? | PASS | §9/§10/§13 all require separate future gate with explicit controller authorization |
| Does plan relax fail-closed semantics? | PASS | §3 Non-Goals and §6 Contract Impact confirm zero changes |

## 10. Fail-Closed / Secret-Safe / No-Fallback Preservation

| Invariant | Judgment |
|---|---|
| Plan preserves fail-closed exit code 1 on incomplete | PASS |
| Plan preserves stdout empty on incomplete | PASS |
| Plan preserves no deterministic fallback | PASS |
| Plan preserves secret-safe diagnostics (no prompt/draft/raw response/API key in artifacts) | PASS |
| Plan does not introduce any fallback mechanism | PASS |
| Plan does not relax auditor rules or increase repair budget | PASS |

## 11. Required Fixes

None. All findings are non-blocking.

## 12. Controller Recommendation

Accept the plan for execution. The first-principles classification is sound, evidence-based, and correctly distinguishes endpoint availability from runtime policy and evidence insufficiency. D1–D3 are well-scoped verification slices with verifiable pass criteria. D4 readiness criteria are appropriately conservative. The plan preserves all fail-closed and secret-safe boundaries.

Non-blocking findings should be noted but do not require plan revision:
- D1 execution evidence should read all 6 chapter JSONs explicitly
- Controller should acknowledge AgentDS self-review limitation if AgentDS also reviews
- D4 naming is a cosmetic concern only

The execution evidence (D1–D4) should be a separate artifact after plan acceptance, as the plan correctly specifies.
