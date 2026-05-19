# P4-S1 Code Review Controller Judgment

> 日期：2026-05-19
> Gate：`P4-S1 review judgment`
> 审查对象：Selected Fund Extraction Snapshot + Quality Gate MVP
> Review artifacts：
> - `docs/reviews/p4-s1-code-review-mimo-20260519.md`
> - `docs/reviews/p4-s1-code-review-glm-20260519.md`
> 裁决：PASS；无 blocking finding；可进入 P4-S1 accepted / next gate。

## 总体裁决

MiMo 和 GLM 均给出 PASS，且都确认以下核心条件成立：

- Snapshot 核心位于 Capability 层 `fund_agent/fund/extraction_snapshot.py`。
- UI 通过 Service 层 `ExtractionSnapshotService` 调用，不直接依赖 Capability。
- 年报访问通过 `FundDataExtractor.extract(...)` 进入，没有在 UI/Service 直接读取 PDF 或 cache。
- 输入参数显式建模，没有 `extra_payload`。
- Snapshot schema 与 `docs/implementation-control-p4.md` §4.5 字段契约一致。
- 单基金失败会写入 `errors.jsonl` 并继续 run。
- 重复代码会在 summary 标红，不阻断 P4-S1。
- `004393` 当前误判为 `index_fund` 时被记录为 known failure，没有被静默修正。
- 测试均使用 fake extractor / monkeypatch / dry-run，不触发真实网络或 PDF。

因此 P4-S1 implementation 可接受。

## Finding 裁决

| 来源 | Finding | Severity | Controller 裁决 | 处理 |
|---|---|---:|---|---|
| MiMo | `_validate_request` docstring 的 Raises 描述未单独点名 `limit` | INFO | accepted as cleanup | 不阻塞；后续文档清理可补 |
| MiMo | `_normalize_extraction_mode` 对未知模式降级为 `missing` 的行为可更明确 | INFO | accepted as cleanup | 不阻塞；P4-S2 scoring 前可补 doc/test |
| MiMo | `estimated/partial` normalization 测试不足 | LOW | deferred to P4-S2 | P4-S2 字段评分会更依赖 extraction_mode，届时补充 |
| MiMo | Service validation rejection 分支未全覆盖 | LOW | accepted as non-blocking test gap | 当前核心路径、非法代码和 Capability 参数校验已覆盖；不阻塞 |
| GLM | `_path_for_output` 使用 CWD-relative 而非严格 repo-root-relative | INFO | accepted risk | P4-S1 CLI 默认从 repo root 运行；若后续需要跨 cwd 稳定输出，在 P4-S2 前清理 |
| GLM | `004393` known failure note 是单基金硬编码 | INFO | accepted by design | P4-S1 明确记录已知 failure，不做通用 registry；P4-S3 修分类器后移除或泛化 |
| GLM | 重复代码不去重，会重复抽取 | INFO | accepted by design | P4-S1 控制文档允许重复但 summary 标红；真实修正需用户核对 CSV |
| GLM | `SnapshotExtractor` 与已有 extractor Protocol 签名重复 | LOW | deferred cleanup | 结构性类型重复不影响 correctness；若后续出现第三个复用点再抽共享 Protocol |
| GLM | summary 中失败行展示原始 error message | INFO | accepted risk | P4-S1 summary 面向人工扫描；结构化错误仍在 `errors.jsonl` |

## Controller 自验

- `.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/ui/test_cli.py tests/services -q`
  - `13 passed in 0.70s`
- `.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/ui/test_cli.py tests/services tests/scripts/test_selected_funds_smoke.py -q`
  - `17 passed in 0.39s`
- `.venv/bin/python scripts/selected_funds_smoke.py --limit 1`
  - dry-run passed；确认 `016492` 重复
- `.venv/bin/fund-analysis extraction-snapshot --help`
  - passed
- `git diff --check ...`
  - passed

## 残余风险

- 未运行真实 `fund-analysis extraction-snapshot --run-id ... --fund-code 004393`，因为会触发真实年报仓库、PDF/network 与净值数据路径。该项作为人工 smoke 或后续 P4-S1 accepted 后验证。
- P4-S1 只度量 coverage / traceability，不度量 correctness；correctness 留到 P4-S2 golden set。
- `004393` 分类误判仍按计划留给 P4-S3 修复。

## 下一步

P4-S1 可进入 accepted 状态。下一 gate 为 `P4-S2 plan / implementation`，前提是将 P4-S1 artifact、review artifacts 和本裁决写回控制文档。
