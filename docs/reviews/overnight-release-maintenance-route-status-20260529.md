# Overnight Release Maintenance Route Status

日期：2026-05-29

角色：Phaseflow controller fallback/status artifact。本文只做 overnight route 状态固化；不是 implementation artifact，不是 promotion manifest，不修改 runtime、golden、fixtures、manifests、preflight、score、quality gate、Host/Agent/dayu 或外部 GitHub 状态。

## Summary

| Route | Status | Reason | Next gate |
|---|---|---|---|
| Route 1: minimum golden v1 readiness | accepted blocked-with-reason | 004393 rejected, 004194 diagnostic-only, 006597 rerun configured but blocked by same-fund unavailable P0 manager_strategy_text. | `006597 same-fund unavailable field review / extractor projection gate` |
| Route 2: deferred coverage | blocked-with-reason, conservative deferred | Specialist worker timed out before writing artifact; controller preserves accepted roadmap/manifests: QDII/FOF/110020/017641 remain deferred from minimum v1 and full-v1 blockers. | future deferred coverage status gate or explicit QDII/FOF/110020/017641 policy gates |
| Route 3: source/provenance hardening | controller roadmap status accepted | No Python changes authorized; future planning only. CSRC EID 006597-family runtime path remains accepted; hardening items require future gates. | source/provenance hardening plan gate |
| Route 4: future Host/Agent/dayu architecture | controller roadmap status accepted | Architecture only; no Host/Agent/dayu package or runtime implementation. Facet inference / ITEM_RULE routing remains future Agent/Fund design residual. | facet inference / ITEM_RULE routing design gate |
| Route 5: artifact/manifest lifecycle | controller disposition status accepted | No deletion/staging of unrelated untracked files; manifests remain control-plane evidence only. | artifact disposition / manifest lifecycle gate |

## Route 2 Conservative Status

The attempted Track 2 specialist handoff read the relevant manifest and controller-judgment evidence but did not produce the requested artifact before timing out. Per the overnight instruction, this single-gate timeout does not block independent tracks. Controller applies the conservative default:

| Item | Status | blocks_minimum_v1 | blocks_full_v1 | promotion_allowed | Owner | Next gate |
|---|---|---:|---:|---:|---|---|
| QDII candidates `096001`, `040046`, `019172`, `021539` | deferred / not_ready | false | true | false | future QDII diagnosis / asset-class fitness owner | QDII diagnosis or explicit deferred-from-v1 disposition gate |
| `FOF_SLOT` | deferred / not_ready | false | true | false | future FOF taxonomy owner | pure FOF repository-verified candidate gate |
| `110020 / 2024` | reviewed candidate only / not_ready | false | true | false | future index evidence sufficiency owner | index reviewed fact-freeze / methodology / constituents evidence gate |
| `017641 / 2024` | replace / deferred / not_ready | false | true | false | future QDII diagnosis / replacement owner | QDII diagnosis or explicit deferred-from-v1 gate |

Hard constraints preserved:

- No QDII probing restarted.
- No FOF taxonomy work started.
- QDII-FOF is not counted as pure FOF.
- `110020` is not treated as fact-frozen or ready.
- `017641` is not repaired or promoted.
- No manifest, runtime, score, quality, golden, fixture, PR, push, merge, release or promotion changes.

## Route 3 Source / Provenance Hardening

Current accepted state:

- CSRC EID accumulated NAV through `FundNavRepository()` is accepted for the verified 006597 family.
- Raw-unit NAV and stock-sdk remain ineligible for strong runtime evidence where adjusted / accumulated basis is required.
- Future hardening residuals: source query/request split, source generalization beyond verified 006597 family, parser/schema drift hardening, duplicate-date detection, endpoint caching/SLA, strict bool parsing for source metadata, and manifest/preflight consumption boundaries.

No Python implementation is authorized by this overnight route-status artifact. If any future hardening gate modifies Python/runtime, it must run full `uv run ruff check .` and full pytest coverage command.

## Route 4 Future Host / Agent / Dayu Architecture

Current accepted state:

- Current deterministic path remains UI -> Service -> `fund_agent/fund`.
- Future Host must use `dayu.host`.
- Future Agent engine/tool loop must use `dayu.engine`.
- No Host/Agent/dayu integration is authorized now.

Future residual:

`facet inference / ITEM_RULE routing design gate`

Required future answers:

- Boundary between `fund_type` and facet.
- Deterministic evidence-derived facet inference, not LLM guessing.
- How facets route ITEM_RULE and alter `must_answer`, `must_not_cover`, and `preferred_lens`.
- Ownership in Agent/Fund layer, not UI/Service/Host.
- Compatibility with future dayu agent first-step facet flow.

## Route 5 Artifact / Manifest Lifecycle

Current untracked inventory remains unmodified:

| Path / group | Category | Decision | Owner | Next gate | Blocker |
|---|---|---|---|---|---|
| `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-*` | evidence-chain artifact, superseded by accepted 006597-specific rerun for current truth | leave-untracked | artifact disposition owner | artifact disposition gate | no |
| `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md` / `20260527.md` | old review/audit evidence | leave-untracked | artifact disposition owner | archive/disposition gate | no |
| `docs/reviews/repo-review-20260526-231040.md`, `20260527-215953.md`, `20260527-225303.md` | old review evidence | leave-untracked | artifact disposition owner | archive/disposition gate | no |
| `docs/tmux-agent-memory-store.md` | user/agent memory artifact | leave-untracked | user / artifact disposition owner | explicit disposition or deletion authorization | no |
| `reviews/` | untracked review directory | leave-untracked | artifact disposition owner | artifact disposition gate | no |
| `--help` | stray file | leave-untracked; deletion requires explicit authorization | user / artifact disposition owner | explicit cleanup authorization | no |

Tracked manifests:

- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`

Both remain control-plane evidence only. They are not promotion manifests and are not runtime/preflight-consumed by this gate.

## Validation

This is a docs-only controller status artifact.

Validation required before checkpoint:

```text
git diff --check -- docs/reviews/overnight-release-maintenance-route-status-20260529.md
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json docs/design.md reports/golden-answers
```

`ruff` / `pytest` are not required because this artifact does not modify Python, tests, runtime, score, quality gate, snapshots, reports, manifests, preflight consumption, golden answers, or fixtures.

## Final Status

The overnight phase has a durable Track 1 accepted blocked-with-reason result. Routes 2-5 have conservative route-status artifacts / dispositions and no unsafe action was taken. The next operational entry remains:

`006597 same-fund unavailable field review / extractor projection gate`
