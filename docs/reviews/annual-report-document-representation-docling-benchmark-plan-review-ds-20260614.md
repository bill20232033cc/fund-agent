# Annual-report Document Representation / Docling Benchmark Plan Review (DS)

Date: 2026-06-14

Role: AgentDS (adversarial plan review)

Gate: `Annual-report Document Representation / Docling Benchmark Planning Gate`

Review target: `docs/reviews/annual-report-document-representation-docling-benchmark-plan-20260614.md`

Verdict: `PASS_WITH_FINDINGS` — 2 medium findings, 4 low findings. No blocking findings. Plan is code-generation-ready enough for Slice 0/1 no-live implementation, contingent on the two medium findings being dispositioned before any evidence gate.

Release/readiness: no change (`NOT_READY` preserved).

---

## Findings

### F1 [MEDIUM] Tier A Sample Authorization Boundary Is Insufficiently Specified

Section 4 Tier A says include `004393 / 2021-2025` "only if the later evidence gate explicitly authorizes FDR/PDF access or uses existing accepted non-body metadata."

The problem: the current accepted facts for `004393 / 2021-2025` conflate two distinct authorization scopes:

| Scope | Accepted? | Evidence |
|---|---|---|
| Source identity / availability metadata | Yes | `a4f4289`: all five years available, EID single-source, `fallback_year_count=0` |
| PDF body reading through FDR for parser benchmark | No | No gate has authorized FDR body access for parser comparison purposes |

The plan treats these as a single conditional ("FDR/PDF access or existing accepted non-body metadata"), but they are separate. The later evidence gate could mistakenly assume source-identity acceptance implies body-access authorization.

The plan should split Tier A into:
- **Tier A1**: source-identity and availability metadata (already accepted; usable for sample identity anchoring without new authorization).
- **Tier A2**: FDR body access for parser benchmark (requires separate explicit authorization in the evidence gate).

Without this split, Slice 0 (preflight and sample manifest) has an ambiguous authorization precondition.

**Recommendation**: Add to Section 4 a sub-table distinguishing source-identity authorization from body-access authorization. The minimum set recommendation should separately list which samples are eligible under A1 (metadata-only anchoring) vs A2 (body-access required).

### F2 [MEDIUM] Tier B Fund-Type Panel Has No Concrete Selection Heuristic

Section 4 Tier B says cover six fund types "when available" and "Select by exact `(fund_code, report_year, report_type=annual)` identity and source metadata through `FundDocumentRepository`."

The problem: Tier B provides no selection heuristic, priority order, or fallback rule. If a given fund type has no annual report available through FDR, does the benchmark:
- Skip that fund type entirely?
- Substitute another fund of the same type?
- Redefine the panel?

Without this, Slice 0 cannot produce a deterministic Tier B manifest. The "when available" qualifier pushes an unresolved decision into the evidence gate, where it will become a live discovery exercise rather than a pre-planned comparison.

**Recommendation**: Add a Tier B selection rule: pre-declare candidate fund codes for each type; if FDR returns `not_found`/`unavailable` for a candidate, record the gap and proceed with remaining types. The gap itself is benchmark evidence (coverage limitation), not a planning failure. Minimum: specify that Tier B must include at least one active equity fund and one bond fund, with other types as best-effort.

### F3 [LOW] Paragraph Dimension in Comparison Matrix May Overclaim

Section 6 includes a "Paragraphs" dimension comparing "raw text paragraph boundaries" against "normalized paragraph blocks with reading order and provenance."

The fail-closed signal correctly notes that paragraph segmentation could "drop disclaimers, table notes or manager discussion context." But the dimension itself may be inappropriate for a benchmark that explicitly avoids committing report body text (per artifact policy). If paragraph text cannot be committed, how is paragraph segmentation measured and reviewed?

The plan doesn't specify whether paragraph comparison uses:
- Redacted excerpts with page/section references (consistent with artifact policy)?
- Structural metrics only (paragraph count, reading-order integrity)?
- Full text that must remain untracked?

**Recommendation**: Clarify in the Paragraphs dimension whether measurement is structural-only or requires body-text samples, and how this interacts with the artifact policy's prohibition on committing raw body text.

### F4 [LOW] V3 Validation Condition Is Vague

Section 9 V3 says: "Missing optional Docling reports benchmark-unavailable without production failure."

"Benchmark-unavailable" has no concrete definition. Does it mean:
- The benchmark run skips Docling for all samples?
- A per-sample metric records `parser=docling, status=unavailable`?
- The evidence artifact reports a skipped validator?

**Recommendation**: Define `benchmark-unavailable` as a concrete per-sample metric: `parser_status=unavailable` with `unavailable_reason` and the Docling-less dimensions recorded as `skipped`. The evidence gate can then report coverage without ambiguity.

### F5 [LOW] Slice 3 Optional Import Mechanism Is Underspecified

Slice 3 says "optional import with clear `DoclingUnavailable` benchmark-only failure" but doesn't specify the mechanism. Options include:
- `try/except ImportError` at adapter construction time;
- Separate `[benchmark]` dependency group in `pyproject.toml`;
- Environment variable gate.

Each has different implications for CI, reproducibility, and accidental production dependency. The plan should recommend one approach.

**Recommendation**: Add a note that the later implementation gate should use `try/except ImportError` at adapter construction (not at module level) to avoid import-time side effects, and that Docling must not appear in default/production dependency groups.

### F6 [LOW] No Docling Version/Reproducibility Contract

The plan mentions "Record parser version/options/cache key" (Risk #5) and "Repeat runs produce identical normalized snapshots or explainable versioned diffs" (Reproducibility dimension). But there is no explicit requirement that Docling version be pinned, recorded in benchmark metadata, or compared across versions.

Without this, two evidence gates run months apart could produce different Docling output with no explanation, and the benchmark would have no way to distinguish version drift from genuine parser behavior differences.

**Recommendation**: Add to Section 6 (Reproducibility dimension) or Section 10 (Risks) an explicit requirement that both `pdfplumber` and Docling versions be recorded in benchmark metadata, and that normalized snapshots include a version field. If a future evidence gate changes Docling version, the benchmark must re-run both parsers.

---

## Cross-reference Verification

### AGENTS.md Compliance

| Rule | Status | Evidence |
|---|---|---|
| 年报解析器属于 `FundDocumentRepository` 内部实现边界 | PASS | Section 7 explicitly places candidate schema under `fund_agent/fund/documents/`; non-goals forbid Service/UI/Host direct calls |
| 文档中间层不等于事实真源 | PASS | Section 5 artifact policy: "Parser intermediate only; not fund fact truth"; Section 7: `DisclosureAnchorCandidate` "Does not replace project-owned `EvidenceAnchor`" |
| 年报来源 fallback 显式按失败分类决策 | PASS | Section 2 accepted facts table preserves `not_found`/`unavailable` as terminal, `schema_drift`/`identity_mismatch`/`integrity_error` as fail-closed; Section 6 failure taxonomy dimension requires composition with source failures |
| 禁止把显式参数放在 extra_payload 里传递 | PASS | No `extra_payload` usage proposed; all parameters are typed in candidate schema |

### design.md Compliance

| Rule | Status | Evidence |
|---|---|---|
| Docling 只能作为 benchmark/candidate | PASS | Section 3 non-goals: "Docling installation, dependency changes or production dependency declaration" not authorized; Section 7: "DoclingDisclosureParser: converts Docling output into the same candidate representation for benchmark only" |
| 基金事实须经自研 extractor 形成可审计字段 | PASS | Section 5: "fund facts still require project-owned extractor / chapter fact projection / `EvidenceAnchor`" |
| 三层状态标注 | PASS | Section 7: "This section is candidate-only. It is not current design truth" |
| UI→Service→Host→Agent 边界 | PASS | Section 7 candidate module ownership: "non-consumers: UI, Service, Host, renderer and quality gate must not directly parse or inspect parser-specific documents" |

### implementation-control.md Compliance

| Rule | Status | Evidence |
|---|---|---|
| Planning only gate | PASS | Section 3 non-goals explicitly forbid source/test/runtime changes, live commands, parser replacement |
| EID single-source/no-fallback preserved | PASS | Section 2 accepted facts; Section 3 non-goals; Section 6 failure taxonomy |
| NOT_READY preserved | PASS | Stated in header, Section 2, Section 3, Section 10 Risk #8 |
| No annual-period LLM route | PASS | Section 2: "This plan must not design an annual-period LLM route or default-on LLM analysis"; Section 3 non-goals |
| No repair-budget change | PASS | Section 2: "Benchmark planning must not change repair budget" |

### current-startup-packet.md Compliance

| Rule | Status | Evidence |
|---|---|---|
| Current mainline is Docling Benchmark Planning Gate | PASS | Plan is the target artifact for this gate |
| No live/provider/network/PDF/FDR commands | PASS | Section 3 non-goals |
| No production parser replacement | PASS | Section 3 non-goals; Docling is parallel benchmark candidate only |

### Provider/LLM Route Stabilization Closeout Compliance

| Closeout requirement | Status | Evidence |
|---|---|---|
| Plan only | PASS | Entire plan is planning artifact |
| Benchmark matrix for pdfplumber vs Docling | PASS | Section 6: 11-dimension comparison matrix |
| Future `FundDisclosureDocument`-like schema as candidate only | PASS | Section 7: explicitly candidate-only |
| Deferred entries preserved | PASS | Section 11: explicitly lists deferred gates matching closeout |

---

## Smuggled Work Audit

Checked for prohibited content; all clear:

| Prohibited category | Present? | Notes |
|---|---|---|
| Live/provider/LLM/network commands | No | Non-goals forbid; no command invocation proposed |
| PDF/FDR body access authorization | No | Conditional on future evidence gate |
| Production parser replacement | No | Explicitly rejected |
| Docling as fact truth | No | Artifact policy: "Parser intermediate only" |
| Service/UI/Host direct parser calls | No | Candidate ownership explicitly restricts consumers |
| Fallback/source expansion | No | Non-goals forbid |
| Annual-period LLM route | No | Explicitly deferred |
| Readiness/release/PR work | No | Non-goals forbid; NOT_READY preserved |
| Repair-budget change | No | Explicitly preserved |
| Source/test/runtime implementation | No | Planning only |

---

## Code-Generation-Readiness Assessment

| Component | Ready for Slice 0/1? | Gaps |
|---|---|---|
| Sample policy | Conditional on F1 resolution | Tier A authorization split; Tier B selection heuristic (F2) |
| Artifact policy | Yes | Paths, retention, truth status are concrete |
| Comparison matrix | Yes (minor F3, F6) | Paragraph dimension overclaim; version pinning missing |
| Candidate schema | Yes | Dataclass sketch + field concepts table are sufficient for Slice 1 |
| Implementation slices | Yes (minor F5) | Slice 3 import mechanism underspecified |
| Validation matrix | Yes (minor F4) | V3 condition vague |

Overall: the plan is code-generation-ready for Slice 0 (preflight and sample manifest) and Slice 1 (candidate schema types only). F1 and F2 should be dispositioned before Slice 0 proceeds. F3-F6 are nonblocking and can be addressed in the implementation gate.

---

## Recommendation

Proceed to review closeout with two medium findings requiring disposition before any evidence gate. The plan correctly preserves all hard boundaries: EID single-source/no-fallback, NOT_READY, FundDocumentRepository encapsulation, Docling-as-candidate-only, and four-layer architecture. No blocked or rejected findings.

Next step: Route this review to MiMo for independent review, then to controller judgment for final disposition of F1 and F2.
