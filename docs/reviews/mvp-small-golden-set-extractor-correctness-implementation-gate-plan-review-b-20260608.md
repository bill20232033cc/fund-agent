# Small Golden Set / Extractor Correctness Implementation Gate Plan Review B

Verdict: `BLOCKED`.

## Findings

- `[high] [B1]` `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md:131` - Slice C only allowed changes under `fund_agent/fund/extractors/`, but same-source failures may be in `FundDataExtractor` orchestration or fund-type classification. Minimal fix: expand allowed repair scope to the smallest proven Fund extraction-chain module, including `fund_agent/fund/extractors/`, `fund_agent/fund/data_extractor.py` and `fund_agent/fund/fund_type.py`, with matching regression tests.
- `[high] [B2]` `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md:189` - Promotion boundary verification is unreliable. The glob can fail under zsh `nomatch`, and `git diff --name-only HEAD -- ...` misses untracked production golden/readiness files. Minimal fix: use `git status --short -- reports/golden-answers reports/golden-readiness-preflight docs/reviews`, and add a separate promotion-signal check for `promotion_allowed=true` and `fixture-promotion`.
- `[medium] [B3]` `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md:107` - Slice B may add a new fixture directory but did not allow `tests/README.md` until Slice C. This conflicts with the repo rule that tests changes require README sync. Minimal fix: add `tests/README.md` to Slice B allowed files and require it to record the new fixture directory, offline constraint and focused pytest command.
- `[high] [B4]` `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md:116` - Synthetic fixture handling is not closed. The plan says synthetic fixtures cannot satisfy source identity alone, but Slice C allowed source identity from offline fixture metadata. Minimal fix: add `fixture_source_kind` to the manifest/expected fields and state that only real minimal excerpts plus matched source identity may drive exact/numeric correctness. Synthetic fixtures can only test parser mechanics.

## Open Questions

None.
