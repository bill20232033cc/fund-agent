# Source-like residue ownership / non-impact disposition evidence

Date: 2026-06-10

Gate: `source-like residue ownership / non-impact disposition gate`

Scope:

- `fund_agent/tools/`
- `scripts/claude_mimo_simple.py`

## Controller note on worker routing

The intended disposition/evidence worker was AgentCodex. AgentCodex was not used because two consecutive `/clear` attempts left prior-session prompt text visible in the pane capture. Per `init-agents` clear-verification rules, the controller did not send a new handoff to that pane.

This artifact is a bounded controller evidence artifact. It uses only local Git/search/file-metadata checks and does not execute the source-like residue.

## Direct evidence

### Working tree state

Command:

```bash
git status --branch --short
```

Relevant result:

```text
## feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 31]
?? fund_agent/tools/
?? scripts/claude_mimo_simple.py
```

Tracked diff remains clean; the relevant paths are untracked.

### Tracked-file ownership

Command:

```bash
git ls-files -- fund_agent/tools scripts/claude_mimo_simple.py
```

Result: no tracked files.

Command:

```bash
git ls-files --others --exclude-standard -- fund_agent/tools scripts/claude_mimo_simple.py
```

Result:

```text
fund_agent/tools/claude_mimo.py
scripts/claude_mimo_simple.py
```

Ignored generated residue:

```text
.gitignore:3:__pycache__/ fund_agent/tools/__pycache__/claude_mimo.cpython-311.pyc
```

### Staging state

Command:

```bash
git diff --cached --name-only
```

Result: empty. No candidate residue is staged.

### Tracked source/test/config references

Command:

```bash
git grep -n -e 'claude_mimo' -e 'fund_agent\.tools' -e 'claude_mimo_simple' -- fund_agent tests pyproject.toml
```

Result: no matches.

Interpretation: tracked source, tests and packaging config do not import or reference `claude_mimo`, `fund_agent.tools`, or `claude_mimo_simple`.

### Packaging boundary

Relevant `pyproject.toml` excerpt:

```toml
[project.scripts]
fund-analysis = "fund_agent.ui.cli:app"

[tool.setuptools.packages.find]
where = ["."]
include = ["fund_agent*"]
exclude = ["tests*", "docs*", "reports*", "scripts*", "workspace*", "cache*"]
```

Interpretation:

- `scripts/claude_mimo_simple.py` is outside the package include scope and `scripts*` is excluded from package discovery.
- `fund_agent/tools/` is currently untracked, but if it were staged/committed as package source, it would fall under `include = ["fund_agent*"]`. That makes it source-like residue with package-scope risk, not a harmless generated artifact.
- `fund_agent/tools/__init__.py` is absent. The current untracked directory contains only `fund_agent/tools/claude_mimo.py` at max depth 1, so current tracked code cannot import it as an established tracked subpackage. This is a mitigating factor only; it does not authorize staging the directory.

### File content classification

`fund_agent/tools/claude_mimo.py` and `scripts/claude_mimo_simple.py` are local Claude/MiMo configuration helpers. Their documented behavior is to write local Claude configuration files under the user's home directory, including `~/.claude/settings.json` and `~/.claude.json`.

The files were read only as text snippets. They were not executed.

## Disposition table

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
| --- | --- | --- | --- | --- | --- | --- |
| `fund_agent/tools/claude_mimo.py` | source-like user-owned residue | Untracked; not staged; no tracked source/test/config references; package include would cover `fund_agent*` if committed; no `fund_agent/tools/__init__.py` present | `leave-untracked`; do not stage, import, execute, or use as source truth | User/controller disposition owner | EID implementation planning may proceed only with explicit ignore boundary | No, if left untracked and unused |
| `fund_agent/tools/__pycache__/claude_mimo.cpython-311.pyc` | ignored generated residue | Ignored by `.gitignore:3:__pycache__/` | `leave-ignored`; deletion requires explicit user authorization | User | None | No |
| `scripts/claude_mimo_simple.py` | source-like user-owned residue | Untracked; not staged; no tracked source/test/config references; `scripts*` excluded from package discovery | `leave-untracked`; do not stage, execute, or use as source truth | User/controller disposition owner | EID implementation planning may proceed only with explicit ignore boundary | No, if left untracked and unused |

## Non-impact judgment for EID planning

Direct evidence supports converting the prior hygiene blocker into a bounded residual:

- The source-like files are untracked and unstaged.
- No tracked source, tests, or packaging config currently reference them.
- They do not participate in the EID source policy, `FundDocumentRepository`, source adapters, extractor behavior, fixtures, provider runtime, fallback, or quality gate.
- They are not valid evidence for current architecture truth, source truth, implementation truth, or release readiness.

The main residual risk is package-scope drift: `fund_agent/tools/` would become package source if accidentally staged later. Therefore the next EID planning gate must explicitly state that these paths are ignored workspace residue and are outside allowed files.

## Validation

No live EID/network/PDF/FDR/fallback/provider command was run.

No source, tests, README, runtime config, provider defaults, extractor code, fixture data or control docs were modified.

No cleanup, deletion, reset, rebase, squash, push, PR, merge, release or mark-ready action was performed.
