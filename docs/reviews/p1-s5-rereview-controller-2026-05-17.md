# P1-S5 Re-review Controller Confirmation

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S5 `§3` 表现提取与投资者收益 fallback
> Source judgment：`docs/reviews/p1-s5-code-review-controller-judgment-2026-05-17.md`
> Source fix artifact：`docs/reviews/p1-s5-fix-2026-05-17.md`

## 1. 说明

- `AgentMiMo` 与 `AgentGLM` 的独立初审均已完成，并用于 controller finding judgment。
- 本轮 fix 覆盖：
  - `fund_agent/fund/extractors/models.py`
  - `fund_agent/fund/extractors/performance.py`
  - `tests/fund/extractors/test_performance.py`
  - `tests/fixtures/fund/extractors/performance/performance_with_partial_nav_only.txt`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - `docs/implementation-control.md`
- 这些 fix 已同时关闭：
  - `nav_benchmark_performance` 部分命中的语义误导
  - `estimated` 路径状态命名误导
  - 证据锚点完整性测试缺口
  - README / 总控同步缺口
- controller 依据：
  - 已接受的 controller judgment
  - fix artifact
  - 当前最终 worktree 快照
  - 本地验证命令结果
  
  对 A1 / A2 做最终状态确认。

## 2. Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py -q
```

结果：

```text
9 passed in 0.67s
```

## 3. Final Status Mapping

### A1-已修复-中-`nav_benchmark_performance` 在部分命中时仍标记为 `direct`

- **当前证据**:
  - [fund_agent/fund/extractors/performance.py](/Users/maomao/fund-agent/fund_agent/fund/extractors/performance.py:144) 当前只有在两项都缺失时才返回完全 `missing`
  - [fund_agent/fund/extractors/performance.py](/Users/maomao/fund-agent/fund_agent/fund/extractors/performance.py:151) 当前仅在两个字段都命中时才返回 `extraction_mode="direct"`
  - [fund_agent/fund/extractors/performance.py](/Users/maomao/fund-agent/fund_agent/fund/extractors/performance.py:153) 部分命中时显式补充缺失说明
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:182) 已新增部分命中测试
- **测试支撑**:
  - 部分命中路径当前已由测试锁定
- **最终状态**: `已修复`

### A2-已修复-低-`estimated` 路径的 `fallback_status` 命名存在语义误导

- **当前证据**:
  - [fund_agent/fund/extractors/performance.py](/Users/maomao/fund-agent/fund_agent/fund/extractors/performance.py:198) 当前状态名已改为 `estimated_disclosure_in_section`
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:144) 测试已同步锁定新状态名
- **测试支撑**:
  - `estimated` 路径当前测试通过
- **最终状态**: `已修复`

### A3-已修复-低-证据锚点完整性 contract 未被测试锁定

- **当前证据**:
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:85) 已断言 `source_kind`
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:86) 已断言 `section_id`
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:87) 已断言 `document_year`
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:88) 已断言 `note`
  - [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:116) 与 [tests/fund/extractors/test_performance.py](/Users/maomao/fund-agent/tests/fund/extractors/test_performance.py:146) 已对 investor_return 两条命中路径补齐同类断言
- **测试支撑**:
  - 当前 anchor 完整性 contract 已被测试锁定
- **最终状态**: `已修复`

### A4-已修复-中-`fund` 与 `tests` 文档未随当前稳定 extractor 契约同步

- **当前证据**:
  - [fund_agent/fund/README.md](/Users/maomao/fund-agent/fund_agent/fund/README.md:11) 已补充 `extract_performance(report)` 的当前用法
  - [fund_agent/fund/README.md](/Users/maomao/fund-agent/fund_agent/fund/README.md:33) 已明确 `PerformanceExtractionResult` 的当前边界
  - [fund_agent/fund/README.md](/Users/maomao/fund-agent/fund_agent/fund/README.md:37) 已明确 `investor_return` 的 `direct / estimated / missing`
  - [tests/README.md](/Users/maomao/fund-agent/tests/README.md:11) 已纳入 `tests/fund/extractors/test_performance.py`
  - [tests/README.md](/Users/maomao/fund-agent/tests/README.md:13) 已纳入 `tests/fixtures/fund/extractors/performance/*.txt`
  - [tests/README.md](/Users/maomao/fund-agent/tests/README.md:24) 已更新当前 extractor 测试命令
- **测试支撑**:
  - 当前 extractor 相关测试已整体通过
- **最终状态**: `已修复`

### A5-已修复-中-总控文档尚未把 `P1-S5` implementation 完成事实和 review gate 对齐

- **当前证据**:
  - [docs/implementation-control.md](/Users/maomao/fund-agent/docs/implementation-control.md:34) 当前 gate 保持在 `P1-S5 implementation + review`
  - [docs/implementation-control.md](/Users/maomao/fund-agent/docs/implementation-control.md:55) 已补充 `P1-S5` implementation 已完成、当前进入 review 的事实
  - [docs/implementation-control.md](/Users/maomao/fund-agent/docs/implementation-control.md:61) 下一 entry point 已明确仍在 `P1-S5 implementation + review`
  - [docs/implementation-control.md](/Users/maomao/fund-agent/docs/implementation-control.md:107) 已登记 `P1-S5` baseline reconciliation 与 implementation artifact
  - [docs/implementation-control.md](/Users/maomao/fund-agent/docs/implementation-control.md:298) 已新增 `P1-S5 当前状态（2026-05-17）`
  - [docs/implementation-control.md](/Users/maomao/fund-agent/docs/implementation-control.md:499) 已写入 phase 进展日志
- **测试支撑**:
  - 总控更新不依赖额外自动化测试；其正确性由当前 accepted plan、implementation artifact、review artifact 和最终 worktree 快照对照确认
- **最终状态**: `已修复`

## 4. Re-review Conclusion

- `P1-S5 re-review` 结论：`pass`
- 当前没有新的 blocker
- `P1-S5` 可推进到 accepted local commit，并把下一 entry point 切到 `P1-S6 implementation + review`
