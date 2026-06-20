PR_REVIEW_PASS

## Findings

No blocking findings.

本 review 未发现阻塞性 finding。PR 33 的当前 diff 与本 gate 的 stacked PR surface、source-truth direct extraction 范围和 hard-stop 边界一致。

## Mandatory Checks

- PR metadata: GitHub PR 33 当前为 draft/open，title `FundDisclosureDocument current_stage source-truth extraction`，base `funddisclosure-investor-experience-source-truth`，head `funddisclosure-current-stage-source-truth`，current head oid `ada31d89a4ec3ff7604df47f1b880c699f3b2a3e`，base oid `f81030d956780a2d0a4b4a101012c98e060a29c8`。这与用户指定 stacked surface 匹配。PR 当前 mergeStateStatus 为 `CLEAN`，CI `test` 为 `SUCCESS`。
- PR scope: PR diff 为 19 files changed, +1887/-40；文件面只包含 current_stage source-truth implementation、processor/facade tests、Fund README、design/control/startup docs 和 gate artifacts。未改 Service/UI/Host/renderer/quality-gate、document source/parser modules 或 public extractor model schema。
- Allowed public keys: `fund_agent/fund/processors/fund_disclosure_processor.py:357` 固定 current_stage required top-level 为 `basic_identity`、`share_change`、`holdings_snapshot`、`portfolio_managers`；`fund_agent/fund/processors/fund_disclosure_processor.py:6597` 只在有值时追加 `schema_version="current_stage.v1"`。测试在 `tests/fund/processors/test_fund_disclosure_processor.py:6291` 明确断言 public keys 精确为五个 allowed keys。
- No bundle current_stage / semantic judgment: `StructuredFundDataBundle` dataclass 在 `fund_agent/fund/data_extractor.py:193` 起没有 `current_stage` 字段；projection docstring 明确 `current_stage.v1 -> informational/redundant，不投影`，见 `fund_agent/fund/data_extractor.py:719` 到 `fund_agent/fund/data_extractor.py:725`；projection 只读取 product/return/manager/investor/core families，见 `fund_agent/fund/data_extractor.py:729` 到 `fund_agent/fund/data_extractor.py:735`。tests 断言 no bundle projection，见 `tests/fund/test_data_extractor.py:1111`、`tests/fund/test_data_extractor.py:1188`、`tests/fund/test_data_extractor.py:1424`。
- Direct route candidate evidence: `_field_families_for_intermediate()` 只在 `source_truth_extraction_allowed` 时调用 current_stage direct extractor，见 `fund_agent/fund/processors/fund_disclosure_processor.py:986` 到 `fund_agent/fund/processors/fund_disclosure_processor.py:1001`；direct-route evidence suppression 在 `fund_agent/fund/processors/fund_disclosure_processor.py:1023` 到 `fund_agent/fund/processors/fund_disclosure_processor.py:1028`；direct result 固定 `candidate_evidence=()`，见 `fund_agent/fund/processors/fund_disclosure_processor.py:6487` 到 `fund_agent/fund/processors/fund_disclosure_processor.py:6496`。direct missing test 覆盖 `status="missing"`、`value={}`、`anchors=()`、`candidate_evidence=()`，见 `tests/fund/processors/test_fund_disclosure_processor.py:6357` 到 `tests/fund/processors/test_fund_disclosure_processor.py:6364`。
- Proof-missing/proof-invalid/candidate-boundary fail-closed: admission helper 在 missing provenance / failure_class / candidate_boundary 下阻断或 blocked，见 `fund_agent/fund/processors/fund_disclosure_dispatch.py:101` 到 `fund_agent/fund/processors/fund_disclosure_dispatch.py:130`；positive proof validation 要求 proof、identity、source kind 和 candidate/failure/provenance 全部合法，见 `fund_agent/fund/processors/fund_disclosure_processor.py:1072` 到 `fund_agent/fund/processors/fund_disclosure_processor.py:1118`；tests 覆盖 missing proof、invalid proof、candidate boundary，见 `tests/fund/processors/test_fund_disclosure_processor.py:6367`、`tests/fund/processors/test_fund_disclosure_processor.py:6406`、`tests/fund/processors/test_fund_disclosure_processor.py:6444`。
- core_risk remains candidate-only/missing: PR 没有 `_extract_core_risk_source_truth`，core risk candidate selector仍在 `fund_agent/fund/processors/fund_disclosure_processor.py:1028` 无条件走 candidate evidence；test `test_current_stage_source_truth_does_not_implement_core_risk` 断言 core_risk remains missing with candidate evidence，见 `tests/fund/processors/test_fund_disclosure_processor.py:6491` 到 `tests/fund/processors/test_fund_disclosure_processor.py:6540`。
- No parser replacement / schema expansion / upper-layer consumption: `git diff --name-status funddisclosure-investor-experience-source-truth...HEAD` 显示无 `fund_agent/fund/documents/`、`fund_agent/services/`、`fund_agent/ui/`、`fund_agent/host/`、renderer、audit 或 quality-gate implementation changes；targeted diff for those paths is empty. No `EvidenceSourceKind` or public `EvidenceAnchor` schema file changed.
- Docs/gate artifact consistency: plan, implementation evidence, DS code review, DS aggregate review and controller judgments agree on five allowed keys, no bundle projection, direct-route candidate evidence empty, fail-closed proof boundary, and `core_risk.v1` remaining unimplemented. `docs/design.md` and `fund_agent/fund/README.md` state current_stage source-truth as fact-input only and preserve NOT_READY / no parser replacement / no upper-layer consumption boundaries.

## Residual Risks / Test Gaps

- I did not rerun local pytest/ruff during this PR review to avoid creating any cache or generated files under the user's "write exactly one artifact" constraint. Validation relied on PR CI `test` success and existing gate evidence: processor tests `181 passed`, facade tests `40 passed`, ruff passed, `git diff --check` passed.
- PR creation-time docs still record the PR head at creation (`4ddae7b`) and CI queued/UNSTABLE state. Current GitHub metadata is newer: head `ada31d8`, merge state `CLEAN`, CI `test` success. This is not a code blocker; this review artifact records the current PR state.
- `current_stage.v1` remains a fact-input family only. Any semantic current-stage summary, bundle-level current_stage projection, market/valuation judgment, or final hold/replace output remains a separate schema/public-contract gate.
- `core_risk.v1` remains the only FDD field family without source-truth direct extraction and requires a separate planned work unit.
- Existing untracked workspace files are outside PR 33 and were excluded from this PR review scope: `docs/reviews/pr-33-review-ds-20260620.md` plus unrelated docs/scripts shown by `git status --short`.

## PR Metadata / Validation Summary

- Repository: `bill20232033cc/fund-agent`
- PR: `33`
- URL: `https://github.com/bill20232033cc/fund-agent/pull/33`
- Author: `bill20232033cc`
- Base: `funddisclosure-investor-experience-source-truth`
- Head: `funddisclosure-current-stage-source-truth`
- State: `OPEN`
- Draft: `true`
- Merge state: `CLEAN`
- CI: `test` success, completed at `2026-06-20T08:00:18Z`
- Current local branch: `funddisclosure-current-stage-source-truth`
- Current local head: `ada31d89a4ec3ff7604df47f1b880c699f3b2a3e`
- PR diff validation: `git diff --check funddisclosure-investor-experience-source-truth...HEAD` passed with no output.

## Stop Condition Status

Stop condition satisfied: wrote exactly this artifact at `docs/reviews/pr-33-review-codex-20260620.md`; no code/docs changes beyond this artifact, no commit, no push, no mark-ready, no merge, no subsequent gate entered.
