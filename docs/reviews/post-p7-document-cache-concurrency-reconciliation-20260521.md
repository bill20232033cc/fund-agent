# Post-P7 Document Cache Concurrency Reconciliation（2026-05-21）

## 背景

Repo-level deepreview 将文档仓库并发与 TOCTOU 列为 post-P7 follow-up。完整仓库事务化设计会牵动 repository、cache、source、parser 与跨进程锁，本轮只收口当前代码中已经可以低风险修复的同进程同实例并发问题。

## 裁决

接受“同进程并发读写缓存需要最小串行保护”的 finding，但不把本轮扩展为完整 repository transaction redesign。

本轮范围：

- parsed report 缓存的 `load_parsed_report()` / `save_parsed_report()` 在同一 `AnnualReportDocumentCache` 实例内串行执行。
- EID PDF 下载对同一基金代码/年份使用实例级锁，避免同 key 并发请求重复下载并竞争写同一路径。

本轮不做：

- 不实现跨进程文件锁。
- 不重构 SQLite transaction 边界。
- 不改变 Eastmoney helper 的缓存接口。
- 不实现 parse 失败后的 repository retry/invalidate 状态机。

## 代码收口

变更点：

- `fund_agent/fund/documents/cache.py`
  - 为 `AnnualReportDocumentCache` 增加实例级 `asyncio.Lock`。
  - `load_parsed_report()` 和 `save_parsed_report()` 在进入同步 SQLite/JSON 读写前获取锁。
- `fund_agent/fund/documents/sources.py`
  - 为 `EidAnnualReportSource` 增加按 `fund_code:year` 分桶的实例级锁。
  - 同 key 请求串行执行；后到请求在首个请求落地有效 PDF 后复用缓存，不重复访问 PDF 端点。
- `tests/fund/documents/test_cache.py`
  - 增加 parsed report load/save 串行回归测试。
- `tests/fund/documents/test_annual_report_sources.py`
  - 增加同 key EID 并发 fetch 只下载一次 PDF 的回归测试。
- `fund_agent/fund/README.md`
  - 明确当前并发保护边界是同进程同实例，不是跨进程锁或完整事务化仓库。

## 验证

已运行：

```bash
pytest tests/fund/documents/test_cache.py tests/fund/documents/test_annual_report_sources.py -q
```

预期结果：文档缓存和来源编排测试全部通过。

## 残余风险

跨进程并发、多个 cache/source 实例共享同一路径、PDF 存在性检查后被外部删除、parse 失败后的自动失效重试仍未在本轮解决。这些需要单独的 repository-level design slice，而不是在当前轻量锁补丁中隐式完成。
