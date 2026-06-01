# MVP chapter generation score loop design

日期：2026-05-31

Phase：`MVP real-provider stabilization and score-loop phase`

Gate：`MVP chapter generation score loop design gate`

角色：AgentCodex planning/design worker。本文是 design-only handoff，不是实现证据，不改变源码、测试、golden、fixtures、score、quality gate、readiness pipeline、PR 或 release 状态。

## 1. Design decisions

### 1.1 目标

为后续 MVP 章节生成闭环定义一个独立、可复盘、可生成修复任务的评分产物。评分只服务于真实 provider 稳定化和章节写作迭代观察，不接入当前 deterministic `fund-analysis analyze/checklist` 默认路径，不替代现有 FQ0-FQ6 quality gate，不改变 golden / fixture / promotion 语义。

### 1.2 三类 score 的精确定义

本 gate 只接受以下三个 score 名称，未来实现不得混用：

| Score | 评估对象 | 回答的问题 | 不负责 |
|---|---|---|---|
| `extraction_score` | `StructuredFundDataBundle` 中结构化字段的抽取质量 | extractor 是否把年报/结构化来源中的字段抽对、抽全、保留来源锚点 | 不评价 ChapterFactProvider 投影是否适合写章节；不评价 LLM 文稿质量 |
| `chapter_fact_score` | `ChapterFactProvider` 输出的 `chapter_fact_projection.v1` / `ChapterFactInput` | 该章节投影是否足以支撑 CHAPTER_CONTRACT / preferred_lens / ITEM_RULE 写作 | 不评价底层字段是否真实正确；不评价 writer/auditor 输出 |
| `chapter_generation_score` | writer/auditor 产物：`ChapterWriteResult`、`ChapterDraft`、`ChapterAuditResult`、`ChapterRunResult` | 章节输出是否满足 CHAPTER_CONTRACT / ITEM_RULE / evidence / missing semantics | 不评价 provider runtime 是否稳定；不把 timeout、rate limit、network error 当成生成质量通过或失败 |

### 1.3 Gate B blocker 的处理

Gate B 当前 blocker 是 `provider_runtime / timeout`，底层 `stop_reason=llm_timeout`。该情况必须进入独立 `runtime_status` / `runtime_failure` 轨道：

- `chapter_id=2`、`stop_reason=llm_timeout` 时，`chapter_generation_score.status` 必须为 `not_scored`。
- 不得把 timeout 计为 `chapter_generation_score.pass=false`，也不得计为 `chapter_generation_score.pass=true`。
- timeout run 的 overall result 必须为 `blocked_provider_runtime`。
- 后续任务生成必须产出 provider runtime hardening / prompt runtime-cost diagnostic 任务，而不是生成质量修复任务。

## 2. Non-goals

- 不实现代码，不修改源码、测试、README 或配置。
- 不修改现有 `score.json`、quality gate、golden answer、fixture、snapshot、manifest 或 promotion state。
- 不接入当前 readiness / golden / release pipeline。
- 不进入 Gate 5，不引入 `dayu.host`、`dayu.engine`、Host、Agent runtime 或 ToolTrace。
- 不改变 deterministic `fund-analysis analyze` / `fund-analysis checklist` 默认行为。
- 不降低证据锚点、ITEM_RULE、candidate facet、交易建议边界或 E2 deferred 边界。
- 不记录 API key、Authorization header、完整 provider response 或完整 writer draft。

## 3. Score schema

### 3.1 Root artifact

建议未来实现输出 JSON 到：

`reports/chapter-score-runs/<run_id>/chapter-score-report.json`

`run_id` 格式建议：`YYYYMMDD-HHMMSS-<fund_code>-<report_year>-<provider_alias>-<short_hash>`。

```json
{
  "schema_version": "chapter_generation_score_loop.v1",
  "run_id": "20260531-153000-006597-2024-mimo-a1b2c3d4",
  "created_at": "2026-05-31T15:30:00+08:00",
  "fund_code": "006597",
  "report_year": 2024,
  "scenario": "real_provider_smoke",
  "input_refs": {
    "structured_bundle_ref": "reports/chapter-score-runs/.../structured-bundle.redacted.json",
    "chapter_projection_ref": "reports/chapter-score-runs/.../chapter-fact-projection.redacted.json",
    "orchestration_diagnostic_ref": "reports/chapter-score-runs/.../orchestration-diagnostic.json"
  },
  "runtime_status": {
    "status": "blocked",
    "category": "provider_runtime",
    "reason": "timeout",
    "stop_reason": "llm_timeout",
    "first_blocked_chapter_id": 2,
    "safe_message": "chapter 2 provider call timed out"
  },
  "overall": {
    "status": "blocked_provider_runtime",
    "pass": false,
    "threshold_profile": "mvp_strict_v1",
    "score_summary": {
      "extraction_score_min": 0.92,
      "chapter_fact_score_min": 0.88,
      "chapter_generation_score_min": null
    }
  },
  "chapters": []
}
```

Root 约束：

- `runtime_status.status` 取值：`complete`、`blocked`、`failed_before_scoring`。
- `runtime_status.category` 取值：`none`、`provider_config`、`provider_runtime`、`source_runtime`、`orchestration_dependency`、`code_bug`、`unknown`。
- 当 `runtime_status.category=provider_runtime` 且 `reason=timeout` 时，所有未获得 draft/audit 的章节 `chapter_generation_score.status` 必须为 `not_scored`。
- `input_refs` 只能保存脱敏、截断或摘要 artifact 路径，不保存完整 provider response 和完整 writer draft。

### 3.2 Score object

三个 score 共享同一基础形状：

```json
{
  "name": "chapter_generation_score",
  "status": "pass",
  "value": 0.94,
  "threshold": 0.90,
  "blocking_failure_count": 0,
  "reviewable_failure_count": 1,
  "not_scored_reason": null,
  "checks": [
    {
      "check_id": "generation.evidence_anchor_allowed",
      "status": "pass",
      "severity": "blocking",
      "points_earned": 1.0,
      "points_possible": 1.0,
      "failure_code": null,
      "message": "all used anchors are in allowed anchor set",
      "source_refs": ["chapter_audit:P2", "chapter_draft.used_anchor_ids"]
    }
  ]
}
```

约束：

- `status` 取值：`pass`、`fail`、`blocked`、`not_scored`。
- `value` 范围为 `0.0..1.0`；`not_scored` 时必须为 `null`。
- 任一 `severity=blocking` check fail 时，该 score 必须 `status=fail`，即使加权均分高于阈值。
- `not_scored_reason` 只能用于前置 runtime / dependency 缺失，不得用于掩盖质量失败。

## 4. Per-chapter score report shape

```json
{
  "chapter_id": 2,
  "title": "收益归因：R = A + B - C",
  "run_status": {
    "status": "failed",
    "stop_reason": "llm_timeout",
    "attempt_count": 0,
    "accepted_draft": false,
    "accepted_conclusion": false
  },
  "extraction_score": {
    "name": "extraction_score",
    "status": "pass",
    "value": 0.93,
    "threshold": 0.90,
    "blocking_failure_count": 0,
    "reviewable_failure_count": 1,
    "not_scored_reason": null,
    "checks": []
  },
  "chapter_fact_score": {
    "name": "chapter_fact_score",
    "status": "pass",
    "value": 0.88,
    "threshold": 0.85,
    "blocking_failure_count": 0,
    "reviewable_failure_count": 2,
    "not_scored_reason": null,
    "checks": []
  },
  "chapter_generation_score": {
    "name": "chapter_generation_score",
    "status": "not_scored",
    "value": null,
    "threshold": 0.90,
    "blocking_failure_count": 0,
    "reviewable_failure_count": 0,
    "not_scored_reason": "provider_runtime_timeout",
    "checks": []
  },
  "top_failures": [
    {
      "failure_code": "runtime.provider_timeout",
      "failure_class": "provider_runtime",
      "owner": "service_provider_runtime",
      "severity": "blocking",
      "safe_detail": "writer/auditor call did not complete before timeout"
    }
  ],
  "task_candidates": [
    {
      "task_id": "provider-timeout-chapter-2-runtime-cost-diagnostic",
      "task_type": "runtime_diagnostic",
      "priority": "P0",
      "owner": "future_provider_runtime_gate",
      "allowed_files_hint": [
        "fund_agent/services/llm_provider.py",
        "fund_agent/services/chapter_orchestrator.py",
        "tests/services/test_llm_provider.py",
        "tests/services/test_chapter_orchestrator.py"
      ],
      "blocked_by_manual_review": false
    }
  ]
}
```

章节报告约束：

- `run_status` 来自 orchestration diagnostic，是 score 的前置状态，不是 score 本身。
- `chapter_generation_score` 只能在存在 writer result 且 audit result 可判定时评分。
- `accepted_draft=false` 且 `attempt_count=0` 的 provider runtime timeout 不允许生成 writer/auditor prompt 修复任务，除非人工标记为 runtime cost/prompt-size 问题。
- `top_failures.safe_detail` 必须脱敏，不包含完整 prompt、完整 draft、完整 response 或 secret。

## 5. Failure taxonomy

### 5.1 Runtime / pipeline failures

这些失败先于质量评分，必须路由到 `runtime_status`：

| Failure code | Class | 示例 stop reason | Score 处理 | 默认 owner |
|---|---|---|---|---|
| `runtime.provider_timeout` | `provider_runtime` | `llm_timeout` | generation `not_scored` | provider runtime gate |
| `runtime.provider_rate_limited` | `provider_runtime` | `llm_rate_limited` | generation `not_scored` | provider runtime gate |
| `runtime.provider_network_error` | `provider_runtime` | `llm_network_error` | generation `not_scored` | provider runtime gate |
| `runtime.provider_malformed_response` | `provider_runtime` | `llm_malformed_response` | generation `not_scored` 或 audit parse blocked | provider contract gate |
| `runtime.provider_exception` | `provider_runtime` | `llm_exception` | generation `not_scored` | provider runtime gate |
| `runtime.config_invalid` | `provider_config` | missing config | whole run `failed_before_scoring` | provider config gate |
| `runtime.dependency_missing` | `orchestration_dependency` | `dependency_missing` | dependent chapters `not_scored` | upstream chapter owner |

### 5.2 `extraction_score` failures

| Failure code | Severity | 含义 | 修复方向 |
|---|---|---|---|
| `extraction.identity_missing` | blocking | 基金代码、年份、报告类型或基金类型身份缺失 | extractor / repository identity |
| `extraction.identity_mismatch` | blocking | 返回候选与基金代码、年份或报告类型冲突 | source fail-closed，不 fallback 掩盖 |
| `extraction.required_field_missing` | blocking | CHAPTER_CONTRACT 必需字段未抽出且无合法 missing reason | extractor / field mapping |
| `extraction.anchor_missing` | blocking | 数值字段存在但无 EvidenceAnchor | evidence projection |
| `extraction.value_invalid` | blocking | 单位、日期、数值类型不可解析 | normalization |
| `extraction.schema_drift` | blocking | 来源结构偏离契约 | source parser gate |
| `extraction.reviewable_gap` | reviewable | 字段缺失但有合法 `not_disclosed` / `unavailable` 语义 | 数据源补强或接受缺口 |

### 5.3 `chapter_fact_score` failures

| Failure code | Severity | 含义 | 修复方向 |
|---|---|---|---|
| `fact.contract_input_missing` | blocking | must_answer 所需 fact 不存在且没有 missing reason | `ChapterFactProvider` field spec |
| `fact.item_rule_projection_missing` | blocking | ITEM_RULE 决策缺失或章节归属错误 | ITEM_RULE projection |
| `fact.lens_resolution_missing` | blocking | 基金类型有效但 preferred_lens 未解析 | lens API / fund type |
| `fact.asserted_candidate_facet` | blocking | 把 `non_asserted_facets` 放进 asserted `facets` | facet fail-closed |
| `fact.anchor_ref_broken` | blocking | fact 引用不存在的 anchor id | projection integrity |
| `fact.missing_semantics_absent` | blocking | 缺关键事实但没有 `missing_reasons` | missing semantics |
| `fact.coverage_reviewable_gap` | reviewable | 事实足以写缺口，但不足以强判断 | 数据源或章节策略 |

### 5.4 `chapter_generation_score` failures

| Failure code | Severity | 对应规则 | 修复方向 |
|---|---|---|---|
| `generation.missing_required_structure` | blocking | P1 / C1 | writer prompt / parser |
| `generation.missing_required_output_marker` | blocking | C1 | writer prompt |
| `generation.unknown_anchor` | blocking | E1 | writer anchor discipline |
| `generation.evidence_line_missing` | blocking | E3 | writer evidence format |
| `generation.must_not_cover_violation` | blocking | C2 | writer prompt / auditor rule |
| `generation.item_rule_deleted_content_present` | blocking | C2 | ITEM_RULE enforcement |
| `generation.asserted_candidate_facet` | blocking | L2 | candidate facet wording |
| `generation.numerical_closure_missing` | blocking | L1 | chapter 2 calculation wording |
| `generation.missing_semantics_violation` | blocking | R1 / R2 | data gap wording |
| `generation.trading_advice` | blocking | R2 | forbidden wording |
| `generation.llm_audit_parse_failed` | blocking | LLM audit protocol | auditor prompt / parser |
| `generation.readability_reviewable` | reviewable | LLM audit | wording iteration |

E2 源文核验仍是 Evidence Confirm gate 边界。score-loop 可以记录 `E2_deferred=true`，但不得把 E2 deferred 当作通过源文核验。

## 6. Check weights and thresholds

### 6.1 Threshold profile `mvp_strict_v1`

| Score | Pass threshold | Blocking rule |
|---|---:|---|
| `extraction_score` | `>= 0.90` | 任一 blocking extraction failure 即 fail |
| `chapter_fact_score` | `>= 0.85` | 任一 blocking fact failure 即 fail |
| `chapter_generation_score` | `>= 0.90` | 任一 blocking generation failure 即 fail |

整体 run pass 条件：

1. `runtime_status.status=complete`。
2. 第 1-6 章均有 `run_status.status=accepted`。
3. 第 1-6 章三个 score 均为 `pass`。
4. final assembly 完整生成第 0/7 章，且没有 deterministic fallback。
5. 没有 secret leak finding，没有完整 provider response / 完整 writer draft artifact。

整体 run blocked 条件：

- 任一 provider runtime timeout / rate limit / network error 阻断章节生成。
- 任一上游 dependency 导致章节未运行。
- 配置错误、source runtime 或 code bug 导致 score 输入不完整。

### 6.2 建议初始 weights

`extraction_score`：

- identity and fund type：20%
- required structured fields：35%
- value normalization：20%
- evidence anchor presence：20%
- legal missing semantics：5%

`chapter_fact_score`：

- CHAPTER_CONTRACT coverage：30%
- ITEM_RULE projection：20%
- preferred_lens / fund type alignment：15%
- evidence anchor integrity：20%
- missing semantics and non-asserted facet discipline：15%

`chapter_generation_score`：

- required structure and output markers：20%
- evidence anchor and quote format：20%
- CHAPTER_CONTRACT must_answer / must_not_cover：20%
- ITEM_RULE and candidate facet boundary：15%
- missing semantics / next minimal validation question：10%
- numerical closure / chapter-specific logic：10%
- readability without unsafe advice：5%

Weights 只用于 reviewable failures 的排序；blocking failure 永远覆盖加权分。

## 7. Pro-Codex task generation rules

未来 score-loop 可以生成 `pro_codex_tasks.json`，但不得自动改代码、提交或推送。任务生成只把 score findings 转成 code-generation-ready handoff 候选，供 controller 裁决。

### 7.1 Task schema

```json
{
  "schema_version": "pro_codex_task_candidates.v1",
  "source_run_id": "20260531-153000-006597-2024-mimo-a1b2c3d4",
  "tasks": [
    {
      "task_id": "generation-chapter-1-required-output-markers",
      "priority": "P1",
      "task_type": "writer_contract_fix",
      "failure_codes": ["generation.missing_required_output_marker"],
      "chapters": [1],
      "root_cause_class": "chapter_generation",
      "allowed_files_hint": [
        "fund_agent/fund/chapter_writer.py",
        "fund_agent/fund/chapter_auditor.py",
        "tests/fund/test_chapter_writer.py",
        "tests/fund/test_chapter_auditor.py"
      ],
      "non_goals": [
        "do not change quality gate semantics",
        "do not relax evidence or ITEM_RULE boundaries",
        "do not alter deterministic analyze/checklist defaults"
      ],
      "acceptance_checks": [
        "targeted writer/auditor tests pass",
        "score rerun shows chapter_generation_score pass for affected chapter",
        "secret leak check passes"
      ]
    }
  ]
}
```

### 7.2 Routing rules

- `runtime.provider_timeout` -> `runtime_diagnostic` task，owner `future_provider_runtime_gate`；优先检查 timeout budget、bounded retry/backoff、prompt size/runtime cost，不生成 writer quality fix。
- `extraction.*` -> extractor / source / `FundDocumentRepository` derived-data task；不得修改 writer/auditor 来掩盖字段错误。
- `fact.*` -> `ChapterFactProvider` projection task；不得修改 extraction 或 writer 来绕过 projection 缺陷。
- `generation.*` -> writer/auditor/orchestrator task；不得降低审计规则、删 ITEM_RULE、放宽 candidate facet 或交易建议禁区。
- `runtime.dependency_missing` -> 指向第一个 upstream failed / blocked chapter，不为被跳过章节重复生成任务。
- 同一 root cause 影响多章时合并成一个 task，列出 chapters；不同 score class 不合并。
- 只有 `severity=blocking` 或连续两次出现的 `reviewable` finding 可以生成 P0/P1 task。
- human override 标记为 `accepted_risk` 的 finding 不生成实现任务，但必须保留在 residuals。

### 7.3 Priority rules

| Priority | 条件 |
|---|---|
| P0 | runtime blocker 阻断完整 run；或 secret leak；或交易建议边界违规 |
| P1 | blocking score failure；章节无法 accepted |
| P2 | reviewable failure 连续复现，影响可读性或行动性 |
| P3 | artifact hygiene、报告展示、诊断可读性 |

## 8. Future rerun command

设计建议未来新增一个 opt-in、非 readiness、非 quality gate 命令：

```bash
uv run fund-analysis score-chapters 006597 --report-year 2024 --use-llm --score-profile mvp_strict_v1 --output-dir reports/chapter-score-runs/20260531-manual
```

命令边界：

- 只生成 score-loop artifacts，不写 golden / fixtures / score.json / quality gate result。
- 不改变 `fund-analysis analyze` 和 `fund-analysis checklist` 默认行为。
- 遇到 provider timeout 时 exit code 建议为 `3`，含义是 `blocked_provider_runtime`；stdout 为空或只输出 artifact path，stderr 只输出脱敏摘要。
- 若未来 controller 需要复用现有 real smoke，可先保留当前命令：

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

并通过独立 diagnostic script 读取脱敏 orchestration diagnostic 生成 score report。该兼容方式仍不得接入 readiness/golden pipeline。

## 9. Artifact lifecycle

### 9.1 Run artifacts

未来一次 score run 的目录建议：

```text
reports/chapter-score-runs/<run_id>/
  chapter-score-report.json
  chapter-score-summary.md
  pro-codex-tasks.json
  orchestration-diagnostic.json
  structured-bundle.redacted.json
  chapter-fact-projection.redacted.json
  secret-leak-check.txt
```

保留规则：

- `reports/chapter-score-runs/` 是本地 run 产物，不自动进入 golden / fixture。
- 只有 controller 接受的摘要或 judgment 才写入 `docs/reviews/`。
- redacted artifacts 必须截断长文本字段，并删除 API key、Authorization header、完整 provider response、完整 writer draft。
- 人工复核后需要长期留存的输入，必须通过独立 fixture/golden gate 裁决，不能由 score-loop 自动晋升。

### 9.2 Review artifacts

当前 design artifact 是：

`docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md`

未来实现 gate 建议产生：

- Plan：`docs/reviews/mvp-chapter-generation-score-loop-plan-YYYYMMDD.md`
- Implementation evidence：`docs/reviews/mvp-chapter-generation-score-loop-implementation-evidence-YYYYMMDD.md`
- Review / re-review：`docs/reviews/mvp-chapter-generation-score-loop-*-review-*.md`
- Controller judgment：`docs/reviews/mvp-chapter-generation-score-loop-controller-judgment-YYYYMMDD.md`

## 10. Human review and manual override entry points

Manual override 只允许改变 score-loop artifact 的人工裁决状态，不允许改变原始 score、现有 quality gate、golden 或 release readiness。

### 10.1 Override schema

```json
{
  "schema_version": "chapter_score_manual_override.v1",
  "source_run_id": "20260531-153000-006597-2024-mimo-a1b2c3d4",
  "override_id": "manual-20260531-001",
  "reviewer": "controller",
  "created_at": "2026-05-31T16:00:00+08:00",
  "target": {
    "chapter_id": 2,
    "score_name": "chapter_generation_score",
    "failure_code": "runtime.provider_timeout"
  },
  "decision": "accepted_risk",
  "rationale": "timeout already tracked by provider runtime gate; not a generation quality finding",
  "expires_at": "2026-06-07",
  "allowed_effect": "suppress_task_generation_only"
}
```

### 10.2 Allowed decisions

| Decision | Allowed effect | 禁止事项 |
|---|---|---|
| `accepted_risk` | 阻止重复 task 生成，保留 residual | 不得把 fail 改 pass |
| `false_positive` | 标记 check 设计需修正，要求后续 score-loop fix | 不得删除原始证据 |
| `deferred_with_owner` | 指定 later gate / issue owner | 不得无 owner defer |
| `requires_more_evidence` | 阻止实现任务，要求补 diagnostic | 不得默认通过 |

Manual override 必须写入同 run 目录的 `manual-overrides.json`，并在 `chapter-score-summary.md` 显示。

## 11. Validation and readiness boundary

未来实现完成后，最小验证矩阵应覆盖：

- unit tests：score object validation、threshold、blocking failure precedence、not-scored timeout path。
- fixture-style tests：构造脱敏 `ChapterFactProjection` / orchestration diagnostic，验证 extraction / fact / generation 三类 score 不混淆。
- provider timeout regression：输入 Gate B 形状的 diagnostic，断言 overall 为 `blocked_provider_runtime`，chapter 2 generation 为 `not_scored`。
- secret hygiene：artifact 不包含 API key、Authorization header、完整 provider response、完整 writer draft。
- CLI boundary：`score-chapters` 为 opt-in；默认 `analyze/checklist` 不变。

Readiness boundary：

- score-loop pass 不是 release readiness pass。
- score-loop pass 不是 golden promotion。
- score-loop blocked 不改变现有 quality gate 语义。
- score-loop 只能作为后续 Gate B rerun、provider runtime hardening、writer/auditor hardening或 projection/extraction 修复的诊断输入。

## 12. Future implementation slices

建议后续 controller 若进入实现，拆成以下小 slice：

1. `score_schema_models`：新增 score dataclass / JSON schema / validation；只处理内存对象和 JSON 序列化。
2. `diagnostic_to_score_mapper`：把 `StructuredFundDataBundle`、`ChapterFactProjection`、`ChapterOrchestrationResult` 或脱敏 diagnostic 映射为三类 score；实现 Gate B timeout `not_scored` 路径。
3. `task_candidate_generator`：按 failure taxonomy 生成 `pro_codex_tasks.json`；不执行任务。
4. `score_cli_opt_in`：新增 opt-in score command 或 diagnostic script；不接入 readiness/golden pipeline。
5. `artifact_hygiene_tests`：覆盖 redaction、secret leak、完整 draft/response 禁止项。

每个 slice 都必须明确 allowed files，并同步测试。若涉及 CLI 用户入口，再更新根 `README.md`；若只新增内部 Fund/Service score models，则更新对应包 README。

## 13. Residual risks

| Risk | Disposition | Owner |
|---|---|---|
| 当前真实 provider 仍 blocked by `llm_timeout` | 本设计单独分类，不伪装为 generation failure | future provider runtime gate |
| `extraction_score` 需要同源真值或人工核验才能判断“抽对” | 初版只能对结构完整性和锚点做自动评分，正确性需人工 review | future extraction scoring gate |
| LLM audit 本身可能不稳定 | generation score 必须以程序审计 blocking rules 为硬约束，LLM audit 作为补充 | future writer/auditor hardening gate |
| score-loop artifact 可能被误用为 readiness pass | 本设计禁止接入 readiness/golden，controller judgment 必须再次确认 | controller |
| manual override 被滥用 | override 只能影响 task generation，不改变 raw score | controller / reviewer |

## 14. Self-check

- Current gate / role：Gate C design-only；我是 planning/design worker，不是 controller 或 implementation worker。
- Source of truth：已读取 `AGENTS.md` 用户内联规则、`docs/current-startup-packet.md`、`docs/implementation-control.md`、Gate A judgment、Gate B blocked judgment 和 real-provider diagnostic。
- Scope boundary：只新增本 design artifact；未修改源码、测试、golden、fixtures、score、quality gate、README、control docs 或 runtime。
- Gate B blocker：`provider_runtime / timeout`、`stop_reason=llm_timeout` 被单独路由为 `not_scored` / `blocked_provider_runtime`，不隐藏成 generation pass/fail。
- Secret boundary：本文未记录 API key、Authorization header、完整 provider response 或完整 writer draft。
- Completion status：design artifact 已给出 schema、failure taxonomy、per-chapter report、Pro-Codex task rules、thresholds、rerun command、artifact lifecycle、manual override、readiness boundary 和 residual risks。
