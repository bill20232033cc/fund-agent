# Source-like residue ownership / non-impact disposition — DS review

Date: 2026-06-10
Reviewer: AgentDS
Gate: `source-like residue ownership / non-impact disposition gate`

## Verdict

**PASS**

The evidence artifact is sound. The two source-like paths are conclusively untracked, unstaged, and unreferenced by any tracked source, test, or config. The residue can safely be downgraded from blocker to non-impact residual, provided the EID implementation planning gate includes an explicit ignore boundary for these paths.

## Evidence verification

### 1. Untracked and unstaged status — CONFIRMED

| Check | Command | Expected | Actual | Match |
| --- | --- | --- | --- | --- |
| Working tree status | `git status --branch --short` | `??` prefix for both paths | `?? fund_agent/tools/`, `?? scripts/claude_mimo_simple.py` | Yes |
| Tracked file check | `git ls-files -- fund_agent/tools scripts/claude_mimo_simple.py` | Empty | Empty | Yes |
| Untracked non-ignored | `git ls-files --others --exclude-standard -- fund_agent/tools scripts/claude_mimo_simple.py` | Both paths listed | `fund_agent/tools/claude_mimo.py`, `scripts/claude_mimo_simple.py` | Yes |
| Ignored residue | `git ls-files --others --ignored --exclude-standard -- fund_agent/tools` | `.pyc` under `__pycache__/` | `fund_agent/tools/__pycache__/claude_mimo.cpython-311.pyc` | Yes |
| Staging state | `git diff --cached --name-only` | Empty | Empty | Yes |

The `.pyc` is covered by `.gitignore:3:__pycache__/` (not a file-specific rule). All `.gitignore` entries are project-global; the rule is correct.

### 2. No tracked dependency — CONFIRMED

| Check | Command | Expected | Actual | Match |
| --- | --- | --- | --- | --- |
| Direct name grep | `git grep -n -e 'claude_mimo' -e 'fund_agent\.tools' -e 'claude_mimo_simple' -- fund_agent tests pyproject.toml` | No matches | Exit code 1 (no matches) | Yes |
| Import pattern grep | `git grep -n -e 'from fund_agent.tools' -e 'import fund_agent.tools' -e 'from fund_agent\.tools'` | No matches | Exit code 1 (no matches) | Yes |
| Broad residual grep | `git grep -n -e 'claude_mimo' -e 'claude.mimo' -- fund_agent tests scripts pyproject.toml README.md` | No matches | Exit code 1 (no matches) | Yes |
| Dynamic import audit | `git grep -n -e 'sys\.path' -e 'importlib' -e '__import__' -e 'pkg_resources' -- fund_agent tests` | Only refer to tracked packages | Only `fund_agent.config.paths` and `fund_agent.fund.report_quality_validation` — both tracked | Yes |

### 3. pyproject package include risk — CORRECTLY DOCUMENTED

The evidence correctly identifies:

- `include = ["fund_agent*"]` would capture `fund_agent/tools/` if committed → residual risk.
- `exclude = ["scripts*"]` excludes `scripts/claude_mimo_simple.py` from package discovery → no risk.
- `[project.scripts]` entry point `fund-analysis` does not reference either residue path.

**Additional finding not in evidence**: `fund_agent/tools/` does NOT contain `__init__.py`. It is not a Python package and cannot be imported as `fund_agent.tools` even while the directory exists on disk. This is a mitigating factor — it reduces the risk of accidental runtime import below what the evidence implies. The pyproject `include` risk (if staged) remains real but requires both staging AND adding `__init__.py` to become an importable subpackage.

### 4. Non-impact downgrade assessment — SAFE

Conditions for safe downgrade:

- [x] Paths are untracked and unstaged
- [x] No tracked source/test/config imports or references them
- [x] No dynamic import or sys.path manipulation targets them
- [x] They do not participate in EID source policy, FundDocumentRepository, source adapters, extractors, fixtures, provider runtime, or fallback
- [x] They are not valid evidence for architecture truth, source truth, implementation truth, or release readiness
- [x] `fund_agent/tools/` has no `__init__.py`, so it's not an importable subpackage

The residual risk (accidental staging later) is real but bounded. The evidence's recommendation that EID planning must include an explicit ignore boundary is correct and sufficient mitigation.

### 5. Hidden risks — NONE FOUND

| Risk area | Finding |
| --- | --- |
| Namespace package collision | No. `fund_agent/tools/` has no `__init__.py` |
| sys.path injection | No dynamic path manipulation found in tracked code |
| .pth file interference | No `.pth` files observed |
| importlib / pkg_resources | Both grep hits refer to tracked packages only |
| Entry point shadowing | `[project.scripts]` only defines `fund-analysis = "fund_agent.ui.cli:app"`, no collision |
| .gitignore false coverage | `__pycache__/` rule is project-global and correctly matches |
| exec/eval of residue paths | No grep matches found |

## Recommendations

1. The evidence artifact should be amended to note the absence of `__init__.py` in `fund_agent/tools/` — this is a material mitigating factor that reduces the stated risk level of the pyproject `include` concern.
2. EID implementation planning gate startup judgment must include an explicit ignore boundary clause listing both paths as excluded workspace residue.
3. The pyproject include risk, while real, requires two independent actions to manifest (stage the directory AND add `__init__.py`). This should be noted in the EID planning gate's risk register rather than treated as a gate-level blocker.
