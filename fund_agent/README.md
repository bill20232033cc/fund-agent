# fund_agent 开发手册

`fund_agent` 是基金分析 Agent 的 Python 包。当前主链路是确定性三层架构：

```text
UI CLI -> Service use case -> Fund Capability
```

当前代码不接入外部 Dayu Host、Engine、tool loop、scene registry 或 LLM prompt runtime。后续如需要这些能力，应在本项目内按当前边界实现，不通过外部 Dayu API 包装主链路。

## 当前包边界

| 包 | 职责 |
|----|------|
| `fund_agent/ui` | Typer CLI、参数采集、stdout/stderr 输出和退出码 |
| `fund_agent/services` | 用例编排、请求校验、调用 Fund Capability、组合返回结果 |
| `fund_agent/fund` | 基金领域能力：文档仓库、抽取、分析、模板、审计、quality gate、数据 adapter |
| `fund_agent/config` | 配置命名空间占位；当前不参与主链路装配 |

## 稳定边界

- UI 只调用 Service，不直接读取年报、PDF、cache 或 Fund 内部 helper。
- Service 可编排 Capability 的公开函数和数据对象，不承载基金领域规则。
- Fund Capability 拥有基金类型判断、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点和审计规则。
- 文档读取只通过 `FundDocumentRepository.load_annual_report(...)` 进入生产路径。
- Dayu 相关 Host/Engine/Prompting 只作为方法论参考，不是安装依赖或当前主链路事实。

## 阅读顺序

1. `fund_agent/ui/cli.py`
2. `fund_agent/services/fund_analysis_service.py`
3. `fund_agent/fund/data_extractor.py`
4. `fund_agent/fund/documents/repository.py`
5. `fund_agent/fund/template/renderer.py`
6. `fund_agent/fund/audit/audit_programmatic.py`

更细的 Fund Capability 机制见 `fund_agent/fund/README.md`。
