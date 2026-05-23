# Pre-7AM Audit Reconciliation - 2026-05-21

## Reviewed Input

- `docs/fund-agent_仓库级综合审核报告_2026-05-21.docx`
- Note: the audit was based on the repository state before the morning 7:00 push, not current `main`.
- Current comparison HEAD at reconciliation time: `f65c14e chore: remove external dayu runtime dependency`

## Controller Judgment

The report is useful as a historical audit artifact, but it must not be applied directly to current HEAD. Several findings were closed by later commits; several remain real open risks; a few proposed fixes conflict with current architecture decisions.

## Finding Decisions

| ID | Audit finding | Current HEAD status | Decision | Next action |
|---|---|---|---|---|
| C1 | EID source uses plain HTTP | Still true: `EID_BASE_URL = "http://eid.csrc.gov.cn/fund"` | Accept risk, revise remedy | Validate HTTPS support first; if supported, switch to HTTPS. If not, keep explicit source-risk metadata and fail-closed identity/integrity checks. Do not claim fixed sha256 for dynamic PDFs. |
| C2 | `dayu-agent` direct GitHub wheel without integrity | Closed in `f65c14e` | Accept finding, reject proposed hash/vendor remedy | No further action in `pyproject.toml`; external Dayu runtime dependency removed. |
| C3 | `uv.lock` contains Dayu / torch / ML dependency chain | Still true in `uv.lock` | Accept | Regenerate or remove/recreate `uv.lock` so it matches current `pyproject.toml` without Dayu/ML deps. |
| C4 | `analyze` requires too many manual parameters | Still substantially true | Accept product issue, narrow scope | Split inputs into auto-extractable fields vs genuine user context. Do not force zero-parameter analysis for user-only facts such as time horizon and risk tolerance. |
| H1 | `CLAUDE.md` / `AGENTS.md` outdated | Partially stale | Accept partially | `CLAUDE.md` still mentions `dayu-agent`; `AGENTS.md` still has old `/workspace/...` and Runtime/Engine wording. Update to current design. |
| H2 | Missing `§6` / `§7` section catalog entries | Still true | Accept | Add §6/§7 as boundary sections to prevent §8+ extraction pollution, even if not analyzed directly. |
| H3 | Thermometer HTML scraping has legal/stability risk | Still true by design | Accept as residual, not blocker | Keep read-only/cache/unavailable behavior; document authorization risk; pursue official API or alternative source later. |
| H4 | Browser-like User-Agent for downloads | Partially true | Accept partially | Prefer explicit product UA, rate limiting and cache. Some UA may be operationally required; do not treat all UA use as inherently invalid. |
| H5 | Cache directories are relative paths | Still true for PDF/NAV/thermometer/document cache defaults | Accept | Move defaults to XDG/`~/.cache/fund-agent` or add central cache root configuration; keep tests using temp dirs. |
| H6 | `.gitignore` too small | Partially fixed | Accept remaining gap | Already ignores generated reports/local helpers. Still add `.env`, `*.env`, `*.sqlite3`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `build/`, `*.egg-info/`, `.coverage`, `htmlcov/`. Do not ignore tracked golden-answer fixtures wholesale. |
| M1 | `akshare` API instability and loose version bound | Still true | Accept | Add dependency strategy: upper bound or contract/smoke tests. Avoid freezing blindly without update path. |
| M2 | Ratio parsing ambiguity | Partially addressed | Accept narrow CLI/API issue | Current tests document numeric inputs as already-normalized and disclosure strings as percent-like. For CLI/user inputs, improve help text or require `%` for ambiguous whole percentages. |
| M3 | Forbidden investment-advice terms incomplete | Still true | Accept direction, avoid blacklist-only design | Expand high-risk terms, but also keep final-judgment contract and audit wording checks. Avoid overbroad substring false positives. |
| M4 | Section regexes fragile across real annual reports | Still true generally | Accept | Treat as ongoing extractor/parser quality risk; expand fixtures and section aliases based on observed failures. |
| M5 | Turnover cost rate `0.3%` hardcoded | Still true | Accept | Make transaction-cost assumption explicit/configurable and consider fund-type-specific defaults. |
| M6 | No CI configuration | Still true | Accept | Add GitHub Actions for `ruff` and `pytest`; keep network/PDF smoke opt-in. |
| M7 | EID search only fetches first 20 records | Still true | Accept | Add pagination or larger bounded search with tests to avoid not-found false negatives. |
| M8 | Final judgment passed by user | Still true | Accept product issue | Derive default final judgment from checklist/risk outputs; keep explicit override only as dev/user override with clear labeling. |
| L1 | Consistency check keyword matching is shallow | True but expected MVP limitation | Defer | Document limitation and improve only when evidence-backed cases show unacceptable false positives/negatives. |
| L2 | Logging configuration missing | Still true | Accept | Add CLI `--verbose` / `--log-level` and central logging setup. |
| L3 | `docs/implementation-control.md` too large | Still true | Accept as doc hygiene | Split or summarize only with recovery-preserving archive policy; do not delete phaseflow evidence. |
| L4 | Golden Answer Markdown parsing format-sensitive | True but controlled workflow | Defer | Consider form/JSON editing flow later; current strict parser is acceptable for controlled artifacts. |
| L5 | `tests/README.md` incomplete | Mostly stale | Reject as current finding | Current `tests/README.md` includes `tests/fund/integration` and the major test layers. Keep normal doc maintenance only. |

## Priority After Current-HEAD Reconciliation

1. Regenerate `uv.lock` after removing `dayu-agent`.
2. Update `CLAUDE.md` / `AGENTS.md` to current no-external-Dayu architecture and repo-relative paths.
3. Add §6/§7 section catalog boundary entries with parser tests.
4. Expand `.gitignore` and add CI.
5. Plan product-contract slice for `analyze` inputs and derived final judgment.

## Rejected Remedies

- Do not vendor or hash-lock `dayu-agent`; the architecture decision is to remove the external dependency and internalize any future runtime capability.
- Do not ignore all `reports/`; generated report runs are ignored, but tracked golden-answer fixtures are part of the quality gate baseline.
- Do not promise fully zero-parameter `analyze`; user-specific risk tolerance, time horizon and override inputs remain explicit unless a same-source derivation exists.
