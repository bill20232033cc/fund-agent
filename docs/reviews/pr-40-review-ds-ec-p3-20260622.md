# Deep Review: EC-P3 PR Review Gate for PR-40

- **Gate**: EC-P3 PR review gate
- **PR**: https://github.com/bill20232033cc/fund-agent/pull/40
- **Branch**: `evidence-confirm-productionization`
- **PR head**: `972b8f0730f3547ab846f51072c9fc98c12bf2cc`
- **Date**: 2026-06-22
- **Artifact path**: `docs/reviews/pr-40-review-ds-ec-p3-20260622.md`

## Scope

Review EC-P1A + EC-P2 + EC-P3 code changes on PR-40 for correctness, design contract adherence, non-goal boundary enforcement, deterministic V2 authority, fail-closed semantics, PR body truthfulness, and residual risk classification.

## Checked Evidence

### PR Metadata

| Field | Observed |
|---|---|
| State | OPEN, draft |
| Base branch | `evidence-confirm-anchor-audit-score` |
| Head branch | `evidence-confirm-productionization` |
| Files changed | 76 (+10177 / -13) |
| CI test workflow | SUCCESS (completed 2026-06-22T09:42:15Z) |
| Reviews | none |
| Labels | none |
| Merge state | not checked (draft PR, non-goal) |

### Test Verification

| Command | PR claim | Observed |
|---|---|---|
| `pytest test_evidence_confirm.py test_evidence_confirm_semantic.py -q` | 60 passed | 60 passed |
| `pytest test_evidence_confirm.py test_evidence_confirm_sources.py -q` | 86 passed | 86 passed |
| `ruff check evidence_confirm_semantic.py test_evidence_confirm_semantic.py` | passed | passed |
| `ruff check evidence_confirm_sources.py test_evidence_confirm_sources.py` | — | passed |
| `git diff --check` (semantic files + READMEs) | passed | passed |

### Design Contract Verification

| Contract | Source | Status |
|---|---|---|
| EC-P3 is no-live Fund-layer semantic companion | `evidence_confirm_semantic.py:1-8` module docstring | matched |
| `EvidenceEntailmentClient` is injected Protocol | `evidence_confirm_semantic.py:99-113` | matched |
| `confirm_semantic_entailment()` consumes V2 result + explicit references + explicit claims + injected client | `evidence_confirm_semantic.py:160-199` | matched |
| Deterministic V2 is authoritative gate | `evidence_confirm_semantic.py:224-232` (`_confirm_single_claim` gate check) | matched |
| Semantic output cannot override V2 failures | `evidence_confirm_semantic.py:224-232` (returns `deterministic_gate_failed`) | matched |
| `missing_bounded_excerpt` blocks without client call | `evidence_confirm_semantic.py:249-258` | matched |
| Client exception fail-closed without detail leak | `evidence_confirm_semantic.py:262-270` (generic message) | matched |
| Malformed client result fail-closed | `evidence_confirm_semantic.py:272-280` + `_judgment_is_valid()` | matched |
| Severity: contradicted→block, insufficient→warn, not_applicable→info, entailed→info (warn under V2 warn) | `evidence_confirm_semantic.py:434-459` | matched |
| Overall: contradict/block→fail, insufficient/warn→warn, entailed→pass, else not_applicable | `evidence_confirm_semantic.py:500-521` | matched |
| Design.md §Evidence Confirm semantic wording matches implementation | `docs/design.md:226-234` vs code | matched |
| Design.md §Evidence Confirm sources wording matches implementation | `docs/design.md:236-245` vs code | matched |

### Non-goal Boundary Verification

| Boundary | Code evidence | Status |
|---|---|---|
| No Service imports | ast import analysis test `test_semantic_module_import_isolated_from_service_provider_host_renderer_quality_gate` | enforced |
| No Host imports | same ast test | enforced |
| No UI imports | same ast test | enforced |
| No renderer/quality-gate imports | same ast test | enforced |
| No provider/LLM client construction | `EvidenceEntailmentClient` is Protocol, test uses `_FakeEntailmentClient` | enforced |
| No `FundDocumentRepository` instantiation in materializer | `evidence_confirm_sources.py` module docstring + no repository import in `build_annual_report_evidence_confirm_references()` | enforced |
| No PDF/cache/source helper in semantic module | module only imports from `fund_agent.fund.evidence_confirm` + stdlib | enforced |
| Live sample hard-limited to 004393/2025 | `scripts/evidence_confirm_ec_p2_live_sample.py:34-35` constants, `_main_async()` rejects non-matching | enforced |
| Live sample emits safe scalar JSON only | `_safe_result_payload()` no excerpt/PDF path/URL | enforced |
| `field_correctness_proven=false` in live sample | `scripts/evidence_confirm_ec_p2_live_sample.py:210` hardcoded | enforced |

### PR Body Truthfulness

| PR claim | Verified |
|---|---|
| EC-P1A: no-live Fund-layer annual-report reference materializer | yes — `build_annual_report_evidence_confirm_references()` |
| EC-P2: repository-bounded runner | yes — `run_repository_bounded_evidence_confirm()` |
| EC-P3: no-live semantic entailment companion contract | yes — `confirm_semantic_entailment()` |
| Deterministic V2 remains authoritative | yes — `_deterministic_gate_blocks()` enforces 3 prereq dimensions + value_match |
| Warning disposition: section-only smoke → strict fail, V2 warn, pathway pass | yes — `_repository_pathway_status()` code matches |
| Non-goal: no provider-backed semantic quality | yes — `EvidenceEntailmentClient` is Protocol, no provider construction |
| Non-goal: no Service/UI/renderer/quality-gate production integration | yes — no imports, no integration code |
| Non-goal: no `EvidenceSourceKind` / `EvidenceAnchor` expansion | yes — no changes to public anchor/source kind types |
| Non-goal: no source fallback behavior change | yes — no changes to source policy |
| Non-goal: no readiness/release promotion | yes — `NOT_READY` preserved in control docs |
| PR remains draft | yes — state is OPEN, draft |

## Findings

**No substantive issues found.**

The EC-P3 semantic entailment implementation is correct, well-tested (13 focused unit tests + import isolation test), and faithfully implements the design contract. Deterministic V2 authority is properly enforced: `source_support`, `missing_evidence`, `proof_boundary` non-pass or `value_match` fail all block semantic client invocation. Fail-closed behavior is comprehensive: client exceptions, malformed results, missing bounded excerpts, and empty claims all produce safe, non-leaking results.

EC-P1A materializer and EC-P2 repository runner are correctly implemented with proper admission checks, failure classification, and pathway status separation from strict V2 status.

The live sample script is properly constrained: hard-limited to `004393/2025`, emits only safe scalar JSON, and explicitly sets `field_correctness_proven=false`.

Non-goal boundaries are respected: no cross-layer imports (verified by ast-based test and manual review), no provider construction, no Service/UI/renderer/quality-gate integration.

PR body claims are truthful. All accepted evidence reproduces.

## Residual Risks

| Risk | Classification | Owner |
|---|---|---|
| Provider-backed semantic quality is unproven | accepted residual | later controlled semantic provider evidence gate |
| Service/renderer claim extraction not implemented | accepted residual | later integration gate |
| Quality-gate consumption not implemented | accepted residual | later integration gate |
| Same-run V2 result/reference binding uses anchor ids (not excerpt hashes) | accepted residual | later integration gate |
| Release/readiness remains `NOT_READY` | accepted residual | later release/readiness gate |
| Section-only smoke `pathway_status="pass"` may be misinterpreted as V2 pass | mitigation in place | `field_correctness_proven=false` and explicit `pathway_warning_reasons` prevent overclaim |

No unclassified residual risk.

## CI/PR State Observed

- CI test workflow: SUCCESS (completed)
- PR state: OPEN, draft
- No reviews, no labels
- Control docs (`implementation-control.md`, `current-startup-packet.md`) correctly reflect EC-P3 as current active gate with `NOT_READY`

## Conclusion

**PASS.** No actionable findings. The EC-P3 semantic entailment contract, EC-P2 repository runner, and EC-P1A materializer are correctly implemented against their design contracts. Deterministic V2 authority is maintained. Non-goal boundaries are enforced. PR body is truthful. CI is green. All residual risks are classified and owned.
