# Source-like residue ownership / non-impact disposition startup judgment

Date: 2026-06-10

## Controller startup judgment

Gate: `source-like residue ownership / non-impact disposition gate`

Classification: `standard`

Reason: this gate does not change product behavior, source code, tests, runtime config, source policy, extractor behavior, fixture projection, release state, or external state. It does affect whether the next `EID Single Source Operational Implementation Planning Gate` can proceed without relying on source-like untracked workspace residue.

## Live control truth

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Branch state: ahead of `origin/feat/mvp-llm-incomplete-run-artifacts` by 31 commits.
- Tracked diff: clean.
- Untracked residue remains present.
- Current accepted steering: `EID Single Source Operational Hardening Gate` truth-doc steering accepted as future implementation direction, not code fact.
- Current source policy target: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- Eastmoney, fund-company official website/CDN, CNINFO and other non-EID routes remain deferred candidates or historical evidence-intake routes only, not current production fallback.
- `row-shape contract decision gate` remains queued / paused by steering.

## Scope

This gate only classifies the source-like untracked paths identified by the prior Post-EID artifact disposition gate:

- `fund_agent/tools/`
- `scripts/claude_mimo_simple.py`

The gate must determine whether they are:

- tracked or staged;
- imported or referenced by tracked source/tests/config;
- relevant to the EID single-source planning boundary;
- safe to leave untracked while proceeding to EID implementation planning; or
- blocking because tracked code depends on them or they would alter package/source assumptions.

## Allowed actions

- Read control truth and bounded file metadata/snippets needed for classification.
- Run no-live local Git/search commands.
- Write `docs/reviews/` disposition, review and controller judgment artifacts.
- Leave all candidate residue untracked.

## Forbidden actions

- Do not execute the source-like scripts.
- Do not stage, commit, delete, move, archive, format, or edit `fund_agent/tools/` or `scripts/claude_mimo_simple.py`.
- Do not modify source, tests, README, runtime config, provider defaults, extractor code, fixture data, source acquisition code, or control docs in this gate.
- Do not run live EID/network/PDF/FDR/fallback/provider probes.
- Do not reset, rebase, squash, push, PR, merge, release, or mark ready.

## Worker handoff target

Dispatch one disposition/evidence worker to write:

`docs/reviews/mvp-source-like-residue-ownership-nonimpact-disposition-evidence-20260610.md`

The worker must produce direct evidence and a disposition table. It must not perform cleanup.

## Review routing

Dispatch two independent reviewers after the evidence artifact exists:

- AgentDS
- AgentMiMo

Review focus:

- Whether the evidence proves no tracked source/test/config dependency.
- Whether the residue is correctly classified as untracked source-like user-owned residue rather than accepted project source.
- Whether proceeding to EID implementation planning would be safe if the planning gate explicitly ignores and does not stage/use the residue.
- Whether any hidden package inclusion or source-boundary risk remains.

## Controller acceptance condition

This gate may be accepted only if direct evidence shows the source-like paths are untracked, unstaged, not imported/referenced by tracked source/tests/config, and can remain untracked without becoming source truth for EID planning.

If tracked code depends on either path, or if evidence is inconclusive, EID implementation planning remains blocked pending user disposition.
