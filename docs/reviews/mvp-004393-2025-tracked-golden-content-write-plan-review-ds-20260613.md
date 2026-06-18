# DS Plan Review — 004393 / 2025 Tracked Golden Content Write Plan

Date: 2026-06-13

Reviewer role: DS plan reviewer

Target: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-20260613.md`

Gate: `004393 / 2025 Tracked Golden Content Write Planning Gate`

Verdict: `PASS_WITH_FINDINGS`

## 1. Reviewed Target and Scope

The plan under review decides whether seven accepted candidate rows from the same-year reviewed golden content evidence may proceed to tracked golden content write, or whether controlled source-body verification must happen first. The plan concludes that source-body verification must happen first and rejects direct tracked write implementation. It recommends a next gate (`004393 / 2025 Controlled Source-body Verification Gate`) and sketches its minimum scope, validation matrix, review plan, stop conditions, and residuals.

## 2. Assumptions Tested

| # | Assumption | Verdict |
|---|---|---|
| A1 | Source-body residuals on candidate rows are insufficient for correctness oracle promotion. | Supported. Design doc `fund_code + report_year + field_name + sub_field` identity contract requires exact values; FQ1/block severity means unverified rows become blocking truth. |
| A2 | The seven candidate rows have locators specific enough for controlled source-body verification. | Partially supported. Five `basic_identity.*` rows cite `§2 page-5 page-5-table-0`; `benchmark.benchmark_name` cites `§2 page-5-table-1`; `investment_objective` cites `§2 page-5 page-5-table-1`. These are specific but their machine-resolvability in PDF body text is unproven. |
| A3 | The recommended next gate (controlled source-body verification) is compatible with current control-truth boundaries. | **Tension identified.** See Finding F1. |
| A4 | The two fee rows are correctly excluded per the current comparable golden contract. | Supported. Golden answer template and instructions mark `fee_schedule` as skipped; both DS and MiMo reviews concur; controller judgment accepted rejection. |
| A5 | The validation matrix commands are non-destructive in the planning gate and correctly scoped for future gates. | Mostly supported. See Finding F5 for a future-gate concern. |

## 3. Findings

### F1 — Medium — Source-body verification gate implicitly requires live access not yet authorized

- **位置**: Decision section "source-body verification first" and recommended next entry "Controlled Source-body Verification Gate"
- **问题类型**: 架构边界 / 不可直接实施
- **当前写法**: The plan recommends a next gate whose minimum scope is "Read only the 2025 annual-report body for `004393` through the project-authorized document repository boundary." It calls this a "controlled" gate requiring "explicitly authorized repository-bounded source-body verification."
- **反例/失败场景**: The current production document repository boundary (`FundDocumentRepository`) requires live EID/network access to fetch an annual report PDF. The current control truth (startup packet §4, implementation-control.md "Non-goal Reminder") explicitly says live EID/network/PDF/FDR commands are not authorized without a separately reviewed gate. The plan acknowledges this indirectly by saying the verification gate must be "explicitly authorized," but does not address the circular dependency: the source-body verification gate cannot execute without live access, and live access cannot be obtained without a gate that authorizes it. If the verification gate opens and the 2025 PDF is not already cached locally, the gate will stall at its first step.
- **为什么有问题**: The plan delegates the live-authorization problem to the next gate without providing the next gate's planner with the constraint that live access must be separately authorized first. An implementation agent reading only this plan would not know that the verification gate itself needs a prerequisite live-authorization step or a check for local PDF availability.
- **直接证据**: Startup packet §4: "do not run live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness, release, PR, push or merge commands." Implementation-control.md Non-goal Reminder: "additional live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands beyond accepted evidence checkpoint `271a052`." The `271a052` checkpoint only authorized `004393 / 2021-2025`, not a new `004393 / 2025` body read.
- **影响**: 实施 Agent 跑偏 — the next gate's planner may design a verification gate that assumes live access is already authorized, leading to a blocked gate or an unauthorized live command.
- **建议改法和验证点**: Add an explicit prerequisite to the recommended next entry: either (a) confirm the 2025 annual-report PDF for `004393` is already locally available (e.g., in the user-owned `基金年报/` directory, noting that the data artifact disposition classified those PDFs as `leave-untracked`) before opening the verification gate, or (b) explicitly state that the source-body verification gate must include a live EID authorization sub-gate as its first slice. The stop conditions should also include "Stop if the 2025 annual-report body cannot be loaded through the repository boundary AND no locally available PDF exists."
- **修复风险**: 低 — a one-sentence prerequisite note resolves the ambiguity.
- **严重程度**: 中

### F2 — Low–Medium — No partial acceptance path for source-body verification

- **位置**: Stop conditions: "Stop if any of the seven candidate rows cannot be matched exactly to source body text/table evidence."
- **问题类型**: 切片过粗 / open question 未收敛
- **当前写法**: All-or-nothing stop: if any one row fails verification, the entire gate stops.
- **反例/失败场景**: Six `basic_identity.*` rows match exactly against the annual-report body, but `benchmark.benchmark_name` formula characters differ in a single whitespace or punctuation character (e.g., `×` vs `*`). The plan's stop condition would block all seven rows, discarding six verified rows that could independently become tracked golden truth.
- **为什么有问题**: The identity contract `(fund_code, report_year, field_name, sub_field)` makes each row independently verifiable. Blocking all rows because one fails is unnecessarily coarse and contradicts the row-level independence built into the golden answer schema. The controller judgment already accepted each row with an independent disposition; the verification gate should preserve that granularity.
- **直接证据**: Design doc: correctness oracle identity key is `fund_code + report_year + field_name + sub_field` — row-level, not batch-level. `golden_answer.py` validates and rejects at the individual record level.
- **影响**: 后续返工 — a single problematic row could force re-planning of the entire verification gate, when only that row needs a separate disposition.
- **建议改法和验证点**: Change the stop condition to per-row granularity: "Stop for any individual row that cannot be matched; that row must be deferred or rejected in the verification controller judgment. Verified rows may proceed independently." Add a stop-condition category for "partial pass" where the controller judgment explicitly lists which rows passed and which failed.
- **修复风险**: 低 — a wording change in stop conditions.
- **严重程度**: 低—中

### F3 — Low — Source-body match criteria undefined

- **位置**: Proposed verification scope: "Confirm each row's exact `expected_value`, confidence, and source locator" and "confirm formula characters, percentage weights, index names and currency-adjustment wording exactly."
- **问题类型**: 契约缺失
- **当前写法**: The plan says to "verify" and "confirm" but does not define what constitutes a successful match between a candidate `expected_value` and the annual-report body text.
- **反例/失败场景**: A candidate row has `expected_value: "安信企业价值优选混合型证券投资基金"` and the PDF body text contains `"安信企业价值优选混合型证券投资基金A"` (with share class suffix). Is this a match or mismatch? Without defined match criteria (exact string equality, normalized comparison, substring match, fuzzy match with threshold), the verification agent must invent its own standard.
- **为什么有问题**: The verification agent needs unambiguous match criteria to produce a reviewable result. Without them, two reviewers could disagree on whether the same body text "confirms" a candidate value, making the verification gate's output non-deterministic and unreviewable.
- **直接证据**: The plan's validation matrix row "Source-body row verification" says "Row-by-row exact comparison against body/table text" but does not define "exact comparison" for fields where the PDF text may differ in whitespace, punctuation, or share-class suffix from the candidate value.
- **影响**: review 不可验收 — reviewer cannot determine whether the verification agent's match/mismatch judgment is correct without independently re-reading the PDF.
- **建议改法和验证点**: Add a match-criteria section to the source-body verification scope: (1) for identity fields (`fund_name`, `fund_code`, `management_company`, `custodian`): normalized whitespace-insensitive exact match; (2) for `inception_date`: ISO-format date equality; (3) for `investment_objective`: the body text must contain the candidate value as a contiguous substring after whitespace normalization; (4) for `benchmark.benchmark_name`: character-by-character exact match after stripping leading/trailing whitespace. Any deviation must be recorded as a mismatch with explicit diff.
- **修复风险**: 低 — a short match-criteria subsection.
- **严重程度**: 低

### F4 — Low — investment_objective span boundary verification may be inherently manual

- **位置**: Verification scope: "For `product_profile.investment_objective`, confirm the exact source-body span and record whether `medium` confidence remains required."
- **问题类型**: open question 未收敛
- **当前写法**: The plan treats span-boundary confirmation as a mechanical verification step.
- **反例/失败场景**: The annual report §2 "投资目标" section is a prose paragraph like "本基金的投资目标是在严格控制风险的前提下，通过积极主动的投资管理，力争实现基金资产的长期稳健增值。" The candidate `expected_value` may be a human-selected excerpt of this paragraph. The PDF body has no machine-readable span boundaries — there is no XML tag, no structured field delimiter. The verification agent cannot programmatically determine where the span starts and ends; it must rely on human judgment. If the verification agent is an LLM or a human, the result is a new judgment, not a mechanical verification of the candidate's judgment.
- **为什么有问题**: The plan presents this as "verification" when it is actually re-extraction. The candidate's `medium` confidence already acknowledges span-boundary ambiguity. "Verifying" the span means making the same judgment again, which could produce a different result, creating a conflict between the candidate and the "verified" value without a clear resolution rule.
- **直接证据**: Candidate row uses `confidence: medium` with rationale "long-text span requires bounded judgment." The golden answer instructions say `medium` means "需要判断（如多列选哪一列、文本截取范围）." The design doc offers no machine-readable span-boundary contract for free-text fields.
- **影响**: 实施 Agent 跑偏 — the verification agent may spend disproportionate effort on a fundamentally manual step, or may produce a span that conflicts with the candidate without clear authority to override.
- **建议改法和验证点**: Explicitly scope `investment_objective` verification as "confirm the candidate value appears verbatim in the source body" rather than "confirm exact span boundaries." If the candidate value is a verbatim substring of the body text, accept it; if not, record the discrepancy. Do not require the verification agent to re-judge span boundaries. Keep `medium` confidence unless the verbatim check conclusively passes or fails.
- **修复风险**: 低 — scope adjustment only.
- **严重程度**: 低

### F5 — Low — Future JSON rebuild lacks explicit backup/rollback step

- **位置**: Validation matrix, "Strict JSON build" and "No tracked-output overwrite accident" rows (future write implementation gate).
- **问题类型**: 契约缺失
- **当前写法**: The future write implementation gate's validation matrix runs `build_golden_answer_json(...)` which overwrites `reports/golden-answers/golden-answer.json`, then runs `git diff` to verify only intended keys changed. There is no pre-write backup step.
- **反例/失败场景**: The `build_golden_answer_json` function writes the output file before the `git diff` verification check runs. If the Markdown contains a valid but incorrect `004393 / 2025` block (e.g., wrong `expected_value` for `fund_name`), the JSON is already overwritten. The subsequent `git diff` check would show the `004393 / 2025` keys changed as intended, but would not catch that the value itself is wrong — because the diff check only verifies which keys changed, not whether the new values are correct. The source-body verification gate is supposed to catch wrong values, but if a process error causes a wrong value to slip through, the JSON is corrupted with no backup.
- **为什么有问题**: The verification chain has a gap: source-body verification confirms values, then a separate implementation gate writes them. If the implementation agent makes a transcription error between verified values and Markdown input, the `git diff` check won't catch it because it validates key scope, not value correctness.
- **直接证据**: `build_golden_answer_json` at `golden_answer.py:131` writes directly to `output_path` after parsing. The `git diff` check at plan validation matrix row "No tracked-output overwrite accident" only compares `(fund_code, report_year, field_name, sub_field)` keys, not values.
- **影响**: 数据损坏 — a transcription error in the write implementation could produce incorrect golden answer rows that trigger FQ1/block false positives or false negatives.
- **建议改法和验证点**: Add to the future write implementation validation matrix: (1) before `build_golden_answer_json`, copy the existing `golden-answer.json` to a timestamped backup path; (2) after build, add a value-level cross-check: compare each new/updated record's `expected_value` against the source-body verification artifact's accepted values; (3) if the cross-check fails, restore from backup. This should be a stop condition.
- **修复风险**: 低 — additive validation step only.
- **严重程度**: 低

## 4. Positive Findings

The plan correctly:

- Rejects direct tracked write from candidate-level acceptance. Given that candidate rows carry explicit source-body residuals and FQ1 correctness conflicts are `block` severity, writing unverified rows into the correctness oracle would be structurally unsound.
- Excludes the two fee rows with clear reasoning tied to the accepted comparable contract (golden answer template/instructions mark `fee_schedule` as skipped). No scope creep.
- Preserves the `NOT_READY` state and explicitly lists release/readiness, fixture promotion, and cleanup as non-goals or deferred residuals.
- Scopes the future write implementation to the reviewed-Markdown→JSON build path, rejecting hand-edited JSON.
- Provides a comprehensive validation matrix that covers parser smoke, identity uniqueness, fee exclusion, Markdown→JSON build provenance, loader round-trip, overwrite safety, test regression, and boundary diff.
- Lists stop conditions that cover all material failure modes: body unavailability, row mismatch, span ambiguity, formula deviation, fee-row leakage, JSON hand-edit, unrelated-row mutation, and unauthorized side effects.

## 5. Required Amendments

| # | Finding | Amendment |
|---|---|---|
| F1 | Live authorization circular dependency | Add to recommended next entry: "Prerequisite: before opening the source-body verification gate, either confirm the `004393 / 2025` annual-report PDF is already locally accessible, or include a live EID authorization sub-slice as the verification gate's first step. Stop if neither condition is met." |
| F2 | All-or-nothing stop condition | Change stop condition from "Stop if any of the seven candidate rows cannot be matched" to "Stop for each individual row that cannot be matched; that row must be deferred or rejected. Rows that pass independent verification may proceed." |
| F3 | Match criteria undefined | Add a match-criteria subsection defining exact comparison semantics per field category (identity fields, date fields, long-text fields, formula fields). |

F4 and F5 are low-severity recommendations for the next gate's planner, not required amendments for this planning gate.

## 6. Open Questions

- Can the 2025 annual-report body be accessed without a new live EID command? The data artifact disposition classified `基金年报/` PDFs as `user-owned/data artifact candidate` with `leave-untracked` — the next gate's planner should check whether the needed PDF already exists locally before requesting live authorization.
- Should `investment_objective` verification be scoped as "verbatim substring confirmation" rather than "span boundary confirmation" to avoid re-litigating a human judgment?

## 7. Residual Risks

| Risk | Severity | Owner | Suggested tracking |
|---|---|---|---|
| The source-body verification gate may be blocked if live EID access is required but not yet authorized. | Medium | Controller / next gate planner | Track as a prerequisite check in the verification gate's plan. |
| `investment_objective` span-boundary judgment may produce a different result than the candidate row, creating a conflict without a resolution rule. | Low | Golden content owner | Track in the verification gate's stop conditions or controller judgment. |
| Fixture promotion remains year-blind and unresolved — even after tracked golden content is written, fixture projection still cannot express `004393 / 2025`-specific promotion. | Medium | Fixture promotion owner | Already tracked as a separate residual in the control doc; no action in this gate. |

## 8. Conclusion

**Verdict: `PASS_WITH_FINDINGS`**

The plan makes the correct architectural decision (source-body verification before tracked write) and correctly rejects direct write from candidate-level acceptance. The scope boundaries, fee-row exclusion, validation matrix, and stop conditions are well-formed. The three required amendments (F1–F3) are low-risk clarifications that do not change the plan's direction. After these amendments, the plan is ready for controller judgment and can route to the next gate.

No blocking findings. All findings are advisory amendments that improve the plan's executability for the next gate's planner.
