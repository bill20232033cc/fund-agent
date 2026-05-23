# P12-S2 Targeted Plan Re-review — AgentGLM（2026-05-22）

## Verdict

**PASS**

Plan 修订已关闭全部 findings。无阻塞或残留问题。

---

## Finding Closure Assessment

### GLM F1 — 多锚点断言应验证具体 anchor 文本 — CLOSED ✅

Plan 修订内容：

- §9 Slice 1（第 124-126 行）现在要求：提取 `- 证据边界：` 所在行后，断言该行同时包含 "at least one benchmark anchor reference and at least one R=A+B-C attribution anchor reference from the fixture, using the exact `_body_anchor_reference(...)` text or exact equivalent literal expected text"；并明确 "checking `；` alone is insufficient"。
- §10（第 206 行）补充："The multi-anchor test must verify concrete anchor reference text, not only punctuation: at least one benchmark `_body_anchor_reference(...)` output and at least one R=A+B-C `_body_anchor_reference(...)` output must appear on the same `- 证据边界：` line。"

原文仅要求 `；`，修订后要求具体 anchor 文本子串 + `；` 作为附加断言。F1 关闭。

### GLM F2 — empty anchor 路径需要显式测试策略 — CLOSED ✅

Plan 修订内容：

- §9 Slice 1（第 128-132 行）新增独立段落："Add an explicit empty-anchor path test"，指定：保持 `identity_present`（不从 `missing=True` 出发），用 inline `replace(...)` 清空相关 anchors，不扩展 fixture factory，断言 exact no-anchor 文本。
- §10（第 207 行）重申同样要求。

原文未指定如何构造 empty anchor 场景，修订后给出 inline `replace(...)` 策略并限制不改 fixture factory。F2 关闭。

### GLM F3 — duplicate anchor 消除需要显式测试方案 — CLOSED ✅

Plan 修订内容：

- §9 Slice 1（第 133-136 行）新增独立段落："Add an explicit duplicate-anchor path test"，指定：构造包含同一 `EvidenceAnchor` 多次的 tuple，验证 anchor reference 只渲染一次；允许直接测 `_item_rule_evidence_bullet(...)` 或通过 segment 间接触发；私有 helper 访问仅限 renderer unit test，不得导出。
- §10（第 208 行）重申："A separate duplicate-anchor path test must prove the same anchor reference is rendered once after de-duplication; direct private-helper testing is acceptable only in renderer unit tests。"

原文仅在 failure paths 列表中提到 "Duplicate anchors do not render twice" 但无测试方案，修订后明确构造方法和验证断言。F3 关闭。

### MiMo F1 — duplicate anchor 测试路径未明确要求为独立 test case — CLOSED ✅

Plan 新增 §10.1 Finding Disposition 表（第 222-229 行），明确记录 MiMo F1 为 accepted，并与 GLM F3 合并处理。§9 Slice 1 第 133-136 行的 duplicate-anchor 测试要求同时关闭了此 finding。

---

## §10.1 Finding Disposition 验证

Plan §10.1 新增的 finding disposition table 覆盖了全部 4 条 finding（MiMo F1 + GLM F1/F2/F3），每条均标注 accepted 并指向具体的 plan 更新位置。Dispositions 与修订内容一致，无遗漏或矛盾。

---

## Residual Risks

Plan 修订未改变 residual risks 清单（§14），无新增风险。

---

## Summary

全部 4 条 finding 已被 plan 修订明确关闭。修订精确、无过度扩展、未引入新的设计或边界问题。Plan 可进入 implementation gate。
