# AGENTS Rules Truth Sync Review Controller Judgment - 2026-06-15

## 1. Scope

This controller judgment reviews the current workspace diff for `AGENTS.md` as the final item in the scoped accepted checkpoint sequence.

This gate does not edit `AGENTS.md`, source code, tests, runtime behavior, source policy, parser behavior, `FundDocumentRepository`, Service/Host/Agent contracts, readiness, release, PR, or external state.

## 2. Evidence Reviewed

- `git branch --show-current`: `feat/mvp-llm-incomplete-run-artifacts`
- `git status --short`: one tracked diff in `AGENTS.md`, plus untracked residue already dispositioned by prior workspace-scope reconciliation.
- `git diff --stat -- AGENTS.md`: `336` changed lines, `122` insertions, `214` deletions.
- Current workspace `AGENTS.md`
- `git show HEAD:AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` targeted guardrail search

## 3. Accepted Current Facts

| Fact | Basis |
|---|---|
| `AGENTS.md` is the highest-priority execution-rule source. | `AGENTS.md`; `docs/implementation-control.md`; `docs/current-startup-packet.md` |
| Current mainline remains `Docling Baseline Qualification Acquisition Status Planning Gate`. | `docs/current-startup-packet.md`; `docs/implementation-control.md` |
| Current mainline is planning-only and preserves `NOT_READY`. | `docs/current-startup-packet.md`; `docs/implementation-control.md` |
| Current annual-report source policy remains EID single-source/no-fallback. | `docs/implementation-control.md`; `docs/current-startup-packet.md` |
| Docling, pdfplumber and EID HTML render remain candidate/evidence inputs only; no source-truth, field-correctness, taxonomy or readiness proof is accepted. | `docs/current-startup-packet.md`; `docs/implementation-control.md`; `docs/design.md` |

## 4. Diff Classification

| Area | Current Diff Result | Controller Disposition |
|---|---|---|
| Developer commands / project structure | Adds useful local command and package structure notes. | Acceptable content, but not sufficient to justify the full rewrite. |
| Truth-doc hierarchy | Keeps high-level hierarchy but deletes detailed `docs/design.md` and `docs/implementation-control.md` norms. | Rejected as-is. |
| Gate classification | Keeps labels but deletes important scope limits: final judgment, Host/Agent/dayu, external source strategy, baseline/golden, release/PR state. | Rejected as-is. |
| Module boundary | Keeps short ownership bullets but deletes explicit UI/Service/Host/Agent responsibilities and dependency constraints. | Rejected as-is. |
| Dayu boundary | Keeps high-level "not production dependency" but deletes no direct `dayu-agent` / `dayu.host` / `dayu.engine` dependency and license/compliance-gate wording. | Rejected as-is. |
| Repository/source boundary | Keeps `FundDocumentRepository` and parser-internal wording. | Partially acceptable. |
| EID source policy | Updates fallback section to current EID single-source/no-fallback. | Acceptable and better aligned with current control truth. |
| README/doc sync | Compresses fixed README role definitions and trigger matrix too aggressively. | Rejected as-is. |
| Testing/docstring rules | Keeps key rules, adds useful fake/mock isolation guidance. | Partially acceptable. |
| Fund analysis must-do rules | Deletes explicit structural alpha vs stage alpha, manager holding check, stress test, and next minimum validation question. | Rejected as-is. |
| Release/readiness guard | Does not explicitly encode preserve `NOT_READY` / no readiness claim discipline. | Rejected as-is for current workflow. |
| XBRL/Docling candidate guard | Does not encode current candidate-only / no raw XML / no source-truth guard. | Rejected as-is for current workflow. |

## 5. Findings

| ID | Finding | Severity | Disposition | Basis |
|---|---|---:|---|---|
| A1 | The rewrite removes detailed truth-doc rules that prevent candidate/research/future design from being written as current fact. | High | ACCEPT_FINDING | `AGENTS.md` HEAD; `docs/implementation-control.md`; current `docs/design.md` route sync |
| A2 | The rewrite weakens gate classification constraints by omitting specific high-impact dimensions: final judgment, Host/Agent/dayu, source strategy, baseline/golden, release/PR external state. | High | ACCEPT_FINDING | `AGENTS.md` HEAD; current gate classification in control docs |
| A3 | The rewrite compresses UI/Service/Host/Agent responsibilities enough that future agents could blur ownership, especially Service/Host/Agent and Fund documents boundaries. | High | ACCEPT_FINDING | `AGENTS.md` HEAD; `docs/implementation-control.md` current guardrails |
| A4 | The rewrite does not carry the current Docling/XBRL candidate-only guardrails into `AGENTS.md`, even though these are now central workflow risks. | Medium | ACCEPT_FINDING | `docs/current-startup-packet.md`; `docs/implementation-control.md`; `docs/design.md` |
| A5 | The rewrite improves current source-policy wording by replacing old fallback-eligible language with EID single-source terminal-failure wording. | Medium | ACCEPT_AS_KEEPER | `docs/implementation-control.md`; `docs/current-startup-packet.md` |
| A6 | The rewrite adds useful developer commands and project structure, but these are operational conveniences, not a reason to accept hard-rule deletion. | Low | ACCEPT_AS_KEEPER_FOR_REWRITE | Current `AGENTS.md` diff |
| A7 | The rewrite deletes several fund-analysis must-do requirements that are still domain guardrails, including structural/stage alpha distinction, manager holding check, stress test and next minimum validation question. | Medium | ACCEPT_FINDING | `AGENTS.md` HEAD |

## 6. Verdict

VERDICT: REJECT_AGENTS_RULES_SYNC_NEEDS_REWRITE_NOT_READY

The current `AGENTS.md` diff must not be staged or committed as a rules-truth sync checkpoint. It is a broad rewrite with useful additions, but it weakens the repository's highest-priority rule source.

## 7. Accepted / Rejected / Deferred Table

| Item | Decision | Reason |
|---|---|---|
| Commit current `AGENTS.md` diff | REJECT | Removes or weakens hard constraints from the highest-priority rule source. |
| Preserve EID single-source/no-fallback wording | ACCEPT_FOR_REWRITE | Aligns with current control truth and corrects old fallback wording. |
| Preserve developer commands/project structure additions | ACCEPT_FOR_REWRITE | Useful if merged into a rule-preserving rewrite. |
| Preserve fake/mock/network isolation test guidance | ACCEPT_FOR_REWRITE | Useful testing discipline and consistent with non-live gate style. |
| Delete detailed truth-doc, gate, boundary and README role rules | REJECT | These are still active guardrails and must be retained or equivalently rewritten. |
| Add Docling/XBRL candidate-only and `NOT_READY` guardrails to `AGENTS.md` | DEFER_TO_REWRITE_GATE | Needed, but should be implemented as a separate rules-sync rewrite, not by accepting current diff. |

## 8. Required Rewrite Plan

A safe follow-up `AGENTS.md` rules-sync rewrite should:

1. Start from HEAD `AGENTS.md` rather than from the compressed diff.
2. Apply only accepted additions:
   - developer commands and project structure, if kept accurate;
   - EID single-source/no-fallback terminal failure wording;
   - parser internals through `FundDocumentRepository`;
   - test fake/mock/network isolation guidance.
3. Preserve or equivalently restate:
   - full truth-doc norms;
   - full gate classification semantics;
   - UI/Service/Host/Agent responsibilities and dependency boundaries;
   - Dayu no-runtime-dependency and license/compliance gate;
   - README role definitions and trigger matrix;
   - fund-analysis must-do requirements.
4. Add current route guardrails:
   - Docling candidate-only, not production parser replacement;
   - EID XBRL HTML render candidate, not raw XML/source truth;
   - no field-correctness/taxonomy/readiness claim without later accepted gates;
   - preserve release/readiness `NOT_READY`.

## 9. Residuals

| Residual | Owner | Next Handling | Blocks Docling Planning Gate? |
|---|---|---|---|
| `AGENTS.md` remains modified in workspace. | Controller / rules owner | Separate `AGENTS.md Rules Truth Sync Rewrite Gate`; do not stage current diff. | Does not block planning if left unstaged, but blocks PR/clean workspace. |
| Untracked residue remains visible. | Artifact owners | Already dispositioned as leave-untracked / future gates; do not bulk stage. | Does not block current Docling planning gate; blocks PR/readiness cleanliness. |
| Current route still `NOT_READY`. | Release owner | Future readiness gate only. | No. |

## 10. Next Entry

Recommended next entry after this checkpoint sequence:

`Docling Baseline Qualification Acquisition Status Planning Gate`

This next gate is planning-only. It must not run Docling conversion, EID acquisition, live/network/PDF/FDR, pdfplumber export, manual reference review, provider/LLM/analyze/checklist/golden/readiness/release/PR commands, and must not change repository behavior or production parser/source policy.
