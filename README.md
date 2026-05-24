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
fund-analysis analyze 004393 --report-year 2024
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
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json

# 基于 score.json 生成报告质量 gate
fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json

# 查询默认全 A 市场温度计
fund-analysis thermometer

# 查询自建全 A / 宽基指数温度计
fund-analysis thermometer --index wind_all_a,000300,000905 --json

# 生成独立买入前检查清单
fund-analysis checklist 004393 --report-year 2024
```

`fund-analysis checklist FUND_CODE` 已接入当前分析主链路，会输出 7 问题检查清单摘要、估值状态和最终判断，不渲染完整 8 章报告。

## 常用参数

| 参数 | 用途 |
|------|------|
| `--report-year` | 年报年份，默认 `2024` |
| `--investment-amount` | 压力测试投入金额，默认 `10000` |
| `--max-tolerable-loss-rate` | 最大可承受亏损比例，如 `50%` |
| `--valuation-state` | 手动估值状态：`low` / `fair` / `high` / `unavailable`；不传时尝试自建温度计自动估值 |
| `--thermometer-cache-dir` | `analyze` 自动估值使用的自建温度计缓存目录 |
| `--user-money-horizon-years` | 用户资金不用年限 |
| `--force-refresh` | 强制刷新底层数据 |

`analyze` 默认是 product mode：最终判断由 Agent 层基金能力根据检查清单、否决项、压力测试和 quality gate 派生；R=A+B-C 股票仓位、言行一致性实际风格、经理任期、同类费率、跟踪误差、当前阶段、最终判断覆盖和 quality gate `warn/off` 等夹具参数仅供开发验证使用，必须显式传 `--dev-override`。

`fund-analysis analyze FUND_CODE` 不传 `--valuation-state` 时，会先识别基金类型，再仅对 `index_fund` / `enhanced_index` 且业绩基准可精确映射到沪深300 `000300` 或中证500 `000905` 的基金调用项目内自建温度计。主动、债券、QDII、FOF、缺少基准、复合基准不确定、派生/策略/行业指数或未支持指数都会保持 `unavailable` 灰灯且不调用温度计。显式传 `--valuation-state unavailable` 会恢复旧的手动灰灯路径，并且不调用温度计；显式传 `low/fair/high` 也同样优先于自动估值。

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
- `fund-analysis checklist FUND_CODE` 独立买入前检查清单入口
- 统一年报仓库入口：`FundDocumentRepository.load_annual_report(...)`
- P1 结构化抽取：基金类型、产品画像、表现、经理/持有人、持仓和份额变化
- P2 分析：R=A+B-C、超额性质、言行一致性、投资者获得感、风险检查、压力测试、7 问题检查清单
- `analyze` 自动估值：仅对沪深300/中证500指数基金或指数增强基金使用自建温度计生成第 6 问估值状态
- 8 章 Markdown 模板渲染
- 程序审计规则：P1/P2/P3/C2/L1/R1/R2
- 有知有行温度计 data adapter：保留为过渡/对比能力，不再作为默认 CLI 查询路径
- 自建全 A 市场温度计 CLI 默认入口：`fund-analysis thermometer`
- 自建全 A / 宽基指数温度计 CLI 查询入口：`fund-analysis thermometer --index wind_all_a`、`fund-analysis thermometer --index 000300,000905`
- 精选基金池字段级抽取快照：`snapshot.jsonl`、`summary.md`、`errors.jsonl`
- 精选基金池字段级评分：`score.json`、`score.md`、`golden_set.json`
- Correctness golden answer 预填底稿：`fund-analysis golden-prefill`
- Correctness golden answer JSON 构建与 strict 校验：`fund-analysis golden-build`
- 报告质量 gate 骨架：`fund-analysis quality-gate`
- `fund-analysis analyze` 主链路质量保护：复用已抽取结构化数据生成 score/gate，默认 `block` 策略会阻断低质量精选基金报告输出，`warn` 策略只提示不阻断，`off` 明确跳过
- 3 只样本基金 CLI 端到端矩阵，覆盖报告完整性、程序审计和证据锚点

尚未接入：

- 真实 PDF/network 路径的普通 pytest gate；当前保留为显式 `--run` smoke

明确非目标：

- 主动基金持仓估值、债券/QDII/FOF 估值状态自动判断

## 本地验证

CI 使用 Python 3.11，并执行以下发布就绪检查：

```bash
uv sync --extra dev --frozen
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

当前自动 CI gate 是 `fund_agent` 全局覆盖率不低于 50%。仓库开发规则同时要求新增或大幅修改模块以单文件覆盖率 ≥80% 为评审目标；低于目标时应在 review 或 residual risk 中解释，不应在未评估缺口前直接提高 CI 阈值。

本地也可以按关注范围运行较小的测试集：

```bash
pytest tests/fund/data/test_thermometer.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/scripts/test_selected_funds_smoke.py -q
pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
pytest tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q
pytest tests/fund/test_extraction_snapshot.py tests/ui/test_cli.py -q
pytest tests/scripts/test_selected_funds_smoke.py -q
```

## 温度计查询

`fund-analysis thermometer` 通过 Service 调用 Agent 层基金 data 能力中的自建温度计，默认查询全 A 市场 `wind_all_a`。CLI 不再默认查询有知有行公开页快照；公开页 adapter 仅保留为过渡/对比能力，不作为当前默认 CLI 路径。

```bash
fund-analysis thermometer
fund-analysis thermometer --json
fund-analysis thermometer --force-refresh --cache-dir cache/thermometer
```

指定 `--index` 时，命令查询项目内自建全 A / 宽基指数温度计，不依赖有知有行页面抓取。当前支持全 A 市场 `wind_all_a`、沪深300 `000300` 和中证500 `000905`，可用逗号分隔批量查询：

```bash
fund-analysis thermometer --index wind_all_a
fund-analysis thermometer --index 000300
fund-analysis thermometer --index 000300 --json
fund-analysis thermometer --index wind_all_a,000300,000905
fund-analysis thermometer --index wind_all_a,000300,000905 --json
```

该命令只输出温度计摘要。`--force-refresh` 会刷新自有温度计历史数据。上游不可用会以 `unavailable: true` 或批量结果里的单项 `unavailable: true` 表示并正常退出；malformed `--index` 参数退出 2，运行异常退出 1。`analyze` 自动估值仍只使用沪深300/中证500 exact supported-index 单指数路径，不把全 A 自动套用于主动基金或复合基准，也不使用有知有行公开页快照作为分析真源。

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

默认输出到 snapshot 所在目录，包含 `score.json`、`score.md` 和 `golden_set.json`。`score.json` 同时包含字段级 `field_scores`、单基金 `fund_scores`、`fund_quality`、`failed_funds` 和 `correctness`。Correctness 只对 snapshot `comparable_values` 显式暴露的可比 golden 子字段做保守 normalize 后比较，skipped 和不可比记录不进入分母；`correctness.status` 只表达 `available / unavailable`，`coverage_scope` 进一步区分 `not_configured / fund_not_covered / no_comparable_fields / partially_covered / covered`。提供 `--errors-path` 时，`errors.jsonl` 中的完全失败基金会进入 `failed_funds` 并由 quality gate 阻断；未提供 `--golden-answer-path` 时只输出 `FQ0/info` 所需 metadata。最小 golden set 固定包含 `004393`，并暂时排除货币基金类。

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
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
```

`golden-build` 会校验每条有效行必须填写 `expected_value`、`confidence` 和 `source`，其中 `confidence` 只能是 `high / medium / low`，`source` 不能是 `manual_required`。校验通过后输出机器可读 JSON；该 JSON 是 correctness 自动比对的数据源。

基于 `score.json` 生成报告质量 gate：

```bash
fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json
```

默认输出到 `score.json` 所在目录，包含 `quality_gate.json` 和 `quality_gate.md`。当前 gate 消费 coverage / traceability / `fund_quality` / `failed_funds` / correctness：字段级或单基金 P0 fail 会阻断，单基金 issue 会保留 `fund_code`；P1 fail 会警告；App 类别与基金类型明确冲突或 strict golden answer mismatch 会触发 `FQ1/block`；字段缺失率达到阈值会触发 FQ4；基金类型无法解析 preferred_lens 会触发 FQ5；完全失败基金会触发 FQ6；strict golden answer 未配置、当前基金未覆盖或当前基金无可比字段时记录带 `reason` / `coverage_scope` / `fund_code` 的 `FQ0/info`，不等同于 gate 未运行。

`fund-analysis analyze` 默认也会运行 quality gate，product mode 使用 `docs/code_20260519.csv` 作为精选池 membership source，并使用默认 strict golden answer 路径。若 gate 状态为 `block` 或 gate 未运行，默认策略会非零退出并在 stderr 输出结构化原因，不输出完整报告；精选池成员缺 strict golden 覆盖时仍会输出报告，并在 stderr 增加 `quality_gate_info: ...`。`--quality-gate-policy warn/off` 仅可在 `--dev-override` 模式下用于开发验证。

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

真实运行的 smoke 命令会显式传入 `--dev-override --quality-gate-policy warn`，用于观察真实 PDF/network/report-rendering 路径，同时仍在 stderr 记录质量 gate 状态；生产 `fund-analysis analyze` 默认 `block` 策略不受影响。`results.jsonl` 和 `summary.md` 会分别记录进程退出状态与 `quality_gate_status`，避免把“链路跑完”误读为“质量 gate 通过”。

输出目录会包含每只基金的 Markdown 报告、stderr、`results.jsonl` 和 `summary.md`。当前 CSV 有 56 条记录、55 个唯一基金代码，`016492` 重复，需要人工确认后再启用 `--strict`。

完整开发验证入口见 [tests/README.md](tests/README.md)。

## 仓库产物策略

仓库采用 MIT License。发布基础验证由 GitHub Actions 执行 Python 3.11 下的 `uv sync --extra dev --frozen`、`uv run ruff check .` 和 `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`。

覆盖率策略分两层：CI 自动阻断使用全局 `--cov-fail-under=50`；单文件 ≥80% 是代码评审目标，适用于新增或大幅修改模块，需要通过定向测试、review 说明或 residual risk 追踪落实。

当前会跟踪人工维护或可复核的输入产物，例如 `docs/code_20260519.csv`、`docs/golden-answer-template.md` 和 `reports/golden-answers/` 下的 curated golden answer 文件。运行时生成物保持本地：`cache/`、`reports/extraction-snapshots/`、`reports/quality-gate-runs/`、`reports/smoke/`、`reports/scoring-runs/`、`reports/writing-runs/`、`reports/data-source-runs/`、`report.md`、`report-*.md` 和 `docs/*.docx` 不纳入默认版本控制。后续用于评分、数据源迭代、写作脚本迭代和报告质量调参的大量输出，应优先落在上述本地 run 目录；只有经人工复核后要作为长期基准的输入，才进入 `docs/` 或 curated fixture。

## 文档导航

| 文档 | 用途 |
|------|------|
| [docs/design.md](docs/design.md) | 设计真源 |
| [docs/implementation-control.md](docs/implementation-control.md) | Phase 与 gate 总控 |
| [docs/fund-analysis-template-draft.md](docs/fund-analysis-template-draft.md) | 8 章分析模板 |
| [docs/sample-funds.md](docs/sample-funds.md) | 样本基金基线 |
| [docs/code_20260519.csv](docs/code_20260519.csv) | 有知有行 App 精选基金池手动清单 |
| [fund_agent/README.md](fund_agent/README.md) | 开发手册总览，说明当前 UI / Service / Host / Agent 边界 |
| [fund_agent/fund/README.md](fund_agent/fund/README.md) | Fund 作为 Agent 层基金能力包的说明 |
| [fund_agent/config/README.md](fund_agent/config/README.md) | 配置命名空间当前状态 |
| [tests/README.md](tests/README.md) | 测试说明 |
