# Docling Dedicated Extractor Template-field Mapping — Code Re-review (AgentDS)

**Gate**: `Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`
**Reviewer**: AgentDS
**Date**: 2026-06-17
**Scope**: Targeted re-review of patches applied after initial code review
**Base review**: `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-ds-20260617.md`

**Verdict**: `CODE_REREVIEW_PASS_NOT_READY`

---

## 1. 补丁清单

相对于初评时的代码，共 2 个文件变更：

### 1.1 生产代码 — 1 处变更

`CandidateTemplateFieldAnchor.__post_init__` 新增（`:114-128`）：
- 校验 `note` 必须以 `"candidate_only:"` 开头
- 不满足时 `ValueError` fail-closed

对应初评 **Finding 1**（non-blocking）。

### 1.2 测试代码 — 3 个新测试

| 测试 | 覆盖目标 | 对应初评 Finding |
|------|---------|-----------------|
| `test_docling_template_field_extractor_rejects_invalid_target_field_paths` | `_validate_target_field_paths` 三个 fail-closed 分支：空路径、重复路径、不支持路径 | Finding 5 缺口 1 |
| `test_docling_template_field_extractor_uses_text_label_fallback` | 文本 fallback 路径：无表格时从 `CandidateTextBlock` 抽取 `basic_identity.fund_code` | Finding 5 缺口 2 |
| `test_candidate_template_field_anchor_rejects_non_candidate_note` | `CandidateTemplateFieldAnchor.__post_init__` 拒绝无 `candidate_only:` 前缀的 note | Finding 1（新增 guard 的验证） |

---

## 2. 验证结果

### 2.1 测试 — 10 passed

```text
10 passed in 0.59s
```

原有 7 个测试无回归，新增 3 个全部通过。

### 2.2 Ruff — 全部通过

```text
All checks passed!
```

---

## 3. 变更逐项审查

### 3.1 `CandidateTemplateFieldAnchor.__post_init__` — PASS

- Guard 逻辑正确：`not self.note.startswith("candidate_only:")` → `ValueError`
- 两个现有构造点（`_anchor_for_cell`、`_anchor_for_text_block`）均已硬编码 `candidate_only:` 前缀，零回归风险
- 新测试通过直接构造非法锚点验证 fail-closed 行为
- 无性能或类型安全退化

### 3.2 `test_..._rejects_invalid_target_field_paths` — PASS

- 覆盖 `_validate_target_field_paths` 的三个 `ValueError` 分支
- 每条断言匹配对应错误消息：`"cannot be empty"`、`"duplicates"`、`"unsupported"`
- 边界不重叠，相互独立

### 3.3 `test_..._uses_text_label_fallback` — PASS

- 构造仅含文本块（无表格）的文档，目标字段 `basic_identity.fund_code`
- 文本块内容 `"基金代码：004393"` 在 `§2` 章节
- 验证 `extraction_mode == "direct"`、`value == "004393"`
- 额外校验锚点 note 以 `candidate_only:` 开头（回归 Finding 1 guard）
- 通过 `_match_key_value_field` → `_match_text_label_field` → `_value_after_label` 路径

### 3.4 `test_..._anchor_rejects_non_candidate_note` — PASS

- 直接构造 `CandidateTemplateFieldAnchor(note="production-looking-note")` 触发 `__post_init__`
- 捕获 `ValueError` 并匹配 `"candidate_only"` 消息片段
- 与 Finding 1 guard 紧密耦合，确保护卫不会被意外移除

---

## 4. 新 Blocker 检查

对补丁做 adversarial 检查：

1. **边界回归**：`__post_init__` 不影响已有构造路径。两个现有辅助函数均硬编码 `candidate_only:` 前缀。无新增依赖。PASS。
2. **测试隔离**：新测试各自独立构造 document 或直接调用 dataclass 构造器，不共享可变状态。PASS。
3. **错误消息稳定性**：`test_..._rejects_invalid_target_field_paths` 使用 `match="cannot be empty"` 等子串匹配，不会因完整消息微调而失效。PASS。
4. **文本 fallback 测试与表格测试的互斥性**：`test_..._uses_text_label_fallback` 构造 `tables=()` 的文档，确保走文本路径而非表格路径。PASS。
5. **初评其他 Finding 仍有效**：Finding 3（holdings 单行）、Finding 4（turnover_rate group 归类）、Finding 5 缺口 3-5（turnover_rate 值测试、CandidateTemplateField post_init guard 测试、DoclingTemplateFieldExtractionResult schema_version 测试）、Finding 6（字段路径命名不一致）均未被本补丁覆盖。这些仍是 non-blocking residual。

**结论：未引入新 blocker。**

---

## 5. 初评 Finding 消解状态

| Finding | 状态 | 说明 |
|---------|------|------|
| Finding 1 (anchor note 前缀) | **已消解** | `__post_init__` 已添加，测试覆盖 |
| Finding 2 (blocked 语义) | 保留 | 无变更，仍无生产通路 |
| Finding 3 (holdings 单行) | 保留 | 无变更，仍只返回第一行 |
| Finding 4 (turnover_rate group) | 保留 | 无变更 |
| Finding 5 缺口 1 (target_field_paths fail-closed) | **已消解** | 新测试覆盖三个分支 |
| Finding 5 缺口 2 (text fallback) | **已消解** | 新测试覆盖文本标签抽取 |
| Finding 5 缺口 3 (turnover_rate 值) | 保留 | 无变更 |
| Finding 5 缺口 4 (CandidateTemplateField post_init) | 保留 | 无变更 |
| Finding 5 缺口 5 (result schema_version) | 保留 | 无变更 |
| Finding 6 (命名一致性) | 保留 | 无变更 |

初评 6 个 finding 中 3 个已消解，4 个子缺口已消解。

---

## 6. 结论

补丁精准、最小化，未引入新 blocker。`CandidateTemplateFieldAnchor.__post_init__` 加固了 candidate-only 边界，三个新测试覆盖了初评指出的核心 fail-closed 分支和文本 fallback 路径。原有 7 个测试全部通过，ruff 无警告。

初评 verdict `CODE_REVIEW_PASS_NOT_READY` 保持不变，本次 re-review 不降级。

**VERDICT: `CODE_REREVIEW_PASS_NOT_READY`**
