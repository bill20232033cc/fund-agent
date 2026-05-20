# Post-P7 Follow-up Planning

## Scope

- Trigger: repo-level `deepreview --all` completed with no remaining blocking code issues.
- Current HEAD before this planning update: `58bba13 Fix repo deepreview cache and gate findings`.
- Planning date: 2026-05-21 Asia/Shanghai.

## High-Priority Follow-ups

| Item | Priority | Current status | Next action |
|---|---:|---|---|
| `CLAUDE.md` describes the wrong project | P0 | Fixed in this follow-up. Rewritten from the old `zhixing` stock-agent guidance to current `fund-agent` commands, structure, layer boundaries, document-source behavior, quality gate semantics and testing guidance. | Verify no stale `zhixing`/ticker/yfinance/FastAPI references remain; commit as documentation cleanup. |
| Parsed report JSON cache crash loop | P0 | Already fixed in `58bba13`. `AnnualReportDocumentCache._load_parsed_report_sync()` treats corrupt/non-object payloads and invalid model payloads as cache miss. | Keep covered by `tests/fund/documents/test_cache.py::test_cache_returns_none_for_corrupt_parsed_report_payload`. |
| PDF cache/data integrity | P1 | Already fixed in `58bba13`. EID and Eastmoney validate `%PDF-` cache hits and use atomic writes. | Keep covered by document source and downloader tests. |
| quality gate `block + not_run` semantics | P1 | Already fixed in `58bba13`. CLI exits code 2 with `quality_gate_status: not_run`. | Keep covered by Service and UI tests. |

## Deferred Planning Queue

| Item | Rationale | Suggested owner |
|---|---|---|
| `docs/design.md` / `docs/implementation-control*.md` reconciliation | Repo review found design/control docs are stale against current code facts. This should be a dedicated design-control-code reconciliation artifact rather than incidental edits. | Controller with reviewer support |
| Compound fund type semantics (`QDII`/`FOF` + index/enhanced identity) | Requires preferred_lens/domain decision: compound type, basis-only evidence, or precedence rule. | Capability design pass |
| `share_change` A-class fallback | Existing tests intentionally avoid defaulting to A class without evidence. Needs fixture-backed domain rule if changed. | Capability extractor pass |
| `judge_alpha_nature(())` empty observations | Quality gap, not crash risk. Needs mapping from `holdings_snapshot` / alpha observations into the existing alpha judgment contract. | Analysis capability pass |
| Repository concurrency / TOCTOU retry | Larger document repository design change; not needed for current post-P7 acceptance. | Document repository pass |
| `AGENTS.md` cleanup | Current file is mostly accurate. User marked Codex update as non-urgent. | Later documentation pass |

## Verification Plan

After `CLAUDE.md` cleanup:

```bash
rg "zhixing|ticker|600519|yfinance|DeepSeek|Obsidian|flomo|NoNotes|FastAPI|zhixing/" CLAUDE.md
pytest
```

Expected:

- `rg` returns no stale old-project references.
- Full test suite remains green.

Actual:

- `rg` returned no stale old-project references.
- `pytest` passed: `299 passed in 0.73s`.
