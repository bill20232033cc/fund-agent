# Controller Judgment: Quality Warning Issue Root-cause Planning Gate

Date: 2026-06-12

Role: controller

Gate: `Quality warning issue root-cause planning gate`

Classification: `standard`

Plan artifact:

- `docs/reviews/mvp-quality-warning-issue-root-cause-plan-20260612.md`

Independent reviews:

- `docs/reviews/mvp-quality-warning-issue-root-cause-plan-review-ds-20260612.md`
- `docs/reviews/mvp-quality-warning-issue-root-cause-plan-review-mimo-20260612.md`

Accepted input:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md`
- `docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-evidence-controller-judgment-20260612.md`
- Checkpoint `0e50986`
- Control-sync checkpoint `ebe74ae`

## 1. Verdict

**ACCEPT_WITH_LINEAGE_AMENDMENT_NOT_READY**

The plan is accepted after amendment.

Accepted planning facts:

- the durable evidence chain currently accepts `quality_gate_status=warn` and `quality_gate_issues=3`
- the durable evidence chain does not yet accept the three issue identities, rule codes, fields or messages
- arbitrary untracked `reports/` residue must not be used as proof
- issue identity/root-cause evidence must precede implementation/fix
- live reproduction, if needed, must be a separate accepted evidence gate with exact command, sample, stop conditions, capture identity and allowed reads

Release/readiness remains **`NOT_READY`**.

The user's live authorization is not consumed by this planning gate.

## 2. Review Finding Disposition

| Finding | Controller disposition | Basis | Required handling |
|---|---|---|---|
| DS-PLAN-001: no inference from unaccepted `reports/` residue | ACCEPT | Plan §4 discards exploratory reports observations for proof | Carry forward |
| DS-PLAN-002: live reproduction separated and bounded | ACCEPT | Plan puts live reproduction in future evidence gate E3 | Carry forward |
| DS-PLAN-003: root-cause evidence before implementation | ACCEPT | Plan defers implementation/fix until issue identity/root cause evidence | Carry forward |
| DS-PLAN-004: `warn/issues=3` remains `NOT_READY` | ACCEPT | Plan and control docs preserve readiness residual | Carry forward |
| DS-PLAN-005: residual owner/next gate explicit | ACCEPT | Plan residual owner table and next entry are explicit | Carry forward |
| MIMO-RC-PLAN-001: E1 lineage PASS condition too weak | ACCEPT_AS_AMENDED | Plan E1 now requires accepted issue rows, or path plus hash/size/run id matching current file; path existence alone is insufficient | No further plan change |
| MIMO-RC-PLAN-002: next live evidence gate must restate authorization and exact boundary | ACCEPT | Plan E3 and live reproduction stop conditions require separate accepted evidence gate | Controller must carry this into next gate |

No finding blocks acceptance after amendment.

## 3. Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| `Quality warning issue identity evidence gate` as next entry | ACCEPT | Issue identities are not accepted durable facts yet |
| Path-exists-only use of untracked `reports/` artifacts | REJECT | Mutable residue cannot become proof |
| No-live lineage using accepted issue rows or path+hash/size/run id | ACCEPT | Provides direct evidence if available |
| Controlled live reproduction if lineage fails | ACCEPT_AS_SEPARATE_GATE_ONLY | Requires next gate to restate exact live boundary and authorization |
| Root-cause evidence before implementation | ACCEPT | Prevents premature fix or policy change |
| Implementation/fix in this planning gate | REJECT | Planning-only |
| Treating `warn/issues=3` as readiness pass | REJECT | Contradicts accepted controller facts |
| Additional live sample coverage | DEFER | Separate live sample gate |
| Provider/LLM readiness | DEFER | Separate provider/LLM gate |
| Fixture/golden/readiness promotion | DEFER | Separate promotion/readiness gate |
| Cleanup/archive/delete/import/ignore | DEFER | Explicit artifact-action gate only |
| PR/push/merge/mark-ready/release | DEFER | Explicit external-state gate only |

## 4. Verification

| Command | Result |
|---|---|
| `git status --short` | Exit `0`; existing unrelated untracked residue plus this gate's plan/review/controller artifacts |
| `git status --branch --short` | Exit `0`; branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 197]`; existing unrelated untracked residue plus this gate's artifacts |
| `git diff --name-only` | Exit `0`; no output |
| `git diff --check` | Exit `0`; no output |

No live/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR command was run for this planning gate.

An exploratory `rg` over untracked `reports/` residue occurred during planning. It is explicitly discarded from the proof chain and did not inform accepted issue identity/root-cause facts.

## 5. Residuals

| Residual | Owner | Next handling | Blocks readiness? |
|---|---|---|---|
| Issue identity not accepted | controller/evidence owner | `Quality warning issue identity evidence gate` | Yes |
| Three quality warnings unresolved | release/readiness owner + quality gate owner | identity evidence, then root-cause disposition | Yes |
| Possible extractor data gap | Fund/extractor owner | only after issue identity proves extractor-related rule | Unknown |
| Possible strict golden coverage gap | golden/readiness owner | only after issue identity proves correctness/coverage rule | Unknown |
| Possible artifact lineage gap | controller/evidence owner | record blocker if no accepted lineage exists | Yes |
| Additional live sample coverage | evidence/release owner | separate live sample gate | Yes for broader readiness |
| Provider/LLM readiness | provider/runtime owner | separate provider/LLM gate | Yes for LLM readiness |

## 6. Next Entry

Accepted next mainline:

`Quality warning issue identity evidence gate`

Boundary:

- evidence-only unless a later reviewed implementation gate is accepted
- first try accepted durable lineage
- do not use path existence alone as proof
- if live reproduction is needed, use only a separately accepted one-command live gate
- no source/test/runtime behavior changes
- no readiness claim
- no cleanup or external-state action

Deferred entries:

- quality warning implementation/fix gate
- additional EID live sample gate
- live provider / LLM acceptance gate
- fixture/golden/readiness promotion gate
- cleanup/archive/delete/import/ignore artifact-action gate
- PR / push / merge / mark-ready / release external-state gate

## 7. Final State

Quality warning issue root-cause plan is accepted.

Release/readiness remains **`NOT_READY`**.
