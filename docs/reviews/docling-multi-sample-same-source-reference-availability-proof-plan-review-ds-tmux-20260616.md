# Docling Multi-sample Same-source Reference Availability Proof Plan Review (DS) - 2026-06-16

Gate: `Docling Multi-sample Same-source Reference Availability Proof Gate`
Role: AgentDS plan review worker
Release/readiness: `NOT_READY`

## Scope

Review the plan artifact `docs/reviews/docling-multi-sample-same-source-reference-availability-proof-plan-20260616.md` against:

- `AGENTS.md` execution constraints
- `docs/current-startup-packet.md` current gate scope and boundary
- `docs/implementation-control.md` current control truth
- Prior controller judgment `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-controller-judgment-20260616.md`
- Prior evidence `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md`
- `fund_agent/fund/documents/repository.py` actual `load_annual_report()` implementation

Review focus:

1. Same-source reference availability proof semantics
2. Whether candidate JSON / pdfplumber output / Docling output / untracked residue / cache internals / direct PDF path are incorrectly treated as reference proof
3. Whether Route B `FundDocumentRepository(force_refresh=False)` is safely bounded
4. Whether stop conditions are sufficient
5. Whether `NOT_READY`, no source truth, no full correctness, no parser replacement are preserved

This review does not modify source, tests, runtime, control, or design. It does not run live/network/EID/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge.

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Execution constraint truth source |
| `docs/current-startup-packet.md` | Current gate scope, boundary, and accepted facts |
| `docs/implementation-control.md` §Current Gate, §Non-goal Reminder | Current control truth and non-goal constraints |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-controller-judgment-20260616.md` | Prior controller judgment; accepted blocked evidence fact for S4/S5/S6 |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md` | Prior evidence; S4/S5/S6 candidate JSON availability, reference unavailability, blocked claims |
| `fund_agent/fund/documents/repository.py` | Actual `load_annual_report()` implementation for Route B safety analysis |

## Findings

### F1: Same-source reference proof semantics are correctly defined (PASS)

The plan defines "same-source reference proof" as proof that the same annual-report PDF was acquired through the accepted EID single-source/no-fallback policy. This aligns with:

- `AGENTS.md`: "生产年报 PDF 访问必须经过 `FundDocumentRepository`" and the fallback policy table (only `not_found`/`unavailable` allow fallback)
- `docs/current-startup-packet.md` §2: "EID single-source annual-report access is current operational source policy"
- Prior controller judgment: the blocker fact that "no accepted no-live same-source reference artifact or no-live repository metadata proof was established" for S4/S5/S6

The plan's two-route structure (Route A: accepted reference artifact; Route B: bounded FDR parsed-cache metadata proof) correctly maps to the two proof categories identified in the prior controller judgment.

### F2: Candidate JSON / pdfplumber / Docling output correctly excluded as reference proof (PASS)

The plan explicitly rules out each prohibited input as reference proof:

- **Candidate JSON**: Route A step 5 — "If only Docling/pdfplumber candidate JSON exists, status is `blocked_candidate_only`, not available"
- **pdfplumber output**: Same as candidate JSON; covered by the same exclusion
- **Docling output**: Section 5 Route A step 2 — eligible artifact must evidence "reference availability for the same annual-report source, not a Docling/pdfplumber candidate output alone"
- **Untracked residue**: Section 6 — "unaccepted untracked residue as proof" is explicitly forbidden
- **Cache internals**: Section 6 — "cache internals or direct cache database/file inspection" explicitly forbidden
- **Direct PDF path**: Section 6 — "direct PDF paths, direct PDF file metadata as source proof, or PDF body read" explicitly forbidden

This is correctly aligned with the prior controller judgment's accepted fact: "Existing candidate JSONs are not source truth and are not field-correctness proof."

### F3: Route A artifact search scope is appropriately constrained (PASS)

Route A §5 step 1 limits search to "accepted artifacts already inside the reviewed evidence chain" with static candidate locations `reports/representation-json/` and `docs/reviews/`. The plan correctly requires an eligible artifact to bind all identity fields (`fund_code`, `document_year`, `report_type=annual_report`, same-source identity). If body lacks any identity field, status is `blocked_identity_unproven`. This prevents accepting a loosely related artifact as reference proof.

The prior controller judgment confirms that for S4/S5/S6, "no accepted no-live same-source reference artifact or no-live repository metadata proof was established." Route A should therefore yield `blocked_no_accepted_artifact` for all three samples under current evidence. This is the expected and correct outcome.

### F4: Route B repository semantics analysis is accurate (PASS)

The plan's analysis of `FundDocumentRepository.load_annual_report(force_refresh=False)` in Section 5 correctly traces the code path from `repository.py`:

1. Parsed cache lookup (`load_parsed_report`) → if hit with EID single-source metadata, return immediately (SAFE)
2. PDF cache entry lookup (`get_pdf_entry`) → if hit with valid metadata, use cached pdf_path (LOCAL, but accesses cache internals)
3. PDF acquisition (`fetch_pdf` / `fetch_pdf_path`) → network/EID acquisition (UNSAFE, requires authorization)
4. PDF parsing (`parse_pdf`) → local parsing of acquired PDF (UNSAFE in this gate context)

The plan correctly concludes: "`FundDocumentRepository(force_refresh=False)` is not inherently a no-live/static proof route. It is bounded only when the evidence worker can prove the call will stop at an already accepted parsed-report cache hit without triggering PDF acquisition or PDF parsing."

### F5: Route B pre-execution proof circularity not explicitly acknowledged (REQUIRED AMENDMENT)

The plan requires Route B to stop before execution if "the planned call would need PDF cache lookup." However, `load_annual_report(force_refresh=False)` always performs a PDF cache lookup (`get_pdf_entry`) when the parsed cache misses. The evidence worker cannot prove the parsed cache will hit without either:

- Inspecting cache internals (forbidden by Section 6)
- Actually executing `load_annual_report()` and observing whether it proceeds to PDF cache lookup or acquisition (which is the risky action the plan aims to prevent)

This creates a circular dependency: you cannot prove Route B is safe without either violating the cache-internals prohibition or executing the risky path. The plan should explicitly acknowledge this circularity and recommend one of:

- (a) A separate "Cache Metadata Contract Gate" that authorizes read-only, metadata-only `cache.load_parsed_report()` inspection before any FDR call
- (b) An explicit "Route B preflight" step that authorizes a single `cache.load_parsed_report(document_key)` call with the binding constraint that only `metadata.source` envelope fields may be recorded and no parsed report body may be inspected

Without this amendment, Route B is effectively inexecutable under the current plan constraints, and the evidence worker will correctly produce `blocked_repository_route_requires_authorization` for all samples. While this is fail-safe, the plan should make this outcome explicit rather than implying Route B may be attempted.

### F6: No explicit prohibition on parsed report body inspection in Route B cache-hit path (REQUIRED AMENDMENT)

Section 5 Route B allowed outcome states "no PDF path, PDF body, cache internals, parser output body, or live/source helper output is included." This prohibits including body content in the evidence artifact, but does not explicitly prohibit the evidence worker from inspecting, serializing, diffing, or comparing the parsed report body during evidence collection.

If Route B hits the parsed cache, `load_annual_report()` returns a full `ParsedAnnualReport` with complete parsed report body. The plan should add an explicit constraint: the evidence worker must only access and record `metadata.source` envelope fields; it must not inspect, serialize, diff, or compare the parsed report body content for any purpose. This closes the gap between "not included in artifact" and "not accessed during evidence collection."

### F7: Stop conditions are comprehensive and sufficient (PASS)

Section 10 stop conditions cover all prohibited actions enumerated in Section 6 and the review focus area #4:

- Route A fails → stop with blocked status
- Candidate JSON only → stop
- Identity unproven → stop
- Route B not authorized → stop
- FDR would exceed parsed-cache metadata → stop
- Any prohibited route/command implied → stop
- Any source truth/full correctness/parser replacement/readiness implication → stop

These conditions are correctly gated before execution (not after), preventing the evidence worker from entering a risky path and then attempting to remediate.

### F8: NOT_READY, no source truth, no full correctness, no parser replacement are preserved (PASS)

The plan preserves all required constraints:

- All four allowed verdicts carry `NOT_READY` suffix
- Section 2 out of scope explicitly excludes source-truth claim, full correctness claim, production parser replacement, readiness/release claim
- Section 7 per-sample residual field requires "Must preserve not source truth, not field correctness, not full correctness, not parser replacement, not readiness"
- Section 7 aggregate field requires `release_readiness=NOT_READY`
- Section 10 final stop condition: "Any evidence would imply source truth, full field correctness, production parser replacement, or readiness"

The plan additionally aligns with the current gate scope from `docs/current-startup-packet.md` §2: "Do not promote Docling baseline, replace the production parser, change `FundDocumentRepository`, change source policy, claim source truth/full field correctness/readiness."

### F9: Evidence worker procedure order is correct (PASS)

Section 8 correctly sequences: preflight → Route A first → if all samples proven, write evidence → if Route A fails, do NOT attempt FDR by default → only if explicitly authorized, attempt bounded Route B → stop before any unsafe path. This preserves the "Route A before Route B" requirement and the default-no-FDR safety posture.

### F10: Validation commands are appropriately constrained (PASS, with observation)

Section 9 allows only status/metadata commands. The `shasum -a 256 <accepted-reference-artifact-paths-only>` command is only applicable when Route A discovers at least one accepted reference artifact. When all samples are blocked via Route A, this command has no valid target. The plan would benefit from noting this conditional applicability, but the constraint is self-evident from the command description (minor, not a required amendment).

### F11: Plan does not authorize any prohibited gate action (PASS)

The plan's Section 2 out-of-scope list, Section 6 forbidden routes, Section 8 evidence worker procedure, Section 9 validation commands, and Section 10 stop conditions collectively ensure that no Docling conversion, pdfplumber export, PDF body read, source helper call, cache internals access, live/network/EID/PDF acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge, or source/test/runtime/control/design change is authorized.

### F12: Plan input list references correct prior artifacts (PASS)

Section 3 correctly references the prior controller judgment and evidence artifacts, and the `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` machine-readable evidence. The accepted facts in Section 3 accurately summarize the prior controller judgment's accepted evidence facts.

## Required Amendments

### A1: Acknowledge Route B pre-execution proof circularity (mandatory, pre-evidence)

Add to Section 5 (Route B) or Section 8 (Evidence Worker Procedure) an explicit statement that:

> The evidence worker cannot prove a parsed-cache hit will occur without either inspecting cache internals (forbidden by §6) or executing `load_annual_report()` (which may trigger PDF cache lookup/acquisition). Under current plan constraints, Route B is inexecutable unless a prior gate has already established parsed-cache metadata proof for the exact `(fund_code, document_year)` identity. If no such prior proof exists, Route B must stop with `blocked_repository_route_requires_authorization` and recommend a separate Cache Metadata Contract Gate that authorizes read-only, metadata-only `cache.load_parsed_report()` inspection.

**Why**: Without this amendment, the plan implies Route B may be attempted when in reality the constraints make it inexecutable without violating the cache-internals prohibition or risking live acquisition. The evidence worker needs explicit guidance on this circularity.

### A2: Add explicit parsed report body non-inspection constraint for Route B (mandatory, pre-evidence)

Add to Section 5 Route B allowed outcome or to a new constraint paragraph:

> If Route B hits the parsed cache, the evidence worker must only access and record `metadata.source` envelope fields. The evidence worker must not inspect, serialize, diff, compare, or otherwise use the parsed report body content for any purpose including correctness verification, fact extraction, or field comparison.

**Why**: Section 5 currently prohibits including body content in the evidence artifact but does not explicitly prohibit accessing it during evidence collection. This closes the gap and prevents the evidence worker from performing de-facto correctness review under the guise of reference availability proof.

### A3: Mark Section 9 shasum command as conditionally applicable (recommended, not blocking)

Add a note to Section 9 that the `shasum -a 256 <accepted-reference-artifact-paths-only>` command only applies when Route A discovers at least one accepted reference artifact. When all samples are blocked, this command has no valid target and should be recorded as not applicable rather than attempted with an empty or invalid path.

**Why**: Minor clarity improvement. Does not affect safety or correctness; the command description is self-documenting. Non-blocking.

## Deferred Risks

| Risk | Why deferred | Mitigation in current plan |
|---|---|---|
| Route B may never be executable without a separate cache-metadata authorization gate | Resolving this requires a new gate boundary beyond plan review scope | Plan already defaults to no-FDR; blocked status is fail-safe |
| S4/S5/S6 may never have accepted same-source reference artifacts in the evidence chain | Depends on prior acquisition history, not a plan defect | Route A correctly yields `blocked_no_accepted_artifact` |
| Parsed cache state for S4/S5/S6 is unknown without cache inspection | Cache inspection is correctly forbidden in this gate | A1 addresses this explicitly |

## Verdict

```text
VERDICT: PASS_WITH_REQUIRED_AMENDMENTS_NOT_READY
```

The plan correctly defines same-source reference availability proof semantics, correctly excludes candidate JSON/pdfplumber/Docling output/untracked residue/cache internals/direct PDF paths as reference proof, accurately analyzes `FundDocumentRepository(force_refresh=False)` safety bounds, provides comprehensive stop conditions, and preserves `NOT_READY`/no source truth/no full correctness/no parser replacement.

Required amendments A1 and A2 must be applied before the evidence gate proceeds. A1 resolves the Route B pre-execution proof circularity. A2 closes the parsed report body inspection gap. A3 is recommended but non-blocking.

After amendments are applied, the evidence gate should proceed under the plan's own constraints: Route A first, no FDR by default, Route B only with explicit controller/user authorization, stop before any unsafe path.

### Amendment Application Self-Check

If the plan author applies A1 and A2 to the plan artifact and records the amendment application (e.g., in an amendment application note or updated plan version), the plan advances to `PLAN_READY_FOR_EVIDENCE_GATE_NOT_READY` without requiring a new plan review cycle. A3 is non-blocking and can be applied or deferred at the plan author's discretion.

If A1 or A2 is rejected, the plan should not proceed to evidence gate and requires a revised plan.
