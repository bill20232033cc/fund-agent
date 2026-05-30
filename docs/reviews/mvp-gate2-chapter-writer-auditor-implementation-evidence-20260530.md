# MVP Gate 2 chapter_writer + chapter_auditor Implementation Evidence

日期：2026-05-30

角色：AgentCodex implementation worker

依据：
- Accepted plan commit：`b46a80a`
- Accepted plan：`docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`
- Controller decision：`docs/reviews/mvp-gate2-chapter-writer-auditor-plan-decision-20260530.md`

## Scope

本次实现只覆盖 MVP Gate 2：Fund 层 `chapter_writer` 与 `chapter_auditor` 单章 primitive。实现只消费 Gate 1 `ChapterFactProjection` / `ChapterFactInput` 与 writer 产物，不新增 orchestrator、repair loop、final assembler、chapter 0 生成链路、CLI `--use-llm`、Host/Agent/dayu runtime、promotion 或 release。

## Changed Files

- `fund_agent/fund/chapter_writer.py`
  - 新增章节写作 dataclass / Protocol / public function。
  - 实现 prompt 构造、LLM 响应契约解析、fail-closed 写作结果。
- `fund_agent/fund/chapter_auditor.py`
  - 新增章节审计 dataclass / Protocol / public function。
  - 实现 programmatic audit、LLM audit 行协议解析、汇总审计结果。
- `tests/fund/test_chapter_writer.py`
  - 覆盖 writer 输入、prompt、anchor/missing marker、stop_reason、关键缺锚、ITEM_RULE、无越界 import。
- `tests/fund/test_chapter_auditor.py`
  - 覆盖 programmatic audit、LLM audit 行协议、parse failure、repair_hint 聚合、non_asserted_facets、chapter 5 跨期缺口。
- `fund_agent/fund/README.md`
  - 同步 Fund 包当前实现说明，记录 Gate 2 primitive 与边界。
- `tests/README.md`
  - 同步新增测试文件与 targeted validation 命令。
- `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-evidence-20260530.md`
  - 本实现证据。

未修改 `fund_agent/fund/__init__.py`，因为 Gate 2 不需要包级稳定导出。

## Contract Summary

Writer：
- 公开契约使用显式 typed dataclass 与 Protocol：`ChapterLLMClient`、`ChapterLLMRequest`、`ChapterLLMResponse`、`ChapterWriterInput`、`ChapterWriterPrompt`、`ChapterDraft`、`ChapterWriteIssue`、`ChapterWriteResult`。
- `build_chapter_writer_input` 只从 `ChapterFactProjection` 选择单章 `ChapterFactInput`。
- `build_chapter_prompt` 将 CHAPTER_CONTRACT 的 `must_answer` / `must_not_cover`、preferred_lens、ITEM_RULE delete、evidence anchors、missing/unavailable/not_applicable、fund_type、non_asserted_facets 写入 prompt 约束。
- `write_chapter` 只通过显式注入的 `ChapterLLMClient` 生成文本；没有真实 provider SDK、env/config loading 或默认 client。
- anchor marker 固定为 `<!-- anchor:<anchor_id> -->`；missing marker 固定为 `<!-- missing:<reason> -->`。
- `max_output_chars` 是硬 post-check；超过即 `blocked`，不截断。
- `prompt_only` 固定返回 `status="blocked"`、`stop_reason="prompt_only"`、`draft=None`，不伪造草稿。
- 关键 `evidence_missing` 判定使用 `fact.required_by`、数值字段与 source field id；必要锚点缺失时 fail-closed。
- `bond_risk_evidence` 内部组级锚点不会被当作正文可引用锚点，错误信息明确要求后续 conversion helper 展开后才可引用。

Auditor：
- 公开契约使用显式 typed dataclass 与 Protocol：`ChapterAuditLLMClient`、`ChapterAuditLLMRequest`、`ChapterAuditLLMResponse`、`ChapterAuditInput`、`ChapterAuditIssue`、`ChapterProgrammaticAuditResult`、`ChapterLLMAuditResult`、`ChapterAuditResult`。
- Programmatic audit 覆盖结构、占位符、证据锚点、必答项、ITEM_RULE 删除内容、must_not_cover/禁用交易建议、non_asserted_facets 断言误用、chapter 5 跨期断言缺事实。
- chapter 5 缺 `cross_period_comparison` 时，只对稳定/变化断言短语触发确定性检查；带缺口、否定或问题式表达不阻断。
- LLM audit 默认 `audit_focus` 为 `evidence_support`、`must_not_cover_boundary`、`missing_semantics`、`readability`、`non_asserted_facet_boundary`。
- LLM audit 响应行协议固定为 `SEVERITY|LOCATION|MESSAGE`，`PASS|chapter|no issues` 表示零 issue 通过；informational-only 也是通过。
- LLM audit parse failure 固定生成 blocking `C1` issue 并 `status="blocked"`，不 silent pass。
- `ChapterAuditResult.repair_hint` 聚合优先级固定为 `needs_more_facts > regenerate > patch > none`。
- E2 evidence-vs-assertion source verification 明确延后到 Evidence Confirm gate；本 Gate 2 不读取源文、不做源码级核验。

## Fix Pass Summary

针对 DS implementation review 的 controller-accepted findings，本次 fix pass 只做以下修复：

- MEDIUM must_not_cover programmatic check gap：
  - 在 `chapter_auditor` 中新增确定性 `must_not_cover` 检查。
  - 规则只从 `ChapterContract.must_not_cover` 文本抽取明确禁止主题短语，命中正文即产生 blocking `C2` issue。
  - 新增测试覆盖第 1 章写入“基金经理选股能力”禁区时被阻断。
- LOW L1 checked_rules mismatch：
  - 保留 `L1` checked rule，并新增小型 R=A+B-C 数字闭环检查。
  - 当正文出现 `A=R-B`、`A-C` 或 `R=A+B-C` 等公式断言且包含百分比数值，但邻近上下文没有 `<!-- anchor:` marker 时，产生 blocking `L1` issue。
  - 新增测试覆盖缺 marker 阻断、有邻近 marker 不触发。
- LOW missing direct test for `mode="llm"` + `llm_client=None` after preflight passes：
  - 新增 writer 测试，确认 preflight 通过后缺少显式 LLM client 返回 `status="blocked"`、`stop_reason="llm_unavailable"`、`draft=None`。

## No Scope Creep Proof

- 新增 runtime 模块只位于 `fund_agent/fund/`，属于 Agent 层基金领域能力包。
- 未修改 Service/UI/Host/Agent/dayu runtime、CLI、repository、PDF、cache、source helper、downloader、parser、golden fixtures、score、snapshot、quality gate、FQ0-FQ6 或 final judgment。
- Writer/auditor 模块不导入 repository/PDF/cache/source/helper/parser/Service/Host/dayu，也不导入 provider SDK。
- 测试中的 fake LLM client 只存在于测试文件；生产代码没有 fake pass 或默认真实 client。
- 没有通过 `extra_payload` 传递显式参数；契约字段均为 dataclass 显式字段。

## Validation

已执行：

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
38 passed in 0.78s
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1010 passed in 4.83s
Required test coverage of 50% reached. Total coverage: 91.69%
```

```text
git diff --check
```

结果：无输出，退出码 0。

## Residual Risks

- Gate 2 只提供单章 writer/auditor primitive；跨章节编排、repair loop、accepted conclusion 注入、final assembler 与 CLI 接入属于后续 Gate。
- E2 源文核验仍未实现，需由 Evidence Confirm gate 基于源文仓库接口完成。
- `bond_risk_evidence` 组级锚点仍需后续 conversion helper 展开为正文可引用 anchor。
- 当前 LLM audit 只冻结响应行协议与 parse failure 语义，不证明真实 LLM 审计质量。

## Blocking Questions

无。
