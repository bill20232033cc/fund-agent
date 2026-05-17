# 测试手册

当前测试按能力边界分层，新增用例应尽量跟随实现所在目录组织。

## 当前目录

- `tests/fund/documents/test_repository.py`：文档仓库契约测试，验证仓库对外返回 `ParsedAnnualReport`，不暴露本地 `Path`
- `tests/fund/pdf/test_downloader.py`：PDF 下载 helper 测试，验证内部缓存命中、强制刷新下载和年报 URL 组装

## 运行方式

运行本次改动直接相关的测试：

```bash
pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py
```

## 维护约定

- 新增 Capability 测试时，优先使用 mock 或临时目录隔离网络和文件系统副作用。
- 文档仓库相关测试应围绕公共契约断言，不直接把 `pdf/*` helper 当成上层接口。
- `pdf/*` 目录下的测试允许直接覆盖内部 helper，但 README、示例和业务代码不应把它们当作稳定入口。
