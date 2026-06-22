# Code Review: EC-P4 Slice 6 — Docs Sync and Control Evidence

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `code review - Slice 6 Docs Sync and Control Evidence`
- Branch: `evidence-confirm-productionization`
- Review artifact: `docs/reviews/code-review-20260623-001200-mimo-ec-p4-slice6.md`
- Implementation evidence artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice6-docs-sync-evidence-20260623.md`

## Verdict

**PASS**

## Scope

Changed files reviewed:

- `README.md`
- `fund_agent/README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice6-docs-sync-evidence-20260623.md`

Forbidden files verified not edited: `docs/implementation-control.md`, `docs/current-startup-packet.md`, production source files, test source files.

## Review Focus Verification

### 1. Docs match accepted Slice 1-5 implementation behavior

**PASS** — All documentation changes are additive and consistent with accepted Slice 1-5 code:

- `README.md`: Adds `--evidence-confirm-policy off|warn|block` parameter row, default-no-call statement, dev-override opt-in paragraph, and ECQ projection paragraph. All match `fund_agent/ui/cli.py:747` (option definition), `fund_agent/services/fund_analysis_service.py:1330` (off=no-run), and `fund_agent/fund/quality_gate_integration.py:173` (ECQ projection).
- `fund_agent/README.md`: Adds Evidence Confirm opt-in to Service boundary description and renderer non-rendering bullet. Matches `fund_agent/services/fund_analysis_service.py:1306` and `fund_agent/fund/template/renderer.py` (no evidence_confirm references).
- `fund_agent/fund/README.md`: Adds `EvidenceConfirmProductionSummary` import, production summary section, ECQ table, quality gate integration section, and module summary entries. All match `fund_agent/fund/evidence_confirm_production.py` and `fund_agent/fund/quality_gate_integration.py` source.
- `tests/README.md`: Adds `test_evidence_confirm_production.py` test entry and combined test command. Matches existing test file.
- `docs/design.md`: Adds Evidence Confirm opt-in section with policy semantics, ECQ projection, semantic companion boundary, and future/candidate boundary. All match source implementation.

### 2. No overclaim verification

**PASS** — Four overclaim checks executed via `rg` with no positive hits:

- **Default-on Evidence Confirm**: All docs consistently state "默认 `analyze` 和 `checklist` 都不会调用 Evidence Confirm". Source at `fund_analysis_service.py:1330` confirms `if policy == "off": return None`.
- **Release/readiness**: `docs/design.md:892` explicitly states "Release/readiness remains `NOT_READY`". No doc claims readiness or release.
- **Provider-backed semantic quality/client**: All docs consistently state "当前不构造 provider-backed semantic client". Source `evidence_confirm_semantic.py` only accepts injected `EvidenceEntailmentClient`.
- **Checklist Evidence Confirm CLI support**: All docs consistently state "checklist CLI 支持属于后续单独 gate". `cli.py:907` confirms checklist function has no `--evidence-confirm-policy` parameter.

### 3. Policy `off` documented as no-run/off, only `warn|block` call runner

**PASS** — Verified at three levels:

- `docs/design.md:887`: "`off` 是显式 no-run/off policy，不调用 Evidence Confirm runner；`warn|block` 才通过 Service 调用 Fund 层 repository-bounded runner"
- `fund_analysis_service.py:1330`: `if policy == "off": return None`
- `fund_analysis_service.py:1335`: `warn|block` path calls `self._evidence_confirm_runner()`
- `fund_analysis_service.py:1679`: checklist always returns `"off"` regardless of contract

### 4. Renderer non-rendering and CLI/UI summary outside report body

**PASS** — Verified at two levels:

- `fund_agent/README.md`: "Renderer 当前不渲染 Evidence Confirm。`fund_agent/fund/template/renderer.py` 只生成既有 8 章报告 Markdown；Evidence Confirm summary 属于 CLI/UI 与 quality gate metadata，不进入投资报告正文或证据附录。"
- `renderer.py`: `rg` returns no `evidence.confirm` references.
- `README.md`: "该摘要不包含年报原文 excerpt、PDF/cache 路径、parser JSON 或 source adapter 对象；报告 Markdown 正文不渲染 Evidence Confirm 段落"
- `cli.py:2664-2668`: `_echo_evidence_confirm_summary()` writes to stderr only.

### 5. ECQ0-ECQ4 taxonomy accurate and limited to compact summary consumption

**PASS** — Source at `quality_gate_integration.py:173-288` confirms:

| Rule | Doc claim | Source implementation |
|------|-----------|----------------------|
| ECQ0 | not-run info | `summary is None` or `status == "not_run"` → `SEVERITY_INFO` |
| ECQ1 | pathway fail | `pathway_status == "fail"` → policy-dependent severity |
| ECQ2 | deterministic V2 hard-gate fail | `deterministic_status == "fail"` → policy-dependent severity |
| ECQ3 | deterministic V2 warn | `deterministic_status == "warn"` → `SEVERITY_WARN` |
| ECQ4 | semantic companion fail/warn | `semantic_status in {"fail", "warn"}` → policy-dependent severity |

All ECQ projection functions only consume `EvidenceConfirmProductionSummary`, confirmed by docstring "只消费调用方传入的 compact summary，不读取 repository、PDF/cache、source adapter、parser、Docling、provider 或 LLM" at line 181.

### 6. Docs don't direct Service/UI/renderer/quality gate to access internals

**PASS** — All docs consistently document boundary separation:

- Service: "Service 不读取 PDF、cache、source helper、parser artifact，也不构造 provider-backed semantic client"
- ECQ: "ECQ 投影不读取文档仓库、PDF/cache、source helper、parser artifact、renderer、provider 或 LLM"
- Renderer: "Evidence Confirm summary 属于 CLI/UI 与 quality gate metadata，不进入投资报告正文或证据附录"
- Summary: "摘要字段只包含...不包含原文 excerpt、PDF/cache 路径、parser JSON、source adapter 对象或 provider payload"

### 7. Evidence artifact records validation and residual risks

**PASS** — Implementation evidence artifact at `docs/reviews/evidence-confirm-productionization-ec-p4-slice6-docs-sync-evidence-20260623.md` records:

- Executed validation: broad `rg` returned only negative/boundary statements; positive-overclaim `rg` returned no hits; `git diff --check` passed; trailing whitespace check passed.
- Residual risks table with 4 items, each with classification and owner assignment:
  - Checklist EC CLI support absent → later work unit
  - Provider-backed semantic quality not implemented → later work unit
  - Default-on EC not authorized → later work unit
  - Release/readiness remains blocked → existing control truth
- Forbidden file list explicitly verified.

## Findings

**0 findings.**

## Blocking Open Questions

None.
