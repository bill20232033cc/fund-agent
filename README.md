# 基金分析 Agent

基于有知有行投资方法论 `R = A + B - C` 的基金分析工具。当前 CLI 可以读取基金年报，抽取结构化信息，生成 8 章 Markdown 体检报告，并通过程序审计检查报告结构、证据锚点和关键判断边界。

报告只输出三类判断：`值得持有`、`需要关注`、`建议替换`。不会输出买入、卖出指令，也不会预测未来收益。

## 快速开始

环境要求：Python 3.11 或更高版本。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
fund-analysis --help
```

5 分钟跑通一只基金：

```bash
fund-analysis analyze 110011 \
  --report-year 2024 \
  --equity-position 80% \
  --actual-style 均衡 \
  --actual-equity-position 70% \
  --manager-tenure-months 24 \
  --peer-fee-median 1.00% \
  --investment-amount 10000 \
  --max-tolerable-loss-rate 50% \
  --valuation-state low \
  --user-money-horizon-years 4 \
  --current-stage 估值较低但需继续跟踪境外市场波动。 \
  --final-judgment worth_holding
```

命令成功后会把完整 Markdown 报告写到 stdout。需要保存报告时可使用 shell 重定向：

```bash
fund-analysis analyze 110011 --report-year 2024 > report-110011.md
```

## 常用命令

```bash
# 查看顶层命令
fund-analysis --help

# 查看 analyze 参数
fund-analysis analyze --help

# 强制刷新底层数据
fund-analysis analyze 110011 --report-year 2024 --force-refresh
```

当前 `fund-analysis checklist FUND_CODE` 是占位命令，尚未接入 Service。请使用 `fund-analysis analyze FUND_CODE` 生成包含检查清单的完整报告。

## 常用参数

| 参数 | 用途 |
|------|------|
| `--report-year` | 年报年份，默认 `2024` |
| `--equity-position` | R=A+B-C 使用的显式股票仓位，如 `80%` |
| `--actual-style` | 言行一致性检查使用的实际持仓风格 |
| `--actual-equity-position` | 言行一致性检查使用的实际股票仓位 |
| `--manager-tenure-months` | 基金经理管理本基金月数 |
| `--peer-fee-median` | 同类总费率中位数，如 `1.00%` |
| `--tracking-error` | 指数基金跟踪误差，如 `1.50%` |
| `--investment-amount` | 压力测试投入金额，默认 `10000` |
| `--max-tolerable-loss-rate` | 最大可承受亏损比例，如 `50%` |
| `--valuation-state` | 估值状态：`low` / `fair` / `high` / `unavailable` |
| `--money-horizon` | 资金期限分类：`long_enough` / `uncertain` / `too_short` |
| `--user-money-horizon-years` | 用户资金不用年限 |
| `--current-stage` | 当前阶段与关键变化说明 |
| `--final-judgment` | `worth_holding` / `needs_attention` / `suggest_replace` |
| `--force-refresh` | 强制刷新底层数据 |

## 输出内容

`fund-analysis analyze` 输出 8 章报告：

| 章节 | 内容 |
|------|------|
| 第 0 章 | 投资要点概览 |
| 第 1 章 | 产品本质 |
| 第 2 章 | `R=A+B-C` 收益归因 |
| 第 3 章 | 基金经理画像与言行一致性 |
| 第 4 章 | 投资者获得感 |
| 第 5 章 | 当前阶段与关键变化 |
| 第 6 章 | 核心风险与否决项 |
| 第 7 章 | 最终判断 |

报告正文会以 `> 📎 证据：...` 标注章节证据，末尾会输出 `## 证据与出处` 附录。年报来源按 `年报{年份}§{章节}表{编号}行{行号}` 格式渲染，便于复核。

## 当前能力

已实现：

- `fund-analysis analyze FUND_CODE` CLI 分析入口
- 统一年报仓库入口：`FundDocumentRepository.load_annual_report(...)`
- P1 结构化抽取：基金类型、产品画像、表现、经理/持有人、持仓和份额变化
- P2 分析：R=A+B-C、超额性质、言行一致性、投资者获得感、风险检查、压力测试、7 问题检查清单
- 8 章 Markdown 模板渲染
- 程序审计规则：P1/P2/P3/L1/R1/R2
- 有知有行温度计 data adapter
- 3 只样本基金 CLI 端到端矩阵，覆盖报告完整性、程序审计和证据锚点

尚未接入：

- 温度计数据进入 CLI/Service 分析报告
- 独立 `fund-analysis checklist` Service 命令
- 真实 PDF/network 路径的自动化 smoke gate

## 本地验证

```bash
pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
pytest tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q
```

完整开发验证入口见 [tests/README.md](tests/README.md)。

## 文档导航

| 文档 | 用途 |
|------|------|
| [docs/design.md](docs/design.md) | 设计真源 |
| [docs/implementation-control.md](docs/implementation-control.md) | Phase 与 gate 总控 |
| [docs/fund-analysis-template-draft.md](docs/fund-analysis-template-draft.md) | 8 章分析模板 |
| [docs/sample-funds.md](docs/sample-funds.md) | 样本基金基线 |
| [fund_agent/fund/README.md](fund_agent/fund/README.md) | Fund capability 说明 |
| [tests/README.md](tests/README.md) | 测试说明 |
