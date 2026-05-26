# Gate D First Report-Quality Improvement Slice Implementation Controller Judgment - 2026-05-26

## Scope

This judgment closes Gate D for the accepted minimal implementation slice:

`active_fund` Chapter 3 turnover / style-consistency data-gap wording contract implementation.

The gate stayed inside Fund-layer contract / audit / evidence wording and tests. It did not modify renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, production extraction, `FundDocumentRepository`, PDF/cache/source helpers, fixtures, tracked reports, or product default command behavior.

## Accepted Implementation

Changed files:

- `docs/fund-analysis-template-draft.md`
- `fund_agent/fund/template/contracts.py`
- `fund_agent/fund/audit/contract_rules.py`
- `tests/fund/template/test_contracts.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `tests/fund/test_report_evidence.py`
- `fund_agent/fund/README.md`

Accepted behavior:

- Chapter 3 now states that active-fund style stability / style consistency /言行一致 claims require reviewed turnover or style-change evidence.
- Missing, unavailable, or unreviewed turnover/style-change evidence is a semantic `must_not_cover` prohibition, covered by `narrative_guidance`.
- `ReportDataGapOverride.required_report_wording` preserves insufficiency wording and the next minimum validation question.
- The implementation deliberately did not add a new runtime `ContractRequiredItemRule` for the gap wording because current renderer output cannot satisfy that marker without a later renderer/report-writing gate.

## Mandatory Preflight Result

The implementation agent verified the Gate D preflight:

- Runtime C2 audit checks `ContractRequiredItemRule` markers unconditionally.
- Adding a Chapter 3 required item for `换手率/风格变化证据缺口说明与下一步最小验证问题` would make current active-fund renderer output fail contract audit.
- The safe option was therefore applied: contract wording and `narrative_guidance` coverage were added, while the runtime required item rule was deferred.

Controller disposition: accepted. This preserves the user-default product behavior boundary while still hardening the report-quality contract for future evaluation and renderer/report-writing work.

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted. Findings are minor / informational and non-blocking. |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted. Findings are informational or accepted residuals. |

Accepted non-blocking review observations:

- Template draft is stricter than runtime `contracts.py` for the deferred required output item; this is intentional safe-option asymmetry and is guarded by tests.
- `must_answer_coverages` count assertion can be considered in a future robustness pass.
- Template-draft / contracts.py drift remains process-dependent; no new blocker introduced.
- Renderer still does not emit the new gap wording marker; future renderer/report-writing gate owns that.

## Validation

Commands accepted for this gate:

```text
uv run pytest tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
```

Result: `83 passed`.

```text
uv run pytest tests/fund/template tests/fund/audit tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Result: `190 passed`.

```text
uv run ruff check fund_agent/fund/template/contracts.py fund_agent/fund/audit/contract_rules.py tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
```

Result: `All checks passed`.

```text
git diff --check
```

Result: clean.

Boundary check:

- `git diff --name-only` showed only the seven accepted files.
- Diff against renderer, Service, UI, FQ0-FQ6, extraction score, and document/source paths was empty.

## Residuals

| Residual | Owner / next gate | Blocking? |
|---|---|---|
| Current renderer does not emit the new gap wording marker. | Future renderer/report-writing gate | No |
| Runtime `ContractRequiredItemRule` for gap wording remains deferred. | Future renderer/report-writing gate after product output can satisfy it | No |
| Turnover/style-change extraction remains incomplete. | Future data/source extraction gate only if same-source evaluation requires it | No |
| Template draft vs machine contract asymmetry needs care. | Future renderer/report-writing or contract robustness gate | No |
| Fallback-blocked index/QDII and pure FOF coverage remain unresolved. | Source recovery / corpus / fund-type taxonomy gates | No |
| Durable baseline remains blocked. | Curated-fixture gate after reviewed facts and clean validation | No |

## Next Entry Point

Current goal's local development loop is accepted through Gate D.

The queued next user request is a more aggressive real-iteration gate:

`small baseline real evaluation run + first concrete quality fix + dev-only reporting tool`

Before entering that queued goal, the controller must reread the Startup Packet and reconcile the latest accepted commit, current gate, accepted artifacts, and verifier matrix.
