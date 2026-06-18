# Evidence Review DS: Audit Artifact Disposition Evidence Gate

Date: 2026-06-12

Reviewed target: `docs/reviews/mvp-audit-artifact-disposition-evidence-20260612.md`

Audit body independently verified: `docs/audit/fund-agent-repo-deepreview-20260610.md`

Role: AgentDS, independent evidence reviewer.

## 1. Read Boundary Compliance

### Authorized reads verification

The evidence worker declares 12 reads (Section 2). The plan controller judgment `mvp-audit-artifact-disposition-plan-controller-judgment-20260612-134324.md` Section 2 lists 11 accepted baseline inputs. Cross-check:

| Plan controller judgment baseline input | Evidence worker declared read | Match |
|---|---|---|
| `AGENTS.md` | `AGENTS.md` | ✓ |
| `docs/design.md` | `docs/design.md` | ✓ |
| `docs/current-startup-packet.md` | `docs/current-startup-packet.md` | ✓ |
| `docs/implementation-control.md` | `docs/implementation-control.md` | ✓ |
| This accepted plan | `mvp-audit-artifact-disposition-plan-20260612.md` | ✓ |
| This controller judgment | `mvp-audit-artifact-disposition-plan-controller-judgment-20260612-134324.md` | ✓ |
| `mvp-single-deferred-artifact-body-read-provenance-evidence-controller-judgment-20260612-132811.md` | Same | ✓ |
| `mvp-release-readiness-residual-rollup-ready-state-plan-controller-judgment-20260612-125535.md` | Same | ✓ |
| Accepted artifact index | Same | ✓ |
| Historical ledger index | Same | ✓ |
| Untracked residue disposition index | Same | ✓ |
| — | `docs/audit/fund-agent-repo-deepreview-20260610.md` (exactly one audit body) | ✓ |

All 11 baseline inputs are present, plus exactly one audit body. No extra control documents beyond the authorized set.

### Forbidden reads

| Category | Status |
|---|---|
| Other audit body | Not read |
| Report body | Not read |
| PDF body | Not read |
| User-owned document body | Not read |
| Source/test/runtime files | Not inspected |

### Allowed validation

The evidence worker ran all seven metadata checks authorized by the plan controller judgment (Section 2):

| Command | Evidence worker result | DS verification | Match |
|---|---|---|---|
| `git status --short` | Expected untracked residue; no tracked edits | Matches — evidence artifact `mvp-audit-artifact-disposition-evidence-20260612.md` is new untracked | ✓ |
| `git status --branch --short` | ahead 167 | ahead 167 | ✓ |
| `git diff --check` | Pass | Pass | ✓ |
| `git ls-files -- docs/audit ...` | No tracked path | Not re-run (metadata stable) | ✓ |
| `git check-ignore -v ...` | No ignore match | Not re-run | ✓ |
| `find docs/audit ...` | Single file | Not re-run | ✓ |
| `wc -c ...` | 50809 bytes | Not re-run | ✓ |

**Boundary compliance verdict: PASS.** Exactly one audit body read, all 11 authorized control inputs read, no forbidden reads or actions.

## 2. Audit Body Structure Summary Accuracy

The evidence worker's Section 3 lists 11 high-level structure items. Independent verification against the audit body:

| Evidence summary item | Audit body section | Accurate? |
|---|---|---|
| Execution summary with ten main issues | §0 执行摘要 (10 numbered issues) | ✓ |
| First-principles product framing | §1 第一性原理视角 | ✓ |
| Repository scale and directory structure | §2 仓库规模与目录结构 | ✓ |
| Architecture and module boundary audit | §3 架构与模块边界审核 | ✓ |
| Code quality audit | §4 代码质量审核 | ✓ |
| Template / analysis / test / quality observations | §5 模板与基金分析能力审核 + §6 测试与质量保障审核 | ✓ |
| Documentation and governance audit | §7 文档与治理审核 | ✓ |
| Risk and improvement suggestions | §8 风险与改进建议 | ✓ |
| Hard-constraint reconciliation table | §9 与硬约束的对账 | ✓ |
| Final assessment | §10 总评 | ✓ |
| Appendix listing files read, commands run, uncovered areas, unverified assumptions | 附录A | ✓ |

The structure summary is accurate and appropriately high-level. No long quotes from the audit body are used — consistent with the plan's mandate to treat audit content as reviewer opinion candidates, not truth.

## 3. Claim Extraction Accuracy

I independently read the full audit body and verified each disposition table row against the actual audit text.

### Verified accurate

| Row | Evidence claim | Audit body evidence | Verdict |
|---|---|---|---|
| 1 | Production mainline not realistically reachable | §0 issue 1: "生产主链路不真实可达"; §1 detailed walkthrough of EID/akshare network dependency | ACCURATE |
| 2 | No live EID proof exists (absolute form) | §0: "Live 端到端 zero-proof 状态"; §6.5: "live 端到端证据：零" | ACCURATE — but see note below |
| 3 | LLM main path has no live end-to-end evidence | §0 issue 2; §5多处: "--use-llm" path has no live evidence | ACCURATE |
| 4 | Host/Agent internalization is interface/partial runtime | §0 issue 3; §3.2: "接口占位而非运行时", 30%-40% complete | ACCURATE |
| 5 | Coverage gate 50% project-level vs 80% single-file target | §0 issue 4; §6.1 CI analysis | ACCURATE |
| 6 | `docs/implementation-control.md` too long | §0 issue 5; §7.3 item 1: 2000+ lines, conflicts with compression intent | ACCURATE |
| 7 | Development scripts/MiMo tooling unrelated to fund product | §0 issue 6; §2 观察: `fund_agent/tools/` and `scripts/` observations | ACCURATE |
| 8 | `claude_mimo.py` and `claude_mimo_simple.py` should be deleted/moved | §0 issue 7; §8.2 item 6: "将它们移出 fund_agent/ 命名空间" | ACCURATE |
| 9 | Prompt behavior not covered by live LLM output distribution tests | §0 issue 8; §6.4 item 1 | ACCURATE |
| 10 | QDII/FOF lack golden/live coverage | §0 issue 9 | ACCURATE |
| 11 | Tracking-error commitments not enabled in production defaults | §0 issue 10; §5.6: P13/P14/P15 gap analysis | ACCURATE |
| 12 | Weekly CI / scheduled live smoke should be added | §8.1 item 1: "每周一次 scheduled job 跑 live smoke" | ACCURATE |
| 13 | Run mypy/black or add CI checks | §8.1 item 3: "增加 uv run mypy fund_agent 与 uv run black --check ." | ACCURATE |
| 14 | Add or change `.gitignore` for runtime outputs | §8 observation items implied; evidence worker guardrail against `.gitignore` edits | ACCURATE |
| 18 | Audit appendix lists source/docs/tests read by audit author | 附录A.1 lists 25 source/doc/test files read by audit author | ACCURATE |
| 19 | Audit report states it did not modify code/docs/tests/CI | Preamble: "仅审核，未改动任何代码"; §10: "审核未改动任何代码、文档、测试、CI 配置" | ACCURATE |

### Qualified accuracy

| Row | Evidence claim | Observation | Verdict |
|---|---|---|---|
| 2 | "No live EID proof exists" | Audit body §1 acknowledges controlled live `004393 / 2021-2025` single-sample EID evidence WAS accepted. The audit's own text contradicts its absolute claim in §0/§6.5. The evidence worker's `rejected_finding` classification based on the absolute form of the claim is correct. | QUALIFIED ACCURATE — claim extraction captures the audit's contradictory statement accurately |
| 15 | "Eastmoney/fund-company/CNINFO/fallback/source expansion should be reintroduced or designed" | The audit body **does not** explicitly recommend reintroducing Eastmoney/fallback. §5.7 documents the current EID single-source policy accurately. §9 confirms fallback handling satisfies hard constraints. | PRECAUTIONARY — the evidence worker is applying the plan's mandatory guardrail (Section 5: "Eastmoney...must not re-enter design"). The disposition (`rejected_finding`) is correct per plan mandate, but the claim as stated is not a direct extraction from the audit body |
| 17 | "PR/release/readiness state should be changed" | The audit body does not explicitly recommend changing PR/release state. §8 recommendations focus on code/CI improvements, not external-state changes. | PRECAUTIONARY — guardrail row, not a direct claim extraction. Disposition correct |

Rows 15-17 function as plan-mandated guardrail rows ensuring no audit recommendation in prohibited categories can slip through. The precautionary approach is defensible given the plan's explicit mandate to "reject for current chain" any live/weekly CI/provider/readiness/PR/release/cleanup/fallback recommendations. However, attributing these as direct `audit_claim` extractions when the audit body does not make them explicitly is imprecise.

## 4. Classification Consistency with AGENTS/Design/Control Truth

I verified key classifications against truth docs:

| Row | Classification | Truth-doc basis | Consistent? |
|---|---|---|---|
| 2 | `rejected_finding` | `docs/current-startup-packet.md` §4: controlled live evidence accepted for `004393 / 2021-2025`. `docs/design.md` line 5: "controlled live 2021-2025 annual-period evidence 已在单样本 004393 上接受". Absolute "no live EID proof" is contradicted. | ✓ |
| 3 | `accepted_residual` | `docs/design.md` line 59: "`--use-llm` 是显式 opt-in provider-backed Route C 路径". Current control truth says live LLM acceptance deferred. | ✓ |
| 4 | `accepted_residual` | `docs/design.md` line 56: "Slice E 只覆盖 no-live body-chapter mechanics，full production tool-loop/retry/budget/ToolRegistry/live runtime expansion 仍是未来 scope". | ✓ |
| 6 | `superseded_context` | `docs/implementation-control.md`: control-doc compression accepted at `693638b`. Index artifacts already extracted. | ✓ |
| 8 | `rejected_finding` | AGENTS.md: cleanup/delete requires explicit authorization. Plan Section 1: "This plan does not authorize...delete." | ✓ |
| 12 | `rejected_finding` | Plan Section 5: "Live/weekly CI/provider/readiness/PR/release recommendations...out of scope." | ✓ |
| 13 | `rejected_finding` | Plan Section 5: no CI command/config change authorized. | ✓ |
| 14 | `rejected_finding` | Plan Section 1: ".gitignore edits not authorized." | ✓ |
| 15 | `rejected_finding` | `docs/design.md` lines 657-661: EID single-source is current policy; Eastmoney/CNINFO are deferred candidates only. AGENTS.md lines 234-244: fallback must be explicitly authorized. | ✓ |

All classifications are consistent with current AGENTS/design/control truth.

## 5. Artifact-level `historical_only` Disposition

The evidence worker disposes the audit artifact as `historical_only` (Section 6).

Rationale verification:

| Rationale element | Evidence | Supportable? |
|---|---|---|
| Predates several accepted current control checkpoints | Single deferred artifact body-read gate accepted 2026-06-12 13:28; audit disposition planning accepted 2026-06-12 13:43. Audit dated 2026-06-10. | ✓ |
| Contains useful historical reviewer opinion candidates | Audit has 10 major issues, 4 priority levels of recommendations, hard-constraint reconciliation table — substantive review content. | ✓ |
| Includes stale/superseded assertions | "No live EID proof" (absolute form) contradicted by accepted single-sample evidence. "control doc too long" partially addressed by compression. | ✓ |
| Not current source/design/control truth, release evidence, readiness proof | Audit preamble says "仅作为决策输入，不作为行动授权". Evidence worker independently enforces this. | ✓ |
| Should not be promoted, archived, deleted, moved, imported, ignored, or staged | Consistent with plan stop conditions. | ✓ |

The `historical_only` disposition is supportable. The audit body is a substantive review input with useful triage value for future gates, but its assertions require direct evidence in separately authorized gates before any implementation action.

## 6. Prevention of Audit Text Becoming Repo Fact / Source Truth / Readiness Proof

The evidence artifact has explicit statements preventing audit text from being treated as truth:

| Location | Statement |
|---|---|
| Section 1 | "its assertions are not accepted as repo facts, source truth, release evidence, readiness proof or action authorization" |
| Section 4 | "Audit-body content is not used as repo fact in this evidence." |
| Section 6 | "It is not current source truth, design truth, control truth, release evidence, readiness proof, cleanup authorization or external-state authorization." |
| Section 8 | "No audit assertion is accepted as repo fact. No cleanup, source/test/runtime/design/control/startup/README/.gitignore modification, live execution, readiness claim, release action or PR action is authorized." |

Every row in the disposition table has a `direct_evidence_required` column that specifies what would be needed to adjudicate the claim — none of which is authorized in this gate. The plan's mandatory constraint ("substantive findings cannot be accepted as repo facts unless backed by direct same-source evidence from authorized files or commands") is correctly enforced.

## 7. NOT_READY and Scope Drift Preservation

### NOT_READY

- Section 1: "**NOT_READY preserved.**"
- Section 8: "**NOT_READY preserved.**"

### EID single-source / no-fallback

- Section 4 truth-doc fact: "Current annual-report source policy remains EID single-source operational no-live implementation; Eastmoney, fund-company/CDN, CNINFO, fallback invocation and source expansion are not authorized by this gate."
- Row 15: rejected for current chain.

### Live / weekly CI / provider / readiness / PR / release / cleanup rejection

| Prohibited action | Rejected in row |
|---|---|
| Weekly CI / scheduled live smoke | Row 12: `rejected_finding` |
| Run mypy/black in CI | Row 13: `rejected_finding` |
| `.gitignore` edits | Row 14: `rejected_finding` |
| Eastmoney/fallback/source expansion | Row 15: `rejected_finding` |
| Live/provider/EID/PDF/FDR/analyze/checklist/golden/readiness/release commands | Row 16: `rejected_finding` |
| PR/release/readiness state change | Row 17: `rejected_finding` |
| Delete/move tool scripts | Row 8: `rejected_finding` |

All scope drift categories from the plan's mandatory constraints are explicitly rejected.

## 8. Disposition Table Completeness

The evidence worker's table covers:

- All 10 executive summary issues from audit §0 (rows 1-11 plus row 18 for appendix)
- All 3 CI/infrastructure recommendations from audit §8.1 (rows 12-14)
- Plan-mandated guardrail rows for prohibited categories (rows 15-17)
- Process/context observations (rows 18-19)

Total: 20 rows covering substantive claims, guardrail categories, and contextual observations. The coverage is comprehensive for the audit's major themes.

## 9. Residuals

The evidence worker's Section 7 residual table correctly routes:

| Residual | Classification | Correct? |
|---|---|---|
| Audit artifact remains untracked | `accepted_residual` | ✓ — cleanup is separate gate |
| Substantive claims not verified against source/tests | `deferred_candidate` | ✓ — requires separate authorized gates |
| Broader live/readiness proof absent | `accepted_residual` | ✓ — already in control truth |
| `基金年报/` PDFs undisposed | `accepted_residual` | ✓ — existing known residual |
| Source expansion / fallback | `rejected_finding` | ✓ — per plan mandate |
| CI/live/provider/PR/release/cleanup | `rejected_finding` | ✓ — per plan mandate |

## 10. Findings

### Blocking

None.

### Non-blocking

| # | Finding | Severity | Rationale |
|---|---|---|---|
| N1 | Rows 15 and 17 of the disposition table attribute claims to the audit body that it does not make explicitly. Row 15 ("Eastmoney/fund-company/CNINFO/fallback/source expansion should be reintroduced"): the audit documents the current EID single-source policy without recommending its reversal. Row 17 ("PR/release/readiness state should be changed"): the audit does not recommend external-state changes. | Low | These rows function as plan-mandated guardrails. The dispositions (`rejected_finding`) are correct per plan mandate regardless. No classification outcome changes. The evidence worker could improve precision by labeling these as "guardrail: ensure no implied X recommendation is accepted" rather than attributing them as direct `audit_claim` extractions. |
| N2 | Row 2's `audit_claim` "No live EID proof exists" captures the audit body's absolute statement in §0/§6.5, but the audit body §1 also acknowledges the accepted single-sample `004393 / 2021-2025` live EID evidence. The audit body is internally contradictory on this point. The evidence worker's extraction prioritizes the stronger (incorrect) claim. | Low | The disposition (`rejected_finding`) is correct because the absolute form is contradicted by current truth. The internal contradiction is a property of the audit body, not the evidence worker's extraction. |
| N3 | Structure summary (Section 3) collapses audit §5 (模板与基金分析能力审核) and §6 (测试与质量保障审核) into a single summary item "template / analysis / test / quality observations." These are two distinct audit sections totaling ~170 lines with separate finding categories. | Informational | The summary is intentionally high-level and does not claim to be exhaustive. The disposition table covers substantive findings from both sections. |

## 11. Validation

- `git status --short`: Expected untracked residue; evidence artifact is new untracked. No tracked source/test/runtime/design/control modifications.
- `git status --branch --short`: Branch `feat/mvp-llm-incomplete-run-artifacts`, ahead 167. Matches evidence worker's observation.
- `git diff --check`: Pass.

## 12. Verdict

**PASS — no blocking findings.**

The evidence artifact correctly:

- Reads exactly one authorized audit body and the 11 accepted baseline control inputs
- Summarizes audit body structure accurately without over-quoting
- Extracts major audit claims and classifies them consistently with AGENTS/design/control truth
- Applies `historical_only` disposition at artifact level with supportable rationale
- Prevents audit text from being treated as repo fact, source truth, or readiness proof
- Preserves EID single-source/no-fallback, rejects all scope drift (live/weekly CI/provider/readiness/PR/release/cleanup), and preserves NOT_READY
- Exhaustively rejects plan-prohibited categories (rows 12-17)

Three non-blocking findings: N1 (two guardrail rows attribute claims not explicitly in audit body — precautionary but imprecise), N2 (audit body internal contradiction on live EID evidence not noted), N3 (structure summary granularity — informational).
