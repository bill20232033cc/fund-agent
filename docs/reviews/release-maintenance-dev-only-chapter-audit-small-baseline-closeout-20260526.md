# Dev-only Chapter Audit x Small Baseline Closeout

> Date: 2026-05-26
> Role: Controller
> Gate: dev-only chapter audit x small baseline corpus evaluation
> Verdict: ACCEPTED_WITH_CONTRACT_TUNING; NEXT_GATE_RENDERER_MINIMAL_INTEGRATION_DESIGN

## Scope

This gate verified the Fund-layer executable CHAPTER_CONTRACT sidecar and dev-only report-writing audit against the accepted small baseline candidate set. It did not integrate with the v0 renderer, FQ0-FQ6 quality gate, Service/CLI default `analyze` / `checklist`, Host/Agent, Dayu runtime, `FundDocumentRepository`, PDF/cache/source helpers, downloaders, or production extractors.

## Gate A Readiness

Artifact: `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-readiness-20260526.md`

Result: passed.

- Sidecar and dev-only writing audit were accepted by `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md`.
- Worktree was clean at readiness start.
- README, design, tests README, and control doc were already synchronized.
- Clean audit candidates were `004393` / active, `004194` / enhanced index, and `006597` / bond.
- `110020` / index and `017641` / QDII remain fallback-blocked; `007721` and `017970` remain FOF data-gap / taxonomy residuals.

## Gate B Dev-only Audit Run

Artifact: `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-run-20260526.md`

Scratch path: `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/`

Result: passed for evidence collection, but found a contract tuning blocker.

| fund_code | report_year | fund_type_slot | audited chapter | material audit? | Result |
|---|---:|---|---|---|---|
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | Reviewed fact positive control passed; missing evidence and missing wording controls failed as expected. |
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | Initial false-positive probe incorrectly emitted `unsupported_stability_claim` for a valid next-minimum-validation question. |
| `004194` | 2024 | `enhanced_index` | Chapter 2 | no | Deferred `config_only` sidecar visibility only; not tracking-error audit evidence. |
| `006597` | 2024 | `bond_fund` | Chapter 6 | no | Deferred `config_only` sidecar visibility only; not bond-risk audit evidence. |

## Gate C Taxonomy And Tuning

Artifact: `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-taxonomy-decision-20260526.md`

Initial decision: `CONTRACT_TUNING_REQUIRED_BEFORE_RENDERER_INTEGRATION`.

Accepted issue:

- Category: `chapter contract too strict`
- Evidence: `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-compatible-datagap-wording-false-positive-probe.json`
- Root cause: phrase matcher treated `风格稳定性和言行一致性判断是否仍成立？` inside a next-minimum-validation question as a positive stability claim.

Tuning implemented:

- `fund_agent/fund/report_writing_audit.py` now recognizes question context in the same sentence segment when stability phrases are preceded by `下一步最小验证问题` / `复核` / `验证` / `确认` and followed by question wording.
- `tests/fund/test_report_writing_audit.py` now covers the exact false-positive wording.

Post-tuning rerun over original scratch inputs:

| Variant | Post-tuning issue count | Taxonomy |
|---|---:|---|
| `004393-active-ch3-compatible-datagap-wording-false-positive-probe.json` | 0 | none |
| `004393-active-ch3-missing-evidence-stability-claim.json` | 2 | `required_evidence_missing=1`, `unsupported_stability_claim=1` |
| `004393-active-ch3-compatible-datagap-missing-wording.json` | 1 | `insufficient_evidence_wording_missing=1` |
| `004393-active-ch3-compatible-datagap-insufficient-wording.json` | 0 | none |

Taxonomy after tuning:

| Category | Status |
|---|---|
| data/source extraction | Still blocks broader Chapter 2 / Chapter 6 material coverage and index/QDII clean samples. |
| evidence traceability | Adequate for active Chapter 3 dev-only slice; resolvable anchors are required. |
| chapter contract too strict | Initial blocker fixed for the reproduced next-question wording. |
| chapter contract too loose | Not observed in active Chapter 3 controls. |
| report writing/template gap | Renderer/writer still needs a design gate for deterministic active Chapter 3 insufficiency wording. |
| validator schema issue | Not blocking for `audit_report_writing_bundle`; prior combined JSONL limitation remains separate. |
| fund-type taxonomy issue | FOF remains data-gap / taxonomy residual. |

## Gate D Escalation Decision

Next gate: `renderer minimal integration design`.

This is design-only readiness, not implementation authorization.

Rationale:

- The dev-only audit is now stable on the active-fund Chapter 3 control set after tuning.
- The reproduced false positive has a direct fix and regression test.
- Current deterministic MVP remains unchanged: no renderer, FQ0-FQ6, Service/CLI, Host/Agent, Dayu, repository/source-helper integration was added.
- FQ0-FQ6 can remain unchanged because the audit remains a dev-only chapter-writing contract, not a product quality gate.

Required guardrails for the next gate:

- Scope renderer design to active-fund Chapter 3 insufficiency wording only.
- Do not implement renderer changes until a separate design/review gate accepts the minimal output contract.
- Do not broaden Chapter 2 / Chapter 6 material enforcement in the renderer gate.
- Keep default `fund-analysis analyze` / `checklist` behavior unchanged until explicitly authorized by a future implementation gate.
- Do not promote small baseline outputs to durable fixtures.

## Validation Matrix

| Check | Command | Result |
|---|---|---|
| Focused audit tests | `uv run pytest tests/fund/test_report_writing_audit.py` | `16 passed` |
| Sidecar + audit tests | `uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py` | `20 passed` |
| Adjacent tests | `uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py` | `147 passed` |
| Ruff | `uv run ruff check fund_agent/fund/report_writing_audit.py tests/fund/test_report_writing_audit.py fund_agent/fund/template/chapter_contract_constraints.py tests/fund/template/test_chapter_contract_constraints.py` | Passed |
| Scratch rerun | Python rerun over four `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-*.json` controls | Passed |
| Whitespace | `git diff --check` | Passed |

## Residual Risks

- Renderer minimal integration is not implemented and remains a future design gate.
- Chapter 2 enhanced-index and Chapter 6 bond-fund constraints are still deferred `config_only`; they are not material audit proof.
- Clean baseline still lacks index, QDII, and pure FOF samples.
- Records-mode audit remains narrow and fail-closed.
- Broader natural-language claim coverage remains a future dev-only corpus concern.
