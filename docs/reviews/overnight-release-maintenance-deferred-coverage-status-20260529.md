# Overnight Release Maintenance Deferred Coverage Status

日期：2026-05-29

角色：Track 2 deferred coverage status artifact worker。

本文是 docs-only deferred coverage status artifact。它只记录 overnight release maintenance roadmap Track 2 的已接受延后覆盖状态，不做新 probing，不实现 taxonomy / extractor / runtime，不修改 manifest、control doc、design doc、golden、fixtures、reports、score、snapshot 或 quality gate。

## Scope And Guardrails

Gate：`Track 2 deferred coverage status`

Gate classification：`standard`。原因：本 gate 是 disposition / roadmap artifact，不改变 runtime、schema、score、quality gate、golden readiness、fixture promotion 或 release state。

硬边界：

- 不重启 QDII automatic probing。
- 不实现 FOF taxonomy，不把 QDII-FOF 计为 pure FOF。
- 不修复 `110020`、`017641`，不运行 rerun / probe / evidence commands。
- 不修改 golden answer、golden fixtures、reports、preflight output、residual manifest、fixture promotion manifest、runtime code、tests、scripts、`docs/design.md` 或 `docs/implementation-control.md`。
- 不改变 FQ0-FQ6、score policy、quality gate severity、final judgment、Service/CLI、renderer、Host/Agent/dayu。
- 不 promotion、不 stage、不 commit、不 push、不 PR、不 merge、不 release。

## Evidence Freeze

本 artifact 基于已接受证据链：

| Evidence | Use |
|---|---|
| `AGENTS.md` | gate 分类、真源、fail-closed 来源纪律、禁止 promotion / GitHub mutation |
| `docs/design.md` §7.3 / §7.4 | strict correctness、P0/P1 字段、quality gate 语义 |
| `docs/implementation-control.md` | current release-maintenance state、Track 2 residual 口径 |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` | five-route roadmap；Route 2 deferred coverage scope |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` | Controller accepted：QDII candidates、`017641`、`FOF_SLOT`、`110020` deferred from minimum v1 and still block full v1 |
| `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` / `.md` | Preflight remains BLOCK；QDII/FOF/110020/017641 not ready |
| `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | Track 2 rows keep `blocks_minimum_v1=false`, `blocks_v1=true`, `promotion_allowed=false` |
| `docs/reviews/fixture-promotion-state-manifest-20260529.json` | Track 2 rows keep `fixture_state=deferred_from_v1` or not applicable, `promotion_allowed=false` |
| `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` | QDII automatic probing stopped；QDII candidates remain quality-blocked / not promoted |
| `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` | `017641=replace`；`FOF_SLOT=needs_taxonomy_gate`; `110020=include_for_later_review` |
| `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | `110020` provenance complete / warn；`017641` provenance complete but quality block |
| `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` | `110020` accepted only as reviewed coverage candidate input, not promoted |
| `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | `017641` terminal `disclosure_data_gap_not_baseline_ready`, not promoted |

## Summary Decision

Track 2 deferred coverage rows are not current Track 1 minimum v1 promotion-prep candidates.

| Scope | State |
|---|---|
| `track` | `deferred_coverage` |
| `minimum_v1_candidate_now` | `false` |
| `promotion_allowed` | `false` |
| `promotion_manifest` | `false` |
| `probe_now` | `false` |
| `runtime_change_now` | `false` |
| `manifest_mutation_now` | `false` |

All Track 2 items remain deferred / not ready. They do not block the current minimum-v1 path, but they remain full-v1 blockers until separate policy, taxonomy, evidence sufficiency, or fact-freeze gates accept a different disposition.

## Deferred Coverage Matrix

| Item | Current disposition | Owner | Next gate | Blocks minimum v1 | Blocks full v1 | Promotion allowed |
|---|---|---|---|---:|---:|---:|
| QDII hard stop | `blocked_until_policy`; automatic QDII probing stopped | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | false | true | false |
| QDII candidates `096001`, `040046`, `019172`, `021539` | deferred from minimum v1; source provenance eligible but quality block / not promoted | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | false | true | false |
| `017641 / 2024` | `replace` / `defer_from_v1`; source provenance complete but P0 `manager_strategy_text` quality/data gap remains | future QDII diagnosis / replacement owner | QDII diagnosis or explicit deferred-from-v1 gate | false | true | false |
| `FOF_SLOT / 2024` | `defer_from_v1`; pure FOF taxonomy/data gap | future FOF taxonomy / pure FOF candidate gate | pure FOF repository-verified candidate gate | false | true | false |
| `110020 / 2024` | `defer_from_v1`; reviewed coverage candidate input only; index evidence insufficient | future index evidence sufficiency gate | index reviewed fact-freeze / methodology / constituents evidence gate | false | true | false |

## QDII Status

Accepted QDII state:

- QDII is deferred from minimum v1.
- Automatic QDII probing remains stopped.
- QDII remains a full-v1 blocker.
- QDII candidates are not ready and not promoted.
- No further QDII candidate evidence may run until a separate diagnosis, taxonomy / asset-class fitness, or explicit coverage-blocked gate is accepted.

Rows covered by this status:

- global `qdii_replacement_hard_stop`
- `096001 / 2024`
- `040046 / 2024`
- `019172 / 2024`
- `021539 / 2024`
- `017641 / 2024` as the prior QDII row with replacement / deferred disposition

This artifact does not authorize new QDII evidence, candidate search, replacement probing, source probing, extractor work, fixture work, or golden changes.

## FOF Status

Accepted FOF state:

- `FOF_SLOT` is deferred from minimum v1.
- `FOF_SLOT` remains a full-v1 blocker.
- Pure FOF coverage has a taxonomy/data gap.
- QDII-FOF cannot count as pure FOF without a separate accepted taxonomy decision.
- No repository-verified pure FOF candidate is accepted for promotion-prep.

Future work is optional and gated: a pure FOF repository-verified candidate gate or FOF taxonomy gate may be opened later. This artifact does not implement taxonomy and does not run any FOF search.

## 110020 Status

Accepted `110020 / 2024` state:

- `110020` is accepted only as `reviewed_coverage_candidate_input_accepted`.
- It remains `not_promoted`.
- It is deferred from minimum v1.
- It remains a full-v1 blocker.
- Source provenance is complete and quality status is `warn`, but that does not create durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus state.
- Index evidence remains insufficient for durable full-v1 coverage: methodology / constituents / reviewed fact-freeze and strict golden absence disposition still require a separate gate.

Future work, if prioritized, belongs to an index reviewed fact-freeze / methodology / constituents evidence gate. This artifact does not fix, rerun, promote, or mutate `110020`.

## 017641 Status

Accepted `017641 / 2024` state:

- `017641` has `replacement_disposition=replace`.
- It is deferred from minimum v1.
- It remains a full-v1 blocker.
- It remains `not_promoted`.
- Source provenance is complete after the bounded public rerun, but quality remains `block`.
- The blocking public-output fact is P0 `manager_strategy_text`: missing extraction, no value, no anchor, no section/page/table/row locator, and quality gate block through FQ2 / FQ3 / FQ2F.
- Terminal classification remains `disclosure_data_gap_not_baseline_ready`.

This artifact does not authorize an extractor fix, policy/taxonomy change, quality weakening, baseline inclusion, fixture promotion, or golden answer promotion for `017641`.

## Work Type Split

| Work type | Track 2 examples | Authorized now |
|---|---|---:|
| Code implementation | FOF taxonomy implementation, QDII source/candidate automation, extractor projection for `017641`, index methodology / constituents extractor expansion, manifest runtime consumption | no |
| Business / policy fact-freeze | QDII deferred-from-v1 policy, pure FOF definition and candidate acceptance, `110020` reviewed fact-freeze, `017641` replacement/quality disposition | future optional gates only |
| Manifest / control-plane maintenance | Updating residual / fixture manifests, control doc route summaries, preflight consumption of manifests | no mutation in this gate |
| Docs-only disposition | Recording current deferred coverage status and next optional gates | yes, this artifact only |

## Future Optional Gates

These are future optional gates, not immediate probing instructions:

| Future gate | Purpose | Preconditions |
|---|---|---|
| QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | Decide whether QDII stays deferred, needs taxonomy / asset-class fitness review, or gets a new approved candidate process | Controller explicitly opens gate; plan/review before evidence |
| Pure FOF repository-verified candidate gate | Establish a pure FOF candidate or maintain data gap | Taxonomy decision must not count QDII-FOF as pure FOF |
| Index reviewed fact-freeze / methodology / constituents evidence gate | Decide if `110020` can move beyond reviewed candidate input | Reviewed evidence and strict golden disposition required |
| `017641` QDII replacement / quality disposition gate | Decide replacement, exclusion, or future evidence path | No extractor implementation unless new same-source public evidence and accepted plan justify it |
| Manifest/control-plane lifecycle gate | Reconcile manifests / preflight if desired | Separate schema/lifecycle plan; no promotion by implication |

## Non-Goals / Forbidden Changes

This Track 2 artifact explicitly does not:

- make any item ready;
- promote any item;
- add or edit golden rows;
- mutate residual or fixture manifests;
- update preflight outputs;
- rerun score, quality gate, snapshot, extraction, source probing, QDII probing, FOF probing, or evidence commands;
- modify runtime, tests, scripts, `docs/design.md`, `docs/implementation-control.md`, AGENTS, README, pyproject or lock files;
- change FQ / score / quality semantics;
- enter Track 1 minimum v1 promotion-prep;
- enter Host/Agent/dayu, PR, push, merge, release, or promotion work.

## Validation

Required docs-only validation for this artifact:

```text
git diff --check -- docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
```

Expected result：passed, no output.

Forbidden diff check:

```text
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json docs/implementation-control.md docs/design.md reports/golden-answers
```

Expected result：passed, no output.

`ruff` / `pytest` are not required because this is docs-only disposition work and does not modify Python, tests, runtime behavior, snapshot projection, score semantics, quality gate semantics, preflight consumption, manifests, reports or golden fixtures.

## Self-Check

Self-check：pass. This artifact records Track 2 as deferred / not ready, with `blocks_minimum_v1=false`, `blocks_full_v1=true`, and `promotion_allowed=false` for QDII, FOF, `110020`, and `017641`, and it does not authorize probing or implementation.
