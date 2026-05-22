# PR Review (AgentGLM)

## Scope

- Mode: PR
- PR: `https://github.com/bill20232033cc/fund-agent/pull/9`
- Title: P14-S1 index quality denominators
- Author: bill20232033cc
- Head: `docs/post-p13-follow-up-planning`
- Base: `main`
- Branch: draft, mergeState CLEAN
- CI: test passed (Actions run 26259041713)
- Output file: `docs/reviews/p14-pr-review-glm-20260522.md`
- Included scope: 89 files changed, +9981 / -110 lines。完整 diff 覆盖 post-P13 follow-up planning artifacts、P14-S1 plan/review/rereview artifacts、implementation（extraction_snapshot/extraction_score/golden_prefill/_value_utils）、golden answer template/JSON/reviewed markdown、sample matrix fixture、control doc update、Fund/test README sync、service test fixture adaptation
- Excluded scope: `docs/repo-audit-20260521.md`（untracked, 未触碰）；RR-13 source data
- Parallel review coverage: 无 subagent；主 reviewer 逐一走读全部生产代码变更、golden answer 一致性、control doc 状态和关键测试链路

## Conclusion

**PASS_WITH_FINDINGS**

PR 9 严格限于 post-P13 planning 和 P14-S1 quality-denominator scope。核心实现正确：`index_profile`/`tracking_error` 对 `index_fund`/`enhanced_index` 条件进入 P1 分母；非指数基金排除；unknown/conflicting 保守可评分。`ExtractionMode` 未扩展。dataclass comparable/golden prefill 路径共享 Fund Capability 内部 helper。golden answer JSON 与 reviewed markdown/template 一致。未新增 production tracking_error golden。未违反 FundDocumentRepository 边界、Dayu 非依赖、extra_payload 禁令或分层约束。CI 通过，全量 428 passed。

发现 1 个低严重度 finding（planning-to-code golden field substitution 的 rationale 虽已由 controller aggregate judgment 记录，但 PR body 未显式提及该偏差）。无阻断问题。

## Findings

### F-1-已记录-[低]-PR body 未显式提及 001548 golden field substitution 偏差

- **入口/函数**: PR body "Validation" 和 "Review artifacts" sections
- **文件(行号)**: PR description（GitHub）
- **输入场景**: PR reviewer 对比 PR body 与 plan/implementation 的 001548 golden rows
- **实际分支**: PR body 未说明实际 golden rows（`benchmark_text`/`source_tier`）替代了 plan 指定的 `methodology_availability`/`constituents_availability`
- **预期行为**: PR body 或 Summary 应提及字段替换及理由，使独立 PR reviewer 无需阅读全部 aggregate artifacts 即可理解偏差
- **实际行为**: PR body 只写了 "Adds stable comparable sub-fields, dataclass-aware golden prefill support, reviewed 001548 index_profile golden rows"，未说明字段替换和 confidence 提升从 medium→high
- **直接证据**: PR body "Summary" bullet 3 列出 "reviewed 001548 index_profile golden rows"；controller aggregate judgment (`p14-s1-aggregate-deepreview-controller-judgment-20260522.md` line 11) 记录了该 substitution 并裁决 accepted；但 PR body 本身无此信息
- **影响**: 仅 PR-level 文档追溯性影响。独立 PR reviewer 如不阅读 aggregate artifacts，可能误认为 golden rows 与 plan 完全一致。不影响生产行为正确性
- **建议改法和验证点**: 在 PR body 的 "Explicit non-goals" 或新增一行说明：001548 production golden rows 使用 `benchmark_text`/`source_tier` 替代 plan 初始指定的 `methodology_availability`/`constituents_availability`，confidence 从 medium 提升为 high，由 controller aggregate judgment 裁决接受。或接受现状，因 controller judgment 已记录
- **修复风险（低）**: 纯 PR body 文字补充
- **严重程度（低）**: 不影响代码正确性；review artifacts 已覆盖

## Scope Boundary Verification

### 1. PR diff 是否严格限于 post-P13 planning 与 P14-S1 quality-denominator scope

**PASS**

生产代码变更仅涉及：

| 文件 | 变更类型 | scope 归属 |
|---|---|---|
| `fund_agent/fund/_value_utils.py` | 新增 | Slice A/C：shared dict/dataclass helper |
| `fund_agent/fund/extraction_snapshot.py` | 修改 | Slice A：comparable sub-fields + dataclass support |
| `fund_agent/fund/extraction_score.py` | 修改 | Slice B：conditional P1 + applicability filtering |
| `fund_agent/fund/golden_prefill.py` | 修改 | Slice C：dataclass golden prefill support |
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | 修改 | Slice C：001548 index_profile reviewed rows |
| `reports/golden-answers/golden-answer.json` | 修改 | Slice C：strict JSON rebuild |
| `docs/golden-answer-template.md` | 修改 | Slice C：template rows |
| `fund_agent/fund/README.md` | 修改 | Slice E：docs sync |
| `tests/README.md` | 修改 | Slice E：docs sync |
| `docs/implementation-control.md` | 修改 | Control doc：gate/phase state update |
| `tests/services/test_fund_analysis_service.py` | 修改 | Test fixture adaptation：补充 P13 新增的 index_profile/tracking_error 字段 |

`test_fund_analysis_service.py` 的变更是因为 P13 在 `StructuredFundDataBundle` 新增了 `index_profile` 和 `tracking_error` 字段，测试 fixture 需要填充这些字段。属于最小测试适配，不是 scope expansion。

`docs/reviews/` 下新增约 20 个 review artifacts，全部属于 post-P13 planning 和 P14-S1 gate 链。

**无 scope 越界**：无 Service/UI/Engine 层生产代码变更；无 `docs/design.md` 变更；无 root `README.md` 变更；无 `extractors/models.py` 变更；无 CLI 入口变更。

### 2. index_profile / tracking_error conditional P1 denominator

**PASS**

`extraction_score.py` 实现链路：

- `INDEX_QUALITY_FIELD_NAMES = ("index_profile", "tracking_error")` — 精确限定两个字段
- `INDEX_QUALITY_APPLICABLE_FUND_TYPES = ("index_fund", "enhanced_index")` — 精确限定适用类型
- `_is_non_applicable_index_quality_record()` 三条路径：
  - `fund_type is None` → `return False`（保守保留）✓
  - `fund_type not in INDEX_QUALITY_APPLICABLE_FUND_TYPES` → `return True`（排除）✓
  - 否则 → `return False`（保留）✓
- `_scorable_records()` 在 5 个消费点一致应用：`score_snapshot_records`、`_build_fund_score_row`、`_score_records_for_single_fund`、`_build_fund_quality_row`、`_missing_fields_by_priority`
- GLM code review F-1 修复：`_build_fund_score_row` 现在也通过 `_unique_optional_text` 解析基金级类型，使用 `use_record_fund_type=False`，与 `_build_fund_quality_row` 路径完全一致

测试覆盖：

- `test_index_quality_fields_are_p1_only_for_applicable_fund_types`：active_fund 排除、index_fund/enhanced_index 计入、unknown（空字符串）保守计入
- `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts`：冲突类型下 fund_score 和 fund_quality 均保守保留
- `test_derive_fund_quality_records_marks_conflicting_fund_type_without_first_resolving_lens`：已更新为包含 index_profile 冲突断言

### 3. dataclass comparable / golden prefill、golden answer 一致性

**PASS**

`_value_utils.py`（新增）：

```python
def value_mapping(value: object) -> Mapping[str, object] | None:
    if value is None: return None
    if isinstance(value, Mapping): return value
    if is_dataclass(value) and not isinstance(value, type): return asdict(value)
    return None
```

- 仅 stdlib import，无跨层依赖
- 被 `extraction_snapshot.py:22` 和 `golden_prefill.py:16` 共享 import
- 模块名 `_value_utils` 单下划线前缀，明确 Capability 内部

`COMPARABLE_SUB_FIELDS_BY_FIELD` 新增：

- `index_profile`：7 个子字段（benchmark_text, benchmark_identity_status, benchmark_index_name, benchmark_index_code, methodology_availability, constituents_availability, source_tier）— 全部标量
- `tracking_error`：10 个子字段 — 全部标量，含 bool 字段 annualized/input_period_complete

Golden answer 三方一致性：

| 来源 | fund_code | field_name | sub_fields | confidence | 一致 |
|---|---|---|---|---|---|
| template | 001548 | index_profile | benchmark_text, benchmark_identity_status, benchmark_index_name, source_tier | — | — |
| reviewed markdown | 001548 | index_profile | 同上，4 行 | high | ✓ |
| strict JSON | 001548 | index_profile | 同上，4 条记录，record_count 121→125 | high | ✓ |

- 无 production tracking_error golden 行 ✓
- JSON schema_version 保持 `fund-agent.golden-answer.v1` ✓
- fund_count 保持 6 ✓

### 4. FundDocumentRepository / Dayu / extra_payload / 分层边界

**PASS**

| 约束 | 证据 |
|---|---|
| FundDocumentRepository 边界 | extraction_score/snapshot/golden_prefill/_value_utils 均不 import documents 层或访问 PDF/cache |
| Dayu 非依赖 | 全部变更文件无 dayu import |
| extra_payload 禁令 | 无 extra_payload 使用 |
| Service/UI/Engine 不处理 Fund source internals | `_value_utils.py` 在 `fund_agent/fund/` 内部，所有变更在 Capability 层 |
| ExtractionMode 不扩展 | `extractors/models.py` 未被修改；enum 保持 `Literal["direct", "derived", "estimated", "missing"]` |

### 5. PR body / control doc / review artifacts / CI 一致性

**PASS**

| 维度 | PR body | Control doc / artifacts | 一致 |
|---|---|---|---|
| 当前 gate | "Adds post-P13 follow-up planning and accepted P14-S1 plan/review artifacts" | implementation-control.md: `ready-to-open-draft-PR` | ✓ |
| 测试结果 | "pytest -q: 428 passed" | Implementation artifact fix pass: 428 passed | ✓ |
| Review artifacts | 列出 plan/code/aggregate judgment paths | Control doc Startup Packet 引用完全一致 | ✓ |
| CI | PR body 未显式列 CI URL | CI test passed (Actions 26259041713) | ✓ |
| Non-goals | 列出完整 non-goals | Plan/controller judgment non-goals 完全一致 | ✓ |
| 001548 golden | "reviewed 001548 index_profile golden rows" | 实际 4 行 benchmark-derived rows | ✓（字段偏差见 F-1） |
| 161725 fixture | "161725 enhanced-index fixture coverage" | test_p1_sample_matrix.py 确实新增 161725 case | ✓ |

### 6. docs/repo-audit-20260521.md 未纳入 PR

**PASS**

- `git status` 确认 `?? docs/repo-audit-20260521.md`（untracked）
- PR diff 不包含该文件
- Control doc "Open residuals" 明确记录 "excluded docs/repo-audit-20260521.md"
- PR body "Explicit non-goals" 明确声明排除

## Open Questions

- 无。

## Residual Risk

| Risk | Owner | Blocking for draft-PR-pass |
|---|---|---|
| `tracking_error` production golden correctness 缺失 — 无 001548 verified direct tracking-error value | Future golden evidence slice | 否 |
| enhanced-index production golden 缺失 — 161725 仅为 deterministic fixture | Future selected-fund/golden expansion | 否 |
| `methodology_availability` / `constituents_availability` 无 production golden — 实现选择了替代子字段 | Future source-contract phase | 否 |
| calculated tracking error 仍缺 | Future data-source/calculation phase | 否 |
| external index series adapter / methodology / constituents extraction 仍缺 | Future source-contract phases | 否 |
| QDII index subtype 仍 unmodeled | Future subtype-design phase | 否 |
| E1-E3 / Evidence Confirm 仍缺 | Future audit architecture phase | 否 |
| RR-13 duplicate `016492` | User / App source | 否 |
| `docs/repo-audit-20260521.md` publication decision | Controller / user | 否 |
| F-1 PR body 未显式提及 golden substitution | Controller / docs cleanup | 否（低严重度） |

## Ready-for-draft-PR-pass Assessment

PR 9 满足 draft-PR-pass 条件：

1. PR diff 严格限于 post-P13 planning 和 P14-S1 quality-denominator scope，无 scope 越界。
2. `index_profile`/`tracking_error` 条件 P1 denominator 正确实现：index_fund/enhanced_index 适用，non-index 排除，unknown/conflicting 保守。
3. `ExtractionMode` 未扩展。dataclass comparable/golden prefill 路径正确共享 helper。golden answer JSON/reviewed markdown/template 三方一致。
4. 未违反 FundDocumentRepository 边界、Dayu 非依赖、extra_payload 禁令或分层约束。
5. PR body、control doc、review artifacts、CI 状态一致。唯一的低严重度偏差（golden field substitution 未在 PR body 显式提及）已有 controller aggregate judgment 记录。
6. `docs/repo-audit-20260521.md` 正确排除在 PR 外。
7. 全量测试 428 passed，ruff passed，CI passed。
8. 所有 residual risks 有明确 owner，无阻断项。
