# Code Review

## Scope

- Mode: PR
- Branch or PR: PR #34 `FundDisclosureDocument core_risk source-truth extraction`
- Repository: `bill20232033cc/fund-agent`
- URL: `https://github.com/bill20232033cc/fund-agent/pull/34`
- Author: `bill20232033cc`
- Draft: `true`
- Base: `funddisclosure-current-stage-source-truth`
- Head: `funddisclosure-core-risk-source-truth`
- Expected head: `24c6761f9da81110cc303a187680c952a2c98354`
- Observed head: `24c6761f9da81110cc303a187680c952a2c98354`
- Merge state: `CLEAN`
- CI/check information: `test` check `SUCCESS`, completed 2026-06-20T09:25:41Z, duration 51s
- Output file: `docs/reviews/pr-34-review-codex-20260620.md`
- Included scope: PR metadata/body, GitHub PR diff, changed implementation/tests/docs, accepted core-risk plan/controller artifacts, explicit next-entry residue check in `docs/current-startup-packet.md` and `docs/implementation-control.md`
- Excluded scope: no full repository review; no local test rerun beyond CI verification; no code edits, staging, commit, push, PR mutation or GitHub review action
- Parallel review coverage: 无

## Findings

### F1-未修复-[中]-控制文档仍指向过期 next-entry，PR review gate 无法从真源恢复
- **入口/函数**: Controller resume / next gate selection from `docs/current-startup-packet.md` and `docs/implementation-control.md`
- **文件(行号)**: `docs/current-startup-packet.md:23`, `docs/current-startup-packet.md:24`, `docs/current-startup-packet.md:63`, `docs/implementation-control.md:10`, `docs/implementation-control.md:50`, `docs/implementation-control.md:51`, `docs/implementation-control.md:555`
- **输入场景**: Agent/controller after PR #34 creation or this PR review gate resumes from the repository control docs and uses the documented next-entry fields to decide the current gate.
- **实际分支**: PR #34 exists as a draft PR with base `funddisclosure-current-stage-source-truth`, head `funddisclosure-core-risk-source-truth`, observed head `24c6761f9da81110cc303a187680c952a2c98354`, merge state `CLEAN`, and CI `test` SUCCESS. The PR create controller artifact says next gate is `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Gate`.
- **预期行为**: Current control surfaces should identify the current/next gate as PR review or at least not point to completed earlier gates. They must not tell a resumed agent that push/PR are unauthorized after a draft PR already exists and CI is complete.
- **实际行为**: `docs/current-startup-packet.md:23-24` still says `Implementation Gate Completed Locally`, `pending code review`, next entry `Code Review Gate`, and "No commit/stage/push/PR"; `docs/current-startup-packet.md:63` repeats `Code Review Gate`. `docs/implementation-control.md:10` and `docs/implementation-control.md:50-51` repeat implementation/code-review wording and "No ... push/PR". `docs/implementation-control.md:555` still says current next entry is `FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Follow-up Push Gate`.
- **直接证据**: GitHub PR metadata from `gh pr view 34` reports corrected PR state at head `24c6761f9da81110cc303a187680c952a2c98354`, merge state `CLEAN`, and `statusCheckRollup[0].conclusion="SUCCESS"`. PR artifact `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-create-draft-pr-controller-judgment-20260620.md` records next gate as `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Gate`, while the current control docs retain older next-entry strings at the cited lines.
- **影响**: Control truth is stale. A resumed controller/agent can route to an already-completed code review/push workflow, deny already-authorized PR state, or resurrect an older `current_stage` push gate. This is not an implementation data extraction bug, but it is a gate-control correctness issue in the PR diff.
- **建议改法和验证点**: Update both current control surfaces so current/next gate reflects PR #34 PR review state, with PR number, head OID, merge state and CI pass if desired. Remove the old `No ... push/PR` and `current_stage ... Follow-up Push Gate` residue from active/current sections or clearly move it to historical evidence-chain context. Verify with `rg -n "Code Review Gate|No commit/stage/push/PR|current_stage.v1 Source-truth Direct Extraction Follow-up Push Gate|PR Review Gate" docs/current-startup-packet.md docs/implementation-control.md`.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Verified Non-Findings

- PR body after correction is now scoped correctly: it states only `core_risk.v1.risk_characteristic_text` is implemented, explicitly denies complete `core_risk.v1` source truth, lists the four deferred roles, and denies parser replacement, `EvidenceSourceKind`/public anchor expansion, `StructuredFundDataBundle.core_risk`, upper-layer consumption, real-report correctness, readiness, release, mark-ready and merge.
- Stacked base/head are correct on GitHub: base `funddisclosure-current-stage-source-truth`, head `funddisclosure-core-risk-source-truth`.
- PR head matches the requested current head: `24c6761f9da81110cc303a187680c952a2c98354`.
- CI status is pass: `test` check succeeded.
- Implementation diff matches the accepted `core_risk.v1.risk_characteristic_text` source-truth scope: `fund_agent/fund/processors/fund_disclosure_processor.py` only adds the proof-positive direct route for `core_risk.v1`, builds a public value with `schema_version` and `risk_characteristic_text`, emits only annual-report anchors for the emitted subvalue, suppresses candidate evidence on direct route, and exposes the other four roles only as `required=False` `deferred_role` gaps.
- Tests cover the core boundary: positive direct extraction, direct missing with candidate suppression, ambiguous text fail-closed, proof missing, invalid proof, candidate boundary, candidate-token suppression, forbidden public keys, facade fallback to `StructuredFundDataBundle.risk_characteristic_text`, product-essence precedence, and absence of `StructuredFundDataBundle.core_risk`.
- No parser replacement, repository/source/cache/PDF/Docling/pdfplumber, Service/UI/Host/renderer/quality-gate, `EvidenceSourceKind`, public `EvidenceAnchor`, `StructuredFundDataBundle.core_risk`, readiness, release, mark-ready, merge, or complete core-risk claim was found in the implementation/test diff.

## Open Questions

- 无

## Residual Risk

- Local branch `funddisclosure-current-stage-source-truth` resolves to a different OID than the GitHub PR base OID observed from `gh pr view`; this review therefore used GitHub PR metadata/diff as the authoritative PR surface and local checked-out head only for line-level code reading.
- Local workspace already contained unrelated untracked files before this review. They were not reviewed or modified.
- Complete `core_risk.v1` source truth remains deferred; this PR only covers `risk_characteristic_text`.

## Verdict

PR_REVIEW_FAIL
