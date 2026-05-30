# Plan Review: 110020 Reviewed Coverage Candidate Decision Plan

> Reviewer: AgentMiMo (independent plan reviewer, not controller)  
> Date: 2026-05-27  
> Target: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md`  
> Gate: `110020 reviewed coverage candidate decision gate`

## Truth Sources Used

| Source | Role |
|---|---|
| `AGENTS.md` | Agent execution rules, hard constraints, module boundaries |
| `docs/design.md` v2.2 §1-§12 | Design truth: architecture, quality gate, golden answer, source provenance, index profile, tracking error |
| `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point | Control truth: current phase, accepted artifacts, next cursor |
| `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | Accepted provenance rerun: 110020/2024 classification |
| `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md` | Bounded evidence rerun: command fidelity, row consistency, quality notes |
| `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-controller-judgment-20260527.md` | Controller accepted next cursor: 110020 reviewed coverage candidate decision gate |
| `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md` | Small baseline: 110020 visible as index fund, index/QDII fallback-blocked, golden corpus v1 not ready |

## Verdict: PASS_WITH_FINDINGS

The plan is correctly scoped, uses accepted evidence, and respects all hard prohibitions. Five findings of varying severity are identified below. None are blocking, but the medium-severity findings should be addressed before the evidence gate executes.

---

## Focus 1: 是否正确把 110020/2024 限定为 reviewed coverage candidate evidence gate 输入，而不是 promotion

**结论：PASS**

Plan correctly limits 110020/2024 to evidence gate input:

- Accepted Evidence Summary table: `promotion_disposition: not_promoted` (line 50)
- Candidate A entry conditions: "The later gate explicitly treats `110020` as an index slot coverage candidate under review, not as durable baseline / clean denominator / fixture / golden material" (line 83)
- All three terminal states in Acceptance Matrix: `promotion_disposition=not_promoted` (lines 174-176)
- Explicit Non-Goals: "Do not promote `110020` to durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus" (line 184)
- Recommendation section explicitly states why not enter `golden answer corpus v1` (lines 148-154)
- Forbidden scope section lists all promotion-related prohibitions (lines 30-33)

No scope creep toward promotion detected.

---

## Focus 2: Evidence summary 是否与 accepted provenance rerun 和 small baseline artifacts 同源一致

**结论：PASS**

Evidence summary field-by-field cross-reference against accepted provenance rerun controller judgment (lines 26-28 of that artifact):

| Plan field | Plan value | Accepted artifact value | Match |
|---|---|---|---|
| `fund_code` | `110020` | `110020` | yes |
| `report_year` | `2024` | `2024` | yes |
| `source_provenance_status` | `complete` | `complete` | yes |
| `fallback_used` | `true` | `true` | yes |
| `primary_failure_category` | `unavailable` | `unavailable` | yes |
| `fallback_eligibility` | `eligible` | `eligible` | yes |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `fallback_used_primary_failure_category_eligible` | yes |
| `quality_gate_status` | `warn` | `warn` | yes |
| `terminal_state` | `provenance_eligible_for_next_review` | `provenance_eligible_for_next_review` | yes |
| `promotion_disposition` | `not_promoted` | `not_promoted` | yes |

Quality notes (plan line 55-56): "Public quality notes cite `FQ2` warn for `turnover_rate` and `FQ2F` warn for `110020` P1 field failure" — matches bounded evidence rerun artifact line 41.

Small baseline corpus v1 controller judgment (line 27): "`110020` / 2024 / `index_fund`: kept visible as fallback-blocked excluded row" — this characterization predates the provenance rerun. After the rerun, 110020 is no longer "fallback-blocked" in the source provenance sense; it is now `complete`/`eligible`. The plan correctly reflects the post-rerun state rather than the older small baseline characterization. This is not an inconsistency; it is correct evolution of evidence.

---

## Focus 3: Unresolved risks 是否完整

**结论：PASS_WITH_FINDINGS (2 medium, 1 low)**

The plan identifies 5 unresolved risks. Cross-reference against review focus checklist:

| Required risk | Present | Assessment |
|---|---|---|
| `turnover_rate` P1 warn | yes (line 67) | Correctly described; quality notes evidence cited |
| Strict golden not configured | yes (line 68) | Correctly described; FQ0 info evidence cited |
| Reviewed fact readiness | yes (line 69) | Correctly described |
| Fixture-promotion absence | yes (line 70) | Correctly described |
| Index methodology/constituents/tracking evidence | yes (line 71) | Correctly described |

**Finding M1 (medium): 缺少 index-lens evidence sufficiency 定义**

Risk table row (line 71) correctly identifies that "index methodology, constituents, tracking quality, or index-lens evidence sufficiency" is not yet reviewed. However, the plan does not define what would constitute *sufficient* index-lens evidence for 110020 as an `index_fund` candidate. The later evidence gate needs acceptance criteria for this risk, not just an obligation to "record whether [it] is sufficient, insufficient, or out of scope."

Per `docs/design.md` §7.3-§7.4: `index_profile` and `tracking_error` are conditional P1 fields for index funds. Per §10: "`tracking_error` production golden rows only be added after reviewed direct observed disclosure evidence is accepted." The plan should note that `tracking_error` reviewed evidence is a specific prerequisite for this index fund candidate.

**Finding M2 (medium): strict golden not configured 缺少 concrete resolution path**

Risk table row (line 68) states strict golden is not configured, but does not specify what action would resolve it. Options include:
- Running `golden-prefill` + `golden-build` for 110020/2024 (requires reviewed facts first)
- Accepting that correctness cannot be reviewed until golden coverage exists
- Deferring the candidate until golden coverage is established

The plan's Candidate A recommendation implicitly chooses "accept that correctness is not reviewed," but this should be explicit as a carried-forward residual, not just a risk observation. The evidence gate acceptance matrix row for "Public score" (line 164) does say "Score output explicitly records strict golden coverage state," which partially addresses this, but the risk table itself should state the disposition.

**Finding L1 (low): fund_type 缺失**

The plan does not explicitly state that 110020 is `index_fund`. The small baseline controller judgment confirms this (line 27: "`index_fund`"). The risk about "index slot methodology / constituents / tracking evidence" implicitly tells the reader this is an index fund, but explicit identification would improve clarity for the evidence gate executor. This is a presentation issue, not an evidence gap.

---

## Focus 4: Recommended Candidate A 是否最小、是否应 defer/reject

**结论：PASS**

Candidate A is the minimum next step:

- The previous blocker was unknown fallback provenance; accepted evidence now resolves it as `complete`/`eligible`/`unavailable`.
- Quality is `warn`, not `block`, so the row is fit for reviewed evidence gate.
- The step is reversible: only authorizes evidence review, not corpus promotion or product behavior changes.

Candidate B (defer) and Candidate C (reject) are both presented with explicit entry conditions and stop conditions. The plan does not dismiss them; it provides the controller with all three options and recommends A.

Why not defer: The unresolved risks are warnings, not blockers. Deferring without a concrete missing-evidence plan would be unbounded. The plan correctly notes that the evidence gate itself will validate the risks.

Why not reject: No public evidence makes the row unsuitable. Quality is `warn`, provenance is `complete`/`eligible`.

Assessment: Recommendation is sound.

---

## Focus 5: Evidence gate acceptance matrix 是否 public-only、ignored outputs、tracked summary only、review required、stop conditions 足够

**结论：PASS_WITH_FINDINGS (1 medium, 1 low)**

| Matrix property | Present | Assessment |
|---|---|---|
| Public-only commands | yes | All three commands (`extraction-snapshot`, `extraction-score`, `quality-gate`) are public CLI |
| Ignored outputs | yes | "Ignored run directory" specified for snapshot, score, quality-gate steps |
| Tracked summary only | yes | "Tracked summary artifact only; generated run outputs remain ignored" (line 166) |
| Review required | yes | "Route to two independent reviewers...then controller judgment" (line 167) |
| Stop conditions | present but incomplete | See findings below |

**Finding M3 (medium): Stop conditions 过窄**

Current stop conditions for the evidence gate (lines 162-167) cover:
- Expansion to promotion: "Stop if the gate expands to baseline/golden/fixture promotion or implementation"
- Provenance regression: "Stop if provenance regresses"
- Quality block: "Stop if quality becomes `block`"
- FQ0-FQ6 weakening: "Stop if the plan weakens FQ0-FQ6 semantics"

Missing stop conditions:
1. **New unresolved warnings**: If fresh evidence produces *additional* P0/P1 warnings beyond the currently known `turnover_rate` P1 warn and FQ0 info, the evidence gate should stop and report, not silently carry forward an expanded warning set.
2. **Source strategy regression**: If `--force-refresh` triggers a different source strategy or fallback path than the accepted `primary_then_fallback` / `eastmoney` path, the gate should stop.
3. **Review BLOCK**: If independent reviews return `BLOCK` (not just `PASS` or `PASS_WITH_FINDINGS`), the gate should not proceed to controller judgment without explicit risk acceptance.

**Finding L2 (low): Independent review stop condition 不明确**

Acceptance matrix row "Independent reviews" (line 167) says "Reviews confirm public-only evidence, no promotion, no boundary violation, and explicit unresolved-risk disposition" as acceptance condition. The stop condition says "Stop if fewer reviews are accepted without controller risk acceptance, or if any material finding remains unresolved." This is reasonable but should explicitly state that a `BLOCK` verdict from any reviewer halts the gate.

---

## Focus 6: 是否违反硬禁止

**结论：PASS**

逐项检查 against `AGENTS.md` hard constraints and plan Forbidden scope:

| Hard prohibition | Violated | Evidence |
|---|---|---|
| No code implementation | no | Plan contains no code changes; only produces a review artifact |
| No renderer / FQ0-FQ6 changes | no | Evidence gate commands use public CLI; no FQ semantics changes |
| No Service / CLI default changes | no | Commands use existing `fund-analysis` CLI |
| No source strategy / FundDocumentRepository / source helper changes | no | `--force-refresh` is a public CLI option; no source strategy modification |
| No direct PDF/cache inspection | no | "Ignored run directory"; no private file access |
| No Host/Agent/dayu | no | No Host/Agent package creation or dayu integration |
| No baseline/golden/fixture promotion | no | All terminal states: `promotion_disposition=not_promoted` |
| No GitHub mutation | no | "Do not commit, push, create PR, merge, delete branches" (line 187) |
| Four-layer boundary | no | No `UI -> Service -> Host -> Agent` boundary violation |
| `docs/implementation-control.md` update | no | Explicitly listed as non-goal (line 185) |

Per `AGENTS.md`: "对基金文档的存取都应该只通过统一的文档仓库接口" — the evidence gate uses public CLI commands that internally use `FundDocumentRepository`. No direct file system access.

Per `AGENTS.md`: "生产年报 PDF 访问必须经过 `FundDocumentRepository`" — the evidence gate does not access PDF directly.

Per `docs/design.md` §12 plan review checks:
- §1.3 non-goals: not violated
- Four-layer boundary: maintained
- Production annual report access through `FundDocumentRepository` only: maintained
- No Host/tool loop/LLM splicing: maintained
- `pyproject.toml` engineering baseline: no changes
- Test coverage: not applicable (no code changes)
- License/repo hygiene: not affected

---

## Findings Summary

| ID | Severity | Description | Evidence |
|---|---|---|---|
| M1 | medium | 缺少 index-lens evidence sufficiency 定义；plan 未说明 `tracking_error` reviewed evidence 是 index fund 候选的具体前提 | Plan line 71; `docs/design.md` §7.3, §10 |
| M2 | medium | strict golden not configured 缺少 concrete resolution path；应明确为 carried-forward residual 而非仅 risk observation | Plan line 68; evidence gate matrix line 164 |
| M3 | medium | Stop conditions 过窄；缺少 new warnings、source strategy regression、review BLOCK 三个停止条件 | Plan lines 162-167 |
| L1 | low | fund_type 缺失；110020 是 `index_fund` 但 plan 未显式标注 | Small baseline controller judgment line 27 |
| L2 | low | Independent review stop condition 应显式说明 `BLOCK` verdict halt | Plan line 167 |

---

## Review Completeness Checklist

| Focus area | Reviewed | Verdict |
|---|---|---|
| 1. 限定为 evidence gate input 而非 promotion | yes | PASS |
| 2. Evidence summary 与 accepted artifacts 同源一致 | yes | PASS |
| 3. Unresolved risks 完整性 | yes | PASS_WITH_FINDINGS |
| 4. Candidate A 最小性 | yes | PASS |
| 5. Acceptance matrix 完整性 | yes | PASS_WITH_FINDINGS |
| 6. Hard prohibition compliance | yes | PASS |

---

## Recommendation

Controller should accept this plan with the following conditions:

1. **Before evidence gate executes**: Address M1 by adding `tracking_error` reviewed evidence as a specific index-lens prerequisite in the unresolved risks table or acceptance matrix.
2. **Before evidence gate executes**: Address M2 by adding a disposition line to the strict-golden risk (e.g., "carried forward as residual; correctness cannot be reviewed until golden coverage is established").
3. **Before evidence gate executes**: Address M3 by adding the three missing stop conditions to the acceptance matrix.
4. **Optional**: Add explicit `fund_type=index_fund` to the evidence summary (L1) and clarify BLOCK verdict handling (L2).

None of the findings are blocking. The plan is sound and the recommendation to proceed with Candidate A is correct.
