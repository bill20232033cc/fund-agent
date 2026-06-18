# Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Plan — DS Adversarial Review

Date: 2026-06-14

Role: AgentDS plan reviewer. Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Planning Gate`.

Artifact under review: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-20260614.md`

## 1. Review Scope

This review checks whether the plan is safe, code-generation-ready, and correctly scoped for the next no-live root-cause evidence gate. It applies all checks listed in the planreview invocation and reports findings before verdict.

Evidence reviewed for this review:
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-20260614.md` (the plan artifact)
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` (accepted live evidence controller judgment)
- Safe metadata from `summary.json` and `chapters/chapter-02.json` via `jq`

Commands executed: `git status --short`, `git diff --check`, `jq` selections only.

No forbidden bodies were read. No live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands were executed.

## 2. Findings

### F1. CRITICAL — Unauthorized read artifacts listed in Section 2

Section 2 ("Evidence Reviewed") lists three artifacts not authorized by this gate's allowed reads:

- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-mimo-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md`

The gate's allowed reads include only the controller judgment (`docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`), not the DS review, MiMo review, or evidence artifact from that chain.

The DS review artifact in particular almost certainly contains DS observations about `writer_deleted_item_rule_ids` and repair evidence-usage regression — the very observations the plan itself says must be treated as hypotheses, not accepted root cause (Section 4). Reading that artifact before hypothesis formation creates a taint risk: the plan's H1-H5 may have been shaped by observations the evidence worker should not see until after independent no-live root cause classification.

**Required amendment**: Remove these three artifacts from Section 2. Restrict evidence reviewed to the explicitly allowed controller judgment, safe metadata, template, code excerpts and test surface identification only. Add an explicit prohibition in Section 6 against reading these three artifacts.

### F2. MODERATE — Ambiguous "Out of scope" phrasing for DS observation prohibition

Section 1 states as out of scope:

> Treating DS observations about `writer_deleted_item_rule_ids` or repair evidence usage as accepted root cause before direct no-live evidence.

The phrase "Out of scope" followed by what is actually a prohibition creates a reading ambiguity: a worker could interpret this as "the prohibition against treating DS observations as root cause is out of scope" (i.e., the prohibition doesn't apply), rather than the intended "treating DS observations as root cause is forbidden."

The intent is clear from Section 4 (all five hypotheses marked "unproven") and Section 7 criteria (requires direct no-live evidence for acceptance). But a literal reading of Section 1 would permit what the rest of the plan forbids.

**Required amendment**: Rephrase as an explicit active prohibition. Example: "The evidence worker must not treat DS observations about `writer_deleted_item_rule_ids` or repair evidence usage as accepted root cause before direct no-live evidence proves them."

### F3. MODERATE — Test `-k` selectors assume infrastructure that may not exist

E3 through E7 each contain `uv run pytest ... -k "selector"` commands with specific marker/keyword patterns:

- E3: `-k "required_output_block or l1_numerical_closure or tracking_error"`
- E4: `-k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework"`
- E5: `-k "repair_budget_exhausted"` / `-k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted"`
- E6: `-k "chapter_2 or tracking_error"` / `-k "required_output_block"`
- E7: `-k "l1 or repair_budget_exhausted or writer_used"` / `-k "l1_prompt_contract_serialization"`

If the existing test suite lacks tests matching these selectors, pytest returns exit code 5 ("no tests collected") or 0 with "0 selected." Either outcome is ambiguous: the worker cannot distinguish "no relevant tests exist" from "tests exist but match nothing relevant." This creates a scope-drift risk: a worker seeing "no tests collected" may be tempted to write new tests to satisfy the plan, potentially crossing into implementation territory without explicit evidence-gate authorization.

The plan's "If adding tests is authorized" language is conditional and properly gated. However, the unconditional `uv run pytest` commands presuppose existing test coverage that may not be present. If `required_output_block` tests don't exist, running `-k "required_output_block"` produces a misleading signal.

**Recommended amendment** (non-blocking if F1 is fixed): Add a pre-check step: list available test function names with `uv run pytest --collect-only -q` for each test file before running `-k` selectors. If no tests match, record "no matching existing tests" as evidence rather than treating empty output as a pass.

### F4. LOW — Section 2 lists `docs/design.md` without gate-level explicit authorization

Section 2 lists `docs/design.md relevant Route C / CHAPTER_CONTRACT / L1 / repair-budget sections` as evidence reviewed. The gate's allowed reads list does not explicitly name `docs/design.md`. However, `AGENTS.md` designates `docs/design.md` as a mandatory read (second in priority list), and `docs/implementation-control.md` references it as design truth source. Reading relevant design.md sections for contract-to-rule comparison (E2) is within the spirit of the gate's analysis scope. This is noted as a process observation, not a blocker.

### F5. LOW — E2 code read scope is stated but not enforced

E2 says to read `_audit_numerical_closure()` and `_audit_item_rule_deleted_sections()` "only." The plan relies on worker discipline to not read surrounding code. While the scope is correctly stated, there is no mechanical enforcement. This is inherent to markdown-based gate artifacts and not a defect of this plan specifically.

### F6. PASS — NOT_READY and EID single-source/no-fallback preserved

The plan consistently:
- States `NOT_READY` in Section 1, Section 7, and Section 8
- Preserves EID single-source/no-fallback in Section 1 and Section 8
- Forbids release/readiness/PR claims in Section 1 and Section 6
- Defers repair budget calibration to a separate gate (Section 8)

### F7. PASS — Forbidden commands correctly excluded

Section 1, Section 6, and Section 8 all forbid live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands. The allowed shell commands in Section 6 are precisely scoped: `git status --short`, `git diff --check`, `rg`, `sed`, `nl`, `jq`, and focused `uv run pytest ... -k ...`. No code/test/control/design/README edits are authorized.

### F8. PASS — Hypotheses correctly structured as unproven with direct evidence paths

Section 4 lists H1-H5, all marked "unproven" or "plausible but unproven." Section 5 provides E3-E7 as direct no-live evidence paths, each with:
- Specific reads/commands
- Conditional test addition authorization
- Clear acceptance evidence criteria (when to accept vs reject each hypothesis)
- Required disposition classification (accepted root cause, contributing cause, rejected, needs more evidence, blocked)

### F9. PASS — No implementation work over-authorized

The plan is scoped as planning only (Section 1). Evidence-gate test additions are conditional ("If adding tests is authorized by the evidence gate"). The plan does not authorize repair budget changes, source policy changes, or production behavior modifications (Section 5 preamble, Section 8).

### F10. PASS — Accepted current facts derived from allowed sources

Cross-checking Section 3 facts against the allowed controller judgment and safe metadata shows all facts are derivable from allowed sources:
- Chapter 3 fact-gap block: from controller judgment ✓
- Chapter 2 failure details: from `summary.json` and `chapter-02.json` ✓
- Per-attempt metadata: from `chapter-02.json` ✓
- Chapter 2 contract details: from template (allowed) ✓
- Writer prompt/anchor rules: from code read (allowed) ✓
- Repair policy mapping: from code read (allowed) ✓
- Diagnostic gaps: from `chapter_runtime_diagnostics` null fields ✓

No fact in Section 3 requires the unauthorized DS/MiMo review or evidence artifacts.

## 3. Verdict

VERDICT: **ACCEPT_WITH_AMENDMENTS**

The plan is structurally sound: it preserves NOT_READY and EID single-source/no-fallback, correctly treats DS observations as hypotheses, separates H1-H5 with direct no-live evidence paths, does not over-authorize implementation work, and provides precise enough commands for a disciplined worker. The accepted current facts are derivable from allowed sources.

Two amendments are required before this plan proceeds to the evidence gate:

1. **Remove three unauthorized artifacts from Section 2** (F1): `...review-ds-20260614.md`, `...review-mimo-20260614.md`, `...re-evidence-20260614.md`. Add explicit prohibition in Section 6 against reading these artifacts. The evidence worker must derive all hypotheses solely from the allowed controller judgment and safe metadata.

2. **Rephrase Section 1 DS-observation prohibition** (F2): Replace the ambiguous "Out of scope" phrasing with an active prohibition: "The evidence worker must not treat DS observations about `writer_deleted_item_rule_ids` or repair evidence usage as accepted root cause before direct no-live evidence proves them."

One non-blocking recommendation:

3. **Add test-collection pre-check** (F3): Before running `-k` selectors in E3-E7, collect available test names with `pytest --collect-only -q` and record "no matching existing tests" as evidence when selectors match nothing, rather than risking ambiguous empty output.

## 4. Residuals After Amendments

| Residual | Severity | Notes |
|---|---|---|
| Test `-k` selector existence not pre-verified | Low | Worker discipline risk; mitigated if F3 recommendation is adopted |
| E2 code read scope enforced only by worker discipline | Low | Inherent to markdown-based gate artifacts |
| `docs/design.md` read not explicitly in gate allowed list | Low | Covered by AGENTS.md mandatory read hierarchy |

## 5. Next Gate Recommendation

After amendments are applied, proceed to `Provider/LLM Chapter 2 L1 Numerical Closure No-live Root-cause Evidence Gate`. The evidence worker must:

- Confirm the amended plan's Section 2 contains only allowed reads
- Execute E0-E7 without reading the three prohibited artifacts
- Apply the acceptance criteria in Section 7 strictly
- Not treat H1-H5 as pre-accepted based on DS/MiMo observations
