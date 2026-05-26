# Fund-layer CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit Controller Judgment

> Date: 2026-05-26
> Role: Controller
> Gate: Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation
> Verdict: ACCEPTED_AFTER_FIXES

## Scope

This judgment covers the implementation of:

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`

The accepted implementation remains Fund-layer only. It does not modify the v0 renderer, FQ0-FQ6 quality gate, Service/CLI default analyze/checklist paths, Host/Agent packages, Dayu runtime, document repository, PDF/cache/source helpers, downloaders, or production extractors.

## Evidence Chain

| Purpose | Artifact |
|---|---|
| Implementation plan | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-mimo-20260526.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-glm-20260526.md` |
| Plan controller judgment | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-controller-judgment-20260526.md` |
| Implementation evidence | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md` |
| Code review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-mimo-20260526.md` |
| Code review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-glm-20260526.md` |
| Re-review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview-mimo-20260526.md` |
| Re-review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview-glm-20260526.md` |
| Targeted re-review 2: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview2-glm-20260526.md` |

## Controller Findings Judgment

| Finding | Source | Judgment | Rationale |
|---|---|---|---|
| Compatible Chapter 3 `data_gap` could pass without insufficient-evidence wording when no positive stability claim was present. | MiMo High | Accepted and fixed | The gate requires explicit insufficient-evidence disclosure whenever active-fund Chapter 3 turnover/style evidence is missing and represented by a compatible data gap. |
| Reviewed fact with dangling `source_anchor_ids` could satisfy required evidence. | MiMo High | Accepted and fixed | Evidence-anchor integrity is central to the contract; facts used to satisfy the requirement must reference resolvable anchors. |
| Malformed records `report_year` could raise instead of returning issue-based fail-closed output. | MiMo Medium | Accepted and fixed | The dev-only audit API promises deterministic issue output for caller-supplied records. |
| Conflicting explicit Chapter 3 `fund_type_slot` values could silently disable active-fund audit. | GLM Major | Accepted and fixed | Input contradiction must fail closed; otherwise the active-fund Chapter 3 contract can be bypassed. |
| Records helper could fabricate compatible data gaps from missing `reason_code` / `field_path` defaults. | GLM Major | Accepted and fixed | Compatibility-bearing fields must be explicit; otherwise required evidence can be masked by parser defaults. |
| Duplicate occurrence-level `issue_id` values may appear for repeated drafts. | GLM Minor | Deferred | Current ids are deterministic issue class ids. Occurrence-level ids require draft locators or ordinals and are outside this first sidecar slice. |
| Mixed valid + dangling anchor ids still satisfied required evidence after first fix. | GLM Re-review Major | Accepted and fixed in Fix2 | The accepted anchor contract is stricter than "any anchor resolves"; all declared fact anchors must resolve before the fact can satisfy required evidence. |

## Accepted Implementation Behavior

- The sidecar wraps the existing CHAPTER_CONTRACT manifest and adds executable constraints without creating a parallel chapter truth.
- Default constraints cover chapters 0-7 and preserve existing `must_answer` / `must_not_cover` values.
- The first material slice enforces active-fund Chapter 3 turnover/style-consistency evidence.
- A reviewed fact satisfies the active Chapter 3 requirement only when it has a supported fact id, reviewed status, accepted extraction mode, non-empty value, non-empty `source_anchor_ids`, and all declared anchors resolve in `bundle.evidence_anchors`.
- A compatible `data_gap` can downgrade the requirement only when the report draft preserves insufficient-evidence wording and the next minimum validation question.
- Positive style stability / style consistency / words-actions-consistent claims remain unsupported when only a data gap exists.
- Records-mode inputs fail closed for malformed `report_year`, conflicting Chapter 3 explicit fund types, or incomplete compatibility-bearing data-gap fields.

## Verifier Matrix

| Check | Command / Evidence | Result |
|---|---|---|
| Focused tests | `uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py` | `19 passed` |
| Adjacent tests | `uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py` | `147 passed` |
| Ruff | `uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py` | Passed |
| Boundary grep | Forbidden keywords for renderer, quality gate, Service/CLI, repository/PDF/cache/source/extractor, Host/Agent/dayu, `extra_payload` | No forbidden production-chain matches |
| Re-review | MiMo re-review and GLM targeted re-review 2 | Passed |

## Residual Risks

- Duplicate occurrence-level `issue_id` uniqueness is deferred to a later audit-output ergonomics slice.
- Per-file coverage measurement could not be completed locally because coverage collection hit the existing numpy import issue recorded in the implementation evidence. Focused tests cover the accepted material behavior.
- Phrase matching remains a deterministic surrogate for the first active Chapter 3 slice, not full natural-language claim coverage.
- Records-mode gap parsing is intentionally fail-closed and narrow to this active Chapter 3 slice; broader records ingestion needs a future design gate.

## Next Entry Point

Close out this gate with README / design / control-doc synchronization, final validation, and a local accepted commit. The next implementation gate should not connect this audit to renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent, or Dayu runtime without a separate explicit gate.
