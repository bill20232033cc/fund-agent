# 测试手册

当前测试按 Capability 边界分层，新增用例应跟随实现所在目录组织，并优先覆盖当前稳定公共契约，而不是偶然实现细节。

## 当前目录

- `tests/fund/documents/test_repository.py`：文档仓库契约测试，验证仓库对外返回 `ParsedAnnualReport`，不暴露本地 `Path`
- `tests/fund/documents/test_cache.py`：文档缓存最小闭环测试，覆盖 PDF 元信息缓存、parsed report 物化和缓存失效回退
- `tests/fund/pdf/test_downloader.py`：PDF 下载 helper 测试，验证内部缓存命中、强制刷新下载和年报 URL 组装
- `tests/fund/pdf/test_parser.py`：章节定位测试，覆盖 `§3` 正文命中、目录误判回归和偏移单调递增
- `tests/fund/extractors/test_profile.py`：基础画像 extractor 测试，覆盖分类先行、`classified_fund_type` / `classification_basis` 稳定输出，以及费率/基准/规模/经理 anchor
- `tests/fixtures/fund/extractors/profile/*.txt`：基础画像最小文本夹具，当前覆盖主动权益、增强指数、债券三类样本

## 运行方式

运行当前已接受 slice 直接相关的测试：

```bash
pytest tests/fund/documents -q
pytest tests/fund/pdf/test_parser.py -q
pytest tests/fund/extractors/test_profile.py -q
```

如果只验证 P1-S4 当前 worktree，可运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q
```

## 维护约定

- 新增 Capability 测试时，优先使用 fixture、mock 或临时目录隔离网络和文件系统副作用。
- 文档仓库相关测试应围绕公共契约断言，不直接把 `pdf/*` helper 当成上层接口。
- `pdf/*` 目录下的测试允许直接覆盖内部 helper，但 README、示例和业务代码不应把它们当成稳定入口。
- extractor 测试必须优先锁定章节边界、证据锚点和 `missing/direct/estimated` 状态，不把后续 P2 的分析结论混入 P1 数据层测试。
- 新增基金类型或章节 extractor 时，先补 fixture，再补测试，再扩实现；不要只靠真实年报手工回归。
