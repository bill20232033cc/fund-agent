# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Implementation Evidence

Date: 2026-06-14

Role: AgentCodex implementation worker, not controller

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate`

Release/readiness: `NOT_READY`

## 1. Scope

Implemented the accepted narrow Chapter 2 `l1_numerical_closure` deterministic evidence-gap / minimum-verification route under no-live boundaries.

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command was run. No staging, commit, push, PR, merge, source-policy, fallback, provider default, repair budget, annual-period LLM route or Docling change was made.

Production Python source was not touched.

## 2. Files Changed

| File | Reason |
|---|---|
| `docs/fund-analysis-template-draft.md` | Changed only seven Chapter 2 required-output `when_evidence_missing` values and exact `missing_evidence_reason` text. |
| `tests/fund/template/test_typed_contracts.py` | Added exact Ch2 behavior/reason assertions and structure-preservation assertions. |
| `tests/fund/test_chapter_writer.py` | Added Ch2 writer positive gap/minimum-verification tests, missing `EvidenceAvailability` fail-closed test and gap-specific issue-id test. |
| `tests/services/test_chapter_orchestrator.py` | Added Ch2 typed missing-evidence accepted path and available-fact L1 one-repair fail-closed path. |
| `tests/agent/test_runner.py` | Added Agent runner Ch2 positive and unsafe-output no-live coverage. |
| `tests/services/test_fund_analysis_service_llm.py` | Added Service final-assembly positive and negative no-live coverage for Ch2 gap behavior. |

Not changed: `tests/fund/test_chapter_auditor.py` already covered safe Ch2 gap/minimum-verification pass and concrete unanchored percentage L1 fail; `tests/fund/test_evidence_availability.py` already covered Ch2 requirement mapping.

Existing unrelated dirty/untracked workspace residue was left untouched.

## 3. Exact Missing Evidence Reasons

| Required-output ids | Behavior | Exact `missing_evidence_reason` |
|---|---|---|
| `ch2.required_output.item_01`, `ch2.required_output.item_02` | `render_evidence_gap` | `第 2 章同源已复核净值增长率与业绩基准证据不足时只能输出证据缺口，不得编造近 1/3/5 年收益数值。` |
| `ch2.required_output.item_03`, `ch2.required_output.item_04` | `render_minimum_verification_question` | `第 2 章同源已复核 R 与 B 证据不足时只能输出下一步最小验证问题，不得给出 Alpha 或稳定性结论。` |
| `ch2.required_output.item_05`, `ch2.required_output.item_06` | `render_evidence_gap` | `第 2 章同源已复核费用与成本证据不足时只能输出证据缺口，不得编造费率、交易成本或成本合理性判断。` |
| `ch2.required_output.item_07` | `render_minimum_verification_question` | `第 2 章同源已复核 R、B 与 C 证据不足时只能输出下一步最小验证问题，不得输出具体 R=A+B-C 数字闭环。` |

`missing_evidence_reason` carries the domain insufficiency reason. Existing writer prompt instructions continue to carry output mechanics: output marker requirement, status, required gap phrase or minimum-verification phrase and no positive conclusion.

## 4. Boundary Assertions

- Chapter 2 item ids, order, text, chapter structure and internal subcontract ids remain unchanged.
- Gap/minimum-verification behavior applies only when typed `EvidenceAvailability` is non-available: `missing`, `unavailable`, `unreviewed` or `not_applicable`.
- Available facts with anchors remain `render`; if writer ignores them and emits unanchored concrete `R/A/B/C/A-C` percentages, current L1 `l1_numerical_closure` fail-closed behavior remains.
- Missing `EvidenceAvailability` envelope remains fail-closed with `ValueError`; it is not treated as product evidence absence.
- Existing `writer:required_output_block:` semantics are preserved for block cases. Non-available defective gap/verification output now uses specific issue ids such as `writer:required_output_gap_missing:*`.
- `max_repair_attempts` remains unchanged; tests prove current one-repair semantics with two writer attempts when available facts produce repeated L1 failures.
- EID single-source/no-fallback policy is untouched. Eastmoney, fund-company, CNINFO and fallback routes were not added.
- Release/readiness remains `NOT_READY`.

## 5. Validation

```text
$ uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/test_evidence_availability.py -q
260 passed in 1.42s
```

```text
$ uv run ruff check tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/test_evidence_availability.py
All checks passed!
```

```text
$ git diff --check
passed with no output
```

Source files were not touched, so ruff did not need extension to production source files.

## 6. Residuals

| Residual | Disposition |
|---|---|
| No-live tests cannot prove future live LLM wording compliance. | Carried to future bounded live/provider evidence gate. |
| Exact live sample fact-absence vs present-but-ignored ambiguity is not proven under this no-live boundary. | Preserved by typed availability discriminator and available-fact L1 fail-closed tests. |
| Release/readiness remains incomplete. | `NOT_READY`; no readiness or release claim made. |

## 7. Verdict

`VERDICT: IMPLEMENTED_AND_VALIDATED_NO_LIVE_NOT_READY`

Self-check: pass. Scope stayed within assigned gate/write set; no commit/push/PR; artifact, validation and residuals are complete.
