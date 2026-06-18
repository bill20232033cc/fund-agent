# EID Single Source Operational Implementation Planning Gate startup judgment

Date: 2026-06-10

Gate: `EID Single Source Operational Implementation Planning Gate`

Classification: `heavy`

## Controller startup judgment

The gate may open as planning-only.

Reason:

- The accepted truth-doc steering selects `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- EID single-source operational hardening is accepted as a future implementation direction, not current code fact.
- The preceding `source-like residue ownership / non-impact disposition gate` accepted `fund_agent/tools/` and `scripts/claude_mimo_simple.py` as non-blocking residuals only if explicitly ignored.
- No source implementation, tests, README, runtime config, live EID/network/PDF/FDR acquisition, fallback invocation, provider probe, push, PR, release, merge or mark-ready action is authorized.

## Current control truth

- Current phase: `MVP typed-template-to-agent report generation stabilization phase`.
- Current steering target: EID single operational annual-report source MVP.
- Current source policy target: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- Eastmoney, fund-company official website/CDN, CNINFO and other non-EID routes are deferred candidates or historical evidence-intake routes only.
- `FundDocumentRepository` remains the only production annual-report PDF access boundary.
- UI, Service, Host, renderer and quality gate must not directly call EID source, downloader helper, PDF cache, parser internals or third-party source helpers.
- `schema_drift`, `identity_mismatch` and `integrity_error` must fail closed.
- `not_found` and `unavailable` are terminal EID failures in single-source mode and do not authorize fallback.
- `row-shape contract decision gate` remains queued / paused by steering.

## Explicit ignore boundary

The following untracked source-like residue is outside this planning gate:

- `fund_agent/tools/`
- `scripts/claude_mimo_simple.py`

Planning worker and reviewers must not use these paths as architecture truth, source truth, source policy evidence, implementation evidence, package design input, allowed files, or validation inputs. They must not stage, edit, delete, move, import or execute them.

## Planning deliverable

Planning worker must produce:

`docs/reviews/mvp-eid-single-source-operational-implementation-planning-gate-plan-20260610.md`

The plan must be code-generation-ready and include:

- current EID implementation inventory;
- EID discovery contract;
- EID identity validation contract;
- EID PDF integrity contract;
- source metadata schema;
- repository/cache persistence boundaries;
- failure category matrix;
- allowed files and forbidden files;
- implementation slices;
- no-live tests per slice;
- no-live validation matrix;
- direct evidence matrix;
- rollback and residual risk;
- design/control update points;
- optional live EID smoke gate marked as requiring separate user authorization.

## Planning prohibitions

The plan must prohibit:

- multi-source fallback;
- Eastmoney production fallback;
- fund-company website/CDN production fallback;
- CNINFO production fallback;
- UI/Service/Host/renderer/quality gate direct calls to EID source/downloader/cache/parser helpers;
- use of `unavailable` to mask `schema_drift`, `identity_mismatch` or `integrity_error`;
- live EID/network/PDF/FDR/provider/fallback validation as planning acceptance;
- `dayu-agent` production runtime dependency;
- `extra_payload`.

## Review routing

After the plan exists, dispatch two independent reviewers:

- AgentDS
- AgentMiMo

Reviewers must focus on single-source discipline, fallback prohibition, fail-closed failure classification, `FundDocumentRepository` boundary, no-live validation, deferred Eastmoney risk handling, and scope drift.

## Controller acceptance condition

The gate may be accepted only if plan plus reviews prove the next implementation slices are code-generation-ready, no-live verifiable, and bounded to EID single-source policy without source/runtime implementation happening in this gate.
