# P1-S8 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵
> Implementation artifact：`docs/reviews/p1-s8-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现新增：
  - `FundDataExtractor`
  - `StructuredFundDataBundle`
  - `FundNavDataAdapter`
  - `NavDataResult`
  - `nav_cache`
- controller 本地边界检查确认：
  - `data_extractor.py` 不直接读文件
  - `data_extractor.py` 不直接写缓存
  - 净值缓存写入只在 `nav_data.py`
  - 测试不访问真实网络
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q
```

结果：`32 passed`

## 2. Accepted Findings

### A1-已修复-低-README 测试命令路径 typo

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - `tests/README.md` 中曾出现 `test/fund/data/test_nav_data.py`
  - 正确路径应为 `tests/fund/data/test_nav_data.py`
- **修复**：
  - 已同步为当前真实测试路径

## 3. Deferred Findings

### D1-未修复-中-真实 PDF 样本矩阵未在本 slice 跑通

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P3 / end-to-end validation`
- **原因**：
  - 当前 P1-S8 以 fake repository 锁定 P1 façade contract 和 36 格矩阵
  - 真实 PDF 下载、解析和端到端报告属于后续端到端验证范围

### D2-未修复-低-`structured_data` 未物化为 SQLite 表

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`later cache governance`
- **原因**：
  - 当前已用 `StructuredFundDataBundle` 冻结 schema
  - 直接物化 SQLite 表会引入缓存治理和失效策略，当前没有上层消费者必须依赖该表
  - 维持 dataclass 契约更符合“以代码为准，不设计未来”

### D3-未修复-低-默认 akshare fetcher 未做真实网络验证

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P3 / external integration validation`
- **原因**：
  - 单元测试必须可重复，不应依赖真实网络
  - fetcher 已封装并可注入，真实网络验证应放在外部集成阶段

## 4. 当前 Gate 结论

- `P1-S8 code review` 结论：`pass`
- 当前没有 blocker
- `P1-S8` 可推进到 accepted local commit
- P1 可进入 aggregate review / phase closeout
