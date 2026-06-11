# Source-like Residue Ownership Plan Controller Judgment

日期：2026-06-11 12:20:48

Gate: `Source-like residue ownership gate for fund_agent/tools`

Classification: `standard`

Plan: `docs/reviews/mvp-source-like-residue-ownership-plan-20260611-121626.md`

Reviews:

- `docs/reviews/mvp-source-like-residue-ownership-plan-review-mimo-20260611-122048.md`
- `docs/reviews/mvp-source-like-residue-ownership-plan-review-ds-20260611-122048.md`

Verdict: `ACCEPT_WITH_EXPLICIT_DELETE_AUTH_REQUIRED`

## Basis

Accepted truth sources:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`

Review input:

- `docs/reviews/repo-review-20260611-114133.md`

## Controller Decision

The plan is accepted. The next gate may be a bounded implementation gate to remove `fund_agent/tools/` from the product package namespace.

Deletion is destructive and targets untracked local files. This controller judgment does not itself authorize deletion. The implementation gate requires explicit user authorization before any delete command or equivalent file removal action.

## Accepted Plan Findings

| Finding | Decision | Rationale |
|---|---|---|
| `fund_agent/tools/` is source-like residue under product package namespace | ACCEPT | Current control truth already identifies it as the active mainline residual; `pyproject.toml` package discovery makes future accidental package-scope drift a real release hygiene risk |
| `fund_agent/tools/claude_mimo.py` is non-product local workstation tooling | ACCEPT | It configures Claude/MiMo Token Plan and writes user home config/token fields; it is not fund-analysis functionality or accepted evidence |
| No tracked files or tracked references depend on `fund_agent/tools/` | ACCEPT | `git ls-files fund_agent/tools` is empty; tracked grep over `fund_agent`, `tests`, `pyproject.toml` and `README.md` has no relevant references |
| Main disposition should be `delete` | ACCEPT_WITH_AUTHORIZATION_REQUIRED | Delete is the smallest product-boundary fix, but it is destructive to untracked local files and must be separately authorized |
| `scripts/claude_mimo_simple.py` remains out of scope | ACCEPT | It is a separate tooling residue and must not be touched in this gate |
| `.gitignore`, `pyproject.toml`, README, source/tests/runtime remain out of scope | ACCEPT | Current gate only resolves `fund_agent/tools/` ownership/disposition; no product behavior or packaging config changes are accepted |

## Accepted Implementation Envelope

Allowed delete set, only after explicit user authorization:

- `fund_agent/tools/claude_mimo.py`
- `fund_agent/tools/__pycache__/claude_mimo.cpython-311.pyc`
- empty directory `fund_agent/tools/__pycache__/`
- empty directory `fund_agent/tools/`

Allowed evidence artifact:

- `docs/reviews/mvp-source-like-residue-ownership-implementation-evidence-20260611.md`

Forbidden:

- `.gitignore`
- `pyproject.toml`
- `README.md`
- `docs/design.md`
- `tests/**`
- `reports/**`
- `scripts/claude_mimo_simple.py`
- any archive/move destination
- source/test/runtime behavior changes
- stage/commit/push/PR/release state
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands

## Required Implementation Validation

Before deletion:

- `git status --branch --short`
- `find fund_agent/tools -maxdepth 2 -type f -print`
- `git ls-files fund_agent/tools`
- `git grep -n -e 'claude_mimo' -e 'fund_agent\.tools' -e 'claude_mimo_simple' -- fund_agent tests pyproject.toml README.md`

Stop condition:

- If `fund_agent/tools/` contains any file other than `claude_mimo.py` and `__pycache__/claude_mimo.cpython-311.pyc`, stop and return to controller.

After deletion:

- `test ! -e fund_agent/tools`
- `git status --short fund_agent/tools`
- `git ls-files | rg '(^fund_agent/tools/|__pycache__|\.pyc$)'`
- `git diff --check`

Tests/lint are not required unless tracked source/tests/runtime files unexpectedly change, which this gate forbids.

## Next Entry

Recommended next entry: `Source-like residue ownership implementation gate for fund_agent/tools`.

Required authorization: explicit user authorization to delete the accepted exact paths above.

Deferred entries:

- `scripts/claude_mimo_simple.py` tooling disposition gate
- runtime artifact disposition / ignore-rule planning gate
- EID source provenance truth alignment gate
- LLM execution request validation ordering gate
- UI-Service-Host boundary reconciliation gate
- release-readiness cleanliness gate
