# Code Review: Evidence Confirm Default-on Policy Slice EC-DO-4

## Meta

- **Reviewer**: AgentDS
- **Work unit**: Evidence Confirm Productionization default-on policy
- **Slice**: EC-DO-4 Documentation And Control Sync
- **Gate type**: code review gate (`heavy`)
- **Implementation evidence**: `docs/reviews/evidence-confirm-productionization-default-on-policy-slice4-implementation-evidence-20260623.md`
- **Prior accepted slice**: EC-DO-1 (`c5d7718`), EC-DO-2 (`115a097`), EC-DO-3 (`3e7a9a1`)
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`, `docs/current-startup-packet.md`
- **Changed files**: `README.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`
- **Artifact**: `docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice4.md`

## Scope

Review only the EC-DO-4 documentation/control sync diff against accepted code facts from EC-DO-1 through EC-DO-3 and the implementation evidence artifact.

## Validation Commands Run

```text
git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md
# exit 0, clean

rg -n 'stale|Evidence Confirm opt-in|default-off|current-entry pattern|实施入口' docs/design.md README.md docs/implementation-control.md docs/current-startup-packet.md
# NO_MATCHES_FOUND

rg -n 'product disable|disable flag|禁用.*Evidence|Evidence.*禁用' README.md
# NO_DISABLE_FLAG_FOUND

rg -n 'product.*analyze.*warn|product.*analyze-annual-period.*inherit|Release.readiness remains.*NOT_READY|checklist Evidence Confirm CLI support|provider.*semantic quality|mark-ready|merge|release transition|annual-period.*summary' docs/design.md README.md docs/implementation-control.md docs/current-startup-packet.md
# all expected boundary patterns present in correct scope, no false-positive overclaims
```

## Findings

No findings. Zero findings across all five review questions.

## Review Questions — Per-Question Assessment

### Q1: Do docs truthfully reflect accepted current code facts from EC-DO-1 to EC-DO-3?

**PASS.** All four accepted implementation facts are correctly reflected with no drift:

| Accepted fact (EC-DO-1/2/3) | design.md | README.md | control docs |
|---|---|---|---|
| product `analyze` default EC policy = `warn` | L886 | L113 | imp-ctrl L118, startup L24 |
| `analyze-annual-period` inherits through `analyze()` delegation | L887 | L117 | imp-ctrl L118 |
| `checklist` remains `off` | L888 | L113, L115 | imp-ctrl L118 |
| developer override remains bounded (`--dev-override` only) | L889 | L110 | startup L24 |

- `docs/design.md` L885-894：correctly states default-on `warn` for `analyze`, delegation-based inheritance for `analyze-annual-period`, checklist `off`, and developer sandbox override bounded via `--dev-override`.
- `README.md` L113：product mode description correctly lists Evidence Confirm 摘要 as a default input to final judgment alongside checklist/veto/stress-test/quality-gate, replacing the old claim that Evidence Confirm is never called.
- `README.md` L110：`--evidence-confirm-policy` dev-override wording changed from "开发者显式 opt-in" to "开发者覆盖 Evidence Confirm 策略，默认 developer sandbox 为 `off`" — accurately reflects that product default is now `warn` and `--dev-override` overrides it.

### Q2: Do docs avoid overclaiming release/readiness, PR mark-ready, merge, provider-backed semantic quality, report-body rendering, checklist Evidence Confirm support, multi-sample live source/PDF evidence?

**PASS.** All future/unauthorized items are explicitly gated:

- **Release/readiness**: `NOT_READY` consistently stated in all four files (design.md L894, README multiple locations via startup-packet reference, imp-ctrl L109/L129/L142, startup L24/L63/L228).
- **PR mark-ready / merge**: listed as "未由当前实现授权" / "remain unauthorized before separate reviewed gates" in design.md L894, imp-ctrl L109, startup L24.
- **Provider-backed semantic quality**: design.md L894 lists as future/候选边界.
- **Report-body rendering**: design.md L890 explicitly states "renderer 报告 Markdown 仍不渲染 Evidence Confirm", L894 lists as future.
- **Checklist Evidence Confirm CLI support**: design.md L888 "checklist Evidence Confirm support 仍是后续独立 gate", README L115 "默认 `checklist` 仍不会调用 Evidence Confirm", startup L24 "checklist Evidence Confirm CLI support ... remain unauthorized".
- **Multi-sample live source/PDF evidence**: imp-ctrl L109, startup L24 list as unauthorized.

### Q3: Does README avoid documenting any product disable flag while keeping developer sandbox wording accurate?

**PASS.**

- `rg` for "product disable" / "disable flag" / "禁用.*Evidence" / "Evidence.*禁用" returned zero matches in README.md.
- `README.md` L113 explicitly states "普通 product `analyze` 不暴露 Evidence Confirm disable flag".
- `README.md` L110：`--evidence-confirm-policy off|warn|block` correctly scoped to "仅 `analyze --dev-override` 支持", with default described as "developer sandbox 为 `off`" — not a product feature, not a user-facing toggle.
- `design.md` L889 mirrors: "`off` 是 developer sandbox no-run/off policy" and "普通 product `analyze` 不暴露 Evidence Confirm disable flag".

### Q4: Is annual-period Evidence Confirm CLI summary display recorded as a future residual rather than claimed implemented behavior?

**PASS.** All four documents consistently record this as a future residual:

- `docs/design.md` L887: "CLI 尚未单独展示 annual-period 的 Evidence Confirm summary 行，该显示问题保留为后续 UI/CLI residual，不改变当前运行语义"
- `README.md` L117: "当前 CLI 不额外展示 annual-period 专用 Evidence Confirm summary 行"
- `docs/current-startup-packet.md` L24: "annual-period Evidence Confirm CLI summary display refinement ... remain unauthorized before separate reviewed gates"
- `docs/implementation-control.md` L109: same listing
- Implementation evidence `docs/reviews/evidence-confirm-productionization-default-on-policy-slice4-implementation-evidence-20260623.md` L40-47: explicitly records the current code fact and dispositions as "future UI/CLI residual"

No doc claims annual-period summary display as implemented.

### Q5: Are control docs correctly at EC-DO-4 code review gate and not accepted slice / release ready?

**PASS.** All control surface entries correctly identify the current gate:

- `docs/current-startup-packet.md` L24: "Current active gate | Evidence Confirm Productionization default-on policy Slice EC-DO-4 **code review gate**" and "Slice EC-DO-4 Documentation And Control Sync is implemented locally ... and **ready for review, not yet accepted**"
- `docs/current-startup-packet.md` L63: "Next entry point | Evidence Confirm Productionization default-on policy Slice EC-DO-4 **code review gate**"
- `docs/current-startup-packet.md` L228: "Current next entry is Evidence Confirm Productionization default-on policy Slice EC-DO-4 **code review gate** ... Do not claim **accepted EC-DO-4** ..."
- `docs/implementation-control.md` L126: "Active gate | Evidence Confirm Productionization default-on policy Slice EC-DO-4 **code review gate**"
- `docs/implementation-control.md` L129: "Slice EC-DO-4 documentation/control sync is implemented locally ... and is **ready for review, not yet accepted**"
- `docs/implementation-control.md` L142: "Next entry point | Evidence Confirm Productionization default-on policy Slice EC-DO-4 **code review gate**"

No control doc claims accepted slice, release ready, or any state beyond "implemented locally, ready for review."

## Adversarial Pass

- Searched for stale "opt-in/default-off" pattern in all four files — zero matches. The old wording "开发者显式 opt-in Evidence Confirm，默认 `off`" and "默认 `analyze` 和 `checklist` 都不会调用 Evidence Confirm" have been completely replaced.
- Searched for "禁用" (disable) near "Evidence Confirm" in README — zero matches.
- Cross-checked: design.md L65 still references "no-live Evidence Confirm helper" for the Fund-layer helper module. This is correct and distinct from the product-level default-on policy; the helper remains a Fund-internal contract. No overclaim conflating helper scope with product scope.
- Cross-checked: `fund_agent/fund/evidence_confirm.py` line 415 reference in design.md still describes the no-live helper (pre-dates EC-DO-1). The new EC default-on text at L885-894 is in a separate section and correctly describes the product-level behavior independently. No contradiction.
- Cross-checked: README L300 quality gate projection now reads "Evidence Confirm 摘要可被 quality gate 投影为 `ECQ0`-`ECQ4` issue family；默认 product `analyze` 和继承该路径的 `analyze-annual-period` 会以 `warn` 策略提供该摘要". Old wording "开发 opt-in 的 Evidence Confirm 摘要" removed. Correct.
- `git diff --check` passed — no whitespace errors.

## Residual Risks / Uncovered Areas

These are scope boundary items, not findings:

| Residual | Owner | Destination |
|---|---|---|
| Checklist Evidence Confirm CLI support | Service/CLI owner | Separate reviewed gate |
| Provider-backed/live semantic quality | Provider/quality owner | Separate reviewed gate |
| Multi-sample live source/PDF evidence | Evidence owner | Separate reviewed gate |
| Annual-period Evidence Confirm CLI summary display refinement | UI/CLI owner | Future UI/CLI residual gate |
| Report-body Evidence Confirm rendering | Renderer owner | Future renderer gate |
| PR-40 mark-ready / merge / release transition | Controller / release owner | Separate reviewed gate |
| EC-DO-4 controller judgment | Controller | Next gate after this review |

## Verdict

**CODE_REVIEW_PASS**

EC-DO-4 documentation/control sync diff is correct, internally consistent, and truthful to accepted code facts from EC-DO-1 through EC-DO-3. No overclaims, no stale patterns, no product disable flag documented, annual-period CLI summary correctly recorded as future residual, and all control docs correctly at code review gate (not accepted slice, not release ready). Zero findings.
