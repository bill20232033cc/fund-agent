# Evidence Review: 004393 / 004194 / 006597 Strict Correctness Follow-up

Date: 2026-05-29
Reviewer: AgentMiMo (independent evidence/code review)
Artifacts reviewed:
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json`
- `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json`
- `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/golden_set.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`

## Verdict: PASS

---

## Verification Results

### 1. 006597 same-fund unavailable=11 — CONFIRMED

score.json `record_results` 中 006597 条目：9 match + 11 unavailable，与 evidence 和 decision JSON 完全一致。11 个 unavailable 字段逐一列于 decision JSON 的 `same_fund_unavailable_fields`，均因 `snapshot 未显式暴露该 golden 子字段`，属于 legitimate unavailable 而非 mismatch。

### 2. 006597 stop condition triggered — CONFIRMED

evidence 明确声明 `stop_condition_triggered=true`，decision JSON 中 `manual_field_review_required=true`，与 accepted plan 的停止条件一致：same-fund 存在 unavailable 记录时必须暂停，不得推进 promotion。该停止条件是合理的——11 个 unavailable 字段覆盖产品画像、策略文本、持有人结构、份额变动等关键分析维度，不能绕过。

### 3. No manual field review / No golden/fixture/manifest/code modification — CONFIRMED

- `manual_field_review_performed=false`
- `golden_answer_modified=false`
- `golden_fixtures_modified=false`
- `fixture_manifest_modified=false`
- `residual_manifest_modified=false`
- `code_modified=false`
- `tests_modified=false`
- `promotion_run_performed=false`

git status 无 golden-answers、manifests、fund_agent、tests 目录的未提交变更，确认 worker 未进行任何文件修改。

### 4. 004393 decision — CONFIRMED

- Score source: `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json`
- 验证数据：comparable=9, matched=9, mismatched=0, unavailable=141
- Decision: `not_minimum_v1_promotion_prep_by_default`
- Promotion allowed: false
- 理由：9/150 comparable 覆盖率不足，partial coverage 不符合 minimum v1 promotion 标准。裁决合理。

### 5. 004194 decision — CONFIRMED

- Score source: `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`
- 验证数据：comparable=5, matched=5, mismatched=0, unavailable=145
- Decision: `index_profile_only_candidate_not_full_fixture_ready`
- Promotion allowed: false
- 理由：5 个匹配记录全部为 index_profile 字段，不构成 full fixture readiness。裁决合理。

### 6. All promotion_allowed=false — CONFIRMED

三个基金 decision 条目的 `promotion_allowed` 均为 false。顶层 `promotion_allowed=false`，`not_promotion_manifest=true`。

### 7. JSON parsability — CONFIRMED

decision JSON 结构完整，所有字段类型正确，可正常解析。score.json 和 golden_set.json 同样可正常解析。

### 8. No FQ0-FQ6 semantic modification — CONFIRMED

score.json 中 field_scores 共 14 条，均基于现有 snapshot 数据计算，未修改 golden answer 或 field 语义定义。golden_set.json 内容为基金选择元数据（source_csv、selection_reason），不含 FQ 语义字段。worker 未动代码、未动 golden answer。

---

## Additional Observations

- 004194 仅 5 个 comparable records 且均为 index_profile 子字段，decision 为 `index_profile_only_candidate_not_full_fixture_ready` 是准确的。
- 004393 9/150 comparable records 的 partial coverage 不满足 v1 promotion 标准，decision 合理。
- 006597 的 bond_blocker 状态为 `closed` / `resolved_context` / `active_blocker=false`，正确标记为已关闭的历史上下文而非当前阻塞项。
- evidence 和 decision JSON 之间的数据完全对齐，无矛盾。
