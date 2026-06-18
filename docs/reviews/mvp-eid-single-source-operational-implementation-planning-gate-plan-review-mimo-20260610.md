# EID Single Source Operational Implementation Planning Gate — Plan Review (MiMo)

Date: 2026-06-10

Reviewer: AgentMiMo

Gate: `EID Single Source Operational Implementation Planning Gate`

Plan under review: `docs/reviews/mvp-eid-single-source-operational-implementation-planning-gate-plan-20260610.md`

## Verdict

**PASS**

## Review Summary

The plan is code-generation-ready, correctly enforces EID single-source policy with `fallback_enabled=false`, and satisfies all eight review criteria. No blocking findings.

## Criterion-by-Criterion Analysis

### 1. 是否真的 single-source EID，且 fallback_enabled=false

**PASS.**

- §1 明确 `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`。
- Slice 1 将 `AnnualReportSourceOrchestrator(None)` 默认从 `(EidAnnualReportSource, EastmoneyAnnualReportSource)` 改为恰好一个 `EidAnnualReportSource`。
- §9 failure category matrix 中所有五类失败均为 terminal、不 fallback。
- Slice 2 新增 `selected_source="eid"`, `source_mode="single_source_only"`, `fallback_enabled=False` 元数据字段。
- Slice 3 cache admissibility 检查要求全部六个条件同时满足才可复用缓存。

代码验证确认：当前代码默认 sources 确实是 `(EidAnnualReportSource, EastmoneyAnnualReportSource)` 二元组，且 `selected_source` / `source_mode` / `fallback_enabled` 字段确实不存在于当前代码中——这正是需要实现的增量变更。

### 2. 是否没有把 Eastmoney/基金公司官网/CNINFO 建模为当前生产 fallback

**PASS.**

- §2 non-goals 明确 "No Eastmoney, fund-company official website/CDN, CNINFO or multi-source fallback production behavior"。
- §1 Slice 1 要求 "Keep `EastmoneyAnnualReportSource` only as an unused deferred candidate"。
- §17 residual risk 将 Eastmoney wrapper integrity bug 标记为 "Deferred future source-candidate/fallback risk only; not production-reachable under EID-only default"。
- startup judgment 明确 "Eastmoney、fund-company official website/CDN、CNINFO and other non-EID routes are deferred source candidates or historical evidence-intake routes only"。

### 3. 是否保持 FundDocumentRepository 为生产年报访问唯一入口

**PASS.**

- §8 明确 "`FundDocumentRepository` remains the only production annual-report read boundary"。
- §8 第 6 条 "The repository must not expose local PDF paths to UI/Service/Host/renderer/quality gate beyond existing internal metadata; callers continue consuming `ParsedAnnualReport`"。
- Slice 4 回归测试验证 "repository boundary preserved" 和 "returns ParsedAnnualReport without path exposure"。

### 4. 是否禁止 UI/Service/Host/renderer/quality gate 直接调用 source/downloader/cache/parser helper

**PASS.**

- §2 non-goals 列出 "No direct source/downloader/cache/parser calls from UI, Service, Host, renderer or quality gate"。
- §11 forbidden actions 列出 "invoking `FundDocumentRepository.load_annual_report()` against real sources"。
- §11 forbidden files 包含 `fund_agent/ui/`, `fund_agent/services/`, `fund_agent/host/`, `render/`。
- startup judgment §当前控制真源 明确 "UI, Service, Host, renderer and quality gate must not directly call EID source, downloader helper, PDF cache, parser internals or third-party source helpers"。

### 5. schema_drift / identity_mismatch / integrity_error 是否 fail-closed；not_found/unavailable 在 single-source mode 是否 terminal 且不 fallback

**PASS.**

- §9 failure matrix 明确所有五类失败均为 "Terminal? Yes" 且 "Fallback? No"。
- §9 指出 "Implementation may introduce `AnnualReportSourceFailClosedError` to replace fallback-specific wrapping for schema/mismatch/integrity"。
- §4 EID discovery contract 中 `schema_drift` 和 `identity_mismatch` 的触发条件明确定义。
- §6 PDF integrity contract 中 `integrity_error` 的触发条件明确定义，且 "No HTML body, redirect landing page, JSON error page, empty body or non-PDF file may be classified as `unavailable` after a 200 response with non-PDF content. It is `integrity_error`"。

代码验证确认：当前代码中 `schema_drift`/`identity_mismatch`/`integrity_error` 已经 fail-closed（`_raise_fallback_blocked`），`not_found`/`unavailable` 当前允许 fallback——plan 正确描述了需要将这两类也 terminal 化。

### 6. no-live validation matrix 是否完整，且没有把 live smoke 当作验收

**PASS.**

- §14 no-live validation matrix 包含 8 项验证：source policy tests, repository/cache tests, boundary regressions, broader local regression, lint, whitespace, forbidden path audit, no fallback wording grep。
- §14 forbidden validation 明确排除：`fund-analysis analyze ...` against real source, `FundDocumentRepository.load_annual_report()` with default real source, curl/DNS/socket/browser/network/PDF live smoke, fallback invocation, provider/LLM commands。
- §19 optional live EID smoke gate 明确标记为 "deferred; requires separate user authorization"，且 "This is not part of implementation acceptance"。
- §13 no-live tests per slice 使用 `httpx.MockTransport` 和 fake sources，不依赖网络。

### 7. allowed/forbidden files 是否合理，是否有 scope drift 或过度设计

**PASS.**

- §10 allowed files 限于 `fund_agent/fund/documents/` 下的核心文件（models, sources, repository, adapters, cache）和对应测试，加上必要的文档更新。范围合理。
- §11 forbidden files 正确排除 `fund_agent/tools/`, `scripts/claude_mimo_simple.py`, UI/Service/Host/agent 层, extractors, parser, downloader, render, reports 等。
- §11 forbidden actions 正确排除 live 验证、staging/commit/push/PR、dayu runtime 依赖、extra_payload 等。
- Slice 1 stop condition 处理了 reviewer 可能要求保留 multi-source injection 用于测试的边界情况。
- 元数据变更是 additive（新增可选字段），不需要 SQLite migration，不过度设计。
- cache admissibility 通过 policy check 而非 bulk migration 实现，避免了不必要的数据迁移风险。

### 8. 是否正确忽略 fund_agent/tools/ 和 scripts/claude_mimo_simple.py residue

**PASS.**

- §11 forbidden files 明确列出 `fund_agent/tools/` 和 `scripts/claude_mimo_simple.py`。
- §11 forbidden actions 列出 "importing, executing or reading source-like residue paths"。
- startup judgment §显式忽略边界 明确 "Planning worker and reviewers must not use these paths as architecture truth, source truth, source policy evidence, implementation evidence, package design input, allowed files, or validation inputs"。

## Additional Observations

### 强项

1. **代码验证准确性高**：§3 current EID implementation inventory 的每一项声明均经代码验证确认。特别是准确识别了 `selected_source`/`source_mode`/`fallback_enabled` 字段不存在于当前代码中。
2. **Eastmoney integrity bug 处理得当**：plan 没有试图在本 gate 修复 Eastmoney wrapper 的 `ValueError` 路径可能掩盖 PDF integrity failure 的问题，而是正确地将其标记为 deferred risk。
3. **Legacy cache 处理务实**：通过 policy check 忽略旧缓存而非 bulk migration，避免了数据丢失风险。
4. **Direct evidence matrix 完整**：§15 列出了所有关键声明的直接证据来源，可追溯。
5. **Rollback 简单明确**：§16 rollback 方案不涉及 cache migration，仅需 revert commit。

### 无阻塞问题

未发现 scope drift、过度设计、架构边界违反或验收标准缺失。

## Conclusion

Plan 满足所有八个 review criteria，是 code-generation-ready 的。五个 implementation slice 排序合理、边界清晰、测试覆盖完整。建议按 plan 进入 implementation gate。
