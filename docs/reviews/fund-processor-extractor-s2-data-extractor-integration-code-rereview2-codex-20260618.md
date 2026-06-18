# Fund Processor/Extractor S2 DataExtractor Integration - Code Re-review 2 (AgentCodex)

> Date: 2026-06-18
> Role: AgentCodex independent code re-reviewer
> Gate: S2 code re-review gate, round 2 after fix2
> Verdict: PASS_NOT_READY

## Scope

- Mode: current changes, targeted S2 code re-review after fix2
- Branch or PR: `post-merge/pr22-origin-main`
- Base: current workspace diff and accepted S2 review/fix artifacts; no PR metadata inspected
- Output file: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-rereview2-codex-20260618.md`
- Included scope:
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-rereview-codex-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix2-evidence-20260618.md`
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/test_data_extractor.py`
  - `fund_agent/fund/README.md`
  - `fund_agent/fund/processors/contracts.py`
  - `fund_agent/fund/processors/registry.py`
  - `fund_agent/fund/processors/active_annual.py`
- Excluded scope:
  - No live/source/PDF/FDR/Docling conversion/provider/LLM/analyze/checklist/golden/readiness/release commands.
  - Unrelated untracked residue was not reviewed or classified.
  - Repository-wide stale documentation outside `fund_agent/fund/README.md` was not treated as this fix2 write-set scope.
- Parallel review coverage: 无 subagent；main reviewer covered the accepted blocking identity/NAV order finding, processor result identity mismatch test, Fund README sync, candidate/parser boundary scan, forbidden write-set scan, focused no-live tests, ruff, and whitespace check.

## Findings

未发现实质性问题。

## Accepted Finding Verification

- Repository/report mismatch before NAV: closed. `FundDataExtractor.extract()` loads the report at `fund_agent/fund/data_extractor.py:303-307`, checks `report.key.fund_code != fund_code or report.key.year != report_year` at `fund_agent/fund/data_extractor.py:308-312`, and only then calls `_load_nav_data_or_unavailable()` at `fund_agent/fund/data_extractor.py:313-317`. Therefore a report fund code or year mismatch raises before NAV provider access and before processor dispatch.
- Required NAV no-call assertion: present. `tests/fund/test_data_extractor.py:879-900` uses a repository returning fund `110011`, calls `extract("999999", 2024)`, expects `RuntimeError("Report identity mismatch")`, and asserts `nav_provider.calls == []`.
- Processor result identity mismatch test: preserved. `tests/fund/test_data_extractor.py:863-876` still registers `_MismatchedIdentityProcessor`, calls `extract("110011", 2024)`, and expects `RuntimeError("Processor result identity mismatch")`.
- Processor identity validator remains on the active path. `_extract_active_fund_via_processor()` validates `FundProcessorResult` against the dispatch key at `fund_agent/fund/data_extractor.py:384`; `_validate_processor_result_identity()` checks fund code, report year, fund type, report type, and intermediate kind at `fund_agent/fund/data_extractor.py:511-554`.
- README sync remains correct for this write set. `fund_agent/fund/README.md:77` states S2 active fund annual `ParsedAnnualReport` now routes through `FundProcessorRegistry` / `ActiveFundAnnualProcessor` and keeps non-active/unclassified as S2 residual direct legacy path. `fund_agent/fund/README.md:111` says active fund covered fields come from processor output and keeps the no direct file/cache write boundary.
- Candidate/parser boundary: no new blocking crossing found. `fund_agent/fund/data_extractor.py` imports and consumes `ParsedAnnualReport`, processor contracts, registry, existing narrow extractors, NAV data, and source provenance; it does not import Docling, candidate representation modules, PDF cache/source helpers, Service, Host, renderer, quality gate, LLM, or `extra_payload`.
- Forbidden write-set expansion: no staged files and the targeted diff name-only scan returned only `fund_agent/fund/README.md`, `fund_agent/fund/data_extractor.py`, and `tests/fund/test_data_extractor.py`.

## Open Questions

- 无。

## Residual Risk

- Verdict remains `PASS_NOT_READY` because this is a local code re-review gate only. It does not prove parser replacement, source truth, golden/readiness, release readiness, or live provider behavior.
- The new mismatch test exercises fund-code mismatch and asserts NAV was not called. The code also checks report-year mismatch in the same pre-NAV condition, but there is no separate year-only regression test in this fix2 scope.
- Non-active processors remain unimplemented and the direct legacy path remains active for index/enhanced/bond/QDII/FOF/unclassified funds, as an S2 residual.
- `index_profile` still comes from bootstrap `extract_profile()` for active funds, as an accepted S2 residual.
- `_field_from_family()` still returns `ExtractedField[Any]`; retained as a nonblocking residual from the previous review chain.

## Commands Inspected/Run

```text
git branch --show-current
git status --short
sed -n '1,520p' /Users/maomao/.codex/skills/deepreview/SKILL.md
rg -n "Fund Processor|DataExtractor|Processor/Extractor|Extractor Architecture|S2" /Users/maomao/.codex/memories/MEMORY.md
sed -n '120,135p' /Users/maomao/.codex/memories/MEMORY.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-rereview-codex-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix2-evidence-20260618.md
git diff -- fund_agent/fund/data_extractor.py
git diff -- tests/fund/test_data_extractor.py
git diff -- fund_agent/fund/README.md
nl -ba fund_agent/fund/data_extractor.py | sed -n '260,690p'
nl -ba tests/fund/test_data_extractor.py | sed -n '1,120p'
nl -ba tests/fund/test_data_extractor.py | sed -n '628,930p'
nl -ba fund_agent/fund/README.md | sed -n '60,125p'
nl -ba fund_agent/fund/processors/contracts.py | sed -n '1,260p'
nl -ba fund_agent/fund/processors/registry.py | sed -n '1,220p'
nl -ba fund_agent/fund/processors/active_annual.py | sed -n '1,340p'
rg -n "extra_payload|FundDisclosureDocument|docling|Docling|candidate|pdfplumber|EID|service|host|renderer|quality" fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md
uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix2-evidence-20260618.md
git diff --name-only -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/documents/candidates fund_agent/service fund_agent/host fund_agent/agent fund_agent/render fund_agent/quality
git diff --cached --name-only
git diff --stat -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md
date +%Y-%m-%d
test -e docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-rereview2-codex-20260618.md
```

Observed verification:

```text
uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py -> 30 passed in 0.52s
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py -> All checks passed!
git diff --check ... -> no output
git diff --cached --name-only -> no output
target write-set name-only scan -> fund_agent/fund/README.md, fund_agent/fund/data_extractor.py, tests/fund/test_data_extractor.py
```
