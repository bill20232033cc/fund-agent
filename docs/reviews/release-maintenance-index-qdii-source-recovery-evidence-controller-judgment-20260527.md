# Controller Judgment: index/QDII source recovery evidence

> Controller: Codex
> Date: 2026-05-27
> Gate: `index/QDII source recovery evidence gate`
> Latest accepted checkpoint before gate: `bb1b67f`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `index/QDII source recovery and replacement plan accepted locally` |
| Reviewed evidence gate | `index/QDII source recovery evidence gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted plan artifacts |

## Decision

Accepted.

Both `110020` / 2024 and `017641` / 2024 remain outside the clean denominator. The public CLI path completed snapshot, score, and quality-gate runs, but public outputs did not expose the original upstream failure category behind the earlier fallback-blocked state. Under the accepted source fallback contract, CLI success and downstream field-quality results are not direct evidence that fallback was eligible. The correct terminal state for both rows is `unrecoverable_safe_path`.

Because no controller-approved replacement candidates were provided, Subgate B closes as `not_run_no_approved_candidates` for both rows.

## Review Summary

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS` | Accepted. No material findings. |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted. Low terminal-state documentation finding fixed in evidence artifact; no re-review required. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| Subgate B `not_run_no_approved_candidates` not formally stated | GLM F1 | Accepted and fixed | Evidence artifact now explicitly records Subgate B closes as `not_run_no_approved_candidates` for both rows while original rows remain `unrecoverable_safe_path`. |

## Evidence Results

| Candidate | Public CLI result | Upstream category recovered? | Terminal state | Clean denominator status |
|---|---|---|---|---|
| `110020` / 2024 | snapshot / score / quality-gate exit 0; classified `index_fund`; quality gate `warn` | No | `unrecoverable_safe_path`; replacement subgate `not_run_no_approved_candidates` | excluded |
| `017641` / 2024 | snapshot / score / quality-gate exit 0; classified `qdii_fund`; quality gate `block` | No | `unrecoverable_safe_path`; replacement subgate `not_run_no_approved_candidates` | excluded |

Generated outputs stayed in ignored `reports/extraction-snapshots/index-qdii-source-110020-2024/` and `reports/extraction-snapshots/index-qdii-source-017641-2024/`. No generated snapshot, score, quality-gate JSON, golden-set, PDF/cache output, durable baseline, or golden corpus file is accepted as tracked evidence.

## Validation

- `git diff --check`: passed.
- Evidence review: MiMo `PASS`.
- Evidence review: GLM `PASS_WITH_FINDINGS`; finding fixed.

## Scope Guard

No code, tests, renderer, Service/CLI behavior, Host/Agent/dayu, source strategy, source helpers, extractors, `fund_type.py`, FQ0-FQ6 policy, golden fixtures, baseline fixtures, direct PDF/cache/source-helper access, replacement search, or GitHub state was changed.

## Residual Risks

- Public Fund CLI output does not currently expose source fallback provenance for fallback-backed rows. A future public-output contract design would be required to recover this metadata without violating source boundaries.
- No approved replacement candidates exist for index/QDII coverage in this gate.
- Pure FOF coverage remains unresolved.
- `006597` remains baseline-blocked by `bond_risk_evidence_missing.baseline_blocking=true` and other residual P1 gaps.
- Golden corpus v1 remains blocked.

## Next Entry Point

`coverage replacement candidate selection or source provenance output design gate`

The next gate must choose between two safe paths:

- design an additive public-output contract for repository source fallback provenance; or
- provide controller-approved replacement candidates for index/QDII and run a separate repository-verified evidence gate.

Do not enter durable baseline/golden preflight until index/QDII, FOF, bond baseline-blocking, and reviewed-fact blockers are resolved.
