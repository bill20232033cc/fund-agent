# CLAUDE.md

This file gives Claude Code project-specific guidance for working in this repository.

## Project Overview

`fund-agent` 是基金分析 Agent 项目，基于有知有行投资方法论 `R = A + B - C`，从基金年报、招募说明书和定期报告中抽取结构化信息，生成买入前基金体检报告。

核心输出是 8 章 Markdown 报告：

1. 投资要点概览
2. 产品本质
3. `R=A+B-C` 收益归因
4. 基金经理画像与言行一致性
5. 投资者获得感
6. 当前阶段与关键变化
7. 核心风险与否决项
8. 最终判断

报告只允许输出 `值得持有`、`需要关注`、`建议替换` 这类判断；不要输出买入/卖出指令，不预测未来收益。

## Stack

- Runtime: Python 3.11+
- CLI: Typer, entry point `fund-analysis`
- Fund document parsing: `pdfplumber`
- Network/data: `httpx`, `akshare`
- Agent framework dependency: `dayu-agent`
- Tests: `pytest`, `pytest-asyncio`
- Lint/format: `ruff`

## Common Commands

```bash
# Install editable package
pip install -e .

# Run all tests
pytest

# Run focused tests
pytest tests/fund/documents tests/fund/pdf -q
pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q

# CLI help
fund-analysis --help
fund-analysis analyze --help

# Analyze one fund
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
  --quality-gate-policy warn

# Generate extraction snapshot and score
fund-analysis extraction-snapshot --run-id p4-s1-004393 --fund-code 004393 --report-year 2024
fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/p4-s1-004393/snapshot.jsonl

# Build correctness golden answers
fund-analysis golden-prefill \
  --template-path docs/golden-answer-template.md \
  --output-path reports/golden-answers/golden-answer-prefill.md
fund-analysis golden-build \
  --input-path reports/golden-answers/golden-answer-prefill-reviewed.md \
  --output-path reports/golden-answers/golden-answer.json
```

## Repository Structure

```text
fund_agent/
├── ui/                       # Typer CLI; only parses input and renders output
├── services/                 # Use-case orchestration; coordinates Capability modules
├── fund/                     # Fund Capability: domain rules, extractors, audit, template
│   ├── documents/            # Unified annual-report repository, sources, cache, metadata
│   ├── pdf/                  # Internal PDF parser/downloader helpers
│   ├── extractors/           # P1 structured extraction from parsed annual reports
│   ├── analysis/             # R=A+B-C, alpha nature, consistency, risk, checklist
│   ├── audit/                # Programmatic audit rules
│   ├── template/             # CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, renderer
│   └── data/                 # NAV and thermometer adapters
└── config/                   # Config package and prompt directory
tests/                        # Layered tests matching the implementation boundaries
docs/                         # Design/control docs, golden answer templates, reviews
reports/                      # Generated local artifacts; usually not source truth
```

## Layer Boundaries

Respect these boundaries when changing code:

- UI only handles CLI/user interaction and output. It must not implement fund analysis rules.
- Service orchestrates use cases and may call Capability modules. It must not read PDF/cache files directly.
- Fund Capability owns fund-domain knowledge, document parsing, extractor rules, CHAPTER_CONTRACT, preferred_lens, audit rules and evidence anchors.
- PDF and annual-report storage access must go through the unified document repository path, not ad hoc filesystem reads.
- Explicit parameters must stay explicit. Do not hide them inside `extra_payload`.

If a change crosses a boundary, adjust the design or implementation first instead of documenting an exception.

## Fund Analysis Rules

Always follow this flow:

```text
识别基金类型 -> 应用 preferred_lens -> 按 8 章模板分析 -> 审计检查 -> 生成证据锚点
```

Standard fund types:

- `index_fund`
- `active_fund`
- `bond_fund`
- `enhanced_index`
- `qdii_fund`
- `fof_fund`

Evidence requirements:

- Body citation format: `> 📎 证据：年报§[章节] [内容描述]`
- Appendix format: `年报[年份]§[章节]表[编号]行[行号]`
- All numeric judgments need traceable source locations.
- Do not use phrases like “根据经验” or “通常认为” for unsupported conclusions.

## Current Document Source Behavior

Annual-report PDF access is internal to `fund_agent.fund.documents`:

- Primary source: EID/证监会资本市场统一信息披露平台
- Fallback source: Eastmoney/akshare
- CNINFO is not the primary source for public fund annual reports
- PDF cache entries validate `%PDF-` magic bytes before reuse
- PDF writes use temp file + atomic replace
- Parsed-report JSON cache corruption is treated as cache miss and reparsed

Do not bypass `FundDocumentRepository` for fund documents in production code.

## Quality Gate

`fund-analysis analyze` defaults to `--quality-gate-policy block`.

- `block`: low-quality reports or not-run gate conditions block output and exit with code 2
- `warn`: prints quality gate summary but still emits the report
- `off`: skips the gate explicitly

The analyze path reuses already extracted `StructuredFundDataBundle`; it should not re-extract just to run the gate.

## Coding Conventions

- Use Python type hints.
- Public modules/classes/functions should have Chinese docstrings with Args/Returns/Raises where applicable.
- Keep helper functions module-level unless a closure is truly needed.
- Prefer structured parsers and existing local helpers over ad hoc string manipulation.
- Keep tests close to the changed boundary.
- Do not introduce new hardcoded fund rules when a config/manifest path already exists.

## Testing Guidance

Run at least the focused tests for the changed layer. For broad changes, run:

```bash
pytest
```

Important focused suites:

- Document repository/source/cache: `pytest tests/fund/documents tests/fund/pdf -q`
- Extractors: `pytest tests/fund/extractors -q`
- Template/audit: `pytest tests/fund/template tests/fund/audit -q`
- Service/UI: `pytest tests/services tests/ui -q`
- Full integration matrix: `pytest tests/fund/integration -q`

Tests should use fake repositories, fake sources, fixtures, or temporary directories unless the task explicitly asks for real network smoke.

## Documentation

Keep docs aligned with code:

- User-facing CLI changes: update root `README.md`
- Fund Capability changes: update `fund_agent/fund/README.md`
- Test structure changes: update `tests/README.md`
- Design/control status changes: update relevant `docs/` files

Do not keep old project names, old paths, or old commands alongside new ones.
