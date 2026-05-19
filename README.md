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
fund-analysis analyze 004393 \
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
  --final-judgment worth_holding \
  --quality-gate-policy warn
```

命令成功后会把完整 Markdown 报告写到 stdout，quality gate 摘要写到 stderr。需要保存报告时可使用 shell 重定向：

```bash
fund-analysis analyze 004393 --report-year 2024 > report-004393.md
```

## 常用命令

```bash
# 查看顶层命令
fund-analysis --help

# 查看 analyze 参数
fund-analysis analyze --help

# 强制刷新底层数据
fund-analysis analyze 004393 --report-year 2024 --force-refresh

# 生成精选基金池字段级抽取快照
fund-analysis extraction-snapshot \
  --run-id p4-s1-004393 \
  --fund-code 004393 \
  --report-year 2024

# 对已有 snapshot 生成字段级评分
fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/p4-s1-004393/snapshot.jsonl

# 生成 correctness golden answer 预填底稿
fund-analysis golden-prefill \
  --template-path docs/golden-answer-template.md \
  --output-path reports/golden-answers/golden-answer-prefill.md

# 将人工审核后的 golden answer Markdown 转为 strict JSON
fund-analysis golden-build \
  --input-path reports/golden-answers/golden-answer-prefill.md \
  --output-path reports/golden-answers/golden-answer.json

# 基于 score.json 生成报告质量 gate
fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json
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
| `--quality-gate-policy` | 报告质量 gate 策略：`block` / `warn` / `off`，默认 `block` |
| `--quality-gate-source-csv` | 精选基金池 CSV，默认 `docs/code_20260519.csv` |
| `--quality-gate-output-dir` | quality gate 输出目录；为空时自动生成不覆盖的运行目录 |
| `--quality-gate-run-id` | quality gate 运行 ID；为空时自动生成 |
| `--quality-gate-golden-answer-path` | strict golden answer JSON 路径，默认 `reports/golden-answers/golden-answer.json` |

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
- 有知有行温度计 Service/CLI 查询入口：`fund-analysis thermometer`
- 精选基金池字段级抽取快照：`snapshot.jsonl`、`summary.md`、`errors.jsonl`
- 精选基金池字段级评分：`score.json`、`score.md`、`golden_set.json`
- Correctness golden answer 预填底稿：`fund-analysis golden-prefill`
- Correctness golden answer JSON 构建与 strict 校验：`fund-analysis golden-build`
- 报告质量 gate 骨架：`fund-analysis quality-gate`
- `fund-analysis analyze` 主链路质量保护：复用已抽取结构化数据生成 score/gate，默认 `block` 策略会阻断低质量精选基金报告输出，`warn` 策略只提示不阻断，`off` 明确跳过
- 3 只样本基金 CLI 端到端矩阵，覆盖报告完整性、程序审计和证据锚点

尚未接入：

- 温度计数据自动映射为 `analyze --valuation-state`
- 独立 `fund-analysis checklist` Service 命令
- 真实 PDF/network 路径的普通 pytest gate；当前保留为显式 `--run` smoke

## 本地验证

```bash
pytest tests/fund/data/test_thermometer.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/scripts/test_selected_funds_smoke.py -q
pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
pytest tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q
pytest tests/fund/test_extraction_snapshot.py tests/ui/test_cli.py -q
pytest tests/scripts/test_selected_funds_smoke.py -q
```

## 温度计查询

`fund-analysis thermometer` 通过 Service 调用 Capability data 层的 `FundThermometerAdapter`，查询有知有行公开温度计数据并复用本地缓存：

```bash
fund-analysis thermometer
fund-analysis thermometer --json
fund-analysis thermometer --force-refresh --cache-dir cache/thermometer
```

该命令只输出温度计快照摘要。上游不可用会以 `unavailable: true` 表示并正常退出；只有参数校验或运行异常才非零退出。当前不会把温度计数值自动映射为 `low/fair/high`，分析报告仍需要显式传入 `--valuation-state`。

## 精选基金池抽取快照

`fund-analysis extraction-snapshot` 会读取 `docs/code_20260519.csv`，通过 `FundDataExtractor.extract(...)` 生成字段级抽取状态，不直接读取 PDF 或缓存文件：

```bash
fund-analysis extraction-snapshot \
  --run-id p4-s1-selected-1x \
  --report-year 2024 \
  --sample-per-category 1
```

默认输出到 `reports/extraction-snapshots/<run-id>/`，包含 `snapshot.jsonl`、`summary.md` 和 `errors.jsonl`。当前 CSV 中 `016492` 重复，summary 会标红但不阻断 P4-S1 快照。

对已有 snapshot 生成字段级 coverage / traceability 评分：

```bash
fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/p4-s1-selected-1x/snapshot.jsonl \
  --errors-path reports/extraction-snapshots/p4-s1-selected-1x/errors.jsonl \
  --golden-answer-path reports/golden-answers/golden-answer.json
```

默认输出到 snapshot 所在目录，包含 `score.json`、`score.md` 和 `golden_set.json`。`score.json` 同时包含字段级 `field_scores`、单基金 `fund_scores`、`fund_quality`、`failed_funds` 和 `correctness`。Correctness 只对 snapshot `comparable_values` 显式暴露的可比 golden 子字段做保守 normalize 后比较，skipped 和不可比记录不进入分母；提供 `--errors-path` 时，`errors.jsonl` 中的完全失败基金会进入 `failed_funds` 并由 quality gate 阻断；未提供 `--golden-answer-path` 时只输出 `FQ0/info` 所需 skeleton。最小 golden set 固定包含 `004393`，并暂时排除货币基金类。

生成 correctness golden answer 自动预填底稿：

```bash
fund-analysis golden-prefill \
  --template-path docs/golden-answer-template.md \
  --output-path reports/golden-answers/golden-answer-prefill.md \
  --report-year 2024
```

该命令读取模板中的基金代码，通过 `FundDataExtractor.extract(...)` 自动填入当前 extractor 输出值、置信度和证据来源。输出是人工复核底稿，不能直接作为 correctness golden answer。

人工审核底稿后，生成 strict JSON：

```bash
fund-analysis golden-build \
  --input-path reports/golden-answers/golden-answer-prefill.md \
  --output-path reports/golden-answers/golden-answer.json
```

`golden-build` 会校验每条有效行必须填写 `expected_value`、`confidence` 和 `source`，其中 `confidence` 只能是 `high / medium / low`，`source` 不能是 `manual_required`。校验通过后输出机器可读 JSON；该 JSON 是 correctness 自动比对的数据源。

基于 `score.json` 生成报告质量 gate：

```bash
fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json
```

默认输出到 `score.json` 所在目录，包含 `quality_gate.json` 和 `quality_gate.md`。当前 gate 消费 coverage / traceability / `fund_quality` / `failed_funds` / correctness：字段级或单基金 P0 fail 会阻断，单基金 issue 会保留 `fund_code`；P1 fail 会警告；App 类别与基金类型明确冲突或 strict golden answer mismatch 会触发 `FQ1/block`；字段缺失率达到阈值会触发 FQ4；基金类型无法解析 preferred_lens 会触发 FQ5；完全失败基金会触发 FQ6；correctness 未接入时只记录 `FQ0/info`。

`fund-analysis analyze` 默认也会运行 quality gate。若 gate 状态为 `block`，默认策略会非零退出并在 stderr 输出 `quality_gate.json` / `quality_gate.md` 路径，不输出完整报告；使用 `--quality-gate-policy warn` 可保留报告输出并只在 stderr 提示；使用 `--quality-gate-policy off` 会明确跳过 gate。

## 真实精选基金池 Smoke

`docs/code_20260519.csv` 是当前手动维护的有知有行 App 精选基金池清单。默认 smoke 脚本只校验清单并打印计划，不触发网络或 PDF 下载：

```bash
.venv/bin/python scripts/selected_funds_smoke.py
```

先跑一只已知精选基金：

```bash
.venv/bin/python scripts/selected_funds_smoke.py \
  --code 004393 \
  --run \
  --output-dir reports/smoke/004393
```

按类别各抽 1 只并继续记录所有失败：

```bash
.venv/bin/python scripts/selected_funds_smoke.py \
  --sample-per-category 1 \
  --run \
  --continue-on-fail \
  --output-dir reports/smoke/selected-1x
```

真实运行的 smoke 命令会显式传入 `--quality-gate-policy warn`，用于观察真实 PDF/network/report-rendering 路径，同时仍在 stderr 记录质量 gate 状态；生产 `fund-analysis analyze` 默认 `block` 策略不受影响。`results.jsonl` 和 `summary.md` 会分别记录进程退出状态与 `quality_gate_status`，避免把“链路跑完”误读为“质量 gate 通过”。

输出目录会包含每只基金的 Markdown 报告、stderr、`results.jsonl` 和 `summary.md`。当前 CSV 有 56 条记录、55 个唯一基金代码，`016492` 重复，需要人工确认后再启用 `--strict`。

完整开发验证入口见 [tests/README.md](tests/README.md)。

## 文档导航

| 文档 | 用途 |
|------|------|
| [docs/design.md](docs/design.md) | 设计真源 |
| [docs/implementation-control.md](docs/implementation-control.md) | Phase 与 gate 总控 |
| [docs/implementation-control-p4.md](docs/implementation-control-p4.md) | P4 精选基金池质量闭环执行控制 |
| [docs/post-mvp-p4-first-principles-plan.md](docs/post-mvp-p4-first-principles-plan.md) | P4 第一性原理行动计划 |
| [docs/fund-analysis-template-draft.md](docs/fund-analysis-template-draft.md) | 8 章分析模板 |
| [docs/sample-funds.md](docs/sample-funds.md) | 样本基金基线 |
| [docs/code_20260519.csv](docs/code_20260519.csv) | 有知有行 App 精选基金池手动清单 |
| [fund_agent/fund/README.md](fund_agent/fund/README.md) | Fund capability 说明 |
| [tests/README.md](tests/README.md) | 测试说明 |
