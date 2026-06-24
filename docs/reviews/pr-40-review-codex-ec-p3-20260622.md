# Code Review

## Scope

- Mode: PR
- Branch or PR: PR #40, `https://github.com/bill20232033cc/fund-agent/pull/40`
- Repository: `bill20232033cc/fund-agent`
- Author: `bill20232033cc`
- Title: `Add Evidence Confirm productionization materializer, live pathway, and semantic contract`
- Head branch / OID observed: `evidence-confirm-productionization` / `972b8f0730f3547ab846f51072c9fc98c12bf2cc`
- Base branch / OID observed: `evidence-confirm-anchor-audit-score` / `dc586516e9f122670dc97a8c62474c9303fb6621`
- Local branch / HEAD: `evidence-confirm-productionization` / `972b8f0730f3547ab846f51072c9fc98c12bf2cc`
- Review timestamp: `2026-06-22 20:07:36 CST`
- Output file: `docs/reviews/pr-40-review-codex-ec-p3-20260622.md`
- Included scope: PR-40 diff for EC-P1A annual-report reference materializer, EC-P2 repository-bounded runner and authorized sample script, EC-P3 semantic entailment companion contract, related tests, Fund/tests README deltas, control docs, PR body, prior accepted review artifacts directly referenced by the gate.
- Excluded scope: no Service/UI/Host/renderer/quality-gate implementation review beyond boundary verification; no live/PDF/provider commands; no mark-ready/merge/reviewer request/PR edit.
- Parallel review coverage: 无。

## Findings

### 001-未修复-[中]-semantic client 可以返回自相矛盾的 status/reason 并被聚合为 pass

- **入口/函数**: `confirm_semantic_entailment()` -> `_confirm_single_claim()` -> `_judgment_is_valid()` / `_severity_for_judgment()` / `_overall_status()`
- **文件(行号)**: `fund_agent/fund/evidence_confirm_semantic.py:272`, `fund_agent/fund/evidence_confirm_semantic.py:427`, `fund_agent/fund/evidence_confirm_semantic.py:451`, `fund_agent/fund/evidence_confirm_semantic.py:515`
- **输入场景**: deterministic V2 已通过、bounded excerpt 存在，注入的 `EvidenceEntailmentClient` 返回 `EvidenceEntailmentJudgment(status="entailed", reason_code="contradicted_by_excerpt")`。
- **实际分支**: `_judgment_is_valid()` 只校验返回对象类型、`status` literal 闭集、`reason_code` literal 闭集；该组合通过校验。随后 `_severity_for_judgment()` 只按 `status` 计算 severity，`status="entailed"` 得到 `info`；`_overall_status()` 看到 entailed 且无 block/warn 后返回 `pass`。
- **预期行为**: semantic companion contract 的 `status` 与 `reason_code` 都是对外稳定语义，`contradicted_by_excerpt` 不能与 `entailed` 组合成通过结果。此类 client 输出应按 `malformed_client_result` fail-closed，避免未来 provider adapter 或 fake client bug 把矛盾判断投影为 pass。
- **实际行为**: 自相矛盾的 client judgment 会保留 `reason_code="contradicted_by_excerpt"`，但以 `status="entailed"` 驱动 severity/aggregate，最终可产生 semantic `overall_status="pass"`。
- **直接证据**: `_judgment_is_valid()` 的布尔条件只包含 `isinstance(judgment, EvidenceEntailmentJudgment)`、`judgment.status in _SEMANTIC_STATUSES`、`judgment.reason_code in _SEMANTIC_REASON_CODES`，没有 status/reason compatibility 表；`_severity_for_judgment()` 对 `entailed` 默认返回 `info`；`_overall_status()` 对任一 `entailed` 且无 block/warn 返回 `pass`。现有 malformed 测试只覆盖 `object()` 非 dataclass 返回，未覆盖合法 literal 但语义冲突的 pair：`tests/fund/test_evidence_confirm_semantic.py:284`。
- **影响**: 语义复核 contract 可产生外部可见的 incoherent result；后续 Service/renderer/quality-gate 或 provider-backed adapter 接入时，provider/client mapping bug 可能把 contradiction reason 隐藏在 pass aggregate 后面。 deterministic V2 source/proof/value authority 不会被绕过，但 EC-P3 semantic contract 本身的 fail-closed 边界不完整。
- **建议改法和验证点**: 增加 status -> allowed reason codes 显式表，例如 `entailed -> {"entailed_by_excerpt"}`、`contradicted -> {"contradicted_by_excerpt"}`、`insufficient -> {"insufficient_excerpt_support"}`、`not_applicable -> {"not_applicable"}`，并保留内部 fail-closed reason codes 只由本模块生成。扩展 `_judgment_is_valid()` 或新增 `_judgment_reason_matches_status()`，不匹配时返回 `malformed_client_result`。新增测试：passing deterministic V2 + client returns `status="entailed", reason_code="contradicted_by_excerpt"`，断言 `overall_status == "fail"`、claim `reason_code == "malformed_client_result"`。
- **修复风险（低/中/高）**: 低。变更局限于 semantic module client-output validation，不触碰 V1/V2 deterministic result schema、repository/source/PDF、Service/UI/renderer/quality-gate 或 provider path。
- **严重程度（低/中/高/严重）**: 中。

## Open Questions

- 无。

## Residual Risk

- Same-run binding between `EvidenceConfirmResultV2` and `references` still relies on anchor ids rather than excerpt hash/reference identity. This is already classified in accepted EC-P3 controller judgment as later Service/UI/renderer/quality-gate integration work, not a blocker for the no-live companion slice.
- Provider-backed semantic quality remains unproven and is correctly classified as a later controlled semantic provider evidence gate.
- Service/renderer claim extraction and quality-gate consumption are not implemented in this PR and remain later gates.
- Release/readiness remains `NOT_READY`.
- Control docs in this PR still record CI/head observations from the prior push/update checkpoint in places; this review records the current observed PR state below and does not treat that as a code correctness blocker.

## Checked Evidence

- `AGENTS.md` instructions from the user prompt.
- `docs/design.md`: Evidence Confirm is still described as Fund-layer no-live V1/V2 helper; Service/UI/Host/renderer/quality-gate/readiness integration remains non-current.
- `docs/current-startup-packet.md` and `docs/implementation-control.md`: current entry remains PR-40 EC-P3 PR review; release/readiness and external PR state changes are unauthorized.
- PR body: explicitly says EC-P3 is no-live semantic companion, deterministic V2 remains authoritative, no provider-backed semantic quality proof, no Service/UI/renderer/quality-gate integration, no readiness/release promotion, and PR remains draft.
- EC-P1A/EC-P2 code paths reviewed: `build_annual_report_evidence_confirm_references()`, `run_repository_bounded_evidence_confirm()`, source provenance admission, materializer failure propagation, V2 mismatch handling, authorized sample safe payload.
- EC-P3 code path reviewed: deterministic gate guard, bounded excerpt selection, client exception/malformed result handling, severity mapping, aggregate status mapping, import isolation.
- Related tests reviewed: `tests/fund/test_evidence_confirm_sources.py`, `tests/fund/test_evidence_confirm_semantic.py`.
- Prior EC-P3 accepted artifacts reviewed: aggregate deepreview fix, DS/MiMo targeted re-reviews, AgentCodex after-fix aggregate review, and controller judgment.
- Commands run for review only: `git branch --show-current`, `git status --short`, `git rev-parse HEAD`, `gh repo view`, `gh pr view 40`, `gh pr diff 40 --name-only`, `gh pr checks 40`, local `git diff`/`rg`/`sed`/`nl` reads.

## CI / PR State Observed

- PR state: `OPEN`
- Draft: `true`
- Mergeable: `MERGEABLE`
- Review decision: empty
- Head observed by `gh pr view`: `972b8f0730f3547ab846f51072c9fc98c12bf2cc`
- Local HEAD: `972b8f0730f3547ab846f51072c9fc98c12bf2cc`
- Check observed by `gh pr checks 40`: `test` pass, duration `55s`, job `https://github.com/bill20232033cc/fund-agent/actions/runs/27943703378/job/82683039485`

## Conclusion

FAIL. PR-40 has one accepted candidate finding for EC-P3 semantic contract validation. The PR body does not overclaim provider-backed semantic quality, Service/UI/renderer/quality-gate production integration, release/readiness, or mark-ready/merge state.
