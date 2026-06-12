# Review: Quality Warning Issue Identity Evidence Gate

Date: 2026-06-12

Reviewer: Meitner sub-agent

Gate: `Quality warning issue identity evidence gate`

Review target: `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`

Accepted basis:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-quality-warning-issue-root-cause-plan-controller-judgment-20260612.md`

## 1. Verdict

**PASS_WITH_FINDINGS**

## 2. Findings

| id | severity | finding | evidence | recommendation |
|---|---|---|---|---|
| QW-ID-001 | non-blocking | 三条 issue identity 证据足以接受：`FQ2/warn turnover_rate`、`FQ2F/warn 004393 derived from turnover_rate`、`FQ0/info year_not_covered` 均有 current-gate `quality_gate.json` 直接行与 `score.json` 摘要支撑。 | Evidence artifact §6-§8；`quality_gate.json` 三条 issue 与 artifact 一致；`score.json` 中 `turnover_rate` 为 P1 fail、004393 `p1_failed_fields=["turnover_rate"]`、correctness `coverage_reason=year_not_covered`。 | Accept issue identities for controller judgment. |
| QW-ID-002 | non-blocking | Artifact 正确拒绝 path-exists-only `reports/` residue，并在 E1 记录 durable lineage gap 后才使用 current-gate bounded live reproduction。 | Evidence artifact §3-§5；root-cause judgment requires no path-only proof and bounded reproduction. | Accept lineage approach. |
| QW-ID-003 | low | Current-gate generated report artifacts 有 path+size+SHA-256；stdout/stderr capture 记录了 temp path、size 和 header facts，但未记录 stdout/stderr 文件 SHA-256。该缺口不阻断 issue identity，因为 issue rows 来自已 hash 的 `quality_gate.json` / `score.json`。 | Evidence artifact §4-§5 records stdout/stderr path/size and output paths; artifact identity table records hashes for quality artifacts. | Controller judgment should note stdout/stderr capture hash absence as lineage hygiene residual; future live evidence artifacts should hash stdout/stderr captures too. |
| QW-ID-004 | non-blocking | Release/readiness 口径正确保持 `NOT_READY`；未把本次 live command 扩展成 broader readiness/sample/provider claim。 | Evidence artifact §1, §10-§11; startup/control docs preserve single-sample/no-readiness boundary. | Accept. |
| QW-ID-005 | non-blocking | Next mainline 推荐 `Turnover rate extraction/traceability root-cause planning gate` 合理；`Strict golden 2025 coverage/promotion planning gate` 应作为 deferred entry，而非当前主线。 | Evidence artifact §9-§11; design/control docs keep extractor and golden/readiness as separate owners. | Accept routing. |

## 3. Residuals

| Residual | Owner | Blocks readiness? |
|---|---|---|
| `turnover_rate` P1 coverage/traceability failure | Fund extractor / traceability owner | Yes |
| `FQ2F` aggregate fund-level warning | Quality gate + Fund extractor owner | Yes until the underlying P1 failure is dispositioned |
| `FQ0/info year_not_covered` | golden/readiness owner | Yes for readiness/promotion, not an extractor failure |
| Broader live sample coverage | release/evidence owner | Yes for broader readiness |
| Provider/LLM readiness, PR/release/readiness | corresponding owners | Out of scope and unproven |
| stdout/stderr capture hash absence | controller/evidence owner | No for this gate; improve future live evidence hygiene |

## 4. Final Recommendation

Accept `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md` with the low-severity lineage hygiene note above.

Recommended next mainline:

`Turnover rate extraction/traceability root-cause planning gate`

Deferred:

- `Strict golden 2025 coverage/promotion planning gate`
- additional controlled live sample gate
- provider/LLM readiness gate
- PR/release/readiness external-state gate

Release/readiness remains **`NOT_READY`**.
