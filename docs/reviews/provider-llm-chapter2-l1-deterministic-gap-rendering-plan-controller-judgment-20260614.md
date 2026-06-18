# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate`

Verdict: `ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the planning gate for a narrow Chapter 2 `l1_numerical_closure` deterministic evidence-gap / minimum-verification route.

This judgment authorizes only the next no-live implementation gate under the allowed write set and binding amendments below. It does not authorize live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands, source-policy changes, fallback expansion, provider default changes, repair budget changes, annual-period LLM route work, Docling work, push, merge, or readiness claims.

EID annual-report access remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, module boundaries, template sync rule and EID single-source/no-fallback boundary. |
| `docs/current-startup-packet.md` | Current active gate and checkpoint `5689082`. |
| `docs/implementation-control.md` | Current control truth and planning-only gate scope. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-20260614.md` | Planning artifact under review. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-review-ds-20260614.md` | DS independent review, verdict `PASS_WITH_FINDINGS`. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-review-mimo-20260614.md` | MiMo independent review, verdict `PASS_WITH_FINDINGS`. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-controller-judgment-20260614.md` | Prior binding amendments accepted at checkpoint `e840418`. |

No report bodies, prompt bodies, provider request/response payloads, PDF/source/cache bodies, source bodies or final report body were read for this judgment.

## 3. Accepted Plan Facts

| Fact | Disposition |
|---|---|
| The plan scopes behavior to Chapter 2 `l1_numerical_closure` and does not generalize to all L1 subcategories. | Accepted. |
| Gap/minimum-verification behavior is gated by typed `EvidenceAvailability` non-`available` statuses. | Accepted. |
| Present-but-ignored facts with `available` status and anchors remain fail-closed as `l1_numerical_closure`. | Accepted. |
| Repair budget remains unchanged. | Accepted. |
| EID source policy remains single-source/no-fallback. | Accepted. |
| The plan recommends exactly one next gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate`. | Accepted. |
| Release/readiness remains `NOT_READY`. | Accepted. |

## 4. Review Finding Disposition

| Finding | Controller disposition | Binding amendment |
|---|---|---|
| DS F1: exact `missing_evidence_reason` text is unspecified. | `ACCEPT` | Implementation must specify exact `missing_evidence_reason` text per item group before/while editing the template, and V1 must assert those exact texts. |
| DS F2: product wording field mapping is implicit. | `ACCEPT_WITH_REWRITE` | Implementation evidence must state that `missing_evidence_reason` carries the domain insufficiency reason, while existing writer prompt instruction carries the output mechanics. If this is false in implementation, worker must stop for controller review. |
| DS F3: `AGENTS.md` template-structure sync rule requires explicit check. | `ACCEPT` | Implementation evidence must confirm Chapter 2 item ids, order, text, chapter structure and template section structure are unchanged. If changed, implementation must stop before design/README sync. |
| DS F4: no-live tests cannot prove future LLM wording compliance. | `ACCEPTED_RESIDUAL` | Carry to future bounded live/provider evidence gate; not blocking this no-live implementation plan. |
| DS F5: prompt header interaction with new reasons must be verified. | `ACCEPT` | Implementation evidence must include full prompt-assembly assertions or writer tests proving new reasons do not contradict gap/minimum-verification instructions. |
| MiMo F1: conditional source escape hatch may invite overbroad source changes. | `ACCEPT_WITH_REWRITE` | Next implementation gate must treat production source edits as forbidden by default. Source edits are allowed only if a no-live test fails because existing code lacks the needed enum behavior, and the fix is confined to the five named files. Otherwise stop for controller review. |
| MiMo F2: V5 issue-id naming needs explicit implementation contract. | `ACCEPT` | Preserve existing `writer:required_output_block:` for available-fact block cases. Add or use more specific gap/verification issue ids only for non-`available` gap or verification output defects. |
| MiMo F3/F4: ambiguity handling and validation commands are sufficient. | `ACCEPT` | No extra amendment beyond preserving typed availability gating and scoped validation commands. |

## 5. Accepted Implementation Gate

Next gate:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate
```

Gate classification: `standard`.

Allowed write set:

| Path | Disposition |
|---|---|
| `docs/fund-analysis-template-draft.md` | Allowed only for the seven Chapter 2 required-output `when_evidence_missing` values and exact `missing_evidence_reason` text. No item id/order/text/chapter structure changes. |
| `tests/fund/template/test_typed_contracts.py` | Allowed for exact Ch2 template policy and reason assertions; Ch3 behavior must remain covered. |
| `tests/fund/test_chapter_writer.py` | Allowed for Ch2 positive gap/minimum-verification writer tests, missing-envelope fail-closed test and prompt-assembly checks. |
| `tests/fund/test_chapter_auditor.py` | Allowed for safe gap/minimum-verification L1 pass and unsafe concrete unanchored percentage L1 fail. |
| `tests/services/test_chapter_orchestrator.py` | Allowed for Ch2 missing-evidence accepted path, present-but-ignored fail-closed path and repair-budget-preservation path. |
| `tests/agent/test_runner.py` | Allowed for Agent runner Ch2 positive and unsafe-output no-live coverage. |
| `tests/services/test_fund_analysis_service_llm.py` | Allowed for Service hosted/final-assembly no-live positive and negative coverage. |
| `tests/fund/test_evidence_availability.py` | Allowed only if needed to prove same-source Ch2 requirement mappings remain unchanged. |
| `tests/README.md` | Conditional only if current test-surface descriptions become false. |

Conditional source write set:

Production Python source edits are forbidden by default. They become allowed only if a no-live test fails because existing code does not support the required enum behavior, and the minimal fix is confined to:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/agent/runner.py`
- `fund_agent/agent/repair.py`

Any need outside those files must stop and return to controller.

Forbidden write set:

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- root `README.md`
- provider/default/runtime config
- source acquisition, FDR, PDF/cache, fallback, Eastmoney, fund-company, CNINFO
- annual-period LLM route
- Docling/parser policy
- readiness/release/PR artifacts

## 6. Required Validation For Implementation Gate

Minimum commands:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/test_evidence_availability.py -q
uv run ruff check tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/test_evidence_availability.py
git diff --check
```

If production source is touched under the conditional rule, ruff must include the touched source files and evidence must identify the failing no-live test that justified the source edit.

Implementation evidence must additionally report:

1. Exact `missing_evidence_reason` text per item group.
2. Confirmation that Chapter 2 item ids/order/text/chapter structure are unchanged.
3. Confirmation that `writer:required_output_block:` remains for available-fact block cases.
4. Confirmation that `max_repair_attempts` is unchanged.
5. Confirmation that EID single-source/no-fallback policy is untouched.
6. Confirmation that release/readiness remains `NOT_READY`.

## 7. Accepted / Rejected / Residual Table

| Item | Disposition | Owner / next handling |
|---|---|---|
| Plan recommendation to proceed to no-live implementation gate | `ACCEPT_WITH_AMENDMENTS` | Implementation worker. |
| Template route for Ch2 `when_evidence_missing` policy | `ACCEPT` | Implementation worker, within exact seven-item scope. |
| Design/control doc edit before implementation | `REJECT` | Not required if template structure is unchanged. |
| Repair budget change | `REJECT` | Separate future gate only. |
| Source-policy/fallback change | `REJECT` | Out of scope. |
| Live/provider proof of future LLM wording compliance | `DEFER` | Future bounded live/provider evidence gate after no-live implementation. |
| Missing exact reason text | `ACCEPTED_RESIDUAL` | Must be closed in implementation evidence. |
| Conditional source edit ambiguity | `ACCEPTED_RESIDUAL` | Must be constrained by controller amendment above. |

## 8. Validation

Controller validation for this planning gate:

```text
git status --short
git status --branch --short
git diff --check
```

No live/provider/LLM/network/source/PDF/readiness/release/PR validation is authorized by this planning gate.

## 9. Final Verdict

`VERDICT: ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`

Next entry point:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate
```
