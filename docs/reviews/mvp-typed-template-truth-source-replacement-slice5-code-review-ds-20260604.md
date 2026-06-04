# MVP typed template truth-source replacement Slice 5 code review (AgentDS)

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Slice: Slice 5 Documentation/control sync
- Role: AgentDS reviewer only
- Review date: 2026-06-04
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Accepted checkpoints: plan `266e18f`, Slice 1 `3c2b237`, Slice 2 `0263bc2`, Slice 3 `202b396`, Slice 4 `e613876`

## Verdict

**PASS** — no blocking findings.

---

## Findings

### F1 (LOW): design.md and implementation-control.md version dates lag behind Slice 5 edits

- `docs/design.md:4`: version header shows `日期: 2026-06-02`, but Slice 5 edits were applied 2026-06-04.
- `docs/implementation-control.md:4`: same `日期: 2026-06-02` lag.

The change summaries in both headers correctly describe the truth-source replacement facts, so the content is authoritative. The date lag is cosmetic and does not create ambiguity about current state. AGENTS.md discourages time-sensitive content in docs; the version date field is the one place where staleness marginally matters.

**Impact**: None functional. A future docs pass could bump both dates to 2026-06-04.

**Disposition**: Non-blocking. Accepted as-is for this slice.

### F2 (LOW): Historical ledger row at implementation-control.md:414 retains "additive sidecar" language

- `docs/implementation-control.md:414`: The row for `MVP typed template contract Slice 8 Documentation And Control Sync After Accepted Implementation gate` describes that gate's scope as "additive sidecar/current typed path facts while preserving template truth."

This is historically accurate for what that old Slice 8 gate did — at that time, the typed path WAS additive and template truth WAS preserved unchanged. The current gate (Slice 5 of the truth-source replacement gate) supersedes that state, and all current-status sections (Startup Packet, Current Truth Guardrails, Current Gate, Current Decision Summary) correctly describe the post-replacement state. The evidence artifact already acknowledges this as the only remaining historical reference.

**Impact**: None. No reader would be confused because the row is in a historical ledger table, not in a current-status section.

**Disposition**: Non-blocking. No fix required.

---

## Review-focus checklist

### 1. Docs reclassify template truth-source replacement as current implemented fact

| Check | Result |
|---|---|
| `docs/design.md` header (line 5) states truth-source replacement is current | PASS |
| `docs/design.md` §3.2 (line 154) says canonical JSON is authored truth source | PASS |
| `docs/design.md` §3.2 "当前已实现：typed template truth-source replacement" (line 176) | PASS |
| `docs/design.md` §5.1 (line 513) confirms as Fund-layer current fact | PASS |
| `docs/implementation-control.md` header (line 9) states JSON is authored truth source | PASS |
| `docs/implementation-control.md` Current Truth Guardrails (line 52) confirms | PASS |
| `docs/current-startup-packet.md` (lines 62, 74) confirms | PASS |

### 2. Docs state contracts.py parses untyped, typed_contracts.py projects typed from same JSON

| Check | Result |
|---|---|
| `docs/design.md:154` documents both roles correctly | PASS |
| `docs/design.md:166` machine contract manifest section correct | PASS |
| `docs/design.md:176-177` typed truth-source replacement section correct | PASS |
| `fund_agent/fund/README.md:116-121` documents both projections from canonical JSON | PASS |
| `fund_agent/fund/README.md:379` manifest loader documentation correct | PASS |
| `tests/README.md:49-50` test documentation references canonical JSON | PASS |

### 3. docs/implementation-control.md verifies contracts.py/typed_contracts.py role as in #2

| Check | Result |
|---|---|
| Header (line 9): `contracts.py` 解析/投影/验证 untyped, `typed_contracts.py` 从同一 JSON 投影/验证 typed | PASS |
| Current Truth Guardrails (line 52): both roles confirmed | PASS |
| Current Gate objective (line 117): same | PASS |
| Current Decision Summary (line 339): comprehensive confirmation | PASS |

### 4. Current gate, checkpoints, next entry point concise and correct

| Check | Result |
|---|---|
| `docs/current-startup-packet.md` §2: gate correctly states Slice 5, status correct, next entry clear | PASS |
| `docs/implementation-control.md` Startup Packet table: same consistency | PASS |
| No long historical append in startup or current gate sections | PASS |
| No stale current gate referencing old aggregate deepreview or PR readiness as current | PASS |
| Next entry point explicitly prohibits phaseflow/provider/runtime/Agent/score-loop/PR actions | PASS |

### 5. Fund README and tests README align

| Check | Result |
|---|---|
| `fund_agent/fund/README.md` updated with template truth-source facts (lines 116-136) | PASS |
| `tests/README.md` references template truth-source parser/projection tests (lines 49-50) | PASS |
| `tests/README.md:246` maintenance rule requires no live provider probes for template contract tests | PASS |
| Both READMEs maintain correct scope boundaries (Fund README stays Fund-focused, tests README stays test-focused) | PASS |

### 6. Non-goals/deferred state preserved

| Non-goal | Status |
|---|---|
| Agent runtime/tool-loop | Confirmed deferred/non-goal in all docs |
| Multi-year runtime | Confirmed deferred |
| Provider/default/runtime/live probe | Confirmed prohibited in current gate |
| Score-loop | Confirmed deferred |
| Ch2 public split | Explicitly non-goal (public chapter ids remain 0-7) |
| Deterministic analyze/checklist behavior change | Explicitly preserved unchanged |
| Renderer behavior change | Explicitly preserved unchanged |
| Quality/golden/readiness promotion | Confirmed non-goal |
| PR/push/release/external state | Confirmed prohibited |
| Public chapter ids 0-7 | Explicitly preserved in all docs |

Forbidden current-overclaim grep (11 patterns) returned zero matches in current-status sections. All matches found were in historical ledger rows describing PAST next actions, not current state.

### 7. Evidence validation adequacy

| Check | Result |
|---|---|
| 46 template contract tests pass (`test_contracts.py` + `test_typed_contracts.py`) | PASS (verified) |
| Docs self-check script: 26 required assertions present, 11 forbidden overclaims absent | PASS (from evidence) |
| Targeted grep: truth-source statements present in all 5 docs | PASS (verified) |
| Forbidden overclaim grep: exited 1 (no matches) | PASS (verified) |
| Historical sidecar wording: only in superseded Slice 8 ledger row | PASS (verified) |
| `git diff --check` for changed docs: exited 0 | PASS (verified) |
| Whitespace self-check for all 6 files (including untracked evidence): PASS | PASS (from evidence) |
| No provider/runtime/live probe was executed | PASS (confirmed) |

---

## Validation reviewed from evidence

Evidence artifact: `docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md`

All evidence claims were independently rechecked:

- **46 template tests**: Re-ran `uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q` — confirmed 46 passed.
- **Docs self-check**: Reviewed the script logic — 26 required assertions across 5 files, 11 forbidden patterns. The evidence output says PASS. I independently grep-verified truth-source statements in all 5 files (see checklist above) and forbidden overclaims (zero matches).
- **Whitespace**: `git diff --check` re-ran — exited 0, no output.
- **Forbidden overclaims**: Re-ran grep — exited 1 (no matches), confirmed.

---

## Residual risks

| Risk | Blocking? | Disposition |
|---|---|---|
| **design.md / implementation-control.md version date lag** (2026-06-02 vs 2026-06-04) | No | Cosmetic only; change summaries are correct. Deferred to next docs pass. |
| **Historical ledger row at impl-control:414 uses "additive sidecar" language** | No | Historically accurate for the old Slice 8 gate it describes; current-status sections supersede it. |
| **Slice 5 did not rerun full service/UI/provider/Host suites** | No | In-scope for this docs-only slice; those suites are not in allowed scope. 46 targeted template tests pass. |
| **Prior non-blocking residuals (Ch3 single-year, Ch7 polish, `TypedTemplatePathMode` cleanup, `TemplateLensRule` naming)** | No | Already accepted as future cleanup in prior controller judgments; not in Slice 5 scope. |
| **Untracked unrelated workspace artifacts** | No | Intentionally ignored; Slice 5 scope is docs-only. |
