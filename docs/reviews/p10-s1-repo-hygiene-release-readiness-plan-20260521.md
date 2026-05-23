# P10-S1 Repo Hygiene / Release Readiness Plan

- **Date**: 2026-05-21
- **Gate**: `P10-S1 repo hygiene and release readiness plan/review`
- **Role**: planning specialist only
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Previous planning input**: `docs/reviews/post-p9-follow-up-planning-20260521.md`
- **Current branch observed during planning**: `main`

## 1. Goal

把 P9 后的仓库卫生和发布就绪基础补齐到可 review、可 CI、可复现的状态，同时不改变基金分析产品行为。

本计划只允许处理仓库级发布基础设施：

- 增加明确 LICENSE。
- 增加 GitHub Actions CI，固定 Python 3.11，执行 ruff 和 pytest。
- 明确 `.gitignore` 与 artifact inclusion/exclusion policy。
- 收口默认路径定义，降低 UI / Service / Fund Capability 之间的重复常量。
- 明确当前两个未跟踪文件的处理方式。
- 同步 README 与测试手册。

Blocking prerequisite before implementation:

- P10-S1-A 不得开始写 `LICENSE`，直到 maintainer / controller 显式确认 MIT License 的 copyright holder legal name。`bill20232033cc` 只是根据 GitHub remote 推断出的候选值，不能在未确认时写入法律声明。

## 2. Non-Goals

- 不改 `fund-analysis analyze` 用户契约、quality gate 语义、最终判断派生、renderer 文案或基金分析规则。
- 不引入外部 Dayu runtime、Host、Engine、tool loop、prompt scene registry 或 LLM writing。
- 不重写 `docs/implementation-control.md` 结构。
- 不修 RR-13 / `docs/code_20260519.csv` 中 `016492` 重复；该项继续 human-owned。
- 不删除当前未跟踪 `.docx` 文件。
- 不提交 runtime cache、snapshot run、quality gate run 或本地自动化辅助文件。
- 不启用、读取或清理 `fund_agent/config/prompts/` 下的 prompt skeleton；P10-S1 只文档化它当前不参与生产主链路。

## 3. Direct Evidence

Planning preflight observed:

- `git branch --show-current` -> `main`
- `git status --short` shows only:
  - `?? docs/fund-agent_仓库级综合审核报告_2026-05-21.docx`
  - `?? docs/reviews/code-review-p8-s3-ds-20260521.md`
- No `.github/workflows` directory exists.
- No `LICENSE*` file is tracked.
- `pyproject.toml` requires Python `>=3.11`, has dev dependencies `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, and `uv.lock` is tracked.
- `fund_agent/config/prompts/{base,scenes,tasks}` exists locally as prompt skeleton directories, but current design truth says production main path has no prompt manifest / scene registry runtime.
- Current `.gitignore` already ignores `cache/`, `reports/extraction-snapshots/`, `reports/quality-gate-runs/`, `report-*.md`, `.venv/`, `.claude/`, and local tmux / launchd helper scripts.
- Curated default artifacts are tracked:
  - `docs/code_20260519.csv`
  - `docs/golden-answer-template.md`
  - `reports/golden-answers/golden-answer-prefill.md`
  - `reports/golden-answers/golden-answer-prefill-reviewed.md`
  - `reports/golden-answers/golden-answer.json`
- Default paths are currently duplicated across `fund_agent/ui/cli.py`, `fund_agent/services/fund_analysis_service.py`, and multiple `fund_agent/fund/*` modules.

## 4. Implementation Decisions

### 4.1 LICENSE

Decision: add a root `LICENSE` file using the MIT License.

Exact strategy:

- File: `LICENSE`
- Copyright line:
  - `Copyright (c) 2026 <confirmed copyright holder>`
- Do not add per-file license headers.
- Update `pyproject.toml` `[project]` with `license = "MIT"` after the holder is confirmed. This is package metadata only; it must not change dependencies, build backend, version, scripts, or runtime behavior.

Reasoning:

- The repository is hosted under `https://github.com/bill20232033cc/fund-agent.git`.
- The project currently has no license declaration, which makes external review and reuse ambiguous.
- MIT is a minimal permissive default and does not require code behavior changes.
- Adding the `pyproject.toml` license field keeps package metadata aligned with the root `LICENSE` file; P10-S1 still does not add PyPI publishing or release automation.

Holder confirmation gate:

- Before Slice P10-S1-A implementation starts, ask the maintainer / controller for the exact copyright holder string.
- If the holder is confirmed as `bill20232033cc`, use that exact string.
- If a legal personal name or organization is provided, use that exact string.
- If no holder is confirmed, stop; do not add `LICENSE` or `pyproject.toml` license metadata.

### 4.2 CI

Decision: add one GitHub Actions workflow for Python 3.11.

Exact file:

- `.github/workflows/ci.yml`

Workflow shape:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --extra dev --frozen
      - run: uv run ruff check .
      - run: uv run pytest -q
```

Rules:

- Use `uv.lock` because it is already tracked.
- Do not add matrix versions in P10-S1; Python 3.11 is the release readiness baseline.
- Do not add network smoke tests to CI.
- Do not run `fund-analysis analyze` against real PDF/network sources in CI.

### 4.3 Artifact Policy

Decision: keep release fixtures tracked, keep generated runtime outputs ignored.

Tracked by policy:

- Source and design docs under `docs/*.md`.
- Review artifacts under `docs/reviews/*.md`.
- Curated selected fund CSV: `docs/code_20260519.csv`.
- Golden answer template: `docs/golden-answer-template.md`.
- Curated golden answer files:
  - `reports/golden-answers/golden-answer-prefill.md`
  - `reports/golden-answers/golden-answer-prefill-reviewed.md`
  - `reports/golden-answers/golden-answer.json`

Ignored by policy:

- Runtime caches: `cache/`.
- Generated extraction snapshots: `reports/extraction-snapshots/`.
- Generated quality gate runs: `reports/quality-gate-runs/`.
- One-off rendered reports: `report-*.md`.
- Local virtualenv, Python caches, pytest/ruff caches, build outputs.
- Binary source audit documents under `docs/*.docx`.
- Local tmux / launchd helper scripts already listed in `.gitignore`.

`.gitignore` update requirements:

- Keep existing generated-output entries.
- Add release hygiene entries:
  - `.pytest_cache/`
  - `.ruff_cache/`
  - `.coverage`
  - `htmlcov/`
  - `dist/`
  - `build/`
  - `*.egg-info/`
  - `docs/*.docx`
- Keep generated reports ignores narrowly scoped to `reports/extraction-snapshots/` and `reports/quality-gate-runs/`.
- Add a short comment near those entries: `reports/golden-answers/` contains curated golden answer fixtures and is intentionally outside the generated-output ignore rules. Do not add a broad `reports/` ignore.

### 4.4 Default Path Policy

Decision: introduce a small static path-defaults config module.

This is not a runtime config system. It must not read environment variables, workspace config files, prompt manifests, Dayu config, Host config, or Engine config.

New file:

- `fund_agent/config/paths.py`

`fund_agent/config/` scope:

- `fund_agent/config/paths.py` is the only new public surface in P10-S1.
- `fund_agent/config/__init__.py` must remain empty or contain only a package-level Chinese docstring. It must not re-export `paths` constants and must not define `__all__`.
- Existing `fund_agent/config/prompts/{base,scenes,tasks}` directories are not part of P10-S1 implementation. Do not delete them, do not add prompt files, and do not make production code read from them.
- `fund_agent/config/README.md` must state that prompt skeleton directories, if present locally, are inert placeholders and do not represent a production prompt manifest, scene registry, Host, Engine, or Dayu runtime.

Allowed API:

```python
from pathlib import Path
from typing import Final

DEFAULT_SELECTED_FUNDS_CSV: Final[Path] = Path("docs/code_20260519.csv")
DEFAULT_GOLDEN_TEMPLATE_PATH: Final[Path] = Path("docs/golden-answer-template.md")
DEFAULT_GOLDEN_PREFILL_OUTPUT: Final[Path] = Path(
    "reports/golden-answers/golden-answer-prefill.md"
)
DEFAULT_GOLDEN_REVIEWED_MARKDOWN: Final[Path] = Path(
    "reports/golden-answers/golden-answer-prefill-reviewed.md"
)
DEFAULT_GOLDEN_ANSWER_JSON: Final[Path] = Path(
    "reports/golden-answers/golden-answer.json"
)
DEFAULT_EXTRACTION_SNAPSHOT_ROOT: Final[Path] = Path("reports/extraction-snapshots")
DEFAULT_QUALITY_GATE_OUTPUT_ROOT: Final[Path] = Path("reports/quality-gate-runs")
DEFAULT_CACHE_ROOT: Final[Path] = Path("cache")
DEFAULT_DOCUMENT_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "documents"
DEFAULT_PDF_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "pdf"
DEFAULT_NAV_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "nav"
DEFAULT_THERMOMETER_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "thermometer"
```

Import migration rules:

- Existing module-level constant names must remain as aliases when external call sites or tests may import them. Aliases must point to `fund_agent.config.paths`; do not keep independent `Path("...")` definitions except the explicitly excluded CLI historical score path below.
- `fund_agent/config/paths.py` must not import from UI, Service, Fund Capability, Engine, or Runtime.
- UI, Service, and Fund Capability may import these static path constants.
- Explicit CLI / Service parameters remain authoritative over defaults.
- No behavior should change when no explicit path option is provided.
- `fund_agent/ui/cli.py::DEFAULT_QUALITY_GATE_SCORE` is excluded from `config.paths`: it points to one historical P4 controller score file used as the CLI default for the standalone `quality-gate` helper command, not a repository-wide default root. Keep it as a CLI-local constant, add a short comment naming it as a historical score fixture path, and do not move it to `config.paths`.

Exact existing-constant migration table:

| Current file | Current constant | Current value | `config.paths` source | Required migration |
|--------------|------------------|---------------|------------------------|--------------------|
| `fund_agent/ui/cli.py` | `DEFAULT_SELECTED_FUNDS_CSV` | `docs/code_20260519.csv` | `DEFAULT_SELECTED_FUNDS_CSV` | import directly; no local `Path(...)` |
| `fund_agent/ui/cli.py` | `DEFAULT_GOLDEN_TEMPLATE` | `docs/golden-answer-template.md` | `DEFAULT_GOLDEN_TEMPLATE_PATH` | keep alias `DEFAULT_GOLDEN_TEMPLATE = DEFAULT_GOLDEN_TEMPLATE_PATH` |
| `fund_agent/ui/cli.py` | `DEFAULT_GOLDEN_PREFILL_OUTPUT` | `reports/golden-answers/golden-answer-prefill.md` | `DEFAULT_GOLDEN_PREFILL_OUTPUT` | import directly; no local `Path(...)` |
| `fund_agent/ui/cli.py` | `DEFAULT_GOLDEN_ANSWER_OUTPUT` | `reports/golden-answers/golden-answer.json` | `DEFAULT_GOLDEN_ANSWER_JSON` | keep alias `DEFAULT_GOLDEN_ANSWER_OUTPUT = DEFAULT_GOLDEN_ANSWER_JSON` |
| `fund_agent/ui/cli.py` | `DEFAULT_QUALITY_GATE_SCORE` | `reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json` | none | keep CLI-local, with comment; excluded from config |
| `fund_agent/services/fund_analysis_service.py` | `DEFAULT_GOLDEN_ANSWER_PATH` | `reports/golden-answers/golden-answer.json` | `DEFAULT_GOLDEN_ANSWER_JSON` | keep alias `DEFAULT_GOLDEN_ANSWER_PATH = DEFAULT_GOLDEN_ANSWER_JSON` |
| `fund_agent/fund/extraction_snapshot.py` | `DEFAULT_SELECTED_FUNDS_CSV` | `docs/code_20260519.csv` | `DEFAULT_SELECTED_FUNDS_CSV` | import/re-export existing name |
| `fund_agent/fund/extraction_snapshot.py` | `DEFAULT_SNAPSHOT_OUTPUT_ROOT` | `reports/extraction-snapshots` | `DEFAULT_EXTRACTION_SNAPSHOT_ROOT` | keep alias `DEFAULT_SNAPSHOT_OUTPUT_ROOT = DEFAULT_EXTRACTION_SNAPSHOT_ROOT` |
| `fund_agent/fund/golden_prefill.py` | `DEFAULT_GOLDEN_TEMPLATE_PATH` | `docs/golden-answer-template.md` | `DEFAULT_GOLDEN_TEMPLATE_PATH` | import/re-export existing name |
| `fund_agent/fund/golden_prefill.py` | `DEFAULT_GOLDEN_PREFILL_OUTPUT` | `reports/golden-answers/golden-answer-prefill.md` | `DEFAULT_GOLDEN_PREFILL_OUTPUT` | import/re-export existing name |
| `fund_agent/fund/golden_answer.py` | `DEFAULT_GOLDEN_REVIEWED_MARKDOWN` | `reports/golden-answers/golden-answer-prefill-reviewed.md` | `DEFAULT_GOLDEN_REVIEWED_MARKDOWN` | import/re-export existing name |
| `fund_agent/fund/golden_answer.py` | `DEFAULT_GOLDEN_ANSWER_JSON` | `reports/golden-answers/golden-answer.json` | `DEFAULT_GOLDEN_ANSWER_JSON` | import/re-export existing name |
| `fund_agent/fund/quality_gate_integration.py` | `DEFAULT_QUALITY_GATE_OUTPUT_ROOT` | `reports/quality-gate-runs` | `DEFAULT_QUALITY_GATE_OUTPUT_ROOT` | import/re-export existing name |
| `fund_agent/fund/documents/cache.py` | `DOCUMENT_CACHE_ROOT` | `cache/documents` | `DEFAULT_DOCUMENT_CACHE_ROOT` | keep alias `DOCUMENT_CACHE_ROOT = DEFAULT_DOCUMENT_CACHE_ROOT` |
| `fund_agent/fund/pdf/downloader.py` | `DEFAULT_CACHE_DIR` | `cache/pdf` | `DEFAULT_PDF_CACHE_ROOT` | keep alias `DEFAULT_CACHE_DIR = DEFAULT_PDF_CACHE_ROOT` |
| `fund_agent/fund/documents/sources.py` | imported `DEFAULT_CACHE_DIR` from downloader | `cache/pdf` via downloader | no direct config import required | no direct edit required unless ruff import cleanup requires it; preserving downloader alias is acceptable |
| `fund_agent/fund/data/nav_data.py` | `NAV_CACHE_ROOT` | `cache/nav` | `DEFAULT_NAV_CACHE_ROOT` | keep alias `NAV_CACHE_ROOT = DEFAULT_NAV_CACHE_ROOT` |
| `fund_agent/fund/data/thermometer.py` | `THERMOMETER_CACHE_ROOT` | `cache/thermometer` | `DEFAULT_THERMOMETER_CACHE_ROOT` | keep alias `THERMOMETER_CACHE_ROOT = DEFAULT_THERMOMETER_CACHE_ROOT` |
| `fund_agent/fund/extraction_score.py` | none | none | none | no-op verification only; do not edit solely for paths |

Files expected to consume the new module:

- `fund_agent/ui/cli.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/golden_prefill.py`
- `fund_agent/fund/golden_answer.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/pdf/downloader.py`
- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/thermometer.py`

No-op / indirect verification files:

- `fund_agent/fund/extraction_score.py`: verify there is no path default to migrate.
- `fund_agent/fund/documents/sources.py`: verify existing downloader-level `DEFAULT_CACHE_DIR` alias still supplies the same `cache/pdf` default.

### 4.5 Current Untracked Files

Decision for `docs/reviews/code-review-p8-s3-ds-20260521.md`:

- Treat it as a durable review artifact.
- Include it in the P10-S1 implementation commit, but do not edit its content unless `git diff --check` fails on that file.
- Reason: `docs/reviews/*.md` is the established review artifact location, and this file closes prior P8-S3 review record hygiene.

Decision for `docs/fund-agent_仓库级综合审核报告_2026-05-21.docx`:

- Do not commit it.
- Do not delete it.
- Add `docs/*.docx` to `.gitignore` so binary source audit inputs stay local unless explicitly converted to Markdown and accepted as a review artifact.
- If future source audit documents must be tracked, they should be converted to Markdown under `docs/reviews/` with provenance noted.

## 5. File Ownership

### Release / Repo Hygiene

Allowed files:

- `LICENSE`
- `.github/workflows/ci.yml`
- `.gitignore`
- `pyproject.toml` only for `[project].license = "MIT"` after holder confirmation
- `docs/reviews/code-review-p8-s3-ds-20260521.md`

### Config Path Defaults

Allowed files:

- `fund_agent/config/paths.py`
- `fund_agent/config/__init__.py` only if keeping it empty or adding a package-level Chinese docstring; no re-exports
- `fund_agent/config/README.md`
- path default imports in the modules listed in section 4.4
- no-op verification only for `fund_agent/fund/extraction_score.py` and `fund_agent/fund/documents/sources.py`

### Tests

Allowed files:

- `tests/config/test_paths.py`
- `tests/test_repo_hygiene.py`
- Existing tests that assert default paths, only if they need import-path updates.
- `tests/README.md`

### Documentation

Allowed files:

- `README.md`
- `fund_agent/README.md`
- `fund_agent/config/README.md`
- `tests/README.md`

Do not modify:

- `docs/implementation-control.md`
- `docs/design.md`
- `docs/code_20260519.csv`
- Fund analysis template files
- analysis / audit / renderer behavior modules except static path import migration listed above

## 6. Implementation Slices

### Slice P10-S1-A: License, CI, Ignore Policy

Objective:

- Add release-readiness skeleton without touching product code.

Allowed changes:

- After maintainer / controller holder confirmation, add `LICENSE` with MIT text and the confirmed holder string.
- Add `license = "MIT"` to `pyproject.toml` `[project]`; do not touch any other package metadata.
- Add `.github/workflows/ci.yml` exactly following section 4.2.
- Update `.gitignore` using section 4.3.
- Add `tests/test_repo_hygiene.py` assertions for:
  - `LICENSE` exists and contains `MIT License`.
  - `pyproject.toml` declares project license `MIT`.
  - CI workflow exists and includes Python `3.11`, `uv sync --extra dev --frozen`, `uv run ruff check .`, and `uv run pytest -q`.
  - `.gitignore` contains generated-output and docx ignore entries.
  - `.gitignore` does not contain a broad `reports/` ignore and keeps `reports/golden-answers/` outside generated-output ignores.
  - `reports/quality-gate-runs/`, `reports/extraction-snapshots/`, and `cache/` are ignored by policy.

Non-goals:

- Do not add packaging/release publish workflow.
- Do not add test coverage thresholds in CI.

Validation:

```bash
uv lock --check
uv run pytest tests/test_repo_hygiene.py -q
uv run ruff check .
git diff --check
```

Completion signal:

- Holder confirmation is recorded in the implementation report.
- Repo hygiene test passes and no product behavior files are modified in this slice.

### Slice P10-S1-B: Static Path Defaults Config

Objective:

- Centralize repository default paths without changing runtime behavior.

Allowed changes:

- Add `fund_agent/config/paths.py` with constants from section 4.4.
- Update imports in the listed UI / Service / Fund modules following the exact alias migration table.
- Keep existing module-level exported constant names as aliases exactly where section 4.4 says to keep aliases.
- Keep `fund_agent/ui/cli.py::DEFAULT_QUALITY_GATE_SCORE` as a CLI-local historical score path, with a short comment; do not move it to `config.paths`.
- Verify `fund_agent/fund/extraction_score.py` has no path default migration and do not edit it solely for P10-S1-B.
- Keep `fund_agent/fund/documents/sources.py` on the downloader alias unless a direct import is needed for ruff; behavior must remain `cache/pdf`.
- Keep `fund_agent/config/__init__.py` empty or docstring-only; no re-export star imports.
- Add `tests/config/test_paths.py` to assert:
  - every default path is relative, not absolute;
  - selected CSV, golden template, golden answer, report roots, and cache roots match current documented defaults;
  - `fund_agent.config.paths` imports without importing UI or Service modules.
  - each current alias in the migration table is object-equal or value-equal to its `config.paths` source;
  - `DEFAULT_QUALITY_GATE_SCORE` remains defined only in `fund_agent.ui.cli` and equals the historical P4 score path;
  - `fund_agent/fund/extraction_score.py` has no module-level repository path default to migrate;
  - no UI / Service / Fund module outside the approved alias table defines a new module-level `Path("docs/...")`, `Path("reports/...")`, or `Path("cache/...")` default;
  - `fund_agent/config/__init__.py` does not re-export path constants.

Non-goals:

- No env var override.
- No workspace config discovery.
- No dataclass settings loader.
- No Dayu / Host / Engine config.

Validation:

```bash
uv run pytest tests/config/test_paths.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate_integration.py tests/fund/test_golden_answer.py tests/fund/documents tests/fund/pdf tests/fund/data -q
uv run ruff check .
git diff --check
```

Expected assertions:

- Existing CLI default path assertions still pass.
- Service still supplies selected CSV and golden answer defaults in product mode.
- Cache defaults remain `cache/documents`, `cache/pdf`, `cache/nav`, and `cache/thermometer`.
- `rg -n '= Path\\("docs/|= Path\\("reports/|= Path\\("cache/' fund_agent/ui fund_agent/services fund_agent/fund` shows no new independent default definitions outside `fund_agent/config/paths.py` and the explicitly excluded CLI historical score path.

### Slice P10-S1-C: Artifact Handling And Existing Untracked Files

Objective:

- Resolve current untracked-file policy without losing evidence.

Allowed changes:

- Stage `docs/reviews/code-review-p8-s3-ds-20260521.md` as-is.
- Leave `docs/fund-agent_仓库级综合审核报告_2026-05-21.docx` untracked and ignored by `.gitignore`.
- Add repo hygiene test coverage that `docs/*.docx` is ignored by policy.

Non-goals:

- Do not inspect or rewrite the `.docx`.
- Do not convert it to Markdown in this slice.
- Do not remove local binary files.

Validation:

```bash
git status --short
git check-ignore "docs/fund-agent_仓库级综合审核报告_2026-05-21.docx"
git diff --check -- docs/reviews/code-review-p8-s3-ds-20260521.md
```

Expected status after implementation:

- `docs/reviews/code-review-p8-s3-ds-20260521.md` appears as tracked/staged when committing P10-S1.
- The `.docx` does not appear in `git status --short` once `.gitignore` is active.

### Slice P10-S1-D: Documentation And Final Validation

Objective:

- Make the repo hygiene policy visible to users and developers.

Allowed documentation updates:

- `README.md`
  - Add license mention.
  - Add CI validation commands.
  - Add concise artifact policy: curated golden fixtures are tracked; generated snapshots, quality gate runs, reports, and cache are ignored.
- `fund_agent/README.md`
  - Add one sentence that `fund_agent/config/paths.py` owns static repository path defaults and does not represent a Host/Engine runtime.
- `fund_agent/config/README.md`
  - Document current config package responsibility: static default paths only.
  - Explicitly state no workspace override, env override, Dayu runtime, prompt scene registry, or tool loop config exists in P10.
  - Explicitly state `fund_agent/config/prompts/{base,scenes,tasks}` is inert in current production code if present; production code must not read it in P10-S1.
- `tests/README.md`
  - Add CI command set and repo hygiene tests.
  - Note generated-output policy for tests that produce report artifacts.
  - Document that `tests/config/test_paths.py` is the migration guard for repository path defaults.

Non-goals:

- Do not update `docs/implementation-control.md`.
- Do not add changelog or time-sensitive release notes.

Validation:

```bash
uv run pytest -q
uv run ruff check .
git diff --check
git status --short
```

Expected final status:

- Only P10-S1 files and the accepted P8-S3 review artifact are modified/tracked.
- The `.docx` source audit input is ignored and not staged.
- Full test suite passes.

## 7. Contract / Schema / Public Interface Impact

- Public CLI behavior: no change.
- Fund analysis behavior: no change.
- Quality gate semantics: no change.
- Cache behavior: no change in path values or invalidation behavior.
- New import surface: `fund_agent.config.paths`.
- `fund_agent.config.__init__` is not a public re-export surface in P10-S1.
- `fund_agent/config/prompts/` remains inert and outside the production runtime.
- No data schema changes.
- No state-machine changes.
- No service request/response contract changes.

## 8. Risks

| Risk | Mitigation |
|------|------------|
| MIT copyright holder may be legally incorrect | Block implementation until maintainer / controller explicitly confirms the exact holder string |
| Path-default config could become an accidental runtime config system | Keep constants only; no env/workspace/Dayu/Host/Engine loading |
| Moving constants may create import cycles | `fund_agent.config.paths` must import only `pathlib.Path` and `typing.Final`; tests assert import isolation |
| Alias migration may leave duplicate independent `Path(...)` defaults | Follow the migration table and add `tests/config/test_paths.py` guard scanning UI / Service / Fund modules |
| `DEFAULT_QUALITY_GATE_SCORE` may be mistaken for a repository-wide default | Keep it CLI-local as a documented historical score path and exclude it from `config.paths` |
| `fund_agent/fund/extraction_score.py` may receive unnecessary churn | Treat it as no-op verification only |
| Golden answer files live under `reports/`, which is otherwise generated-output territory | Keep ignores narrowly scoped to generated subdirs; do not add broad `reports/` ignore |
| `config/prompts/` skeleton may confuse config package scope | Document it as inert and out of P10-S1 production scope; no code may read it |
| CI full pytest may be slower than local targeted runs | Accept for release readiness; do not add network smoke tests |
| `.docx` ignore could hide future intentionally tracked Word docs | Policy says durable artifacts should be Markdown under `docs/reviews/`; future exceptions require explicit scope decision |

## 9. Review Checklist

Reviewers should verify:

- The implementation report records explicit holder confirmation before `LICENSE` was added.
- `LICENSE` exists and uses the confirmed MIT holder string.
- `pyproject.toml` declares `license = "MIT"` and does not include unrelated package metadata churn.
- CI runs Python 3.11, installs with `uv sync --extra dev --frozen`, and executes both `uv run ruff check .` and `uv run pytest -q`.
- `.gitignore` ignores generated outputs and binary source audit docs, does not contain a broad `reports/` ignore, and does not ignore curated golden answer fixtures.
- `docs/reviews/code-review-p8-s3-ds-20260521.md` is tracked as a durable review artifact.
- The `.docx` file is not staged or committed.
- `docs/code_20260519.csv` is unchanged; RR-13 remains human-owned.
- `fund_agent.config.paths` contains static path constants only.
- `fund_agent/config/__init__.py` remains empty or docstring-only and does not re-export path constants.
- `fund_agent/config/README.md` documents static path defaults and inert prompt skeleton scope.
- UI / Service / Fund modules preserve the same default path values after import migration, following the exact alias table.
- `DEFAULT_QUALITY_GATE_SCORE` remains CLI-local and documented as a historical score path.
- `fund_agent/fund/extraction_score.py` has no path migration churn.
- `tests/config/test_paths.py` covers every path consumer, alias, CLI historical score exclusion, import isolation, and migration guard.
- No Dayu / Host / Engine / prompt registry runtime is introduced.
- No product CLI, analysis, renderer, audit, or quality gate behavior changes are introduced.
- README updates describe current behavior only and do not advertise future config features.
- `uv lock --check`, `uv run pytest -q`, `uv run ruff check .`, and `git diff --check` pass.

## 10. Completion Report Format

Implementation agent should report:

- Files changed by slice.
- The confirmed LICENSE copyright holder string.
- Whether `LICENSE`, CI, `.gitignore`, path defaults, docs, and tests were completed.
- Validation commands and results.
- Confirmation that `.docx` remains untracked/ignored and not committed.
- Confirmation that `docs/code_20260519.csv`, `docs/implementation-control.md`, and `fund_agent/fund/extraction_score.py` were not modified.
- Confirmation that `DEFAULT_QUALITY_GATE_SCORE` remains CLI-local and excluded from `config.paths`.
- Residual risks, if any.
