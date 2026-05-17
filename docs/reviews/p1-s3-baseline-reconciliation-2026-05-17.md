# P1-S3 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S3 两级缓存与仓库内解析物化
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S3 implementation + review`
> 上一 accepted slice commit：`c3bd264` (`gateflow: accept P1 P1-S2`)

## 1. 触发原因

- `docs/implementation-control.md` 当前 next entry point 已切到 `P1-S3 implementation + review`。
- `docs/reviews/p1-plan-2026-05-17.md` 第 8.2 节要求：
  - 落地 raw PDF 与 parsed report 的文件缓存 + SQLite 缓存
  - 仓库优先命中缓存，而不是重复下载 / 重复全文解析
  - `structured_data` 不能在本 slice 提前冻结

## 2. 当前工作树状态

当前 `git status --short` 仅剩无关未跟踪项：

```text
?? docs/reviews/code-review-20260517-0727.md
?? scripts/
```

裁决：

- 这两项不纳入 `P1-S3` 范围
- 当前可以安全基于 `HEAD=94c71e1` 继续推进

## 3. 代码基线事实

### 3.1 当前 documents 层现状

当前 `fund_agent/fund/documents/` 仅包含：

- `models.py`
- `repository.py`
- `adapters/annual_report_pdf.py`

缺失项：

- 没有 `fund_agent/fund/documents/cache.py`
- repository 没有 SQLite / 文件缓存抽象
- repository 每次调用都会继续走：
  - downloader
  - `extract_text`
  - `extract_tables`
  - `locate_sections`

### 3.2 当前 repository 行为

当前 [repository.py](/Users/maomao/fund-agent/fund_agent/fund/documents/repository.py:92) 的事实：

- `FundDocumentRepository.load_annual_report(...)` 公开签名已经稳定
- 它只做：
  - `fund_code` / `year` 校验
  - 直接委派 `self._annual_report_loader.load_annual_report(...)`

当前没有：

- 文档元信息缓存
- parsed report 物化缓存
- `force_refresh=True` 对缓存层的穿透行为

### 3.3 当前 adapter / downloader 行为

当前 [annual_report_pdf.py](/Users/maomao/fund-agent/fund_agent/fund/documents/adapters/annual_report_pdf.py:202) 的事实：

- 每次 `load_annual_report()` 都会：
  - 下载或命中底层 PDF 文件
  - 重新提取全文
  - 重新提取表格
  - 重新定位章节

当前 [downloader.py](/Users/maomao/fund-agent/fund_agent/fund/pdf/downloader.py:69) 的事实：

- 只对原始 PDF 文件有本地文件缓存
- 并没有 parsed report 的持久化缓存

### 3.4 当前测试现状

当前 `tests/fund/documents/` 只有：

- `test_repository.py`

缺失项：

- 没有 `tests/fund/documents/test_cache.py`
- 没有任何针对：
  - 首次加载写入缓存
  - 重复加载命中 parsed report 缓存
  - `force_refresh=True` 绕过缓存
  - repository 不再重复调 downloader / parser

的回归测试

## 4. 范围裁决

### 4.1 Allowed files/modules

按已接受 plan，`P1-S3` 允许文件为：

- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `tests/fund/documents/test_cache.py`
- `tests/fund/documents/test_repository.py`

### 4.2 当前最小必要实现范围

controller 裁决本轮最小必要落地为：

- `fund_agent/fund/documents/cache.py`
  - 定义 raw PDF / parsed report 的仓库内缓存抽象
  - 只覆盖 P1-S3 当前需要的最小 schema，不预设计 `structured_data`
- `fund_agent/fund/documents/repository.py`
  - 在不改变公开签名的前提下接入缓存层
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
  - 保持其仍能生成 `ParsedAnnualReport`
  - 但 repository 需要能把其结果物化并复用
- `tests/fund/documents/test_cache.py`
  - 验证 raw PDF / parsed report 的缓存命中和 refresh 行为
- `tests/fund/documents/test_repository.py`
  - 补充 repository 级“不再重复下载 / 不再重复解析 / force_refresh 穿透”断言

### 4.3 当前不建议触碰

- `fund_agent/fund/pdf/parser.py`
  - `P1-S2` 刚被冻结，本轮不应再改章节语义
- `fund_agent/fund/data/nav_data.py`
- 任意 extractor
- `FundDocumentRepository.load_annual_report(...)` 公开签名
- `structured_data` 表或任何 P1-S8 才允许冻结的 schema

## 5. Root Cause 裁决

`P1-S3` 当前要解决的不是“缓存目录不存在”这么浅的问题，而是：

1. documents 层没有“已解析年报”的稳定物化层
   - 导致 repository 每次都重新执行文本提取、表格提取、章节定位
2. 当前只有原始 PDF 文件缓存
   - 无法满足 plan 要求的“重复加载同一年报不重新全文解析”
3. 当前测试只覆盖仓库契约，不覆盖缓存命中行为
   - 缺少可重复验证的回归护栏

## 6. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S3` 可以直接进入 implementation
- controller 对本轮的额外约束：
  - 不接受把 SQLite 或缓存细节直接暴露给上层查询
  - 不接受提前落 `structured_data`
  - 不接受为了省事把 parsed report 缓存塞回 `pdf/*`
  - 若最终实现不含 `test_cache.py`，视为未满足本 slice 最小闭环

## 7. 后续执行约束

- `AgentCodex` 负责：
  - 只在 `P1-S3` 允许文件内完成实现
  - 输出 durable implementation artifact
  - 不 commit、不 push、不进入下一 gate
- `AgentMiMo` 与 `AgentGLM` 负责：
  - 独立 code review / re-review
  - 重点检查是否真的避免重复下载 / 重复全文解析、是否没提前冻结 `structured_data`、是否无缓存越界
- controller 负责：
  - 对 findings 做 accepted / deferred / rejected 裁决
  - 必要时继续 `fix -> re-review`
  - 通过后再更新 `docs/implementation-control.md`
