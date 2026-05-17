# P1-S1 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S1 文档访问契约收口
> Branch：`chore/reconcile-baseline`
> Review artifacts：
> - `docs/reviews/p1-s1-code-review-mimo-2026-05-17.md`
> - `docs/reviews/p1-s1-code-review-glm-2026-05-17.md`
> Implementation artifact：
> - `docs/reviews/p1-s1-implementation-2026-05-17.md`

## 1. 裁决前提

- 两份 code review 已独立完成，且都确认 `P1-S1` 核心目标达成：
  - 对外唯一仓库入口为 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`
  - 公共契约位于 `fund_agent/fund/documents/*`
  - `fund_agent/fund/pdf/*` 已降为仓库内部 helper / adapter
- controller 对当前最终快照做了二次核对，并运行：

```bash
.venv/bin/python -m pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py
```

结果：`7 passed`

- 注意：两份初审 artifact 生成后，`tests/fund/documents/test_repository.py` 又新增了仓库输入校验与标准化测试，因此与“负向测试缺失”相关的 finding 必须按**当前最终快照**重新裁决。

## 2. Accepted Findings

### A1-未修复-高-async 调用链中仍直接执行同步 I/O

- **来源**:
  - `AgentMiMo` Finding 1
  - `AgentGLM` Finding F1
- **文件(当前行号)**:
  - [fund_agent/fund/pdf/downloader.py](/Users/maomao/fund-agent/fund_agent/fund/pdf/downloader.py:33)
  - [fund_agent/fund/pdf/downloader.py](/Users/maomao/fund-agent/fund_agent/fund/pdf/downloader.py:126)
  - [fund_agent/fund/documents/adapters/annual_report_pdf.py](/Users/maomao/fund-agent/fund_agent/fund/documents/adapters/annual_report_pdf.py:223)
  - [fund_agent/fund/documents/adapters/annual_report_pdf.py](/Users/maomao/fund-agent/fund_agent/fund/documents/adapters/annual_report_pdf.py:228)
- **直接证据**:
  - `_download_annual_report_pdf()` 是 async 函数，但内部直接调用同步的 `_find_annual_report_id()`
  - `AnnualReportPdfAdapter.load_annual_report()` 是 async 函数，但内部直接调用同步的 `text_extractor` / `table_extractor` / `section_locator`
- **裁决**: `accepted`
- **为什么接受**:
  - 这是当前 slice 允许文件内可直接修复的问题
  - 不修会让后续 Runtime / Service 并发场景退化为串行，属于真实行为风险，而不是未来过度设计
- **Fix 要求**:
  - 不改 `parser.py`
  - 仅在当前允许文件内通过 `asyncio.to_thread(...)` 或等价方式隔离阻塞调用
  - 如低成本可测，补充一条能证明 wrapper 生效的测试；否则至少更新验证说明
- **当前状态**: `未修复`

### A2-未修复-中-找不到目标年份时静默回退到最新年报

- **来源**:
  - `AgentMiMo` Finding 2
  - `AgentGLM` Finding F2
- **文件(当前行号)**:
  - [fund_agent/fund/pdf/downloader.py](/Users/maomao/fund-agent/fund_agent/fund/pdf/downloader.py:41)
- **直接证据**:
  - `_find_annual_report_id()` 在未命中目标年份但存在其它年报时，仍返回最新一份完整年报 ID
  - 这会让 `_download_annual_report_pdf()` 以目标年份文件名保存实际属于其它年份的 PDF
- **裁决**: `accepted`
- **为什么接受**:
  - 这是数据正确性问题，且可在当前 slice 内小范围修复
  - 与统一仓库契约直接相关，不能带着静默错配进入 `P1-S2`
- **Fix 要求**:
  - 移除该 silent fallback，未命中目标年份时返回 `None` 并让上层抛出 `FileNotFoundError`
  - 补一条对应测试，覆盖“无目标年份时不应回退到其它年份”
- **当前状态**: `未修复`

## 3. Deferred Findings

### D1-未修复-中-章节置信度固定为 `1.0`

- **来源**:
  - `AgentMiMo` Finding 3
- **裁决**: `deferred-with-owner`
- **Owner / Destination**: `P1-S2 章节定位修复与 §3 冻结`
- **原因**:
  - 该信号是否应低于 `1.0`，取决于 `section_locator` 的稳定契约和匹配规则来源
  - 在 `P1-S2` 修复章节定位前，当前只用常量改数值无法真正建立可信度语义，收益有限

### D2-未修复-低-缓存目录仍依赖相对路径 CWD

- **来源**:
  - `AgentMiMo` Finding 6
- **裁决**: `deferred-with-owner`
- **Owner / Destination**: `P1-S3 两级缓存与仓库内解析物化`
- **原因**:
  - 该问题与缓存层冻结和缓存根目录策略一起裁决更合理
  - 当前 `P1-S1` 的目标是公共契约收口，不是缓存根路径设计定版

## 4. Rejected Findings

### R1-证据失效-低-表格缺页号时默认写入 `0`

- **来源**:
  - `AgentMiMo` Finding 4
  - `AgentGLM` Finding F3
- **裁决**: `rejected-with-reason`
- **原因**:
  - 当前最终快照已不再使用 `raw_table.get("page_number", 0)`
  - `annual_report_pdf.py` 已改为 `_normalize_page_number()` 显式校验，缺失或非法页码会抛 `ValueError`

### R2-证据失效-低-`DocumentKey.document_kind` 从 `Literal` 弱化为 `str`

- **来源**:
  - `AgentMiMo` Finding 5
- **裁决**: `rejected-with-reason`
- **原因**:
  - 当前最终快照已引入 `ANNUAL_REPORT_DOCUMENT_KIND` 与 `Literal["annual_report"]`

### R3-证据失效-中-负向测试完全缺失

- **来源**:
  - `AgentMiMo` Finding 7
  - `AgentGLM` Finding F5
- **裁决**: `rejected-with-reason`
- **原因**:
  - 当前最终快照已新增：
    - 基金代码标准化测试
    - 非法 fund_code / year 输入校验测试
  - 该 finding 的“完全缺失”判断已经失效
- **备注**:
  - `A2` fix 仍要求顺手补一条“无目标年份时报错”的测试，但这已并入 accepted finding，不再单列为独立缺陷

### R4-驳回-低-年份校验需要增加上界

- **来源**:
  - `AgentGLM` Finding F4
- **裁决**: `rejected-with-reason`
- **原因**:
  - 当前需求只要求正整数年份
  - 再引入“未来年份上界”属于额外策略，不是 `P1-S1` 为达成统一仓库契约所必需

## 5. 当前 Gate 结论

- `P1-S1 code review` 当前结论：`fix required`
- 进入原因：
  - 存在 2 条 controller-accepted findings（A1 / A2）
  - 它们都属于当前 slice 范围内的小范围修复，不应后移
- 下一 gate：
  - `P1-S1 fix -> re-review`
