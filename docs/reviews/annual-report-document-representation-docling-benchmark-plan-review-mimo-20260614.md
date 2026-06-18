# Annual-report Document Representation / Docling Benchmark Plan Review — MiMo

Date: 2026-06-14

Reviewer: AgentMiMo

Role: Plan review (adversarial lens)

Gate: `Annual-report Document Representation / Docling Benchmark Planning Gate`

Review target: `docs/reviews/annual-report-document-representation-docling-benchmark-plan-20260614.md`

## 1. Verdict

**PASS_WITH_NONBLOCKING_RESIDUALS**

The plan is accepted. It preserves all hard boundaries, is code-generation-ready enough for the next evidence/implementation gates, and correctly positions Docling as a bounded benchmark candidate rather than production parser or fact truth.

No blocking findings.

## 2. Review Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/provider-llm-route-stabilization-closeout-controller-judgment-20260614.md`
- Review target plan

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands were run for this review.

## 3. Findings

### 3.1 Hard Boundary Compliance

| Boundary | Status | Evidence |
|---|---|---|
| EID single-source / no-fallback preserved | PASS | Plan §2 explicitly lists `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false` as accepted current facts with planning consequences. §4 sample policy requires source identity through `FundDocumentRepository`. §9 V8 requires failure taxonomy to compose with EID source failures. |
| `NOT_READY` preserved | PASS | Plan §2 accepts `NOT_READY` from control truth. §10 risk table explicitly lists "benchmark is mistaken for readiness" with mitigation "preserve `NOT_READY`; require separate readiness/release gate." |
| Docling bounded as benchmark candidate only | PASS | Plan §3 non-goals reject "production parser replacement" and "Docling Markdown/HTML/JSON/raw output as fund fact truth." §7 candidate schema is explicitly "candidate-only" and "not current design truth." §8 Slice 3 requires "later gate explicitly authorizes dependency strategy." |
| No Service/UI/Host/renderer/quality-gate direct parser dependency | PASS | Plan §3 non-goals reject "direct Service/UI/Host/renderer/quality-gate calls to pdfplumber, Docling, parser cache, PDF cache, source helpers or download helpers." §7 candidate schema places ownership under `fund_agent/fund/documents/` with non-consumer list. |
| No live/PDF/network/provider/LLM/readiness/release/PR work smuggled in | PASS | Plan §3 non-goals reject all of these explicitly. §8 implementation slices are all future-gated. Slice 5 requires "later evidence gate" with explicit authorization. |
| No source/test/runtime behavior changes | PASS | Plan §3 non-goals list "source, test, runtime, README, design doc, control doc or startup packet changes." |

### 3.2 Findings Ordered by Severity

**F1 [informational] — Sample manifest Tier A wording could be tighter**

Plan §4 Tier A says "Include `004393 / 2021-2025` only if the later evidence gate explicitly authorizes FDR/PDF access or uses existing accepted non-body metadata." The "or" clause ("uses existing accepted non-body metadata") is slightly ambiguous — it could be read as permitting Tier A inclusion without FDR/PDF authorization if only metadata is used. The intent is likely correct (metadata-only benchmarking is acceptable without PDF access), but the later evidence gate should still explicitly declare which samples use body access vs metadata-only. This is nonblocking because §4 already requires the later gate to "predeclare" this.

**F2 [informational] — Candidate schema §7 does not explicitly declare `DisclosureBlock` text retention policy**

§7 `DisclosureBlock` says "Full body text may be excluded from committed fixtures" which is correct, but §5 artifact policy already covers this ("Raw body text and full extracted report bodies should not be committed"). The two sections are consistent but the candidate schema field description could cross-reference the artifact policy for clarity. Nonblocking because the artifact policy is authoritative.

**F3 [informational] — Comparison matrix §6 paragraph dimension is weaker than others**

The "Paragraphs" row in §6 has acceptance signal "Paragraph blocks reduce same-field ambiguity and preserve context" and fail-closed signal "Paragraph segmentation drops disclaimers, table notes or manager discussion context." This is reasonable but less operationally precise than the table-block or section-hierarchy rows. The later evidence gate should define concrete paragraph-level test cases (e.g., manager discussion §4 paragraphs vs disclaimer §12 paragraphs). Nonblocking because the matrix is a planning framework, not an evidence contract.

**F4 [informational] — Risk table §10 "local 基金年报/ corpus" residual**

§10 correctly identifies the risk that "local `基金年报/` corpus is treated as truth" and assigns owner "controller/evidence owner." This is consistent with `docs/implementation-control.md` data artifact disposition evidence (`cc842d7`) which accepted `基金年报/` as `user-owned/data artifact candidate` with `leave-untracked`. The plan correctly does not authorize using local corpus as benchmark truth. Nonblocking.

**F5 [informational] — Implementation slices §8 do not specify test coverage targets**

The plan defines 7 slices with expected assertions but does not state whether each slice should meet the project-wide `--cov-fail-under=50` floor or the per-file ≥80% review target. The later implementation gate should clarify this. Nonblocking because `AGENTS.md` §5 already sets the project-wide policy and the later gate can apply it.

### 3.4 EID Single-source / No-fallback / NOT_READY Verification

All three invariants are preserved throughout the plan:

- §2 Accepted Current Facts table explicitly maps EID source policy, terminal failures, fail-closed categories and `NOT_READY` to planning consequences.
- §4 Sample Policy requires source identity proof through `FundDocumentRepository` and does not authorize fallback.
- §6 Comparison Matrix Failure Taxonomy row requires "New taxonomy composes with current EID source failures and extractor fail-closed semantics" and "Parser failures are reported as source not-found/unavailable, fallback eligibility or silent success" as a fail-closed signal.
- §7 Candidate Schema `DisclosureSourceIdentity` requires "Must preserve EID single-source/no-fallback."
- §7 Candidate Schema `DisclosureParseIssue` requires "Must not collapse into source fallback policy."
- §9 Validation Matrix V8 requires "Parser failures map to parse issues and compose with EID source failure taxonomy" and "Does not authorize fallback."
- §10 Risks explicitly list source/parser failure conflation as a risk with mitigation.

### 3.5 Docling Bounded Benchmark Candidate Verification

Docling is correctly positioned throughout:

- §1 motivation: "not that Docling is currently required for OCR or should replace the production parser."
- §3 non-goals: "production parser replacement" and "Docling installation, dependency changes or production dependency declaration" rejected.
- §7 candidate adapters: `DoclingDisclosureParser` is "for benchmark only."
- §8 Slice 3: "only if a later gate explicitly authorizes dependency strategy" with "optional import with clear `DoclingUnavailable` benchmark-only failure."
- §9 V3: "Missing optional Docling reports benchmark-unavailable without production failure."

### 3.6 No Smuggled Work Verification

The plan does not smuggle in any unauthorized work:

- No live/provider/LLM/network/PDF/FDR commands (§3 non-goals).
- No source/test/runtime changes (§3 non-goals).
- No readiness/release/PR changes (§3 non-goals, §10 risks).
- No fallback/source expansion (§3 non-goals).
- No annual-period LLM route (§3 non-goals).
- No repair-budget calibration (§3 non-goals).

### 3.7 Code-generation-readiness Verification

The plan is sufficiently code-generation-ready for the next gates:

- **Sample policy** (§4): defines 4 tiers with inclusion/exclusion policies, minimum benchmark set, and predeclaration requirements. Sufficient for Slice 0 manifest creation.
- **Artifact policy** (§5): defines 5 artifact classes with path, retention and truth status. Sufficient for artifact routing decisions.
- **Comparison matrix** (§6): defines 11 dimensions with current-pipeline observation, Docling observation, acceptance signal and fail-closed signal. Sufficient for Slice 4 comparator design.
- **Candidate schema** (§7): defines 10 concepts with required contents and boundaries, plus 3 adapter sketches. Sufficient for Slice 1 dataclass implementation.
- **Implementation slices** (§8): defines 7 slices with goals, allowed changes, expected files, expected assertions and stop conditions. Sufficient for gate-by-gate implementation planning.
- **Validation matrix** (§9): defines 13 validations with scope, command class, expected pass condition and must-not-prove constraints. Sufficient for evidence gate design.

## 4. Residual Risks (Nonblocking)

| Residual | Impact | Mitigation |
|---|---|---|
| Sample manifest Tier A body-vs-metadata boundary needs later-gate tightening | Could cause ambiguity in benchmark scope | Later Slice 0 gate must predeclare which Tier A samples use body access vs metadata-only |
| Paragraph dimension in comparison matrix needs concrete test cases | Could produce vague paragraph-level benchmark results | Later evidence gate should define paragraph test cases for §4 manager discussion vs §12 disclaimers |
| Test coverage targets not specified per slice | Could lead to inconsistent coverage expectations | Later implementation gate should apply project-wide `--cov-fail-under=50` floor and per-file ≥80% target |

## 5. Disposition

| Item | Decision | Rationale |
|---|---|---|
| Plan artifact | ACCEPT | Preserves all hard boundaries, is code-generation-ready, correctly positions Docling as benchmark candidate |
| EID single-source/no-fallback | VERIFIED | Explicitly preserved in §2, §4, §6, §7, §9, §10 |
| NOT_READY | VERIFIED | Explicitly preserved in §2, §10 |
| Docling bounded as benchmark | VERIFIED | Explicitly preserved in §1, §3, §7, §8, §9 |
| No smuggled work | VERIFIED | All unauthorized work explicitly rejected in §3 non-goals |
| Code-generation readiness | VERIFIED | Sample policy, artifact policy, comparison matrix, candidate schema, slices and validation matrix are sufficient for next gates |

## 6. Next Gate Recommendation

Proceed to:

```text
Annual-report Document Representation / Docling Benchmark Sample Manifest And Candidate Schema No-live Implementation Gate
```

Starting with Slice 0 and Slice 1 only, as the plan recommends. The plan review residuals (F1-F5) are informational and should be dispositioned in the next gate's plan or controller judgment.
