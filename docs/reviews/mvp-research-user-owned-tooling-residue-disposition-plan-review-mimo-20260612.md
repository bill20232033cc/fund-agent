# MiMo Plan Review: Research/user-owned/tooling residue disposition planning gate

Date: 2026-06-12

Reviewer: AgentMiMo (independent plan reviewer)

Target plan: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-plan-20260612.md`

## Review Dimensions

### 1. Boundary Adequacy

**Verdict: ADEQUATE**

The plan correctly identifies and excludes already-handled residue groups:
- `docs/reviews/` untracked review artifacts — handled by review-artifact residue evidence chain
- `docs/audit/` — handled as audit input/residue by prior review/audit disposition chain
- `reports/live-evidence/` — handled by runtime/live report metadata evidence
- `reports/manual-llm-smoke/` — handled by runtime/live report metadata evidence

Eight candidate paths are correctly identified with initial category, disposition status, and required future gate. The git status cross-check confirms all candidate paths are currently untracked.

Non-goals section is tight and comprehensive. No file deletion/movement/archival/cleanup/import/promotion is authorized.

**Non-blocking observation**: The plan does not re-verify whether newly untracked files under `docs/reviews/` (visible in current git status, e.g., `mvp-research-user-owned-tooling-residue-disposition-plan-review-ds-20260612.md`) fall within the prior review-artifact evidence chain exclusion or require re-evaluation. The prior evidence checkpoint at `387d16a` classified 36 paths; current git status shows more untracked review files. This is acceptable because the prior chain's exclusion scope covers `docs/reviews/` as a path root, but the evidence gate should re-confirm the current count.

### 2. Top-level `reviews/` Ambiguity

**Verdict: ADEQUATE with minor note**

The plan correctly identifies `reviews/` (top-level, outside `docs/reviews/`) as a separate candidate path with ambiguous routing. Section 2.2 states it is "unclassified residue; not release evidence" and proposes routing to "metadata evidence gate; may be routed to review/audit follow-up instead of research/tooling acceptance."

This is an honest ambiguity acknowledgment. The plan correctly defers the routing decision rather than forcing it into the research/tooling disposition family.

**Non-blocking note**: The proposed metadata evidence gate (section 4.2) includes `find reviews -maxdepth 3 -type f -print | sort` for listing. This is appropriate for discovering the file count. However, the plan should note that if `reviews/` contains review-style artifacts, the controller may need to route them to the review/audit residue chain rather than treating them as research/tooling residue. The current plan text implies this but does not make it explicit in the decision matrix (section 6) — the top-level `reviews/` row says "DEFER to metadata evidence; likely route to review/audit residue follow-up" which is sufficient.

### 3. PDF Corpus Boundary

**Verdict: ADEQUATE**

The plan correctly identifies `基金年报/` as "user-owned PDF/document corpus" with explicit non-proof classification:
- "not repository source truth and not production access path"
- "metadata-only corpus listing gate; import/use requires separate document-repository ingestion gate"

This aligns with the AGENTS.md hard constraint that production annual-report PDF access must go through `FundDocumentRepository`. The plan correctly defers all corpus use to a separate ingestion gate.

Section 4.2 proposes `find 基金年报 -maxdepth 2 -type f -print | sort` for metadata listing only, which is appropriate and non-invasive.

### 4. Source-like Script Risk

**Verdict: ADEQUATE**

The plan correctly identifies `scripts/claude_mimo_simple.py` as "unclassified source-like/tooling residue; not runtime source" and proposes a separate "source-like tooling ownership gate" as the required future gate.

This follows the established pattern from the `fund_agent/tools/` source-like residue ownership gate. The plan correctly separates this from the mainline metadata evidence gate and defers ownership classification to a dedicated gate.

**Non-blocking observation**: The decision matrix (section 6) groups this with `docs/tmux-agent-memory-store.md` under "tooling note/script" with the same disposition. This is acceptable grouping, but the source-like script risk is qualitatively different from a tooling note — the script could potentially be invoked as code. The plan handles this correctly by specifying a separate "source-like tooling ownership gate" in the deferred entries.

### 5. Design/Template Truth-source Risk

**Verdict: ADEQUATE**

The plan correctly identifies two design/template truth-source risks:
- `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` — "research/spec residue; not design truth"
- `定性分析模板.md` — "user-owned template/research doc; not template truth"

Both are deferred to metadata evidence with explicit non-acceptance as design or template truth. The non-goals section (section 3) explicitly states no acceptance of these as "source truth, design truth, template truth, release evidence or readiness proof."

This correctly protects `docs/design.md` as the design truth source and `docs/fund-analysis-template-draft.md` as the template truth source.

### 6. Non-proof Fields

**Verdict: ADEQUATE**

Section 4.3 defines 12 required evidence fields including five mandatory non-proof flags:
- `not_source_truth=true`
- `not_design_truth=true`
- `not_template_truth=true`
- `not_release_evidence=true`
- `not_readiness_proof=true`

This matches the established pattern from prior evidence gates and provides comprehensive non-proof coverage. Each candidate path must carry all five flags, preventing any path from being accidentally promoted to truth status.

### 7. Single Next Entry

**Verdict: ADEQUATE**

Section 7 defines a single mainline next entry: `Research/user-owned/tooling residue metadata evidence gate`.

Seven deferred entries are listed with clear separation from the mainline. No ambiguity about what happens next.

**Non-blocking observation**: The deferred entries have no explicit sequencing or priority ordering. This is acceptable for a planning gate — the controller will determine ordering based on future gate results. However, it would be slightly more helpful to note which deferred entries are likely to be needed first (e.g., top-level `reviews/` routing may be needed before PDF corpus ingestion).

## Cross-check: git status alignment

Current `git status --short` confirms:
- All 8 candidate paths from section 2.2 are visible as untracked (`??`)
- All excluded paths from section 2.1 are also visible as untracked but correctly excluded
- `docs/audit/` is correctly excluded (handled by prior chain)
- `reports/live-evidence/` and `reports/manual-llm-smoke/` are correctly excluded (handled by runtime/live report evidence)

`git diff --check` passes with no output — no whitespace errors.

## Blocking Findings

None.

## Non-blocking Findings

1. **docs/reviews/ untracked count drift**: The plan does not re-verify the current untracked file count under `docs/reviews/` against the prior evidence checkpoint's 36-path classification. The evidence gate should confirm whether newly visible files fall within the existing exclusion scope.

2. **Deferred entry sequencing**: The seven deferred entries in section 7 have no explicit priority ordering. This is acceptable but would benefit from a note on likely sequencing.

3. **Top-level `reviews/` routing**: The plan correctly acknowledges ambiguity but does not explicitly state that if `reviews/` contains review-style artifacts, they should be routed to the review/audit chain rather than the research/tooling chain. The current text implies this but could be more explicit.

## Verdict

**ACCEPT**

The plan is well-bounded, correctly identifies all candidate paths and exclusions, maintains clear non-proof classification fields, protects design/template truth sources, and defines a single clear next entry. The non-blocking findings are minor and do not require plan revision — they can be addressed during the evidence gate execution.

The plan meets the `standard` gate classification requirements: it is planning-only, non-live, non-cleanup, and makes no source/test/runtime behavior changes.
